# Vercel Deployment Guide for SafeSite

This guide will help you deploy the SafeSite Django application to Vercel with a PostgreSQL database.

## Prerequisites

- Vercel account (sign up at https://vercel.com)
- Vercel CLI installed (`npm i -g vercel`)
- Git repository connected to Vercel

## Step 1: Set Up Vercel Postgres Database

1. **Go to your Vercel Dashboard**
   - Navigate to https://vercel.com/dashboard

2. **Create a Postgres Database**
   - Go to the "Storage" tab
   - Click "Create Database"
   - Select "Postgres"
   - Choose a name (e.g., `safesite-db`)
   - Select your preferred region
   - Click "Create"

3. **Get Database Credentials**
   - After creation, go to the database settings
   - Copy the `POSTGRES_URL` connection string
   - It should look like: `postgres://user:pass@host:5432/db`

## Step 2: Configure Environment Variables

In your Vercel project settings:

1. **Go to Project Settings → Environment Variables**

2. **Add the following variables:**

   ```
   POSTGRES_URL = <your-postgres-connection-string>
   SECRET_KEY = <generate-a-random-secret-key>
   VERCEL_ENV = production
   GEMINI_API_KEY = <your-gemini-api-key>
   ```

3. **Generate a SECRET_KEY:**
   ```python
   # Run this in Python to generate a secure key
   import secrets
   print(secrets.token_urlsafe(50))
   ```

4. **Apply to all environments** (Production, Preview, Development)

## Step 3: Deploy to Vercel

### Option A: Deploy via Git (Recommended)

1. **Connect your repository to Vercel:**
   ```bash
   vercel link
   ```

2. **Push to your repository:**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

3. **Vercel will automatically deploy**

### Option B: Deploy via CLI

1. **Deploy directly:**
   ```bash
   cd /home/sebacc/Documents/Hackathon
   vercel --prod
   ```

2. **Follow the prompts**

## Step 4: Run Database Migrations

After deployment, you need to run migrations on the production database.

### Method 1: Using Vercel CLI (Recommended)

```bash
# Set environment variables locally
export POSTGRES_URL="your-postgres-url-from-vercel"
export VERCEL_ENV="production"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Method 2: Using Vercel Serverless Function

The build script (`build.sh`) automatically runs migrations during deployment.

## Step 5: Create Admin User

Since you can't run `createsuperuser` interactively on Vercel, use one of these methods:

### Option 1: Local Connection to Production DB

```bash
# Set production database URL
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"

# Create superuser
python manage.py createsuperuser
```

### Option 2: Create via Django Shell Script

Create a file `create_admin.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from seguridad.models import PerfilUsuario

User = get_user_model()

# Create superuser
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@safesite.com',
        password='ChangeThisPassword123!',
        is_staff=True,
        is_superuser=True
    )
    print(f"✅ Superuser created: {user.username}")
else:
    print("❌ Superuser already exists")
```

Run it:
```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"
python create_admin.py
```

### Option 3: Use Django Admin Panel

If you have at least one user, you can promote them via SQL:

```sql
-- Connect to your Vercel Postgres database
UPDATE auth_user 
SET is_staff = true, is_superuser = true 
WHERE username = 'your-username';
```

## Step 6: Create Test Users

After creating the admin, you can create test users via the admin panel:

1. Go to `https://your-app.vercel.app/admin/`
2. Login with your admin credentials
3. Navigate to "Users" → "Add User"
4. Create users with different roles:
   - **Supervisor:** Check "Staff status"
   - **Trabajador:** Leave "Staff status" unchecked

## Step 7: Verify Deployment

1. **Check the main site:**
   ```
   https://your-app.vercel.app/
   ```

2. **Test login:**
   ```
   https://your-app.vercel.app/login/
   ```

3. **Access admin panel:**
   ```
   https://your-app.vercel.app/admin/
   ```

4. **Test dashboard (Supervisor only):**
   ```
   https://your-app.vercel.app/dashboard/
   ```

## Troubleshooting

### Issue: "CSRF verification failed"

**Solution:** Make sure your deployment URL is in `CSRF_TRUSTED_ORIGINS`:

In `settings.py`, the following should handle it:
```python
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.now.sh",
]
```

If you have a custom domain, add it:
```python
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://your-domain.com",
]
```

### Issue: "Can't connect to database"

**Check:**
1. Environment variable `POSTGRES_URL` is set correctly
2. Database is in the same region as your deployment
3. Connection string format is correct

### Issue: "Static files not loading"

**Solution:** 
1. Ensure `build.sh` runs `collectstatic`
2. Check static files configuration in `settings.py`
3. Verify `STATIC_ROOT` is set to `staticfiles`

### Issue: "No users exist / Can't login"

**Solution:**
1. Check database is connected (not using SQLite)
2. Run migrations on production database
3. Create superuser using methods above
4. Verify `PerfilUsuario` is created for each user

### Issue: "Internal Server Error (500)"

**Check Vercel Logs:**
```bash
vercel logs your-deployment-url
```

Common causes:
- Missing environment variables
- Database migration not run
- Static files not collected
- Import errors

## Important Notes

### Database Persistence

✅ **Vercel Postgres:** Data persists across deployments  
❌ **SQLite:** Does NOT work on Vercel (ephemeral filesystem)

### Sessions

The app is configured to use database-backed sessions in production:
```python
SESSION_ENGINE = "django.contrib.sessions.backends.db"
```

### File Uploads

Media files uploaded via the app will NOT persist on Vercel's filesystem. For production, you should:

1. Use Vercel Blob Storage
2. Use AWS S3
3. Use Cloudinary

Add to `settings.py`:
```python
if PRODUCTION:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # Configure S3 settings
```

## Security Checklist

Before going live:

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` set in environment variables
- [ ] `ALLOWED_HOSTS` configured properly
- [ ] `CSRF_TRUSTED_ORIGINS` includes your domain
- [ ] SSL enabled (`SECURE_SSL_REDIRECT = True`)
- [ ] Secure cookies enabled
- [ ] Admin password is strong and unique
- [ ] Database credentials are in environment variables (not committed)
- [ ] API keys are in environment variables

## Updating the Deployment

1. **Make changes locally**
2. **Test locally:**
   ```bash
   python manage.py runserver
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

4. **Vercel auto-deploys** from your connected Git repository

## Rollback

If something goes wrong:

1. **Via Vercel Dashboard:**
   - Go to Deployments
   - Find a previous working deployment
   - Click "Promote to Production"

2. **Via CLI:**
   ```bash
   vercel rollback
   ```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_URL` | Database connection string | `postgres://user:pass@host/db` |
| `SECRET_KEY` | Django secret key | `abc123...xyz789` |
| `VERCEL_ENV` | Environment identifier | `production` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `.vercel.app,yourdomain.com` |

## Support

If you encounter issues:

1. Check Vercel logs: `vercel logs`
2. Review Django check: `python manage.py check --deploy`
3. Verify environment variables are set
4. Check database connection
5. Review build logs in Vercel dashboard

## Additional Resources

- [Vercel Django Guide](https://vercel.com/guides/django)
- [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

**Last Updated:** December 20, 2024  
**Deployment Status:** Configured for production with PostgreSQL