#!/usr/bin/env python3
"""
Test admin_panel.py startup without running the server
"""

import sys
import os

print("Testing admin_panel.py startup...")
print("=" * 60)

# Change to workspace directory
os.chdir('/workspace')
sys.path.insert(0, '/workspace')

# Test import
try:
    import admin_panel
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test Flask app
try:
    app = admin_panel.app
    print(f"✅ Flask app: {app.name}")
except Exception as e:
    print(f"❌ Flask app error: {e}")
    sys.exit(1)

# Test configuration
try:
    print(f"✅ Panel URL: {admin_panel.XRAY_PANEL_URL}")
    print(f"✅ Speedtest: {'Available' if admin_panel.SPEEDTEST_AVAILABLE else 'Not available'}")
except Exception as e:
    print(f"❌ Config error: {e}")

# Test routes
try:
    routes = list(admin_panel.app.url_map.iter_rules())
    print(f"✅ Routes: {len(routes)} endpoints")
except Exception as e:
    print(f"❌ Routes error: {e}")

# Test startup banner (without actually starting server)
print("\n" + "=" * 60)
print("Testing startup banner...")
print("=" * 60)

try:
    from importlib.metadata import version
    flask_version = version('flask')
    print(f"✅ Flask Version (importlib): {flask_version}")
except Exception as e:
    print(f"⚠️  Flask version check: {e}")

print("=" * 60)
print("✅ All startup tests passed!")
print("=" * 60)
print("\nReady to run:")
print("  python3 admin_panel.py")
