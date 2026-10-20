#!/usr/bin/env python3
"""Arranque del método (hook SessionStart): imprime en pocas líneas dónde quedó el proyecto.

Lee `.claude/metodo.json` del repo y muestra el estado vigente, las tareas activas y bloqueadas
y las lecciones más recientes. No escribe nada y no falla: si algo falta, lo dice y sigue.
Uso: python3 .claude/skills/metodo-proyectos/scripts/arranque.py [raiz_del_repo]
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_TAREAS = 6
MAX_LECCIONES = 3
TOPE_ESTADO_KB = 30


def raiz() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    return Path(env).resolve() if env else Path(__file__).resolve().parents[4]


def ultima_fecha(r: Path, ruta: str) -> str:
    try:
        superficial = subprocess.run(["git", "-C", str(r), "rev-parse", "--is-shallow-repository"],
                                     capture_output=True, text=True, timeout=5).stdout.strip()
        if superficial == "true":
            return "sin fecha (clon superficial)"
        out = subprocess.run(["git", "-C", str(r), "log", "-1", "--format=%cs", "--", ruta],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        return out or "sin commits"
    except Exception:
        return "?"


def siguiente_paso(texto: str) -> str:
    m = re.search(r"^##\s*(Siguiente paso|Next step)s?\s*\n+(.+)", texto, re.M | re.I)
    if not m:
        # tareas viejas sin la sección: mostrar su línea de estado
        m = re.search(r"^\*\*(Estado|Status):\*\*\s*(.+)", texto, re.M | re.I)
        return ("estado: " + m.group(2).strip()[:100]) if m else ""
    linea = m.group(2).strip().lstrip("-*0123456789. ").strip()
    return linea[:110]


def tareas(r: Path, cfg: dict) -> list[str]:
    t = cfg.get("tareas")
    if not t:
        return []
    p = r / t
    if p.is_file():
        return [f"tareas: {t} (lista única)"]
    if not p.is_dir():
        return [f"tareas: {t} NO EXISTE"]
    lineas = []
    for estado, carpeta in (("activa", "ACTIVE"), ("bloqueada", "BLOCKED")):
        d = p / carpeta
        archivos = sorted(d.glob("*.md")) if d.is_dir() else []
        for f in archivos[:MAX_TAREAS]:
            paso = siguiente_paso(f.read_text(encoding="utf-8", errors="ignore"))
            lineas.append(f"  [{estado}] {f.stem}" + (f" → {paso}" if paso else ""))
        if len(archivos) > MAX_TAREAS:
            lineas.append(f"  … y {len(archivos) - MAX_TAREAS} {estado}s más en {t}/{carpeta}/")
    return [f"tareas ({t}):"] + (lineas or ["  ninguna activa ni bloqueada"])


def lecciones(r: Path, cfg: dict) -> list[str]:
    l = cfg.get("lecciones")
    if not l or not (r / l).is_file():
        return [f"lecciones: {l or '—'} NO EXISTE"]
    texto = (r / l).read_text(encoding="utf-8", errors="ignore")
    bloques = re.split(r"^### ", texto, flags=re.M)[1:]
    out = [f"lecciones ({l}, {len(bloques)}):"]
    for b in bloques[:MAX_LECCIONES]:
        titulo = b.splitlines()[0].strip()
        m = re.search(r"\*\*Señal:\*\*\s*(.+)", b)
        out.append(f"  - {titulo}" + (f" — señal: {m.group(1).strip()[:90]}" if m else ""))
    return out


def main() -> None:
    r = raiz()
    cfg_path = r / ".claude" / "metodo.json"
    if not cfg_path.is_file():
        print("método: falta .claude/metodo.json — ver skill metodo-proyectos §8 (proyecto nuevo)")
        return
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"método: .claude/metodo.json ilegible ({e})")
        return
    print(f"MÉTODO metodo-proyectos · proyecto: {cfg.get('proyecto', r.name)}")
    mapa = cfg.get("mapa") or []
    if mapa:
        print("ubicarse: " + " → ".join(mapa))
    e = cfg.get("estado")
    if e:
        p = r / e
        if p.is_file():
            kb = p.stat().st_size / 1024
            aviso = f" — PASA DE {TOPE_ESTADO_KB} KB: resumir antes de agregar" if kb > TOPE_ESTADO_KB else ""
            print(f"estado: {e} ({kb:.0f} KB, último cambio {ultima_fecha(r, e)}){aviso}")
        else:
            print(f"estado: {e} NO EXISTE")
    for linea in tareas(r, cfg) + lecciones(r, cfg):
        print(linea)
    if cfg.get("nota"):
        print(f"nota: {cfg['nota']}")
    if cfg.get("verificar"):
        print(f"verificar: {cfg['verificar']}")
    print("ciclo: ubicarse → tarea con contrato → etapas (el coach decide) → verificar → cerrar → lección con evidencia")


if __name__ == "__main__":
    try:  # consola de Windows (cp1252): que las flechas y tildes no rompan la salida
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        main()
    except Exception as exc:  # el arranque nunca debe romper la sesión
        print(f"método: arranque con error ({exc}); seguir con CLAUDE.md")
