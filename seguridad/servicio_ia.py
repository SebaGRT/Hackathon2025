import json
import os

from django.conf import settings
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCU4lKGMKoFffnoOAxNaJREvjeUyRgju_M")


def analisis_fotos(ruta_imagen, text_norma):
    print("Analizando fotos...")
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
        with open(ruta_imagen, "rb") as f:
            imagen_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                types.Part.from_text(text=prompt_inspector),
                types.Part.from_bytes(data=imagen_bytes, mime_type="image/jpeg"),
            ],
        )
        respuesta_texto = response.text.strip()

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
        return resultado_json
    except Exception as e:
        print(f"Error al analizar la imagen: {e}")
        return {
            "violacion_detectada": False,
            "norma_infringida_titulo": None,
            "descripcion_detallada": "Error al analizar la imagen",
            "severidad_sugerida": "BAJA",
        }
