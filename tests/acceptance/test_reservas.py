"""Aceptación: crear reserva (AC-04 a AC-11). Tareas T-05 a T-08.

AC-05 y AC-06 son las pruebas obligatorias de no doble reserva.
"""
import pytest

pytestmark = [
    pytest.mark.aceptacion,
    pytest.mark.skip(reason="pendiente T-06: POST /api/reservas"),
]


@pytest.mark.ac("AC-04")
def test_ac04_reserva_confirmada_con_codigo(client):
    """Dado una franja libre y datos válidos
    Cuando el jugador hace POST /api/reservas
    Entonces responde 201 con estado `confirmada` y un código de 8 caracteres,
    y la franja pasa a ocupada en la disponibilidad."""


@pytest.mark.conflicto
@pytest.mark.ac("AC-05")
def test_ac05_rechaza_doble_reserva(client):
    """Dado una franja ya reservada de una cancha
    Cuando otro jugador reserva la misma cancha, fecha y franja
    Entonces responde 409 con error `conflicto` y no se crea una segunda reserva."""


@pytest.mark.conflicto
@pytest.mark.ac("AC-06")
def test_ac06_rechaza_doble_reserva_concurrente(client):
    """Dado una franja libre
    Cuando 10 solicitudes POST /api/reservas para esa franja llegan a la vez (hilos + Barrier)
    Entonces exactamente una responde 201, las demás 409 `conflicto`, ninguna 500,
    y la disponibilidad muestra una sola reserva."""


@pytest.mark.ac("AC-07")
def test_ac07_rechaza_franja_pasada_o_iniciada(client):
    """Dado una franja que ya empezó o está en el pasado
    Cuando el jugador intenta reservarla
    Entonces responde 422 `regla_negocio`."""


@pytest.mark.ac("AC-08")
def test_ac08_rechaza_mas_de_30_dias(client):
    """Dado una fecha a más de 30 días
    Cuando el jugador intenta reservarla
    Entonces responde 422 `regla_negocio`."""


@pytest.mark.validacion
@pytest.mark.ac("AC-09")
@pytest.mark.parametrize(
    "cambio, campo",
    [
        ({"nombre": ""}, "nombre"),
        ({"nombre": "A"}, "nombre"),
        ({"telefono": "6200abcd"}, "telefono"),
        ({"telefono": "123"}, "telefono"),
    ],
)
def test_ac09_rechaza_datos_invalidos(client, cambio, campo):
    """Dado un nombre vacío o de menos de 2 caracteres, o un teléfono con letras o de longitud inválida
    Cuando el jugador intenta reservar
    Entonces responde 422 `validacion` y `campos` indica el campo inválido."""


@pytest.mark.ac("AC-10")
def test_ac10_rechaza_cancha_desactivada(client, admin_headers):
    """Dado una cancha desactivada
    Cuando el jugador intenta reservarla
    Entonces responde 422 `regla_negocio`."""


@pytest.mark.ac("AC-11")
def test_ac11_maximo_tres_activas_por_telefono(client):
    """Dado un teléfono con 3 reservas activas
    Cuando intenta crear una cuarta
    Entonces responde 422 `regla_negocio`."""
