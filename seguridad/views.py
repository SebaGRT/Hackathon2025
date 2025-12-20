# Create your views here.
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import ReporteDeCampo
from .servicio_ia import analisis_fotos


def home(request):
    return render(request, "seguridad/home.html")


NORMAS_VIGENTES_TEXTO = """
1. NORMA EPP BÁSICO: Todo personal en obra debe utilizar casco de seguridad, lentes de protección y calzado de seguridad en todo momento.
2. NORMA TRABAJO EN ALTURA: Cualquier trabajo sobre 1.8 metros requiere uso obligatorio de arnés de seguridad anclado a un punto fijo certificado.
3. NORMA ORDEN Y LIMPIEZA: Las zonas de tránsito deben estar libres de escombros, cables sueltos o materiales que puedan causar tropiezos.
"""


def crear_reporte(request):
    if request.method == "POST" and request.FILES.get("imagen_terreno"):
        # 1. Guardar la imagen cruda primero
        nuevo_reporte = ReporteDeCampo()
        nuevo_reporte.foto_incidente = request.FILES["imagen_terreno"]
        nuevo_reporte.save()  # Al guardar, Django genera la ruta física del archivo

        # 2. Llamar a la IA pasando la ruta de la foto y las normas
        print(f"Enviando a IA imagen: {nuevo_reporte.foto_incidente.path}")

        resultado_ia = analisis_fotos(
            nuevo_reporte.foto_incidente.path, NORMAS_VIGENTES_TEXTO
        )

        # 3. Actualizar el reporte con la inteligencia obtenida
        nuevo_reporte.image_check = True
        nuevo_reporte.check_estado_norma = resultado_ia.get(
            "violacion_detectada", False
        )
        nuevo_reporte.norma_infringida = resultado_ia.get("norma_infringida_titulo", "")
        nuevo_reporte.descripcion = resultado_ia.get(
            "descripcion_detallada", "Sin descripción disponible"
        )
        nuevo_reporte.clasificacion = resultado_ia.get("severidad_sugerida", "BAJA")

        nuevo_reporte.save()

        # Redirigir al dashboard o página de éxito (ajusta la URL según tu proyecto)
        return redirect("home")

    return render(request, "seguridad/reporte_camara.html")


def reporte_emergencia(request):
    """Vista para reportes de emergencia"""
    if request.method == "POST":
        # Crear un reporte de emergencia con alta prioridad
        nuevo_reporte = ReporteDeCampo()

        # Si hay imagen, procesarla
        if request.FILES.get("imagen_emergencia"):
            nuevo_reporte.foto_incidente = request.FILES["imagen_emergencia"]

        # Marcar como emergencia (clasificación ALTA)
        nuevo_reporte.clasificacion = "ALTA"
        nuevo_reporte.check_estado_norma = True
        nuevo_reporte.norma_infringida = "EMERGENCIA - Reporte Prioritario"
        nuevo_reporte.descripcion = request.POST.get(
            "descripcion_emergencia", "Reporte de emergencia sin descripción"
        )
        nuevo_reporte.image_check = True

        nuevo_reporte.save()

        # Aquí se podría agregar:
        # - Envío de emails a supervisores
        # - Notificaciones SMS
        # - Alertas al sistema de gestión

        return redirect("home")

    return render(request, "seguridad/emergencia.html")
