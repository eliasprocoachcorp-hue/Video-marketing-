# CLAUDE.md — Video marketing

Índice, no enciclopedia. Método de trabajo: skill `metodo-proyectos` (rutas en `.claude/metodo.json`;
el hook de arranque muestra estado, tareas y lecciones).

## Qué es
Distribución de los videos de Video-factory (base armada el 2026-11-07 a pedido del coach): variantes
para probar ganchos (trial reels), calendario y registro de resultados. Publica el coach a mano; nada
se publica solo ni se guardan llaves de redes. Plataformas: por confirmar.

## Dónde está cada cosa
| Necesito | Abrir |
|---|---|
| Estado vigente | `ESTADO.md` (leer primero; reemplazar, no acumular) |
| Tareas | `TAREAS/ACTIVE`, `TAREAS/BLOCKED` |
| Decisiones | `DECISIONS/` |
| Lecciones | `LECCIONES.md` |
| Resultados por publicación | `registro.csv` · `python3 scripts/registro.py agregar · medir · resumen` |
| Variantes de un video | `variantes/<id_video>.md` (plantilla `variantes/_plantilla.md`) |
| Qué se publica y cuándo | `CALENDARIO.md` |

## Fuente de verdad
código → tests → configuración → docs → historial de git → conversación. Lo que no se puede verificar: **DESCONOCIDO**.

## Reglas que no se rompen
- El coach decide; el agente organiza, ejecuta y pregunta en las decisiones de criterio.
- `git add` con rutas explícitas; sin credenciales en archivos; nada de merge/reset/force-push sin pedirlo.

## Verificar
`python3 -m unittest discover -s tests`
