import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@online_cazino_big"  # Ensure bot is Admin in this channel
PLAY_NOW_URL = "https://cazino-big.com/?register=true&campaign_id=7&source_landing=telegram&agent_id=33"
HELP_URL = "https://www.cazino-big.com/article/faq?agent_id=33"

async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Tracking: Capture start parameters from Ads
    ref_param = context.args[0] if context.args else "direct"
    
    # Log for your Dashboard/Analytics
    print(f"User {user.id} joined via {ref_param}")

    text = (
        "Welcome 👋\n\n"
        "Join the inner circle! Subscribe now to unlock:\n"
        "🎟 Monthly VIP Raffle entry (1 free ticket)\n"
        "✨ Exclusive member-only perks\n"
        "🎁 Much, much more...\n\n"
        "Every month, our members get the chance to win luxury prizes — "
        "including high-end watches and special rewards you won’t find anywhere else.\n\n"
        "Don’t just play. Be part of the inner circle. 💎\n\n"
        "Step 1/2: Join our channel to unlock."
    )
    
    buttons = [
        [InlineKeyboardButton("✅ Join Channel", url="https://t.me/online_cazino_big")],
        [InlineKeyboardButton("🔓 I Joined (Unlock)", callback_data="check_sub")]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "check_sub":
        is_subscribed = await check_subscription(user_id, context)
        
        if is_subscribed:
            unlocked_text = (
                "Unlocked 🎉\n\n"
                "Step 2/2: Continue to the site."
            )
            buttons = [
                [InlineKeyboardButton("🎰 Play Now", url=PLAY_NOW_URL)],
                [InlineKeyboardButton("🎁 YOUR $25 WELCOME GIFT IS WAITING!", url=PLAY_NOW_URL)],
                [InlineKeyboardButton("💬 Support", url=HELP_URL)]
            ]
            await query.edit_message_text(unlocked_text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            fail_text = (
                "You’re not subscribed yet. Join the channel to unlock access.\n\n"
                "• Access VIP Raffles\n• Daily Bonuses\n• Exclusive Content"
            )
            buttons = [
                [InlineKeyboardButton("✅ Join Channel", url="https://t.me/online_cazino_big")],
                [InlineKeyboardButton("🔓 Try Again", callback_data="check_sub")],
                [InlineKeyboardButton("💬 Help", url=HELP_URL)]
            ]
            await query.edit_message_text(fail_text, reply_markup=InlineKeyboardMarkup(buttons))

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
