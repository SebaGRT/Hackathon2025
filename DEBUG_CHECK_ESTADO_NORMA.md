# Debug: Check Estado Norma (Norma Infringida)

**Fecha:** 2025-12-20  
**Problema Reportado:** "Norma infringida está stucked en False"  
**Estado:** 🔍 Cambios de debug implementados - Pendiente prueba

---

## Problema Identificado

El campo `check_estado_norma` (checkbox "¿Hay norma incumplida?") aparentemente siempre queda en `False` incluso cuando la IA detecta una violación.

## Posibles Causas

1. **La IA no está detectando violaciones** → `violacion_detectada` siempre retorna `false`
2. **Problema en el template** → El checkbox no se marca correctamente con el valor de la IA
3. **Problema en el POST** → El valor del checkbox no se procesa correctamente al guardar
4. **Tipo de dato incorrecto** → La IA devuelve string en lugar de boolean

## Cambios Implementados (Autorizados)

### 1. Debug en `views.py` - Análisis de IA (Líneas 81-127)

```python
# Se agregó logging detallado del resultado de la IA:
print(f"[DEBUG] ===== RESULTADO COMPLETO DE LA IA =====")
print(f"[DEBUG] Resultado IA: {resultado_ia}")
print(f"[DEBUG] violacion_detectada: {resultado_ia.get('violacion_detectada')}")
print(f"[DEBUG] norma_infringida_titulo: {resultado_ia.get('norma_infringida_titulo')}")
print(f"[DEBUG] descripcion_detallada: {resultado_ia.get('descripcion_detallada')}")
print(f"[DEBUG] severidad_sugerida: {resultado_ia.get('severidad_sugerida')}")
```

**Objetivo:** Ver exactamente qué está devolviendo la IA y si `violacion_detectada` es realmente `true` o `false`.

### 2. Debug en `views.py` - Guardado del Reporte (Líneas 148-188)

```python
print("[DEBUG] ===== GUARDANDO REPORTE FINAL =====")
print(f"[DEBUG] POST data keys: {list(request.POST.keys())}")
print(f"[DEBUG] Valor inicial del checkbox (IA): {request.POST.get('debug_check_inicial')}")

checkbox_value = request.POST.get("check_estado_norma")
print(f"[DEBUG] check_estado_norma POST value: '{checkbox_value}'")
nuevo_reporte.check_estado_norma = checkbox_value == "on"
print(f"[DEBUG] check_estado_norma final value: {nuevo_reporte.check_estado_norma}")
```

**Objetivo:** Rastrear el valor del checkbox desde que la IA lo determina hasta que se guarda en la base de datos.

### 3. Campo Hidden en Template (Línea 392-396)

```html
<input
    type="hidden"
    name="debug_check_inicial"
    value="{{ check_estado_norma }}"
/>
```

**Objetivo:** Guardar el valor inicial que la IA determinó para compararlo con lo que el usuario envió.

### 4. Script de Testing (`test_ia_response.py`)

Script independiente para probar la IA sin el flujo completo del servidor.

**Uso:**
```bash
python test_ia_response.py media/incidentes/imagen_prueba.jpg
```

**Qué hace:**
- Llama directamente a `analisis_fotos()`
- Muestra la estructura completa del resultado
- Valida tipos de datos
- Simula el comportamiento del template y POST
- Identifica si el problema está en la IA o en el procesamiento

---

## Cómo Probar

### Prueba 1: Verificar Respuesta de la IA

```bash
# Busca alguna imagen en media/incidentes/ y pruébala:
python test_ia_response.py media/incidentes/tu_imagen.jpg
```

**Busca en la salida:**
```
🔍 Valores individuales:
  [violacion_detectada] (bool): True  ← ¿Es True o False?
  [norma_infringida_titulo] (str): ...
```

### Prueba 2: Verificar Flujo Completo

1. Inicia el servidor Django:
   ```bash
   python manage.py runserver
   ```

2. Ve a `/seguridad/crear-reporte/`

3. Sube una imagen de prueba

4. **Revisa la consola del servidor** - Deberías ver:
   ```
   [DEBUG] ===== RESULTADO COMPLETO DE LA IA =====
   [DEBUG] violacion_detectada: True  ← ¿Qué dice aquí?
   [DEBUG] Valor de check_estado_norma que se pasa al template: True
   ```

5. En la página web, verifica si el checkbox aparece marcado (✓)

6. Haz clic en "Guardar Reporte"

7. **Revisa la consola nuevamente** - Deberías ver:
   ```
   [DEBUG] ===== GUARDANDO REPORTE FINAL =====
   [DEBUG] Valor inicial del checkbox (IA): True
   [DEBUG] check_estado_norma POST value: 'on'  ← ¿Qué dice aquí?
   [DEBUG] check_estado_norma final value: True
   ```

---

## Interpretación de Resultados

### Escenario A: La IA siempre devuelve False
```
[DEBUG] violacion_detectada: False
```
**Causa:** La IA no está detectando violaciones correctamente
**Solución:** Revisar el prompt o las normas en `servicio_ia.py`

### Escenario B: La IA devuelve True pero el checkbox no se marca
```
[DEBUG] violacion_detectada: True
[DEBUG] Valor de check_estado_norma que se pasa al template: True
# Pero el checkbox no aparece marcado en la web
```
**Causa:** Problema en el template
**Solución:** Revisar `reporte_camara.html` línea 400-407

### Escenario C: El checkbox se marca pero el POST llega vacío
```
[DEBUG] Valor inicial del checkbox (IA): True
[DEBUG] check_estado_norma POST value: 'None'
```
**Causa:** El checkbox se desmarca antes de enviar o problema con el formulario
**Solución:** Revisar JavaScript/Alpine.js en el template

### Escenario D: Todo correcto hasta el guardado
```
[DEBUG] check_estado_norma POST value: 'on'
[DEBUG] check_estado_norma final value: True
# Pero en la BD queda False
```
**Causa:** Problema en el modelo o guardado
**Solución:** Revisar modelo `ReporteDeCampo` y proceso de guardado

---

## Información del Checkbox

### Cómo funciona un checkbox en HTML/Django:

- **Checkbox MARCADO** → Envía `name="check_estado_norma" value="on"` en el POST
- **Checkbox DESMARCADO** → NO envía nada (la key no existe en POST)

### Código actual de procesamiento:

```python
checkbox_value = request.POST.get("check_estado_norma")  # 'on' o None
nuevo_reporte.check_estado_norma = checkbox_value == "on"  # True o False
```

- Si `checkbox_value = 'on'` → `'on' == 'on'` → `True` ✓
- Si `checkbox_value = None` → `None == 'on'` → `False` ✓

**Esto está correcto.** El problema debe estar antes.

---

## Próximos Pasos

1. **Ejecutar pruebas** usando el script y el flujo completo
2. **Analizar los logs** de la consola
3. **Identificar en qué punto** el valor cambia de True a False
4. **Aplicar solución específica** según el escenario detectado

---

## Archivos Modificados

- ✅ `seguridad/views.py` - Agregado debug extensivo
- ✅ `seguridad/templates/seguridad/reporte_camara.html` - Campo hidden de debug
- ✅ `test_ia_response.py` - Script de prueba independiente
- ✅ `DEBUG_CHECK_ESTADO_NORMA.md` - Esta documentación

## Rollback

Si necesitas revertir estos cambios de debug:

```bash
git diff HEAD seguridad/views.py
git diff HEAD seguridad/templates/seguridad/reporte_camara.html

# Para revertir:
git checkout HEAD -- seguridad/views.py
git checkout HEAD -- seguridad/templates/seguridad/reporte_camara.html
rm test_ia_response.py
```

---

**Nota:** Estos cambios NO afectan la funcionalidad, solo agregan logging para diagnóstico.