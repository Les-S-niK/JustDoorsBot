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
