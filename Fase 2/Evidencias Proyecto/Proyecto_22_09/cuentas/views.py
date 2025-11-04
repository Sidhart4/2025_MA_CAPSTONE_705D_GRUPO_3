# cuentas/views.py
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, resolve_url  # <- resolve_url AQUÍ
from django.conf import settings

# 👇 Mensajes y traducción
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class LoginConRemember(LoginView):
    """
    Login que respeta el checkbox 'remember' para la duración de sesión.
    Usa tu template existente: cuentas/login.html
    """
    template_name = "cuentas/login.html"
    redirect_authenticated_user = True  # si ya está logueado, redirige

    def form_valid(self, form):
        response = super().form_valid(form)
        # Si NO marcó "recordarme", la sesión expira al cerrar el navegador
        if not self.request.POST.get("remember"):
            self.request.session.set_expiry(0)
        # Mensaje opcional de bienvenida
        messages.success(self.request, _("¡Bienvenido/a! Has iniciado sesión correctamente."))
        return response

    # Mensajes claros según el caso
    def form_invalid(self, form):
        username = (self.request.POST.get("username") or "").strip()
        password = (self.request.POST.get("password") or "").strip()

        if not username or not password:
            messages.error(self.request, _("Por favor completa email y contraseña."))
        else:
            messages.error(self.request, _("Usuario y/o contraseña incorrecto."))
        return super().form_invalid(form)

    def get_success_url(self):
        # Respeta ?next=..., si no, resuelve el nombre configurado a URL segura
        return self.get_redirect_url() or resolve_url(settings.LOGIN_REDIRECT_URL)


def registro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email  = request.POST.get("email", "").strip().lower()
        pass1  = request.POST.get("password", "")
        pass2  = request.POST.get("password2", "")
        acepto = request.POST.get("acepto")

        errores = []
        if not nombre:
            errores.append("Debes ingresar tu nombre.")
        if not email:
            errores.append("Debes ingresar un email.")
        if pass1 != pass2:
            errores.append("Las contraseñas no coinciden.")
        if not acepto:
            errores.append("Debes aceptar los términos.")

        if errores:
            for e in errores:
                messages.error(request, e)
            return render(request, "cuentas/registro.html")

        try:
            # Usamos el EMAIL como username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=pass1,
                first_name=nombre,
            )
        except IntegrityError:
            messages.error(request, "Ese email ya está registrado.")
            return render(request, "cuentas/registro.html")

        # Auto-login tras registrarse
        user = authenticate(request, username=email, password=pass1)
        if user:
            login(request, user)
            messages.success(request, _("Cuenta creada e inicio de sesión correcto."))
            # Redirige seguro (respeta ?next=..., si no, LOGIN_REDIRECT_URL)
            return redirect(request.GET.get("next") or resolve_url(settings.LOGIN_REDIRECT_URL))

    # GET
    return render(request, "cuentas/registro.html")
