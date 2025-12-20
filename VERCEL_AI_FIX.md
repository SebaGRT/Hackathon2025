# Vercel AI Fix Guide

## Problem
When deploying to Vercel, image analysis fails with a 500 error due to:
1. Read-only filesystem (except `/tmp`)
2. Missing environment variables
3. File path issues with media uploads

## Solutions Implemented

### 1. Fixed File Storage (✅ DONE)
Changed from `default_storage.path()` to `/tmp` directory:
- Updated `views.py` to use `tempfile.gettempdir()`
- Files are now saved to `/tmp` which is writable on Vercel
- Temporary files are cleaned up after analysis

### 2. Enhanced Error Logging (✅ DONE)
Added comprehensive debug logging to track issues:
- File existence checks
- File size verification
- API call tracing
- Error stacktraces

### 3. Better Error Handling (✅ DONE)
- Try-catch blocks in view
- Graceful error messages displayed to user
- Fallback responses when AI fails

## Required Configuration on Vercel

### Environment Variables
You **MUST** set these in your Vercel project settings:

1. **GEMINI_API_KEY** (Required)
   ```
   Your Google Gemini API key from https://aistudio.google.com/app/apikey
   ```

2. **SECRET_KEY** (Required)
   ```
   Django secret key (generate a secure random string)
   ```

3. **DEBUG** (Recommended)
   ```
   False
   ```

4. **ALLOWED_HOSTS** (Required)
   ```
   .vercel.app,yourdomain.com
   ```

### How to Set Environment Variables in Vercel

#### Option 1: Via Vercel Dashboard
1. Go to your project in Vercel
2. Click "Settings" → "Environment Variables"
3. Add each variable:
   - Name: `GEMINI_API_KEY`
   - Value: `your-api-key-here`
   - Environment: Production, Preview, Development
4. Click "Save"
5. Redeploy your application

#### Option 2: Via Vercel CLI
```bash
vercel env add GEMINI_API_KEY
# Paste your API key when prompted

vercel env add SECRET_KEY
# Paste your secret key when prompted

# Redeploy
vercel --prod
```

## Verifying the Fix

### 1. Check Vercel Logs
After deploying, check the logs to see debug output:
```bash
vercel logs --follow
```

Look for:
- `[DEBUG] Analizando fotos desde ruta: /tmp/...`
- `[DEBUG] Archivo existe: True`
- `[DEBUG] Imagen leída: XXXX bytes`
- `[DEBUG] Respuesta recibida de Gemini`

### 2. Test Image Analysis
1. Go to your deployed app
2. Navigate to "Nuevo Registro"
3. Upload or capture an image
4. Submit for analysis

If successful, you should see:
- Analysis results appear
- No 500 error
- AI description of the image

### 3. Common Error Messages

#### Error: "El archivo de imagen no se encontró"
**Cause:** File wasn't saved to `/tmp` properly
**Fix:** Check file upload is working, verify request.FILES contains the image

#### Error: "Error al parsear respuesta de IA"
**Cause:** Gemini returned invalid JSON
**Fix:** Check API key is valid, check Gemini API quota

#### Error: "Error al analizar la imagen: [API Error]"
**Cause:** Gemini API key missing or invalid
**Fix:** 
1. Verify `GEMINI_API_KEY` is set in Vercel environment variables
2. Verify the API key is valid and has quota
3. Test API key locally first

## Testing Locally Before Deploy

Test the `/tmp` fix locally:
```bash
# Set environment variable
export GEMINI_API_KEY="your-key-here"

# Run Django
python manage.py runserver

# Upload an image and check logs
```

You should see debug output like:
```
[DEBUG] Iniciando análisis de imagen...
[DEBUG] Imagen recibida: photo.jpg, tamaño: 123456 bytes
[DEBUG] Guardando en: /tmp/temp_1234567890.123_photo.jpg
[DEBUG] Archivo guardado, tamaño: 123456 bytes
[DEBUG] Llamando a analisis_fotos...
[DEBUG] Analizando fotos desde ruta: /tmp/temp_1234567890.123_photo.jpg
[DEBUG] Archivo existe: True
[DEBUG] Abriendo archivo de imagen...
[DEBUG] Imagen leída: 123456 bytes
[DEBUG] Enviando solicitud a Gemini API...
[DEBUG] Respuesta recibida de Gemini
[DEBUG] JSON parseado exitosamente: {...}
```

## Production Database Note

⚠️ **Important:** SQLite won't work on Vercel in production!

You'll need to:
1. Set up PostgreSQL (Vercel Postgres, Supabase, or Neon)
2. Update `settings.py` to use `dj-database-url`
3. Set `DATABASE_URL` environment variable in Vercel

## Media Files Note

⚠️ **Important:** Uploaded files are ephemeral on Vercel!

For production, integrate external storage:
- **Cloudinary** (Recommended for images)
- **Vercel Blob**
- **AWS S3**

Add to `requirements.txt`:
```
django-cloudinary-storage
```

Update `settings.py`:
```python
if os.getenv('VERCEL_ENV'):
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
        'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

## Summary Checklist

- [x] Code updated to use `/tmp` directory
- [x] Error logging added
- [x] Error handling improved
- [ ] Set `GEMINI_API_KEY` in Vercel
- [ ] Set `SECRET_KEY` in Vercel
- [ ] Set `ALLOWED_HOSTS` in Vercel
- [ ] Test image analysis on Vercel
- [ ] Check Vercel logs for errors
- [ ] (Optional) Migrate to PostgreSQL
- [ ] (Optional) Add Cloudinary for media storage

## Need Help?

If still getting errors:
1. Check Vercel logs: `vercel logs --follow`
2. Look for `[ERROR]` messages
3. Verify all environment variables are set
4. Test API key independently at https://aistudio.google.com
5. Check Gemini API quota/billing

Good luck! 🚀