import pickle
import os
import time

import telebot
import requests

from pydantic import BaseModel

TOKEN = os.environ.get(
    "TOKEN",
    default='your_token'
)
BASE_URL = 'https://api.exchangeratesapi.io/latest?base='
DB_NAME = 'db.p'
BASE_RATE = 'USD'

bot = telebot.TeleBot(TOKEN)


class CurrencyData(BaseModel):
    rates: dict
    base: str
    date: str
    last_request = time.time()


def pars_data(currency: str = BASE_RATE) -> CurrencyData:
    url = BASE_URL + currency
    exchange_rate = requests.get(url).json()
    data = CurrencyData(**exchange_rate)
    return data


def open_db() -> dict:
    with open(DB_NAME, 'rb') as file:
        db = pickle.load(file)
    return db


def update_db(currency: str) -> dict:
    with open(DB_NAME, 'wb') as file:
        data = pars_data().dict()
        pickle.dump({currency: data}, file)
    return data


def output_list(data: dict) -> str:
    output = ''
    for i, j in data['rates'].items():
        output += f'{i}: {round(j, 2)}\n'
    return output


def check_rate(currency: str) -> dict:
    try:
        if os.path.getsize(DB_NAME) > 0:
            data = open_db()
            if currency in open_db() and \
                    data.get(currency, False).get('last_request', 0) < 600:
                currency_data = data[currency]
            else:
                currency_data = update_db(currency)
        else:
            currency_data = update_db(currency)
    except Exception:
        open(DB_NAME, 'wb')
        currency_data = update_db(currency)
    return currency_data


@bot.message_handler(commands=['start', 'help'])
def start(mess):
    output = """Hi, I am exchange rate telegram bot
My commands:
    🟢/start and /help - output this message;
    🟢/list or /list [currency] - output list of all available rates
    (example: list RUB. Default currency USD);
    🟢/exchange [amount] [currency_1] to [currency_2] - converts the first brew to the second;
    (example: exchange 10 USD to RUB)
"""
    bot.send_message(mess.chat.id, output)


@bot.message_handler(commands=['list'])
def list_rate(mess):
    currency = 'USD'
    message = mess.text.split(' ')
    if len(message) > 1:
        currency = message[1]
    try:
        data = check_rate(currency)
        output = output_list(data)
        bot.send_message(mess.chat.id, output)
    except Exception:
        bot.send_message(mess.chat.id, 'Error')


@bot.message_handler(commands=['exchange'])
def exchange(mess):
    try:
        command = mess.text.split(' ')
        amount = command[1]
        first_currency = command[2]
        second_currency = command[-1]

        if amount.startswith('$'):
            amount = int(amount.replace('$', ''))
            first_currency = 'USD'

        data = check_rate(first_currency)
        answer = data['rates'][second_currency] * int(amount)
        output = f'{round(answer, 2)}'
        bot.send_message(mess.chat.id, output)
    except Exception:
        bot.send_message(mess.chat.id, 'Error')


bot.polling()
