import json
import os

from django.conf import settings
from google import genai
from google.genai import types

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv(
    "mi_llave", "AIzaSyDXbRDxjQJBuVvpIZc_egVlQBjFobr1GPI"
)

print(f"[DEBUG] Initializing Gemini client with API key: {GEMINI_API_KEY[:10]}...")
client = genai.Client(api_key=GEMINI_API_KEY)


def analisis_fotos(ruta_imagen, text_norma):
    print(f"[DEBUG] Analizando fotos desde ruta: {ruta_imagen}")
    print(f"[DEBUG] Archivo existe: {os.path.exists(ruta_imagen)}")

    if not os.path.exists(ruta_imagen):
        print(f"[ERROR] El archivo no existe: {ruta_imagen}")
        return {
            "violacion_detectada": False,
            "norma_infringida_titulo": None,
            "descripcion_detallada": "Error: El archivo de imagen no se encontró",
            "severidad_sugerida": "BAJA",
        }
    prompt_inspector = f"""
        Actúa como un Inspector de Seguridad y Salud Ocupacional (HSE) experto y estricto en una obra de construcción.

        Tu tarea es analizar la imagen proporcionada y verificar si VIOLA alguna de las siguientes normas de seguridad vigentes:

        --- INICIO DE LAS NORMAS VIGENTES ---
        {text_norma}
        --- FIN DE LAS NORMAS VIGENTES ---

        Si la imagen muestra una situación segura que cumple las normas, indícalo.
        Si la imagen muestra una violación clara de alguna de las normas listadas arriba, repórtalo.

        RESPONDE ÚNICAMENTE CON UN JSON VÁLIDO. No uses bloques de código markdown. El JSON debe tener esta estructura exacta:
        {{
            "violacion_detectada": true/false, (booleano: true si hay peligro/violación, false si está seguro)
            "norma_infringida_titulo": "Título corto de la norma violada (ej: Uso de Arnés)", (o null si no hay violación)
            "descripcion_detallada": "Explicación técnica de por qué lo que se ve en la foto viola la norma específica citada arriba.",
            "severidad_sugerida": "BAJA", (Usa solo: "BAJA", "MEDIA", o "ALTA")
        }}
        """

    try:
        print(f"[DEBUG] Abriendo archivo de imagen...")
        with open(ruta_imagen, "rb") as f:
            imagen_bytes = f.read()

        print(f"[DEBUG] Imagen leída: {len(imagen_bytes)} bytes")

        if len(imagen_bytes) == 0:
            print("[ERROR] El archivo de imagen está vacío")
            return {
                "violacion_detectada": False,
                "norma_infringida_titulo": None,
                "descripcion_detallada": "Error: El archivo de imagen está vacío",
                "severidad_sugerida": "BAJA",
            }

        print(f"[DEBUG] Enviando solicitud a Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                types.Part.from_text(text=prompt_inspector),
                types.Part.from_bytes(data=imagen_bytes, mime_type="image/jpeg"),
            ],
        )
        print(f"[DEBUG] Respuesta recibida de Gemini")
        respuesta_texto = response.text.strip()
        print(f"[DEBUG] Respuesta sin procesar: {respuesta_texto[:200]}...")

        # Remove markdown code blocks if present
        if respuesta_texto.startswith("```json"):
            respuesta_texto = respuesta_texto[7:]
        elif respuesta_texto.startswith("```"):
            respuesta_texto = respuesta_texto[3:]

        if respuesta_texto.endswith("```"):
            respuesta_texto = respuesta_texto[:-3]

        respuesta_texto = respuesta_texto.strip()

        # Find JSON content between first { and last }
        start_idx = respuesta_texto.find("{")
        end_idx = respuesta_texto.rfind("}")

        if start_idx != -1 and end_idx != -1:
            respuesta_texto = respuesta_texto[start_idx : end_idx + 1]

        resultado_json = json.loads(respuesta_texto)
        print(f"[DEBUG] JSON parseado exitosamente: {resultado_json}")
        return resultado_json
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error al parsear JSON: {e}")
        print(f"[ERROR] Respuesta que causó el error: {respuesta_texto}")
        return {
            "violacion_detectada": False,
            "norma_infringida_titulo": None,
            "descripcion_detallada": f"Error al parsear respuesta de IA: {str(e)}",
            "severidad_sugerida": "BAJA",
        }
    except FileNotFoundError as e:
        print(f"[ERROR] Archivo no encontrado: {e}")
        return {
            "violacion_detectada": False,
            "norma_infringida_titulo": None,
            "descripcion_detallada": f"Error: Archivo no encontrado - {str(e)}",
            "severidad_sugerida": "BAJA",
        }
    except Exception as e:
        print(
            f"[ERROR] Error inesperado al analizar la imagen: {type(e).__name__}: {e}"
        )
        import traceback

        print(f"[ERROR] Traceback completo:\n{traceback.format_exc()}")
        return {
            "violacion_detectada": False,
            "norma_infringida_titulo": None,
            "descripcion_detallada": f"Error al analizar la imagen: {type(e).__name__}: {str(e)}",
            "severidad_sugerida": "BAJA",
        }
