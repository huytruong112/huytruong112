/**
 * SECURITY CONFIGURATION FILE
 * Cấu hình các tính năng bảo mật cho trang thanh toán
 * 
 * Cách sử dụng: Include file này trong <head> của pay.php
 * <script src="security-config.js"></script>
 */

const SECURITY_CONFIG = {
  // ================== CÁC TÍNH NĂNG BẢO MẬT ==================
  
  // Phát hiện và chặn DevTools
  ANTI_DEVTOOLS: {
    enabled: true,
    redirectUrl: 'about:blank',  // URL chuyển hướng khi phát hiện DevTools
    checkInterval: 1000,          // Kiểm tra mỗi 1 giây
    threshold: 160                // Ngưỡng phát hiện (pixels)
  },
  
  // Vô hiệu hóa Console
  CONSOLE_PROTECTION: {
    enabled: true,
    clearInterval: 100,           // Xóa console mỗi 100ms
    overrideConsole: true         // Override console methods
  },
  
  // Chặn chuột phải
  DISABLE_RIGHT_CLICK: {
    enabled: true,
    showMessage: false,           // Hiển thị thông báo khi chuột phải
    message: 'Chức năng này đã bị vô hiệu hóa!'
  },
  
  // Chặn phím tắt
  KEYBOARD_SHORTCUTS: {
    enabled: true,
    blockF12: true,               // Chặn F12 (DevTools)
    blockCtrlShiftI: true,        // Chặn Ctrl+Shift+I (Inspector)
    blockCtrlShiftJ: true,        // Chặn Ctrl+Shift+J (Console)
    blockCtrlShiftC: true,        // Chặn Ctrl+Shift+C (Element picker)
    blockCtrlU: true,             // Chặn Ctrl+U (View source)
    blockCtrlS: true,             // Chặn Ctrl+S (Save page)
    blockF11: true                // Chặn F11 (Fullscreen)
  },
  
  // Chặn select và copy
  COPY_PROTECTION: {
    enabled: true,
    disableSelection: true,       // Ngăn chọn text
    disableCopy: true,            // Ngăn copy
    disableCut: true,             // Ngăn cut
    disablePaste: true            // Ngăn paste
  },
  
  // Anti-debugger
  ANTI_DEBUGGER: {
    enabled: false,               // TẮT mặc định vì có thể gây lag
    interval: 100                 // Interval cho debugger trap
  },
  
  // Bảo vệ hình ảnh
  IMAGE_PROTECTION: {
    enabled: true,
    disableDrag: true,            // Ngăn kéo hình ảnh
    disableRightClick: true       // Ngăn chuột phải trên ảnh
  },
  
  // Watermark
  WATERMARK: {
    enabled: true,
    opacity: 0.03,                // Độ trong suốt
    color: '#000000',             // Màu
    pattern: 'diagonal'           // 'diagonal', 'grid', 'text'
  },
  
  // Theo dõi hành vi đáng ngờ
  SUSPICIOUS_ACTIVITY: {
    enabled: true,
    scoreThreshold: 10,           // Điểm ngưỡng trước khi chặn
    keyboardScore: 1,             // Điểm cho mỗi lần dùng Ctrl/Shift/Alt
    focusLossScore: 2,            // Điểm khi mất focus
    consoleAccessScore: 5,        // Điểm khi truy cập console
    actionOnThreshold: 'redirect' // 'redirect', 'alert', 'log'
  },
  
  // Chống iframe embedding
  ANTI_IFRAME: {
    enabled: true,
    action: 'breakout'            // 'breakout' hoặc 'blank'
  },
  
  // Chặn print/screenshot
  PRINT_PROTECTION: {
    enabled: true,
    hideOnPrint: true
  },
  
  // Chặn drag & drop
  DRAG_DROP_PROTECTION: {
    enabled: true
  },
  
  // ================== CÁC TÙYCHỌN NÂNG CAO ==================
  
  // Chế độ debug (tắt tất cả bảo mật)
  DEBUG_MODE: false,
  
  // Danh sách IP được phép (bỏ qua bảo mật)
  WHITELIST_IPS: [],
  
  // Log các hành vi đáng ngờ
  LOGGING: {
    enabled: true,
    logToConsole: false,          // TẮT vì console bị disable
    logToServer: false,           // Gửi log về server
    serverEndpoint: '/api/security-log.php'
  }
};

/**
 * Khởi tạo các biện pháp bảo mật
 */
(function initSecurity() {
  // Nếu debug mode = ON, tắt tất cả bảo mật
  if (SECURITY_CONFIG.DEBUG_MODE) {
    console.warn('🚨 SECURITY DEBUG MODE ENABLED - All protections disabled!');
    return;
  }
  
  // 1. Anti-DevTools
  if (SECURITY_CONFIG.ANTI_DEVTOOLS.enabled) {
    const detectDevTools = () => {
      const widthThreshold = window.outerWidth - window.innerWidth > SECURITY_CONFIG.ANTI_DEVTOOLS.threshold;
      const heightThreshold = window.outerHeight - window.innerHeight > SECURITY_CONFIG.ANTI_DEVTOOLS.threshold;
      if (widthThreshold || heightThreshold) {
        window.location.href = SECURITY_CONFIG.ANTI_DEVTOOLS.redirectUrl;
      }
    };
    detectDevTools();
    setInterval(detectDevTools, SECURITY_CONFIG.ANTI_DEVTOOLS.checkInterval);
  }
  
  // 2. Console Protection
  if (SECURITY_CONFIG.CONSOLE_PROTECTION.enabled) {
    if (SECURITY_CONFIG.CONSOLE_PROTECTION.overrideConsole) {
      const disabledConsole = {};
      ['log', 'warn', 'error', 'info', 'debug', 'table', 'trace', 'clear'].forEach(method => {
        disabledConsole[method] = function() {};
      });
      Object.defineProperty(window, 'console', {
        get: () => disabledConsole
      });
    }
    setInterval(() => { console.clear(); }, SECURITY_CONFIG.CONSOLE_PROTECTION.clearInterval);
  }
  
  // 3. Right-click Protection
  if (SECURITY_CONFIG.DISABLE_RIGHT_CLICK.enabled) {
    document.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      if (SECURITY_CONFIG.DISABLE_RIGHT_CLICK.showMessage) {
        alert(SECURITY_CONFIG.DISABLE_RIGHT_CLICK.message);
      }
      return false;
    });
  }
  
  // 4. Keyboard Shortcuts Protection
  if (SECURITY_CONFIG.KEYBOARD_SHORTCUTS.enabled) {
    document.addEventListener('keydown', (e) => {
      const cfg = SECURITY_CONFIG.KEYBOARD_SHORTCUTS;
      
      // F12
      if (cfg.blockF12 && e.keyCode === 123) {
        e.preventDefault();
        return false;
      }
      
      // Ctrl+Shift+I/J/C
      if (e.ctrlKey && e.shiftKey) {
        if ((cfg.blockCtrlShiftI && e.keyCode === 73) ||
            (cfg.blockCtrlShiftJ && e.keyCode === 74) ||
            (cfg.blockCtrlShiftC && e.keyCode === 67)) {
          e.preventDefault();
          return false;
        }
      }
      
      // Ctrl+U, Ctrl+S
      if (e.ctrlKey) {
        if ((cfg.blockCtrlU && e.keyCode === 85) ||
            (cfg.blockCtrlS && e.keyCode === 83)) {
          e.preventDefault();
          return false;
        }
      }
      
      // F11
      if (cfg.blockF11 && e.keyCode === 122) {
        e.preventDefault();
        return false;
      }
    });
  }
  
  // 5. Copy Protection
  if (SECURITY_CONFIG.COPY_PROTECTION.enabled) {
    if (SECURITY_CONFIG.COPY_PROTECTION.disableSelection) {
      document.addEventListener('selectstart', (e) => e.preventDefault());
      document.body.style.userSelect = 'none';
      document.body.style.webkitUserSelect = 'none';
      document.body.style.mozUserSelect = 'none';
      document.body.style.msUserSelect = 'none';
    }
    if (SECURITY_CONFIG.COPY_PROTECTION.disableCopy) {
      document.addEventListener('copy', (e) => e.preventDefault());
    }
    if (SECURITY_CONFIG.COPY_PROTECTION.disableCut) {
      document.addEventListener('cut', (e) => e.preventDefault());
    }
    if (SECURITY_CONFIG.COPY_PROTECTION.disablePaste) {
      document.addEventListener('paste', (e) => e.preventDefault());
    }
  }
  
  // 6. Anti-debugger
  if (SECURITY_CONFIG.ANTI_DEBUGGER.enabled) {
    setInterval(() => { debugger; }, SECURITY_CONFIG.ANTI_DEBUGGER.interval);
  }
  
  // 7. Image Protection
  if (SECURITY_CONFIG.IMAGE_PROTECTION.enabled) {
    document.addEventListener('DOMContentLoaded', () => {
      const images = document.querySelectorAll('img');
      images.forEach(img => {
        if (SECURITY_CONFIG.IMAGE_PROTECTION.disableDrag) {
          img.style.pointerEvents = 'none';
          img.style.userDrag = 'none';
          img.style.webkitUserDrag = 'none';
          img.addEventListener('dragstart', (e) => e.preventDefault());
        }
      });
    });
  }
  
  // 8. Watermark
  if (SECURITY_CONFIG.WATERMARK.enabled) {
    const watermark = document.createElement('div');
    watermark.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 9999;
      opacity: ${SECURITY_CONFIG.WATERMARK.opacity};
      background: repeating-linear-gradient(
        45deg,
        transparent,
        transparent 100px,
        ${SECURITY_CONFIG.WATERMARK.color} 100px,
        ${SECURITY_CONFIG.WATERMARK.color} 101px
      );
    `;
    document.body.appendChild(watermark);
  }
  
  // 9. Suspicious Activity Tracking
  if (SECURITY_CONFIG.SUSPICIOUS_ACTIVITY.enabled) {
    let suspiciousScore = 0;
    
    const handleSuspiciousActivity = () => {
      if (suspiciousScore >= SECURITY_CONFIG.SUSPICIOUS_ACTIVITY.scoreThreshold) {
        const action = SECURITY_CONFIG.SUSPICIOUS_ACTIVITY.actionOnThreshold;
        if (action === 'redirect') {
          window.location.href = 'about:blank';
        } else if (action === 'alert') {
          alert('Phát hiện hành vi đáng ngờ!');
        }
        suspiciousScore = 0; // Reset
      }
    };
    
    // Track keyboard
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.shiftKey || e.altKey) {
        suspiciousScore += SECURITY_CONFIG.SUSPICIOUS_ACTIVITY.keyboardScore;
        handleSuspiciousActivity();
      }
    });
    
    // Track focus loss
    window.addEventListener('blur', () => {
      suspiciousScore += SECURITY_CONFIG.SUSPICIOUS_ACTIVITY.focusLossScore;
      handleSuspiciousActivity();
    });
  }
  
  // 10. Anti-iframe
  if (SECURITY_CONFIG.ANTI_IFRAME.enabled) {
    if (window.top !== window.self) {
      if (SECURITY_CONFIG.ANTI_IFRAME.action === 'breakout') {
        window.top.location = window.self.location;
      } else {
        window.location.href = 'about:blank';
      }
    }
  }
  
  // 11. Print Protection
  if (SECURITY_CONFIG.PRINT_PROTECTION.enabled && SECURITY_CONFIG.PRINT_PROTECTION.hideOnPrint) {
    const style = document.createElement('style');
    style.textContent = '@media print { body { display: none !important; } }';
    document.head.appendChild(style);
  }
  
  // 12. Drag & Drop Protection
  if (SECURITY_CONFIG.DRAG_DROP_PROTECTION.enabled) {
    document.addEventListener('dragstart', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => e.preventDefault());
  }
  
  // Final cleanup before unload
  window.addEventListener('beforeunload', () => {
    console.clear();
  });
  
})();

// Export config (nếu cần)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SECURITY_CONFIG;
}
