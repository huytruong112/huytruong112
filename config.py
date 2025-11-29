import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///xui_manager.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Panel Configuration
    PANEL_TYPE = os.getenv('PANEL_TYPE', '3xui')  # 'xui' or '3xui'
    
    # X-UI Configuration
    XUI_PANEL_URL = os.getenv('XUI_PANEL_URL', '')
    XUI_USERNAME = os.getenv('XUI_USERNAME', 'admin')
    XUI_PASSWORD = os.getenv('XUI_PASSWORD', 'admin')
    
    # 3X-UI Configuration
    THREE_XUI_PANEL_URL = os.getenv('THREE_XUI_PANEL_URL', '')
    THREE_XUI_USERNAME = os.getenv('THREE_XUI_USERNAME', 'admin')
    THREE_XUI_PASSWORD = os.getenv('THREE_XUI_PASSWORD', 'admin')
    
    # Service Defaults
    DEFAULT_TRAFFIC_GB = int(os.getenv('DEFAULT_TRAFFIC_GB', '100'))
    DEFAULT_EXPIRY_DAYS = int(os.getenv('DEFAULT_EXPIRY_DAYS', '30'))
    DEFAULT_PORT = int(os.getenv('DEFAULT_PORT', '443'))
    DEFAULT_PROTOCOL = os.getenv('DEFAULT_PROTOCOL', 'vless')
