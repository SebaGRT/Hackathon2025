# Create your views here.
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.text import slugify

from .models import Formulario, RegistroFormulario, ReporteDeCampo
from .servicio_ia import analisis_formulario, analisis_fotos


def home(request):
    return render(request, "seguridad/home.html")


NORMAS_VIGENTES_TEXTO = """
1. NORMA EPP (EQUIPO DE PROTECCIÓN PERSONAL) [Ley 16.744 / DS 594]
- Obligatorio: Todos los trabajadores deben usar casco de seguridad, calzado de seguridad y chaleco reflectante (alta visibilidad) en zonas de tránsito.
- Específico: Si hay proyección de partículas (uso de herramientas de corte/pulido), deben usar lentes de seguridad.
- Guantes: Uso obligatorio para manipulación de materiales.
- Violación Visual: Trabajador sin casco, sin chaleco o usando zapatillas deportivas.

2. NORMA TRABAJO EN ALTURA [Circular 2345 / Guía ISP]
- Altura > 1.8 metros: Uso obligatorio de arnés de seguridad de cuerpo completo anclado a un punto fijo (cuerda de vida).
- Andamios: Deben tener barandas perimetrales completas (superior e intermedia), superficies de trabajo completas (sin huecos) y ruedas bloqueadas o bases fijas.
- Violación Visual: Trabajador en techo o borde de losa sin arnés conectado. Andamio incompleto o improvisado sobre tambores.

3. NORMA RIESGO ELÉCTRICO [Pliego Técnico RIC / DS 92]
- Tableros: Todos los tableros eléctricos provisionales deben tener tapa cerrada y señalética de advertencia.
- Cables: Prohibidos los cables con conductores expuestos (cobre a la vista) o uniones con cinta aislante doméstica. Los cables deben estar elevados o protegidos, no tirados en zonas inundadas o de tránsito vehicular.
- Violación Visual: Tablero abierto con cables colgando. Extensiones eléctricas en mal estado en el suelo.

4. NORMA ORDEN Y ASEO (HOUSEKEEPING) [DS 594 Art. 11]
- Pasillos: Las vías de evacuación y tránsito deben estar libres de escombros, maderas con clavos o materiales acopiados.
- Acopio: Los materiales deben estar ordenados y delimitados.
- Violación Visual: Escombros bloqueando pasillos. Maderas con clavos tiradas. Basura acumulada fuera de zonas de acopio.

5. NORMA EXCAVACIONES Y PERÍMETROS [NCh 349]
- Bordes: Toda excavación o borde de losa abierta debe tener barandas rígidas o señalización clara de advertencia para evitar caídas.
- Señalética: Debe existir señalización de peligro en zonas de izaje o movimiento de maquinaria.
- Violación Visual: Pozo o zanja sin delimitación. Falta de señalética en zonas de riesgo.

6. NORMA GESTIÓN DE INCENDIOS Y EMERGENCIAS [DS 594]
- Extintores: Deben estar visibles, señalizados, colgados y despejados (no en el suelo ni bloqueados por materiales).
- Violación Visual: Extintor en el suelo, bloqueado por cajas o no visible.
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

        # Capturar tipo de emergencia
        tipo_emergencia = request.POST.get("tipo_emergencia", "otro")

        # Capturar descripción de la emergencia
        descripcion_emergencia = request.POST.get(
            "descripcion_emergencia", "Reporte de emergencia sin descripción"
        )

        # Si hay imagen, procesarla
        if request.FILES.get("imagen_emergencia"):
            nuevo_reporte.foto_incidente = request.FILES["imagen_emergencia"]
            nuevo_reporte.image_check = True
        else:
            nuevo_reporte.image_check = False

        # Construir descripción completa con tipo de emergencia
        descripcion_completa = (
            f"[EMERGENCIA - {tipo_emergencia.upper()}]\n\n{descripcion_emergencia}"
        )

        # Marcar como emergencia (clasificación ALTA)
        nuevo_reporte.clasificacion = "ALTA"
        nuevo_reporte.check_estado_norma = True
        nuevo_reporte.norma_infringida = f"EMERGENCIA - {tipo_emergencia.upper()}"
        nuevo_reporte.descripcion = descripcion_completa

        nuevo_reporte.save()

        # Aquí se podría agregar:
        # - Envío de emails a supervisores
        # - Notificaciones SMS
        # - Alertas al sistema de gestión

        return redirect("home")

    return render(request, "seguridad/emergencia.html")


def lista_formularios(request):
    formularios = Formulario.objects.all().order_by("-fecha_subida")
    return render(request, "seguridad/lista_formularios.html", {"formularios": formularios})


def subir_formulario(request):
    if request.method == "POST" and request.FILES.get("archivo_formulario"):
        nuevo_form = Formulario()
        nuevo_form.nombre = request.POST.get("nombre", "Formulario sin nombre")
        nuevo_form.archivo = request.FILES["archivo_formulario"]
        nuevo_form.save()

        # Procesar con IA
        try:
            resultado = analisis_formulario(nuevo_form.archivo.path)
            nuevo_form.resultado_json = resultado
            nuevo_form.resumen = resultado.get("resumen", "Sin resumen disponible")
            nuevo_form.procesado = True
            nuevo_form.save()
            return redirect("detalle_formulario", pk=nuevo_form.pk)
        except Exception as e:
            print(f"Error procesando formulario: {e}")
            # Podríamos redirigir con un error o mostrarlo en la lista
            return redirect("lista_formularios")

    return render(request, "seguridad/subir_formulario.html")


def detalle_formulario(request, pk):
    formulario = Formulario.objects.get(pk=pk)

    if request.method == "POST":
        # Guardar los datos llenados
        datos = {}
        # Iteramos sobre los campos esperados para sacar del POST
        if formulario.resultado_json and "campos" in formulario.resultado_json:
            for campo in formulario.resultado_json["campos"]:
                # User defined structure uses 'id'
                key = campo.get("id", campo.get("nombre", "")).strip() 
                if key:
                     # Template uses slugify for input names (e.g. 'item_1' -> 'item-1')
                     input_name = slugify(key)
                     print(f"DEBUG: Looking for input '{input_name}' for field '{key}'")
                     val = request.POST.get(input_name, "")
                     print(f"DEBUG: Found value: '{val}'")
                     datos[key] = val
        
        registro = RegistroFormulario(
            formulario=formulario,
            datos_llenados=datos
        )
        registro.save()
        return redirect("ver_registros", pk=formulario.pk)

    return render(request, "seguridad/detalle_formulario.html", {"formulario": formulario})


def ver_registros(request, pk):
    formulario = Formulario.objects.get(pk=pk)
    registros = formulario.registros.all().order_by("-fecha_registro")
    return render(request, "seguridad/ver_registros.html", {"formulario": formulario, "registros": registros})


def detalle_registro(request, pk):
    registro = RegistroFormulario.objects.get(pk=pk)
    return render(request, "seguridad/detalle_registro.html", {"registro": registro, "formulario": registro.formulario})
