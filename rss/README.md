# News Parser

## 1) Цели и задачи проекта
- Асинхронно собирать новости из RSS и GNews.
- Отправлять каждую новость во внешний backend `/test/save_news`.
- Останавливать обработку конкретного источника только если backend отвечает HTTP 200 и `created=false`.
- Логировать сетевые ошибки, таймауты и HTTP-коды, отличные от 200, без остановки разбора источника.

## 2) Основные функции
- Загрузка RSS через `httpx` с повторными попытками и экспоненциальным backoff.
- Парсинг RSS через `feedparser`.
- Нормализация текста, дат и источников в общий формат.
- Поддержка GNews API.
- Отправка в backend через единый `NEWS_API_URL`.
- Периодический цикл обработки включённых источников из `config/sources.yaml`.

## 3) Настройка
RSS-парсер берёт runtime-настройки только из переменных окружения. В Docker они передаются через корневой `.env`.

Обязательные переменные:
- `NEWS_API_URL` - полный URL backend endpoint, например `http://host.docker.internal:8080/test/save_news`.
- `NEWS_API_TIMEOUT` - таймаут отправки новости в backend в секундах.
- `SLEEP_SECONDS` - пауза между циклами опроса.
- `REQUEST_TIMEOUT` - таймаут HTTP-запросов в секундах.
- `MAX_RETRIES` - число повторных попыток загрузки источника.
- `LOG_LEVEL` - уровень логирования, например `INFO` или `DEBUG`.

Важный Docker-момент:
- не используйте `http://localhost:8080` для backend-а, если backend запущен на хост-машине;
- внутри контейнера `localhost` указывает на сам контейнер;
- для backend-а на хосте используйте `http://host.docker.internal:8080`.

## 4) Конфиг источников
Источники хранятся в `rss/config/sources.yaml`. В текущей реализации файл содержит JSON-структуру и читается как JSON.

Пример:
```json
{
  "sources": [
    {
      "name": "bbc",
      "type": "rss",
      "rss_url": "https://feeds.bbci.co.uk/news/rss.xml",
      "enabled": true
    },
    {
      "name": "gnews-top",
      "type": "gnews",
      "params": {
        "topic": "world",
        "api_token": "YOUR_TOKEN"
      },
      "enabled": true
    }
  ]
}
```

Источники с `enabled: false` пропускаются.

## 5) Запуск
Из корня проекта:
```bash
docker compose up --build -d rss-parser rss-ui
```

RSS UI доступен по адресу:
```text
http://localhost:9000
```

Локальный запуск RSS-парсера возможен только если нужные переменные окружения уже заданы:
```bash
python rss/main.py
```

Локальный запуск UI:
```bash
python rss/ui.py
```

## 6) Поведение отправки в backend
`BackendClient.save_news()` возвращает:
- `True`, если backend создал новость.
- `False`, если backend вернул `created=false`; обработка текущего источника останавливается.
- `None`, если произошла сетевая, HTTP или JSON-ошибка; парсер логирует ошибку и продолжает обработку.
