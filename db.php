<?php
/**
 * Database connection file
 * File kết nối database - Thay đổi thông tin kết nối phù hợp với server của bạn
 */

// Thông tin kết nối database
$db_host = 'localhost';
$db_user = 'root';
$db_pass = '';
$db_name = 'vpn_database'; // Thay đổi tên database của bạn

// Tạo kết nối
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);

// Kiểm tra kết nối
if ($conn->connect_error) {
    die("Kết nối database thất bại: " . $conn->connect_error);
}

// Set charset UTF-8
$conn->set_charset("utf8mb4");

// Set timezone cho MySQL
$conn->query("SET time_zone = '+07:00'");

// Hàm helper để escape string
function escape_string($str) {
    global $conn;
    return $conn->real_escape_string($str);
}

// Hàm helper để close connection (gọi ở cuối file nếu cần)
function close_db_connection() {
    global $conn;
    if ($conn) {
        $conn->close();
    }
}

// Optional: Error reporting cho development (tắt trên production)
// mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
