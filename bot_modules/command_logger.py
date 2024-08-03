from main import logger, BOT_NAME


def cog_logger(
    cog_name: str,
) -> None:
    """Функция логгирования запуска когов для <BOT_NAME>

    Args:
        cog_name (str): Название запускаемого кога.
    """
    logger.info(f"""
        {BOT_NAME} COG LOGGER >>>
        Ког: {cog_name}
        Успешно запушен.
        <<<
        """
    )



def command_logger(
    global_name: str,
    name: str,
    command_name: str,
    args: str = None
) -> None:
    """Функция логгирования команд для <BOT_NAME>

    Args:
        global_name (str): Глобальное имя пользователя.
        name (str): Идентификационное имя пользователя.
        command_name (str): Название команды.
        args (str, optional): Аргументы, переданные в команду. Defaults to None.
    """
    logger.debug(f"""
        {BOT_NAME} COMMAND LOGGER >>>
        Пользователь {global_name} ({name})
        Использовал <{command_name}>
        с агрументами <<{args}>>.
        <<<
        """
    )


def event_logger(
    bot_name: str,
    event_name: str,
    args: str = None
) -> None:
    """Функция логгирования событий для <BOT_NAME>

    Args:
        bot_name (str): Глобальное имя бота.
        event_name (str): Название события.
        args (str, optional): Аргументы, переданные в событие. Defaults to None.
    """
    logger.info(f"""
        {BOT_NAME} Event LOGGER >>>
        Бот {bot_name}.
        Использовал <{event_name}>
        с агрументами <<{args}>>.
        <<<
        """
    )


def error_logger(
    error: str,
    command_name: str,
    user_name: str = None,
    args: str = None,
    line: int = None
) -> None:
    """Функция логгирования событий для <BOT_NAME>

    Args:
        error (str): вызванное исключение.
        command_name (str): название команды / события.
        user_name (str): Ник пользователя. Defaults to None.
        args (str): Аргументы, переданные в событие. Defaults to None.
        line (int): строка, на которой произошла ошибка.
    """
    logger.error(f"""
        {BOT_NAME} error LOGGER >>>
        Пользователь {user_name}
        При использовании <{command_name}>
        с агрументами <<{args}>>
        вызвал ошибку: <<<{error}>>>
        на строке №{line}.
        <<<
        """
    )