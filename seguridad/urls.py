from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("pwa-test/", views.pwa_test, name="pwa_test"),
    path("debug-static/", views.debug_static_files, name="debug_static"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("bitacora/", views.bitacora, name="bitacora"),
    path("reportar/", views.crear_reporte, name="crear_reporte"),
    path("emergencia/", views.reporte_emergencia, name="reporte_emergencia"),
    path("registros/", views.lista_registros, name="lista_registros"),
    path("registros/<int:pk>/", views.detalle_registro, name="detalle_registro"),
    path("reportes/<int:pk>/", views.detalle_reporte, name="detalle_reporte"),
    path("formularios/", views.lista_formularios, name="lista_formularios"),
    path("formularios/subir/", views.subir_formulario, name="subir_formulario"),
    path("formularios/<int:pk>/", views.detalle_formulario, name="detalle_formulario"),
    path("formularios/<int:pk>/registros/", views.ver_registros, name="ver_registros"),
    path("api/faltantes/", views.get_faltantes, name="get_faltantes"),
]
