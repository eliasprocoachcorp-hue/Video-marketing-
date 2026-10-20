# CLAUDE.md — <proyecto>

Índice, no enciclopedia. Método de trabajo: skill `metodo-proyectos` (rutas en `.claude/metodo.json`;
el hook de arranque muestra estado, tareas y lecciones).

## Qué es
<2–3 líneas>

## Dónde está cada cosa
| Necesito | Abrir |
|---|---|
| Estado vigente | `SESSION_CONTEXT_CURRENT.md` (leer primero; reemplazar, no acumular) |
| Tareas | `TAREAS/ACTIVE`, `TAREAS/BLOCKED` |
| Decisiones | `DECISIONS/` |
| Lecciones | `LECCIONES.md` |

## Fuente de verdad
código → tests → configuración → docs → historial de git → conversación. Lo que no se puede verificar: **DESCONOCIDO**.

## Reglas que no se rompen
- El coach decide; el agente organiza, ejecuta y pregunta en las decisiones de criterio.
- `git add` con rutas explícitas; sin credenciales en archivos; nada de merge/reset/force-push sin pedirlo.

## Verificar
<comando>
