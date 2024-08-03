import requests
from fake_headers import Headers
from random import randint
from main import EMPTY_IMG_URL

class FreepikImagesParser(object):
    """Класс-парсер изображений с сайта стоковых изображений freepik.com.

    Args:
        object: базовый класс наследования в Python3.
    """
    
    def __init__(self, request: str) -> None:
        """Парсер изображений с freepik.

        Args:
            request (str): запрос, переданный для парсинга.
        """
        self.request: str = request
        self.URL: str = f"https://ru.freepik.com/api/regular/search?locale=ru&term={self.request}"
        self.headers: Headers = self._generate_headers()
        self.image_url: str = self._get_img_url_from_response()


    def _get_img_url_from_response(self) -> str:
        """Получение ссылки на изображение с ответа на <GET> запрос.

        Returns:
            str: Ссылка на изображение.
        """
        response: requests.Response = self._get_response()
        ## Из ответа получаем все словари с изображениями в списке.
        all_images: list = response.json().get("items")
        ## Получаем длину списка.
        all_dicts_counter: int = len(all_images)
        ## Выбираем случайный индекс словаря из доступного количества.
        choiced_dict_number: int = randint(1, all_dicts_counter)
        ## Получаем словарь по индексу.
        choiced_image_dict: dict = all_images[choiced_dict_number]
        ## Из словаря получаем ссылку на изображение.
        image_url: str = choiced_image_dict.get("preview").get("url")
        if image_url:
            return image_url
        else:
            return EMPTY_IMG_URL
        


    def _get_response(self) -> requests.Response:
        """Получает ответ на GET запрос с <URL>.

        Returns:
            requests.Response: ответ на GET запрос.
        """
        response: requests.Response = requests.get(
            url=self.URL,
            headers=self.headers
        )
        if response.ok:
            return response
        else:
            raise requests.RequestException(
                f"""
                Не удалось получить успешный ответ на <GET> запрос с сайта {self.URL}.
                Статус ответа: {response.status_code}.
                """
            )


    @staticmethod
    def _generate_headers() -> Headers:
        """Генерация заголовков для парсинга freepik

        Returns:
            Headers: _description_
        """
        headers = Headers(
            headers=True
        )
        return headers.generate()