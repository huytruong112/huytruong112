from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./vpn_service.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # X-UI Panel 1 (dopaemon/x-ui)
    XUI_1_URL: Optional[str] = None  # e.g., "http://your-server-ip:54321"
    XUI_1_USERNAME: Optional[str] = None
    XUI_1_PASSWORD: Optional[str] = None
    XUI_1_ENABLED: bool = False
    
    # 3X-UI Panel (mhsanaei/3x-ui)
    XUI_2_URL: Optional[str] = None  # e.g., "http://your-server-ip:2053"
    XUI_2_USERNAME: Optional[str] = None
    XUI_2_PASSWORD: Optional[str] = None
    XUI_2_ENABLED: bool = False
    
    # Service Settings
    DEFAULT_TRAFFIC_LIMIT_GB: int = 50  # Default traffic limit per customer (GB)
    DEFAULT_EXPIRY_DAYS: int = 30  # Default service expiry (days)
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
