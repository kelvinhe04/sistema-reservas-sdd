"""No doble reserva (RN-01, RN-02, RN-17, RNF-01). PRUEBA OBLIGATORIA.

Tareas T-02, T-06, T-07 y T-13 del plan de implementación.

Diseño de la prueba concurrente (docs/testing.md):
- base SQLite en archivo temporal (fixture `db_path`), nunca :memory:;
- una conexión por hilo, N hilos sincronizados con threading.Barrier;
- se espera exactamente 1 éxito y N-1 conflictos, ningún otro error,
  y COUNT(*) = 1 reserva confirmada en la franja;
- se repite varias veces para detectar fallos intermitentes.
"""
import sqlite3
import threading

import pytest

from src.app.db import connect
from src.app.errors import Conflicto
from src.app.services import bloqueos, reservas
from tests.helpers import MANANA, contar_confirmadas

pytestmark = [pytest.mark.conflicto, pytest.mark.regla_critica]

N_HILOS = 10
REPETICIONES = 20


def _en_paralelo(n, funcion):
    """Ejecuta funcion(i, conn) en n hilos a la vez, cada uno con su conexión."""
    barrera = threading.Barrier(n)
    resultados = [None] * n

    def trabajo(i):
        conn = connect(_en_paralelo.db_path)
        try:
            barrera.wait()
            resultados[i] = ("ok", funcion(i, conn))
        except Exception as e:  # se clasifica después
            resultados[i] = ("error", e)
        finally:
            conn.close()

    hilos = [threading.Thread(target=trabajo, args=(i,)) for i in range(n)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=30)
    return resultados


@pytest.mark.ac("AC-05")
def test_segunda_reserva_misma_franja_es_conflicto(conn, reservar, cancha):
    """Dada una reserva confirmada en (cancha 1, 2026-11-21, 18:00),
    cuando otro teléfono reserva la misma franja,
    entonces se lanza el error de dominio `conflicto` y hay 1 sola fila confirmada."""
    reservar()
    with pytest.raises(Conflicto):
        reservar(telefono="65559999", nombre="Luis Gómez")
    assert contar_confirmadas(conn, cancha, MANANA, "18:00") == 1


@pytest.mark.ac("AC-05")
def test_indice_unico_rechaza_insercion_directa(conn, reservar, cancha):
    """Dada una reserva confirmada, cuando se inserta otra igual directamente con SQL
    (saltándose el servicio), entonces SQLite lanza IntegrityError (ux_reserva_activa)."""
    reservar()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO reservas (codigo, cancha_id, fecha, hora_inicio, nombre, telefono, precio_hora,"
            " estado, creada_en) VALUES ('ZZZZZZZZ', ?, ?, '18:00', 'Otro', '65559999', 1500,"
            " 'confirmada', '2026-11-20T10:00:00-05:00')",
            (cancha, MANANA),
        )


@pytest.mark.ac("AC-06")
@pytest.mark.parametrize("repeticion", range(REPETICIONES))
def test_reservas_simultaneas_solo_una_gana(conn, settings, reloj, cancha, repeticion):
    """Dada una franja libre, cuando N_HILOS hilos (cada uno con su conexión)
    reservan a la vez tras una Barrier, entonces exactamente 1 se confirma,
    N_HILOS-1 reciben `conflicto`, ninguno recibe otra excepción
    (en especial `database is locked`) y queda 1 sola reserva confirmada."""
    _en_paralelo.db_path = settings.db_path

    def reservar(i, c):
        return reservas.crear(c, settings, reloj.ahora(), {
            "cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00",
            "nombre": f"Jugador {i}", "telefono": f"6200{i:04d}",
        })

    resultados = _en_paralelo(N_HILOS, reservar)
    exitos = [r for r in resultados if r and r[0] == "ok"]
    conflictos = [r for r in resultados if r and r[0] == "error" and isinstance(r[1], Conflicto)]
    otros = [r for r in resultados if r is None or (r[0] == "error" and not isinstance(r[1], Conflicto))]
    assert not otros, f"Errores inesperados: {otros}"
    assert len(exitos) == 1
    assert len(conflictos) == N_HILOS - 1
    assert contar_confirmadas(conn, cancha, MANANA, "18:00") == 1


def test_franja_cancelada_se_puede_volver_a_reservar(conn, settings, reloj, reservar, cancha):
    """Dada una reserva cancelada, cuando se reserva otra vez la misma franja,
    entonces se confirma (índice parcial, RN-03)."""
    r = reservar()
    reservas.cancelar_jugador(conn, settings, reloj.ahora(), r["codigo"], r["telefono"])
    nueva = reservar(telefono="65559999")
    assert nueva["estado"] == "confirmada"
    assert contar_confirmadas(conn, cancha, MANANA, "18:00") == 1


@pytest.mark.ac("AC-20")
def test_no_se_reserva_franja_bloqueada(conn, settings, reloj, reservar, cancha):
    """Dada una franja bloqueada, cuando se intenta reservar, entonces `conflicto` (RN-02)."""
    bloqueos.crear(conn, settings, reloj.ahora(), cancha, MANANA, "18:00", "Mantenimiento")
    with pytest.raises(Conflicto):
        reservar()


@pytest.mark.ac("AC-21")
def test_no_se_bloquea_franja_reservada(conn, settings, reloj, reservar, cancha):
    """Dada una franja con reserva confirmada, cuando se bloquea, entonces `conflicto` (RN-17)."""
    reservar()
    with pytest.raises(Conflicto):
        bloqueos.crear(conn, settings, reloj.ahora(), cancha, MANANA, "18:00", None)


def test_triggers_impiden_cruce_reserva_bloqueo_por_sql(conn, reservar, cancha):
    """Cuando se inserta por SQL un bloqueo sobre una franja reservada, o al revés,
    entonces el trigger aborta la inserción."""
    reservar()
    with pytest.raises(sqlite3.IntegrityError, match="franja_reservada"):
        conn.execute(
            "INSERT INTO bloqueos (cancha_id, fecha, hora_inicio, creado_en) VALUES (?, ?, '18:00', 'x')",
            (cancha, MANANA),
        )
    conn.execute(
        "INSERT INTO bloqueos (cancha_id, fecha, hora_inicio, creado_en) VALUES (?, ?, '19:00', 'x')",
        (cancha, MANANA),
    )
    with pytest.raises(sqlite3.IntegrityError, match="franja_bloqueada"):
        conn.execute(
            "INSERT INTO reservas (codigo, cancha_id, fecha, hora_inicio, nombre, telefono, precio_hora,"
            " estado, creada_en) VALUES ('YYYYYYYY', ?, ?, '19:00', 'Otro', '65559999', 1500,"
            " 'confirmada', 'x')",
            (cancha, MANANA),
        )


@pytest.mark.parametrize("repeticion", range(5))
def test_bloqueo_y_reserva_simultaneos_solo_uno_gana(conn, settings, reloj, cancha, repeticion):
    """Dada una franja libre, cuando a la vez un hilo reserva y otro bloquea,
    entonces queda exactamente una de las dos (reserva o bloqueo), nunca ambas."""
    _en_paralelo.db_path = settings.db_path

    def accion(i, c):
        if i == 0:
            return reservas.crear(c, settings, reloj.ahora(), {
                "cancha_id": cancha, "fecha": MANANA, "hora_inicio": "18:00",
                "nombre": "Ana Pérez", "telefono": "62001234",
            })
        return bloqueos.crear(c, settings, reloj.ahora(), cancha, MANANA, "18:00", None)

    resultados = _en_paralelo(2, accion)
    assert [r[0] for r in resultados].count("ok") == 1
    assert all(isinstance(r[1], Conflicto) for r in resultados if r[0] == "error")
    n_bloqueos = conn.execute("SELECT COUNT(*) FROM bloqueos").fetchone()[0]
    assert contar_confirmadas(conn, cancha, MANANA, "18:00") + n_bloqueos == 1


@pytest.mark.ac("AC-11")
@pytest.mark.parametrize("repeticion", range(5))
def test_mismo_telefono_con_2_activas_solo_una_mas_simultanea(conn, settings, reloj, cancha, repeticion):
    """Dado un teléfono con 2 reservas activas, cuando intenta 4 reservas distintas a la vez,
    entonces solo 1 se acepta y el teléfono queda con 3 activas (RN-11, dentro de la transacción)."""
    _en_paralelo.db_path = settings.db_path
    for h in ("08:00", "09:00"):
        reservas.crear(conn, settings, reloj.ahora(), {
            "cancha_id": cancha, "fecha": MANANA, "hora_inicio": h,
            "nombre": "Ana Pérez", "telefono": "62001234"})
    horas = ["10:00", "11:00", "12:00", "13:00"]

    def reservar(i, c):
        return reservas.crear(c, settings, reloj.ahora(), {
            "cancha_id": cancha, "fecha": MANANA, "hora_inicio": horas[i],
            "nombre": "Ana Pérez", "telefono": "62001234"})

    resultados = _en_paralelo(4, reservar)
    assert sum(1 for r in resultados if r and r[0] == "ok") == 1, resultados
    assert reservas.contar_activas(conn, "62001234", reloj.ahora()) == 3
