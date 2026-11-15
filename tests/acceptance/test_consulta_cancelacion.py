"""Aceptación: consultar y cancelar (AC-12 a AC-16). Tareas T-09 y T-10."""
import pytest

pytestmark = [
    pytest.mark.aceptacion,
    pytest.mark.skip(reason="pendiente T-09/T-10: consulta y cancelación"),
]


@pytest.mark.ac("AC-12")
def test_ac12_consulta_con_codigo_y_telefono(client):
    """Dado una reserva existente
    Cuando el jugador consulta con el código y el teléfono correctos
    Entonces responde 200 con el detalle de su reserva."""


@pytest.mark.ac("AC-13")
@pytest.mark.parametrize("caso", ["telefono_distinto", "codigo_inexistente"])
def test_ac13_no_revela_datos_si_no_coinciden(client, caso):
    """Dado un código correcto con un teléfono distinto, o un código inexistente
    Cuando se consulta o se intenta cancelar
    Entonces responde 404 `no_encontrado`, con el mismo cuerpo en ambos casos."""


@pytest.mark.ac("AC-14")
def test_ac14_cancela_y_libera_franja(client, reloj):
    """Dado una reserva confirmada que empieza en más de 2 horas
    Cuando el jugador la cancela con código y teléfono
    Entonces responde 200 con estado `cancelada` y la franja vuelve a aparecer libre."""


@pytest.mark.ac("AC-15")
def test_ac15_rechaza_cancelar_a_menos_de_2h(client, reloj):
    """Dado una reserva que empieza en menos de 2 horas
    Cuando el jugador intenta cancelarla
    Entonces responde 422 `regla_negocio` indicando que ya pasó el límite."""


@pytest.mark.ac("AC-16")
def test_ac16_no_cancela_dos_veces(client):
    """Dado una reserva cancelada
    Cuando se intenta cancelar de nuevo
    Entonces responde 422 `regla_negocio`.
    (No existe operación de reactivar en api.md; ver issue #22.)"""
