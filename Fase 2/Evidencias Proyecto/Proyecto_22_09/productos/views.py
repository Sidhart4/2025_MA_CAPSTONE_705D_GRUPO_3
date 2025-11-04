from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, IntegerField, Value
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test, login_required

from .models import Producto
from .forms import ProductoForm

# --- Decorador: solo usuarios activos y staff ---
def staff_required(view_func):
    decorated = login_required(
        user_passes_test(
            lambda u: u.is_active and u.is_staff,
            login_url="cuentas:login"  # ajusta si tu nombre de url es distinto
        )(view_func)
    )
    return decorated



def lista(request):
    qs = Producto.objects.filter(activo=True)

    # --- Parámetros GET
    q          = request.GET.get("q", "").strip()
    cats       = request.GET.getlist("cat")
    pets       = request.GET.getlist("pet")
    brands     = request.GET.getlist("brand")
    minp       = request.GET.get("min")
    maxp       = request.GET.get("max")
    in_stock   = request.GET.get("inStock") == "1"
    only_deals = request.GET.get("onlyDeals") == "1"
    rating_min = request.GET.get("rating", "0")
    sort       = request.GET.get("sort", "relevance")
    size       = int(request.GET.get("size", "12"))

    # --- Filtros
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    if cats:
        qs = qs.filter(categoria__in=cats)
    if pets:
        qs = qs.filter(tipo_mascota__in=pets)
    if brands:
        qs = qs.filter(marca__in=brands)
    if minp:
        qs = qs.filter(precio__gte=minp)
    if maxp:
        qs = qs.filter(precio__lte=maxp)
    if in_stock:
        qs = qs.filter(stock__gt=0)
    if only_deals:
        qs = qs.filter(precio_anterior__isnull=False)
    if rating_min.isdigit() and int(rating_min) > 0:
        qs = qs.filter(valoracion__gte=rating_min)

    # --- Anotación oferta
    qs = qs.annotate(
        tiene_oferta=Case(
            When(precio_anterior__isnull=False, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    )

    # --- Orden
    ordering_map = {
        "relevance": ("-tiene_oferta", "-valoracion", "-creado"),
        "priceAsc": "precio",
        "priceDesc": "-precio",
        "rating": "-valoracion",
        "new": "-creado",
    }
    ordering = ordering_map.get(sort, ordering_map["relevance"])
    qs = qs.order_by(*ordering) if isinstance(ordering, tuple) else qs.order_by(ordering)

    # --- Paginación
    paginator = Paginator(qs, size)
    page_obj = paginator.get_page(request.GET.get("page"))

    # --- Datos para filtros
    all_cats   = list(Producto.objects.values_list("categoria", flat=True).distinct().order_by("categoria"))
    all_brands = list(Producto.objects.values_list("marca", flat=True).distinct().order_by("marca"))

    context = {
        "page_obj": page_obj,
        "total": qs.count(),
        "q": q,
        "sort": sort,
        "size": size,
        "all_cats": all_cats,
        "all_brands": all_brands,
        "cats": cats,
        "pets": pets,
        "brands": brands,
        "minp": minp,
        "maxp": maxp,
        "in_stock": in_stock,
        "only_deals": only_deals,
        "rating_min": rating_min,
        "params": request.GET.copy(),
        "form_crear": ProductoForm(),
    }
    return render(request, "productos/lista.html", context)


@staff_required
def crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado con éxito.")
            return redirect("productos:lista")
    else:
        form = ProductoForm()
    return render(request, "productos/form_page.html", {"form": form, "titulo": "Nuevo producto"})


@staff_required
def editar(request, pk):
    prod = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado.")
            return redirect("productos:lista")
    else:
        form = ProductoForm(instance=prod)
    return render(request, "productos/form_page.html", {"form": form, "titulo": "Editar producto"})


@staff_required
def borrar(request, pk):
    prod = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        prod.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("productos:lista")
    return render(request, "productos/confirm_delete.html", {"obj": prod})
