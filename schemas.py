from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class PanelTypeSchema(str, Enum):
    XUI = "xui"
    THREEXUI = "3x-ui"


class SubscriptionStatusSchema(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class CustomerCreate(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    customer_email: EmailStr
    customer_name: str
    customer_phone: Optional[str] = None
    panel_type: PanelTypeSchema
    inbound_id: int
    traffic_limit_gb: Optional[float] = None
    expiry_days: Optional[int] = None
    protocol: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    panel_type: str
    uuid: str
    email_identifier: str
    protocol: str
    traffic_limit_gb: float
    traffic_used_gb: float
    expiry_date: datetime
    status: str
    is_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionRenew(BaseModel):
    additional_days: int
    additional_traffic_gb: float = 0


class SubscriptionUpdate(BaseModel):
    status: SubscriptionStatusSchema
    enable: bool


class ConfigResponse(BaseModel):
    uuid: str
    email: str
    protocol: str
    address: str
    port: int
    network: str
    security: str
    expiry_date: str
    traffic_limit_gb: float
    traffic_used_gb: float
    status: str
