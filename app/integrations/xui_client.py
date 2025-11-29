"""
X-UI Panel API Client
Documentation: https://github.com/dopaemon/x-ui
"""
import requests
import json
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class XUIClient:
    """Client for interacting with X-UI panel API"""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize X-UI client
        
        Args:
            base_url: Base URL of X-UI panel (e.g., http://server-ip:54321)
            username: Admin username
            password: Admin password
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session_cookie = None
        
    def login(self) -> bool:
        """
        Login to X-UI panel and get session cookie
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            url = f"{self.base_url}/login"
            data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(url, data=data)
            
            if response.status_code == 200 and response.json().get('success'):
                logger.info("Successfully logged in to X-UI panel")
                return True
            else:
                logger.error(f"Failed to login to X-UI: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during X-UI login: {e}")
            return False
    
    def get_inbounds(self) -> Optional[List[Dict]]:
        """
        Get list of all inbounds
        
        Returns:
            List of inbound configurations or None if failed
        """
        try:
            if not self.session_cookie:
                if not self.login():
                    return None
            
            url = f"{self.base_url}/panel/api/inbounds/list"
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj', [])
            
            logger.error(f"Failed to get inbounds: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting inbounds: {e}")
            return None
    
    def add_client(self, inbound_id: int, email: str, uuid: str, 
                   total_gb: int, expiry_time: int, enable: bool = True,
                   flow: str = "") -> Optional[Dict]:
        """
        Add a new client to an inbound
        
        Args:
            inbound_id: ID of the inbound to add client to
            email: Client email/identifier
            uuid: Client UUID
            total_gb: Total traffic in GB (0 for unlimited)
            expiry_time: Expiry timestamp in milliseconds (0 for no expiry)
            enable: Whether client is enabled
            flow: Flow control (e.g., xtls-rprx-vision)
        
        Returns:
            Client configuration dict or None if failed
        """
        try:
            if not self.session_cookie:
                if not self.login():
                    return None
            
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            
            # Convert GB to bytes
            total_bytes = total_gb * 1024 * 1024 * 1024
            
            client_data = {
                "id": inbound_id,
                "settings": json.dumps({
                    "clients": [{
                        "id": uuid,
                        "flow": flow,
                        "email": email,
                        "limitIp": 0,
                        "totalGB": total_bytes,
                        "expiryTime": expiry_time,
                        "enable": enable,
                        "tgId": "",
                        "subId": ""
                    }]
                })
            }
            
            response = self.session.post(url, json=client_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Successfully added client {email}")
                    return {
                        'email': email,
                        'uuid': uuid,
                        'inbound_id': inbound_id
                    }
            
            logger.error(f"Failed to add client: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return None
    
    def delete_client(self, inbound_id: int, uuid: str) -> bool:
        """
        Delete a client from an inbound
        
        Args:
            inbound_id: ID of the inbound
            uuid: Client UUID to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.session_cookie:
                if not self.login():
                    return False
            
            url = f"{self.base_url}/panel/api/inbounds/{inbound_id}/delClient/{uuid}"
            response = self.session.post(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Successfully deleted client {uuid}")
                    return True
            
            logger.error(f"Failed to delete client: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting client: {e}")
            return False
    
    def update_client(self, inbound_id: int, uuid: str, email: str,
                     total_gb: int, expiry_time: int, enable: bool = True,
                     flow: str = "") -> bool:
        """
        Update an existing client
        
        Args:
            inbound_id: ID of the inbound
            uuid: Client UUID
            email: Client email/identifier
            total_gb: Total traffic in GB
            expiry_time: Expiry timestamp in milliseconds
            enable: Whether client is enabled
            flow: Flow control
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.session_cookie:
                if not self.login():
                    return False
            
            url = f"{self.base_url}/panel/api/inbounds/updateClient/{uuid}"
            
            total_bytes = total_gb * 1024 * 1024 * 1024
            
            client_data = {
                "id": inbound_id,
                "settings": json.dumps({
                    "clients": [{
                        "id": uuid,
                        "flow": flow,
                        "email": email,
                        "limitIp": 0,
                        "totalGB": total_bytes,
                        "expiryTime": expiry_time,
                        "enable": enable,
                        "tgId": "",
                        "subId": ""
                    }]
                })
            }
            
            response = self.session.post(url, json=client_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Successfully updated client {email}")
                    return True
            
            logger.error(f"Failed to update client: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating client: {e}")
            return False
    
    def get_client_traffic(self, email: str) -> Optional[Dict]:
        """
        Get traffic statistics for a client
        
        Args:
            email: Client email/identifier
        
        Returns:
            Dict with traffic stats or None if failed
        """
        try:
            if not self.session_cookie:
                if not self.login():
                    return None
            
            url = f"{self.base_url}/panel/api/inbounds/getClientTraffics/{email}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj')
            
            logger.error(f"Failed to get client traffic: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting client traffic: {e}")
            return None
