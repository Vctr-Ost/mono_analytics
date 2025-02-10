from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import requests
import os
import json
import ast
import asyncio

from dotenv import load_dotenv
load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL')
ALLOWED_USER_ID = os.getenv('ALLOWED_USER_ID')

state_marker = True
categories = []
transaction_id = None
category_upd = None


async def check_state_marker(application: Application):
    """ Фоновий процес, який перевіряє змінну state_marker кожні 5 секунд. """
    global state_marker
    while True:
        if state_marker:
            print("🔄 State marker == True, викликаю get_last_trn...")
            for chat_id in application.bot_data.get("active_chats", []):
                await get_last_trn(chat_id, application)
            state_marker = False  # Скидаємо state_marker після обробки
        await asyncio.sleep(5)  # Перевіряємо кожні 5 секунд


def get_categories():
    global categories
    url = f'{BACKEND_URL}/get_categories'
    resp = requests.get(url)
    if resp.status_code == 200:
        categories = ast.literal_eval(resp.text)
        print(categories)
    else:
        print(f'{url} URL is not response (Status {resp.status_code})')


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
    if resp.status_code == 200:
        return True
    else:
        return False
        


async def start(update: Update, context: CallbackContext):
    if update.message.from_user.id == int(ALLOWED_USER_ID):
        await update.message.reply_text(f"Привіт! Я твій Telegram-бот нахуй 🤖")
    else:
        await update.message.reply_text('You do not have sufficient rights to use the bot.')
    


async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == 'more_info':
        
        print(f'transaction_id - {transaction_id}')
        categories_chunks = [categories[i:i + 3] for i in range(0, len(categories), 3)]
        keyboard = [
            [InlineKeyboardButton(category, callback_data=f"category:{category}") for category in chunk] 
            for chunk in categories_chunks
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    
    if query.data.startswith('category:'):
        global category_upd
        category_upd = query.data.split(":")[1]
        resp = update_trn(transaction_id, category_upd)
        print(resp)
        if resp:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))


async def get_last_trn(update: Update, context: CallbackContext):
    url = f'{BACKEND_URL}/get_last_trn'
    resp = requests.get(url)
    if resp.status_code == 200:
        resp = resp.text
        resp_dict = json.loads(resp)

        global transaction_id
        transaction_id = resp_dict['trn_id']
        
        message = f"""🙀 New unknown transaction 🙀\n
🗓 Date: {resp_dict['dt']}\n
💰 Amount: {resp_dict['amount']}\n
📜 Description: {resp_dict['bank_description']}, {resp_dict['mcc_group_description']} ({resp_dict['mcc_short_description']})"""

        keyboard = [
            [InlineKeyboardButton("Choose category", callback_data='more_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup)


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("g", get_last_trn))

    app.add_handler(CallbackQueryHandler(button))       # Обробка натискання кнопок
    
    print("Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    get_categories()
    main()
