<?php
// Simple test version - Inline everything for testing
session_start();

if (!isset($_SESSION['user_id'])) {
    die("Please login first");
}

// Test VLESS URI
$testVlessUri = "vless://test-uuid@example.com:443?encryption=none&security=reality&type=tcp&sni=example.com&pbk=testkey&sid=testid#TestConfig";
?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test VLESS Button</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            border: none;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
        }
        .warning {
            background: #fff3cd;
            color: #856404;
        }
        .log {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
            text-align: left;
            font-family: monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Test VLESS Button</h1>
        <p>Simple inline test - No external JS</p>
        
        <div>
            <strong>VLESS URI:</strong>
            <div style="word-break: break-all; font-size: 12px; margin: 10px 0;">
                <?= htmlspecialchars($testVlessUri) ?>
            </div>
        </div>
        
        <button class="btn" onclick="testButton1()">
            ✅ Test 1: Alert
        </button>
        
        <button class="btn" onclick="testButton2()">
            🚀 Test 2: openV2Box()
        </button>
        
        <button class="btn" onclick="testButton3()">
            📱 Test 3: Full Deep Link
        </button>
        
        <div id="status" class="status"></div>
        
        <div class="log" id="log"></div>
    </div>

    <script>
        // Set VLESS URI
        window.vlessUri = <?= json_encode($testVlessUri) ?>;
        
        // Logging
        function log(msg) {
            const logDiv = document.getElementById('log');
            const time = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${time}] ${msg}<br>`;
            logDiv.scrollTop = logDiv.scrollHeight;
            console.log(msg);
        }
        
        function showStatus(msg, type) {
            const status = document.getElementById('status');
            status.className = 'status ' + type;
            status.textContent = msg;
            status.style.display = 'block';
            log('Status: ' + msg);
        }
        
        // Test 1: Simple alert
        function testButton1() {
            log('Test 1: Button clicked');
            alert('✅ Button 1 works!\n\nBasic onclick functioning.');
        }
        
        // Test 2: Call openV2Box
        function testButton2() {
            log('Test 2: Button clicked');
            if (typeof window.openV2Box === 'function') {
                log('openV2Box function found, calling...');
                window.openV2Box();
            } else {
                alert('❌ openV2Box function not found!');
                log('ERROR: openV2Box not found');
            }
        }
        
        // Test 3: Full implementation
        function testButton3() {
            log('Test 3: Full deep link test');
            fullDeepLinkTest();
        }
        
        // Device detection
        function detectDevice() {
            const ua = navigator.userAgent || navigator.vendor || window.opera;
            if (/iPad|iPhone|iPod/.test(ua) && !window.MSStream) {
                return 'iOS';
            }
            if (/android/i.test(ua)) {
                return 'Android';
            }
            return 'Other';
        }
        
        // Full deep link function
        window.openV2Box = function() {
            log('openV2Box() called');
            
            if (typeof window.vlessUri === 'undefined') {
                showStatus('❌ VLESS URI not defined', 'warning');
                return;
            }
            
            log('VLESS URI: ' + window.vlessUri);
            
            const device = detectDevice();
            log('Device: ' + device);
            
            const vlessUri = window.vlessUri;
            
            if (device === 'iOS') {
                log('iOS detected - would redirect to: ' + vlessUri);
                showStatus('✅ iOS: Would open V2Box with VLESS URI', 'success');
                // window.location.href = vlessUri; // Commented for testing
            } else if (device === 'Android') {
                const intent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=dev.hexasoftware.v2box;end`;
                log('Android detected - would redirect to: ' + intent);
                showStatus('✅ Android: Would open V2Box with Intent', 'success');
                // window.location.href = intent; // Commented for testing
            } else {
                log('Desktop detected');
                showStatus('⚠️ Desktop: V2Box only available on iOS/Android', 'warning');
            }
        };
        
        function fullDeepLinkTest() {
            log('=== Full Deep Link Test ===');
            log('Step 1: Check VLESS URI');
            if (window.vlessUri) {
                log('✅ VLESS URI exists: ' + window.vlessUri.substring(0, 50) + '...');
            } else {
                log('❌ VLESS URI missing!');
                return;
            }
            
            log('Step 2: Check openV2Box function');
            if (typeof window.openV2Box === 'function') {
                log('✅ openV2Box function exists');
            } else {
                log('❌ openV2Box function missing!');
                return;
            }
            
            log('Step 3: Detect device');
            const device = detectDevice();
            log('Device: ' + device);
            
            log('Step 4: Call openV2Box()');
            window.openV2Box();
        }
        
        // Init log
        log('Page loaded');
        log('Device: ' + detectDevice());
        log('VLESS URI set: ' + (window.vlessUri ? 'Yes' : 'No'));
        log('openV2Box function: ' + (typeof window.openV2Box));
        log('');
        log('Click buttons above to test...');
    </script>
</body>
</html>
