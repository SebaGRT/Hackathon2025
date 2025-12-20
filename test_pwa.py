#!/usr/bin/env python3
"""
Test script to verify PWA setup for SafeSite.
Checks that all necessary files and configurations are in place.
"""

import json
import os
from pathlib import Path


def test_pwa_files():
    """Test that all PWA files exist."""
    print("Testing PWA Files...")
    print("=" * 60)

    base_dir = Path(__file__).parent
    pwa_dir = base_dir / "seguridad" / "static" / "pwa"

    required_files = [
        "manifest.json",
        "sw.js",
        "favicon.svg",
        "apple-touch-icon.svg",
        "icon-72x72.svg",
        "icon-96x96.svg",
        "icon-128x128.svg",
        "icon-144x144.svg",
        "icon-152x152.svg",
        "icon-192x192.svg",
        "icon-384x384.svg",
        "icon-512x512.svg",
    ]

    all_exist = True
    for file in required_files:
        file_path = pwa_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            all_exist = False

    print("=" * 60)
    return all_exist


def test_manifest_json():
    """Test manifest.json structure."""
    print("\nTesting manifest.json...")
    print("=" * 60)

    base_dir = Path(__file__).parent
    manifest_path = base_dir / "seguridad" / "static" / "pwa" / "manifest.json"

    if not manifest_path.exists():
        print("❌ manifest.json not found!")
        return False

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        required_keys = [
            "name",
            "short_name",
            "start_url",
            "display",
            "icons",
            "theme_color",
            "background_color",
        ]

        all_valid = True
        for key in required_keys:
            if key in manifest:
                print(
                    f"✅ {key}: {manifest.get(key)[:50] if isinstance(manifest.get(key), str) else '...'}"
                )
            else:
                print(f"❌ {key} - MISSING!")
                all_valid = False

        # Check icons array
        if "icons" in manifest and isinstance(manifest["icons"], list):
            print(f"\n📱 Icons defined: {len(manifest['icons'])}")
            for icon in manifest["icons"]:
                print(
                    f"   - {icon.get('sizes', 'unknown')} ({icon.get('src', 'no src')})"
                )

        # Check shortcuts
        if "shortcuts" in manifest and isinstance(manifest["shortcuts"], list):
            print(f"\n⚡ Shortcuts defined: {len(manifest['shortcuts'])}")
            for shortcut in manifest["shortcuts"]:
                print(
                    f"   - {shortcut.get('name', 'unnamed')} → {shortcut.get('url', 'no url')}"
                )

        print("=" * 60)
        return all_valid

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        print("=" * 60)
        return False


def test_service_worker():
    """Test service worker file."""
    print("\nTesting service worker...")
    print("=" * 60)

    base_dir = Path(__file__).parent
    sw_path = base_dir / "seguridad" / "static" / "pwa" / "sw.js"

    if not sw_path.exists():
        print("❌ sw.js not found!")
        return False

    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_features = [
        ("install", "Install event handler"),
        ("activate", "Activate event handler"),
        ("fetch", "Fetch event handler"),
        ("CACHE_NAME", "Cache name constant"),
        ("caches.open", "Cache API usage"),
    ]

    all_valid = True
    for feature, description in required_features:
        if feature in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - MISSING!")
            all_valid = False

    # Check file size
    size_kb = len(content) / 1024
    print(f"\n📦 Service worker size: {size_kb:.2f} KB")

    print("=" * 60)
    return all_valid


def test_base_template():
    """Test that base.html includes PWA meta tags."""
    print("\nTesting base.html template...")
    print("=" * 60)

    base_dir = Path(__file__).parent
    template_path = base_dir / "seguridad" / "templates" / "seguridad" / "base.html"

    if not template_path.exists():
        print("❌ base.html not found!")
        return False

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_elements = [
        ('rel="manifest"', "Manifest link"),
        ('name="theme-color"', "Theme color meta tag"),
        ('name="apple-mobile-web-app-capable"', "iOS web app capable"),
        ("serviceWorker", "Service worker registration"),
        ("beforeinstallprompt", "Install prompt handler"),
    ]

    all_valid = True
    for element, description in required_elements:
        if element in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - MISSING!")
            all_valid = False

    print("=" * 60)
    return all_valid


def test_settings():
    """Test Django settings for static files."""
    print("\nTesting Django settings...")
    print("=" * 60)

    base_dir = Path(__file__).parent
    settings_path = base_dir / "core" / "settings.py"

    if not settings_path.exists():
        print("❌ settings.py not found!")
        return False

    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    checks = [
        ("STATIC_URL", "Static URL configured"),
        ("STATIC_ROOT", "Static root configured"),
        ("STATICFILES_DIRS", "Static files dirs configured"),
    ]

    all_valid = True
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - MISSING!")
            all_valid = False

    print("=" * 60)
    return all_valid


def test_staticfiles_collected():
    """Test that static files have been collected."""
    print("\nTesting collected static files...")
    print("=" * 60)

    base_dir = Path(__file__).parent
    staticfiles_dir = base_dir / "staticfiles" / "pwa"

    if not staticfiles_dir.exists():
        print("❌ staticfiles/pwa directory not found!")
        print("   Run: python manage.py collectstatic")
        return False

    files = list(staticfiles_dir.glob("*"))
    print(f"✅ Found {len(files)} files in staticfiles/pwa/")

    for file in sorted(files):
        size_kb = file.stat().st_size / 1024
        print(f"   - {file.name} ({size_kb:.2f} KB)")

    print("=" * 60)
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PWA SETUP VERIFICATION TEST")
    print("=" * 60 + "\n")

    results = {
        "PWA Files": test_pwa_files(),
        "Manifest JSON": test_manifest_json(),
        "Service Worker": test_service_worker(),
        "Base Template": test_base_template(),
        "Django Settings": test_settings(),
        "Collected Static Files": test_staticfiles_collected(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed! PWA is ready to deploy.")
        print("\nNext steps:")
        print("1. Test locally: python manage.py runserver")
        print("2. Open http://localhost:8000 in Chrome")
        print("3. Check Application tab in DevTools")
        print("4. Deploy to Vercel: git push")
        print("5. Test on mobile device with production URL")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        print("\nCommon fixes:")
        print("- Run: python manage.py collectstatic")
        print("- Check file paths in settings.py")
        print("- Verify all PWA files were generated")

    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
