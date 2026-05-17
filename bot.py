import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BOT_TOKEN = "8628532806:AAEICE60cqpf6AAr00JkS6Py47dA7osc6CU"  # Replace with your actual Bot Token from BotFather
TRACKING_INVITE_LINK = "https://t.me/online_cazino_big"

# Target Destination Links
TRADING_LINK = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
SUPPORT_LINK = "https://www.cazino-big.com/article/faq?agent_id=33"


def get_gatekeeper_keyboard():
    """Returns the keyboard for Step 1 (Join & Verify)"""
    keyboard = [
        [InlineKeyboardButton("📢 Join Trading Channel", url=TRACKING_INVITE_LINK)],
        [InlineKeyboardButton("✅ Verify Channel Join", callback_data="bypass_verify")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_success_keyboard():
    """Returns the keyboard for Step 3 (Success & Links)"""
    keyboard = [
        [InlineKeyboardButton("🔥 Start Trading Now", url=TRADING_LINK)],
        [InlineKeyboardButton("🤝 Contact Support / FAQ", url=SUPPORT_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: The Entry Point (/start command)"""
    text = (
        "Welcome to PLAYHUBZONE! 🚀\n\n"
        "To access our premium trading signals and start winning, you must join our "
        "official community channel first. Click the button below to join, then click "
        "'✅ Verify Channel Join'."
    )
    await update.message.reply_text(text, reply_markup=get_gatekeeper_keyboard())


async def verify_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Instant Success (Bypasses verification check completely)"""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback click immediately
    
    text = (
        "✅ Verification Successful!\n\n"
        "Welcome to the zone. You now have full access to our trading platform. "
        "Click 'Start Trading' below to set up your account and claim your campaign bonuses!"
    )
    
    # Edit the gatekeeper message into the success state cleanly
    try:
        await query.edit_message_text(text=text, reply_markup=get_success_keyboard())
    except TelegramError as e:
        logger.error(f"Error updating message: {e}")


def main():
    """Starts the bot application."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_button_click, pattern="^bypass_verify$"))

    # Run polling for Render background worker
    logger.info("Starting trusted bot polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
