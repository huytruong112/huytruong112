from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, BigInteger, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ServiceStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING = "pending"


class PanelType(str, enum.Enum):
    XUI_1 = "xui_1"  # dopaemon/x-ui
    XUI_2 = "xui_2"  # mhsanaei/3x-ui


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vpn_configs = relationship("VPNConfig", back_populates="customer")


class VPNConfig(Base):
    """VPN Configuration model"""
    __tablename__ = "vpn_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Panel info
    panel_type = Column(Enum(PanelType), nullable=False)
    panel_inbound_id = Column(Integer)  # Inbound ID in the panel
    panel_client_id = Column(String)  # UUID/Client ID in the panel
    
    # Configuration details
    config_name = Column(String, nullable=False)
    protocol = Column(String, default="vless")  # vless, vmess, trojan, etc.
    
    # Traffic and limits
    traffic_limit_gb = Column(Integer)  # Total traffic limit in GB
    traffic_used_gb = Column(Integer, default=0)  # Used traffic in GB
    
    # Service period
    service_status = Column(Enum(ServiceStatus), default=ServiceStatus.PENDING)
    activated_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Connection details (encrypted or stored securely)
    connection_url = Column(String)  # Full connection URL/link
    subscription_url = Column(String)  # Subscription URL if available
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="vpn_configs")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
