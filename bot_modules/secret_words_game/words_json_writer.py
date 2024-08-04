
## Основные модули 
from json import dump, load

## Модули бота
from main import DIRPATH, BOT_PREFIX
from bot_modules.command_logger import error_logger

WORDS_PATH = f"{DIRPATH}/bot_modules/secret_words_game/secret_words.json"

def write_secret_word(
    word: str,
    add: bool
) -> None:
    """Запись `секретного слова в JSON файл для дальнейших надобностей.`

    Args:
        word (str): `Секретное слово`, которое записывается в JSON.
        add (bool): Удаляем или добавляем слово.
    """
    
    ## Переводим слово в нижний регистр.
    word: str = word.lower()
    
    ## Пытаемся открыть файл.
    try:
        with open(
            file=WORDS_PATH,
            mode="r",
            encoding="utf-8"
        ) as file:
            ## Читаем открытый файл.
            readed_file: dict = load(
                fp=file
            )
    ## Если файл не существует.
    except FileNotFoundError:
        readed_file: dict = {
            "words": {}
        }
    ## В любом случае записываем новую информацию в JSON, создавая его.
    finally:
        with open(
            file=WORDS_PATH,
            mode="w",
            encoding="utf-8"
        ) as file:
            ## Получаем все секретные слова и добавляем в них новое.
            all_secret_words: set = set(readed_file.get("words"))
            ## Добавляем или удаляем слово в записимости от надобности.
            if add:
                all_secret_words.add(word)
            else:
                try:
                    all_secret_words.remove(word)
                except KeyError as error:
                    file.close()
                    error_logger(
                        error=error,
                        command_name=f"{BOT_PREFIX}del_secret",
                        args=f"word: {word}"
                    )
                    return None

            all_secret_words: list = list(all_secret_words)
            
            ## Создаём словарь, который записываем в JSON.
            to_write: dict = {
                "words": all_secret_words
            }
            ## Запись словаря в JSON.
            dump(
                obj=to_write,
                fp=file,
                ensure_ascii=False,
                indent=4
            )


def get_all_secret_words() -> list:
    """Получаем все `секретные` слова из JSON файла.

    Returns:
        list: Список из секретных слов.
    """
    ## Попытка чтения файла.
    try:
        with open(
                file=WORDS_PATH,
                mode="r",
                encoding="utf-8"
            ) as file:
                ## Читаем открытый файл.
                readed_file: dict = load(
                    fp=file
                )
        ## Получаем все секретные слова и возвращаем их.
        all_secret_words: list = readed_file.get("words")
        
        return all_secret_words
    ## Если файл не существует - возвращаем пустой список.
    except FileNotFoundError:
        return []