# main/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactoForm
def home(request):
    return render(request, "main/home.html")

def contacto(request):
    # si luego quieres procesar POST, aquí lo manejas
    return render(request, "main/contacto.html")



def contacto(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Aquí harías lo que quieras (guardar, enviar email, etc.)
            messages.success(request, "¡Gracias! Recibimos tu mensaje y te contactaremos pronto.")
            return redirect("main:contacto")  # o a una página de gracias
        else:
            # Muestra los errores en la consola del server
            print("ERRORES FORM:", form.errors.as_json())
            # Devuelve 400 para que se note que el POST falló por validación
            return render(request, "main/contacto.html", {"form": form}, status=400)

    # GET
    form = ContactoForm()
    return render(request, "main/contacto.html", {"form": form})