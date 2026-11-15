# API

Estado: borrador del ciclo 1 (Architecture / Dev Lead). API REST sobre HTTP, con cuerpos JSON en UTF-8. Cubre RF-01 a RF-11. Cada endpoint indica los criterios de aceptación (AC) que lo verifican.

## Convenciones

- Prefijo `/api`. Fechas `YYYY-MM-DD`, horas `HH:MM`, en la zona horaria de la sede (RNF-04).
- Dinero en centavos (`precio_hora`), como en `data-model.md`.
- Endpoints de administrador: exigen el encabezado `X-Admin-Key` (RN-19, RNF-07). Sin él, o con una clave incorrecta, responden 401.
- Los nombres de campos van en español, igual que el modelo de datos.

## Formato de error

Todos los errores usan la misma forma:

```json
{ "error": "conflicto", "mensaje": "La franja ya está reservada", "campos": {} }
```

`campos` solo se llena en errores de validación, con el nombre del campo inválido y el motivo (RNF-02, AC-09).

| `error` | HTTP | Cuándo |
|---|---|---|
| `validacion` | 422 | Dato de entrada con formato o longitud inválidos (RN-08, RN-09) |
| `regla_negocio` | 422 | La petición es válida pero viola una regla: franja pasada o fuera de horario, más de 30 días, cancha desactivada, límite de 3 reservas, fuera del límite de cancelación, reserva ya cancelada |
| `no_encontrado` | 404 | Recurso inexistente; también código y teléfono que no coinciden (RN-14) |
| `no_autorizado` | 401 | Falta la clave de administrador o es incorrecta |
| `conflicto` | 409 | La franja ya tiene una reserva confirmada o un bloqueo (RN-01, RN-02), o se intenta bloquear una franja con reserva (RN-17) |

## Endpoints del jugador

### GET /api/canchas — RF-01

Lista las canchas activas (RN-15).

Respuesta 200:

```json
[ { "id": 1, "nombre": "Cancha 1", "deporte": "fútbol", "precio_hora": 1500 } ]
```

Criterios: AC-01.

### GET /api/canchas/{id}/disponibilidad?fecha=YYYY-MM-DD — RF-02

Devuelve todas las franjas de la cancha para la fecha, de 08:00 a 21:00 (RN-04, RN-05), marcadas como libres u ocupadas (reserva confirmada o bloqueo). Cada franja indica además `pasada: true` si ya empezó según la hora de la sede (RN-06), para que la interfaz no la ofrezca; una franja pasada puede seguir `libre`, pero no se puede reservar.

Respuesta 200:

```json
{
  "cancha_id": 1, "fecha": "2026-11-20",
  "franjas": [
    { "hora_inicio": "08:00", "estado": "libre", "pasada": true },
    { "hora_inicio": "09:00", "estado": "ocupada", "pasada": false }
  ]
}
```

Errores: 404 `no_encontrado` (cancha inexistente o desactivada), 422 `validacion` (fecha mal formada).

Criterios: AC-02, AC-03.

### POST /api/reservas — RF-03, RF-04

Crea una reserva sobre una franja libre.

Entrada:

```json
{ "cancha_id": 1, "fecha": "2026-11-20", "hora_inicio": "18:00", "nombre": "Ana Pérez", "telefono": "62001234" }
```

Respuesta 201:

```json
{
  "codigo": "K7M2QX9P", "cancha_id": 1, "fecha": "2026-11-20", "hora_inicio": "18:00",
  "nombre": "Ana Pérez", "telefono": "62001234", "precio_hora": 1500, "estado": "confirmada"
}
```

Errores:

| HTTP | `error` | Caso |
|---|---|---|
| 422 | `validacion` | Nombre fuera de 2–60 caracteres, teléfono con letras o longitud fuera de 7–15, campos faltantes (RN-08, RN-09) |
| 422 | `regla_negocio` | Franja ya iniciada o pasada (RN-06), más de 30 días (RN-07), hora fuera del horario o no en punto (RN-04, RN-05), cancha desactivada (RN-15), teléfono con 3 reservas activas (RN-11) |
| 404 | `no_encontrado` | Cancha inexistente |
| 409 | `conflicto` | Franja con reserva confirmada o bloqueo, incluidas dos solicitudes simultáneas (RN-01, RN-02) |

Criterios: AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11.

### GET /api/reservas/{codigo}?telefono=... — RF-05

Consulta una reserva. El código y el teléfono deben coincidir (RN-14).

Respuesta 200: el mismo objeto que devuelve la creación, con su `estado` actual (`confirmada` o `cancelada`).

Errores: 404 `no_encontrado` si el código no existe o el teléfono no coincide; el mensaje es igual en ambos casos, sin revelar datos (AC-13).

Criterios: AC-12, AC-13.

### POST /api/reservas/{codigo}/cancelar — RF-06

Cancela la reserva del jugador. El teléfono va en el cuerpo, no en la URL, para no dejarlo en registros de acceso.

Entrada: `{ "telefono": "62001234" }`

Respuesta 200: la reserva con `estado: "cancelada"`. La franja vuelve a aparecer libre (RN-03).

Errores:

| HTTP | `error` | Caso |
|---|---|---|
| 404 | `no_encontrado` | Código inexistente o teléfono distinto (RN-14) |
| 422 | `regla_negocio` | Faltan menos de 2 horas para el inicio (RN-13), o la reserva ya estaba cancelada (RN-12) |

Criterios: AC-13, AC-14, AC-15, AC-16.

## Endpoints del administrador

Todos exigen `X-Admin-Key`. Sin ella o con una incorrecta: 401 `no_autorizado` (AC-17).

### POST /api/admin/login — RF-07

Comprueba la clave para que el panel decida si mostrar la pantalla de administración. No crea sesión: cada petición siguiente envía la clave.

Respuesta 200: `{ "ok": true }`. Respuesta 401 si la clave es incorrecta.

Criterios: AC-17.

### GET /api/admin/agenda?fecha=YYYY-MM-DD — RF-08

Agenda del día por cancha, con todas las franjas.

Respuesta 200:

```json
{
  "fecha": "2026-11-20",
  "canchas": [
    {
      "cancha_id": 1, "nombre": "Cancha 1",
      "franjas": [
        { "hora_inicio": "08:00", "estado": "libre" },
        { "hora_inicio": "09:00", "estado": "reservada", "reserva": { "codigo": "K7M2QX9P", "nombre": "Ana Pérez", "telefono": "62001234" } },
        { "hora_inicio": "10:00", "estado": "bloqueada", "bloqueo": { "id": 3, "motivo": "Mantenimiento" } }
      ]
    }
  ]
}
```

Incluye las canchas desactivadas que aún tengan reservas confirmadas ese día (RN-16).

Criterios: AC-18.

### Gestión de canchas — RF-09

| Método y ruta | Acción |
|---|---|
| GET /api/admin/canchas | Lista todas las canchas, activas e inactivas |
| POST /api/admin/canchas | Crea una cancha |
| PUT /api/admin/canchas/{id} | Edita nombre, deporte y precio |
| POST /api/admin/canchas/{id}/desactivar | Desactiva la cancha; no cancela ni borra sus reservas confirmadas (RN-16) |

Entrada de POST y PUT: `{ "nombre": "Cancha 3", "deporte": "pádel", "precio_hora": 2000 }`. Respuesta 201 (POST) o 200 (PUT y desactivar) con la cancha: `id`, `nombre`, `deporte`, `precio_hora`, `activa`.

Errores: 422 `validacion` (nombre vacío, precio negativo), 409 `conflicto` (nombre repetido), 404 `no_encontrado`.

Cambiar el precio no modifica las reservas ya creadas (RN-20).

Criterios: AC-19.

### POST /api/admin/bloqueos — RF-10

Bloquea una franja.

Entrada: `{ "cancha_id": 1, "fecha": "2026-11-20", "hora_inicio": "10:00", "motivo": "Mantenimiento" }`

Respuesta 201: `{ "id": 3, "cancha_id": 1, "fecha": "2026-11-20", "hora_inicio": "10:00", "motivo": "Mantenimiento" }`

Errores: 409 `conflicto` si la franja ya tiene una reserva confirmada (RN-17) o ya está bloqueada; 404 `no_encontrado` si la cancha no existe; 422 `validacion` o `regla_negocio` si la hora no es una franja válida.

Criterios: AC-20, AC-21.

### DELETE /api/admin/bloqueos/{id} — RF-10

Quita el bloqueo y la franja vuelve a estar libre (RN-18).

Respuesta 204 sin cuerpo. Error: 404 `no_encontrado`.

Criterios: AC-20.

### POST /api/admin/reservas/{codigo}/cancelar — RF-11

Cancela cualquier reserva confirmada, sin límite de tiempo (RN-13). No pide teléfono.

Respuesta 200: la reserva con `estado: "cancelada"`; la franja queda libre.

Errores: 404 `no_encontrado`; 422 `regla_negocio` si ya estaba cancelada (RN-12).

Criterios: AC-22.

## Trazabilidad

| Requisito | Endpoint |
|---|---|
| RF-01 | GET /api/canchas |
| RF-02 | GET /api/canchas/{id}/disponibilidad |
| RF-03, RF-04 | POST /api/reservas |
| RF-05 | GET /api/reservas/{codigo} |
| RF-06 | POST /api/reservas/{codigo}/cancelar |
| RF-07 | POST /api/admin/login y encabezado `X-Admin-Key` |
| RF-08 | GET /api/admin/agenda |
| RF-09 | GET, POST, PUT y POST desactivar en /api/admin/canchas |
| RF-10 | POST y DELETE en /api/admin/bloqueos |
| RF-11 | POST /api/admin/reservas/{codigo}/cancelar |
