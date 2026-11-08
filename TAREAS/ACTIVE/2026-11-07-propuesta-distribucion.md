---
tarea: propuesta-distribucion
proyecto: Video-marketing-
estado: activa
creada: 2026-11-07
actualizada: 2026-11-07
---

# Video-marketing- como repo de distribución

**Qué y para qué:** Video-factory hace los videos; este repo se ocuparía de lo que pasa
después: variantes de gancho para probar (trial reels), textos de publicación, calendario y
el registro de resultados por video. La base se armó a pedido del coach (2026-11-07);
plataformas y qué variar en cada video los decide él.

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
4. Después de 3–4 semanas de datos: mostrarle al coach qué tipo de gancho funcionó
   (`registro.py resumen`) y, **si él lo aprueba**, llevarlo como regla a
   `Video-factory/sistema/preferencias_coach.json` (con evidencia, como manda el método).

`registro.csv` propuesto:
`id_video,variante,tipo_gancho,gancho,musica,duracion_s,plataforma,fecha,url,vistas_24h,vistas_7d,guardados,compartidos,seguidores_nuevos,nota`

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
- Antes de la etapa 2: ¿este es el objetivo del repo? → el coach pidió el 2026-11-07 «haz todo lo
  que se pueda» y se armó la base; **confirmarlo con él al mostrarla**. ¿Qué plataformas? → pendiente.
- Antes de la etapa 3: qué se puede variar en cada video.
- Antes de llevar un resultado a `preferencias_coach.json`: que el coach lo apruebe.

## Estado
- 2026-11-07: base armada (`registro.csv`, `scripts/registro.py` con 5 tests, `variantes/_plantilla.md`,
  `CALENDARIO.md`). Objetivo por confirmar con el coach al mostrársela; plataformas sin confirmar.

## Depende de
- El coach: plataformas y qué variar en el primer video.

## Siguiente paso
Elegir con el coach el primer video y llenar `variantes/<id_video>.md`.
