"""Errores de dominio y su traducción a HTTP (api.md, "Formato de error")."""


class ErrorDominio(Exception):
    codigo = "error"
    http = 400

    def __init__(self, mensaje: str, campos: dict | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campos = campos or {}

    def cuerpo(self) -> dict:
        return {"error": self.codigo, "mensaje": self.mensaje, "campos": self.campos}


class Validacion(ErrorDominio):
    codigo, http = "validacion", 422


class ReglaNegocio(ErrorDominio):
    codigo, http = "regla_negocio", 422


class NoEncontrado(ErrorDominio):
    codigo, http = "no_encontrado", 404


class NoAutorizado(ErrorDominio):
    codigo, http = "no_autorizado", 401


class Conflicto(ErrorDominio):
    codigo, http = "conflicto", 409
