#!/usr/bin/env python3
"""
Test connection to x-ui and 3x-ui panels
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clients.xui_client import XUIClient
from clients.threexui_client import ThreeXUIClient
from config import settings


async def test_xui():
    """Test x-ui connection"""
    if not settings.xui_panel_url:
        print("❌ X-UI not configured")
        return False
    
    print(f"\n🔍 Testing X-UI connection...")
    print(f"   URL: {settings.xui_panel_url}")
    print(f"   Username: {settings.xui_username}")
    
    client = XUIClient(
        settings.xui_panel_url,
        settings.xui_username,
        settings.xui_password
    )
    
    try:
        # Test login
        print("   Logging in...")
        if await client.login():
            print("   ✅ Login successful")
            
            # Test get inbounds
            print("   Getting inbounds...")
            inbounds = await client.get_inbounds()
            
            if inbounds:
                print(f"   ✅ Found {len(inbounds)} inbound(s)")
                for inbound in inbounds:
                    print(f"      - ID: {inbound.get('id')}, Port: {inbound.get('port')}, Protocol: {inbound.get('protocol')}")
                return True
            else:
                print("   ⚠️  No inbounds found")
                return True
        else:
            print("   ❌ Login failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        await client.close()


async def test_threexui():
    """Test 3x-ui connection"""
    if not settings.threexui_panel_url:
        print("❌ 3X-UI not configured")
        return False
    
    print(f"\n🔍 Testing 3X-UI connection...")
    print(f"   URL: {settings.threexui_panel_url}")
    print(f"   Username: {settings.threexui_username}")
    
    client = ThreeXUIClient(
        settings.threexui_panel_url,
        settings.threexui_username,
        settings.threexui_password
    )
    
    try:
        # Test login
        print("   Logging in...")
        if await client.login():
            print("   ✅ Login successful")
            
            # Test get inbounds
            print("   Getting inbounds...")
            inbounds = await client.get_inbounds()
            
            if inbounds:
                print(f"   ✅ Found {len(inbounds)} inbound(s)")
                for inbound in inbounds:
                    print(f"      - ID: {inbound.get('id')}, Port: {inbound.get('port')}, Protocol: {inbound.get('protocol')}")
                return True
            else:
                print("   ⚠️  No inbounds found")
                return True
        else:
            print("   ❌ Login failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    finally:
        await client.close()


async def main():
    """Main function"""
    print("=" * 50)
    print("VPN Panel Connection Test")
    print("=" * 50)
    
    xui_ok = await test_xui()
    threexui_ok = await test_threexui()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    if settings.xui_panel_url:
        print(f"X-UI: {'✅ OK' if xui_ok else '❌ FAILED'}")
    else:
        print("X-UI: ⚠️  Not configured")
    
    if settings.threexui_panel_url:
        print(f"3X-UI: {'✅ OK' if threexui_ok else '❌ FAILED'}")
    else:
        print("3X-UI: ⚠️  Not configured")
    
    print("=" * 50)
    
    if not settings.xui_panel_url and not settings.threexui_panel_url:
        print("\n⚠️  No panels configured!")
        print("Please configure at least one panel in .env file")
        return False
    
    return (xui_ok or not settings.xui_panel_url) and (threexui_ok or not settings.threexui_panel_url)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
