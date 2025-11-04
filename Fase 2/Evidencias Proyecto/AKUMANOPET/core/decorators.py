# core/decorators.py
from django.contrib.auth.decorators import user_passes_test

def is_veterinario(user):
    return user.is_authenticated and user.groups.filter(name="veterinario").exists()

veterinario_required = user_passes_test(is_veterinario, login_url="cuentas:login")
