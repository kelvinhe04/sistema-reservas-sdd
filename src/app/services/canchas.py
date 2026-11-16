"""Canchas (RF-01, RF-09, RN-15, RN-16, RN-20)."""
import sqlite3
from datetime import datetime

from ..errors import Conflicto, NoEncontrado, Validacion
from ..schemas import validar_texto


def _salida(fila, incluir_activa: bool) -> dict:
    d = {"id": fila["id"], "nombre": fila["nombre"], "deporte": fila["deporte"],
         "precio_hora": fila["precio_hora"]}
    if incluir_activa:
        d["activa"] = bool(fila["activa"])
    return d


def listar_activas(conn) -> list[dict]:
    filas = conn.execute("SELECT * FROM canchas WHERE activa = 1 ORDER BY nombre").fetchall()
    return [_salida(f, False) for f in filas]


def listar_todas(conn) -> list[dict]:
    filas = conn.execute("SELECT * FROM canchas ORDER BY activa DESC, nombre").fetchall()
    return [_salida(f, True) for f in filas]


def obtener(conn, cancha_id: int):
    fila = conn.execute("SELECT * FROM canchas WHERE id = ?", (cancha_id,)).fetchone()
    if fila is None:
        raise NoEncontrado("No se encontró la cancha")
    return fila


def _datos(nombre, deporte, precio_hora):
    if not isinstance(precio_hora, int) or precio_hora < 0:
        raise Validacion("Datos inválidos", {"precio_hora": "El precio no puede ser negativo"})
    errores, limpio = {}, {}
    for campo, valor in (("nombre", nombre), ("deporte", deporte)):
        try:
            limpio[campo] = validar_texto(valor, campo)
        except ValueError as e:
            errores[campo] = str(e)
    if errores:
        raise Validacion("Datos de la cancha inválidos", errores)
    return limpio["nombre"], limpio["deporte"], precio_hora


def crear(conn, ahora: datetime, nombre: str, deporte: str, precio_hora: int) -> dict:
    nombre, deporte, precio_hora = _datos(nombre, deporte, precio_hora)
    try:
        cur = conn.execute(
            "INSERT INTO canchas (nombre, deporte, precio_hora, activa, creada_en) VALUES (?, ?, ?, 1, ?)",
            (nombre, deporte, precio_hora, ahora.isoformat()),
        )
    except sqlite3.IntegrityError:
        raise Conflicto("Ya existe una cancha con ese nombre") from None
    return _salida(obtener(conn, cur.lastrowid), True)


def editar(conn, cancha_id: int, nombre: str, deporte: str, precio_hora: int) -> dict:
    nombre, deporte, precio_hora = _datos(nombre, deporte, precio_hora)
    obtener(conn, cancha_id)
    try:
        conn.execute(
            "UPDATE canchas SET nombre = ?, deporte = ?, precio_hora = ? WHERE id = ?",
            (nombre, deporte, precio_hora, cancha_id),
        )
    except sqlite3.IntegrityError:
        raise Conflicto("Ya existe una cancha con ese nombre") from None
    return _salida(obtener(conn, cancha_id), True)


def desactivar(conn, cancha_id: int) -> dict:
    """RN-16: no toca las reservas confirmadas de la cancha."""
    obtener(conn, cancha_id)
    conn.execute("UPDATE canchas SET activa = 0 WHERE id = ?", (cancha_id,))
    return _salida(obtener(conn, cancha_id), True)
