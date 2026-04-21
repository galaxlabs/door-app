# Door App

QR-powered coordination platform: mode-driven QR codes + visitor interactions + queue/token control, with a Django (DRF + Channels + Celery) backend, Next.js admin panel, and Flutter mobile client.

## Repo layout

- `door_backend/` — Django API + realtime + workers
- `door_web/` — Next.js 14 admin dashboard
- `door_mobile/` — Flutter app shell

## Ports

- Backend API (Daphne/ASGI): `8010` (`http://localhost:8010/api/v1/`)
- Web admin (Next.js): `3002` (`http://localhost:3002/`)
- Postgres: `5432`
- Redis: internal to Docker network (`redis:6379`)

## Agent start (avoid repeating work)

Before doing any new task, read in this order:
1. `PROJECT_STATUS.md`
2. `PROJECT_MEMORY.md`
3. `MEMORY.md`
4. `errors.md`
5. `00_DOOR_APP_MASTER_ROADMAP.md`
6. `01_SCOPE_GUARDRAILS.md`
7. `02_IMPLEMENTATION_INSTRUCTIONS.md`
8. `03_PHASE_WISE_PROMPTS.md`
9. `04_EXISTING_APP_REWRITE_PLAN.md`
10. `05_COMPLETE_APP_FEATURES.md`

When a task is complete, append a dated note to `PROJECT_MEMORY.md`, and update `errors.md` if you fixed a runtime/build error.

After each task, run:
```bash
cd /home/dg/door-app
bash scripts/dev_smoke.sh
```

## Quick start (backend via Docker)

1. Copy environment template:
   - `cp door_backend/.env.example door_backend/.env`
2. Start services:
   - `docker compose up --build`
3. API docs:
   - `http://localhost:8010/api/v1/docs/`

## Dev without Docker (optional)

If you want to avoid running the Django backend inside Docker during development, you can run only the dependencies in Docker and run Django/Celery locally:

1) Start only Postgres + Redis:
```bash
docker compose up -d db redis
```

2) In a local Python environment (venv) run backend:
```bash
cd door_backend
python manage.py migrate
python manage.py runserver 0.0.0.0:8010
```

3) (Optional) Local workers:
```bash
cd door_backend
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Note: this “hybrid dev” mode requires you to have Python deps installed locally. If not, use full Docker.

## Run the web admin

```bash
cd door_web
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` if your backend URL differs (default: `http://localhost:8010/api/v1`).

## Visual workflow (recommended)

Keep these running while you work:

Terminal A (backend):
```bash
cd /home/dg/door-app
docker compose up --build
```

Terminal B (web):
```bash
cd /home/dg/door-app/door_web
npm run dev
```

Then after each task:
```bash
cd /home/dg/door-app
bash scripts/dev_smoke.sh
```

## Run the Flutter app

```bash
cd door_mobile
flutter pub get
flutter run
```

## Notes

- Local-only roadmap/instruction files are intentionally ignored by git.
- Do not commit secrets: keep `door_backend/.env` and Firebase service-account files local.
