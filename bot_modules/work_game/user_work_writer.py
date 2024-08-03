
## Базовые модули.
from json import dump, load
from typing import Tuple

## Модули бота.
from main import DIRPATH

WORK_PATH = f"{DIRPATH}/bot_modules/work_game/users_work"

def write_user_work(
    user_name: str,
    work_start_time: float,
    add_wood: bool,
    id: int
) -> None:
    """Запись информации пользователя о его "работе" на сервере.

    Args:
        user_name (str): имя пользователя (member.name)
        work_start_time (float): начало времени работы.
    """
    data_to_write: dict = {
        "user_name": user_name,
        "work_start_time": work_start_time,
        "add_wood": add_wood,
        "id": id
    }
    
    with open(
        file=f"{WORK_PATH}/{user_name}.json",
        mode="w",
        encoding="utf-8"
    ) as file:
        dump(
            obj=data_to_write,
            fp=file,
            indent=4,
            ensure_ascii=False
        )
    return None


def get_user_work_info(
    user_name: str
) -> Tuple[float, bool, int]:
    """Получение информации о "работе" пользователя на сервере Discord.

    Args:
        user_name (str): .name пользователя Discord.

    Returns:
        Tuple[float, bool, int]: Время начала работы и добавлять ли деревяшки пользователю, а также его ID.
    """
    try:
        with open(
            file=f"{WORK_PATH}/{user_name}.json",
            mode="r",
            encoding="utf-8"
        ) as file:
            readed_info: dict = load(
                fp=file
            )
        start_time: float = readed_info.get("work_start_time")
        add_wood: bool = readed_info.get("add_wood")
        user_id: int = readed_info.get("id")
        
        return (start_time, add_wood, user_id) 
    
    except Exception:
        return None


