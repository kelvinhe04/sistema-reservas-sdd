"""Reglas críticas de consulta y cancelación (RN-12, RN-13, RN-14). Tareas T-09 y T-10."""
import pytest

pytestmark = [
    pytest.mark.regla_critica,
    pytest.mark.skip(reason="pendiente T-09/T-10: services/reservas.py"),
]


@pytest.mark.ac("AC-13")
def test_telefono_distinto_es_no_encontrado(db_path, reloj):
    """Dado un código correcto con otro teléfono, entonces `no_encontrado`,
    igual que un código inexistente."""


@pytest.mark.ac("AC-14")
def test_cancelar_libera_franja(db_path, reloj):
    """Dada una reserva cancelada, entonces la disponibilidad muestra la franja libre (RN-03)."""


@pytest.mark.ac("AC-16")
def test_cancelada_no_se_cancela_otra_vez(db_path, reloj):
    """Dada una reserva cancelada, cuando se cancela otra vez, entonces `regla_negocio`
    y `cancelada_en` no cambia (RN-12)."""
