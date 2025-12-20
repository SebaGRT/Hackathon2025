from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("reportar/", views.crear_reporte, name="crear_reporte"),
    path("emergencia/", views.reporte_emergencia, name="reporte_emergencia"),
    path("formularios/", views.lista_formularios, name="lista_formularios"),
    path("formularios/subir/", views.subir_formulario, name="subir_formulario"),
    path("formularios/<int:pk>/", views.detalle_formulario, name="detalle_formulario"),
    path("formularios/<int:pk>/registros/", views.ver_registros, name="ver_registros"),
    path("registros/<int:pk>/", views.detalle_registro, name="detalle_registro"),
]
