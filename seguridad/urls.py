import os

from django.conf import settings
from django.urls import path
from django.views.static import serve

from . import views


# PWA static file serving function
def serve_pwa_file(request, filename):
    """Serve PWA files directly"""
    from django.http import FileResponse, HttpResponseNotFound

    file_path = os.path.join(settings.BASE_DIR, "seguridad", "static", "pwa", filename)
    if os.path.exists(file_path):
        content_type = (
            "application/json"
            if filename.endswith(".json")
            else "application/javascript"
            if filename.endswith(".js")
            else "image/svg+xml"
        )
        return FileResponse(open(file_path, "rb"), content_type=content_type)
    return HttpResponseNotFound("File not found")


urlpatterns = [
    # PWA files - serve directly
    path("static/pwa/<str:filename>", serve_pwa_file, name="serve_pwa"),
    path("", views.home, name="home"),
    path("pwa-test/", views.pwa_test, name="pwa_test"),
    path("debug-static/", views.debug_static_files, name="debug_static"),
    path("test-manifest/", views.test_manifest, name="test_manifest"),
    path("admin/run-migrations/", views.run_migrations, name="run_migrations"),
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
