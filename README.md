# CChC SafeApp - Sistema de Inspección de Seguridad con IA

Sistema de inspección inteligente para obras de construcción que utiliza IA (Google Gemini Vision) para analizar imágenes y detectar violaciones de normas de seguridad.

## 🚀 Características

- 📸 Captura de imágenes directa desde la cámara o carga de archivos
- 🤖 Análisis automático con Google Gemini Vision AI
- 🛡️ Detección de violaciones de normas de seguridad
- 📊 Clasificación de severidad (Baja, Media, Alta)
- 🎨 Interfaz moderna estilo Lyra con diseño boxy
- ⚡ Reportes en tiempo real

## 🛠️ Tecnologías

- **Backend:** Django 6.0
- **IA:** Google Gemini Vision API
- **Frontend:** TailwindCSS, Alpine.js, Lucide Icons
- **Despliegue:** Vercel

## 📋 Requisitos Previos

- Python 3.9+
- Google Gemini API Key
- Cuenta de Vercel (para deployment)

## 🔧 Instalación Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/SebaGRT/Hackathon2025.git
cd Hackathon2025
```

2. **Crear y activar entorno virtual:**
```bash
python -m venv mienv
source mienv/bin/activate  # En Windows: mienv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Edita .env y agrega tu GEMINI_API_KEY
```

5. **Ejecutar migraciones:**
```bash
python manage.py migrate
```

6. **Recolectar archivos estáticos:**
```bash
python manage.py collectstatic
```

7. **Iniciar servidor de desarrollo:**
```bash
python manage.py runserver
```

Visita `http://localhost:8000` en tu navegador.

## 🚀 Despliegue en Vercel

### Opción 1: Despliegue desde GitHub (Recomendado)

1. **Sube tu código a GitHub:**
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

2. **Conecta con Vercel:**
   - Ve a [vercel.com](https://vercel.com) e inicia sesión
   - Click en "Add New Project"
   - Importa tu repositorio de GitHub
   - Vercel detectará automáticamente la configuración de Django

3. **Configurar Variables de Entorno en Vercel:**
   - En el dashboard de tu proyecto, ve a Settings → Environment Variables
   - Agrega las siguientes variables:
     ```
     SECRET_KEY=tu-django-secret-key-aqui
     GEMINI_API_KEY=tu-gemini-api-key-aqui
     VERCEL_ENV=production
     ```

4. **Deploy:**
   - Click en "Deploy"
   - Espera a que termine el build
   - ¡Tu app estará live en `https://tu-proyecto.vercel.app`!

### Opción 2: Despliegue con Vercel CLI

1. **Instalar Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login a Vercel:**
```bash
vercel login
```

3. **Configurar variables de entorno:**
```bash
vercel env add SECRET_KEY
vercel env add GEMINI_API_KEY
vercel env add VERCEL_ENV
```

4. **Deploy:**
```bash
vercel --prod
```

## ⚙️ Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False

# Vercel Environment
VERCEL_ENV=production

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Allowed Hosts
ALLOWED_HOSTS=.vercel.app,.now.sh,localhost,127.0.0.1

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://*.vercel.app,https://*.now.sh
```

### Obtener API Key de Google Gemini:

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea un nuevo proyecto o selecciona uno existente
3. Genera una nueva API key
4. Copia la key y agrégala a tus variables de entorno

## 📁 Estructura del Proyecto

```
Hackathon/
├── core/                   # Configuración principal de Django
│   ├── settings.py        # Settings con config para Vercel
│   ├── urls.py
│   ├── wsgi.py
│   └── wsgi_vercel.py     # WSGI handler para Vercel
├── seguridad/             # App principal
│   ├── models.py          # Modelo ReporteDeCampo
│   ├── views.py           # Vistas
│   ├── urls.py
│   ├── servicio_ia.py     # Integración con Gemini AI
│   └── templates/         # Templates HTML
├── media/                 # Archivos subidos (no se deploya)
├── staticfiles/           # Archivos estáticos compilados
├── requirements.txt       # Dependencias Python
├── vercel.json           # Configuración de Vercel
├── build_files.sh        # Script de build
└── .vercelignore         # Archivos a ignorar en deploy
```

## 🎨 Características del UI

- **Diseño Lyra-style:** Interfaz moderna con elementos boxy y geométricos
- **Modo oscuro:** Paleta de colores oscura profesional
- **Responsive:** Optimizado para móviles y desktop
- **Iconos Lucide:** Iconos vectoriales escalables y consistentes
- **Animaciones suaves:** Transiciones y efectos hover elegantes

## 📝 Uso

1. **Accede a la aplicación**
2. **Click en "Crear Nuevo Registro"**
3. **Elige una opción:**
   - 📸 Usar Cámara: Captura una foto en tiempo real
   - 📁 Subir Archivo: Sube una imagen existente
4. **Captura/sube la imagen**
5. **Click en "Analizar con IA"**
6. **Espera el análisis automático**
7. **Revisa los resultados:**
   - Violación detectada (Sí/No)
   - Norma infringida
   - Descripción detallada
   - Severidad clasificada

## 🔍 Normas de Seguridad Vigentes

El sistema verifica contra las siguientes normas:

1. **EPP BÁSICO:** Uso obligatorio de casco, lentes y calzado de seguridad
2. **TRABAJO EN ALTURA:** Arnés de seguridad para trabajos sobre 1.8m
3. **ORDEN Y LIMPIEZA:** Zonas de tránsito libres de obstáculos

## 🐛 Troubleshooting

### Error: "Port already in use"
```bash
# Encuentra y mata el proceso usando el puerto 8000
lsof -i :8000
kill <PID>
```

### Error de migración en Vercel
- Vercel usa SQLite que es read-only en producción
- Para producción, considera usar PostgreSQL o MySQL
- Configura la DATABASE_URL en las variables de entorno de Vercel

### Archivos media no se muestran en Vercel
- Vercel es serverless y no persiste archivos
- Solución: Usa un servicio de almacenamiento como:
  - AWS S3
  - Cloudinary
  - Vercel Blob Storage

## 📄 Licencia

Hackathon CChC 2025

## 👥 Contribución

Este proyecto fue desarrollado para el Hackathon CChC 2025.

## 🆘 Soporte

Para problemas o preguntas:
1. Revisa la documentación de Django: https://docs.djangoproject.com/
2. Revisa la documentación de Vercel: https://vercel.com/docs
3. Consulta la documentación de Gemini API: https://ai.google.dev/

---

**Hecho con ❤️ para la seguridad en obras de construcción**