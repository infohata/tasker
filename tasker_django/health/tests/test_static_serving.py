"""Verify nginx serves /static/ directly, not by proxying to Django.

Runs from inside the web container and hits the nginx service over the
Docker network, so it exercises the full real nginx hop. Django's
test Client would bypass nginx entirely and prove nothing here.

Requires `make collectstatic` to have run at least once.
"""
from urllib.request import urlopen


def test_nginx_serves_admin_static():
    with urlopen("http://nginx/static/admin/css/base.css", timeout=5) as resp:
        body = resp.read()

    assert resp.status == 200
    assert body, "expected non-empty static file body"


def test_nginx_returns_404_for_missing_media():
    """try_files $uri =404 — missing media must be 404, not 5xx."""
    from urllib.error import HTTPError

    try:
        urlopen("http://nginx/media/does-not-exist.png", timeout=5)
    except HTTPError as exc:
        assert exc.code == 404
    else:
        raise AssertionError("expected HTTP 404 for missing media file")
