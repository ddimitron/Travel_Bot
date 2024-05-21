import telebot
import logging

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from gpt import gpt
from weather_function import get_weather

bot = telebot.TeleBot()
ADMIN = []  # список админов, должен быть в config.py


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
    keyboard = ['/info_city', '/weather_city']
    markup = make_keyboard(keyboard)
    bot.send_message(message.from_user.id,
                     "Привет, я помогу тебе в путешествиях. "
                     "Для работы нажимай на кнопки снизу\n"
                     "/info_city - информация о городе и его "
                     "интересных местах\n"
                     "/weather_city - подсказать погоду в городе",
                     reply_markup=markup)


@bot.message_handler(commands=['info_city'])
def choice_city(message):
    bot.send_message(message.from_user.id, "Напиши любой город мира:")
    bot.register_next_step_handler(message, give_info_city)


def give_info_city(message):
    city = message.text
    if message.content_type != 'text':
        bot.send_message(message.from_user.id, 'Отправь текстовое сообщение')
        return
    # TODO: добавить здесь валидации
    # добавка пользователя в бд
    status, content = gpt(city)

    bot.send_message(message.from_user.id, content)


@bot.message_handler(commands=['weather_city'])
def choice_city(message):
    bot.send_message(message.from_user.id, "Напиши любой город мира:")
    bot.register_next_step_handler(message, give_weather_city)


def give_weather_city(message):
    city = message.text
    if message.content_type != 'text':
        bot.send_message(message.from_user.id, 'Отправь текстовое сообщение')
        return
    # TODO: добавить здесь валидации
    # добавка пользователя в бд
    content = get_weather(city)

    bot.send_message(message.from_user.id, content)


@bot.message_handler(commands=["debug"])
def send_logs(message):
    user_id = message.chat.id
    if user_id in ADMIN:
        with open("log_file.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(user_id, "У вас недостаточно прав")


bot.infinity_polling()
