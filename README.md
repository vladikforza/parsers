Установка
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Общий запуск (все парсеры сразу)
```bash
python run_all.py
```
`run_all.py` запускает Lenta, RIA и Telegram и перезапускает их при падении. Парсеры работают в режиме `run_forever` (пауза между итерациями).

Запуск отдельных парсеров
```bash
python -m lenta.lenta_parser.runner
python -m ria.ria_parser.runner
python -m telegram_parser.runner
```

Выходные файлы и формат
- Lenta: `lenta/lenta_parser/data/lenta_world_politic.jsonl`
- RIA: `ria/ria_parser/data/ria_politics.jsonl`
- Telegram: `telegram_parser/data/telegram_posts.jsonl`

Каждая строка JSONL содержит только поля:
```json
{
  "header": "...",
  "text": "...",
  "date": "...",
  "hashtags": ["..."],
  "source_name": "..."
}
```

Backend API (отправка новостей)
По умолчанию запросы идут на `http://localhost:8080/test/save_news`.
Переменные окружения:
- `NEWS_API_URL` — URL backend API
- `NEWS_API_TIMEOUT` — таймаут запроса (секунды)

Переменные окружения Lenta
- `LENTA_DATA_DIR` — папка данных (по умолчанию `lenta/lenta_parser/data`)
- `LENTA_LOG_DIR` — папка логов
- `LENTA_BASE_URL`
- `LENTA_SECTION_URL`
- `LENTA_SOURCE_NAME`
- `LENTA_INTERVAL_MINUTES`
- `LENTA_DAYS_BACK`
- `LENTA_MAX_PAGES`
- `LENTA_TIMEOUT_SECONDS`
- `LENTA_RETRY_COUNT`
- `LENTA_BACKOFF_SECONDS`
- `LENTA_RATE_DELAY_MIN`
- `LENTA_RATE_DELAY_MAX`
- `LENTA_USER_AGENT`
- `LENTA_ACCEPT_LANGUAGE`
- `LENTA_REFERER`
- `LENTA_LOG_LEVEL`
- `LENTA_DISABLE_DEDUP`

Переменные окружения RIA
- `RIA_DATA_DIR` — папка данных (по умолчанию `ria/ria_parser/data`)
- `RIA_LOG_DIR` — папка логов
- `RIA_BASE_URL`
- `RIA_SECTION_URL`
- `RIA_SOURCE_NAME`
- `RIA_INTERVAL_MINUTES`
- `RIA_DAYS_BACK`
- `RIA_MAX_PAGES`
- `RIA_ARTICLE_MASK`
- `RIA_TIMEOUT_SECONDS`
- `RIA_RETRY_COUNT`
- `RIA_BACKOFF_SECONDS`
- `RIA_RATE_DELAY_MIN`
- `RIA_RATE_DELAY_MAX`
- `RIA_USER_AGENT`
- `RIA_ACCEPT_LANGUAGE`
- `RIA_REFERER`
- `RIA_LOG_LEVEL`
- `RIA_DISABLE_DEDUP`

Переменные окружения Telegram
- `API_ID` — ID приложения Telegram
- `API_HASH` — hash приложения Telegram
- `SESSION_PATH` — путь к файлу сессии
- `CHANNELS_PATH` — путь к списку каналов (`telegram_parser/data/channels.txt`)
- `OUTPUT_PATH` — общий файл вывода (`telegram_parser/data/telegram_posts.jsonl`)
- `OUTPUT_DIR` — директория для постов (если используется отдельно)
- `INDEX_PATH` — файл индекса
- `LOG_PATH` — лог-файл
- `TELEGRAM_PHONE` — номер телефона для входа
- `TELEGRAM_CODE` — код подтверждения
- `TELEGRAM_PASSWORD` — пароль 2FA (если включен)
- `TELEGRAM_BOT_TOKEN` — токен бота (альтернатива логину по телефону)
- `POLL_INTERVAL_MINUTES` — интервал между итерациями
- `LOOKBACK_DAYS` — глубина по дате
- `REQUEST_DELAY_RANGE` — задержка между запросами (например `0.3,1.0`)

Авторизация Telegram
- Если используется телефон: задать `TELEGRAM_PHONE`, запустить парсер, получитье код и установить `TELEGRAM_CODE` (и `TELEGRAM_PASSWORD`, если включена 2FA).
- Если используется бот: задать `TELEGRAM_BOT_TOKEN`.
