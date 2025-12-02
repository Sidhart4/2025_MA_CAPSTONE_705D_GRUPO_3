from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.decorators import staff_required
from .forms import FichaClinicaForm, MascotaPerfilStaffForm
from .models import FichaClinica


@staff_required
def fichas_lista(request):
    q = (request.GET.get("q") or "").strip()
    fichas = (
        FichaClinica.objects.select_related("cliente", "mascota", "profesional")
        .order_by("-fecha", "-created_at")
    )
    if q:
        fichas = fichas.filter(
            Q(mascota__nombre__icontains=q)
            | Q(cliente__first_name__icontains=q)
            | Q(cliente__username__icontains=q)
            | Q(cliente__email__icontains=q)
        )
    return render(request, "fichas/lista.html", {"fichas": fichas, "q": q})


@staff_required
def ficha_crear(request):
    form = FichaClinicaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ficha creada correctamente.")
        return redirect("fichas:lista")
    return render(request, "fichas/form.html", {"form": form, "titulo": "Nueva ficha"})


@staff_required
def ficha_editar(request, pk: int):
    ficha = get_object_or_404(
        FichaClinica.objects.select_related("cliente", "mascota", "profesional"), pk=pk
    )
    form = FichaClinicaForm(request.POST or None, instance=ficha)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ficha actualizada.")
        return redirect("fichas:lista")
    return render(
        request, "fichas/form.html", {"form": form, "titulo": f"Editar ficha #{ficha.id}"}
    )


@staff_required
def mascota_crear(request):
    form = MascotaPerfilStaffForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        mascota = form.save()
        messages.success(request, f"Mascota {mascota.nombre} creada para {mascota.usuario}.")
        return redirect("fichas:lista")
    return render(request, "fichas/mascota_form.html", {"form": form})
