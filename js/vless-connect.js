// VLESS Connection Script - STREISAND ONLY - COMPLETE SOLUTION
// Tự động thêm cấu hình VLESS vào Streisand

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

// Main function - Open Streisand
async function openVPNApp() {
    const device = detectDevice();
    const btn = document.getElementById('openAppBtn');
    
    if (!btn) return;
    btn.disabled = true;
    
    if (device === 'iOS') {
        await openStreisandiOS(btn);
    } else if (device === 'Android') {
        await openStreisandAndroid(btn);
    } else {
        showStatus('⚠️ Tính năng này chỉ khả dụng trên iOS và Android. Vui lòng quét mã QR bằng ứng dụng Streisand.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
    }
}

// iOS - Open Streisand
async function openStreisandiOS(btn) {
    showStatus('🔄 Đang mở Streisand và thêm cấu hình...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const appStoreURL = 'https://apps.apple.com/app/streisand/id6450534064';
    
    // Tạo deep link - iOS sử dụng vless:// URL scheme
    const deepLink = vlessUri;
    console.log('iOS Deep Link:', deepLink);
    
    let appOpened = false;
    const startTime = Date.now();
    
    // Event handlers để detect app opening
    const handleBlur = () => {
        console.log('✓ Window blur - App opened');
        appOpened = true;
    };
    
    const handleVisibilityChange = () => {
        if (document.hidden) {
            console.log('✓ Document hidden - App opened');
            appOpened = true;
        }
    };
    
    const handlePageHide = () => {
        console.log('✓ Page hide - App opened');
        appOpened = true;
    };
    
    // Add listeners
    window.addEventListener('blur', handleBlur, { once: false });
    window.addEventListener('pagehide', handlePageHide, { once: false });
    document.addEventListener('visibilitychange', handleVisibilityChange, { once: false });
    
    // Try to open app with deep link
    try {
        // Method 1: Tạo invisible iframe
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = 'none';
        iframe.style.position = 'absolute';
        iframe.style.left = '-9999px';
        
        document.body.appendChild(iframe);
        iframe.src = deepLink;
        
        // Method 2: Backup với window.location (sau 300ms)
        setTimeout(() => {
            if (!appOpened) {
                console.log('Trying backup method: window.location');
                window.location.href = deepLink;
            }
        }, 300);
        
        // Cleanup iframe sau 1s
        setTimeout(() => {
            if (iframe.parentNode) {
                document.body.removeChild(iframe);
            }
        }, 1000);
        
    } catch (e) {
        console.error('Error opening deep link:', e);
    }
    
    // Wait and check result
    setTimeout(() => {
        // Remove listeners
        window.removeEventListener('blur', handleBlur);
        window.removeEventListener('pagehide', handlePageHide);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        
        const elapsed = Date.now() - startTime;
        console.log(`Check after ${elapsed}ms - appOpened: ${appOpened}, hidden: ${document.hidden}`);
        
        if (appOpened || document.hidden) {
            // App đã mở
            showStatus('✅ Streisand đã mở! Cấu hình VLESS đang được thêm tự động.', 'success');
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở Streisand';
            btn.disabled = false;
        } else {
            // App chưa có → Chuyển App Store
            showStatus('📱 Chưa cài đặt Streisand. Đang chuyển đến App Store...', 'info');
            btn.innerHTML = '<i class="fas fa-download"></i> Đang mở App Store...';
            
            setTimeout(() => {
                window.location.href = appStoreURL;
            }, 500);
        }
    }, 2500);
}

// Android - Open Streisand
async function openStreisandAndroid(btn) {
    showStatus('🔄 Đang mở Streisand và thêm cấu hình...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const playStoreURL = 'https://play.google.com/store/apps/details?id=com.github.shadowsocks.tv.vpn';
    
    // Android Intent URL - Tự động fallback to Play Store nếu app không có
    const vlessData = vlessUri.replace('vless://', '');
    const intentURL = `intent://${vlessData}#Intent;scheme=vless;package=com.github.shadowsocks.tv.vpn;S.browser_fallback_url=${encodeURIComponent(playStoreURL)};end`;
    
    console.log('Android Intent URL:', intentURL);
    
    let appOpened = false;
    
    // Event handlers
    const handleBlur = () => {
        console.log('✓ Window blur - App opened');
        appOpened = true;
    };
    
    const handleVisibilityChange = () => {
        if (document.hidden) {
            console.log('✓ Document hidden - App opened');
            appOpened = true;
        }
    };
    
    // Add listeners
    window.addEventListener('blur', handleBlur, { once: false });
    document.addEventListener('visibilitychange', handleVisibilityChange, { once: false });
    
    // Open with intent URL
    try {
        window.location.href = intentURL;
    } catch (e) {
        console.error('Error opening intent:', e);
    }
    
    // Check result
    setTimeout(() => {
        // Remove listeners
        window.removeEventListener('blur', handleBlur);
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        
        if (appOpened || document.hidden) {
            // App đã mở
            showStatus('✅ Streisand đã mở! Cấu hình VLESS đang được thêm tự động.', 'success');
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở Streisand';
            btn.disabled = false;
        } else {
            // Đang chuyển đến Play Store (Android tự động fallback)
            showStatus('📱 Nếu chưa cài Streisand, bạn sẽ được chuyển đến Google Play.', 'info');
            btn.innerHTML = '<i class="fas fa-download"></i> Mở Play Store nếu cần';
            btn.disabled = false;
        }
    }, 2500);
}

// Copy URI to clipboard (backup method)
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

// Initialize on page load
window.addEventListener('load', () => {
    // Copy URI to clipboard as backup
    copyToClipboard();
    
    // Show initial message
    const device = detectDevice();
    if (device === 'iOS' || device === 'Android') {
        showStatus('📱 Bấm "Thêm Cấu Hình" để tự động mở Streisand và thêm cấu hình VLESS.', 'info');
    } else {
        showStatus('💡 Vui lòng sử dụng thiết bị di động hoặc quét mã QR bằng ứng dụng Streisand.', 'info');
    }
});

// Handle visibility change - User quay lại trang sau khi cài app
let hadLeftPage = false;
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        hadLeftPage = true;
    } else if (hadLeftPage) {
        // User quay lại trang
        const btn = document.getElementById('openAppBtn');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
        }
        showStatus('💡 Nếu bạn vừa cài đặt Streisand, hãy bấm "Thử Lại" để thêm cấu hình.', 'info');
        hadLeftPage = false;
    }
});

// Auto trigger nếu có param ?auto=1
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auto') === '1') {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const btn = document.getElementById('openAppBtn');
            if (btn) {
                openVPNApp();
            }
        }, 500);
    });
}
