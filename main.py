from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import schemas
import auth
from database import get_db, init_db, Customer, VPNConfig
from service import VPNService
from xui_client import xui_manager
from config import settings

app = FastAPI(
    title="VPN Service Auto Provisioning API",
    description="Automatic VPN configuration system for x-ui and 3x-ui panels",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")
    
    # Check available panels
    panels = xui_manager.get_available_panels()
    print(f"Available panels: {panels}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await xui_manager.close_all()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VPN Service Auto Provisioning API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================
# PUBLIC ENDPOINTS - Registration and Login
# ============================================================

@app.post("/register", response_model=schemas.ServiceRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_service(
    registration: schemas.ServiceRegistration,
    db: Session = Depends(get_db)
):
    """
    Register a new customer and automatically create VPN configuration
    
    This endpoint:
    1. Creates a new customer account
    2. Automatically selects an available x-ui/3x-ui panel
    3. Creates a VPN client configuration
    4. Returns login credentials and connection details
    """
    try:
        customer, vpn_config = await VPNService.create_customer_with_vpn(
            db=db,
            registration=registration
        )
        
        return schemas.ServiceRegistrationResponse(
            customer=schemas.CustomerResponse.from_orm(customer),
            vpn_config=schemas.VPNConfigResponse.from_orm(vpn_config),
            message="Service registered successfully! Please save your connection details."
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register service: {str(e)}"
        )


@app.post("/login", response_model=schemas.Token)
async def login(
    credentials: schemas.CustomerLogin,
    db: Session = Depends(get_db)
):
    """
    Login endpoint for customers
    """
    customer = db.query(Customer).filter(
        Customer.username == credentials.username
    ).first()
    
    if not customer or not auth.verify_password(credentials.password, customer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account"
        )
    
    access_token = auth.create_access_token(data={"sub": customer.username})
    
    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


@app.get("/panels", response_model=List[schemas.PanelInfo])
async def get_available_panels():
    """
    Get information about available x-ui panels
    """
    try:
        panels_info = await VPNService.get_available_panels()
        return panels_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch panel information: {str(e)}"
        )


# ============================================================
# PROTECTED ENDPOINTS - Require Authentication
# ============================================================

@app.get("/me", response_model=schemas.CustomerResponse)
async def get_current_customer_info(
    current_customer: Customer = Depends(auth.get_current_active_customer)
):
    """
    Get current customer information
    """
    return schemas.CustomerResponse.from_orm(current_customer)


@app.get("/my-vpn-configs", response_model=List[schemas.VPNConfigResponse])
async def get_my_vpn_configs(
    current_customer: Customer = Depends(auth.get_current_active_customer),
    db: Session = Depends(get_db)
):
    """
    Get all VPN configurations for the current customer
    """
    configs = db.query(VPNConfig).filter(
        VPNConfig.customer_id == current_customer.id
    ).all()
    
    return [schemas.VPNConfigResponse.from_orm(config) for config in configs]


@app.get("/vpn-config/{config_id}", response_model=schemas.VPNConfigResponse)
async def get_vpn_config(
    config_id: int,
    current_customer: Customer = Depends(auth.get_current_active_customer),
    db: Session = Depends(get_db)
):
    """
    Get specific VPN configuration details
    """
    config = db.query(VPNConfig).filter(
        VPNConfig.id == config_id,
        VPNConfig.customer_id == current_customer.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPN configuration not found"
        )
    
    return schemas.VPNConfigResponse.from_orm(config)


@app.get("/vpn-config/{config_id}/stats")
async def get_vpn_config_stats(
    config_id: int,
    current_customer: Customer = Depends(auth.get_current_active_customer),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for a VPN configuration
    """
    config = db.query(VPNConfig).filter(
        VPNConfig.id == config_id,
        VPNConfig.customer_id == current_customer.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPN configuration not found"
        )
    
    try:
        stats = await VPNService.get_client_stats(config)
        return {
            "config_id": config_id,
            "stats": stats,
            "traffic_limit_gb": config.traffic_limit_gb,
            "traffic_used_gb": config.traffic_used_gb,
            "expires_at": config.expires_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@app.post("/vpn-config/{config_id}/renew")
async def renew_vpn_config(
    config_id: int,
    additional_days: int,
    additional_traffic_gb: int = 0,
    current_customer: Customer = Depends(auth.get_current_active_customer),
    db: Session = Depends(get_db)
):
    """
    Renew VPN service (extend expiry date and/or add more traffic)
    """
    config = db.query(VPNConfig).filter(
        VPNConfig.id == config_id,
        VPNConfig.customer_id == current_customer.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPN configuration not found"
        )
    
    try:
        updated_config = await VPNService.renew_vpn_service(
            db=db,
            vpn_config=config,
            additional_days=additional_days,
            additional_traffic_gb=additional_traffic_gb if additional_traffic_gb > 0 else None
        )
        
        return {
            "message": "Service renewed successfully",
            "config": schemas.VPNConfigResponse.from_orm(updated_config)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to renew service: {str(e)}"
        )


@app.post("/vpn-config/{config_id}/suspend")
async def suspend_vpn_config(
    config_id: int,
    current_customer: Customer = Depends(auth.get_current_active_customer),
    db: Session = Depends(get_db)
):
    """
    Suspend VPN service
    """
    config = db.query(VPNConfig).filter(
        VPNConfig.id == config_id,
        VPNConfig.customer_id == current_customer.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VPN configuration not found"
        )
    
    try:
        updated_config = await VPNService.suspend_vpn_service(
            db=db,
            vpn_config=config
        )
        
        return {
            "message": "Service suspended successfully",
            "config": schemas.VPNConfigResponse.from_orm(updated_config)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suspend service: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
