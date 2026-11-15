# AI Development Log

| Fecha | Actividad | IA utilizada | Solicitud (prompt) | Resultado | Decision | Autor |
|---|---|---|---|---|---|---|
| 15/11/2026 | Redactar specs/api.md (issue #12) | Claude Code (Sonnet 5.5) | Un endpoint por RF-01 a RF-11, con entradas, salidas y errores (conflicto, validación, no encontrado, no autorizado) | 15 endpoints, formato único de errores con 5 códigos, trazabilidad a RF y AC | Aceptado; el teléfono de cancelación va en el cuerpo y no en la URL para no registrarlo en logs | Roy |
| 13/11/2026 | Redactar borrador de specs (outcomes, requirements, business-rules, acceptance-criteria) | Claude Code (Sonnet 5.5) | Escribir el borrador del ciclo 1 como Product / Spec Lead, partiendo del enunciado y de franjas de 1 h, reserva con nombre y teléfono, y cancelación hasta 2 h antes | Cuatro specs con 5 outcomes, 11 RF, 7 RNF, 20 reglas y 22 criterios de aceptación trazables | Aceptado como borrador; los valores marcados [Supuesto] se validan en grupo (PR #2, #4, #6, #8) | Kelvin |
