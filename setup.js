#!/usr/bin/env node

/**
 * Script setup hệ thống
 * Chạy script này để kiểm tra và cấu hình hệ thống lần đầu
 */

require('dotenv').config();
const readline = require('readline');
const fs = require('fs');
const path = require('path');
const { initDatabase } = require('./database/init');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

async function setup() {
  console.log('='.repeat(60));
  console.log('🚀 SETUP HỆ THỐNG QUẢN LÝ DỊCH VỤ 3X-UI');
  console.log('='.repeat(60));
  console.log();

  // Kiểm tra file .env
  if (!fs.existsSync('.env')) {
    console.log('❌ Không tìm thấy file .env');
    console.log('📝 Đang tạo file .env từ .env.example...');
    
    if (fs.existsSync('.env.example')) {
      fs.copyFileSync('.env.example', '.env');
      console.log('✅ Đã tạo file .env');
      console.log('⚠️  VUI LÒNG CHỈNH SỬA FILE .env VỚI THÔNG TIN CỦA BẠN');
      console.log();
    } else {
      console.log('❌ Không tìm thấy file .env.example');
      process.exit(1);
    }
  } else {
    console.log('✅ File .env đã tồn tại');
  }

  // Kiểm tra các biến môi trường bắt buộc
  console.log();
  console.log('📋 Kiểm tra cấu hình...');
  
  const requiredEnvVars = [
    'X3UI_PANEL_URL',
    'X3UI_USERNAME',
    'X3UI_PASSWORD',
    'JWT_SECRET',
    'DEFAULT_INBOUND_ID'
  ];

  let missingVars = [];
  requiredEnvVars.forEach(varName => {
    if (!process.env[varName] || process.env[varName].includes('your-') || process.env[varName].includes('change-this')) {
      console.log(`⚠️  ${varName} chưa được cấu hình`);
      missingVars.push(varName);
    } else {
      console.log(`✅ ${varName} đã được cấu hình`);
    }
  });

  if (missingVars.length > 0) {
    console.log();
    console.log('❌ Vui lòng cấu hình các biến sau trong file .env:');
    missingVars.forEach(varName => console.log(`   - ${varName}`));
    console.log();
    console.log('Sau khi cấu hình xong, chạy lại: npm run setup');
    rl.close();
    process.exit(1);
  }

  // Kiểm tra kết nối 3X-UI
  console.log();
  console.log('🔌 Kiểm tra kết nối 3X-UI...');
  
  try {
    const x3ui = require('./services/x3ui');
    await x3ui.login();
    console.log('✅ Kết nối 3X-UI thành công!');
    
    // Kiểm tra inbound
    console.log();
    console.log(`🔍 Kiểm tra inbound ID: ${process.env.DEFAULT_INBOUND_ID}...`);
    const inbound = await x3ui.getInbound(parseInt(process.env.DEFAULT_INBOUND_ID));
    console.log(`✅ Inbound "${inbound.remark}" tìm thấy`);
    console.log(`   Protocol: ${inbound.protocol}`);
    console.log(`   Port: ${inbound.port}`);
    
  } catch (error) {
    console.log('❌ Lỗi kết nối 3X-UI:', error.message);
    console.log();
    console.log('Vui lòng kiểm tra:');
    console.log('1. 3X-UI đang chạy');
    console.log('2. X3UI_PANEL_URL đúng (ví dụ: http://ip:2053)');
    console.log('3. Username và password đúng');
    console.log('4. Firewall cho phép kết nối');
    rl.close();
    process.exit(1);
  }

  // Khởi tạo database
  console.log();
  console.log('💾 Khởi tạo database...');
  
  try {
    await initDatabase();
    console.log('✅ Database đã sẵn sàng');
  } catch (error) {
    console.log('❌ Lỗi khởi tạo database:', error.message);
    rl.close();
    process.exit(1);
  }

  // Hoàn tất
  console.log();
  console.log('='.repeat(60));
  console.log('✅ SETUP HOÀN TẤT!');
  console.log('='.repeat(60));
  console.log();
  console.log('📝 Các bước tiếp theo:');
  console.log();
  console.log('1. Khởi động server:');
  console.log('   npm start');
  console.log();
  console.log('2. Truy cập:');
  console.log(`   - Customer portal: http://localhost:${process.env.PORT || 3000}`);
  console.log(`   - Admin panel: http://localhost:${process.env.PORT || 3000}/admin`);
  console.log();
  console.log('3. Quản lý gói dịch vụ trong Admin panel');
  console.log();
  console.log('🎉 Chúc bạn sử dụng thành công!');
  console.log();

  rl.close();
}

// Chạy setup
setup().catch(error => {
  console.error('❌ Lỗi:', error);
  rl.close();
  process.exit(1);
});
