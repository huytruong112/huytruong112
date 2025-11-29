/**
 * VÍ DỤ TÍCH HỢP THANH TOÁN
 * 
 * File này chứa các ví dụ về cách tích hợp các cổng thanh toán phổ biến
 * Bạn có thể sử dụng làm tham khảo để tích hợp vào hệ thống
 */

// =============================================================================
// VÍ DỤ 1: TÍCH HỢP VNPAY
// =============================================================================

const crypto = require('crypto');
const querystring = require('querystring');

class VNPayService {
  constructor() {
    this.vnp_TmnCode = process.env.VNPAY_TMN_CODE;
    this.vnp_HashSecret = process.env.VNPAY_HASH_SECRET;
    this.vnp_Url = process.env.VNPAY_URL || 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html';
    this.vnp_ReturnUrl = process.env.VNPAY_RETURN_URL || 'http://localhost:3000/api/payment/vnpay/callback';
  }

  /**
   * Tạo URL thanh toán VNPay
   */
  createPaymentUrl(orderId, amount, orderInfo, ipAddr) {
    const date = new Date();
    const createDate = this.formatDate(date);
    
    let vnp_Params = {
      vnp_Version: '2.1.0',
      vnp_Command: 'pay',
      vnp_TmnCode: this.vnp_TmnCode,
      vnp_Amount: amount * 100, // VNPay yêu cầu số tiền * 100
      vnp_CreateDate: createDate,
      vnp_CurrCode: 'VND',
      vnp_IpAddr: ipAddr,
      vnp_Locale: 'vn',
      vnp_OrderInfo: orderInfo,
      vnp_OrderType: 'other',
      vnp_ReturnUrl: this.vnp_ReturnUrl,
      vnp_TxnRef: orderId.toString(),
      vnp_ExpireDate: this.formatDate(new Date(date.getTime() + 15 * 60000)) // 15 phút
    };

    // Sort params
    vnp_Params = this.sortObject(vnp_Params);

    // Create signature
    const signData = querystring.stringify(vnp_Params, { encode: false });
    const hmac = crypto.createHmac('sha512', this.vnp_HashSecret);
    const signed = hmac.update(Buffer.from(signData, 'utf-8')).digest('hex');
    vnp_Params['vnp_SecureHash'] = signed;

    // Create URL
    return this.vnp_Url + '?' + querystring.stringify(vnp_Params, { encode: false });
  }

  /**
   * Xác thực callback từ VNPay
   */
  verifyCallback(vnp_Params) {
    const secureHash = vnp_Params['vnp_SecureHash'];
    delete vnp_Params['vnp_SecureHash'];
    delete vnp_Params['vnp_SecureHashType'];

    const sortedParams = this.sortObject(vnp_Params);
    const signData = querystring.stringify(sortedParams, { encode: false });
    const hmac = crypto.createHmac('sha512', this.vnp_HashSecret);
    const signed = hmac.update(Buffer.from(signData, 'utf-8')).digest('hex');

    return secureHash === signed;
  }

  formatDate(date) {
    const year = date.getFullYear().toString();
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const day = ('0' + date.getDate()).slice(-2);
    const hour = ('0' + date.getHours()).slice(-2);
    const minute = ('0' + date.getMinutes()).slice(-2);
    const second = ('0' + date.getSeconds()).slice(-2);
    return year + month + day + hour + minute + second;
  }

  sortObject(obj) {
    const sorted = {};
    const keys = Object.keys(obj).sort();
    keys.forEach(key => {
      sorted[key] = obj[key];
    });
    return sorted;
  }
}

// Sử dụng trong routes/api.js:
/*
router.post('/orders', authenticateToken, async (req, res) => {
  const { packageId, paymentMethod } = req.body;
  
  if (paymentMethod === 'vnpay') {
    // Tạo đơn hàng với status = 'pending'
    // ...
    
    const vnpay = new VNPayService();
    const paymentUrl = vnpay.createPaymentUrl(
      orderId,
      package.price,
      `Thanh toan goi dich vu ${package.name}`,
      req.ip
    );
    
    return res.json({
      success: true,
      paymentUrl: paymentUrl,
      orderId: orderId
    });
  }
});

// Callback endpoint
router.get('/payment/vnpay/callback', async (req, res) => {
  const vnpay = new VNPayService();
  const vnp_Params = req.query;
  
  if (vnpay.verifyCallback(vnp_Params)) {
    const orderId = vnp_Params['vnp_TxnRef'];
    const responseCode = vnp_Params['vnp_ResponseCode'];
    
    if (responseCode === '00') {
      // Thanh toán thành công - tạo client tự động
      // Update order status = 'paid'
      // Create client in 3X-UI
      // ...
      
      return res.redirect('/success?orderId=' + orderId);
    }
  }
  
  res.redirect('/failed');
});
*/

// =============================================================================
// VÍ DỤ 2: TÍCH HỢP MOMO
// =============================================================================

class MoMoService {
  constructor() {
    this.partnerCode = process.env.MOMO_PARTNER_CODE;
    this.accessKey = process.env.MOMO_ACCESS_KEY;
    this.secretKey = process.env.MOMO_SECRET_KEY;
    this.endpoint = process.env.MOMO_ENDPOINT || 'https://test-payment.momo.vn/v2/gateway/api/create';
    this.redirectUrl = process.env.MOMO_REDIRECT_URL || 'http://localhost:3000/api/payment/momo/callback';
    this.ipnUrl = process.env.MOMO_IPN_URL || 'http://localhost:3000/api/payment/momo/ipn';
  }

  /**
   * Tạo request thanh toán MoMo
   */
  async createPayment(orderId, amount, orderInfo) {
    const requestId = orderId + '-' + Date.now();
    const rawSignature = `accessKey=${this.accessKey}&amount=${amount}&extraData=&ipnUrl=${this.ipnUrl}&orderId=${orderId}&orderInfo=${orderInfo}&partnerCode=${this.partnerCode}&redirectUrl=${this.redirectUrl}&requestId=${requestId}&requestType=captureWallet`;
    
    const signature = crypto
      .createHmac('sha256', this.secretKey)
      .update(rawSignature)
      .digest('hex');

    const requestBody = {
      partnerCode: this.partnerCode,
      accessKey: this.accessKey,
      requestId: requestId,
      amount: amount,
      orderId: orderId,
      orderInfo: orderInfo,
      redirectUrl: this.redirectUrl,
      ipnUrl: this.ipnUrl,
      extraData: '',
      requestType: 'captureWallet',
      signature: signature,
      lang: 'vi'
    };

    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });

    return await response.json();
  }

  /**
   * Xác thực callback từ MoMo
   */
  verifyCallback(data) {
    const rawSignature = `accessKey=${this.accessKey}&amount=${data.amount}&extraData=${data.extraData}&message=${data.message}&orderId=${data.orderId}&orderInfo=${data.orderInfo}&orderType=${data.orderType}&partnerCode=${this.partnerCode}&payType=${data.payType}&requestId=${data.requestId}&responseTime=${data.responseTime}&resultCode=${data.resultCode}&transId=${data.transId}`;
    
    const signature = crypto
      .createHmac('sha256', this.secretKey)
      .update(rawSignature)
      .digest('hex');

    return signature === data.signature;
  }
}

// =============================================================================
// VÍ DỤ 3: TÍCH HỢP STRIPE
// =============================================================================

// npm install stripe
// const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

class StripeService {
  constructor() {
    // this.stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
  }

  /**
   * Tạo payment intent
   */
  async createPaymentIntent(amount, orderId, customerEmail) {
    // const paymentIntent = await this.stripe.paymentIntents.create({
    //   amount: amount * 100, // Stripe tính bằng cents
    //   currency: 'usd',
    //   metadata: {
    //     orderId: orderId,
    //     customerEmail: customerEmail
    //   }
    // });
    // 
    // return paymentIntent;
  }

  /**
   * Xác thực webhook từ Stripe
   */
  verifyWebhook(payload, signature) {
    // const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;
    // 
    // try {
    //   const event = this.stripe.webhooks.constructEvent(
    //     payload,
    //     signature,
    //     endpointSecret
    //   );
    //   return event;
    // } catch (err) {
    //   return null;
    // }
  }
}

// =============================================================================
// SỬ DỤNG TRONG API ROUTES
// =============================================================================

/*
// Thêm vào routes/api.js

const VNPayService = require('../services/payment/vnpay');
const MoMoService = require('../services/payment/momo');

// Endpoint tạo đơn hàng với thanh toán
router.post('/orders', authenticateToken, async (req, res) => {
  const { packageId, paymentMethod } = req.body;
  const customerId = req.user.customerId;
  
  const db = getDatabase();
  
  // Lấy thông tin gói
  db.get('SELECT * FROM service_packages WHERE id = ?', [packageId], async (err, package) => {
    if (err || !package) {
      return res.status(404).json({ error: 'Không tìm thấy gói dịch vụ' });
    }
    
    // Tạo đơn hàng với status = 'pending'
    db.run(
      'INSERT INTO orders (customer_id, package_id, status, payment_method, total_amount) VALUES (?, ?, ?, ?, ?)',
      [customerId, packageId, 'pending', paymentMethod, package.price],
      async function(err) {
        if (err) {
          return res.status(500).json({ error: 'Lỗi tạo đơn hàng' });
        }
        
        const orderId = this.lastID;
        
        // Xử lý thanh toán theo phương thức
        if (paymentMethod === 'vnpay') {
          const vnpay = new VNPayService();
          const paymentUrl = vnpay.createPaymentUrl(
            orderId,
            package.price,
            `Thanh toan goi ${package.name}`,
            req.ip
          );
          
          res.json({
            success: true,
            paymentUrl: paymentUrl,
            orderId: orderId
          });
          
        } else if (paymentMethod === 'momo') {
          const momo = new MoMoService();
          const result = await momo.createPayment(
            orderId,
            package.price,
            `Thanh toan goi ${package.name}`
          );
          
          if (result.resultCode === 0) {
            res.json({
              success: true,
              paymentUrl: result.payUrl,
              orderId: orderId
            });
          } else {
            res.status(500).json({ error: 'Lỗi tạo thanh toán MoMo' });
          }
          
        } else {
          // Thanh toán thủ công - tự động tạo client luôn
          // (như code hiện tại)
        }
      }
    );
  });
});

// Callback VNPay
router.get('/payment/vnpay/callback', async (req, res) => {
  const vnpay = new VNPayService();
  const vnp_Params = req.query;
  
  if (vnpay.verifyCallback(vnp_Params)) {
    const orderId = vnp_Params['vnp_TxnRef'];
    const responseCode = vnp_Params['vnp_ResponseCode'];
    
    if (responseCode === '00') {
      // Thanh toán thành công
      await processSuccessfulPayment(orderId);
      return res.redirect('/payment-success?orderId=' + orderId);
    }
  }
  
  res.redirect('/payment-failed');
});

// IPN MoMo (webhook)
router.post('/payment/momo/ipn', async (req, res) => {
  const momo = new MoMoService();
  const data = req.body;
  
  if (momo.verifyCallback(data)) {
    if (data.resultCode === 0) {
      // Thanh toán thành công
      await processSuccessfulPayment(data.orderId);
    }
  }
  
  res.status(204).send();
});

// Hàm xử lý thanh toán thành công
async function processSuccessfulPayment(orderId) {
  const db = getDatabase();
  
  // Lấy thông tin đơn hàng
  const order = await new Promise((resolve, reject) => {
    db.get('SELECT * FROM orders WHERE id = ?', [orderId], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
  
  // Lấy thông tin khách hàng và gói
  const customer = await new Promise((resolve, reject) => {
    db.get('SELECT * FROM customers WHERE id = ?', [order.customer_id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
  
  const package = await new Promise((resolve, reject) => {
    db.get('SELECT * FROM service_packages WHERE id = ?', [order.package_id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
  
  // Tạo client trong 3X-UI
  const clientId = require('uuid').v4();
  const expiryTime = Date.now() + (package.duration_days * 24 * 60 * 60 * 1000);
  
  const x3ui = require('../services/x3ui');
  const clientResult = await x3ui.createClient({
    email: customer.email,
    clientId: clientId,
    expiryTime: expiryTime,
    totalGB: package.data_limit_gb || 0,
    limitIp: package.max_connections
  });
  
  // Cập nhật đơn hàng
  await new Promise((resolve, reject) => {
    db.run(
      'UPDATE orders SET status = ?, paid_at = CURRENT_TIMESTAMP WHERE id = ?',
      ['paid', orderId],
      (err) => err ? reject(err) : resolve()
    );
  });
  
  // Lưu client
  await new Promise((resolve, reject) => {
    db.run(
      'INSERT INTO clients (order_id, customer_id, client_id, email, connection_url, subscription_url, expiry_date, data_limit_gb, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
      [
        orderId,
        customer.id,
        clientId,
        customer.email,
        clientResult.connectionUrl,
        clientResult.subscriptionUrl,
        new Date(expiryTime).toISOString(),
        package.data_limit_gb || 0,
        'active'
      ],
      (err) => err ? reject(err) : resolve()
    );
  });
  
  // TODO: Gửi email thông báo cho khách hàng
}
*/

module.exports = {
  VNPayService,
  MoMoService,
  StripeService
};
