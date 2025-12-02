// VLESS Connection Script - Cascade Logic
// Thứ tự: Streisand → sing-box → Store

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

// Hàm thử mở app với timeout
function tryOpenApp(deepLink, appName, timeout = 2000) {
    return new Promise((resolve) => {
        let appOpened = false;
        
        const handleBlur = () => {
            appOpened = true;
            resolve(true);
        };
        
        const handleVisibilityChange = () => {
            if (document.hidden) {
                appOpened = true;
                resolve(true);
            }
        };
        
        window.addEventListener('blur', handleBlur, { once: true });
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Thử mở app
        window.location.href = deepLink;
        
        // Timeout check
        setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                resolve(false);
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

// iOS Logic
async function openVPNAppiOS(btn) {
    const appStoreStreisand = 'https://apps.apple.com/app/streisand/id6450534064';
    const appStoreSingBox = 'https://apps.apple.com/app/sing-box/id6451272673';
    
    // Bước 1: Thử Streisand
    showStatus('🔍 Đang thử mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    const streisandDeepLink = vlessUri; // Streisand có thể dùng VLESS URI trực tiếp
    const streisandOpened = await tryOpenApp(streisandDeepLink, 'Streisand', 2000);
    
    if (streisandOpened) {
        showStatus('✅ Đã mở Streisand thành công! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box
    showStatus('🔍 Streisand không có, đang thử mở sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    const singBoxDeepLink = vlessUri; // sing-box cũng support VLESS URI
    const singBoxOpened = await tryOpenApp(singBoxDeepLink, 'sing-box', 2000);
    
    if (singBoxOpened) {
        showStatus('✅ Đã mở sing-box thành công! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
        }, 2000);
        return;
    }
    
    // Bước 3: Không có app nào → Chuyển Store
    showStatus('⚠️ Chưa cài ứng dụng. Đang chuyển đến App Store để tải Streisand...', 'warning');
    btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến App Store...';
    
    setTimeout(() => {
        window.location.href = appStoreStreisand;
    }, 1000);
}

// Android Logic
async function openVPNAppAndroid(btn) {
    const playStoreStreisand = 'https://play.google.com/store/apps/details?id=com.github.shadowsocks.tv.vpn';
    const playStoreSingBox = 'https://play.google.com/store/apps/details?id=io.nekohasekai.sfa';
    
    // Bước 1: Thử Streisand
    showStatus('🔍 Đang thử mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    // Android Intent cho Streisand (giả sử package name)
    const streisandIntent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=com.github.shadowsocks.tv.vpn;end`;
    const streisandOpened = await tryOpenApp(streisandIntent, 'Streisand', 2000);
    
    if (streisandOpened) {
        showStatus('✅ Đã mở Streisand thành công! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box
    showStatus('🔍 Streisand không có, đang thử mở sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    // Android Intent cho sing-box
    const singBoxIntent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=io.nekohasekai.sfa;end`;
    const singBoxOpened = await tryOpenApp(singBoxIntent, 'sing-box', 2000);
    
    if (singBoxOpened) {
        showStatus('✅ Đã mở sing-box thành công! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
        }, 2000);
        return;
    }
    
    // Bước 3: Không có app nào → Chuyển Store
    showStatus('⚠️ Chưa cài ứng dụng. Đang chuyển đến Google Play để tải Streisand...', 'warning');
    btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến Google Play...';
    
    setTimeout(() => {
        window.location.href = playStoreStreisand;
    }, 1000);
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
    showStatus('📱 Bấm nút "Thêm Cấu Hình" để tự động mở Streisand hoặc sing-box và thêm cấu hình VLESS.', 'warning');
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
