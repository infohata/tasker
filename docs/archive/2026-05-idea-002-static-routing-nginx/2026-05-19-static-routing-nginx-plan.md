---
stage: plan
slug: static-routing-nginx
created: 2026-05-19
source: ./IDEA-002-static-routing-nginx.md
status: shipped
project: tasker
---

# IDEA-002 — Static & Media Serving via nginx Plan

## Context

IDEA-001 brought up the full stack but routed every URL through Daphne. `collectstatic` works (127 admin files written to `static_collected/`) but `GET /static/admin/css/base.css` returns 404 because nginx has no `location /static/` block and Daphne doesn't auto-serve static. Any UI work — starting with `/admin/` — will visibly break until this lands.

This IDEA sets the static-serving convention every later UI IDEA inherits, so it's worth doing deliberately even though the scope is small. The non-goal list keeps it tight: no media uploads, no WhiteNoise, no CDN, no hashed-filename storage backend.

## Problem Frame

- `curl http://localhost/static/admin/css/base.css` → HTTP 404 (proxied to Daphne, which has no static serving wired up).
- nginx config currently has a single catch-all `location /` → `proxy_pass http://tasker_web` (see `nginx/default.conf` from IDEA-001).
- The `web` container produces static files via `collectstatic` into `/app/static_collected`; nginx has no view of that directory.
- No Makefile target for `collectstatic`; developers must remember the long `docker compose exec -T web python manage.py collectstatic --noinput` invocation.
- `media/` doesn't exist yet — but the first feature that needs uploads will trip on the same volume-topology question.

## Requirements Trace

- **R1.** `curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/css/base.css` returns `200` after `make collectstatic`. Source: IDEA-002 proposal.
- **R2.** nginx serves `/static/*` from disk, with HTTP `Cache-Control` and `Expires` headers set sanely (1 day default for now — premature to optimise further). Source: best-practice; IDEA-002 proposal.
- **R3.** nginx config exposes a `/media/*` location pointing at a `/srv/media/` mount, ready for the first upload IDEA — no model changes here. Source: IDEA-002 proposal (non-goal: media uploads themselves; in-scope: the routing stub).
- **R4.** `make collectstatic` runs `python manage.py collectstatic --noinput` inside `web`. Source: IDEA-002 proposal.
- **R5.** Plain Django requests (e.g. `/health/`, `/admin/`) still proxy to Daphne unchanged. Source: regression safeguard.
- **R6.** One smoke test asserts `/static/admin/css/base.css` returns 200 through the full nginx hop (NOT pytest-django's `Client`, since that bypasses nginx). Source: IDEA-002 proposal; verifies the full chain.
- **R7.** `CLAUDE.md` Commands section lists `make collectstatic` and the "Static URLs hit nginx directly, Django URLs proxy to Daphne" rule. Source: documentation hygiene.

## Scope Boundaries

**In scope:**

- `nginx/default.conf`: add `location /static/` (active) and `location /media/` (live but pointing at an empty `media/` dir until a feature populates it).
- `compose.yml`: bind-mount `./static_collected` and `./media` into both `web` and `nginx` (read-write on web, read-only on nginx).
- `Makefile`: add `collectstatic` target.
- `media/.gitkeep` so the directory exists in the repo (the contents stay gitignored).
- `.gitignore`: confirm `/media/*` is ignored except `.gitkeep` (touchup if needed).
- One smoke test under `tasker_django/health/tests/test_static_serving.py` that uses `requests`/`urllib` to hit `http://nginx/static/admin/css/base.css` from inside the `web` container (so it exercises the actual nginx hop, not Django's test client).
- `CLAUDE.md` updates.

**Out of scope (separate IDEAs):**

- Media uploads (model fields, upload views, storage backend) — separate IDEA.
- `ManifestStaticFilesStorage` (hashed filenames) — premature.
- gzip/brotli compression at the nginx layer — premature; revisit once we have a real bundle.
- CDN / cloud storage backends — far-future.
- collectstatic baked into the image build — preserves dev-time admin-template hot-reload by NOT doing this now.
- Custom admin theming — irrelevant.

**Explicit non-goals:**

- No WhiteNoise. Rejected (dev/prod divergence).
- No "fast-path" `try_files` shortcut that serves static from a different location than collectstatic writes to. One source of truth.
- No automatic collectstatic on `make up`. Manual or CI-triggered only.

## Context & Research

### Existing code and patterns to reuse

- `nginx/default.conf` (IDEA-001) — current single `location /` block. Add new locations BEFORE the catch-all so nginx matches `/static/` and `/media/` first.
- `tasker/settings.py` (IDEA-001) — `STATIC_URL`, `STATIC_ROOT = BASE_DIR / "static_collected"`. **Amendment (during /work):** flipped `STATIC_URL` from `"static/"` (relative) to `"/static/"` (leading slash) so browser-resolved admin asset URLs are absolute regardless of the current request path — otherwise the test client's `/static/...` and Django-rendered relative URLs disagree. Matches the path topology nginx will serve from.
- `compose.yml` (IDEA-001) — existing volume `- .:/app` on `web` already exposes `static_collected/`; we just need to also expose it to nginx.
- `Makefile` — existing pattern (`migrate`, `makemigrations`) is the template for the new `collectstatic` target.

### Institutional learnings

- Global `CLAUDE.md` § Preferences — "Production parity in local dev is important". nginx-served static fits; WhiteNoise wouldn't.
- `mind-vault/skills/deployment/SKILL.md` — production patterns assume nginx fronts everything; this IDEA lays the dev-time pattern that prod will inherit.
- `mind-vault/rules/RULE_git-safety.md` — IDEA-002 branch lives off `main`; PR is the HITL gate; commits flow normally.
- `mind-vault/rules/RULE_self-sweep-before-push.md` — only `.py` touch in this IDEA is the one new test file; pyflakes self-sweep before push.

### External references

- nginx [`alias` vs `root`](https://nginx.org/en/docs/http/ngx_http_core_module.html#alias) — `alias` is more explicit for path mapping; `root` prepends to the URI. Plan uses `alias` for `/static/` to keep the mapping clear.
- Django [staticfiles deployment notes](https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/) — nginx-fronted static is the canonical production pattern.

## Key Technical Decisions

- **Bind mounts, not named volumes.** Dev-time visibility wins over container-only state. `./static_collected:/srv/static:ro` on nginx lets a developer `ls static_collected/` and see exactly what nginx will serve. Production may switch to named volumes; that's a separate decision.
- **`alias`, not `root`, on the nginx locations.** `alias /srv/static/;` for `/static/` is unambiguous about path remapping; `root` would require a directory named `static/` *inside* `/srv/`, which is a footgun.
- **Smoke test runs from inside the `web` container, hitting `http://nginx/`.** Exercises the real nginx hop. Django's `Client` would bypass nginx and prove nothing about routing. Service name `nginx` is resolvable via Docker DNS.
- **`/media/` location is live, not commented out.** The location block points at `/srv/media/`, which is mounted from an (initially empty) `./media/` directory. Inactive in practice (no URL maps to media yet) but ready. Activating it later is zero-config.
- **No automatic `collectstatic` on `make up`.** Adds boot latency, masks failures, surprises developers. Keep it explicit.
- **`expires 1d;` + `add_header Cache-Control "public";`** on static. Cheap caching, easy to override later. No fingerprinting, so don't go aggressive (a `1y` Cache-Control here would bite when admin's static updates).
- **`autoindex off;`** explicitly on `/static/` and `/media/` — never let nginx directory-list these.

## Open Questions

- **Q1. Do we need `try_files $uri =404;` inside the `/static/` location, or is the default behaviour fine?**
  - **Default:** Add `try_files $uri =404;`. Explicit 404 on missing files is clearer than nginx's default "internal server error if file is unreadable" path; cheaper to debug.
  - **Trade-off:** One more line, zero runtime cost.
- **Q2. Should `make collectstatic` clear `static_collected/` first (so removed files don't linger)?**
  - **Default:** No. Django's `collectstatic --noinput` doesn't delete by default, but stale files in a dev `static_collected/` are harmless. A `make collectstatic-fresh` variant (uses `--clear`) could be added when a real need surfaces.
  - **Trade-off:** Slightly less hygienic dev state vs. simpler default behaviour. Defer.
- **Q3. Should the smoke test be in `tasker_django/health/tests/` or a new `tasker_django/_static/tests/` (or similar)?**
  - **Default:** `tasker_django/health/tests/test_static_serving.py`. The health app is the natural home for infra smoke tests at this scale; promoting to a dedicated app would be premature.
  - **Trade-off:** Mild misnomer (health app testing static) vs ceremony of a one-test app.

## Execution Sequence

Branch `feature/idea-002-static-routing-nginx` already exists off `origin/main`. RULE_self-sweep-before-push runs before each push. All commits below land on this branch.

1. **`docs(plan)`** — emit this plan + the IDEA frontmatter flip + ideas-index update. _(This commit.)_
2. **`feat(nginx)`** — `nginx/default.conf`: add `location /static/` (alias, expires, cache headers, `try_files`, `autoindex off`) and `location /media/` (parallel structure, same hardening) before the catch-all `location /`.
3. **`feat(compose)`** — `compose.yml`: bind-mount `./static_collected` and `./media` into both `web` (rw) and `nginx` (ro). Create empty `./media/.gitkeep`; touchup `.gitignore` to ignore `/media/*` except `.gitkeep`.
4. **`chore(make)`** — `Makefile`: add `collectstatic` target. Update `help` listing (auto-discovered, no edit needed).
5. **`test(static)`** — `tasker_django/health/tests/test_static_serving.py`: runs `requests.get("http://nginx/static/admin/css/base.css")` and asserts 200 + non-empty body. The test depends on `requests` being importable; check whether to add it to `requirements/dev.txt` (probably yes — useful test util) or use stdlib `urllib.request`. Default: `urllib.request` to avoid the dep.
6. **`docs(claude)`** — update `CLAUDE.md` Commands section: `make collectstatic`. Add a one-line "What gets served by whom" rule under Stack: nginx serves `/static/` and `/media/` directly; everything else proxies to Django.
7. **PR ready for review** — push, mark draft → ready, human merges.

### Key file shapes (sketch)

**`nginx/default.conf`** new block (inserted before `location /`):

```nginx
location /static/ {
    alias /srv/static/;
    autoindex off;
    # No `always` — keep Cache-Control off 404s so missing files
    # aren't cached by shared proxies.
    add_header Cache-Control "public, max-age=86400";
    try_files $uri =404;
}

location /media/ {
    alias /srv/media/;
    autoindex off;
    # User uploads are publicly accessible at this stage (no auth on
    # /media/). `private` is a caching directive — shared proxies
    # won't store the response — not an access-control mechanism.
    add_header Cache-Control "private, max-age=86400";
    try_files $uri =404;
}
```

> **Amendment (during /work + Copilot review cycles):** the original sketch used `expires 1d; add_header Cache-Control "public";`. Copilot flagged the duplicate Cache-Control headers + the broader caching of 404s implied by `always`. The shipped config consolidates into a single `Cache-Control` header per location, drops `expires`, and uses `private` for `/media/` so shared caches don't store per-user uploads.

**`compose.yml`** additions (services.web.volumes + services.nginx.volumes):

```yaml
services:
  web:
    volumes:
      - .:/app
      - ./static_collected:/app/static_collected   # already covered by .:/app but explicit
      - ./media:/app/media                          # ditto
  nginx:
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - ./static_collected:/srv/static:ro
      - ./media:/srv/media:ro
```

(The `.:/app` mount on `web` already exposes `static_collected/` and `media/` — the explicit lines above are redundant on `web`. Plan keeps it implicit on `web`; explicit only on `nginx`. Decision in step 3.)

**`Makefile`** addition:

```make
collectstatic: ## Run Django collectstatic into static_collected/
	$(DC) exec -T web python manage.py collectstatic --noinput
```

## Verification

After step 6, all of the following must be green:

- `make up` (stack already up, but confirms no compose syntax regression).
- `make collectstatic` — exit 0, "N static files copied" output.
- `curl -s -o /dev/null -w "%{http_code}\n" http://localhost/static/admin/css/base.css` → `200`.
- `curl -s -o /dev/null -w "%{http_code}\n" http://localhost/media/does-not-exist.png` → `404` (not 502; not 500; confirms `try_files $uri =404`).
- `curl -s http://localhost/health/` → `{"status": "ok"}` (regression check — Django routes still work).
- `make test` — both IDEA-001 smoke tests + the new static-serving test pass.
- `make self-sweep` — clean.
- `git log --oneline feature/idea-002-static-routing-nginx ^main` shows the 6-step commit sequence.

## Architect Review

Skipping — scope is small (1 nginx config block + 1 compose mount + 1 Makefile target + 1 test). Open Questions Q1–Q3 are operational defaults, not architectural forks. Will invoke `AGENT_architect` if Q1–Q3 outcomes change during `/work` or scope grows.

---

**Status:** shipped — Q1–Q3 defaults accepted; six work commits landed on `feature/idea-002-static-routing-nginx`; verification green; PR #2 open for review.
