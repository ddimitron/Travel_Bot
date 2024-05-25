import requests
from database import *
from config import *
import json
import time

def promt(message):
    user_id = message.from_user.id
    database = execute_selection_query('''SELECT city FROM database WHERE user_id = ?''', (user_id,))[0]
    if message.text == "Узнать экстренные контакты": # Впиши сюда то что у тебя будет на кнопке Посмотреть Контакты
        return f"Скажи адреса Посольств, Аэропортов и Номера экстренных служб в городе {database[0]}."
    elif message.text == "Узнать интересные места": # Впиши сюда то что у тебя будет на кнопке Посмотреть Достопримечательности
        return f"Расскажи о достопримечательностях и впринципе своё мнение о городе {database[0]}. Ограничься 5 Достопримечательностями."
    else:
        return f"Расскажи свежие новости в городе {database[0]}"

# TODO GPT запросы для получения информации о городе или важных контактах
def gpt(message):
    TOKEN = get_creds()
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

def create_new_token():
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    token_data = response.json()
    token_data["expires_at"] = time.time() + token_data["expires_in"]
    with open("TOKEN_PATH.json", "w") as token_file:
        json.dump(token_data, token_file)

def get_creds():
    try:
        with open("TOKEN_PATH.json", "r") as f:
            d = json.load(f)
            expiration = d["expires_at"]
        if expiration < time.time():
            create_new_token()
    except:
        create_new_token()
    with open("TOKEN_PATH.json", "r") as f:
        d = json.load(f)
        token = d["access_token"]

    return token