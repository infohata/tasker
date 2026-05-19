# Development Log — 2026-05

Chronological record of merged work, newest first. Authored by `/wrap` per IDEA at merge time.

---

## 2026-05-19 — IDEA-001: Django + Docker Compose Skeleton (PR #1)

**Scope**: Bootstrap the `tasker` repo into a runnable Django stack. Establishes every convention later IDEAs inherit — project package + apps-container layout, Daphne single-server ASGI, nginx-fronted dev mirroring prod, Docker Compose for everything, Makefile-first developer workflow, `django-environ`-driven settings, `pytest-django` test surface. Also the first end-to-end exercise of the mind-vault sprint workflow against this repo, from `/idea` through `/wrap`.

### What shipped

- **Docker layer**: `Dockerfile` (python:3.12-slim, Daphne entrypoint, build deps for psycopg), `.dockerignore`, `requirements/base.txt` (Django 5.2, django-environ, daphne, psycopg[binary], django-redis), `requirements/dev.txt` (extends base with pytest, pytest-django, pyflakes), `.python-version` pinned to 3.12.7.
- **Compose stack**: `compose.yml` with services `web` (Daphne), `db` (postgres:16 with healthcheck), `redis` (redis:7), `nginx` (alpine, host port `80`). `nginx/default.conf` proxies everything to `web:8000` with `Upgrade`/`Connection` headers pre-armed for future WS.
- **Django project**: `tasker/` package with `settings.py` / `urls.py` / `asgi.py` / `wsgi.py`, plus `manage.py` at the repo root. Settings driven entirely by env vars — `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASES`, `CACHES` all from `environ`.
- **Apps container**: `tasker_django/` (named-by-project, not generic `apps/`) with `tasker_django.health` as the first inhabitant — exposes `GET /health/` returning `JsonResponse({"status": "ok"})`. Sets the import-namespace convention for future domain apps (`tasker_django.projects`, `tasker_django.tasks`, etc.).
- **Test surface**: `pytest.ini` configures `pytest-django` against `tasker.settings`, `testpaths = tasker_django`. Two smoke tests under `tasker_django/health/tests/test_health.py` — one asserts the 200 + JSON body, one locks the public URL to `/health/`.
- **Makefile**: `up`, `down`, `build`, `rebuild`, `shell`, `test`, `migrate`, `makemigrations`, `logs`, `ps`, `self-sweep` (pyflakes against project source), `clean` (destructive `down -v`).
- **CLAUDE.md** flipped from the pre-scaffolding seed to actual: Commands section enumerates every Makefile target, "What lives where" reflects real layout, Stack section names exact versions (Django 5.2.9, Postgres 16, Redis 7, Python 3.12.7).

### Infrastructure fixes landed in the same PR

- **DB credentials — single source of truth.** Original `.env.template` carried the password twice (in `DATABASE_URL` and `POSTGRES_PASSWORD`); updating one without the other broke the Postgres↔Django auth handshake silently on first run. Fix (`f13360b`): drop `DATABASE_URL` from `.env.template` entirely. `compose.yml` now interpolates `DATABASE_URL` from `POSTGRES_*` into the web container's environment block. One knob, no drift.
- **`$`-escape note in `.env.template`.** Docker Compose interpolates `$VAR` references inside `env_file` values, silently corrupting any secret containing a literal `$`. Documented the `$$` escape requirement at the top of the template after a generated key with `$x` came through as garbage on first run.

### Related

- [IDEA-001 archive](2026-05-idea-001-django-skeleton/)
- [Plan doc](2026-05-idea-001-django-skeleton/2026-05-19-django-skeleton-plan.md)
- [PR #1](https://github.com/infohata/tasker/pull/1)
- Spinoff: [IDEA-002 (in progress, PR #2)](https://github.com/infohata/tasker/pull/2) — Static & Media Serving via nginx; surfaced when IDEA-001's `collectstatic` verification revealed that `/static/...` returns 404 because Daphne doesn't auto-serve static and nginx has no `location /static/` block yet.
