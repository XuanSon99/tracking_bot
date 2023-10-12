from telegram import *
from telegram.ext import *
import requests
import json
from types import SimpleNamespace
import math
import random
import time
from datetime import datetime
import pytz
from dateutil import tz

domain = "https://api.chootc.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Tham giá @chootcvn để mua, bán USDT số lượng lớn.", parse_mode=constants.ParseMode.HTML)

async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    print(chat_id)

async def callback_minute(context: ContextTypes.DEFAULT_TYPE):

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for index, item in enumerate(data):
        res = requests.get(
            f"https://api.trongrid.io/v1/accounts/{item['wallet']}/transactions/trc20?limit=1&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
        tx = res.json()['data'][0]
        if item['block_timestamp'] != tx['block_timestamp']:
            data[index]['block_timestamp'] = tx['block_timestamp']
            value = round(float(tx['value'])*pow(10, -6))

            if value >= 50000:

                time = datetime.fromtimestamp(tx['block_timestamp']/1000)

                if tx['from'] == item['wallet']:

                    account = [p for p in data if p['wallet'] == tx['to']]
                    acc = tx['to'][-5:]
                    if account:
                        acc = account[0]['name']

                    text = f"🔴 <b>{item['name']}</b> vừa gửi <b>{value}</b> tới ví <b>{acc}</b>\n<a href='https://tronscan.org/#/transaction/{tx['transaction_id']}'>Chi tiết giao dịch</a>"

                if tx['to'] == item['wallet']:

                    account = [p for p in data if p['wallet'] == tx['from']]
                    acc = tx['from'][-5:]
                    if account:
                        acc = account[0]['name']

                    text = f"<b>🟢 {item['name']}</b> vừa nhận <b>{value}</b> từ ví <b>{acc}</b>\n<a href='https://tronscan.org/#/transaction/{tx['transaction_id']}'>Chi tiết giao dịch</a>"

                await context.bot.send_message(chat_id=-1001986367510, text=text, parse_mode=constants.ParseMode.HTML, disable_web_page_preview=True)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_balance(address):
    url = "https://apilist.tronscan.org/api/account"
    payload = {
        "address": address,
    }
    res = requests.get(url, params=payload)
    trc20token_balances = json.loads(res.text)["trc20token_balances"]
    token_balance = next(
        (item for item in trc20token_balances if item["tokenId"] == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'), None)
    if token_balance == None:
        return 0
    else:
        return f'{round(float(token_balance["balance"])*pow(10, -6)):,}'

app = ApplicationBuilder().token(
    "6568702208:AAGfPceJaWQae39zX57FqqotN3Zx8FWKIUA").build()

# app = ApplicationBuilder().token(
#     "6673254814:AAHt6zx49L2ARt7Yxr46cyrFF2xJeBpY-gs").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, messageHandler))

# job_queue = app.job_queue

# job_minute = job_queue.run_repeating(callback_minute, interval=20, first=1)

app.run_polling()
