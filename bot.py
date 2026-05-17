import os
import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import TelegramError

# Set up logging so you can see errors clearly in your Render logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 1. Configuration & Links
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@online_cazino_big"  # Make sure the bot is an admin in this channel!

URL_CHANNEL = "https://t.me/online_cazino_big"
URL_PLAY_NOW = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
URL_HELP = "https://www.cazino-big.com/article/faq?agent_id=33"

# 2. Keyboards - Kept exactly as you like them
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("🎮 Game Mechanics"), KeyboardButton("📝 Strategy Guides")],
        [KeyboardButton("🛡️ Fair Play Rules"), KeyboardButton("⚖️ Privacy Policy")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Inline Keyboard for when someone fails the subscription check
def try_again_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url=URL_CHANNEL)],
        [InlineKeyboardButton("🔓 Try Again / Unlocks", callback_data="check_sub_again")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Inline Keyboard for the Final Unlocked Step
def final_unlocked_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎰 PLAY NOW", url=URL_PLAY_NOW)],
        [InlineKeyboardButton("💬 Support", url=URL_HELP)]
    ]
    return InlineKeyboardMarkup(keyboard)

# 3. Verification Helper Logic
async def is_subscribed(app_bot, user_id: int) -> bool:
    """Checks if the user is actually a member/admin/creator of the channel."""
    try:
        member = await app_bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except TelegramError as e:
        logger.error(f"Could not check channel status for user {user_id}: {e}")
        return False

# 4. Logic Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 *Welcome to the Play Zone Hub!*\n\n"
        "Your dedicated educational tool for mastering game mechanics and strategies. "
        "Our goal is to help you improve your skills through data-driven tips and fair play guides.\n\n"
        "Select a category below to start learning!"
    )
    await update.message.reply_text(
        welcome_text, 
        parse_mode='Markdown', 
        reply_markup=main_menu_keyboard()
    )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🎮 Game Mechanics":
        msg = (
            "⚙️ *Understanding Game Mechanics*\n\n"
            "Mastering the 'rules of the engine' is the first step to winning. We analyze:\n"
            "• Physics and movement timing\n"
            "• Resource management loops\n"
            "• Probability and RNG factors"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    elif text == "📝 Strategy Guides":
        msg = (
            "📝 *Advanced Strategy Guides*\n\n"
            "Elevate your playstyle with these core concepts:\n"
            "• Map awareness and positioning\n"
            "• Effective counter-play techniques\n"
            "• Long-term vs. Short-term objectives"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    elif text == "🛡️ Fair Play Rules":
        # --- VERIFICATION TRIGGER POINT ---
        # When they click this, we verify if they're actually in the channel
        subscribed = await is_subscribed(context.bot, user_id)
        
        if subscribed:
            # Flow 4: If user IS subscribed (Unlocked)
            unlocked_msg = (
                "Unlocked 🎉\n"
                "Step 2/2: Continue to the site.\n\n"
                "🎁 *YOUR $25 WELCOME GIFT IS WAITING!*\n"
                "We’re putting a FREE $25 ticket in your hands just for joining. "
                "Use it to enter our Monthly VIP Raffle and chase the big prize. 💎\n\n"
                "👉 _Account creation takes 30 seconds!_"
            )
            await update.message.reply_text(
                unlocked_msg,
                parse_mode='Markdown',
                reply_markup=final_unlocked_keyboard()
            )
        else:
            # Flow 3: If user is NOT subscribed (Show strict warning benefits)
            not_sub_msg = (
                "❌ *You’re not subscribed yet. Join the channel to unlock access.*\n\n"
                "• 🎟️ Access VIP Raffles\n"
                "• 📈 Daily Bonuses\n"
                "• 💎 Exclusive Content\n"
                "• 💵 15% weekly cashback\n"
                "• 💰 €200,000 monthly withdrawals\n"
                "• 🎁 €500 birthday bonus"
            )
            await update.message.reply_text(
                not_sub_msg,
                parse_mode='Markdown',
                reply_markup=try_again_keyboard()
            )

    elif text == "⚖️ Privacy Policy":
        await update.message.reply_text(
            "Play Zone Hub is an educational tool. We do not collect, store, or share any personal user data."
        )

# 5. Dynamic Inline Button Verification Click Flow
async def check_sub_again_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()  # Removes the loading hour-glass on the button
    
    subscribed = await is_subscribed(context.bot, user_id)
    
    if subscribed:
        unlocked_msg = (
            "Unlocked 🎉\n"
            "Step 2/2: Continue to the site.\n\n"
            "🎁 *YOUR $25 WELCOME GIFT IS WAITING!*\n"
            "We’re putting a FREE $25 ticket in your hands just for joining. "
            "Use it to enter our Monthly VIP Raffle and chase the big prize. 💎\n\n"
            "👉 _Account creation takes 30 seconds!_"
        )
        await query.edit_message_text(
            text=unlocked_msg,
            parse_mode='Markdown',
            reply_markup=final_unlocked_keyboard()
        )
    else:
        # If they lied again, throw a native Telegram alert pop-up message box
        await query.answer(
            text="❌ System check failed! You must join the channel first to unlock this content.",
            show_alert=True
        )

# --- ASYNC MAIN FOR RENDER WORKER ---
async def main():
    if not TOKEN:
        print("ERROR: BOT_TOKEN is missing!")
        return

    print("Play Zone Hub Educational Bot starting...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    # Callback handler to handle the interactive inline 'Try Again / Unlocks' click event
    application.add_handler(CallbackQueryHandler(check_sub_again_callback, pattern="^check_sub_again$"))
    
    async with application:
        await application.initialize()
        await application.start()
        print("Bot is now polling...")
        await application.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
