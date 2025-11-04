from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.db import IntegrityError

class LoginConRemember(LoginView):
    """Respeta tu checkbox 'remember' para la duración de sesión."""
    def form_valid(self, form):
        resp = super().form_valid(form)
        if not self.request.POST.get("remember"):
            self.request.session.set_expiry(0)  # expira al cerrar el navegador
        return resp

def registro(request):
    if request.method == "POST":
        nombre    = request.POST.get("nombre", "").strip()
        email     = request.POST.get("email", "").strip().lower()
        pass1     = request.POST.get("password", "")
        pass2     = request.POST.get("password2", "")
        acepto    = request.POST.get("acepto")

        errores = []
        if not nombre: errores.append("Debes ingresar tu nombre.")
        if not email:  errores.append("Debes ingresar un email.")
        if pass1 != pass2: errores.append("Las contraseñas no coinciden.")
        if not acepto: errores.append("Debes aceptar los términos.")

        if errores:
            return render(request, "cuentas/registro.html", {"errores": errores})

        try:
            # Usamos el EMAIL como username para que el login funcione con tu input
            user = User.objects.create_user(
                username=email,  # <- importante
                email=email,
                password=pass1,
                first_name=nombre
            )
        except IntegrityError:
            return render(request, "cuentas/registro.html", {"errores": ["Ese email ya está registrado."]})

        # Auto-login tras registrarse
        user = authenticate(request, username=email, password=pass1)
        if user:
            login(request, user)
            return redirect(request.GET.get("next") or "productos:lista")  # cambia a la ruta que prefieras

    # GET
    return render(request, "cuentas/registro.html")
