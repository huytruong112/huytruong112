// Dashboard JavaScript

const API_BASE_URL = '/api';

document.addEventListener('DOMContentLoaded', function() {
    loadCustomers();
    
    // Search functionality
    const searchBox = document.getElementById('searchBox');
    searchBox.addEventListener('input', filterCustomers);
});

let allCustomers = [];

async function loadCustomers() {
    const tableContainer = document.getElementById('customersTable');
    tableContainer.innerHTML = '<p class="loading">Đang tải dữ liệu...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/customers`);
        const result = await response.json();
        
        if (result.success) {
            allCustomers = result.customers;
            displayCustomers(allCustomers);
        } else {
            tableContainer.innerHTML = `<p class="error">Lỗi: ${result.error}</p>`;
        }
    } catch (error) {
        tableContainer.innerHTML = `<p class="error">Lỗi kết nối: ${error.message}</p>`;
    }
}

function displayCustomers(customers) {
    const tableContainer = document.getElementById('customersTable');
    
    if (customers.length === 0) {
        tableContainer.innerHTML = '<p class="loading">Chưa có khách hàng nào.</p>';
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tên</th>
                    <th>Email</th>
                    <th>Số điện thoại</th>
                    <th>Subscription</th>
                    <th>Trạng thái</th>
                    <th>Thao tác</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    customers.forEach(customer => {
        const statusClass = customer.is_active ? 'status-active' : 'status-inactive';
        const statusText = customer.is_active ? 'Hoạt động' : 'Không hoạt động';
        const subscriptionCount = customer.subscriptions ? customer.subscriptions.length : 0;
        
        html += `
            <tr>
                <td>${customer.id}</td>
                <td>${customer.name}</td>
                <td>${customer.email}</td>
                <td>${customer.phone || 'N/A'}</td>
                <td>${subscriptionCount}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>
                    <button class="btn btn-primary" style="padding: 5px 10px; margin-right: 5px;" onclick="viewCustomer(${customer.id})">Chi tiết</button>
                    <button class="btn btn-danger" style="padding: 5px 10px;" onclick="deleteCustomer(${customer.id})">Xóa</button>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    tableContainer.innerHTML = html;
}

function filterCustomers() {
    const searchTerm = document.getElementById('searchBox').value.toLowerCase();
    
    const filtered = allCustomers.filter(customer => 
        customer.name.toLowerCase().includes(searchTerm) ||
        customer.email.toLowerCase().includes(searchTerm)
    );
    
    displayCustomers(filtered);
}

async function viewCustomer(customerId) {
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${customerId}`);
        const result = await response.json();
        
        if (result.success) {
            const customer = result.customer;
            
            let detailHtml = `
                <div class="customer-detail">
                    <h3>📋 Thông tin khách hàng</h3>
                    <p><strong>ID:</strong> ${customer.id}</p>
                    <p><strong>Tên:</strong> ${customer.name}</p>
                    <p><strong>Email:</strong> ${customer.email}</p>
                    <p><strong>Số điện thoại:</strong> ${customer.phone || 'N/A'}</p>
                    <p><strong>Telegram:</strong> ${customer.telegram_id || 'N/A'}</p>
                    <p><strong>Trạng thái:</strong> ${customer.is_active ? '✅ Hoạt động' : '❌ Không hoạt động'}</p>
                    <p><strong>Ngày tạo:</strong> ${new Date(customer.created_at).toLocaleString('vi-VN')}</p>
                    
                    <h3 style="margin-top: 20px;">📊 Danh sách Subscription</h3>
            `;
            
            if (customer.subscriptions && customer.subscriptions.length > 0) {
                detailHtml += '<div class="subscriptions-list">';
                
                customer.subscriptions.forEach(sub => {
                    const isExpired = sub.is_expired;
                    const statusClass = sub.is_active ? (isExpired ? 'status-expired' : 'status-active') : 'status-inactive';
                    const statusText = sub.is_active ? (isExpired ? 'Hết hạn' : 'Hoạt động') : 'Không hoạt động';
                    
                    detailHtml += `
                        <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px;">
                            <p><strong>UUID:</strong> <code>${sub.uuid}</code></p>
                            <p><strong>Gói dịch vụ:</strong> ${sub.service_name}</p>
                            <p><strong>Dung lượng:</strong> ${sub.traffic_limit_gb} GB ${sub.traffic_limit_gb === 0 ? '(Không giới hạn)' : ''}</p>
                            <p><strong>Đã sử dụng:</strong> ${sub.traffic_used_gb.toFixed(2)} GB</p>
                            <p><strong>Ngày hết hạn:</strong> ${sub.expiry_date ? new Date(sub.expiry_date).toLocaleString('vi-VN') : 'Không giới hạn'}</p>
                            <p><strong>Trạng thái:</strong> <span class="status-badge ${statusClass}">${statusText}</span></p>
                            <div style="margin-top: 10px;">
                                <button class="btn btn-success" style="padding: 5px 10px; margin-right: 5px;" onclick="viewTraffic(${sub.id})">Xem traffic</button>
                                <button class="btn btn-danger" style="padding: 5px 10px;" onclick="deleteSubscription(${sub.id})">Xóa</button>
                            </div>
                        </div>
                    `;
                });
                
                detailHtml += '</div>';
            } else {
                detailHtml += '<p>Chưa có subscription nào.</p>';
            }
            
            detailHtml += '</div>';
            
            document.getElementById('customerDetail').innerHTML = detailHtml;
            document.getElementById('customerModal').style.display = 'block';
        } else {
            alert(`Lỗi: ${result.error}`);
        }
    } catch (error) {
        alert(`Lỗi kết nối: ${error.message}`);
    }
}

async function deleteCustomer(customerId) {
    if (!confirm('Bạn có chắc chắn muốn xóa khách hàng này? Tất cả subscription sẽ bị xóa.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/customers/${customerId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Xóa khách hàng thành công!');
            loadCustomers();
        } else {
            alert(`❌ Lỗi: ${result.error}`);
        }
    } catch (error) {
        alert(`❌ Lỗi kết nối: ${error.message}`);
    }
}

async function deleteSubscription(subscriptionId) {
    if (!confirm('Bạn có chắc chắn muốn xóa subscription này?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/subscriptions/${subscriptionId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Xóa subscription thành công!');
            closeModal();
            loadCustomers();
        } else {
            alert(`❌ Lỗi: ${result.error}`);
        }
    } catch (error) {
        alert(`❌ Lỗi kết nối: ${error.message}`);
    }
}

async function viewTraffic(subscriptionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/subscriptions/${subscriptionId}/traffic`);
        const result = await response.json();
        
        if (result.success) {
            const traffic = result.traffic;
            alert(`📊 Thông tin traffic:\n\n` +
                  `Download: ${traffic.download_gb} GB\n` +
                  `Upload: ${traffic.upload_gb} GB\n` +
                  `Tổng: ${traffic.total_gb} GB\n` +
                  `Giới hạn: ${traffic.limit_gb} GB\n` +
                  `Còn lại: ${traffic.remaining_gb} GB`);
        } else {
            alert(`❌ Lỗi: ${result.error}`);
        }
    } catch (error) {
        alert(`❌ Lỗi kết nối: ${error.message}`);
    }
}

function closeModal() {
    document.getElementById('customerModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('customerModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
