"""
Django settings for akumanopet project.
"""

from pathlib import Path
import os
from datetime import timedelta

# ⬇️ Si usas DATABASE_URL (Neon/Render), necesitamos dj_database_url
try:
    import dj_database_url  # pip install dj-database-url
except Exception:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Debug ---
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-pkkmlw+78(ye#9n8j(aue2=xnnmqi*f#n3w#)vo^y=8bcwbw5k"  # solo para desarrollo
)

# En local: DEBUG=True por defecto.
# En Render: define DEBUG=False en variables de entorno.
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# En local: permite localhost y 127.0.0.1.
# En Render: pisa esto con ALLOWED_HOSTS=tuapp.onrender.com
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# --- Apps ---
INSTALLED_APPS = [
    "jazzmin",

    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",

    # allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Apps del proyecto
    "cuentas",
    "clientes",
    "agenda",
    "productos",
    "ventas",
    "main",
    "carrito",
    "reserva",
    "fichas",

    # API / extras
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    # CORS primero (recomendado)
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "akumanopet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # si después haces carpeta templates global la agregas acá
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "carrito.context_processors.cart_context",
            ],
        },
    },
]

WSGI_APPLICATION = "akumanopet.wsgi.application"

# --- Base de datos ---
# Usa DATABASE_URL (Neon/Render) si existe; si no, SQLite local.
# Ejemplo .env:
# DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and dj_database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Validación de contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Hashers (Argon2 primero) ---
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# --- I18N / TZ ---
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# CSRF confiables: en local, localhost; en Render se pisa por env
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

# --- Auth redirects ---
LOGIN_URL = "/cuentas/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1  # requerido por django.contrib.sites

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# --- Jazzmin ---
JAZZMIN_SETTINGS = {
    "site_title": "Akuma no Pet – Admin",
    "site_header": "Akuma no Pet",
    "site_brand": "Akuma no Pet",
    "welcome_sign": "Bienvenido(a) 👋",
    "copyright": "© Akuma no Pet",
    "site_logo": "images/logo_transparente.png",
    "login_logo": "images/logo_transparente.png",
    "login_logo_dark": "images/logo_transparente.png",
    "site_icon": "images/favicon.ico",
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "auth"},
        {"app": "productos"},
    ],
    "show_ui_builder": False,
}
JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
    "brand_colour": "#5213a1",
    "accent": "#7C3AED",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    "footer_fixed": True,
    "navbar_fixed": True,
}

# =========================
#  API / DRF / JWT / CORS
# =========================

# CORS (en desarrollo, solo frontend local)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
}

# SimpleJWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Asegura que Django encuentre plantillas dentro de las apps (extra, aunque ya está arriba)
TEMPLATES[0]["APP_DIRS"] = True

# --- Email (SMTP, con defaults para local; en prod usa env) ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "akumanopet@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "xvml ksxa nsvz fcrv")
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "Akuma no Pet <akumanopet@gmail.com>"
)

# --- Transbank Integration ---
TRANSBANK_ENV = os.getenv("TRANSBANK_ENV", "integration")
TRANSBANK_COMMERCE_CODE = os.getenv("TRANSBANK_COMMERCE_CODE", "597055555532")
TRANSBANK_API_KEY_ID = os.getenv("TRANSBANK_API_KEY_ID", "597055555532")
TRANSBANK_API_KEY_SECRET = os.getenv(
    "TRANSBANK_API_KEY_SECRET",
    "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
)
_TIMEOUT = int(os.getenv("TRANSBANK_TIMEOUT", "15"))

# === Allauth / cuentas ===

# con qué se puede iniciar sesión:
# "username_email" = acepta usuario o correo
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

# obligar a tener correo
ACCOUNT_EMAIL_REQUIRED = True

# en desarrollo no mandamos correo de verificación todavía
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"

# pedimos a Google el correo y lo guardamos en User.email
SOCIALACCOUNT_QUERY_EMAIL = True

# permitimos que siga existiendo username (para no romper nada de Django Admin)
ACCOUNT_USERNAME_REQUIRED = True
SOCIALACCOUNT_LOGIN_ON_GET = True
