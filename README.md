# Sistema de Reservas de Canchas Deportivas (ODD → SDD)

Proyecto 2 – Tópicos Especiales II (Prof. Regis Rivera). Desarrollo orientado por Resultados (ODD) y por Especificaciones (SDD).

Recorrido: **ODD → SDD → código → pruebas → Resultado al Usuario (valor)**

## Equipo y rotación de roles

| Ciclo | Enfoque | Product / Spec Lead | Architecture / Dev Lead | QA / DevOps Lead |
|---|---|---|---|---|
| 1 | ODD + especificaciones (`specs/`) | Kelvin He (kelvinhe04) | Roy Barrera (Roy-x24) | Einer Mosquera (Jassiel-1331) |
| 2 | Implementación + pruebas base | Einer Mosquera (Jassiel-1331) | Kelvin He (kelvinhe04) | Roy Barrera (Roy-x24) |
| 3 | Cambio de requerimiento + cierre + entrega | Roy Barrera (Roy-x24) | Einer Mosquera (Jassiel-1331) | Kelvin He (kelvinhe04) |

## Cómo ejecutar

```
py -m venv .venv                      # Windows (en macOS/Linux: python -m venv .venv)
.venv\Scripts\Activate.ps1           # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
$env:ADMIN_KEY = "una-clave"          # macOS/Linux: export ADMIN_KEY=una-clave
uvicorn src.app.main:app --reload
```

- Jugador: http://127.0.0.1:8000/
- Administración: http://127.0.0.1:8000/admin.html (clave = `ADMIN_KEY`)
- API documentada: http://127.0.0.1:8000/docs
- Pruebas: `pytest` (todas), `pytest -m conflicto` (no doble reserva)

La base SQLite se crea sola en `data/reservas.db`. Para la demo, crea las canchas desde el panel de administración.

## Material

- `docs/ia-context.md`: contexto y reglas para los asistentes de IA de cada integrante
- `docs/material/enunciado-proyecto2.pdf`: enunciado del proyecto
- `docs/material/presentacion.pptx`: presentación del grupo

## Estructura

```
README.md
specs/   outcomes, requirements, business-rules, architecture, data-model, api, acceptance-criteria, implementation-plan
docs/    ai-log.md, decisions.md, testing.md
src/
tests/
```

## Flujo de trabajo (obligatorio)

1. Todo trabajo parte de un **Issue**.
2. Una **rama** por issue: `ciclo<N>/<rol>/<tema-corto>` (ej. `ciclo1/spec/outcomes`).
3. **Commits identificables**: `tipo(#issue): descripción` (ej. `docs(#3): define outcomes de reserva`).
4. **Pull Request** hacia `main`, revisado por otro miembro (no por el autor).
5. Cada uso de IA se registra en `docs/ai-log.md` (actividad, IA utilizada, solicitud, resultado, decisión).
6. Decisiones técnicas en `docs/decisions.md`; el stack elegido debe estar en `specs/architecture.md`.

## Checklist de entrega

- [ ] Repositorio Git, Issues, commits identificables, ramas, Pull Requests, historial
- [ ] `specs/` completo y coherente con el código
- [ ] Pruebas automatizadas: unitarias, reglas críticas, conflictos de reserva, validaciones de usuario, criterios de aceptación
- [ ] Prueba automatizada obligatoria de **no permitir doble reserva**
- [ ] `docs/ai-log.md` completo
- [ ] Evidencia del cambio de requerimiento a mitad del proyecto (cambio → specs → criterios → plan → código → pruebas → resultados)
- [ ] Material de presentación (PPT/Canva o equivalente)
- [ ] Todos preparados para presentar y recibir un cambio en vivo
