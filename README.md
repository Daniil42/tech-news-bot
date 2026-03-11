# 🤖 Tech News Bot v2.0

Автоматический парсер техно-новостей для Telegram канала с AI-суммаризацией.

## ✨ Новое в v2.0

- 🧠 **AI-суммаризация** через Gemini Flash (бесплатно)
- 📰 **Скрыпинг полных статей** через Jina AI Reader (бесплатно)
- 📝 Развёрнутые посты 150-250 слов вместо 1-2 предложений
- 🇷🇺 Посты на русском языке

## Функции

- 📰 Парсинг 10 источников новостей (ИИ, телефоны, гаджеты, мероприятия)
- ⏰ 1 пост в час — без спама
- 🔄 Чередование категорий: ИИ → телефоны → гаджеты → мероприятия → другое

## Деплой на Railway

### 1. Создать GitHub репозиторий

```bash
git clone https://github.com/YOUR_USERNAME/tech-news-bot.git
cd tech-news-bot
```

### 2. Настроить Railway.com

1. Зайди на [railway.app](https://railway.app)
2. Sign up with GitHub
3. New Project → Deploy from GitHub repo → выбери `tech-news-bot`

### 3. Добавить переменные окружения

В Railway Dashboard → Environment:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
GEMINI_API_KEY=your_gemini_api_key
PARSER_INTERVAL=30
```

### 4. Получить Gemini API Key (бесплатно!)

1. Зайди на [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Создай API Key
3. Добавь в Railway как `GEMINI_API_KEY`

**Gemini Flash бесплатный** — 1500 запросов/день.

### 5. Деплой

Нажать "Deploy" — всё!

## Локальный запуск

```bash
pip install -r requirements.txt

# Создать .env файл
echo "TELEGRAM_BOT_TOKEN=your_token" > .env
echo "TELEGRAM_CHANNEL_ID=your_channel" >> .env
echo "GEMINI_API_KEY=your_gemini_key" >> .env
echo "PARSER_INTERVAL=30" >> .env

python parser.py
```

## Источники новостей

- Hacker News
- TechCrunch
- The Verge
- Ars Technica
- MIT Technology Review
- Engadget
- GSMArena
- Android Authority
- OpenAI Blog
- Google AI

## Как работает AI-суммаризация

1. Бот находит новость по ключевым словам
2. Скрыпит полную статью через Jina AI Reader
3. Отправляет текст в Gemini Flash
4. Gemini пишет структурированный пост на русском:
   - Что произошло
   - Основные детали
   - Почему это важно

## Лицензия

MIT