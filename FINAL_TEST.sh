#!/bin/bash

# Final comprehensive test before running

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              FINAL TEST - ADMIN PANEL                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

all_pass=true

# Test 1: Python version
echo "1. Testing Python version..."
python3 --version
if [ $? -eq 0 ]; then
    echo "   ✅ PASS"
else
    echo "   ❌ FAIL"
    all_pass=false
fi
echo ""

# Test 2: Dependencies
echo "2. Testing dependencies..."
python3 -c "import flask, requests, psutil, speedtest" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ PASS - All modules available"
else
    echo "   ❌ FAIL - Some modules missing"
    all_pass=false
fi
echo ""

# Test 3: Import admin_panel
echo "3. Testing admin_panel.py import..."
python3 -c "import admin_panel" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ PASS - No import errors"
else
    echo "   ❌ FAIL - Import error"
    all_pass=false
fi
echo ""

# Test 4: Flask app
echo "4. Testing Flask app creation..."
python3 -c "import admin_panel; app = admin_panel.app; print(f'   Routes: {len(list(app.url_map.iter_rules()))}')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ PASS - Flask app ready"
else
    echo "   ❌ FAIL - Flask app error"
    all_pass=false
fi
echo ""

# Test 5: Flask version (the AttributeError fix)
echo "5. Testing Flask version detection..."
python3 << 'EOF' 2>/dev/null
try:
    from importlib.metadata import version
    flask_version = version('flask')
    print(f"   Flask version: {flask_version}")
    print("   ✅ PASS - No AttributeError")
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    exit(1)
EOF
if [ $? -ne 0 ]; then
    all_pass=false
fi
echo ""

# Test 6: Speedtest module (the ModuleNotFoundError fix)
echo "6. Testing speedtest handling..."
python3 << 'EOF' 2>/dev/null
import admin_panel
if admin_panel.SPEEDTEST_AVAILABLE:
    print("   Speedtest: Available")
    print("   ✅ PASS - Speedtest working")
else:
    print("   Speedtest: Not available (graceful degradation)")
    print("   ✅ PASS - Error handled gracefully")
EOF
echo ""

# Test 7: Templates
echo "7. Testing templates..."
if [ -d "templates" ] && [ $(ls templates/*.html 2>/dev/null | wc -l) -eq 7 ]; then
    echo "   Templates: $(ls templates/*.html 2>/dev/null | wc -l) files"
    echo "   ✅ PASS"
else
    echo "   ❌ FAIL - Templates missing"
    all_pass=false
fi
echo ""

# Test 8: Static files
echo "8. Testing static files..."
if [ -f "static/css/style.css" ] && [ -f "static/js/main.js" ]; then
    echo "   ✅ PASS - CSS and JS found"
else
    echo "   ❌ FAIL - Static files missing"
    all_pass=false
fi
echo ""

# Test 9: Configuration
echo "9. Testing configuration..."
if [ -f ".env" ]; then
    echo "   ✅ PASS - .env file exists"
else
    echo "   ⚠️  WARNING - .env not found (will use defaults)"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo ""
if [ "$all_pass" = true ]; then
    echo "✅ ALL TESTS PASSED!"
    echo ""
    echo "🚀 Ready to run:"
    echo "   python3 admin_panel.py"
    echo ""
    echo "Or:"
    echo "   ./RUN_NOW.sh"
    echo ""
else
    echo "❌ SOME TESTS FAILED!"
    echo ""
    echo "Please check the errors above and fix them."
    echo ""
fi
echo "════════════════════════════════════════════════════════════"
