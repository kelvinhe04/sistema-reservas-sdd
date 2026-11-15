"""Aceptación: canchas y disponibilidad (AC-01 a AC-03). Tareas T-03 y T-04."""
import pytest

pytestmark = [
    pytest.mark.aceptacion,
    pytest.mark.skip(reason="pendiente T-04: GET /api/canchas y disponibilidad"),
]


@pytest.mark.ac("AC-01")
def test_ac01_lista_solo_canchas_activas(client):
    """Dado que existen canchas activas e inactivas
    Cuando el jugador hace GET /api/canchas
    Entonces ve solo las activas, con nombre, deporte y precio_hora."""


@pytest.mark.ac("AC-02")
def test_ac02_disponibilidad_de_08_a_21(client):
    """Dado una cancha activa y una fecha futura
    Cuando el jugador hace GET /api/canchas/{id}/disponibilidad?fecha=...
    Entonces recibe 14 franjas de 08:00 a 21:00, cada una libre u ocupada."""


@pytest.mark.ac("AC-03")
def test_ac03_franja_reservada_o_bloqueada_aparece_ocupada(client, admin_headers):
    """Dado una franja con reserva confirmada y otra con bloqueo
    Cuando el jugador consulta la disponibilidad
    Entonces ambas aparecen como ocupadas."""
