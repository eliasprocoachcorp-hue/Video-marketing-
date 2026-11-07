---
tarea: propuesta-distribucion
proyecto: Video-marketing-
estado: activa
creada: 2026-11-07
actualizada: 2026-11-07
---

# Propuesta: Video-marketing- como repo de distribución (espera al coach)

**Qué y para qué:** Video-factory hace los videos; este repo se ocuparía de lo que pasa
después: variantes de gancho para probar (trial reels), textos de publicación, calendario y
el registro de resultados por video. Es una **propuesta**: el objetivo del repo lo define
el coach.

## Entradas
| Fuente | Archivo / lugar | Sección | Por qué |
|---|---|---|---|
| reglas de video | `Video-factory/CLAUDE.md` | reglas del coach | ≤ 90 s, zona segura, sin dosis, citas |
| registro actual | `Video-factory/videos/ledger.csv` | todo | hoy el registro de publicados vive ahí, sin resultados |
| textos de publicación | `Video-factory/videos/<id>/copy.md` | todo | caption, títulos y citas por video |
| idea externa | `nextwork-projects/ai-video-editor-cooked` @ `881b72c` (MIT), skill `trial-reels` | solo la idea | variantes de un mismo video para probar ganchos |

## Proceso
1. El coach aprueba (o cambia) el objetivo.
2. `registro.csv` con una fila por publicación (columnas abajo); se llena a mano.
3. Trial reels: por cada video, el coach elige qué puede cambiar entre versiones según el
   tipo (historia, lista o explicación): gancho, música, primera escena o duración. Las
   variantes salen siempre de la toma cruda y del `motion.md` en Video-factory, nunca del
   archivo ya publicado.
4. Después de 3–4 semanas de datos: leer qué gancho funcionó y llevarlo como regla a
   `Video-factory/sistema/preferencias_coach.json` (con evidencia, como manda el método).

`registro.csv` propuesto:
`id_video,variante,gancho,musica,duracion_s,plataforma,fecha,url,vistas_24h,vistas_7d,guardados,compartidos,seguidores_nuevos,nota`

## Salidas
| Entrega | Dónde | Formato |
|---|---|---|
| registro de resultados | `registro.csv` | CSV |
| plan de variantes por video | `variantes/<id_video>.md` | md |
| calendario | `CALENDARIO.md` | md |

## Lo que NO se hace (seguridad)
- Nada de publicar automáticamente (Zernio u otros) ni de guardar llaves de redes sociales.
- No se instala el plugin de cooked ni su auto-update; solo se adapta la idea.
- No se descargan videos de otros creadores. El análisis de estilo ajeno vive en
  `epc-content-intel` con sus reglas (anónimo, privado, fuera del repo).

## Checkpoints (el coach decide)
- Antes de la etapa 2: ¿este es el objetivo del repo? ¿qué plataformas?
- Antes de la etapa 3: qué se puede variar en cada video.

## Estado
- 2026-11-07: propuesta escrita; nada creado todavía.

## Depende de
- Decisión del coach sobre el objetivo del repo.

## Siguiente paso
Mostrarle esta propuesta al coach.
