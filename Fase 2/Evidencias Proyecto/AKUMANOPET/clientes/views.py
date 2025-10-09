from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def lista(request):   return HttpResponse("Clientes: listado")
def crear(request):   return HttpResponse("Clientes: crear")
def detalle(request, pk): return HttpResponse(f"Clientes: detalle {pk}")
def editar(request, pk):  return HttpResponse(f"Clientes: editar {pk}")
def eliminar(request, pk):return HttpResponse(f"Clientes: eliminar {pk}")
