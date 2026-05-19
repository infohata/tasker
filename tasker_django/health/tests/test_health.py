from django.test import Client
from django.urls import reverse


def test_health_endpoint_returns_ok():
    client = Client()
    response = client.get(reverse("health:check"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_path():
    """Lock the public URL to /health/ — ops surface contract."""
    assert reverse("health:check") == "/health/"
