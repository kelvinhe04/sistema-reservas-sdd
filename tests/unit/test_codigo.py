"""Código de reserva (RN-10, D-05). Tarea T-06."""
import pytest

pytestmark = [pytest.mark.unitaria, pytest.mark.skip(reason="pendiente T-06: generación del código")]


@pytest.mark.ac("AC-04")
def test_codigo_tiene_8_caracteres_sin_ambiguos():
    """Entonces el código tiene 8 caracteres en mayúsculas y dígitos, sin 0/O ni 1/I/L."""


def test_codigos_no_se_repiten_en_muchas_generaciones():
    """Al generar 10 000 códigos, entonces no hay repetidos."""
