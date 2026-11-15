# AI Development Log

| Fecha | Actividad | IA utilizada | Solicitud (prompt) | Resultado | Decision | Autor |
|---|---|---|---|---|---|---|
| 15/11/2026 | Redactar specs/data-model.md (issue #11) | Claude Code (Sonnet 5.5) | Definir entidades canchas, reservas y bloqueos, con la restricción que impide dos reservas activas para la misma cancha y franja | Tres tablas, índice único parcial para reservas confirmadas, triggers de exclusión reserva/bloqueo, precio copiado a la reserva | Aceptado; se agregaron triggers porque un índice por tabla no cubre el cruce reserva/bloqueo | Roy |
