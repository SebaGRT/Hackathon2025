import json
import os

from django.conf import settings
from google import genai
from google.genai import types

# Get API key from environment variable with multiple fallbacks
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


def analisis_formulario(ruta_archivo):
    print(f"Analizando formulario: {ruta_archivo}")

    prompt_formulario = """

Eres un asistente administrativo experto. Tu tarea es analizar este formulario (documento o imagen) y

generar una guía simplificada para que un usuario pueda completarlo fácilmente.


Identifica todos los campos que requieren ser llenados por el usuario.

RESPONDE ÚNICAMENTE CON UN JSON VÁLIDO. Estructura:

{

"resumen": "Breve descripción de para qué sirve este formulario y qué se necesita para llenarlo.",

"campos": [

{

"nombre": "Nombre del campo (ej: Apellido Paterno)",

"tipo": "Texto / Fecha / Firma / Selección / Checkbox",

"instruccion": "Instrucción clara y sencilla de qué poner aquí."

}

]

}

"""

    try:
        # Determine mime_type based on extension
        mime_type = "application/pdf"
        if ruta_archivo.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        elif ruta_archivo.lower().endswith(".png"):
            mime_type = "image/png"

        # Using File API for documents which is more robust for PDFs
        upload_file = client.files.upload(
            file=ruta_archivo, config={"mime_type": mime_type}
        )

        # Wait for file processing if necessary (mostly for large PDFs)
        # In a real async scenario we might want to poll, but for this sync view:
        import time

        while upload_file.state.name == "PROCESSING":
            time.sleep(2)
            upload_file = client.files.get(name=upload_file.name)

        if upload_file.state.name == "FAILED":
            raise Exception("Google AI File Upload Failed")

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                types.Part.from_text(text=prompt_formulario),
                types.Part.from_uri(
                    file_uri=upload_file.uri, mime_type=upload_file.mime_type
                ),
            ],
        )

        respuesta_texto = response.text.strip()
        print("------- INICIO RESPUESTA GEMINI -------")
        print(respuesta_texto)
        print("------- FIN RESPUESTA GEMINI -------")

        # Clean markdown
        if respuesta_texto.startswith("```json"):
            respuesta_texto = respuesta_texto[7:]
        elif respuesta_texto.startswith("```"):
            respuesta_texto = respuesta_texto[3:]
        if respuesta_texto.endswith("```"):
            respuesta_texto = respuesta_texto[:-3]

        respuesta_texto = respuesta_texto.strip()

        # Extract JSON
        start_idx = respuesta_texto.find("{")
        end_idx = respuesta_texto.rfind("}")
        if start_idx != -1 and end_idx != -1:
            respuesta_texto = respuesta_texto[start_idx : end_idx + 1]

        resultado_json = json.loads(respuesta_texto)
        print("------- JSON PARSEADO CORRECTAMENTE -------")
        print(json.dumps(resultado_json, indent=2))
        return resultado_json

    except Exception as e:
        print(f"Error al analizar formulario: {e}")
        import traceback

        traceback.print_exc()
        return {"resumen": "Error al procesar el formulario con IA.", "campos": []}
