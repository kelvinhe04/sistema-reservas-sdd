"""Aceptación: canchas y disponibilidad (AC-01 a AC-03). Tareas T-03 y T-04."""
import pytest

from src.app.services import bloqueos
from tests.helpers import MANANA

pytestmark = [pytest.mark.aceptacion]


@pytest.mark.ac("AC-01")
def test_ac01_lista_solo_canchas_activas(client, nueva_cancha):
    """Dado que existen canchas activas e inactivas
    Cuando el jugador hace GET /api/canchas
    Entonces ve solo las activas, con nombre, deporte y precio_hora."""
    nueva_cancha("Cancha Norte", "fútbol", 1500)
    nueva_cancha("Pádel 1", "pádel", 2000)
    nueva_cancha("Vieja", "fútbol", 1000, activa=False)
    r = client.get("/api/canchas")
    assert r.status_code == 200
    datos = r.json()
    assert {c["nombre"] for c in datos} == {"Cancha Norte", "Pádel 1"}
    assert set(datos[0]) == {"id", "nombre", "deporte", "precio_hora"}


@pytest.mark.ac("AC-02")
def test_ac02_disponibilidad_de_08_a_21(client, cancha):
    """Dado una cancha activa y una fecha futura
    Cuando el jugador hace GET /api/canchas/{id}/disponibilidad?fecha=...
    Entonces recibe 14 franjas de 08:00 a 21:00, cada una libre u ocupada."""
    r = client.get(f"/api/canchas/{cancha}/disponibilidad", params={"fecha": MANANA})
    assert r.status_code == 200
    franjas = r.json()["franjas"]
    assert [f["hora_inicio"] for f in franjas][0::13] == ["08:00", "21:00"]
    assert len(franjas) == 14
    assert {f["estado"] for f in franjas} == {"libre"}


@pytest.mark.ac("AC-03")
def test_ac03_franja_reservada_o_bloqueada_aparece_ocupada(client, conn, settings, reloj, cancha, reservar):
    """Dado una franja con reserva confirmada y otra con bloqueo
    Cuando el jugador consulta la disponibilidad
    Entonces ambas aparecen como ocupadas."""
    reservar(hora="18:00")
    bloqueos.crear(conn, settings, reloj.ahora(), cancha, MANANA, "19:00", "Mantenimiento")
    franjas = client.get(f"/api/canchas/{cancha}/disponibilidad", params={"fecha": MANANA}).json()["franjas"]
    estado = {f["hora_inicio"]: f["estado"] for f in franjas}
    assert estado["18:00"] == estado["19:00"] == "ocupada"
    assert estado["20:00"] == "libre"


def test_disponibilidad_marca_franjas_pasadas(client, cancha):
    """Las franjas de hoy que ya empezaron vienen con pasada=true (para que la UI no las ofrezca)."""
    franjas = client.get(f"/api/canchas/{cancha}/disponibilidad", params={"fecha": "2026-11-20"}).json()["franjas"]
    pasada = {f["hora_inicio"]: f["pasada"] for f in franjas}
    assert pasada["10:00"] is True and pasada["11:00"] is False


def test_disponibilidad_de_cancha_inexistente_o_inactiva(client, nueva_cancha):
    inactiva = nueva_cancha(activa=False)
    for cid in (999, inactiva):
        r = client.get(f"/api/canchas/{cid}/disponibilidad", params={"fecha": MANANA})
        assert r.status_code == 404 and r.json()["error"] == "no_encontrado"


def test_disponibilidad_fecha_mal_formada(client, cancha):
    r = client.get(f"/api/canchas/{cancha}/disponibilidad", params={"fecha": "21/11/2026"})
    assert r.status_code == 422
    assert r.json()["error"] == "validacion" and "fecha" in r.json()["campos"]
