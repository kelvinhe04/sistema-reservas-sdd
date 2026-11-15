"""Aceptación: administración (AC-17 a AC-22). Tareas T-11 a T-15."""
import pytest

pytestmark = [
    pytest.mark.aceptacion,
    pytest.mark.skip(reason="pendiente T-11 a T-15: endpoints de administración"),
]

ENDPOINTS_ADMIN = [
    ("POST", "/api/admin/login"),
    ("GET", "/api/admin/agenda?fecha=2026-11-21"),
    ("GET", "/api/admin/canchas"),
    ("POST", "/api/admin/canchas"),
    ("POST", "/api/admin/bloqueos"),
    ("POST", "/api/admin/reservas/XXXXXXXX/cancelar"),
]


@pytest.mark.ac("AC-17")
@pytest.mark.parametrize("metodo, ruta", ENDPOINTS_ADMIN)
@pytest.mark.parametrize("clave", [None, "incorrecta"])
def test_ac17_admin_sin_clave_denegado(client, metodo, ruta, clave):
    """Dado que no se envía la clave de administrador, o es incorrecta
    Cuando se accede a cualquier operación del panel
    Entonces responde 401 `no_autorizado`."""


@pytest.mark.ac("AC-18")
def test_ac18_agenda_del_dia(client, admin_headers):
    """Dado un día con reservas, bloqueos y franjas libres
    Cuando el administrador hace GET /api/admin/agenda?fecha=...
    Entonces ve, por cancha, cada franja con su estado y los datos de la reserva o del bloqueo."""


@pytest.mark.ac("AC-19")
def test_ac19_gestion_de_canchas(client, admin_headers):
    """Dado el panel de administración
    Cuando el administrador crea, edita o desactiva una cancha
    Entonces el cambio se refleja en GET /api/canchas
    y las reservas futuras confirmadas de la cancha desactivada no se borran."""


@pytest.mark.ac("AC-20")
def test_ac20_bloquear_y_desbloquear(client, admin_headers):
    """Dado una franja libre
    Cuando el administrador la bloquea
    Entonces el jugador la ve ocupada y no puede reservarla (409);
    al desbloquearla (DELETE, 204) vuelve a estar libre."""


@pytest.mark.conflicto
@pytest.mark.ac("AC-21")
def test_ac21_no_bloquea_franja_reservada(client, admin_headers):
    """Dado una franja con reserva confirmada
    Cuando el administrador intenta bloquearla
    Entonces responde 409 `conflicto`; tras cancelar la reserva, el bloqueo se acepta."""


@pytest.mark.ac("AC-22")
def test_ac22_admin_cancela_sin_limite(client, admin_headers, reloj):
    """Dado una reserva confirmada que empieza en menos de 2 horas
    Cuando el administrador la cancela
    Entonces responde 200 con estado `cancelada` y la franja se libera."""
