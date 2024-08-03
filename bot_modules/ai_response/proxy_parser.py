from random import choice
import requests
from requests import exceptions
from bs4 import BeautifulSoup
from fake_headers import Headers


class ProxyParser(object):
    
    URL = "https://free-proxy-list.net/"
    
    def __init__(self) -> None:
        self.headers = self._generate_headers()
        self.soup = self._get_soup()
        self.proxies = self._parse_html()
    
    def _parse_html(self) -> dict:
        """Парсинг HTML разметки и получение нужных прокси.

        Returns:
            str: Прокси, полученные при парсинге
        """
        ## Получаем элементы из HTML разметки.
        _proxy_html_element: BeautifulSoup = self.soup.find("tbody")
        _all_proxies: list = _proxy_html_element.find_all("tr")
        _random_proxy: BeautifulSoup = choice(_all_proxies)
        _proxy_params: list = _random_proxy.find_all("td")
        
        ## Структурируем полученную информацию из прокси.
        ip = _proxy_params[0].text
        port = _proxy_params[1].text
        _proxy = f"{ip}:{port}"
        
        proxies = {
            "http": f"http://{_proxy}",
            # "https": f"https://{_proxy}"
            }
        return proxies
    
    
    def _get_response(self) -> requests.Response:
        """Получаем ответ от сайта.

        Returns:
            requests.Response: Полученный в ходе GET запроса ответ.
        """
        response: requests.Response = requests.get(
            url=self.URL,
            headers=self.headers
        )
        if response.ok:
            return response
        else:
            raise exceptions.RequestException(f"""
                    Ошибка GET запроса на сайт: {self.URL},
                    Код ответа: {response.status_code})
                    """)

    def _get_soup(self) -> BeautifulSoup:
        """Получаем объект класса BeautifulSoup, содержащий html разметку.

        Returns:
            BeautifulSoup: Html разметка сайта.
        """
        soup = BeautifulSoup(
            markup=self._get_response().content,
            features="lxml"
        )
        return soup


    @staticmethod
    def _generate_headers() -> dict:
        """Генерация заголовков для запросов от cайта.
        Returns:
            dict: Полученные заголовки.
        """
        headers = Headers(
            browser=None,
            os=None,
            headers=True,
        ).generate()
        
        return headers

if __name__ == "__main__":
    parser = ProxyParser()
    print(parser.proxies)
