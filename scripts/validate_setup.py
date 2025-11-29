#!/usr/bin/env python3
"""
Validate complete setup and configuration
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from clients.xui_client import XUIClient
from clients.threexui_client import ThreeXUIClient


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: OK")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists"""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        print(f"✅ {description}: OK")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False


def check_env_var(var_name, var_value, required=True):
    """Check if environment variable is set"""
    if var_value:
        print(f"✅ {var_name}: Configured")
        return True
    else:
        if required:
            print(f"❌ {var_name}: Not configured (required)")
        else:
            print(f"⚠️  {var_name}: Not configured (optional)")
        return not required


async def test_panel_connection(panel_name, client):
    """Test connection to a panel"""
    try:
        print(f"\n  Testing {panel_name} connection...")
        
        # Test login
        if await client.login():
            print(f"    ✅ Login successful")
            
            # Test get inbounds
            inbounds = await client.get_inbounds()
            if inbounds:
                print(f"    ✅ Can retrieve inbounds ({len(inbounds)} found)")
                print(f"    📋 Available inbound IDs: {[i.get('id') for i in inbounds]}")
                return True
            else:
                print(f"    ⚠️  No inbounds found (create one in panel)")
                return True
        else:
            print(f"    ❌ Login failed - check credentials")
            return False
    except Exception as e:
        print(f"    ❌ Connection error: {e}")
        return False
    finally:
        await client.close()


async def main():
    """Main validation"""
    
    print("\n" + "🔍" * 30)
    print("VPN Subscription Management - Setup Validation")
    print("🔍" * 30)
    
    all_ok = True
    
    # 1. Check project structure
    print_section("1. Project Structure")
    
    structure_checks = [
        ("main.py", "Main application file"),
        ("config.py", "Configuration file"),
        ("models.py", "Database models"),
        ("database.py", "Database configuration"),
        ("schemas.py", "API schemas"),
        ("requirements.txt", "Dependencies file"),
        (".env", "Environment file"),
    ]
    
    for filepath, description in structure_checks:
        if not check_file(filepath, description):
            all_ok = False
    
    # Check directories
    dir_checks = [
        ("clients", "API clients directory"),
        ("services", "Services directory"),
        ("examples", "Examples directory"),
        ("scripts", "Scripts directory"),
    ]
    
    for dirpath, description in dir_checks:
        if not check_directory(dirpath, description):
            all_ok = False
    
    # 2. Check dependencies
    print_section("2. Python Dependencies")
    
    try:
        import fastapi
        import uvicorn
        import httpx
        import sqlalchemy
        import qrcode
        import cryptography
        print("✅ All required packages installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Run: pip install -r requirements.txt")
        all_ok = False
    
    # 3. Check configuration
    print_section("3. Configuration")
    
    # Basic config
    check_env_var("API_HOST", settings.api_host)
    check_env_var("API_PORT", settings.api_port)
    check_env_var("API_SECRET_KEY", settings.api_secret_key)
    check_env_var("DATABASE_URL", settings.database_url)
    
    # Panel configuration
    print("\n  Panel Configuration:")
    
    xui_configured = all([
        check_env_var("XUI_PANEL_URL", settings.xui_panel_url, required=False),
        check_env_var("XUI_USERNAME", settings.xui_username, required=False) if settings.xui_panel_url else True,
        check_env_var("XUI_PASSWORD", settings.xui_password, required=False) if settings.xui_panel_url else True,
    ])
    
    threexui_configured = all([
        check_env_var("THREEXUI_PANEL_URL", settings.threexui_panel_url, required=False),
        check_env_var("THREEXUI_USERNAME", settings.threexui_username, required=False) if settings.threexui_panel_url else True,
        check_env_var("THREEXUI_PASSWORD", settings.threexui_password, required=False) if settings.threexui_panel_url else True,
    ])
    
    if not xui_configured and not threexui_configured:
        print("\n❌ No panels configured!")
        print("   Configure at least one panel (X-UI or 3X-UI) in .env file")
        all_ok = False
    
    # 4. Test panel connections
    print_section("4. Panel Connections")
    
    if settings.xui_panel_url and settings.xui_username and settings.xui_password:
        print(f"\n  X-UI Panel: {settings.xui_panel_url}")
        client = XUIClient(
            settings.xui_panel_url,
            settings.xui_username,
            settings.xui_password
        )
        if not await test_panel_connection("X-UI", client):
            all_ok = False
    else:
        print("\n  X-UI Panel: Not configured (skipping)")
    
    if settings.threexui_panel_url and settings.threexui_username and settings.threexui_password:
        print(f"\n  3X-UI Panel: {settings.threexui_panel_url}")
        client = ThreeXUIClient(
            settings.threexui_panel_url,
            settings.threexui_username,
            settings.threexui_password
        )
        if not await test_panel_connection("3X-UI", client):
            all_ok = False
    else:
        print("\n  3X-UI Panel: Not configured (skipping)")
    
    # 5. Check database
    print_section("5. Database")
    
    try:
        from database import init_db
        print("✅ Database module loaded")
        print(f"   Database URL: {settings.database_url}")
        
        # Try to initialize database
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database error: {e}")
        all_ok = False
    
    # 6. Summary
    print_section("Validation Summary")
    
    if all_ok:
        print("\n✅ ✅ ✅  All checks passed!  ✅ ✅ ✅")
        print("\nYou're ready to start the API:")
        print("  python main.py")
        print("\nOr with Docker:")
        print("  docker-compose up -d")
        print("\nAPI will be available at:")
        print(f"  http://localhost:{settings.api_port}")
        print(f"  http://localhost:{settings.api_port}/docs (API documentation)")
        return True
    else:
        print("\n❌ ❌ ❌  Some checks failed  ❌ ❌ ❌")
        print("\nPlease fix the issues above before starting the API.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env file: cp .env.example .env && nano .env")
        print("  3. Check panel URLs and credentials")
        print("  4. Ensure panels are running and accessible")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
