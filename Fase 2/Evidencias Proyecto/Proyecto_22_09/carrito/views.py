# carrito/views.py
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from productos.models import Producto


# ---------- helpers de sesión ----------
def _get_cart(request):
    """Obtiene el carrito de la sesión (dict)."""
    return request.session.get("cart", {}) or {}


def _save_cart(request, cart: dict):
    """Guarda el carrito en la sesión."""
    request.session["cart"] = cart
    request.session.modified = True


def _img_url(producto: Producto) -> str:
    """Obtiene una URL de imagen si existe (ajústalo a tu modelo)."""
    # Si tienes ImageField en el modelo:
    if hasattr(producto, "imagen") and getattr(producto.imagen, "url", None):
        return producto.imagen.url
    # O algún campo personalizado:
    if hasattr(producto, "imagen_url") and producto.imagen_url:
        return producto.imagen_url
    return ""


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _totales(cart: dict):
    total = 0
    count = 0
    for it in cart.values():
        qty = _safe_int(it.get("qty"), 0)
        price = _safe_int(it.get("price"), 0)
        total += qty * price
        count += qty
    return count, total


# ---------- vistas de página completa (opcional) ----------
def detalle(request):
    """
    Página de carrito en vista completa (si quieres /carrito/detail/).
    """
    cart = _get_cart(request)
    items = []
    for pid, it in cart.items():
        producto = get_object_or_404(Producto, pk=pid)
        qty = _safe_int(it.get("qty"), 0)
        price = _safe_int(it.get("price"), 0)
        items.append(
            {
                "producto": producto,
                "qty": qty,
                "price": price,
                "subtotal": price * qty,
                "img": it.get("img") or _img_url(producto),
            }
        )
    count, total = _totales(cart)
    return render(
        request,
        "carrito/detalle.html",
        {"items": items, "count": count, "total": total},
    )


# ---------- APIs para drawer/modal (AJAX) ----------
def mini(request):
    """
    Devuelve JSON con el HTML del parcial del drawer y los totales.
    Úsalo para pintar/repintar el carrito lateral o modal.
    """
    cart = _get_cart(request)

    lines = []
    for pid, it in cart.items():
        producto = get_object_or_404(Producto, pk=pid)
        qty = _safe_int(it.get("qty"), 0)
        price = _safe_int(it.get("price"), 0)
        lines.append(
            {
                "id": producto.id,
                "name": producto.nombre,
                "img": it.get("img") or _img_url(producto),
                "qty": qty,
                "price": price,
                "subtotal": price * qty,
            }
        )

    count, total = _totales(cart)
    html = render_to_string(
        "carrito/_mini.html",
        {"lines": lines, "count": count, "total": total},
        request=request,
    )
    return JsonResponse({"ok": True, "html": html, "count": count, "total": total})


@require_POST
def add(request, producto_id):
    """
    Agrega un producto al carrito.
    En el body espera:
      - qty (opcional, default 1)
      - override ("1" para asignar qty exacto, "0" para acumular)
    """
    producto = get_object_or_404(Producto, pk=producto_id)
    qty = _safe_int(request.POST.get("qty"), 1)
    if qty < 1:
        qty = 1
    override = request.POST.get("override") == "1"

    cart = _get_cart(request)
    pid = str(producto.id)
    if pid not in cart:
        cart[pid] = {
            "price": _safe_int(producto.precio),
            "qty": 0,
            "name": producto.nombre,
            "img": _img_url(producto),
        }

    cart[pid]["qty"] = qty if override else cart[pid]["qty"] + qty
    _save_cart(request, cart)

    count, total = _totales(cart)

    # Opcionalmente devuelves también el HTML del drawer listo:
    html = render_to_string(
        "carrito/_mini.html",
        {"lines": _lines_for_template(cart), "count": count, "total": total},
        request=request,
    )

    return JsonResponse(
        {
            "ok": True,
            "cart": {"count": count, "total": total},
            "item": {
                "id": producto.id,
                "name": producto.nombre,
                "price": _safe_int(producto.precio),
                "qty": cart[pid]["qty"],
                "img": cart[pid]["img"],
            },
            "html": html,  # si quieres abrir el drawer inmediatamente
        }
    )


@require_POST
def update(request, producto_id):
    """Actualiza cantidad de una línea y retorna drawer actualizado (JSON+HTML)."""
    qty = _safe_int(request.POST.get("qty"), 1)
    if qty < 1:
        return HttpResponseBadRequest("qty >= 1")

    cart = _get_cart(request)
    pid = str(producto_id)
    if pid in cart:
        cart[pid]["qty"] = qty
        _save_cart(request, cart)

    return mini(request)  # devuelve mismo JSON {ok, html, count, total}


@require_POST
def remove(request, producto_id):
    """Elimina una línea del carrito y retorna drawer actualizado (JSON+HTML)."""
    cart = _get_cart(request)
    pid = str(producto_id)
    if pid in cart:
        del cart[pid]
        _save_cart(request, cart)

    return mini(request)  # devuelve mismo JSON {ok, html, count, total}


# ---------- helper interno para reutilizar armado de líneas ----------
def _lines_for_template(cart: dict):
    lines = []
    for pid, it in cart.items():
        producto = get_object_or_404(Producto, pk=pid)
        qty = _safe_int(it.get("qty"), 0)
        price = _safe_int(it.get("price"), 0)
        lines.append(
            {
                "id": producto.id,
                "name": producto.nombre,
                "img": it.get("img") or _img_url(producto),
                "qty": qty,
                "price": price,
                "subtotal": price * qty,
            }
        )
    return lines
