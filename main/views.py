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


def equipo(request):
    doctores = [
        {
            "iniciales": "GS",
            "nombre": "Gabriela Silva",
            "bio": "Dueña asociada y cliente. Lidera la visión de servicio y acompaña cada caso.",
            "tags": ["Coordinación", "Experiencia cliente", "Seguimiento"],
            "experiencia": "Referente principal para clientes",
            "turno": "Disponible en sede central",
            "avatar_class": "team-avatar--lila",
        },
        {
            "iniciales": "PS",
            "nombre": "Patricia Silva",
            "bio": "Dueña asociada y cliente. Custodia la calidad de las atenciones y del equipo.",
            "tags": ["Relación con clientes", "Calidad de servicio", "Supervisión"],
            "experiencia": "Contacto directo con familias",
            "turno": "Disponible en sede central",
            "avatar_class": "team-avatar--peach",
        },
    ]
    staff = [
        {
            "iniciales": "MR",
            "nombre": "Matías Ríos",
            "rol": "Coordinador de reservas y pagos",
            "descripcion": "Gestiona tu agenda, recordatorios y soporte en línea 24/7.",
        },
        {
            "iniciales": "VG",
            "nombre": "Valentina Gómez",
            "rol": "Enfermera veterinaria",
            "descripcion": "Acompaña cada procedimiento y monitorea la recuperación en casa.",
        },
    ]
    stats = [
        {"valor": "18+", "label": "Años combinados de experiencia"},
        {"valor": "4.9/5", "label": "Promedio de satisfacción"},
        {"valor": "600+", "label": "Pacientes atendidos al año"},
    ]
    return render(
        request,
        "main/equipo.html",
        {"doctores": doctores, "staff": staff, "stats": stats},
    )
def precios(request):
    servicios = (
        Servicio.objects.all()
        .annotate(reservas=Count("citas"))
        .order_by("-reservas", "precio")[:6]
    )
    planes = []
    for servicio in servicios:
        reservas = getattr(servicio, "reservas", 0) or 0
        precio_raw = getattr(servicio, "precio", 0) or 0
        valor_display = f"{precio_raw:,.0f}".replace(",", ".")
        planes.append(
            {
                "badge": "Popular" if len(planes) == 1 else None,
                "eyebrow": servicio.nombre,
                "titulo": servicio.nombre,
                "descripcion": servicio.descripcion or "Servicio disponible en Akuma no Pet.",
                "valor": valor_display,
                "simbolo": "$",
                "moneda": "CLP",
                "periodo": "por sesión",
                "features": [
                    f"Duración estimada: {getattr(servicio, 'duracion_min_default', 30)} min.",
                    f"{reservas} reservas realizadas",
                    "Recordatorios automáticos",
                ],
                "cta": "Reservar",
                "url": "agenda:reservar",
                "filled": len(planes) == 1,
            }
        )
    if not planes:
        planes = [
            {
                "badge": None,
                "eyebrow": "Consulta General",
                "titulo": "Consulta General",
                "descripcion": "Chequeo preventivo, anamnesis y plan de vacunas.",
                "valor": "19.990",
                "simbolo": "$",
                "moneda": "CLP",
                "periodo": "por sesión",
                "features": [
                    "Duración estimada: 30 min.",
                    "Recordatorios automáticos",
                    "Ficha clínica digital",
                ],
                "cta": "Reservar",
                "url": "agenda:reservar",
                "filled": False,
            }
        ]
    return render(request, "main/precios.html", {"planes": planes})
