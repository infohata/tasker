# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`tasker` — a simple project/task manager built with Django, deployable via Docker Compose.

The primary purpose of this repo is to serve as a **testbed for the mind-vault workflows** (`/idea`, `/plan`, `/work`, `/wrap`, `/compound`, `/sprint-auto`, review-loops). Feature scope is intentionally modest so the workflow plumbing — not the domain — is what gets exercised.

## Stack

- Python 3.12 (pinned in `.python-version` for pyenv-aligned host venvs)
- Django 5.2.9 (LTS track)
- Daphne ASGI — single server, no Gunicorn+Daphne split
- PostgreSQL 16
- Redis 7 (cache via `django-redis`; Channels layer when WebSockets land)
- nginx (alpine) as the host-facing proxy on port `80`, mirroring prod — serves `/static/` and `/media/` directly from disk; everything else proxies to Daphne
- Docker Compose for everything — no bare `docker` commands, no host-level installs
- `django-environ` driving settings; `.env` is gitignored, `.env.template` is the contract

DRF, Django Channels, and Celery are intentionally NOT in `requirements/base.txt` yet — they install with the first IDEA that actually needs them (per `CLAUDE.md` "no over-engineering").

## Commands

The Makefile is the canonical entrypoint. `make help` lists everything; the most common targets:

```
make up              # start the stack (web, db, redis, nginx) detached
make down            # stop the stack (volumes preserved)
make build           # rebuild the web image
make rebuild         # down + build + up in one shot
make shell           # bash in the web container
make test            # run pytest inside web
make migrate         # apply Django migrations
make makemigrations  # create migrations from model changes
make collectstatic   # collect static files into static_collected/ (served by nginx)
make logs            # tail logs for all services
make ps              # show running services
make self-sweep      # pyflakes against project source (RULE_self-sweep-before-push)
make clean           # DESTRUCTIVE: down -v (drops named volumes / wipes DB)
```

Run a single test: `docker compose exec -T web pytest tasker_django/health/tests/test_health.py::test_health_endpoint_returns_ok`.

First-time setup: `cp .env.template .env`, then `make up`, then `make migrate`. The stack is reachable at `http://localhost/` via nginx; `http://localhost/health/` should return `{"status": "ok"}`.

## What lives where

- `compose.yml` / `Dockerfile` / `.dockerignore` — container definitions
- `nginx/default.conf` — nginx vhost; proxies host `:80` to `web:8000`
- `Makefile` — developer shortcuts (see Commands)
- `manage.py` — Django entrypoint at the repo root
- `tasker/` — Django **project** package (`settings.py`, `urls.py`, `asgi.py`, `wsgi.py`)
- `tasker_django/` — **apps container** (named-by-project, not generic `apps/`); future domain apps register as `tasker_django.projects`, `tasker_django.tasks`, etc.
- `tasker_django/health/` — diagnostic `GET /health/` endpoint + smoke tests; first inhabitant of the apps container
- `requirements/` — split into `base.txt` (runtime) and `dev.txt` (pytest, pyflakes); dev extends base
- `pytest.ini` — `pytest-django` config; `testpaths = tasker_django`
- `.env.template` — env var contract; real `.env` is gitignored and off-limits to Claude in the primary tree
- `.python-version` — pyenv pin (3.12.7)
- `docs/ideas/` — atomic IDEA backlog (`IDEA-NNN-<slug>.md`) + `README.md` index
- `docs/archive/YYYY-MM-idea-NNN-<slug>/` — permanent home for in-progress/complete/superseded/rejected IDEAs and their plans, devlogs, screenshots

## Mind-vault conventions

- Atomic IDEAs live in `docs/ideas/IDEA-NNN-<slug>.md`; index at `docs/ideas/README.md`.
- Per-IDEA archive at `docs/archive/YYYY-MM-idea-NNN-<slug>/` (IDEA file, plan, devlog, amendments).
- Sprint workflow: `/idea` → `/plan` → `/work` → review-loop → `/wrap` → `/compound`.
- Feature work on `feature/idea-NNN-<slug>` branches; PRs target `main`; human merges (`RULE_git-safety`).
- Self-sweep (`make self-sweep`) before every push (`RULE_self-sweep-before-push`).
