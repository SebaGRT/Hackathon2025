from django.contrib import admin

from seguridad.models import Formulario, RegistroFormulario, ReporteDeCampo


@admin.register(ReporteDeCampo)
class ReporteDeCampoAdmin(admin.ModelAdmin):
    list_display = ['id_reporte', 'fecha_reporte', 'image_check', 'check_estado_norma', 'norma_infringida', 'clasificacion', 'casco', 'chaleco', 'guantes', 'botas']
    list_filter = ['fecha_reporte', 'check_estado_norma', 'clasificacion']
    search_fields = ['id_reporte', 'norma_infringida', 'descripcion']
    readonly_fields = ['id_reporte', 'fecha_reporte']


@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ['id_formulario', 'nombre', 'fecha_subida', 'procesado']
    list_filter = ['procesado', 'fecha_subida']
    search_fields = ['nombre', 'resumen']


@admin.register(RegistroFormulario)
class RegistroFormularioAdmin(admin.ModelAdmin):
    list_display = ['id_registro', 'formulario', 'fecha_registro', 'responsable']
    list_filter = ['fecha_registro']
    search_fields = ['responsable']
