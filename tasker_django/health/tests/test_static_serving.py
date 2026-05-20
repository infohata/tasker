"""Verify nginx serves /static/ directly, not by proxying to Django.

Runs from inside the web container and hits the nginx service over the
Docker network, so it exercises the full real nginx hop. Django's
test Client would bypass nginx entirely and prove nothing here.

The module-scoped autouse fixture runs `collectstatic` once so the
suite is self-contained on a clean checkout / CI run.
"""
import uuid
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest
from django.core.management import call_command


@pytest.fixture(scope="module", autouse=True)
def _collected_static():
    call_command("collectstatic", interactive=False, verbosity=0)


def test_nginx_serves_admin_static():
    with urlopen("http://nginx/static/admin/css/base.css", timeout=5) as resp:
        body = resp.read()
        cache_control = resp.headers.get("Cache-Control")

    assert resp.status == 200
    assert body, "expected non-empty static file body"
    # Lock in the cache policy so config changes that drop / weaken it
    # show up here instead of as silent prod cache behaviour drift.
    assert cache_control == "public, max-age=86400", cache_control


def test_nginx_returns_404_for_missing_media():
    """try_files $uri =404 — missing media must be 404, not 5xx."""
    # UUID under a test-reserved subdir so a real upload can never collide.
    url = f"http://nginx/media/__pytest__/{uuid.uuid4()}.png"

    try:
        resp = urlopen(url, timeout=5)
    except HTTPError as exc:
        try:
            assert exc.code == 404
            # Cache-Control must NOT be present on the 404 (achieved by
            # omitting `always` from the add_header directive). Asserting
            # absence here means a future change re-introducing `always`
            # — and thereby caching 404s for a day — fails this test.
            assert exc.headers.get("Cache-Control") is None, exc.headers.get(
                "Cache-Control"
            )
        finally:
            exc.close()
    else:
        resp.close()
        raise AssertionError("expected HTTP 404 for missing media file")
