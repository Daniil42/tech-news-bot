"""
Tech News Parser
Парсер новостей о технологиях: ИИ, мобильные устройства, гаджеты, техно-мероприятия
"""

import logging
import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import requests
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env из директории скрипта
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Токены берём из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
TRANSLATE_ENABLED = True  # Включить перевод на русский


def translate_to_russian(text: str) -> str:
    """
    Перевод текста на русский через MyMemory API (бесплатно, без ключа).
    Лимит: 1000 слов/день бесплатно.
    """
    if not TRANSLATE_ENABLED:
        return text
    
    # Пропускаем очень короткие тексты
    if len(text.strip()) < 10:
        return text
    
    try:
        # MyMemory Translation API (бесплатный, без ключа)
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": "en|ru"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if "responseData" in result and "translatedText" in result["responseData"]:
            translated = result["responseData"]["translatedText"]
            
            # Проверяем качество перевода (иногда API возвращает пустоту)
            if translated and len(translated) > 5:
                logger.info(f"✓ Переведено (MyMemory): {text[:40]}... → {translated[:40]}...")
                return translated
        
        # Если перевод не удался, возвращаем оригинал
        logger.info(f"⚠ Перевод не удался, используем оригинал: {text[:40]}")
        return text
        
    except Exception as e:
        logger.warning(f"⚠ Ошибка перевода: {e}. Используем оригинал.")
        return text

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Конфигурация
PARSER_INTERVAL = int(os.getenv("PARSER_INTERVAL", "30"))  # минут

# Ключевые слова для фильтрации новостей
# Включает: ИИ, мобильные технологии, гаджеты, техно-мероприятия
TECH_KEYWORDS = [
    # ИИ и машинное обучение
    "artificial intelligence", "AI", "machine learning", "ML",
    "deep learning", "neural network", "GPT", "LLM",
    "ChatGPT", "Claude", "Gemini", "Midjourney", "DALL-E",
    "генеративный", "нейросеть", "ИИ", "машинное обучение",
    
    # Мобильные технологии и телефоны
    "smartphone", "iPhone", "Android", "Samsung", "Google Pixel",
    "OnePlus", "Xiaomi", "Huawei", "mobile", "5G", "6G",
    "телефон", "смартфон", "мобильный",
    
    # Техно-мероприятия
    "MWC", "Mobile World Congress", "CES", "WWDC", "Google I/O",
    "Samsung Unpacked", "Apple Event", "Microsoft Build",
    "техно-мероприятие", "конференция", "выставка технологий",
    
    # Гаджеты и устройства
    "gadget", "wearable", "smartwatch", "tablet", "laptop",
    "VR", "AR", "virtual reality", "augmented reality",
    "Metaverse", "Quest", "Vision Pro",
    "гаджет", "устройство", "носимый",
    
    # Инновации и стартапы
    "startup", "innovation", "tech startup", "funding", "venture capital",
    "инновация", "стартап", "инвестиции",
    
    # Общие технологии
    "technology", "tech", "software", "hardware", "app",
    "cloud", "cybersecurity", "blockchain", "crypto",
    "технология", "программное обеспечение", "приложение"
]

# Источники новостей
SOURCES = {
    "hackernews": {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/rss",
        "type": "rss"
    },
    "techcrunch": {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "type": "rss"
    },
    "theverge": {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "rss"
    },
    "ars_technica": {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "type": "rss"
    },
    "mit_technology_review": {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "type": "rss"
    },
    "engadget": {
        "name": "Engadget",
        "url": "https://www.engadget.com/rss.xml",
        "type": "rss"
    },
    "gsmarena": {
        "name": "GSMArena",
        "url": "https://www.gsmarena.com/rss-news.php3",
        "type": "rss"
    },
    "android_authority": {
        "name": "Android Authority",
        "url": "https://www.androidauthority.com/feed/",
        "type": "rss"
    },
    "openai": {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss/",
        "type": "rss"
    },
    "anthropic": {
        "name": "Anthropic",
        "url": "https://www.anthropic.com/news?format=rss",
        "type": "rss"
    },
    "google_ai": {
        "name": "Google AI",
        "url": "https://ai.google/rss.xml",
        "type": "rss"
    }
}

# Хранилище
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SEEN_FILE = DATA_DIR / "seen_news.json"
QUEUE_FILE = DATA_DIR / "news_queue.json"
LAST_POST_FILE = DATA_DIR / "last_post.json"
CATEGORY_FILE = DATA_DIR / "last_category.json"

# Категории для чередования
CATEGORIES = ["ai", "mobile", "gadget", "event", "other"]
CATEGORY_KEYWORDS = {
    "ai": ["AI", "artificial intelligence", "machine learning", "GPT", "LLM", "ChatGPT", "Claude", "Gemini", "нейросеть", "ИИ", "OpenAI", "Anthropic"],
    "mobile": ["iPhone", "Android", "Samsung", "Google Pixel", "smartphone", "телефон", "смартфон", "5G", "6G", "mobile", "MWC", "Mobile World Congress"],
    "gadget": ["VR", "AR", "Vision Pro", "Quest", "smartwatch", "tablet", "laptop", "гаджет", "устройство", "wearable"],
    "event": ["CES", "WWDC", "Google I/O", "Apple Event", "Samsung Unpacked", "Microsoft Build", "конференция", "выставка"],
    "other": []  # Все остальное
}

# Интервал публикации (минуты)
POST_INTERVAL = 60  # 1 пост в час


def load_seen_news() -> set:
    """Загрузить уже виденные новости"""
    if SEEN_FILE.exists():
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen_news(seen: set):
    """Сохранить виденные новости"""
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, indent=2)


def load_queue() -> List[Dict]:
    """Загрузить очередь новостей"""
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_queue(queue: List[Dict]):
    """Сохранить очередь новостей"""
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def get_last_post_time() -> Optional[datetime]:
    """Получить время последней публикации"""
    if LAST_POST_FILE.exists():
        with open(LAST_POST_FILE, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    return None


def save_last_post_time(dt: datetime):
    """Сохранить время последней публикации"""
    with open(LAST_POST_FILE, "w") as f:
        f.write(dt.isoformat())


def get_last_category() -> str:
    """Получить последнюю категорию"""
    if CATEGORY_FILE.exists():
        with open(CATEGORY_FILE, "r") as f:
            return f.read().strip()
    return "other"


def save_last_category(category: str):
    """Сохранить последнюю категорию"""
    with open(CATEGORY_FILE, "w") as f:
        f.write(category)


def detect_category(title: str, summary: str = "") -> str:
    """Определить категорию новости"""
    text = f"{title} {summary}".lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "other":
            continue
        for keyword in keywords:
            if keyword.lower() in text:
                return category
    
    return "other"


def get_next_category() -> str:
    """Получить следующую категорию для публикации (по кругу)"""
    last = get_last_category()
    try:
        idx = CATEGORIES.index(last)
        next_idx = (idx + 1) % len(CATEGORIES)
        return CATEGORIES[next_idx]
    except ValueError:
        return CATEGORIES[0]


def select_news_by_category(queue: List[Dict], preferred_category: str) -> Optional[Dict]:
    """Выбрать новость по категории (или первую попавшуюся, если нет нужной)"""
    # Сначала ищем новость нужной категории
    for i, news in enumerate(queue):
        if news.get("category") == preferred_category:
            return queue.pop(i)
    
    # Если нет, берём первую с категорией, отличной от последней
    for i, news in enumerate(queue):
        if news.get("category") != get_last_category():
            return queue.pop(i)
    
    # Если все одинаковые или очередь пуста, берём первую
    if queue:
        return queue.pop(0)
    
    return None


def contains_tech_keywords(title: str, summary: str = "") -> bool:
    """Проверить, содержит ли новость технологические ключевые слова"""
    text = f"{title} {summary}".lower()
    return any(keyword.lower() in text for keyword in TECH_KEYWORDS)


def parse_rss_feed(source_key: str, limit: int = 10) -> List[Dict]:
    """Парсинг RSS ленты"""
    source = SOURCES.get(source_key)
    if not source:
        logger.error(f"Источник {source_key} не найден")
        return []

    logger.info(f"Парсинг {source['name']}...")

    try:
        response = requests.get(source["url"], timeout=10)
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        news_items = []

        for entry in feed.entries[:limit]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            published = entry.get("published", "")

            # Очищаем summary от HTML тегов
            if summary:
                soup = BeautifulSoup(summary, "html.parser")
                summary = soup.get_text()[:500]  # Ограничиваем длину

            news_items.append({
                "source": source["name"],
                "source_key": source_key,
                "title": title,
                "link": link,
                "summary": summary,
                "published": published,
                "parsed_at": datetime.now().isoformat()
            })

        logger.info(f"Найдено {len(news_items)} новостей из {source['name']}")
        return news_items

    except Exception as e:
        logger.error(f"Ошибка парсинга {source['name']}: {e}")
        return []


def filter_tech_news(news_items: List[Dict]) -> List[Dict]:
    """Фильтрация новостей по технологической тематике"""
    filtered = []
    for item in news_items:
        if contains_tech_keywords(item["title"], item["summary"]):
            filtered.append(item)
    return filtered


def format_telegram_post(news: Dict, translate: bool = True) -> str:
    """Форматирование новости для Telegram"""
    # Очищаем заголовок
    title = news["title"].strip()
    
    # Переводим заголовок на русский
    if translate and TRANSLATE_ENABLED:
        logger.info(f"Перевод заголовка: {title[:50]}...")
        title = translate_to_russian(title)
    
    if len(title) > 100:
        title = title[:97] + "..."

    # Формируем пост
    post = f"🔥 **{title}**\n\n"

    if news["summary"]:
        summary = news["summary"].strip()
        # Переводим summary на русский
        if translate and TRANSLATE_ENABLED and len(summary) > 50:
            logger.info(f"Перевод описания...")
            summary = translate_to_russian(summary)
        
        if len(summary) > 500:
            summary = summary[:497] + "..."
        post += f"{summary}\n\n"

    post += f"📌 **Источник:** {news['source']}\n"
    post += f"🔗 [Читать далее]({news['link']})\n\n"

    # Добавляем хэштеги
    hashtags = generate_hashtags(news["title"])
    post += hashtags

    return post


def generate_hashtags(title: str) -> str:
    """Генерация хэштегов на основе заголовка"""
    hashtags = []
    title_lower = title.lower()

    if any(word in title_lower for word in ["openai", "gpt", "chatgpt"]):
        hashtags.append("#OpenAI")
    if any(word in title_lower for word in ["anthropic", "claude"]):
        hashtags.append("#Claude")
    if any(word in title_lower for word in ["google", "gemini"]):
        hashtags.append("#Google")
    if any(word in title_lower for word in ["midjourney", "stable diffusion", "dall"]):
        hashtags.append("#GenerativeAI")
    if any(word in title_lower for word in ["llm", "language model"]):
        hashtags.append("#LLM")
    if any(word in title_lower for word in ["ai", "artificial intelligence", "ии", "нейросеть"]):
        hashtags.append("#ИИ")

    hashtags.append("#Новости")
    hashtags.append("#Технологии")

    return " ".join(hashtags)


async def send_to_telegram(post: str):
    """Отправка поста в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        logger.warning("Telegram токен или ID канала не настроены")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": post,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        logger.info("Пост отправлен в Telegram")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False


def save_news(news_items: List[Dict]):
    """Сохранение новостей в файл"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = DATA_DIR / f"news_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(news_items, f, indent=2, ensure_ascii=False)

    logger.info(f"Новости сохранены в {filename}")


async def parse_and_send(sources: List[str] = None, auto_post: bool = True):
    """Парсинг и добавление новостей в очередь"""
    if sources is None:
        sources = list(SOURCES.keys())

    # Загружаем уже виденные новости
    seen_news = load_seen_news()

    # Загружаем очередь
    queue = load_queue()

    all_news = []
    new_news = []

    # Парсим каждый источник
    for source_key in sources:
        news_items = parse_rss_feed(source_key)
        all_news.extend(news_items)

    # Фильтруем по технологической тематике
    tech_news = filter_tech_news(all_news)
    logger.info(f"Найдено {len(tech_news)} техно-новостей")

    # Фильтруем уже виденные и добавляем категорию
    for news in tech_news:
        news_id = news["link"]
        if news_id not in seen_news:
            # Определяем категорию
            news["category"] = detect_category(news["title"], news["summary"])
            new_news.append(news)
            seen_news.add(news_id)

    logger.info(f"Новых новостей: {len(new_news)}")

    # Сохраняем виденные
    save_seen_news(seen_news)

    # Добавляем в очередь
    if new_news:
        queue.extend(new_news)
        save_queue(queue)
        save_news(new_news)
        logger.info(f"Очередь: {len(queue)} новостей")

    return queue


async def post_from_queue():
    """Опубликовать одну новость из очереди"""
    queue = load_queue()
    
    if not queue:
        logger.info("Очередь пуста, нечего публиковать")
        return False
    
    # Проверяем время последней публикации
    last_post = get_last_post_time()
    if last_post:
        time_since_last = datetime.now() - last_post
        min_interval = timedelta(minutes=POST_INTERVAL)
        
        if time_since_last < min_interval:
            wait_seconds = (min_interval - time_since_last).total_seconds()
            logger.info(f"До следующей публикации: {int(wait_seconds)} сек")
            return False
    
    # Получаем следующую категорию
    next_category = get_next_category()
    logger.info(f"Ищем новость категории: {next_category}")
    
    # Выбираем новость
    news = select_news_by_category(queue, next_category)
    
    if not news:
        logger.info("Нет подходящих новостей")
        return False
    
    # Публикуем
    post = format_telegram_post(news)
    success = await send_to_telegram(post)
    
    if success:
        # Сохраняем время и категорию
        save_last_post_time(datetime.now())
        save_last_category(news.get("category", "other"))
        
        # Обновляем очередь
        save_queue(queue)
        logger.info(f"Опубликовано: {news['title'][:50]}...")
        return True
    
    return False


async def main():
    """Основная функция с разделением парсинга и публикации"""
    logger.info("🤖 Запуск Tech News Parser...")
    logger.info(f"📅 Режим: 1 пост каждые {POST_INTERVAL} минут с чередованием категорий")

    while True:
        try:
            # Парсим новости и пополняем очередь
            await parse_and_send()
            
            # Публикуем одну новость из очереди (если прошло время)
            await post_from_queue()
            
        except Exception as e:
            logger.error(f"Ошибка в цикле: {e}")

        logger.info(f"⏳ Следующий цикл через {PARSER_INTERVAL} минут")
        await asyncio.sleep(PARSER_INTERVAL * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Парсер остановлен пользователем")
