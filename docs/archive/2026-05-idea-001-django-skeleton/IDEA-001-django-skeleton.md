---
id: 001
title: Django + Docker Compose Skeleton
status: complete      # idea | in-progress | complete | superseded
priority: high   # high | medium | low
supersedes: []       # list of IDEA ids this replaces, or []
superseded_by: null
depends_on: []       # list of IDEA ids required before starting, or []
related: []             # list of IDEA ids that share context, or []
created: 2026-05-19
completed: 2026-05-19
# Sprint-auto eligibility gates — both must be `true` with explicit reasoning
# before sprint-auto can run this idea unattended overnight.
# Default to `false` at capture; upgrade in `/plan` once the unknowns are nailed down.
auto_safe: false                                     # true | false
auto_safe_reason: "Greenfield scaffolding — naming (project package, apps layout), Daphne/nginx wiring, and Makefile target shapes are all judgment calls. Needs a human-reviewed /plan pass before automation is appropriate."
sensitive_paths_cleared: false         # true | false
sensitive_paths_cleared_reason: "Lands docker-compose.yml, nginx config, Dockerfile, and .env.template — all explicit sensitive-zone paths. Human review required on the infrastructure surface."
---

# IDEA-001: Django + Docker Compose Skeleton

**Status**: ✅ Complete (2026-05-19, PR #1)
**Priority**: High

**Problem** (or opportunity): The `tasker` repo is empty. Nothing can be planned, worked, reviewed, or shipped until a runnable Django stack exists. Until then the mind-vault workflow has nothing to bite on.

**Proposal** (or idea): Stand up the minimum runnable surface defined in the seed `CLAUDE.md`:

- Django 5.2.9 project package (`tasker/`) with `settings`, `urls`, `asgi`
- `tasker_django/` directory (project-named apps container, not generic `apps/`) for future domain apps (no domain apps land in this IDEA — only a minimal `tasker_django.health` app to exercise the layout)
- Docker Compose stack: `web` (Daphne ASGI), `db` (Postgres), `redis`, `nginx` (proxy_pass)
- `Dockerfile` for the web image (pyenv-friendly Python, Daphne entrypoint)
- `Makefile` shortcuts: `up`, `down`, `shell`, `test`, `migrate`, `makemigrations`, `logs`
- `.env.template` (real `.env` gitignored; Claude never reads `.env` in primary tree)
- `requirements/` split: `base.txt`, `dev.txt` (pytest, pytest-django, pyflakes)
- `.gitignore`, `.dockerignore`, `pytest.ini` / `pyproject.toml` for test config
- `docs/ideas/`, `docs/archive/` directory layout (this IDEA's own archive is the first user)
- One smoke test that proves the stack boots and Django responds 200 on `/`

**Why now**:
- Foundational. Every subsequent IDEA (auth, projects model, tasks model, HTMX UI) depends on a running stack.
- Dogfoods the mind-vault workflow from commit zero — IDEA-001 → `/plan` → `/work` → `/wrap` → `/compound` is the first complete loop.
- Establishes the directory + tooling conventions that all later IDEAs inherit, so they don't have to relitigate layout.

**Non-goals**:
- No domain models (`Project`, `Task`) — those are separate IDEAs.
- No authentication / user model customisation beyond Django default — separate IDEA.
- No HTMX / Alpine / Bulma frontend wiring — separate IDEA.
- No Celery — deferred until a real async workload appears (per `CLAUDE.md`: watching Django 6 native workers).
- No CI/CD pipeline — separate IDEA once the stack is stable.
- No production deployment config — separate IDEA via `/deployment` skill.

**Related**: _(none — first IDEA in the project)_
