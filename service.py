from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Tuple
import random

from database import Customer, VPNConfig, ServiceStatus, PanelType
from xui_client import xui_manager, XUIClient
from auth import get_password_hash
from config import settings
import schemas


class VPNService:
    """Service for managing VPN configurations"""
    
    @staticmethod
    async def create_customer_with_vpn(
        db: Session,
        registration: schemas.ServiceRegistration
    ) -> Tuple[Customer, VPNConfig]:
        """
        Create a new customer and automatically provision VPN configuration
        
        This is the main function that handles the entire registration flow:
        1. Create customer account
        2. Select appropriate panel and inbound
        3. Create VPN client in the panel
        4. Store configuration in database
        """
        
        # Check if customer already exists
        existing = db.query(Customer).filter(
            (Customer.email == registration.email) | 
            (Customer.username == registration.username)
        ).first()
        
        if existing:
            raise ValueError("Customer with this email or username already exists")
        
        # Create customer
        customer = Customer(
            email=registration.email,
            username=registration.username,
            hashed_password=get_password_hash(registration.password),
            full_name=registration.full_name,
            phone=registration.phone
        )
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        try:
            # Select panel and create VPN configuration
            vpn_config = await VPNService._create_vpn_config(
                db=db,
                customer=customer,
                panel_type=registration.panel_type,
                inbound_id=registration.inbound_id,
                traffic_limit_gb=registration.traffic_limit_gb,
                service_duration_days=registration.service_duration_days
            )
            
            return customer, vpn_config
            
        except Exception as e:
            # If VPN creation fails, rollback customer creation
            db.delete(customer)
            db.commit()
            raise Exception(f"Failed to create VPN configuration: {str(e)}")
    
    @staticmethod
    async def _create_vpn_config(
        db: Session,
        customer: Customer,
        panel_type: Optional[PanelType],
        inbound_id: Optional[int],
        traffic_limit_gb: int,
        service_duration_days: int
    ) -> VPNConfig:
        """Create VPN configuration on the panel"""
        
        # Select panel if not specified
        if not panel_type:
            available_panels = xui_manager.get_available_panels()
            if not available_panels:
                raise Exception("No x-ui panels are configured")
            
            # Select first available panel
            panel_type = available_panels[0]
        
        # Get panel client
        panel_client = xui_manager.get_panel(panel_type)
        if not panel_client:
            raise Exception(f"Panel {panel_type} is not available")
        
        # Login to panel
        login_success = await panel_client.login()
        if not login_success:
            raise Exception(f"Failed to login to panel {panel_type}")
        
        # Get available inbounds
        inbounds = await panel_client.get_inbounds()
        if not inbounds:
            raise Exception("No inbounds available on the panel")
        
        # Select inbound if not specified
        if not inbound_id:
            # Select first active inbound
            active_inbounds = [i for i in inbounds if i.get("enable", False)]
            if not active_inbounds:
                raise Exception("No active inbounds available")
            
            inbound_id = active_inbounds[0].get("id")
        
        # Create client on the panel
        result = await panel_client.add_client_to_inbound(
            inbound_id=inbound_id,
            email=customer.email,
            traffic_limit_gb=traffic_limit_gb,
            expiry_days=service_duration_days
        )
        
        if not result.get("success"):
            raise Exception(f"Failed to create client: {result.get('msg')}")
        
        # Create VPN config record in database
        now = datetime.utcnow()
        vpn_config = VPNConfig(
            customer_id=customer.id,
            panel_type=panel_type,
            panel_inbound_id=inbound_id,
            panel_client_id=result.get("client_id"),
            config_name=f"{customer.username}-{panel_type.value}",
            protocol=inbounds[0].get("protocol", "vless") if inbounds else "vless",
            traffic_limit_gb=traffic_limit_gb,
            traffic_used_gb=0,
            service_status=ServiceStatus.ACTIVE,
            activated_at=now,
            expires_at=now + timedelta(days=service_duration_days),
            connection_url=result.get("connection_url"),
            subscription_url=None  # Can be implemented later
        )
        
        db.add(vpn_config)
        db.commit()
        db.refresh(vpn_config)
        
        return vpn_config
    
    @staticmethod
    async def renew_vpn_service(
        db: Session,
        vpn_config: VPNConfig,
        additional_days: int,
        additional_traffic_gb: Optional[int] = None
    ) -> VPNConfig:
        """Renew VPN service for a customer"""
        
        panel_client = xui_manager.get_panel(vpn_config.panel_type)
        if not panel_client:
            raise Exception(f"Panel {vpn_config.panel_type} is not available")
        
        # Update expiry date
        if vpn_config.expires_at and vpn_config.expires_at > datetime.utcnow():
            new_expiry = vpn_config.expires_at + timedelta(days=additional_days)
        else:
            new_expiry = datetime.utcnow() + timedelta(days=additional_days)
        
        vpn_config.expires_at = new_expiry
        vpn_config.service_status = ServiceStatus.ACTIVE
        
        # Update traffic limit if specified
        if additional_traffic_gb:
            new_limit = (vpn_config.traffic_limit_gb or 0) + additional_traffic_gb
            vpn_config.traffic_limit_gb = new_limit
            
            # Update on panel
            await panel_client.update_client_traffic(
                inbound_id=vpn_config.panel_inbound_id,
                client_id=vpn_config.panel_client_id,
                traffic_limit_gb=new_limit
            )
        
        db.commit()
        db.refresh(vpn_config)
        
        return vpn_config
    
    @staticmethod
    async def suspend_vpn_service(
        db: Session,
        vpn_config: VPNConfig
    ) -> VPNConfig:
        """Suspend VPN service"""
        
        panel_client = xui_manager.get_panel(vpn_config.panel_type)
        if not panel_client:
            raise Exception(f"Panel {vpn_config.panel_type} is not available")
        
        # Delete client from panel
        success = await panel_client.delete_client(
            inbound_id=vpn_config.panel_inbound_id,
            client_id=vpn_config.panel_client_id
        )
        
        if success:
            vpn_config.service_status = ServiceStatus.SUSPENDED
            db.commit()
            db.refresh(vpn_config)
        
        return vpn_config
    
    @staticmethod
    async def get_client_stats(vpn_config: VPNConfig) -> Optional[dict]:
        """Get client usage statistics from panel"""
        
        panel_client = xui_manager.get_panel(vpn_config.panel_type)
        if not panel_client:
            return None
        
        customer = vpn_config.customer
        stats = await panel_client.get_client_stats(customer.email)
        
        return stats
    
    @staticmethod
    async def get_available_panels():
        """Get information about available panels"""
        panels_info = []
        
        for panel_type in xui_manager.get_available_panels():
            panel_client = xui_manager.get_panel(panel_type)
            if not panel_client:
                continue
            
            try:
                await panel_client.login()
                inbounds = await panel_client.get_inbounds()
                
                panels_info.append({
                    "panel_type": panel_type,
                    "is_enabled": True,
                    "inbound_count": len(inbounds),
                    "available": True
                })
            except Exception as e:
                panels_info.append({
                    "panel_type": panel_type,
                    "is_enabled": True,
                    "inbound_count": 0,
                    "available": False,
                    "error": str(e)
                })
        
        return panels_info
