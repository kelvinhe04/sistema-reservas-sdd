"""Fixtures compartidas. Ver docs/testing.md."""
from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from src.app.config import Settings
from src.app.db import connect, init_db
from src.app.services import canchas as canchas_srv
from src.app.services import reservas as reservas_srv
from tests.helpers import ADMIN_KEY_PRUEBA, AHORA_POR_DEFECTO, MANANA


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
def settings(db_path) -> Settings:
    return replace(Settings(), admin_key=ADMIN_KEY_PRUEBA, db_path=str(db_path))


@pytest.fixture
def conn(settings):
    """Conexión para preparar datos y verificar la base directamente."""
    init_db(settings.db_path)
    c = connect(settings.db_path)
    yield c
    c.close()


@pytest.fixture
def app(settings, reloj):
    from src.app.main import create_app

    return create_app(settings=settings, reloj=reloj)


@pytest.fixture
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c


@pytest.fixture
def nueva_cancha(conn, reloj):
    """Crea canchas directamente con el servicio. Devuelve el id."""
    contador = {"n": 0}

    def _crear(nombre=None, deporte="fútbol", precio_hora=1500, activa=True) -> int:
        contador["n"] += 1
        c = canchas_srv.crear(conn, reloj.ahora(), nombre or f"Cancha {contador['n']}", deporte, precio_hora)
        if not activa:
            canchas_srv.desactivar(conn, c["id"])
        return c["id"]

    return _crear


@pytest.fixture
def cancha(nueva_cancha) -> int:
    return nueva_cancha()


@pytest.fixture
def reservar(conn, settings, reloj, cancha):
    """Crea una reserva con el servicio; por defecto, mañana a las 18:00 en `cancha`."""

    def _reservar(fecha=MANANA, hora="18:00", telefono="62001234", nombre="Ana Pérez", cancha_id=None):
        return reservas_srv.crear(conn, settings, reloj.ahora(), {
            "cancha_id": cancha_id or cancha, "fecha": fecha, "hora_inicio": hora,
            "nombre": nombre, "telefono": telefono,
        })

    return _reservar

