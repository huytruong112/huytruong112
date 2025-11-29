# 🤝 Đóng góp cho dự án

Cảm ơn bạn đã quan tâm đến việc đóng góp cho dự án! Dưới đây là hướng dẫn để bạn có thể đóng góp hiệu quả.

## 🎯 Cách đóng góp

### Báo lỗi (Bug Report)

Nếu bạn tìm thấy lỗi, vui lòng tạo issue với thông tin:
- Mô tả lỗi chi tiết
- Các bước để tái hiện lỗi
- Môi trường (OS, Node.js version, 3X-UI version)
- Screenshots (nếu có)
- Log files

### Đề xuất tính năng (Feature Request)

Có ý tưởng tính năng mới? Tạo issue với:
- Mô tả tính năng
- Lý do tại sao cần tính năng này
- Cách tính năng sẽ hoạt động
- Mockups/wireframes (nếu có)

### Pull Request

1. Fork repository
2. Tạo branch mới từ `main`:
   ```bash
   git checkout -b feature/ten-tinh-nang
   ```
3. Code và test
4. Commit với message rõ ràng
5. Push lên fork của bạn
6. Tạo Pull Request

## 📋 Quy tắc code

### JavaScript Style Guide

- Sử dụng ES6+ syntax
- Indent: 2 spaces
- Semicolons: bắt buộc
- Naming:
  - camelCase cho variables và functions
  - PascalCase cho classes
  - UPPER_CASE cho constants

### Code Organization

```javascript
// 1. Imports
const express = require('express');

// 2. Constants
const DEFAULT_PORT = 3000;

// 3. Functions
function myFunction() {
  // code
}

// 4. Exports
module.exports = { myFunction };
```

### Comments

```javascript
/**
 * Mô tả function
 * @param {string} param - Mô tả parameter
 * @returns {Promise<Object>} Mô tả return value
 */
async function myFunction(param) {
  // Implementation
}
```

## 🧪 Testing

Trước khi submit PR, đảm bảo:
- [ ] Code chạy không lỗi
- [ ] Test các API endpoints
- [ ] Test UI trên nhiều browsers
- [ ] Kiểm tra tích hợp với 3X-UI

## 📝 Commit Messages

Format:
```
<type>: <subject>

<body>
```

Types:
- `feat`: Tính năng mới
- `fix`: Sửa lỗi
- `docs`: Cập nhật documentation
- `style`: Format code (không thay đổi logic)
- `refactor`: Refactor code
- `test`: Thêm tests
- `chore`: Maintenance tasks

Ví dụ:
```
feat: thêm tích hợp thanh toán VNPay

- Thêm webhook handler
- Cập nhật UI checkout
- Thêm validation
```

## 🌟 Ý tưởng đóng góp

Một số ý tưởng bạn có thể đóng góp:

### Backend
- [ ] Tích hợp các cổng thanh toán (VNPay, Momo, Stripe)
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Rate limiting
- [ ] API documentation (Swagger)
- [ ] Unit tests
- [ ] Webhook endpoints cho automation

### Frontend
- [ ] Dashboard với charts
- [ ] Responsive design improvements
- [ ] Multi-language support (i18n)
- [ ] Dark mode
- [ ] PWA support
- [ ] Better error handling

### Features
- [ ] Referral system
- [ ] Coupon/Discount codes
- [ ] Auto-renewal subscriptions
- [ ] Trial periods
- [ ] Usage statistics và analytics
- [ ] Client app (mobile/desktop)
- [ ] Telegram bot integration
- [ ] Multi-server support

### DevOps
- [ ] CI/CD pipeline
- [ ] Docker improvements
- [ ] Kubernetes deployment
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Automated backups
- [ ] Health checks

### Documentation
- [ ] Video tutorials
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] FAQ
- [ ] Translations

## 🔍 Review Process

1. Code review bởi maintainers
2. Automated checks (nếu có)
3. Testing
4. Merge vào main branch
5. Deploy

## 📞 Liên hệ

Có câu hỏi? Liên hệ qua:
- GitHub Issues
- Email
- Discord (nếu có)

## 📜 License

Bằng việc đóng góp, bạn đồng ý rằng contributions của bạn sẽ được licensed dưới MIT License giống như project.

---

Cảm ơn bạn đã đóng góp! 🎉
