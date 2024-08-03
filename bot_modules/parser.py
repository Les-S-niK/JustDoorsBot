import requests
from bs4 import BeautifulSoup as BS
from fake_headers import Headers
import random

header = Headers(
    browser='edge',
    os='win',
    headers=True
)

def main(request):
    page = random.randint(1, 5)
    url = f'https://www.shutterstock.com/ru/search/{request}?page={page}'
    response = requests.get(url=url, headers=header.generate())
    if response.ok:
        soup = BS(response.text, features='lxml')
    else:
        return 'https://cdn.discordapp.com/attachments/1208854198112886814/1209465619280437278/908531f5d55a28312b84a4e5a0285e39.jpeg?ex=65e705a2&is=65d490a2&hm=2309fc3acb2c2c4a25b54e91fb81ae553cf6aafdbbeed239313908f054bd6424&'

    images = []
    divs = soup.find('div', class_='mui-1nl4cpc-gridContainer-root')
    links = divs.find_all('img')
    for link in links:
        images.append(link.get('src'))
        
    return random.choice(images)

if __name__ == '__main__':
    print(main('еда'))