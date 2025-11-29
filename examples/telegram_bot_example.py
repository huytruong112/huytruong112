#!/usr/bin/env python3
"""
Example: Telegram Bot Integration
This demonstrates how to create a Telegram bot for VPN subscription management

Install required package: pip install python-telegram-bot
"""
import httpx
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
VPN_API_URL = "http://localhost:8000"

# Plans
PLANS = {
    "basic": {"name": "Basic", "traffic": 50, "days": 30, "price": "$5"},
    "premium": {"name": "Premium", "traffic": 100, "days": 30, "price": "$10"},
    "ultimate": {"name": "Ultimate", "traffic": 0, "days": 30, "price": "$15"}
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    await update.message.reply_text(
        f"Xin chào {user.first_name}! 👋\n\n"
        f"Tôi là bot quản lý VPN.\n"
        f"Sử dụng /plans để xem các gói dịch vụ."
    )


async def plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available plans"""
    keyboard = []
    
    for plan_id, plan_info in PLANS.items():
        traffic = f"{plan_info['traffic']}GB" if plan_info['traffic'] > 0 else "Unlimited"
        button_text = f"{plan_info['name']} - {traffic} - {plan_info['price']}"
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=f"buy_{plan_id}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📦 Chọn gói dịch vụ:\n\n"
        "• Basic: 50GB/tháng - $5\n"
        "• Premium: 100GB/tháng - $10\n"
        "• Ultimate: Unlimited - $15",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("buy_"):
        plan_id = query.data.replace("buy_", "")
        plan = PLANS.get(plan_id)
        
        if not plan:
            await query.edit_message_text("❌ Gói không hợp lệ!")
            return
        
        # Here you would integrate with payment gateway
        # For this example, we'll simulate immediate purchase
        
        user = query.from_user
        
        # Create subscription
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                subscription_data = {
                    "customer_email": f"{user.username}@telegram.user",
                    "customer_name": f"{user.first_name} {user.last_name or ''}".strip(),
                    "customer_phone": str(user.id),
                    "panel_type": "xui",
                    "inbound_id": 1,
                    "traffic_limit_gb": plan['traffic'],
                    "expiry_days": plan['days'],
                    "protocol": "vless"
                }
                
                response = await client.post(
                    f"{VPN_API_URL}/subscriptions",
                    json=subscription_data
                )
                
                if response.status_code == 201:
                    subscription = response.json()
                    
                    # Get configuration
                    config_response = await client.get(
                        f"{VPN_API_URL}/subscriptions/{subscription['id']}/config"
                    )
                    
                    if config_response.status_code == 200:
                        config = config_response.json()
                        
                        # Send configuration to user
                        message = (
                            f"✅ Đăng ký thành công!\n\n"
                            f"📋 Thông tin:\n"
                            f"• Gói: {plan['name']}\n"
                            f"• Lưu lượng: {plan['traffic']}GB\n"
                            f"• Thời hạn: {plan['days']} ngày\n"
                            f"• UUID: {config['uuid']}\n\n"
                            f"🔗 Để xem QR code và cấu hình chi tiết, sử dụng:\n"
                            f"/config {subscription['id']}"
                        )
                        
                        await query.edit_message_text(message)
                    else:
                        await query.edit_message_text(
                            "✅ Đăng ký thành công!\n"
                            "Tuy nhiên không thể lấy cấu hình. Vui lòng liên hệ admin."
                        )
                else:
                    await query.edit_message_text(
                        f"❌ Lỗi khi tạo đăng ký: {response.text}"
                    )
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            await query.edit_message_text(
                f"❌ Lỗi: {str(e)}"
            )


async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get configuration for subscription"""
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "❌ Sử dụng: /config <subscription_id>"
        )
        return
    
    subscription_id = int(context.args[0])
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            config_response = await client.get(
                f"{VPN_API_URL}/subscriptions/{subscription_id}/config"
            )
            
            if config_response.status_code == 200:
                config = config_response.json()
                
                message = (
                    f"📋 Cấu hình VPN\n\n"
                    f"UUID: `{config['uuid']}`\n"
                    f"Protocol: {config['protocol']}\n"
                    f"Address: {config['address']}\n"
                    f"Port: {config['port']}\n"
                    f"Network: {config['network']}\n"
                    f"Security: {config['security']}\n\n"
                    f"📊 Sử dụng:\n"
                    f"• Đã dùng: {config['traffic_used_gb']:.2f}GB\n"
                    f"• Giới hạn: {config['traffic_limit_gb']}GB\n"
                    f"• Hết hạn: {config['expiry_date']}\n"
                    f"• Trạng thái: {config['status']}"
                )
                
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown'
                )
                
                # You can also send QR code here
                # qr_response = await client.get(
                #     f"{VPN_API_URL}/subscriptions/{subscription_id}/qrcode?connection_url=..."
                # )
            else:
                await update.message.reply_text(
                    f"❌ Không tìm thấy đăng ký #{subscription_id}"
                )
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("plans", plans))
    application.add_handler(CommandHandler("config", config_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
