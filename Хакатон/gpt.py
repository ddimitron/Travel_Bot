import requests
from database import *

FOLDER_ID = "b1g23q9ip6n1jnscc7v7"
GPT_MODEL = "yandexgpt-lite"
TOKEN = "t1.9euelZrGzc7MjIqQlI-UjIuMk4zIzO3rnpWayI7Gl4rKiprMyouKlpbPj8bl8_ctdE1N-e94MVhI_d3z920iS03573gxWEj9zef1656Vmp7OnY3NlMeUicuQnpPOmpKS7_zF656Vmp7OnY3NlMeUicuQnpPOmpKSveuelZqelMqdipuZyZyNj5WJzZOUmLXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.UzCCuDTBPN0WgND96tvMGe4en53892b5kz2yuioXgwRn9ftiSU1cFMm0b9c7Hw42kh4wmplGUUAlTI18v8aRAw"
MODEL_TEMPERATURE = "0.6"
MAX_MODEL_TOKENS = "500"

def promt(message):
    user_id = message.from_user.id
    database = execute_selection_query('''SELECT city FROM database WHERE user_id = ?''', (user_id,))[0]
    if message.text == "Узнать экстренные контакты": # Впиши сюда то что у тебя будет на кнопке Посмотреть Контакты
        return f"Скажи адреса Посольств, Аэропортов и Номера экстренных служб в городе {database[0]}."
    elif message.text == "Узнать интересные места": # Впиши сюда то что у тебя будет на кнопке Посмотреть Достопримечательности
        return f"Расскажи о достопримечательностях и впринципе своё мнение о городе {database[0]}. Ограничься 5 Достопримечательностями."

# TODO GPT запросы для получения информации о городе или важных контактах
def gpt(message):
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    user_content = promt(message)

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": MODEL_TEMPERATURE,
            "maxTokens": MAX_MODEL_TOKENS
        },
        "messages": [
            {"role": "system",
             "text": "Ты бот помощник в путешествиях и ты должен помогать пользователю узнать о городе в который он хочет поехать. Не используй ссылки на страницы в браузере."},
            {"role": "user", "text": user_content},
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        return True, result
    else:
        return False, "При запросе к YandexGPT возникла ошибка."

# TODO Инструкция как получать ответ от яндект GPT:
# status, content = gpt(message)
# if status:
#     print(content) # Ответ
# else:
#     print(content) # При ошибке будет выдавать её.