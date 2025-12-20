from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from seguridad.models import (
    Formulario,
    PerfilUsuario,
    RegistroFormulario,
    ReporteDeCampo,
)


@admin.register(ReporteDeCampo)
class ReporteDeCampoAdmin(admin.ModelAdmin):
    list_display = [
        "id_reporte",
        "fecha_reporte",
        "image_check",
        "check_estado_norma",
        "norma_infringida",
        "clasificacion",
        "casco",
        "chaleco",
        "guantes",
        "botas",
    ]
    list_filter = ["fecha_reporte", "check_estado_norma", "clasificacion"]
    search_fields = ["id_reporte", "norma_infringida", "descripcion"]
    readonly_fields = ["id_reporte", "fecha_reporte"]


@admin.register(Formulario)
class FormularioAdmin(admin.ModelAdmin):
    list_display = ["id_formulario", "nombre", "fecha_subida", "procesado"]
    list_filter = ["procesado", "fecha_subida"]
    search_fields = ["nombre", "resumen"]


@admin.register(RegistroFormulario)
class RegistroFormularioAdmin(admin.ModelAdmin):
    list_display = ["id_registro", "formulario", "fecha_registro", "responsable"]
    list_filter = ["fecha_registro"]
    search_fields = ["responsable"]


# Inline admin for PerfilUsuario
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = "Perfil"
    fields = ["rol"]


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Register PerfilUsuario separately for direct management
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ["user", "rol", "fecha_creacion"]
    list_filter = ["rol", "fecha_creacion"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["fecha_creacion"]
