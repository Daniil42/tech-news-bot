# 🤖 Tech News Bot

Автоматический парсер техно-новостей для Telegram канала.

## Функции

- 📰 Парсинг 11 источников новостей (ИИ, телефоны, гаджеты, мероприятия)
- 🇷🇺 Автоматический перевод на русский (MyMemory API)
- ⏰ 1 пост в час — без спама
- 🔄 Чередование категорий: ИИ → телефоны → гаджеты → мероприятия → другое

## Деплой на Render.com

### 1. Создать GitHub репозиторий

```bash
# Создать новый репозиторий на GitHub: tech-news-bot
# Склонировать:
git clone https://github.com/YOUR_USERNAME/tech-news-bot.git
cd tech-news-bot

# Добавить файлы из папки deploy/
# (parser.py, requirements.txt, render.yaml, .gitignore, .env.example)
```

### 2. Настроить Render.com

1. Зайти на [render.com](https://render.com)
2. Sign up with GitHub
3. New → Background Worker
4. Connect repository
5. Render автоматически найдет `render.yaml`

### 3. Добавить переменные окружения

В Render Dashboard → Environment:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
PARSER_INTERVAL=30
```

### 4. Деплой

Нажать "Create Background Worker" — всё!

## Локальный запуск

```bash
pip install -r requirements.txt
python parser.py
```

## Источники новостей

- Hacker News
- TechCrunch
- Ars Technica
- MIT Technology Review
- Engadget
- и другие...

## Лицензия

MIT