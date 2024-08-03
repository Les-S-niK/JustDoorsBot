import os
import json
from time import time
from typing import Union

PATH = os.path.dirname(__file__)

def write_voice_channel_info(channel_name: str, channel_id: int) -> None:
    """Записывает в JSON файл информацию о созданном канале.

    Args:
        channel_name (str): Название канала.
        channel_id (int): ID созданного канала.
    """
    start_time: float = time()
    data: dict = {
        'id': channel_id,
        'stime': start_time,
    }
    with open(
        file=f'{PATH}//channels//{channel_name}.json',
        mode='w',
        encoding='utf-8'
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

def get_voice_channel_info() -> Union[dict[int, str],  bool]:
    for channel_name in os.listdir(f'{PATH}//channels'):
        with open(
            file=f'{PATH}//channels//{channel_name}',
            mode='r',
            encoding='utf-8'
        ) as file:
            readed_file: dict = json.load(file)
            if abs(time() - readed_file.get('stime')) > 3_600:
                channel_id: int = readed_file.get('id')
                file.close()
                return [channel_id, channel_name]
            else:
                return False

def delete_voice_channel_file(channel_name: str):
    os.remove(f'{PATH}//channels//{channel_name}')

