"""Interfaz web (T-16, RNF-05) y formato único de errores (api.md)."""
import pytest

pytestmark = [pytest.mark.aceptacion]


@pytest.mark.parametrize("ruta, texto", [
    ("/", "Reserva tu cancha"),
    ("/admin.html", "Entrar al panel"),
])
def test_paginas_se_sirven_y_son_adaptables(client, ruta, texto):
    r = client.get(ruta)
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert texto in r.text
    assert 'name="viewport"' in r.text  # RNF-05: diseño adaptable a móvil


@pytest.mark.parametrize("recurso", ["/styles.css", "/comun.js", "/jugador.js", "/admin.js"])
def test_recursos_estaticos(client, recurso):
    assert client.get(recurso).status_code == 200


def test_la_interfaz_no_usa_recursos_externos(client):
    """La app funciona sin internet: nada de CDN."""
    for ruta in ("/", "/admin.html"):
        html = client.get(ruta).text
        assert "http://" not in html and "https://" not in html


def test_ruta_api_inexistente_usa_formato_unico(client):
    r = client.get("/api/no-existe")
    assert r.status_code == 404
    assert r.json() == {"error": "no_encontrado", "mensaje": "Recurso no encontrado", "campos": {}}


def test_cuerpo_ilegible_usa_formato_unico(client):
    r = client.post("/api/reservas", content=b"\xff\xfe no es json", headers={"Content-Type": "application/json"})
    assert r.status_code in (400, 422)
    assert r.json()["error"] == "validacion"
