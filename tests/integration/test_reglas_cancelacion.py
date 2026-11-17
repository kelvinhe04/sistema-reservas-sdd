"""Reglas críticas de consulta y cancelación (RN-12, RN-13, RN-14). Tareas T-09 y T-10."""
from datetime import datetime

import pytest

from src.app.errors import NoEncontrado, ReglaNegocio
from src.app.services import disponibilidad, reservas
from tests.helpers import MANANA, TZ

pytestmark = [pytest.mark.regla_critica]


@pytest.mark.ac("AC-13")
def test_telefono_distinto_es_no_encontrado(conn, settings, reloj, reservar):
    """Dado un código correcto con otro teléfono, entonces `no_encontrado`,
    igual que un código inexistente."""
    r = reservar()
    with pytest.raises(NoEncontrado) as otro_tel:
        reservas.consultar(conn, r["codigo"], "65559999")
    with pytest.raises(NoEncontrado) as inexistente:
        reservas.consultar(conn, "ZZZZZZZZ", "62001234")
    assert otro_tel.value.cuerpo() == inexistente.value.cuerpo()
    with pytest.raises(NoEncontrado):
        reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], "65559999")


@pytest.mark.ac("AC-14")
def test_cancelar_libera_franja(conn, settings, reloj, reservar, cancha):
    """Dada una reserva cancelada, entonces la disponibilidad muestra la franja libre (RN-03)."""
    r = reservar()
    reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], r["telefono"])
    franjas = disponibilidad.disponibilidad(conn, settings, reloj.ahora(), cancha, MANANA)["franjas"]
    assert next(f for f in franjas if f["hora_inicio"] == "18:00")["estado"] == "libre"


@pytest.mark.ac("AC-15")
def test_rechaza_cancelar_a_menos_de_6h(conn, settings, reloj, reservar):
    r = reservar()
    reloj.fijar(datetime(2026, 11, 21, 16, 30, tzinfo=TZ))  # faltan 1 h 30 min
    with pytest.raises(ReglaNegocio):
        reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], r["telefono"])


@pytest.mark.ac("AC-14")
def test_acepta_cancelar_a_exactamente_6h(conn, settings, reloj, reservar):
    """Cambio de requerimiento (ciclo 3): el límite es de 6 h; la reserva es a las 18:00."""
    r = reservar()
    reloj.fijar(datetime(2026, 11, 21, 12, 0, tzinfo=TZ))
    assert reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], r["telefono"])["estado"] == "cancelada"


@pytest.mark.ac("AC-16")
def test_cancelada_no_se_cancela_otra_vez(conn, settings, reloj, reservar):
    """Dada una reserva cancelada, cuando se cancela otra vez, entonces `regla_negocio`
    y `cancelada_en` no cambia (RN-12)."""
    r = reservar()
    reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], r["telefono"])
    antes = conn.execute("SELECT cancelada_en FROM reservas WHERE codigo = ?", (r["codigo"],)).fetchone()[0]
    reloj.avanzar(minutes=5)
    with pytest.raises(ReglaNegocio):
        reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], r["telefono"])
    with pytest.raises(ReglaNegocio):
        reservas.cancelar_admin(conn, reloj.ahora(), r["codigo"])
    despues = conn.execute("SELECT cancelada_en FROM reservas WHERE codigo = ?", (r["codigo"],)).fetchone()[0]
    assert antes == despues


@pytest.mark.ac("AC-22")
def test_admin_cancela_sin_ventana(conn, settings, reloj, reservar):
    r = reservar()
    reloj.fijar(datetime(2026, 11, 21, 17, 50, tzinfo=TZ))  # faltan 10 min
    assert reservas.cancelar_admin(conn, reloj.ahora(), r["codigo"])["estado"] == "cancelada"
    fila = conn.execute("SELECT cancelada_por FROM reservas WHERE codigo = ?", (r["codigo"],)).fetchone()
    assert fila[0] == "admin"
