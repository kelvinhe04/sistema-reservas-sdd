"""Validaciones de usuario (RN-08, RN-09, RNF-02). Tarea T-05."""
import pytest

pytestmark = [
    pytest.mark.unitaria,
    pytest.mark.validacion,
    pytest.mark.skip(reason="pendiente T-05: schemas.py"),
]


@pytest.mark.ac("AC-09")
@pytest.mark.parametrize("nombre", ["", " ", "A", "x" * 61])
def test_rechaza_nombre_invalido(nombre):
    """Dado un nombre vacío, de 1 carácter o de más de 60, entonces es inválido en el campo `nombre`."""


@pytest.mark.ac("AC-09")
@pytest.mark.parametrize("nombre", ["Al", "Ana Pérez", "x" * 60])
def test_acepta_nombre_valido(nombre):
    """Dado un nombre de 2 a 60 caracteres, entonces es válido."""


@pytest.mark.ac("AC-09")
@pytest.mark.parametrize("telefono", ["", "123456", "6200abcd", "+50762001234", "6200 1234", "1" * 16])
def test_rechaza_telefono_invalido(telefono):
    """Dado un teléfono con letras, símbolos o fuera de 7-15 dígitos, entonces es inválido en `telefono`."""


@pytest.mark.ac("AC-09")
@pytest.mark.parametrize("telefono", ["1234567", "62001234", "1" * 15])
def test_acepta_telefono_valido(telefono):
    """Dado un teléfono de 7 a 15 dígitos, entonces es válido."""


@pytest.mark.parametrize("fecha", ["2026-13-01", "20-11-2026", "manana"])
def test_rechaza_fecha_mal_formada(fecha):
    """Dada una fecha que no es YYYY-MM-DD válida, entonces es inválida en `fecha`."""
