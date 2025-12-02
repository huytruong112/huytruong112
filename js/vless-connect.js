// VLESS Connection Script - FIXED Detection
// Đã cài app → Tự động mở, KHÔNG chuyển Store

let vlessUri;
let vlessUriEncoded;

function initializeConfig(uri, uriEncoded) {
    vlessUri = uri;
    vlessUriEncoded = uriEncoded;
}

function detectDevice() {
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    
    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
        return 'iOS';
    }
    
    if (/android/i.test(userAgent)) {
        return 'Android';
    }
    
    return 'Other';
}

function showStatus(message, type = 'success') {
    const statusDiv = document.getElementById('status-message');
    statusDiv.innerHTML = message;
    statusDiv.className = type === 'success' ? 'status-success' : (type === 'info' ? 'status-info' : 'status-warning');
    statusDiv.style.display = 'block';
}

// Hàm thử mở app - SIMPLIFIED & RELIABLE
function tryOpenApp(deepLink, appName, timeout = 5000) {
    return new Promise((resolve) => {
        let resolved = false;
        let startTime = Date.now();
        
        const resolveOnce = (success) => {
            if (!resolved) {
                resolved = true;
                resolve(success);
            }
        };
        
        // Detect khi app mở thành công
        const handleBlur = () => {
            console.log('Window blur detected - App opened');
            resolveOnce(true);
        };
        
        const handleVisibilityChange = () => {
            if (document.hidden) {
                console.log('Document hidden - App opened');
                resolveOnce(true);
            }
        };
        
        const handlePageHide = () => {
            console.log('Page hide - App opened');
            resolveOnce(true);
        };
        
        // Add listeners
        window.addEventListener('blur', handleBlur);
        window.addEventListener('pagehide', handlePageHide);
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Cleanup function
        const cleanup = () => {
            window.removeEventListener('blur', handleBlur);
            window.removeEventListener('pagehide', handlePageHide);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
        
        // Tạo iframe để trigger deep link
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = 'none';
        
        try {
            iframe.src = deepLink;
            document.body.appendChild(iframe);
            
            // Backup: Cũng thử với window.location
            setTimeout(() => {
                if (!resolved) {
                    window.location.href = deepLink;
                }
            }, 200);
        } catch (e) {
            console.error('Error opening deep link:', e);
        }
        
        // Timeout - CHỈ resolve false khi CHẮC CHẮN app không mở
        setTimeout(() => {
            cleanup();
            
            // Remove iframe
            if (iframe.parentNode) {
                document.body.removeChild(iframe);
            }
            
            // Kiểm tra thời gian: nếu đã blur/hidden thì app đã mở
            if (!resolved) {
                const elapsed = Date.now() - startTime;
                console.log(`Timeout after ${elapsed}ms, page still visible: ${!document.hidden}, has focus: ${document.hasFocus()}`);
                
                // Chỉ return false nếu trang vẫn visible VÀ có focus
                if (!document.hidden && document.hasFocus()) {
                    resolveOnce(false);
                } else {
                    // Không chắc chắn → assume app đã mở
                    resolveOnce(true);
                }
            }
        }, timeout);
    });
}

// Logic cascade chính
async function openVPNApp() {
    const device = detectDevice();
    const btn = document.getElementById('openAppBtn');
    btn.disabled = true;
    
    if (device === 'iOS') {
        await openVPNAppiOS(btn);
    } else if (device === 'Android') {
        await openVPNAppAndroid(btn);
    } else {
        showStatus('⚠️ Tính năng này chỉ khả dụng trên iOS và Android. Vui lòng sử dụng thiết bị di động hoặc quét mã QR.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
    }
}

// iOS Logic - FIXED
async function openVPNAppiOS(btn) {
    const appStoreStreisand = 'https://apps.apple.com/app/streisand/id6450534064';
    const appStoreSingBox = 'https://apps.apple.com/app/sing-box/id6451272673';
    
    // Bước 1: Thử Streisand với timeout DÀI (5s)
    showStatus('🔍 Đang mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const streisandDeepLink = vlessUri;
    console.log('Trying Streisand with deep link:', streisandDeepLink);
    const streisandOpened = await tryOpenApp(streisandDeepLink, 'Streisand', 5000);
    
    if (streisandOpened) {
        showStatus('✅ Streisand đã mở! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box với timeout DÀI (5s)
    showStatus('🔍 Đang mở sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    const singBoxDeepLink = vlessUri;
    console.log('Trying sing-box with deep link:', singBoxDeepLink);
    const singBoxOpened = await tryOpenApp(singBoxDeepLink, 'sing-box', 5000);
    
    if (singBoxOpened) {
        showStatus('✅ sing-box đã mở! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
        }, 2000);
        return;
    }
    
    // Bước 3: Cả 2 đều không có → Hiển thị links Store (KHÔNG tự động chuyển)
    showStatus('⚠️ Không tìm thấy ứng dụng. Vui lòng tải ứng dụng từ bên dưới.', 'warning');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
    
    // Hiển thị nổi bật các link store
    const storeLinks = document.querySelectorAll('.store-link');
    storeLinks.forEach(link => {
        link.style.border = '3px solid #ff0000';
        link.style.animation = 'pulse 1s infinite';
    });
}

// Android Logic - FIXED
async function openVPNAppAndroid(btn) {
    const playStoreStreisand = 'https://play.google.com/store/apps/details?id=com.github.shadowsocks.tv.vpn';
    const playStoreSingBox = 'https://play.google.com/store/apps/details?id=io.nekohasekai.sfa';
    
    // Bước 1: Thử Streisand với timeout DÀI (5s)
    showStatus('🔍 Đang mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    // Intent KHÔNG có fallback URL (để tránh tự động chuyển store)
    const streisandIntent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=com.github.shadowsocks.tv.vpn;end`;
    console.log('Trying Streisand with intent:', streisandIntent);
    const streisandOpened = await tryOpenApp(streisandIntent, 'Streisand', 5000);
    
    if (streisandOpened) {
        showStatus('✅ Streisand đã mở! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box với timeout DÀI (5s)
    showStatus('🔍 Đang mở sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    const singBoxIntent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=io.nekohasekai.sfa;end`;
    console.log('Trying sing-box with intent:', singBoxIntent);
    const singBoxOpened = await tryOpenApp(singBoxIntent, 'sing-box', 5000);
    
    if (singBoxOpened) {
        showStatus('✅ sing-box đã mở! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
        }, 2000);
        return;
    }
    
    // Bước 3: Cả 2 đều không có → Hiển thị links Store (KHÔNG tự động chuyển)
    showStatus('⚠️ Không tìm thấy ứng dụng. Vui lòng tải ứng dụng từ bên dưới.', 'warning');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
    
    // Hiển thị nổi bật các link store
    const storeLinks = document.querySelectorAll('.store-link');
    storeLinks.forEach(link => {
        link.style.border = '3px solid #ff0000';
        link.style.animation = 'pulse 1s infinite';
    });
}

function copyToClipboard() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(vlessUri)
            .then(() => {
                console.log('✓ VLESS URI đã được copy vào clipboard');
            })
            .catch(err => {
                console.error('Lỗi khi copy:', err);
            });
    }
}

// Khởi tạo khi trang load
window.addEventListener('load', () => {
    copyToClipboard();
    showStatus('📱 Bấm "Thêm Cấu Hình" để tự động mở ứng dụng. Nếu đã cài app, sẽ tự động mở. Nếu không mở, vui lòng tải từ Store bên dưới.', 'info');
});

// Theo dõi khi người dùng quay lại trang
let wasHidden = false;
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        wasHidden = true;
    } else if (wasHidden) {
        const btn = document.getElementById('openAppBtn');
        if (btn.disabled) {
            btn.disabled = false;
        }
        btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
        showStatus('💡 Nếu bạn vừa cài đặt ứng dụng, hãy bấm "Thử Lại" để mở app.', 'info');
        wasHidden = false;
    }
});

// Tự động mở ứng dụng nếu có tham số auto=1
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auto') === '1') {
    setTimeout(() => {
        openVPNApp();
    }, 500);
}
