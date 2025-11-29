#!/usr/bin/env python3
"""
Test speedtest module installation
"""

print("Testing speedtest module imports...")
print("=" * 50)

# Test 1: Direct import
print("\n1. Testing: import speedtest")
try:
    import speedtest
    print("   ✅ SUCCESS: import speedtest")
    print(f"   Module: {speedtest}")
    print(f"   Path: {speedtest.__file__}")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")

# Test 2: Import Speedtest class
print("\n2. Testing: from speedtest import Speedtest")
try:
    from speedtest import Speedtest
    print("   ✅ SUCCESS: from speedtest import Speedtest")
    print(f"   Class: {Speedtest}")
except ImportError as e:
    print(f"   ❌ FAILED: {e}")

# Test 3: Try to create instance
print("\n3. Testing: Create Speedtest instance")
try:
    import speedtest
    if hasattr(speedtest, 'Speedtest'):
        st = speedtest.Speedtest()
        print("   ✅ SUCCESS: Created Speedtest() instance")
        print(f"   Instance: {st}")
    else:
        print("   ⚠️  WARNING: speedtest module has no Speedtest class")
        print(f"   Available: {dir(speedtest)}")
except Exception as e:
    print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 50)
print("\nRecommendation:")
print("If tests failed, run: ./fix_speedtest.sh")
print("Or manually: pip3 install --user --force-reinstall speedtest-cli")
