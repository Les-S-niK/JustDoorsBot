import random

FILES = ['ddp.gif', 'ddr.gif', 'dpd.gif', 'dpp.gif',
'drd.gif', 'drr.gif', 'pdd.gif', 'pdp.gif',
'ppd.gif', 'ppr.gif', 'prp.gif', 'prr.gif',
'rdd.gif', 'rdr.gif', 'rpp.gif', 'rpr.gif',
'rrd.gif', 'rrp.gif', 'prd.gif', 'drp.gif',
'dpr.gif', 'pdr.gif', 'rdp.gif', 'rpd.gif',]



def win_or_defeat() -> bool:
    """Расчёт победы / поражения в казино. 
    Returns:
        bool: True-победа, False-поражение
    """
    choise: float = round(random.random(), 2)
    
    if choise > 0.3:
        return False
    else:
        return True


def calc_inwin() -> str:
    """В случае победы расчёт какой куш сорвёт пользователь.

    Returns:
        str: название GIF файла с удачным спином.
    """
    choise: float = round(random.random(), 2)
    if choise <= 0.11:
        return 'DDD'
    elif choise <= 0.35:
        return 'PPP'
    elif choise > 0.35:
        return 'RRR'


def get_random_filename_defeat() -> str:
    """Получает случайное имя файла из списка <FILES> в случае проигрыша.

    Returns:
        str: случайное имя файла.
    """
    file_name: str = random.choice(FILES)
    return file_name

