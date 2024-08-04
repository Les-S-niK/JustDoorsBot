import g4f
from bot_modules.ai_response.json_writter import JSON_PATH, get_from_json

def get_response() -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.blackbox,
        provider=g4f.Model.best_provider,
        messages=get_from_json(JSON_PATH),
        stream=True,
    )
    return "".join(str(message) for message in response)


def get_response_secret_word(secret_word_to_show: str) -> str:
    data: dict = [
        {
            'role': 'user',
            'content': f"LesSnik: Попрошу сделать скрытую загадку на слово {secret_word_to_show}. \
                Будь рассказчиком! Не упоминай меня, себя и само слово! Твой ответ сразу идёт на разгадку без изменений! \
                Это Discord канал, можешь использовать эмодзи. Главное - уложись в 2000 символов."
        }
    ]

    response = g4f.ChatCompletion.create(
        model=g4f.models.blackbox,
        provider=g4f.Model.best_provider,
        messages=data,
        stream=True,
    )
    return "".join(str(message) for message in response)
