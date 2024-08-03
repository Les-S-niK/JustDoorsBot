
## Базовые импорты
from json import dump, load

## Импорты модулей бота.
from main import DIRPATH

def write_new_last_word(
    last_word: str,
    percent: int,
    angle: int
) -> None:
    """Записывает в JSON слово и процент его совпаденя.

    Args:
        last_word (str): Последнее слово.
        percent (int): Процент совпадения.
        angle (int): угол относительно центра.
    """
    to_write_data: dict = {
        "last_word": last_word,
        "percent": percent,
        "angle": angle
    }
    
    with open(
        file=f"{DIRPATH}/bot_modules/words_game/last_word.json",
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

def check_last_word() -> list:
    """Проверяет последнее слово с наивысшим процентом совпадения.

    Returns:
        List[str, int, int]: Слово и процент совпадения.
    """
    try:
        with open(
            file=f"{DIRPATH}/bot_modules/words_game/last_word.json",
            mode="r",
            encoding="utf-8"
        ) as file:
            ## Чтение данных из JSON.
            readed_data: dict = load(
                fp=file
            )
            ## Получение значений из JSON.
            last_word: str = readed_data.get("last_word")
            percent: int = readed_data.get("percent")
            angle: int = readed_data.get("angle")
            return [last_word, percent, angle]
    
    except FileNotFoundError:
        write_new_last_word(
            last_word="Удачи",
            percent=0,
            angle=0
        )
        return ["Удачи", 0, 0]