# 🚀 Guía de Despliegue en Vercel

Esta guía te llevará paso a paso para desplegar tu aplicación CChC SafeApp en Vercel.

## 📋 Pre-requisitos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta de GitHub (tu código ya está subido)
- ✅ Cuenta de Vercel (gratis en [vercel.com](https://vercel.com))
- ✅ Google Gemini API Key ([obtener aquí](https://makersuite.google.com/app/apikey))
- ✅ Tu repositorio: `https://github.com/SebaGRT/Hackathon2025.git`

## 🎯 Método 1: Despliegue desde el Dashboard de Vercel (Recomendado)

### Paso 1: Crear cuenta en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Click en **"Sign Up"**
3. Elige **"Continue with GitHub"**
4. Autoriza a Vercel para acceder a tus repositorios

### Paso 2: Importar tu Proyecto

1. En el dashboard de Vercel, click en **"Add New..."** → **"Project"**
2. Busca tu repositorio: `Hackathon2025`
3. Click en **"Import"**

### Paso 3: Configurar el Proyecto

Vercel detectará automáticamente que es un proyecto Python/Django.

**Framework Preset:** Debería detectar "Other" (está bien)

**Root Directory:** Déjalo como está (`.`)

**Build Command:** 
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Output Directory:** Déjalo vacío

**Install Command:** 
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

**MUY IMPORTANTE:** Antes de hacer deploy, configura las variables de entorno.

Click en **"Environment Variables"** y agrega:

| Name | Value | Environment |
|------|-------|-------------|
| `SECRET_KEY` | `tu-django-secret-key-super-secreta-aqui` | Production |
| `GEMINI_API_KEY` | `tu-gemini-api-key-aqui` | Production |
| `VERCEL_ENV` | `production` | Production |

#### Cómo generar un SECRET_KEY seguro:

```python
# En tu terminal local, ejecuta Python:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Cómo obtener GEMINI_API_KEY:

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click en **"Get API Key"**
3. Selecciona **"Create API key in new project"** o usa un proyecto existente
4. Copia la API key generada
5. Pégala en Vercel

### Paso 5: Deploy

1. Revisa que todo esté configurado correctamente
2. Click en **"Deploy"**
3. Espera 2-5 minutos mientras Vercel:
   - Clona tu repositorio
   - Instala las dependencias
   - Ejecuta collectstatic
   - Despliega tu app

### Paso 6: Verificar el Despliegue

1. Una vez completado, verás **"Congratulations!"**
2. Click en **"Visit"** o copia la URL (será algo como `https://hackathon2025-xxx.vercel.app`)
3. Verifica que la aplicación cargue correctamente

---

## 🖥️ Método 2: Despliegue con Vercel CLI

### Paso 1: Instalar Vercel CLI

```bash
npm install -g vercel
```

O con yarn:
```bash
yarn global add vercel
```

### Paso 2: Login

```bash
vercel login
```

Sigue las instrucciones en tu navegador para autenticarte.

### Paso 3: Configurar Variables de Entorno

Desde la raíz de tu proyecto:

```bash
cd ~/Documents/Hackathon

# Agregar SECRET_KEY
vercel env add SECRET_KEY production
# Pega tu secret key cuando se te pida

# Agregar GEMINI_API_KEY
vercel env add GEMINI_API_KEY production
# Pega tu Gemini API key cuando se te pida

# Agregar VERCEL_ENV
vercel env add VERCEL_ENV production
# Escribe: production
```

### Paso 4: Deploy

```bash
# Deploy en modo producción
vercel --prod
```

Vercel te preguntará:
- **Set up and deploy?** → `Y`
- **Which scope?** → Selecciona tu cuenta
- **Link to existing project?** → `N` (primera vez) o `Y` (deploy subsecuente)
- **What's your project's name?** → `hackathon2025` (o el nombre que prefieras)
- **In which directory is your code located?** → `./` (presiona Enter)

### Paso 5: Esperar y Verificar

Vercel mostrará el progreso en la terminal y al final te dará la URL de tu app desplegada.

---

## 🔧 Configuración Adicional

### Agregar Dominio Personalizado

1. En el dashboard de Vercel, ve a tu proyecto
2. Click en **"Settings"** → **"Domains"**
3. Agrega tu dominio personalizado
4. Sigue las instrucciones de DNS que Vercel te proporciona

### Configurar Base de Datos (Opcional pero Recomendado)

SQLite no funciona bien en Vercel (es read-only). Para producción, usa PostgreSQL:

#### Opción A: Vercel Postgres

1. En tu proyecto en Vercel, ve a **"Storage"**
2. Click en **"Create Database"** → **"Postgres"**
3. Sigue el wizard de configuración
4. Vercel agregará automáticamente `POSTGRES_URL` a tus variables de entorno

Luego actualiza `settings.py`:

```python
import dj_database_url

if PRODUCTION:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('POSTGRES_URL'),
            conn_max_age=600
        )
    }
```

Y agrega a `requirements.txt`:
```
dj-database-url
psycopg2-binary
```

#### Opción B: Supabase (Gratis)

1. Crea una cuenta en [supabase.com](https://supabase.com)
2. Crea un nuevo proyecto
3. Copia la connection string de PostgreSQL
4. Agrégala como variable de entorno `DATABASE_URL` en Vercel

### Configurar Almacenamiento de Media Files

Vercel no persiste archivos subidos. Usa un servicio externo:

#### Cloudinary (Recomendado)

1. Crea cuenta en [cloudinary.com](https://cloudinary.com)
2. Instala la librería:
```bash
pip install django-cloudinary-storage
```

3. Agrega a `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'cloudinary_storage',
    'cloudinary',
    # ...
]

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

4. Agrega las variables de entorno en Vercel:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

---

## 🐛 Troubleshooting

### Error: "Application error"

**Solución:**
1. Ve a tu proyecto en Vercel → **"Deployments"**
2. Click en el deployment más reciente → **"View Function Logs"**
3. Revisa los logs para ver el error específico

### Error: "ModuleNotFoundError"

**Solución:**
- Asegúrate de que todas las dependencias estén en `requirements.txt`
- Haz commit y push de los cambios
- Vercel re-desplegará automáticamente

### Error: "Database is locked" o "Attempt to write a readonly database"

**Solución:**
- SQLite no funciona en Vercel
- Migra a PostgreSQL (ver sección "Configurar Base de Datos")

### Las imágenes no se guardan

**Solución:**
- Vercel es serverless y no persiste archivos
- Configura Cloudinary u otro servicio de almacenamiento (ver sección anterior)

### CSRF Verification Failed

**Solución:**
Asegúrate de que tu dominio de Vercel esté en `CSRF_TRUSTED_ORIGINS`:

```python
# settings.py
CSRF_TRUSTED_ORIGINS = [
    'https://tu-app.vercel.app',
    'https://*.vercel.app',
]
```

### Error 500 en producción pero funciona local

**Solución:**
1. Revisa los logs en Vercel
2. Asegúrate de que `DEBUG = False` en producción
3. Verifica que todas las variables de entorno estén configuradas
4. Ejecuta `python manage.py check --deploy` localmente

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
vercel logs --follow
```

### Ver Logs desde el Dashboard

1. Ve a tu proyecto en Vercel
2. Click en **"Deployments"**
3. Selecciona un deployment
4. Click en **"View Function Logs"** o **"Runtime Logs"**

### Métricas

En el dashboard de Vercel, puedes ver:
- Número de requests
- Response time
- Error rate
- Bandwidth usage

---

## 🔄 Actualizar la Aplicación

### Despliegue Automático

Cada vez que hagas `git push` a la rama `main`, Vercel desplegará automáticamente:

```bash
git add .
git commit -m "Update: descripción de cambios"
git push origin main
```

### Despliegue Manual con CLI

```bash
vercel --prod
```

### Rollback a una Versión Anterior

1. En Vercel Dashboard → **"Deployments"**
2. Encuentra el deployment que funcionaba
3. Click en **"..."** → **"Promote to Production"**

---

## ✅ Checklist Final

Antes de compartir tu app en producción:

- [ ] Todas las variables de entorno están configuradas
- [ ] `DEBUG = False` en producción
- [ ] Secret key es seguro y único
- [ ] Base de datos de producción configurada (si aplica)
- [ ] Almacenamiento de media configurado (Cloudinary, etc.)
- [ ] ALLOWED_HOSTS incluye tu dominio de Vercel
- [ ] CSRF_TRUSTED_ORIGINS configurado correctamente
- [ ] Probaste la funcionalidad principal (captura de foto, análisis IA)
- [ ] Revisaste los logs para asegurarte de que no hay errores
- [ ] La app carga rápido y funciona en móviles

---

## 🎉 ¡Felicidades!

Tu aplicación CChC SafeApp está ahora desplegada en Vercel y accesible desde cualquier parte del mundo.

**URL de tu app:** `https://tu-proyecto.vercel.app`

### Próximos Pasos

1. **Comparte la URL** con tu equipo o stakeholders
2. **Monitorea los logs** en las primeras horas
3. **Configura alertas** en Vercel para errores
4. **Agrega Google Analytics** si necesitas métricas de uso
5. **Considera un dominio personalizado** para mayor profesionalismo

---

## 📞 Soporte

- **Documentación de Vercel:** https://vercel.com/docs
- **Documentación de Django:** https://docs.djangoproject.com/
- **Google Gemini API:** https://ai.google.dev/

¡Buena suerte con tu proyecto! 🚀