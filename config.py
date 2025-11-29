from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-this-secret-key"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./vpn_service.db"
    
    # X-UI Panel
    xui_panel_url: Optional[str] = None
    xui_username: Optional[str] = None
    xui_password: Optional[str] = None
    
    # 3X-UI Panel
    threexui_panel_url: Optional[str] = None
    threexui_username: Optional[str] = None
    threexui_password: Optional[str] = None
    
    # Service Configuration
    default_traffic_limit_gb: int = 50
    default_expiry_days: int = 30
    default_protocol: str = "vless"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
