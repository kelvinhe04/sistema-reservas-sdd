"""Escrituras con la base ocupada (#52): formato único de error, nunca 500 en texto plano."""
from dataclasses import replace

import pytest

from src.app.db import connect
from src.app.main import create_app
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.regla_critica]


@pytest.fixture
def client_ocupado(settings, reloj, conn, reservar):
    """App con `busy_timeout` corto y otra conexión que retiene el candado de escritura."""
    reserva = reservar()
    app = create_app(settings=replace(settings, busy_timeout_ms=200), reloj=reloj)
    otra = connect(settings.db_path)
    otra.execute("BEGIN IMMEDIATE")
    try:
        with TestClient(app) as c:
            yield c, reserva
    finally:
        otra.execute("ROLLBACK")
        otra.close()


def _es_error_base_ocupada(r):
    assert r.status_code == 503
    assert r.headers["content-type"].startswith("application/json")
    cuerpo = r.json()
    assert cuerpo["error"] == "base_ocupada" and cuerpo["campos"] == {}
    assert r.headers["retry-after"] == "1"


def test_cancelar_jugador_con_base_ocupada(client_ocupado):
    """Dada la base ocupada, cuando el jugador cancela, entonces 503 `base_ocupada` en el formato único."""
    client, reserva = client_ocupado
    r = client.post(f"/api/reservas/{reserva['codigo']}/cancelar", json={"telefono": reserva["telefono"]})
    _es_error_base_ocupada(r)


def test_cancelar_admin_con_base_ocupada(client_ocupado, admin_headers):
    """Dada la base ocupada, cuando el administrador cancela, entonces 503 `base_ocupada`."""
    client, reserva = client_ocupado
    r = client.post(f"/api/admin/reservas/{reserva['codigo']}/cancelar", headers=admin_headers)
    _es_error_base_ocupada(r)


def test_la_reserva_sigue_confirmada_tras_el_error(client_ocupado, conn):
    """Dado un 503 al cancelar, entonces la reserva sigue confirmada (no se pierde ni se corrompe)."""
    client, reserva = client_ocupado
    client.post(f"/api/reservas/{reserva['codigo']}/cancelar", json={"telefono": reserva["telefono"]})
    estado = conn.execute("SELECT estado FROM reservas WHERE codigo = ?", (reserva["codigo"],)).fetchone()[0]
    assert estado == "confirmada"
