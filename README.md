»нструкци€ по запуску парсеров


”становка
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

ќбщий запуск (все парсеры сразу)
```bash
python run_all.py
```
`run_all.py` запускает Lenta, RIA и Telegram и перезапускает их при падении. ѕарсеры работают в режиме `run_forever` (пауза между итераци€ми).

«апуск отдельных парсеров
```bash
python -m lenta.lenta_parser.runner
python -m ria.ria_parser.runner
python -m telegram_parser.runner
```

¬ыходные файлы и формат
- Lenta: `lenta/lenta_parser/data/lenta_world_politic.jsonl`
- RIA: `ria/ria_parser/data/ria_politics.jsonl`
- Telegram: `telegram_parser/data/telegram_posts.jsonl`

 ажда€ строка JSONL содержит только пол€:
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
ѕо умолчанию запросы идут на `http://localhost:8080/test/save_news`.
ѕеременные окружени€:
- `NEWS_API_URL` Ч URL backend API
- `NEWS_API_TIMEOUT` Ч таймаут запроса (секунды)

ѕеременные окружени€ Lenta
- `LENTA_DATA_DIR` Ч папка данных (по умолчанию `lenta/lenta_parser/data`)
- `LENTA_LOG_DIR` Ч папка логов
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

ѕеременные окружени€ RIA
- `RIA_DATA_DIR` Ч папка данных (по умолчанию `ria/ria_parser/data`)
- `RIA_LOG_DIR` Ч папка логов
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

ѕеременные окружени€ Telegram
- `API_ID` Ч ID приложени€ Telegram
- `API_HASH` Ч hash приложени€ Telegram
- `SESSION_PATH` Ч путь к файлу сессии
- `CHANNELS_PATH` Ч путь к списку каналов (`telegram_parser/data/channels.txt`)
- `OUTPUT_PATH` Ч общий файл вывода (`telegram_parser/data/telegram_posts.jsonl`)
- `OUTPUT_DIR` Ч директори€ дл€ постов (если используетс€ отдельно)
- `INDEX_PATH` Ч файл индекса
- `LOG_PATH` Ч лог-файл
- `TELEGRAM_PHONE` Ч номер телефона дл€ входа
- `TELEGRAM_CODE` Ч код подтверждени€
- `TELEGRAM_PASSWORD` Ч пароль 2FA (если включен)
- `TELEGRAM_BOT_TOKEN` Ч токен бота (альтернатива логину по телефону)
- `POLL_INTERVAL_MINUTES` Ч интервал между итераци€ми
- `LOOKBACK_DAYS` Ч глубина по дате
- `REQUEST_DELAY_RANGE` Ч задержка между запросами (например `0.3,1.0`)

јвторизаци€ Telegram
- ≈сли используетс€ телефон: задать `TELEGRAM_PHONE`, запустить парсер, получитье код и установить `TELEGRAM_CODE` (и `TELEGRAM_PASSWORD`, если включена 2FA).
- ≈сли используетс€ бот: задать `TELEGRAM_BOT_TOKEN`.