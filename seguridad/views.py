# Create your views here.
import base64
import json
from calendar import monthrange
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.text import slugify

from .models import Formulario, RegistroFormulario, ReporteDeCampo
from .servicio_ia import analisis_formulario, analisis_fotos, extraer_datos_formulario


def home(request):
    return render(request, "seguridad/home.html")


def pwa_test(request):
    """PWA diagnostic test page"""
    return render(request, "seguridad/pwa_test.html")


def debug_static_files(request):
    """Debug view to check if static files exist"""
    import os

    from django.conf import settings

    debug_info = {
        "STATIC_ROOT": str(settings.STATIC_ROOT),
        "STATIC_URL": settings.STATIC_URL,
        "STATICFILES_DIRS": [str(d) for d in settings.STATICFILES_DIRS],
        "BASE_DIR": str(settings.BASE_DIR),
        "PRODUCTION": getattr(settings, "PRODUCTION", False),
    }

    # Check if staticfiles directory exists
    static_root = settings.STATIC_ROOT
    debug_info["static_root_exists"] = os.path.exists(static_root)

    if os.path.exists(static_root):
        debug_info["static_root_contents"] = os.listdir(static_root)

        # Check PWA directory
        pwa_dir = os.path.join(static_root, "pwa")
        debug_info["pwa_dir_exists"] = os.path.exists(pwa_dir)

        if os.path.exists(pwa_dir):
            debug_info["pwa_contents"] = os.listdir(pwa_dir)

            # Check specific files
            manifest_path = os.path.join(pwa_dir, "manifest.json")
            sw_path = os.path.join(pwa_dir, "sw.js")

            debug_info["manifest_exists"] = os.path.exists(manifest_path)
            debug_info["sw_exists"] = os.path.exists(sw_path)

            if os.path.exists(manifest_path):
                debug_info["manifest_size"] = os.path.getsize(manifest_path)
            if os.path.exists(sw_path):
                debug_info["sw_size"] = os.path.getsize(sw_path)

    # Check source static directory
    source_static = os.path.join(settings.BASE_DIR, "seguridad", "static", "pwa")
    debug_info["source_pwa_exists"] = os.path.exists(source_static)
    if os.path.exists(source_static):
        debug_info["source_pwa_contents"] = os.listdir(source_static)

    # Return as JSON for easy viewing
    from django.http import JsonResponse

    return JsonResponse(debug_info, json_dumps_params={"indent": 2})


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
    contexto = {}

    if request.method == "POST":
        if request.FILES.get("imagen_terreno") and not request.POST.get("finalizar"):
            # Paso 1: Análisis IA sin guardar
            # Guardar temporalmente la imagen para análisis
            import os
            import tempfile

            try:
                print("[DEBUG] Iniciando análisis de imagen...")
                imagen = request.FILES["imagen_terreno"]
                print(
                    f"[DEBUG] Imagen recibida: {imagen.name}, tamaño: {imagen.size} bytes"
                )

                # Usar /tmp para compatibilidad con Vercel
                temp_dir = tempfile.gettempdir()
                temp_filename = f"temp_{timezone.now().timestamp()}_{imagen.name}"
                temp_full_path = os.path.join(temp_dir, temp_filename)
                print(f"[DEBUG] Guardando en: {temp_full_path}")

                # Guardar archivo temporal
                with open(temp_full_path, "wb+") as temp_file:
                    for chunk in imagen.chunks():
                        temp_file.write(chunk)

                print(
                    f"[DEBUG] Archivo guardado, tamaño: {os.path.getsize(temp_full_path)} bytes"
                )

                # Llamar a la IA
                print("[DEBUG] Llamando a analisis_fotos...")
                resultado_ia = analisis_fotos(temp_full_path, NORMAS_VIGENTES_TEXTO)
                print(f"[DEBUG] ===== RESULTADO COMPLETO DE LA IA =====")
                print(f"[DEBUG] Resultado IA: {resultado_ia}")
                print(
                    f"[DEBUG] violacion_detectada: {resultado_ia.get('violacion_detectada')}"
                )
                print(
                    f"[DEBUG] norma_infringida_titulo: {resultado_ia.get('norma_infringida_titulo')}"
                )
                print(
                    f"[DEBUG] descripcion_detallada: {resultado_ia.get('descripcion_detallada')}"
                )
                print(
                    f"[DEBUG] severidad_sugerida: {resultado_ia.get('severidad_sugerida')}"
                )
                print(f"[DEBUG] ==========================================")

                # Leer imagen para base64
                with open(temp_full_path, "rb") as f:
                    imagen_base64 = base64.b64encode(f.read()).decode("utf-8")

                # Preparar datos para el formulario
                check_estado_valor = resultado_ia.get("violacion_detectada", False)
                print(
                    f"[DEBUG] Valor de check_estado_norma que se pasa al template: {check_estado_valor}"
                )

                contexto.update(
                    {
                        "analisis_completado": True,
                        "imagen_base64": imagen_base64,
                        "check_estado_norma": check_estado_valor,
                        "norma_infringida": resultado_ia.get(
                            "norma_infringida_titulo", ""
                        ),
                        "descripcion": resultado_ia.get(
                            "descripcion_detallada", "Sin descripción disponible"
                        ),
                        "clasificacion": resultado_ia.get("severidad_sugerida", "BAJA"),
                        "casco": resultado_ia.get("epp_faltante", {}).get("casco", 0),
                        "chaleco": resultado_ia.get("epp_faltante", {}).get(
                            "chaleco", 0
                        ),
                        "guantes": resultado_ia.get("epp_faltante", {}).get(
                            "guantes", 0
                        ),
                        "botas": resultado_ia.get("epp_faltante", {}).get("botas", 0),
                    }
                )

                print(
                    f"[DEBUG] Contexto preparado para template: analisis_completado={contexto['analisis_completado']}, check_estado_norma={contexto['check_estado_norma']}"
                )

                # Limpiar archivo temporal después de análisis
                if os.path.exists(temp_full_path):
                    os.remove(temp_full_path)
                    print("[DEBUG] Archivo temporal eliminado")

            except Exception as e:
                print(f"[ERROR] Error en análisis de imagen: {type(e).__name__}: {e}")
                import traceback

                print(f"[ERROR] Traceback:\n{traceback.format_exc()}")

                contexto.update(
                    {
                        "error_analisis": True,
                        "error_mensaje": f"Error al analizar la imagen: {str(e)}",
                    }
                )

        elif request.POST.get("finalizar"):
            # Paso 2: Guardar el reporte final
            print("[DEBUG] ===== GUARDANDO REPORTE FINAL =====")
            print(f"[DEBUG] POST data keys: {list(request.POST.keys())}")
            print(
                f"[DEBUG] Valor inicial del checkbox (IA): {request.POST.get('debug_check_inicial')}"
            )

            imagen_data = request.POST.get("imagen_data")
            if imagen_data:
                # Decodificar base64
                imagen_bytes = base64.b64decode(imagen_data)
                import uuid

                from django.core.files.base import ContentFile

                filename = f"{uuid.uuid4()}.jpg"
                file_obj = ContentFile(imagen_bytes, name=filename)

                nuevo_reporte = ReporteDeCampo()
                nuevo_reporte.foto_incidente = file_obj
                nuevo_reporte.image_check = True

                # Debug checkbox value
                checkbox_value = request.POST.get("check_estado_norma")
                print(f"[DEBUG] check_estado_norma POST value: '{checkbox_value}'")
                nuevo_reporte.check_estado_norma = checkbox_value == "on"
                print(
                    f"[DEBUG] check_estado_norma final value: {nuevo_reporte.check_estado_norma}"
                )

                nuevo_reporte.norma_infringida = request.POST.get(
                    "norma_infringida", ""
                )
                print(f"[DEBUG] norma_infringida: '{nuevo_reporte.norma_infringida}'")

                nuevo_reporte.descripcion = request.POST.get("descripcion", "")
                print(
                    f"[DEBUG] descripcion: '{nuevo_reporte.descripcion[:50] if nuevo_reporte.descripcion else 'None'}...'"
                )

                nuevo_reporte.clasificacion = request.POST.get("clasificacion", "BAJA")
                print(f"[DEBUG] clasificacion: '{nuevo_reporte.clasificacion}'")

                nuevo_reporte.casco = int(request.POST.get("casco", 0))
                nuevo_reporte.chaleco = int(request.POST.get("chaleco", 0))
                nuevo_reporte.guantes = int(request.POST.get("guantes", 0))
                nuevo_reporte.botas = int(request.POST.get("botas", 0))
                print(
                    f"[DEBUG] EPP: casco={nuevo_reporte.casco}, chaleco={nuevo_reporte.chaleco}, guantes={nuevo_reporte.guantes}, botas={nuevo_reporte.botas}"
                )

                nuevo_reporte.save()
                print(f"[DEBUG] Reporte guardado con ID: {nuevo_reporte.id_reporte}")
                print("[DEBUG] ===== REPORTE GUARDADO EXITOSAMENTE =====")
                return redirect("home")

    return render(request, "seguridad/reporte_camara.html", contexto)


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
    return render(
        request, "seguridad/lista_formularios.html", {"formularios": formularios}
    )


def subir_formulario(request):
    formularios_existentes = Formulario.objects.all().order_by("nombre")

    if request.method == "POST":
        # Check if we are uploading a completed form (has archivo_completado)
        if request.FILES.get("archivo_completado"):
            print("Procesando formulario completado...")
            try:
                archivo_completado = request.FILES["archivo_completado"]
                formulario_id = request.POST.get("formulario_id")

                # Si NO hay formulario_id, creamos uno nuevo automáticamente
                if not formulario_id:
                    print(
                        "No se seleccionó plantilla. Creando una nueva desde el archivo completado..."
                    )
                    nuevo_form = Formulario()
                    nuevo_form.nombre = request.POST.get(
                        "nombre",
                        f"Formulario Auto-generado {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                    )
                    nuevo_form.categoria = request.POST.get("categoria", "PARTICULAR")
                    # Usamos el mismo archivo completado como "plantilla"
                    nuevo_form.archivo = archivo_completado
                    nuevo_form.save()

                    # Analizamos estructura primero
                    print("Analizando estructura de la nueva plantilla...")
                    nuevo_form.archivo.open("rb")
                    resultado_estructural = analisis_formulario(nuevo_form.archivo)
                    nuevo_form.archivo.close()
                    nuevo_form.resultado_json = resultado_estructural
                    nuevo_form.resumen = resultado_estructural.get(
                        "resumen", "Sin resumen disponible"
                    )
                    nuevo_form.procesado = True
                    nuevo_form.save()

                    formulario = nuevo_form
                else:
                    formulario = Formulario.objects.get(pk=formulario_id)

                # Guardar temporalmente para analisis (extraccion de datos)
                import os
                import tempfile

                temp_dir = tempfile.gettempdir()
                temp_filename = (
                    f"completed_{timezone.now().timestamp()}_{archivo_completado.name}"
                )
                temp_full_path = os.path.join(temp_dir, temp_filename)

                # Para evitar problemas de puntero de archivo, lo escribimos de nuevo desde el in-memory file.
                archivo_completado.seek(0)  # Reset pointer
                with open(temp_full_path, "wb+") as temp_file:
                    for chunk in archivo_completado.chunks():
                        temp_file.write(chunk)

                # Extraer datos con IA
                print(f"Llamando a extraer_datos_formulario para: {formulario.nombre}")
                datos_extraidos = extraer_datos_formulario(
                    temp_full_path, formulario.resultado_json
                )

                # Crear registro
                nuevo_registro = RegistroFormulario(
                    formulario=formulario,
                    datos_llenados=datos_extraidos,
                    responsable=request.user.username
                    if request.user.is_authenticated
                    else "Anonimo",
                )
                nuevo_registro.save()

                # Limpiar
                if os.path.exists(temp_full_path):
                    os.remove(temp_full_path)

                messages.success(
                    request, "Formulario completado subido y procesado exitosamente."
                )
                return redirect("detalle_registro", pk=nuevo_registro.pk)

            except Exception as e:
                print(f"Error procesando formulario completado: {e}")
                import traceback

                traceback.print_exc()
                messages.error(request, f"Error al procesar el formulario: {e}")
                return redirect("lista_formularios")

        # Check if we are uploading a new template
        elif request.FILES.get("archivo_formulario"):
            print("Subiendo nueva plantilla...")
            try:
                archivo_formulario = request.FILES["archivo_formulario"]
                nuevo_form = Formulario()
                nuevo_form.nombre = request.POST.get("nombre", "Nuevo Formulario")
                nuevo_form.categoria = request.POST.get("categoria", "PARTICULAR")
                nuevo_form.archivo = archivo_formulario
                nuevo_form.save()

                # Procesar con IA
                nuevo_form.archivo.open("rb")
                resultado = analisis_formulario(nuevo_form.archivo)
                nuevo_form.archivo.close()
                nuevo_form.resultado_json = resultado
                nuevo_form.resumen = resultado.get("resumen", "Sin resumen disponible")
                nuevo_form.procesado = True
                nuevo_form.save()
                return redirect("detalle_formulario", pk=nuevo_form.pk)
            except Exception as e:
                print(f"Error procesando formulario: {e}")
                return redirect("lista_formularios")

    return render(
        request,
        "seguridad/subir_formulario.html",
        {"formularios": formularios_existentes},
    )


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

        registro = RegistroFormulario(formulario=formulario, datos_llenados=datos)
        registro.save()
        return redirect("ver_registros", pk=formulario.pk)

    return render(
        request, "seguridad/detalle_formulario.html", {"formulario": formulario}
    )


def ver_registros(request, pk):
    formulario = Formulario.objects.get(pk=pk)
    registros = formulario.registros.all().order_by("-fecha_registro")
    return render(
        request,
        "seguridad/ver_registros.html",
        {"formulario": formulario, "registros": registros},
    )


def detalle_registro(request, pk):
    registro = RegistroFormulario.objects.get(pk=pk)
    return render(
        request,
        "seguridad/detalle_registro.html",
        {"registro": registro, "formulario": registro.formulario},
    )


def lista_registros(request):
    """Vista para listar todos los reportes de campo"""
    registros = ReporteDeCampo.objects.all().order_by("-fecha_reporte")

    # Calcular estadísticas
    total_reportes = registros.count()
    con_violaciones = registros.filter(check_estado_norma=True).count()
    conformes = registros.filter(check_estado_norma=False).count()

    return render(
        request,
        "seguridad/lista_reportes.html",
        {
            "registros": registros,
            "total_reportes": total_reportes,
            "con_violaciones": con_violaciones,
            "conformes": conformes,
        },
    )


def detalle_reporte(request, pk):
    """Vista para mostrar el detalle de un reporte de campo"""
    reporte = ReporteDeCampo.objects.get(id_reporte=pk)
    return render(
        request,
        "seguridad/detalle_reporte.html",
        {"reporte": reporte},
    )


@login_required
def dashboard(request):
    """Vista del dashboard con estadísticas y métricas - Solo SUPERVISORES"""
    # Verificar que el usuario sea supervisor
    if not request.user.is_authenticated or request.user.perfil.rol != "SUPERVISOR":
        messages.error(
            request, "No tienes permisos para acceder al dashboard. Solo supervisores."
        )
        return redirect("home")

    from datetime import datetime, timedelta

    from django.db.models import Count, Q

    # Fecha actual y hace 30 días
    ahora = timezone.now()
    hace_30_dias = ahora - timedelta(days=30)
    inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Total de reportes
    total_reportes = ReporteDeCampo.objects.count()
    reportes_mes = ReporteDeCampo.objects.filter(fecha_reporte__gte=inicio_mes).count()

    # Violaciones detectadas
    total_violaciones = ReporteDeCampo.objects.filter(check_estado_norma=True).count()

    # Violaciones por severidad
    violaciones_alta = ReporteDeCampo.objects.filter(
        check_estado_norma=True, clasificacion="ALTA"
    ).count()
    violaciones_media = ReporteDeCampo.objects.filter(
        check_estado_norma=True, clasificacion="MEDIA"
    ).count()
    violaciones_baja = ReporteDeCampo.objects.filter(
        check_estado_norma=True, clasificacion="BAJA"
    ).count()

    # Total de formularios
    total_formularios = Formulario.objects.count()
    formularios_mes = Formulario.objects.filter(fecha_subida__gte=inicio_mes).count()

    # Tasa de cumplimiento (porcentaje de reportes sin violaciones)
    if total_reportes > 0:
        reportes_conformes = ReporteDeCampo.objects.filter(
            check_estado_norma=False
        ).count()
        tasa_cumplimiento = round((reportes_conformes / total_reportes) * 100, 1)
    else:
        tasa_cumplimiento = 0

    # Reportes recientes (últimos 5)
    reportes_recientes = ReporteDeCampo.objects.all().order_by("-fecha_reporte")[:5]

    # Datos para el calendario (mes actual)
    import json
    from datetime import date

    today = date.today()

    # Obtener reportes del mes actual agrupados por fecha
    reportes_calendario = (
        ReporteDeCampo.objects.filter(
            fecha_reporte__year=today.year, fecha_reporte__month=today.month
        )
        .values("fecha_reporte")
        .annotate(count=Count("id_reporte"))
        .order_by("fecha_reporte")
    )

    # Crear diccionario con formato fecha: {count, violations}
    calendar_data = {}
    for r in reportes_calendario:
        fecha = r["fecha_reporte"]
        fecha_str = fecha.strftime("%Y-%m-%d")

        # Contar violaciones en ese día
        violations = ReporteDeCampo.objects.filter(
            fecha_reporte=fecha, check_estado_norma=True
        ).count()

        calendar_data[fecha_str] = {"count": r["count"], "violations": violations}

    max_count = (
        max([d["count"] for d in calendar_data.values()]) if calendar_data else 0
    )

    contexto = {
        "total_reportes": total_reportes,
        "reportes_mes": reportes_mes,
        "total_violaciones": total_violaciones,
        "violaciones_alta": violaciones_alta,
        "violaciones_media": violaciones_media,
        "violaciones_baja": violaciones_baja,
        "total_formularios": total_formularios,
        "formularios_mes": formularios_mes,
        "tasa_cumplimiento": tasa_cumplimiento,
        "reportes_recientes": reportes_recientes,
        "calendar_data": json.dumps(calendar_data),
        "max_count": max_count,
        "current_year": today.year,
        "current_month": today.month,
        "current_month_name": today.strftime("%B"),
    }

    return render(request, "seguridad/dashboard.html", contexto)


@login_required
def bitacora(request):
    """Vista de bitácora diaria con calendario y filtrado por fecha"""
    import json
    from datetime import date, datetime

    # Obtener fecha del query param o usar hoy
    fecha_str = request.GET.get("date")
    today = date.today()

    if fecha_str:
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha_seleccionada = today
    else:
        fecha_seleccionada = today

    # Filtrar reportes por la fecha seleccionada
    reportes_dia = ReporteDeCampo.objects.filter(
        fecha_reporte__year=fecha_seleccionada.year,
        fecha_reporte__month=fecha_seleccionada.month,
        fecha_reporte__day=fecha_seleccionada.day,
    ).order_by("-fecha_reporte")

    # Obtener formularios diarios y verificar si fueron completados hoy
    formularios_diarios = Formulario.objects.filter(categoria="DIARIO")
    formularios_diarios_estado = []

    for formulario in formularios_diarios:
        completado = RegistroFormulario.objects.filter(
            formulario=formulario,
            fecha_registro__year=fecha_seleccionada.year,
            fecha_registro__month=fecha_seleccionada.month,
            fecha_registro__day=fecha_seleccionada.day,
        ).exists()

        formularios_diarios_estado.append(
            {"formulario": formulario, "completado": completado}
        )

    # Estadísticas del día seleccionado
    total_dia = reportes_dia.count()
    violaciones_dia = reportes_dia.filter(check_estado_norma=True).count()

    # Datos para el calendario (mes actual de la fecha seleccionada)
    # Mostramos el calendario del mes de la fecha seleccionada, no necesariamente "hoy"
    mes_target = fecha_seleccionada.month
    year_target = fecha_seleccionada.year

    reportes_calendario = (
        ReporteDeCampo.objects.filter(
            fecha_reporte__year=year_target, fecha_reporte__month=mes_target
        )
        .values("fecha_reporte")
        .annotate(count=Count("id_reporte"))
        .order_by("fecha_reporte")
    )

    calendar_data = {}
    for r in reportes_calendario:
        f = r["fecha_reporte"]
        f_str = f.strftime("%Y-%m-%d")
        violations = ReporteDeCampo.objects.filter(
            fecha_reporte=f, check_estado_norma=True
        ).count()
        calendar_data[f_str] = {"count": r["count"], "violations": violations}

    max_count = (
        max([d["count"] for d in calendar_data.values()]) if calendar_data else 0
    )

    contexto = {
        "reportes_dia": reportes_dia,
        "fecha_seleccionada": fecha_seleccionada,
        "total_dia": total_dia,
        "violaciones_dia": violaciones_dia,
        "calendar_data": json.dumps(calendar_data),
        "max_count": max_count,
        "current_year": year_target,
        "current_month": mes_target,
        "today": today,
        "formularios_diarios_estado": formularios_diarios_estado,
        # Nombres de meses en español para display si es necesario, o usar filtro date de django
    }

    return render(request, "seguridad/bitacora.html", contexto)


def login_view(request):
    """Vista para iniciar sesión"""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"¡Bienvenido {user.username}!")

            # Redirect to next page or dashboard
            next_page = request.GET.get("next", "dashboard")
            return redirect(next_page)
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "seguridad/login.html")


def logout_view(request):
    """Vista para cerrar sesión"""
    if request.method == "POST":
        auth_logout(request)
        messages.success(request, "Has cerrado sesión correctamente")
        return redirect("home")
    else:
        # Allow GET requests as well for convenience
        auth_logout(request)
        messages.success(request, "Has cerrado sesión correctamente")
        return redirect("home")


def get_faltantes(request):
    """Vista para obtener los elementos faltantes acumulados"""
    faltantes = {
        "cascos": ReporteDeCampo.objects.aggregate(total=Sum("casco"))["total"] or 0,
        "chalecos": ReporteDeCampo.objects.aggregate(total=Sum("chaleco"))["total"]
        or 0,
        "guantes": ReporteDeCampo.objects.aggregate(total=Sum("guantes"))["total"] or 0,
        "botas": ReporteDeCampo.objects.aggregate(total=Sum("botas"))["total"] or 0,
    }
    return JsonResponse(faltantes)
