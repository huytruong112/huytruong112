const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'database.sqlite');

let db;

function initDatabase() {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(DB_PATH, (err) => {
      if (err) {
        reject(err);
        return;
      }
      console.log('✅ Kết nối database thành công');
      
      // Tạo các bảng
      db.serialize(() => {
        // Bảng gói dịch vụ
        db.run(`
          CREATE TABLE IF NOT EXISTS service_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            duration_days INTEGER NOT NULL,
            data_limit_gb INTEGER,
            price REAL NOT NULL,
            max_connections INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // Bảng khách hàng
        db.run(`
          CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            phone TEXT,
            password_hash TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          )
        `);

        // Bảng đơn hàng
        db.run(`
          CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            package_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            total_amount REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            paid_at DATETIME,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (package_id) REFERENCES service_packages(id)
          )
        `);

        // Bảng client (lưu thông tin client trong 3X-UI)
        db.run(`
          CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            client_id TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            connection_url TEXT,
            subscription_url TEXT,
            expiry_date DATETIME NOT NULL,
            data_limit_gb INTEGER,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
          )
        `, (err) => {
          if (err) {
            reject(err);
            return;
          }
          
          // Thêm dữ liệu mẫu cho gói dịch vụ nếu chưa có
          db.get('SELECT COUNT(*) as count FROM service_packages', (err, row) => {
            if (err) {
              reject(err);
              return;
            }
            
            if (row.count === 0) {
              const packages = [
                ['Gói Cơ Bản', 'Phù hợp cho người dùng cá nhân', 30, 50, 50000, 1],
                ['Gói Tiêu Chuẩn', 'Dung lượng cao hơn cho nhu cầu thường xuyên', 30, 100, 90000, 2],
                ['Gói Premium', 'Không giới hạn dung lượng', 30, 0, 150000, 5],
                ['Gói 3 Tháng', 'Tiết kiệm cho gói 3 tháng', 90, 150, 250000, 2],
                ['Gói 6 Tháng', 'Tiết kiệm nhất cho gói 6 tháng', 180, 300, 450000, 3]
              ];
              
              const stmt = db.prepare('INSERT INTO service_packages (name, description, duration_days, data_limit_gb, price, max_connections) VALUES (?, ?, ?, ?, ?, ?)');
              packages.forEach(pkg => stmt.run(pkg));
              stmt.finalize();
              
              console.log('✅ Đã thêm dữ liệu mẫu cho gói dịch vụ');
            }
            
            resolve(db);
          });
        });
      });
    });
  });
}

function getDatabase() {
  return db;
}

module.exports = {
  initDatabase,
  getDatabase
};
