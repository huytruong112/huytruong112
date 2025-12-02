// VLESS Connection Script - Improved Detection
// Tự động mở app nếu đã cài, chỉ chuyển Store nếu chưa có

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

// Hàm thử mở app - IMPROVED: Better detection
function tryOpenApp(deepLink, appName, timeout = 3000) {
    return new Promise((resolve) => {
        let appOpened = false;
        let checkTimer;
        const startTime = Date.now();
        
        // Tạo iframe ẩn để thử mở deep link
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.style.width = '0';
        iframe.style.height = '0';
        
        const handleBlur = () => {
            appOpened = true;
            cleanup();
            resolve(true);
        };
        
        const handleVisibilityChange = () => {
            if (document.hidden) {
                appOpened = true;
                cleanup();
                resolve(true);
            }
        };
        
        // Check nếu user rời khỏi trang (app đã mở)
        const handlePageHide = () => {
            appOpened = true;
            cleanup();
            resolve(true);
        };
        
        const cleanup = () => {
            clearTimeout(checkTimer);
            window.removeEventListener('blur', handleBlur);
            window.removeEventListener('pagehide', handlePageHide);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            setTimeout(() => {
                if (iframe.parentNode) {
                    document.body.removeChild(iframe);
                }
            }, 100);
        };
        
        // Thêm các event listeners
        window.addEventListener('blur', handleBlur);
        window.addEventListener('pagehide', handlePageHide);
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Set deep link và thêm vào body
        iframe.src = deepLink;
        document.body.appendChild(iframe);
        
        // Alternative: Cũng thử với window.location cho iOS
        setTimeout(() => {
            if (!appOpened) {
                window.location.href = deepLink;
            }
        }, 100);
        
        // Timeout check - kiểm tra kỹ hơn
        checkTimer = setTimeout(() => {
            const elapsed = Date.now() - startTime;
            
            // Nếu trang vẫn còn focus sau timeout → app không có
            if (!appOpened && !document.hidden && document.hasFocus()) {
                cleanup();
                resolve(false);
            } else if (appOpened || document.hidden) {
                // App đã mở hoặc đang mở
                cleanup();
                resolve(true);
            } else {
                // Trường hợp không chắc chắn → cho là app đã mở
                cleanup();
                resolve(true);
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

// iOS Logic - IMPROVED
async function openVPNAppiOS(btn) {
    const appStoreStreisand = 'https://apps.apple.com/app/streisand/id6450534064';
    const appStoreSingBox = 'https://apps.apple.com/app/sing-box/id6451272673';
    
    // Bước 1: Thử Streisand với timeout dài hơn
    showStatus('🔍 Đang kiểm tra Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const streisandDeepLink = vlessUri;
    const streisandOpened = await tryOpenApp(streisandDeepLink, 'Streisand', 3000);
    
    if (streisandOpened) {
        showStatus('✅ Streisand đã mở! Đang thêm cấu hình tự động...', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Kết Nối';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box
    showStatus('🔍 Đang kiểm tra sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    const singBoxDeepLink = vlessUri;
    const singBoxOpened = await tryOpenApp(singBoxDeepLink, 'sing-box', 3000);
    
    if (singBoxOpened) {
        showStatus('✅ sing-box đã mở! Đang thêm cấu hình tự động...', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Kết Nối';
        }, 2000);
        return;
    }
    
    // Bước 3: Không có app nào → Chuyển Store
    showStatus('⚠️ Chưa cài ứng dụng. Đang chuyển đến App Store để tải Streisand...', 'warning');
    btn.innerHTML = '<span class="spinner"></span> Đang mở App Store...';
    
    setTimeout(() => {
        window.location.href = appStoreStreisand;
    }, 1500);
}

// Android Logic - IMPROVED
async function openVPNAppAndroid(btn) {
    const playStoreStreisand = 'https://play.google.com/store/apps/details?id=com.github.shadowsocks.tv.vpn';
    const playStoreSingBox = 'https://play.google.com/store/apps/details?id=io.nekohasekai.sfa';
    
    // Bước 1: Thử Streisand với timeout dài hơn
    showStatus('🔍 Đang kiểm tra Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const streisandIntent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=com.github.shadowsocks.tv.vpn;S.browser_fallback_url=${encodeURIComponent(playStoreStreisand)};end`;
    const streisandOpened = await tryOpenApp(streisandIntent, 'Streisand', 3000);
    
    if (streisandOpened) {
        showStatus('✅ Streisand đã mở! Đang thêm cấu hình tự động...', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Kết Nối';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box
    showStatus('🔍 Đang kiểm tra sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    const singBoxIntent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=io.nekohasekai.sfa;S.browser_fallback_url=${encodeURIComponent(playStoreSingBox)};end`;
    const singBoxOpened = await tryOpenApp(singBoxIntent, 'sing-box', 3000);
    
    if (singBoxOpened) {
        showStatus('✅ sing-box đã mở! Đang thêm cấu hình tự động...', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Kết Nối';
        }, 2000);
        return;
    }
    
    // Bước 3: Không có app nào → Chuyển Store
    showStatus('⚠️ Chưa cài ứng dụng. Đang chuyển đến Google Play để tải Streisand...', 'warning');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Google Play...';
    
    setTimeout(() => {
        window.location.href = playStoreStreisand;
    }, 1500);
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
    // Copy URI vào clipboard
    copyToClipboard();

    // Hiển thị thông báo hướng dẫn
    showStatus('📱 Bấm nút "Thêm Cấu Hình" để tự động kết nối. Nếu đã cài app, sẽ mở ngay. Nếu chưa cài, sẽ chuyển đến Store.', 'warning');
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
        showStatus('💡 Nếu bạn vừa cài đặt ứng dụng, hãy bấm "Thử Lại" để tự động thêm cấu hình.', 'warning');
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
