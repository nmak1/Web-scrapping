import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List, Optional
import time
from datetime import datetime
import os

# Конфигурация
KEYWORDS = ['дизайн', 'фото', 'web', 'python']
BASE_URL = 'https://habr.com'
ALL_POSTS_URL = urljoin(BASE_URL, '/ru/all/')
REQUEST_DELAY = 1  # Задержка между запросами в секундах
SESSION_CACHE = set()  # Кэш просмотренных статей


# Декоратор для логгирования (простой вариант)
def logger(old_function):
    def new_function(*args, **kwargs):
        call_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        function_name = old_function.__name__

        result = old_function(*args, **kwargs)

        log_entry = (
            f"{call_time} - Вызов функции: {function_name}\n"
            f"Аргументы: args={args}, kwargs={kwargs}\n"
            f"Результат: {result if isinstance(result, (str, int, float, bool)) else 'complex object'}\n"
            "----------------------------------------\n"
        )

        with open('habr_parser.log', 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

        return result

    return new_function


# Альтернативный параметризованный декоратор
def parametrized_logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            call_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            function_name = old_function.__name__

            result = old_function(*args, **kwargs)

            log_entry = (
                f"{call_time} - Вызов функции: {function_name}\n"
                f"Аргументы: args={args}, kwargs={kwargs}\n"
                f"Результат: {result if isinstance(result, (str, int, float, bool)) else 'complex object'}\n"
                "----------------------------------------\n"
            )

            with open(path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)

            return result

        return new_function

    return __logger


@logger
def normalize_text(text: str) -> str:
    """Нормализация текста для поиска"""
    return re.sub(r'[^\w\s]', '', text.lower())


@logger
def contains_keywords(text: str, keywords: List[str]) -> bool:
    """Проверяет содержит ли текст ключевые слова"""
    normalized_text = normalize_text(text)
    return any(normalize_text(keyword) in normalized_text for keyword in keywords)


@parametrized_logger('habr_articles.log')
def get_article_preview_data(article) -> Optional[dict]:
    """Извлекает данные из превью статьи"""
    try:
        title_element = article.find('h2')
        if not title_element:
            return None

        link_element = title_element.find('a')
        if not link_element:
            return None

        preview_element = article.find('div', class_=re.compile(r'article-formatted-body'))
        time_element = article.find('time')

        return {
            'title': link_element.text.strip(),
            'url': urljoin(BASE_URL, link_element.get('href')),
            'preview': preview_element.text.strip() if preview_element else '',
            'date': time_element.get('title') if time_element else 'Дата неизвестна'
        }
    except Exception as e:
        print(f"Ошибка при парсинге превью статьи: {e}")
        return None


@parametrized_logger('habr_full_articles.log')
def check_full_article(url: str) -> bool:
    """Проверяет полный текст статьи на наличие ключевых слов"""
    if url in SESSION_CACHE:
        return False

    try:
        time.sleep(REQUEST_DELAY)
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = soup.find('div', class_=re.compile(r'article-formatted-body|tm-article-body'))

        if article_body:
            return contains_keywords(article_body.text, KEYWORDS)

        return False
    except Exception as e:
        print(f"Ошибка при проверке статьи {url}: {e}")
        return False
    finally:
        SESSION_CACHE.add(url)


@logger
def main():
    try:
        response = requests.get(ALL_POSTS_URL, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        for article in articles:
            article_data = get_article_preview_data(article)
            if not article_data:
                continue

            # Проверяем превью
            preview_matches = contains_keywords(article_data['title'], KEYWORDS) or \
                              contains_keywords(article_data['preview'], KEYWORDS)

            if preview_matches:
                print(f"{article_data['date']} — {article_data['title']} — {article_data['url']}")
            else:
                # Проверяем полный текст
                if check_full_article(article_data['url']):
                    print(
                        f"{article_data['date']} — {article_data['title']} — {article_data['url']} (найдено в полном тексте)")

    except Exception as e:
        print(f"Ошибка при выполнении скрипта: {e}")


if __name__ == '__main__':
    if os.path.exists('habr_parser.log'):
        os.remove('habr_parser.log')
    if os.path.exists('habr_articles.log'):
        os.remove('habr_articles.log')
    if os.path.exists('habr_full_articles.log'):
        os.remove('habr_full_articles.log')

    main()