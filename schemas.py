from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from database import ServiceStatus, PanelType


# Customer schemas
class CustomerBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    password: str = Field(..., min_length=6)


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CustomerLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# VPN Config schemas
class VPNConfigBase(BaseModel):
    traffic_limit_gb: Optional[int] = None
    protocol: str = "vless"


class VPNConfigCreate(VPNConfigBase):
    panel_type: PanelType
    inbound_id: Optional[int] = None


class VPNConfigResponse(BaseModel):
    id: int
    config_name: str
    protocol: str
    panel_type: PanelType
    service_status: ServiceStatus
    traffic_limit_gb: Optional[int]
    traffic_used_gb: int
    activated_at: Optional[datetime]
    expires_at: Optional[datetime]
    connection_url: Optional[str]
    subscription_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Service registration
class ServiceRegistration(BaseModel):
    """Schema for customer service registration"""
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Service options
    panel_type: Optional[PanelType] = None  # Auto-select if not provided
    inbound_id: Optional[int] = None  # Auto-select if not provided
    traffic_limit_gb: int = Field(default=50, ge=1, le=1000)
    service_duration_days: int = Field(default=30, ge=1, le=365)


class ServiceRegistrationResponse(BaseModel):
    """Response after successful service registration"""
    customer: CustomerResponse
    vpn_config: VPNConfigResponse
    message: str = "Service registered successfully"


# Panel info
class PanelInfo(BaseModel):
    panel_type: PanelType
    is_enabled: bool
    inbound_count: int
    available: bool


class InboundInfo(BaseModel):
    id: int
    protocol: str
    port: int
    remark: str
    enable: bool
    client_count: int
