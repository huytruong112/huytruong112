from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class PanelType(enum.Enum):
    XUI = "xui"
    THREEXUI = "3x-ui"


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    panel_type = Column(Enum(PanelType), nullable=False)
    panel_inbound_id = Column(Integer, nullable=True)
    
    # Configuration details
    uuid = Column(String, unique=True, nullable=False, index=True)
    email_identifier = Column(String, nullable=False)
    protocol = Column(String, default="vless")
    
    # Limits
    traffic_limit_gb = Column(Float, nullable=False)
    traffic_used_gb = Column(Float, default=0.0)
    expiry_date = Column(DateTime, nullable=False)
    
    # Status
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    is_enabled = Column(Boolean, default=True)
    
    # Connection details
    connection_config = Column(String, nullable=True)  # JSON string with full config
    qr_code_path = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PanelConfig(Base):
    """Panel configuration model"""
    __tablename__ = "panel_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    panel_type = Column(Enum(PanelType), unique=True, nullable=False)
    panel_url = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    session_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
