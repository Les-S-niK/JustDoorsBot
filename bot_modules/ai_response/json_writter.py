import json
from os import path

JSON_PATH = f"{path.dirname(__file__)}//assistant.json"


def write_into_json(json_path: str, data: list) -> None:
    history_data: list = get_from_json(json_path=json_path)
    history_data.append(data)
    new_data = {
        "history":
            history_data
    }
    
    with open(json_path, 'w', encoding="utf-8") as file:
        json.dump(new_data, file, ensure_ascii=False, indent=4)

def get_from_json(json_path: str) -> dict:
    with open(json_path, 'r', encoding="utf-8") as file:
        history_data: dict = json.load(file).get("history")
        
    return history_data