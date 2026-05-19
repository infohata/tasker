# Course Roadmap — Tasker

A living teaching plan for the **tasker** project. Eight guided sessions (~4 hours each) demonstrate the mind-vault sprint workflow against a real Django stack, with Django itself introduced incrementally for students coming from the PHP world (Symfony / Laravel).

Each session is one full sprint cycle: **ideate → plan → work → review → wrap → merge**. The mechanics are taught *by doing them*, not by lecture — every step lands a commit students can grep, diff, and replay.

This document is iterated each session: status flips, links to the merged PRs land here, and pacing can shift based on student questions or surprise findings.

---

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
5. **No solo sessions.** Instructor drives the workflow; students debate decisions, vote on open questions, take turns dispatching personas.

## Pre-requisites checklist

Before Session 1:

- `docker compose` working
- `git` configured with name + email
- GitHub account + `gh` CLI authenticated
- Claude Code installed with mind-vault skills accessible
- This repo cloned, `.env` from `.env.template`, `make up` successful, `curl http://localhost/health/` → 200

Session 0 (self-paced, ~30 min) walks the existing IDEA-001 archive so students see one complete sprint before they live one.

---

## Phase overview

| Phase | Sessions | Theme |
|---|---|---|
| 0 — Onboarding | 0 (self-paced) | Read one shipped sprint end-to-end |
| 1 — Stabilise & harden | 1 | nginx-served static + media routing |
| 2 — Django ORM intro | 2, 3 | Custom User; then Project + Task models (admin-only) |
| 3 — Polished UI foundation | 4, 5 | AI-assisted base template; then auth UI templates |
| 4 — Domain CRUD UI | 6, 7, 8 | Project list CRUD; Kanban + Task CRUD; Task detail page |

---

## Sessions

### Session 0 — Onboarding (self-paced, ~30 min)

**Status**: ✅ Available

**Goal**: Familiarise with the existing skeleton and one complete sprint trail.

**Activities**:
- Read `CLAUDE.md` end-to-end.
- Walk `docs/archive/2026-05-idea-001-django-skeleton/` — IDEA → plan → devlog.
- Trace one commit through `git show` and explain what each chunk delivered.
- Run `make up && make migrate && make test`, hit `http://localhost/health/`.

**Mind-vault**: artefact taxonomy (IDEA, plan, devlog), `RULE_git-safety`, `RULE_self-sweep-before-push`.

**Django**: project vs app distinction, `manage.py`, `django-environ`, why a custom User is *not* there yet (foreshadow Session 2).

---

### Session 1 — Static & media routing via nginx (PHASE 1)

**Status**: 🚧 In progress — IDEA-002, PR #2 draft.

**Goal**: Run one full sprint, draft-plan → merge. Introduce nginx-level routing, volume sharing between containers, and the "smoke test through the real hop" pattern.

**IDEAs (already captured)**: IDEA-002 — Static & Media Serving via nginx.

**Activities**:
- Review IDEA-002 + plan together. Resolve open questions Q1–Q3 as a group.
- Flip plan `draft → ready`; run `/work`.
- Watch smoke test pass live. Debug if it doesn't.
- Run review-loop (Bugbot or Copilot) if configured; manual review otherwise.
- `/wrap` → merge PR #2 → `/compound`.

**Django**:
- `STATIC_URL` vs `STATIC_ROOT` — why two? Symfony's `assets:install` is the rough analogue; Laravel uses Vite.
- `collectstatic` mechanics; manifest vs filesystem finders.
- Why Django *itself* shouldn't serve static in production (and why `runserver` does anyway).

**Mind-vault**:
- Forward-syncing a feature branch after a parent IDEA merges (we demonstrated this between IDEA-001 → IDEA-002 already).
- "Smoke test through the real hop" vs in-process test clients — pattern recurs.
- `/wrap` pre-merge sweep mechanics.

**Outputs**: PR #2 merged. IDEA-002 in `## ✅ References — Implemented`. Devlog entry appended.

---

### Session 2 — Custom User model (PHASE 2 starts)

**Status**: 📋 Planned

**Goal**: Add a custom `User` model **before any other model** — the single most-important "do this on day one or regret it" Django rule. Admin-only surface, no public auth UI yet.

**IDEAs to capture**: one IDEA for custom User + minimal admin registration.

**Activities**:
- Ideate: what should `User` carry beyond `AbstractUser`? (timezone? locale? avatar URL?) Pick a minimum useful set; the rest is YAGNI.
- `/plan` — architect-review pass **mandatory** here. `AUTH_USER_MODEL` decisions are high-blast-radius and easy to get wrong.
- `/work`: create `tasker_django.users` app, custom `User(AbstractUser)`, `AUTH_USER_MODEL = "users.User"`, regenerate initial migrations.
- Show `manage.py sqlmigrate` to expose the actual SQL.
- Register a `UserAdmin` subclass; show admin list/search/filter wiring.

**Django**:
- `AbstractUser` vs `AbstractBaseUser` — when to extend which.
- Migrations: Django auto-generation vs Doctrine `make:migration`. Show what auto-generated migrations actually look like.
- The "custom User on day one" rule — *why* it's painful to retrofit later (every FK to `auth.User` would need re-pointing).
- `LOGIN_URL`, `LOGIN_REDIRECT_URL` — set the dials early.

**Mind-vault**:
- `AGENT_architect` reviewer pass — mandatory for high-blast-radius decisions.
- Open-questions discipline — when a Q's default is wrong for *this* project's context.

**Outputs**: PR merged. `tasker_django.users` app with `User` model migrated; admin works against the custom user.

---

### Session 3 — Project + Task models (PHASE 2 continued)

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

**Django**:
- `ForeignKey(on_delete=...)` — `CASCADE` vs `SET_NULL` vs `PROTECT`. PHP frameworks defer this to DB; Django moves it into Python.
- `__str__`, `Meta.ordering` defaults.
- `TextChoices` / `IntegerChoices` — proper enums in Django 5.
- ORM lookups, `Q`, `F`, annotations, `select_related` vs `prefetch_related`.
- `related_name`, `related_query_name`, when to set them.
- Composite indexes + `UniqueConstraint`.

**Mind-vault**:
- Two IDEAs in one session — when it works (shared domain, tight coupling) and when it doesn't.
- Parallel worktrees demo (optional, if cohort wants depth on the isolation contract).

**Outputs**: Two PRs merged. `tasker_django.projects` and `tasker_django.tasks` apps live. Admin shows projects with inline tasks and annotated counts. All tests pass.

---

### Session 4 — AI-assisted base template (PHASE 3 starts)

**Status**: 📋 Planned

**Goal**: Land the generic base template every later page extends. Demonstrates the `frontend-design` skill *and* Django's template inheritance. No domain content yet — just the chrome.

**IDEAs to capture**: one IDEA for `base.html` + navigation + footer + a working "design system" foundation (Bulma is the default per `CLAUDE.md` — confirm or override at /plan time).

**Activities**:
- Ideate the layout *with* the `frontend-design` skill — let it produce a few variants, students pick. Teaches AI-collaborative design judgement (not "use the first thing it suggests").
- Wire Bulma (CDN initially; build pipeline IDEA later if needed).
- Decide on the nav contract: where does "Login / Sign up" live? Where does a user's "Projects" link sit? Stub the links to `#` for now.
- Plan should include a `block content`, `block title`, `block extra_head`, `block extra_scripts` contract — the dial-in points every later template uses.
- Write a renders-without-crashing template test for `base.html` via a tiny placeholder view.

**Django**:
- Template inheritance: `{% extends %}`, `{% block %}` — closest cousin is Twig in Symfony; Laravel Blade is similar.
- `{% load static %}` and how that ties back to Session 1's nginx work.
- `{% url %}` reverse routing.
- Context processors (mention; don't implement — earned later).
- DRY templates without sacrificing readability.

**Mind-vault**:
- `frontend-design` skill — when to invoke it; how to evaluate its output critically.
- "Generative content" IDEAs — the artefact is partly authored by the AI; the IDEA's success criteria become "the output passes this rubric".

**Outputs**: PR merged. `base.html` lives in `tasker_django/templates/base.html`. A placeholder home view renders the empty chrome. Tests assert it doesn't 500.

---

### Session 5 — Auth UI: registration + login + password-change (PHASE 3 continued)

**Status**: 📋 Planned

**Goal**: Wire user-facing authentication — registration, login, logout, password change — using Django's built-in views + templates extending the Session-4 base.

**IDEAs to capture**: one IDEA for the four auth flows, all template-driven.

**Activities**:
- Plan the URL surface: `/accounts/login/`, `/accounts/logout/`, `/accounts/register/`, `/accounts/password-change/`. Whether to mount under `/accounts/` or `/auth/` — debate.
- `/work`: use `LoginView`, `LogoutView`, `PasswordChangeView` from `django.contrib.auth.views`; write a custom `RegisterView` (Django doesn't ship one).
- Template per view extending `base.html`. Form errors rendered with Bulma classes.
- Decision: `@login_required` everywhere by default or per-view? Debate, write a default, document.
- Tests: anonymous user can register → logs in automatically; logged-in user can change password and the new password works on the next login; logout actually logs out.

**Django**:
- Built-in auth views — Symfony's Security bundle requires bootstrap; Laravel Breeze/Jetstream are the rough parallel.
- `UserCreationForm` and how to customise it (we'll need to subclass since we have a custom User).
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` settings.
- CSRF behaviour: how the middleware works, what `{% csrf_token %}` injects, why AJAX needs the header.
- Message framework — `django.contrib.messages` for "you've registered!" toasts.

**Mind-vault**:
- The "use the framework's built-ins until they break" rule — applies to Django auth, Symfony security, every mature framework. Don't reach for django-allauth until you've outgrown built-ins.

**Outputs**: PR merged. Users can register, log in, log out, change passwords. Tests cover each flow. The nav from Session 4 now links to live URLs.

---

### Session 6 — Project list CRUD (PHASE 4 starts)

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

**Django**:
- Class-based views vs function-based — when each shines. (PHP world: closer to Symfony controllers than Laravel function-style routes.)
- `LoginRequiredMixin`, `UserPassesTestMixin`, `PermissionRequiredMixin`.
- `ModelForm` auto-generation; `fields = [...]` vs `exclude = [...]`.
- `get_queryset()` override pattern for ownership-scoped data.
- `get_success_url()` and `reverse_lazy`.
- Django messages on create/update/delete.

**Mind-vault**:
- Security-test-first habit: write the "user A can't access user B's data" assertion *before* the view exists. This is `superpowers:test-driven-development` applied to authz.
- Ownership-scoping as a project pattern worth `/compound`-ing to `docs/solutions/` once it solidifies.

**Outputs**: PR merged. Logged-in users see their projects, create/edit/delete them. Cross-user-access tests pass (= are red without the scoping).

---

### Session 7 — Project Kanban + Task CRUD (PHASE 4 continued)

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

**Django**:
- Template partials (`include`, custom inclusion tags) — Twig and Blade have direct parallels.
- View returning a *partial* (just a `<tr>` or `<div>`) vs a full page — Django doesn't care; the framework is HTTP-aware all the way down.
- Form processing in CBVs vs FBVs for HTMX-friendly responses.
- `django-htmx` package (or `django.contrib.htmx` — depending on what's current at session time).

**Mind-vault**:
- `django-frontend` skill applied — HTMX partial-response contract, Alpine.js state shape, Bulma component primitives.
- `mobile-ux-polish` skill if drag-and-drop lands — touch vs mouse drag discrimination.
- Two-IDEA session where the second depends on the first — when to ship as one PR vs two.

**Outputs**: PR(s) merged. Project detail page shows a working Kanban with inline task CRUD.

---

### Session 8 — Feature-rich Task detail page (PHASE 4 closes)

**Status**: 📋 Planned

**Goal**: A full task detail page that goes beyond CRUD — activity log, comments, attachments (optional), assignee changes, due-date reminders. Demonstrates Django signals, generic FKs, file uploads (if attachments land), and proper "feature" scope discipline.

**IDEAs to capture** (pick a coherent subset together — full list is over-ambitious for one session):
- Comments on a task (separate model, FK to task + author).
- Activity log (signal-driven, records assignee/status/priority changes).
- File attachments (FK to task, uses media routing from Session 1).
- "Due soon" indicator on the task list (today/this-week/overdue badges).

**Activities**:
- Ideate the *minimum viable* set with the cohort. Pin scope before plan.
- For activity log: Django signals (`post_save` on Task) — show why signals can be a debugging nightmare (run order, recursion, hidden side effects).
- For comments: a fresh app `tasker_django.comments` with a `Comment` model linked to `Task`. If we generalise to "comments on anything", introduce generic FKs — but only if the cohort wants that depth.
- For attachments: revisit Session 1's `/media/` route — *now* it goes live. `FileField` + `upload_to` lambdas + safety considerations.
- Tests per feature subset.

**Django**:
- Django signals — when they're great (decoupling), when they're a footgun (untraceable side effects).
- Generic relations (`contenttypes.GenericForeignKey`) — covered only if comments-on-anything is in scope.
- `FileField`, `ImageField`, `upload_to`, `MEDIA_ROOT`/`MEDIA_URL`.
- Storage backends (mention S3/MinIO as future options — don't implement).

**Mind-vault**:
- Scope-pinning discipline — Session 8 is the most over-scopable session in this roadmap. Use `/plan`'s open-questions section to *say no* to features.
- `/compound` value compounds: every Django pattern learned earlier collapses time on this session.

**Outputs**: PR(s) merged. Task detail page does materially more than Session 7's inline edit.

---

## Beyond Session 8 — backlog seeds

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

- After each session's `/wrap`, flip the session's `Status:` line.
- Append a one-line "what actually shipped" note linking the merged PRs.
- Update "Beyond Session 8" if any candidate IDEAs were captured but deferred.
- The `Outputs` line for each session becomes a permanent record once the session has run.

If a session unexpectedly grows or shrinks (a student question opens a tangent, a finding demands its own IDEA), update the roadmap **before** the next session — keeps expectations aligned across the cohort.

---

**Status legend**: 📋 planned · 🚧 in progress · ✅ shipped · ⚠️ deferred · ❌ rejected
