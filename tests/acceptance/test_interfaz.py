"""Interfaz web (T-16, RNF-05) y formato único de errores (api.md)."""
import re

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


@pytest.mark.parametrize("recurso", ["/styles.css", "/reserva.css", "/comun.js", "/jugador.js", "/admin.js"])
def test_recursos_estaticos(client, recurso):
    assert client.get(recurso).status_code == 200


@pytest.mark.parametrize("ruta", ["/", "/admin.html"])
def test_todo_recurso_referenciado_existe(client, ruta):
    """Cada <script src> y <link href> de la página responde 200 (incluidos los ?v= de caché)."""
    html = client.get(ruta).text
    refs = re.findall(r'(?:src|href)="(/[^"#]+)"', html)
    assert refs
    for ref in refs:
        if ref.endswith(".html") or ref == "/":
            continue
        assert client.get(ref).status_code == 200, ref


def test_vista_del_jugador_es_un_asistente_por_pasos(client):
    """Issue #62: asistente de 4 pasos y vista aparte para consultar o cancelar."""
    html = client.get("/").text
    for marcador in ('id="lista-pasos"', 'id="principal"', 'id="resumen"', 'id="vista-mia"',
                     'href="#mi-reserva"', 'id="form-buscar"'):
        assert marcador in html, marcador
    js = client.get("/jugador.js").text
    for paso in ("1. Selecciona la cancha", "2. Selecciona fecha y horario",
                 "3. Datos del responsable", "4. Confirmación"):
        assert paso in js, paso
    # sin diálogos nativos del navegador: la confirmación de cancelar está en la página
    assert "confirm(" not in js and "prompt(" not in js


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


def test_la_ui_muestra_el_mismo_limite_de_cancelacion_que_el_servidor(client):
    """RN-13: el plazo que ve el jugador (paso 4 y Mi reserva) debe ser el que aplica el servidor."""
    from src.app.config import Settings

    horas = Settings().cancel_limit_hours
    js = client.get("/jugador.js").text
    m = re.search(r"const LIMITE_CANCELACION_H = (\d+);", js)
    assert m and int(m.group(1)) == horas
    html = client.get("/").text
    assert f"Hasta {horas} horas antes" in html and f"Con menos de {horas} horas" in html
