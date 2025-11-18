# cuentas/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    LoginConRemember,
    eliminar_mascota,
    enviar_codigo_password,
    perfil_usuario,
    registro,
)

app_name = "cuentas"

urlpatterns = [
    # Login / Logout
    path("login/",  LoginConRemember.as_view(),  name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Registro
    path("registro/", registro, name="registro"),
    path("perfil/", perfil_usuario, name="perfil"),
    path(
        "mis-mascotas/<int:pk>/eliminar/",
        eliminar_mascota,
        name="mascota_eliminar",
    ),
    path(
        "perfil/codigo-seguridad/",
        enviar_codigo_password,
        name="codigo_password",
    ),

    # Password reset (plantillas opcionales si las tienes)
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="cuentas/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="cuentas/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="cuentas/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="cuentas/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
