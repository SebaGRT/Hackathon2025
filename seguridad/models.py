from django.db import models


# Create your models here.
class ReporteDeCampo(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    fecha_reporte = models.DateField(auto_now_add=True)
    foto_incidente = models.ImageField(upload_to="incidentes/")
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

    def __str__(self):
        return f"Reporte #{self.id_reporte} - Violacion: {self.check_estado_norma}"
