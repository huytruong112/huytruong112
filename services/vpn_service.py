import uuid as uuid_lib
import json
import qrcode
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from models import Customer, Subscription, PanelType, SubscriptionStatus
from clients.xui_client import XUIClient
from clients.threexui_client import ThreeXUIClient
from config import settings

logger = logging.getLogger(__name__)


class VPNService:
    """Service for managing VPN subscriptions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.xui_client: Optional[XUIClient] = None
        self.threexui_client: Optional[ThreeXUIClient] = None
        
        # Initialize clients if configured
        if settings.xui_panel_url and settings.xui_username and settings.xui_password:
            self.xui_client = XUIClient(
                settings.xui_panel_url,
                settings.xui_username,
                settings.xui_password
            )
        
        if settings.threexui_panel_url and settings.threexui_username and settings.threexui_password:
            self.threexui_client = ThreeXUIClient(
                settings.threexui_panel_url,
                settings.threexui_username,
                settings.threexui_password
            )
    
    async def create_customer(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None
    ) -> Customer:
        """Create a new customer"""
        # Check if customer already exists
        result = await self.db.execute(
            select(Customer).where(Customer.email == email)
        )
        existing_customer = result.scalar_one_or_none()
        
        if existing_customer:
            return existing_customer
        
        customer = Customer(
            email=email,
            name=name,
            phone=phone
        )
        
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        
        logger.info(f"Created customer: {email}")
        return customer
    
    async def create_subscription(
        self,
        customer_id: int,
        panel_type: PanelType,
        inbound_id: int,
        traffic_limit_gb: Optional[float] = None,
        expiry_days: Optional[int] = None,
        protocol: Optional[str] = None
    ) -> Optional[Subscription]:
        """Create a new subscription for a customer"""
        
        # Get customer
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            logger.error(f"Customer not found: {customer_id}")
            return None
        
        # Use defaults if not specified
        traffic_limit = traffic_limit_gb or settings.default_traffic_limit_gb
        days = expiry_days or settings.default_expiry_days
        proto = protocol or settings.default_protocol
        
        # Generate UUID
        client_uuid = str(uuid_lib.uuid4())
        email_identifier = f"{customer.email}_{client_uuid[:8]}"
        
        # Create client in appropriate panel
        client_data = None
        if panel_type == PanelType.XUI and self.xui_client:
            client_data = await self.xui_client.add_client(
                inbound_id=inbound_id,
                email=email_identifier,
                uuid=client_uuid,
                traffic_limit_gb=traffic_limit,
                expiry_days=days
            )
        elif panel_type == PanelType.THREEXUI and self.threexui_client:
            client_data = await self.threexui_client.add_client(
                inbound_id=inbound_id,
                email=email_identifier,
                uuid=client_uuid,
                traffic_limit_gb=traffic_limit,
                expiry_days=days
            )
        
        if not client_data:
            logger.error(f"Failed to create client in panel")
            return None
        
        # Create subscription record
        subscription = Subscription(
            customer_id=customer_id,
            panel_type=panel_type,
            panel_inbound_id=inbound_id,
            uuid=client_uuid,
            email_identifier=email_identifier,
            protocol=proto,
            traffic_limit_gb=traffic_limit,
            expiry_date=datetime.utcnow() + timedelta(days=days),
            status=SubscriptionStatus.ACTIVE
        )
        
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        
        logger.info(f"Created subscription for customer {customer.email}")
        return subscription
    
    async def get_subscription_config(
        self,
        subscription_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get connection configuration for a subscription"""
        
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return None
        
        # Get inbound details from panel
        inbounds = []
        if subscription.panel_type == PanelType.XUI and self.xui_client:
            inbounds = await self.xui_client.get_inbounds()
        elif subscription.panel_type == PanelType.THREEXUI and self.threexui_client:
            inbounds = await self.threexui_client.get_inbounds()
        
        # Find the specific inbound
        inbound = next(
            (i for i in inbounds if i.get('id') == subscription.panel_inbound_id),
            None
        )
        
        if not inbound:
            return None
        
        # Extract connection details
        settings_data = json.loads(inbound.get('settings', '{}'))
        stream_settings = json.loads(inbound.get('streamSettings', '{}'))
        
        # Build connection URL (simplified, you may need to customize based on protocol)
        config = {
            "uuid": subscription.uuid,
            "email": subscription.email_identifier,
            "protocol": subscription.protocol,
            "address": inbound.get('address', ''),
            "port": inbound.get('port'),
            "network": stream_settings.get('network', 'tcp'),
            "security": stream_settings.get('security', 'none'),
            "expiry_date": subscription.expiry_date.isoformat(),
            "traffic_limit_gb": subscription.traffic_limit_gb,
            "traffic_used_gb": subscription.traffic_used_gb,
            "status": subscription.status.value
        }
        
        return config
    
    async def generate_qr_code(
        self,
        subscription_id: int,
        connection_url: str
    ) -> Optional[str]:
        """Generate QR code for subscription"""
        
        # Create qrcodes directory if it doesn't exist
        qr_dir = Path("qrcodes")
        qr_dir.mkdir(exist_ok=True)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(connection_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_path = qr_dir / f"subscription_{subscription_id}.png"
        img.save(str(qr_path))
        
        # Update subscription
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            subscription.qr_code_path = str(qr_path)
            await self.db.commit()
        
        return str(qr_path)
    
    async def update_subscription_status(
        self,
        subscription_id: int,
        status: SubscriptionStatus,
        enable: bool
    ) -> bool:
        """Update subscription status"""
        
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return False
        
        # Update in panel
        success = False
        if subscription.panel_type == PanelType.XUI and self.xui_client:
            success = await self.xui_client.update_client(
                inbound_id=subscription.panel_inbound_id,
                uuid=subscription.uuid,
                email=subscription.email_identifier,
                traffic_limit_gb=subscription.traffic_limit_gb,
                enable=enable
            )
        elif subscription.panel_type == PanelType.THREEXUI and self.threexui_client:
            success = await self.threexui_client.update_client(
                inbound_id=subscription.panel_inbound_id,
                uuid=subscription.uuid,
                email=subscription.email_identifier,
                traffic_limit_gb=subscription.traffic_limit_gb,
                enable=enable
            )
        
        if success:
            subscription.status = status
            subscription.is_enabled = enable
            await self.db.commit()
            return True
        
        return False
    
    async def renew_subscription(
        self,
        subscription_id: int,
        additional_days: int,
        additional_traffic_gb: float = 0
    ) -> bool:
        """Renew a subscription"""
        
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return False
        
        # Calculate new expiry
        new_expiry = subscription.expiry_date + timedelta(days=additional_days)
        new_traffic_limit = subscription.traffic_limit_gb + additional_traffic_gb
        
        # Update in panel
        success = False
        expiry_days = (new_expiry - datetime.utcnow()).days
        
        if subscription.panel_type == PanelType.XUI and self.xui_client:
            success = await self.xui_client.update_client(
                inbound_id=subscription.panel_inbound_id,
                uuid=subscription.uuid,
                email=subscription.email_identifier,
                traffic_limit_gb=new_traffic_limit,
                expiry_days=expiry_days,
                enable=True
            )
        elif subscription.panel_type == PanelType.THREEXUI and self.threexui_client:
            success = await self.threexui_client.update_client(
                inbound_id=subscription.panel_inbound_id,
                uuid=subscription.uuid,
                email=subscription.email_identifier,
                traffic_limit_gb=new_traffic_limit,
                expiry_days=expiry_days,
                enable=True
            )
        
        if success:
            subscription.expiry_date = new_expiry
            subscription.traffic_limit_gb = new_traffic_limit
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.is_enabled = True
            await self.db.commit()
            return True
        
        return False
    
    async def delete_subscription(self, subscription_id: int) -> bool:
        """Delete a subscription"""
        
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return False
        
        # Delete from panel
        success = False
        if subscription.panel_type == PanelType.XUI and self.xui_client:
            success = await self.xui_client.delete_client(
                inbound_id=subscription.panel_inbound_id,
                uuid=subscription.uuid
            )
        elif subscription.panel_type == PanelType.THREEXUI and self.threexui_client:
            success = await self.threexui_client.delete_client(
                inbound_id=subscription.panel_inbound_id,
                uuid=subscription.uuid
            )
        
        if success:
            await self.db.delete(subscription)
            await self.db.commit()
            return True
        
        return False
    
    async def sync_traffic_usage(self, subscription_id: int) -> bool:
        """Sync traffic usage from panel"""
        
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return False
        
        # Get traffic from panel
        traffic_data = None
        if subscription.panel_type == PanelType.XUI and self.xui_client:
            traffic_data = await self.xui_client.get_client_traffic(
                subscription.email_identifier
            )
        elif subscription.panel_type == PanelType.THREEXUI and self.threexui_client:
            traffic_data = await self.threexui_client.get_client_traffic(
                subscription.email_identifier
            )
        
        if traffic_data:
            # Convert bytes to GB
            up = traffic_data.get('up', 0)
            down = traffic_data.get('down', 0)
            total_bytes = up + down
            total_gb = total_bytes / (1024 ** 3)
            
            subscription.traffic_used_gb = total_gb
            await self.db.commit()
            return True
        
        return False
    
    async def close(self):
        """Close all clients"""
        if self.xui_client:
            await self.xui_client.close()
        if self.threexui_client:
            await self.threexui_client.close()
