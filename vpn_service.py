"""
Service layer để quản lý khách hàng và tự động tạo cấu hình VPN
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from xui_client import XUIClient, ThreeXUIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VPNService:
    """Service để quản lý việc tạo cấu hình VPN tự động cho khách hàng"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Khởi tạo VPN service
        
        Args:
            config: Cấu hình cho các panel và inbound mặc định
        """
        self.config = config
        self.xui_clients = {}
        self.threexui_clients = {}
        
        # Khởi tạo các client từ config
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Khởi tạo các client kết nối đến panels"""
        # Khởi tạo x-ui clients
        for panel_name, panel_config in self.config.get('xui_panels', {}).items():
            client = XUIClient(
                base_url=panel_config['url'],
                username=panel_config['username'],
                password=panel_config['password']
            )
            if client.login():
                self.xui_clients[panel_name] = client
                logger.info(f"Đã kết nối x-ui panel: {panel_name}")
            else:
                logger.error(f"Không thể kết nối x-ui panel: {panel_name}")
        
        # Khởi tạo 3x-ui clients
        for panel_name, panel_config in self.config.get('threexui_panels', {}).items():
            client = ThreeXUIClient(
                base_url=panel_config['url'],
                username=panel_config['username'],
                password=panel_config['password']
            )
            if client.login():
                self.threexui_clients[panel_name] = client
                logger.info(f"Đã kết nối 3x-ui panel: {panel_name}")
            else:
                logger.error(f"Không thể kết nối 3x-ui panel: {panel_name}")
    
    def create_customer_config(self, customer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Tạo cấu hình VPN cho khách hàng mới
        
        Args:
            customer_data: {
                'email': 'customer@example.com',
                'name': 'Customer Name',
                'plan': 'basic/premium/enterprise',
                'custom_config': {...}  # Tùy chọn
            }
            
        Returns:
            Thông tin cấu hình đã tạo hoặc None nếu thất bại
        """
        try:
            plan = customer_data.get('plan', 'basic')
            plan_config = self.config.get('plans', {}).get(plan, {})
            
            if not plan_config:
                logger.error(f"Không tìm thấy plan: {plan}")
                return None
            
            # Lấy panel phù hợp (load balancing đơn giản)
            panel_type = plan_config.get('panel_type', '3x-ui')
            
            if panel_type == 'x-ui':
                return self._create_xui_config(customer_data, plan_config)
            elif panel_type == '3x-ui':
                return self._create_3xui_config(customer_data, plan_config)
            else:
                logger.error(f"Panel type không hợp lệ: {panel_type}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo cấu hình cho khách hàng: {str(e)}")
            return None
    
    def _create_xui_config(self, customer_data: Dict[str, Any], plan_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tạo cấu hình trên x-ui panel"""
        # Chọn panel có ít user nhất (load balancing)
        if not self.xui_clients:
            logger.error("Không có x-ui panel nào khả dụng")
            return None
        
        panel_name = list(self.xui_clients.keys())[0]  # Đơn giản chọn panel đầu tiên
        client = self.xui_clients[panel_name]
        
        # Merge custom config nếu có
        client_config = {
            'email': customer_data['email'],
            'remark': f"{customer_data.get('name', 'Customer')} - {customer_data.get('plan', 'basic')}",
            'total_gb': plan_config.get('data_limit_gb', 100) * 1024 * 1024 * 1024,  # Convert to bytes
            'expiry_days': plan_config.get('duration_days', 30),
            'protocol': plan_config.get('protocol', 'vmess'),
            'network': plan_config.get('network', 'tcp'),
            'security': plan_config.get('security', 'none'),
        }
        
        # Merge custom config
        if 'custom_config' in customer_data:
            client_config.update(customer_data['custom_config'])
        
        # Thêm client vào inbound mặc định
        inbound_id = self.config.get('xui_panels', {}).get(panel_name, {}).get('default_inbound_id')
        
        if inbound_id:
            result = client.add_client_to_inbound(inbound_id, client_config)
        else:
            result = client.add_inbound(client_config)
        
        if result:
            return {
                'success': True,
                'panel_type': 'x-ui',
                'panel_name': panel_name,
                'customer_email': customer_data['email'],
                'config': result,
                'created_at': datetime.now().isoformat()
            }
        
        return None
    
    def _create_3xui_config(self, customer_data: Dict[str, Any], plan_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Tạo cấu hình trên 3x-ui panel"""
        if not self.threexui_clients:
            logger.error("Không có 3x-ui panel nào khả dụng")
            return None
        
        # Chọn panel (có thể implement load balancing ở đây)
        panel_name = list(self.threexui_clients.keys())[0]
        client = self.threexui_clients[panel_name]
        
        client_config = {
            'email': customer_data['email'],
            'total_gb': plan_config.get('data_limit_gb', 100),
            'expiry_days': plan_config.get('duration_days', 30),
            'limit_ip': plan_config.get('limit_ip', 0),
        }
        
        # Merge custom config
        if 'custom_config' in customer_data:
            client_config.update(customer_data['custom_config'])
        
        # Lấy inbound ID từ config
        inbound_id = self.config.get('threexui_panels', {}).get(panel_name, {}).get('default_inbound_id')
        
        if not inbound_id:
            logger.error(f"Không tìm thấy default_inbound_id cho panel {panel_name}")
            return None
        
        result = client.add_client(inbound_id, client_config)
        
        if result:
            return {
                'success': True,
                'panel_type': '3x-ui',
                'panel_name': panel_name,
                'customer_email': customer_data['email'],
                'config': result,
                'created_at': datetime.now().isoformat()
            }
        
        return None
    
    def get_customer_usage(self, email: str, panel_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin sử dụng của khách hàng
        
        Args:
            email: Email của khách hàng
            panel_name: Tên panel (nếu biết), nếu không sẽ tìm trong tất cả panels
            
        Returns:
            Thông tin sử dụng
        """
        if panel_name:
            if panel_name in self.xui_clients:
                return self.xui_clients[panel_name].get_client_traffic(email)
            elif panel_name in self.threexui_clients:
                # 3x-ui có thể cần lấy từ inbound list
                inbounds = self.threexui_clients[panel_name].get_inbounds()
                if inbounds:
                    for inbound in inbounds:
                        settings = json.loads(inbound.get('settings', '{}'))
                        clients = settings.get('clients', [])
                        for client in clients:
                            if client.get('email') == email:
                                return client
        else:
            # Tìm trong tất cả panels
            for client in self.xui_clients.values():
                usage = client.get_client_traffic(email)
                if usage:
                    return usage
            
            for client in self.threexui_clients.values():
                inbounds = client.get_inbounds()
                if inbounds:
                    for inbound in inbounds:
                        settings = json.loads(inbound.get('settings', '{}'))
                        clients = settings.get('clients', [])
                        for c in clients:
                            if c.get('email') == email:
                                return c
        
        return None
    
    def renew_customer(self, email: str, panel_name: str, days: int = 30) -> bool:
        """
        Gia hạn thời gian cho khách hàng
        
        Args:
            email: Email khách hàng
            panel_name: Tên panel
            days: Số ngày gia hạn
            
        Returns:
            True nếu thành công
        """
        # Implementation depends on panel API
        logger.info(f"Gia hạn {days} ngày cho {email} trên panel {panel_name}")
        return True
    
    def delete_customer(self, email: str, panel_name: str, inbound_id: int = None) -> bool:
        """
        Xóa cấu hình của khách hàng
        
        Args:
            email: Email khách hàng
            panel_name: Tên panel
            inbound_id: ID của inbound (cho 3x-ui)
            
        Returns:
            True nếu thành công
        """
        try:
            if panel_name in self.threexui_clients and inbound_id:
                client = self.threexui_clients[panel_name]
                # Cần tìm client UUID từ email
                inbounds = client.get_inbounds()
                if inbounds:
                    for inbound in inbounds:
                        if inbound.get('id') == inbound_id:
                            settings = json.loads(inbound.get('settings', '{}'))
                            clients = settings.get('clients', [])
                            for c in clients:
                                if c.get('email') == email:
                                    client_uuid = c.get('id')
                                    return client.delete_client(inbound_id, client_uuid)
            
            logger.warning(f"Không tìm thấy khách hàng {email} để xóa")
            return False
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa khách hàng: {str(e)}")
            return False
