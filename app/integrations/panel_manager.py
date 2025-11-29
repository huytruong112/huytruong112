"""
Panel Manager - Unified interface for X-UI and 3X-UI panels
"""
import uuid as uuid_lib
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
from config import Config
from .xui_client import XUIClient
from .three_xui_client import ThreeXUIClient

logger = logging.getLogger(__name__)


class PanelManager:
    """Unified manager for X-UI and 3X-UI panels"""
    
    def __init__(self):
        """Initialize panel manager based on configuration"""
        self.panel_type = Config.PANEL_TYPE.lower()
        
        if self.panel_type == 'xui':
            self.client = XUIClient(
                base_url=Config.XUI_PANEL_URL,
                username=Config.XUI_USERNAME,
                password=Config.XUI_PASSWORD
            )
        elif self.panel_type == '3xui':
            self.client = ThreeXUIClient(
                base_url=Config.THREE_XUI_PANEL_URL,
                username=Config.THREE_XUI_USERNAME,
                password=Config.THREE_XUI_PASSWORD
            )
        else:
            raise ValueError(f"Invalid panel type: {self.panel_type}")
    
    def create_client_config(self, 
                            email: str,
                            inbound_id: int = 1,
                            traffic_gb: Optional[int] = None,
                            expiry_days: Optional[int] = None,
                            enable: bool = True) -> Optional[Dict]:
        """
        Create a new client configuration
        
        Args:
            email: Client email/identifier (must be unique)
            inbound_id: ID of the inbound to add client to (default: 1)
            traffic_gb: Total traffic limit in GB (None uses default from config)
            expiry_days: Days until expiry (None uses default from config)
            enable: Whether client is enabled
        
        Returns:
            Dict containing client info (uuid, email, config_url) or None if failed
        """
        try:
            # Generate UUID for client
            client_uuid = str(uuid_lib.uuid4())
            
            # Use defaults from config if not specified
            if traffic_gb is None:
                traffic_gb = Config.DEFAULT_TRAFFIC_GB
            if expiry_days is None:
                expiry_days = Config.DEFAULT_EXPIRY_DAYS
            
            # Calculate expiry time in milliseconds
            expiry_time = 0
            if expiry_days > 0:
                expiry_date = datetime.now() + timedelta(days=expiry_days)
                expiry_time = int(expiry_date.timestamp() * 1000)
            
            # Convert GB to bytes
            total_bytes = traffic_gb * 1024 * 1024 * 1024 if traffic_gb > 0 else 0
            
            # Create client based on panel type
            if self.panel_type == 'xui':
                result = self.client.add_client(
                    inbound_id=inbound_id,
                    email=email,
                    uuid=client_uuid,
                    total_gb=traffic_gb,
                    expiry_time=expiry_time,
                    enable=enable,
                    flow="xtls-rprx-vision"
                )
            else:  # 3xui
                client_data = {
                    "id": client_uuid,
                    "email": email,
                    "limitIp": 0,
                    "totalGB": total_bytes,
                    "expiryTime": expiry_time,
                    "enable": enable,
                    "tgId": "",
                    "subId": "",
                    "reset": 0
                }
                result = self.client.add_client(inbound_id, client_data)
            
            if result:
                return {
                    'uuid': client_uuid,
                    'email': email,
                    'inbound_id': inbound_id,
                    'traffic_gb': traffic_gb,
                    'expiry_time': expiry_time,
                    'enabled': enable
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating client config: {e}")
            return None
    
    def update_client_config(self,
                            uuid: str,
                            inbound_id: int,
                            email: str,
                            traffic_gb: int,
                            expiry_days: int,
                            enable: bool = True) -> bool:
        """
        Update an existing client configuration
        
        Args:
            uuid: Client UUID
            inbound_id: ID of the inbound
            email: Client email/identifier
            traffic_gb: Total traffic limit in GB
            expiry_days: Days until expiry
            enable: Whether client is enabled
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Calculate expiry time
            expiry_time = 0
            if expiry_days > 0:
                expiry_date = datetime.now() + timedelta(days=expiry_days)
                expiry_time = int(expiry_date.timestamp() * 1000)
            
            if self.panel_type == 'xui':
                return self.client.update_client(
                    inbound_id=inbound_id,
                    uuid=uuid,
                    email=email,
                    total_gb=traffic_gb,
                    expiry_time=expiry_time,
                    enable=enable,
                    flow="xtls-rprx-vision"
                )
            else:  # 3xui
                total_bytes = traffic_gb * 1024 * 1024 * 1024 if traffic_gb > 0 else 0
                client_data = {
                    "id": uuid,
                    "email": email,
                    "limitIp": 0,
                    "totalGB": total_bytes,
                    "expiryTime": expiry_time,
                    "enable": enable,
                    "tgId": "",
                    "subId": "",
                    "reset": 0
                }
                return self.client.update_client(uuid, client_data)
                
        except Exception as e:
            logger.error(f"Error updating client config: {e}")
            return False
    
    def delete_client_config(self, inbound_id: int, uuid: str) -> bool:
        """
        Delete a client configuration
        
        Args:
            inbound_id: ID of the inbound
            uuid: Client UUID
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.client.delete_client(inbound_id, uuid)
        except Exception as e:
            logger.error(f"Error deleting client config: {e}")
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
            if self.panel_type == 'xui':
                return self.client.get_client_traffic(email)
            else:  # 3xui
                return self.client.get_client_traffics(email)
        except Exception as e:
            logger.error(f"Error getting client traffic: {e}")
            return None
    
    def get_inbounds(self) -> Optional[List[Dict]]:
        """
        Get list of all inbounds
        
        Returns:
            List of inbound configurations or None if failed
        """
        try:
            if self.panel_type == 'xui':
                return self.client.get_inbounds()
            else:  # 3xui
                return self.client.list_inbounds()
        except Exception as e:
            logger.error(f"Error getting inbounds: {e}")
            return None
    
    def reset_client_traffic(self, inbound_id: int, email: str) -> bool:
        """
        Reset traffic statistics for a client (3X-UI only)
        
        Args:
            inbound_id: ID of the inbound
            email: Client email/identifier
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.panel_type == '3xui':
                return self.client.reset_client_traffic(inbound_id, email)
            else:
                logger.warning("Traffic reset not supported for X-UI")
                return False
        except Exception as e:
            logger.error(f"Error resetting client traffic: {e}")
            return False
