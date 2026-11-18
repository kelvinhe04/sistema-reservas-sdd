# Plan de implementación

Estado: borrador del ciclo 1 (Architecture / Dev Lead). Tareas ordenadas para el ciclo 2 (implementación y pruebas base). Cada tarea enlaza los RF, RN y AC que cubre, según `requirements.md`, `business-rules.md` y `acceptance-criteria.md`. Stack y estructura: `architecture.md`.

## Reglas de trabajo

- Un issue por tarea, una rama `ciclo2/<rol>/<tema>`, commits `tipo(#issue): descripción`, PR revisado por otra persona.
- Cada tarea incluye las pruebas de sus criterios de aceptación: una tarea no está terminada si sus AC no pasan.
- Los parámetros configurables (franja, horario, límites) se leen de `config.py`, no se escriben en las reglas.
- Quien usa IA registra la fila en `docs/ai-log.md` dentro del mismo PR.

## Tareas

| # | Tarea | Contenido | RF | RN | AC |
|---|---|---|---|---|---|
| T-01 | Esqueleto del proyecto | Estructura de `src/` y `tests/`, `requirements.txt` (fastapi, uvicorn, pytest, httpx, tzdata), `config.py` con parámetros y variable `ADMIN_KEY`, `main.py` con la fábrica `create_app(db_path, reloj)`, `conftest.py` con base temporal y reloj controlable, `pytest` ejecutable | | | |
| T-02 | Base de datos | `db.py`: conexión, `PRAGMA foreign_keys`, WAL, esquema de `data-model.md` con índice único parcial, índices y triggers; helper de transacción `BEGIN IMMEDIATE`; cada conexión con `isolation_level=None`, `busy_timeout`, claves foráneas y WAL | | RN-01, RN-02, RN-10 | |
| T-03 | Franjas y disponibilidad | `services/disponibilidad.py`: generación de franjas de 08:00 a 21:00 y estado libre u ocupada | RF-02 | RN-02, RN-04, RN-05 | AC-02, AC-03 |
| T-04 | Canchas públicas | Servicio de canchas y `GET /api/canchas`, `GET /api/canchas/{id}/disponibilidad` | RF-01, RF-02 | RN-15 | AC-01, AC-02, AC-03 |
| T-05 | Errores y validaciones | `errors.py` con formato único y códigos, `schemas.py` con validación de nombre y teléfono | | RN-08, RN-09 | AC-09 |
| T-06 | Crear reserva | `services/reservas.py` y `POST /api/reservas`: validaciones, código único, copia del precio, conflicto por índice y transacción | RF-03, RF-04 | RN-01, RN-02, RN-06, RN-07, RN-08, RN-10, RN-15, RN-20 | AC-04, AC-05, AC-07, AC-08, AC-10 |
| T-07 | Prueba de no doble reserva concurrente | Prueba que lanza solicitudes simultáneas sobre la misma franja y verifica una sola reserva confirmada (obligatoria) | RF-03 | RN-01 | AC-05, AC-06 |
| T-08 | Límite por teléfono | Máximo de reservas confirmadas por teléfono, dentro de la transacción de creación | RF-03 | RN-11 | AC-11 |
| T-09 | Consultar reserva | `GET /api/reservas/{codigo}` con código y teléfono, respuesta uniforme si no coincide | RF-05 | RN-14 | AC-12, AC-13 |
| T-10 | Cancelar como jugador | `POST /api/reservas/{codigo}/cancelar`: ventana de 6 h (cambio ciclo 3), estado, liberación de la franja | RF-06 | RN-03, RN-12, RN-13, RN-14 | AC-13, AC-14, AC-15, AC-16 |
| T-11 | Acceso de administrador | Dependencia que valida `X-Admin-Key` en tiempo constante y `POST /api/admin/login` | RF-07 | RN-19 | AC-17 |
| T-12 | Gestión de canchas | Endpoints de administración de canchas, desactivar sin tocar reservas | RF-09 | RN-15, RN-16, RN-20 | AC-19 |
| T-13 | Bloqueos | `POST` y `DELETE /api/admin/bloqueos`, rechazo si hay reserva confirmada, cruce con triggers | RF-10 | RN-02, RN-17, RN-18 | AC-20, AC-21 |
| T-14 | Cancelar como administrador | `POST /api/admin/reservas/{codigo}/cancelar` sin límite de tiempo | RF-11 | RN-03, RN-13 | AC-22 |
| T-15 | Agenda del día | `GET /api/admin/agenda` con reservas, bloqueos y franjas libres por cancha | RF-08 | RN-16 | AC-18 |
| T-16 | Interfaz web | Páginas HTML adaptables a móvil: vista del jugador (elegir cancha, día y franja, reservar, consultar y cancelar) y panel de administrador | RF-01 a RF-11 | | RNF-05 |
| T-17 | Integración continua y empaquetado | Flujo que ejecuta `pytest` en cada PR; `Dockerfile` opcional; instrucciones de arranque en el README | | | RNF-06 |
| T-18 | Verificación final | Revisar que todos los AC-01 a AC-22 tengan prueba automatizada y registrar resultados en `docs/testing.md` | | | AC-01 a AC-22 |

## Orden y dependencias

```
T-01 → T-02 → T-05 → T-03 → T-04 → T-06 → T-07 → T-08
                                     └──→ T-09 → T-10
T-01 → T-11 → T-12 → T-13 → T-14 → T-15
T-04, T-10, T-15 → T-16
T-01 → T-17 (en paralelo desde el inicio)
todas → T-18
```

Prioridad: T-01 a T-07 primero. Con ellas existe el camino principal (reservar sin doble reserva) y la prueba obligatoria, que es lo que se demuestra en la presentación.

## Reparto sugerido en el ciclo 2

| Rol (ciclo 2) | Tareas |
|---|---|
| Architecture / Dev Lead (Kelvin) | T-01, T-02, T-03, T-04, T-05, T-06, T-08, T-09, T-10 |
| Product / Spec Lead (Einer) | T-11 a T-15, T-16, y actualizar las specs si cambia algún criterio |
| QA / DevOps Lead (Roy) | T-07, T-17, T-18 y la revisión de las pruebas de todas las tareas |

El reparto es una propuesta: el grupo puede ajustarlo al abrir los issues del ciclo 2.

## Cobertura de requisitos

| Requisito | Tareas |
|---|---|
| RF-01 | T-04 |
| RF-02 | T-03, T-04 |
| RF-03, RF-04 | T-06, T-07, T-08 |
| RF-05 | T-09 |
| RF-06 | T-10 |
| RF-07 | T-11 |
| RF-08 | T-15 |
| RF-09 | T-12 |
| RF-10 | T-13 |
| RF-11 | T-14 |
| RNF-01 | T-02, T-06, T-07 |
| RNF-02 | T-05 |
| RNF-03 | T-02, T-03 |
| RNF-04 | T-01 |
| RNF-05 | T-16 |
| RNF-06 | T-07, T-17, T-18 |
| RNF-07 | T-11 |

## Preparación para el cambio de requerimiento (ciclo 3)

El plan deja los parámetros en configuración y las reglas en `services/`, de modo que un cambio de requerimiento toque pocas piezas: la spec, los criterios, la tarea correspondiente, el servicio y sus pruebas. El ciclo completo se documenta en el PR del cambio.
