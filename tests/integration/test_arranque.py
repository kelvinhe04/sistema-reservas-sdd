"""Arranque y bloqueos (menores de #69)."""
from dataclasses import replace

import pytest

from src.app.errors import NoEncontrado
from src.app.main import create_app
from src.app.services import bloqueos

pytestmark = [pytest.mark.regla_critica]


def test_create_app_falla_sin_admin_key(settings):
    """Dada una ADMIN_KEY vacía, entonces la aplicación no arranca (RN-19)."""
    with pytest.raises(RuntimeError, match="ADMIN_KEY"):
        create_app(settings=replace(settings, admin_key=""))


def test_eliminar_bloqueo_y_no_encontrado(conn, settings, reloj, cancha):
    """Quitar un bloqueo lo borra; quitarlo otra vez da no encontrado (RN-18)."""
    b = bloqueos.crear(conn, settings, reloj.ahora(), cancha, "2026-12-01", "10:00", "obra")
    bloqueos.eliminar(conn, b["id"])
    assert conn.execute("SELECT COUNT(*) FROM bloqueos").fetchone()[0] == 0
    with pytest.raises(NoEncontrado):
        bloqueos.eliminar(conn, b["id"])
