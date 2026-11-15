"""Ventana de cancelación del jugador (RN-13). Tarea T-10."""
import pytest

pytestmark = [pytest.mark.unitaria, pytest.mark.skip(reason="pendiente T-10: services/reservas.py")]


@pytest.mark.ac("AC-14")
def test_puede_cancelar_a_2h_01min():
    """Dada una reserva que empieza en 2 h 01 min, entonces el jugador puede cancelar."""


@pytest.mark.ac("AC-15")
def test_no_puede_cancelar_a_1h_59min():
    """Dada una reserva que empieza en 1 h 59 min, entonces el jugador no puede cancelar."""


@pytest.mark.skip(reason="pendiente decisión del Product Lead (issue #22)")
def test_exactamente_2h():
    """Dada una reserva que empieza en exactamente 2 h: resultado por definir."""


def test_admin_no_tiene_ventana():
    """Dada una reserva que empieza en 10 min, entonces el administrador sí puede cancelar (AC-22)."""
