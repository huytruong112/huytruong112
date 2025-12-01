/**
 * VLESS Open Page JavaScript
 * Deep linking and V2Box integration
 * Original logic preserved 100%
 */

// Detect thiết bị
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

// Hiển thị thông báo trạng thái
function showStatus(message, type = 'success') {
    const statusDiv = document.getElementById('status-message');
    statusDiv.innerHTML = message;
    statusDiv.className = type === 'success' ? 'status-success' : 'status-warning';
    statusDiv.style.display = 'block';
}

// Mở ứng dụng V2Box và tự động thêm cấu hình VLESS
function openV2Box() {
    const device = detectDevice();
    const btn = document.getElementById('openAppBtn');
    
    // Vô hiệu hóa nút trong khi xử lý
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Đang thêm cấu hình...';

    // Store links
    const appStoreUrl = 'https://apps.apple.com/app/v2box/id6446814690';
    const playStoreUrl = 'https://play.google.com/store/apps/details?id=dev.hexasoftware.v2box';

    if (device === 'iOS') {
        // iOS - Tự động mở V2Box và thêm cấu hình VLESS
        const deepLink = vlessUri; // Deep link trực tiếp với VLESS URI
        
        let appOpened = false;

        // Lắng nghe sự kiện blur (khi chuyển sang app khác)
        const handleBlur = () => {
            appOpened = true;
        };
        window.addEventListener('blur', handleBlur);

        // Lắng nghe visibility change (phương pháp đáng tin cậy nhất)
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

        // Mở ứng dụng V2Box với cấu hình VLESS
        window.location.href = deepLink;

        // Kiểm tra sau 2.5 giây
        const checkTimer = setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                // V2Box chưa được cài đặt - Chuyển sang App Store
                showStatus('⚠️ V2Box chưa được cài đặt. Đang chuyển đến App Store để tải...', 'warning');
                btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến App Store...';
                setTimeout(() => {
                    window.location.href = appStoreUrl;
                }, 1000);
            }
        }, 2500);

    } else if (device === 'Android') {
        // Android - Tự động mở V2Box và thêm cấu hình VLESS
        // Intent scheme để mở V2Box với VLESS URI
        const intent = `intent:${vlessUri.replace('vless://', '')}#Intent;scheme=vless;package=dev.hexasoftware.v2box;end`;
        
        let appOpened = false;

        // Lắng nghe sự kiện blur
        const handleBlur = () => {
            appOpened = true;
        };
        window.addEventListener('blur', handleBlur);

        // Lắng nghe visibility change
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

        // Mở ứng dụng V2Box với cấu hình VLESS
        window.location.href = intent;

        // Kiểm tra sau 2.5 giây
        const checkTimer = setTimeout(() => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            
            if (!appOpened && !document.hidden) {
                // V2Box chưa được cài đặt - Chuyển sang Google Play
                showStatus('⚠️ V2Box chưa được cài đặt. Đang chuyển đến Google Play để tải...', 'warning');
                btn.innerHTML = '<span class="spinner"></span> Đang chuyển đến Google Play...';
                setTimeout(() => {
                    window.location.href = playStoreUrl;
                }, 1000);
            }
        }, 2500);

    } else {
        // Desktop hoặc thiết bị khác
        showStatus('⚠️ V2Box chỉ khả dụng trên iOS và Android. Vui lòng sử dụng thiết bị di động hoặc quét mã QR bằng ứng dụng.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
    }
}

// Tự động copy URI vào clipboard
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

// Copy URI và hiển thị hướng dẫn khi trang load
window.addEventListener('load', () => {
    // Copy URI để người dùng có thể paste thủ công nếu cần
    copyToClipboard();
    
    // Hiển thị thông báo hướng dẫn
    showStatus('📱 Bấm nút "Thêm Cấu Hình" để tự động mở V2Box và thêm cấu hình VLESS.', 'warning');
});

// Xử lý khi quay lại từ App Store/Play Store
let wasHidden = false;
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        wasHidden = true;
    } else if (wasHidden) {
        // User quay lại từ Store (có thể đã cài app)
        const btn = document.getElementById('openAppBtn');
        if (btn.disabled) {
            btn.disabled = false;
        }
        btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
        showStatus('💡 Nếu bạn vừa cài đặt V2Box, hãy bấm "Thử Lại" để tự động thêm cấu hình vào ứng dụng.', 'warning');
        wasHidden = false;
    }
});

// Tự động mở app nếu có tham số auto=1
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auto') === '1') {
    setTimeout(() => {
        openV2Box();
    }, 500);
}
