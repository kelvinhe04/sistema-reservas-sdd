"""Ventana de cancelación del jugador (RN-13). Tarea T-10."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.app.services.reservas import puede_cancelar_jugador

pytestmark = [pytest.mark.unitaria]

AHORA = datetime(2026, 11, 20, 10, 0, tzinfo=ZoneInfo("America/Panama"))


@pytest.mark.ac("AC-14")
def test_puede_cancelar_a_2h_01min():
    """Dada una reserva que empieza en 2 h 01 min, entonces el jugador puede cancelar."""
    assert puede_cancelar_jugador(AHORA + timedelta(hours=2, minutes=1), AHORA, 2)


@pytest.mark.ac("AC-15")
def test_no_puede_cancelar_a_1h_59min():
    """Dada una reserva que empieza en 1 h 59 min, entonces el jugador no puede cancelar."""
    assert not puede_cancelar_jugador(AHORA + timedelta(hours=1, minutes=59), AHORA, 2)


@pytest.mark.ac("AC-14")
def test_puede_cancelar_a_exactamente_2h():
    """Dada una reserva que empieza en exactamente 2 h, entonces el jugador todavía puede cancelar
    (RN-13: 2 horas o más, decidido en #22)."""
    assert puede_cancelar_jugador(AHORA + timedelta(hours=2), AHORA, 2)


def test_no_puede_cancelar_una_franja_pasada():
    """Dada una reserva que ya empezó, entonces el jugador no puede cancelar."""
    assert not puede_cancelar_jugador(AHORA - timedelta(hours=1), AHORA, 2)
