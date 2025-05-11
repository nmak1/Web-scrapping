import requests
from bs4 import BeautifulSoup
from time import sleep

# Определяем список ключевых слов:
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# URL страницы с новыми статьями
URL = 'https://habr.com/ru/all/'

# Получаем HTML-код страницы
response = requests.get(URL)
response.raise_for_status()

# Парсим HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Находим все статьи на странице
articles = soup.find_all('article')

for article in articles:
    # Получаем заголовок статьи
    title = article.find('h2').find('a').text

    # Получаем ссылку на статью
    link = article.find('h2').find('a')['href']
    if not link.startswith('http'):
        link = 'https://habr.com' + link

    # Получаем текст превью
    preview = article.find('div', class_='article-formatted-body').text

    # Получаем дату публикации
    time = article.find('time')['title']

    # Проверяем наличие ключевых слов в заголовке или превью
    found_in_preview = any(word.lower() in title.lower() or word.lower() in preview.lower() for word in KEYWORDS)

    if found_in_preview:
        print(f'{time} - {title} - {link}')
    else:
        # Если не найдено в превью, проверяем полный текст статьи
        try:
            article_response = requests.get(link)
            article_response.raise_for_status()
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            article_text = article_soup.find('div', class_='article-formatted-body').text

            if any(word.lower() in article_text.lower() for word in KEYWORDS):
                print(f'{time} - {title} - {link} (найдено в полном тексте)')
        except Exception as e:
            print(f'Ошибка при обработке статьи {link}: {e}')

    # Делаем небольшую паузу между запросами
    sleep(1)