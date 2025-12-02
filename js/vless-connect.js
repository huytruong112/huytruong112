// VLESS Connection Script - STREISAND ONLY - NO AUTO REDIRECT
// CHỈ gọi Streisand, KHÔNG tự động chuyển Store

let vlessUri = '';
let vlessUriEncoded = '';

function initializeConfig(uri, uriEncoded) {
    vlessUri = uri;
    vlessUriEncoded = uriEncoded;
    console.log('✓ Config initialized');
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

// Main function - CHỈ gọi Streisand
async function openVPNApp() {
    const device = detectDevice();
    const btn = document.getElementById('openAppBtn');
    
    if (!btn) return;
    btn.disabled = true;
    
    if (device === 'iOS') {
        openStreisandiOS(btn);
    } else if (device === 'Android') {
        openStreisandAndroid(btn);
    } else {
        showStatus('⚠️ Vui lòng sử dụng thiết bị di động hoặc quét mã QR.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
    }
}

// iOS - CHỈ gọi Streisand, KHÔNG redirect Store
function openStreisandiOS(btn) {
    showStatus('🔄 Đang mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const deepLink = vlessUri;
    console.log('Opening Streisand with:', deepLink);
    
    let appOpened = false;
    
    // Event handlers
    const handleBlur = () => {
        console.log('✓ App opened (blur)');
        appOpened = true;
    };
    
    const handleVisibilityChange = () => {
        if (document.hidden) {
            console.log('✓ App opened (hidden)');
            appOpened = true;
        }
    };
    
    const handlePageHide = () => {
        console.log('✓ App opened (pagehide)');
        appOpened = true;
    };
    
    // Add listeners
    window.addEventListener('blur', handleBlur);
    window.addEventListener('pagehide', handlePageHide);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Thử mở app
    try {
        // Method 1: iframe
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = 'none';
        iframe.style.position = 'absolute';
        iframe.style.left = '-9999px';
        
        document.body.appendChild(iframe);
        iframe.src = deepLink;
        
        // Method 2: window.location (backup sau 250ms)
        setTimeout(() => {
            if (!appOpened) {
                window.location.href = deepLink;
            }
        }, 250);
        
        // Cleanup iframe
        setTimeout(() => {
            if (iframe.parentNode) {
                document.body.removeChild(iframe);
            }
        }, 1000);
        
    } catch (e) {
        console.error('Error:', e);
    }
    
    // Check result sau 2s
    setTimeout(() => {
        window.removeEventListener('blur', handleBlur);
        window.removeEventListener('pagehide', handlePageHide);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        
        if (appOpened || document.hidden) {
            // App đã mở
            showStatus('✅ Streisand đã mở! Cấu hình VLESS đang được thêm.', 'success');
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở Streisand';
            btn.disabled = false;
        } else {
            // Không detect được app - KHÔNG redirect, chỉ show message
            showStatus('⚠️ Không mở được Streisand. Vui lòng đảm bảo ứng dụng đã được cài đặt.', 'warning');
            btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
            btn.disabled = false;
        }
    }, 2000);
}

// Android - CHỈ gọi Streisand, KHÔNG redirect Store
function openStreisandAndroid(btn) {
    showStatus('🔄 Đang mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    // Android Intent - KHÔNG có browser_fallback_url
    const vlessData = vlessUri.replace('vless://', '');
    const intentURL = `intent://${vlessData}#Intent;scheme=vless;package=com.github.shadowsocks.tv.vpn;end`;
    
    console.log('Opening Streisand with:', intentURL);
    
    let appOpened = false;
    
    // Event handlers
    const handleBlur = () => {
        console.log('✓ App opened (blur)');
        appOpened = true;
    };
    
    const handleVisibilityChange = () => {
        if (document.hidden) {
            console.log('✓ App opened (hidden)');
            appOpened = true;
        }
    };
    
    // Add listeners
    window.addEventListener('blur', handleBlur);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Mở với intent
    try {
        window.location.href = intentURL;
    } catch (e) {
        console.error('Error:', e);
    }
    
    // Check result sau 2s
    setTimeout(() => {
        window.removeEventListener('blur', handleBlur);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        
        if (appOpened || document.hidden) {
            // App đã mở
            showStatus('✅ Streisand đã mở! Cấu hình VLESS đang được thêm.', 'success');
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở Streisand';
            btn.disabled = false;
        } else {
            // Không detect được app - KHÔNG redirect, chỉ show message
            showStatus('⚠️ Không mở được Streisand. Vui lòng đảm bảo ứng dụng đã được cài đặt.', 'warning');
            btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
            btn.disabled = false;
        }
    }, 2000);
}

// Copy URI to clipboard (backup)
async function copyToClipboard() {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(vlessUri);
            console.log('✓ URI copied to clipboard');
        }
    } catch (err) {
        console.error('Copy failed:', err);
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    copyToClipboard();
    
    const device = detectDevice();
    if (device === 'iOS' || device === 'Android') {
        showStatus('📱 Bấm "Thêm Cấu Hình" để mở Streisand và tự động thêm cấu hình VLESS.', 'info');
    } else {
        showStatus('💡 Vui lòng sử dụng thiết bị di động hoặc quét mã QR.', 'info');
    }
});

// Handle page visibility - User quay lại
let hadLeftPage = false;
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        hadLeftPage = true;
    } else if (hadLeftPage) {
        const btn = document.getElementById('openAppBtn');
        if (btn && btn.disabled) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
        }
        hadLeftPage = false;
    }
});
