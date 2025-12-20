# Vercel Quick Reference Card

## 🚨 Login Issue? Start Here

**Problem:** Can't login on Vercel deployment  
**Cause:** SQLite doesn't work on Vercel (filesystem is ephemeral)  
**Solution:** Use PostgreSQL (see steps below)

---

## Quick Setup (5 Minutes)

### 1. Create Postgres Database
```
Vercel Dashboard → Storage → Create Database → Postgres
Name: safesite-db
```

### 2. Deploy Changes
```bash
cd /home/sebacc/Documents/Hackathon
git add .
git commit -m "Add PostgreSQL support"
git push origin main
```

### 3. Create Admin User
```bash
# Get POSTGRES_URL from: Vercel Dashboard → Storage → Database → .env.local
export POSTGRES_URL="postgres://..."
export VERCEL_ENV="production"
python create_production_admin.py
```

### 4. Login
```
https://your-app.vercel.app/login/
```

---

## Common Commands

### Deploy
```bash
# Via Git (automatic)
git push origin main

# Via CLI (manual)
vercel --prod
```

### View Logs
```bash
vercel logs
vercel logs --follow  # Live logs
```

### Pull Environment Variables
```bash
vercel env pull .env.production
cat .env.production
```

### List Deployments
```bash
vercel list
```

### Rollback
```bash
vercel rollback
```

---

## Database Management

### Run Migrations
```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"
python manage.py migrate
```

### Create Superuser
```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"
python create_production_admin.py
```

### List Users
```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"
python create_production_admin.py --list
```

### Django Shell (Production DB)
```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"
python manage.py shell
```

---

## Environment Variables

### Required for SafeSite:
- `POSTGRES_URL` - Database connection (auto-added by Vercel)
- `SECRET_KEY` - Django secret (generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `GEMINI_API_KEY` - Google Gemini API key
- `VERCEL_ENV` - Environment identifier (auto-set by Vercel)

### Set via Dashboard:
```
Vercel Dashboard → Project → Settings → Environment Variables
```

### Set via CLI:
```bash
vercel env add SECRET_KEY
vercel env add GEMINI_API_KEY
```

---

## Troubleshooting

### "CSRF verification failed"
**Fix:** Already configured in settings.py
```python
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
```

### "Can't connect to database"
**Check:** 
```bash
vercel env ls  # List environment variables
```
Ensure `POSTGRES_URL` exists.

### "No such table: auth_user"
**Fix:** Migrations didn't run
```bash
# Check build logs
vercel logs your-deployment-url

# Run manually
export POSTGRES_URL="..."
python manage.py migrate
```

### "User has no profile"
**Fix:** Profile wasn't created
```bash
export POSTGRES_URL="..."
export VERCEL_ENV="production"
python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()
from django.contrib.auth.models import User
from seguridad.models import PerfilUsuario
user = User.objects.get(username='admin')
PerfilUsuario.objects.create(user=user, rol='SUPERVISOR')
"
```

### "Internal Server Error (500)"
**Check logs:**
```bash
vercel logs --follow
```

---

## File Structure

```
Hackathon/
├── build.sh                    # Vercel build script
├── vercel.json                 # Vercel configuration
├── vercel_app.py              # WSGI entry point
├── create_production_admin.py # Admin user script
├── requirements.txt           # Python dependencies
├── core/
│   └── settings.py            # Django settings (prod/dev split)
└── seguridad/
    └── ...                    # App files
```

---

## Important URLs

| Purpose | URL |
|---------|-----|
| Dashboard | `https://vercel.com/dashboard` |
| Project Settings | `https://vercel.com/[team]/[project]/settings` |
| Storage (Database) | `https://vercel.com/[team]/stores` |
| Deployments | `https://vercel.com/[team]/[project]/deployments` |
| Logs | `https://vercel.com/[team]/[project]/logs` |

---

## Production vs Development

| Feature | Local (Dev) | Vercel (Prod) |
|---------|-------------|---------------|
| Database | SQLite | PostgreSQL |
| Debug | ON | OFF |
| Static files | Dev server | Collected |
| Sessions | File-based | Database |
| SSL | No | Yes (enforced) |

---

## Best Practices

✅ **DO:**
- Use environment variables for secrets
- Test locally before deploying
- Monitor build logs after deployment
- Use strong passwords
- Keep dependencies updated

❌ **DON'T:**
- Commit `SECRET_KEY` or database credentials
- Use `DEBUG = True` in production
- Store sensitive data in code
- Use weak passwords
- Upload large files to repo

---

## Quick Checks

### Is deployment successful?
```bash
curl -I https://your-app.vercel.app
# Should return: HTTP/2 200
```

### Is database connected?
```bash
export POSTGRES_URL="..."
python manage.py dbshell
# Should connect to Postgres
```

### Are migrations current?
```bash
export POSTGRES_URL="..."
python manage.py showmigrations
# All should have [X]
```

---

## Emergency: Reset Everything

```bash
# 1. Delete all deployments
vercel remove [project-name] --yes

# 2. Delete database
# Via Dashboard: Storage → Database → Settings → Delete

# 3. Redeploy
git push origin main

# 4. Recreate database & users
# Follow "Quick Setup" above
```

---

## Get Help

- **Full Guide:** `VERCEL_SETUP.md`
- **Login Fix:** `VERCEL_LOGIN_FIX.md`
- **Vercel Docs:** https://vercel.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/5.0/howto/deployment/

---

**Last Updated:** December 20, 2024  
**Version:** 1.0