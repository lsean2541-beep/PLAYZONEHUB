import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# Enable logging so you can see details in your Render Log dashboard
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
BOT_TOKEN = "8628532806:AAEICE60cqpf6AAr00JkS6Py47dA7osc6CU"  
# TIP: If @online_cazino_big still fails, replace it with your channel's numerical ID (e.g., -100XXXXXXXXXX)
CHANNEL_ID = "@online_cazino_big" 
TRACKING_INVITE_LINK = "https://t.me/online_cazino_big"

# Target Destination Links
TRADING_LINK = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
SUPPORT_LINK = "https://www.cazino-big.com/article/faq?agent_id=33"


async def is_user_in_channel(app: Application, user_id: int) -> bool:
    """Checks if the user is a valid member of the channel."""
    try:
        member = await app.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        
        # This will print the exact status Telegram sees directly to your Render Logs!
        logger.info(f"Telegram API response for User {user_id}: Status is '{member.status}'")
        
        # Valid active statuses
        if member.status in ["member", "administrator", "creator"]:
            return True
            
        return False
    except TelegramError as e:
        # If this triggers, your bot token is wrong, or the bot isn't an admin in the channel specified
        logger.error(f"Telegram API Error for user {user_id} on channel {CHANNEL_ID}: {e}")
        return False


def get_gatekeeper_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Join Trading Channel", url=TRACKING_INVITE_LINK)],
        [InlineKeyboardButton("✅ Verify Channel Join", callback_data="verify_join")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_success_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔥 Start Trading Now", url=TRADING_LINK)],
        [InlineKeyboardButton("🤝 Contact Support / FAQ", url=SUPPORT_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await is_user_in_channel(context.application, user_id)
    
    if is_member:
        text = (
            "✅ Verification Successful!\n\n"
            "Welcome to the zone. You now have full access to our trading platform. "
            "Click 'Start Trading' below to set up your account and claim your campaign bonuses!"
        )
        await update.message.reply_text(text, reply_markup=get_success_keyboard())
    else:
        text = (
            "Welcome to PLAYHUBZONE! 🚀\n\n"
            "To access our premium trading signals and start winning, you must join our "
            "official community channel first. Click the button below to join, then click "
            "'✅ Verify Channel Join'."
        )
        await update.message.reply_text(text, reply_markup=get_gatekeeper_keyboard())


async def verify_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    
    user_id = query.from_user.id
    is_member = await is_user_in_channel(context.application, user_id)
    
    if is_member:
        text = (
            "✅ Verification Successful!\n\n"
            "Welcome to the zone. You now have full access to our trading platform. "
            "Click 'Start Trading' below to set up your account and claim your campaign bonuses!"
        )
        await query.edit_message_text(text=text, reply_markup=get_success_keyboard())
    else:
        text = (
            "❌ Verification Failed!\n\n"
            "It looks like you haven't joined our channel yet. Please click the button "
            "below to join the channel, then come back and tap verify again to unlock your access."
        )
        # Using a popup alert alongside editing ensures the user notices the interaction immediately
        try:
            await query.answer(text="⚠️ Verification failed. Please make sure you joined!", show_alert=False)
            await query.edit_message_text(text=text, reply_markup=get_gatekeeper_keyboard())
        except TelegramError:
            pass


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_button_click, pattern="^verify_join$"))
    
    logger.info("Starting bot polling safely...")
    application.run_polling()


if __name__ == "__main__":
    main()
