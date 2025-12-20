from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("reportar/", views.crear_reporte, name="crear_reporte"),
]
