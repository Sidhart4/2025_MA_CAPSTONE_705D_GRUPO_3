from django.shortcuts import render

from django.http import HttpResponse

def lista(request):   return HttpResponse("Ventas: listado")
def crear(request):   return HttpResponse("Ventas: crear")
def detalle(request, pk): return HttpResponse(f"Ventas: detalle {pk}")
