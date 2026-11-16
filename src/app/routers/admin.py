"""Endpoints del administrador (api.md, RF-07 a RF-11). Todos exigen X-Admin-Key."""
import hmac
from datetime import datetime

from fastapi import APIRouter, Depends, Header, Query, Response

from ..config import Settings
from ..errors import NoAutorizado, Validacion
from ..schemas import BloqueoEntrada, CanchaEntrada, validar_fecha
from ..services import bloqueos, canchas, disponibilidad, reservas
from .deps import get_ahora, get_conn, get_settings


def exigir_admin(
    x_admin_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """RN-19, RNF-07: compara la clave en tiempo constante."""
    if not x_admin_key or not hmac.compare_digest(
        x_admin_key.encode("utf-8"), settings.admin_key.encode("utf-8")
    ):
        raise NoAutorizado("Clave de administrador incorrecta o ausente")


router = APIRouter(prefix="/api/admin", dependencies=[Depends(exigir_admin)])


@router.post("/login")
def login():
    return {"ok": True}


@router.get("/agenda")
def ver_agenda(fecha: str = Query(...), conn=Depends(get_conn), settings: Settings = Depends(get_settings)):
    try:
        fecha = validar_fecha(fecha)
    except ValueError as e:
        raise Validacion("Datos inválidos", {"fecha": str(e)}) from None
    return disponibilidad.agenda(conn, settings, fecha)


@router.get("/canchas")
def listar_canchas(conn=Depends(get_conn)):
    return canchas.listar_todas(conn)


@router.post("/canchas", status_code=201)
def crear_cancha(entrada: CanchaEntrada, conn=Depends(get_conn), ahora: datetime = Depends(get_ahora)):
    return canchas.crear(conn, ahora, entrada.nombre, entrada.deporte, entrada.precio_hora)


@router.put("/canchas/{cancha_id}")
def editar_cancha(cancha_id: int, entrada: CanchaEntrada, conn=Depends(get_conn)):
    return canchas.editar(conn, cancha_id, entrada.nombre, entrada.deporte, entrada.precio_hora)


@router.post("/canchas/{cancha_id}/desactivar")
def desactivar_cancha(cancha_id: int, conn=Depends(get_conn)):
    return canchas.desactivar(conn, cancha_id)


@router.post("/bloqueos", status_code=201)
def crear_bloqueo(
    entrada: BloqueoEntrada,
    conn=Depends(get_conn),
    settings: Settings = Depends(get_settings),
    ahora: datetime = Depends(get_ahora),
):
    return bloqueos.crear(conn, settings, ahora, entrada.cancha_id, entrada.fecha,
                          entrada.hora_inicio, entrada.motivo)


@router.delete("/bloqueos/{bloqueo_id}", status_code=204)
def eliminar_bloqueo(bloqueo_id: int, conn=Depends(get_conn)):
    bloqueos.eliminar(conn, bloqueo_id)
    return Response(status_code=204)


@router.post("/reservas/{codigo}/cancelar")
def cancelar_reserva(codigo: str, conn=Depends(get_conn), ahora: datetime = Depends(get_ahora)):
    return reservas.cancelar_admin(conn, ahora, codigo.strip().upper())
