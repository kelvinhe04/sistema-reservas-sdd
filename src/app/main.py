"""Aplicación FastAPI (architecture.md).

Arranque local:  ADMIN_KEY=<clave> uvicorn src.app.main:app --reload
Pruebas:         create_app(db_path=..., reloj=...) desde tests/conftest.py
"""
from dataclasses import replace
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import RelojReal, load_settings
from .db import init_db
from .errors import ErrorDominio
from .routers import publico

STATIC = Path(__file__).parent / "static"


def _mensaje(error: dict) -> str:
    msg = error.get("msg", "Valor inválido")
    return msg.removeprefix("Value error, ")


def create_app(db_path=None, reloj=None, settings=None) -> FastAPI:
    settings = settings or load_settings()
    if db_path is not None:
        settings = replace(settings, db_path=str(db_path))
    if not settings.admin_key:
        raise RuntimeError("Falta la variable de entorno ADMIN_KEY (RN-19)")
    init_db(settings.db_path, settings.busy_timeout_ms)

    app = FastAPI(title="Reservas de canchas", version="1.0.0")
    app.state.settings = settings
    app.state.reloj = reloj or RelojReal(settings.tz)

    @app.exception_handler(ErrorDominio)
    async def _error_dominio(request: Request, exc: ErrorDominio):
        return JSONResponse(status_code=exc.http, content=exc.cuerpo())

    @app.exception_handler(RequestValidationError)
    async def _error_validacion(request: Request, exc: RequestValidationError):
        campos = {}
        for e in exc.errors():
            loc = [str(p) for p in e.get("loc", []) if p not in ("body", "query", "path")]
            campos[loc[-1] if loc else "cuerpo"] = _mensaje(e)
        return JSONResponse(
            status_code=422,
            content={"error": "validacion", "mensaje": "Datos de entrada inválidos", "campos": campos},
        )

    app.include_router(publico.router)
    if STATIC.is_dir():
        app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
    return app


def __getattr__(nombre: str):
    # `uvicorn src.app.main:app` crea la aplicación al arrancar, no al importar el módulo,
    # para que las pruebas puedan importarlo sin ADMIN_KEY.
    if nombre == "app":
        return create_app()
    raise AttributeError(nombre)
