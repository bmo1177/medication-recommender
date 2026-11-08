import pytest

from main import app as flask_app
from main import create_app


@pytest.fixture()
def client():
    # Disable form CSRF in tests for deterministic POSTs (API is exempt anyway);
    # production keeps CSRFProtect enabled.
    flask_app.config["WTF_CSRF_ENABLED"] = False
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def factory_client():
    fresh = create_app()
    fresh.config["WTF_CSRF_ENABLED"] = False
    with fresh.test_client() as c:
        yield c
