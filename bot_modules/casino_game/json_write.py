import json
from os import listdir
from main import BOT_NAME, DIRPATH

DIR_PATH = f"{DIRPATH}/bot_modules/casino_game/user_saves"


def get_user_balance(user_name: str) -> float:
    """Чтение JSON файла с монетами.
    
    Args:
        user_name (str): Имя пользователя, чей файл надо искать.
        
    Returns:
        float: Полученное количество монет.
    """
    ## Проверка есть ли файл с пользователем в директории.
    if f'{user_name}.json' not in listdir(DIR_PATH):
        data_to_write: dict = {
            'user_name': user_name,
            'count': 0.0
        }
        ## Если нет: создаём файл и записываем туда количество монет, равное 0 и возвращаем 0.
        with open(
                file=f'{DIR_PATH}/{user_name}.json',
                mode='w',
                encoding="utf-8"
            ) as file:
            json.dump(fp=file, obj=data_to_write)
        
        return 0.0
    
    else:
        ## Если есть: читаем файл и возвращаем количество монет пользователя. 
        with open(
                file=f'{DIR_PATH}/{user_name}.json',
                mode='r',
                encoding="utf-8"
            ) as file:
            readed_info: dict = json.load(fp=file)
        
        return readed_info['count']


def get_turnover() -> float:
    """Чтение всех файлов и возвращение общего оборота монет.
    
    Returns:
        float: Оборот монет.
    """
    all_files: list = listdir(DIR_PATH)
    all_moneys: float = 0.0
    ## Перебираем каждый файл в директории и получаем количество монет каждого пользователя.
    for file in all_files:
        with open(
                file=f'{DIR_PATH}/{file}',
                mode='r',
                encoding="utf-8"
            ) as file:
            readed_info = json.load(file)
        ## Получаем монеты пользователя и добавляем их количество в сумму всех монет.
        money: float = readed_info['count']
        all_moneys += money
    
    return all_moneys


def add_balance_all_users(
    count: float
) -> None:
    """Запись <count> монет всем пользователям в JSON файл.

    Args:
        count (float): Количество монет пользователя.
    """
    
    all_user_files: list = listdir(DIR_PATH)
    
    for user_file in all_user_files:
        with open(
            file=f"{DIR_PATH}/{user_file}.json",
            mode="r",
            encoding="utf-8",
        ) as file:
            readed_data: dict = json.load(
                fp=file
            )
            balance: float = readed_data.get("count")
            user_name: str = readed_data.get("user_name")

        data_to_write: dict = {
            'user_name': user_name,
            'count': round(balance + count, 2)
        }
    
        with open(
            file=f'{DIR_PATH}/{user_name}.json',
            mode='w',
            encoding="utf-8"
        ) as file:
            json.dump(
                fp=file,
                obj=data_to_write
            )
        
    return None


def get_bot_money() -> float:
    """Получение количества монет у <BOT_NAME>.

    Returns:
        float: Полученное количество монет.
    """
    ## Получаем баланс бота.
    bot_money: float = get_user_balance(user_name=BOT_NAME)
    
    return bot_money


def write_user_balance(user_name: str, count: float) -> None:
    """Запись <count> монет пользователя <user_name> в JSON файл.

    Args:
        user_name (str): Имя пользователя.
        count (float): Количество монет пользователя.
    """
    data_to_write: dict = {
        'user_name': user_name,
        'count': round(count, 2)
    }
    with open(
            file=f'{DIR_PATH}/{user_name}.json',
            mode='w',
            encoding="utf-8"
        ) as file:
        json.dump(
            fp=file,
            obj=data_to_write
        )
    
    return None


