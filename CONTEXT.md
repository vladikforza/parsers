# Context summary

## Project root
D:\par

## Last tasks
- Brought `lenta` and `ria` parsers in line with TЗ: use backend stubs instead of JSONL/index for dedup/push.
- Added `backend.py` with stubs:
  - `check_if_news_exists(header, source_name) -> bool`
  - `push_news_to_db(header, text, date, hashtags, source_name) -> None`
- Adjusted Lenta/RIA to first-page-only collection (pagination removed) for test run.
- Set Lenta/RIA interval to 5 minutes.
- RIA run_forever started in background, then stopped.

## TestApp-main (Docker)
- Location: `D:\par\TestApp-main\TestApp-main`
- `.env` created from `.env-example` with `WEB_PORT=8080`.
- `docker compose up --build -d` failed: Docker engine not running (`open //./pipe/docker_engine`).
- User said Docker Desktop opened, but daemon still not reachable. Need to run `docker info` to verify, then retry compose.
- App endpoint: `POST /test/save_news` (FastAPI). Swagger at `/docs` on exposed port.

## Files changed (key)
- `backend.py` (new)
- `lenta/lenta_parser/runner.py` (uses backend, no JSONL/index)
- `ria/ria_parser/runner.py` (uses backend, no JSONL/index)
- `lenta/lenta_parser/config.py` (interval 5)
- `ria/ria_parser/config.py` (interval 5)

## Pending next steps
1) Fix Docker engine availability and run `docker compose up --build -d` in `TestApp-main\TestApp-main`.
2) Call API method (from Swagger or curl) and report request/response.

