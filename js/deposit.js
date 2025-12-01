/**
 * Deposit Page JavaScript
 * Security: Anti-debugging and source protection
 */

(function() {
  'use strict';
  
  // Anti-debugging protection
  const initSecurityProtection = () => {
    // Disable right-click context menu
    document.body.oncontextmenu = () => false;
    
    // Disable copy, cut, select
    document.body.oncopy = () => false;
    document.body.oncut = () => false;
    document.body.onselectstart = () => false;
    
    // Disable keyboard shortcuts
    document.body.onkeydown = function(e) {
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
  
  // Check balance automatically (every 10 seconds)
  let currentBalance = null;
  
  const initBalanceChecker = (initialBalance) => {
    currentBalance = initialBalance;
    
    setInterval(() => {
      fetch('check_balance.php')
        .then(response => response.json())
        .then(data => {
          if (typeof data.balance !== 'undefined' && data.balance != currentBalance) {
            location.reload();
          }
        })
        .catch(error => {
          console.error('Balance check error:', error);
        });
    }, 10000); // 10 seconds
  };
  
  // Refresh transaction status
  const initTransactionStatusRefresh = (transactionCode) => {
    const btnRefresh = document.getElementById('btn-refresh-status');
    if (!btnRefresh || !transactionCode) return;
    
    btnRefresh.addEventListener('click', () => {
      fetch('check_transaction_status.php?code=' + encodeURIComponent(transactionCode))
        .then(response => response.json())
        .then(data => {
          const statusSpan = document.getElementById('transaction-status');
          if (!statusSpan) return;
          
          if (data.status === 'success' || data.status === 'Thành công') {
            statusSpan.innerHTML = '<span class="badge text-bg-success">Đã Thanh Toán</span>';
          } else if (data.status === 'pending') {
            statusSpan.innerHTML = '<span class="badge text-bg-warning">Chờ xử lý</span>';
          } else if (data.status) {
            statusSpan.innerHTML = '<span class="badge text-bg-secondary">' + escapeHtml(data.status) + '</span>';
          } else {
            statusSpan.innerHTML = '<span class="badge text-bg-secondary">Không rõ</span>';
          }
        })
        .catch(error => {
          console.error('Transaction status check error:', error);
        });
    });
  };
  
  // View transaction detail modal
  const initTransactionDetailButtons = () => {
    document.querySelectorAll('.btn-detail-transaction').forEach(btn => {
      btn.addEventListener('click', function() {
        const transactionId = this.getAttribute('data-transaction-id');
        const modalBody = document.getElementById('transaction-detail-modal-content');
        
        if (!modalBody) return;
        
        modalBody.innerHTML = '<div class="text-center text-secondary">Đang tải...</div>';
        
        fetch('transaction_detail.php?id=' + encodeURIComponent(transactionId))
          .then(response => response.text())
          .then(html => {
            modalBody.innerHTML = html;
          })
          .catch(error => {
            console.error('Transaction detail error:', error);
            modalBody.innerHTML = '<div class="text-danger">Không lấy được dữ liệu!</div>';
          });
        
        // Show modal using Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
          const modalElement = document.getElementById('transactionDetailModal');
          if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
          }
        }
      });
    });
  };
  
  // Escape HTML to prevent XSS
  const escapeHtml = (text) => {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  };
  
  // Initialize all features on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    // Initialize security protection
    initSecurityProtection();
    
    // Get initial balance from page
    const balanceElement = document.getElementById('userBalance');
    if (balanceElement) {
      const balanceText = balanceElement.textContent.trim();
      const balanceValue = parseFloat(balanceText.replace(/[^0-9.-]+/g, ''));
      if (!isNaN(balanceValue)) {
        initBalanceChecker(balanceValue);
      }
    }
    
    // Get transaction code from URL if present
    const urlParams = new URLSearchParams(window.location.search);
    const transactionCode = urlParams.get('code');
    if (transactionCode) {
      initTransactionStatusRefresh(transactionCode);
    }
    
    // Initialize transaction detail buttons
    initTransactionDetailButtons();
    
    // Console warning
    console.log('%cStop!', 'color: red; font-size: 50px; font-weight: bold;');
    console.log('%cĐây là tính năng dành cho nhà phát triển. Nếu ai đó bảo bạn sao chép-dán nội dung vào đây, đó là hành vi lừa đảo.', 'font-size: 16px;');
  });
  
  // Prevent console debugging
  setInterval(() => {
    debugger;
  }, 100);
  
  // Expose necessary functions to global scope if needed
  window.depositPageInit = {
    initialized: true,
    version: '1.0.0'
  };
  
})();
