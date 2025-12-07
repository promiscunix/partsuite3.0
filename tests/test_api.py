from io import BytesIO
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.config import Settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


def setup_test_app(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path}/test.db", storage_path=tmp_path / "storage")
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), settings


def test_upload_and_list_invoices(tmp_path, monkeypatch):
    client, settings = setup_test_app(tmp_path)
    sample = Path("fixtures/sample_invoice.txt").read_bytes()

    response = client.post(
        "/upload",
        files={"files": ("invoice.pdf", BytesIO(sample), "application/pdf")},
    )
    assert response.status_code == 200
    payload = response.json()[0]
    assert payload["invoice"]["invoice_number"] == "12345"

    response = client.get("/invoices")
    assert response.status_code == 200
    assert len(response.json()) == 1
