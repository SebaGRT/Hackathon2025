# 🔐 SafeSite - Authentication System

## Overview

SafeSite now includes a complete login/logout authentication system with role-based access control.

## User Roles

The system supports two types of users:

- **SUPERVISOR**: Full access to all features including dashboard and reports
- **TRABAJADOR**: Access to create reports and view basic information (NO dashboard access)

## Features

✅ Login page with modern UI matching the app design
✅ Logout functionality (POST request with CSRF protection)
✅ User profile dropdown showing username and role
✅ Login button for unauthenticated users
✅ Success/error messages for authentication actions
✅ Redirect to requested page after login
✅ Role-based access control (Dashboard restricted to Supervisors)
✅ Dashboard link hidden for Trabajadores in all templates

## URLs

- `/login/` - Login page
- `/logout/` - Logout (redirects to home)
- `/dashboard/` - Dashboard (**SUPERVISOR ONLY** - Trabajadores will be redirected with error message)

## Creating Test Users

### Method 1: Using Django Admin

1. Create a superuser (if you haven't already):
```bash
python manage.py createsuperuser
```

2. Run the development server:
```bash
python manage.py runserver
```

3. Go to http://localhost:8000/admin/

4. Create users and their profiles:
   - Navigate to "Users" → "Add user"
   - Set username and password
   - Save and add more information (email, name, etc.)
   - Go to "Perfil usuarios" → "Add perfil usuario"
   - Select the user and assign a role (SUPERVISOR or TRABAJADOR)

### Method 2: Using Django Shell

```bash
python manage.py shell
```

Then run:

```python
from django.contrib.auth.models import User
from seguridad.models import PerfilUsuario

# Create Supervisor
supervisor = User.objects.create_user(
    username='supervisor',
    password='supervisor123',
    email='supervisor@safesite.com',
    first_name='Juan',
    last_name='Pérez'
)
PerfilUsuario.objects.create(user=supervisor, rol='SUPERVISOR')

# Create Trabajador
trabajador = User.objects.create_user(
    username='trabajador',
    password='trabajador123',
    email='trabajador@safesite.com',
    first_name='María',
    last_name='González'
)
PerfilUsuario.objects.create(user=trabajador, rol='TRABAJADOR')

print("Users created successfully!")
```

### Method 3: Using the Provided Script

Run the included script:

```bash
python create_test_users.py
```

This will create:
- **Supervisor**: username: `supervisor` / password: `supervisor123`
- **Trabajador**: username: `trabajador` / password: `trabajador123`

## Testing the Authentication

1. **Start the server**:
```bash
python manage.py runserver
```

2. **Visit the home page**: http://localhost:8000/
   - You should see a "INICIAR SESIÓN" button in the top-right

3. **Click "INICIAR SESIÓN"** or go to http://localhost:8000/login/

4. **Log in with test credentials**:
   - Supervisor: `supervisor` / `supervisor123`
   - Trabajador: `trabajador` / `trabajador123`

5. **After login**, you'll be redirected to the dashboard and see:
   - Your username in the top-right
   - A dropdown menu with your role and logout option

6. **Click your username** to see the profile dropdown with:
   - Username
   - Role (Supervisor/Trabajador)
   - Dashboard link
   - Logout link

## Login Page Features

- **Modern cyberpunk design** matching SafeSite's aesthetic
- **Icon-based inputs** with user and lock icons
- **Error/success messages** displayed prominently
- **Role information** displayed at the bottom
- **Responsive design** works on mobile and desktop

## Security Notes

⚠️ **Important for Production**:

1. **Change default passwords** - The test credentials are only for development
2. **Use strong passwords** - Enforce password policies
3. **Enable HTTPS** - Never transmit credentials over HTTP
4. **Secure SECRET_KEY** - Use environment variables
5. **Set ALLOWED_HOSTS** - Restrict which domains can access your app
6. **Use CSRF protection** - Already enabled by default in Django

## Customization

### Adding Login Required to Views

To protect a view, add the `@login_required` decorator:

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_protected_view(request):
    # Your view code here
    return render(request, 'template.html')
```

### Checking User Role in Views

```python
def my_view(request):
    if request.user.is_authenticated:
        if request.user.perfil.rol == "SUPERVISOR":
            # Supervisor-specific logic
            pass
        else:
            # Trabajador-specific logic
            pass
```

### Checking User Role in Templates

```django
{% if user.is_authenticated %}
    {% if user.perfil.rol == "SUPERVISOR" %}
        <!-- Supervisor-only content -->
    {% else %}
        <!-- Trabajador content -->
    {% endif %}
{% else %}
    <!-- Anonymous user content -->
{% endif %}
```

## Troubleshooting

### "User has no perfil" error

If you get this error, it means a user was created without a PerfilUsuario:

```python
from django.contrib.auth.models import User
from seguridad.models import PerfilUsuario

user = User.objects.get(username='username_here')
PerfilUsuario.objects.create(user=user, rol='TRABAJADOR')
```

### Reset a user's password

```bash
python manage.py changepassword username_here
```

Or in Django shell:
```python
from django.contrib.auth.models import User
user = User.objects.get(username='username_here')
user.set_password('new_password')
user.save()
```

## Future Enhancements

Possible additions to the authentication system:

- [ ] Password reset functionality
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] Social authentication (Google, GitHub, etc.)
- [ ] User registration page
- [ ] Remember me functionality
- [ ] Session timeout
- [ ] Activity logging
- [ ] Password strength requirements
- [ ] Account lockout after failed attempts

---

**Last Updated**: December 2024
**Version**: 1.0