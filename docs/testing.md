# Plan de pruebas

Estado: borrador del ciclo 1 (QA / DevOps Lead). Cubre los criterios AC-01 a AC-22 de `specs/acceptance-criteria.md` con pytest + httpx (`TestClient` de FastAPI), según `specs/architecture.md`. Los resultados de cada ejecución se registran al final de este archivo.

## Tipos de prueba

| Tipo | Marcador pytest | Qué verifica | Carpeta |
|---|---|---|---|
| Unitaria | `unitaria` | Funciones puras sin base de datos ni HTTP: generación de franjas, validaciones, ventana de cancelación, código de reserva | `tests/unit/` |
| Regla crítica | `regla_critica` | Reglas RN-01, RN-02, RN-03, RN-06, RN-07, RN-11, RN-13, RN-14, RN-15, RN-17 contra los servicios y una base SQLite temporal | `tests/integration/` |
| Conflicto de reserva | `conflicto` | No doble reserva (secuencial y concurrente) y cruce reserva/bloqueo | `tests/integration/` |
| Validación de usuario | `validacion` | Datos de entrada inválidos: nombre, teléfono, campos faltantes, formatos de fecha y hora | `tests/unit/` y `tests/acceptance/` |
| Aceptación | `aceptacion` | Un caso por criterio AC-xx contra la API, en formato Dado / Cuando / Entonces | `tests/acceptance/` |

Cada prueba lleva el marcador de su tipo y el marcador `ac("AC-xx")` del criterio que cubre. Ejemplos:

```
pytest -m conflicto          # solo no doble reserva
pytest -m regla_critica      # reglas críticas
pytest tests/acceptance      # criterios de aceptación
```

## Mapa de criterios a pruebas

Todos los AC tienen al menos una prueba de aceptación. La columna "Otras" indica las pruebas adicionales de nivel inferior.

| AC | Regla / requisito | Prueba de aceptación | Otras pruebas | Tarea (plan) | Prioridad |
|---|---|---|---|---|---|
| AC-01 | RF-01, RN-15 | `acceptance/test_canchas.py::test_ac01_lista_solo_canchas_activas` | — | T-04 | Media |
| AC-02 | RF-02, RN-04, RN-05 | `acceptance/test_canchas.py::test_ac02_disponibilidad_de_08_a_21` | unitaria: `unit/test_franjas.py` | T-03, T-04 | Media |
| AC-03 | RF-02, RN-02 | `acceptance/test_canchas.py::test_ac03_franja_reservada_o_bloqueada_aparece_ocupada` | — | T-03, T-04 | Media |
| AC-04 | RF-03, RF-04, RN-08, RN-10 | `acceptance/test_reservas.py::test_ac04_reserva_confirmada_con_codigo` | unitaria: `unit/test_codigo.py` | T-06 | Alta |
| **AC-05** | **RN-01, RNF-01** | `acceptance/test_reservas.py::test_ac05_rechaza_doble_reserva` | conflicto: `integration/test_no_doble_reserva.py` | T-06, T-07 | **Obligatoria** |
| **AC-06** | **RN-01, RNF-01** | `acceptance/test_reservas.py::test_ac06_rechaza_doble_reserva_concurrente` | conflicto: `integration/test_no_doble_reserva.py` | T-07 | **Obligatoria** |
| AC-07 | RN-06 | `acceptance/test_reservas.py::test_ac07_rechaza_franja_pasada_o_iniciada` | regla crítica: `integration/test_reglas_reserva.py` | T-06 | Alta |
| AC-08 | RN-07 | `acceptance/test_reservas.py::test_ac08_rechaza_mas_de_30_dias` | regla crítica: `integration/test_reglas_reserva.py` | T-06 | Alta |
| AC-09 | RN-09, RNF-02 | `acceptance/test_reservas.py::test_ac09_rechaza_datos_invalidos` | validación: `unit/test_validaciones.py` | T-05 | Alta |
| AC-10 | RN-15 | `acceptance/test_reservas.py::test_ac10_rechaza_cancha_desactivada` | regla crítica: `integration/test_reglas_reserva.py` | T-06 | Alta |
| AC-11 | RN-11 | `acceptance/test_reservas.py::test_ac11_maximo_tres_activas_por_telefono` | regla crítica: `integration/test_reglas_reserva.py` | T-08 | Alta |
| AC-12 | RF-05, RN-14 | `acceptance/test_consulta_cancelacion.py::test_ac12_consulta_con_codigo_y_telefono` | — | T-09 | Media |
| AC-13 | RN-14 | `acceptance/test_consulta_cancelacion.py::test_ac13_no_revela_datos_si_no_coinciden` | regla crítica: `integration/test_reglas_cancelacion.py` | T-09, T-10 | Alta |
| AC-14 | RF-06, RN-03, RN-13 | `acceptance/test_consulta_cancelacion.py::test_ac14_cancela_y_libera_franja` | unitaria: `unit/test_ventana_cancelacion.py` | T-10 | Alta |
| AC-15 | RN-13 | `acceptance/test_consulta_cancelacion.py::test_ac15_rechaza_cancelar_a_menos_de_2h` | unitaria: `unit/test_ventana_cancelacion.py` | T-10 | Alta |
| AC-16 | RN-12 | `acceptance/test_consulta_cancelacion.py::test_ac16_no_cancela_dos_veces` | — | T-10 | Media |
| AC-17 | RF-07, RNF-07, RN-19 | `acceptance/test_admin.py::test_ac17_admin_sin_clave_denegado` | — | T-11 | Alta |
| AC-18 | RF-08 | `acceptance/test_admin.py::test_ac18_agenda_del_dia` | — | T-15 | Media |
| AC-19 | RF-09, RN-15, RN-16 | `acceptance/test_admin.py::test_ac19_gestion_de_canchas` | — | T-12 | Media |
| AC-20 | RF-10, RN-02, RN-18 | `acceptance/test_admin.py::test_ac20_bloquear_y_desbloquear` | conflicto: `integration/test_no_doble_reserva.py` (cruce reserva/bloqueo) | T-13 | Alta |
| AC-21 | RN-17 | `acceptance/test_admin.py::test_ac21_no_bloquea_franja_reservada` | conflicto: `integration/test_no_doble_reserva.py` | T-13 | Alta |
| AC-22 | RF-11, RN-13 | `acceptance/test_admin.py::test_ac22_admin_cancela_sin_limite` | — | T-14 | Media |

La prueba `tests/test_trazabilidad.py` comprueba de forma automática que cada AC de `specs/acceptance-criteria.md` tenga al menos una prueba marcada con su ID. Si se añade un AC sin prueba, la CI falla.

## No doble reserva (AC-05 y AC-06)

Son las pruebas obligatorias del proyecto. Se prueban en dos niveles: servicio (`integration/`) y API (`acceptance/`).

**Secuencial (AC-05).** Se reserva una franja; un segundo intento con otro nombre y teléfono sobre la misma cancha, fecha y hora debe responder 409 `conflicto`, y en la base debe quedar una sola reserva `confirmada` para esa franja.

**Concurrente (AC-06).** Para que la prueba demuestre algo real con SQLite:

- Base en un **archivo temporal**, no `:memory:` (cada conexión a `:memory:` es una base distinta).
- **Una conexión por hilo**: cada hilo abre la suya, igual que dos peticiones reales.
- **N = 10 hilos** sincronizados con `threading.Barrier`, para que todos intenten insertar a la vez.
- Resultado esperado: exactamente **1** éxito y **9** `conflicto`; ningún error inesperado (en particular, ningún `database is locked`, que la API convertiría en 500); `COUNT(*) = 1` reservas confirmadas en esa franja.
- Se repite 20 veces (`pytest.mark.parametrize`) para detectar fallos intermitentes.
- Requisito para la implementación (comentado en el PR #16): `PRAGMA busy_timeout` e `isolation_level=None`, de modo que `BEGIN IMMEDIATE` espere en lugar de fallar.

**Re-reserva tras cancelar.** Tras cancelar, la misma franja se puede volver a reservar (índice único parcial, RN-03).

**Cruce reserva/bloqueo.** No se puede bloquear una franja con reserva (RN-17) ni reservar una bloqueada (RN-02), tanto por la lógica como por los triggers (insertando directo en la base).

## Control del tiempo

Las reglas RN-06, RN-07 y RN-13 dependen de la hora actual. Las pruebas no usan el reloj real: `conftest.py` ofrece un reloj controlable que se inyecta en los servicios (ver `architecture.md`), fijado por defecto en `2026-11-20 10:00` America/Panama. Casos de borde que se prueban:

- Franja que empieza justo ahora (rechazada) y la siguiente (aceptada).
- Exactamente 30 días (aceptada) y 31 días (rechazada).
- Cancelación a 6 h 01 min (aceptada), a 5 h 59 min (rechazada) y a exactamente 6 h (aceptada). Límite de 6 h desde el cambio de requerimiento del ciclo 3 (#64); antes 2 h (#22).
- Límite por teléfono: 3 reservas futuras bloquean la cuarta; 3 reservas ya jugadas no (RN-11 según #22).

## Datos de prueba

- Cada prueba usa una base SQLite nueva en `tmp_path`; nunca toca `data/`.
- `ADMIN_KEY` de prueba: `clave-de-prueba` (fixture `admin_headers`). La CI define la misma variable.
- Canchas de ejemplo: una activa de fútbol, una activa de pádel y una desactivada.

## Integración continua

`.github/workflows/tests.yml` ejecuta `pytest` en cada Pull Request y en cada push a `main`, con Python 3.12, y después repite aparte `pytest -m conflicto` para que la prueba obligatoria se vea en su propio paso. Instala siempre `requirements.txt` (ya no hay rama de respaldo). El PR no debe fusionarse si la CI falla.

**Nota para T-01:** `requirements.txt` debe incluir `tzdata`. En Windows, `zoneinfo` no trae la base de zonas horarias y `ZoneInfo("America/Panama")` falla sin ese paquete (detectado al ejecutar el esqueleto en local).

Ejecución local (PowerShell):

```
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install pytest httpx tzdata      # o: pip install -r requirements.txt
pytest
```

Recomendación para el repositorio: activar en GitHub la protección de `main` que exige que el check `pytest` pase antes de fusionar.

## Estado actual

T-01 a T-16 están implementadas y **ninguna prueba está en `skip`**; `test_trazabilidad.py::test_ninguna_prueba_queda_en_skip` lo exige (issue #25). La concurrencia se prueba en los dos niveles: servicio (una conexión por hilo, 20 repeticiones) y API (un `TestClient` por hilo, 5 repeticiones). `acceptance/test_interfaz.py` comprueba que las páginas se sirven, son adaptables (viewport) y no dependen de recursos externos, y que todos los errores usan el formato único.

### Prueba manual de la interfaz (15/11/2026)

En el navegador, con el servidor local y una base de demostración, se recorrió el flujo completo en escritorio y en móvil (375 px):

- Admin: clave incorrecta rechazada; entrar; crear canchas; precio negativo rechazado en el campo; agenda del día; bloquear una franja con motivo; cancelar una reserva a menos de 6 h (permitido al admin).
- Jugador: elegir cancha, día y franja; las franjas ya iniciadas salen deshabilitadas; teléfono inválido marcado en su campo; reserva confirmada con código; la franja pasa a ocupada; consultar con código y teléfono; cancelar a menos de 6 h rechazado con el mensaje del límite.
- Sin errores de JavaScript en consola (solo los 401/422 esperados de los casos negativos).
- Corregido durante la prueba: columnas de la agenda, alineación de formularios cuando aparece un error, precio en formato `$12.00`, y errores de Starlette (cuerpo ilegible, ruta inexistente) con el formato único.

## Dudas resueltas (issue #22)

- RN-13: con exactamente 6 h de antelación el jugador todavía puede cancelar (antes 2 h; cambiado en el ciclo 3, #64).
- RN-11: solo cuentan como activas las reservas confirmadas cuya franja no ha empezado.
- AC-16: reformulado; no existe operación de "reactivar", se prueba cancelar dos veces.

## Resultados

| Fecha | Commit | Total | Pasan | Fallan | Omitidas | Notas |
|---|---|---|---|---|---|---|
| 15/11/2026 | esqueleto ciclo 1 (local, Windows, Python 3.13) | 109 | 3 | 0 | 106 | Pasan las 3 de trazabilidad; las demás en `skip` hasta implementar `src/`. `pytest -m conflicto`: 30 omitidas |
| 15/11/2026 | T-01 a T-10 (local, Windows, Python 3.13) | 134 | 117 | 0 | 17 | Omitidas solo las de administración (T-11 a T-15). AC-05 y AC-06 pasan en servicio y API |
| 15/11/2026 | T-01 a T-16 (local, Windows, Python 3.13) | 157 | 157 | 0 | 0 | AC-01 a AC-22 cubiertos; `pytest -m conflicto`: 38 pasan |
| 16/11/2026 | `8c33d13` (main, T-01 a T-16; local, Windows, Python 3.13) | 157 | 157 | 0 | 0 | Verificación final T-18 (#46): AC-01 a AC-22 con prueba y sin `skip` (`test_trazabilidad.py` pasa; 70 pruebas de aceptación). `pytest -m conflicto`: 38 de 38 pasan. Hallazgo abierto: #52 |
| 16/11/2026 | Cambio ciclo 3: ventana de cancelación 2 h → 6 h (#64), commit de la rama `ciclo3/spec/cambio-ventana-cancelacion` (local, Windows, Python 3.13) | 157 | 157 | 0 | 0 | Pruebas de cancelación al límite (6 h 01, 5 h 59, 6 h exacta) ajustadas; `pytest -m conflicto`: 38 pasan |
| 17/11/2026 | Corrección #52 (rama `ciclo3/qa/base-ocupada-503`; local, Windows, Python 3.13) | 160 | 160 | 0 | 0 | 3 pruebas nuevas en `integration/test_base_ocupada.py`: cancelar con la base ocupada responde 503 `base_ocupada` en el formato único y la reserva sigue confirmada |
