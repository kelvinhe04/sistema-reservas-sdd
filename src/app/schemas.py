"""Validaciones de entrada (RN-08, RN-09, RNF-02) y modelos de la API.

Las funciones `validar_*` son puras: devuelven el valor normalizado o lanzan
ValueError con el motivo. Las usan los modelos y los servicios.
"""
import re
from datetime import date

from pydantic import BaseModel, field_validator

_TELEFONO = re.compile(r"\d{7,15}")
_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")
_HORA = re.compile(r"\d{2}:\d{2}")


def validar_nombre(valor) -> str:
    if not isinstance(valor, str):
        raise ValueError("El nombre es obligatorio")
    limpio = " ".join(valor.split())
    if not 2 <= len(limpio) <= 60:
        raise ValueError("El nombre debe tener entre 2 y 60 caracteres")
    return limpio


def validar_telefono(valor) -> str:
    if not isinstance(valor, str) or not _TELEFONO.fullmatch(valor):
        raise ValueError("El teléfono debe tener solo dígitos, entre 7 y 15")
    return valor


def validar_fecha(valor) -> str:
    if not isinstance(valor, str) or not _FECHA.fullmatch(valor):
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD")
    try:
        date.fromisoformat(valor)
    except ValueError:
        raise ValueError("La fecha no existe") from None
    return valor


def validar_hora(valor) -> str:
    if not isinstance(valor, str) or not _HORA.fullmatch(valor):
        raise ValueError("La hora debe tener el formato HH:MM")
    return valor


def validar_texto(valor, campo: str, maximo: int = 60) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo {campo} es obligatorio")
    limpio = " ".join(valor.split())
    if len(limpio) > maximo:
        raise ValueError(f"El campo {campo} admite como máximo {maximo} caracteres")
    return limpio


class ReservaEntrada(BaseModel):
    cancha_id: int
    fecha: str
    hora_inicio: str
    nombre: str
    telefono: str

    @field_validator("fecha")
    @classmethod
    def v_fecha(cls, v):
        return validar_fecha(v)
    @field_validator("hora_inicio")
    @classmethod
    def v_hora(cls, v):
        return validar_hora(v)
    @field_validator("nombre")
    @classmethod
    def v_nombre(cls, v):
        return validar_nombre(v)
    @field_validator("telefono")
    @classmethod
    def v_tel(cls, v):
        return validar_telefono(v)


class TelefonoEntrada(BaseModel):
    telefono: str

    @field_validator("telefono")
    @classmethod
    def v_tel(cls, v):
        return validar_telefono(v)


class CanchaEntrada(BaseModel):
    nombre: str
    deporte: str
    precio_hora: int

    @field_validator("nombre")
    @classmethod
    def v_nombre(cls, v):
        return validar_texto(v, "nombre")
    @field_validator("deporte")
    @classmethod
    def v_deporte(cls, v):
        return validar_texto(v, "deporte")

    @field_validator("precio_hora")
    @classmethod
    def v_precio(cls, v):
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v


class BloqueoEntrada(BaseModel):
    cancha_id: int
    fecha: str
    hora_inicio: str
    motivo: str | None = None

    @field_validator("fecha")
    @classmethod
    def v_fecha(cls, v):
        return validar_fecha(v)
    @field_validator("hora_inicio")
    @classmethod
    def v_hora(cls, v):
        return validar_hora(v)

    @field_validator("motivo")
    @classmethod
    def v_motivo(cls, v):
        if v is None:
            return None
        limpio = " ".join(v.split())
        if len(limpio) > 120:
            raise ValueError("El motivo admite como máximo 120 caracteres")
        return limpio or None
