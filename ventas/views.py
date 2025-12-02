import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import F, Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from carrito.cart import Cart
from productos.models import Producto
from .forms import CheckoutForm
from .models import PagoTransbank, Venta, VentaItem
from .serializers import VentaReadSerializer, VentaSerializer
from .transbank import TransbankClient, TransbankError

logger = logging.getLogger(__name__)

try:
    from clientes.models import Cliente
except Exception:
    Cliente = None


# ===============================
# Helpers internos
# ===============================

def _cart_lines(request) -> Tuple[List[Dict], Decimal]:
    cart = request.session.get("cart", {}) or {}
    if not cart:
        return [], Decimal("0")

    productos = {
        str(p.id): p
        for p in Producto.objects.filter(id__in=[int(pid) for pid in cart.keys()])
    }

    items = []
    total = Decimal("0")

    for pid, data in cart.items():
        producto = productos.get(pid)
        if not producto:
            continue
        qty = int(data.get("qty", 0))
        if qty <= 0:
            continue

        price = Decimal(str(data.get("price", producto.precio)))
        subtotal = price * qty
        total += subtotal

        items.append({
            "producto": producto,
            "qty": qty,
            "price": price,
            "subtotal": subtotal,
            "pid": pid,
        })

    return items, total


def _sync_cliente(data: Dict) -> Cliente | None:
    if not Cliente:
        return None

    email = data.get("email", "").strip().lower()
    if not email:
        return None

    cliente, created = Cliente.objects.get_or_create(
        email=email,
        defaults={
            "nombre": data.get("nombre", ""),
            "telefono": data.get("telefono", ""),
        },
    )

    updated = False
    nombre = data.get("nombre") or ""
    telefono = data.get("telefono") or ""

    if not created:
        if nombre and cliente.nombre != nombre:
            cliente.nombre = nombre
            updated = True
        if telefono and cliente.telefono != telefono:
            cliente.telefono = telefono
            updated = True

    if updated:
        cliente.save(update_fields=["nombre", "telefono"])

    return cliente


def _generate_buy_order(venta_id: int) -> str:
    stamp = timezone.now().strftime("%m%d%H%M%S")
    return f"AK{venta_id:06d}{stamp}"[:26]


def _build_session_id(request) -> str:
    user_part = (
        str(request.user.pk)
        if getattr(request.user, "is_authenticated", False)
        else "anon"
    )
    return f"{user_part}-{timezone.now().strftime('%H%M%S%f')}"


def _amount_to_int(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _send_boleta_email(venta: Venta) -> None:
    if not venta.email_cliente:
        return

    pago = getattr(venta, "pago_transbank", None)
    if pago and pago.email_enviado:
        return

    items = venta.items.select_related("producto")
    detalle_items = [
        {
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad,
            "precio": item.precio_unitario,
            "subtotal": item.cantidad * item.precio_unitario,
        }
        for item in items
    ]

    context = {"venta": venta, "detalle_items": detalle_items}
    subject = f"Boleta Akuma no Pet #{venta.pk}"
    html = render_to_string("ventas/email_boleta.html", context)
    txt = render_to_string("ventas/email_boleta.txt", context)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[venta.email_cliente],
        )
        email.attach_alternative(html, "text/html")
        email.send()
    except Exception as exc:
        logger.exception("Error enviando boleta: %s", exc)
    else:
        pago.email_enviado = True
        pago.save(update_fields=["email_enviado"])


# ===============================
# Checkout
# ===============================

@require_http_methods(["GET", "POST"])
def checkout(request):
    items, total = _cart_lines(request)

    if not items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect("carrito:ver")

    initial = {}
    if request.user.is_authenticated:
        initial = {
            "nombre": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
        }

    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        try:
            response, venta = _crear_transaccion(request, form.cleaned_data, items, total)
        except TransbankError as exc:
            messages.error(request, f"Error iniciando pago: {exc}")
        else:
            request.session["checkout_sale_id"] = venta.pk
            request.session.modified = True
            return render(
                request,
                "ventas/transbank_redirect.html",
                {"url_tbk": response["url"], "token": response["token"]},
            )

    return render(
        request,
        "ventas/checkout.html",
        {"form": form, "items": items, "total": total},
    )


def _crear_transaccion(request, data, items, total):
    client = TransbankClient()
    with transaction.atomic():

        cliente_obj = _sync_cliente(data)
        venta = Venta.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            cliente=cliente_obj,
            metodo_pago="WEBPAY",
            estado="PENDIENTE",
            nombre_cliente=data.get("nombre", ""),
            rut_cliente=data.get("rut", ""),
            email_cliente=data.get("email", ""),
            telefono_cliente=data.get("telefono", ""),
            direccion_entrega="",
            notas_cliente=data.get("comentarios", ""),
        )

        for item in items:
            VentaItem.objects.create(
                venta=venta,
                producto=item["producto"],
                cantidad=item["qty"],
                precio_unitario=item["price"],
            )

        venta.recomputar_total()
        venta.save(update_fields=["total"])

        buy_order = _generate_buy_order(venta.pk)
        session_id = _build_session_id(request)
        return_url = request.build_absolute_uri(reverse("ventas:transbank_confirm"))

        response = client.create_transaction(
            amount=_amount_to_int(total),
            buy_order=buy_order,
            session_id=session_id,
            return_url=return_url,
        )

        token = response.get("token")
        if not token:
            raise TransbankError("Transbank no entregó token.")

        PagoTransbank.objects.create(
            venta=venta,
            token=token,
            buy_order=buy_order,
            session_id=session_id,
            amount=_amount_to_int(total),
            response_payload=response,
        )

    return response, venta


# ===============================
# CONFIRMACIÓN WEBPAY
# ===============================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def transbank_confirm(request):
    """
    Acepta:
    - GET con ?token_ws
    - POST con token_ws
    - POST con TBK_TOKEN (cancelación)
    """

    # Tokens de Transbank
    token_ws = request.POST.get("token_ws") or request.GET.get("token_ws")
    tbk_token = request.POST.get("TBK_TOKEN")

    # CANCELACIÓN del usuario (TBK_TOKEN)
    if tbk_token and not token_ws:
        pago = PagoTransbank.objects.filter(token=tbk_token).select_related("venta").first()
        if pago:
            venta = pago.venta
            pago.status = "ANULADA"
            pago.save(update_fields=["status"])
            venta.estado = "ANULADA"
            venta.save(update_fields=["estado"])

        request.session["checkout_result"] = {
            "venta_id": venta.pk if pago else None,
            "success": False,
            "message": "El pago fue cancelado.",
        }
        return redirect("ventas:checkout_result")

    # FALLA: No viene token_ws
    if not token_ws:
        return HttpResponseBadRequest("token_ws no encontrado.")

    # Buscar pago asociado al token_ws
    pago = get_object_or_404(
        PagoTransbank.objects.select_related("venta"),
        token=token_ws
    )
    venta = pago.venta

    # CONFIRMAR TRANSACCIÓN
    try:
        client = TransbankClient()
        resp = client.commit_transaction(token_ws)
    except TransbankError as exc:
        pago.status = "ERROR"
        pago.response_payload = {"error": str(exc)}
        pago.save(update_fields=["status", "response_payload"])

        request.session["checkout_result"] = {
            "venta_id": venta.pk,
            "success": False,
            "message": f"Ocurrió un error al confirmar el pago: {exc}",
        }
        return redirect("ventas:checkout_result")

    estado_tbk = resp.get("status")
    autorizado = estado_tbk == "AUTHORIZED"

    # Guardar respuesta
    pago.status = "AUTORIZADA" if autorizado else "RECHAZADA"
    pago.authorization_code = resp.get("authorization_code", "")
    pago.payment_type = resp.get("payment_type_code", "")
    pago.installments = resp.get("installments_number")
    pago.accounting_date = resp.get("accounting_date", "")
    pago.response_payload = resp

    txn_date = resp.get("transaction_date")
    if txn_date:
        try:
            dt = timezone.datetime.fromisoformat(txn_date)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            pago.transaction_date = dt
        except:
            pass

    pago.save()

    # Resultado final
    if autorizado:
        venta.estado = "PAGADA"
        venta.metodo_pago = "WEBPAY"

        amount = resp.get("amount")
        if amount:
            try:
                venta.total = Decimal(str(amount))
            except:
                pass

        venta.save(update_fields=["estado", "metodo_pago", "total"])

        Cart(request).clear()
        _send_boleta_email(venta)

        request.session["checkout_result"] = {
            "venta_id": venta.pk,
            "success": True,
            "message": "Pago aprobado. Se envió boleta al correo.",
        }

    else:
        venta.estado = "ANULADA"
        venta.save(update_fields=["estado"])

        request.session["checkout_result"] = {
            "venta_id": venta.pk,
            "success": False,
            "message": "El pago fue rechazado.",
        }

    return redirect("ventas:checkout_result")


# ===============================
# Pantalla de resultado
# ===============================

def checkout_result(request):
    data = request.session.pop("checkout_result", None)

    if not data:
        messages.warning(request, "No encontramos información del pago.")
        return redirect("productos:lista")

    venta = get_object_or_404(
        Venta.objects.prefetch_related("items__producto"),
        pk=data["venta_id"],
    )

    detalle_items = [
        {
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad,
            "precio": item.precio_unitario,
            "subtotal": item.cantidad * item.precio_unitario,
        }
        for item in venta.items.all()
    ]

    pago = getattr(venta, "pago_transbank", None)

    return render(
        request,
        "ventas/checkout_result.html",
        {
            "venta": venta,
            "pago": pago,
            "success": data.get("success"),
            "message": data.get("message"),
            "detalle_items": detalle_items,
        },
    )


# ===============================
# API
# ===============================

class VentaListCreateView(generics.ListCreateAPIView):
    queryset = Venta.objects.select_related("cliente", "usuario").prefetch_related(
        "items__producto"
    )
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return VentaSerializer if self.request.method == "POST" else VentaReadSerializer


class VentasResumenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        desde = parse_date(request.GET.get("desde") or "")
        hasta = parse_date(request.GET.get("hasta") or "")
        qs = Venta.objects.all()

        if desde:
            qs = qs.filter(creado_en__date__gte=desde)
        if hasta:
            qs = qs.filter(creado_en__date__lte=hasta)

        ingresos = qs.aggregate(suma=Sum("total"))["suma"] or 0
        total_ventas = qs.count()
        total_items = (
            VentaItem.objects.filter(venta__in=qs).aggregate(suma=Sum("cantidad"))["suma"]
            or 0
        )
        ticket_promedio = ingresos / total_ventas if total_ventas else 0

        return Response({
            "ingresos": float(ingresos),
            "total_ventas": total_ventas,
            "total_items": int(total_items),
            "ticket_promedio": float(ticket_promedio),
        })


class VentasTopProductosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        desde = request.GET.get("desde") or ""
        hasta = request.GET.get("hasta") or ""
        limit = int(request.GET.get("limit") or 5)

        items = VentaItem.objects.select_related("producto")
        if desde:
            items = items.filter(venta__creado_en__date__gte=desde)
        if hasta:
            items = items.filter(venta__creado_en__date__lte=hasta)

        agg = (
            items.values("producto", "producto__nombre")
            .annotate(
                unidades=Sum("cantidad"),
                ingresos=Sum(F("cantidad") * F("precio_unitario")),
            )
            .order_by("-unidades")[:limit]
        )

        data = [
            {
                "producto": row["producto"],
                "nombre": row["producto__nombre"],
                "unidades": int(row["unidades"] or 0),
                "ingresos": float(row["ingresos"] or 0),
            }
            for row in agg
        ]

        return Response(data)
