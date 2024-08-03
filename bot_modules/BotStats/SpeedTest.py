import speedtest

def calculate_download_speed() -> float:
    """Проводит тест скорости интернета. Возвращает скорость загрузки в МБ.

    Returns:
        float: Скорость загрузки. МБ.
    """
    try:
        speed_test = speedtest.Speedtest(secure=True)
        download_speed = speed_test.download()
        return round((download_speed / 1048576) * 0.08, 2)
    except speedtest.ConfigRetrievalError:
        return "Ошибка с подключением. Попробуйте позже."
        

