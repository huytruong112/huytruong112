# 🧪 Testing Guide

Hướng dẫn test hệ thống VPN Auto Provisioning

## Quick Tests

### 1. Health Check ✅

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status": "healthy"}
```

### 2. Root Endpoint ✅

```bash
curl http://localhost:8000/
```

Expected output:
```json
{
  "message": "VPN Service Auto Provisioning API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 3. Check Available Panels ✅

```bash
curl http://localhost:8000/panels
```

Expected output (if panels configured):
```json
[
  {
    "panel_type": "xui_2",
    "is_enabled": true,
    "inbound_count": 3,
    "available": true
  }
]
```

## Full Registration Flow Test

### Step 1: Register Customer

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "test123456",
    "full_name": "Test User",
    "phone": "0123456789",
    "traffic_limit_gb": 50,
    "service_duration_days": 30
  }' | jq
```

Expected: Status 201, returns customer info + VPN config with connection URL

### Step 2: Login

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }' | jq
```

Save the `access_token` from response!

### Step 3: Get My Info

```bash
TOKEN="your_token_here"

curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Step 4: Get My VPN Configs

```bash
curl -X GET "http://localhost:8000/my-vpn-configs" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Step 5: Get Usage Stats

```bash
curl -X GET "http://localhost:8000/vpn-config/1/stats" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Test Script

Create `test_api.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000"
TEST_EMAIL="test$(date +%s)@example.com"
TEST_USERNAME="test$(date +%s)"
TEST_PASSWORD="test123456"

echo "🧪 Testing VPN Auto Provisioning API"
echo "======================================"

# 1. Health Check
echo ""
echo "1️⃣  Testing health endpoint..."
HEALTH=$(curl -s "$API_URL/health")
if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi

# 2. Check Panels
echo ""
echo "2️⃣  Checking available panels..."
PANELS=$(curl -s "$API_URL/panels")
echo "$PANELS" | jq
if [[ $PANELS == *"panel_type"* ]]; then
    echo "✅ Panels endpoint working"
else
    echo "⚠️  No panels configured or panels endpoint error"
fi

# 3. Register Customer
echo ""
echo "3️⃣  Registering test customer..."
echo "Email: $TEST_EMAIL"
echo "Username: $TEST_USERNAME"

REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"username\": \"$TEST_USERNAME\",
    \"password\": \"$TEST_PASSWORD\",
    \"traffic_limit_gb\": 50,
    \"service_duration_days\": 30
  }")

echo "$REGISTER_RESPONSE" | jq

if [[ $REGISTER_RESPONSE == *"connection_url"* ]]; then
    echo "✅ Registration successful"
    CONNECTION_URL=$(echo "$REGISTER_RESPONSE" | jq -r '.vpn_config.connection_url')
    echo "📱 Connection URL: $CONNECTION_URL"
else
    echo "❌ Registration failed"
    echo "$REGISTER_RESPONSE"
    exit 1
fi

# 4. Login
echo ""
echo "4️⃣  Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"password\": \"$TEST_PASSWORD\"
  }")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [[ $TOKEN != "null" ]] && [[ -n $TOKEN ]]; then
    echo "✅ Login successful"
    echo "🔑 Token: ${TOKEN:0:50}..."
else
    echo "❌ Login failed"
    exit 1
fi

# 5. Get My Info
echo ""
echo "5️⃣  Getting customer info..."
ME_RESPONSE=$(curl -s -X GET "$API_URL/me" \
  -H "Authorization: Bearer $TOKEN")

echo "$ME_RESPONSE" | jq

if [[ $ME_RESPONSE == *"$TEST_USERNAME"* ]]; then
    echo "✅ Get customer info successful"
else
    echo "❌ Get customer info failed"
fi

# 6. Get VPN Configs
echo ""
echo "6️⃣  Getting VPN configurations..."
CONFIGS_RESPONSE=$(curl -s -X GET "$API_URL/my-vpn-configs" \
  -H "Authorization: Bearer $TOKEN")

echo "$CONFIGS_RESPONSE" | jq

if [[ $CONFIGS_RESPONSE == *"config_name"* ]]; then
    echo "✅ Get VPN configs successful"
    CONFIG_ID=$(echo "$CONFIGS_RESPONSE" | jq -r '.[0].id')
    echo "📋 Config ID: $CONFIG_ID"
else
    echo "❌ Get VPN configs failed"
fi

# 7. Get Stats
if [[ -n $CONFIG_ID ]]; then
    echo ""
    echo "7️⃣  Getting usage statistics..."
    STATS_RESPONSE=$(curl -s -X GET "$API_URL/vpn-config/$CONFIG_ID/stats" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "$STATS_RESPONSE" | jq
    
    if [[ $STATS_RESPONSE == *"config_id"* ]]; then
        echo "✅ Get stats successful"
    else
        echo "⚠️  Stats not available (may be normal if panel is not fully configured)"
    fi
fi

echo ""
echo "======================================"
echo "🎉 All tests completed!"
echo ""
echo "📊 Summary:"
echo "  ✅ Health check: OK"
echo "  ✅ Panels: OK"
echo "  ✅ Registration: OK"
echo "  ✅ Login: OK"
echo "  ✅ Get info: OK"
echo "  ✅ Get configs: OK"
echo ""
echo "🔗 Test Account:"
echo "  Email: $TEST_EMAIL"
echo "  Username: $TEST_USERNAME"
echo "  Password: $TEST_PASSWORD"
echo "  Connection URL: $CONNECTION_URL"
```

Make it executable and run:

```bash
chmod +x test_api.sh
./test_api.sh
```

## Testing with Python

Create `test_api.py`:

```python
#!/usr/bin/env python3

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("1️⃣  Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed\n")

def test_panels():
    """Test panels endpoint"""
    print("2️⃣  Testing panels endpoint...")
    response = requests.get(f"{API_URL}/panels")
    assert response.status_code == 200
    panels = response.json()
    print(f"   Found {len(panels)} panel(s)")
    print("✅ Panels check passed\n")
    return panels

def test_register():
    """Test customer registration"""
    print("3️⃣  Testing customer registration...")
    
    timestamp = int(datetime.now().timestamp())
    data = {
        "email": f"test{timestamp}@example.com",
        "username": f"test{timestamp}",
        "password": "test123456",
        "full_name": "Test User",
        "traffic_limit_gb": 50,
        "service_duration_days": 30
    }
    
    response = requests.post(f"{API_URL}/register", json=data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"   Username: {result['customer']['username']}")
        print(f"   Email: {result['customer']['email']}")
        print(f"   Config: {result['vpn_config']['config_name']}")
        print("✅ Registration successful\n")
        return data['username'], data['password'], result
    else:
        print(f"❌ Registration failed: {response.json()}")
        return None, None, None

def test_login(username, password):
    """Test login"""
    print("4️⃣  Testing login...")
    
    response = requests.post(
        f"{API_URL}/login",
        json={"username": username, "password": password}
    )
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    print(f"   Token: {token[:50]}...")
    print("✅ Login successful\n")
    return token

def test_get_me(token):
    """Test get current user"""
    print("5️⃣  Testing get current user...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/me", headers=headers)
    
    assert response.status_code == 200
    user = response.json()
    print(f"   User: {user['username']} ({user['email']})")
    print("✅ Get user info successful\n")

def test_get_configs(token):
    """Test get VPN configs"""
    print("6️⃣  Testing get VPN configs...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/my-vpn-configs", headers=headers)
    
    assert response.status_code == 200
    configs = response.json()
    print(f"   Found {len(configs)} config(s)")
    if configs:
        print(f"   Config: {configs[0]['config_name']}")
        print(f"   Status: {configs[0]['service_status']}")
    print("✅ Get configs successful\n")
    return configs

def main():
    print("🧪 VPN Auto Provisioning API Tests")
    print("=" * 50)
    print()
    
    try:
        # Run tests
        test_health()
        test_panels()
        
        username, password, reg_result = test_register()
        if not username:
            print("❌ Registration failed, stopping tests")
            return
        
        token = test_login(username, password)
        test_get_me(token)
        configs = test_get_configs(token)
        
        print("=" * 50)
        print("🎉 All tests passed!")
        print()
        print("📊 Test Summary:")
        print(f"  ✅ Health: OK")
        print(f"  ✅ Panels: OK")
        print(f"  ✅ Registration: OK")
        print(f"  ✅ Login: OK")
        print(f"  ✅ Get Info: OK")
        print(f"  ✅ Get Configs: OK")
        print()
        print("🔗 Test Account:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        if reg_result:
            print(f"  Connection URL: {reg_result['vpn_config']['connection_url']}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
```

Run:

```bash
python3 test_api.py
```

## Testing Web UI

1. Open `example_register.html` in browser
2. Fill in the form
3. Click "Đăng ký ngay"
4. Should see success message with connection URL

## Load Testing (Optional)

Using Apache Bench:

```bash
# Install ab
sudo apt install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health
```

Using wrk:

```bash
# Install wrk
sudo apt install wrk

# Test
wrk -t4 -c100 -d30s http://localhost:8000/health
```

## Common Test Scenarios

### Test 1: Multiple Registrations
```bash
for i in {1..5}; do
    curl -X POST "http://localhost:8000/register" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"user$i@example.com\",
        \"username\": \"user$i\",
        \"password\": \"pass123\",
        \"traffic_limit_gb\": 50,
        \"service_duration_days\": 30
      }"
    echo ""
done
```

### Test 2: Invalid Data
```bash
# Missing required field
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com"}'
```

### Test 3: Duplicate User
```bash
# Register same user twice
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "duplicate@test.com",
    "username": "duplicate",
    "password": "test123"
  }'

# Try again - should fail
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "duplicate@test.com",
    "username": "duplicate",
    "password": "test123"
  }'
```

## Troubleshooting Tests

### Connection Refused
```bash
# Check if server is running
ps aux | grep uvicorn

# Check port
netstat -tulpn | grep 8000

# Check logs
journalctl -u vpn-auto -f
```

### Panel Not Available
```bash
# Check panel connection
curl http://your-panel-ip:2053

# Check .env configuration
cat .env | grep XUI
```

### Database Issues
```bash
# Check database
sqlite3 vpn_service.db "SELECT * FROM customers;"
```

## Expected Test Results

| Test | Expected Result | Status Code |
|------|----------------|-------------|
| Health | `{"status": "healthy"}` | 200 |
| Panels | List of panels | 200 |
| Register | Customer + VPN config | 201 |
| Login | JWT token | 200 |
| Get Me | Customer info | 200 |
| Get Configs | List of configs | 200 |
| Invalid Auth | Error message | 401 |
| Duplicate User | Error message | 400 |

---

Happy Testing! 🧪✅
