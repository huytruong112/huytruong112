"""
Ví dụ tích hợp VPN API với Python
Có thể sử dụng với Flask, Django, hoặc FastAPI
"""

import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VPNAPIClient:
    """Client để tương tác với VPN API"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def register_customer(
        self, 
        email: str, 
        name: str, 
        plan: str, 
        phone: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Đăng ký khách hàng mới"""
        try:
            url = f"{self.api_url}/api/v1/customer/register"
            data = {
                'email': email,
                'name': name,
                'plan': plan,
                'phone': phone,
                'custom_config': custom_config
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error registering customer: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_customer_usage(
        self, 
        email: str, 
        panel_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lấy thông tin usage của khách hàng"""
        try:
            url = f"{self.api_url}/api/v1/customer/usage"
            data = {
                'email': email,
                'panel_name': panel_name
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting usage: {e}")
            return {'success': False, 'error': str(e)}
    
    def renew_customer(
        self, 
        email: str, 
        panel_name: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Gia hạn dịch vụ"""
        try:
            url = f"{self.api_url}/api/v1/customer/renew"
            data = {
                'email': email,
                'panel_name': panel_name,
                'days': days
            }
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error renewing customer: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_customer(
        self, 
        email: str, 
        panel_name: str,
        inbound_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Xóa khách hàng"""
        try:
            url = f"{self.api_url}/api/v1/customer/delete"
            data = {
                'email': email,
                'panel_name': panel_name,
                'inbound_id': inbound_id
            }
            
            response = self.session.delete(url, json=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting customer: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_plans(self) -> Dict[str, Any]:
        """Lấy danh sách plans"""
        try:
            url = f"{self.api_url}/api/v1/plans"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting plans: {e}")
            return {'success': False, 'error': str(e)}


# ============================================
# Flask Integration Example
# ============================================

from flask import Flask, request, jsonify

app = Flask(__name__)

# Khởi tạo VPN API client
vpn_api = VPNAPIClient(
    api_url='http://localhost:8000',
    api_key='your_secret_api_key_here'
)


@app.route('/webhook/payment-success', methods=['POST'])
def payment_webhook():
    """Webhook từ payment gateway"""
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        customer_email = data.get('customer_email')
        customer_name = data.get('customer_name')
        plan = data.get('plan', 'basic')
        
        logger.info(f"Processing payment for order {order_id}")
        
        # Tạo VPN config
        result = vpn_api.register_customer(customer_email, customer_name, plan)
        
        if result['success']:
            # Lưu vào database
            save_vpn_config(order_id, customer_email, result['data'])
            
            # Gửi email
            send_vpn_email(customer_email, result['data'])
            
            return jsonify({'success': True, 'message': 'VPN created'}), 200
        else:
            logger.error(f"Failed to create VPN: {result}")
            return jsonify({'success': False, 'error': 'Failed to create VPN'}), 500
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/customer/<email>/usage', methods=['GET'])
def get_usage(email):
    """Lấy usage của khách hàng"""
    try:
        usage = vpn_api.get_customer_usage(email)
        
        if usage['success']:
            data = usage['data']
            used_bytes = (data.get('up', 0) + data.get('down', 0))
            total_bytes = data.get('total', data.get('totalGB', 0))
            used_percent = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
            
            return jsonify({
                'success': True,
                'data': {
                    'email': email,
                    'used': format_bytes(used_bytes),
                    'total': format_bytes(total_bytes),
                    'percent': round(used_percent, 2),
                    'expiry': data.get('expiryTime'),
                    'warning': used_percent > 80
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/customer/<email>/renew', methods=['POST'])
def renew_subscription(email):
    """Gia hạn dịch vụ"""
    try:
        data = request.get_json()
        panel_name = data.get('panel_name')
        months = data.get('months', 1)
        days = months * 30
        
        result = vpn_api.renew_customer(email, panel_name, days)
        
        if result['success']:
            update_renewal_date(email, days)
            send_renewal_email(email, days)
            return jsonify({'success': True, 'message': f'Renewed for {days} days'})
        else:
            return jsonify({'success': False, 'error': 'Failed to renew'}), 500
            
    except Exception as e:
        logger.error(f"Error renewing: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# Django Integration Example
# ============================================

# views.py
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def payment_webhook(request):
    try:
        data = json.loads(request.body)
        
        vpn_api = VPNAPIClient(
            api_url=settings.VPN_API_URL,
            api_key=settings.VPN_API_KEY
        )
        
        result = vpn_api.register_customer(
            email=data['customer_email'],
            name=data['customer_name'],
            plan=data['plan']
        )
        
        if result['success']:
            # Save to database
            VPNConfig.objects.create(
                order_id=data['order_id'],
                customer_email=data['customer_email'],
                config_data=result['data']
            )
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False}, status=500)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
"""


# ============================================
# Scheduled Tasks Example (using APScheduler)
# ============================================

from apscheduler.schedulers.background import BackgroundScheduler


def check_expiring_customers():
    """Kiểm tra khách hàng sắp hết hạn"""
    logger.info("Checking for expiring customers...")
    
    # Lấy danh sách khách hàng từ database
    customers = get_all_customers()
    
    for customer in customers:
        try:
            usage = vpn_api.get_customer_usage(customer['email'])
            
            if usage['success']:
                data = usage['data']
                expiry_time = data.get('expiryTime', 0)
                
                if expiry_time:
                    expiry_date = datetime.fromtimestamp(expiry_time / 1000)
                    days_remaining = (expiry_date - datetime.now()).days
                    
                    # Gửi email nhắc nhở nếu còn 3 ngày
                    if 0 < days_remaining <= 3:
                        send_expiry_warning(customer['email'], days_remaining)
                    
                    # Kiểm tra dung lượng
                    used_bytes = data.get('up', 0) + data.get('down', 0)
                    total_bytes = data.get('total', data.get('totalGB', 0))
                    
                    if total_bytes > 0:
                        used_percent = (used_bytes / total_bytes) * 100
                        if used_percent > 90:
                            send_data_warning(customer['email'], used_percent)
                            
        except Exception as e:
            logger.error(f"Error checking customer {customer['email']}: {e}")


def start_scheduler():
    """Khởi động scheduler"""
    scheduler = BackgroundScheduler()
    
    # Chạy mỗi ngày lúc 9 giờ sáng
    scheduler.add_job(
        check_expiring_customers,
        'cron',
        hour=9,
        minute=0
    )
    
    scheduler.start()
    logger.info("Scheduler started")


# ============================================
# Helper Functions
# ============================================

def format_bytes(bytes_value: int) -> str:
    """Format bytes thành human-readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def save_vpn_config(order_id: str, email: str, config_data: Dict):
    """Lưu cấu hình VPN vào database"""
    logger.info(f"Saving VPN config for order {order_id}")
    # Implement database save
    pass


def send_vpn_email(email: str, config_data: Dict):
    """Gửi email cấu hình VPN cho khách hàng"""
    logger.info(f"Sending VPN email to {email}")
    # Implement email sending
    pass


def update_renewal_date(email: str, days: int):
    """Cập nhật ngày gia hạn"""
    logger.info(f"Updating renewal for {email}: +{days} days")
    # Implement database update
    pass


def send_renewal_email(email: str, days: int):
    """Gửi email xác nhận gia hạn"""
    logger.info(f"Sending renewal email to {email}")
    pass


def get_all_customers():
    """Lấy danh sách khách hàng từ database"""
    # Implement database query
    return []


def send_expiry_warning(email: str, days_remaining: int):
    """Gửi cảnh báo sắp hết hạn"""
    logger.info(f"Sending expiry warning to {email}: {days_remaining} days")
    pass


def send_data_warning(email: str, used_percent: float):
    """Gửi cảnh báo dung lượng"""
    logger.info(f"Sending data warning to {email}: {used_percent:.2f}% used")
    pass


# ============================================
# Command Line Example
# ============================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='VPN API Client')
    parser.add_argument('action', choices=['register', 'usage', 'renew', 'delete', 'plans'])
    parser.add_argument('--email', help='Customer email')
    parser.add_argument('--name', help='Customer name')
    parser.add_argument('--plan', help='Plan name', default='basic')
    parser.add_argument('--panel', help='Panel name')
    parser.add_argument('--days', type=int, help='Days to renew', default=30)
    
    args = parser.parse_args()
    
    # Khởi tạo client
    client = VPNAPIClient(
        api_url='http://localhost:8000',
        api_key='your_secret_api_key_here'
    )
    
    if args.action == 'register':
        result = client.register_customer(args.email, args.name, args.plan)
        print(f"Registration result: {result}")
        
    elif args.action == 'usage':
        result = client.get_customer_usage(args.email, args.panel)
        print(f"Usage: {result}")
        
    elif args.action == 'renew':
        result = client.renew_customer(args.email, args.panel, args.days)
        print(f"Renewal result: {result}")
        
    elif args.action == 'delete':
        result = client.delete_customer(args.email, args.panel)
        print(f"Deletion result: {result}")
        
    elif args.action == 'plans':
        result = client.get_plans()
        print(f"Plans: {result}")
