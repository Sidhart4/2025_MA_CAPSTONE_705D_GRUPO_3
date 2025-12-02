# core/management/commands/seed_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Crea grupos y asigna permisos base (Clientes, Veterinarios)."

    def handle(self, *args, **options):
        clientes, _ = Group.objects.get_or_create(name="Clientes")
        veterinarios, _ = Group.objects.get_or_create(name="Veterinarios")

        from agenda.models import Cita
        from productos.models import Producto

        # Permisos de Cita → Veterinarios (add/change/delete/view)
        ct_cita = ContentType.objects.get_for_model(Cita)
        for p in Permission.objects.filter(content_type=ct_cita):
            veterinarios.permissions.add(p)

        # Permisos de Producto → todos para Veterinarios
        ct_prod = ContentType.objects.get_for_model(Producto)
        for p in Permission.objects.filter(content_type=ct_prod):
            veterinarios.permissions.add(p)

        # Clientes solo pueden ver productos
        try:
            view_producto = Permission.objects.get(
                content_type=ct_prod, codename="view_producto"
            )
            clientes.permissions.add(view_producto)
        except Permission.DoesNotExist:
            self.stdout.write(self.style.WARNING("Permiso view_producto no encontrado"))

        self.stdout.write(self.style.SUCCESS("Grupos y permisos creados/asignados."))
