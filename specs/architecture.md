# Arquitectura

Estado: borrador del ciclo 1 (Architecture / Dev Lead). Cubre RNF-01 a RNF-07 y garantiza RN-01 (no doble reserva).

## Stack elegido

| Capa | Tecnología | Justificación |
|---|---|---|
| Lenguaje | Python 3.12 | Simple, legible y con buen soporte de pruebas |
| Framework web | FastAPI | Validación de entradas integrada (RNF-02), documentación OpenAPI automática y cliente de pruebas incluido |
| Base de datos | SQLite (modo WAL) | Sin servidor que instalar, un solo archivo, soporta índices únicos parciales y transacciones; suficiente para una sede (supuesto de `outcomes.md`) |
| Acceso a datos | `sqlite3` de la librería estándar, con funciones SQL explícitas | Control total de transacciones y de los errores de restricción; sin ORM que oculte la concurrencia |
| Pruebas | pytest + httpx (`TestClient` de FastAPI) | Pruebas unitarias, de integración y de aceptación con la misma herramienta |
| Frontend | Páginas HTML estáticas con JavaScript simple, servidas por la misma aplicación | RNF-05 (adaptable a móvil) sin una segunda aplicación que desplegar |

Alternativa descartada: PostgreSQL. Es más robusto para varias sedes, pero exige un servidor y complica las pruebas y el despliegue de un proyecto de una sede. Si el sistema creciera, el cambio se limita a la capa de acceso a datos.

## Cómo se garantiza RN-01 y RNF-01 (no doble reserva)

Dos capas que se refuerzan:

1. **Base de datos (garantía final).** Un índice único parcial sobre las reservas confirmadas:
   `UNIQUE (cancha_id, fecha, hora_inicio) WHERE estado = 'confirmada'`.
   Se usa un índice parcial, no una restricción simple, porque las reservas canceladas permanecen en la tabla y no deben impedir volver a reservar esa franja (RN-03, RN-12). Si dos solicitudes simultáneas pasan la lógica, la base rechaza la segunda con un error de restricción, que la API traduce a conflicto (HTTP 409).
2. **Lógica y transacción.** Crear una reserva y crear un bloqueo se ejecutan en una transacción `BEGIN IMMEDIATE`, que serializa a los escritores. Dentro de la transacción se comprueba que la franja no tenga reserva confirmada ni bloqueo (RN-02, RN-17) antes de insertar. Esto cubre el cruce entre reservas y bloqueos, que un índice por tabla no puede impedir.

Ninguna regla de concurrencia depende de comprobaciones en memoria ni de bloqueos de la aplicación.

## Estructura de `src/`

```
src/
  app/
    main.py          crea la aplicación FastAPI y registra los routers
    config.py        parámetros configurables (franja, horario, anticipación, límites, zona horaria, clave de admin)
    db.py            conexión SQLite, creación del esquema, transacciones
    schemas.py       modelos de entrada y salida (validación)
    errors.py        errores de dominio y su traducción a códigos HTTP
    services/
      reservas.py    reglas de reserva, consulta y cancelación
      canchas.py     reglas de canchas
      bloqueos.py    reglas de bloqueos
      disponibilidad.py  cálculo de franjas libres y ocupadas
    routers/
      publico.py     endpoints del jugador
      admin.py       endpoints del administrador (protegidos)
    static/          páginas HTML, CSS y JavaScript
tests/
  unit/              reglas puras (franjas, validaciones, ventana de cancelación)
  integration/       servicios contra una base SQLite temporal (incluye conflictos y concurrencia)
  acceptance/        un caso por criterio AC-xx contra la API
  conftest.py        fixtures: base temporal, cliente, reloj controlable
```

Las reglas viven en `services/`, sin depender de FastAPI, para poder probarlas de forma unitaria.

## Configuración

Los valores marcados como supuesto en `business-rules.md` viven en `config.py` y se pueden sobrescribir con variables de entorno, no en el código de las reglas:

| Parámetro | Valor por defecto | Regla |
|---|---|---|
| `SLOT_MINUTES` | 60 | RN-04 |
| `OPEN_HOUR` / `CLOSE_HOUR` | 8 / 22 | RN-05 |
| `MAX_ADVANCE_DAYS` | 30 | RN-07 |
| `MAX_ACTIVE_PER_PHONE` | 3 | RN-11 |
| `CANCEL_LIMIT_HOURS` | 2 | RN-13 |
| `TIMEZONE` | America/Panama | RNF-04 |
| `ADMIN_KEY` | sin valor por defecto; obligatoria al iniciar | RN-19, RNF-07 |
| `DB_PATH` | `data/reservas.db` | |

## Decisiones transversales

- **Tiempo.** Todas las fechas y horas se calculan en `America/Panama` (RNF-04). El servicio recibe un reloj inyectable para poder probar las reglas de pasado, anticipación y límite de cancelación sin esperar (RN-06, RN-07, RN-13).
- **Autenticación del administrador.** Una única clave enviada en el encabezado `X-Admin-Key`; se compara en tiempo constante. Sin clave o con clave incorrecta, la API responde 401 (RN-19, AC-17).
- **Errores.** Formato único `{ "error": "<codigo>", "mensaje": "<texto>", "campos": {...} }`. Códigos: `conflicto`, `validacion`, `no_encontrado`, `no_autorizado`, `regla_negocio`. El detalle está en `api.md`.
- **Privacidad.** Consultar o cancelar con código y teléfono que no coinciden responde `no_encontrado`, igual que un código inexistente (RN-14).
- **Código de reserva.** Cadena aleatoria de 8 caracteres en mayúsculas y dígitos, sin caracteres ambiguos, con restricción única en base de datos (RN-10).

## Ejecución

Desde la raíz del repositorio:

```
python -m venv .venv
pip install -r requirements.txt
ADMIN_KEY=<clave> uvicorn src.app.main:app --reload     # servidor local
pytest                                                   # todas las pruebas
pytest tests/unit                                        # solo unitarias
pytest tests/acceptance                                  # criterios de aceptación
```

La base se crea sola en el primer arranque. Las pruebas usan una base temporal por prueba, sin tocar `data/`.

## Despliegue

Un solo proceso `uvicorn` y un archivo SQLite en un volumen persistente. Un `Dockerfile` opcional empaqueta la aplicación (tarea del plan de implementación). La integración continua ejecuta `pytest` en cada PR (a cargo del QA / DevOps Lead, ver `docs/testing.md`).

## Trazabilidad

| Requisito | Dónde se resuelve |
|---|---|
| RNF-01 | Índice único parcial + transacción `BEGIN IMMEDIATE` |
| RNF-02 | Esquemas de FastAPI + validaciones en `services/` |
| RNF-03 | SQLite local con índices por cancha y fecha |
| RNF-04 | `TIMEZONE` en `config.py` y reloj inyectable |
| RNF-05 | Frontend HTML adaptable servido en `static/` |
| RNF-06 | Estructura `tests/` con pruebas de reglas críticas y de aceptación |
| RNF-07 | Cabecera `X-Admin-Key` en todos los endpoints de `routers/admin.py` |
