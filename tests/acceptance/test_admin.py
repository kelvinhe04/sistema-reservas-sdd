"""Aceptación: administración (AC-17 a AC-22). Tareas T-11 a T-15."""
from datetime import datetime

import pytest

from tests.helpers import MANANA, TZ

pytestmark = [pytest.mark.aceptacion]

ENDPOINTS_ADMIN = [
    ("POST", "/api/admin/login"),
    ("GET", "/api/admin/agenda?fecha=2026-11-21"),
    ("GET", "/api/admin/canchas"),
    ("POST", "/api/admin/canchas"),
    ("PUT", "/api/admin/canchas/1"),
    ("POST", "/api/admin/canchas/1/desactivar"),
    ("POST", "/api/admin/bloqueos"),
    ("DELETE", "/api/admin/bloqueos/1"),
    ("POST", "/api/admin/reservas/XXXXXXXX/cancelar"),
]


def _reservar(client, cancha_id, hora="18:00", telefono="62001234"):
    r = client.post("/api/reservas", json={
        "cancha_id": cancha_id, "fecha": MANANA, "hora_inicio": hora,
        "nombre": "Ana Pérez", "telefono": telefono,
    })
    assert r.status_code == 201, r.json()
    return r.json()


def _estado_publico(client, cancha_id, hora):
    franjas = client.get(f"/api/canchas/{cancha_id}/disponibilidad", params={"fecha": MANANA}).json()["franjas"]
    return next(f for f in franjas if f["hora_inicio"] == hora)["estado"]


@pytest.mark.ac("AC-17")
@pytest.mark.parametrize("metodo, ruta", ENDPOINTS_ADMIN)
@pytest.mark.parametrize("clave", [None, "incorrecta"])
def test_ac17_admin_sin_clave_denegado(client, cancha, metodo, ruta, clave):
    """Dado que no se envía la clave de administrador, o es incorrecta
    Cuando se accede a cualquier operación del panel
    Entonces responde 401 `no_autorizado`."""
    headers = {"X-Admin-Key": clave} if clave else {}
    r = client.request(metodo, ruta, headers=headers, json={})
    assert r.status_code == 401
    assert r.json()["error"] == "no_autorizado"


@pytest.mark.ac("AC-17")
def test_ac17_login_con_clave_correcta(client, admin_headers):
    r = client.post("/api/admin/login", headers=admin_headers)
    assert r.status_code == 200 and r.json() == {"ok": True}


@pytest.mark.ac("AC-18")
def test_ac18_agenda_del_dia(client, admin_headers, nueva_cancha):
    """Dado un día con reservas, bloqueos y franjas libres
    Cuando el administrador hace GET /api/admin/agenda?fecha=...
    Entonces ve, por cancha, cada franja con su estado y los datos de la reserva o del bloqueo."""
    c1, c2 = nueva_cancha("Cancha A"), nueva_cancha("Cancha B")
    reserva = _reservar(client, c1, "18:00")
    b = client.post("/api/admin/bloqueos", headers=admin_headers,
                    json={"cancha_id": c2, "fecha": MANANA, "hora_inicio": "10:00", "motivo": "Mantenimiento"})
    assert b.status_code == 201
    r = client.get("/api/admin/agenda", params={"fecha": MANANA}, headers=admin_headers)
    assert r.status_code == 200
    agenda = {c["nombre"]: {f["hora_inicio"]: f for f in c["franjas"]} for c in r.json()["canchas"]}
    assert set(agenda) == {"Cancha A", "Cancha B"}
    assert agenda["Cancha A"]["18:00"]["estado"] == "reservada"
    assert agenda["Cancha A"]["18:00"]["reserva"] == {
        "codigo": reserva["codigo"], "nombre": "Ana Pérez", "telefono": "62001234"}
    assert agenda["Cancha B"]["10:00"]["estado"] == "bloqueada"
    assert agenda["Cancha B"]["10:00"]["bloqueo"] == {"id": b.json()["id"], "motivo": "Mantenimiento"}
    assert agenda["Cancha A"]["08:00"]["estado"] == "libre"
    assert len(agenda["Cancha A"]) == 14


@pytest.mark.ac("AC-18")
def test_ac18_agenda_incluye_cancha_desactivada_con_reservas(client, admin_headers, nueva_cancha):
    """RN-16: la agenda muestra la cancha desactivada que aún tiene reservas ese día."""
    con_reserva, sin_reserva = nueva_cancha("Con reserva"), nueva_cancha("Sin reserva")
    _reservar(client, con_reserva)
    for cid in (con_reserva, sin_reserva):
        client.post(f"/api/admin/canchas/{cid}/desactivar", headers=admin_headers)
    canchas = client.get("/api/admin/agenda", params={"fecha": MANANA}, headers=admin_headers).json()["canchas"]
    assert [c["nombre"] for c in canchas] == ["Con reserva"]
    assert canchas[0]["activa"] is False


@pytest.mark.ac("AC-19")
def test_ac19_gestion_de_canchas(client, admin_headers):
    """Dado el panel de administración
    Cuando el administrador crea, edita o desactiva una cancha
    Entonces el cambio se refleja en GET /api/canchas
    y las reservas futuras confirmadas de la cancha desactivada no se borran."""
    r = client.post("/api/admin/canchas", headers=admin_headers,
                    json={"nombre": "Cancha 3", "deporte": "pádel", "precio_hora": 2000})
    assert r.status_code == 201
    cancha = r.json()
    assert cancha["activa"] is True
    assert [c["nombre"] for c in client.get("/api/canchas").json()] == ["Cancha 3"]

    r = client.put(f"/api/admin/canchas/{cancha['id']}", headers=admin_headers,
                   json={"nombre": "Pádel Central", "deporte": "pádel", "precio_hora": 2500})
    assert r.status_code == 200
    assert client.get("/api/canchas").json()[0] == {
        "id": cancha["id"], "nombre": "Pádel Central", "deporte": "pádel", "precio_hora": 2500}

    reserva = _reservar(client, cancha["id"])
    r = client.post(f"/api/admin/canchas/{cancha['id']}/desactivar", headers=admin_headers)
    assert r.status_code == 200 and r.json()["activa"] is False
    assert client.get("/api/canchas").json() == []
    assert client.get(f"/api/reservas/{reserva['codigo']}", params={"telefono": "62001234"}).json()["estado"] == "confirmada"
    todas = client.get("/api/admin/canchas", headers=admin_headers).json()
    assert [(c["nombre"], c["activa"]) for c in todas] == [("Pádel Central", False)]


@pytest.mark.ac("AC-19")
@pytest.mark.parametrize("cuerpo, campo", [
    ({"nombre": "", "deporte": "fútbol", "precio_hora": 1000}, "nombre"),
    ({"nombre": "X", "deporte": " ", "precio_hora": 1000}, "deporte"),
    ({"nombre": "X", "deporte": "fútbol", "precio_hora": -1}, "precio_hora"),
])
def test_ac19_valida_datos_de_cancha(client, admin_headers, cuerpo, campo):
    r = client.post("/api/admin/canchas", headers=admin_headers, json=cuerpo)
    assert r.status_code == 422 and campo in r.json()["campos"]


@pytest.mark.ac("AC-19")
def test_ac19_nombre_repetido_y_cancha_inexistente(client, admin_headers):
    datos = {"nombre": "Única", "deporte": "fútbol", "precio_hora": 1000}
    assert client.post("/api/admin/canchas", headers=admin_headers, json=datos).status_code == 201
    r = client.post("/api/admin/canchas", headers=admin_headers, json=datos)
    assert r.status_code == 409 and r.json()["error"] == "conflicto"
    assert client.put("/api/admin/canchas/999", headers=admin_headers, json=datos).status_code == 404
    assert client.post("/api/admin/canchas/999/desactivar", headers=admin_headers).status_code == 404


@pytest.mark.ac("AC-20")
def test_ac20_bloquear_y_desbloquear(client, admin_headers, cancha):
    """Dado una franja libre
    Cuando el administrador la bloquea
    Entonces el jugador la ve ocupada y no puede reservarla (409);
    al desbloquearla (DELETE, 204) vuelve a estar libre."""
    r = client.post("/api/admin/bloqueos", headers=admin_headers,
                    json={"cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00", "motivo": "Evento"})
    assert r.status_code == 201
    bloqueo = r.json()
    assert _estado_publico(client, cancha, "18:00") == "ocupada"
    intento = client.post("/api/reservas", json={"cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00",
                                                 "nombre": "Ana Pérez", "telefono": "62001234"})
    assert intento.status_code == 409
    # bloquear dos veces la misma franja también es conflicto
    otra = client.post("/api/admin/bloqueos", headers=admin_headers,
                       json={"cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00"})
    assert otra.status_code == 409

    assert client.delete(f"/api/admin/bloqueos/{bloqueo['id']}", headers=admin_headers).status_code == 204
    assert _estado_publico(client, cancha, "18:00") == "libre"
    assert client.delete(f"/api/admin/bloqueos/{bloqueo['id']}", headers=admin_headers).status_code == 404
    _reservar(client, cancha, "18:00")


@pytest.mark.ac("AC-20")
def test_ac20_bloqueo_en_franja_invalida_o_cancha_inexistente(client, admin_headers, cancha):
    r = client.post("/api/admin/bloqueos", headers=admin_headers,
                    json={"cancha_id": cancha, "fecha": MANANA, "hora_inicio": "22:00"})
    assert r.status_code == 422
    r = client.post("/api/admin/bloqueos", headers=admin_headers,
                    json={"cancha_id": 999, "fecha": MANANA, "hora_inicio": "10:00"})
    assert r.status_code == 404


@pytest.mark.conflicto
@pytest.mark.ac("AC-21")
def test_ac21_no_bloquea_franja_reservada(client, admin_headers, cancha):
    """Dado una franja con reserva confirmada
    Cuando el administrador intenta bloquearla
    Entonces responde 409 `conflicto`; tras cancelar la reserva, el bloqueo se acepta."""
    reserva = _reservar(client, cancha)
    cuerpo = {"cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00"}
    r = client.post("/api/admin/bloqueos", headers=admin_headers, json=cuerpo)
    assert r.status_code == 409 and r.json()["error"] == "conflicto"
    client.post(f"/api/admin/reservas/{reserva['codigo']}/cancelar", headers=admin_headers)
    assert client.post("/api/admin/bloqueos", headers=admin_headers, json=cuerpo).status_code == 201


@pytest.mark.ac("AC-22")
def test_ac22_admin_cancela_sin_limite(client, admin_headers, reloj, cancha):
    """Dado una reserva confirmada que empieza en menos de 2 horas
    Cuando el administrador la cancela
    Entonces responde 200 con estado `cancelada` y la franja se libera."""
    reserva = _reservar(client, cancha)
    reloj.fijar(datetime(2026, 11, 21, 17, 50, tzinfo=TZ))
    jugador = client.post(f"/api/reservas/{reserva['codigo']}/cancelar", json={"telefono": "62001234"})
    assert jugador.status_code == 422
    r = client.post(f"/api/admin/reservas/{reserva['codigo']}/cancelar", headers=admin_headers)
    assert r.status_code == 200 and r.json()["estado"] == "cancelada"
    assert _estado_publico(client, cancha, "18:00") == "libre"
    again = client.post(f"/api/admin/reservas/{reserva['codigo']}/cancelar", headers=admin_headers)
    assert again.status_code == 422
    assert client.post("/api/admin/reservas/ZZZZZZZZ/cancelar", headers=admin_headers).status_code == 404
