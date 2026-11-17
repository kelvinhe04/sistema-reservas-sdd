# Modelo de datos

Estado: borrador del ciclo 1 (Architecture / Dev Lead). Base de datos SQLite (ver `architecture.md`). Tres entidades: canchas, reservas y bloqueos.

## Convenciones

- Fecha: texto `YYYY-MM-DD`. Hora de inicio de franja: texto `HH:MM` (siempre en punto, RN-04). Ambas en la zona horaria de la sede, America/Panama (RNF-04).
- **Comparación de fecha y hora como texto.** Las consultas que necesitan saber si una franja ya empezó comparan `fecha || ' ' || hora_inicio` con el instante actual formateado como `'YYYY-MM-DD HH:MM'` en la hora de la sede. Funciona porque ambos formatos tienen ancho fijo y ceros a la izquierda, así que el orden alfabético coincide con el cronológico. Requisitos para no romperlo: guardar siempre `fecha` en ISO `YYYY-MM-DD` y `hora_inicio` en `HH:MM` de 24 h (lo garantizan las validaciones de `schemas.py`), y formatear el instante actual en la misma zona horaria, nunca en UTC.
- Dinero: entero en centavos (`precio_hora`), para evitar errores de redondeo.
- Marcas de tiempo (`creada_en`, `cancelada_en`): texto ISO 8601 con zona horaria.
- Claves primarias enteras autoincrementales. Claves foráneas activadas (`PRAGMA foreign_keys = ON`).

## Diagrama

```
canchas 1 ──── N reservas
canchas 1 ──── N bloqueos
```

Una franja queda identificada por (`cancha_id`, `fecha`, `hora_inicio`). Una franja puede tener como máximo una reserva confirmada o un bloqueo, nunca ambos.

## Entidad `canchas`

| Campo | Tipo | Restricciones | Notas |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `nombre` | TEXT | NOT NULL, UNIQUE | RF-01, RF-09 |
| `deporte` | TEXT | NOT NULL | Por ejemplo: fútbol, pádel, baloncesto |
| `precio_hora` | INTEGER | NOT NULL, CHECK (`precio_hora` >= 0) | En centavos. RN-20 |
| `activa` | INTEGER | NOT NULL, DEFAULT 1, CHECK (`activa` IN (0, 1)) | RN-15. Desactivar no borra la fila |
| `creada_en` | TEXT | NOT NULL | |

Las canchas no se borran; se desactivan (RF-09, RN-16).

## Entidad `reservas`

| Campo | Tipo | Restricciones | Notas |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `codigo` | TEXT | NOT NULL, UNIQUE | RN-10. 8 caracteres, sin caracteres ambiguos |
| `cancha_id` | INTEGER | NOT NULL, FK → `canchas.id` | |
| `fecha` | TEXT | NOT NULL | |
| `hora_inicio` | TEXT | NOT NULL | Franja de 1 hora (RN-04) |
| `nombre` | TEXT | NOT NULL, CHECK (longitud entre 2 y 60) | RN-09 |
| `telefono` | TEXT | NOT NULL, CHECK (solo dígitos, longitud entre 7 y 15) | RN-09 |
| `precio_hora` | INTEGER | NOT NULL | Copia del precio de la cancha al reservar. RN-20 |
| `estado` | TEXT | NOT NULL, CHECK (`estado` IN ('confirmada', 'cancelada')) | RN-12 |
| `cancelada_por` | TEXT | NULL, CHECK (`cancelada_por` IN ('jugador', 'admin')) | Solo con estado `cancelada` |
| `creada_en` | TEXT | NOT NULL | |
| `cancelada_en` | TEXT | NULL | |

Las reservas no se borran: al cancelar cambian de estado, para conservar el historial (RN-12). Una cancelada no vuelve a `confirmada`.

### Restricción de no doble reserva (RN-01, RNF-01)

```sql
CREATE UNIQUE INDEX ux_reserva_activa
  ON reservas (cancha_id, fecha, hora_inicio)
  WHERE estado = 'confirmada';
```

Es un índice único **parcial**: solo cuenta las reservas confirmadas. Con una restricción única simple, una reserva cancelada impediría volver a reservar la misma franja, lo que contradice RN-03. Si dos solicitudes simultáneas intentan insertar la misma franja, la base rechaza la segunda con un error de restricción, que la API traduce a conflicto.

### Otros índices

| Índice | Uso |
|---|---|
| `ix_reserva_telefono` sobre (`telefono`, `estado`) | Contar reservas activas por teléfono (RN-11) |
| `ix_reserva_agenda` sobre (`cancha_id`, `fecha`) | Disponibilidad y agenda del día (RF-02, RF-08, RNF-03) |

## Entidad `bloqueos`

| Campo | Tipo | Restricciones | Notas |
|---|---|---|---|
| `id` | INTEGER | PK | |
| `cancha_id` | INTEGER | NOT NULL, FK → `canchas.id` | |
| `fecha` | TEXT | NOT NULL | |
| `hora_inicio` | TEXT | NOT NULL | |
| `motivo` | TEXT | NULL | Mantenimiento, evento privado (RF-10) |
| `creado_en` | TEXT | NOT NULL | |

Restricción: `UNIQUE (cancha_id, fecha, hora_inicio)`, para no bloquear dos veces la misma franja.

Desbloquear borra la fila (RN-18): la franja vuelve a estar libre y no hace falta conservar el historial de bloqueos en esta versión.

## Exclusión entre reservas y bloqueos (RN-02, RN-17)

Un índice único por tabla no puede impedir que una reserva y un bloqueo ocupen la misma franja, porque están en tablas distintas. Se garantiza en dos niveles:

1. **Triggers en la base de datos** (garantía final):
   - `BEFORE INSERT` sobre `reservas` con `estado = 'confirmada'`: aborta si existe un bloqueo para esa cancha, fecha y hora.
   - `BEFORE INSERT` sobre `bloqueos`: aborta si existe una reserva confirmada para esa cancha, fecha y hora.
2. **Transacción `BEGIN IMMEDIATE`** en el servicio, que comprueba antes de insertar y devuelve un error de regla de negocio claro. El trigger es la red de seguridad si algo omitiera la comprobación.

## Reglas que no son restricciones de base de datos

Estas se validan en la capa de servicio, con parámetros de `config.py` (ver `architecture.md`):

| Regla | Dónde |
|---|---|
| RN-04, RN-05: franja de 1 h dentro del horario 08:00–22:00 | `services/disponibilidad.py` |
| RN-06, RN-07: no pasado, máximo 30 días de anticipación | `services/reservas.py` con reloj inyectable |
| RN-11: máximo 3 reservas activas (confirmadas y con franja aún no iniciada) por teléfono | `services/reservas.py`, dentro de la transacción de creación |
| RN-13: cancelación del jugador si faltan 2 h o más | `services/reservas.py` |
| RN-15: cancha activa para reservar | `services/reservas.py` |

## Consultas clave

- **Disponibilidad de una cancha y fecha (RF-02):** todas las franjas del horario, marcadas ocupadas si existe una reserva confirmada o un bloqueo para esa franja.
- **Reservas activas de un teléfono (RN-11, decidido en #22):** `SELECT COUNT(*) FROM reservas WHERE telefono = ? AND estado = 'confirmada' AND (fecha || ' ' || hora_inicio) > ?`, donde el parámetro es el instante actual como `'YYYY-MM-DD HH:MM'` (ver "Comparación de fecha y hora como texto"). Las reservas ya jugadas no cuentan.
- **Consultar o cancelar (RN-14):** `WHERE codigo = ? AND telefono = ?`; si no hay fila, se responde no encontrado.

## Trazabilidad

| Requisito o regla | Elemento del modelo |
|---|---|
| RN-01, RNF-01 | `ux_reserva_activa` |
| RN-02, RN-17 | Triggers de exclusión y transacción |
| RN-03, RN-12 | Campo `estado` y borrado lógico por cancelación |
| RN-09 | CHECK de `nombre` y `telefono` |
| RN-10 | `codigo` UNIQUE |
| RN-15, RN-16 | Campo `activa` en `canchas` |
| RN-18 | Borrado de la fila en `bloqueos` |
| RN-20 | `reservas.precio_hora` |
