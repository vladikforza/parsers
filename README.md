# Парсеры новостей (Lenta, RIA, Telegram)

## 1) Цели и задачи, решаемые проектом
- Собирать свежие новости из Lenta, RIA и Telegram.
- Приводить данные к единому формату.
- Передавать новости в backend API для дальнейшей обработки/хранения.

## 2) Основные функции и возможности программы
- Парсинг новостей из заданных разделов Lenta и RIA.
- Сбор постов из заданных Telegram-каналов.
- Логирование хода работы и сохранение результатов локально.
- Отправка каждой новости в backend API.

## 3) Зависимости
- Python 3.10+.
- Пакеты из `requirements.txt`:
  - `beautifulsoup4==4.12.3`
  - `requests==2.32.3`
  - `telethon==1.36.0`
- Доступный backend API (по умолчанию `http://localhost:8080/test/save_news`).

## 4) Настройка программы
1. Создать виртуальное окружение и установить зависимости:
```bash
pip install -r requirements.txt
```
2. Настройть параметры через переменные окружения (ключевые):
- Общие: `NEWS_API_URL`, `NEWS_API_TIMEOUT`.
- Lenta: `LENTA_SECTION_URL`, `LENTA_DAYS_BACK`, `LENTA_INTERVAL_MINUTES` и другие.
- RIA: `RIA_SECTION_URL`, `RIA_DAYS_BACK`, `RIA_INTERVAL_MINUTES` и другие.
- Telegram: `API_ID`, `API_HASH`, `CHANNELS_PATH`, `POLL_INTERVAL_MINUTES` и другие.

Полные списки параметров лежат в файлах:
- `lenta/lenta_parser/config.py`
- `ria/ria_parser/config.py`
- `telegram_parser/config.py`

## 5) Запуск программы
- Запуск всех парсеров:
```bash
python run_all.py
```
- Запуск по отдельности:
```bash
python -m lenta.lenta_parser.runner
python -m ria.ria_parser.runner
python -m telegram_parser.runner
```

## 6) Пример работы
Пример сохраненной новости в JSONL формате:
```json
{
  "header": "Пример заголовка",
  "text": "Текст новости...",
  "date": "2024-01-01T12:00:00",
  "hashtags": ["политика", "мир"],
  "source_name": "lenta"
}
```
