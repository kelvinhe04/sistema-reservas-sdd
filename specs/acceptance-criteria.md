# Criterios de aceptación

Estado: borrador del ciclo 1. Formato Dado / Cuando / Entonces. Cada criterio apunta al requisito (RF/RNF) y a las reglas (RN) que verifica. QA convierte cada uno en al menos una prueba automatizada.

## Disponibilidad y consulta

**AC-01** (RF-01, RN-15)
- Dado que existen canchas activas e inactivas
- Cuando el jugador pide la lista de canchas
- Entonces ve solo las activas, con nombre, deporte y precio por hora

**AC-02** (RF-02, RN-04, RN-05)
- Dado una cancha activa y una fecha futura
- Cuando el jugador consulta la disponibilidad
- Entonces recibe las franjas de 08:00 a 21:00, cada una marcada como libre u ocupada

**AC-03** (RF-02, RN-02)
- Dado una franja con reserva confirmada o con bloqueo
- Cuando el jugador consulta la disponibilidad
- Entonces esa franja aparece como ocupada

## Crear reserva

**AC-04** (RF-03, RF-04, RN-08, RN-10)
- Dado una franja libre y datos válidos
- Cuando el jugador reserva
- Entonces la reserva queda `confirmada`, recibe un código único y la franja pasa a ocupada

**AC-05 — No doble reserva** (RN-01, RNF-01)
- Dado una franja ya reservada de una cancha
- Cuando otro jugador intenta reservar la misma cancha, fecha y franja
- Entonces el sistema rechaza la solicitud con un error de conflicto y no crea una segunda reserva

**AC-06 — No doble reserva concurrente** (RN-01, RNF-01)
- Dado una franja libre
- Cuando dos solicitudes de reserva para esa franja llegan al mismo tiempo
- Entonces exactamente una se confirma, la otra se rechaza por conflicto, y existe una sola reserva activa para esa franja

**AC-07** (RN-06)
- Dado una franja que ya empezó o está en el pasado
- Cuando el jugador intenta reservarla
- Entonces el sistema la rechaza

**AC-08** (RN-07)
- Dado una fecha a más de 30 días
- Cuando el jugador intenta reservarla
- Entonces el sistema la rechaza

**AC-09** (RN-09, RNF-02)
- Dado un nombre vacío o de menos de 2 caracteres, o un teléfono con letras o de longitud inválida
- Cuando el jugador intenta reservar
- Entonces el sistema rechaza la solicitud e indica qué campo es inválido

**AC-10** (RN-15)
- Dado una cancha desactivada
- Cuando el jugador intenta reservarla
- Entonces el sistema rechaza la solicitud

**AC-11** (RN-11)
- Dado un teléfono con 3 reservas activas
- Cuando intenta crear una cuarta
- Entonces el sistema la rechaza

## Consultar y cancelar

**AC-12** (RF-05, RN-14)
- Dado una reserva existente
- Cuando el jugador consulta con el código y el teléfono correctos
- Entonces ve el detalle de su reserva

**AC-13** (RN-14)
- Dado un código correcto con un teléfono distinto, o un código inexistente
- Cuando se consulta o se intenta cancelar
- Entonces el sistema responde que no se encontró la reserva, sin revelar información

**AC-14** (RF-06, RN-03, RN-13)
- Dado una reserva confirmada que empieza en más de 2 horas
- Cuando el jugador la cancela con código y teléfono
- Entonces queda `cancelada` y la franja vuelve a aparecer como libre

**AC-15** (RN-13)
- Dado una reserva que empieza en menos de 2 horas
- Cuando el jugador intenta cancelarla
- Entonces el sistema lo rechaza e indica que ya pasó el límite

**AC-16** (RN-12)
- Dado una reserva cancelada
- Cuando se intenta cancelar o reactivar de nuevo
- Entonces el sistema lo rechaza

## Administración

**AC-17** (RF-07, RNF-07, RN-19)
- Dado que no se envía la clave de administrador, o es incorrecta
- Cuando se accede al panel o a sus operaciones
- Entonces el acceso es denegado

**AC-18** (RF-08)
- Dado un día con reservas, bloqueos y franjas libres
- Cuando el administrador abre la agenda de ese día
- Entonces ve, por cancha, cada franja con su estado y los datos de la reserva

**AC-19** (RF-09, RN-15, RN-16)
- Dado el panel de administración
- Cuando el administrador crea, edita o desactiva una cancha
- Entonces el cambio se refleja en la lista pública y las reservas futuras confirmadas no se borran

**AC-20** (RF-10, RN-02, RN-18)
- Dado una franja libre
- Cuando el administrador la bloquea
- Entonces el jugador la ve ocupada y no puede reservarla; al desbloquearla vuelve a estar libre

**AC-21** (RN-17)
- Dado una franja con reserva confirmada
- Cuando el administrador intenta bloquearla
- Entonces el sistema lo rechaza hasta que se cancele la reserva

**AC-22** (RF-11, RN-13)
- Dado cualquier reserva confirmada, incluso a menos de 2 horas del inicio
- Cuando el administrador la cancela
- Entonces queda `cancelada` y la franja se libera

## Trazabilidad

| Outcome | Criterios |
|---|---|
| O-01 | AC-05, AC-06 |
| O-02 | AC-01 a AC-04, AC-07 a AC-11 |
| O-03 | AC-12 a AC-16 |
| O-04 | AC-17 a AC-22 |
| O-05 | AC-14, AC-22 |
