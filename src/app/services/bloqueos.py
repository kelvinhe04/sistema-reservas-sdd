"""Bloqueos de franjas (RF-10, RN-02, RN-17, RN-18)."""
import sqlite3
from datetime import datetime

from ..config import Settings
from ..db import transaccion
from ..errors import Conflicto, NoEncontrado
from .disponibilidad import exigir_franja_valida


def crear(conn, settings: Settings, ahora: datetime, cancha_id: int, fecha: str,
          hora_inicio: str, motivo: str | None) -> dict:
    exigir_franja_valida(hora_inicio, settings)
    try:
        with transaccion(conn):
            if conn.execute("SELECT 1 FROM canchas WHERE id = ?", (cancha_id,)).fetchone() is None:
                raise NoEncontrado("No se encontró la cancha")
            if conn.execute(
                "SELECT 1 FROM reservas WHERE cancha_id = ? AND fecha = ? AND hora_inicio = ? "
                "AND estado = 'confirmada'",
                (cancha_id, fecha, hora_inicio),
            ).fetchone():
                raise Conflicto("La franja tiene una reserva confirmada; cancélala antes de bloquear")
            cur = conn.execute(
                "INSERT INTO bloqueos (cancha_id, fecha, hora_inicio, motivo, creado_en) "
                "VALUES (?, ?, ?, ?, ?)",
                (cancha_id, fecha, hora_inicio, motivo, ahora.isoformat()),
            )
    except sqlite3.IntegrityError as e:
        if "franja_reservada" in str(e):
            raise Conflicto("La franja tiene una reserva confirmada; cancélala antes de bloquear") from e
        raise Conflicto("La franja ya está bloqueada") from e
    except sqlite3.OperationalError as e:
        if "locked" in str(e).lower():
            raise Conflicto("La franja se está modificando en este momento; intenta de nuevo") from e
        raise
    return {"id": cur.lastrowid, "cancha_id": cancha_id, "fecha": fecha,
            "hora_inicio": hora_inicio, "motivo": motivo}


def eliminar(conn, bloqueo_id: int) -> None:
    """RN-18: quitar el bloqueo libera la franja."""
    cur = conn.execute("DELETE FROM bloqueos WHERE id = ?", (bloqueo_id,))
    if cur.rowcount == 0:
        raise NoEncontrado("No se encontró el bloqueo")
