"""No doble reserva (RN-01, RN-02, RN-17, RNF-01). PRUEBA OBLIGATORIA.

Tareas T-02, T-06, T-07 y T-13 del plan de implementación.

Diseño de la prueba concurrente (docs/testing.md):
- base SQLite en archivo temporal (fixture `db_path`), nunca :memory:;
- una conexión por hilo, N hilos sincronizados con threading.Barrier;
- se espera exactamente 1 éxito y N-1 conflictos, ningún otro error,
  y COUNT(*) = 1 reserva confirmada en la franja;
- se repite varias veces para detectar fallos intermitentes.
"""
import pytest

pytestmark = [
    pytest.mark.conflicto,
    pytest.mark.regla_critica,
    pytest.mark.skip(reason="pendiente T-02/T-06/T-07: db.py y services/reservas.py"),
]

N_HILOS = 10
REPETICIONES = 20


@pytest.mark.ac("AC-05")
def test_segunda_reserva_misma_franja_es_conflicto(db_path, reloj):
    """Dada una reserva confirmada en (cancha 1, 2026-11-21, 18:00),
    cuando otro teléfono reserva la misma franja,
    entonces se lanza el error de dominio `conflicto` y hay 1 sola fila confirmada."""


@pytest.mark.ac("AC-05")
def test_indice_unico_rechaza_insercion_directa(db_path):
    """Dada una reserva confirmada, cuando se inserta otra igual directamente con SQL
    (saltándose el servicio), entonces SQLite lanza IntegrityError (ux_reserva_activa)."""


@pytest.mark.ac("AC-06")
@pytest.mark.parametrize("repeticion", range(REPETICIONES))
def test_reservas_simultaneas_solo_una_gana(db_path, reloj, repeticion):
    """Dada una franja libre, cuando N_HILOS hilos (cada uno con su conexión)
    reservan a la vez tras una Barrier, entonces exactamente 1 se confirma,
    N_HILOS-1 reciben `conflicto`, ninguno recibe otra excepción
    (en especial `database is locked`) y queda 1 sola reserva confirmada."""


def test_franja_cancelada_se_puede_volver_a_reservar(db_path, reloj):
    """Dada una reserva cancelada, cuando se reserva otra vez la misma franja,
    entonces se confirma (índice parcial, RN-03)."""


@pytest.mark.ac("AC-20")
def test_no_se_reserva_franja_bloqueada(db_path, reloj):
    """Dada una franja bloqueada, cuando se intenta reservar, entonces `conflicto` (RN-02)."""


@pytest.mark.ac("AC-21")
def test_no_se_bloquea_franja_reservada(db_path, reloj):
    """Dada una franja con reserva confirmada, cuando se bloquea, entonces `conflicto` (RN-17)."""


def test_triggers_impiden_cruce_reserva_bloqueo_por_sql(db_path):
    """Cuando se inserta por SQL un bloqueo sobre una franja reservada, o al revés,
    entonces el trigger aborta la inserción."""


def test_bloqueo_y_reserva_simultaneos_solo_uno_gana(db_path, reloj):
    """Dada una franja libre, cuando a la vez un hilo reserva y otro bloquea,
    entonces queda exactamente una de las dos (reserva o bloqueo), nunca ambas."""
