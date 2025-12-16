# akumanopet/urls.py
from django.contrib import admin
from django.urls import path, include, re_path  # <--- Agregado re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.static import serve           # <--- Agregado serve

# Opcional: JWT para API
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
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
    path("fichas/",    include(("fichas.urls",    "fichas"),    namespace="fichas")),
    
    # API General (Router con todos los ViewSets)
    path("api/", include("akumanopet.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
    
    # Allauth
    path('accounts/', include('allauth.urls')),

    # === Password reset ===
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="cuentas/password_reset_form.html"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="cuentas/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="cuentas/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="cuentas/password_reset_complete.html"), name="password_reset_complete"),

    # =======================
    #         API (DRF)
    # =======================
    # Nota: Si "akumanopet.api_urls" ya incluye productos, esta línea podría ser redundante, 
    # pero la dejo por si tienes rutas extra específicas ahí.
    path("api/productos-extra/", include("productos.urls_api")), 

    # JWT para clientes externos
    path("api/auth/jwt/create/",  TokenObtainPairView.as_view(), name="jwt_create"),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view(),   name="jwt_refresh"),
]

# --- BLOQUE CRÍTICO PARA RENDER ---
# Esto permite ver las fotos aunque DEBUG=False.
# Se agrega a las rutas SIEMPRE, para forzar el servicio de archivos media.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]