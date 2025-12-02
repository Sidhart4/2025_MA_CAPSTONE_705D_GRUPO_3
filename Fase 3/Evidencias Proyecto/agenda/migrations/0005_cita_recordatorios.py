from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agenda", "0004_propietario_mascota"),
    ]

    operations = [
        migrations.AddField(
            model_name="cita",
            name="email_contacto",
            field=models.EmailField(blank=True, default="", max_length=254),
        ),
        migrations.AddField(
            model_name="cita",
            name="nombre_cliente",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="cita",
            name="recordatorio_mail_enviado",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cita",
            name="recordatorio_wa_enviado",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cita",
            name="recuerda_mail",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="cita",
            name="recuerda_wa",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cita",
            name="whatsapp_contacto",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
    ]
