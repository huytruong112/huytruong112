import httpx
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ThreeXUIClient:
    """Client for 3x-ui panel API (mhsanaei/3x-ui)"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session_cookie: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def login(self) -> bool:
        """Login to 3x-ui panel"""
        try:
            response = await self.client.post(
                f"{self.base_url}/login",
                data={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Store session cookie
                    self.session_cookie = response.cookies.get("3x-ui")
                    logger.info("Successfully logged in to 3x-ui panel")
                    return True
            
            logger.error(f"Login failed: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    async def ensure_authenticated(self):
        """Ensure we have a valid session"""
        if not self.session_cookie:
            await self.login()
    
    async def get_inbounds(self) -> List[Dict[str, Any]]:
        """Get all inbounds"""
        await self.ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/list",
                cookies={"3x-ui": self.session_cookie}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("obj", [])
            
            return []
        except Exception as e:
            logger.error(f"Error getting inbounds: {e}")
            return []
    
    async def add_client(
        self,
        inbound_id: int,
        email: str,
        uuid: str,
        traffic_limit_gb: float = 0,
        expiry_days: int = 30,
        enable: bool = True,
        flow: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Add a new client to an inbound"""
        await self.ensure_authenticated()
        
        # Calculate expiry time in milliseconds
        expiry_time = int((datetime.utcnow() + timedelta(days=expiry_days)).timestamp() * 1000)
        
        # Traffic limit in bytes (0 means unlimited)
        total_gb = int(traffic_limit_gb * 1024 * 1024 * 1024) if traffic_limit_gb > 0 else 0
        
        client_data = {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [{
                    "id": uuid,
                    "flow": flow,
                    "email": email,
                    "limitIp": 0,
                    "totalGB": total_gb,
                    "expiryTime": expiry_time,
                    "enable": enable,
                    "tgId": "",
                    "subId": ""
                }]
            })
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/addClient",
                json=client_data,
                cookies={"3x-ui": self.session_cookie}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Successfully added client: {email}")
                    return {
                        "email": email,
                        "uuid": uuid,
                        "inbound_id": inbound_id
                    }
            
            logger.error(f"Failed to add client: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return None
    
    async def update_client(
        self,
        inbound_id: int,
        uuid: str,
        email: str,
        traffic_limit_gb: float = 0,
        expiry_days: Optional[int] = None,
        enable: bool = True,
        flow: str = ""
    ) -> bool:
        """Update an existing client"""
        await self.ensure_authenticated()
        
        expiry_time = 0
        if expiry_days:
            expiry_time = int((datetime.utcnow() + timedelta(days=expiry_days)).timestamp() * 1000)
        
        total_gb = int(traffic_limit_gb * 1024 * 1024 * 1024) if traffic_limit_gb > 0 else 0
        
        client_data = {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [{
                    "id": uuid,
                    "flow": flow,
                    "email": email,
                    "limitIp": 0,
                    "totalGB": total_gb,
                    "expiryTime": expiry_time,
                    "enable": enable,
                    "tgId": "",
                    "subId": ""
                }]
            })
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/updateClient/{uuid}",
                json=client_data,
                cookies={"3x-ui": self.session_cookie}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            
            return False
        except Exception as e:
            logger.error(f"Error updating client: {e}")
            return False
    
    async def delete_client(self, inbound_id: int, uuid: str) -> bool:
        """Delete a client"""
        await self.ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/{inbound_id}/delClient/{uuid}",
                cookies={"3x-ui": self.session_cookie}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            
            return False
        except Exception as e:
            logger.error(f"Error deleting client: {e}")
            return False
    
    async def get_client_traffic(self, email: str) -> Optional[Dict[str, Any]]:
        """Get traffic statistics for a client"""
        await self.ensure_authenticated()
        
        try:
            response = await self.client.get(
                f"{self.base_url}/panel/api/inbounds/getClientTraffics/{email}",
                cookies={"3x-ui": self.session_cookie}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("obj")
            
            return None
        except Exception as e:
            logger.error(f"Error getting client traffic: {e}")
            return None
    
    async def reset_client_traffic(self, inbound_id: int, email: str) -> bool:
        """Reset client traffic statistics"""
        await self.ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/panel/api/inbounds/{inbound_id}/resetClientTraffic/{email}",
                cookies={"3x-ui": self.session_cookie}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            
            return False
        except Exception as e:
            logger.error(f"Error resetting client traffic: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
