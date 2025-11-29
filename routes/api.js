const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { getDatabase } = require('../database/init');
const x3ui = require('../services/x3ui');

/**
 * GET /api/packages
 * Lấy danh sách gói dịch vụ
 */
router.get('/packages', (req, res) => {
  const db = getDatabase();
  
  db.all('SELECT * FROM service_packages ORDER BY price ASC', (err, packages) => {
    if (err) {
      return res.status(500).json({ error: 'Lỗi lấy danh sách gói dịch vụ' });
    }
    res.json({ packages });
  });
});

/**
 * POST /api/register
 * Đăng ký khách hàng mới
 */
router.post('/register', async (req, res) => {
  const { email, name, phone, password } = req.body;
  
  if (!email || !name || !password) {
    return res.status(400).json({ error: 'Thiếu thông tin bắt buộc' });
  }
  
  const db = getDatabase();
  
  try {
    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);
    
    // Thêm khách hàng mới
    db.run(
      'INSERT INTO customers (email, name, phone, password_hash) VALUES (?, ?, ?, ?)',
      [email, name, phone, passwordHash],
      function(err) {
        if (err) {
          if (err.message.includes('UNIQUE')) {
            return res.status(400).json({ error: 'Email đã tồn tại' });
          }
          return res.status(500).json({ error: 'Lỗi đăng ký' });
        }
        
        // Tạo JWT token
        const token = jwt.sign(
          { customerId: this.lastID, email },
          process.env.JWT_SECRET,
          { expiresIn: '7d' }
        );
        
        res.json({
          success: true,
          customerId: this.lastID,
          token,
          message: 'Đăng ký thành công'
        });
      }
    );
  } catch (error) {
    res.status(500).json({ error: 'Lỗi server' });
  }
});

/**
 * POST /api/login
 * Đăng nhập
 */
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({ error: 'Thiếu email hoặc password' });
  }
  
  const db = getDatabase();
  
  db.get('SELECT * FROM customers WHERE email = ?', [email], async (err, customer) => {
    if (err) {
      return res.status(500).json({ error: 'Lỗi server' });
    }
    
    if (!customer) {
      return res.status(401).json({ error: 'Email hoặc password không đúng' });
    }
    
    // Kiểm tra password
    const validPassword = await bcrypt.compare(password, customer.password_hash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Email hoặc password không đúng' });
    }
    
    // Tạo JWT token
    const token = jwt.sign(
      { customerId: customer.id, email: customer.email },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.json({
      success: true,
      token,
      customer: {
        id: customer.id,
        email: customer.email,
        name: customer.name,
        phone: customer.phone
      }
    });
  });
});

/**
 * POST /api/orders
 * Tạo đơn hàng mới và tự động tạo client
 */
router.post('/orders', authenticateToken, async (req, res) => {
  const { packageId, paymentMethod } = req.body;
  const customerId = req.user.customerId;
  
  if (!packageId) {
    return res.status(400).json({ error: 'Thiếu thông tin gói dịch vụ' });
  }
  
  const db = getDatabase();
  
  try {
    // Lấy thông tin gói dịch vụ
    db.get('SELECT * FROM service_packages WHERE id = ?', [packageId], async (err, package) => {
      if (err || !package) {
        return res.status(404).json({ error: 'Không tìm thấy gói dịch vụ' });
      }
      
      // Lấy thông tin khách hàng
      db.get('SELECT * FROM customers WHERE id = ?', [customerId], async (err, customer) => {
        if (err || !customer) {
          return res.status(404).json({ error: 'Không tìm thấy khách hàng' });
        }
        
        // Tạo đơn hàng
        db.run(
          'INSERT INTO orders (customer_id, package_id, status, payment_method, total_amount, paid_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
          [customerId, packageId, 'paid', paymentMethod || 'manual', package.price],
          async function(err) {
            if (err) {
              return res.status(500).json({ error: 'Lỗi tạo đơn hàng' });
            }
            
            const orderId = this.lastID;
            
            try {
              // Tự động tạo client trong 3X-UI
              const clientId = uuidv4();
              const expiryTime = Date.now() + (package.duration_days * 24 * 60 * 60 * 1000);
              
              const clientResult = await x3ui.createClient({
                email: customer.email,
                clientId: clientId,
                expiryTime: expiryTime,
                totalGB: package.data_limit_gb || 0,
                limitIp: package.max_connections
              });
              
              // Lưu thông tin client vào database
              db.run(
                'INSERT INTO clients (order_id, customer_id, client_id, email, connection_url, subscription_url, expiry_date, data_limit_gb, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [
                  orderId,
                  customerId,
                  clientId,
                  customer.email,
                  clientResult.connectionUrl,
                  clientResult.subscriptionUrl,
                  new Date(expiryTime).toISOString(),
                  package.data_limit_gb || 0,
                  'active'
                ],
                function(err) {
                  if (err) {
                    console.error('Lỗi lưu client:', err);
                    return res.status(500).json({ error: 'Lỗi lưu thông tin client' });
                  }
                  
                  res.json({
                    success: true,
                    orderId: orderId,
                    clientId: this.lastID,
                    connectionUrl: clientResult.connectionUrl,
                    subscriptionUrl: clientResult.subscriptionUrl,
                    expiryDate: new Date(expiryTime).toISOString(),
                    message: 'Đơn hàng đã được tạo và kích hoạt thành công'
                  });
                }
              );
              
            } catch (error) {
              console.error('Lỗi tạo client trong 3X-UI:', error);
              
              // Cập nhật trạng thái đơn hàng thành failed
              db.run('UPDATE orders SET status = ? WHERE id = ?', ['failed', orderId]);
              
              res.status(500).json({
                error: 'Lỗi tạo client trong 3X-UI',
                details: error.message
              });
            }
          }
        );
      });
    });
  } catch (error) {
    res.status(500).json({ error: 'Lỗi server' });
  }
});

/**
 * GET /api/my-services
 * Lấy danh sách dịch vụ của khách hàng
 */
router.get('/my-services', authenticateToken, (req, res) => {
  const customerId = req.user.customerId;
  const db = getDatabase();
  
  db.all(
    `SELECT 
      c.*,
      sp.name as package_name,
      sp.description as package_description,
      o.created_at as order_date
    FROM clients c
    JOIN orders o ON c.order_id = o.id
    JOIN service_packages sp ON o.package_id = sp.id
    WHERE c.customer_id = ?
    ORDER BY c.created_at DESC`,
    [customerId],
    (err, services) => {
      if (err) {
        return res.status(500).json({ error: 'Lỗi lấy danh sách dịch vụ' });
      }
      res.json({ services });
    }
  );
});

/**
 * GET /api/client/:clientId/info
 * Lấy thông tin chi tiết client
 */
router.get('/client/:clientId/info', authenticateToken, async (req, res) => {
  const clientId = req.params.clientId;
  const customerId = req.user.customerId;
  const db = getDatabase();
  
  // Kiểm tra quyền truy cập
  db.get(
    'SELECT * FROM clients WHERE id = ? AND customer_id = ?',
    [clientId, customerId],
    async (err, client) => {
      if (err || !client) {
        return res.status(404).json({ error: 'Không tìm thấy client' });
      }
      
      try {
        // Lấy thông tin từ 3X-UI
        const x3uiClients = await x3ui.listClients();
        const x3uiClient = x3uiClients.find(c => c.id === client.client_id);
        
        if (x3uiClient) {
          res.json({
            ...client,
            traffic: {
              up: x3uiClient.up,
              down: x3uiClient.down,
              total: x3uiClient.total
            },
            enable: x3uiClient.enable
          });
        } else {
          res.json(client);
        }
      } catch (error) {
        console.error('Lỗi lấy thông tin từ 3X-UI:', error);
        res.json(client);
      }
    }
  );
});

/**
 * Middleware xác thực JWT token
 */
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Thiếu token xác thực' });
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Token không hợp lệ' });
    }
    req.user = user;
    next();
  });
}

module.exports = router;
