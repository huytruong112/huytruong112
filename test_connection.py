"""
Script để test kết nối với x-ui và 3x-ui panels
Chạy script này để kiểm tra cấu hình có đúng không
"""

import json
import sys
from xui_client import XUIClient, ThreeXUIClient


def load_config():
    """Load cấu hình từ config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Không tìm thấy config.json")
        print("   Vui lòng tạo từ config.example.json")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi parse JSON: {e}")
        sys.exit(1)


def test_xui_panels(config):
    """Test kết nối với x-ui panels"""
    xui_panels = config.get('xui_panels', {})
    
    if not xui_panels:
        print("⚠️  Không có x-ui panel nào được cấu hình")
        return True
    
    print("\n🔍 Testing x-ui panels...")
    print("=" * 50)
    
    all_success = True
    
    for panel_name, panel_config in xui_panels.items():
        print(f"\n📡 Testing panel: {panel_name}")
        print(f"   URL: {panel_config['url']}")
        
        try:
            client = XUIClient(
                base_url=panel_config['url'],
                username=panel_config['username'],
                password=panel_config['password']
            )
            
            # Test login
            if client.login():
                print("   ✅ Đăng nhập thành công")
                
                # Test get inbounds
                inbounds = client.get_inbounds()
                if inbounds is not None:
                    print(f"   ✅ Lấy inbounds thành công ({len(inbounds)} inbounds)")
                    
                    # Kiểm tra default_inbound_id
                    default_id = panel_config.get('default_inbound_id')
                    if default_id:
                        found = any(inbound.get('id') == default_id for inbound in inbounds)
                        if found:
                            print(f"   ✅ Default inbound ID {default_id} tồn tại")
                        else:
                            print(f"   ⚠️  Default inbound ID {default_id} không tồn tại")
                            print(f"       Available IDs: {[inbound.get('id') for inbound in inbounds]}")
                            all_success = False
                else:
                    print("   ❌ Không thể lấy danh sách inbounds")
                    all_success = False
            else:
                print("   ❌ Đăng nhập thất bại")
                print("       Kiểm tra lại username/password")
                all_success = False
                
        except Exception as e:
            print(f"   ❌ Lỗi: {str(e)}")
            all_success = False
    
    return all_success


def test_3xui_panels(config):
    """Test kết nối với 3x-ui panels"""
    threexui_panels = config.get('threexui_panels', {})
    
    if not threexui_panels:
        print("⚠️  Không có 3x-ui panel nào được cấu hình")
        return True
    
    print("\n🔍 Testing 3x-ui panels...")
    print("=" * 50)
    
    all_success = True
    
    for panel_name, panel_config in threexui_panels.items():
        print(f"\n📡 Testing panel: {panel_name}")
        print(f"   URL: {panel_config['url']}")
        
        try:
            client = ThreeXUIClient(
                base_url=panel_config['url'],
                username=panel_config['username'],
                password=panel_config['password']
            )
            
            # Test login
            if client.login():
                print("   ✅ Đăng nhập thành công")
                
                # Test get inbounds
                inbounds = client.get_inbounds()
                if inbounds is not None:
                    print(f"   ✅ Lấy inbounds thành công ({len(inbounds)} inbounds)")
                    
                    # Kiểm tra default_inbound_id
                    default_id = panel_config.get('default_inbound_id')
                    if default_id:
                        found = any(inbound.get('id') == default_id for inbound in inbounds)
                        if found:
                            print(f"   ✅ Default inbound ID {default_id} tồn tại")
                            
                            # Hiển thị thông tin inbound
                            for inbound in inbounds:
                                if inbound.get('id') == default_id:
                                    print(f"       Protocol: {inbound.get('protocol')}")
                                    print(f"       Port: {inbound.get('port')}")
                                    print(f"       Remark: {inbound.get('remark')}")
                        else:
                            print(f"   ⚠️  Default inbound ID {default_id} không tồn tại")
                            print(f"       Available IDs: {[inbound.get('id') for inbound in inbounds]}")
                            all_success = False
                else:
                    print("   ❌ Không thể lấy danh sách inbounds")
                    all_success = False
            else:
                print("   ❌ Đăng nhập thất bại")
                print("       Kiểm tra lại username/password")
                all_success = False
                
        except Exception as e:
            print(f"   ❌ Lỗi: {str(e)}")
            all_success = False
    
    return all_success


def validate_plans(config):
    """Kiểm tra cấu hình plans"""
    plans = config.get('plans', {})
    
    if not plans:
        print("\n⚠️  Không có plan nào được cấu hình")
        return False
    
    print("\n🔍 Validating plans...")
    print("=" * 50)
    
    all_valid = True
    
    for plan_name, plan_config in plans.items():
        print(f"\n📋 Plan: {plan_name}")
        
        # Check required fields
        required_fields = ['panel_type', 'data_limit_gb', 'duration_days']
        for field in required_fields:
            if field in plan_config:
                print(f"   ✅ {field}: {plan_config[field]}")
            else:
                print(f"   ❌ Thiếu field: {field}")
                all_valid = False
        
        # Validate panel_type
        panel_type = plan_config.get('panel_type')
        if panel_type not in ['x-ui', '3x-ui']:
            print(f"   ⚠️  Panel type không hợp lệ: {panel_type}")
            print(f"       Chỉ chấp nhận: x-ui hoặc 3x-ui")
            all_valid = False
        elif panel_type == 'x-ui' and not config.get('xui_panels'):
            print(f"   ⚠️  Plan sử dụng x-ui nhưng không có panel nào được cấu hình")
            all_valid = False
        elif panel_type == '3x-ui' and not config.get('threexui_panels'):
            print(f"   ⚠️  Plan sử dụng 3x-ui nhưng không có panel nào được cấu hình")
            all_valid = False
    
    return all_valid


def main():
    """Main function"""
    print("=" * 50)
    print("🧪 VPN API Connection Test")
    print("=" * 50)
    
    # Load config
    config = load_config()
    print("✅ Config loaded successfully")
    
    # Test connections
    xui_success = test_xui_panels(config)
    threexui_success = test_3xui_panels(config)
    plans_valid = validate_plans(config)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    if xui_success and threexui_success and plans_valid:
        print("✅ Tất cả tests đều PASS")
        print("✅ Hệ thống sẵn sàng sử dụng!")
        print("\n💡 Bạn có thể chạy API server bằng lệnh:")
        print("   python api_server.py")
        sys.exit(0)
    else:
        print("❌ Có lỗi trong quá trình test")
        print("   Vui lòng kiểm tra lại cấu hình")
        sys.exit(1)


if __name__ == '__main__':
    main()
