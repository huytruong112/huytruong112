#!/usr/bin/env python3
"""
Example: Payment webhook integration
This demonstrates how to automatically create subscriptions when payments are received
"""
from fastapi import FastAPI, Request, HTTPException
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Payment Webhook Example")

# Configuration
VPN_API_URL = "http://localhost:8000"

# Plan configurations
PLANS = {
    "basic": {
        "traffic_limit_gb": 50,
        "expiry_days": 30,
        "inbound_id": 1
    },
    "premium": {
        "traffic_limit_gb": 100,
        "expiry_days": 30,
        "inbound_id": 1
    },
    "unlimited": {
        "traffic_limit_gb": 0,  # 0 means unlimited
        "expiry_days": 30,
        "inbound_id": 1
    }
}


@app.post("/webhook/payment")
async def payment_webhook(request: Request):
    """
    Webhook endpoint to receive payment notifications
    
    Expected payload format:
    {
        "payment_id": "PAY123456",
        "status": "paid",
        "customer_email": "customer@example.com",
        "customer_name": "Nguyen Van A",
        "customer_phone": "+84901234567",
        "plan": "premium"
    }
    """
    try:
        data = await request.json()
        logger.info(f"Received payment webhook: {data}")
        
        # Verify payment status
        if data.get('status') != 'paid':
            logger.warning(f"Payment not completed: {data.get('status')}")
            return {"status": "ignored", "reason": "payment_not_completed"}
        
        # Get plan configuration
        plan = data.get('plan', 'basic')
        if plan not in PLANS:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
        
        plan_config = PLANS[plan]
        
        # Create subscription via VPN API
        async with httpx.AsyncClient(timeout=30.0) as client:
            subscription_data = {
                "customer_email": data['customer_email'],
                "customer_name": data['customer_name'],
                "customer_phone": data.get('customer_phone'),
                "panel_type": "xui",  # or "3x-ui" based on your setup
                "inbound_id": plan_config['inbound_id'],
                "traffic_limit_gb": plan_config['traffic_limit_gb'],
                "expiry_days": plan_config['expiry_days'],
                "protocol": "vless"
            }
            
            logger.info(f"Creating subscription: {subscription_data}")
            
            response = await client.post(
                f"{VPN_API_URL}/subscriptions",
                json=subscription_data
            )
            
            if response.status_code == 201:
                subscription = response.json()
                logger.info(f"✅ Subscription created: {subscription['id']}")
                
                # Get configuration
                config_response = await client.get(
                    f"{VPN_API_URL}/subscriptions/{subscription['id']}/config"
                )
                
                if config_response.status_code == 200:
                    config = config_response.json()
                    
                    # Here you can:
                    # 1. Send email to customer with configuration
                    # 2. Send SMS with QR code link
                    # 3. Update your database
                    # 4. Send notification to admin
                    
                    logger.info("Configuration retrieved, sending to customer...")
                    # await send_welcome_email(data['customer_email'], config)
                    
                    return {
                        "status": "success",
                        "subscription_id": subscription['id'],
                        "message": "Subscription created successfully"
                    }
            else:
                logger.error(f"Failed to create subscription: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create subscription"
                )
                
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-webhook")
async def test_webhook():
    """Test endpoint to simulate a payment webhook"""
    test_data = {
        "payment_id": "TEST123456",
        "status": "paid",
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "customer_phone": "+1234567890",
        "plan": "premium"
    }
    
    # Simulate webhook call
    result = await payment_webhook(
        Request(scope={"type": "http", "method": "POST"})
    )
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
