"""Reglas críticas al crear una reserva. Tareas T-06 y T-08."""
import pytest

pytestmark = [
    pytest.mark.regla_critica,
    pytest.mark.skip(reason="pendiente T-06/T-08: services/reservas.py"),
]


@pytest.mark.ac("AC-07")
def test_rechaza_franja_que_ya_empezo(db_path, reloj):
    """Dado el reloj en 10:00, cuando se reserva la franja de 10:00 de hoy,
    entonces `regla_negocio`; la de 11:00 se acepta."""


@pytest.mark.ac("AC-07")
def test_rechaza_fecha_pasada(db_path, reloj):
    """Cuando se reserva una franja de ayer, entonces `regla_negocio` (RN-06)."""


@pytest.mark.ac("AC-08")
def test_limite_de_30_dias(db_path, reloj):
    """Dado hoy 2026-11-20, a 30 días se acepta y a 31 días se rechaza (RN-07)."""


@pytest.mark.ac("AC-10")
def test_rechaza_cancha_desactivada(db_path, reloj):
    """Dada una cancha desactivada, cuando se reserva, entonces `regla_negocio` (RN-15)."""


@pytest.mark.ac("AC-11")
def test_cuarta_reserva_del_mismo_telefono(db_path, reloj):
    """Dado un teléfono con 3 reservas confirmadas futuras, la cuarta se rechaza;
    tras cancelar una, se acepta (RN-11)."""


@pytest.mark.ac("AC-11")
def test_reservas_pasadas_no_cuentan_para_el_limite(db_path, reloj):
    """Dado un teléfono con 3 reservas confirmadas cuya franja ya pasó,
    cuando reserva otra franja futura, entonces se acepta (RN-11: activa = confirmada y futura, #22)."""


def test_precio_se_copia_a_la_reserva(db_path, reloj):
    """Dada una reserva creada, cuando cambia el precio de la cancha,
    entonces la reserva conserva su precio (RN-20)."""
