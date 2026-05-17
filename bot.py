import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION (Environment Variables) ---
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@online_cazino_big") 

# Target Links
WEBSITE_LINK = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
SUPPORT_LINK = "https://www.cazino-big.com/article/faq?agent_id=33"
CHANNEL_LINK = "https://t.me/online_cazino_big"


async def is_user_subscribed(bot, user_id: int) -> bool:
    """Checks if the user is a member of the target channel."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # Allowed statuses: 'member', 'creator', 'administrator'
        if member.status in ['member', 'creator', 'administrator']:
            return True
        return False
    except TelegramError as e:
        logger.error(f"Error checking chat member: {e}")
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    user = update.effective_user
    bot = context.bot
    
    # Check subscription status right away
    subscribed = await is_user_subscribed(bot, user.id)
    
    if subscribed:
        # If already joined, send success buttons immediately
        keyboard = [
            [InlineKeyboardButton("🔥 Start Trading Now", url=WEBSITE_LINK)],
            [InlineKeyboardButton("🤝 Contact Support / FAQ", url=SUPPORT_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Welcome back to **PLAYHUBZONE**, {user.first_name}! 🚀\n\n"
            "You are already verified. Click below to start trading or get support.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # If not joined, present the gatekeeper message
        keyboard = [
            [InlineKeyboardButton("📢 Join Trading Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Verify Channel Join", callback_data="verify_join")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Welcome to **PLAYHUBZONE**, {user.first_name}! 🚀\n\n"
            "To access our premium trading signals and start winning, you must join our official community channel first. "
            "Click the button below to join, then click '✅ Verify Channel Join'.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def handle_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'Verify Channel Join' button clicks."""
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot
    
    # Always answer callback queries immediately to stop the loading animation on Telegram
    await query.answer()
    
    subscribed = await is_user_subscribed(bot, user_id)
    
    if subscribed:
        # Success state: Show website and support buttons
        keyboard = [
            [InlineKeyboardButton("🔥 Start Trading Now", url=WEBSITE_LINK)],
            [InlineKeyboardButton("🤝 Contact Support / FAQ", url=SUPPORT_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "✅ **Verification Successful!**\n\n"
            "Welcome to the zone. You now have full access to our trading platform. "
            "Click 'Start Trading Now' below to setup your account and claim your campaign bonuses!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # Failure state: Loop back and force them to try again
        keyboard = [
            [InlineKeyboardButton("📢 Join Trading Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Try Verification Again", callback_data="verify_join")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "❌ **Verification Failed!**\n\n"
            "It looks like you haven't joined our channel yet. Please click the button below to join the channel, "
            "then tap verify again to unlock your access.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


def main():
    if not TOKEN:
        logger.error("No BOT_TOKEN found in environment variables!")
        return

    # Build the application using Long Polling (ideal for Background Workers)
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_verification, pattern="^verify_join$"))

    # Start the Bot
    logger.info("Bot starting as background worker...")
    application.run_polling()


if __name__ == '__main__':
    main()
