#!/usr/bin/env python3
"""
Admin Panel for vless Configuration Management and VPS Monitoring
Complete dashboard with all features for managing VPN service
Version: 1.0.0
"""

import os
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from functools import wraps

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash

# System monitoring
import psutil

# HTTP requests
import requests

# Speed test - with proper error handling
SPEEDTEST_AVAILABLE = False
try:
    import speedtest as speedtest_module
    SPEEDTEST_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import
        from speedtest import Speedtest as speedtest_module
        SPEEDTEST_AVAILABLE = True
    except ImportError:
        logging.warning("Speedtest module not available. Speed test feature will be disabled.")
        speedtest_module = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vpnvietnam_secret_key_2025')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
        self.session.timeout = 10
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
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.session_cookie = self.session.cookies.get_dict()
                    logger.info("Successfully logged in to 3X-UI panel")
                    return True
            
            logger.error(f"Login failed: Status {response.status_code}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Login error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            return False
    
    def get_inbounds(self):
        """Get all inbound configurations"""
        try:
            if not self.session_cookie:
                if not self.login():
                    return []
            
            url = f"{self.base_url}/panel/api/inbounds/list"
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('obj', [])
            
            # Try to login again if failed
            if self.login():
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
                if not self.login():
                    return False
            
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
                if not self.login():
                    return False
            
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
                if not self.login():
                    return False
            
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
                if not self.login():
                    return None
            
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
                if not self.login():
                    return False
            
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
                if not self.login():
                    return None
            
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
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == 2:  # IPv4
                        interfaces.append({
                            'name': interface,
                            'ip': addr.address
                        })
        except Exception as e:
            logger.warning(f"Error getting network interfaces: {e}")
        
        # Uptime
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = str(uptime).split('.')[0]
        except Exception as e:
            logger.warning(f"Error getting uptime: {e}")
            uptime_str = "Unknown"
        
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
            'uptime': uptime_str,
            'timestamp': time.time()
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return None

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    except:
        return "0 B"

# ==================== SPEED TEST ====================

def run_speed_test():
    """Run internet speed test"""
    if not SPEEDTEST_AVAILABLE:
        logger.warning("Speed test not available - module not installed")
        return {
            'error': 'Speed test module not available',
            'download': 0,
            'upload': 0,
            'ping': 0,
            'timestamp': time.time()
        }
    
    try:
        logger.info("Starting speed test...")
        st = speedtest_module.Speedtest() if hasattr(speedtest_module, 'Speedtest') else speedtest_module()
        st.get_best_server()
        
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        ping = st.results.ping
        
        result = {
            'download': round(download_speed, 2),
            'upload': round(upload_speed, 2),
            'ping': round(ping, 2),
            'timestamp': time.time(),
            'server': {
                'name': st.results.server.get('name', 'Unknown'),
                'sponsor': st.results.server.get('sponsor', 'Unknown'),
                'country': st.results.server.get('country', 'Unknown')
            } if hasattr(st.results, 'server') else {}
        }
        
        logger.info(f"Speed test completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Speed test error: {e}")
        return {
            'error': str(e),
            'download': 0,
            'upload': 0,
            'ping': 0,
            'timestamp': time.time()
        }

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
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Check credentials
        if email == XRAY_ADMIN_EMAIL and password == XRAY_ADMIN_PASSWORD:
            session['logged_in'] = True
            session['email'] = email
            session.permanent = True
            flash('Đăng nhập thành công!', 'success')
            logger.info(f"User logged in: {email}")
            return redirect(url_for('dashboard'))
        else:
            flash('Email hoặc mật khẩu không đúng!', 'error')
            logger.warning(f"Failed login attempt: {email}")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    email = session.get('email', 'unknown')
    session.clear()
    flash('Đã đăng xuất thành công!', 'info')
    logger.info(f"User logged out: {email}")
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
    try:
        stats = get_system_stats()
        if stats:
            with cache_lock:
                system_stats_cache.update(stats)
            return jsonify({'success': True, 'data': stats})
        return jsonify({'success': False, 'error': 'Failed to get system stats'})
    except Exception as e:
        logger.error(f"Error in api_system_stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/speed/test', methods=['POST'])
@login_required
def api_speed_test():
    """API endpoint to run speed test"""
    if not SPEEDTEST_AVAILABLE:
        return jsonify({
            'success': False, 
            'error': 'Speed test module not available. Install with: pip3 install speedtest-cli'
        })
    
    def run_test_async():
        try:
            result = run_speed_test()
            if result:
                with cache_lock:
                    speed_test_cache.update(result)
        except Exception as e:
            logger.error(f"Async speed test error: {e}")
    
    # Run speed test in background thread
    thread = threading.Thread(target=run_test_async, daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Speed test started'})

@app.route('/api/speed/result')
@login_required
def api_speed_result():
    """API endpoint to get speed test result"""
    try:
        with cache_lock:
            if speed_test_cache:
                return jsonify({'success': True, 'data': speed_test_cache})
        return jsonify({'success': False, 'message': 'No speed test data available'})
    except Exception as e:
        logger.error(f"Error in api_speed_result: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/configs')
@login_required
def configs():
    """vless configurations page"""
    return render_template('configs.html')

@app.route('/api/configs/list')
@login_required
def api_configs_list():
    """API endpoint to list all configurations"""
    try:
        inbounds = xray_api.get_inbounds()
        return jsonify({'success': True, 'data': inbounds})
    except Exception as e:
        logger.error(f"Error listing configs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/add', methods=['POST'])
@login_required
def api_configs_add():
    """API endpoint to add new configuration"""
    try:
        data = request.json
        
        # Create vless inbound configuration
        config = {
            'enable': True,
            'port': int(data.get('port', 443)),
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
            logger.info(f"Config added: {config['remark']}")
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
            'port': int(data.get('port', 443)),
            'protocol': 'vless',
            'settings': json.dumps({
                'clients': data.get('clients', []),
                'decryption': 'none'
            }),
            'streamSettings': json.dumps({
                'network': data.get('network', 'tcp'),
                'security': data.get('security', 'none')
            }),
            'remark': data.get('remark', '')
        }
        
        success = xray_api.update_inbound(config_id, config)
        if success:
            logger.info(f"Config updated: {config_id}")
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
            logger.info(f"Config deleted: {config_id}")
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
        inbound_id = int(data.get('inbound_id'))
        
        import uuid
        client_config = {
            'id': str(uuid.uuid4()),
            'email': data.get('email', ''),
            'limitIp': int(data.get('limit_ip', 0)),
            'totalGB': int(data.get('total_gb', 0)),
            'expiryTime': int(data.get('expiry_time', 0)),
            'enable': True,
            'tgId': '',
            'subId': ''
        }
        
        success = xray_api.add_client(inbound_id, client_config)
        if success:
            logger.info(f"User added: {client_config['email']}")
            return jsonify({'success': True, 'message': 'User added successfully'})
        return jsonify({'success': False, 'error': 'Failed to add user'})
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/server/status')
@login_required
def api_server_status():
    """API endpoint to get server status from 3X-UI"""
    try:
        status = xray_api.get_server_status()
        if status:
            return jsonify({'success': True, 'data': status})
        return jsonify({'success': False, 'error': 'Failed to get server status'})
    except Exception as e:
        logger.error(f"Error getting server status: {e}")
        return jsonify({'success': False, 'error': str(e)})

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

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('login.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== BACKGROUND TASKS ====================

def background_monitoring():
    """Background task to continuously monitor system"""
    logger.info("Background monitoring started")
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
    # Print startup information
    print("=" * 60)
    print("  VPN Vietnam - Admin Panel")
    print("=" * 60)
    print(f"Python Version: {os.sys.version.split()[0]}")
    
    # Get Flask version properly
    try:
        from importlib.metadata import version
        flask_version = version('flask')
    except:
        try:
            import flask
            flask_version = getattr(flask, '__version__', '3.0+')
        except:
            flask_version = '3.0+'
    print(f"Flask Version: {flask_version}")
    
    print(f"3X-UI Panel: {XRAY_PANEL_URL}")
    print(f"Speed Test Available: {SPEEDTEST_AVAILABLE}")
    print("=" * 60)
    
    # Start background monitoring thread
    monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitor_thread.start()
    logger.info("Background monitoring thread started")
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Start Flask app
    logger.info(f"Starting admin panel on {host}:{port}")
    print(f"\n🚀 Server starting on http://{host}:{port}")
    print(f"📧 Login: {XRAY_ADMIN_EMAIL}")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        logger.info("Admin panel stopped by user")
        print("\n\n👋 Admin panel stopped. Goodbye!")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\n❌ Error: {e}")
