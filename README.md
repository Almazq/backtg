### Минимальный Python-бэкенд для Telegram Mini Apps (FastAPI)

Этот бэкенд делает две вещи:
- **/health**: проверка, что сервер жив.
- **/auth/verify**: верификация `initData` из Telegram WebApp (без этого мини‑приложение не должно доверять данным с фронта).

#### Что внутри
- FastAPI + Uvicorn
- CORS (настраивается через env)
- Проверка подписи `initData` по правилам Telegram (HMAC-SHA256, ключ = SHA256 от токена бота)

#### Установка
1) Установите Python 3.10+
2) В консоли (PowerShell) из папки проекта:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3) Создайте файл `.env` рядом с `requirements.txt` и задайте переменные:

```bash
BOT_TOKEN=1234567:ABC-Your-Bot-Token-Here
CORS_ORIGINS=*
```

Пример также есть в `env.example`.

#### Запуск (локально)

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Проверка:
- `GET http://localhost:8000/health` → {"status":"ok"}
- `POST http://localhost:8000/auth/verify` с телом:

```json
{
  "init_data": "query_id=...&user=%7B...%7D&auth_date=...&hash=..."
}
```

Ответ:
- При успехе: `{ "ok": true, "user": {...}, "query_id": "...", "auth_date": 1234567890 }`
- При ошибке: `{ "ok": false, "reason": "Invalid hash" }`

Где взять `init_data`:
- На фронте в Telegram WebApp доступно `window.Telegram.WebApp.initData`.
- Отправляйте сырую строку (как есть) в `init_data` на этот бэкенд.

#### Деплой
- Любой хостинг Python/ASGI (Uvicorn/Gunicorn).
- Не храните токен бота в коде — используйте переменные окружения.


