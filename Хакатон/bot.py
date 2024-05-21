import telebot
import logging

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from gpt import gpt
from weather_function import get_weather
from database import execute_selection_query, execute_query, prepare_database

bot = telebot.TeleBot("7002498917:AAG82cmSQFUN_Y6epWLQkQEXlrlbTuIgHpg")
ADMIN = []  # список админов, должен быть в config.py
keyboard = ['Узнать интересные места', 'Узнать экстренные контакты',
            'Узнать погоду'] # должнo быть в config.py


prepare_database()

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
                     "Введите /help чтобы посмотреть доступные команды.")
    user = execute_selection_query("SELECT * FROM database WHERE user_id = ?", (message.chat.id,))
    if user:
        handle_help(message)
    else:
        execute_query('''INSERT INTO database (user_id) VALUES (?)''', (message.chat.id,))


@bot.message_handler(commands=['help'])
def handle_help(message):

    bot.send_message(message.from_user.id,
                     "Привет, я помогу тебе в путешествиях. "
                     "Для работы нажимай на кнопки снизу\n"
                     "/choose_city - выбрать город")


@bot.message_handler(commands=['choose_city'])
def choose_city(message):
    bot.send_message(message.from_user.id, "Напиши любой город мира:")
    bot.register_next_step_handler(message, city)

def city(message):
    if message.content_type != 'text':
        bot.send_message(message.from_user.id, 'Отправь текстовое сообщение')
        bot.register_next_step_handler(message, choose_city)
    execute_query('''UPDATE database SET city = ? WHERE user_id = ?''', (message.text, message.from_user.id))
    choose_action(message)

def choose_action(message):
    markup = make_keyboard(keyboard)
    bot.send_message(message.from_user.id, 'Выбери что ты хочешь сделать',
                     reply_markup=markup)
    bot.register_next_step_handler(message, give_info_city)

def give_info_city(message):
    if message.text not in keyboard:
        bot.send_message(message.from_user.id,
                         'Выберите действие из предложенных')
        return
    if message.text == 'Узнать погоду':
        city = execute_selection_query("SELECT city FROM database WHERE user_id = ?", (message.from_user.id,))[0][0]
        weather = get_weather(city)
        bot.send_message(message.from_user.id, weather)
        choose_action(message)
    elif message.text == 'Узнать интересные места' or 'Узнать экстренные контакты':
        status, content = gpt(message)
        if status:
            bot.send_message(message.from_user.id, content) # Ответ
            choose_action(message)
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


