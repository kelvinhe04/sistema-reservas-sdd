# AI Development Log

| Fecha | Actividad | IA utilizada | Solicitud (prompt) | Resultado | Decision | Autor |
|---|---|---|---|---|---|---|
| 15/11/2026 | Redactar specs/architecture.md y docs/decisions.md (issue #10) | Claude Code (Sonnet 5.5) | Elegir stack simple y probable; garantizar RN-01 y RNF-01 también con concurrencia; definir estructura de src/ y cómo correr las pruebas | Stack Python + FastAPI + SQLite, índice único parcial más transacción BEGIN IMMEDIATE, estructura de carpetas, configuración y 5 decisiones | Aceptado; se descartó la restricción única simple porque impediría re-reservar franjas canceladas | Roy |
