# AI Development Log

| Fecha | Actividad | IA utilizada | Solicitud (prompt) | Resultado | Decision | Autor |
|---|---|---|---|---|---|---|
| 15/11/2026 | Redactar specs/data-model.md (issue #11) | Claude Code (Sonnet 5.5) | Definir entidades canchas, reservas y bloqueos, con la restricción que impide dos reservas activas para la misma cancha y franja | Tres tablas, índice único parcial para reservas confirmadas, triggers de exclusión reserva/bloqueo, precio copiado a la reserva | Aceptado; se agregaron triggers porque un índice por tabla no cubre el cruce reserva/bloqueo | Roy |
| 13/11/2026 | Redactar borrador de specs (outcomes, requirements, business-rules, acceptance-criteria) | Claude Code (Sonnet 5.5) | Escribir el borrador del ciclo 1 como Product / Spec Lead, partiendo del enunciado y de franjas de 1 h, reserva con nombre y teléfono, y cancelación hasta 2 h antes | Cuatro specs con 5 outcomes, 11 RF, 7 RNF, 20 reglas y 22 criterios de aceptación trazables | Aceptado como borrador; los valores marcados [Supuesto] se validan en grupo (PR #2, #4, #6, #8) | Kelvin |
