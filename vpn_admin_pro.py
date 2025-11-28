import streamlit as st
import requests
import json
import time
import uuid
import random
import pandas as pd
import socket
import qrcode
from io import BytesIO
import psutil
from PIL import Image
import base64
from datetime import datetime, timedelta

# --- CẤU HÌNH HỆ THỐNG ---
HOST = "http://74.81.55.39:8001"  # Thay IP:Port của bạn
USERNAME = "admin"
PASSWORD = "password"             # Thay Mật khẩu của bạn

# --- HÀM HỖ TRỢ HỆ THỐNG ---
def get_public_ip():
    try:
        return HOST.split("//")[-1].split(":")[0]
    except:
        return "127.0.0.1"

VPS_IP = get_public_ip()

def get_system_stats():
    # Lấy thông tin CPU và RAM của VPS
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

def generate_qr(data):
    # Tạo ảnh QR Code từ text
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    return buf.getvalue()

def generate_link(inbound):
    """Tạo link kết nối từ thông tin inbound"""
    try:
        settings = json.loads(inbound['settings'])
        protocol = inbound['protocol']
        port = inbound['port']
        remark = inbound['remark']
        
        if protocol == 'vless':
            client_id = settings['clients'][0]['id']
            link = f"vless://{client_id}@{VPS_IP}:{port}?security=none&encryption=none&type=tcp&headerType=none#{remark}"
        elif protocol == 'vmess':
            client_id = settings['clients'][0]['id']
            vmess_json = {
                "v": "2",
                "ps": remark,
                "add": VPS_IP,
                "port": port,
                "id": client_id,
                "aid": "0",
                "net": "tcp",
                "type": "none",
                "host": "",
                "tls": ""
            }
            link = "vmess://" + base64.b64encode(json.dumps(vmess_json).encode()).decode()
        else:
            link = f"Không hỗ trợ protocol {protocol}"
        return link
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- HÀM TƯƠNG TÁC API ---
def get_session():
    session = requests.Session()
    try:
        login = session.post(f"{HOST}/login", data={"username": USERNAME, "password": PASSWORD}, timeout=5)
        if login.status_code == 200 and "success" in login.text.lower():
            return session
        return None
    except Exception as e:
        st.error(f"Lỗi kết nối: {str(e)}")
        return None

def get_inbounds(session):
    try:
        resp = session.post(f"{HOST}/xui/inbound/list")
        if resp.status_code == 200:
            return resp.json().get('obj', [])
        return []
    except:
        return []

def create_inbound(session, remark, days, protocol="vless", data_limit_gb=0):
    new_uuid = str(uuid.uuid4())
    new_port = random.randint(10000, 60000)
    expiry_time = int(time.time() * 1000) + (days * 86400 * 1000)
    
    # Giới hạn data (0 = unlimited)
    total_bytes = data_limit_gb * 1024 * 1024 * 1024 if data_limit_gb > 0 else 0
    
    # Cấu hình VLESS
    settings = {
        "clients": [{"id": new_uuid, "email": remark, "flow": ""}],
        "decryption": "none", "fallbacks": []
    }
    stream = {
        "network": "tcp", "security": "none",
        "tcpSettings": {"header": {"type": "none"}}
    }
    
    # Nếu chọn VMess
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
        resp = session.post(f"{HOST}/xui/inbound/add", data=payload)
        if resp.status_code == 200 and "success" in resp.text.lower():
            return {"uuid": new_uuid, "port": new_port, "protocol": protocol}, "OK"
        return None, resp.text
    except Exception as e:
        return None, str(e)

def delete_inbound(session, inbound_id):
    try:
        resp = session.post(f"{HOST}/xui/inbound/del/{inbound_id}")
        return resp.status_code == 200
    except:
        return False

def update_inbound(session, inbound_id, inbound_data):
    """Cập nhật thông tin inbound"""
    try:
        resp = session.post(f"{HOST}/xui/inbound/update/{inbound_id}", data=inbound_data)
        return resp.status_code == 200 and "success" in resp.text.lower()
    except:
        return False

def toggle_inbound(session, inbound_id, enable):
    """Bật/Tắt inbound"""
    try:
        # Lấy thông tin inbound hiện tại
        inbounds = get_inbounds(session)
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        
        target['enable'] = enable
        return update_inbound(session, inbound_id, target)
    except:
        return False

def reset_traffic(session, inbound_id):
    """Reset lưu lượng về 0"""
    try:
        inbounds = get_inbounds(session)
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        
        target['up'] = 0
        target['down'] = 0
        return update_inbound(session, inbound_id, target)
    except:
        return False

def extend_expiry(session, inbound_id, additional_days):
    """Gia hạn thêm ngày"""
    try:
        inbounds = get_inbounds(session)
        target = next((x for x in inbounds if x['id'] == inbound_id), None)
        if not target:
            return False
        
        current_expiry = target['expiryTime']
        # Nếu đã hết hạn, tính từ hiện tại
        if current_expiry < int(time.time() * 1000):
            new_expiry = int(time.time() * 1000) + (additional_days * 86400 * 1000)
        else:
            new_expiry = current_expiry + (additional_days * 86400 * 1000)
        
        target['expiryTime'] = new_expiry
        return update_inbound(session, inbound_id, target)
    except:
        return False

def backup_config(session):
    """Tạo backup cấu hình"""
    try:
        inbounds = get_inbounds(session)
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'inbounds': inbounds
        }
        return json.dumps(backup_data, indent=2)
    except:
        return None

# --- GIAO DIỆN CHÍNH (STREAMLIT) ---
st.set_page_config(page_title="VPN Admin Pro", page_icon="🛡️", layout="wide")

# CSS tùy chỉnh để làm đẹp giao diện
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b;}
    div[data-testid="stMetricValue"] {font-size: 24px;}
    .stButton>button {border-radius: 8px; font-weight: 600;}
    .success-box {background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;}
    .warning-box {background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;}
</style>
""", unsafe_allow_html=True)

# SIDEBAR MENU
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9664/9664780.png", width=100)
    st.title("Admin Console")
    menu = st.radio("Menu", ["📊 Dashboard", "➕ Tạo Gói Mới", "👥 Quản Lý User", "📋 Chi Tiết User", "⚙️ Hệ Thống"])
    st.write("---")
    st.caption(f"🌐 Server: {VPS_IP}")
    
    # Hiển thị thời gian
    st.caption(f"🕒 {datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}")
    
    # Nút làm mới
    if st.button("🔄 Làm mới", use_container_width=True):
        st.rerun()

session = get_session()
if not session:
    st.error("❌ Mất kết nối tới Panel! Kiểm tra lại HOST, USERNAME, PASSWORD.")
    st.stop()

inbounds = get_inbounds(session)

# --- 1. DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("📊 Tổng quan hệ thống")
    
    # Tính toán số liệu
    total_users = len(inbounds)
    total_traffic = sum([x['up'] + x['down'] for x in inbounds]) / (1024**3) # GB
    active_users = len([x for x in inbounds if x['enable']])
    expired_users = len([x for x in inbounds if x['expiryTime'] > 0 and x['expiryTime'] < int(time.time() * 1000)])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Tổng User", f"{total_users}", delta="Người dùng")
    col2.metric("✅ Đang Hoạt Động", f"{active_users}", delta="Online")
    col3.metric("📊 Tổng Lưu Lượng", f"{total_traffic:.2f} GB", delta="Download + Upload")
    col4.metric("⚠️ Đã Hết Hạn", f"{expired_users}", delta_color="inverse")
    
    st.write("---")
    
    # Tài nguyên VPS
    stats = get_system_stats()
    st.subheader("🖥️ Tài nguyên Server")
    
    col_cpu, col_ram, col_disk = st.columns(3)
    
    with col_cpu:
        st.metric("CPU Usage", f"{stats['cpu']:.1f}%")
        st.progress(min(stats['cpu'] / 100, 1.0))
    
    with col_ram:
        st.metric("RAM Usage", f"{stats['ram_percent']:.1f}%", delta=f"{stats['ram_used']:.1f}/{stats['ram_total']:.1f} GB")
        st.progress(stats['ram_percent'] / 100)
    
    with col_disk:
        st.metric("Disk Usage", f"{stats['disk_percent']:.1f}%", delta=f"{stats['disk_used']:.1f}/{stats['disk_total']:.1f} GB")
        st.progress(stats['disk_percent'] / 100)
    
    st.write("---")
    
    # Biểu đồ
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if total_users > 0:
            st.subheader("📈 Phân bổ giao thức")
            proto_counts = pd.DataFrame(inbounds)['protocol'].value_counts()
            st.bar_chart(proto_counts)
    
    with col_chart2:
        if total_users > 0:
            st.subheader("🔝 Top 5 User tiêu thụ data")
            top_data = sorted(inbounds, key=lambda x: x['up'] + x['down'], reverse=True)[:5]
            top_df = pd.DataFrame([{
                'User': x['remark'],
                'Data (GB)': (x['up'] + x['down']) / (1024**3)
            } for x in top_data])
            st.dataframe(top_df, use_container_width=True, hide_index=True)

# --- 2. TẠO GÓI MỚI ---
elif menu == "➕ Tạo Gói Mới":
    st.header("🚀 Khởi tạo dịch vụ VPN")
    
    tab1, tab2 = st.tabs(["➕ Tạo User Đơn", "📦 Tạo Hàng Loạt"])
    
    with tab1:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                remark = st.text_input("Tên khách hàng / Email", placeholder="ví dụ: khach_vip_01")
                protocol = st.selectbox("Giao thức", ["vless", "vmess"])
            with col2:
                days = st.slider("Thời hạn (Ngày)", 1, 365, 30)
                data_limit = st.number_input("Giới hạn Data (GB, 0 = Unlimited)", min_value=0, value=0, step=10)
                
            st.info(f"📅 Hết hạn vào: {(datetime.now() + timedelta(days=days)).strftime('%d/%m/%Y %H:%M')}")
                
            if st.button("✨ Kích Hoạt Ngay", type="primary", use_container_width=True):
                if not remark:
                    st.warning("⚠️ Vui lòng nhập tên khách hàng")
                else:
                    with st.spinner("Đang kết nối API..."):
                        res, msg = create_inbound(session, remark, days, protocol, data_limit)
                    
                    if res:
                        st.balloons()
                        st.success(f"✅ Đã tạo thành công cổng {res['port']}!")
                        
                        # Tạo Link
                        if res['protocol'] == 'vless':
                            link = f"vless://{res['uuid']}@{VPS_IP}:{res['port']}?security=none&encryption=none&type=tcp&headerType=none#{remark}"
                        else:
                            vmess_json = {"v": "2", "ps": remark, "add": VPS_IP, "port": res['port'], "id": res['uuid'], "aid": "0", "net": "tcp", "type": "none", "host": "", "tls": ""}
                            link = "vmess://" + base64.b64encode(json.dumps(vmess_json).encode()).decode()

                        # Hiển thị Link và QR Code
                        st.subheader("📱 Thông tin kết nối")
                        c_res1, c_res2 = st.columns([3, 1])
                        with c_res1:
                            st.text_area("Sao chép liên kết:", link, height=100)
                            st.code(f"UUID: {res['uuid']}", language="text")
                            st.code(f"Port: {res['port']}", language="text")
                        with c_res2:
                            st.image(generate_qr(link), caption="Quét mã QR", width=200)
                    else:
                        st.error(f"❌ Lỗi: {msg}")
    
    with tab2:
        st.subheader("📦 Tạo nhiều User cùng lúc")
        with st.container(border=True):
            prefix = st.text_input("Tiền tố tên user", placeholder="ví dụ: user")
            num_users = st.number_input("Số lượng user", min_value=1, max_value=50, value=5)
            bulk_protocol = st.selectbox("Giao thức", ["vless", "vmess"], key="bulk_proto")
            bulk_days = st.slider("Thời hạn (Ngày)", 1, 365, 30, key="bulk_days")
            bulk_data = st.number_input("Giới hạn Data (GB, 0 = Unlimited)", min_value=0, value=0, step=10, key="bulk_data")
            
            if st.button("🚀 Tạo Hàng Loạt", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                results = []
                
                for i in range(num_users):
                    user_name = f"{prefix}_{i+1:03d}"
                    status_text.text(f"Đang tạo {i+1}/{num_users}: {user_name}")
                    
                    res, msg = create_inbound(session, user_name, bulk_days, bulk_protocol, bulk_data)
                    if res:
                        results.append({'User': user_name, 'Port': res['port'], 'Status': '✅ OK'})
                    else:
                        results.append({'User': user_name, 'Port': 'N/A', 'Status': f'❌ {msg[:30]}'})
                    
                    progress_bar.progress((i + 1) / num_users)
                    time.sleep(0.5)
                
                st.success(f"✅ Hoàn thành! Đã tạo {len([r for r in results if '✅' in r['Status']])}/{num_users} user")
                st.dataframe(pd.DataFrame(results), use_container_width=True)

# --- 3. QUẢN LÝ USER ---
elif menu == "👥 Quản Lý User":
    st.header("📋 Danh sách khách hàng")
    
    # Ô tìm kiếm và filter
    col_search, col_filter, col_sort = st.columns([2, 1, 1])
    with col_search:
        search = st.text_input("🔍 Tìm kiếm user...", placeholder="Nhập tên hoặc port...")
    with col_filter:
        filter_status = st.selectbox("Trạng thái", ["Tất cả", "Đang hoạt động", "Đã tắt", "Hết hạn"])
    with col_sort:
        sort_by = st.selectbox("Sắp xếp", ["Mới nhất", "Tên A-Z", "Data nhiều nhất"])
    
    if inbounds:
        filtered_data = []
        for item in inbounds:
            # Filter tìm kiếm
            if search and (search.lower() not in item['remark'].lower() and search not in str(item['port'])):
                continue
            
            # Filter trạng thái
            is_expired = item['expiryTime'] > 0 and item['expiryTime'] < int(time.time() * 1000)
            if filter_status == "Đang hoạt động" and not item['enable']:
                continue
            if filter_status == "Đã tắt" and item['enable']:
                continue
            if filter_status == "Hết hạn" and not is_expired:
                continue
            
            gb_used = (item['up'] + item['down']) / (1024**3)
            exp_date = datetime.fromtimestamp(item['expiryTime']/1000).strftime('%d/%m/%Y %H:%M') if item['expiryTime'] > 0 else "Vĩnh viễn"
            
            status_emoji = "✅" if item['enable'] else "❌"
            if is_expired:
                status_emoji = "⚠️"
            
            filtered_data.append({
                "ID": item['id'],
                "Status": status_emoji,
                "User": item['remark'],
                "Port": item['port'],
                "Type": item['protocol'].upper(),
                "Data (GB)": round(gb_used, 2),
                "Hết hạn": exp_date,
                "Enable": item['enable']
            })
        
        # Sắp xếp
        if sort_by == "Tên A-Z":
            filtered_data.sort(key=lambda x: x['User'])
        elif sort_by == "Data nhiều nhất":
            filtered_data.sort(key=lambda x: x['Data (GB)'], reverse=True)
        else:  # Mới nhất
            filtered_data.reverse()
        
        df = pd.DataFrame(filtered_data)
        
        st.info(f"📊 Hiển thị {len(filtered_data)} / {len(inbounds)} user")
        
        # Hiển thị bảng
        st.dataframe(
            df.drop(columns=['ID', 'Enable']), 
            use_container_width=True,
            column_config={
                "Data (GB)": st.column_config.ProgressColumn("Data (GB)", format="%.2f GB", min_value=0, max_value=100)
            },
            hide_index=True
        )
        
        st.write("---")
        
        # Khu vực hành động
        st.subheader("⚡ Hành động nhanh")
        
        if filtered_data:
            user_dict = {f"{x['User']} (Port {x['Port']})": x['ID'] for x in filtered_data}
            selected_user = st.selectbox("Chọn user để thao tác:", list(user_dict.keys()))
            selected_id = user_dict[selected_user]
            
            col_act1, col_act2, col_act3, col_act4, col_act5 = st.columns(5)
            
            with col_act1:
                if st.button("🔄 Reset Traffic", use_container_width=True):
                    if reset_traffic(session, selected_id):
                        st.success("✅ Đã reset traffic!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Reset thất bại")
            
            with col_act2:
                if st.button("⏱️ Gia hạn +30d", use_container_width=True):
                    if extend_expiry(session, selected_id, 30):
                        st.success("✅ Đã gia hạn thêm 30 ngày!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Gia hạn thất bại")
            
            with col_act3:
                current_item = next((x for x in inbounds if x['id'] == selected_id), None)
                if current_item:
                    action_text = "⏸️ Tắt" if current_item['enable'] else "▶️ Bật"
                    if st.button(action_text, use_container_width=True):
                        if toggle_inbound(session, selected_id, not current_item['enable']):
                            st.success(f"✅ Đã {'tắt' if current_item['enable'] else 'bật'} user!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Thao tác thất bại")
            
            with col_act4:
                if st.button("📋 Xem Link", use_container_width=True):
                    current_item = next((x for x in inbounds if x['id'] == selected_id), None)
                    if current_item:
                        st.session_state['view_link_user'] = current_item
            
            with col_act5:
                if st.button("🗑️ Xóa", use_container_width=True, type="primary"):
                    st.session_state['confirm_delete_id'] = selected_id
        
        # Hiển thị link nếu được yêu cầu
        if 'view_link_user' in st.session_state:
            with st.container(border=True):
                st.subheader("📱 Thông tin kết nối")
                user_data = st.session_state['view_link_user']
                link = generate_link(user_data)
                
                col_link, col_qr = st.columns([3, 1])
                with col_link:
                    st.text_area("Link kết nối:", link, height=100, key="user_link_display")
                with col_qr:
                    st.image(generate_qr(link), caption="QR Code", width=200)
                
                if st.button("❌ Đóng"):
                    del st.session_state['view_link_user']
                    st.rerun()
        
        # Xác nhận xóa
        if 'confirm_delete_id' in st.session_state:
            with st.container(border=True):
                st.warning("⚠️ Bạn có chắc chắn muốn xóa user này? Hành động không thể hoàn tác!")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Xác nhận xóa", type="primary", use_container_width=True):
                        if delete_inbound(session, st.session_state['confirm_delete_id']):
                            st.success("✅ Đã xóa user!")
                            del st.session_state['confirm_delete_id']
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Xóa thất bại")
                with col_no:
                    if st.button("❌ Hủy", use_container_width=True):
                        del st.session_state['confirm_delete_id']
                        st.rerun()
    else:
        st.info("ℹ️ Chưa có user nào trong hệ thống.")

# --- 4. CHI TIẾT USER ---
elif menu == "📋 Chi Tiết User":
    st.header("🔍 Xem chi tiết User")
    
    if inbounds:
        user_list = {f"{x['remark']} (Port {x['port']})": x['id'] for x in inbounds}
        selected = st.selectbox("Chọn user:", list(user_list.keys()))
        
        if selected:
            user_id = user_list[selected]
            user_data = next((x for x in inbounds if x['id'] == user_id), None)
            
            if user_data:
                st.write("---")
                
                # Thông tin cơ bản
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📛 Tên User", user_data['remark'])
                    st.metric("🔌 Port", user_data['port'])
                with col2:
                    st.metric("🔧 Protocol", user_data['protocol'].upper())
                    status = "✅ Đang hoạt động" if user_data['enable'] else "❌ Đã tắt"
                    st.metric("🔋 Trạng thái", status)
                with col3:
                    exp_date = datetime.fromtimestamp(user_data['expiryTime']/1000).strftime('%d/%m/%Y %H:%M') if user_data['expiryTime'] > 0 else "Vĩnh viễn"
                    st.metric("📅 Hết hạn", exp_date)
                    
                    gb_used = (user_data['up'] + user_data['down']) / (1024**3)
                    st.metric("📊 Data đã dùng", f"{gb_used:.2f} GB")
                
                st.write("---")
                
                # Lưu lượng chi tiết
                st.subheader("📈 Chi tiết lưu lượng")
                col_up, col_down, col_total = st.columns(3)
                with col_up:
                    st.metric("⬆️ Upload", f"{user_data['up'] / (1024**3):.2f} GB")
                with col_down:
                    st.metric("⬇️ Download", f"{user_data['down'] / (1024**3):.2f} GB")
                with col_total:
                    total_limit = user_data.get('total', 0)
                    if total_limit > 0:
                        st.metric("📦 Giới hạn", f"{total_limit / (1024**3):.2f} GB")
                    else:
                        st.metric("📦 Giới hạn", "Không giới hạn")
                
                st.write("---")
                
                # Cấu hình kỹ thuật
                st.subheader("⚙️ Cấu hình kỹ thuật")
                
                try:
                    settings = json.loads(user_data['settings'])
                    stream_settings = json.loads(user_data['streamSettings'])
                    
                    with st.expander("🔑 UUID / Client ID"):
                        if user_data['protocol'] == 'vless':
                            client_id = settings['clients'][0]['id']
                        else:
                            client_id = settings['clients'][0]['id']
                        st.code(client_id, language="text")
                    
                    with st.expander("📡 Stream Settings"):
                        st.json(stream_settings)
                    
                    with st.expander("🔧 Full Settings"):
                        st.json(settings)
                    
                except Exception as e:
                    st.error(f"Lỗi hiển thị cấu hình: {str(e)}")
                
                st.write("---")
                
                # Link và QR Code
                st.subheader("📱 Link kết nối")
                link = generate_link(user_data)
                col_link, col_qr = st.columns([2, 1])
                with col_link:
                    st.text_area("Sao chép link:", link, height=150)
                    if st.button("📋 Copy to Clipboard"):
                        st.info("Sử dụng nút copy bên cạnh text area")
                with col_qr:
                    st.image(generate_qr(link), caption="QR Code", width=250)
    else:
        st.info("ℹ️ Chưa có user nào.")

# --- 5. HỆ THỐNG ---
elif menu == "⚙️ Hệ Thống":
    st.header("⚙️ Cài đặt & Quản lý hệ thống")
    
    tab1, tab2, tab3 = st.tabs(["💾 Backup & Restore", "📊 Thống kê", "🔧 Cấu hình"])
    
    with tab1:
        st.subheader("💾 Sao lưu dữ liệu")
        
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            if st.button("📥 Tải xuống Backup", use_container_width=True, type="primary"):
                backup_data = backup_config(session)
                if backup_data:
                    st.download_button(
                        label="💾 Download JSON File",
                        data=backup_data,
                        file_name=f"vpn_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    st.success("✅ Backup đã sẵn sàng tải xuống!")
                else:
                    st.error("❌ Không thể tạo backup")
        
        with col_backup2:
            st.info("📋 Backup bao gồm:\n- Tất cả cấu hình user\n- Thông tin port và protocol\n- Thiết lập traffic\n- Thời hạn và trạng thái")
        
        st.write("---")
        
        st.subheader("📤 Khôi phục dữ liệu")
        uploaded_file = st.file_uploader("Chọn file backup (.json)", type=['json'])
        if uploaded_file:
            try:
                backup_content = json.loads(uploaded_file.read())
                st.json(backup_content)
                st.warning("⚠️ Chức năng restore đang phát triển. Hiện tại chỉ xem được nội dung backup.")
            except Exception as e:
                st.error(f"Lỗi đọc file: {str(e)}")
    
    with tab2:
        st.subheader("📊 Thống kê chi tiết")
        
        if inbounds:
            # Thống kê theo protocol
            proto_stats = {}
            for item in inbounds:
                proto = item['protocol']
                if proto not in proto_stats:
                    proto_stats[proto] = {'count': 0, 'traffic': 0}
                proto_stats[proto]['count'] += 1
                proto_stats[proto]['traffic'] += (item['up'] + item['down']) / (1024**3)
            
            st.write("**📡 Thống kê theo Protocol:**")
            for proto, data in proto_stats.items():
                col1, col2, col3 = st.columns(3)
                col1.metric("Protocol", proto.upper())
                col2.metric("Số User", data['count'])
                col3.metric("Tổng Traffic", f"{data['traffic']:.2f} GB")
                st.write("---")
            
            # Thống kê theo trạng thái
            enabled_count = len([x for x in inbounds if x['enable']])
            disabled_count = len(inbounds) - enabled_count
            expired_count = len([x for x in inbounds if x['expiryTime'] > 0 and x['expiryTime'] < int(time.time() * 1000)])
            
            st.write("**🔋 Thống kê trạng thái:**")
            status_df = pd.DataFrame([
                {'Trạng thái': '✅ Đang hoạt động', 'Số lượng': enabled_count},
                {'Trạng thái': '❌ Đã tắt', 'Số lượng': disabled_count},
                {'Trạng thái': '⚠️ Hết hạn', 'Số lượng': expired_count}
            ])
            st.dataframe(status_df, use_container_width=True, hide_index=True)
            
            # User sắp hết hạn
            st.write("**⏰ User sắp hết hạn (trong 7 ngày):**")
            next_week = int(time.time() * 1000) + (7 * 86400 * 1000)
            expiring_soon = [x for x in inbounds if 0 < x['expiryTime'] < next_week and x['expiryTime'] > int(time.time() * 1000)]
            
            if expiring_soon:
                expiring_df = pd.DataFrame([{
                    'User': x['remark'],
                    'Port': x['port'],
                    'Hết hạn': datetime.fromtimestamp(x['expiryTime']/1000).strftime('%d/%m/%Y'),
                    'Còn lại': f"{((x['expiryTime'] - int(time.time() * 1000)) / (86400 * 1000)):.1f} ngày"
                } for x in expiring_soon])
                st.dataframe(expiring_df, use_container_width=True, hide_index=True)
            else:
                st.info("✅ Không có user nào sắp hết hạn")
        else:
            st.info("ℹ️ Chưa có dữ liệu để thống kê")
    
    with tab3:
        st.subheader("🔧 Cấu hình ứng dụng")
        
        with st.container(border=True):
            st.write("**📡 Thông tin kết nối Panel:**")
            st.code(f"HOST: {HOST}", language="text")
            st.code(f"USERNAME: {USERNAME}", language="text")
            st.code(f"VPS IP: {VPS_IP}", language="text")
            st.caption("⚠️ Để thay đổi, chỉnh sửa trong source code")
        
        st.write("---")
        
        col_sys1, col_sys2 = st.columns(2)
        with col_sys1:
            if st.button("🔄 Làm mới Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Đã xóa cache!")
                time.sleep(1)
                st.rerun()
        
        with col_sys2:
            if st.button("🔌 Test Connection", use_container_width=True):
                test_session = get_session()
                if test_session:
                    st.success("✅ Kết nối thành công!")
                else:
                    st.error("❌ Không thể kết nối!")
        
        st.write("---")
        
        st.subheader("ℹ️ Thông tin phiên bản")
        st.info("""
        **VPN Admin Pro v2.0**
        - ✅ Dashboard với thống kê real-time
        - ✅ Tạo user đơn và hàng loạt
        - ✅ Quản lý user: Bật/Tắt, Reset traffic, Gia hạn
        - ✅ Export link và QR code
        - ✅ Backup/Restore cấu hình
        - ✅ Thống kê chi tiết
        - ✅ Xem chi tiết user
        
        Phát triển bởi: Admin Team
        """)

# Footer
st.write("---")
st.caption("© 2024 VPN Admin Pro - Powered by Streamlit & 3X-UI API")
