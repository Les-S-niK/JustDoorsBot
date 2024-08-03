
## Базовые импорты
from json import dump, load

## Импорты модулей бота.
from main import DIRPATH

def write_new_game_state(
    is_active: bool
) -> None:
    """Записывает в JSON файл bool значение о том, идёт игра или нет (T/F)

    Args:
        is_active (bool): Идёт ли игра сейчас?
    """
    to_write_data: dict = {
        "is_active": is_active
    }
    
    with open(
        file=f"{DIRPATH}/bot_modules/words_game/is_active.json",
        mode="w+",
        encoding="utf-8"
    ) as file:
        ## Запись данных в файл JSON.
        dump(
            obj=to_write_data,
            fp=file,
            ensure_ascii=False,
            indent=4
        )

def check_game_state() -> bool:
    """Читает из is_active.json значение о том, идёт ли сейчас игра. 

    Returns:
        bool: Идёт ли игра сейчас?
    """
    try:
        with open(
            file=f"{DIRPATH}/bot_modules/words_game/is_active.json",
            mode="r",
            encoding="utf-8"
        ) as file:
            ## Чтение данных из JSON.
            readed_data: dict = load(
                fp=file
            )
            ## Получение bool значения из dict.
            is_active: bool = readed_data.get("is_active")
            return is_active
    
    except FileNotFoundError:
        print("Файл .json не существует!")