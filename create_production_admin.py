#!/usr/bin/env python
"""
Script to create a production admin user for SafeSite on Vercel.

Usage:
    1. Set environment variables:
       export POSTGRES_URL="your-postgres-connection-string"
       export VERCEL_ENV="production"

    2. Run the script:
       python create_production_admin.py
"""

import os
import sys

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model

from seguridad.models import PerfilUsuario

User = get_user_model()


def create_admin_user():
    """Create a superuser with admin privileges."""

    print("=" * 60)
    print("SafeSite Production Admin User Creator")
    print("=" * 60)
    print()

    # Check if running in production
    if os.getenv("VERCEL_ENV") != "production":
        print("⚠️  Warning: VERCEL_ENV is not set to 'production'")
        print(f"   Current value: {os.getenv('VERCEL_ENV')}")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != "y":
            print("❌ Aborted.")
            return
        print()

    # Check database connection
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        print()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure POSTGRES_URL is set correctly:")
        print("  export POSTGRES_URL='postgres://user:pass@host:5432/db'")
        return

    # Get admin credentials
    print("Enter admin credentials:")
    username = input("Username [admin]: ").strip() or "admin"
    email = input("Email [admin@safesite.com]: ").strip() or "admin@safesite.com"

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"\n⚠️  User '{username}' already exists!")
        user = User.objects.get(username=username)
        print(f"   Email: {user.email}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")

        response = input("\nUpdate this user to admin? (y/N): ")
        if response.lower() == "y":
            user.is_staff = True
            user.is_superuser = True
            user.save()

            # Ensure profile exists with SUPERVISOR role
            try:
                profile = user.perfil
                profile.rol = "SUPERVISOR"
                profile.save()
                print(f"✅ User '{username}' updated to admin/supervisor")
            except PerfilUsuario.DoesNotExist:
                PerfilUsuario.objects.create(user=user, rol="SUPERVISOR")
                print(f"✅ User '{username}' updated with supervisor profile")

            print(f"\n✅ Admin user ready: {username}")
        else:
            print("❌ Aborted.")
        return

    # Create new admin user
    import getpass

    while True:
        password = getpass.getpass("Password: ")
        password2 = getpass.getpass("Password (again): ")

        if password != password2:
            print("❌ Passwords don't match. Try again.\n")
            continue

        if len(password) < 8:
            print("❌ Password must be at least 8 characters. Try again.\n")
            continue

        break

    try:
        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )

        print(f"\n✅ Superuser created: {username}")

        # Check if profile was auto-created by signal
        try:
            profile = user.perfil
            if profile.rol != "SUPERVISOR":
                profile.rol = "SUPERVISOR"
                profile.save()
                print(f"✅ Profile updated to SUPERVISOR role")
            else:
                print(f"✅ Profile auto-created with SUPERVISOR role")
        except PerfilUsuario.DoesNotExist:
            # Create profile manually if signal didn't work
            PerfilUsuario.objects.create(user=user, rol="SUPERVISOR")
            print(f"✅ Profile created with SUPERVISOR role")

        print()
        print("=" * 60)
        print("Admin User Created Successfully!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Role: SUPERVISOR")
        print()
        print("You can now login at:")
        print("  • https://your-app.vercel.app/login/")
        print("  • https://your-app.vercel.app/admin/")
        print()

    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        import traceback

        traceback.print_exc()


def list_existing_users():
    """List all existing users."""
    print("\nExisting users:")
    print("-" * 60)
    users = User.objects.all()

    if not users.exists():
        print("No users found in database.")
        return

    for user in users:
        try:
            role = user.perfil.get_rol_display()
        except:
            role = "No profile"

        status = []
        if user.is_superuser:
            status.append("SUPERUSER")
        if user.is_staff:
            status.append("STAFF")
        if user.is_active:
            status.append("ACTIVE")
        else:
            status.append("INACTIVE")

        print(f"  {user.username:<20} {user.email:<30} {role:<15} {', '.join(status)}")
    print("-" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create production admin user")
    parser.add_argument("--list", action="store_true", help="List existing users")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Create admin/admin with default password (NOT for production!)",
    )

    args = parser.parse_args()

    if args.list:
        list_existing_users()
    elif args.quick:
        print("Creating quick admin user (admin/admin123)...")
        print("⚠️  THIS IS NOT SECURE - CHANGE PASSWORD IMMEDIATELY!")

        try:
            if User.objects.filter(username="admin").exists():
                print("❌ User 'admin' already exists")
                sys.exit(1)

            user = User.objects.create_superuser(
                username="admin",
                email="admin@safesite.com",
                password="admin123",
                is_staff=True,
                is_superuser=True,
            )

            try:
                profile = user.perfil
                profile.rol = "SUPERVISOR"
                profile.save()
            except:
                PerfilUsuario.objects.create(user=user, rol="SUPERVISOR")

            print("✅ Quick admin created: admin/admin123")
            print("⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        create_admin_user()
