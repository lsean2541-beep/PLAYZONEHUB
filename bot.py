import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# 1. Logging Setup (Crucial for monitoring on Render)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 2. Configuration & Direct Links
TOKEN = os.environ.get("BOT_TOKEN")

# MUST include the '@' for public channels, or use the integer ID (-100xxxxxxxxx) for private channels
CHANNEL_ID = "@online_cazino_big" 

# Tracked URLs
URL_CHANNEL = "https://t.me/online_cazino_big"
URL_PLAY_NOW = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
URL_HELP = "https://www.cazino-big.com/article/faq?agent_id=33"

# 3. Dynamic Text Templates
NOT_SUBSCRIBED_TEXT = (
    "❌ *You’re not subscribed yet. Join the channel to unlock access.*\n\n"
    "• 🎟️ Access VIP Raffles\n"
    "• 📈 Daily Bonuses\n"
    "• 💎 Exclusive Content\n"
    "• 💵 15% weekly cashback\n"
    "• 💰 €200,000 monthly withdrawals\n"
    "• 🎁 €500 birthday bonus"
)

UNLOCKED_TEXT = (
    "🎉 *Unlocked Successfully!*\n\n"
    "*Step 2/2:* Continue to the site.\n\n"
    "🎁 *YOUR $25 WELCOME GIFT IS WAITING!*\n"
    "We’re putting a FREE $25 ticket in your hands just for joining. "
    "Use it to enter our Monthly VIP Raffle and chase the big prize. 💎\n\n"
    "👉 _Account creation takes only 30 seconds!_"
)

# 4. Inline Keyboard Generators
def get_not_subscribed_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url=URL_CHANNEL)],
        [InlineKeyboardButton("🔓 Try Again / Unlocks", callback_data="check_subscription")],
        [InlineKeyboardButton("💬 Help", url=URL_HELP)]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_unlocked_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎰 PLAY NOW (Claim $25 Free)", url=URL_PLAY_NOW)],
        [InlineKeyboardButton("💬 Support / FAQ", url=URL_HELP)]
    ]
    return InlineKeyboardMarkup(keyboard)

# 5. Subscription Checker Core Logic
async def is_user_subscribed(app_bot, user_id: int) -> bool:
    """Queries Telegram API to verify if user is explicitly inside the channel."""
    try:
        member = await app_bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Allowed states: creator, administrator, member
        # Rejected states: left, kicked
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except TelegramError as e:
        logger.error(f"Error verifying subscription status for {user_id}: {e}")
        # Defaulting to False if the bot cannot check (e.g. not an admin in the channel)
        return False

# 6. Interaction Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when user sends /start"""
    user_id = update.effective_user.id
    subscribed = await is_user_subscribed(context.bot, user_id)
    
    if subscribed:
        await update.message.reply_text(
            text=UNLOCKED_TEXT,
            parse_mode='Markdown',
            reply_markup=get_unlocked_keyboard()
        )
    else:
        await update.message.reply_text(
            text=NOT_SUBSCRIBED_TEXT,
            parse_mode='Markdown',
            reply_markup=get_not_subscribed_keyboard()
        )

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when user clicks 'Try Again / Unlocks' button"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Always answer callback to remove loading animation on the button
    await query.answer()
    
    subscribed = await is_user_subscribed(context.bot, user_id)
    
    if subscribed:
        # Edit text and update buttons directly to show success
        await query.edit_message_text(
            text=UNLOCKED_TEXT,
            parse_mode='Markdown',
            reply_markup=get_unlocked_keyboard()
        )
    else:
        # Alert the user they still haven't joined using a non-intrusive alert banner
        await query.answer(
            text="❌ Verification failed. Please make sure you have joined the channel!", 
            show_alert=True
        )

# --- ENGINE RUNNER ---
def main():
    if not TOKEN:
        logger.error("BOT_TOKEN is missing environment variables. Process killed.")
        return

    logger.info("Initializing Play Zone Hub Lock-Gateway Engine...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Event routers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
    
    # Catch-all routing to fallback to /start logic if users type messages manually
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    # Native looping setup built for easy handling on Render Workers
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
