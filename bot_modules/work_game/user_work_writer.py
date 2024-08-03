
## Базовые модули.
from json import dump, load

## Модули бота.
from main import DIRPATH

WORK_PATH = f"{DIRPATH}/bot_modules/work_game/user_work"

def write_user_work(
    user_name: str,
    work_start_time: float
) -> None:
    """Запись информации пользователя о его "работе" на сервере.

    Args:
        user_name (str): имя пользователя (member.name)
        work_start_time (float): начало времени работы.
    """
    data_to_write: dict = {
        "user_name": user_name,
        "work_start_time": work_start_time
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


