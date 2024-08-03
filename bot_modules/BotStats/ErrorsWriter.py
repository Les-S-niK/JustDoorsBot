from main import DIRPATH
from datetime import datetime

def error_write(error: str) -> None:
    """Запись ошибок бота в специальную папку Errors для их дальнейшего изучения.

    Args:
        error (str): Произошедшая ошибка.
    """
    with open(f"{DIRPATH}//Errors//{str(datetime.now()).replace(':', '.')}.error", "w", encoding="utf-8") as file:
        file.write(error)
