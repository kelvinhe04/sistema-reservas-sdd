"""Endpoints del jugador (api.md, RF-01 a RF-06)."""
from datetime import datetime

from fastapi import APIRouter, Depends, Query

from ..config import Settings
from ..errors import Validacion
from ..schemas import ReservaEntrada, TelefonoEntrada, validar_fecha, validar_telefono
from ..services import canchas, disponibilidad, reservas
from .deps import get_ahora, get_conn, get_settings

router = APIRouter(prefix="/api")


def _validar(campo: str, valor: str, funcion) -> str:
    try:
        return funcion(valor)
    except ValueError as e:
        raise Validacion("Datos inválidos", {campo: str(e)}) from None


@router.get("/canchas")
def listar_canchas(conn=Depends(get_conn)):
    return canchas.listar_activas(conn)


@router.get("/canchas/{cancha_id}/disponibilidad")
def ver_disponibilidad(
    cancha_id: int,
    fecha: str = Query(...),
    conn=Depends(get_conn),
    settings: Settings = Depends(get_settings),
    ahora: datetime = Depends(get_ahora),
):
    fecha = _validar("fecha", fecha, validar_fecha)
    return disponibilidad.disponibilidad(conn, settings, ahora, cancha_id, fecha)


@router.post("/reservas", status_code=201)
def crear_reserva(
    entrada: ReservaEntrada,
    conn=Depends(get_conn),
    settings: Settings = Depends(get_settings),
    ahora: datetime = Depends(get_ahora),
):
    return reservas.crear(conn, settings, ahora, entrada.model_dump())


@router.get("/reservas/{codigo}")
def consultar_reserva(codigo: str, telefono: str = Query(...), conn=Depends(get_conn)):
    telefono = _validar("telefono", telefono, validar_telefono)
    return reservas.consultar(conn, codigo.strip().upper(), telefono)


@router.post("/reservas/{codigo}/cancelar")
def cancelar_reserva(
    codigo: str,
    entrada: TelefonoEntrada,
    conn=Depends(get_conn),
    settings: Settings = Depends(get_settings),
    ahora: datetime = Depends(get_ahora),
):
    return reservas.cancelar_jugador(conn, settings, ahora, codigo.strip().upper(), entrada.telefono)
