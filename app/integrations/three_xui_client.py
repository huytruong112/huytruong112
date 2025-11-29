"""
3X-UI Panel API Client
Documentation: https://github.com/mhsanaei/3x-ui
"""
import requests
import json
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class ThreeXUIClient:
    """Client for interacting with 3X-UI panel API"""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize 3X-UI client
        
        Args:
            base_url: Base URL of 3X-UI panel (e.g., http://server-ip:2053)
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
        Login to 3X-UI panel and get session cookie
        
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
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("Successfully logged in to 3X-UI panel")
                    return True
            
            logger.error(f"Failed to login to 3X-UI: {response.text}")
            return False
                
        except Exception as e:
            logger.error(f"Error during 3X-UI login: {e}")
            return False
    
    def list_inbounds(self) -> Optional[List[Dict]]:
        """
        Get list of all inbounds
        
        Returns:
            List of inbound configurations or None if failed
        """
        try:
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
    
    def get_inbound(self, inbound_id: int) -> Optional[Dict]:
        """
        Get a specific inbound by ID
        
        Args:
            inbound_id: ID of the inbound
        
        Returns:
            Inbound configuration dict or None if failed
        """
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/panel/api/inbounds/get/{inbound_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj')
            
            logger.error(f"Failed to get inbound: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting inbound: {e}")
            return None
    
    def add_client(self, inbound_id: int, client_data: Dict) -> Optional[Dict]:
        """
        Add a new client to an inbound
        
        Args:
            inbound_id: ID of the inbound to add client to
            client_data: Client configuration dict containing:
                - id: Client UUID
                - email: Client email/identifier
                - limitIp: IP limit (0 for no limit)
                - totalGB: Total traffic in bytes (0 for unlimited)
                - expiryTime: Expiry timestamp in milliseconds (0 for no expiry)
                - enable: Whether client is enabled
                - tgId: Telegram ID (optional)
                - subId: Subscription ID (optional)
                - reset: Reset period in days (0 for no reset)
        
        Returns:
            Client configuration dict or None if failed
        """
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            
            payload = {
                "id": inbound_id,
                "settings": json.dumps({
                    "clients": [client_data]
                })
            }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Successfully added client {client_data.get('email')}")
                    return client_data
            
            logger.error(f"Failed to add client: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return None
    
    def update_client(self, uuid: str, client_data: Dict) -> bool:
        """
        Update an existing client
        
        Args:
            uuid: Client UUID
            client_data: Updated client configuration dict
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.login():
                return False
            
            url = f"{self.base_url}/panel/api/inbounds/updateClient/{uuid}"
            
            response = self.session.post(url, json=client_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Successfully updated client {uuid}")
                    return True
            
            logger.error(f"Failed to update client: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating client: {e}")
            return False
    
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
    
    def reset_client_traffic(self, inbound_id: int, email: str) -> bool:
        """
        Reset traffic statistics for a client
        
        Args:
            inbound_id: ID of the inbound
            email: Client email/identifier
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.login():
                return False
            
            url = f"{self.base_url}/panel/api/inbounds/resetClientTraffic/{inbound_id}/{email}"
            response = self.session.post(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"Successfully reset traffic for client {email}")
                    return True
            
            logger.error(f"Failed to reset client traffic: {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Error resetting client traffic: {e}")
            return False
    
    def get_client_traffics(self, email: str) -> Optional[Dict]:
        """
        Get traffic statistics for a specific client
        
        Args:
            email: Client email/identifier
        
        Returns:
            Dict with traffic stats or None if failed
        """
        try:
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
    
    def get_all_client_stats(self) -> Optional[List[Dict]]:
        """
        Get traffic statistics for all clients
        
        Returns:
            List of client traffic stats or None if failed
        """
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/panel/api/inbounds/clientStats"
            response = self.session.get(url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('obj', [])
            
            logger.error(f"Failed to get client stats: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting client stats: {e}")
            return None
    
    def create_backup(self) -> Optional[str]:
        """
        Create a backup of the database
        
        Returns:
            Backup data as string or None if failed
        """
        try:
            if not self.login():
                return None
            
            url = f"{self.base_url}/panel/api/inbounds/createbackup"
            response = self.session.get(url)
            
            if response.status_code == 200:
                logger.info("Successfully created backup")
                return response.text
            
            logger.error(f"Failed to create backup: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
