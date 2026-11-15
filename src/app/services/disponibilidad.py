"""Franjas y disponibilidad (RF-02, RF-08, RN-02, RN-04, RN-05)."""
import sqlite3
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from ..config import Settings
from ..errors import NoEncontrado, ReglaNegocio


def franjas(settings: Settings) -> list[str]:
    """Horas de inicio de todas las franjas del día, p. ej. ["08:00", ..., "21:00"]."""
    resultado = []
    actual = datetime.combine(date(2000, 1, 1), time(settings.open_hour))
    fin = datetime.combine(date(2000, 1, 1), time(0)) + timedelta(hours=settings.close_hour)
    paso = timedelta(minutes=settings.slot_minutes)
    while actual + paso <= fin:
        resultado.append(actual.strftime("%H:%M"))
        actual += paso
    return resultado


def es_franja_valida(hora: str, settings: Settings) -> bool:
    return hora in franjas(settings)


def exigir_franja_valida(hora: str, settings: Settings) -> None:
    if not es_franja_valida(hora, settings):
        raise ReglaNegocio(
            f"{hora} no es una franja válida: las franjas empiezan en punto, "
            f"de {franjas(settings)[0]} a {franjas(settings)[-1]}"
        )


def inicio_franja(fecha: str, hora: str, tz: ZoneInfo) -> datetime:
    return datetime.combine(date.fromisoformat(fecha), time.fromisoformat(hora), tzinfo=tz)


def ocupacion(conn: sqlite3.Connection, cancha_id: int, fecha: str) -> dict[str, dict]:
    """Por hora: {"reserva": fila} o {"bloqueo": fila} para las franjas ocupadas."""
    ocupadas: dict[str, dict] = {}
    for r in conn.execute(
        "SELECT codigo, nombre, telefono, hora_inicio FROM reservas "
        "WHERE cancha_id = ? AND fecha = ? AND estado = 'confirmada'",
        (cancha_id, fecha),
    ):
        ocupadas[r["hora_inicio"]] = {"reserva": dict(r)}
    for b in conn.execute(
        "SELECT id, motivo, hora_inicio FROM bloqueos WHERE cancha_id = ? AND fecha = ?",
        (cancha_id, fecha),
    ):
        ocupadas[b["hora_inicio"]] = {"bloqueo": dict(b)}
    return ocupadas


def disponibilidad(conn, settings: Settings, ahora: datetime, cancha_id: int, fecha: str) -> dict:
    cancha = conn.execute("SELECT id, activa FROM canchas WHERE id = ?", (cancha_id,)).fetchone()
    if cancha is None or not cancha["activa"]:
        raise NoEncontrado("No se encontró la cancha")
    ocupadas = ocupacion(conn, cancha_id, fecha)
    lista = []
    for hora in franjas(settings):
        lista.append({
            "hora_inicio": hora,
            "estado": "ocupada" if hora in ocupadas else "libre",
            "pasada": inicio_franja(fecha, hora, settings.tz) <= ahora,
        })
    return {"cancha_id": cancha_id, "fecha": fecha, "franjas": lista}


def agenda(conn, settings: Settings, fecha: str) -> dict:
    """Agenda del día por cancha (RF-08). Incluye canchas desactivadas con reservas ese día (RN-16)."""
    canchas = conn.execute(
        "SELECT id, nombre, deporte, activa FROM canchas c WHERE activa = 1 OR EXISTS ("
        "  SELECT 1 FROM reservas r WHERE r.cancha_id = c.id AND r.fecha = ? AND r.estado = 'confirmada')"
        " ORDER BY nombre",
        (fecha,),
    ).fetchall()
    resultado = []
    for c in canchas:
        ocupadas = ocupacion(conn, c["id"], fecha)
        lista = []
        for hora in franjas(settings):
            item = {"hora_inicio": hora, "estado": "libre"}
            if hora in ocupadas and "reserva" in ocupadas[hora]:
                r = ocupadas[hora]["reserva"]
                item = {"hora_inicio": hora, "estado": "reservada",
                        "reserva": {"codigo": r["codigo"], "nombre": r["nombre"], "telefono": r["telefono"]}}
            elif hora in ocupadas:
                b = ocupadas[hora]["bloqueo"]
                item = {"hora_inicio": hora, "estado": "bloqueada",
                        "bloqueo": {"id": b["id"], "motivo": b["motivo"]}}
            lista.append(item)
        resultado.append({"cancha_id": c["id"], "nombre": c["nombre"], "deporte": c["deporte"],
                          "activa": bool(c["activa"]), "franjas": lista})
    return {"fecha": fecha, "canchas": resultado}
