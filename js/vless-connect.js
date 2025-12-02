// VLESS Connection Script - QR CODE ONLY
// Streisand không hỗ trợ vless:// deep link → CHỈ dùng QR Code

let vlessUri = '';
let vlessUriEncoded = '';

function initializeConfig(uri, uriEncoded) {
    vlessUri = uri;
    vlessUriEncoded = uriEncoded;
    console.log('✓ Config initialized');
    console.log('VLESS URI:', uri);
}

// Detect device
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

// Show status message
function showStatus(message, type = 'success') {
    const statusDiv = document.getElementById('status-message');
    if (!statusDiv) return;
    
    statusDiv.innerHTML = message;
    statusDiv.className = type === 'success' ? 'status-success' : 
                         (type === 'info' ? 'status-info' : 'status-warning');
    statusDiv.style.display = 'block';
}

// Copy URI to clipboard
async function copyToClipboard() {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(vlessUri);
            console.log('✓ URI copied to clipboard');
            return true;
        }
    } catch (err) {
        console.error('Copy failed:', err);
    }
    return false;
}

// Main function - Copy và hướng dẫn quét QR
async function openVPNApp() {
    const btn = document.getElementById('openAppBtn');
    if (!btn) return;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang sao chép...';
    
    // Copy URI vào clipboard
    const copied = await copyToClipboard();
    
    setTimeout(() => {
        if (copied) {
            showStatus('✅ Đã sao chép cấu hình vào clipboard!<br><br>📱 <strong>Hướng dẫn:</strong><br>1️⃣ Mở ứng dụng Streisand<br>2️⃣ Nhấn nút "+" hoặc "Add"<br>3️⃣ Chọn "Scan QR Code" và quét mã QR bên trên<br><br>✨ Hoặc chọn "Import from Clipboard" để paste cấu hình đã copy.', 'success');
        } else {
            showStatus('📱 <strong>Hướng dẫn thêm cấu hình:</strong><br>1️⃣ Mở ứng dụng Streisand trên điện thoại<br>2️⃣ Nhấn nút "+" hoặc "Add Server"<br>3️⃣ Chọn "Scan QR Code"<br>4️⃣ Quét mã QR bên trên<br><br>✅ Cấu hình sẽ được tự động thêm vào Streisand!', 'info');
        }
        
        btn.innerHTML = '<i class="fas fa-qrcode"></i> Đã Copy - Hãy Quét QR';
        btn.disabled = false;
        
        // Highlight QR code
        const qrContainer = document.querySelector('.qr-container');
        if (qrContainer) {
            qrContainer.style.border = '3px solid #4CAF50';
            qrContainer.style.animation = 'pulse 1.5s ease-in-out 3';
            qrContainer.style.boxShadow = '0 0 20px rgba(76, 175, 80, 0.5)';
        }
    }, 500);
}

// Initialize on page load
window.addEventListener('load', () => {
    // Auto copy on load
    copyToClipboard();
    
    const device = detectDevice();
    if (device === 'iOS' || device === 'Android') {
        showStatus('📱 <strong>Cách thêm cấu hình vào Streisand:</strong><br><br>1️⃣ Mở ứng dụng Streisand<br>2️⃣ Nhấn nút "+" (Add)<br>3️⃣ Chọn "Scan QR Code"<br>4️⃣ Quét mã QR bên trên<br><br>✅ Hoặc bấm nút bên dưới để copy cấu hình, sau đó paste vào Streisand.', 'info');
    } else {
        showStatus('💡 Vui lòng mở trang này trên điện thoại và quét mã QR bằng ứng dụng Streisand.', 'info');
    }
});
