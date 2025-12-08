from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, InlineQueryHandler, CallbackQueryHandler, ContextTypes

from core.texts import TEXTS
from core.config_loader import CFG
from core.admin_system import adminpanel, admin_userinfo, broadcast, admin_callbacks, show_all_users
from core.utils import check_user
from core.anime_bot_core import random_inline

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_user(update, context) < 0:
        return
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(TEXTS["main_menu"]["inline_button"], switch_inline_query_current_chat="")]])
    await context.bot.send_message(chat_id=chat_id, reply_to_message_id=message_id, text=TEXTS["main_menu"]["title"].format(version=CFG["VERSION"]), reply_markup=keyboard, parse_mode="HTML")

async def developer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_user(update, context) < 0:
        return
    message_id = update.effective_message.message_id
    markup = InlineKeyboardMarkup([[InlineKeyboardButton(r"¯\_(ツ)_/¯", callback_data="emptycallback")]])
    await update.effective_chat.send_animation("CAACAgQAAxkBAAEYyVZpDKbhBLct5GxqAgLGhtlAtFw-XgAC5RoAAl5MgVAKPOJUbDxWLjYE", reply_to_message_id=message_id)
    await update.effective_chat.send_message(text=TEXTS["dev"].format(version=CFG["VERSION"]), reply_to_message_id=message_id, reply_markup=markup, parse_mode="HTML")

# ——— Global Callbacks ———
async def global_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    # user_id = update.effective_user.id

    # Empty Callback
    if data == "emptycallback":
        await query.answer(r"¯\_(ツ)_/¯")
        return

# ——— App bootstrap ———
def main():
    token = CFG["BOT_TOKEN"]
    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dev", developer))
    app.add_handler(CommandHandler("users", show_all_users))
    app.add_handler(CommandHandler("user", admin_userinfo))
    app.add_handler(CommandHandler("adminpanel", adminpanel))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Inline Handler
    app.add_handler(InlineQueryHandler(random_inline))

    # Callbacks
    app.add_handler(CallbackQueryHandler(global_callbacks, pattern=r"^(emptycallback)$"))
    app.add_handler(CallbackQueryHandler(admin_callbacks, pattern=r"^(admin_|show_users:|toggle_user_notify|status_panel|adminpanel)"))

    print("Bot started")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
