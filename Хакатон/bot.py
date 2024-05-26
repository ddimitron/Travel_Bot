import telebot
import logging

from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from gpt import gpt
from weather_function import get_weather
from database import execute_selection_query, execute_query, prepare_database
from config import keyboard, keyboard2, ADMINS

bot = telebot.TeleBot("")

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
    user = execute_selection_query("SELECT * FROM database WHERE user_id = ?", (message.chat.id,))
    if user:
        start_keyboard(message)
    else:
        execute_query('''INSERT INTO database (user_id) VALUES (?)''', (message.chat.id,))
        bot.send_message(message.chat.id,
                         "Привет! Я твой помощник в путешествиях. Что бы ознакомиться с информацией как мной пользоваться нажмите на кнопку помощь.")
        start_keyboard(message)

def handle_help(message):
    bot.send_message(message.from_user.id,
                     "Это бот - Помощник в путешествиях, он может рассказать о городе что бы начать нужно нажать на кнопку выбрать город и ввести нужный вам город.")
    start_keyboard(message)

def start_keyboard(message):
    markup = make_keyboard(keyboard2)
    bot.send_message(message.from_user.id, 'Выбери что ты хочешь сделать',
                        reply_markup=markup)
    bot.register_next_step_handler(message, detection_start_start_keyboard)
def detection_start_start_keyboard(message):
    if message.text == "Дать Обратную свзязь":
        reception_back_info(message)
    elif message.text == "Помощь":
        handle_help(message)
    elif message.text == "Выбрать город":
        choose_city(message)

def choose_city(message):
    bot.send_message(message.from_user.id, "Напиши любой город мира:")
    bot.register_next_step_handler(message, city)


def city(message):
    if message.content_type != 'text':
        bot.send_message(message.from_user.id, 'Отправь текстовое сообщение')
        choose_city(message)
        return
    status, content = get_weather(message.text)
    if status:
        execute_query('''UPDATE database SET city = ? WHERE user_id = ?''', (message.text, message.from_user.id))
        choose_action(message)
    else:
        bot.send_message(message.from_user.id, "Такого города несуществует.")
        choose_city(message)


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
        status, content = get_weather(city)
        bot.send_message(message.from_user.id, content)
        choose_action(message)
        return
    elif message.text == 'Другой город':
        choose_city(message)
        return
    elif message.text =="Вернуться в главное меню":
        start_keyboard(message)
        return
    status, content = gpt(message)
    if status:
        bot.send_message(message.from_user.id, content) # Ответ
        choose_action(message)
    else:
        bot.send_message(message.from_user.id, content) # При ошибке будет выдавать её.

def reception_back_info(message):
    bot.send_message(message.from_user.id, "Напиши обратную связь:")
    bot.register_next_step_handler(message, send_back_info)


def send_back_info(message):
    bot.send_message(message.chat.id, "Спасибо за обратную связь")
    bot.send_message("-1002217836488", f"От юзера {message.from_user.id} "
                            f"отправлена обратная информация:\n {message.text}")
    start_keyboard(message)


@bot.message_handler(commands=["debug"])
def send_logs(message):
    user_id = message.chat.id
    if user_id in ADMINS:
        with open("log_file.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(user_id, "У вас недостаточно прав")


if __name__ == "__main__":
    bot.infinity_polling()
    logging.info("The bot is running")
    prepare_database()




