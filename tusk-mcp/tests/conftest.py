import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

TEST_DIR = Path(tempfile.mkdtemp())
os.environ["SQLITE_DATABASE_URI"] = f"sqlite:///{TEST_DIR / 'tusk-test.db'}"
os.environ["STORAGE_PATH"] = str(TEST_DIR / "uploads")
os.environ["SEED_DEMO"] = "true"
os.environ["PAYSTACK_SECRET_KEY"] = ""
os.environ["PUBLIC_BASE_URL"] = "http://testserver"
os.environ["GEOCODER_URL"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from tusk_mcp.app import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def login(client: TestClient, email: str, password: str = "tusk-demo-123") -> dict[str, str]:
    response = client.post("/api/v1/login", data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def tolu(client: TestClient) -> dict[str, str]:
    return login(client, "tolu@tuskapp.demo")
