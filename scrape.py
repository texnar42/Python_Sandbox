import wikipediaapi
import tiktoken
import time
import os
import re

# Настройка токенизатора
enc = tiktoken.get_encoding("cl100k_base")

# Инициализация Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(
    language='ru',
    user_agent='MyResearchBot/1.0 (myemail@example.com)'
)


def sanitize_filename(filename):
    """Очищает имя файла от недопустимых символов"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def save_article_to_file(article, folder_path="wikipedia_articles\\10000-30000"):
    """Сохраняет статью в отдельный TXT файл"""

    # Создаем папку если не существует
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Очищаем название для имени файла
    safe_title = sanitize_filename(article['title'])

    # Создаем имя файла
    filename = f"{safe_title}_{article['tokens']}tokens.txt"
    filepath = os.path.join(folder_path, filename)

    # Записываем статью в файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Заголовок: {article['title']}\n")
        f.write(f"URL: {article['url']}\n")
        f.write(f"Количество токенов: {article['tokens']}\n")
        f.write(f"Дата сохранения: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(article['content'])

    return filepath


def get_wikipedia_articles_by_length(min_tokens=10000, max_tokens=30000, target_count=100):
    articles = []
    saved_files = []

    # Популярные категории для поиска длинных статей
    categories = [
        "История", "Наука", "Технологии", "Философия", "Литература",
        "Искусство", "Политика", "Экономика", "Медицина", "Физика",
        "Математика", "Химия", "Биология", "География", "Астрономия"
    ]

    for category in categories:
        if len(articles) >= target_count:
            break

        print(f"Поиск в категории: {category}")
        cat = wiki_wiki.page(f"Категория:{category}")

        if not cat.exists():
            print(f"Категория {category} не найдена")
            continue

        print(f"Найдено страниц в категории: {len(cat.categorymembers)}")

        for page in cat.categorymembers.values():
            if len(articles) >= target_count:
                break

            if page.ns == 0:  # Только статьи, а не подкатегории
                try:
                    text = page.text
                    token_count = len(enc.encode(text))

                    if min_tokens <= token_count <= max_tokens:
                        article_data = {
                            'title': page.title,
                            'url': page.fullurl,
                            'tokens': token_count,
                            'content': text
                        }
                        articles.append(article_data)

                        # Сохраняем статью в файл
                        filepath = save_article_to_file(article_data)
                        saved_files.append(filepath)

                        print(f"✓ Сохранена: {page.title} ({token_count} токенов) -> {filepath}")
                    else:
                        print(f"  Пропущена: {page.title} ({token_count} токенов) - не подходит по размеру")

                    time.sleep(0.1)  # Уважаем API

                except Exception as e:
                    print(f"✗ Ошибка с {page.title}: {e}")

    print(f"\nИтоги:")
    print(f"Найдено подходящих статей: {len(articles)}")
    print(f"Сохранено файлов: {len(saved_files)}")

    return articles, saved_files


def get_articles_by_titles(article_titles, min_tokens=10000, max_tokens=30000):
    """Альтернативная функция для получения конкретных статей по названиям"""
    articles = []
    saved_files = []

    for title in article_titles:
        try:
            print(f"Получаем статью: {title}")
            page = wiki_wiki.page(title)

            if not page.exists():
                print(f"Статья '{title}' не найдена")
                continue

            text = page.text
            token_count = len(enc.encode(text))

            if min_tokens <= token_count <= max_tokens:
                article_data = {
                    'title': page.title,
                    'url': page.fullurl,
                    'tokens': token_count,
                    'content': text
                }
                articles.append(article_data)

                # Сохраняем статью в файл
                filepath = save_article_to_file(article_data)
                saved_files.append(filepath)

                print(f"✓ Сохранена: {page.title} {page.fullurl} ({token_count} токенов)")
            else:
                print(f"  Пропущена: {page.title} ({token_count} токенов) - не подходит по размеру")

            time.sleep(0.1)

        except Exception as e:
            print(f"✗ Ошибка с {title}: {e}")

    return articles, saved_files


# Запуск сбора через категории
print("Начинаем сбор статей через категории...")
articles, saved_files = get_wikipedia_articles_by_length()

# Если через категории нашлось мало статей, используем альтернативный метод
if len(articles) < 100:
    print("\nДобираем статьи по конкретным названиям...")

    # Список потенциально длинных статей
    long_articles_titles = [
        "Вторая мировая война", "Древний Рим", "Средние века", "Русская литература",
        "Физика", "Химия", "Биология", "История России", "Великая Отечественная война",
        "Теория относительности", "Квантовая механика", "Экономика", "Философия",
        "Психология", "Литература", "Математика", "География", "Астрономия",
        "Советский Союз", "Древняя Греция", "Эволюция", "Генетика", "Экология",
        "Искусство Древнего Египта", "Ренессанс", "Барокко", "Романтизм",
        "Импрессионизм", "Классицизм", "Реализм", "Модернизм", "Постмодернизм"
    ]

    additional_articles, additional_files = get_articles_by_titles(long_articles_titles)
    articles.extend(additional_articles)
    saved_files.extend(additional_files)

# Сохранение мета-информации о всех статьях
if articles:
    with open('wikipedia_articles/metadata.txt', 'w', encoding='utf-8') as f:
        f.write("МЕТАДАННЫЕ СОБРАННЫХ СТАТЕЙ\n")
        f.write("=" * 50 + "\n")
        f.write(f"Всего статей: {len(articles)}\n")
        f.write(f"Общее количество токенов: {sum(article['tokens'] for article in articles)}\n")
        f.write(f"Дата сбора: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for i, article in enumerate(articles, 1):
            f.write(f"{i}. {article['title']} - {article['tokens']} токенов\n")
            f.write(f"   URL: {article['url']}\n\n")

print(f"\nГотово! Сохранено {len(articles)} статей в папку 'wikipedia_articles'")
print(f"Список всех статей сохранен в файл 'wikipedia_articles/metadata.txt'")