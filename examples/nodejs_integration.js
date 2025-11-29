/**
 * Ví dụ tích hợp VPN API với Node.js/Express
 * 
 * npm install axios express body-parser
 */

const axios = require('axios');
const express = require('express');
const bodyParser = require('body-parser');

class VPNAPIClient {
  constructor(apiUrl, apiKey) {
    this.apiUrl = apiUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: this.apiUrl,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Đăng ký khách hàng mới
   */
  async registerCustomer(email, name, plan, phone = null) {
    try {
      const response = await this.client.post('/api/v1/customer/register', {
        email,
        name,
        plan,
        phone
      });
      return response.data;
    } catch (error) {
      console.error('Error registering customer:', error.response?.data || error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Lấy thông tin usage
   */
  async getCustomerUsage(email, panelName = null) {
    try {
      const response = await this.client.post('/api/v1/customer/usage', {
        email,
        panel_name: panelName
      });
      return response.data;
    } catch (error) {
      console.error('Error getting usage:', error.response?.data || error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Gia hạn dịch vụ
   */
  async renewCustomer(email, panelName, days = 30) {
    try {
      const response = await this.client.post('/api/v1/customer/renew', {
        email,
        panel_name: panelName,
        days
      });
      return response.data;
    } catch (error) {
      console.error('Error renewing customer:', error.response?.data || error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Xóa khách hàng
   */
  async deleteCustomer(email, panelName, inboundId = null) {
    try {
      const response = await this.client.delete('/api/v1/customer/delete', {
        data: {
          email,
          panel_name: panelName,
          inbound_id: inboundId
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error deleting customer:', error.response?.data || error.message);
      return { success: false, error: error.message };
    }
  }

  /**
   * Lấy danh sách plans
   */
  async getPlans() {
    try {
      const response = await this.client.get('/api/v1/plans');
      return response.data;
    } catch (error) {
      console.error('Error getting plans:', error.response?.data || error.message);
      return { success: false, error: error.message };
    }
  }
}

// ============================================
// Express API Server Example
// ============================================

const app = express();
app.use(bodyParser.json());

// Khởi tạo VPN API client
const vpnApi = new VPNAPIClient(
  process.env.VPN_API_URL || 'http://localhost:8000',
  process.env.VPN_API_KEY || 'your_secret_api_key_here'
);

/**
 * Endpoint: Webhook từ payment gateway
 */
app.post('/webhook/payment-success', async (req, res) => {
  try {
    const { order_id, customer_email, customer_name, plan } = req.body;
    
    console.log(`Processing payment for order ${order_id}`);
    
    // Tạo VPN config cho khách hàng
    const result = await vpnApi.registerCustomer(
      customer_email,
      customer_name,
      plan
    );
    
    if (result.success) {
      // Lưu vào database
      await saveVPNConfig(order_id, customer_email, result.data);
      
      // Gửi email cho khách hàng
      await sendVPNEmail(customer_email, result.data);
      
      res.json({ success: true, message: 'VPN created successfully' });
    } else {
      console.error('Failed to create VPN:', result);
      res.status(500).json({ success: false, error: 'Failed to create VPN' });
    }
  } catch (error) {
    console.error('Error processing payment webhook:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Endpoint: Kiểm tra usage của khách hàng
 */
app.get('/api/customer/:email/usage', async (req, res) => {
  try {
    const { email } = req.params;
    
    const usage = await vpnApi.getCustomerUsage(email);
    
    if (usage.success) {
      const data = usage.data;
      const usedBytes = (data.up || 0) + (data.down || 0);
      const totalBytes = data.total || data.totalGB;
      const usedPercent = (usedBytes / totalBytes) * 100;
      
      res.json({
        success: true,
        data: {
          email: email,
          used: formatBytes(usedBytes),
          total: formatBytes(totalBytes),
          percent: usedPercent.toFixed(2),
          expiry: data.expiryTime ? new Date(data.expiryTime).toISOString() : null,
          warning: usedPercent > 80
        }
      });
    } else {
      res.status(404).json({ success: false, error: 'Customer not found' });
    }
  } catch (error) {
    console.error('Error getting usage:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Endpoint: Gia hạn dịch vụ
 */
app.post('/api/customer/:email/renew', async (req, res) => {
  try {
    const { email } = req.params;
    const { panel_name, months = 1 } = req.body;
    
    const days = months * 30;
    const result = await vpnApi.renewCustomer(email, panel_name, days);
    
    if (result.success) {
      await updateRenewalDate(email, days);
      await sendRenewalEmail(email, days);
      
      res.json({ success: true, message: `Renewed for ${days} days` });
    } else {
      res.status(500).json({ success: false, error: 'Failed to renew' });
    }
  } catch (error) {
    console.error('Error renewing customer:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Endpoint: Xóa khách hàng
 */
app.delete('/api/customer/:email', async (req, res) => {
  try {
    const { email } = req.params;
    const { panel_name, inbound_id } = req.body;
    
    const result = await vpnApi.deleteCustomer(email, panel_name, inbound_id);
    
    if (result.success) {
      await deleteCustomerFromDB(email);
      res.json({ success: true, message: 'Customer deleted' });
    } else {
      res.status(500).json({ success: false, error: 'Failed to delete' });
    }
  } catch (error) {
    console.error('Error deleting customer:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * Endpoint: Danh sách plans
 */
app.get('/api/plans', async (req, res) => {
  try {
    const plans = await vpnApi.getPlans();
    res.json(plans);
  } catch (error) {
    console.error('Error getting plans:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// ============================================
// Scheduled Tasks Example (using node-cron)
// ============================================

const cron = require('node-cron');

/**
 * Kiểm tra khách hàng sắp hết hạn mỗi ngày lúc 9 giờ sáng
 */
cron.schedule('0 9 * * *', async () => {
  console.log('Checking for expiring customers...');
  
  try {
    const customers = await getCustomersFromDB();
    
    for (const customer of customers) {
      const usage = await vpnApi.getCustomerUsage(customer.email);
      
      if (usage.success) {
        const expiryDate = new Date(usage.data.expiryTime);
        const daysRemaining = Math.ceil((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
        
        // Gửi email nhắc nhở nếu còn 3 ngày
        if (daysRemaining <= 3 && daysRemaining > 0) {
          await sendExpiryWarning(customer.email, daysRemaining);
        }
        
        // Kiểm tra dung lượng
        const usedBytes = (usage.data.up || 0) + (usage.data.down || 0);
        const totalBytes = usage.data.total || usage.data.totalGB;
        const usedPercent = (usedBytes / totalBytes) * 100;
        
        if (usedPercent > 90) {
          await sendDataWarning(customer.email, usedPercent);
        }
      }
    }
  } catch (error) {
    console.error('Error in scheduled task:', error);
  }
});

// ============================================
// Helper Functions
// ============================================

function formatBytes(bytes) {
  if (bytes >= 1073741824) {
    return (bytes / 1073741824).toFixed(2) + ' GB';
  } else if (bytes >= 1048576) {
    return (bytes / 1048576).toFixed(2) + ' MB';
  } else if (bytes >= 1024) {
    return (bytes / 1024).toFixed(2) + ' KB';
  }
  return bytes + ' bytes';
}

async function saveVPNConfig(orderId, email, vpnData) {
  // Implement database save
  console.log(`Saving VPN config for order ${orderId}`);
}

async function sendVPNEmail(email, vpnData) {
  // Implement email sending
  console.log(`Sending VPN email to ${email}`);
}

async function updateRenewalDate(email, days) {
  // Update database
  console.log(`Updating renewal for ${email}: +${days} days`);
}

async function sendRenewalEmail(email, days) {
  // Send renewal confirmation
  console.log(`Sending renewal email to ${email}`);
}

async function deleteCustomerFromDB(email) {
  // Delete from database
  console.log(`Deleting customer ${email} from database`);
}

async function getCustomersFromDB() {
  // Get all active customers
  return [];
}

async function sendExpiryWarning(email, daysRemaining) {
  console.log(`Sending expiry warning to ${email}: ${daysRemaining} days remaining`);
}

async function sendDataWarning(email, usedPercent) {
  console.log(`Sending data warning to ${email}: ${usedPercent.toFixed(2)}% used`);
}

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// ============================================
// Standalone usage example
// ============================================

async function example() {
  const vpn = new VPNAPIClient(
    'http://localhost:8000',
    'your_secret_api_key_here'
  );
  
  // Đăng ký khách hàng mới
  const result = await vpn.registerCustomer(
    'customer@example.com',
    'Nguyễn Văn A',
    'premium',
    '0123456789'
  );
  
  console.log('Registration result:', result);
  
  // Kiểm tra usage
  const usage = await vpn.getCustomerUsage('customer@example.com');
  console.log('Usage:', usage);
}

// Uncomment to run example
// example().catch(console.error);

module.exports = { VPNAPIClient };
