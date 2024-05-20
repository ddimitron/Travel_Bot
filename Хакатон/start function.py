import telebot
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

@bot.message_handler(commands=['start'])
def start_message(message):
    logger.info(f"Получено сообщение от {message.from_user.first_name}: {message.text}")
    bot.reply_to(message, "Привет! Я твой помощник в путешествиях. Чем я могу помочь?")

bot.polling()