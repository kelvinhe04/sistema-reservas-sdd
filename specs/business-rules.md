# Reglas de negocio

Estado: borrador del ciclo 1. Los valores marcados con **[Supuesto]** son parámetros que el grupo puede ajustar; deben vivir en configuración, no en el código.

## Reglas críticas

| ID | Regla |
|---|---|
| RN-01 | **No doble reserva.** Una cancha solo puede tener una reserva activa por franja. Un segundo intento sobre la misma cancha, fecha y franja se rechaza. Esto aplica también a solicitudes simultáneas: si dos llegan a la vez, una se confirma y la otra se rechaza |
| RN-02 | Una franja ocupada por una reserva activa o por un bloqueo no se puede reservar |
| RN-03 | Una reserva cancelada libera la franja de inmediato |

## Franjas y horarios

| ID | Regla |
|---|---|
| RN-04 | Las franjas duran 1 hora y empiezan en hora en punto **[Supuesto]** |
| RN-05 | Horario de operación de 08:00 a 22:00, es decir, la última franja empieza a las 21:00 **[Supuesto]** |
| RN-06 | No se puede reservar una franja que ya empezó o que está en el pasado |
| RN-07 | Se puede reservar con un máximo de 30 días de anticipación **[Supuesto]** |

## Reservas

| ID | Regla |
|---|---|
| RN-08 | Una reserva requiere cancha activa, fecha, franja, nombre y teléfono |
| RN-09 | Nombre: entre 2 y 60 caracteres. Teléfono: solo dígitos, entre 7 y 15 |
| RN-10 | Cada reserva recibe un código único e irrepetible, que se usa junto al teléfono para consultarla o cancelarla |
| RN-11 | Un teléfono puede tener como máximo 3 reservas activas a la vez **[Supuesto]** |
| RN-12 | Estados de una reserva: `confirmada` y `cancelada`. Una cancelada no se reactiva; se crea una nueva |
| RN-13 | El jugador puede cancelar hasta 2 horas antes del inicio de la franja **[Supuesto]**. El administrador puede cancelar en cualquier momento |
| RN-14 | Consultar o cancelar exige que el código y el teléfono coincidan; si no, el sistema responde que no se encontró la reserva, sin revelar datos |

## Canchas y bloqueos

| ID | Regla |
|---|---|
| RN-15 | Una cancha desactivada no aparece para reservar y no admite nuevas reservas |
| RN-16 | Desactivar una cancha no borra ni cancela sus reservas futuras ya confirmadas; el administrador decide qué hacer con ellas |
| RN-17 | El administrador no puede bloquear una franja que ya tiene una reserva confirmada; primero debe cancelar esa reserva |
| RN-18 | Un bloqueo se puede quitar en cualquier momento y la franja vuelve a estar libre |

## Administración

| ID | Regla |
|---|---|
| RN-19 | Las operaciones del panel de administración exigen la clave de administrador |
| RN-20 | El precio por hora se define por cancha y no cambia el precio mostrado en reservas ya creadas |
