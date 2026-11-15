"""Fixtures compartidas. Ver docs/testing.md.

Las fixtures que dependen de la aplicación (`db_path`, `client`) se saltan
mientras `src/app` no exista (tarea T-01 del plan de implementación).
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

TZ = ZoneInfo("America/Panama")
ADMIN_KEY_PRUEBA = "clave-de-prueba"
AHORA_POR_DEFECTO = datetime(2026, 11, 20, 10, 0, tzinfo=TZ)


class RelojControlable:
    """Reloj inyectable en los servicios (architecture.md, 'Tiempo')."""

    def __init__(self, ahora: datetime = AHORA_POR_DEFECTO):
        self._ahora = ahora

    def ahora(self) -> datetime:
        return self._ahora

    def fijar(self, ahora: datetime) -> None:
        self._ahora = ahora

    def avanzar(self, **delta) -> None:
        self._ahora += timedelta(**delta)


@pytest.fixture
def reloj() -> RelojControlable:
    return RelojControlable()


@pytest.fixture
def admin_headers() -> dict:
    return {"X-Admin-Key": ADMIN_KEY_PRUEBA}


@pytest.fixture
def db_path(tmp_path):
    """Base SQLite en archivo temporal (no :memory:, ver AC-06)."""
    return tmp_path / "reservas.db"


@pytest.fixture
def client(db_path, reloj, monkeypatch):
    """TestClient de FastAPI contra una base temporal y el reloj controlable."""
    main = pytest.importorskip("src.app.main", reason="pendiente T-01: src/app no existe")
    from fastapi.testclient import TestClient

    monkeypatch.setenv("ADMIN_KEY", ADMIN_KEY_PRUEBA)
    monkeypatch.setenv("DB_PATH", str(db_path))
    # T-01 debe exponer una fábrica create_app(db_path=..., reloj=...).
    app = main.create_app(db_path=db_path, reloj=reloj)
    with TestClient(app) as c:
        yield c
