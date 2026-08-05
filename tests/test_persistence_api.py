import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def load_app_module(db_path: Path):
    os.environ["CAPABILITIES_DB_PATH"] = str(db_path)
    if "app" in sys.modules:
        return importlib.reload(sys.modules["app"])
    import app  # type: ignore

    return app


def test_get_capabilities_returns_seed_data(tmp_path):
    db_path = tmp_path / "capabilities.db"
    app_module = load_app_module(db_path)

    with TestClient(app_module.app) as client:
        response = client.get("/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert "Cloud Architecture" in payload
    assert payload["Cloud Architecture"]["practice_area"] == "Technology"


def test_register_and_unregister_consultant(tmp_path):
    db_path = tmp_path / "capabilities.db"
    app_module = load_app_module(db_path)
    email = "new.consultant@slalom.com"

    with TestClient(app_module.app) as client:
        register_response = client.post(
            "/capabilities/Cloud%20Architecture/register",
            params={"email": email},
        )
        assert register_response.status_code == 200

        capabilities = client.get("/capabilities").json()
        assert email in capabilities["Cloud Architecture"]["consultants"]

        unregister_response = client.delete(
            "/capabilities/Cloud%20Architecture/unregister",
            params={"email": email},
        )
        assert unregister_response.status_code == 200

        capabilities_after = client.get("/capabilities").json()
        assert email not in capabilities_after["Cloud Architecture"]["consultants"]


def test_registration_persists_after_reload(tmp_path):
    db_path = tmp_path / "capabilities.db"
    email = "persistent.consultant@slalom.com"

    app_module = load_app_module(db_path)
    with TestClient(app_module.app) as client:
        response = client.post(
            "/capabilities/Data%20Analytics/register",
            params={"email": email},
        )
        assert response.status_code == 200

    reloaded_module = load_app_module(db_path)
    with TestClient(reloaded_module.app) as client:
        capabilities = client.get("/capabilities").json()

    assert email in capabilities["Data Analytics"]["consultants"]
