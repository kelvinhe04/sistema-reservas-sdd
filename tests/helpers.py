"""Constantes y utilidades compartidas por las pruebas."""
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Panama")
ADMIN_KEY_PRUEBA = "clave-de-prueba"
AHORA_POR_DEFECTO = datetime(2026, 11, 20, 10, 0, tzinfo=TZ)  # viernes, 10:00
MANANA = "2026-11-21"


def contar_confirmadas(conn, cancha_id, fecha, hora) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM reservas WHERE cancha_id = ? AND fecha = ? AND hora_inicio = ? "
        "AND estado = 'confirmada'",
        (cancha_id, fecha, hora),
    ).fetchone()[0]
