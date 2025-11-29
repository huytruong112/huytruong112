const express = require('express');
const router = express.Router();
const path = require('path');
const { getDatabase } = require('../database/init');
const x3ui = require('../services/x3ui');

/**
 * GET /admin
 * Admin dashboard page
 */
router.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'admin.html'));
});

/**
 * GET /admin/api/stats
 * Lấy thống kê tổng quan
 */
router.get('/api/stats', (req, res) => {
  const db = getDatabase();
  
  const stats = {};
  
  // Tổng số khách hàng
  db.get('SELECT COUNT(*) as total FROM customers', (err, result) => {
    if (err) return res.status(500).json({ error: 'Lỗi server' });
    stats.totalCustomers = result.total;
    
    // Tổng số đơn hàng
    db.get('SELECT COUNT(*) as total FROM orders', (err, result) => {
      if (err) return res.status(500).json({ error: 'Lỗi server' });
      stats.totalOrders = result.total;
      
      // Tổng doanh thu
      db.get('SELECT SUM(total_amount) as total FROM orders WHERE status = "paid"', (err, result) => {
        if (err) return res.status(500).json({ error: 'Lỗi server' });
        stats.totalRevenue = result.total || 0;
        
        // Tổng số client đang hoạt động
        db.get('SELECT COUNT(*) as total FROM clients WHERE status = "active"', (err, result) => {
          if (err) return res.status(500).json({ error: 'Lỗi server' });
          stats.activeClients = result.total;
          
          res.json(stats);
        });
      });
    });
  });
});

/**
 * GET /admin/api/customers
 * Lấy danh sách khách hàng
 */
router.get('/api/customers', (req, res) => {
  const db = getDatabase();
  
  db.all(
    `SELECT 
      c.*,
      COUNT(DISTINCT o.id) as total_orders,
      COUNT(DISTINCT cl.id) as total_clients
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    LEFT JOIN clients cl ON c.id = cl.customer_id
    GROUP BY c.id
    ORDER BY c.created_at DESC`,
    (err, customers) => {
      if (err) {
        return res.status(500).json({ error: 'Lỗi lấy danh sách khách hàng' });
      }
      
      // Loại bỏ password_hash
      customers.forEach(c => delete c.password_hash);
      
      res.json({ customers });
    }
  );
});

/**
 * GET /admin/api/orders
 * Lấy danh sách đơn hàng
 */
router.get('/api/orders', (req, res) => {
  const db = getDatabase();
  
  db.all(
    `SELECT 
      o.*,
      c.name as customer_name,
      c.email as customer_email,
      sp.name as package_name
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN service_packages sp ON o.package_id = sp.id
    ORDER BY o.created_at DESC`,
    (err, orders) => {
      if (err) {
        return res.status(500).json({ error: 'Lỗi lấy danh sách đơn hàng' });
      }
      res.json({ orders });
    }
  );
});

/**
 * GET /admin/api/clients
 * Lấy danh sách tất cả clients
 */
router.get('/api/clients', (req, res) => {
  const db = getDatabase();
  
  db.all(
    `SELECT 
      cl.*,
      c.name as customer_name,
      c.email as customer_email
    FROM clients cl
    JOIN customers c ON cl.customer_id = c.id
    ORDER BY cl.created_at DESC`,
    async (err, clients) => {
      if (err) {
        return res.status(500).json({ error: 'Lỗi lấy danh sách clients' });
      }
      
      try {
        // Lấy thông tin traffic từ 3X-UI
        const x3uiClients = await x3ui.listClients();
        
        // Merge thông tin
        clients.forEach(client => {
          const x3uiClient = x3uiClients.find(c => c.id === client.client_id);
          if (x3uiClient) {
            client.traffic = {
              up: x3uiClient.up,
              down: x3uiClient.down,
              total: x3uiClient.total
            };
            client.enable = x3uiClient.enable;
          }
        });
        
        res.json({ clients });
      } catch (error) {
        console.error('Lỗi lấy thông tin từ 3X-UI:', error);
        res.json({ clients });
      }
    }
  );
});

/**
 * POST /admin/api/packages
 * Tạo gói dịch vụ mới
 */
router.post('/api/packages', (req, res) => {
  const { name, description, duration_days, data_limit_gb, price, max_connections } = req.body;
  
  if (!name || !duration_days || !price) {
    return res.status(400).json({ error: 'Thiếu thông tin bắt buộc' });
  }
  
  const db = getDatabase();
  
  db.run(
    'INSERT INTO service_packages (name, description, duration_days, data_limit_gb, price, max_connections) VALUES (?, ?, ?, ?, ?, ?)',
    [name, description, duration_days, data_limit_gb || 0, price, max_connections || 1],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Lỗi tạo gói dịch vụ' });
      }
      res.json({
        success: true,
        packageId: this.lastID,
        message: 'Tạo gói dịch vụ thành công'
      });
    }
  );
});

/**
 * PUT /admin/api/packages/:id
 * Cập nhật gói dịch vụ
 */
router.put('/api/packages/:id', (req, res) => {
  const packageId = req.params.id;
  const { name, description, duration_days, data_limit_gb, price, max_connections } = req.body;
  
  const db = getDatabase();
  
  db.run(
    'UPDATE service_packages SET name = ?, description = ?, duration_days = ?, data_limit_gb = ?, price = ?, max_connections = ? WHERE id = ?',
    [name, description, duration_days, data_limit_gb, price, max_connections, packageId],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Lỗi cập nhật gói dịch vụ' });
      }
      res.json({
        success: true,
        message: 'Cập nhật gói dịch vụ thành công'
      });
    }
  );
});

/**
 * DELETE /admin/api/packages/:id
 * Xóa gói dịch vụ
 */
router.delete('/api/packages/:id', (req, res) => {
  const packageId = req.params.id;
  const db = getDatabase();
  
  db.run('DELETE FROM service_packages WHERE id = ?', [packageId], function(err) {
    if (err) {
      return res.status(500).json({ error: 'Lỗi xóa gói dịch vụ' });
    }
    res.json({
      success: true,
      message: 'Xóa gói dịch vụ thành công'
    });
  });
});

/**
 * POST /admin/api/clients/:clientId/disable
 * Vô hiệu hóa client
 */
router.post('/api/clients/:clientId/disable', async (req, res) => {
  const clientId = req.params.clientId;
  const db = getDatabase();
  
  db.get('SELECT * FROM clients WHERE id = ?', [clientId], async (err, client) => {
    if (err || !client) {
      return res.status(404).json({ error: 'Không tìm thấy client' });
    }
    
    try {
      // Cập nhật trong 3X-UI
      await x3ui.updateClient(client.client_id, { enable: false });
      
      // Cập nhật trong database
      db.run('UPDATE clients SET status = ? WHERE id = ?', ['disabled', clientId], (err) => {
        if (err) {
          return res.status(500).json({ error: 'Lỗi cập nhật database' });
        }
        res.json({
          success: true,
          message: 'Đã vô hiệu hóa client'
        });
      });
    } catch (error) {
      res.status(500).json({
        error: 'Lỗi vô hiệu hóa client',
        details: error.message
      });
    }
  });
});

/**
 * POST /admin/api/clients/:clientId/enable
 * Kích hoạt lại client
 */
router.post('/api/clients/:clientId/enable', async (req, res) => {
  const clientId = req.params.clientId;
  const db = getDatabase();
  
  db.get('SELECT * FROM clients WHERE id = ?', [clientId], async (err, client) => {
    if (err || !client) {
      return res.status(404).json({ error: 'Không tìm thấy client' });
    }
    
    try {
      // Cập nhật trong 3X-UI
      await x3ui.updateClient(client.client_id, { enable: true });
      
      // Cập nhật trong database
      db.run('UPDATE clients SET status = ? WHERE id = ?', ['active', clientId], (err) => {
        if (err) {
          return res.status(500).json({ error: 'Lỗi cập nhật database' });
        }
        res.json({
          success: true,
          message: 'Đã kích hoạt lại client'
        });
      });
    } catch (error) {
      res.status(500).json({
        error: 'Lỗi kích hoạt client',
        details: error.message
      });
    }
  });
});

/**
 * DELETE /admin/api/clients/:clientId
 * Xóa client
 */
router.delete('/api/clients/:clientId', async (req, res) => {
  const clientId = req.params.clientId;
  const db = getDatabase();
  
  db.get('SELECT * FROM clients WHERE id = ?', [clientId], async (err, client) => {
    if (err || !client) {
      return res.status(404).json({ error: 'Không tìm thấy client' });
    }
    
    try {
      // Xóa trong 3X-UI
      await x3ui.deleteClient(client.client_id);
      
      // Xóa trong database
      db.run('DELETE FROM clients WHERE id = ?', [clientId], (err) => {
        if (err) {
          return res.status(500).json({ error: 'Lỗi xóa client' });
        }
        res.json({
          success: true,
          message: 'Đã xóa client'
        });
      });
    } catch (error) {
      res.status(500).json({
        error: 'Lỗi xóa client',
        details: error.message
      });
    }
  });
});

module.exports = router;
