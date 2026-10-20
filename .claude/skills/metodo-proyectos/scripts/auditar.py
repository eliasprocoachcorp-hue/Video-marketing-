#!/usr/bin/env python3
"""Auditoría del método: revisa que el repo cumpla la estructura sin usar el modelo.

Comprueba que existan las rutas de `.claude/metodo.json`, el tamaño de `CLAUDE.md` y del estado,
que cada tarea activa diga su siguiente paso y que cada lección tenga evidencia.
Imprime una línea por hallazgo. Sale con 1 solo si se pasa --estricto y hay avisos.
Uso: python3 .claude/skills/metodo-proyectos/scripts/auditar.py [raiz] [--estricto]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOPE_CLAUDE_LINEAS = 200
TOPE_ESTADO_KB = 30
CAMPOS = ("proyecto", "estado", "lecciones")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    estricto = "--estricto" in sys.argv
    r = Path(args[0]).resolve() if args else Path(__file__).resolve().parents[4]
    avisos: list[str] = []

    cfg_path = r / ".claude" / "metodo.json"
    if not cfg_path.is_file():
        print("AVISO falta .claude/metodo.json")
        return 1 if estricto else 0
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    for c in CAMPOS:
        if not cfg.get(c):
            avisos.append(f"metodo.json sin '{c}'")

    rutas = list(cfg.get("mapa") or []) + [cfg.get(k) for k in ("estado", "tareas", "decisiones", "lecciones")]
    for ruta in filter(None, rutas):
        if not (r / ruta).exists():
            avisos.append(f"no existe {ruta}")

    claude = r / "CLAUDE.md"
    if not claude.is_file():
        avisos.append("falta CLAUDE.md")
    else:
        n = len(claude.read_text(encoding="utf-8").splitlines())
        if n > TOPE_CLAUDE_LINEAS:
            avisos.append(f"CLAUDE.md tiene {n} líneas (tope {TOPE_CLAUDE_LINEAS}): mover contenido a docs")
        if "metodo-proyectos" not in claude.read_text(encoding="utf-8"):
            avisos.append("CLAUDE.md no menciona metodo-proyectos")

    e = cfg.get("estado")
    if e and (r / e).is_file() and (r / e).stat().st_size / 1024 > TOPE_ESTADO_KB:
        avisos.append(f"{e} pasa de {TOPE_ESTADO_KB} KB: resumir (estado = solo lo vigente)")

    t = cfg.get("tareas")
    if t and (r / t / "ACTIVE").is_dir():
        for f in sorted((r / t / "ACTIVE").glob("*.md")):
            if not re.search(r"^##\s*(Siguiente paso|Next step)", f.read_text(encoding="utf-8"), re.M | re.I):
                avisos.append(f"tarea sin 'Siguiente paso': {f.relative_to(r)}")

    l = cfg.get("lecciones")
    if l and (r / l).is_file():
        for b in re.split(r"^### ", (r / l).read_text(encoding="utf-8"), flags=re.M)[1:]:
            m = re.search(r"\*\*Evidencia:\*\*\s*(.*)", b)
            if not m or not m.group(1).strip() or m.group(1).strip().startswith("<"):
                avisos.append(f"lección sin evidencia: {b.splitlines()[0].strip()}")

    hooks = r / ".claude" / "settings.json"
    if not (hooks.is_file() and "metodo-proyectos/scripts/arranque.py" in hooks.read_text(encoding="utf-8")):
        avisos.append(".claude/settings.json no corre arranque.py en SessionStart")

    for a in avisos:
        print(f"AVISO {a}")
    print(f"auditoría: {'OK' if not avisos else f'{len(avisos)} aviso(s)'} · {cfg.get('proyecto', r.name)}")
    return 1 if (estricto and avisos) else 0


if __name__ == "__main__":
    try:  # consola de Windows (cp1252): que las flechas y tildes no rompan la salida
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
