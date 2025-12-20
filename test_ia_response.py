#!/usr/bin/env python
"""
Script de prueba para verificar la respuesta de la IA
Ejecutar: python test_ia_response.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from seguridad.servicio_ia import analisis_fotos

# Texto de normas (mismo que en views.py)
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
"""


def test_ia_con_imagen(ruta_imagen):
    """
    Prueba la función de análisis de IA con una imagen
    """
    print("=" * 80)
    print("TEST DE ANÁLISIS DE IA")
    print("=" * 80)
    print(f"\nRuta de imagen: {ruta_imagen}")
    print(f"Archivo existe: {os.path.exists(ruta_imagen)}")

    if not os.path.exists(ruta_imagen):
        print("\n❌ ERROR: La imagen no existe")
        print("\nPara usar este script:")
        print("  python test_ia_response.py <ruta_a_imagen.jpg>")
        return

    print("\n" + "-" * 80)
    print("Llamando a analisis_fotos()...")
    print("-" * 80 + "\n")

    resultado = analisis_fotos(ruta_imagen, NORMAS_VIGENTES_TEXTO)

    print("\n" + "=" * 80)
    print("RESULTADO DEL ANÁLISIS")
    print("=" * 80)

    # Verificar estructura
    print("\n📋 Estructura del resultado:")
    print(f"  Tipo: {type(resultado)}")
    print(f"  Keys: {list(resultado.keys()) if isinstance(resultado, dict) else 'N/A'}")

    print("\n🔍 Valores individuales:")
    if isinstance(resultado, dict):
        for key, value in resultado.items():
            value_type = type(value).__name__
            print(f"  [{key}] ({value_type}): {value}")

    print("\n✅ Validación de campos esperados:")
    campos_esperados = [
        "violacion_detectada",
        "norma_infringida_titulo",
        "descripcion_detallada",
        "severidad_sugerida",
    ]

    for campo in campos_esperados:
        if campo in resultado:
            valor = resultado[campo]
            tipo = type(valor).__name__
            print(f"  ✓ {campo}: {tipo} = {valor}")
        else:
            print(f"  ✗ {campo}: FALTA")

    # Verificar tipos
    print("\n🔬 Verificación de tipos:")
    violacion = resultado.get("violacion_detectada")
    print(f"  violacion_detectada es bool: {isinstance(violacion, bool)}")
    print(f"  violacion_detectada valor: {violacion}")
    print(f"  violacion_detectada == True: {violacion == True}")
    print(f"  violacion_detectada == False: {violacion == False}")

    # Simulación de lo que haría el template
    print("\n🎭 Simulación del template:")
    print(f"  {% if check_estado_norma %} → {'checked' if violacion else 'NO checked'}")

    # Simulación de lo que haría el POST
    print("\n📨 Simulación del POST:")
    checkbox_enviado = "on" if violacion else None
    print(f"  Checkbox enviado: {checkbox_enviado}")
    check_final = checkbox_enviado == "on"
    print(f"  check_estado_norma final: {check_final}")

    print("\n" + "=" * 80)
    if violacion:
        print("🚨 VIOLACIÓN DETECTADA")
        print(f"   Norma: {resultado.get('norma_infringida_titulo', 'N/A')}")
        print(f"   Severidad: {resultado.get('severidad_sugerida', 'N/A')}")
    else:
        print("✅ NO HAY VIOLACIÓN DETECTADA")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        # Buscar alguna imagen en media/incidentes/
        import glob

        imagenes = glob.glob("media/incidentes/*.jpg") + glob.glob(
            "media/incidentes/*.png"
        )
        if imagenes:
            ruta = imagenes[0]
            print(f"\n⚠️  No se especificó imagen, usando: {ruta}")
        else:
            print("\n❌ No se encontraron imágenes de prueba")
            print("\nUso:")
            print("  python test_ia_response.py <ruta_a_imagen.jpg>")
            print("\nEjemplo:")
            print("  python test_ia_response.py media/incidentes/test.jpg")
            sys.exit(1)

    test_ia_con_imagen(ruta)
