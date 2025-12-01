/**
 * Manage Services JavaScript
 * Security: Anti-debugging and source protection
 */

(function() {
  'use strict';
  
  // Anti-debugging protection
  const initSecurityProtection = () => {
    // Disable right-click context menu (except on input fields)
    document.body.oncontextmenu = (e) => {
      const target = e.target;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
        return true; // Allow context menu on form fields
      }
      return false;
    };
    
    // Disable copy, cut, select (except on input fields)
    document.body.oncopy = (e) => {
      const target = e.target;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
        return true; // Allow copy in form fields
      }
      return false;
    };
    
    document.body.oncut = (e) => {
      const target = e.target;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
        return true; // Allow cut in form fields
      }
      return false;
    };
    
    document.body.onselectstart = (e) => {
      const target = e.target;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') {
        return true; // Allow selection in form fields
      }
      return false;
    };
    
    // Disable keyboard shortcuts (except in input fields)
    document.body.onkeydown = function(e) {
      const target = e.target;
      const isFormField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT';
      
      // Allow all keys in form fields
      if (isFormField) {
        return true;
      }
      
      // Block Ctrl+C, Ctrl+U, Ctrl+S
      if (e.ctrlKey && (e.key === 'c' || e.key === 'u' || e.key === 's')) {
        e.preventDefault();
        return false;
      }
      
      // Block F12
      if (e.key === 'F12') {
        e.preventDefault();
        return false;
      }
      
      // Block Ctrl+Shift+I (DevTools)
      if (e.ctrlKey && e.shiftKey && e.key === 'I') {
        e.preventDefault();
        return false;
      }
    };
  };
  
  // Copy public key block to clipboard
  window.copyBlock = function(id) {
    const element = document.getElementById(id);
    if (!element) return;
    
    const content = element.innerText;
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(content)
        .then(() => {
          showNotification('Đã sao chép cấu hình!', 'success');
        })
        .catch(() => {
          fallbackCopy(element);
        });
    } else {
      fallbackCopy(element);
    }
  };
  
  // Fallback copy method
  function fallbackCopy(element) {
    try {
      const range = document.createRange();
      range.selectNodeContents(element);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand('copy');
      showNotification('Đã sao chép cấu hình public key!', 'success');
    } catch (err) {
      showNotification('Không thể sao chép. Vui lòng thử lại.', 'error');
    }
  }
  
  // Copy text to clipboard
  window.copyText = function(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(() => {
          showNotification('Đã copy VLESS URI', 'success');
        })
        .catch(() => {
          showManualCopyDialog(text);
        });
    } else {
      showManualCopyDialog(text);
    }
  };
  
  // Show manual copy dialog
  function showManualCopyDialog(text) {
    const message = 'VLESS URI:\n\n' + text;
    alert(message);
  }
  
  // Show notification
  function showNotification(message, type = 'success') {
    // Try to use alert or custom notification
    if (typeof alert !== 'undefined') {
      alert(message);
    }
  }
  
  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    initSecurityProtection();
    
    // Additional initialization
    console.log('%cStop!', 'color: red; font-size: 50px; font-weight: bold;');
    console.log('%cĐây là tính năng dành cho nhà phát triển. Nếu ai đó bảo bạn sao chép-dán nội dung vào đây, đó là hành vi lừa đảo.', 'font-size: 16px;');
  });
  
  // Prevent console debugging
  setInterval(() => {
    debugger;
  }, 100);
  
})();
