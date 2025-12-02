from django.shortcuts import render, redirect
from django.http import HttpResponse

def lista(request):
    # TODO: traer reservas desde la BD
    reservas = []  # placeholder
    return render(request, "reserva/lista.html", {"reservas": reservas})

def crear(request):
    if request.method == "POST":
        # TODO: validar y guardar
        # ... guardar reserva ...
        return redirect("reserva:lista")
    return render(request, "reserva/crear.html")

def detalle(request, reserva_id: int):
    # TODO: obtener reserva por id
    reserva = {"id": reserva_id}  # placeholder
    return render(request, "reserva/detalle.html", {"reserva": reserva})

def editar(request, reserva_id: int):
    if request.method == "POST":
        # TODO: actualizar
        return redirect("reserva:detalle", reserva_id=reserva_id)
    # TODO: cargar datos iniciales
    reserva = {"id": reserva_id}
    return render(request, "reserva/editar.html", {"reserva": reserva})

def eliminar(request, reserva_id: int):
    if request.method == "POST":
        # TODO: eliminar
        return redirect("reserva:lista")
    # Confirmación simple
    return render(request, "reserva/eliminar.html", {"reserva_id": reserva_id})
