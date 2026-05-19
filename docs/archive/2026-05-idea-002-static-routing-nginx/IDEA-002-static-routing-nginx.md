---
id: 002
title: Static & Media Serving via nginx
status: in-progress   # idea | in-progress | complete | superseded
priority: medium   # high | medium | low
supersedes: []       # list of IDEA ids this replaces, or []
superseded_by: null
depends_on: [001]    # IDEA-001 (skeleton) must be merged before this lands
related: []
created: 2026-05-19
completed: null
# Sprint-auto eligibility gates — both must be `true` with explicit reasoning
# before sprint-auto can run this idea unattended overnight.
# Default to `false` at capture; upgrade in `/plan` once the unknowns are nailed down.
auto_safe: false
auto_safe_reason: "Touches nginx vhost config and inter-container volume sharing — non-trivial judgment calls about volume vs bind-mount, /media/ stub placement, and collectstatic placement (image build vs runtime). Needs a /plan review pass."
sensitive_paths_cleared: false
sensitive_paths_cleared_reason: "nginx/default.conf and compose.yml volume topology are explicit sensitive-zone paths. Human review required on the infrastructure surface change."
---

# IDEA-002: Static & Media Serving via nginx

**Status**: 🚧 In Progress
**Priority**: Medium

**Problem** (or opportunity): IDEA-001 landed Daphne behind nginx with everything proxied to `web:8000`. `collectstatic` works and writes 127 files into `static_collected/`, but `GET /static/...` returns **404** because:

- Daphne does not auto-serve static (unlike Django's `runserver`).
- nginx has no `location /static/` block — every URL proxies to Django.
- No WhiteNoise.

The moment a developer visits `/admin/` (or any future UI that loads CSS/JS), the page renders unstyled. Static serving is also a hard prerequisite for any later IDEA that introduces an HTMX/Alpine/Bulma front-end.

**Proposal** (or idea): Configure nginx to serve `/static/` directly from the disk volume that `web` writes to via `collectstatic`. Pre-configure a `/media/` location stub so future user-uploaded content needs only a directory + setting, not a config refactor. Add a Makefile target so `collectstatic` is one keystroke.

- nginx `location /static/` → `alias /srv/static/;` (or `root` variant), with sane caching headers
- nginx `location /media/` stub → ready for activation when first upload feature lands
- Shared volume mapping `static_collected/` on the host to `web:/app/static_collected` AND `nginx:/srv/static` (read-only on nginx)
- Same pattern for `media/` (`media:/app/media` and `nginx:/srv/media:ro`)
- `make collectstatic` target
- One smoke test that asserts a known static file (e.g. `/static/admin/css/base.css`) returns 200 through the full nginx hop

**Why now**:
- Skeleton is fresh; the static-serving decision sets a convention every later UI IDEA inherits. Cheaper to bake in now than retrofit after three apps already assume a different layout.
- The first IDEA that touches admin or introduces a UI surface will trip on this. Front-loading is cheaper than reactive.
- nginx-based serving mirrors production. WhiteNoise would diverge dev from prod.

**Non-goals**:
- Media uploads themselves (model fields, upload views, storage backend) — separate IDEA when a domain feature actually needs it.
- WhiteNoise — explicitly rejected (prod-divergence cost).
- CDN integration (CloudFront, Cloudflare) — far-future, prod-only concern.
- `collectstatic` baked into the Docker image build (immutable-static pattern) — preserves dev hot-reload of admin templates if/when we customise them. Could be revisited for a prod-target image later.
- Static file compression / brotli — premature; revisit when bundle sizes warrant.
- `ManifestStaticFilesStorage` hashed filenames — premature; introduces cache-bust complexity before a real cache exists.

**Related**: depends on IDEA-001 (skeleton). No other IDEAs share context yet.
