#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VLESS Config Manager v1.0
Quản lý config VLESS hoàn chỉnh - Không phụ thuộc 3X-UI
"""

import streamlit as st
import json
import uuid
import base64
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
import pandas as pd
from urllib.parse import quote, urlencode

# --- CONFIG STORAGE ---
CONFIG_FILE = "vless_configs.json"

def load_configs():
    """Load configs từ file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_configs(configs):
    """Save configs to file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Lỗi lưu: {e}")
        return False

# --- VLESS LINK GENERATOR ---
def generate_vless_link(config):
    """Generate VLESS link từ config"""
    try:
        uuid_val = config['uuid']
        remark = config['remark']
        server = config['server']
        port = config['port']
        
        # Base params
        params = {
            'security': config.get('security', 'none'),
            'type': config.get('network', 'tcp'),
            'encryption': config.get('encryption', 'none')
        }
        
        # Network specific params
        network = config.get('network', 'tcp')
        
        if network == 'ws':
            params['path'] = config.get('ws_path', '/')
            if config.get('ws_host'):
                params['host'] = config['ws_host']
        
        elif network == 'grpc':
            params['serviceName'] = config.get('grpc_service', '')
            params['mode'] = config.get('grpc_mode', 'gun')
        
        elif network == 'http' or network == 'h2':
            params['path'] = config.get('http_path', '/')
            if config.get('http_host'):
                params['host'] = config['http_host']
        
        elif network == 'tcp':
            if config.get('tcp_header_type'):
                params['headerType'] = config['tcp_header_type']
        
        # TLS params
        if config.get('security') == 'tls':
            if config.get('tls_sni'):
                params['sni'] = config['tls_sni']
            if config.get('tls_alpn'):
                params['alpn'] = config['tls_alpn']
            if config.get('tls_fingerprint'):
                params['fp'] = config['tls_fingerprint']
        
        # Flow for XTLS
        if config.get('flow'):
            params['flow'] = config['flow']
        
        # Build query string
        query = urlencode(params)
        
        # Build link
        link = f"vless://{uuid_val}@{server}:{port}?{query}#{quote(remark)}"
        
        return link
    except Exception as e:
        return f"Error: {e}"

# --- QR CODE GENERATOR ---
def generate_qr(link):
    """Generate QR code"""
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        st.error(f"QR error: {e}")
        return None

# --- CONFIG TEMPLATES ---
TEMPLATES = {
    "VLESS + TCP + REALITY": {
        "network": "tcp",
        "security": "reality",
        "flow": "xtls-rprx-vision",
        "tcp_header_type": "none"
    },
    "VLESS + WebSocket + TLS": {
        "network": "ws",
        "security": "tls",
        "ws_path": "/",
        "ws_host": ""
    },
    "VLESS + WebSocket (No TLS)": {
        "network": "ws",
        "security": "none",
        "ws_path": "/"
    },
    "VLESS + gRPC + TLS": {
        "network": "grpc",
        "security": "tls",
        "grpc_service": "grpcService",
        "grpc_mode": "gun"
    },
    "VLESS + HTTP/2 + TLS": {
        "network": "http",
        "security": "tls",
        "http_path": "/"
    },
    "VLESS + TCP (Simple)": {
        "network": "tcp",
        "security": "none"
    }
}

# --- UI SETUP ---
st.set_page_config(
    page_title="VLESS Config Manager",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    .stApp {background: transparent;}
    .block-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(30,60,114,0.4);
    }
    h1 {
        color: #1e3c72 !important;
        text-align: center;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    h2, h3 {color: #2a5298 !important;}
    .config-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1e3c72;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f1f3f5;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        border: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white !important;
    }
    .stExpander {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🔐 VLESS Config Manager")
    st.markdown("**v1.0** - Standalone Manager")
    st.markdown("---")
    
    configs = load_configs()
    st.success(f"✅ **{len(configs)}** configs")
    
    st.markdown("---")
    
    menu = st.radio(
        "📋 Menu",
        [
            "➕ Tạo Config",
            "📋 Danh Sách Config",
            "📦 Templates",
            "💾 Backup/Restore",
            "📊 Statistics"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 12px;'>
    <p><b>Standalone Manager</b></p>
    <p>Không cần 3X-UI/Panel</p>
    <p>Quản lý config trực tiếp</p>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("🔐 VLESS Config Manager")
st.markdown("<p style='text-align: center; color: #666;'>Quản lý VLESS configs hoàn chỉnh - Standalone</p>", unsafe_allow_html=True)

# ==================== TẠO CONFIG ====================
if menu == "➕ Tạo Config":
    st.header("➕ Tạo Config Mới")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tab1, tab2, tab3 = st.tabs(["📝 Basic Info", "🌐 Network Config", "🔒 Security"])
        
        with tab1:
            st.subheader("📝 Thông Tin Cơ Bản")
            
            remark = st.text_input("📛 Tên Config *", placeholder="VD: Config-001")
            
            col_a, col_b = st.columns(2)
            with col_a:
                server = st.text_input("🌐 Server Address *", placeholder="example.com hoặc 1.2.3.4")
                port = st.number_input("🔌 Port *", min_value=1, max_value=65535, value=443)
            
            with col_b:
                auto_uuid = st.checkbox("🔄 Auto UUID", value=True)
                if auto_uuid:
                    uuid_val = str(uuid.uuid4())
                    st.code(uuid_val, language="text")
                else:
                    uuid_val = st.text_input("🔑 UUID", value=str(uuid.uuid4()))
            
            col_c, col_d = st.columns(2)
            with col_c:
                expiry_days = st.number_input("⏰ Thời hạn (ngày)", min_value=0, max_value=3650, value=30, help="0 = Không giới hạn")
            with col_d:
                data_limit_gb = st.number_input("💾 Data Limit (GB)", min_value=0, max_value=10000, value=0, help="0 = Unlimited")
        
        with tab2:
            st.subheader("🌐 Network Configuration")
            
            network = st.selectbox(
                "🔧 Network Type",
                ["tcp", "ws", "grpc", "http", "h2"],
                help="Transport protocol"
            )
            
            if network == "ws":
                st.markdown("### WebSocket Settings")
                ws_path = st.text_input("📂 Path", value="/", placeholder="/path")
                ws_host = st.text_input("🏠 Host (optional)", placeholder="example.com")
                
                st.info("""
                **WebSocket Tips:**
                - Path: Đường dẫn WebSocket (VD: `/vmess`, `/vless`)
                - Host: Domain cho Host header (optional)
                - Thường dùng kèm CDN (Cloudflare)
                """)
            
            elif network == "grpc":
                st.markdown("### gRPC Settings")
                grpc_service = st.text_input("📡 Service Name", value="grpcService", placeholder="serviceName")
                grpc_mode = st.selectbox("🔧 Mode", ["gun", "multi"], index=0)
                
                st.info("""
                **gRPC Tips:**
                - Service Name: Tên service gRPC
                - Mode: gun (recommended) hoặc multi
                - Performance tốt, ít bị chặn
                """)
            
            elif network in ["http", "h2"]:
                st.markdown("### HTTP/2 Settings")
                http_path = st.text_input("📂 Path", value="/", placeholder="/path")
                http_host = st.text_input("🏠 Host", placeholder="example.com")
                
                st.info("""
                **HTTP/2 Tips:**
                - Path: Đường dẫn HTTP
                - Host: Domain cho Host header
                - H2: HTTP/2 over TLS
                """)
            
            elif network == "tcp":
                st.markdown("### TCP Settings")
                tcp_header_type = st.selectbox("📋 Header Type", ["none", "http"], index=0)
                
                if tcp_header_type == "http":
                    tcp_path = st.text_input("📂 Path", value="/", placeholder="/")
                    tcp_host = st.text_input("🏠 Host", placeholder="example.com")
                
                st.info("""
                **TCP Tips:**
                - none: Direct TCP
                - http: TCP với HTTP header (camouflage)
                """)
        
        with tab3:
            st.subheader("🔒 Security Settings")
            
            security = st.selectbox(
                "🛡️ Security",
                ["none", "tls", "reality"],
                help="Encryption type"
            )
            
            if security == "tls":
                st.markdown("### TLS Settings")
                
                col_e, col_f = st.columns(2)
                with col_e:
                    tls_sni = st.text_input("📛 SNI", placeholder="example.com")
                    tls_alpn = st.text_input("🔤 ALPN", placeholder="h2,http/1.1")
                
                with col_f:
                    tls_fingerprint = st.selectbox("🖐️ Fingerprint", ["", "chrome", "firefox", "safari", "ios", "android", "edge", "random"])
                    tls_allow_insecure = st.checkbox("⚠️ Allow Insecure", value=False)
                
                st.info("""
                **TLS Tips:**
                - SNI: Server Name Indication (domain)
                - ALPN: Application-Layer Protocol Negotiation
                - Fingerprint: TLS fingerprint simulation
                """)
            
            elif security == "reality":
                st.markdown("### REALITY Settings")
                
                reality_public_key = st.text_input("🔑 Public Key", placeholder="public_key_here")
                reality_short_id = st.text_input("🆔 Short ID", placeholder="short_id")
                reality_spider_x = st.text_input("🕷️ Spider X", placeholder="/path")
                
                flow = st.selectbox("💫 Flow", ["xtls-rprx-vision", "xtls-rprx-vision-udp443"])
                
                st.info("""
                **REALITY Tips:**
                - REALITY = XTLS + Reality protocol
                - Rất khó bị phát hiện & chặn
                - Cần config server support REALITY
                """)
            
            else:
                st.info("**No TLS/Encryption** - Không mã hóa (chỉ dùng cho internal network)")
            
            # Flow for XTLS (even without reality)
            if security != "reality":
                use_flow = st.checkbox("💫 Enable Flow (XTLS)", value=False)
                if use_flow:
                    flow = st.selectbox("Flow Type", ["xtls-rprx-vision", "xtls-rprx-vision-udp443", "xtls-rprx-direct"])
                else:
                    flow = None
            
            # Encryption
            encryption = st.selectbox("🔐 Encryption", ["none"], index=0, help="VLESS chỉ support 'none'")
    
    with col2:
        st.subheader("📋 Template Quick Start")
        
        selected_template = st.selectbox(
            "🎨 Chọn Template",
            [""] + list(TEMPLATES.keys())
        )
        
        if selected_template:
            st.success(f"✅ Template: **{selected_template}**")
            template_data = TEMPLATES[selected_template]
            st.json(template_data)
            
            if st.button("🚀 Áp Dụng Template", use_container_width=True):
                st.info("Template sẽ được áp dụng khi tạo config!")
        
        st.markdown("---")
        st.subheader("💡 Quick Tips")
        st.info("""
        **Best Practices:**
        
        🌟 **Cho CDN (Cloudflare):**
        - WebSocket + TLS
        - Port 443
        - Path: /vmess
        
        🌟 **Cho Performance:**
        - gRPC + TLS
        - REALITY
        
        🌟 **Cho Stealth:**
        - REALITY
        - HTTP/2 + TLS
        
        🌟 **Cho Simple:**
        - TCP + TLS
        """)
    
    st.markdown("---")
    
    # CREATE BUTTON
    col_create1, col_create2, col_create3 = st.columns([1, 2, 1])
    
    with col_create2:
        if st.button("✨ TẠO CONFIG", use_container_width=True, type="primary"):
            if not all([remark, server, uuid_val]):
                st.error("❌ Vui lòng điền đầy đủ thông tin bắt buộc!")
            else:
                # Build config
                config = {
                    "id": str(uuid.uuid4()),
                    "remark": remark,
                    "server": server,
                    "port": port,
                    "uuid": uuid_val,
                    "network": network,
                    "security": security,
                    "encryption": encryption,
                    "created_at": datetime.now().isoformat(),
                    "expiry_date": (datetime.now() + timedelta(days=expiry_days)).isoformat() if expiry_days > 0 else None,
                    "data_limit_gb": data_limit_gb,
                    "used_data_gb": 0,
                    "enabled": True
                }
                
                # Add network-specific settings
                if network == "ws":
                    config["ws_path"] = ws_path
                    config["ws_host"] = ws_host
                
                elif network == "grpc":
                    config["grpc_service"] = grpc_service
                    config["grpc_mode"] = grpc_mode
                
                elif network in ["http", "h2"]:
                    config["http_path"] = http_path
                    config["http_host"] = http_host
                
                elif network == "tcp" and tcp_header_type != "none":
                    config["tcp_header_type"] = tcp_header_type
                    if tcp_header_type == "http":
                        config["tcp_path"] = tcp_path
                        config["tcp_host"] = tcp_host
                
                # Add security settings
                if security == "tls":
                    config["tls_sni"] = tls_sni
                    config["tls_alpn"] = tls_alpn
                    config["tls_fingerprint"] = tls_fingerprint
                    config["tls_allow_insecure"] = tls_allow_insecure
                
                elif security == "reality":
                    config["reality_public_key"] = reality_public_key
                    config["reality_short_id"] = reality_short_id
                    config["reality_spider_x"] = reality_spider_x
                    config["flow"] = flow
                
                # Add flow if enabled
                if 'flow' in locals() and flow:
                    config["flow"] = flow
                
                # Save
                configs = load_configs()
                configs.append(config)
                
                if save_configs(configs):
                    st.success("✅ Đã tạo config thành công!")
                    st.balloons()
                    
                    # Show link
                    link = generate_vless_link(config)
                    st.markdown("### 🔗 VLESS Link")
                    st.code(link, language="text")
                    
                    # Show QR
                    qr_buf = generate_qr(link)
                    if qr_buf:
                        st.image(qr_buf, width=300, caption="QR Code")
                    
                    st.info("💡 Config đã được lưu. Vào 'Danh Sách Config' để xem!")

# ==================== DANH SÁCH CONFIG ====================
elif menu == "📋 Danh Sách Config":
    st.header("📋 Danh Sách Config")
    
    configs = load_configs()
    
    if not configs:
        st.info("ℹ️ Chưa có config nào. Tạo config mới ở menu '➕ Tạo Config'!")
    else:
        # Search & Filter
        col_search1, col_search2, col_search3 = st.columns([2, 1, 1])
        
        with col_search1:
            search = st.text_input("🔍 Tìm kiếm", placeholder="Tên, server, UUID...")
        
        with col_search2:
            filter_network = st.selectbox("🌐 Network", ["All"] + ["tcp", "ws", "grpc", "http", "h2"])
        
        with col_search3:
            filter_security = st.selectbox("🔒 Security", ["All"] + ["none", "tls", "reality"])
        
        # Filter configs
        filtered_configs = configs
        
        if search:
            filtered_configs = [c for c in filtered_configs if 
                search.lower() in c.get('remark', '').lower() or
                search.lower() in c.get('server', '').lower() or
                search.lower() in c.get('uuid', '').lower()
            ]
        
        if filter_network != "All":
            filtered_configs = [c for c in filtered_configs if c.get('network') == filter_network]
        
        if filter_security != "All":
            filtered_configs = [c for c in filtered_configs if c.get('security') == filter_security]
        
        st.success(f"✅ Hiển thị **{len(filtered_configs)}** / {len(configs)} configs")
        
        # Bulk actions
        st.markdown("### 🗑️ Bulk Actions")
        col_bulk1, col_bulk2, col_bulk3 = st.columns([2, 1, 1])
        
        with col_bulk1:
            if 'selected_configs' not in st.session_state:
                st.session_state.selected_configs = []
            
            select_all = st.checkbox("☑️ Chọn tất cả")
            if select_all:
                st.session_state.selected_configs = [c['id'] for c in filtered_configs]
        
        with col_bulk2:
            if st.button("❌ Bỏ chọn"):
                st.session_state.selected_configs = []
                st.rerun()
        
        with col_bulk3:
            if st.button(f"🗑️ Xóa ({len(st.session_state.selected_configs)})", type="primary"):
                if st.session_state.selected_configs:
                    if st.checkbox("✅ Xác nhận xóa?"):
                        configs = [c for c in configs if c['id'] not in st.session_state.selected_configs]
                        save_configs(configs)
                        st.session_state.selected_configs = []
                        st.success("✅ Đã xóa!")
                        st.rerun()
        
        st.markdown("---")
        
        # Display configs
        for idx, config in enumerate(filtered_configs):
            # Calculate status
            expiry = config.get('expiry_date')
            if expiry:
                expiry_dt = datetime.fromisoformat(expiry)
                days_left = (expiry_dt - datetime.now()).days
                if days_left < 0:
                    status = "🔴 Expired"
                elif days_left < 7:
                    status = f"🟡 {days_left} days left"
                else:
                    status = f"🟢 {days_left} days left"
            else:
                status = "🟢 No limit"
            
            # Data usage
            used = config.get('used_data_gb', 0)
            limit = config.get('data_limit_gb', 0)
            if limit > 0:
                percent = (used / limit) * 100
                data_status = f"💾 {used:.2f}/{limit:.2f} GB ({percent:.1f}%)"
            else:
                data_status = f"💾 {used:.2f} GB (Unlimited)"
            
            with st.expander(f"**{idx+1}. {config['remark']}** - {status}", expanded=False):
                col_info, col_actions = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"""
**📛 Remark:** {config['remark']}  
**🌐 Server:** `{config['server']}:{config['port']}`  
**🔑 UUID:** `{config['uuid']}`  
**🔧 Network:** {config['network'].upper()}  
**🔒 Security:** {config['security'].upper()}  
**⏰ Expiry:** {status}  
**💾 Data:** {data_status}  
**📅 Created:** {config.get('created_at', 'N/A')[:10]}  
**🔘 Status:** {'🟢 Enabled' if config.get('enabled') else '🔴 Disabled'}
                    """)
                    
                    # Show link
                    link = generate_vless_link(config)
                    st.markdown("**🔗 VLESS Link:**")
                    st.code(link, language="text")
                    
                    # Show QR
                    if st.button(f"📱 Xem QR Code", key=f"qr_{config['id']}"):
                        qr_buf = generate_qr(link)
                        if qr_buf:
                            st.image(qr_buf, width=250)
                    
                    # Export options
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        if st.button(f"📄 Export JSON", key=f"json_{config['id']}"):
                            st.json(config)
                    
                    with col_exp2:
                        if st.button(f"📋 Copy Link", key=f"copy_{config['id']}"):
                            st.code(link)
                
                with col_actions:
                    # Checkbox for bulk
                    is_selected = config['id'] in st.session_state.selected_configs
                    if st.checkbox("☑️", value=is_selected, key=f"select_{config['id']}"):
                        if config['id'] not in st.session_state.selected_configs:
                            st.session_state.selected_configs.append(config['id'])
                    else:
                        if config['id'] in st.session_state.selected_configs:
                            st.session_state.selected_configs.remove(config['id'])
                    
                    st.markdown("---")
                    
                    # Toggle enable
                    if st.button("⏸️" if config.get('enabled') else "▶️", key=f"toggle_{config['id']}", use_container_width=True):
                        config['enabled'] = not config.get('enabled', True)
                        save_configs(configs)
                        st.rerun()
                    
                    # Delete
                    if st.button("🗑️", key=f"del_{config['id']}", use_container_width=True):
                        configs = [c for c in configs if c['id'] != config['id']]
                        save_configs(configs)
                        st.success("✅ Đã xóa!")
                        st.rerun()

# ==================== TEMPLATES ====================
elif menu == "📦 Templates":
    st.header("📦 Config Templates")
    
    st.info("""
    **Templates** là các cấu hình pre-defined để tạo config nhanh.
    Chọn template phù hợp với use case của bạn!
    """)
    
    for template_name, template_data in TEMPLATES.items():
        with st.expander(f"🎨 **{template_name}**", expanded=False):
            st.json(template_data)
            
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                st.markdown("**Use Case:**")
                if "REALITY" in template_name:
                    st.info("🌟 Best cho stealth & performance")
                elif "WebSocket + TLS" in template_name:
                    st.info("🌐 Best cho CDN (Cloudflare)")
                elif "gRPC" in template_name:
                    st.info("⚡ Best cho performance")
                elif "HTTP/2" in template_name:
                    st.info("🔒 Best cho security")
            
            with col_t2:
                if st.button(f"🚀 Dùng Template", key=f"use_{template_name}"):
                    st.success("✅ Vào 'Tạo Config' và chọn template này!")

# ==================== BACKUP/RESTORE ====================
elif menu == "💾 Backup/Restore":
    st.header("💾 Backup & Restore")
    
    tab1, tab2 = st.tabs(["📤 Backup", "📥 Restore"])
    
    with tab1:
        st.subheader("📤 Backup Configs")
        
        configs = load_configs()
        
        if not configs:
            st.info("ℹ️ Chưa có config để backup!")
        else:
            st.success(f"✅ Có **{len(configs)}** configs để backup")
            
            # Show backup data
            backup_data = json.dumps(configs, indent=2, ensure_ascii=False)
            
            st.markdown("### 📄 Backup Data")
            st.code(backup_data, language="json")
            
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                st.download_button(
                    label="💾 Download Backup (JSON)",
                    data=backup_data,
                    file_name=f"vless_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_b2:
                # Export as text links
                links = "\n\n".join([generate_vless_link(c) for c in configs])
                st.download_button(
                    label="📋 Download Links (TXT)",
                    data=links,
                    file_name=f"vless_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    with tab2:
        st.subheader("📥 Restore Configs")
        
        st.warning("⚠️ **Cảnh báo:** Restore sẽ OVERWRITE tất cả configs hiện tại!")
        
        restore_option = st.radio(
            "Chọn phương thức restore:",
            ["📄 Upload JSON File", "📋 Paste JSON Text"]
        )
        
        if restore_option == "📄 Upload JSON File":
            uploaded_file = st.file_uploader("Upload backup file", type=['json'])
            
            if uploaded_file:
                try:
                    restore_data = json.load(uploaded_file)
                    
                    st.success(f"✅ File hợp lệ! Có **{len(restore_data)}** configs")
                    st.json(restore_data)
                    
                    if st.button("🔄 RESTORE", type="primary"):
                        if st.checkbox("✅ Xác nhận restore (sẽ mất data hiện tại)?"):
                            save_configs(restore_data)
                            st.success("✅ Đã restore thành công!")
                            st.balloons()
                            st.rerun()
                
                except Exception as e:
                    st.error(f"❌ File không hợp lệ: {e}")
        
        else:
            restore_text = st.text_area("Paste JSON data", height=300)
            
            if restore_text:
                try:
                    restore_data = json.loads(restore_text)
                    
                    st.success(f"✅ Data hợp lệ! Có **{len(restore_data)}** configs")
                    
                    if st.button("🔄 RESTORE", type="primary"):
                        if st.checkbox("✅ Xác nhận restore (sẽ mất data hiện tại)?"):
                            save_configs(restore_data)
                            st.success("✅ Đã restore thành công!")
                            st.balloons()
                            st.rerun()
                
                except Exception as e:
                    st.error(f"❌ JSON không hợp lệ: {e}")

# ==================== STATISTICS ====================
elif menu == "📊 Statistics":
    st.header("📊 Statistics")
    
    configs = load_configs()
    
    if not configs:
        st.info("ℹ️ Chưa có config nào!")
    else:
        # Overview
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("📊 Total Configs", len(configs))
        
        with col_stat2:
            enabled = sum(1 for c in configs if c.get('enabled', True))
            st.metric("🟢 Enabled", enabled)
        
        with col_stat3:
            expired = sum(1 for c in configs if c.get('expiry_date') and datetime.fromisoformat(c['expiry_date']) < datetime.now())
            st.metric("🔴 Expired", expired)
        
        with col_stat4:
            total_data = sum(c.get('used_data_gb', 0) for c in configs)
            st.metric("💾 Total Data Used", f"{total_data:.2f} GB")
        
        st.markdown("---")
        
        # Network distribution
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 🌐 Network Types")
            network_counts = {}
            for c in configs:
                net = c.get('network', 'unknown')
                network_counts[net] = network_counts.get(net, 0) + 1
            
            df_network = pd.DataFrame(list(network_counts.items()), columns=['Network', 'Count'])
            st.bar_chart(df_network.set_index('Network'))
        
        with col_chart2:
            st.markdown("### 🔒 Security Types")
            security_counts = {}
            for c in configs:
                sec = c.get('security', 'unknown')
                security_counts[sec] = security_counts.get(sec, 0) + 1
            
            df_security = pd.DataFrame(list(security_counts.items()), columns=['Security', 'Count'])
            st.bar_chart(df_security.set_index('Security'))
        
        st.markdown("---")
        
        # Recent configs
        st.markdown("### 🕒 Recent Configs (Last 5)")
        recent = sorted(configs, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        
        for config in recent:
            st.markdown(f"- **{config['remark']}** - {config.get('network')} / {config.get('security')} - {config.get('created_at', 'N/A')[:10]}")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<p>© 2024 VLESS Config Manager v1.0</p>
<p><b>Standalone - Không cần Panel</b></p>
<p>🔐 Quản lý config trực tiếp</p>
</div>
""", unsafe_allow_html=True)
