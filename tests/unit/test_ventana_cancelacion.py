"""Ventana de cancelación del jugador (RN-13). Tarea T-10.

Cambio de requerimiento (ciclo 3): el límite pasó de 2 h a 6 h.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.app.services.reservas import puede_cancelar_jugador

pytestmark = [pytest.mark.unitaria]

AHORA = datetime(2026, 11, 20, 10, 0, tzinfo=ZoneInfo("America/Panama"))
LIMITE = 6


@pytest.mark.ac("AC-14")
def test_puede_cancelar_a_6h_01min():
    """Dada una reserva que empieza en 6 h 01 min, entonces el jugador puede cancelar."""
    assert puede_cancelar_jugador(AHORA + timedelta(hours=6, minutes=1), AHORA, LIMITE)


@pytest.mark.ac("AC-15")
def test_no_puede_cancelar_a_5h_59min():
    """Dada una reserva que empieza en 5 h 59 min, entonces el jugador no puede cancelar."""
    assert not puede_cancelar_jugador(AHORA + timedelta(hours=5, minutes=59), AHORA, LIMITE)


@pytest.mark.ac("AC-14")
def test_puede_cancelar_a_exactamente_6h():
    """Dada una reserva que empieza en exactamente 6 h, entonces el jugador todavía puede cancelar
    (RN-13: 6 horas o más; decidido en #22, ampliado por el cambio de requerimiento del ciclo 3)."""
    assert puede_cancelar_jugador(AHORA + timedelta(hours=6), AHORA, LIMITE)


def test_no_puede_cancelar_una_franja_pasada():
    """Dada una reserva que ya empezó, entonces el jugador no puede cancelar."""
    assert not puede_cancelar_jugador(AHORA - timedelta(hours=1), AHORA, LIMITE)
