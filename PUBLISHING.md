# Publishing to GitHub (clean repo)

This repo is intended to be published **without** the local-only AI instruction pack files.

## Pre-publish checklist (run every time)

1) Backend (migrations)
- `docker compose exec -T backend python manage.py migrate`

2) Web (build)
- `cd door_web && npm run build`

3) Mobile (static checks + tests)
- `cd door_mobile && flutter analyze && flutter test`

4) Live smoke checks
- Backend docs: `curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8010/api/v1/docs/`
- Web profile: `curl -sS -o /dev/null -w "%{http_code}\n" http://<host>:3002/dashboard/profile`
- Mobile root: `curl -sS -o /dev/null -w "%{http_code}\n" http://<host>:8082/`
- Full smoke: `bash scripts/dev_smoke.sh`

Note:
- If `127.0.0.1` is not listening for web/mobile, use the server host IP shown by `ss -lntp`.

## Production run mode (important)

Use production mode on public host:
- `cd door_web && npm run build && npm run start`

Avoid serving public traffic with `npm run dev` unless this is temporary development.

If you see browser errors like:
- `GET /_next/static/css/app/layout.css ... 404`
- `GET /_next/static/chunks/main-app.js ... 404`

Then do this recovery sequence:
1) Stop any running web process on `3002`.
2) `cd door_web && npm run clean && npm run build && npm run start`
3) Hard-refresh browser (`Ctrl+Shift+R`) to clear stale asset references.

## Local-only files (excluded)

These files are ignored by git (see `.gitignore`) and should not be published:
- `00_DOOR_APP_MASTER_ROADMAP.md`
- `01_SCOPE_GUARDRAILS.md`
- `02_IMPLEMENTATION_INSTRUCTIONS.md`
- `03_PHASE_WISE_PROMPTS.md`
- `04_EXISTING_APP_REWRITE_PLAN.md`
- `05_COMPLETE_APP_FEATURES.md`
- `APP_PORTS_AND_PATHS.md`
