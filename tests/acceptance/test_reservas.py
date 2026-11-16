"""Aceptación: crear reserva (AC-04 a AC-11). Tareas T-05 a T-08.

AC-05 y AC-06 son las pruebas obligatorias de no doble reserva.
"""
import re
import threading

import pytest
from fastapi.testclient import TestClient

from src.app.services import canchas
from tests.helpers import MANANA, contar_confirmadas

pytestmark = [pytest.mark.aceptacion]


def _cuerpo(cancha_id, **cambios):
    base = {"cancha_id": cancha_id, "fecha": MANANA, "hora_inicio": "18:00",
            "nombre": "Ana Pérez", "telefono": "62001234"}
    return {**base, **cambios}


@pytest.mark.ac("AC-04")
def test_ac04_reserva_confirmada_con_codigo(client, cancha):
    """Dado una franja libre y datos válidos
    Cuando el jugador hace POST /api/reservas
    Entonces responde 201 con estado `confirmada` y un código de 8 caracteres,
    y la franja pasa a ocupada en la disponibilidad."""
    r = client.post("/api/reservas", json=_cuerpo(cancha))
    assert r.status_code == 201
    datos = r.json()
    assert datos["estado"] == "confirmada"
    assert re.fullmatch(r"[A-Z2-9]{8}", datos["codigo"])
    assert datos["precio_hora"] == 1500
    franjas = client.get(f"/api/canchas/{cancha}/disponibilidad", params={"fecha": MANANA}).json()["franjas"]
    assert next(f for f in franjas if f["hora_inicio"] == "18:00")["estado"] == "ocupada"


@pytest.mark.conflicto
@pytest.mark.ac("AC-05")
def test_ac05_rechaza_doble_reserva(client, conn, cancha):
    """Dado una franja ya reservada de una cancha
    Cuando otro jugador reserva la misma cancha, fecha y franja
    Entonces responde 409 con error `conflicto` y no se crea una segunda reserva."""
    assert client.post("/api/reservas", json=_cuerpo(cancha)).status_code == 201
    r = client.post("/api/reservas", json=_cuerpo(cancha, nombre="Luis Gómez", telefono="65559999"))
    assert r.status_code == 409
    assert r.json()["error"] == "conflicto"
    assert contar_confirmadas(conn, cancha, MANANA, "18:00") == 1


@pytest.mark.conflicto
@pytest.mark.ac("AC-06")
@pytest.mark.parametrize("repeticion", range(5))
def test_ac06_rechaza_doble_reserva_concurrente(app, conn, cancha, repeticion):
    """Dado una franja libre
    Cuando 10 solicitudes POST /api/reservas para esa franja llegan a la vez
    (un TestClient por hilo, sincronizados con Barrier)
    Entonces exactamente una responde 201, las demás 409 `conflicto`, ninguna 500,
    y queda una sola reserva confirmada."""
    n = 10
    barrera = threading.Barrier(n)
    codigos = [None] * n

    def enviar(i):
        with TestClient(app) as c:
            barrera.wait()
            r = c.post("/api/reservas", json=_cuerpo(cancha, nombre=f"Jugador {i}", telefono=f"6300{i:04d}"))
            codigos[i] = r.status_code

    hilos = [threading.Thread(target=enviar, args=(i,)) for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=30)
    assert sorted(codigos) == [201] + [409] * (n - 1)
    assert contar_confirmadas(conn, cancha, MANANA, "18:00") == 1


@pytest.mark.ac("AC-07")
@pytest.mark.parametrize("fecha, hora", [("2026-11-20", "10:00"), ("2026-11-20", "09:00"), ("2026-11-19", "18:00")])
def test_ac07_rechaza_franja_pasada_o_iniciada(client, cancha, fecha, hora):
    """Dado una franja que ya empezó o está en el pasado
    Cuando el jugador intenta reservarla
    Entonces responde 422 `regla_negocio`."""
    r = client.post("/api/reservas", json=_cuerpo(cancha, fecha=fecha, hora_inicio=hora))
    assert r.status_code == 422
    assert r.json()["error"] == "regla_negocio"


@pytest.mark.ac("AC-08")
def test_ac08_rechaza_mas_de_30_dias(client, cancha):
    """Dado una fecha a más de 30 días
    Cuando el jugador intenta reservarla
    Entonces responde 422 `regla_negocio`."""
    assert client.post("/api/reservas", json=_cuerpo(cancha, fecha="2026-12-20")).status_code == 201
    r = client.post("/api/reservas", json=_cuerpo(cancha, fecha="2026-12-21"))
    assert r.status_code == 422
    assert r.json()["error"] == "regla_negocio"


@pytest.mark.validacion
@pytest.mark.ac("AC-09")
@pytest.mark.parametrize(
    "cambio, campo",
    [
        ({"nombre": ""}, "nombre"),
        ({"nombre": "A"}, "nombre"),
        ({"telefono": "6200abcd"}, "telefono"),
        ({"telefono": "123"}, "telefono"),
    ],
)
def test_ac09_rechaza_datos_invalidos(client, cancha, cambio, campo):
    """Dado un nombre vacío o de menos de 2 caracteres, o un teléfono con letras o de longitud inválida
    Cuando el jugador intenta reservar
    Entonces responde 422 `validacion` y `campos` indica el campo inválido."""
    r = client.post("/api/reservas", json=_cuerpo(cancha, **cambio))
    assert r.status_code == 422
    datos = r.json()
    assert datos["error"] == "validacion"
    assert list(datos["campos"]) == [campo]
    assert datos["campos"][campo] and not datos["campos"][campo].startswith("Value error")


@pytest.mark.validacion
def test_campos_faltantes(client):
    r = client.post("/api/reservas", json={})
    assert r.status_code == 422
    assert set(r.json()["campos"]) == {"cancha_id", "fecha", "hora_inicio", "nombre", "telefono"}


@pytest.mark.ac("AC-10")
def test_ac10_rechaza_cancha_desactivada(client, conn, cancha):
    """Dado una cancha desactivada
    Cuando el jugador intenta reservarla
    Entonces responde 422 `regla_negocio`."""
    canchas.desactivar(conn, cancha)
    r = client.post("/api/reservas", json=_cuerpo(cancha))
    assert r.status_code == 422
    assert r.json()["error"] == "regla_negocio"


@pytest.mark.ac("AC-11")
def test_ac11_maximo_tres_activas_por_telefono(client, cancha):
    """Dado un teléfono con 3 reservas activas
    Cuando intenta crear una cuarta
    Entonces responde 422 `regla_negocio`."""
    for h in ("15:00", "16:00", "17:00"):
        assert client.post("/api/reservas", json=_cuerpo(cancha, hora_inicio=h)).status_code == 201
    r = client.post("/api/reservas", json=_cuerpo(cancha, hora_inicio="18:00"))
    assert r.status_code == 422
    assert r.json()["error"] == "regla_negocio"
