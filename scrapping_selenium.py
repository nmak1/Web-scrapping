from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Настройка Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=chrome_options)

try:
    # Основная страница
    driver.get("https://habr.com/ru/all/")
    time.sleep(3)

    articles = driver.find_elements(By.CSS_SELECTOR, "article.tm-articles-list__item")

    for article in articles:
        title_element = article.find_element(By.CSS_SELECTOR, "h2.tm-title a")
        title = title_element.text
        link = title_element.get_attribute("href")
        preview = article.find_element(By.CSS_SELECTOR,
                                       "div.article-formatted-body").text
        date = article.find_element(By.CSS_SELECTOR, "time").get_attribute("title")

        # Проверка в превью
        found_in_preview = any(keyword.lower() in title.lower() or
                               keyword.lower() in preview.lower()
                               for keyword in KEYWORDS)

        if found_in_preview:
            print(f"{date} — {title} — {link}")
        else:
            # Проверка в полном тексте статьи
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(link)
            time.sleep(2)

            try:
                full_text = driver.find_element(By.CSS_SELECTOR,
                                                "div.tm-article-body").text
                if any(keyword.lower() in full_text.lower()
                       for keyword in KEYWORDS):
                    print(f"{date} — {title} — {link} (найдено в полном тексте)")
            except Exception as e:
                print(f"Ошибка при обработке статьи {link}: {e}")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

finally:
    driver.quit()