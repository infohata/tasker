---
stage: plan
slug: django-skeleton
created: 2026-05-19
source: ./IDEA-001-django-skeleton.md
status: ready
project: tasker
---

# IDEA-001 — Django + Docker Compose Skeleton Plan

## Context

`tasker` is empty. We need the minimum runnable Django stack so subsequent IDEAs (auth, projects, tasks, HTMX UI) have somewhere to land. The seed `CLAUDE.md` specifies the intended stack: Django 5.2.9 (LTS track), Daphne ASGI (no Gunicorn split), Postgres, Redis, nginx proxy, Docker Compose, Makefile-first. This IDEA delivers exactly that minimum — no domain models, no auth customisation, no UI library wiring.

This is also the first end-to-end exercise of the mind-vault sprint workflow against this repo. Patterns established here (commit shape, directory layout, Makefile vocabulary, requirements split) become the default every later IDEA inherits.

## Problem Frame

- No `compose.yml`, no `Dockerfile`, no Django project package, no Makefile, no test config. Nothing to run.
- Without a runnable stack, `/work` has no validation surface — every later IDEA's verification step would have to scaffold the stack first.
- The chosen conventions (Daphne-only, nginx mirroring prod, `tasker_django/` apps-container layout, env via django-environ) need to land once, deliberately, before anyone has to relitigate them mid-feature.

## Requirements Trace

- **R1.** `make up` from a fresh clone (with `.env` populated from `.env.template`) brings the full stack online (web + db + redis + nginx). Source: IDEA-001 proposal.
- **R2.** Django responds 200 on `GET /health/` through the nginx proxy port. Source: IDEA-001 proposal (smoke test).
- **R3.** A single smoke test (`pytest`) hits `/health/` against the running stack and asserts the JSON response. Source: IDEA-001 proposal.
- **R4.** Makefile exposes: `up`, `down`, `shell`, `test`, `migrate`, `makemigrations`, `logs`. Source: seed `CLAUDE.md` Commands section.
- **R5.** `.env.template` enumerates every required env var; the real `.env` is gitignored and never read by Claude in the primary tree. Source: global CLAUDE.md guardrail.
- **R6.** Requirements are split: `requirements/base.txt` (runtime) and `requirements/dev.txt` (pytest, pytest-django, pyflakes). Source: IDEA-001 proposal + `RULE_self-sweep-before-push`.
- **R7.** `tasker_django/` is a Python package (`tasker_django/__init__.py`) so future domain apps register as `tasker_django.projects`, `tasker_django.tasks`, etc. The named-by-project container avoids the generic `apps/` smell (which also visually clashes with Django's internal `django.apps`). Source: IDEA-001 proposal, refined per user direction during /plan review.
- **R8.** Daphne is the single ASGI server (`daphne tasker.asgi:application`), no Gunicorn fallback. Source: global CLAUDE.md preference.
- **R9.** Settings driven by environment variables via `django-environ`; no hard-coded secrets. Source: global CLAUDE.md + `.env.template` convention.
- **R10.** `CLAUDE.md`'s "Commands" + "What lives where" sections flip from "planned" to actual once everything lands. Source: seed `CLAUDE.md` self-instruction.

## Scope Boundaries

**In scope:**

- `Dockerfile` (single-stage `python:3.12-slim`, Daphne entrypoint)
- `.dockerignore`
- `compose.yml` (services: `web`, `db`, `redis`, `nginx`)
- `nginx/default.conf` (proxy_pass to `web:8000`)
- `tasker/` Django project package: `__init__.py`, `settings.py`, `urls.py`, `asgi.py`, `wsgi.py`
- `tasker_django/__init__.py` (empty package placeholder — no domain apps yet)
- `tasker_django/health/` — single minimal app exposing `GET /health/` for the smoke test. Lives in `tasker_django/` so the package isn't empty and the layout is exercised by something real.
- `requirements/base.txt`, `requirements/dev.txt`
- `Makefile`
- `.env.template`
- `pytest.ini` + one smoke test under `tasker_django/health/tests/`
- `manage.py`
- `.python-version` pinning to `3.12.7` (pyenv-friendly per CLAUDE.md)
- Update `CLAUDE.md` Commands + structure sections

**Out of scope (separate IDEAs):**

- Domain models (`Project`, `Task`, user customisation) — IDEA-002+
- Authentication beyond Django default — separate IDEA
- HTMX / Alpine / Bulma / Cotton frontend wiring — separate IDEA
- Celery + worker container — deferred per CLAUDE.md (watching Django 6 native workers)
- Django Channels (real ASGI consumers) — added when first WS feature lands
- CI/CD (GitHub Actions) — separate IDEA
- Production deployment + Let's Encrypt — separate IDEA via `/deployment` skill
- DRF wiring — separate IDEA (lands with the first API surface)

**Explicit non-goals:**

- No multi-stage Dockerfile optimisation yet — single-stage is fine, refactor when image size becomes a real cost
- No WhiteNoise — nginx serves static via shared volume, mirroring prod
- No `collectstatic` automation — no static yet to collect
- No custom Django user model — premature without a domain reason
- No `.env` file committed, ever — only `.env.template`

## Context & Research

### Existing code and patterns to reuse

- _(none — greenfield repo)_

### Institutional learnings

- Global `CLAUDE.md` § Stack & Experience — Daphne-only ASGI, pyenv, Docker Compose for everything, Makefile shortcuts.
- Global `CLAUDE.md` § Guardrails — never read `.env`; the worktree-specific exception does NOT apply here (this is the primary tree). `.env.template` is the only env file in git.
- `mind-vault/rules/RULE_git-safety.md` — every commit lands on `feature/idea-001-django-skeleton`, never `main`.
- `mind-vault/rules/RULE_self-sweep-before-push.md` — pyflakes belongs in `requirements/dev.txt` from day one so every later IDEA's self-sweep step works without ceremony.
- `mind-vault/skills/django/SKILL.md` — Django backend conventions (BaseModel etc.) are deferred to first domain-modelling IDEA; this IDEA only provides the skeleton they'll plug into.
- `mind-vault/skills/deployment/SKILL.md` — production Docker Compose patterns; this IDEA lays compatible groundwork (env-driven settings, nginx in front) but stays dev-only.

### External references

- Django 5.2.9 release notes — confirms Python 3.10–3.13 support, `python:3.12-slim` is in the sweet spot.
- `django-environ` README — preferred env loader (typed `env.db()`, `env.cache()`) over hand-rolled `os.environ`.
- Daphne CLI — entrypoint is `daphne -b 0.0.0.0 -p 8000 tasker.asgi:application`.

## Key Technical Decisions

- **Python 3.12.7 via pyenv inside `python:3.12-slim`.** Matches CLAUDE.md preference; 3.12 is the production-default for Django 5.2 in mid-2026; `.python-version` keeps host-side venv tooling aligned.
- **Daphne single-server, no Channels yet.** Daphne happily serves `get_asgi_application()` without Channels. Channels installs when a real WS consumer appears, not before — keeps the dependency surface honest.
- **`tasker_django/` as the apps container; `tasker_django.health` as the first inhabitant.** Named-by-project (not generic `apps/`) — keeps the layout readable when grepping or browsing, and dodges visual confusion with Django's internal `django.apps`. Avoids the empty-package smell, exercises the import path (`INSTALLED_APPS = ["tasker_django.health", ...]`), and gives the smoke test a real view to target.
- **Settings driven by `django-environ`.** Single `tasker/settings.py`, all secrets and connection strings via `env(...)`. Multi-file settings split happens when staging/prod divergence forces it, not pre-emptively.
- **Postgres 16, Redis 7.** Current LTS-ish lines as of 2026-05; both via official docker images pinned to major versions, not `latest`.
- **nginx serves the user-facing port; web container exposes only to the internal docker network.** Mirrors prod, surfaces any proxy_pass quirks early. nginx host port is `80` (resolved Q2 — user opted for prod parity over collision-avoidance).
- **One `compose.yml`, no `docker-compose.override.yml` in git.** The override file is gitignored (already covered in root `.gitignore`); local-only customisations belong there.
- **Smoke test via `pytest-django` + `Client`, NOT live HTTP through nginx.** The pytest run is in-container against Django directly — testing the framework wiring, not nginx config. A manual `curl http://localhost/health/` is the verification step that exercises the nginx hop.
- **Requirements pinning style.** `~=` (compatible-release) for top-level deps to allow patch updates; later Dependabot IDEAs can tighten to exact pins or stay loose — decision deferred.
- **No `BaseModel` abstraction here.** It belongs in the first domain-modelling IDEA where it actually has a consumer. Adding it now would be speculative per CLAUDE.md "no over-engineering".

## Open Questions

- **Q1. Should `django-channels` be installed in base requirements now or deferred?**
  - **Default:** Deferred. Daphne serves plain ASGI Django; Channels adds when a WS feature lands.
  - **Trade-off:** Deferring keeps the dep tree minimal but means later IDEAs add Channels + run migrations for `django_channels`. Installing now front-loads that cost but adds a dep with no current consumer.
- **Q2. nginx host port — `8080` or `80`?** _Resolved: `80`._
  - **Resolution:** Bind nginx to host `:80` for prod parity. User accepts the requirement that no other service (system nginx, apache) holds `:80`, and that docker can bind privileged ports (default on Linux with the docker daemon running as root).
  - **Trade-off accepted:** Maximum dev/prod fidelity; if a collision surfaces on a given machine, override locally via `docker-compose.override.yml` (gitignored).
- **Q3. `tasker_django.health` — keep as a permanent diagnostic app or absorb the `/health/` view into the project `urls.py` later?**
  - **Default:** Keep. `/health/` is a legit ops surface (k8s probes, monitoring) and `tasker_django.health` is a natural home for future readiness/liveness expansion.
  - **Trade-off:** Slight ceremony for a one-view app, but the alternative (a view in `tasker.urls`) blurs the project/apps boundary the layout is trying to establish.
- **Q4. Pin Postgres to `16` (major) or `16-alpine` / a specific minor?**
  - **Default:** `postgres:16` (major-only). Patch updates land transparently; `alpine` postgres has occasional libc-related surprises.
  - **Trade-off:** Slightly larger image vs. fewer surprises.

## Execution Sequence

Branch `feature/idea-001-django-skeleton` already exists with the kickoff commit (`ad85c93`) and draft PR #1. All commits below land on that branch. RULE_self-sweep-before-push runs before each `git push`.

1. **`docs(plan)`** — emit this plan + the IDEA frontmatter flip + ideas index update. _(This commit.)_
2. **`chore(docker)`** — `Dockerfile`, `.dockerignore`, `requirements/base.txt`, `requirements/dev.txt`, `.python-version`. Does NOT yet wire compose.
3. **`chore(compose)`** — `compose.yml` (web/db/redis/nginx), `nginx/default.conf`, `.env.template`. `make up` works after this commit but `web` will error until step 4 lands `manage.py`.
4. **`feat(django)`** — `tasker/` package (`__init__.py`, `settings.py`, `urls.py`, `asgi.py`, `wsgi.py`) + `manage.py` + `tasker_django/__init__.py`. Django boots; `manage.py check` is green.
5. **`feat(health)`** — `tasker_django/health/` (apps.py, urls.py, views.py with `health_view` returning `JsonResponse({"status": "ok"})`), wire into `tasker.urls`. `curl http://localhost/health/` returns 200.
6. **`test(smoke)`** — `pytest.ini`, `tasker_django/health/tests/__init__.py`, `tasker_django/health/tests/test_health.py`. `make test` runs and passes.
7. **`chore(make)`** — `Makefile` with `up`, `down`, `shell`, `test`, `migrate`, `makemigrations`, `logs`. Replaces any raw `docker compose` invocations from earlier commits where applicable in the plan's docs.
8. **`docs(claude)`** — update `CLAUDE.md` Commands + "What lives where" sections from "planned" to actual; remove the pre-scaffolding status banner.
9. **PR ready for review** — mark draft PR #1 ready, request review, human merges (RULE_git-safety: PR is the HITL gate).

### Key file shapes (sketch, not final)

**`tasker/settings.py`** (illustrative excerpt):

```python
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tasker_django.health",
]

DATABASES = {"default": env.db("DATABASE_URL")}
CACHES = {"default": env.cache("REDIS_URL")}

ROOT_URLCONF = "tasker.urls"
ASGI_APPLICATION = "tasker.asgi.application"
```

**`compose.yml`** services (sketch):

```yaml
services:
  web:
    build: .
    command: daphne -b 0.0.0.0 -p 8000 tasker.asgi:application
    env_file: .env
    depends_on: [db, redis]
    volumes: [".:/app"]
  db:
    image: postgres:16
    environment: { POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD }
    volumes: [pg_data:/var/lib/postgresql/data]
  redis:
    image: redis:7
  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes: ["./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro"]
    depends_on: [web]
volumes:
  pg_data:
```

**`.env.template`**:

```
DJANGO_SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,nginx
DATABASE_URL=postgres://tasker:tasker@db:5432/tasker
REDIS_URL=rediscache://redis:6379/1?client_class=django_redis.client.DefaultClient
POSTGRES_DB=tasker
POSTGRES_USER=tasker
POSTGRES_PASSWORD=tasker
```

## Verification

After step 8, all of the following must be green:

- `cp .env.template .env` (no manual edits required for dev defaults to work).
- `make up` — stack boots, no restart loops in `docker compose ps`.
- `make migrate` — applies Django built-in migrations against fresh Postgres, exit 0.
- `make test` — pytest finds and passes the `/health/` smoke test.
- `curl -s http://localhost/health/` — returns `{"status": "ok"}` with HTTP 200 (exercises the nginx → web hop).
- `docker compose exec -T web python -m pyflakes tasker_django/ tasker/` — clean (self-sweep gate).
- `make down` — `docker compose ps` empty, no orphan containers, named volume preserved.
- `git log --oneline feature/idea-001-django-skeleton ^main` shows the commit sequence from step 1–8.

## Architect Review

Skipping for now — scope is medium-bordering-small (one application surface, no abstractions worth pressure-testing, no cross-cutting concerns). The Open Questions section already captures the genuine forks. Will invoke `AGENT_architect` if any Q1–Q4 answer flips during `/work` or if the scope grows.

---

**Status:** ready — user accepted defaults on Q1/Q3/Q4 (Channels deferred, `tasker_django.health` permanent, `postgres:16` major-pin); Q2 resolved to host port `80` for prod parity. `/work` execution starting from step 2 (step 1 already shipped in commits `4ea1de9` + `58c6085` + `354bc57`).
