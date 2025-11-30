#!/bin/bash

##############################################################################
# Script cài đặt Cron Job cho hệ thống thanh toán tự động
# File này giúp tự động cài đặt cron job để kiểm tra giao dịch định kỳ
##############################################################################

echo "=========================================="
echo "Cài đặt Cron Job - Thanh Toán Tự Động"
echo "=========================================="
echo ""

# Lấy đường dẫn hiện tại
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHP_BIN=$(which php)

if [ -z "$PHP_BIN" ]; then
    echo "❌ Lỗi: Không tìm thấy PHP. Vui lòng cài đặt PHP trước."
    exit 1
fi

echo "✓ Tìm thấy PHP: $PHP_BIN"
echo "✓ Thư mục hiện tại: $CURRENT_DIR"
echo ""

# File PHP cron job
CRON_FILE="$CURRENT_DIR/api_check_bank_transactions.php"

if [ ! -f "$CRON_FILE" ]; then
    echo "❌ Lỗi: Không tìm thấy file $CRON_FILE"
    exit 1
fi

echo "✓ Tìm thấy file cron job: $CRON_FILE"
echo ""

# Hỏi người dùng về tần suất chạy
echo "Chọn tần suất kiểm tra giao dịch:"
echo "1. Mỗi phút (khuyến nghị)"
echo "2. Mỗi 2 phút"
echo "3. Mỗi 5 phút"
echo "4. Mỗi 10 phút"
echo "5. Tùy chỉnh"
echo ""
read -p "Nhập lựa chọn (1-5): " choice

case $choice in
    1)
        CRON_SCHEDULE="* * * * *"
        DESCRIPTION="mỗi phút"
        ;;
    2)
        CRON_SCHEDULE="*/2 * * * *"
        DESCRIPTION="mỗi 2 phút"
        ;;
    3)
        CRON_SCHEDULE="*/5 * * * *"
        DESCRIPTION="mỗi 5 phút"
        ;;
    4)
        CRON_SCHEDULE="*/10 * * * *"
        DESCRIPTION="mỗi 10 phút"
        ;;
    5)
        read -p "Nhập cron schedule (ví dụ: */5 * * * *): " CRON_SCHEDULE
        DESCRIPTION="tùy chỉnh"
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac

echo ""
echo "Cron job sẽ chạy $DESCRIPTION"
echo "Schedule: $CRON_SCHEDULE"
echo ""

# Tạo cron command
CRON_COMMAND="$CRON_SCHEDULE cd $CURRENT_DIR && $PHP_BIN $CRON_FILE >> $CURRENT_DIR/logs/cron.log 2>&1"

echo "Lệnh cron:"
echo "$CRON_COMMAND"
echo ""

# Kiểm tra xem cron đã tồn tại chưa
crontab -l 2>/dev/null | grep -q "$CRON_FILE"
if [ $? -eq 0 ]; then
    echo "⚠️ Cron job đã tồn tại!"
    read -p "Bạn có muốn cập nhật lại? (y/n): " update_choice
    if [ "$update_choice" != "y" ]; then
        echo "Hủy bỏ cài đặt."
        exit 0
    fi
    
    # Xóa cron cũ
    crontab -l 2>/dev/null | grep -v "$CRON_FILE" | crontab -
    echo "✓ Đã xóa cron job cũ"
fi

# Thêm cron mới
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓✓✓ CÀI ĐẶT THÀNH CÔNG! ✓✓✓"
    echo "=========================================="
    echo ""
    echo "Cron job đã được cài đặt và sẽ chạy $DESCRIPTION"
    echo "Log file: $CURRENT_DIR/logs/cron.log"
    echo ""
    echo "Để xem danh sách cron jobs:"
    echo "  crontab -l"
    echo ""
    echo "Để xóa cron job này:"
    echo "  crontab -l | grep -v '$CRON_FILE' | crontab -"
    echo ""
else
    echo ""
    echo "❌ Lỗi khi cài đặt cron job"
    exit 1
fi
