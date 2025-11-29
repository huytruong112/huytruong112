"""
Example Integration Script

This script demonstrates how to integrate the X-UI/3X-UI Manager API
into your existing systems.

You can use this as a template for:
- Payment gateway webhooks
- Telegram bots
- Custom registration forms
- Automated provisioning systems
"""

import requests
import json
from typing import Dict, Optional


class VPNManagerClient:
    """Client for interacting with VPN Manager API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the VPN Manager API
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
    
    def register_customer(self, 
                         email: str, 
                         name: str,
                         phone: Optional[str] = None,
                         telegram_id: Optional[str] = None,
                         service_name: str = "Standard Plan",
                         traffic_limit_gb: int = 100,
                         expiry_days: int = 30,
                         inbound_id: int = 1) -> Dict:
        """
        Register a new customer and create VPN account
        
        Args:
            email: Customer email (unique)
            name: Customer name
            phone: Phone number (optional)
            telegram_id: Telegram ID (optional)
            service_name: Service plan name
            traffic_limit_gb: Traffic limit in GB (0 for unlimited)
            expiry_days: Days until expiry (0 for no expiry)
            inbound_id: Inbound ID on panel
        
        Returns:
            Dict with customer and subscription info
        """
        url = f"{self.api_url}/register"
        
        data = {
            "email": email,
            "name": name,
            "service_name": service_name,
            "traffic_limit_gb": traffic_limit_gb,
            "expiry_days": expiry_days,
            "inbound_id": inbound_id
        }
        
        if phone:
            data["phone"] = phone
        if telegram_id:
            data["telegram_id"] = telegram_id
        
        response = requests.post(url, json=data)
        return response.json()
    
    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """Get customer information by email"""
        url = f"{self.api_url}/customers"
        response = requests.get(url)
        result = response.json()
        
        if result.get('success'):
            for customer in result.get('customers', []):
                if customer['email'] == email:
                    return customer
        return None
    
    def get_subscription_traffic(self, subscription_id: int) -> Dict:
        """Get traffic statistics for a subscription"""
        url = f"{self.api_url}/subscriptions/{subscription_id}/traffic"
        response = requests.get(url)
        return response.json()
    
    def create_subscription(self,
                          customer_id: int,
                          service_name: str = "Standard Plan",
                          traffic_limit_gb: int = 100,
                          expiry_days: int = 30,
                          inbound_id: int = 1) -> Dict:
        """Create a new subscription for existing customer"""
        url = f"{self.api_url}/subscriptions"
        
        data = {
            "customer_id": customer_id,
            "service_name": service_name,
            "traffic_limit_gb": traffic_limit_gb,
            "expiry_days": expiry_days,
            "inbound_id": inbound_id
        }
        
        response = requests.post(url, json=data)
        return response.json()


# ==================== USAGE EXAMPLES ====================

def example_1_simple_registration():
    """Example 1: Simple customer registration"""
    print("=" * 50)
    print("Example 1: Simple Registration")
    print("=" * 50)
    
    client = VPNManagerClient("http://localhost:5000")
    
    result = client.register_customer(
        email="customer1@example.com",
        name="John Doe",
        phone="+1234567890"
    )
    
    if result.get('success'):
        print("✅ Registration successful!")
        print(f"Customer ID: {result['customer']['id']}")
        print(f"UUID: {result['subscription']['uuid']}")
        print(f"Traffic Limit: {result['subscription']['traffic_limit_gb']} GB")
        print(f"Expiry Date: {result['subscription']['expiry_date']}")
    else:
        print(f"❌ Error: {result.get('error')}")


def example_2_custom_plan():
    """Example 2: Registration with custom plan"""
    print("\n" + "=" * 50)
    print("Example 2: Custom Plan Registration")
    print("=" * 50)
    
    client = VPNManagerClient("http://localhost:5000")
    
    result = client.register_customer(
        email="premium@example.com",
        name="Jane Smith",
        telegram_id="@janesmith",
        service_name="Premium Plan",
        traffic_limit_gb=500,  # 500 GB
        expiry_days=90         # 3 months
    )
    
    if result.get('success'):
        print("✅ Premium plan created!")
        print(f"Email: {result['customer']['email']}")
        print(f"Plan: {result['subscription']['service_name']}")
        print(f"Traffic: {result['subscription']['traffic_limit_gb']} GB")
    else:
        print(f"❌ Error: {result.get('error')}")


def example_3_unlimited_plan():
    """Example 3: Unlimited plan"""
    print("\n" + "=" * 50)
    print("Example 3: Unlimited Plan")
    print("=" * 50)
    
    client = VPNManagerClient("http://localhost:5000")
    
    result = client.register_customer(
        email="unlimited@example.com",
        name="Bob Johnson",
        service_name="Unlimited Plan",
        traffic_limit_gb=0,    # 0 = unlimited
        expiry_days=365        # 1 year
    )
    
    if result.get('success'):
        print("✅ Unlimited plan created!")
        print(f"UUID: {result['subscription']['uuid']}")
        print("Traffic: Unlimited")
        print(f"Valid for: 1 year")
    else:
        print(f"❌ Error: {result.get('error')}")


def example_4_check_traffic():
    """Example 4: Check traffic usage"""
    print("\n" + "=" * 50)
    print("Example 4: Check Traffic Usage")
    print("=" * 50)
    
    client = VPNManagerClient("http://localhost:5000")
    
    # Get customer first
    customer = client.get_customer_by_email("customer1@example.com")
    
    if customer and customer.get('subscriptions'):
        subscription = customer['subscriptions'][0]
        
        # Get traffic
        traffic = client.get_subscription_traffic(subscription['id'])
        
        if traffic.get('success'):
            print("📊 Traffic Statistics:")
            print(f"Download: {traffic['traffic']['download_gb']} GB")
            print(f"Upload: {traffic['traffic']['upload_gb']} GB")
            print(f"Total: {traffic['traffic']['total_gb']} GB")
            print(f"Limit: {traffic['traffic']['limit_gb']} GB")
            print(f"Remaining: {traffic['traffic']['remaining_gb']} GB")
        else:
            print(f"❌ Error: {traffic.get('error')}")
    else:
        print("❌ Customer not found")


def example_5_payment_webhook():
    """Example 5: Payment gateway webhook integration"""
    print("\n" + "=" * 50)
    print("Example 5: Payment Webhook Simulation")
    print("=" * 50)
    
    # Simulated payment data from payment gateway
    payment_data = {
        "customer_email": "payment@example.com",
        "customer_name": "Alice Wonder",
        "customer_phone": "+9876543210",
        "plan": "Monthly Basic",
        "amount_paid": 10.00,
        "currency": "USD"
    }
    
    # Map payment plan to VPN plan
    plan_mapping = {
        "Monthly Basic": {"traffic_gb": 100, "days": 30},
        "Monthly Premium": {"traffic_gb": 500, "days": 30},
        "Yearly Premium": {"traffic_gb": 500, "days": 365}
    }
    
    plan_config = plan_mapping.get(payment_data["plan"], {"traffic_gb": 100, "days": 30})
    
    # Create VPN account
    client = VPNManagerClient("http://localhost:5000")
    
    result = client.register_customer(
        email=payment_data["customer_email"],
        name=payment_data["customer_name"],
        phone=payment_data["customer_phone"],
        service_name=payment_data["plan"],
        traffic_limit_gb=plan_config["traffic_gb"],
        expiry_days=plan_config["days"]
    )
    
    if result.get('success'):
        print("✅ VPN account created after payment!")
        print(f"Customer: {payment_data['customer_name']}")
        print(f"Plan: {payment_data['plan']}")
        print(f"UUID: {result['subscription']['uuid']}")
        print("\n📧 You would now send email to customer with:")
        print(f"   - UUID: {result['subscription']['uuid']}")
        print(f"   - Configuration link")
        print(f"   - Setup instructions")
    else:
        print(f"❌ Error: {result.get('error')}")


def example_6_renew_subscription():
    """Example 6: Renew/extend existing subscription"""
    print("\n" + "=" * 50)
    print("Example 6: Renew Subscription")
    print("=" * 50)
    
    client = VPNManagerClient("http://localhost:5000")
    
    # Get existing customer
    customer = client.get_customer_by_email("customer1@example.com")
    
    if customer:
        # Create new subscription for renewal
        result = client.create_subscription(
            customer_id=customer['id'],
            service_name="Renewal - Standard Plan",
            traffic_limit_gb=100,
            expiry_days=30
        )
        
        if result.get('success'):
            print("✅ Subscription renewed!")
            print(f"New UUID: {result['subscription']['uuid']}")
        else:
            print(f"❌ Error: {result.get('error')}")
    else:
        print("❌ Customer not found")


# ==================== ADVANCED EXAMPLES ====================

def example_7_bulk_registration():
    """Example 7: Bulk customer registration"""
    print("\n" + "=" * 50)
    print("Example 7: Bulk Registration")
    print("=" * 50)
    
    client = VPNManagerClient("http://localhost:5000")
    
    customers = [
        {"email": f"bulk{i}@example.com", "name": f"Bulk User {i}"}
        for i in range(1, 4)
    ]
    
    success_count = 0
    for customer_data in customers:
        result = client.register_customer(**customer_data)
        if result.get('success'):
            success_count += 1
            print(f"✅ {customer_data['email']} - Created")
        else:
            print(f"❌ {customer_data['email']} - {result.get('error')}")
    
    print(f"\n📊 Created {success_count}/{len(customers)} accounts")


# ==================== MAIN ====================

if __name__ == "__main__":
    print("""
    🚀 VPN Manager API Integration Examples
    
    This script demonstrates various integration scenarios.
    Make sure the VPN Manager API is running at http://localhost:5000
    """)
    
    try:
        # Run examples
        example_1_simple_registration()
        example_2_custom_plan()
        example_3_unlimited_plan()
        # example_4_check_traffic()  # Uncomment if you have existing data
        example_5_payment_webhook()
        # example_6_renew_subscription()  # Uncomment if you have existing data
        # example_7_bulk_registration()  # Uncomment for bulk testing
        
        print("\n" + "=" * 50)
        print("✅ All examples completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API")
        print("Make sure the VPN Manager is running at http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
