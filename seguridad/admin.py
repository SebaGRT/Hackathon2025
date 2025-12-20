from django.contrib import admin

from seguridad.models import Formulario, RegistroFormulario, ReporteDeCampo

# Register your models here.

admin.site.register(ReporteDeCampo)
admin.site.register(Formulario)
admin.site.register(RegistroFormulario)
