"""
Client API cho x-ui và 3x-ui panels
Hỗ trợ tự động tạo cấu hình VPN/Proxy cho khách hàng
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XUIClient:
    """Client để kết nối với x-ui panel"""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Khởi tạo client
        
        Args:
            base_url: URL của x-ui panel (vd: https://your-server.com:54321)
            username: Tên đăng nhập admin
            password: Mật khẩu admin
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session_cookie = None
        
    def login(self) -> bool:
        """Đăng nhập vào x-ui panel"""
        try:
            login_url = f"{self.base_url}/login"
            data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(login_url, data=data, verify=False)
            
            if response.status_code == 200 and response.json().get('success'):
                self.session_cookie = self.session.cookies.get_dict()
                logger.info("Đăng nhập x-ui thành công")
                return True
            else:
                logger.error(f"Đăng nhập x-ui thất bại: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập x-ui: {str(e)}")
            return False
    
    def add_inbound(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Thêm inbound mới cho khách hàng
        
        Args:
            client_data: Thông tin khách hàng và cấu hình
            
        Returns:
            Thông tin inbound đã tạo hoặc None nếu thất bại
        """
        try:
            url = f"{self.base_url}/panel/api/inbounds/add"
            
            # Tạo cấu hình inbound
            inbound_config = {
                "enable": True,
                "remark": client_data.get('remark', f"Client_{uuid.uuid4().hex[:8]}"),
                "listen": "",
                "port": client_data.get('port', 0),  # 0 = auto assign
                "protocol": client_data.get('protocol', 'vmess'),
                "expiryTime": client_data.get('expiry_time', 0),
                "settings": json.dumps({
                    "clients": [{
                        "id": str(uuid.uuid4()),
                        "email": client_data.get('email', ''),
                        "alterId": 0,
                        "expiryTime": client_data.get('expiry_time', 0),
                        "totalGB": client_data.get('total_gb', 0),
                        "enable": True
                    }],
                    "disableInsecureEncryption": False
                }),
                "streamSettings": json.dumps({
                    "network": client_data.get('network', 'tcp'),
                    "security": client_data.get('security', 'none'),
                    "tcpSettings": {},
                    "wsSettings": {
                        "path": client_data.get('ws_path', '/'),
                        "headers": {}
                    }
                }),
                "sniffing": json.dumps({
                    "enabled": True,
                    "destOverride": ["http", "tls"]
                })
            }
            
            response = self.session.post(url, json=inbound_config, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Tạo inbound thành công cho {client_data.get('email')}")
                    return result
                else:
                    logger.error(f"Tạo inbound thất bại: {result.get('msg')}")
                    return None
            else:
                logger.error(f"Lỗi API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo inbound: {str(e)}")
            return None
    
    def add_client_to_inbound(self, inbound_id: int, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Thêm client vào inbound có sẵn
        
        Args:
            inbound_id: ID của inbound
            client_data: Thông tin client
            
        Returns:
            Thông tin client đã tạo hoặc None nếu thất bại
        """
        try:
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            
            client_config = {
                "id": inbound_id,
                "settings": json.dumps({
                    "clients": [{
                        "id": str(uuid.uuid4()),
                        "email": client_data.get('email', ''),
                        "alterId": 0,
                        "expiryTime": client_data.get('expiry_time', 0),
                        "totalGB": client_data.get('total_gb', 0),
                        "enable": True
                    }]
                })
            }
            
            response = self.session.post(url, json=client_config, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Thêm client thành công: {client_data.get('email')}")
                    return result
                else:
                    logger.error(f"Thêm client thất bại: {result.get('msg')}")
                    return None
            else:
                logger.error(f"Lỗi API: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi thêm client: {str(e)}")
            return None
    
    def get_inbounds(self) -> Optional[List[Dict[str, Any]]]:
        """Lấy danh sách tất cả inbounds"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/list"
            response = self.session.get(url, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj', [])
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách inbounds: {str(e)}")
            return None
    
    def get_client_traffic(self, email: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin traffic của client"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/getClientTraffics/{email}"
            response = self.session.get(url, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj')
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy traffic: {str(e)}")
            return None


class ThreeXUIClient:
    """Client để kết nối với 3x-ui panel (API tương tự nhưng có thể có khác biệt nhỏ)"""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Khởi tạo client
        
        Args:
            base_url: URL của 3x-ui panel
            username: Tên đăng nhập admin
            password: Mật khẩu admin
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session_cookie = None
        
    def login(self) -> bool:
        """Đăng nhập vào 3x-ui panel"""
        try:
            login_url = f"{self.base_url}/login"
            data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(login_url, data=data, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.session_cookie = self.session.cookies.get_dict()
                    logger.info("Đăng nhập 3x-ui thành công")
                    return True
                    
            logger.error(f"Đăng nhập 3x-ui thất bại")
            return False
                
        except Exception as e:
            logger.error(f"Lỗi khi đăng nhập 3x-ui: {str(e)}")
            return False
    
    def add_client(self, inbound_id: int, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Thêm client vào inbound
        
        Args:
            inbound_id: ID của inbound
            client_data: Thông tin client
            
        Returns:
            Thông tin client đã tạo
        """
        try:
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            
            # Tính thời gian hết hạn (milliseconds)
            expiry_days = client_data.get('expiry_days', 30)
            expiry_time = int((datetime.now() + timedelta(days=expiry_days)).timestamp() * 1000)
            
            # Tính dung lượng (bytes)
            total_gb = client_data.get('total_gb', 100)
            total_bytes = total_gb * 1024 * 1024 * 1024
            
            client_config = {
                "id": inbound_id,
                "settings": json.dumps({
                    "clients": [{
                        "id": str(uuid.uuid4()),
                        "flow": "",
                        "email": client_data.get('email', ''),
                        "limitIp": client_data.get('limit_ip', 0),
                        "totalGB": total_bytes,
                        "expiryTime": expiry_time,
                        "enable": True,
                        "tgId": "",
                        "subId": client_data.get('sub_id', str(uuid.uuid4().hex[:8]))
                    }]
                })
            }
            
            response = self.session.post(url, json=client_config, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Thêm client 3x-ui thành công: {client_data.get('email')}")
                    return {
                        'success': True,
                        'client_data': client_data,
                        'expiry_time': expiry_time,
                        'total_gb': total_gb
                    }
                else:
                    logger.error(f"Thêm client 3x-ui thất bại: {result.get('msg')}")
                    return None
            else:
                logger.error(f"Lỗi API: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi thêm client 3x-ui: {str(e)}")
            return None
    
    def get_inbounds(self) -> Optional[List[Dict[str, Any]]]:
        """Lấy danh sách tất cả inbounds"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/list"
            response = self.session.get(url, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj', [])
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách inbounds 3x-ui: {str(e)}")
            return None
    
    def update_client(self, inbound_id: int, client_uuid: str, client_data: Dict[str, Any]) -> bool:
        """Cập nhật thông tin client"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/updateClient/{client_uuid}"
            
            response = self.session.post(url, json=client_data, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật client: {str(e)}")
            return False
    
    def delete_client(self, inbound_id: int, client_uuid: str) -> bool:
        """Xóa client"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/{inbound_id}/delClient/{client_uuid}"
            
            response = self.session.post(url, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa client: {str(e)}")
            return False
    
    def get_client_ips(self, email: str) -> Optional[List[str]]:
        """Lấy danh sách IP của client"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/clientIps/{email}"
            response = self.session.get(url, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj', [])
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy client IPs: {str(e)}")
            return None
    
    def reset_client_traffic(self, inbound_id: int, email: str) -> bool:
        """Reset traffic của client"""
        try:
            url = f"{self.base_url}/panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}"
            
            response = self.session.post(url, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Lỗi khi reset traffic: {str(e)}")
            return False
