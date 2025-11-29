import httpx
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
from config import settings, PanelType


class XUIClient:
    """Client for interacting with x-ui and 3x-ui panels"""
    
    def __init__(self, panel_type: PanelType):
        self.panel_type = panel_type
        
        if panel_type == PanelType.XUI_1:
            self.base_url = settings.XUI_1_URL
            self.username = settings.XUI_1_USERNAME
            self.password = settings.XUI_1_PASSWORD
            self.enabled = settings.XUI_1_ENABLED
        elif panel_type == PanelType.XUI_2:
            self.base_url = settings.XUI_2_URL
            self.username = settings.XUI_2_USERNAME
            self.password = settings.XUI_2_PASSWORD
            self.enabled = settings.XUI_2_ENABLED
        else:
            raise ValueError(f"Unknown panel type: {panel_type}")
        
        self.session_cookie = None
        self.client = httpx.AsyncClient(verify=False, timeout=30.0)
    
    async def login(self) -> bool:
        """Login to the x-ui panel"""
        if not self.enabled:
            raise Exception(f"Panel {self.panel_type} is not enabled")
        
        login_url = f"{self.base_url}/login"
        
        try:
            response = await self.client.post(
                login_url,
                data={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            if response.status_code == 200:
                # Store session cookie
                self.session_cookie = response.cookies
                return True
            else:
                return False
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    async def get_inbounds(self) -> List[Dict[str, Any]]:
        """Get all inbounds from the panel"""
        if not self.session_cookie:
            await self.login()
        
        url = f"{self.base_url}/panel/api/inbounds/list"
        
        try:
            response = await self.client.get(
                url,
                cookies=self.session_cookie
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("obj", []) if data.get("success") else []
            return []
        except Exception as e:
            print(f"Error fetching inbounds: {e}")
            return []
    
    async def add_client_to_inbound(
        self,
        inbound_id: int,
        email: str,
        client_id: Optional[str] = None,
        traffic_limit_gb: int = 50,
        expiry_days: int = 30
    ) -> Dict[str, Any]:
        """Add a new client to an existing inbound"""
        if not self.session_cookie:
            await self.login()
        
        if not client_id:
            client_id = str(uuid.uuid4())
        
        # Calculate expiry timestamp (in milliseconds)
        expiry_time = int((datetime.now() + timedelta(days=expiry_days)).timestamp() * 1000)
        
        # Traffic limit in bytes (GB to bytes)
        total_gb = traffic_limit_gb * 1024 * 1024 * 1024
        
        # Prepare client data
        client_data = {
            "id": client_id,
            "email": email,
            "enable": True,
            "flow": "",
            "limitIp": 2,  # Max 2 simultaneous connections
            "totalGB": total_gb,
            "expiryTime": expiry_time,
            "tgId": "",
            "subId": ""
        }
        
        url = f"{self.base_url}/panel/api/inbounds/addClient"
        
        try:
            # Get existing inbound to add client
            inbound = await self.get_inbound(inbound_id)
            if not inbound:
                return {"success": False, "msg": "Inbound not found"}
            
            # Add client to settings
            settings_json = json.loads(inbound.get("settings", "{}"))
            if "clients" not in settings_json:
                settings_json["clients"] = []
            
            settings_json["clients"].append(client_data)
            
            # Update inbound with new client
            payload = {
                "id": inbound_id,
                "settings": json.dumps(settings_json)
            }
            
            response = await self.client.post(
                url,
                json=payload,
                cookies=self.session_cookie
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return {
                        "success": True,
                        "client_id": client_id,
                        "email": email,
                        "inbound_id": inbound_id,
                        "connection_url": self._generate_connection_url(inbound, client_data)
                    }
            
            return {"success": False, "msg": "Failed to add client"}
            
        except Exception as e:
            print(f"Error adding client: {e}")
            return {"success": False, "msg": str(e)}
    
    async def get_inbound(self, inbound_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific inbound by ID"""
        inbounds = await self.get_inbounds()
        for inbound in inbounds:
            if inbound.get("id") == inbound_id:
                return inbound
        return None
    
    async def delete_client(self, inbound_id: int, client_id: str) -> bool:
        """Delete a client from an inbound"""
        if not self.session_cookie:
            await self.login()
        
        url = f"{self.base_url}/panel/api/inbounds/delClient/{inbound_id}/{client_id}"
        
        try:
            response = await self.client.post(
                url,
                cookies=self.session_cookie
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            return False
            
        except Exception as e:
            print(f"Error deleting client: {e}")
            return False
    
    async def update_client_traffic(
        self,
        inbound_id: int,
        client_id: str,
        traffic_limit_gb: int
    ) -> bool:
        """Update client traffic limit"""
        if not self.session_cookie:
            await self.login()
        
        total_gb = traffic_limit_gb * 1024 * 1024 * 1024
        
        url = f"{self.base_url}/panel/api/inbounds/updateClient/{inbound_id}"
        
        try:
            payload = {
                "id": client_id,
                "totalGB": total_gb
            }
            
            response = await self.client.post(
                url,
                json=payload,
                cookies=self.session_cookie
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            return False
            
        except Exception as e:
            print(f"Error updating client traffic: {e}")
            return False
    
    def _generate_connection_url(self, inbound: Dict[str, Any], client: Dict[str, Any]) -> str:
        """Generate connection URL based on inbound and client data"""
        protocol = inbound.get("protocol", "vless")
        port = inbound.get("port")
        
        # Extract server address from base_url
        server = self.base_url.replace("http://", "").replace("https://", "").split(":")[0]
        
        client_id = client.get("id")
        email = client.get("email")
        
        # Basic connection URL (this is simplified, actual format depends on protocol)
        if protocol == "vless":
            stream_settings = json.loads(inbound.get("streamSettings", "{}"))
            network = stream_settings.get("network", "tcp")
            security = stream_settings.get("security", "none")
            
            url = f"vless://{client_id}@{server}:{port}?type={network}&security={security}#{email}"
            return url
        
        elif protocol == "vmess":
            vmess_config = {
                "v": "2",
                "ps": email,
                "add": server,
                "port": port,
                "id": client_id,
                "aid": "0",
                "net": "tcp",
                "type": "none",
                "host": "",
                "path": "",
                "tls": ""
            }
            import base64
            config_json = json.dumps(vmess_config)
            encoded = base64.b64encode(config_json.encode()).decode()
            return f"vmess://{encoded}"
        
        return f"{protocol}://client-{client_id}"
    
    async def get_client_stats(self, email: str) -> Optional[Dict[str, Any]]:
        """Get client statistics"""
        if not self.session_cookie:
            await self.login()
        
        # This endpoint varies by panel version
        url = f"{self.base_url}/panel/api/inbounds/clientStats/{email}"
        
        try:
            response = await self.client.get(
                url,
                cookies=self.session_cookie
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error fetching client stats: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class XUIManager:
    """Manager for handling multiple x-ui panels"""
    
    def __init__(self):
        self.panels = {}
        
        if settings.XUI_1_ENABLED:
            self.panels[PanelType.XUI_1] = XUIClient(PanelType.XUI_1)
        
        if settings.XUI_2_ENABLED:
            self.panels[PanelType.XUI_2] = XUIClient(PanelType.XUI_2)
    
    def get_panel(self, panel_type: PanelType) -> Optional[XUIClient]:
        """Get a specific panel client"""
        return self.panels.get(panel_type)
    
    def get_available_panels(self) -> List[PanelType]:
        """Get list of available panels"""
        return list(self.panels.keys())
    
    async def close_all(self):
        """Close all panel clients"""
        for panel in self.panels.values():
            await panel.close()


# Global manager instance
xui_manager = XUIManager()
