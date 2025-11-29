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

# --- CẤU HÌNH MULTI-SERVER ---
SERVERS_CONFIG_FILE = "servers_config.json"

# --- HÀM QUẢN LÝ SERVER CONFIG ---
def load_servers():
    """Load danh sách server từ file JSON"""
    if os.path.exists(SERVERS_CONFIG_FILE):
        try:
            with open(SERVERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # FIX: Đảm bảo luôn return dict, không phải list
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
        # FIX: Đảm bảo servers là dict
        if not isinstance(servers, dict):
            servers = {}
        
        with open(SERVERS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu file config: {str(e)}")
        return False

def add_server(name, host, username, password, notes=""):
    """Thêm server mới"""
    try:
        servers = load_servers()
        # FIX: Double check servers là dict
        if not isinstance(servers, dict):
            servers = {}
        
        server_id = str(uuid.uuid4())[:8]
        servers[server_id] = {
            "name": name,
            "host": host,
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

# --- HÀM TƯƠNG TÁC API ---
def get_session(host, username, password):
    """Đăng nhập vào panel"""
    session = requests.Session()
    try:
        login = session.post(f"{host}/login", data={"username": username, "password": password}, timeout=10)
        if login.status_code == 200 and "success" in login.text.lower():
            return session
        return None
    except Exception as e:
        st.error(f"Lỗi kết nối {host}: {str(e)}")
        return None

def get_inbounds(session, host):
    """Lấy danh sách inbound"""
    try:
        resp = session.post(f"{host}/xui/inbound/list", timeout=10)
        if resp.status_code == 200:
            return resp.json().get('obj', [])
        return []
    except:
        return []

def create_inbound(session, host, remark, days, protocol, data_limit_gb, vps_ip):
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
        resp = session.post(f"{host}/xui/inbound/add", data=payload, timeout=10)
        if resp.status_code == 200 and "success" in resp.text.lower():
            return {"uuid": new_uuid, "port": new_port, "protocol": protocol}, "OK"
        return None, resp.text
    except Exception as e:
        return None, str(e)

def delete_inbound(session, host, inbound_id):
    """Xóa inbound"""
    try:
        resp = session.post(f"{host}/xui/inbound/del/{inbound_id}", timeout=10)
        return resp.status_code == 200
    except:
        return False

def reset_traffic(session, host, inbound_id, inbounds):
    """Reset traffic của inbound"""
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        target['up'] = 0
        target['down'] = 0
        resp = session.post(f"{host}/xui/inbound/update/{inbound_id}", data=target, timeout=10)
        return resp.status_code == 200
    except:
        return False

def extend_expiry(session, host, inbound_id, additional_days, inbounds):
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
        resp = session.post(f"{host}/xui/inbound/update/{inbound_id}", data=target, timeout=10)
        return resp.status_code == 200
    except:
        return False

def toggle_inbound(session, host, inbound_id, enable, inbounds):
    """Bật/tắt inbound"""
    try:
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        target['enable'] = enable
        resp = session.post(f"{host}/xui/inbound/update/{inbound_id}", data=target, timeout=10)
        return resp.status_code == 200
    except:
        return False

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="VPN Admin Pro - Multi-Server", page_icon="🌐", layout="wide")

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
    st.title("🌐 Multi-Server Admin")
    
    # Load danh sách server
    servers = load_servers()
    
    # FIX: Kiểm tra servers là dict
    if not isinstance(servers, dict):
        st.error("⚠️ Lỗi: Config file không đúng định dạng. Đang tạo mới...")
        servers = {}
        save_servers(servers)
    
    if not servers:
        st.warning("⚠️ Chưa có server nào. Vào menu Quản lý Server để thêm!")
        menu = st.radio("Menu", ["🖥️ Quản lý Server"])
    else:
        # Chọn server
        server_options = {f"{s['name']} ({s['host']})": sid for sid, s in servers.items()}
        selected_server_name = st.selectbox("📡 Chọn Server", list(server_options.keys()))
        selected_server_id = server_options[selected_server_name]
        
        # Lưu vào session state
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

# --- MENU: TỔNG QUAN TOÀN HỆ THỐNG ---
if menu == "🌍 Tổng Quan Toàn Hệ Thống":
    st.header("🌍 Tổng quan tất cả Server")
    
    servers = load_servers()
    
    if not isinstance(servers, dict) or not servers:
        st.info("ℹ️ Chưa có server nào. Vào menu 'Quản lý Server' để thêm!")
    else:
        # Metrics tổng hợp
        total_servers = len(servers)
        total_users_all = 0
        total_traffic_all = 0
        online_servers = 0
        
        server_data = []
        
        for sid, sconfig in servers.items():
            with st.spinner(f"Đang kết nối {sconfig['name']}..."):
                session = get_session(sconfig['host'], sconfig['username'], sconfig['password'])
                
                if session:
                    online_servers += 1
                    inbounds = get_inbounds(session, sconfig['host'])
                    total_users = len(inbounds)
                    total_traffic = sum([x['up'] + x['down'] for x in inbounds]) / (1024**3)
                    active_users = len([x for x in inbounds if x['enable']])
                    status = "🟢 Online"
                else:
                    total_users = 0
                    total_traffic = 0
                    active_users = 0
                    status = "🔴 Offline"
                
                total_users_all += total_users
                total_traffic_all += total_traffic
                
                vps_ip = sconfig['host'].split("//")[-1].split(":")[0]
                
                server_data.append({
                    "ID": sid,
                    "Server": sconfig['name'],
                    "IP": vps_ip,
                    "Status": status,
                    "Users": total_users,
                    "Active": active_users,
                    "Traffic (GB)": round(total_traffic, 2)
                })
        
        # Hiển thị metrics tổng
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🖥️ Tổng Server", total_servers)
        col2.metric("🟢 Server Online", online_servers)
        col3.metric("👥 Tổng User", total_users_all)
        col4.metric("📊 Tổng Traffic", f"{total_traffic_all:.2f} GB")
        
        st.write("---")
        
        # Bảng chi tiết server
        st.subheader("📋 Chi tiết từng Server")
        df = pd.DataFrame(server_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.write("---")
        
        # Biểu đồ
        if len(server_data) > 0:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("📈 Phân bổ User theo Server")
                chart_df = pd.DataFrame(server_data)[['Server', 'Users']].set_index('Server')
                st.bar_chart(chart_df)
            
            with col_chart2:
                st.subheader("📊 Traffic theo Server")
                chart_df2 = pd.DataFrame(server_data)[['Server', 'Traffic (GB)']].set_index('Server')
                st.bar_chart(chart_df2)

# --- MENU: QUẢN LÝ SERVER ---
elif menu == "🖥️ Quản lý Server":
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
                        st.caption(f"**Username:** {sconfig['username']}")
                        st.caption(f"**Thêm lúc:** {sconfig.get('added_date', 'N/A')[:10]}")
                        if sconfig.get('notes'):
                            st.caption(f"**Ghi chú:** {sconfig['notes']}")
                    
                    with col2:
                        if st.button("🔍 Test", key=f"test_{sid}"):
                            with st.spinner("Đang test kết nối..."):
                                test_session = get_session(sconfig['host'], sconfig['username'], sconfig['password'])
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
        
        with st.form("add_server_form"):
            new_name = st.text_input("Tên Server", placeholder="VPS Singapore 01")
            new_host = st.text_input("HOST (URL đầy đủ)", placeholder="http://123.45.67.89:8001")
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
                        test_session = get_session(new_host, new_username, new_password)
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
                            st.error("❌ Không thể kết nối! Kiểm tra lại HOST, USERNAME, PASSWORD.")

# --- CÁC MENU KHÁC ---
elif servers and menu in ["📊 Dashboard Server", "➕ Tạo User", "👥 Quản Lý User", "📋 Chi Tiết User", "⚙️ Hệ Thống"]:
    
    # Lấy config server hiện tại
    current_server_id = st.session_state.current_server_id
    server_config = get_server_config(current_server_id)
    
    if not server_config:
        st.error("❌ Server không tồn tại!")
        st.stop()
    
    st.info(f"🖥️ Đang làm việc trên: **{server_config['name']}** ({server_config['host']})")
    
    # Kết nối
    session = get_session(server_config['host'], server_config['username'], server_config['password'])
    if not session:
        st.error(f"❌ Không thể kết nối tới {server_config['name']}! Kiểm tra lại config.")
        st.stop()
    
    inbounds = get_inbounds(session, server_config['host'])
    vps_ip = server_config['host'].split("//")[-1].split(":")[0]
    
    # --- DASHBOARD SERVER ---
    if menu == "📊 Dashboard Server":
        st.header(f"📊 Dashboard - {server_config['name']}")
        
        total_users = len(inbounds)
        total_traffic = sum([x['up'] + x['down'] for x in inbounds]) / (1024**3)
        active_users = len([x for x in inbounds if x['enable']])
        expired_users = len([x for x in inbounds if x['expiryTime'] > 0 and x['expiryTime'] < int(time.time() * 1000)])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("👥 Tổng User", total_users)
        col2.metric("✅ Hoạt động", active_users)
        col3.metric("📊 Traffic", f"{total_traffic:.2f} GB")
        col4.metric("⚠️ Hết hạn", expired_users)
        
        st.write("---")
        
        # Tài nguyên (nếu chạy local trên VPS này)
        stats = get_system_stats()
        if stats:
            st.subheader("🖥️ Tài nguyên Server")
            col_cpu, col_ram, col_disk = st.columns(3)
            with col_cpu:
                st.metric("CPU", f"{stats['cpu']:.1f}%")
                st.progress(min(stats['cpu'] / 100, 1.0))
            with col_ram:
                st.metric("RAM", f"{stats['ram_percent']:.1f}%")
                st.progress(stats['ram_percent'] / 100)
            with col_disk:
                st.metric("Disk", f"{stats['disk_percent']:.1f}%")
                st.progress(stats['disk_percent'] / 100)
        
        st.write("---")
        
        # Charts
        if total_users > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📈 Phân bổ Protocol")
                proto_df = pd.DataFrame(inbounds)['protocol'].value_counts()
                st.bar_chart(proto_df)
            with col2:
                st.subheader("🔝 Top 5 User")
                top_users = sorted(inbounds, key=lambda x: x['up'] + x['down'], reverse=True)[:5]
                top_df = pd.DataFrame([{
                    'User': x['remark'],
                    'Data (GB)': (x['up'] + x['down']) / (1024**3)
                } for x in top_users])
                st.dataframe(top_df, use_container_width=True, hide_index=True)
    
    # --- TẠO USER ---
    elif menu == "➕ Tạo User":
        st.header(f"➕ Tạo User mới - {server_config['name']}")
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                remark = st.text_input("Tên khách hàng", placeholder="user_01")
                protocol = st.selectbox("Protocol", ["vless", "vmess"])
            with col2:
                days = st.slider("Thời hạn (ngày)", 1, 365, 30)
                data_limit = st.number_input("Data Limit (GB, 0=unlimited)", 0, 1000, 0, 10)
            
            if st.button("✨ Tạo Ngay", type="primary", use_container_width=True):
                if not remark:
                    st.warning("⚠️ Nhập tên khách hàng!")
                else:
                    with st.spinner("Đang tạo..."):
                        res, msg = create_inbound(session, server_config['host'], remark, days, protocol, data_limit, vps_ip)
                    
                    if res:
                        st.balloons()
                        st.success(f"✅ Đã tạo thành công!")
                        
                        if res['protocol'] == 'vless':
                            link = f"vless://{res['uuid']}@{vps_ip}:{res['port']}?security=none&encryption=none&type=tcp&headerType=none#{remark}"
                        else:
                            vmess_json = {"v": "2", "ps": remark, "add": vps_ip, "port": res['port'], "id": res['uuid'], "aid": "0", "net": "tcp", "type": "none", "host": "", "tls": ""}
                            link = "vmess://" + base64.b64encode(json.dumps(vmess_json).encode()).decode()
                        
                        col_link, col_qr = st.columns([3, 1])
                        with col_link:
                            st.text_area("Link:", link, height=100)
                        with col_qr:
                            qr_img = generate_qr(link)
                            if qr_img:
                                st.image(qr_img, width=200)
                    else:
                        st.error(f"❌ Lỗi: {msg}")
    
    # --- QUẢN LÝ USER ---
    elif menu == "👥 Quản Lý User":
        st.header(f"👥 Quản lý User - {server_config['name']}")
        
        search = st.text_input("🔍 Tìm kiếm...", placeholder="Tên hoặc port...")
        
        if inbounds:
            filtered = []
            for item in inbounds:
                if search and (search.lower() not in item['remark'].lower() and search not in str(item['port'])):
                    continue
                
                gb_used = (item['up'] + item['down']) / (1024**3)
                exp_date = datetime.fromtimestamp(item['expiryTime']/1000).strftime('%d/%m/%Y') if item['expiryTime'] > 0 else "Vĩnh viễn"
                status = "✅" if item['enable'] else "❌"
                
                filtered.append({
                    "ID": item['id'],
                    "Status": status,
                    "User": item['remark'],
                    "Port": item['port'],
                    "Protocol": item['protocol'].upper(),
                    "Data (GB)": round(gb_used, 2),
                    "Hết hạn": exp_date
                })
            
            df = pd.DataFrame(filtered)
            st.dataframe(df.drop(columns=['ID']), use_container_width=True, hide_index=True)
            
            st.write("---")
            
            # Actions
            if filtered:
                user_dict = {f"{x['User']} (Port {x['Port']})": x['ID'] for x in filtered}
                selected = st.selectbox("Chọn user:", list(user_dict.keys()))
                selected_id = user_dict[selected]
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    if st.button("🔄 Reset Traffic", use_container_width=True):
                        if reset_traffic(session, server_config['host'], selected_id, inbounds):
                            st.success("✅ Đã reset!")
                            time.sleep(1)
                            st.rerun()
                
                with col2:
                    if st.button("⏱️ Gia hạn +30d", use_container_width=True):
                        if extend_expiry(session, server_config['host'], selected_id, 30, inbounds):
                            st.success("✅ Đã gia hạn!")
                            time.sleep(1)
                            st.rerun()
                
                with col3:
                    current = next((x for x in inbounds if x['id'] == selected_id), None)
                    if current:
                        action_text = "⏸️ Tắt" if current['enable'] else "▶️ Bật"
                        if st.button(action_text, use_container_width=True):
                            if toggle_inbound(session, server_config['host'], selected_id, not current['enable'], inbounds):
                                st.success("✅ Đã cập nhật!")
                                time.sleep(1)
                                st.rerun()
                
                with col4:
                    if st.button("📋 Xem Link", use_container_width=True):
                        current = next((x for x in inbounds if x['id'] == selected_id), None)
                        if current:
                            link = generate_link(current, vps_ip)
                            st.text_area("Link:", link, height=100, key="view_link_area")
                            qr_img = generate_qr(link)
                            if qr_img:
                                st.image(qr_img, width=200)
                
                with col5:
                    if st.button("🗑️ Xóa", use_container_width=True, type="primary"):
                        st.session_state['confirm_delete_id'] = selected_id
                
                # Xác nhận xóa
                if 'confirm_delete_id' in st.session_state and st.session_state.get('confirm_delete_id') == selected_id:
                    st.warning("⚠️ Xác nhận xóa user này?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Xác nhận", key="confirm_yes"):
                            if delete_inbound(session, server_config['host'], selected_id):
                                st.success("✅ Đã xóa!")
                                if 'confirm_delete_id' in st.session_state:
                                    del st.session_state['confirm_delete_id']
                                time.sleep(1)
                                st.rerun()
                    with col_no:
                        if st.button("❌ Hủy", key="confirm_no"):
                            if 'confirm_delete_id' in st.session_state:
                                del st.session_state['confirm_delete_id']
                            st.rerun()
        else:
            st.info("ℹ️ Chưa có user nào.")
    
    # --- CHI TIẾT USER ---
    elif menu == "📋 Chi Tiết User":
        st.header(f"📋 Chi tiết User - {server_config['name']}")
        
        if inbounds:
            user_list = {f"{x['remark']} (Port {x['port']})": x['id'] for x in inbounds}
            selected = st.selectbox("Chọn user:", list(user_list.keys()))
            user_id = user_list[selected]
            user_data = next((x for x in inbounds if x['id'] == user_id), None)
            
            if user_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📛 User", user_data['remark'])
                    st.metric("🔌 Port", user_data['port'])
                with col2:
                    st.metric("🔧 Protocol", user_data['protocol'].upper())
                    status = "✅ Hoạt động" if user_data['enable'] else "❌ Tắt"
                    st.metric("Status", status)
                with col3:
                    exp_date = datetime.fromtimestamp(user_data['expiryTime']/1000).strftime('%d/%m/%Y') if user_data['expiryTime'] > 0 else "Vĩnh viễn"
                    st.metric("Hết hạn", exp_date)
                    gb_used = (user_data['up'] + user_data['down']) / (1024**3)
                    st.metric("Data đã dùng", f"{gb_used:.2f} GB")
                
                st.write("---")
                st.subheader("📱 Link kết nối")
                link = generate_link(user_data, vps_ip)
                col_link, col_qr = st.columns([2, 1])
                with col_link:
                    st.text_area("Link:", link, height=150)
                with col_qr:
                    qr_img = generate_qr(link)
                    if qr_img:
                        st.image(qr_img, width=250)
        else:
            st.info("ℹ️ Chưa có user.")
    
    # --- HỆ THỐNG ---
    elif menu == "⚙️ Hệ Thống":
        st.header(f"⚙️ Hệ thống - {server_config['name']}")
        
        tab1, tab2 = st.tabs(["💾 Backup", "📊 Thống kê"])
        
        with tab1:
            if st.button("📥 Backup dữ liệu", type="primary"):
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'server': server_config['name'],
                    'inbounds': inbounds
                }
                backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)
                st.download_button(
                    "💾 Download JSON",
                    backup_json,
                    f"backup_{server_config['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
        
        with tab2:
            st.subheader("📊 Thống kê")
            if inbounds:
                # Protocol stats
                proto_stats = {}
                for item in inbounds:
                    proto = item['protocol']
                    if proto not in proto_stats:
                        proto_stats[proto] = {'count': 0, 'traffic': 0}
                    proto_stats[proto]['count'] += 1
                    proto_stats[proto]['traffic'] += (item['up'] + item['down']) / (1024**3)
                
                for proto, data in proto_stats.items():
                    st.write(f"**{proto.upper()}:** {data['count']} user, {data['traffic']:.2f} GB")

st.write("---")
st.caption("© 2024 VPN Admin Pro - Multi-Server Edition v2.0 Fixed")
