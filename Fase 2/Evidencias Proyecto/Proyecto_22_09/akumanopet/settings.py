"""
Django settings for akumanopet project.
"""

from pathlib import Path
import os
from datetime import timedelta

# ⬇️ Si usas DATABASE_URL (Neon), necesitamos dj_database_url
try:
    import dj_database_url  # pip install dj-database-url
except Exception:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Debug ---
SECRET_KEY = 'django-insecure-pkkmlw+78(ye#9n8j(aue2=xnnmqi*f#n3w#)vo^y=8bcwbw5k'
DEBUG = True
ALLOWED_HOSTS = []  # agrega dominios en prod (p.ej. ['tu-dominio.com'])

# --- Apps ---
INSTALLED_APPS = [
    'jazzmin',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',  # <--- ahora con coma ✅

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Apps del proyecto
    'cuentas',
    'clientes',
    'agenda',
    'productos',
    'ventas',
    'main',
    'carrito',
    'reserva',
    'fichas',

    # API / extras
    'rest_framework',
    'corsheaders',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # <- debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',  # (queda duplicado pero es inofensivo)
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'akumanopet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'carrito.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'akumanopet.wsgi.application'

# --- Base de datos ---
# Usa DATABASE_URL (Neon) si existe; si no, SQLite local.
# Ejemplo .env:
# DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL and dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,   # Neon exige SSL
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- Validación de contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Hashers (Argon2 primero) ---
# Requiere: pip install argon2-cffi
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # recomendado
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

# --- I18N / TZ ---
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- Email (desarrollo) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'm.galarce@duocuc.cl'

# --- Auth redirects ---
LOGIN_URL = '/cuentas/login/'
LOGIN_REDIRECT_URL = 'productos:lista'
LOGOUT_REDIRECT_URL = 'cuentas:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1  # requerido por django.contrib.sites

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",            # auth normal de Django
    "allauth.account.auth_backends.AuthenticationBackend",  # allauth
]

LOGIN_REDIRECT_URL = "/"      # a dónde mandar al usuario después de logearse
LOGOUT_REDIRECT_URL = "/"     # a dónde mandarlo al salir
# --- Jazzmin ---
JAZZMIN_SETTINGS = {
    'site_title': 'Akuma no Pet – Admin',
    'site_header': 'Akuma no Pet',
    'site_brand': 'Akuma no Pet',
    'welcome_sign': 'Bienvenido(a) 👋',
    'copyright': '© Akuma no Pet',
    'site_logo': 'images/logo_transparente.png',
    'login_logo': 'images/logo_transparente.png',
    'login_logo_dark': 'images/logo_transparente.png',
    'site_icon': 'images/favicon.ico',
    'topmenu_links': [
        {'name': 'Inicio', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'app': 'auth'},
        {'app': 'productos'},
    ],
    'show_ui_builder': False,
}
JAZZMIN_UI_TWEAKS = {
    'theme': 'cosmo',
    'brand_colour': '#5213a1',
    'accent': '#7C3AED',
    'navbar': 'navbar-dark',
    'sidebar': 'sidebar-dark-primary',
    'footer_fixed': True,
    'navbar_fixed': True,
}

# =========================
#  API / DRF / JWT / CORS
# =========================

# CORS (en desarrollo, permite todo; en producción define dominios)
CORS_ALLOW_ALL_ORIGINS = False  
# Alternativa recomendada en prod:
CORS_ALLOWED_ORIGINS = [
     "http://localhost:5173",
 ]

# Si vas a enviar cookies/credenciales cross-site (no necesario con JWT por header):
# CORS_ALLOW_CREDENTIALS = True

# CSRF confiables (si usas cookies y dominios externos)
# CSRF_TRUSTED_ORIGINS = ["https://tu-frontend.com"]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
         'rest_framework.authentication.SessionAuthentication',  # opcional (admin / browsable)
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# SimpleJWT (ajusta tiempos a tu gusto)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Asegura que Django encuentre plantillas dentro de las apps
TEMPLATES[0]["APP_DIRS"] = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "akumanopet@gmail.com"
EMAIL_HOST_PASSWORD = "xvml ksxa nsvz fcrv"
DEFAULT_FROM_EMAIL = "Akuma no Pet <akumanopet@gmail.com>"

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