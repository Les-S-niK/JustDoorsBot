
## Базовые импорты
from json import dump, load

## Импорты модулей бота.
from main import DIRPATH

def write_new_words_count(
    new_count: int
) -> None:
    """Записывает новое число в значение words_count.

    Args:
        new_count (int): Новое число количества слов.
    """
    to_write_data: dict = {
        "words_count": new_count
    }
    
    with open(
        file=f"{DIRPATH}/bot_modules/words_game/words_count.json",
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

def check_words_count() -> int:
    """Читает words_count из JSON файла и возвращает его.

    Returns:
        int: число слов.
    """
    try:
        with open(
            file=f"{DIRPATH}/bot_modules/words_game/words_count.json",
            mode="r",
            encoding="utf-8"
        ) as file:
            ## Чтение данных из JSON.
            readed_data: dict = load(
                fp=file
            )
            ## Получение int значения из dict.
            words_count: int = readed_data.get("words_count")
            return words_count
    
    except FileNotFoundError:
        write_new_words_count(1)
        return 1