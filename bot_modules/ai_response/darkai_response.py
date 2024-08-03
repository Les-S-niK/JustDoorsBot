import requests
from requests import exceptions
import json
from fake_headers import Headers
from bot_modules.ai_response.proxy_parser import ProxyParser
from bot_modules.ai_response.json_writter import JSON_PATH, get_from_json

class DarkAiResponseParser(object):
    
    URL: str = "https://darkai.foundation/chat"
    
    def __init__(self, request: str) -> None:
        """Парсер ответов от Darkai. 
        Args:
            request (str): Запрос, на который пользователь желает получить ответ.
        """
        self.request: str = request
        self.headers: dict = self._generate_headers()
        self.response: dict = self._get_response()
    
    def _get_response(self) -> str:
        """Получаем ответ от генеративной AI модели.

        Returns:
            str: Ответ, полученный при передаче запроса.
        """
        _json: dict = {
            "history":  
                get_from_json(JSON_PATH),
            "model": "llama-3-70b",
            "query": f"{self.request}.",
        }
        response: requests.Response = requests.post(
            url=self.URL,
            json=_json,
            headers=self.headers,
            proxies=self._generate_proxies()
        )
        
        if response.ok:
            ## Получаем нужный блок данных из ответа <response>. Люблю этот поломанный JSON.
            _response_content: dict = json.loads(response.text.split("\n")[-3].replace("data: ", ""))
            ai_response: str = str(_response_content.get("data").get("message"))
            return ai_response
        
        else:
            raise exceptions.RequestException(f"""
                Ошибка подключения к {self.URL}.
                Статус ответа: {response.status_code}.
                Json: {response.text}""")
    
    @staticmethod
    def _generate_proxies():
        proxies = ProxyParser().proxies
        return proxies
        
    @staticmethod
    def _generate_headers() -> dict:
        """Генерация заголовков для запросов от AI модели.

        Returns:
            dict: Полученные заголовки.
        """
        headers = Headers(
            browser=None,
            os=None,
            headers=True,
        ).generate()
        
        return headers
