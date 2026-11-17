"""Parámetros configurables (architecture.md, "Configuración").

Los valores marcados como [Supuesto] en business-rules.md viven aquí y se pueden
sobrescribir con variables de entorno.
"""
import os
from dataclasses import dataclass, replace
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class Settings:
    slot_minutes: int = 60          # RN-04
    open_hour: int = 8              # RN-05
    close_hour: int = 22            # RN-05 (la última franja empieza a close_hour - 1)
    max_advance_days: int = 30      # RN-07
    max_active_per_phone: int = 3   # RN-11
    cancel_limit_hours: int = 6     # RN-13 (cambio ciclo 3: antes 2)
    timezone: str = "America/Panama"  # RNF-04
    admin_key: str = ""             # RN-19, RNF-07
    db_path: str = "data/reservas.db"
    busy_timeout_ms: int = 5000     # espera de escritores en SQLite (AC-06)

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


def _int(nombre: str, defecto: int) -> int:
    valor = os.environ.get(nombre)
    return int(valor) if valor not in (None, "") else defecto


def load_settings(**overrides) -> Settings:
    base = Settings()
    s = Settings(
        slot_minutes=_int("SLOT_MINUTES", base.slot_minutes),
        open_hour=_int("OPEN_HOUR", base.open_hour),
        close_hour=_int("CLOSE_HOUR", base.close_hour),
        max_advance_days=_int("MAX_ADVANCE_DAYS", base.max_advance_days),
        max_active_per_phone=_int("MAX_ACTIVE_PER_PHONE", base.max_active_per_phone),
        cancel_limit_hours=_int("CANCEL_LIMIT_HOURS", base.cancel_limit_hours),
        timezone=os.environ.get("TIMEZONE", base.timezone),
        admin_key=os.environ.get("ADMIN_KEY", ""),
        db_path=os.environ.get("DB_PATH", base.db_path),
        busy_timeout_ms=_int("BUSY_TIMEOUT_MS", base.busy_timeout_ms),
    )
    return replace(s, **overrides)


class RelojReal:
    """Reloj del sistema en la zona horaria de la sede. Las pruebas inyectan otro."""

    def __init__(self, tz: ZoneInfo):
        self._tz = tz

    def ahora(self) -> datetime:
        return datetime.now(self._tz)
