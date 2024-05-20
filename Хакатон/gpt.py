import requests
from database import *

FOLDER_ID = ""
GPT_MODEL = ""
TOKEN = ""
MODEL_TEMPERATURE = ""
MAX_MODEL_TOKENS = ""

def city():
    city = execute_selection_query('''SELECT city, addition FROM database''')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347'
    response = requests.get(url).json()
    if response.status_code == 200:
        weather_data = requests.get(url).json()
        return True, weather_data
    else:
        return False, "При запросе к API возникла ошибка."

def gpt():
    # TOKEN = get_creds()
    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

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
             "text": ""},
            {"role": "user", "text": ""},
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()['result']['alternatives'][0]['message']['text']
        return True, result
    else:
        return False, "При запросе к YandexGPT возникла ошибка."





