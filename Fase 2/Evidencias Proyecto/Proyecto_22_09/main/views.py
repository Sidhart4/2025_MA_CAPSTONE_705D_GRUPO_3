# main/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactoForm
from productos.models import Producto
from agenda.models import Servicio
from django.db.models import Sum, Q, Count

def home(request):
    mas_vendidos = (
        Producto.objects.filter(activo=True)
        .annotate(
            vendidos=Sum(
                "ventaitem__cantidad",
                filter=Q(ventaitem__venta__estado="PAGADA"),
            )
        )
        .order_by("-vendidos", "-creado")[:12]
    )

    if not mas_vendidos:
        mas_vendidos = (
            Producto.objects.filter(activo=True)
            .order_by("-etiqueta", "-creado")[:12]
        )

    servicios = (
        Servicio.objects.all()
        .annotate(reservas=Count("citas"))
        .order_by("-reservas", "nombre")[:6]
    )
    if not servicios:
        servicios = Servicio.objects.all().order_by("nombre")[:6]

    return render(
        request,
        "main/home.html",
        {
            "mas_vendidos": mas_vendidos,
            "servicios": servicios,
        },
    )

def contacto(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Aquí procesas (guardar/enviar email/etc.)
            messages.success(request, "¡Gracias! Recibimos tu mensaje y te contactaremos pronto.")
            return redirect("main:contacto")
        else:
            # Log de errores y respuesta 400 para que se note validación fallida
            print("ERRORES FORM:", form.errors.as_json())
            return render(request, "main/contacto.html", {"form": form}, status=400)

    # GET
    form = ContactoForm()
    return render(request, "main/contacto.html", {"form": form})
