from django.http import HttpResponse

from core.decorators import staff_required


@staff_required
def lista(request):
    return HttpResponse("Clientes: listado")


@staff_required
def crear(request):
    return HttpResponse("Clientes: crear")


@staff_required
def detalle(request, pk):
    return HttpResponse(f"Clientes: detalle {pk}")


@staff_required
def editar(request, pk):
    return HttpResponse(f"Clientes: editar {pk}")


@staff_required
def eliminar(request, pk):
    return HttpResponse(f"Clientes: eliminar {pk}")
