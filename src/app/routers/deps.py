"""Dependencias compartidas por los routers."""
from collections.abc import Iterator
from datetime import datetime

from fastapi import Request

from ..config import Settings
from ..db import connect


def get_conn(request: Request) -> Iterator:
    """Una conexión por petición (nunca compartida entre hilos)."""
    settings: Settings = request.app.state.settings
    conn = connect(settings.db_path, settings.busy_timeout_ms)
    try:
        yield conn
    finally:
        conn.close()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_ahora(request: Request) -> datetime:
    return request.app.state.reloj.ahora()
