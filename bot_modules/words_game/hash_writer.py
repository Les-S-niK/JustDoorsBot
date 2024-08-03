## Базовые импорты
from json import dump, load

## Импорты модулей бота.
from main import DIRPATH

def new_word_hash_write(
    new_word_hash: str
) -> None:
    """Записывает в JSON файл str значение хэша последнего зашифрованного слова.

    Args:
        new_hash (str): новый хэш для записи.
    """
    to_write_data: dict = {
        "word_hash": new_word_hash
    }
    
    with open(
        file=f"{DIRPATH}/bot_modules/words_game/word_hash.json",
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

def check_old_hash() -> str:
    """Читает из word_hash.json значение хэша. 

    Returns:
        str: хэш слова.
    """
    try:
        with open(
            file=f"{DIRPATH}/bot_modules/words_game/word_hash.json",
            mode="r",
            encoding="utf-8"
        ) as file:
            ## Чтение данных из JSON.
            readed_data: dict = load(
                fp=file
            )
            ## Получение bool значения из dict.
            old_word_hash: str = readed_data.get("word_hash")
            return old_word_hash
    
    except FileNotFoundError:
        print("Файл .json не существует!")