from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import logging

from database import init_db, get_db
from services.vpn_service import VPNService
from schemas import (
    CustomerCreate,
    CustomerResponse,
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionRenew,
    SubscriptionUpdate,
    ConfigResponse
)
from models import PanelType, SubscriptionStatus
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Application started")
    yield
    # Shutdown
    logger.info("Application shutting down")


app = FastAPI(
    title="VPN Subscription Management API",
    description="API for managing VPN subscriptions with x-ui and 3x-ui panels",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VPN Subscription Management API",
        "version": "1.0.0",
        "panels": {
            "x-ui": settings.xui_panel_url is not None,
            "3x-ui": settings.threexui_panel_url is not None
        }
    }


@app.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer"""
    vpn_service = VPNService(db)
    
    try:
        customer = await vpn_service.create_customer(
            email=customer_data.email,
            name=customer_data.name,
            phone=customer_data.phone
        )
        return customer
    finally:
        await vpn_service.close()


@app.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new subscription for a customer.
    This endpoint will:
    1. Create a customer if they don't exist
    2. Create a client in the specified panel (x-ui or 3x-ui)
    3. Create a subscription record in the database
    """
    vpn_service = VPNService(db)
    
    try:
        # Create or get customer
        customer = await vpn_service.create_customer(
            email=subscription_data.customer_email,
            name=subscription_data.customer_name,
            phone=subscription_data.customer_phone
        )
        
        # Convert schema enum to model enum
        panel_type = PanelType.XUI if subscription_data.panel_type == "xui" else PanelType.THREEXUI
        
        # Create subscription
        subscription = await vpn_service.create_subscription(
            customer_id=customer.id,
            panel_type=panel_type,
            inbound_id=subscription_data.inbound_id,
            traffic_limit_gb=subscription_data.traffic_limit_gb,
            expiry_days=subscription_data.expiry_days,
            protocol=subscription_data.protocol
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create subscription in panel"
            )
        
        return subscription
    finally:
        await vpn_service.close()


@app.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get subscription details"""
    from sqlalchemy import select
    from models import Subscription
    
    result = await db.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return subscription


@app.get("/subscriptions/{subscription_id}/config", response_model=ConfigResponse)
async def get_subscription_config(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get connection configuration for a subscription"""
    vpn_service = VPNService(db)
    
    try:
        config = await vpn_service.get_subscription_config(subscription_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription or configuration not found"
            )
        
        return config
    finally:
        await vpn_service.close()


@app.get("/subscriptions/{subscription_id}/qrcode")
async def get_subscription_qrcode(
    subscription_id: int,
    connection_url: str,
    db: AsyncSession = Depends(get_db)
):
    """Generate and get QR code for a subscription"""
    vpn_service = VPNService(db)
    
    try:
        qr_path = await vpn_service.generate_qr_code(subscription_id, connection_url)
        
        if not qr_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate QR code"
            )
        
        return FileResponse(qr_path, media_type="image/png")
    finally:
        await vpn_service.close()


@app.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    update_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update subscription status"""
    vpn_service = VPNService(db)
    
    try:
        # Convert schema enum to model enum
        status_value = SubscriptionStatus[update_data.status.value.upper()]
        
        success = await vpn_service.update_subscription_status(
            subscription_id=subscription_id,
            status=status_value,
            enable=update_data.enable
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update subscription"
            )
        
        # Get updated subscription
        from sqlalchemy import select
        from models import Subscription
        
        result = await db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        return subscription
    finally:
        await vpn_service.close()


@app.post("/subscriptions/{subscription_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(
    subscription_id: int,
    renew_data: SubscriptionRenew,
    db: AsyncSession = Depends(get_db)
):
    """Renew a subscription"""
    vpn_service = VPNService(db)
    
    try:
        success = await vpn_service.renew_subscription(
            subscription_id=subscription_id,
            additional_days=renew_data.additional_days,
            additional_traffic_gb=renew_data.additional_traffic_gb
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to renew subscription"
            )
        
        # Get updated subscription
        from sqlalchemy import select
        from models import Subscription
        
        result = await db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        return subscription
    finally:
        await vpn_service.close()


@app.delete("/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a subscription"""
    vpn_service = VPNService(db)
    
    try:
        success = await vpn_service.delete_subscription(subscription_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found or failed to delete"
            )
    finally:
        await vpn_service.close()


@app.post("/subscriptions/{subscription_id}/sync-traffic")
async def sync_traffic(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Sync traffic usage from panel"""
    vpn_service = VPNService(db)
    
    try:
        success = await vpn_service.sync_traffic_usage(subscription_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to sync traffic usage"
            )
        
        return {"message": "Traffic synced successfully"}
    finally:
        await vpn_service.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "panels": {
            "x-ui_configured": settings.xui_panel_url is not None,
            "3x-ui_configured": settings.threexui_panel_url is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
