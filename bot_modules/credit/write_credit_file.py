import json
from os import path, listdir
import time
from typing import Union


directory_path = f'{path.dirname(__file__)}/credit_files'

def create_credit_file(
    user_name: str,
    count: float,
    author_id: int
    ) -> bool:
    """Создаёт JSON файл с записью в него ифнформацию о кредите
    если файла с кредитом не существует. Иначе возвращает False.

    Args:
        user_name (str): Имя пользователя, который берёт кредит.
        count (float): количество монет, на которое взяли кредит.
        author_id (int): ID пользователя.

    Returns:
        bool: Если записать кредит удалось - True, иначе - False.
    """
    if f'{user_name}.json' not in listdir(directory_path):
        credit_data: dict = {
            'user_name': user_name,
            'credit': count,
            'time': time.time(), 
            'id': author_id
        }
        with open(
            file=f'{directory_path}/{user_name}.credit',
            mode='w',
            encoding="utf-8"
        ) as file:
            json.dump(
                obj=credit_data,
                fp=file
            )
        return True
    
    else:
        return False

def check_credit_file_exists(user_name: str) -> bool:
    """Проверка существования файла с кредитной записью пользователя.

    Args:
        user_name (str): Имя пользователя, который берёт кредит.

    Returns:
        bool: Если существет - True, иначе - False.
    """
    all_files: list = listdir(directory_path)
    if f'{user_name}.json' in all_files:
        return True
    else:
        return False
        

def get_info_from_credit() -> Union[list, bool]:
    """Получает информацию с файлов кредита пользователей.

    Returns:
        Union[list, bool]: Словарь с информацией о кредите или False значение, если файла не существует.
    """
    for credit_file in listdir(directory_path):
        with open(f'{directory_path}/{credit_file}', 'r') as file:
            readed_file: dict = json.load(fp=file)
            
        name: str = readed_file['user_name']
        credit: float = readed_file['credit']
        time_: float = readed_file['time']
        user_id: int = readed_file['id']
        
        if time.time() - time_ >= 3_600:
            info: list = [
                name,
                credit,
                time_,
                user_id
            ]
            return info
        else:
            return False
        