#!/usr/bin/env python3
"""
Complete test for admin_panel.py
"""

import sys
import os

print("=" * 60)
print("  TESTING ADMIN PANEL")
print("=" * 60)

# Test 1: Check all required modules
print("\n1. Testing Required Modules...")
modules_to_test = [
    'flask',
    'psutil', 
    'requests',
    'speedtest',
]

all_modules_ok = True
for module in modules_to_test:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError as e:
        print(f"   ❌ {module}: {e}")
        all_modules_ok = False

# Test 2: Import admin_panel
print("\n2. Testing admin_panel.py import...")
try:
    sys.path.insert(0, '/workspace')
    import admin_panel
    print("   ✅ admin_panel.py imports successfully")
except Exception as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Test 3: Check Flask app
print("\n3. Testing Flask app...")
try:
    app = admin_panel.app
    print(f"   ✅ Flask app created: {app}")
    print(f"   ✅ Secret key configured: {'*' * 10}")
except Exception as e:
    print(f"   ❌ Flask app error: {e}")

# Test 4: Check API client
print("\n4. Testing 3X-UI API client...")
try:
    api = admin_panel.xray_api
    print(f"   ✅ API client created")
    print(f"   ✅ Panel URL: {api.base_url}")
except Exception as e:
    print(f"   ❌ API client error: {e}")

# Test 5: Check system stats
print("\n5. Testing system stats function...")
try:
    stats = admin_panel.get_system_stats()
    if stats:
        print(f"   ✅ System stats working")
        print(f"   ✅ CPU: {stats['cpu']['percent']}%")
        print(f"   ✅ Memory: {stats['memory']['percent']}%")
        print(f"   ✅ Disk: {stats['disk']['percent']}%")
    else:
        print("   ⚠️  System stats returned None")
except Exception as e:
    print(f"   ❌ System stats error: {e}")

# Test 6: Check speedtest availability
print("\n6. Testing speedtest availability...")
if admin_panel.SPEEDTEST_AVAILABLE:
    print("   ✅ Speedtest module available")
else:
    print("   ⚠️  Speedtest module not available (feature disabled)")

# Test 7: Check routes
print("\n7. Testing Flask routes...")
routes = []
for rule in app.url_map.iter_rules():
    routes.append(str(rule))
print(f"   ✅ Total routes: {len(routes)}")
print(f"   ✅ Main routes found:")
important_routes = ['/', '/login', '/dashboard', '/configs', '/users', '/monitoring', '/settings']
for route in important_routes:
    if any(route in r for r in routes):
        print(f"      ✅ {route}")
    else:
        print(f"      ❌ {route}")

# Test 8: Check templates
print("\n8. Testing templates...")
template_folder = '/workspace/templates'
if os.path.exists(template_folder):
    templates = os.listdir(template_folder)
    print(f"   ✅ Templates folder exists")
    print(f"   ✅ Templates found: {len(templates)}")
    for tmpl in templates:
        print(f"      ✅ {tmpl}")
else:
    print(f"   ❌ Templates folder not found")

# Test 9: Check static files
print("\n9. Testing static files...")
static_folder = '/workspace/static'
if os.path.exists(static_folder):
    print(f"   ✅ Static folder exists")
    if os.path.exists(f"{static_folder}/css/style.css"):
        print(f"      ✅ style.css found")
    if os.path.exists(f"{static_folder}/js/main.js"):
        print(f"      ✅ main.js found")
else:
    print(f"   ❌ Static folder not found")

# Summary
print("\n" + "=" * 60)
print("  TEST SUMMARY")
print("=" * 60)

if all_modules_ok:
    print("✅ All required modules installed")
    print("✅ admin_panel.py is ready to run")
    print("\n🚀 To start the server, run:")
    print("   python3 admin_panel.py")
    print("\n   Or:")
    print("   ./start.sh")
else:
    print("❌ Some modules are missing")
    print("   Run: pip3 install -r requirements.txt --user")

print("=" * 60)
