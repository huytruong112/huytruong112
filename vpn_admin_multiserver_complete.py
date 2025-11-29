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
from urllib.parse import urlparse

# --- CẤU HÌNH ---
SERVERS_CONFIG_FILE = "servers_config.json"

# --- HÀM PARSE URL ---
def parse_host_url(host_url):
    """Parse URL hỗ trợ cả có và không có path"""
    try:
        if not host_url.startswith(('http://', 'https://')):
            host_url = 'http://' + host_url
        
        parsed = urlparse(host_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path.rstrip('/')
        
        return base_url, path
    except:
        return host_url, ""

def build_api_url(base_url, path, endpoint):
    """Build full API URL"""
    endpoint = endpoint.lstrip('/')
    if path:
        return f"{base_url}{path}/{endpoint}"
    return f"{base_url}/{endpoint}"

# --- SERVER MANAGEMENT ---
def load_servers():
    """Load servers từ file JSON"""
    if os.path.exists(SERVERS_CONFIG_FILE):
        try:
            with open(SERVERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except Exception as e:
            st.error(f"Lỗi đọc config: {str(e)}")
            return {}
    return {}

def save_servers(servers):
    """Lưu servers vào file JSON"""
    try:
        if not isinstance(servers, dict):
            servers = {}
        with open(SERVERS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu config: {str(e)}")
        return False

def add_server(name, host_url, username, password, notes=""):
    """Thêm server mới - FIX: Load servers hiện có, append thêm mới"""
    try:
        # IMPORTANT: Load servers hiện có
        servers = load_servers()
        if not isinstance(servers, dict):
            servers = {}
        
        # Parse URL
        base_url, path = parse_host_url(host_url)
        
        # Tạo ID mới
        server_id = str(uuid.uuid4())[:8]
        
        # IMPORTANT: Thêm vào dict hiện có, KHÔNG overwrite
        servers[server_id] = {
            "name": name,
            "host": host_url,
            "base_url": base_url,
            "path": path,
            "username": username,
            "password": password,
            "notes": notes,
            "added_date": datetime.now().isoformat()
        }
        
        # Lưu lại toàn bộ dict
        if save_servers(servers):
            return server_id
        return None
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
            return save_servers(servers)
        return False
    except:
        return False

def get_server_config(server_id):
    """Lấy config của 1 server"""
    servers = load_servers()
    if not isinstance(servers, dict):
        return None
    return servers.get(server_id, None)

# --- SYSTEM HELPERS ---
def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            'cpu': cpu,
            'ram_percent': ram.percent,
            'ram_used': ram.used / (1024**3),
            'ram_total': ram.total / (1024**3),
            'disk_percent': disk.percent,
            'disk_used': disk.used / (1024**3),
            'disk_total': disk.total / (1024**3)
        }
    except:
        return None

def generate_qr(data):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()
    except:
        return None

def generate_link(inbound, vps_ip):
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
            link = f"Protocol {protocol} chưa hỗ trợ"
        return link
    except:
        return "Lỗi tạo link"

# --- API FUNCTIONS ---
def get_session(server_config):
    """Login vào panel - hỗ trợ path"""
    session = requests.Session()
    try:
        base_url = server_config.get('base_url', server_config['host'])
        path = server_config.get('path', '')
        username = server_config['username']
        password = server_config['password']
        
        login_url = build_api_url(base_url, path, "login")
        
        resp = session.post(
            login_url,
            data={"username": username, "password": password},
            timeout=15
        )
        
        if resp.status_code == 200:
            if "success" in resp.text.lower() or "成功" in resp.text:
                session.base_url = base_url
                session.path = path
                return session
        
        return None
    except Exception as e:
        return None

def get_inbounds(session):
    try:
        url = build_api_url(session.base_url, session.path, "xui/inbound/list")
        resp = session.post(url, timeout=15)
        if resp.status_code == 200:
            return resp.json().get('obj', [])
        return []
    except:
        return []

def create_inbound(session, remark, days, protocol, data_limit_gb, vps_ip):
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
        url = build_api_url(session.base_url, session.path, "xui/inbound/add")
        resp = session.post(url, data=payload, timeout=15)
        if resp.status_code == 200 and "success" in resp.text.lower():
            return {"uuid": new_uuid, "port": new_port, "protocol": protocol}, "OK"
        return None, resp.text
    except Exception as e:
        return None, str(e)

def delete_inbound(session, inbound_id):
    try:
        url = build_api_url(session.base_url, session.path, f"xui/inbound/del/{inbound_id}")
        resp = session.post(url, timeout=15)
        return resp.status_code == 200
    except:
        return False

def reset_traffic(session, inbound_id, inbounds):
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        target['up'] = 0
        target['down'] = 0
        url = build_api_url(session.base_url, session.path, f"xui/inbound/update/{inbound_id}")
        resp = session.post(url, data=target, timeout=15)
        return resp.status_code == 200
    except:
        return False

def extend_expiry(session, inbound_id, days, inbounds):
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        
        current = target['expiryTime']
        if current < int(time.time() * 1000):
            new_expiry = int(time.time() * 1000) + (days * 86400 * 1000)
        else:
            new_expiry = current + (days * 86400 * 1000)
        
        target['expiryTime'] = new_expiry
        url = build_api_url(session.base_url, session.path, f"xui/inbound/update/{inbound_id}")
        resp = session.post(url, data=target, timeout=15)
        return resp.status_code == 200
    except:
        return False

def toggle_inbound(session, inbound_id, enable, inbounds):
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        target['enable'] = enable
        url = build_api_url(session.base_url, session.path, f"xui/inbound/update/{inbound_id}")
        resp = session.post(url, data=target, timeout=15)
        return resp.status_code == 200
    except:
        return False

# --- UI ---
st.set_page_config(page_title="VPN Admin Pro - Multi-Server Complete", page_icon="🌐", layout="wide")

st.markdown("""
<style>
    .stButton>button {border-radius: 8px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9664/9664780.png", width=100)
    st.title("🌐 Multi-Server")
    st.caption("✅ Hỗ trợ nhiều server + Secret Path")
    
    servers = load_servers()
    
    if not isinstance(servers, dict):
        servers = {}
        save_servers(servers)
    
    if not servers:
        st.warning("⚠️ Chưa có server. Thêm server ở tab bên!")
        menu = st.radio("Menu", ["🖥️ Quản lý Server"])
    else:
        server_options = {f"{s['name']} ({s.get('base_url', s['host'])})": sid for sid, s in servers.items()}
        
        # FIX: Đảm bảo có default selection
        if 'current_server_id' not in st.session_state:
            st.session_state.current_server_id = list(servers.keys())[0]
        
        selected_name = st.selectbox("📡 Chọn Server", list(server_options.keys()))
        st.session_state.current_server_id = server_options[selected_name]
        
        st.write("---")
        menu = st.radio("Menu", [
            "🌍 Tổng Quan",
            "📊 Dashboard",
            "➕ Tạo User",
            "👥 Quản Lý User",
            "🖥️ Quản lý Server"
        ])
    
    st.write("---")
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 Làm mới", use_container_width=True):
        st.rerun()

# --- QUẢN LÝ SERVER ---
if menu == "🖥️ Quản lý Server":
    st.header("🖥️ Quản lý Server")
    
    tab1, tab2 = st.tabs(["📋 Danh sách Server", "➕ Thêm Server"])
    
    with tab1:
        servers = load_servers()
        
        if not isinstance(servers, dict) or not servers:
            st.info("ℹ️ Chưa có server. Thêm ở tab bên!")
        else:
            st.success(f"✅ Đang quản lý {len(servers)} server")
            
            for sid, sconfig in servers.items():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.subheader(f"🖥️ {sconfig['name']}")
                        st.caption(f"**Host:** {sconfig['host']}")
                        
                        if sconfig.get('path'):
                            st.caption(f"**Base:** {sconfig.get('base_url')}")
                            st.caption(f"**Path:** {sconfig['path']}")
                        
                        st.caption(f"**User:** {sconfig['username']}")
                        if sconfig.get('notes'):
                            st.caption(f"**Note:** {sconfig['notes']}")
                    
                    with col2:
                        if st.button("🔍 Test", key=f"test_{sid}"):
                            with st.spinner("Testing..."):
                                sess = get_session(sconfig)
                                if sess:
                                    st.success("✅ OK!")
                                else:
                                    st.error("❌ Failed!")
                    
                    with col3:
                        if st.button("🗑️ Xóa", key=f"del_{sid}"):
                            if delete_server(sid):
                                st.success("✅ Đã xóa!")
                                time.sleep(1)
                                st.rerun()
    
    with tab2:
        st.subheader("➕ Thêm Server Mới")
        
        st.info("""
        💡 **Hỗ trợ 2 loại URL:**
        - Chuẩn: `http://123.45.67.89:8001`
        - Có Path: `http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o`
        """)
        
        # FIX: Dùng unique key cho form để reset sau khi submit
        with st.form(key=f"add_form_{int(time.time())}", clear_on_submit=True):
            name = st.text_input("Tên Server *", placeholder="VPS Singapore 01")
            host = st.text_input(
                "HOST (URL đầy đủ) *",
                placeholder="http://45.119.84.238:8888/6SnQh95LlD8LhQxQ2o",
                help="Có thể là http://IP:PORT hoặc http://IP:PORT/PATH"
            )
            
            # Preview parse
            if host:
                base, path = parse_host_url(host)
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.caption(f"📍 Base URL: `{base}`")
                with col_p2:
                    if path:
                        st.caption(f"🔐 Secret Path: `{path}`")
                    else:
                        st.caption("🔐 Secret Path: (không có)")
            
            username = st.text_input("Username *", placeholder="admin")
            password = st.text_input("Password *", type="password")
            notes = st.text_area("Ghi chú", placeholder="Server cho khách VIP...")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("✅ Thêm Server", type="primary", use_container_width=True)
            with col_btn2:
                canceled = st.form_submit_button("❌ Hủy", use_container_width=True)
            
            if submitted:
                if not all([name, host, username, password]):
                    st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc!")
                else:
                    with st.spinner("Đang test kết nối..."):
                        # Test connection
                        temp_config = {
                            "name": name,
                            "host": host,
                            "username": username,
                            "password": password
                        }
                        base_url, path = parse_host_url(host)
                        temp_config['base_url'] = base_url
                        temp_config['path'] = path
                        
                        test_sess = get_session(temp_config)
                        
                        if test_sess:
                            # Connection OK - Thêm vào config
                            server_id = add_server(name, host, username, password, notes)
                            
                            if server_id:
                                st.balloons()
                                st.success(f"✅ Đã thêm server '{name}' thành công!")
                                st.info("🔄 Đang reload để cập nhật danh sách...")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Lỗi khi lưu server. Thử lại!")
                        else:
                            st.error("❌ Không thể kết nối! Kiểm tra lại URL, username, password.")
                            st.caption("💡 Tips: Đảm bảo panel đang chạy và thông tin đăng nhập đúng.")

# --- TỔNG QUAN ---
elif menu == "🌍 Tổng Quan":
    st.header("🌍 Tổng quan tất cả Server")
    
    servers = load_servers()
    
    if not isinstance(servers, dict) or not servers:
        st.info("ℹ️ Chưa có server.")
    else:
        total = len(servers)
        online = 0
        data = []
        
        progress = st.progress(0)
        status_text = st.empty()
        
        for idx, (sid, sconf) in enumerate(servers.items()):
            status_text.text(f"Đang check {sconf['name']}... ({idx+1}/{total})")
            progress.progress((idx + 1) / total)
            
            sess = get_session(sconf)
            if sess:
                online += 1
                inbounds = get_inbounds(sess)
                users = len(inbounds)
                stat = "🟢 Online"
            else:
                users = 0
                stat = "🔴 Offline"
            
            data.append({
                "Server": sconf['name'],
                "Host": sconf['host'],
                "Type": "🔐 Secret" if sconf.get('path') else "📡 Standard",
                "Status": stat,
                "Users": users
            })
        
        status_text.empty()
        progress.empty()
        
        col1, col2 = st.columns(2)
        col1.metric("🖥️ Tổng Server", total)
        col2.metric("🟢 Online", online)
        
        st.write("---")
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# --- CÁC MENU KHÁC ---
elif servers and menu in ["📊 Dashboard", "➕ Tạo User", "👥 Quản Lý User"]:
    
    server_id = st.session_state.current_server_id
    sconf = get_server_config(server_id)
    
    if not sconf:
        st.error("❌ Server không tồn tại!")
        st.stop()
    
    st.info(f"🖥️ Đang làm việc trên: **{sconf['name']}**")
    
    sess = get_session(sconf)
    if not sess:
        st.error(f"❌ Không kết nối được tới {sconf['name']}!")
        st.stop()
    
    inbounds = get_inbounds(sess)
    vps_ip = sconf.get('base_url', sconf['host']).split("//")[-1].split(":")[0]
    
    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.header(f"📊 Dashboard - {sconf['name']}")
        
        total = len(inbounds)
        active = len([x for x in inbounds if x['enable']])
        
        col1, col2 = st.columns(2)
        col1.metric("👥 Tổng User", total)
        col2.metric("✅ Hoạt động", active)
        
        if total > 0:
            st.write("---")
            proto = pd.DataFrame(inbounds)['protocol'].value_counts()
            st.bar_chart(proto)
    
    # --- TẠO USER ---
    elif menu == "➕ Tạo User":
        st.header(f"➕ Tạo User - {sconf['name']}")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                remark = st.text_input("Tên user", placeholder="user_01")
                protocol = st.selectbox("Protocol", ["vless", "vmess"])
            with col2:
                days = st.slider("Thời hạn (ngày)", 1, 365, 30)
                data_gb = st.number_input("Data (GB, 0=unlimited)", 0, 1000, 0, 10)
            
            if st.button("✨ Tạo", type="primary", use_container_width=True):
                if not remark:
                    st.warning("⚠️ Nhập tên user!")
                else:
                    with st.spinner("Đang tạo..."):
                        res, msg = create_inbound(sess, remark, days, protocol, data_gb, vps_ip)
                    
                    if res:
                        st.balloons()
                        st.success(f"✅ Thành công! Port: {res['port']}")
                        
                        if res['protocol'] == 'vless':
                            link = f"vless://{res['uuid']}@{vps_ip}:{res['port']}?security=none&encryption=none&type=tcp&headerType=none#{remark}"
                        else:
                            vmess = {"v": "2", "ps": remark, "add": vps_ip, "port": res['port'], "id": res['uuid'], "aid": "0", "net": "tcp", "type": "none", "host": "", "tls": ""}
                            link = "vmess://" + base64.b64encode(json.dumps(vmess).encode()).decode()
                        
                        st.text_area("Link:", link, height=80)
                        qr = generate_qr(link)
                        if qr:
                            st.image(qr, width=200)
                    else:
                        st.error(f"❌ Lỗi: {msg}")
    
    # --- QUẢN LÝ USER ---
    elif menu == "👥 Quản Lý User":
        st.header(f"👥 Quản lý - {sconf['name']}")
        
        if inbounds:
            data = []
            for item in inbounds:
                gb = (item['up'] + item['down']) / (1024**3)
                data.append({
                    "ID": item['id'],
                    "User": item['remark'],
                    "Port": item['port'],
                    "Data (GB)": round(gb, 2),
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df.drop(columns=['ID']), use_container_width=True, hide_index=True)
            
            st.write("---")
            
            udict = {f"{x['User']} (Port {x['Port']})": x['ID'] for x in data}
            sel = st.selectbox("Chọn user:", list(udict.keys()))
            sel_id = udict[sel]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔄 Reset"):
                    if reset_traffic(sess, sel_id, inbounds):
                        st.success("✅ OK!")
                        time.sleep(1)
                        st.rerun()
            
            with col2:
                if st.button("⏱️ +30d"):
                    if extend_expiry(sess, sel_id, 30, inbounds):
                        st.success("✅ OK!")
                        time.sleep(1)
                        st.rerun()
            
            with col3:
                curr = next((x for x in inbounds if x['id'] == sel_id), None)
                if curr:
                    txt = "⏸️ Tắt" if curr['enable'] else "▶️ Bật"
                    if st.button(txt):
                        if toggle_inbound(sess, sel_id, not curr['enable'], inbounds):
                            st.success("✅ OK!")
                            time.sleep(1)
                            st.rerun()
            
            with col4:
                if st.button("🗑️ Xóa"):
                    if delete_inbound(sess, sel_id):
                        st.success("✅ OK!")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("ℹ️ Chưa có user.")

st.write("---")
st.caption("© 2024 VPN Admin Pro - Multi-Server Complete Edition")
