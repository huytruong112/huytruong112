<?php
/**
 * Script hiển thị thống kê thanh toán
 * 
 * Sử dụng:
 * php payment_statistics.php [date]
 * 
 * Ví dụ:
 * php payment_statistics.php 2025-11-30
 */

date_default_timezone_set('Asia/Ho_Chi_Minh');
require_once __DIR__ . '/db.php';

$date = $argv[1] ?? date('Y-m-d');

echo "=== PAYMENT STATISTICS ===\n";
echo "Date: {$date}\n\n";

// Thống kê tổng quan
$sql = "SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as success_count,
    SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed_count,
    SUM(CASE WHEN status='duplicate' THEN 1 ELSE 0 END) as duplicate_count,
    SUM(CASE WHEN status='success' THEN amount ELSE 0 END) as total_amount,
    AVG(CASE WHEN status='success' THEN amount ELSE NULL END) as avg_amount,
    MIN(CASE WHEN status='success' THEN amount ELSE NULL END) as min_amount,
    MAX(CASE WHEN status='success' THEN amount ELSE NULL END) as max_amount
FROM payment_logs 
WHERE DATE(created_at) = ?";

$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $date);
$stmt->execute();
$stats = $stmt->get_result()->fetch_assoc();

echo "📊 TỔNG QUAN\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "Tổng giao dịch:     " . number_format($stats['total_transactions']) . "\n";
echo "  ✓ Thành công:     " . number_format($stats['success_count']) . "\n";
echo "  ✗ Thất bại:       " . number_format($stats['failed_count']) . "\n";
echo "  ⚠ Trùng lặp:      " . number_format($stats['duplicate_count']) . "\n";
echo "\n";
echo "💰 DOANH THU\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
echo "Tổng tiền:          " . number_format($stats['total_amount'], 0, ',', '.') . " VND\n";
echo "Trung bình:         " . number_format($stats['avg_amount'], 0, ',', '.') . " VND\n";
echo "Nhỏ nhất:           " . number_format($stats['min_amount'], 0, ',', '.') . " VND\n";
echo "Lớn nhất:           " . number_format($stats['max_amount'], 0, ',', '.') . " VND\n";
echo "\n";

// Thống kê theo nguồn
$sql = "SELECT 
    source,
    COUNT(*) as count,
    SUM(CASE WHEN status='success' THEN amount ELSE 0 END) as total_amount
FROM payment_logs 
WHERE DATE(created_at) = ?
GROUP BY source
ORDER BY total_amount DESC";

$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $date);
$stmt->execute();
$sources = $stmt->get_result();

echo "🌐 THEO NGUỒN\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
while ($row = $sources->fetch_assoc()) {
    printf("%-15s %5s GD  %15s VND\n", 
        strtoupper($row['source']), 
        number_format($row['count']),
        number_format($row['total_amount'], 0, ',', '.')
    );
}
echo "\n";

// Thống kê theo giờ
$sql = "SELECT 
    HOUR(created_at) as hour,
    COUNT(*) as count,
    SUM(CASE WHEN status='success' THEN amount ELSE 0 END) as total_amount
FROM payment_logs 
WHERE DATE(created_at) = ?
GROUP BY HOUR(created_at)
ORDER BY hour";

$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $date);
$stmt->execute();
$hours = $stmt->get_result();

echo "⏰ THEO GIỜ\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
while ($row = $hours->fetch_assoc()) {
    $bar = str_repeat('█', min(50, $row['count']));
    printf("%02d:00  %s (%d)\n", $row['hour'], $bar, $row['count']);
}
echo "\n";

// Top 5 giao dịch lớn nhất
$sql = "SELECT 
    unique_code,
    amount,
    description,
    created_at
FROM payment_logs 
WHERE DATE(created_at) = ? AND status='success'
ORDER BY amount DESC
LIMIT 5";

$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $date);
$stmt->execute();
$topTxs = $stmt->get_result();

echo "🏆 TOP 5 GIAO DỊCH LỚN NHẤT\n";
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
$rank = 1;
while ($row = $topTxs->fetch_assoc()) {
    echo "{$rank}. " . str_pad($row['unique_code'], 10) . " - " . number_format($row['amount'], 0, ',', '.') . " VND\n";
    $rank++;
}

echo "\n";
echo "=== END OF REPORT ===\n";
