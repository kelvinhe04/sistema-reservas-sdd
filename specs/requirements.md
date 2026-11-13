# Requisitos

Estado: borrador del ciclo 1. Cada requisito se traza a un outcome de `outcomes.md`, a reglas de `business-rules.md` y a criterios de `acceptance-criteria.md`.

## Requisitos funcionales

### Jugador

| ID | Requisito | Outcome |
|---|---|---|
| RF-01 | El jugador puede ver la lista de canchas activas, con nombre, tipo de deporte y precio por hora | O-02 |
| RF-02 | El jugador puede consultar la disponibilidad de una cancha para una fecha, viendo cada franja como libre u ocupada | O-02, O-05 |
| RF-03 | El jugador puede reservar una franja libre indicando cancha, fecha, franja, nombre y teléfono | O-01, O-02 |
| RF-04 | Al reservar, el sistema entrega un código de reserva único y muestra el resumen | O-03 |
| RF-05 | El jugador puede consultar su reserva con código y teléfono | O-03 |
| RF-06 | El jugador puede cancelar su reserva con código y teléfono, hasta el límite permitido | O-03, O-05 |

### Administrador

| ID | Requisito | Outcome |
|---|---|---|
| RF-07 | El administrador accede a un panel protegido con clave | O-04 |
| RF-08 | El administrador ve la agenda de un día, por cancha, con reservas, bloqueos y franjas libres | O-04 |
| RF-09 | El administrador puede crear, editar y desactivar canchas | O-04 |
| RF-10 | El administrador puede bloquear y desbloquear franjas (mantenimiento, evento privado) | O-04 |
| RF-11 | El administrador puede cancelar cualquier reserva | O-04, O-05 |

## Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 | Integridad: el sistema garantiza a nivel de base de datos y de lógica que no existan dos reservas activas para la misma cancha y franja, incluso con solicitudes simultáneas |
| RNF-02 | Validación: todos los datos de entrada se validan en el servidor, con mensajes de error claros |
| RNF-03 | Consultas de disponibilidad y reservas responden en menos de 1 segundo en condiciones normales |
| RNF-04 | Todas las fechas y horas se manejan en la zona horaria de la sede (America/Panama) |
| RNF-05 | La aplicación se usa correctamente desde un teléfono móvil (diseño adaptable) |
| RNF-06 | Las reglas críticas tienen pruebas automatizadas; la regla de no doble reserva es obligatoria |
| RNF-07 | El panel de administración no es accesible sin la clave |

## Historias de usuario resumidas

- Como jugador, quiero ver qué horarios están libres para reservar sin escribirle a nadie.
- Como jugador, quiero un código para consultar o cancelar mi reserva después.
- Como administrador, quiero ver la agenda del día para saber qué canchas están ocupadas.
- Como administrador, quiero bloquear horarios para que nadie los reserve cuando la cancha no está disponible.
