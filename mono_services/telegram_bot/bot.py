from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
import requests
import os
import json
from dotenv import load_dotenv
import asyncio

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL')
ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))


categories = []
transaction_id = None


def get_categories():
    global categories
    url = f'{BACKEND_URL}/get_categories'
    resp = requests.get(url)
    if resp.status_code == 200:
        categories = json.loads(resp.text)
    else:
        print(f'Error: {url} (Status {resp.status_code})')


def update_trn(trn_id, category, comment=''):
    url = f'{BACKEND_URL}/update_trn/{trn_id}'
    data = {
        "set_dict": {
            "category": category,
            "comment": comment,
            "handle_marker": "False"
        }
    }
    resp = requests.put(url, json=data)
    return True if resp.status_code == 200 else False


# async def start(update: Update, context: CallbackContext):
#     print('START !!!!!')
#     if update.message.from_user.id == ALLOWED_USER_ID:
#         await update.message.reply_text("Привіт! Я твій Telegram-бот 🤖")
#         get_categories()
#         await get_last_trn(update, context)
#     else:
#         await update.message.reply_text('You do not have sufficient rights to use the bot.')

async def start(update: Update, context: CallbackContext):
    print('START !!!!!')
    if update.message.from_user.id == ALLOWED_USER_ID:
        reply_markup = ReplyKeyboardMarkup([['🔄 Update']], resize_keyboard=True, one_time_keyboard=False, callback_data='update')
        await context.bot.send_message(ALLOWED_USER_ID, "Привіт! Я твій Telegram-бот 🤖", reply_markup=reply_markup)

        # await update.message.reply_text("Привіт! Я твій Telegram-бот 🤖")
        get_categories()
        await get_last_trn(update, context)
    else:
        await context.bot.send_message(ALLOWED_USER_ID, 'You do not have sufficient rights to use the bot.')
        # await update.message.reply_text('You do not have sufficient rights to use the bot.')


async def handle_update_button(update: Update, context: CallbackContext):
    if update.message.text == "🔄 Update":
        await get_last_trn(update, context)


async def button(update: Update, context: CallbackContext):
    global transaction_id
    query = update.callback_query
    await query.answer()

    if query.data == 'more_info':
        categories_chunks = [categories[i:i + 3] for i in range(0, len(categories), 3)]
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"category:{cat}") for cat in chunk] for chunk in categories_chunks]
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith('category:'):
        category_upd = query.data.split(":")[1]
        if update_trn(transaction_id, category_upd):
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
            await context.bot.send_message(ALLOWED_USER_ID, '✅ Done')
            print(update)
            print(update.message)
            await get_last_trn(update, context)
    
    elif query.data == 'update':
        await get_last_trn(update, context)


async def get_last_trn(update: Update, context: CallbackContext):
    global transaction_id
    url = f'{BACKEND_URL}/get_last_trn'
    resp = requests.get(url)
    resp_dict = json.loads(resp.text)
    if resp.status_code == 200 and len(resp_dict) > 0:
        print('sdhfshdjfhdsjfhdsjfhsdjhfsjdhfjdshfjds')
        print(len(resp.text))
        print(len(resp_dict))
        resp_dict = json.loads(resp.text)
        transaction_id = resp_dict['trn_id']

        message = f"""🙀 New unknown transaction 🙀\n
🗓 Date: {resp_dict['dt']}\n
💰 Amount: {resp_dict['amount']}\n
📜 Description: {resp_dict['bank_description']}, {resp_dict['mcc_group_description']} ({resp_dict['mcc_short_description']})"""

        keyboard = [[InlineKeyboardButton("Choose category", callback_data='more_info')]]
        # print(update)
        # await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        await context.bot.send_message(ALLOWED_USER_ID, message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    else:
        print('asleep')
        await asyncio.sleep(10)
        await get_last_trn(update, context)


async def send_startup_message(app: Application):
    """Надсилає повідомлення при старті бота"""
    await app.bot.send_message(chat_id=ALLOWED_USER_ID, text="✅ Бот запущено!")

def main():
    get_categories()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_button))
    app.add_handler(CallbackQueryHandler(button))

    # asyncio.run(send_startup_message(app))
    
    print("Бот запущено...")
    app.run_polling()
    

if __name__ == "__main__":
    main()
