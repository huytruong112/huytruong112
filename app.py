"""
VLESS Manager All-in-One
Single-file Flask application for managing VLESS panels (3x-ui compatible)
"""

from flask import Flask, render_template_string, jsonify, request
import uuid
import json
import base64
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Mock Mode: True = Use fake data, False = Connect to real 3x-ui API
MOCK_MODE = True

# Mock data storage (in-memory)
MOCK_INBOUNDS = []
MOCK_CLIENTS = []
MOCK_STATS = {
    "cpu_usage": 0,
    "ram_usage": 0,
    "total_traffic": 0
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_uuid() -> str:
    """Generate a random UUID for new clients"""
    return str(uuid.uuid4())

def generate_keys() -> Dict[str, str]:
    """Generate public/private key pair for Reality"""
    # Simulated key generation (in real app, use proper crypto)
    private_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    public_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
    return {"private_key": private_key, "public_key": public_key}

def bytes_to_gb(bytes_val: int) -> float:
    """Convert bytes to gigabytes"""
    return round(bytes_val / (1024 ** 3), 2)

def gb_to_bytes(gb_val: float) -> int:
    """Convert gigabytes to bytes"""
    return int(gb_val * (1024 ** 3))

def timestamp_to_date(timestamp: int) -> str:
    """Convert Unix timestamp to readable date"""
    if timestamp == 0:
        return "No expiry"
    return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

def date_to_timestamp(date_str: str) -> int:
    """Convert date string to Unix timestamp (milliseconds)"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)

def generate_vless_link(client: Dict, inbound: Dict) -> str:
    """Generate VLESS share link"""
    uuid_val = client.get('id', '')
    email = client.get('email', 'user')
    
    # Get server info from inbound
    server = "example.com"  # In real app, get from config
    port = inbound.get('port', 443)
    network = inbound.get('network', 'tcp')
    
    # Build VLESS link
    link = f"vless://{uuid_val}@{server}:{port}"
    
    params = []
    params.append(f"type={network}")
    
    if network == 'ws':
        path = inbound.get('path', '/')
        params.append(f"path={path}")
    elif network == 'grpc':
        service_name = inbound.get('serviceName', 'grpc')
        params.append(f"serviceName={service_name}")
    
    params.append(f"security=tls")
    params.append(f"encryption=none")
    
    link += "?" + "&".join(params)
    link += f"#{email}"
    
    return link

def initialize_mock_data():
    """Initialize mock data for testing"""
    global MOCK_INBOUNDS, MOCK_CLIENTS, MOCK_STATS
    
    # Create sample inbounds
    MOCK_INBOUNDS = [
        {
            "id": 1,
            "port": 443,
            "protocol": "vless",
            "network": "ws",
            "path": "/vless",
            "security": "tls",
            "remark": "Main VLESS Server",
            "enable": True
        },
        {
            "id": 2,
            "port": 8443,
            "protocol": "vless",
            "network": "grpc",
            "serviceName": "grpc-service",
            "security": "reality",
            "remark": "Reality GRPC Server",
            "enable": True
        }
    ]
    
    # Create sample clients
    now = datetime.now()
    MOCK_CLIENTS = [
        {
            "id": generate_uuid(),
            "email": "user1@example.com",
            "inbound_id": 1,
            "enable": True,
            "expiryTime": int((now + timedelta(days=30)).timestamp() * 1000),
            "totalGB": gb_to_bytes(100),
            "up": gb_to_bytes(5.5),
            "down": gb_to_bytes(12.3),
            "limitIp": 2
        },
        {
            "id": generate_uuid(),
            "email": "user2@example.com",
            "inbound_id": 1,
            "enable": True,
            "expiryTime": int((now + timedelta(days=15)).timestamp() * 1000),
            "totalGB": gb_to_bytes(50),
            "up": gb_to_bytes(2.1),
            "down": gb_to_bytes(8.7),
            "limitIp": 1
        },
        {
            "id": generate_uuid(),
            "email": "user3@example.com",
            "inbound_id": 2,
            "enable": False,
            "expiryTime": int((now - timedelta(days=5)).timestamp() * 1000),
            "totalGB": gb_to_bytes(30),
            "up": gb_to_bytes(15.2),
            "down": gb_to_bytes(18.9),
            "limitIp": 3
        }
    ]
    
    # Mock statistics
    MOCK_STATS = {
        "cpu_usage": random.randint(20, 60),
        "ram_usage": random.randint(30, 70),
        "total_traffic": sum(c['up'] + c['down'] for c in MOCK_CLIENTS)
    }

# Initialize mock data on startup
initialize_mock_data()

# ============================================================================
# FLASK ROUTES - API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Main page - render the complete HTML/CSS/JS interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dashboard')
def api_dashboard():
    """Get dashboard statistics"""
    if MOCK_MODE:
        total_inbounds = len(MOCK_INBOUNDS)
        total_clients = len(MOCK_CLIENTS)
        active_clients = len([c for c in MOCK_CLIENTS if c['enable']])
        total_traffic_gb = bytes_to_gb(MOCK_STATS['total_traffic'])
        
        return jsonify({
            "success": True,
            "data": {
                "total_inbounds": total_inbounds,
                "total_clients": total_clients,
                "active_clients": active_clients,
                "total_traffic_gb": total_traffic_gb,
                "cpu_usage": MOCK_STATS['cpu_usage'],
                "ram_usage": MOCK_STATS['ram_usage']
            }
        })
    else:
        # Real API call would go here
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/inbounds')
def api_inbounds():
    """Get all inbounds"""
    if MOCK_MODE:
        return jsonify({
            "success": True,
            "data": MOCK_INBOUNDS
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/inbounds', methods=['POST'])
def api_add_inbound():
    """Add a new inbound"""
    if MOCK_MODE:
        data = request.json
        
        # Validation
        if data.get('network') == 'ws' and not data.get('path', '').startswith('/'):
            return jsonify({"success": False, "message": "WebSocket path must start with /"})
        
        new_inbound = {
            "id": max([i['id'] for i in MOCK_INBOUNDS], default=0) + 1,
            "port": data.get('port'),
            "protocol": "vless",
            "network": data.get('network'),
            "path": data.get('path', ''),
            "serviceName": data.get('serviceName', ''),
            "security": data.get('security'),
            "remark": data.get('remark'),
            "enable": True
        }
        
        MOCK_INBOUNDS.append(new_inbound)
        
        return jsonify({
            "success": True,
            "message": "Inbound created successfully",
            "data": new_inbound
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/inbounds/<int:inbound_id>', methods=['DELETE'])
def api_delete_inbound(inbound_id):
    """Delete an inbound"""
    if MOCK_MODE:
        global MOCK_INBOUNDS
        MOCK_INBOUNDS = [i for i in MOCK_INBOUNDS if i['id'] != inbound_id]
        return jsonify({"success": True, "message": "Inbound deleted successfully"})
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients')
def api_clients():
    """Get all clients with formatted data"""
    if MOCK_MODE:
        # Format clients for display
        formatted_clients = []
        for client in MOCK_CLIENTS:
            # Find inbound
            inbound = next((i for i in MOCK_INBOUNDS if i['id'] == client['inbound_id']), None)
            
            formatted_clients.append({
                "id": client['id'],
                "email": client['email'],
                "inbound_id": client['inbound_id'],
                "inbound_name": inbound['remark'] if inbound else "Unknown",
                "enable": client['enable'],
                "expiryTime": client['expiryTime'],
                "expiryDate": timestamp_to_date(client['expiryTime']),
                "totalGB": bytes_to_gb(client['totalGB']),
                "up": bytes_to_gb(client['up']),
                "down": bytes_to_gb(client['down']),
                "total_used": bytes_to_gb(client['up'] + client['down']),
                "limitIp": client['limitIp'],
                "status": "Active" if client['enable'] else "Disabled"
            })
        
        return jsonify({
            "success": True,
            "data": formatted_clients
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients', methods=['POST'])
def api_add_client():
    """Add a new client"""
    if MOCK_MODE:
        data = request.json
        
        new_client = {
            "id": data.get('uuid') or generate_uuid(),
            "email": data.get('email'),
            "inbound_id": data.get('inbound_id'),
            "enable": True,
            "expiryTime": date_to_timestamp(data.get('expiryDate')) if data.get('expiryDate') else 0,
            "totalGB": gb_to_bytes(float(data.get('totalGB', 0))),
            "up": 0,
            "down": 0,
            "limitIp": int(data.get('limitIp', 0))
        }
        
        MOCK_CLIENTS.append(new_client)
        
        return jsonify({
            "success": True,
            "message": "Client created successfully",
            "data": new_client
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients/<client_id>', methods=['PUT'])
def api_update_client(client_id):
    """Update a client"""
    if MOCK_MODE:
        data = request.json
        
        # Find client
        client = next((c for c in MOCK_CLIENTS if c['id'] == client_id), None)
        if not client:
            return jsonify({"success": False, "message": "Client not found"})
        
        # Update fields
        if 'email' in data:
            client['email'] = data['email']
        if 'uuid' in data:
            client['id'] = data['uuid']
        if 'limitIp' in data:
            client['limitIp'] = int(data['limitIp'])
        if 'totalGB' in data:
            client['totalGB'] = gb_to_bytes(float(data['totalGB']))
        if 'enable' in data:
            client['enable'] = data['enable']
        
        return jsonify({
            "success": True,
            "message": "Client updated successfully"
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients/<client_id>/renew', methods=['POST'])
def api_renew_client(client_id):
    """Renew/Extend client expiry date"""
    if MOCK_MODE:
        data = request.json
        
        # Find client
        client = next((c for c in MOCK_CLIENTS if c['id'] == client_id), None)
        if not client:
            return jsonify({"success": False, "message": "Client not found"})
        
        # Calculate new expiry
        current_expiry = client['expiryTime']
        now = datetime.now()
        
        if 'days' in data:
            # Add days to current expiry (or from now if expired)
            days = int(data['days'])
            if current_expiry > int(now.timestamp() * 1000):
                # Not expired yet, add to current expiry
                base_date = datetime.fromtimestamp(current_expiry / 1000)
            else:
                # Expired, add from now
                base_date = now
            
            new_expiry = base_date + timedelta(days=days)
            client['expiryTime'] = int(new_expiry.timestamp() * 1000)
        
        elif 'expiryDate' in data:
            # Set specific date
            client['expiryTime'] = date_to_timestamp(data['expiryDate'])
        
        return jsonify({
            "success": True,
            "message": f"Client renewed until {timestamp_to_date(client['expiryTime'])}"
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients/<client_id>/reset-traffic', methods=['POST'])
def api_reset_traffic(client_id):
    """Reset client traffic"""
    if MOCK_MODE:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c['id'] == client_id), None)
        if not client:
            return jsonify({"success": False, "message": "Client not found"})
        
        client['up'] = 0
        client['down'] = 0
        
        return jsonify({
            "success": True,
            "message": "Traffic reset successfully"
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients/<client_id>', methods=['DELETE'])
def api_delete_client(client_id):
    """Delete a client"""
    if MOCK_MODE:
        global MOCK_CLIENTS
        MOCK_CLIENTS = [c for c in MOCK_CLIENTS if c['id'] != client_id]
        return jsonify({"success": True, "message": "Client deleted successfully"})
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

@app.route('/api/clients/<client_id>/share')
def api_share_client(client_id):
    """Get share link for client"""
    if MOCK_MODE:
        # Find client
        client = next((c for c in MOCK_CLIENTS if c['id'] == client_id), None)
        if not client:
            return jsonify({"success": False, "message": "Client not found"})
        
        # Find inbound
        inbound = next((i for i in MOCK_INBOUNDS if i['id'] == client['inbound_id']), None)
        if not inbound:
            return jsonify({"success": False, "message": "Inbound not found"})
        
        # Generate share link
        share_link = generate_vless_link(client, inbound)
        
        return jsonify({
            "success": True,
            "data": {
                "link": share_link,
                "qr_data": share_link
            }
        })
    else:
        return jsonify({"success": False, "message": "Real API not implemented"})

# ============================================================================
# HTML TEMPLATE WITH EMBEDDED CSS/JS
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VLESS Manager All-in-One</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- QRCode.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    
    <style>
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8f9fa;
            --text-primary: #212529;
            --text-secondary: #6c757d;
            --border-color: #dee2e6;
            --card-bg: #ffffff;
            --sidebar-bg: #343a40;
            --sidebar-text: #ffffff;
        }
        
        [data-theme="dark"] {
            --bg-primary: #1a1d23;
            --bg-secondary: #2d3139;
            --text-primary: #e9ecef;
            --text-secondary: #adb5bd;
            --border-color: #495057;
            --card-bg: #2d3139;
            --sidebar-bg: #0d0f12;
            --sidebar-text: #e9ecef;
        }
        
        body {
            background-color: var(--bg-primary);
            color: var(--text-primary);
            transition: all 0.3s ease;
        }
        
        .sidebar {
            min-height: 100vh;
            background: var(--sidebar-bg);
            color: var(--sidebar-text);
            position: fixed;
            left: 0;
            top: 0;
            width: 250px;
            z-index: 100;
        }
        
        .sidebar .nav-link {
            color: var(--sidebar-text);
            padding: 15px 20px;
            border-radius: 8px;
            margin: 5px 10px;
            transition: all 0.3s;
        }
        
        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .main-content {
            margin-left: 250px;
            padding: 30px;
        }
        
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-card .icon {
            font-size: 2.5rem;
            opacity: 0.8;
        }
        
        .table-custom {
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .table {
            color: var(--text-primary);
            margin-bottom: 0;
        }
        
        .table thead {
            background: var(--bg-secondary);
        }
        
        .badge-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .modal-content {
            background: var(--card-bg);
            color: var(--text-primary);
        }
        
        .form-control, .form-select {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .form-control:focus, .form-select:focus {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }
        
        .toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        }
        
        .theme-toggle {
            cursor: pointer;
            padding: 10px;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .theme-toggle:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        #qrcode {
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        
        .progress-sm {
            height: 8px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <!-- Toast Container -->
    <div class="toast-container"></div>
    
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="p-4">
            <h4 class="mb-0"><i class="fas fa-shield-alt"></i> VLESS Manager</h4>
            <small class="text-muted">All-in-One Panel</small>
        </div>
        
        <nav class="nav flex-column">
            <a class="nav-link active" href="#" data-page="dashboard">
                <i class="fas fa-tachometer-alt me-2"></i> Dashboard
            </a>
            <a class="nav-link" href="#" data-page="inbounds">
                <i class="fas fa-server me-2"></i> Inbounds
            </a>
            <a class="nav-link" href="#" data-page="clients">
                <i class="fas fa-users me-2"></i> Clients
            </a>
        </nav>
        
        <div class="p-3 mt-auto">
            <div class="theme-toggle text-center" onclick="toggleTheme()">
                <i class="fas fa-moon" id="themeIcon"></i>
            </div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
        <!-- Dashboard Page -->
        <div id="page-dashboard" class="page-content">
            <h2 class="mb-4">Dashboard Overview</h2>
            
            <div class="row">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Total Inbounds</h6>
                                <h3 class="mb-0" id="stat-inbounds">0</h3>
                            </div>
                            <div class="icon text-primary">
                                <i class="fas fa-server"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Total Clients</h6>
                                <h3 class="mb-0" id="stat-clients">0</h3>
                            </div>
                            <div class="icon text-success">
                                <i class="fas fa-users"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Total Traffic</h6>
                                <h3 class="mb-0" id="stat-traffic">0 GB</h3>
                            </div>
                            <div class="icon text-warning">
                                <i class="fas fa-chart-line"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="text-muted mb-2">Active Clients</h6>
                                <h3 class="mb-0" id="stat-active">0</h3>
                            </div>
                            <div class="icon text-info">
                                <i class="fas fa-check-circle"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="stat-card">
                        <h5 class="mb-3">CPU Usage</h5>
                        <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <div class="progress progress-sm">
                                    <div class="progress-bar bg-primary" id="cpu-bar" style="width: 0%"></div>
                                </div>
                            </div>
                            <span class="ms-3" id="cpu-text">0%</span>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="stat-card">
                        <h5 class="mb-3">RAM Usage</h5>
                        <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <div class="progress progress-sm">
                                    <div class="progress-bar bg-success" id="ram-bar" style="width: 0%"></div>
                                </div>
                            </div>
                            <span class="ms-3" id="ram-text">0%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Inbounds Page -->
        <div id="page-inbounds" class="page-content" style="display: none;">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Inbound Management</h2>
                <button class="btn btn-primary" onclick="showAddInboundModal()">
                    <i class="fas fa-plus me-2"></i> Add Inbound
                </button>
            </div>
            
            <div class="table-custom">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Remark</th>
                            <th>Port</th>
                            <th>Protocol</th>
                            <th>Network</th>
                            <th>Security</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="inbounds-table-body">
                        <tr>
                            <td colspan="7" class="text-center">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Clients Page -->
        <div id="page-clients" class="page-content" style="display: none;">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2>Client Management</h2>
                <button class="btn btn-primary" onclick="showAddClientModal()">
                    <i class="fas fa-plus me-2"></i> Add Client
                </button>
            </div>
            
            <div class="table-custom">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Email</th>
                            <th>Inbound</th>
                            <th>Traffic Used</th>
                            <th>Total GB</th>
                            <th>Expiry Date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="clients-table-body">
                        <tr>
                            <td colspan="7" class="text-center">Loading...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Modal: Add Inbound -->
    <div class="modal fade" id="addInboundModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Inbound</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addInboundForm">
                        <div class="mb-3">
                            <label class="form-label">Remark</label>
                            <input type="text" class="form-control" name="remark" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Port</label>
                            <input type="number" class="form-control" name="port" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Network</label>
                            <select class="form-select" name="network" onchange="toggleInboundFields(this.value)">
                                <option value="tcp">TCP</option>
                                <option value="ws">WebSocket</option>
                                <option value="grpc">GRPC</option>
                            </select>
                        </div>
                        <div class="mb-3" id="pathField" style="display: none;">
                            <label class="form-label">Path (must start with /)</label>
                            <input type="text" class="form-control" name="path" placeholder="/path">
                        </div>
                        <div class="mb-3" id="serviceNameField" style="display: none;">
                            <label class="form-label">Service Name</label>
                            <input type="text" class="form-control" name="serviceName">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Security</label>
                            <select class="form-select" name="security">
                                <option value="tls">TLS</option>
                                <option value="reality">Reality</option>
                                <option value="none">None</option>
                            </select>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitAddInbound()">Create</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal: Add Client -->
    <div class="modal fade" id="addClientModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Client</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addClientForm">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">UUID</label>
                            <div class="input-group">
                                <input type="text" class="form-control" name="uuid" id="clientUUID">
                                <button type="button" class="btn btn-outline-secondary" onclick="generateNewUUID()">
                                    <i class="fas fa-sync"></i>
                                </button>
                            </div>
                            <small class="text-muted">Leave empty to auto-generate</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Inbound</label>
                            <select class="form-select" name="inbound_id" id="clientInbound" required>
                                <option value="">Select Inbound</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Total GB</label>
                            <input type="number" class="form-control" name="totalGB" value="100" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Limit IP</label>
                            <input type="number" class="form-control" name="limitIp" value="2" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Expiry Date</label>
                            <input type="date" class="form-control" name="expiryDate" required>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitAddClient()">Create</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal: Edit Client -->
    <div class="modal fade" id="editClientModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Client</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="editClientForm">
                        <input type="hidden" name="clientId" id="editClientId">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" class="form-control" name="email" id="editEmail" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">UUID</label>
                            <input type="text" class="form-control" name="uuid" id="editUUID" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Total GB</label>
                            <input type="number" class="form-control" name="totalGB" id="editTotalGB" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Limit IP</label>
                            <input type="number" class="form-control" name="limitIp" id="editLimitIp" required>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitEditClient()">Save Changes</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal: Renew Client -->
    <div class="modal fade" id="renewClientModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Renew/Extend Client</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <input type="hidden" id="renewClientId">
                    <p class="text-muted">Current Expiry: <strong id="currentExpiry"></strong></p>
                    
                    <div class="d-grid gap-2 mb-3">
                        <button class="btn btn-outline-primary" onclick="renewByDays(30)">
                            <i class="fas fa-calendar-plus me-2"></i> Extend 30 Days
                        </button>
                        <button class="btn btn-outline-primary" onclick="renewByDays(90)">
                            <i class="fas fa-calendar-plus me-2"></i> Extend 90 Days
                        </button>
                    </div>
                    
                    <hr>
                    
                    <div class="mb-3">
                        <label class="form-label">Or set specific date:</label>
                        <input type="date" class="form-control" id="renewSpecificDate">
                    </div>
                    <button class="btn btn-primary w-100" onclick="renewByDate()">
                        Set Specific Date
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal: Share Client -->
    <div class="modal fade" id="shareClientModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Share Client Configuration</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    <div id="qrcode"></div>
                    <div class="mt-3">
                        <label class="form-label">Configuration Link:</label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="shareLink" readonly>
                            <button class="btn btn-primary" onclick="copyShareLink()">
                                <i class="fas fa-copy me-2"></i> Copy
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // ============================================================================
        // GLOBAL VARIABLES
        // ============================================================================
        
        let currentPage = 'dashboard';
        let inboundsData = [];
        let clientsData = [];
        
        // ============================================================================
        // THEME MANAGEMENT
        // ============================================================================
        
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            
            const icon = document.getElementById('themeIcon');
            icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            
            localStorage.setItem('theme', newTheme);
        }
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        document.getElementById('themeIcon').className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        
        // ============================================================================
        // NAVIGATION
        // ============================================================================
        
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                switchPage(page);
            });
        });
        
        function switchPage(page) {
            // Update nav active state
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            document.querySelector(`[data-page="${page}"]`).classList.add('active');
            
            // Show/hide pages
            document.querySelectorAll('.page-content').forEach(p => {
                p.style.display = 'none';
            });
            document.getElementById(`page-${page}`).style.display = 'block';
            
            currentPage = page;
            
            // Load data for page
            if (page === 'dashboard') {
                loadDashboard();
            } else if (page === 'inbounds') {
                loadInbounds();
            } else if (page === 'clients') {
                loadClients();
            }
        }
        
        // ============================================================================
        // TOAST NOTIFICATIONS
        // ============================================================================
        
        function showToast(message, type = 'success') {
            const toastContainer = document.querySelector('.toast-container');
            const toastId = 'toast-' + Date.now();
            
            const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
            
            const toastHTML = `
                <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            toastContainer.insertAdjacentHTML('beforeend', toastHTML);
            
            const toastElement = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
            toast.show();
            
            toastElement.addEventListener('hidden.bs.toast', function() {
                toastElement.remove();
            });
        }
        
        // ============================================================================
        // API CALLS
        // ============================================================================
        
        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const result = await response.json();
                
                if (result.success) {
                    const data = result.data;
                    document.getElementById('stat-inbounds').textContent = data.total_inbounds;
                    document.getElementById('stat-clients').textContent = data.total_clients;
                    document.getElementById('stat-active').textContent = data.active_clients;
                    document.getElementById('stat-traffic').textContent = data.total_traffic_gb.toFixed(2) + ' GB';
                    
                    // CPU/RAM
                    document.getElementById('cpu-bar').style.width = data.cpu_usage + '%';
                    document.getElementById('cpu-text').textContent = data.cpu_usage + '%';
                    document.getElementById('ram-bar').style.width = data.ram_usage + '%';
                    document.getElementById('ram-text').textContent = data.ram_usage + '%';
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }
        
        async function loadInbounds() {
            try {
                const response = await fetch('/api/inbounds');
                const result = await response.json();
                
                if (result.success) {
                    inboundsData = result.data;
                    renderInboundsTable();
                }
            } catch (error) {
                console.error('Error loading inbounds:', error);
            }
        }
        
        function renderInboundsTable() {
            const tbody = document.getElementById('inbounds-table-body');
            
            if (inboundsData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No inbounds found</td></tr>';
                return;
            }
            
            tbody.innerHTML = inboundsData.map(inbound => `
                <tr>
                    <td><strong>${inbound.remark}</strong></td>
                    <td>${inbound.port}</td>
                    <td><span class="badge bg-primary">${inbound.protocol}</span></td>
                    <td><span class="badge bg-info">${inbound.network}</span></td>
                    <td><span class="badge bg-success">${inbound.security}</span></td>
                    <td>
                        ${inbound.enable ? 
                            '<span class="badge bg-success">Active</span>' : 
                            '<span class="badge bg-secondary">Disabled</span>'
                        }
                    </td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteInbound(${inbound.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        async function loadClients() {
            try {
                const response = await fetch('/api/clients');
                const result = await response.json();
                
                if (result.success) {
                    clientsData = result.data;
                    renderClientsTable();
                }
            } catch (error) {
                console.error('Error loading clients:', error);
            }
        }
        
        function renderClientsTable() {
            const tbody = document.getElementById('clients-table-body');
            
            if (clientsData.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No clients found</td></tr>';
                return;
            }
            
            tbody.innerHTML = clientsData.map(client => {
                const usedPercent = client.totalGB > 0 ? (client.total_used / client.totalGB * 100).toFixed(1) : 0;
                
                return `
                <tr>
                    <td><strong>${client.email}</strong></td>
                    <td><small>${client.inbound_name}</small></td>
                    <td>
                        ${client.total_used.toFixed(2)} GB
                        <div class="progress progress-sm mt-1">
                            <div class="progress-bar" style="width: ${usedPercent}%"></div>
                        </div>
                    </td>
                    <td>${client.totalGB.toFixed(0)} GB</td>
                    <td><small>${client.expiryDate}</small></td>
                    <td>
                        ${client.enable ? 
                            '<span class="badge bg-success badge-status">Active</span>' : 
                            '<span class="badge bg-secondary badge-status">Disabled</span>'
                        }
                    </td>
                    <td>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-primary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="showEditClientModal('${client.id}')">
                                    <i class="fas fa-edit me-2"></i> Edit Info
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="showRenewModal('${client.id}')">
                                    <i class="fas fa-calendar-plus me-2"></i> Renew/Extend
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="resetTraffic('${client.id}')">
                                    <i class="fas fa-sync me-2"></i> Reset Traffic
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="showShareModal('${client.id}')">
                                    <i class="fas fa-share-alt me-2"></i> Share
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="deleteClient('${client.id}')">
                                    <i class="fas fa-trash me-2"></i> Delete
                                </a></li>
                            </ul>
                        </div>
                    </td>
                </tr>
            `;
            }).join('');
        }
        
        // ============================================================================
        // INBOUND OPERATIONS
        // ============================================================================
        
        function showAddInboundModal() {
            document.getElementById('addInboundForm').reset();
            const modal = new bootstrap.Modal(document.getElementById('addInboundModal'));
            modal.show();
        }
        
        function toggleInboundFields(network) {
            document.getElementById('pathField').style.display = network === 'ws' ? 'block' : 'none';
            document.getElementById('serviceNameField').style.display = network === 'grpc' ? 'block' : 'none';
        }
        
        async function submitAddInbound() {
            const form = document.getElementById('addInboundForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Validation
            if (data.network === 'ws' && data.path && !data.path.startsWith('/')) {
                showToast('WebSocket path must start with /', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/inbounds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    bootstrap.Modal.getInstance(document.getElementById('addInboundModal')).hide();
                    loadInbounds();
                } else {
                    showToast(result.message, 'error');
                }
            } catch (error) {
                showToast('Error creating inbound', 'error');
            }
        }
        
        async function deleteInbound(id) {
            if (!confirm('Are you sure you want to delete this inbound?')) return;
            
            try {
                const response = await fetch(`/api/inbounds/${id}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    loadInbounds();
                }
            } catch (error) {
                showToast('Error deleting inbound', 'error');
            }
        }
        
        // ============================================================================
        // CLIENT OPERATIONS
        // ============================================================================
        
        async function showAddClientModal() {
            // Load inbounds for dropdown
            await loadInbounds();
            const select = document.getElementById('clientInbound');
            select.innerHTML = '<option value="">Select Inbound</option>' + 
                inboundsData.map(i => `<option value="${i.id}">${i.remark}</option>`).join('');
            
            // Set default expiry date (30 days from now)
            const expiryDate = new Date();
            expiryDate.setDate(expiryDate.getDate() + 30);
            document.querySelector('#addClientForm input[name="expiryDate"]').value = 
                expiryDate.toISOString().split('T')[0];
            
            const modal = new bootstrap.Modal(document.getElementById('addClientModal'));
            modal.show();
        }
        
        function generateNewUUID() {
            // Simple UUID v4 generator
            const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
            document.getElementById('clientUUID').value = uuid;
        }
        
        async function submitAddClient() {
            const form = document.getElementById('addClientForm');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Convert inbound_id to number
            data.inbound_id = parseInt(data.inbound_id);
            
            try {
                const response = await fetch('/api/clients', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    bootstrap.Modal.getInstance(document.getElementById('addClientModal')).hide();
                    loadClients();
                } else {
                    showToast(result.message, 'error');
                }
            } catch (error) {
                showToast('Error creating client', 'error');
            }
        }
        
        function showEditClientModal(clientId) {
            const client = clientsData.find(c => c.id === clientId);
            if (!client) return;
            
            document.getElementById('editClientId').value = client.id;
            document.getElementById('editEmail').value = client.email;
            document.getElementById('editUUID').value = client.id;
            document.getElementById('editTotalGB').value = client.totalGB;
            document.getElementById('editLimitIp').value = client.limitIp;
            
            const modal = new bootstrap.Modal(document.getElementById('editClientModal'));
            modal.show();
        }
        
        async function submitEditClient() {
            const clientId = document.getElementById('editClientId').value;
            const data = {
                email: document.getElementById('editEmail').value,
                uuid: document.getElementById('editUUID').value,
                totalGB: document.getElementById('editTotalGB').value,
                limitIp: document.getElementById('editLimitIp').value
            };
            
            try {
                const response = await fetch(`/api/clients/${clientId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editClientModal')).hide();
                    loadClients();
                }
            } catch (error) {
                showToast('Error updating client', 'error');
            }
        }
        
        function showRenewModal(clientId) {
            const client = clientsData.find(c => c.id === clientId);
            if (!client) return;
            
            document.getElementById('renewClientId').value = client.id;
            document.getElementById('currentExpiry').textContent = client.expiryDate;
            
            const modal = new bootstrap.Modal(document.getElementById('renewClientModal'));
            modal.show();
        }
        
        async function renewByDays(days) {
            const clientId = document.getElementById('renewClientId').value;
            
            try {
                const response = await fetch(`/api/clients/${clientId}/renew`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ days: days })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    bootstrap.Modal.getInstance(document.getElementById('renewClientModal')).hide();
                    loadClients();
                }
            } catch (error) {
                showToast('Error renewing client', 'error');
            }
        }
        
        async function renewByDate() {
            const clientId = document.getElementById('renewClientId').value;
            const date = document.getElementById('renewSpecificDate').value;
            
            if (!date) {
                showToast('Please select a date', 'error');
                return;
            }
            
            try {
                const response = await fetch(`/api/clients/${clientId}/renew`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ expiryDate: date })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    bootstrap.Modal.getInstance(document.getElementById('renewClientModal')).hide();
                    loadClients();
                }
            } catch (error) {
                showToast('Error renewing client', 'error');
            }
        }
        
        async function resetTraffic(clientId) {
            if (!confirm('Are you sure you want to reset traffic for this client?')) return;
            
            try {
                const response = await fetch(`/api/clients/${clientId}/reset-traffic`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    loadClients();
                }
            } catch (error) {
                showToast('Error resetting traffic', 'error');
            }
        }
        
        async function deleteClient(clientId) {
            if (!confirm('Are you sure you want to delete this client?')) return;
            
            try {
                const response = await fetch(`/api/clients/${clientId}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message);
                    loadClients();
                }
            } catch (error) {
                showToast('Error deleting client', 'error');
            }
        }
        
        async function showShareModal(clientId) {
            try {
                const response = await fetch(`/api/clients/${clientId}/share`);
                const result = await response.json();
                
                if (result.success) {
                    // Clear previous QR code
                    document.getElementById('qrcode').innerHTML = '';
                    
                    // Generate new QR code
                    new QRCode(document.getElementById('qrcode'), {
                        text: result.data.qr_data,
                        width: 256,
                        height: 256
                    });
                    
                    // Set share link
                    document.getElementById('shareLink').value = result.data.link;
                    
                    const modal = new bootstrap.Modal(document.getElementById('shareClientModal'));
                    modal.show();
                }
            } catch (error) {
                showToast('Error generating share link', 'error');
            }
        }
        
        function copyShareLink() {
            const input = document.getElementById('shareLink');
            input.select();
            document.execCommand('copy');
            showToast('Link copied to clipboard!');
        }
        
        // ============================================================================
        // INITIALIZATION
        // ============================================================================
        
        // Load dashboard on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadDashboard();
        });
    </script>
</body>
</html>
"""

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("VLESS Manager All-in-One")
    print("=" * 60)
    print(f"Mock Mode: {MOCK_MODE}")
    print(f"Server starting on http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
