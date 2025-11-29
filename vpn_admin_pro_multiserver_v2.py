import streamlit as st
import requests
import json
import time
import uuid
import random
import pandas as pd
import qrcode
from io import BytesIO
import psutil
from PIL import Image
import base64
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse, urljoin

# --- CẤU HÌNH MULTI-SERVER ---
SERVERS_CONFIG_FILE = "servers_config.json"

# --- HÀM PARSE URL ---
def parse_host_url(host_url):
    """
    Parse URL để hỗ trợ nhiều định dạng:
    - http://IP:PORT
    - http://IP:PORT/SECRET_PATH
    - https://domain.com:PORT/PATH
    
    Returns: (base_url, path) tuple
    """
    try:
        # Ensure URL has scheme
        if not host_url.startswith(('http://', 'https://')):
            host_url = 'http://' + host_url
        
        parsed = urlparse(host_url)
        
        # Base URL (scheme + netloc)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Path (nếu có)
        path = parsed.path.rstrip('/')
        
        return base_url, path
    except Exception as e:
        st.error(f"Lỗi parse URL: {str(e)}")
        return host_url, ""

def build_api_url(base_url, path, endpoint):
    """
    Xây dựng URL API đầy đủ
    Examples:
      - build_api_url("http://1.2.3.4:8001", "", "/login")
        → "http://1.2.3.4:8001/login"
      
      - build_api_url("http://1.2.3.4:8888", "/6SnQh95LlD8LhQxQ2o", "/login")
        → "http://1.2.3.4:8888/6SnQh95LlD8LhQxQ2o/login"
    """
    try:
        # Remove leading slash from endpoint
        endpoint = endpoint.lstrip('/')
        
        if path:
            # Có path: base + path + endpoint
            full_url = f"{base_url}{path}/{endpoint}"
        else:
            # Không path: base + endpoint
            full_url = f"{base_url}/{endpoint}"
        
        return full_url
    except Exception as e:
        st.error(f"Lỗi build URL: {str(e)}")
        return f"{base_url}/{endpoint}"

# --- HÀM QUẢN LÝ SERVER CONFIG ---
def load_servers():
    """Load danh sách server từ file JSON"""
    if os.path.exists(SERVERS_CONFIG_FILE):
        try:
            with open(SERVERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}
        except Exception as e:
            st.error(f"Lỗi đọc file config: {str(e)}")
            return {}
    return {}

def save_servers(servers):
    """Lưu danh sách server vào file JSON"""
    try:
        if not isinstance(servers, dict):
            servers = {}
        
        with open(SERVERS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu file config: {str(e)}")
        return False

def add_server(name, host_url, username, password, notes=""):
    """Thêm server mới - hỗ trợ URL có path"""
    try:
        servers = load_servers()
        if not isinstance(servers, dict):
            servers = {}
        
        # Parse URL để tách base và path
        base_url, path = parse_host_url(host_url)
        
        server_id = str(uuid.uuid4())[:8]
        servers[server_id] = {
            "name": name,
            "host": host_url,  # Lưu full URL gốc
            "base_url": base_url,  # Base URL (IP:Port)
            "path": path,  # Secret path (nếu có)
            "username": username,
            "password": password,
            "notes": notes,
            "added_date": datetime.now().isoformat()
        }
        save_servers(servers)
        return server_id
    except Exception as e:
        st.error(f"Lỗi thêm server: {str(e)}")
        return None

def delete_server(server_id):
    """Xóa server"""
    try:
        servers = load_servers()
        if not isinstance(servers, dict):
            return False
        
        if server_id in servers:
            del servers[server_id]
            save_servers(servers)
            return True
        return False
    except Exception as e:
        st.error(f"Lỗi xóa server: {str(e)}")
        return False

def get_server_config(server_id):
    """Lấy config của 1 server"""
    try:
        servers = load_servers()
        if not isinstance(servers, dict):
            return None
        return servers.get(server_id, None)
    except:
        return None

# --- HÀM HỖ TRỢ HỆ THỐNG ---
def get_system_stats():
    """Lấy thông tin CPU, RAM, Disk của VPS hiện tại"""
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        return {
            'cpu': cpu_usage,
            'ram_percent': ram_info.percent,
            'ram_used': ram_info.used / (1024**3),
            'ram_total': ram_info.total / (1024**3),
            'disk_percent': disk_info.percent,
            'disk_used': disk_info.used / (1024**3),
            'disk_total': disk_info.total / (1024**3)
        }
    except:
        return None

def generate_qr(data):
    """Tạo ảnh QR Code từ text"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"Lỗi tạo QR: {str(e)}")
        return None

def generate_link(inbound, vps_ip):
    """Tạo link kết nối từ thông tin inbound"""
    try:
        settings = json.loads(inbound['settings'])
        protocol = inbound['protocol']
        port = inbound['port']
        remark = inbound['remark']
        
        if protocol == 'vless':
            client_id = settings['clients'][0]['id']
            link = f"vless://{client_id}@{vps_ip}:{port}?security=none&encryption=none&type=tcp&headerType=none#{remark}"
        elif protocol == 'vmess':
            client_id = settings['clients'][0]['id']
            vmess_json = {
                "v": "2", "ps": remark, "add": vps_ip, "port": port,
                "id": client_id, "aid": "0", "net": "tcp", "type": "none",
                "host": "", "tls": ""
            }
            link = "vmess://" + base64.b64encode(json.dumps(vmess_json).encode()).decode()
        else:
            link = f"Không hỗ trợ protocol {protocol}"
        return link
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- HÀM TƯƠNG TÁC API (Hỗ trợ URL có path) ---
def get_session(server_config):
    """
    Đăng nhập vào panel
    Hỗ trợ cả URL chuẩn và URL có secret path
    """
    session = requests.Session()
    try:
        # Lấy thông tin từ config
        base_url = server_config.get('base_url', server_config['host'])
        path = server_config.get('path', '')
        username = server_config['username']
        password = server_config['password']
        
        # Build login URL
        login_url = build_api_url(base_url, path, "login")
        
        # Thử login
        login_response = session.post(
            login_url,
            data={"username": username, "password": password},
            timeout=15
        )
        
        if login_response.status_code == 200:
            response_text = login_response.text.lower()
            if "success" in response_text or "成功" in response_text:
                # Lưu thông tin vào session để dùng sau
                session.base_url = base_url
                session.path = path
                return session
        
        return None
    except Exception as e:
        st.error(f"Lỗi kết nối: {str(e)}")
        return None

def get_inbounds(session):
    """Lấy danh sách inbound"""
    try:
        list_url = build_api_url(session.base_url, session.path, "xui/inbound/list")
        resp = session.post(list_url, timeout=15)
        
        if resp.status_code == 200:
            return resp.json().get('obj', [])
        return []
    except Exception as e:
        st.error(f"Lỗi lấy danh sách: {str(e)}")
        return []

def create_inbound(session, remark, days, protocol, data_limit_gb, vps_ip):
    """Tạo inbound mới"""
    new_uuid = str(uuid.uuid4())
    new_port = random.randint(10000, 60000)
    expiry_time = int(time.time() * 1000) + (days * 86400 * 1000)
    total_bytes = data_limit_gb * 1024 * 1024 * 1024 if data_limit_gb > 0 else 0
    
    settings = {
        "clients": [{"id": new_uuid, "email": remark, "flow": ""}],
        "decryption": "none", "fallbacks": []
    }
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
        add_url = build_api_url(session.base_url, session.path, "xui/inbound/add")
        resp = session.post(add_url, data=payload, timeout=15)
        
        if resp.status_code == 200 and "success" in resp.text.lower():
            return {"uuid": new_uuid, "port": new_port, "protocol": protocol}, "OK"
        return None, resp.text
    except Exception as e:
        return None, str(e)

def delete_inbound(session, inbound_id):
    """Xóa inbound"""
    try:
        del_url = build_api_url(session.base_url, session.path, f"xui/inbound/del/{inbound_id}")
        resp = session.post(del_url, timeout=15)
        return resp.status_code == 200
    except:
        return False

def reset_traffic(session, inbound_id, inbounds):
    """Reset traffic của inbound"""
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        target['up'] = 0
        target['down'] = 0
        
        update_url = build_api_url(session.base_url, session.path, f"xui/inbound/update/{inbound_id}")
        resp = session.post(update_url, data=target, timeout=15)
        return resp.status_code == 200
    except:
        return False

def extend_expiry(session, inbound_id, additional_days, inbounds):
    """Gia hạn thêm ngày"""
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        
        current_expiry = target['expiryTime']
        if current_expiry < int(time.time() * 1000):
            new_expiry = int(time.time() * 1000) + (additional_days * 86400 * 1000)
        else:
            new_expiry = current_expiry + (additional_days * 86400 * 1000)
        
        target['expiryTime'] = new_expiry
        
        update_url = build_api_url(session.base_url, session.path, f"xui/inbound/update/{inbound_id}")
        resp = session.post(update_url, data=target, timeout=15)
        return resp.status_code == 200
    except:
        return False

def toggle_inbound(session, inbound_id, enable, inbounds):
    """Bật/tắt inbound"""
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        target['enable'] = enable
        
        update_url = build_api_url(session.base_url, session.path, f"xui/inbound/update/{inbound_id}")
        resp = session.post(update_url, data=target, timeout=15)
        return resp.status_code == 200
    except:
        return False

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="VPN Admin Pro - Multi-Server v2", page_icon="🌐", layout="wide")

st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
    .stButton>button {border-radius: 8px; font-weight: 600;}
    .server-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9664/9664780.png", width=100)
    st.title("🌐 Multi-Server v2")
    st.caption("Hỗ trợ URL có secret path")
    
    # Load danh sách server
    servers = load_servers()
    
    if not isinstance(servers, dict):
        st.error("⚠️ Lỗi: Config file không đúng định dạng. Đang tạo mới...")
        servers = {}
        save_servers(servers)
    
    if not servers:
        st.warning("⚠️ Chưa có server nào. Vào menu Quản lý Server để thêm!")
        menu = st.radio("Menu", ["🖥️ Quản lý Server"])
    else:
        # Chọn server
        server_options = {f"{s['name']} ({s.get('base_url', s['host'])})": sid for sid, s in servers.items()}
        selected_server_name = st.selectbox("📡 Chọn Server", list(server_options.keys()))
        selected_server_id = server_options[selected_server_name]
        
        if 'current_server_id' not in st.session_state:
            st.session_state.current_server_id = selected_server_id
        else:
            st.session_state.current_server_id = selected_server_id
        
        st.write("---")
        menu = st.radio("Menu", [
            "🌍 Tổng Quan Toàn Hệ Thống",
            "📊 Dashboard Server",
            "➕ Tạo User",
            "👥 Quản Lý User",
            "📋 Chi Tiết User",
            "🖥️ Quản Lý Server",
            "⚙️ Hệ Thống"
        ])
    
    st.write("---")
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}")
    
    if st.button("🔄 Làm mới", use_container_width=True):
        st.rerun()

# --- MENU: QUẢN LÝ SERVER ---
if menu == "🖥️ Quản lý Server":
    st.header("🖥️ Quản lý danh sách Server")
    
    tab1, tab2 = st.tabs(["📋 Danh sách Server", "➕ Thêm Server Mới"])
    
    with tab1:
        servers = load_servers()
        
        if not isinstance(servers, dict) or not servers:
            st.info("ℹ️ Chưa có server nào. Thêm server mới ở tab bên cạnh!")
        else:
            for sid, sconfig in servers.items():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.subheader(f"🖥️ {sconfig['name']}")
                        st.caption(f"**Host:** {sconfig['host']}")
                        
                        # Hiển thị chi tiết parse
                        if sconfig.get('path'):
                            st.caption(f"**Base URL:** {sconfig.get('base_url', 'N/A')}")
                            st.caption(f"**Secret Path:** {sconfig['path']}")
                        
                        st.caption(f"**Username:** {sconfig['username']}")
                        st.caption(f"**Thêm lúc:** {sconfig.get('added_date', 'N/A')[:10]}")
                        if sconfig.get('notes'):
                            st.caption(f"**Ghi chú:** {sconfig['notes']}")
                    
                    with col2:
                        if st.button("🔍 Test", key=f"test_{sid}"):
                            with st.spinner("Đang test kết nối..."):
                                test_session = get_session(sconfig)
                                if test_session:
                                    st.success("✅ Kết nối OK!")
                                else:
                                    st.error("❌ Không kết nối được!")
                    
                    with col3:
                        if st.button("🗑️ Xóa", key=f"del_{sid}", type="primary"):
                            if delete_server(sid):
                                st.success(f"✅ Đã xóa server {sconfig['name']}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Xóa thất bại!")
    
    with tab2:
        st.subheader("➕ Thêm Server mới")
        
        st.info("""
        💡 **Hỗ trợ 2 định dạng URL:**
        
        **Chuẩn:** `http://123.45.67.89:8001`
        
        **Có Secret Path:** `http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o`
        """)
        
        with st.form("add_server_form"):
            new_name = st.text_input("Tên Server", placeholder="VPS Singapore 01")
            
            new_host = st.text_input(
                "HOST (URL đầy đủ)", 
                placeholder="http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o",
                help="Có thể là: http://IP:PORT hoặc http://IP:PORT/SECRET_PATH"
            )
            
            # Preview parse
            if new_host:
                base, path = parse_host_url(new_host)
                st.caption(f"📍 **Base URL:** {base}")
                if path:
                    st.caption(f"🔐 **Secret Path:** {path}")
                else:
                    st.caption(f"🔐 **Secret Path:** (không có)")
            
            new_username = st.text_input("Username", placeholder="admin")
            new_password = st.text_input("Password", type="password")
            new_notes = st.text_area("Ghi chú (optional)", placeholder="Server cho khách VIP...")
            
            submitted = st.form_submit_button("✅ Thêm Server", use_container_width=True, type="primary")
            
            if submitted:
                if not all([new_name, new_host, new_username, new_password]):
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin!")
                else:
                    # Test kết nối trước
                    with st.spinner("Đang test kết nối..."):
                        # Tạo config tạm để test
                        temp_config = {
                            "name": new_name,
                            "host": new_host,
                            "username": new_username,
                            "password": new_password
                        }
                        base_url, path = parse_host_url(new_host)
                        temp_config['base_url'] = base_url
                        temp_config['path'] = path
                        
                        test_session = get_session(temp_config)
                        
                        if test_session:
                            server_id = add_server(new_name, new_host, new_username, new_password, new_notes)
                            if server_id:
                                st.balloons()
                                st.success(f"✅ Đã thêm server {new_name} thành công!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Lỗi khi lưu server!")
                        else:
                            st.error("❌ Không thể kết nối! Kiểm tra lại URL, USERNAME, PASSWORD.")

# --- MENU: TỔNG QUAN (rút gọn để demo) ---
elif menu == "🌍 Tổng Quan Toàn Hệ Thống":
    st.header("🌍 Tổng quan tất cả Server")
    
    servers = load_servers()
    
    if not isinstance(servers, dict) or not servers:
        st.info("ℹ️ Chưa có server nào. Vào menu 'Quản lý Server' để thêm!")
    else:
        total_servers = len(servers)
        online_servers = 0
        server_data = []
        
        for sid, sconfig in servers.items():
            with st.spinner(f"Đang kết nối {sconfig['name']}..."):
                session = get_session(sconfig)
                
                if session:
                    online_servers += 1
                    inbounds = get_inbounds(session)
                    total_users = len(inbounds)
                    status = "🟢 Online"
                else:
                    total_users = 0
                    status = "🔴 Offline"
                
                server_data.append({
                    "Server": sconfig['name'],
                    "Host": sconfig['host'],
                    "Type": "🔐 Secret Path" if sconfig.get('path') else "📡 Standard",
                    "Status": status,
                    "Users": total_users
                })
        
        col1, col2 = st.columns(2)
        col1.metric("🖥️ Tổng Server", total_servers)
        col2.metric("🟢 Server Online", online_servers)
        
        st.write("---")
        st.subheader("📋 Chi tiết từng Server")
        df = pd.DataFrame(server_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- CÁC MENU KHÁC (Tương tự như trước, nhưng dùng get_session(server_config) thay vì get_session(host, user, pass)) ---
elif servers and menu in ["📊 Dashboard Server", "➕ Tạo User", "👥 Quản Lý User", "📋 Chi Tiết User", "⚙️ Hệ Thống"]:
    
    current_server_id = st.session_state.current_server_id
    server_config = get_server_config(current_server_id)
    
    if not server_config:
        st.error("❌ Server không tồn tại!")
        st.stop()
    
    # Hiển thị info server đang làm việc
    st.info(f"🖥️ Đang làm việc trên: **{server_config['name']}** ({server_config['host']})")
    
    # Kết nối
    session = get_session(server_config)
    if not session:
        st.error(f"❌ Không thể kết nối tới {server_config['name']}!")
        st.stop()
    
    inbounds = get_inbounds(session)
    
    # Extract IP để dùng trong link
    base_url = server_config.get('base_url', server_config['host'])
    vps_ip = base_url.split("//")[-1].split(":")[0]
    
    # --- TẠO USER (Demo ngắn gọn) ---
    if menu == "➕ Tạo User":
        st.header(f"➕ Tạo User - {server_config['name']}")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                remark = st.text_input("Tên user", placeholder="user_01")
                protocol = st.selectbox("Protocol", ["vless", "vmess"])
            with col2:
                days = st.slider("Thời hạn (ngày)", 1, 365, 30)
                data_limit = st.number_input("Data (GB, 0=unlimited)", 0, 1000, 0, 10)
            
            if st.button("✨ Tạo", type="primary", use_container_width=True):
                if not remark:
                    st.warning("⚠️ Nhập tên user!")
                else:
                    with st.spinner("Đang tạo..."):
                        res, msg = create_inbound(session, remark, days, protocol, data_limit, vps_ip)
                    
                    if res:
                        st.balloons()
                        st.success(f"✅ Tạo thành công! Port: {res['port']}")
                        
                        if res['protocol'] == 'vless':
                            link = f"vless://{res['uuid']}@{vps_ip}:{res['port']}?security=none&encryption=none&type=tcp&headerType=none#{remark}"
                        else:
                            vmess_json = {"v": "2", "ps": remark, "add": vps_ip, "port": res['port'], "id": res['uuid'], "aid": "0", "net": "tcp", "type": "none", "host": "", "tls": ""}
                            link = "vmess://" + base64.b64encode(json.dumps(vmess_json).encode()).decode()
                        
                        st.text_area("Link:", link, height=80)
                        
                        qr_img = generate_qr(link)
                        if qr_img:
                            st.image(qr_img, width=200)
                    else:
                        st.error(f"❌ Lỗi: {msg}")
    
    # --- QUẢN LÝ USER (Demo ngắn gọn) ---
    elif menu == "👥 Quản Lý User":
        st.header(f"👥 Quản lý User - {server_config['name']}")
        
        if inbounds:
            filtered = []
            for item in inbounds:
                gb_used = (item['up'] + item['down']) / (1024**3)
                filtered.append({
                    "ID": item['id'],
                    "User": item['remark'],
                    "Port": item['port'],
                    "Protocol": item['protocol'].upper(),
                    "Data (GB)": round(gb_used, 2),
                })
            
            df = pd.DataFrame(filtered)
            st.dataframe(df.drop(columns=['ID']), use_container_width=True, hide_index=True)
            
            st.write("---")
            
            if filtered:
                user_dict = {f"{x['User']} (Port {x['Port']})": x['ID'] for x in filtered}
                selected = st.selectbox("Chọn user:", list(user_dict.keys()))
                selected_id = user_dict[selected]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("🔄 Reset Traffic"):
                        if reset_traffic(session, selected_id, inbounds):
                            st.success("✅ Đã reset!")
                            time.sleep(1)
                            st.rerun()
                
                with col2:
                    if st.button("⏱️ Gia hạn +30d"):
                        if extend_expiry(session, selected_id, 30, inbounds):
                            st.success("✅ Đã gia hạn!")
                            time.sleep(1)
                            st.rerun()
                
                with col3:
                    current = next((x for x in inbounds if x['id'] == selected_id), None)
                    if current:
                        action = "⏸️ Tắt" if current['enable'] else "▶️ Bật"
                        if st.button(action):
                            if toggle_inbound(session, selected_id, not current['enable'], inbounds):
                                st.success("✅ OK!")
                                time.sleep(1)
                                st.rerun()
                
                with col4:
                    if st.button("🗑️ Xóa"):
                        if delete_inbound(session, selected_id):
                            st.success("✅ Đã xóa!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("ℹ️ Chưa có user.")
    
    # --- DASHBOARD (Demo ngắn) ---
    elif menu == "📊 Dashboard Server":
        st.header(f"📊 Dashboard - {server_config['name']}")
        
        total_users = len(inbounds)
        active_users = len([x for x in inbounds if x['enable']])
        
        col1, col2 = st.columns(2)
        col1.metric("👥 Tổng User", total_users)
        col2.metric("✅ Hoạt động", active_users)
    
    else:
        st.info(f"Menu {menu} - Đang phát triển...")

st.write("---")
st.caption("© 2024 VPN Admin Pro - Multi-Server v2.0 (Hỗ trợ Secret Path)")
