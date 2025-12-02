# core/decorators.py
from functools import wraps
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse


def is_veterinario(user):
    return user.is_authenticated and user.groups.filter(name="veterinario").exists()


def _resolve_url(name_or_path: str) -> str:
    try:
        return reverse(name_or_path)
    except NoReverseMatch:
        return name_or_path


def staff_required(view_func=None, *, login_url="cuentas:login", deny_url="main:home", allow_groups=None):
    """
    Decorador reutilizable para vistas internas/admin.
    - Obliga a iniciar sesión.
    - Verifica que el usuario sea staff o pertenezca a un grupo permitido.
    - Muestra alertas con el framework de mensajes al redirigir.
    """
    allow_groups = allow_groups or []

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
                login_path = _resolve_url(login_url)
                query = urlencode({"next": request.get_full_path()})
                joiner = "&" if "?" in login_path else "?"
                return redirect(f"{login_path}{joiner}{query}")

            if user.is_staff or (allow_groups and user.groups.filter(name__in=allow_groups).exists()):
                return func(request, *args, **kwargs)

            messages.error(request, "No tienes permisos para ingresar al panel administrativo.")
            return redirect(_resolve_url(deny_url))

        return wrapper

    if view_func is not None:
        return decorator(view_func)
    return decorator


veterinario_required = user_passes_test(is_veterinario, login_url="cuentas:login")
