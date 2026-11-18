"""Aceptación: consultar y cancelar (AC-12 a AC-16). Tareas T-09 y T-10."""
from datetime import datetime

import pytest

from tests.helpers import MANANA, TZ

pytestmark = [pytest.mark.aceptacion]


@pytest.fixture
def reserva(client, cancha):
    r = client.post("/api/reservas", json={
        "cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00",
        "nombre": "Ana Pérez", "telefono": "62001234",
    })
    assert r.status_code == 201
    return r.json()


@pytest.mark.ac("AC-12")
def test_ac12_consulta_con_codigo_y_telefono(client, reserva):
    """Dado una reserva existente
    Cuando el jugador consulta con el código y el teléfono correctos
    Entonces responde 200 con el detalle de su reserva."""
    r = client.get(f"/api/reservas/{reserva['codigo']}", params={"telefono": "62001234"})
    assert r.status_code == 200
    assert r.json() == reserva
    # el código se acepta también en minúsculas
    assert client.get(f"/api/reservas/{reserva['codigo'].lower()}", params={"telefono": "62001234"}).status_code == 200


@pytest.mark.ac("AC-13")
@pytest.mark.parametrize("caso", ["telefono_distinto", "codigo_inexistente"])
def test_ac13_no_revela_datos_si_no_coinciden(client, reserva, caso):
    """Dado un código correcto con un teléfono distinto, o un código inexistente
    Cuando se consulta o se intenta cancelar
    Entonces responde 404 `no_encontrado`, con el mismo cuerpo en ambos casos."""
    codigo, tel = (reserva["codigo"], "65559999") if caso == "telefono_distinto" else ("ZZZZZZZZ", "62001234")
    consulta = client.get(f"/api/reservas/{codigo}", params={"telefono": tel})
    cancelar = client.post(f"/api/reservas/{codigo}/cancelar", json={"telefono": tel})
    esperado = {"error": "no_encontrado", "mensaje": "No se encontró la reserva", "campos": {}}
    assert consulta.status_code == cancelar.status_code == 404
    assert consulta.json() == cancelar.json() == esperado


@pytest.mark.ac("AC-14")
def test_ac14_cancela_y_libera_franja(client, reserva, cancha):
    """Dado una reserva confirmada que empieza en 6 horas o más
    Cuando el jugador la cancela con código y teléfono
    Entonces responde 200 con estado `cancelada` y la franja vuelve a aparecer libre."""
    r = client.post(f"/api/reservas/{reserva['codigo']}/cancelar", json={"telefono": "62001234"})
    assert r.status_code == 200
    assert r.json()["estado"] == "cancelada"
    franjas = client.get(f"/api/canchas/{cancha}/disponibilidad", params={"fecha": MANANA}).json()["franjas"]
    assert next(f for f in franjas if f["hora_inicio"] == "18:00")["estado"] == "libre"


@pytest.mark.ac("AC-14")
def test_ac14_exactamente_6h_se_puede_cancelar(client, reserva, reloj):
    """Cambio de requerimiento (ciclo 3): la reserva es a las 18:00; a las 12:00 faltan 6 h."""
    reloj.fijar(datetime(2026, 11, 21, 12, 0, tzinfo=TZ))
    r = client.post(f"/api/reservas/{reserva['codigo']}/cancelar", json={"telefono": "62001234"})
    assert r.status_code == 200


@pytest.mark.ac("AC-15")
def test_ac15_rechaza_cancelar_a_menos_de_6h(client, reserva, reloj):
    """Dado una reserva que empieza en menos de 6 horas
    Cuando el jugador intenta cancelarla
    Entonces responde 422 `regla_negocio` indicando que ya pasó el límite."""
    reloj.fijar(datetime(2026, 11, 21, 12, 1, tzinfo=TZ))  # faltan 5 h 59 min
    r = client.post(f"/api/reservas/{reserva['codigo']}/cancelar", json={"telefono": "62001234"})
    assert r.status_code == 422
    assert r.json()["error"] == "regla_negocio"
    assert "límite" in r.json()["mensaje"]


@pytest.mark.ac("AC-16")
def test_ac16_no_cancela_dos_veces(client, reserva):
    """Dado una reserva cancelada
    Cuando se intenta cancelar de nuevo
    Entonces responde 422 `regla_negocio` y la reserva sigue `cancelada`.
    (No existe operación de reactivar: RN-12, api.md.)"""
    url = f"/api/reservas/{reserva['codigo']}/cancelar"
    assert client.post(url, json={"telefono": "62001234"}).status_code == 200
    r = client.post(url, json={"telefono": "62001234"})
    assert r.status_code == 422 and r.json()["error"] == "regla_negocio"
    estado = client.get(f"/api/reservas/{reserva['codigo']}", params={"telefono": "62001234"}).json()["estado"]
    assert estado == "cancelada"
