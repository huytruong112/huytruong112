# VPN Subscription Management System

Automated VPN subscription management system with x-ui and 3x-ui panels integration. Automatically creates configurations when customers register for services.

## Features

- ✅ Integration with x-ui panel (dopaemon/x-ui)
- ✅ Integration with 3x-ui panel (mhsanaei/3x-ui)
- ✅ Automatic VPN configuration creation on customer registration
- ✅ Customer and subscription management
- ✅ Traffic usage tracking
- ✅ Subscription renewal and updates
- ✅ QR code generation for configurations
- ✅ RESTful API with FastAPI
- ✅ Subscription status management (active, expired, suspended, cancelled)

## System Requirements

- Python 3.8+
- x-ui or 3x-ui panel installed and configured

## Installation

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` file with your information:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./vpn_service.db

# X-UI Panel Configuration
XUI_PANEL_URL=http://your-xui-panel.com:54321
XUI_USERNAME=admin
XUI_PASSWORD=admin

# 3X-UI Panel Configuration
THREEXUI_PANEL_URL=http://your-3xui-panel.com:2053
THREEXUI_USERNAME=admin
THREEXUI_PASSWORD=admin

# Service Configuration
DEFAULT_TRAFFIC_LIMIT_GB=50
DEFAULT_EXPIRY_DAYS=30
DEFAULT_PROTOCOL=vless
```

### 5. Run the application

```bash
python main.py
```

API will run at `http://localhost:8000`

## API Documentation

After running the application, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

### 1. Create new subscription for customer

```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "John Doe",
    "customer_phone": "+1234567890",
    "panel_type": "xui",
    "inbound_id": 1,
    "traffic_limit_gb": 100,
    "expiry_days": 30,
    "protocol": "vless"
  }'
```

Or with 3x-ui:

```bash
curl -X POST "http://localhost:8000/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "customer@example.com",
    "customer_name": "John Doe",
    "customer_phone": "+1234567890",
    "panel_type": "3x-ui",
    "inbound_id": 1,
    "traffic_limit_gb": 100,
    "expiry_days": 30,
    "protocol": "vless"
  }'
```

### 2. Get configuration

```bash
curl "http://localhost:8000/subscriptions/1/config"
```

### 3. Generate QR code

```bash
curl "http://localhost:8000/subscriptions/1/qrcode?connection_url=vless://..." \
  --output qrcode.png
```

### 4. Renew subscription

```bash
curl -X POST "http://localhost:8000/subscriptions/1/renew" \
  -H "Content-Type: application/json" \
  -d '{
    "additional_days": 30,
    "additional_traffic_gb": 50
  }'
```

### 5. Update status

```bash
curl -X PUT "http://localhost:8000/subscriptions/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "suspended",
    "enable": false
  }'
```

### 6. Sync traffic

```bash
curl -X POST "http://localhost:8000/subscriptions/1/sync-traffic"
```

### 7. Delete subscription

```bash
curl -X DELETE "http://localhost:8000/subscriptions/1"
```

## Payment Gateway Integration

You can integrate this API with:

- Service registration websites
- Payment gateways
- Telegram bots
- Discord bots
- CRM systems

### Example: Website Integration

```javascript
// Frontend - When customer completes payment
async function createSubscription(customerData, planData) {
  const response = await fetch('http://your-api.com/subscriptions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      customer_email: customerData.email,
      customer_name: customerData.name,
      customer_phone: customerData.phone,
      panel_type: 'xui', // or '3x-ui'
      inbound_id: planData.inboundId,
      traffic_limit_gb: planData.trafficLimit,
      expiry_days: planData.duration,
      protocol: 'vless'
    })
  });
  
  const subscription = await response.json();
  
  // Get configuration
  const config = await fetch(`http://your-api.com/subscriptions/${subscription.id}/config`)
    .then(r => r.json());
  
  // Display to customer
  displayConfig(config);
}
```

### Example: Payment Webhook

```python
from fastapi import FastAPI, Request
import httpx

webhook_app = FastAPI()

@webhook_app.post("/payment-webhook")
async def payment_webhook(request: Request):
    """Webhook to receive notifications from payment gateway"""
    data = await request.json()
    
    if data['status'] == 'paid':
        # Automatically create subscription
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'http://localhost:8000/subscriptions',
                json={
                    'customer_email': data['customer_email'],
                    'customer_name': data['customer_name'],
                    'customer_phone': data['customer_phone'],
                    'panel_type': 'xui',
                    'inbound_id': 1,
                    'traffic_limit_gb': data['plan_traffic'],
                    'expiry_days': data['plan_days'],
                    'protocol': 'vless'
                }
            )
            
            if response.status_code == 201:
                subscription = response.json()
                
                # Send welcome email to customer with configuration
                await send_welcome_email(
                    data['customer_email'],
                    subscription['id']
                )
                
    return {'status': 'success'}
```

## Project Structure

```
.
├── clients/                  # API clients for panels
│   ├── __init__.py
│   ├── xui_client.py        # Client for x-ui
│   └── threexui_client.py   # Client for 3x-ui
├── services/                 # Business logic
│   ├── __init__.py
│   └── vpn_service.py       # VPN management service
├── models.py                # Database models
├── database.py              # Database configuration
├── schemas.py               # Pydantic schemas
├── config.py                # Application configuration
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # Documentation
```

## Security

### Recommendations

1. **Change API_SECRET_KEY**: Set a complex key in `.env`
2. **Use HTTPS**: Deploy with reverse proxy (nginx) and SSL
3. **Rate limiting**: Add rate limiting to prevent abuse
4. **Authentication**: Add JWT or API key authentication
5. **Firewall**: Only allow access from trusted IPs

## License

MIT License
