import telebot
import logging

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from gpt import gpt, promt
from weather_function import get_weather
from database import execute_selection_query

bot = telebot.TeleBot()
ADMIN = []  # список админов, должен быть в config.py
keyboard = ['Узнать интересные места', 'Узнать экстренные контакты',
            'Узнать погоду'] # должнo быть в config.py


def make_keyboard(items):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for item in items:
        markup.add(KeyboardButton(item))
    return markup


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename='log_file.txt',
    filemode="w",
)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     "Привет! Я твой помощник в путешествиях. "
                     "Чем я могу помочь?")


@bot.message_handler(commands=['help'])
def handle_help(message):

    bot.send_message(message.from_user.id,
                     "Привет, я помогу тебе в путешествиях. "
                     "Для работы нажимай на кнопки снизу\n"
                     "/choose_city - выбрать город")


@bot.message_handler(commands=['choose_city'])
def choose_city(message):
    bot.send_message(message.from_user.id, "Напиши любой город мира:")
    bot.register_next_step_handler(message, choose_action)


def choose_action(message):
    city = message.text
    markup = make_keyboard(keyboard)
    if message.content_type != 'text':
        bot.send_message(message.from_user.id, 'Отправь текстовое сообщение')
        return
    # добавляем город в бд
    bot.send_message(message.from_user.id, 'Выбери что ты хочешь сделать',
                     reply_markup=markup)
    bot.register_next_step_handler(message, give_info_city)


def give_info_city(message):
    if message.content_type != 'text':
        bot.send_message(message.from_user.id, 'Отправь текстовое сообщение')
        return
    if message.text not in keyboard:
        bot.send_message(message.from_user.id,
                         'Выберите действие из предложенных')
        return
    if message.text == 'Узнать погоду':
        get_weather(message)
    promt(message)
    status, content = gpt(message)
    if status:
        bot.send_message(message.from_user.id, content) # Ответ
    else:
        bot.send_message(message.from_user.id, content) # При ошибке будет выдавать её.


@bot.message_handler(commands=["debug"])
def send_logs(message):
    user_id = message.chat.id
    if user_id in ADMIN:
        with open("log_file.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(user_id, "У вас недостаточно прав")


bot.infinity_polling()
