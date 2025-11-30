<?php
/**
 * File cấu hình database mẫu
 * Copy thành db.php và điền thông tin database thật
 */

// Database configuration
define('DB_HOST', 'localhost');
define('DB_USER', 'your_username');
define('DB_PASS', 'your_password');
define('DB_NAME', 'your_database');

// Kết nối MySQLi
$conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);

// Kiểm tra kết nối
if ($conn->connect_error) {
    error_log('[DB] Connection failed: ' . $conn->connect_error);
    die('Database connection failed. Please check your configuration.');
}

// Set charset UTF-8
$conn->set_charset('utf8mb4');

// Set timezone
$conn->query("SET time_zone = '+07:00'");

// Debug mode (tắt trong production)
if (defined('DB_DEBUG') && DB_DEBUG) {
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
}

return $conn;
