<?php
/**
 * SECURITY CHECKER
 * Script kiểm tra các biện pháp bảo mật đã được áp dụng chính xác
 * 
 * Cách sử dụng: Truy cập check-security.php trong trình duyệt
 * 
 * LƯU Ý: Xóa file này sau khi kiểm tra xong để tránh lộ thông tin!
 */

// Chỉ cho phép local access
$allowed_ips = ['127.0.0.1', '::1', 'localhost'];
$client_ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

// Comment dòng này nếu muốn test từ xa
// if (!in_array($client_ip, $allowed_ips)) die('Access denied');

?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔒 Security Check - VPN Việt Nam</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .subtitle {
            color: #6c757d;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .warning strong {
            color: #856404;
        }
        .check-section {
            margin: 30px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        .check-header {
            background: #f8f9fa;
            padding: 15px 20px;
            font-weight: bold;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .check-body {
            padding: 20px;
        }
        .check-item {
            display: flex;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #6c757d;
        }
        .check-item.pass {
            background: #d4edda;
            border-left-color: #28a745;
        }
        .check-item.fail {
            background: #f8d7da;
            border-left-color: #dc3545;
        }
        .check-item.warning {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        .status {
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 4px;
            margin-right: 15px;
            min-width: 80px;
            text-align: center;
        }
        .status.pass { background: #28a745; color: white; }
        .status.fail { background: #dc3545; color: white; }
        .status.warning { background: #ffc107; color: #856404; }
        .code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #dee2e6;
        }
        .summary-card .number {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .summary-card.pass { border-color: #28a745; }
        .summary-card.pass .number { color: #28a745; }
        .summary-card.fail { border-color: #dc3545; }
        .summary-card.fail .number { color: #dc3545; }
        .summary-card.warning { border-color: #ffc107; }
        .summary-card.warning .number { color: #ffc107; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Security Check Report</h1>
        <p class="subtitle">Kiểm tra các biện pháp bảo mật đã được áp dụng</p>
        
        <div class="warning">
            <strong>⚠️ LƯU Ý:</strong> Xóa file này (<code>check-security.php</code>) sau khi kiểm tra xong để tránh lộ thông tin hệ thống!
        </div>

        <?php
        // Hàm kiểm tra header
        function checkHeader($header, $expectedValue = null) {
            $headers = headers_list();
            foreach ($headers as $h) {
                if (stripos($h, $header . ':') === 0) {
                    $value = trim(substr($h, strlen($header) + 1));
                    if ($expectedValue === null) {
                        return ['status' => 'pass', 'value' => $value];
                    }
                    return ['status' => ($value === $expectedValue ? 'pass' : 'warning'), 'value' => $value];
                }
            }
            return ['status' => 'fail', 'value' => null];
        }

        // Hàm kiểm tra file tồn tại
        function checkFile($filename) {
            return file_exists(__DIR__ . '/' . $filename);
        }

        // Hàm kiểm tra PHP config
        function checkPHPConfig($setting) {
            return ini_get($setting);
        }

        // ============ BẮT ĐẦU KIỂM TRA ============
        
        $checks = [
            'headers' => [],
            'files' => [],
            'php_config' => [],
            'server' => []
        ];

        // Kiểm tra Headers
        $checks['headers']['X-Content-Type-Options'] = checkHeader('X-Content-Type-Options', 'nosniff');
        $checks['headers']['X-Frame-Options'] = checkHeader('X-Frame-Options', 'DENY');
        $checks['headers']['X-XSS-Protection'] = checkHeader('X-XSS-Protection');
        $checks['headers']['Referrer-Policy'] = checkHeader('Referrer-Policy', 'no-referrer');
        $checks['headers']['Content-Security-Policy'] = checkHeader('Content-Security-Policy');
        $checks['headers']['Cache-Control'] = checkHeader('Cache-Control');

        // Kiểm tra Files
        $checks['files']['pay.php'] = checkFile('pay.php');
        $checks['files']['security-config.js'] = checkFile('security-config.js');
        $checks['files']['SECURITY_FEATURES.md'] = checkFile('SECURITY_FEATURES.md');
        $checks['files']['config.php'] = checkFile('config.php');
        
        // Kiểm tra PHP Config
        $checks['php_config']['display_errors'] = checkPHPConfig('display_errors') == '0';
        $checks['php_config']['expose_php'] = checkPHPConfig('expose_php') == '0';
        $checks['php_config']['session.cookie_httponly'] = checkPHPConfig('session.cookie_httponly') == '1';
        
        // Kiểm tra Server
        $checks['server']['https'] = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
        $checks['server']['server_signature'] = !isset($_SERVER['SERVER_SIGNATURE']) || empty($_SERVER['SERVER_SIGNATURE']);

        // Tính toán tổng kết
        $total = 0;
        $pass = 0;
        $fail = 0;
        $warning = 0;

        foreach ($checks as $category => $items) {
            foreach ($items as $item => $result) {
                $total++;
                if (is_array($result)) {
                    if ($result['status'] === 'pass') $pass++;
                    elseif ($result['status'] === 'fail') $fail++;
                    else $warning++;
                } else {
                    if ($result === true) $pass++;
                    else $fail++;
                }
            }
        }
        ?>

        <!-- Summary -->
        <div class="summary">
            <div class="summary-card pass">
                <div>✅ Passed</div>
                <div class="number"><?= $pass ?></div>
                <div>checks</div>
            </div>
            <div class="summary-card fail">
                <div>❌ Failed</div>
                <div class="number"><?= $fail ?></div>
                <div>checks</div>
            </div>
            <div class="summary-card warning">
                <div>⚠️ Warnings</div>
                <div class="number"><?= $warning ?></div>
                <div>checks</div>
            </div>
            <div class="summary-card">
                <div>📊 Score</div>
                <div class="number" style="color: #667eea;"><?= round(($pass / $total) * 100) ?>%</div>
                <div>overall</div>
            </div>
        </div>

        <!-- Security Headers -->
        <div class="check-section">
            <div class="check-header">
                🛡️ Security Headers
            </div>
            <div class="check-body">
                <?php foreach ($checks['headers'] as $header => $result): ?>
                    <div class="check-item <?= $result['status'] ?>">
                        <span class="status <?= $result['status'] ?>">
                            <?= $result['status'] === 'pass' ? '✅ PASS' : ($result['status'] === 'fail' ? '❌ FAIL' : '⚠️ WARN') ?>
                        </span>
                        <div>
                            <strong><?= htmlspecialchars($header) ?></strong><br>
                            <?php if ($result['value']): ?>
                                <span class="code"><?= htmlspecialchars($result['value']) ?></span>
                            <?php else: ?>
                                <span style="color: #dc3545;">Header not found</span>
                            <?php endif; ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <!-- Required Files -->
        <div class="check-section">
            <div class="check-header">
                📁 Required Files
            </div>
            <div class="check-body">
                <?php foreach ($checks['files'] as $file => $exists): ?>
                    <div class="check-item <?= $exists ? 'pass' : 'fail' ?>">
                        <span class="status <?= $exists ? 'pass' : 'fail' ?>">
                            <?= $exists ? '✅ PASS' : '❌ FAIL' ?>
                        </span>
                        <div>
                            <strong><?= htmlspecialchars($file) ?></strong><br>
                            <?= $exists ? '<span style="color: #28a745;">File exists</span>' : '<span style="color: #dc3545;">File not found</span>' ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>

        <!-- PHP Configuration -->
        <div class="check-section">
            <div class="check-header">
                🐘 PHP Configuration
            </div>
            <div class="check-body">
                <div class="check-item <?= $checks['php_config']['display_errors'] ? 'pass' : 'warning' ?>">
                    <span class="status <?= $checks['php_config']['display_errors'] ? 'pass' : 'warning' ?>">
                        <?= $checks['php_config']['display_errors'] ? '✅ PASS' : '⚠️ WARN' ?>
                    </span>
                    <div>
                        <strong>display_errors</strong><br>
                        <span class="code"><?= ini_get('display_errors') ?></span>
                        <?php if (!$checks['php_config']['display_errors']): ?>
                            <span style="color: #856404;"> - Should be 0 in production</span>
                        <?php endif; ?>
                    </div>
                </div>
                
                <div class="check-item <?= $checks['php_config']['expose_php'] ? 'pass' : 'warning' ?>">
                    <span class="status <?= $checks['php_config']['expose_php'] ? 'pass' : 'warning' ?>">
                        <?= $checks['php_config']['expose_php'] ? '✅ PASS' : '⚠️ WARN' ?>
                    </span>
                    <div>
                        <strong>expose_php</strong><br>
                        <span class="code"><?= ini_get('expose_php') ?></span>
                        <?php if (!$checks['php_config']['expose_php']): ?>
                            <span style="color: #856404;"> - Exposes PHP version</span>
                        <?php endif; ?>
                    </div>
                </div>
                
                <div class="check-item <?= $checks['php_config']['session.cookie_httponly'] ? 'pass' : 'warning' ?>">
                    <span class="status <?= $checks['php_config']['session.cookie_httponly'] ? 'pass' : 'warning' ?>">
                        <?= $checks['php_config']['session.cookie_httponly'] ? '✅ PASS' : '⚠️ WARN' ?>
                    </span>
                    <div>
                        <strong>session.cookie_httponly</strong><br>
                        <span class="code"><?= ini_get('session.cookie_httponly') ?></span>
                        <?php if (!$checks['php_config']['session.cookie_httponly']): ?>
                            <span style="color: #856404;"> - Should be 1 for XSS protection</span>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>

        <!-- Server Configuration -->
        <div class="check-section">
            <div class="check-header">
                🖥️ Server Configuration
            </div>
            <div class="check-body">
                <div class="check-item <?= $checks['server']['https'] ? 'pass' : 'fail' ?>">
                    <span class="status <?= $checks['server']['https'] ? 'pass' : 'fail' ?>">
                        <?= $checks['server']['https'] ? '✅ PASS' : '❌ FAIL' ?>
                    </span>
                    <div>
                        <strong>HTTPS Enabled</strong><br>
                        <?= $checks['server']['https'] ? '<span style="color: #28a745;">SSL/TLS is enabled</span>' : '<span style="color: #dc3545;">HTTPS not detected - Security features will not work properly!</span>' ?>
                    </div>
                </div>
                
                <div class="check-item <?= $checks['server']['server_signature'] ? 'pass' : 'warning' ?>">
                    <span class="status <?= $checks['server']['server_signature'] ? 'pass' : 'warning' ?>">
                        <?= $checks['server']['server_signature'] ? '✅ PASS' : '⚠️ WARN' ?>
                    </span>
                    <div>
                        <strong>Server Signature</strong><br>
                        <?= $checks['server']['server_signature'] ? '<span style="color: #28a745;">Hidden</span>' : '<span style="color: #856404;">Visible - Consider hiding</span>' ?>
                    </div>
                </div>
                
                <div class="check-item">
                    <span class="status pass">ℹ️ INFO</span>
                    <div>
                        <strong>Server Software</strong><br>
                        <span class="code"><?= $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown' ?></span>
                    </div>
                </div>
                
                <div class="check-item">
                    <span class="status pass">ℹ️ INFO</span>
                    <div>
                        <strong>PHP Version</strong><br>
                        <span class="code"><?= PHP_VERSION ?></span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recommendations -->
        <?php if ($fail > 0 || $warning > 0): ?>
        <div class="check-section">
            <div class="check-header">
                💡 Khuyến nghị
            </div>
            <div class="check-body">
                <?php if (!$checks['server']['https']): ?>
                    <div class="check-item fail">
                        <strong>🔴 Bắt buộc: Enable HTTPS</strong><br>
                        Tất cả các biện pháp bảo mật client-side sẽ vô nghĩa nếu không dùng HTTPS.
                        Cài đặt SSL certificate (Let's Encrypt miễn phí).
                    </div>
                <?php endif; ?>
                
                <?php if ($checks['headers']['Content-Security-Policy']['status'] === 'fail'): ?>
                    <div class="check-item warning">
                        <strong>🟡 Khuyến nghị: Thêm Content-Security-Policy header</strong><br>
                        Thêm vào file PHP hoặc .htaccess để bảo vệ chống XSS.
                    </div>
                <?php endif; ?>
                
                <?php if (!$checks['files']['security-config.js']): ?>
                    <div class="check-item warning">
                        <strong>🟡 Khuyến nghị: Upload file security-config.js</strong><br>
                        File này chứa cấu hình bảo mật có thể tùy chỉnh.
                    </div>
                <?php endif; ?>
            </div>
        </div>
        <?php endif; ?>

        <!-- Actions -->
        <div style="margin-top: 30px; text-align: center;">
            <a href="pay.php?code=TEST123" class="btn">🔒 Test pay.php</a>
            <a href="security-test.html" class="btn">🧪 Test Security Features</a>
            <a href="javascript:location.reload()" class="btn">🔄 Refresh Check</a>
        </div>

        <div class="warning" style="margin-top: 30px;">
            <strong>⚠️ LẦN NỮA:</strong> Nhớ xóa file <code>check-security.php</code> sau khi kiểm tra xong!
        </div>
    </div>

    <script>
        // Hiển thị thông tin browser
        console.log('%c🔒 Security Check Report', 'font-size: 20px; font-weight: bold; color: #667eea;');
        console.log('Browser:', navigator.userAgent);
        console.log('HTTPS:', window.location.protocol === 'https:');
        console.log('Cookies Enabled:', navigator.cookieEnabled);
    </script>
</body>
</html>
