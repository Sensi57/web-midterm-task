# Space Bounty Hunters API

REST API для космических охотников за головами.
«Я стану Королём охотников за головами!» — Luffy, наверное

**Стек (тот же, что в проектах курса):** FastAPI/Python 3.12 + PostgreSQL 16 + Docker

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

| Что        | Адрес                      |
| ---------- | -------------------------- |
| API        | http://localhost:8000      |
| Swagger UI | http://localhost:8000/docs |

## База данных: настройка и импорт

Схема и тестовые данные лежат в **[`db/init.sql`](db/init.sql)**:

- 2 таблицы: `wanted_criminals` и `hunt_logs`;
- **7 преступников** и **12 записей журнала** (в данных есть преступники без имени, с координатами и с текстовой заметкой вместо координат);
- файл смонтирован в `/docker-entrypoint-initdb.d/`, поэтому PostgreSQL выполняет его **автоматически при первом создании тома** — ничего вручную импортировать не нужно.

Пересоздать базу с нуля (данные вернутся к исходным):

```bash
docker compose down -v
docker compose up --build
```

Ручной импорт в уже запущенную БД:

```bash
docker compose exec -T db psql -U bounty -d bountydb < db/init.sql
```

(значения `bounty` / `bountydb` — из `.env`; при повторном импорте таблицы не пересоздаются, но тестовые строки добавятся заново.)

Посмотреть данные в БД:

```bash
docker compose exec db psql -U bounty -d bountydb -c "SELECT id, nickname, reward FROM wanted_criminals;"
```

## Модели

**WantedCriminal** (`wanted_criminals`)
**HuntLog** (`hunt_logs`)

**Связь:** один-ко-многим — у одного преступника может быть много попыток поимки (`WantedCriminal.hunts` ↔ `HuntLog.criminal`).

## 🏯 Repository Arc: карта нашего додзё

| Файл | Ответственность
| main.py | Главный вход в приложение
| database.py | Подключение к SQLAlchemy
| models.py | Модели WantedCriminal и HuntLog
| schemas.py | Pydantic-схемы и валидация
| routers/criminals.py | Маршруты преступников
| routers/hunts.py | Маршруты журнала охоты
| db/init.sql | Схема БД и тестовые данные
| docker-compose.yml | Запуск контейнеров

### Wanted Criminals

| GET | `/api/criminals/` | Список с фильтрами и сортировкой |
| GET | `/api/criminals/{id}/` | Детали одного преступника |

Query-параметры `GET /api/criminals/` (все необязательные, **работают вместе**):

```
GET /api/criminals/?min_reward=5000&armed=true&sort=-reward
```

### Hunt Logs

| GET | `/api/hunts/` | Все записи (фильтр `?criminal_id=5`) | 200 |
| GET | `/api/hunts/{id}/` | Одна запись | 200 |
| POST | `/api/hunts/` | Записать попытку поимки | 201 |
| PATCH | `/api/hunts/{id}/` | Изменить `success` и/или `notes` | 200 |
| DELETE | `/api/hunts/{id}/` | Удалить запись | 204 |

Пример `POST /api/hunts/`:

```json
{
  "criminal_id": 3,
  "success": false,
  "notes": "Target escaped through an asteroid field."
}
```

`created_at` выставляет сервер. Если клиент пришлёт `created_at` (или любое другое лишнее поле) — запрос отклоняется с `422`.

## Postman

Файл: [`postman/ey.postman_collection.json`](postman/ey.postman_collection.json) → Postman → **Import**.

Запускать сверху вниз (или через Collection Runner). Коллекция содержит:

1. **Wanted Criminals** с получение списка преступников, фильтрация, комбинированные фильтры (min_reward + armed + sort=-reward), сортировка и просмотр деталей.
2. **Hunt Logs (CRUD)** список, фильтр по `criminal_id`, создание (id сохраняется в `huntId`), чтение, PATCH, удаление, проверка 404 после удаления.
3. **Invalid requests** проверка ошибок: 404 для несуществующего преступника, 422 для нечислового ID, 404 при создании лога для несуществующего преступника, 422 для кривого тела, 422 при попытке задать `created_at`, 422 для неверного `sort`, 400 для `min_reward > max_reward`.

Главное правило охотника за головами: Никогда не сдавайся, даже если PostgreSQL вернул 500, Docker не собирается, а Зоро опять потерялся.
