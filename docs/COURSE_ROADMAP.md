# Course Roadmap — Tasker

A living teaching plan for the **tasker** project. Nine guided sessions (~4 hours each) demonstrate the mind-vault sprint workflow against a real Django stack, with Django itself introduced incrementally for students coming from the PHP world (Symfony / Laravel).

Each session is one full sprint cycle: **ideate → plan → work → review → wrap → merge**. The mechanics are taught *by doing them*, not by lecture — every step lands a commit students can grep, diff, and replay.

This document is iterated each session: status flips, links to the merged PRs land here, and pacing can shift based on student questions or surprise findings.

---

## Cohort shape

- Each student maintains **their own fork** of this repo (or their own greenfield repo following the same template). The instructor's repo at `infohata/tasker` is the canonical reference for "what the trajectory looks like when it goes well" — students compare their PR diffs against it for sanity checks, but every student walks the workflow themselves.
- Sessions are **live, paired, and synchronous**: instructor drives the workflow against the canonical repo; students drive against their own. By the end of each session, every student should have an equivalent PR merged in their own fork.
- Drift between the canonical repo and a student's fork is **expected and educational** — different open-question resolutions, different /plan reviewer findings, different review-loop iterations produce honest divergence. The instructor's repo is a *reference*, not a *spec*.

## Audience

- Working developers with PHP-framework backgrounds (Symfony or Laravel as the high-water mark).
- No prior Django exposure assumed.
- Familiar with the *concept* of AI-assisted coding but not the discipline of structured AI workflows.
- Comfortable with Docker Compose, git, and the command line.

## Teaching philosophy

1. **Mechanics first, theory second.** Run the full sprint cycle for every IDEA. The PR diff *is* the lesson — `git log` and `git show` are first-class teaching tools.
2. **Mind-vault is the harness; Django is the payload.** Each session uses the workflow to deliver a Django concept. Students leave knowing *both* better.
3. **Real findings beat curated examples.** When something breaks in verification (as it did with `.env.template` during IDEA-001), surface it, fix it in the same PR, and use the failure as the teaching moment. Don't sanitise the trajectory.
4. **PHP → Django translations are explicit.** Every Django concept gets a short "in Symfony this would be X" / "Laravel does this with Y" anchor when one exists.
5. **No solo sessions.** Instructor drives the canonical workflow; students debate decisions, vote on open questions, take turns dispatching personas in their own forks.

## Pre-requisites checklist

Before Session 1:

- `docker compose` working
- `git` configured with name + email
- GitHub account + `gh` CLI authenticated
- Claude Code installed with mind-vault skills accessible

Session 1 walks every student through repo bootstrap from scratch — nothing exists yet at session start.

---

## Phase overview

| Phase | Sessions | Theme |
|---|---|---|
| 1 — Stabilise & harden | S1, S2 | Repo bootstrap + skeleton; nginx static/media routing |
| 2 — Django ORM intro | S3, S4 | Custom User; then Project + Task models (admin-only) |
| 3 — Polished UI foundation | S5, S6 | AI-assisted base template; then auth UI templates |
| 4 — Domain CRUD UI | S7, S8, S9 | Project list CRUD; Kanban + Task CRUD; feature-rich Task detail page |

---

## Sessions

### Session 1 — Repo bootstrap + first sprint end-to-end (PHASE 1 starts)

**Status**: ✅ Shipped — 2026-05-19

**Goal**: From an empty directory, ship a runnable Django stack via the full mind-vault sprint workflow. The session *itself* is the introduction to both Django and mind-vault — students experience capture-to-merge in one sitting.

**IDEAs**:
- **IDEA-001** — Django + Docker Compose Skeleton (✅ merged via PR #1)
- **IDEA-002** — Static & Media Serving via nginx (📋 captured + planned, work pending in S2)

**What actually shipped (instructor's repo)**:
- IDEA-001 end-to-end: capture → plan (with one /plan-time amendment on `apps/` → `tasker_django/`, one open-question resolution on nginx port 80, two mid-flight `.env.template` fixes) → work (8-commit execution sequence) → wrap → human merge.
- IDEA-002 capture + plan + draft PR opened off a forward-synced branch — work-and-merge deferred to Session 2.
- This roadmap document, opened as PR #3.
- Repo state: Django 5.2.9 on Daphne behind nginx on host port 80, Postgres 16, Redis 7, `tasker_django.health` exposing `GET /health/` returning 200.

**Django teaching moments covered**:
- Project (`tasker/`) vs apps container (`tasker_django/`) — why named-by-project beats generic `apps/`.
- `manage.py`, `settings.py`, `urls.py`, `asgi.py` — Symfony's `bin/console`, `config/`, routing equivalents.
- `django-environ` for env-driven settings — closer to Symfony's `.env` than Laravel's `config/*.php`.
- Daphne single-server ASGI — most Symfony/Laravel students have only seen PHP-FPM behind nginx; Daphne is similar in shape but Python-native and async-capable.
- Smoke testing through the real nginx hop, not Django's in-process test client.

**Mind-vault teaching moments covered**:
- Five-stage workflow: `/idea` → `/plan` → `/work` → review (manual or `/<engine>-loop`) → `/wrap` → `/compound`.
- `RULE_git-safety`: feature branches per IDEA, PRs target `main`, human merges.
- `RULE_self-sweep-before-push`: pyflakes inside the dev container as a pre-push gate.
- Forward-sync of an in-flight branch when its parent IDEA merges (demonstrated between PR #1 and PR #2).
- "If verification fails, document the failure in the plan's Open Questions section before opening the PR" — surfaced live when `.env.template` dual-source-of-truth broke `make migrate`.

**Outputs**:
- PR #1 merged — repo skeleton on `main`
- PR #2 open as draft — IDEA-002 plan ready, work pending
- PR #3 open — this roadmap (iteration 1)

---

### Session 2 — Static & media routing via nginx (PHASE 1 closes)

**Status**: 🚧 Next — picks up IDEA-002 from PR #2.

**Goal**: Finish what S1 started for IDEA-002. Demonstrate the **second half** of a sprint when planning lives across two sessions — students pick up a plan they didn't author, execute it, and discover what's load-bearing in the plan and what isn't.

**IDEAs**:
- IDEA-002 — Static & Media Serving via nginx (work, review, wrap, merge).

**Activities**:
- Re-read IDEA-002's plan as a group; confirm Q1–Q3 resolutions still hold.
- Flip plan `draft → ready`; run `/work`.
- Watch the smoke test pass live. If it fails, treat the failure as the lesson.
- Run review-loop (Bugbot or Copilot) if configured; manual review otherwise.
- `/wrap` IDEA-002 → merge PR #2.
- Run `/compound` on IDEA-001 + IDEA-002 — both have findings worth routing (`.env.template` dual-source-of-truth, Compose `$`-interpolation gotcha, "smoke test through the real hop" pattern).

**Django teaching moments**:
- `STATIC_URL` vs `STATIC_ROOT` — why two? Symfony's `assets:install` is the rough analogue; Laravel uses Vite.
- `collectstatic` mechanics; manifest vs filesystem finders.
- Why Django *itself* shouldn't serve static in production (and why `runserver` does anyway, masking the problem).

**Mind-vault teaching moments**:
- "Picking up another session's plan" — the plan is a *contract*; if it's wrong, route back to `/plan`, don't paper over it.
- `/<engine>-loop` semantics — review bot finds something; you triage; you fix; you push; it re-reviews.
- `/wrap` pre-merge sweep mechanics — index, devlog, downstream-docs grep.
- `/compound` routing — project-local solution doc vs mind-vault rule/skill vs auto-memory.

**Outputs**: PR #2 merged. IDEA-002 in `## ✅ References — Implemented`. Devlog appended. Mind-vault gains entries for any compound-routed findings.

---

### Session 3 — Custom User model (PHASE 2 starts)

**Status**: 📋 Planned

**Goal**: Add a custom `User` model **before any other model** — the single most-important "do this on day one or regret it" Django rule. Admin-only surface, no public auth UI yet.

**IDEAs to capture**: one IDEA for custom User + minimal admin registration.

**Activities**:
- Ideate: what should `User` carry beyond `AbstractUser`? (timezone? locale? avatar URL?) Pick a minimum useful set; the rest is YAGNI.
- `/plan` — architect-review pass **mandatory** here. `AUTH_USER_MODEL` decisions are high-blast-radius and easy to get wrong.
- `/work`: create `tasker_django.users` app, custom `User(AbstractUser)`, `AUTH_USER_MODEL = "users.User"`, regenerate initial migrations.
- Show `manage.py sqlmigrate` to expose the actual SQL.
- Register a `UserAdmin` subclass; show admin list/search/filter wiring.

**Django teaching moments**:
- `AbstractUser` vs `AbstractBaseUser` — when to extend which.
- Migrations: Django auto-generation vs Doctrine `make:migration`. Show what auto-generated migrations actually look like.
- The "custom User on day one" rule — *why* it's painful to retrofit later (every FK to `auth.User` would need re-pointing).
- `LOGIN_URL`, `LOGIN_REDIRECT_URL` — set the dials early.

**Mind-vault teaching moments**:
- `AGENT_architect` reviewer pass — mandatory for high-blast-radius decisions.
- Open-questions discipline — when a Q's default is wrong for *this* project's context.

**Outputs**: PR merged. `tasker_django.users` app with `User` model migrated; admin works against the custom user.

---

### Session 4 — Project + Task models (PHASE 2 closes)

**Status**: 📋 Planned

**Goal**: Land both domain models in one session via two scoped-down IDEAs. Admin-only CRUD. Practise ORM relationships, migrations, and N+1 prevention.

**IDEAs to capture**:
- One IDEA for `Project` (owner=FK(User), name, description, timestamps).
- One IDEA for `Task` (project=FK, assignee=FK(User), status, priority, due_at, completed_at).

**Activities**:
- Ideate field sets jointly. Resist scope creep — keep models minimum-useful.
- Plan both IDEAs back-to-back; `/work` them sequentially or in parallel worktrees (introduces parallel-worktree-docker pattern).
- For each model: define → `makemigrations` → inspect SQL → admin registration → tests (model-level + admin-level).
- Demonstrate `select_related('owner')` on `ProjectAdmin.get_queryset` and `prefetch_related('tasks')` for project lists.
- Show `Count('tasks', filter=Q(tasks__status='open'))` for an annotated open-task count column.
- Inline `Task` editing inside `ProjectAdmin` via `TabularInline`.

**Django teaching moments**:
- `ForeignKey(on_delete=...)` — `CASCADE` vs `SET_NULL` vs `PROTECT`. PHP frameworks defer this to DB; Django moves it into Python.
- `__str__`, `Meta.ordering` defaults.
- `TextChoices` / `IntegerChoices` — proper enums in Django 5.
- ORM lookups, `Q`, `F`, annotations, `select_related` vs `prefetch_related`.
- `related_name`, `related_query_name`, when to set them.
- Composite indexes + `UniqueConstraint`.

**Mind-vault teaching moments**:
- Two IDEAs in one session — when it works (shared domain, tight coupling) and when it doesn't.
- Parallel worktrees demo (optional, if cohort wants depth on the isolation contract).

**Outputs**: Two PRs merged. `tasker_django.projects` and `tasker_django.tasks` apps live. Admin shows projects with inline tasks and annotated counts. All tests pass.

---

### Session 5 — AI-assisted base template (PHASE 3 starts)

**Status**: 📋 Planned

**Goal**: Land the generic base template every later page extends. Demonstrates the `frontend-design` skill *and* Django's template inheritance. No domain content yet — just the chrome.

**IDEAs to capture**: one IDEA for `base.html` + navigation + footer + a working "design system" foundation (Bulma is the default per `CLAUDE.md` — confirm or override at /plan time).

**Activities**:
- Ideate the layout *with* the `frontend-design` skill — let it produce a few variants, students pick. Teaches AI-collaborative design judgement (not "use the first thing it suggests").
- Wire Bulma (CDN initially; build pipeline IDEA later if needed).
- Decide on the nav contract: where does "Login / Sign up" live? Where does a user's "Projects" link sit? Stub the links to `#` for now.
- Plan should include a `block content`, `block title`, `block extra_head`, `block extra_scripts` contract — the dial-in points every later template uses.
- Write a renders-without-crashing template test for `base.html` via a tiny placeholder view.

**Django teaching moments**:
- Template inheritance: `{% extends %}`, `{% block %}` — closest cousin is Twig in Symfony; Laravel Blade is similar.
- `{% load static %}` and how that ties back to Session 2's nginx work.
- `{% url %}` reverse routing.
- Context processors (mention; don't implement — earned later).
- DRY templates without sacrificing readability.

**Mind-vault teaching moments**:
- `frontend-design` skill — when to invoke it; how to evaluate its output critically.
- "Generative content" IDEAs — the artefact is partly authored by the AI; the IDEA's success criteria become "the output passes this rubric".

**Outputs**: PR merged. `base.html` lives in `tasker_django/templates/base.html`. A placeholder home view renders the empty chrome. Tests assert it doesn't 500.

---

### Session 6 — Auth UI: registration + login + password-change (PHASE 3 closes)

**Status**: 📋 Planned

**Goal**: Wire user-facing authentication — registration, login, logout, password change — using Django's built-in views + templates extending the Session-5 base.

**IDEAs to capture**: one IDEA for the four auth flows, all template-driven.

**Activities**:
- Plan the URL surface: `/accounts/login/`, `/accounts/logout/`, `/accounts/register/`, `/accounts/password-change/`. Whether to mount under `/accounts/` or `/auth/` — debate.
- `/work`: use `LoginView`, `LogoutView`, `PasswordChangeView` from `django.contrib.auth.views`; write a custom `RegisterView` (Django doesn't ship one).
- Template per view extending `base.html`. Form errors rendered with Bulma classes.
- Decision: `@login_required` everywhere by default or per-view? Debate, write a default, document.
- Tests: anonymous user can register → logs in automatically; logged-in user can change password and the new password works on the next login; logout actually logs out.

**Django teaching moments**:
- Built-in auth views — Symfony's Security bundle requires bootstrap; Laravel Breeze/Jetstream are the rough parallel.
- `UserCreationForm` and how to customise it (we'll need to subclass since we have a custom User).
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` settings.
- CSRF behaviour: how the middleware works, what `{% csrf_token %}` injects, why AJAX needs the header.
- Message framework — `django.contrib.messages` for "you've registered!" toasts.

**Mind-vault teaching moments**:
- The "use the framework's built-ins until they break" rule — applies to Django auth, Symfony security, every mature framework. Don't reach for django-allauth until you've outgrown built-ins.

**Outputs**: PR merged. Users can register, log in, log out, change passwords. Tests cover each flow. The nav from Session 5 now links to live URLs.

---

### Session 7 — Project list CRUD (PHASE 4 starts)

**Status**: 📋 Planned

**Goal**: First user-facing domain CRUD. Class-based views, model forms, pagination, ownership-scoped querysets. Every authenticated user sees only their own projects.

**IDEAs to capture**: one IDEA — list, create, update, delete for `Project`.

**Activities**:
- Plan URL surface: `/projects/`, `/projects/new/`, `/projects/<pk>/edit/`, `/projects/<pk>/delete/`.
- `/work`: `ListView`, `CreateView`, `UpdateView`, `DeleteView` — pin each to `LoginRequiredMixin` and an `owner=self.request.user`-scoped queryset.
- Use `ModelForm` (Django auto-generates from the model).
- Templates: list + form + confirm-delete, each extending `base.html`.
- Pagination via `ListView.paginate_by` — show how default ordering matters here.
- Tests: anonymous → 302 to login; user A can't see/edit/delete user B's projects (security test, not just functional test).

**Django teaching moments**:
- Class-based views vs function-based — when each shines. (PHP world: closer to Symfony controllers than Laravel function-style routes.)
- `LoginRequiredMixin`, `UserPassesTestMixin`, `PermissionRequiredMixin`.
- `ModelForm` auto-generation; `fields = [...]` vs `exclude = [...]`.
- `get_queryset()` override pattern for ownership-scoped data.
- `get_success_url()` and `reverse_lazy`.
- Django messages on create/update/delete.

**Mind-vault teaching moments**:
- Security-test-first habit: write the "user A can't access user B's data" assertion *before* the view exists. This is `superpowers:test-driven-development` applied to authz.
- Ownership-scoping as a project pattern worth `/compound`-ing to `docs/solutions/` once it solidifies.

**Outputs**: PR merged. Logged-in users see their projects, create/edit/delete them. Cross-user-access tests pass (= are red without the scoping).

---

### Session 8 — Project Kanban + Task CRUD (PHASE 4 continued)

**Status**: 📋 Planned

**Goal**: The killer feature — a Kanban view of one project's tasks, grouped by status, with inline task create/edit/delete. Introduces HTMX (or Alpine) for the interactive parts.

**IDEAs to capture**:
- One IDEA for the Kanban view itself (read-only first: just render tasks grouped by status).
- One IDEA for in-place task CRUD (inline create form per column, edit-in-place, delete with confirm).

**Activities**:
- Plan whether to use HTMX (server-rendered partials, no JS framework) or Alpine.js (light client-side reactivity) or both. `django-frontend` skill applies here.
- Build the Kanban template: columns per status, cards per task. CSS grid or flex layout.
- HTMX partial-response pattern for creating a task without full page reload.
- Edit-in-place: HTMX `hx-get` swap for the edit form, `hx-post` for save.
- Drag-to-change-status — stretch (can be its own IDEA if time runs short).
- Tests: status grouping correct, can create/edit/delete tasks, cross-user authz still holds.

**Django teaching moments**:
- Template partials (`include`, custom inclusion tags) — Twig and Blade have direct parallels.
- View returning a *partial* (just a `<tr>` or `<div>`) vs a full page — Django doesn't care; the framework is HTTP-aware all the way down.
- Form processing in CBVs vs FBVs for HTMX-friendly responses.
- `django-htmx` package (or `django.contrib.htmx` — depending on what's current at session time).

**Mind-vault teaching moments**:
- `django-frontend` skill applied — HTMX partial-response contract, Alpine.js state shape, Bulma component primitives.
- `mobile-ux-polish` skill if drag-and-drop lands — touch vs mouse drag discrimination.
- Two-IDEA session where the second depends on the first — when to ship as one PR vs two.

**Outputs**: PR(s) merged. Project detail page shows a working Kanban with inline task CRUD.

---

### Session 9 — Feature-rich Task detail page (PHASE 4 closes)

**Status**: 📋 Planned

**Goal**: A full task detail page that goes beyond CRUD — activity log, comments, attachments (optional), assignee changes, due-date reminders. Demonstrates Django signals, generic FKs, file uploads (if attachments land), and proper "feature" scope discipline.

**IDEAs to capture** (pick a coherent subset together — full list is over-ambitious for one session):
- Comments on a task (separate model, FK to task + author).
- Activity log (signal-driven, records assignee/status/priority changes).
- File attachments (FK to task, uses media routing from Session 2).
- "Due soon" indicator on the task list (today/this-week/overdue badges).

**Activities**:
- Ideate the *minimum viable* set with the cohort. Pin scope before plan.
- For activity log: Django signals (`post_save` on Task) — show why signals can be a debugging nightmare (run order, recursion, hidden side effects).
- For comments: a fresh app `tasker_django.comments` with a `Comment` model linked to `Task`. If we generalise to "comments on anything", introduce generic FKs — but only if the cohort wants that depth.
- For attachments: revisit Session 2's `/media/` route — *now* it goes live. `FileField` + `upload_to` lambdas + safety considerations.
- Tests per feature subset.

**Django teaching moments**:
- Django signals — when they're great (decoupling), when they're a footgun (untraceable side effects).
- Generic relations (`contenttypes.GenericForeignKey`) — covered only if comments-on-anything is in scope.
- `FileField`, `ImageField`, `upload_to`, `MEDIA_ROOT`/`MEDIA_URL`.
- Storage backends (mention S3/MinIO as future options — don't implement).

**Mind-vault teaching moments**:
- Scope-pinning discipline — Session 9 is the most over-scopable session in this roadmap. Use `/plan`'s open-questions section to *say no* to features.
- `/compound` value compounds: every Django pattern learned earlier collapses time on this session.

**Outputs**: PR(s) merged. Task detail page does materially more than Session 8's inline edit.

---

## Beyond Session 9 — backlog seeds

These are *candidate* themes if the cohort wants follow-on sessions (capture as IDEAs only when committed):

- CI hardening: GitHub Actions running tests + pyflakes self-sweep on every PR
- Custom 404 / 500 error pages with proper templates
- Settings split (`base.py / dev.py / prod.py`) + security headers (HSTS, content-type-nosniff)
- Sentry (or self-hosted alternative) integration for error tracking
- Structured JSON logging with env-driven log levels
- i18n / translation workflow — `RULE_i18n-workflow` is a teaching artefact on its own
- Background workers: Celery + redis-backed task queue, "due soon" email notifications
- DRF API surface: turn the CRUD into a JSON API
- WebSocket-based live Kanban updates (introduces Django Channels properly)
- Production deploy with Let's Encrypt SSL via the `/deployment` skill
- `pre-commit` hooks (ruff, black, pyflakes-gate before push) — complements `RULE_self-sweep-before-push`

---

## Maintenance contract

This file is owned by **whoever wraps the most recent session**:

- After each session's `/wrap`, flip the session's `Status:` line and date-stamp.
- Append a one-line "what actually shipped" note linking the merged PRs.
- Update "Beyond Session 9" if any candidate IDEAs were captured but deferred.
- The `Outputs` line for each session becomes a permanent record once the session has run.

If a session unexpectedly grows or shrinks (a student question opens a tangent, a finding demands its own IDEA), update the roadmap **before** the next session — keeps expectations aligned across the cohort.

---

**Status legend**: 📋 planned · 🚧 in progress · ✅ shipped · ⚠️ deferred · ❌ rejected
