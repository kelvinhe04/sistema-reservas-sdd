# AI Development Log

| Fecha | Actividad | IA utilizada | Solicitud (prompt) | Resultado | Decision | Autor |
|---|---|---|---|---|---|---|
| 15/11/2026 | Redactar specs/architecture.md y docs/decisions.md (issue #10) | Claude Code (Sonnet 5.5) | Elegir stack simple y probable; garantizar RN-01 y RNF-01 también con concurrencia; definir estructura de src/ y cómo correr las pruebas | Stack Python + FastAPI + SQLite, índice único parcial más transacción BEGIN IMMEDIATE, estructura de carpetas, configuración y 5 decisiones | Aceptado; se descartó la restricción única simple porque impediría re-reservar franjas canceladas | Roy |
| 13/11/2026 | Redactar borrador de specs (outcomes, requirements, business-rules, acceptance-criteria) | Claude Code (Sonnet 5.5) | Escribir el borrador del ciclo 1 como Product / Spec Lead, partiendo del enunciado y de franjas de 1 h, reserva con nombre y teléfono, y cancelación hasta 2 h antes | Cuatro specs con 5 outcomes, 11 RF, 7 RNF, 20 reglas y 22 criterios de aceptación trazables | Aceptado como borrador; los valores marcados [Supuesto] se validan en grupo (PR #2, #4, #6, #8) | Kelvin |
