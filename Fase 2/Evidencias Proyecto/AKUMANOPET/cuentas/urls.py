from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import registro, LoginConRemember

app_name = "cuentas"

urlpatterns = [
    # usa tu plantilla actual de login
    path("login/", LoginConRemember.as_view(template_name="cuentas/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="cuentas:login"), name="logout"),
    path("registro/", registro, name="registro"),
]
