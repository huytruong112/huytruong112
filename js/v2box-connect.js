// V2Box Connection Script
// Biến toàn cục được truyền từ PHP
let vlessUri;
let vlessUriEncoded;

// Khởi tạo biến từ PHP
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
    statusDiv.className = type === 'success' ? 'status-success' : 'status-warning';
    statusDiv.style.display = 'block';
}

function openV2Box() {
    const device = detectDevice();
    const btn = document.getElementById('openAppBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang thêm cấu hình...';
    const appStoreUrl = 'https://apps.apple.com/app/v2box/id6446814690';
    const playStoreUrl = 'https://play.google.com/store/apps/details?id=dev.hexasoftware.v2box';

    if (device === 'iOS') {
        const deepLink = vlessUri; 
        
        let appOpened = false;
        const handleBlur = () => {
            appOpened = true;
        };
        window.addEventListener('blur', handleBlur);
        const handleVisibilityChange = () => {
            if (document.hidden) {
                appOpened = true;
                clearTimeout(checkTimer);
                showStatus('✅ Đã thêm cấu hình vào V2Box thành công!', 'success');
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
                }, 2000);
                window.removeEventListener('blur', handleBlur);
                document.removeEventListener('visibilitychange', handleVisibilityChange);
            }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.location.href = deepLink;
        const checkTimer = setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                showStatus('⚠️ V2Box chưa được cài đặt. Đang chuyển đến App Store để tải...', 'warning');
                btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến App Store...';
                setTimeout(() => {
                    window.location.href = appStoreUrl;
                }, 1000);
            }
        }, 2500);

    } else if (device === 'Android') {
        const intent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=dev.hexasoftware.v2box;end`;
        
        let appOpened = false;
        const handleBlur = () => {
            appOpened = true;
        };
        window.addEventListener('blur', handleBlur);
        const handleVisibilityChange = () => {
            if (document.hidden) {
                appOpened = true;
                clearTimeout(checkTimer);
                showStatus('✅ Đã thêm cấu hình vào V2Box thành công!', 'success');
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
                }, 2000);
                window.removeEventListener('blur', handleBlur);
                document.removeEventListener('visibilitychange', handleVisibilityChange);
            }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.location.href = intent;
        const checkTimer = setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                showStatus('⚠️ V2Box chưa được cài đặt. Đang chuyển đến Google Play để tải...', 'warning');
                btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến Google Play...';
                setTimeout(() => {
                    window.location.href = playStoreUrl;
                }, 1000);
            }
        }, 2500);

    } else {
        showStatus('⚠️ V2Box chỉ khả dụng trên iOS và Android. Vui lòng sử dụng thiết bị di động hoặc quét mã QR bằng ứng dụng.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
    }
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
    showStatus('📱 Bấm nút "Thêm Cấu Hình" để tự động mở V2Box và thêm cấu hình VLESS.', 'warning');
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
        showStatus('💡 Nếu bạn vừa cài đặt V2Box, hãy bấm "Thử Lại" để tự động thêm cấu hình vào ứng dụng.', 'warning');
        wasHidden = false;
    }
});

// Tự động mở ứng dụng nếu có tham số auto=1
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auto') === '1') {
    setTimeout(() => {
        openV2Box();
    }, 500);
}
