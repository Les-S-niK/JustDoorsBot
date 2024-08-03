
## Основные импорты.
from requests import post, get, Response, RequestException

def get_word_hash() -> str:
        """Получает с API guess-word.ru хэш дневного слова для отправки запросов к API.

        Returns:
            str: полученный хэш слова.
        """
        API_HASH_URL: str = "https://guess-word.ru/api/get_game_hash/"
        response: Response = get(
            url=API_HASH_URL,
        )
        
        if not response.ok:
            raise RequestException(
                f"""
                Ошибка получения ответа API.
                response_status: {response.status_code}
                """
            )
        ## Получаем json объект из ответа.
        word_hash: str = response.json()
        return word_hash



## Класс-парсер "игры в слова". 
class WordsParserGame(object):
    
    def __init__(
        self,
        word: str
    ) -> None:
        """Инициализация класса WordsParserGame. Парсер слов с сайта 
        https://guess-word.ru с целью получения правильности загаданного слова 
        в процентах.
        
        Args:
            word (str): слово, переданное для проверки.
        """
        self.URL: str = "https://guess-word.ru/api/guess/"
        self.word: dict = word
        self.word_hash: str = get_word_hash()
        self._response: dict = self._get_post_response()
        self.percent: int = self._get_percentage_of_guessing()
        self.angle: int = self._get_angle_of_word()


    def _get_percentage_of_guessing(
        self
    ) -> int:
        """Получает процент близости слова к загаданному.

        Returns:
            int: процент близости
        """
        _distance: float = round(self._response.get("distance"), 2)
        ## Получаем процент угадывания.
        percent: int = int((1 - _distance) * 100)
        
        return percent


    def _get_angle_of_word(
        self
    ) -> int:
        """Получает угол местоположения относительно центра окружности.

        Returns:
            int: углол местоположения.
        """
        ## Получаем угол местоположения слова на окружности.
        angle: int = round(self._response.get("angle"))
        
        return angle


    def _get_post_response(
        self
    ) -> dict:
        """Получение ответа от API guess-word.ru на POST запрос.

        Returns:
            Response: Ответ на POST запрос.
        """
        data_for_request: dict = {
            "game_word_hash": self.word_hash,
            "word": self.word
        }
        
        response: Response = post(
            url=self.URL,
            json=data_for_request,
        )
        
        if not response.ok:
            raise RequestException(
                f"""
                Ошибка получения ответа от сервера.
                response_status: {response.status_code}
                word: {self.word}.
                """
            )
        ## Возвращаем json объект из ответа
        return response.json()
