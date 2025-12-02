// WireGuard Connection Script
// Biến toàn cục được truyền từ PHP
let wgConfig;
let wgConfigBase64;
let wgPublicKey;

// Khởi tạo biến từ PHP
function initializeWireGuardConfig(config, configBase64, publicKey) {
    wgConfig = config;
    wgConfigBase64 = configBase64;
    wgPublicKey = publicKey;
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

function openWireGuard() {
    const device = detectDevice();
    const btn = document.getElementById('openAppBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang kết nối...';
    
    const appStoreUrl = 'https://apps.apple.com/us/app/wireguard/id1441195209';
    const playStoreUrl = 'https://play.google.com/store/apps/details?id=com.wireguard.android';

    if (device === 'iOS') {
        // iOS: Sử dụng wireguard:// URL scheme với base64 encoded config
        const deepLink = `wireguard://import-profile?contents=${encodeURIComponent(wgConfigBase64)}`;
        
        let appOpened = false;
        const handleBlur = () => {
            appOpened = true;
        };
        window.addEventListener('blur', handleBlur);
        
        const handleVisibilityChange = () => {
            if (document.hidden) {
                appOpened = true;
                clearTimeout(checkTimer);
                showStatus('✅ Đã mở WireGuard thành công! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-plug"></i> Kết Nối Ngay';
                }, 2000);
                window.removeEventListener('blur', handleBlur);
                document.removeEventListener('visibilitychange', handleVisibilityChange);
            }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Thử mở ứng dụng
        window.location.href = deepLink;
        
        const checkTimer = setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                showStatus('⚠️ WireGuard chưa được cài đặt. Đang chuyển đến App Store để tải...', 'warning');
                btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến App Store...';
                setTimeout(() => {
                    window.location.href = appStoreUrl;
                }, 1000);
            }
        }, 2500);

    } else if (device === 'Android') {
        // Android: Sử dụng Intent với config text
        const intent = `intent://import-profile?contents=${encodeURIComponent(wgConfigBase64)}#Intent;scheme=wireguard;package=com.wireguard.android;end`;
        
        let appOpened = false;
        const handleBlur = () => {
            appOpened = true;
        };
        window.addEventListener('blur', handleBlur);
        
        const handleVisibilityChange = () => {
            if (document.hidden) {
                appOpened = true;
                clearTimeout(checkTimer);
                showStatus('✅ Đã mở WireGuard thành công! Vui lòng xác nhận thêm cấu hình trong ứng dụng.', 'success');
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fas fa-plug"></i> Kết Nối Ngay';
                }, 2000);
                window.removeEventListener('blur', handleBlur);
                document.removeEventListener('visibilitychange', handleVisibilityChange);
            }
        };
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        // Thử mở ứng dụng
        window.location.href = intent;
        
        const checkTimer = setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                showStatus('⚠️ WireGuard chưa được cài đặt. Đang chuyển đến Google Play để tải...', 'warning');
                btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến Google Play...';
                setTimeout(() => {
                    window.location.href = playStoreUrl;
                }, 1000);
            }
        }, 2500);

    } else {
        showStatus('⚠️ WireGuard chỉ khả dụng trên iOS và Android. Vui lòng sử dụng thiết bị di động hoặc quét mã QR bằng ứng dụng.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plug"></i> Kết Nối Ngay';
    }
}

function copyPublicKey() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(wgPublicKey)
            .then(() => {
                showStatus('✓ Public Key đã được copy vào clipboard', 'success');
                setTimeout(() => {
                    document.getElementById('status-message').style.display = 'none';
                }, 2000);
            })
            .catch(err => {
                console.error('Lỗi khi copy:', err);
            });
    }
}

function copyConfigToClipboard() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(wgConfig)
            .then(() => {
                console.log('✓ WireGuard config đã được copy vào clipboard');
            })
            .catch(err => {
                console.error('Lỗi khi copy:', err);
            });
    }
}

// Khởi tạo khi trang load
window.addEventListener('load', () => {
    // Copy config vào clipboard để dễ dàng paste thủ công nếu cần
    copyConfigToClipboard();

    // Hiển thị thông báo hướng dẫn
    showStatus('📱 Bấm nút "Kết Nối Ngay" để tự động mở WireGuard và thêm cấu hình VPN.', 'warning');
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
        showStatus('💡 Nếu bạn vừa cài đặt WireGuard, hãy bấm "Thử Lại" để tự động thêm cấu hình vào ứng dụng.', 'warning');
        wasHidden = false;
    }
});

// Tự động mở ứng dụng nếu có tham số auto=1
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auto') === '1') {
    setTimeout(() => {
        openWireGuard();
    }, 500);
}
