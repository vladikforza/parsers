# Парсеры новостей (Lenta, RIA, Telegram)

## 1) Цели и задачи, решаемые проектом
- Собирать свежие новости из Lenta, RIA, Telegram и RSS/GNews.
- Приводить данные к единому формату.
- Передавать новости в backend API для дальнейшей обработки и хранения.

## 2) Основные функции и возможности программы
- Парсинг новостей из заданных разделов Lenta и RIA.
- Парсинг ссылок на изображения, которые содержит новость
- Сбор постов из заданных Telegram-каналов.
- Сбор новостей из RSS-лент и GNews.
- Логирование работы и сохранение результатов локально.
- Отправка каждой новости в backend API.

## 3) Зависимости
- Python 3.10+.
- Пакеты из `requirements.txt`:
  - `beautifulsoup4==4.12.3`
  - `requests==2.32.3`
  - `telethon==1.36.0`
- Доступный backend API. Для локального запуска обычно используется `http://localhost:8080/test/save_news`, для Docker в примере настроен `http://host.docker.internal:8080/test/save_news`.

## 4) Настройка программы
### Вариант A. Локальный запуск
1. Установите зависимости:
```bash
pip install -r requirements.txt
```
2. Настройте параметры через переменные окружения (ключевые):
- Общие: `NEWS_API_URL`, `NEWS_API_TIMEOUT`.
- Lenta: `LENTA_SECTION_URL`, `LENTA_DAYS_BACK`, `LENTA_INTERVAL_MINUTES` и другие.
- RIA: `RIA_SECTION_URL`, `RIA_DAYS_BACK`, `RIA_INTERVAL_MINUTES` и другие.
- Telegram: `API_ID`, `API_HASH`, `CHANNELS_PATH`, `POLL_INTERVAL_MINUTES` и другие.
- RSS: `BACKEND_BASE_URL`, `BACKEND_SAVE_NEWS_ENDPOINT`, `SLEEP_SECONDS`, `REQUEST_TIMEOUT`, `MAX_RETRIES`, `LOG_LEVEL`.

Полные списки параметров смотрите в файлах:
- `lenta/lenta_parser/config.py`
- `ria/ria_parser/config.py`
- `telegram_parser/config.py`
- `rss/main.py`
- `rss/config/sources.yaml`

### Вариант B. Запуск в Docker
1. Заполните `.env.example` или сделайте его копию в другой файл и укажите его в `docker-compose.yml` как `env_file`.
2. Заполните `API_ID` и `API_HASH` для Telegram.
3. Убедитесь, что backend API доступен из контейнера по `NEWS_API_URL`.
   По умолчанию в `.env.example` используется `http://host.docker.internal:8080/test/save_news`.
4. Соберите и запустите контейнеры:
```bash
docker compose up --build -d
```

Каждый парсер запускается в отдельном контейнере:
- `rss-parser`
- `lenta-parser`
- `ria-parser`
- `telegram-parser`

Полезные команды:
```bash
docker compose logs -f
docker compose ps
docker compose down
```

## 5) Запуск программы
- Локальный запуск всех парсеров:
```bash
python run_all.py
```
- Локальный запуск по отдельности:
```bash
python -m lenta.lenta_parser.runner
python -m ria.ria_parser.runner
python -m telegram_parser.runner
python rss/main.py
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

## 7) Развёртывание в Docker

Этот раздел описывает запуск проекта в Docker без изменения текущего локального сценария работы.

### Что запускается в контейнерах

Через `docker compose` поднимаются 4 отдельных сервиса:
- `rss-parser`
- `lenta-parser`
- `ria-parser`
- `telegram-parser`

Каждый сервис запускает свой парсер в отдельном контейнере, а результаты работы сохраняются в примонтированные каталоги проекта на хосте.

### Что нужно установить

Перед началом убедитесь, что на машине установлены:
- Docker
- Docker Compose v2

Проверка:
```bash
docker --version
docker compose version
```

### Подготовка конфигурации

Все контейнеры используют переменные окружения из файла `.env.example`, который подключён в `docker-compose.yml` как `env_file`.

Минимально нужно проверить и при необходимости заполнить следующие переменные.

Для `lenta`, `ria` и `telegram`:
- `NEWS_API_URL` - полный URL backend endpoint для сохранения новости
- `NEWS_API_TIMEOUT` - таймаут запроса к backend в секундах

Для `rss-parser`:
- `BACKEND_BASE_URL` - базовый адрес backend
- `BACKEND_SAVE_NEWS_ENDPOINT` - endpoint сохранения новости
- `SLEEP_SECONDS` - пауза между циклами опроса RSS
- `REQUEST_TIMEOUT` - таймаут HTTP-запросов
- `MAX_RETRIES` - число повторных попыток
- `LOG_LEVEL` - уровень логирования

Для `telegram-parser`:
- `API_ID` - Telegram API ID
- `API_HASH` - Telegram API HASH
- `SESSION_PATH` - путь к файлу сессии внутри каталога `telegram_parser/data`
- `CHANNELS_PATH` - путь к файлу со списком каналов
- `TELEGRAM_PHONE` и `TELEGRAM_CODE`, если используется вход по номеру телефона
- `TELEGRAM_BOT_TOKEN`, если используется авторизация ботом

Важно:
- по умолчанию в `.env.example` используется `host.docker.internal`, то есть backend ожидается доступным с хост-машины;
- если backend работает в другом контейнере или на другом сервере, нужно заменить `NEWS_API_URL` и `BACKEND_BASE_URL` на корректные адреса;
- `telegram-parser` не сможет стартовать без валидных `API_ID` и `API_HASH`.

### Как Docker-монтирования устроены в проекте

В `docker-compose.yml` уже настроены bind mounts, поэтому данные не теряются при пересоздании контейнеров.

Используются следующие монтирования:
- `./lenta/lenta_parser/data -> /app/lenta/lenta_parser/data`
- `./lenta/lenta_parser/logs -> /app/lenta/lenta_parser/logs`
- `./ria/ria_parser/data -> /app/ria/ria_parser/data`
- `./ria/ria_parser/logs -> /app/ria/ria_parser/logs`
- `./telegram_parser/data -> /app/telegram_parser/data`
- `./rss/config -> /app/rss/config`

Что это означает на практике:
- JSONL-файлы и индексы `lenta` и `ria` сохраняются в проекте на хосте;
- Telegram session хранится в `telegram_parser/data`, поэтому повторная авторизация обычно не требуется после первого успешного входа;
- конфигурация RSS-источников читается из `rss/config/sources.yaml` на хосте.

### Первый запуск

1. Проверьте `.env.example`.
2. Убедитесь, что backend доступен по адресу, указанному в переменных окружения.
3. При необходимости отредактируйте `rss/config/sources.yaml`.
4. Запустите сборку и старт контейнеров:

```bash
docker compose up --build -d
```

После этого Docker:
- соберёт образ на базе `python:3.12-slim`;
- установит зависимости из корневого `requirements.txt` и `rss/requirements.txt`;
- поднимет 4 контейнера;
- подключит к ним директории данных и конфигов из проекта.

### Проверка после запуска

Проверить список контейнеров:
```bash
docker compose ps
```

Посмотреть логи всех сервисов:
```bash
docker compose logs -f
```

Посмотреть логи конкретного сервиса:
```bash
docker compose logs -f rss-parser
docker compose logs -f lenta-parser
docker compose logs -f ria-parser
docker compose logs -f telegram-parser
```

Перезапустить один сервис:
```bash
docker compose restart telegram-parser
```

Пересобрать и заново поднять проект:
```bash
docker compose up --build -d
```

Остановить контейнеры:
```bash
docker compose down
```

Остановить контейнеры с удалением образов, созданных compose:
```bash
docker compose down --rmi local
```

### Особенности Telegram в контейнере

`telegram-parser` работает в неинтерактивной среде, поэтому нужно заранее предусмотреть способ авторизации.

Поддерживаются варианты:
- авторизация через существующий файл сессии `telegram_parser/data/telegram.session`;
- авторизация по `TELEGRAM_BOT_TOKEN`;
- авторизация по номеру телефона через `TELEGRAM_PHONE` и `TELEGRAM_CODE`.

Если контейнер пишет, что код отправлен и требуется `TELEGRAM_CODE`, порядок действий такой:
1. Остановите `telegram-parser` или весь compose.
2. Запишите `TELEGRAM_CODE` в `.env.example`.
3. При необходимости заполните `TELEGRAM_PASSWORD`.
4. Запустите контейнер снова:

```bash
docker compose up -d telegram-parser
```

После успешной авторизации сессия сохранится в `telegram_parser/data/telegram.session`.

### Если backend находится не на хосте

В текущем примере используются адреса:
- `NEWS_API_URL=http://host.docker.internal:8080/test/save_news`
- `BACKEND_BASE_URL=http://host.docker.internal:8080`

Это подходит, когда backend запущен на той же машине, что и Docker.

Если backend находится:
- в другом контейнере того же `docker compose`, используйте имя сервиса, например `http://backend:8080`;
- на удалённом сервере, укажите его реальный сетевой адрес;
- на Linux-хосте вне compose, проверьте, что `host.docker.internal` поддерживается в вашей конфигурации Docker.

### Типовой сценарий обновления

Если вы изменили код парсеров:
```bash
docker compose up --build -d
```

Если вы изменили только `.env.example` или `rss/config/sources.yaml`:
- для применения env-переменных лучше перезапустить нужные сервисы;
- для RSS-конфига обычно достаточно перезапуска `rss-parser`.

Примеры:
```bash
docker compose restart rss-parser
docker compose restart lenta-parser ria-parser telegram-parser
```

### Где смотреть результаты работы

Результаты сохраняются в каталоги проекта:
- `lenta/lenta_parser/data`
- `ria/ria_parser/data`
- `telegram_parser/data`

Логи дополнительно пишутся:
- `lenta/lenta_parser/logs`
- `ria/ria_parser/logs`

RSS-парсер в текущей реализации пишет логи в stdout контейнера, поэтому их удобнее смотреть через:
```bash
docker compose logs -f rss-parser
```
