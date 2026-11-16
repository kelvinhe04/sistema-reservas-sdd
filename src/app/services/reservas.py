"""Reservas: crear, consultar y cancelar (RF-03 a RF-06, RF-11)."""
import secrets
import sqlite3
from datetime import datetime, timedelta

from ..config import Settings
from ..db import transaccion
from ..errors import Conflicto, NoEncontrado, ReglaNegocio, Validacion
from ..schemas import validar_fecha, validar_hora, validar_nombre, validar_telefono
from .disponibilidad import exigir_franja_valida, inicio_franja

# D-05: mayúsculas y dígitos sin caracteres ambiguos (0/O, 1/I/L)
ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LONGITUD_CODIGO = 8
_INTENTOS_CODIGO = 5


def generar_codigo() -> str:
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(LONGITUD_CODIGO))


def puede_cancelar_jugador(inicio: datetime, ahora: datetime, limite_horas: int) -> bool:
    """RN-13: el jugador cancela si faltan `limite_horas` o más (exactamente el límite incluido)."""
    return inicio - ahora >= timedelta(hours=limite_horas)


def _validar_entrada(datos: dict) -> dict:
    validadores = {
        "fecha": validar_fecha, "hora_inicio": validar_hora,
        "nombre": validar_nombre, "telefono": validar_telefono,
    }
    limpio, errores = dict(datos), {}
    for campo, validar in validadores.items():
        try:
            limpio[campo] = validar(datos.get(campo))
        except ValueError as e:
            errores[campo] = str(e)
    if errores:
        raise Validacion("Datos de la reserva inválidos", errores)
    return limpio


def _salida(fila) -> dict:
    return {
        "codigo": fila["codigo"], "cancha_id": fila["cancha_id"], "fecha": fila["fecha"],
        "hora_inicio": fila["hora_inicio"], "nombre": fila["nombre"], "telefono": fila["telefono"],
        "precio_hora": fila["precio_hora"], "estado": fila["estado"],
    }


def _clave_tiempo(ahora: datetime) -> str:
    """'YYYY-MM-DD HH:MM' comparable con fecha || ' ' || hora_inicio."""
    return ahora.strftime("%Y-%m-%d %H:%M")


def contar_activas(conn, telefono: str, ahora: datetime) -> int:
    """RN-11: activa = confirmada y con franja que aún no empieza."""
    return conn.execute(
        "SELECT COUNT(*) FROM reservas WHERE telefono = ? AND estado = 'confirmada' "
        "AND (fecha || ' ' || hora_inicio) > ?",
        (telefono, _clave_tiempo(ahora)),
    ).fetchone()[0]


def crear(conn: sqlite3.Connection, settings: Settings, ahora: datetime, datos: dict) -> dict:
    d = _validar_entrada(datos)
    cancha_id, fecha, hora = d["cancha_id"], d["fecha"], d["hora_inicio"]
    exigir_franja_valida(hora, settings)
    inicio = inicio_franja(fecha, hora, settings.tz)
    if inicio <= ahora:
        raise ReglaNegocio("La franja ya empezó o está en el pasado")
    if (inicio.date() - ahora.date()).days > settings.max_advance_days:
        raise ReglaNegocio(f"Solo se puede reservar con {settings.max_advance_days} días de anticipación como máximo")

    try:
        with transaccion(conn):
            cancha = conn.execute("SELECT * FROM canchas WHERE id = ?", (cancha_id,)).fetchone()
            if cancha is None:
                raise NoEncontrado("No se encontró la cancha")
            if not cancha["activa"]:
                raise ReglaNegocio("La cancha no está disponible para reservas")
            if conn.execute(
                "SELECT 1 FROM bloqueos WHERE cancha_id = ? AND fecha = ? AND hora_inicio = ?",
                (cancha_id, fecha, hora),
            ).fetchone():
                raise Conflicto("La franja está bloqueada")
            if conn.execute(
                "SELECT 1 FROM reservas WHERE cancha_id = ? AND fecha = ? AND hora_inicio = ? "
                "AND estado = 'confirmada'",
                (cancha_id, fecha, hora),
            ).fetchone():
                raise Conflicto("La franja ya está reservada")
            if contar_activas(conn, d["telefono"], ahora) >= settings.max_active_per_phone:
                raise ReglaNegocio(
                    f"Este teléfono ya tiene {settings.max_active_per_phone} reservas activas"
                )
            for intento in range(_INTENTOS_CODIGO):
                codigo = generar_codigo()
                try:
                    conn.execute(
                        "INSERT INTO reservas (codigo, cancha_id, fecha, hora_inicio, nombre, telefono,"
                        " precio_hora, estado, creada_en) VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmada', ?)",
                        (codigo, cancha_id, fecha, hora, d["nombre"], d["telefono"],
                         cancha["precio_hora"], ahora.isoformat()),
                    )
                    break
                except sqlite3.IntegrityError as e:
                    if "reservas.codigo" in str(e) and intento < _INTENTOS_CODIGO - 1:
                        continue
                    raise
    except sqlite3.IntegrityError as e:
        # Red de seguridad: índice único parcial o trigger (RN-01, RN-02)
        raise Conflicto("La franja ya está ocupada") from e
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            raise Conflicto("La franja se está reservando en este momento; intenta de nuevo") from e
        raise
    return consultar_por_codigo(conn, codigo)


def consultar_por_codigo(conn, codigo: str) -> dict:
    fila = conn.execute("SELECT * FROM reservas WHERE codigo = ?", (codigo,)).fetchone()
    if fila is None:
        raise NoEncontrado("No se encontró la reserva")
    return _salida(fila)


def consultar(conn, codigo: str, telefono: str) -> dict:
    """RN-14: mismo error si el código no existe o el teléfono no coincide."""
    fila = conn.execute(
        "SELECT * FROM reservas WHERE codigo = ? AND telefono = ?", (codigo, telefono)
    ).fetchone()
    if fila is None:
        raise NoEncontrado("No se encontró la reserva")
    return _salida(fila)


def _cancelar(conn, fila, por: str, ahora: datetime) -> dict:
    if fila["estado"] == "cancelada":
        raise ReglaNegocio("La reserva ya estaba cancelada")
    conn.execute(
        "UPDATE reservas SET estado = 'cancelada', cancelada_por = ?, cancelada_en = ? WHERE id = ?",
        (por, ahora.isoformat(), fila["id"]),
    )
    return consultar_por_codigo(conn, fila["codigo"])


def cancelar_jugador(conn, settings: Settings, ahora: datetime, codigo: str, telefono: str) -> dict:
    with transaccion(conn):
        fila = conn.execute(
            "SELECT * FROM reservas WHERE codigo = ? AND telefono = ?", (codigo, telefono)
        ).fetchone()
        if fila is None:
            raise NoEncontrado("No se encontró la reserva")
        if fila["estado"] == "cancelada":
            raise ReglaNegocio("La reserva ya estaba cancelada")
        inicio = inicio_franja(fila["fecha"], fila["hora_inicio"], settings.tz)
        if not puede_cancelar_jugador(inicio, ahora, settings.cancel_limit_hours):
            raise ReglaNegocio(
                f"Ya pasó el límite: solo se puede cancelar hasta {settings.cancel_limit_hours} "
                "horas antes del inicio"
            )
        return _cancelar(conn, fila, "jugador", ahora)


def cancelar_admin(conn, ahora: datetime, codigo: str) -> dict:
    """RF-11: el administrador cancela en cualquier momento (RN-13)."""
    with transaccion(conn):
        fila = conn.execute("SELECT * FROM reservas WHERE codigo = ?", (codigo,)).fetchone()
        if fila is None:
            raise NoEncontrado("No se encontró la reserva")
        return _cancelar(conn, fila, "admin", ahora)
