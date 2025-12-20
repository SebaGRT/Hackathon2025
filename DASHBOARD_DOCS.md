# Dashboard - Documentación Técnica

## Descripción General

El dashboard es un panel de control modular y extensible que proporciona una vista general del sistema de seguridad, incluyendo estadísticas, métricas, reportes recientes y acciones rápidas.

## Arquitectura

### Vista (Backend)
**Archivo:** `seguridad/views.py` → función `dashboard()`

La vista calcula y prepara los siguientes datos:

#### Métricas Principales
- `total_reportes`: Número total de reportes creados
- `reportes_mes`: Reportes creados en el mes actual
- `total_violaciones`: Reportes marcados con violación de norma
- `violaciones_alta/media/baja`: Violaciones por nivel de severidad
- `total_formularios`: Formularios subidos al sistema
- `formularios_mes`: Formularios subidos este mes
- `tasa_cumplimiento`: Porcentaje de reportes conformes (sin violaciones)

#### Datos Dinámicos
- `reportes_recientes`: Últimos 5 reportes ordenados por fecha

### Template (Frontend)
**Archivo:** `seguridad/templates/seguridad/dashboard.html`

## Estructura Modular

El dashboard está dividido en secciones independientes que pueden ser modificadas o extendidas:

### 1. Header Section
```html
<!-- Dashboard Header -->
<div class="flex flex-col md:flex-row...">
```
- Título del dashboard
- Información del usuario (rol)
- Responsive (mobile/desktop)

### 2. Quick Stats Grid
```html
<!-- Quick Stats Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
```
Cuatro tarjetas con estadísticas principales:
- Total Reportes (azul)
- Violaciones (rojo)
- Formularios (verde)
- Tasa de Cumplimiento (amarillo)

**Personalización:** Para agregar una nueva métrica:
1. Calcular el valor en `views.py`
2. Pasar en el contexto
3. Duplicar una tarjeta existente y modificar colores/iconos/datos

### 3. Main Content Grid (2 columnas)

#### Columna Izquierda (lg:col-span-2)

##### a) Distribución por Severidad
Gráfico de barras horizontales mostrando violaciones por severidad.
- Usa `{% widthratio %}` para calcular porcentajes
- Barras de progreso con colores temáticos

##### b) Reportes Recientes
Lista de los últimos 5 reportes con:
- Estado (Violación/Conforme)
- Severidad
- Descripción
- Fecha y hora
- Link al detalle

#### Columna Derecha (lg:col-span-1)

##### a) Acciones Rápidas
Botones de acceso rápido a:
- Crear Nuevo Reporte
- Subir Formulario
- Ver Registros
- Lista de Formularios

##### b) Estado del Sistema
Indicadores del estado de servicios:
- AI Vision
- Base de Datos
- Almacenamiento

##### c) Tips & Information
Consejos y recomendaciones de seguridad.

### 4. Sección de Módulos Adicionales (Comentada)
Al final del template hay una sección comentada para agregar módulos personalizados sin afectar el diseño existente.

## Cómo Extender el Dashboard

### Agregar una Nueva Métrica

**1. Backend (`views.py`):**
```python
def dashboard(request):
    # ... código existente ...
    
    # Nueva métrica
    mi_nueva_metrica = MiModelo.objects.filter(estado="activo").count()
    
    contexto = {
        # ... métricas existentes ...
        "mi_nueva_metrica": mi_nueva_metrica,
    }
    
    return render(request, "seguridad/dashboard.html", contexto)
```

**2. Frontend (`dashboard.html`):**
```html
<div class="boxy-card p-6 relative overflow-hidden group hover:border-purple-500/50 transition-all">
    <div class="absolute top-0 left-0 w-1 h-full bg-purple-600"></div>
    <div class="flex items-start justify-between">
        <div class="flex-1">
            <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">
                Mi Nueva Métrica
            </p>
            <p class="text-3xl font-bold text-white mb-1">
                {{ mi_nueva_metrica|default:0 }}
            </p>
        </div>
        <div class="w-12 h-12 bg-purple-600/20 flex items-center justify-center">
            <i data-lucide="star" class="w-6 h-6 text-purple-400"></i>
        </div>
    </div>
</div>
```

### Agregar un Nuevo Gráfico/Widget

Descomentar la sección al final del template y agregar tu módulo:

```html
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="boxy-card p-6">
        <h3 class="text-lg font-bold uppercase tracking-tight mb-4">
            Mi Nuevo Widget
        </h3>
        
        <!-- Contenido del widget -->
        <div class="space-y-4">
            {% for item in mis_items %}
            <div class="flex items-center justify-between p-3 bg-gray-900/50 border border-gray-800">
                <span class="text-sm text-gray-300">{{ item.nombre }}</span>
                <span class="text-sm font-bold text-white">{{ item.valor }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
```

### Agregar Filtros por Fecha

**Backend:**
```python
from datetime import timedelta

# Obtener rango de fechas del request
dias = int(request.GET.get('dias', 30))
fecha_desde = ahora - timedelta(days=dias)

# Filtrar datos
reportes_filtrados = ReporteDeCampo.objects.filter(
    fecha_creacion__gte=fecha_desde
).count()
```

**Frontend:**
```html
<div class="flex gap-2">
    <a href="?dias=7" class="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-xs uppercase">
        7 días
    </a>
    <a href="?dias=30" class="px-3 py-1 bg-blue-600 text-xs uppercase">
        30 días
    </a>
    <a href="?dias=90" class="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-xs uppercase">
        90 días
    </a>
</div>
```

## Estilos y Diseño

### Clases CSS Principales

- `boxy-card`: Tarjeta estándar con borde y fondo
- `accent-gradient`: Gradiente decorativo de fondo
- Colores temáticos:
  - Azul (`bg-blue-600`): Reportes generales
  - Rojo (`bg-red-600`): Violaciones/Alertas
  - Verde (`bg-green-600`): Formularios/Éxito
  - Amarillo (`bg-yellow-600`): Cumplimiento/Advertencias

### Iconos (Lucide)

Los iconos se inicializan con:
```javascript
lucide.createIcons();
```

Iconos disponibles: https://lucide.dev/icons/

Uso:
```html
<i data-lucide="nombre-icono" class="w-5 h-5"></i>
```

## Responsive Design

- **Mobile (< 768px):** 1 columna, elementos apilados
- **Tablet (768px - 1024px):** 2 columnas en stats, 1 columna en contenido principal
- **Desktop (> 1024px):** 4 columnas en stats, 3 columnas en contenido principal

## URLs

- Vista del dashboard: `/dashboard/`
- URL name: `dashboard`

Uso en templates:
```html
<a href="{% url 'dashboard' %}">Ir al Dashboard</a>
```

## Permisos y Roles

Actualmente el dashboard es accesible para todos los usuarios autenticados.

Para restringir por rol:
```python
@login_required
def dashboard(request):
    # Verificar rol
    if not hasattr(request.user, 'perfil'):
        return redirect('home')
    
    if request.user.perfil.rol == 'TRABAJADOR':
        # Vista limitada para trabajadores
        contexto = {...}
    else:
        # Vista completa para supervisores
        contexto = {...}
```

## Optimización

### Queries
El dashboard hace varias consultas a la base de datos. Para optimizar:

```python
from django.db.models import Count, Q, Prefetch

# Usar aggregation
stats = ReporteDeCampo.objects.aggregate(
    total=Count('id'),
    violaciones=Count('id', filter=Q(check_estado_norma=True)),
    alta=Count('id', filter=Q(clasificacion='ALTA')),
)
```

### Caché
Para dashboards con mucho tráfico:

```python
from django.core.cache import cache

def dashboard(request):
    cache_key = f'dashboard_stats_{request.user.id}'
    contexto = cache.get(cache_key)
    
    if not contexto:
        # Calcular estadísticas...
        contexto = {...}
        cache.set(cache_key, contexto, 300)  # 5 minutos
    
    return render(request, "seguridad/dashboard.html", contexto)
```

## Próximas Mejoras Sugeridas

1. **Gráficos interactivos** con Chart.js o ApexCharts
2. **Exportación de datos** a PDF/Excel
3. **Filtros avanzados** por fecha, usuario, severidad
4. **Dashboard en tiempo real** con WebSockets
5. **Widgets personalizables** drag & drop
6. **Notificaciones** de eventos importantes
7. **Comparativas** período actual vs anterior

## Troubleshooting

### Error: "no such table"
Ejecutar migraciones:
```bash
python manage.py migrate
```

### Las estadísticas no se actualizan
Verificar que los reportes se estén guardando correctamente en la base de datos.

### Iconos no aparecen
Verificar que el script de Lucide esté cargando:
```javascript
document.addEventListener("DOMContentLoaded", function () {
    lucide.createIcons();
});
```

### Error de permisos
Verificar que el usuario tenga un perfil creado:
```python
# En el shell de Django
from django.contrib.auth.models import User
user = User.objects.get(username='tu_usuario')
print(hasattr(user, 'perfil'))  # Debe ser True
```

## Contacto y Soporte

Para preguntas o sugerencias sobre el dashboard, consultar la documentación del proyecto principal o revisar los commits relacionados.