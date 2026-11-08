import pytest

from main import app as flask_app
from main import create_app


@pytest.fixture()
def client():
    # Use the singletons built at import (fast); CSRF disabled by default here
    # (enabling CSRF is covered in its own commit — tests stay deterministic).
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def factory_client():
    fresh = create_app()
    with fresh.test_client() as c:
        yield c
