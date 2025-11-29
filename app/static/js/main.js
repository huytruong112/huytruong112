// Main JavaScript for Registration Page

const API_BASE_URL = '/api';

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const resultDiv = document.getElementById('result');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            telegram_id: document.getElementById('telegram_id').value,
            service_name: document.getElementById('service_name').value,
            traffic_limit_gb: parseInt(document.getElementById('traffic_limit_gb').value),
            expiry_days: parseInt(document.getElementById('expiry_days').value),
            inbound_id: parseInt(document.getElementById('inbound_id').value)
        };
        
        // Show loading
        showResult('Đang xử lý đăng ký...', 'loading');
        
        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showResult(
                    `✅ Đăng ký thành công!<br>
                    <strong>Email:</strong> ${result.customer.email}<br>
                    <strong>UUID:</strong> ${result.subscription.uuid}<br>
                    <strong>Dung lượng:</strong> ${result.subscription.traffic_limit_gb} GB<br>
                    <strong>Thời hạn:</strong> ${result.subscription.expiry_date ? new Date(result.subscription.expiry_date).toLocaleDateString('vi-VN') : 'Không giới hạn'}<br>
                    <br>
                    Khách hàng có thể sử dụng dịch vụ ngay bây giờ!`,
                    'success'
                );
                
                // Reset form after 3 seconds
                setTimeout(() => {
                    form.reset();
                }, 3000);
            } else {
                showResult(`❌ Lỗi: ${result.error}`, 'error');
            }
        } catch (error) {
            showResult(`❌ Lỗi kết nối: ${error.message}`, 'error');
        }
    });
});

function showResult(message, type) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = message;
    resultDiv.className = `result ${type}`;
    resultDiv.style.display = 'block';
    
    // Auto hide after 10 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            resultDiv.style.display = 'none';
        }, 10000);
    }
}
