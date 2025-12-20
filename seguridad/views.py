# Create your views here.
import base64

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
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
        messages.error(request, "No tienes permisos para acceder al dashboard. Solo supervisores.")
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
    }

    return render(request, "seguridad/dashboard.html", contexto)


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
