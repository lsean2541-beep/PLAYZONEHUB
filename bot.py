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
BOT_TOKEN = "8628532806:AAEICE60cqpf6AAr00JkS6Py47dA7osc6CU"  # Replace with your actual Bot Token
CHANNEL_ID = "@online_cazino_big"
TRACKING_INVITE_LINK = "https://t.me/+YOUR_TRACKING_INVITE_LINK"  # Replace with your actual invite link

# Target Destination Links
TRADING_LINK = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
SUPPORT_LINK = "https://www.cazino-big.com/article/faq?agent_id=33"


async def is_user_in_channel(app: Application, user_id: int) -> bool:
    """Checks if the user is a member, administrator, or creator of the channel."""
    try:
        member = await app.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Allowed statuses
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except TelegramError as e:
        logger.error(f"Error checking chat member: {e}")
        return False


def get_gatekeeper_keyboard():
    """Returns the keyboard for Step 1 & Step 2A"""
    keyboard = [
        [InlineKeyboardButton("📢 Join Trading Channel", url=TRACKING_INVITE_LINK)],
        [InlineKeyboardButton("✅ Verify Channel Join", callback_data="verify_join")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_success_keyboard():
    """Returns the keyboard for Step 3"""
    keyboard = [
        [InlineKeyboardButton("🔥 Start Trading Now", url=TRADING_LINK)],
        [InlineKeyboardButton("🤝 Contact Support / FAQ", url=SUPPORT_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_success_state(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback=False):
    """Sends the Step 3 Success message"""
    text = (
        "✅ Verification Successful!\n\n"
        "Welcome to the zone. You now have full access to our trading platform. "
        "Click 'Start Trading' below to set up your account and claim your campaign bonuses!"
    )
    reply_markup = get_success_keyboard()
    
    if is_callback and update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: The Entry Point (/start command)"""
    user_id = update.effective_user.id
    
    # Check if user is already a member
    is_member = await is_user_in_channel(context.application, user_id)
    
    if is_member:
        # Condition A: Skip to Step 3
        await send_success_state(update, context, is_callback=False)
    else:
        # Condition B: Welcome & Gatekeeper message
        text = (
            "Welcome to PLAYHUBZONE! 🚀\n\n"
            "To access our premium trading signals and start winning, you must join our "
            "official community channel first. Click the button below to join, then click "
            "'✅ Verify Channel Join'."
        )
        await update.message.reply_text(text, reply_markup=get_gatekeeper_keyboard())


async def verify_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: The Verification Check (Callback query handler)"""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback click
    
    user_id = query.from_user.id
    is_member = await is_user_in_channel(context.application, user_id)
    
    if is_member:
        # Scenario 2B: Success
        # First delete the old gatekeeper message to clean up the chat
        try:
            await query.message.delete()
        except TelegramError:
            pass
        await send_success_state(update, context, is_callback=True)
    else:
        # Scenario 2A: User DID NOT join (The Loopback)
        text = (
            "❌ Verification Failed!\n\n"
            "It looks like you haven't joined our channel yet. Please click the button "
            "below to join the channel, then come back and tap verify again to unlock your access."
        )
        # Modify the existing message or send a new one. Sending a new one ensures they see the update clearly.
        await query.message.reply_text(text, reply_markup=get_gatekeeper_keyboard())


def main():
    """Starts the bot application."""
    # Build the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_button_click, pattern="^verify_join$"))

    # Start the Bot using polling (Perfect for Render Background Worker)
    logger.info("Starting bot polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
