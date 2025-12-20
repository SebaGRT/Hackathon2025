from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def get_current_date():
    return date.today()


# Create your models here.
class ReporteDeCampo(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    fecha_reporte = models.DateField(default=get_current_date)
    foto_incidente = models.ImageField(upload_to="incidentes/", max_length=500)
    image_check = models.BooleanField(default=False)
    check_estado_norma = models.BooleanField(
        default=False, verbose_name="¿Hay una norma incumplida?"
    )
    norma_infringida = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    clasificacion = models.CharField(
        max_length=20,
        choices=[
            ("BAJA", "Baja"),
            ("MEDIA", "Media"),
            ("ALTA", "Alta"),
        ],
        default="BAJA",
    )

    # Campos para equipos de protección personal
    casco = models.IntegerField(default=0, verbose_name="Cascos faltantes")
    chaleco = models.IntegerField(default=0, verbose_name="Chalecos faltantes")
    guantes = models.IntegerField(default=0, verbose_name="Guantes faltantes")
    botas = models.IntegerField(default=0, verbose_name="Botas faltantes")

    def __str__(self):
        return f"Reporte #{self.id_reporte} - Violacion: {self.check_estado_norma}"


class Formulario(models.Model):
    id_formulario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, default="Formulario sin nombre")
    categoria = models.CharField(
        max_length=20,
        choices=[("DIARIO", "Diario"), ("PARTICULAR", "Particular")],
        default="PARTICULAR",
    )
    archivo = models.FileField(upload_to="formularios/", max_length=500)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)
    # Guardamos el JSON crudo que devuelve la IA
    resultado_json = models.JSONField(blank=True, null=True)
    # Resumen o texto simple para mostrar rápido
    resumen = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Formulario {self.nombre} ({self.fecha_subida})"


class RegistroFormulario(models.Model):
    id_registro = models.AutoField(primary_key=True)
    formulario = models.ForeignKey(
        Formulario, on_delete=models.CASCADE, related_name="registros"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    datos_llenados = models.JSONField()
    responsable = models.CharField(max_length=200, default="Usuario")

    def __str__(self):
        return f"Registro {self.id_registro} - {self.formulario.nombre}"


class PerfilUsuario(models.Model):
    ROLES = [
        ("TRABAJADOR", "Trabajador"),
        ("SUPERVISOR", "Supervisor"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=ROLES, default="TRABAJADOR")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un usuario"""
    if created:
        # Si el usuario es staff, asignar rol de Supervisor
        rol = "SUPERVISOR" if instance.is_staff else "TRABAJADOR"
        PerfilUsuario.objects.create(user=instance, rol=rol)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil cuando se actualiza el usuario"""
    if hasattr(instance, "perfil"):
        instance.perfil.save()
