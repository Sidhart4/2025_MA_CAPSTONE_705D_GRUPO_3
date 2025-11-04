# akumanopet/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Opcional: JWT para API (requiere djangorestframework-simplejwt)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # /api/auth/jwt/create/
    TokenRefreshView,      # /api/auth/jwt/refresh/
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home / páginas principales
    path("", include(("main.urls", "main"), namespace="main")),

    # Apps funcionales
    path("carrito/",   include(("carrito.urls",   "carrito"),   namespace="carrito")),
    path("cuentas/",   include(("cuentas.urls",   "cuentas"),   namespace="cuentas")),
    path("clientes/",  include(("clientes.urls",  "clientes"),  namespace="clientes")),
    path("agenda/",    include(("agenda.urls",    "agenda"),    namespace="agenda")),
    path("productos/", include(("productos.urls", "productos"), namespace="productos")),
    path("ventas/",    include(("ventas.urls",    "ventas"),    namespace="ventas")),
    path("reserva/",   include(("reserva.urls",   "reserva"),   namespace="reserva")),
    path("api/", include("akumanopet.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
    path('accounts/', include('allauth.urls')),
    # === Password reset (coincide con los nombres que usa tu template) ===
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="cuentas/password_reset_form.html"
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
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

    # =======================
    #         API (DRF)
    # =======================
    # Router de productos (crea /api/productos/...)
    path("api/", include("productos.urls_api")),

    # JWT para clientes externos (React/Electron)
    path("api/auth/jwt/create/",  TokenObtainPairView.as_view(), name="jwt_create"),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view(),   name="jwt_refresh"),

    # (Opcional) si más adelante agregas otras apps API:
    # path("api/clientes/", include("clientes.urls_api")),
    # path("api/agenda/", include("agenda.urls_api")),
]

# Archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
