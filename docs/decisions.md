# Decisiones técnicas

| ID | Fecha | Decisión | Alternativas | Motivo | Autor |
|---|---|---|---|---|---|
| D-01 | 15/11/2026 | Stack: Python 3.12 + FastAPI + SQLite (WAL) + pytest | PostgreSQL, Node + Express | Simple de instalar, probar y desplegar para una sola sede; soporta índices únicos parciales y transacciones | Roy |
| D-02 | 15/11/2026 | No doble reserva con índice único parcial `WHERE estado = 'confirmada'` más transacción `BEGIN IMMEDIATE` | Restricción única simple; bloqueos en memoria | La simple impediría re-reservar una franja cancelada; la transacción cubre además el cruce reserva/bloqueo | Roy |
| D-03 | 15/11/2026 | Acceso a datos con `sqlite3` y SQL explícito, sin ORM | SQLAlchemy | Control directo de transacciones y de errores de restricción | Roy |
| D-04 | 15/11/2026 | Clave de administrador en el encabezado `X-Admin-Key`, valor tomado de la variable de entorno `ADMIN_KEY` | Sesiones, JWT | Un único administrador (supuesto de `outcomes.md`); la opción más simple que cumple RN-19 | Roy |
| D-05 | 15/11/2026 | Código de reserva: 8 caracteres aleatorios sin caracteres ambiguos, único en base de datos | UUID completo, número secuencial | Fácil de dictar o copiar; no adivinable por secuencia (RN-10, RN-14) | Roy |
