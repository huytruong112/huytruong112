#!/usr/bin/env python3
"""
Admin Panel for vless Configuration Management and VPS Monitoring
Complete dashboard with all features for managing VPN service
"""

import os
import json
import time
import psutil
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
import speedtest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vpnvietnam_secret_key_2025')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

# Configuration
XRAY_PANEL_URL = os.environ.get('XRAY_PANEL_URL', 'http://74.81.55.39:8001')
XRAY_ADMIN_EMAIL = os.environ.get('XRAY_ADMIN_EMAIL', 'admin@vpnvietnam.com')
XRAY_ADMIN_PASSWORD = os.environ.get('XRAY_ADMIN_PASSWORD', 'Vpnvietnam123@!')

# Global variables for caching
system_stats_cache = {}
speed_test_cache = {}
cache_lock = threading.Lock()

# ==================== AUTHENTICATION ====================

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== 3X-UI API CLIENT ====================

class XrayPanelAPI:
    """Client for interacting with 3X-UI panel API"""
    
    def __init__(self, base_url, email, password):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session_cookie = None
        
    def login(self):
        """Login to 3X-UI panel"""
        try:
            url = f"{self.base_url}/login"
            data = {
                'username': self.email,
                'password': self.password
            }
            response = self.session.post(url, data=data, timeout=10)
            
            if response.status_code == 200 and response.json().get('success'):
                self.session_cookie = self.session.cookies.get_dict()
                logger.info("Successfully logged in to 3X-UI panel")
                return True
            else:
                logger.error(f"Login failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def get_inbounds(self):
        """Get all inbound configurations"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/panel/api/inbounds/list"
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj', [])
            return []
        except Exception as e:
            logger.error(f"Error getting inbounds: {e}")
            return []
    
    def add_inbound(self, config):
        """Add new inbound configuration"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/panel/api/inbounds/add"
            response = self.session.post(url, json=config, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
        except Exception as e:
            logger.error(f"Error adding inbound: {e}")
            return False
    
    def update_inbound(self, inbound_id, config):
        """Update existing inbound configuration"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/panel/api/inbounds/update/{inbound_id}"
            response = self.session.post(url, json=config, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
        except Exception as e:
            logger.error(f"Error updating inbound: {e}")
            return False
    
    def delete_inbound(self, inbound_id):
        """Delete inbound configuration"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/panel/api/inbounds/del/{inbound_id}"
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
        except Exception as e:
            logger.error(f"Error deleting inbound: {e}")
            return False
    
    def get_client_traffic(self, email):
        """Get traffic stats for a client"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/panel/api/inbounds/getClientTraffics/{email}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj')
            return None
        except Exception as e:
            logger.error(f"Error getting client traffic: {e}")
            return None
    
    def add_client(self, inbound_id, client_config):
        """Add client to inbound"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/panel/api/inbounds/addClient"
            data = {
                'id': inbound_id,
                'settings': json.dumps({'clients': [client_config]})
            }
            response = self.session.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            return False
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return False
    
    def get_server_status(self):
        """Get server status and statistics"""
        try:
            if not self.session_cookie:
                self.login()
            
            url = f"{self.base_url}/server/status"
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj')
            return None
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return None

# Initialize API client
xray_api = XrayPanelAPI(XRAY_PANEL_URL, XRAY_ADMIN_EMAIL, XRAY_ADMIN_PASSWORD)

# ==================== SYSTEM MONITORING ====================

def get_system_stats():
    """Get current system statistics"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Network
        net_io = psutil.net_io_counters()
        
        # Network interfaces
        interfaces = []
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # IPv4
                    interfaces.append({
                        'name': interface,
                        'ip': addr.address
                    })
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        stats = {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'frequency': cpu_freq.current if cpu_freq else 0
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'interfaces': interfaces
            },
            'uptime': str(uptime).split('.')[0],
            'timestamp': time.time()
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return None

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

# ==================== SPEED TEST ====================

def run_speed_test():
    """Run internet speed test"""
    try:
        logger.info("Starting speed test...")
        st = speedtest.Speedtest()
        st.get_best_server()
        
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        ping = st.results.ping
        
        result = {
            'download': round(download_speed, 2),
            'upload': round(upload_speed, 2),
            'ping': round(ping, 2),
            'timestamp': time.time(),
            'server': st.results.server
        }
        
        logger.info(f"Speed test completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Speed test error: {e}")
        return None

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Redirect to dashboard"""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check credentials (you can add more admin accounts here)
        if email == XRAY_ADMIN_EMAIL and password == XRAY_ADMIN_PASSWORD:
            session['logged_in'] = True
            session['email'] = email
            session.permanent = True
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email hoặc mật khẩu không đúng!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/system/stats')
@login_required
def api_system_stats():
    """API endpoint for system statistics"""
    stats = get_system_stats()
    if stats:
        with cache_lock:
            system_stats_cache.update(stats)
        return jsonify({'success': True, 'data': stats})
    return jsonify({'success': False, 'error': 'Failed to get system stats'})

@app.route('/api/speed/test', methods=['POST'])
@login_required
def api_speed_test():
    """API endpoint to run speed test"""
    def run_test_async():
        result = run_speed_test()
        if result:
            with cache_lock:
                speed_test_cache.update(result)
    
    # Run speed test in background thread
    thread = threading.Thread(target=run_test_async)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Speed test started'})

@app.route('/api/speed/result')
@login_required
def api_speed_result():
    """API endpoint to get speed test result"""
    with cache_lock:
        if speed_test_cache:
            return jsonify({'success': True, 'data': speed_test_cache})
    return jsonify({'success': False, 'message': 'No speed test data available'})

@app.route('/configs')
@login_required
def configs():
    """vless configurations page"""
    return render_template('configs.html')

@app.route('/api/configs/list')
@login_required
def api_configs_list():
    """API endpoint to list all configurations"""
    inbounds = xray_api.get_inbounds()
    return jsonify({'success': True, 'data': inbounds})

@app.route('/api/configs/add', methods=['POST'])
@login_required
def api_configs_add():
    """API endpoint to add new configuration"""
    try:
        data = request.json
        
        # Create vless inbound configuration
        config = {
            'enable': True,
            'port': data.get('port'),
            'protocol': 'vless',
            'settings': json.dumps({
                'clients': [],
                'decryption': 'none',
                'fallbacks': []
            }),
            'streamSettings': json.dumps({
                'network': data.get('network', 'tcp'),
                'security': data.get('security', 'none'),
                'tcpSettings': {},
                'wsSettings': {
                    'path': data.get('ws_path', '/'),
                    'headers': {}
                } if data.get('network') == 'ws' else {}
            }),
            'sniffing': json.dumps({
                'enabled': True,
                'destOverride': ['http', 'tls']
            }),
            'remark': data.get('remark', 'vless-config')
        }
        
        success = xray_api.add_inbound(config)
        if success:
            return jsonify({'success': True, 'message': 'Configuration added successfully'})
        return jsonify({'success': False, 'error': 'Failed to add configuration'})
    except Exception as e:
        logger.error(f"Error adding config: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/update/<int:config_id>', methods=['POST'])
@login_required
def api_configs_update(config_id):
    """API endpoint to update configuration"""
    try:
        data = request.json
        
        config = {
            'enable': data.get('enable', True),
            'port': data.get('port'),
            'protocol': 'vless',
            'settings': json.dumps({
                'clients': data.get('clients', []),
                'decryption': 'none'
            }),
            'streamSettings': json.dumps({
                'network': data.get('network', 'tcp'),
                'security': data.get('security', 'none')
            }),
            'remark': data.get('remark')
        }
        
        success = xray_api.update_inbound(config_id, config)
        if success:
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        return jsonify({'success': False, 'error': 'Failed to update configuration'})
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/delete/<int:config_id>', methods=['POST'])
@login_required
def api_configs_delete(config_id):
    """API endpoint to delete configuration"""
    try:
        success = xray_api.delete_inbound(config_id)
        if success:
            return jsonify({'success': True, 'message': 'Configuration deleted successfully'})
        return jsonify({'success': False, 'error': 'Failed to delete configuration'})
    except Exception as e:
        logger.error(f"Error deleting config: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/users')
@login_required
def users():
    """Users/clients management page"""
    return render_template('users.html')

@app.route('/api/users/add', methods=['POST'])
@login_required
def api_users_add():
    """API endpoint to add new user/client"""
    try:
        data = request.json
        inbound_id = data.get('inbound_id')
        
        import uuid
        client_config = {
            'id': str(uuid.uuid4()),
            'email': data.get('email'),
            'limitIp': data.get('limit_ip', 0),
            'totalGB': data.get('total_gb', 0),
            'expiryTime': data.get('expiry_time', 0),
            'enable': True,
            'tgId': '',
            'subId': ''
        }
        
        success = xray_api.add_client(inbound_id, client_config)
        if success:
            return jsonify({'success': True, 'message': 'User added successfully'})
        return jsonify({'success': False, 'error': 'Failed to add user'})
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/server/status')
@login_required
def api_server_status():
    """API endpoint to get server status from 3X-UI"""
    status = xray_api.get_server_status()
    if status:
        return jsonify({'success': True, 'data': status})
    return jsonify({'success': False, 'error': 'Failed to get server status'})

@app.route('/monitoring')
@login_required
def monitoring():
    """System monitoring page"""
    return render_template('monitoring.html')

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

# ==================== BACKGROUND TASKS ====================

def background_monitoring():
    """Background task to continuously monitor system"""
    while True:
        try:
            stats = get_system_stats()
            if stats:
                with cache_lock:
                    system_stats_cache.update(stats)
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Background monitoring error: {e}")
            time.sleep(5)

# ==================== MAIN ====================

if __name__ == '__main__':
    # Start background monitoring thread
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting admin panel on port {port}")
    logger.info(f"3X-UI Panel URL: {XRAY_PANEL_URL}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
