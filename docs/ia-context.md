# Contexto para asistentes de IA

Este archivo lo lee la IA de cada integrante antes de trabajar. Es la fuente de verdad del método y las reglas del proyecto.

## Proyecto

Proyecto 2 de Tópicos Especiales II (Prof. Regis Rivera): Desarrollo Orientado por Resultados (ODD) y por Especificaciones (SDD). Sistema de reservas de canchas deportivas. Grupo de 3: Kelvin He, Roy Barrera y Einer Mosquera.

Recorrido obligatorio: **ODD → SDD → código → pruebas → Resultado al Usuario (valor)**.

## Material de referencia

- `docs/material/enunciado-proyecto2.pdf`: enunciado oficial del Proyecto 2. Es la fuente de verdad de lo que se evalúa. Léelo si hay dudas sobre requisitos de entrega.
- `docs/material/presentacion.pptx`: presentación del grupo (11 diapositivas: problema y outcome, recorrido ODD → SDD, specs, flujo de Git, uso de IA, testing, cambio de especificación, rotación de roles, demo y cierre). Al avanzar el proyecto hay que mantenerla coherente con el repo y completar la demo con evidencia real.

## Entrega

Solo se entrega la presentación y el enlace del repositorio de GitHub. Todo lo evaluable (specs, issues, commits, ramas, PRs, pruebas, AI log) debe estar en el repositorio.

## Método

1. **ODD primero.** Antes de programar se define qué resultado queremos conseguir para el usuario, no qué aplicación programar. Borrador: el problema es que las reservas se coordinan por WhatsApp o llamadas, con cruces de horarios y dobles reservas. El outcome es reducir conflictos y que los usuarios encuentren franjas disponibles sin intervención del personal.
2. **SDD después.** Los resultados se convierten en especificaciones dentro de `specs/`. El código sale de las specs, no al revés. Si algo no está en `specs/`, se propone añadirlo a la spec antes de programarlo.
3. **Código y pruebas.** Stack libre, documentado en `specs/architecture.md`.

## Roles y rotación

| Ciclo | Enfoque | Product / Spec Lead | Architecture / Dev Lead | QA / DevOps Lead |
|---|---|---|---|---|
| 1 | ODD + specs | Kelvin | Roy | Einer |
| 2 | Implementación + pruebas base | Einer | Kelvin | Roy |
| 3 | Cambio de requerimiento + cierre + entrega | Roy | Einer | Kelvin |

- **Product / Spec Lead:** requisitos, outcomes, especificaciones y backlog.
- **Architecture / Development Lead:** arquitectura e implementación.
- **QA / DevOps Lead:** testing, integración y despliegue.

### Traspaso al cerrar cada ciclo

1. Todos los issues del ciclo están cerrados o reasignados, y los PRs fusionados.
2. Cada persona agrega al `docs/ai-log.md` sus entradas pendientes.
3. El líder saliente de cada rol deja un issue "Traspaso ciclo N" con: qué quedó hecho, qué quedó pendiente, decisiones tomadas y riesgos.
4. Los roles se intercambian según la tabla. La persona entrante lee el traspaso y revisa el trabajo del rol que hereda antes de continuar.

## Flujo de Git (obligatorio)

- Todo trabajo parte de un Issue.
- Una rama por issue: `ciclo<N>/<rol>/<tema-corto>` (ej. `ciclo1/spec/outcomes`). Nunca commits directos a `main`.
- Commits identificables: `tipo(#issue): descripción` (ej. `docs(#3): define outcomes de reserva`).
- Pull Request a `main`, revisado por alguien distinto al autor.

## Registro de IA (obligatorio)

Cada uso relevante de IA se registra en `docs/ai-log.md`: fecha, actividad, IA utilizada, solicitud, resultado y decisión (aceptado, corregido o rechazado, y por qué). Las decisiones técnicas van en `docs/decisions.md`. También se anotan respuestas incorrectas de la IA y cambios rechazados.

## Testing obligatorio

Como mínimo: pruebas unitarias, de reglas críticas, de conflictos de reserva, de validaciones de usuario y de criterios de aceptación. La regla de **no permitir doble reserva** (misma cancha y misma franja) debe tener una prueba automatizada. Resultados en `docs/testing.md`.

## Cambio de especificación

A mitad del desarrollo se introduce un cambio de requerimiento inesperado. Se sigue este ciclo y se deja evidencia de cada paso: cambio solicitado → actualizar specs → actualizar criterios de aceptación → actualizar plan y tareas → modificar código → modificar pruebas → ver resultados.

## Reglas para la IA

- Antes de escribir código, muestra un plan corto y espera aprobación.
- No inventes requisitos.
- Haz cambios pequeños, un issue a la vez, y di qué archivos tocaste.
- Al terminar cada tarea, entrega la fila lista para pegar en `docs/ai-log.md`.
