#!/usr/bin/env python3
"""
Example script: Create a subscription for a customer
"""
import httpx
import asyncio
import json


async def create_subscription():
    """Create a new subscription"""
    
    api_url = "http://localhost:8000"
    
    # Subscription data
    subscription_data = {
        "customer_email": "customer@example.com",
        "customer_name": "Nguyen Van A",
        "customer_phone": "+84901234567",
        "panel_type": "xui",  # or "3x-ui"
        "inbound_id": 1,  # Your inbound ID from panel
        "traffic_limit_gb": 100,
        "expiry_days": 30,
        "protocol": "vless"
    }
    
    async with httpx.AsyncClient() as client:
        # Create subscription
        print("Creating subscription...")
        response = await client.post(
            f"{api_url}/subscriptions",
            json=subscription_data
        )
        
        if response.status_code == 201:
            subscription = response.json()
            print("✅ Subscription created successfully!")
            print(json.dumps(subscription, indent=2))
            
            subscription_id = subscription['id']
            
            # Get configuration
            print("\nGetting configuration...")
            config_response = await client.get(
                f"{api_url}/subscriptions/{subscription_id}/config"
            )
            
            if config_response.status_code == 200:
                config = config_response.json()
                print("✅ Configuration:")
                print(json.dumps(config, indent=2))
            
            return subscription_id
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None


if __name__ == "__main__":
    asyncio.run(create_subscription())
