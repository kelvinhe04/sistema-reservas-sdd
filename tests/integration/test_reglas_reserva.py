"""Reglas críticas al crear una reserva. Tareas T-06 y T-08."""
from datetime import date, timedelta

import pytest

from src.app.errors import Conflicto, NoEncontrado, ReglaNegocio, Validacion
from src.app.services import canchas, reservas
from tests.helpers import AHORA_POR_DEFECTO, MANANA

pytestmark = [pytest.mark.regla_critica]

HOY = AHORA_POR_DEFECTO.date().isoformat()


def _dias(n: int) -> str:
    return (date.fromisoformat(HOY) + timedelta(days=n)).isoformat()


@pytest.mark.ac("AC-07")
def test_rechaza_franja_que_ya_empezo(reservar):
    """Dado el reloj en 10:00, cuando se reserva la franja de 10:00 de hoy,
    entonces `regla_negocio`; la de 11:00 se acepta."""
    with pytest.raises(ReglaNegocio):
        reservar(fecha=HOY, hora="10:00")
    assert reservar(fecha=HOY, hora="11:00")["estado"] == "confirmada"


@pytest.mark.ac("AC-07")
def test_rechaza_fecha_pasada(reservar):
    """Cuando se reserva una franja de ayer, entonces `regla_negocio` (RN-06)."""
    with pytest.raises(ReglaNegocio):
        reservar(fecha=_dias(-1))


@pytest.mark.ac("AC-08")
def test_limite_de_30_dias(reservar):
    """Dado hoy 2026-11-20, a 30 días se acepta y a 31 días se rechaza (RN-07)."""
    assert reservar(fecha=_dias(30))["estado"] == "confirmada"
    with pytest.raises(ReglaNegocio):
        reservar(fecha=_dias(31))


@pytest.mark.ac("AC-10")
def test_rechaza_cancha_desactivada(nueva_cancha, reservar):
    """Dada una cancha desactivada, cuando se reserva, entonces `regla_negocio` (RN-15)."""
    inactiva = nueva_cancha(activa=False)
    with pytest.raises(ReglaNegocio):
        reservar(cancha_id=inactiva)


def test_cancha_inexistente_es_no_encontrado(reservar):
    with pytest.raises(NoEncontrado):
        reservar(cancha_id=999)


@pytest.mark.parametrize("hora", ["07:00", "22:00", "18:30"])
def test_rechaza_hora_fuera_de_franja(reservar, hora):
    """RN-04, RN-05: solo franjas en punto dentro del horario."""
    with pytest.raises(ReglaNegocio):
        reservar(hora=hora)


@pytest.mark.ac("AC-09")
def test_servicio_valida_los_datos(reservar):
    with pytest.raises(Validacion) as e:
        reservar(nombre="A", telefono="abc")
    assert set(e.value.campos) == {"nombre", "telefono"}


@pytest.mark.ac("AC-11")
def test_cuarta_reserva_del_mismo_telefono(conn, settings, reloj, reservar):
    """Dado un teléfono con 3 reservas confirmadas futuras, la cuarta se rechaza;
    tras cancelar una, se acepta (RN-11)."""
    hechas = [reservar(hora=h) for h in ("15:00", "16:00", "17:00")]
    with pytest.raises(ReglaNegocio):
        reservar(hora="18:00")
    reservas.cancelar_jugador(conn, settings, reloj.ahora(), hechas[0]["codigo"], "62001234")
    assert reservar(hora="18:00")["estado"] == "confirmada"


@pytest.mark.ac("AC-11")
def test_reservas_pasadas_no_cuentan_para_el_limite(reservar, reloj):
    """Dado un teléfono con 3 reservas confirmadas cuya franja ya pasó,
    cuando reserva otra franja futura, entonces se acepta (RN-11: activa = confirmada y futura, #22)."""
    for h in ("11:00", "12:00", "13:00"):
        reservar(fecha=HOY, hora=h)
    reloj.avanzar(hours=5)  # 15:00: las tres ya empezaron
    assert reservar(fecha=MANANA, hora="18:00")["estado"] == "confirmada"


def test_precio_se_copia_a_la_reserva(conn, reservar, cancha):
    """Dada una reserva creada, cuando cambia el precio de la cancha,
    entonces la reserva conserva su precio (RN-20)."""
    r = reservar()
    canchas.editar(conn, cancha, "Cancha 1", "fútbol", 9900)
    assert reservas.consultar_por_codigo(conn, r["codigo"])["precio_hora"] == 1500


def test_dos_canchas_misma_hora_no_es_conflicto(nueva_cancha, reservar):
    otra = nueva_cancha()
    reservar()
    assert reservar(cancha_id=otra, telefono="65559999")["estado"] == "confirmada"


def test_conflicto_no_consume_cupo_del_telefono(reservar):
    reservar()
    with pytest.raises(Conflicto):
        reservar(telefono="65559999")
    assert reservar(hora="19:00", telefono="65559999")["estado"] == "confirmada"
