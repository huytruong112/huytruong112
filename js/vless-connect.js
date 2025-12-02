// VLESS Connection Script - SAFARI FIXED
// Fix lỗi: "Safari không thể mở trang này, vì địa chỉ không hợp lệ"

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

function isSafari() {
    const ua = navigator.userAgent;
    return /Safari/.test(ua) && !/Chrome/.test(ua) && !/CriOS/.test(ua);
}

function showStatus(message, type = 'success') {
    const statusDiv = document.getElementById('status-message');
    statusDiv.innerHTML = message;
    statusDiv.className = type === 'success' ? 'status-success' : (type === 'info' ? 'status-info' : 'status-warning');
    statusDiv.style.display = 'block';
}

// Hàm copy URI vào clipboard
async function copyURIToClipboard() {
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(vlessUri);
            console.log('✓ VLESS URI copied to clipboard');
            return true;
        }
    } catch (err) {
        console.error('Failed to copy:', err);
    }
    return false;
}

// Hàm thử mở app - CHO SAFARI
function tryOpenAppSafari(appScheme, appName, timeout = 3000) {
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
            console.log('Window blur - App opened');
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
        
        // Safari: Dùng window.location trực tiếp (KHÔNG dùng iframe)
        // Chỉ dùng app scheme đơn giản, KHÔNG truyền full VLESS URI
        try {
            // Copy URI vào clipboard trước
            copyURIToClipboard();
            
            // Mở app với scheme đơn giản
            window.location.href = appScheme;
            console.log('Opening app with scheme:', appScheme);
        } catch (e) {
            console.error('Error opening app:', e);
        }
        
        // Timeout check
        setTimeout(() => {
            cleanup();
            
            if (!resolved) {
                const elapsed = Date.now() - startTime;
                console.log(`Timeout after ${elapsed}ms`);
                
                // Kiểm tra nếu trang vẫn visible → app không có
                if (!document.hidden && document.hasFocus()) {
                    resolveOnce(false);
                } else {
                    resolveOnce(true);
                }
            }
        }, timeout);
    });
}

// Hàm thử mở app - CHO ANDROID/CHROME
function tryOpenAppAndroid(deepLink, appName, timeout = 3000) {
    return new Promise((resolve) => {
        let resolved = false;
        
        const resolveOnce = (success) => {
            if (!resolved) {
                resolved = true;
                resolve(success);
            }
        };
        
        const handleBlur = () => {
            console.log('Window blur - App opened');
            resolveOnce(true);
        };
        
        const handleVisibilityChange = () => {
            if (document.hidden) {
                console.log('Document hidden - App opened');
                resolveOnce(true);
            }
        };
        
        window.addEventListener('blur', handleBlur);
        document.addEventListener('visibilitychange', handleVisibilityChange);
        
        const cleanup = () => {
            window.removeEventListener('blur', handleBlur);
            document.removeEventListener('visibilitychange', handleVisibilityChange);
        };
        
        // Android: Dùng intent URL
        try {
            window.location.href = deepLink;
            console.log('Opening app with deep link:', deepLink);
        } catch (e) {
            console.error('Error opening deep link:', e);
        }
        
        setTimeout(() => {
            cleanup();
            
            if (!resolved) {
                if (!document.hidden && document.hasFocus()) {
                    resolveOnce(false);
                } else {
                    resolveOnce(true);
                }
            }
        }, timeout);
    });
}

// Logic cascade chính
async function openVPNApp() {
    const device = detectDevice();
    const safari = isSafari();
    const btn = document.getElementById('openAppBtn');
    btn.disabled = true;
    
    console.log('Device:', device, 'Safari:', safari);
    
    if (device === 'iOS') {
        await openVPNAppiOS(btn, safari);
    } else if (device === 'Android') {
        await openVPNAppAndroid(btn);
    } else {
        showStatus('⚠️ Tính năng này chỉ khả dụng trên iOS và Android. Vui lòng quét mã QR.', 'warning');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus-circle"></i> Thêm Cấu Hình';
    }
}

// iOS Logic - SAFARI COMPATIBLE
async function openVPNAppiOS(btn, safari) {
    const appStoreStreisand = 'https://apps.apple.com/app/streisand/id6450534064';
    const appStoreSingBox = 'https://apps.apple.com/app/sing-box/id6451272673';
    
    // Copy URI vào clipboard trước (cho cả Safari và Chrome)
    await copyURIToClipboard();
    
    if (safari) {
        // SAFARI: Dùng app scheme đơn giản
        showStatus('🔍 Đang mở Streisand... (URI đã copy vào clipboard)', 'info');
        btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
        
        // Streisand app scheme (đơn giản, không có full URI)
        const streisandScheme = 'streisand://';
        const streisandOpened = await tryOpenAppSafari(streisandScheme, 'Streisand', 3000);
        
        if (streisandOpened) {
            showStatus('✅ Streisand đã mở! Vui lòng PASTE (dán) cấu hình từ clipboard vào ứng dụng.', 'success');
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
            }, 2000);
            return;
        }
        
        // sing-box
        showStatus('🔍 Đang mở sing-box... (URI đã copy vào clipboard)', 'info');
        btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
        
        const singBoxScheme = 'sing-box://';
        const singBoxOpened = await tryOpenAppSafari(singBoxScheme, 'sing-box', 3000);
        
        if (singBoxOpened) {
            showStatus('✅ sing-box đã mở! Vui lòng PASTE (dán) cấu hình từ clipboard vào ứng dụng.', 'success');
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
            }, 2000);
            return;
        }
        
    } else {
        // CHROME iOS: Thử dùng full VLESS deep link
        showStatus('🔍 Đang mở Streisand...', 'info');
        btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
        
        const streisandDeepLink = vlessUri;
        const streisandOpened = await tryOpenAppAndroid(streisandDeepLink, 'Streisand', 3000);
        
        if (streisandOpened) {
            showStatus('✅ Streisand đã mở! Cấu hình sẽ tự động được thêm.', 'success');
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
            }, 2000);
            return;
        }
        
        showStatus('🔍 Đang mở sing-box...', 'info');
        btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
        
        const singBoxDeepLink = vlessUri;
        const singBoxOpened = await tryOpenAppAndroid(singBoxDeepLink, 'sing-box', 3000);
        
        if (singBoxOpened) {
            showStatus('✅ sing-box đã mở! Cấu hình sẽ tự động được thêm.', 'success');
            setTimeout(() => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
            }, 2000);
            return;
        }
    }
    
    // Không tìm thấy app
    showStatus('⚠️ Không tìm thấy ứng dụng. Vui lòng tải từ App Store bên dưới.', 'warning');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
    
    const storeLinks = document.querySelectorAll('.store-link');
    storeLinks.forEach(link => {
        link.style.border = '3px solid #ff0000';
        link.style.animation = 'pulse 1s infinite';
    });
}

// Android Logic - VỚI FULL VLESS URI
async function openVPNAppAndroid(btn) {
    const playStoreStreisand = 'https://play.google.com/store/apps/details?id=com.github.shadowsocks.tv.vpn';
    const playStoreSingBox = 'https://play.google.com/store/apps/details?id=io.nekohasekai.sfa';
    
    // Copy URI vào clipboard (backup)
    await copyURIToClipboard();
    
    // Bước 1: Thử Streisand với FULL VLESS URI
    showStatus('🔍 Đang mở Streisand...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở Streisand...';
    
    // Android Intent với full VLESS URI
    const vlessData = vlessUri.replace('vless://', '');
    const streisandIntent = `intent://${vlessData}#Intent;scheme=vless;package=com.github.shadowsocks.tv.vpn;end`;
    console.log('Streisand intent:', streisandIntent);
    const streisandOpened = await tryOpenAppAndroid(streisandIntent, 'Streisand', 3000);
    
    if (streisandOpened) {
        showStatus('✅ Streisand đã mở! Cấu hình sẽ tự động được thêm.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
        }, 2000);
        return;
    }
    
    // Bước 2: Thử sing-box
    showStatus('🔍 Đang mở sing-box...', 'info');
    btn.innerHTML = '<span class="spinner"></span> Đang mở sing-box...';
    
    const singBoxIntent = `intent://${vlessData}#Intent;scheme=vless;package=io.nekohasekai.sfa;end`;
    console.log('sing-box intent:', singBoxIntent);
    const singBoxOpened = await tryOpenAppAndroid(singBoxIntent, 'sing-box', 3000);
    
    if (singBoxOpened) {
        showStatus('✅ sing-box đã mở! Cấu hình sẽ tự động được thêm.', 'success');
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Đã Mở App';
        }, 2000);
        return;
    }
    
    // Không tìm thấy app
    showStatus('⚠️ Không tìm thấy ứng dụng. Vui lòng tải từ Google Play bên dưới.', 'warning');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-redo"></i> Thử Lại';
    
    const storeLinks = document.querySelectorAll('.store-link');
    storeLinks.forEach(link => {
        link.style.border = '3px solid #ff0000';
        link.style.animation = 'pulse 1s infinite';
    });
}

// Khởi tạo khi trang load
window.addEventListener('load', () => {
    copyURIToClipboard();
    const safari = isSafari();
    if (safari) {
        showStatus('📱 Safari đã được hỗ trợ! URI đã copy vào clipboard. Bấm "Thêm Cấu Hình" để mở app, sau đó PASTE vào ứng dụng.', 'info');
    } else {
        showStatus('📱 Bấm "Thêm Cấu Hình" để tự động mở ứng dụng và thêm cấu hình.', 'info');
    }
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
        showStatus('💡 Nếu bạn vừa cài đặt ứng dụng, hãy bấm "Thử Lại".', 'info');
        wasHidden = false;
    }
});
