"""Generación de franjas (RN-04, RN-05). Tarea T-03."""
from dataclasses import replace

import pytest

from src.app.config import Settings
from src.app.services.disponibilidad import es_franja_valida, franjas

pytestmark = [pytest.mark.unitaria]


@pytest.mark.ac("AC-02")
def test_genera_franjas_de_una_hora_de_08_a_21():
    """Dado el horario 08:00-22:00, cuando se generan las franjas,
    entonces son 14, en punto, de "08:00" a "21:00"."""
    lista = franjas(Settings())
    assert len(lista) == 14
    assert lista[0] == "08:00" and lista[-1] == "21:00"
    assert all(h.endswith(":00") for h in lista)


def test_franjas_salen_de_config():
    """Dado SLOT_MINUTES, OPEN_HOUR y CLOSE_HOUR en config, cuando cambian,
    entonces la lista de franjas cambia sin tocar el código de la regla."""
    s = replace(Settings(), open_hour=10, close_hour=14, slot_minutes=90)
    assert franjas(s) == ["10:00", "11:30"]


@pytest.mark.parametrize("hora", ["07:00", "22:00", "10:30", "9:00", "25:00"])
def test_rechaza_hora_que_no_es_franja_valida(hora):
    """Dada una hora fuera de horario o no en punto, entonces no es una franja válida."""
    assert not es_franja_valida(hora, Settings())
