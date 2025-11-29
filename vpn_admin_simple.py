#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VPN Admin Simple - Multi-Server Edition v3.0
ONLY WORKING FEATURES: Create + Delete + View + QR
"""

import streamlit as st
import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse

# --- CONFIG FILE ---
CONFIG_FILE = "servers_config.json"

def load_servers():
    """Load servers từ config file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure dict format
            if isinstance(data, dict):
                return data
            return {}
    except FileNotFoundError:
        return {}
    except:
        return {}

def save_servers(servers):
    """Save servers to config file"""
    try:
        # Ensure dict format
        if not isinstance(servers, dict):
            servers = {}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu config: {e}")
        return False

def add_server(name, host, username, password, notes=""):
    """Thêm server mới"""
    servers = load_servers()
    if not isinstance(servers, dict):
        servers = {}
    
    server_id = str(uuid.uuid4())
    servers[server_id] = {
        "name": name,
        "host": host.rstrip('/'),
        "username": username,
        "password": password,
        "notes": notes,
        "created_date": datetime.now().isoformat()
    }
    
    if save_servers(servers):
        if 'current_server_id' in st.session_state:
            del st.session_state['current_server_id']
        st.rerun()
    return server_id

def delete_server(server_id):
    """Xóa server"""
    servers = load_servers()
    if server_id in servers:
        del servers[server_id]
        save_servers(servers)
        if 'current_server_id' in st.session_state:
            del st.session_state['current_server_id']
        st.rerun()

def login(host, username, password):
    """Login to 3X-UI"""
    session = requests.Session()
    try:
        resp = session.post(
            f"{host}/login",
            data={"username": username, "password": password},
            timeout=10
        )
        if resp.status_code == 200:
            return session
        return None
    except:
        return None

def get_inbounds(session, host):
    """Get all inbounds"""
    try:
        resp = session.post(f"{host}/xui/inbound/list", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                inbounds = data.get("obj", [])
                
                # Parse settings/streamSettings/sniffing to dict
                for item in inbounds:
                    for field in ['settings', 'streamSettings', 'sniffing']:
                        if field in item and isinstance(item[field], str):
                            try:
                                item[field] = json.loads(item[field])
                            except:
                                pass
                
                return inbounds
        return []
    except:
        return []

def create_inbound(session, host, remark, days, data_limit_gb, protocol="vless"):
    """TẠO CLIENT MỚI"""
    new_uuid = str(uuid.uuid4())
    expiry_time = int(time.time() * 1000) + (days * 86400 * 1000)
    total_bytes = data_limit_gb * 1024 * 1024 * 1024 if data_limit_gb > 0 else 0
    
    # Find available port
    inbounds = get_inbounds(session, host)
    used_ports = [i['port'] for i in inbounds]
    new_port = 10000
    while new_port in used_ports:
        new_port += 1
    
    # Settings
    settings = {"clients": [{"id": new_uuid, "flow": "xtls-rprx-vision"}], "decryption": "none", "fallbacks": []}
    stream = {
        "network": "tcp", "security": "none",
        "tcpSettings": {"header": {"type": "none"}}
    }
    
    if protocol == "vmess":
        settings = {"clients": [{"id": new_uuid, "alterId": 0}], "disableInsecureEncryption": False}

    payload = {
        "up": 0, "down": 0, "total": total_bytes, "remark": remark,
        "enable": True, "expiryTime": expiry_time, "listen": "",
        "port": new_port, "protocol": protocol,
        "settings": json.dumps(settings),
        "streamSettings": json.dumps(stream),
        "sniffing": json.dumps({"enabled": True, "destOverride": ["http", "tls"]})
    }
    
    try:
        resp = session.post(f"{host}/xui/inbound/add", data=payload, timeout=10)
        if resp.status_code == 200 and "success" in resp.text.lower():
            return {"uuid": new_uuid, "port": new_port, "protocol": protocol}, "OK"
        return None, resp.text
    except Exception as e:
        return None, str(e)

def delete_inbound(session, host, inbound_id):
    """XÓA CLIENT"""
    try:
        resp = session.post(f"{host}/xui/inbound/del/{inbound_id}", timeout=10)
        return resp.status_code == 200
    except:
        return False

def bulk_delete_inbounds(session, host, inbound_ids):
    """XÓA NHIỀU CLIENT"""
    success_count = 0
    failed_count = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, inbound_id in enumerate(inbound_ids):
        try:
            resp = session.post(f"{host}/xui/inbound/del/{inbound_id}", timeout=10)
            if resp.status_code == 200:
                success_count += 1
            else:
                failed_count += 1
        except:
            failed_count += 1
        
        # Update progress
        progress = (idx + 1) / len(inbound_ids)
        progress_bar.progress(progress)
        status_text.text(f"Đã xóa: {idx + 1}/{len(inbound_ids)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return success_count, failed_count

def generate_qr(uuid_val, host, port, protocol, remark):
    """Generate QR code"""
    try:
        # Parse host
        parsed = urlparse(host)
        server_host = parsed.hostname or host.split(':')[0].replace('http://', '').replace('https://', '')
        
        if protocol == "vless":
            link = f"vless://{uuid_val}@{server_host}:{port}?security=none&type=tcp#{remark}"
        else:  # vmess
            vmess_config = {
                "v": "2",
                "ps": remark,
                "add": server_host,
                "port": str(port),
                "id": uuid_val,
                "aid": "0",
                "net": "tcp",
                "type": "none",
                "host": "",
                "path": "",
                "tls": ""
            }
            import base64
            link = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return buf, link
    except Exception as e:
        st.error(f"QR error: {e}")
        return None, None

# --- UI SETUP ---
st.set_page_config(
    page_title="VPN Admin Simple",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .stApp {background: transparent;}
    .block-container {background: white; padding: 2rem; border-radius: 10px; margin: 1rem;}
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .success-box {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    h1 {color: #667eea !important; text-align: center;}
    h2 {color: #764ba2 !important;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🚀 VPN Admin Simple")
    st.markdown("**v3.0** - Only Working Features")
    st.markdown("---")
    
    # Load servers
    servers = load_servers()
    
    if not isinstance(servers, dict):
        servers = {}
        save_servers(servers)
    
    if not servers:
        st.warning("⚠️ Chưa có server. Thêm server ở tab 'Quản Lý Server'!")
        menu = st.radio("📋 Menu", ["🔧 Quản Lý Server"], label_visibility="collapsed")
    else:
        st.success(f"✅ **{len(servers)}** servers")
        
        # Select server
        server_options = {f"{s['name']}": sid for sid, s in servers.items()}
        
        if 'current_server_id' not in st.session_state or st.session_state.current_server_id not in servers:
            st.session_state.current_server_id = list(servers.keys())[0]
        
        selected_server_name = st.selectbox(
            "📡 Chọn Server",
            list(server_options.keys()),
            label_visibility="collapsed"
        )
        st.session_state.current_server_id = server_options[selected_server_name]
        
        current_server = servers[st.session_state.current_server_id]
        st.info(f"🌐 **{current_server['host']}**")
        
        st.markdown("---")
        
        menu = st.radio(
            "📋 Menu",
            ["👥 Quản Lý Client", "🔧 Quản Lý Server"],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px;'>
    <p><b>Tính năng hoạt động:</b></p>
    <p>✅ Tạo Client<br>
    ✅ Xóa Client<br>
    ✅ Xem Client<br>
    ✅ QR Code</p>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("🚀 VPN Admin Simple v3.0")
st.markdown("<p style='text-align: center; color: #888;'>Chỉ những tính năng hoạt động 100%</p>", unsafe_allow_html=True)

if menu == "🔧 Quản Lý Server":
    st.header("🔧 Quản Lý Server")
    
    tab1, tab2 = st.tabs(["➕ Thêm Server", "📋 Danh Sách Server"])
    
    with tab1:
        st.subheader("➕ Thêm Server Mới")
        
        with st.form("add_server_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("📛 Tên Server *", placeholder="VD: Server US")
                host = st.text_input("🌐 Host *", placeholder="http://45.119.84.238:8888")
            
            with col2:
                username = st.text_input("👤 Username *", placeholder="admin")
                password = st.text_input("🔑 Password *", type="password")
            
            notes = st.text_area("📝 Ghi chú", placeholder="Thông tin thêm...")
            
            submit = st.form_submit_button("➕ Thêm Server", use_container_width=True)
            
            if submit:
                if not all([name, host, username, password]):
                    st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc!")
                else:
                    with st.spinner("Đang kiểm tra kết nối..."):
                        session = login(host, username, password)
                        if session:
                            add_server(name, host, username, password, notes)
                            st.success(f"✅ Đã thêm server **{name}** thành công!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Không thể kết nối! Kiểm tra lại thông tin.")
    
    with tab2:
        st.subheader("📋 Danh Sách Server")
        
        servers = load_servers()
        
        if not servers:
            st.info("ℹ️ Chưa có server nào. Thêm server ở tab bên trái!")
        else:
            st.success(f"✅ Đang quản lý **{len(servers)}** server")
            
            for sid, server in servers.items():
                with st.expander(f"🌐 **{server['name']}** - {server['host']}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write("**Thông tin:**")
                        st.code(f"""
Host: {server['host']}
Username: {server['username']}
Created: {server.get('created_date', 'N/A')}
Notes: {server.get('notes', 'Không có')}
                        """)
                    
                    with col2:
                        if st.button("🔍 Test", key=f"test_{sid}", use_container_width=True):
                            with st.spinner("Testing..."):
                                sess = login(server['host'], server['username'], server['password'])
                                if sess:
                                    st.success("✅ OK!")
                                else:
                                    st.error("❌ Fail!")
                    
                    with col3:
                        if st.button("🗑️ Xóa", key=f"del_{sid}", use_container_width=True):
                            delete_server(sid)
                            st.success("✅ Đã xóa!")
                            time.sleep(0.5)
                            st.rerun()

elif menu == "👥 Quản Lý Client":
    if not servers or st.session_state.current_server_id not in servers:
        st.error("❌ Không có server nào được chọn!")
    else:
        current_server = servers[st.session_state.current_server_id]
        
        # Login
        with st.spinner("Đang kết nối..."):
            session = login(current_server['host'], current_server['username'], current_server['password'])
        
        if not session:
            st.error("❌ Không thể kết nối đến server!")
            st.info("💡 Kiểm tra lại thông tin server ở menu 'Quản Lý Server'")
        else:
            st.success(f"✅ Đã kết nối: **{current_server['name']}**")
            
            tab1, tab2 = st.tabs(["➕ Tạo Client Mới", "📋 Danh Sách Client"])
            
            with tab1:
                st.subheader("➕ Tạo Client Mới")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📝 Thông Tin Client")
                    
                    with st.form("create_client_form"):
                        remark = st.text_input("📛 Tên Client *", placeholder="VD: Client-001")
                        days = st.number_input("⏰ Thời hạn (ngày) *", min_value=1, max_value=365, value=30)
                        data_limit = st.number_input("💾 Data Limit (GB) *", min_value=0, max_value=1000, value=50, help="0 = Unlimited")
                        protocol = st.selectbox("🔐 Protocol", ["vless", "vmess"], index=0)
                        
                        submit = st.form_submit_button("➕ Tạo Client", use_container_width=True, type="primary")
                        
                        if submit:
                            if not remark:
                                st.error("❌ Vui lòng nhập tên client!")
                            else:
                                with st.spinner("Đang tạo client..."):
                                    result, msg = create_inbound(
                                        session,
                                        current_server['host'],
                                        remark,
                                        days,
                                        data_limit,
                                        protocol
                                    )
                                    
                                    if result:
                                        st.success("✅ Đã tạo client thành công!")
                                        st.balloons()
                                        
                                        # Show info
                                        st.markdown("### 📄 Thông Tin Client")
                                        st.info(f"""
**Tên:** {remark}  
**UUID:** `{result['uuid']}`  
**Port:** `{result['port']}`  
**Protocol:** `{result['protocol']}`  
**Thời hạn:** {days} ngày  
**Data:** {data_limit} GB
                                        """)
                                        
                                        # QR Code
                                        qr_buf, link = generate_qr(
                                            result['uuid'],
                                            current_server['host'],
                                            result['port'],
                                            result['protocol'],
                                            remark
                                        )
                                        
                                        if qr_buf:
                                            st.image(qr_buf, width=300, caption="QR Code")
                                            st.code(link, language="text")
                                        
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Lỗi: {msg}")
                
                with col2:
                    st.markdown("### 💡 Hướng Dẫn")
                    st.info("""
**Các bước tạo client:**

1. **Nhập tên client** - Tên định danh duy nhất
2. **Chọn thời hạn** - Số ngày sử dụng
3. **Chọn data limit** - 0 = Unlimited
4. **Chọn protocol** - vless (khuyến nghị) hoặc vmess
5. **Click "Tạo Client"** ✅

**Sau khi tạo:**
- Nhận UUID và Port
- Nhận QR Code để scan
- Nhận link config để copy

**Lưu ý:**
- Mỗi client có port riêng
- UUID tự động random
- Không thể edit sau khi tạo
- Muốn đổi info → Xóa & tạo lại
                    """)
            
            with tab2:
                st.subheader("📋 Danh Sách Client")
                
                # Get clients
                with st.spinner("Đang tải danh sách..."):
                    inbounds = get_inbounds(session, current_server['host'])
                
                if not inbounds:
                    st.info("ℹ️ Chưa có client nào. Tạo client ở tab 'Tạo Client Mới'!")
                else:
                    st.success(f"✅ Có **{len(inbounds)}** clients")
                    
                    # Bulk delete
                    st.markdown("### 🗑️ Xóa Hàng Loạt")
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        if 'selected_for_delete' not in st.session_state:
                            st.session_state.selected_for_delete = []
                        
                        select_all = st.checkbox("☑️ Chọn tất cả")
                        if select_all:
                            st.session_state.selected_for_delete = [i['id'] for i in inbounds]
                    
                    with col2:
                        if st.button("❌ Bỏ chọn"):
                            st.session_state.selected_for_delete = []
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Xóa ({len(st.session_state.selected_for_delete)})", type="primary"):
                            if st.session_state.selected_for_delete:
                                if 'confirm_bulk_delete' not in st.session_state:
                                    st.session_state.confirm_bulk_delete = True
                                    st.warning(f"⚠️ Xác nhận xóa {len(st.session_state.selected_for_delete)} clients?")
                                    if st.button("✅ XÁC NHẬN XÓA"):
                                        with st.spinner("Đang xóa..."):
                                            success, failed = bulk_delete_inbounds(
                                                session,
                                                current_server['host'],
                                                st.session_state.selected_for_delete
                                            )
                                            st.success(f"✅ Đã xóa {success} clients!")
                                            if failed > 0:
                                                st.warning(f"⚠️ {failed} clients không xóa được")
                                            st.session_state.selected_for_delete = []
                                            del st.session_state.confirm_bulk_delete
                                            time.sleep(1)
                                            st.rerun()
                    
                    st.markdown("---")
                    st.markdown("### 📊 Chi Tiết Clients")
                    
                    # Display clients
                    for idx, item in enumerate(inbounds):
                        # Calculate expiry
                        expiry_ms = item.get('expiryTime', 0)
                        if expiry_ms > 0:
                            expiry_date = datetime.fromtimestamp(expiry_ms / 1000)
                            days_left = (expiry_date - datetime.now()).days
                            expiry_str = f"{expiry_date.strftime('%Y-%m-%d')} ({days_left} ngày)"
                            expiry_color = "🟢" if days_left > 7 else "🟡" if days_left > 0 else "🔴"
                        else:
                            expiry_str = "Không giới hạn"
                            expiry_color = "🟢"
                        
                        # Calculate traffic
                        up_gb = item.get('up', 0) / (1024**3)
                        down_gb = item.get('down', 0) / (1024**3)
                        total_gb = item.get('total', 0) / (1024**3)
                        used_gb = up_gb + down_gb
                        
                        if total_gb > 0:
                            percent_used = (used_gb / total_gb) * 100
                            traffic_str = f"{used_gb:.2f}/{total_gb:.2f} GB ({percent_used:.1f}%)"
                            traffic_color = "🟢" if percent_used < 70 else "🟡" if percent_used < 90 else "🔴"
                        else:
                            traffic_str = f"{used_gb:.2f} GB / Unlimited"
                            traffic_color = "🟢"
                        
                        # Status
                        status = "🟢 Active" if item.get('enable') else "🔴 Disabled"
                        
                        with st.expander(f"{idx+1}. **{item['remark']}** - {status}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"""
**📛 Tên:** {item['remark']}  
**🔐 Protocol:** {item['protocol']}  
**🔑 UUID/ID:** `{item['settings'].get('clients', [{}])[0].get('id', 'N/A') if isinstance(item.get('settings'), dict) else 'N/A'}`  
**🌐 Port:** `{item['port']}`  
**⏰ Hết hạn:** {expiry_color} {expiry_str}  
**💾 Traffic:** {traffic_color} {traffic_str}  
**📊 Status:** {status}
                                """)
                                
                                # QR Code
                                if st.button(f"📱 Xem QR Code", key=f"qr_{item['id']}"):
                                    uuid_val = item['settings'].get('clients', [{}])[0].get('id', '') if isinstance(item.get('settings'), dict) else ''
                                    if uuid_val:
                                        qr_buf, link = generate_qr(
                                            uuid_val,
                                            current_server['host'],
                                            item['port'],
                                            item['protocol'],
                                            item['remark']
                                        )
                                        if qr_buf:
                                            st.image(qr_buf, width=250)
                                            st.code(link, language="text")
                            
                            with col2:
                                # Checkbox for bulk delete
                                is_selected = item['id'] in st.session_state.selected_for_delete
                                if st.checkbox("☑️ Chọn", value=is_selected, key=f"select_{item['id']}"):
                                    if item['id'] not in st.session_state.selected_for_delete:
                                        st.session_state.selected_for_delete.append(item['id'])
                                else:
                                    if item['id'] in st.session_state.selected_for_delete:
                                        st.session_state.selected_for_delete.remove(item['id'])
                                
                                st.markdown("---")
                                
                                # Delete button
                                if st.button("🗑️ Xóa", key=f"delete_{item['id']}", use_container_width=True, type="primary"):
                                    with st.spinner("Đang xóa..."):
                                        if delete_inbound(session, current_server['host'], item['id']):
                                            st.success("✅ Đã xóa!")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error("❌ Lỗi xóa!")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
<p>© 2024 VPN Admin Simple v3.0</p>
<p><b>CHỈ NHỮNG TÍNH NĂNG HOẠT ĐỘNG 100%</b></p>
<p>✅ Tạo | ✅ Xóa | ✅ Xem | ✅ QR Code</p>
</div>
""", unsafe_allow_html=True)
