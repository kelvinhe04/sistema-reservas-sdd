"""Código de reserva (RN-10, D-05). Tarea T-06."""
import re

import pytest

from src.app.services.reservas import generar_codigo

pytestmark = [pytest.mark.unitaria]


@pytest.mark.ac("AC-04")
def test_codigo_tiene_8_caracteres_sin_ambiguos():
    """Entonces el código tiene 8 caracteres en mayúsculas y dígitos, sin 0/O ni 1/I/L."""
    for _ in range(200):
        codigo = generar_codigo()
        assert re.fullmatch(r"[A-Z2-9]{8}", codigo)
        assert not set(codigo) & set("01OIL")


def test_codigos_no_se_repiten_en_muchas_generaciones():
    """Al generar 10 000 códigos, entonces no hay repetidos."""
    codigos = {generar_codigo() for _ in range(10_000)}
    assert len(codigos) == 10_000
