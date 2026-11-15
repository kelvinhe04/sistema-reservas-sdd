"""Generación de franjas (RN-04, RN-05). Tarea T-03."""
import pytest

pytestmark = [pytest.mark.unitaria, pytest.mark.skip(reason="pendiente T-03: services/disponibilidad.py")]


@pytest.mark.ac("AC-02")
def test_genera_franjas_de_una_hora_de_08_a_21():
    """Dado el horario 08:00-22:00, cuando se generan las franjas,
    entonces son 14, en punto, de "08:00" a "21:00"."""


def test_franjas_salen_de_config():
    """Dado SLOT_MINUTES, OPEN_HOUR y CLOSE_HOUR en config, cuando cambian,
    entonces la lista de franjas cambia sin tocar el código de la regla."""


@pytest.mark.parametrize("hora", ["07:00", "22:00", "10:30", "9:00", "25:00"])
def test_rechaza_hora_que_no_es_franja_valida(hora):
    """Dada una hora fuera de horario o no en punto, entonces no es una franja válida."""
