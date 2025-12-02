# cuentas/views.py
import datetime as dt
import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from agenda.models import Cita
from .forms import MascotaFotoForm
from .models import MascotaPerfil
from fichas.models import FichaClinica


PASSWORD_CODE_SESSION_KEY = "perfil_password_code"
PASSWORD_CODE_TTL_SECONDS = 600  # 10 minutos
PASSWORD_CODE_COOLDOWN_SECONDS = 60


class LoginConRemember(LoginView):
    """Login que respeta el checkbox 'remember' para la duración de sesión."""

    template_name = "cuentas/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.request.POST.get("remember"):
            self.request.session.set_expiry(0)
        messages.success(
            self.request, _("¡Bienvenido/a! Has iniciado sesión correctamente.")
        )
        return response

    def form_invalid(self, form):
        username = (self.request.POST.get("username") or "").strip()
        password = (self.request.POST.get("password") or "").strip()

        if not username or not password:
            messages.error(self.request, _("Por favor completa email y contraseña."))
        else:
            messages.error(self.request, _("Usuario y/o contraseña incorrecto."))
        return super().form_invalid(form)

    def get_success_url(self):
        return self.get_redirect_url() or resolve_url(settings.LOGIN_REDIRECT_URL)


def registro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip().lower()
        pass1 = request.POST.get("password", "")
        pass2 = request.POST.get("password2", "")
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
            user = User.objects.create_user(
                username=email,
                email=email,
                password=pass1,
                first_name=nombre,
            )
        except IntegrityError:
            messages.error(request, "Ese email ya está registrado.")
            return render(request, "cuentas/registro.html")

        user = authenticate(request, username=email, password=pass1)
        if user:
            login(request, user)
            messages.success(
                request, _("Cuenta creada e inicio de sesión correcto.")
            )
            return redirect(
                request.GET.get("next") or resolve_url(settings.LOGIN_REDIRECT_URL)
            )

    return render(request, "cuentas/registro.html")


@login_required
def perfil_usuario(request):
    """Dashboard con info de usuario, citas y mascotas."""

    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "password":
            password_form = PasswordChangeForm(
                user=request.user, data=request.POST
            )
            submitted_code = (request.POST.get("security_code") or "").strip()
            stored_code = request.session.get(PASSWORD_CODE_SESSION_KEY)
            now_ts = time.time()
            code_error = None

            if not submitted_code:
                code_error = (
                    "Debes ingresar el código de seguridad que enviamos a tu correo."
                )
            elif not stored_code:
                code_error = (
                    "Debes solicitar un código de seguridad antes de guardar."
                )
            else:
                stored_ts = stored_code.get("ts", 0)
                if now_ts - stored_ts > PASSWORD_CODE_TTL_SECONDS:
                    code_error = "El código de seguridad expiró, solicita uno nuevo."
                elif submitted_code != stored_code.get("value"):
                    code_error = "El código de seguridad no coincide."

            form_valid = password_form.is_valid()

            if code_error:
                messages.error(request, code_error)
            elif form_valid:
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
                request.session.pop(PASSWORD_CODE_SESSION_KEY, None)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect("cuentas:perfil")
            else:
                messages.error(
                    request,
                    "Por favor corrige los errores del formulario de contraseña.",
                )
        elif action == "mascota_foto":
            pet_id = request.POST.get("pet_id")
            mascota = get_object_or_404(MascotaPerfil, pk=pet_id, usuario=request.user)
            foto_form = MascotaFotoForm(request.POST, request.FILES, instance=mascota)
            if foto_form.is_valid():
                foto_form.save()
                messages.success(request, "Informaci?n de la mascota actualizada.")
                return redirect("cuentas:perfil")
            messages.error(request, "Revisa los datos enviados.")
        else:
            messages.error(request, "Acción no soportada.")

    mascotas = (
        request.user.mascotas_perfil.all()
        .order_by("nombre", "-creada")
    )

    citas = (
        Cita.objects.filter(cliente=request.user)
        .select_related("profesional", "servicio")
        .order_by("fecha", "hora")
    )

    ahora = timezone.now()
    tz = timezone.get_current_timezone()
    citas_pendientes = []
    citas_pasadas = []

    for cita in citas:
        inicio = dt.datetime.combine(cita.fecha, cita.hora)
        if timezone.is_aware(ahora):
            inicio = timezone.make_aware(inicio, tz)
        target = citas_pendientes if inicio >= ahora else citas_pasadas
        target.append({"cita": cita, "inicio": inicio})

    fichas = (
        FichaClinica.objects.filter(cliente=request.user)
        .select_related("mascota", "profesional")
        .order_by("-fecha", "-created_at")
    )

    context = {
        "mascotas": mascotas,
        "password_form": password_form,
        "citas_pendientes": citas_pendientes,
        "citas_pasadas": citas_pasadas,
        "fichas": fichas,
    }
    return render(request, "cuentas/perfil.html", context)


@login_required
@require_POST
def eliminar_mascota(request, pk: int):
    mascota = get_object_or_404(MascotaPerfil, pk=pk, usuario=request.user)
    nombre = mascota.nombre
    mascota.delete()
    messages.success(request, f"{nombre} se eliminó de tu perfil.")
    return redirect("cuentas:perfil")


@login_required
@require_POST
def enviar_codigo_password(request):
    """Genera y envía un código de seguridad para actualizar la contraseña."""

    email = (request.user.email or "").strip()
    if not email:
        return JsonResponse(
            {"ok": False, "message": "No tienes un correo asociado para recibir el código."},
            status=400,
        )

    now_ts = time.time()
    existing = request.session.get(PASSWORD_CODE_SESSION_KEY)
    if existing:
        elapsed = now_ts - existing.get("ts", 0)
        if elapsed < PASSWORD_CODE_COOLDOWN_SECONDS:
            wait = int(PASSWORD_CODE_COOLDOWN_SECONDS - elapsed)
            return JsonResponse(
                {
                    "ok": False,
                    "message": f"Debes esperar {wait} s antes de solicitar un nuevo código.",
                    "retry_in": wait,
                },
                status=429,
            )

    code = f"{secrets.randbelow(1_000_000):06d}"
    request.session[PASSWORD_CODE_SESSION_KEY] = {"value": code, "ts": now_ts}

    subject = "Código de seguridad - Akuma no Pet"
    saludo = request.user.first_name or request.user.username or "Cliente"
    body = (
        f"Hola {saludo},\n\n"
        f"Tu código de seguridad para actualizar la contraseña es: {code}\n"
        "Este código vence en 10 minutos. Si tú no solicitaste este cambio, ignora este mensaje.\n\n"
        "Equipo Akuma no Pet"
    )

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
    except Exception:
        return JsonResponse(
            {"ok": False, "message": "No pudimos enviar el código. Inténtalo más tarde."},
            status=500,
        )

    return JsonResponse(
        {"ok": True, "message": f"Enviamos un código a {email}."}
    )
