#!/usr/bin/env python3
"""
Test server to check if pages render correctly
"""

import sys
sys.path.insert(0, '/workspace')

from admin_panel import app

print("Testing server responses...")
print("=" * 60)

with app.test_client() as client:
    # Test root
    print("\n1. Testing / (root)...")
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    print(f"   Redirect: {response.location if response.status_code in [301, 302] else 'N/A'}")
    
    # Test login page
    print("\n2. Testing /login...")
    response = client.get('/login', follow_redirects=True)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")
    print(f"   Content length: {len(response.data)} bytes")
    
    # Check if HTML is valid
    html = response.data.decode('utf-8')
    if '<html' in html.lower():
        print("   ✅ HTML structure found")
    else:
        print("   ❌ No HTML structure")
    
    if '<title>' in html:
        print("   ✅ Title tag found")
    else:
        print("   ❌ No title tag")
    
    if 'VPN Vietnam' in html or 'Admin' in html:
        print("   ✅ Content found")
    else:
        print("   ❌ No expected content")
    
    # Test static file
    print("\n3. Testing static file /static/css/style.css...")
    response = client.get('/static/css/style.css')
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.content_type}")
    if response.status_code == 200:
        print(f"   Size: {len(response.data)} bytes")
    
    # Test dashboard (should redirect to login)
    print("\n4. Testing /dashboard (should redirect)...")
    response = client.get('/dashboard')
    print(f"   Status: {response.status_code}")
    print(f"   Redirect: {response.location if response.status_code in [301, 302] else 'N/A'}")

print("\n" + "=" * 60)
print("If all tests show 200 or 302, server is working!")
print("If you see 404 or 500, there's an issue.")
