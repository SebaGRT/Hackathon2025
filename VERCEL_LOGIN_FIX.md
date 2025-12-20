# Quick Fix: Can't Login on Vercel Deployment

## Problem
You can't login because **SQLite doesn't work on Vercel**. The database is reset on every deployment, so any users you create disappear.

## Solution: Switch to PostgreSQL

Follow these steps to fix login on your Vercel deployment:

---

## Step 1: Add PostgreSQL Database (5 minutes)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Select your SafeSite project

2. **Create Postgres Database**
   - Click on "Storage" tab
   - Click "Create Database"
   - Select "Postgres"
   - Name it: `safesite-db`
   - Click "Create"

3. **Connect to Project**
   - After creation, click "Connect Project"
   - Select your SafeSite project
   - Click "Connect"

4. **Copy Environment Variables**
   - Vercel will automatically add these to your project:
     - `POSTGRES_URL`
     - `POSTGRES_PRISMA_URL`
     - `POSTGRES_URL_NON_POOLING`
     - Other Postgres variables

---

## Step 2: Update Code (Already Done!)

The following files have been updated to support PostgreSQL:

✅ `core/settings.py` - Database configuration  
✅ `requirements.txt` - Added PostgreSQL drivers  
✅ `build.sh` - Build script with migrations  
✅ `vercel.json` - Build configuration

**You just need to commit and push:**

```bash
cd /home/sebacc/Documents/Hackathon
git add .
git commit -m "Add PostgreSQL support for Vercel"
git push origin main
```

---

## Step 3: Wait for Deployment

Vercel will automatically:
1. Install dependencies (including PostgreSQL driver)
2. Run `build.sh` which:
   - Collects static files
   - Runs database migrations

Monitor the deployment at: https://vercel.com/dashboard

---

## Step 4: Create Admin User

After deployment succeeds, create an admin user:

### Method 1: Using the Script (Recommended)

```bash
# Set environment variables (get POSTGRES_URL from Vercel dashboard)
export POSTGRES_URL="postgres://your-connection-string-from-vercel"
export VERCEL_ENV="production"

# Run the script
cd /home/sebacc/Documents/Hackathon
python create_production_admin.py
```

Follow the prompts to create your admin user.

### Method 2: Quick Admin (For Testing Only)

```bash
# Creates admin/admin123 - NOT SECURE!
export POSTGRES_URL="postgres://your-connection-string-from-vercel"
export VERCEL_ENV="production"
python create_production_admin.py --quick
```

⚠️ **Change the password immediately after login!**

### Method 3: Via Vercel Postgres SQL Editor

1. Go to Vercel Dashboard → Storage → Your Database
2. Click "Data" tab
3. Run these SQL commands:

```sql
-- First, check if migrations ran
SELECT * FROM django_migrations LIMIT 5;

-- Create admin user (change password!)
INSERT INTO auth_user (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES ('pbkdf2_sha256$870000$CHANGE_THIS$hash', NULL, true, 'admin', '', '', 'admin@safesite.com', true, true, NOW());

-- Get the user ID
SELECT id FROM auth_user WHERE username = 'admin';

-- Create profile (use the ID from above)
INSERT INTO seguridad_perfilusuario (user_id, rol, fecha_creacion)
VALUES (1, 'SUPERVISOR', NOW());
```

**Note:** For Method 3, you'll need to manually hash the password or use Django shell.

---

## Step 5: Test Login

1. **Visit your app:**
   ```
   https://your-app.vercel.app/login/
   ```

2. **Login with your credentials**
   - Username: admin (or what you created)
   - Password: (what you set)

3. **Access dashboard:**
   ```
   https://your-app.vercel.app/dashboard/
   ```

4. **Access admin panel:**
   ```
   https://your-app.vercel.app/admin/
   ```

---

## Troubleshooting

### Error: "CSRF verification failed"

**Fix:** Add your Vercel URL to allowed origins.

If your app is at `https://safesite-xyz.vercel.app`, the code already handles it:

```python
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://*.now.sh",
]
```

This is already in `settings.py` ✅

### Error: "No such table: auth_user"

**Fix:** Migrations didn't run. Check build logs:

```bash
vercel logs your-deployment-url
```

If migrations failed, run manually:

```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"
python manage.py migrate
```

### Error: "Can't connect to database"

**Check:**
1. Is `POSTGRES_URL` set in Vercel environment variables?
2. Go to Vercel Dashboard → Settings → Environment Variables
3. Verify `POSTGRES_URL` exists

### Error: "User has no profile"

**Fix:** Create the profile:

```bash
export POSTGRES_URL="your-postgres-url"
export VERCEL_ENV="production"python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth.models import User
from seguridad.models import PerfilUsuario
user = User.objects.get(username='admin')
PerfilUsuario.objects.create(user=user, rol='SUPERVISOR')
print('✅ Profile created')
"
```

---

## Important Notes

### ✅ What Works Now:
- PostgreSQL database (persistent across deployments)
- User accounts persist
- Sessions work properly
- Login/logout functionality

### ❌ What Still Won't Work:
- **File uploads** - Vercel filesystem is read-only
  - Media files uploaded via forms will disappear
  - Solution: Use Vercel Blob, S3, or Cloudinary

### 🔒 Security:
- Change default passwords immediately
- Use strong passwords for production
- Keep `SECRET_KEY` in environment variables
- Never commit database credentials

---

## Quick Reference: Get Postgres URL

1. **Via Vercel Dashboard:**
   - Go to Storage → Your Database
   - Click ".env.local" tab
   - Copy `POSTGRES_URL` value

2. **Via Vercel CLI:**
   ```bash
   vercel env pull .env.production
   cat .env.production | grep POSTGRES_URL
   ```

---

## After Setup Checklist

- [ ] PostgreSQL database created on Vercel
- [ ] Code pushed to repository
- [ ] Deployment succeeded (check Vercel dashboard)
- [ ] Build logs show migrations ran successfully
- [ ] Admin user created
- [ ] Can login at `/login/`
- [ ] Can access dashboard at `/dashboard/`
- [ ] Can access admin at `/admin/`
- [ ] Password changed from default (if using quick method)

---

## Need More Help?

See the full deployment guide: `VERCEL_SETUP.md`

Or check Vercel logs:
```bash
vercel logs
```

---

**Last Updated:** December 20, 2024  
**Status:** Ready to deploy with PostgreSQL ✅