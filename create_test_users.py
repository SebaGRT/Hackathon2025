#!/usr/bin/env python
"""
Script to create test users for SafeSite application
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User

from seguridad.models import PerfilUsuario


def create_test_users():
    """Create test users for the application"""

    # Create supervisor user
    if not User.objects.filter(username="supervisor").exists():
        supervisor = User.objects.create_user(
            username="supervisor",
            password="supervisor123",
            email="supervisor@safesite.com",
            first_name="Juan",
            last_name="Pérez",
        )
        PerfilUsuario.objects.create(user=supervisor, rol="SUPERVISOR")
        print("✅ Created supervisor user")
        print("   Username: supervisor")
        print("   Password: supervisor123")
        print("   Role: SUPERVISOR")
    else:
        print("ℹ️  Supervisor user already exists")

    # Create trabajador user
    if not User.objects.filter(username="trabajador").exists():
        trabajador = User.objects.create_user(
            username="trabajador",
            password="trabajador123",
            email="trabajador@safesite.com",
            first_name="María",
            last_name="González",
        )
        PerfilUsuario.objects.create(user=trabajador, rol="TRABAJADOR")
        print("\n✅ Created trabajador user")
        print("   Username: trabajador")
        print("   Password: trabajador123")
        print("   Role: TRABAJADOR")
    else:
        print("ℹ️  Trabajador user already exists")

    print("\n" + "=" * 50)
    print("📝 TEST CREDENTIALS")
    print("=" * 50)
    print("Supervisor:")
    print("  Username: supervisor")
    print("  Password: supervisor123")
    print("\nTrabajador:")
    print("  Username: trabajador")
    print("  Password: trabajador123")
    print("=" * 50)


if __name__ == "__main__":
    create_test_users()
