#!/usr/bin/env python3
"""Registro de resultados de cada publicación (registro.csv). Salida corta; no publica nada ni llama a ninguna red.

    python3 scripts/registro.py agregar <id_video> <variante> --gancho "…" --plataforma instagram --fecha 2026-11-10 [--url …] [--musica …] [--duracion 58]
    python3 scripts/registro.py medir <id_video> <variante> <plataforma> --vistas-24h 1200 [--vistas-7d 5400 --guardados 80 --compartidos 30 --seguidores 12]
    python3 scripts/registro.py resumen [--por gancho|variante|plataforma|musica]

- agregar: una fila nueva (sin números todavía); falla si ya existe la misma (id_video, variante, plataforma).
- medir:   llena los números de esa fila (los mira el coach en la app de cada red y los dicta).
- resumen: promedio de vistas a 7 días (o a 24 h si no hay 7 d) y de guardados+compartidos, agrupado.
           Solo describe: qué gancho conviene lo decide el coach. Con menos de 3 publicaciones por grupo lo avisa.
"""
import argparse, csv, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "registro.csv"
CAMPOS = ["id_video", "variante", "gancho", "musica", "duracion_s", "plataforma", "fecha", "url",
          "vistas_24h", "vistas_7d", "guardados", "compartidos", "seguidores_nuevos", "nota"]
NUMEROS = ["duracion_s", "vistas_24h", "vistas_7d", "guardados", "compartidos", "seguidores_nuevos"]


def leer(ruta=REGISTRO):
    if not Path(ruta).exists():
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def escribir(filas, ruta=REGISTRO):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        for fila in filas:
            w.writerow({k: fila.get(k, "") for k in CAMPOS})


def _clave(f):
    return (f["id_video"], f["variante"].upper(), f["plataforma"].lower())


def agregar(filas, id_video, variante, plataforma, fecha, gancho="", musica="", duracion="", url="", nota=""):
    nueva = {"id_video": id_video, "variante": variante.upper(), "plataforma": plataforma.lower(), "fecha": fecha,
             "gancho": gancho, "musica": musica, "duracion_s": duracion, "url": url, "nota": nota}
    if any(_clave(f) == _clave(nueva) for f in filas):
        raise ValueError(f"ya existe {id_video} {variante.upper()} en {plataforma.lower()}")
    return filas + [nueva]


def medir(filas, id_video, variante, plataforma, **numeros):
    clave = (id_video, variante.upper(), plataforma.lower())
    for f in filas:
        if _clave(f) == clave:
            for k, v in numeros.items():
                if v is not None:
                    if int(v) < 0:
                        raise ValueError(f"{k} no puede ser negativo")
                    f[k] = str(int(v))
            return filas
    raise KeyError(f"no está en el registro: {id_video} {variante.upper()} {plataforma.lower()}")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def resumen(filas, por="gancho"):
    """[(grupo, n, vistas_promedio, interaccion_promedio)], de más a menos vistas. Solo filas con algún número."""
    grupos = {}
    for f in filas:
        vistas = _num(f.get("vistas_7d")) if _num(f.get("vistas_7d")) is not None else _num(f.get("vistas_24h"))
        if vistas is None:
            continue
        inter = (_num(f.get("guardados")) or 0) + (_num(f.get("compartidos")) or 0)
        g = grupos.setdefault((f.get(por) or "(sin dato)").strip(), [])
        g.append((vistas, inter))
    out = [(k, len(v), sum(x for x, _ in v) / len(v), sum(y for _, y in v) / len(v)) for k, v in grupos.items()]
    return sorted(out, key=lambda r: -r[2])


def main(argv=None, ruta=REGISTRO):
    ap = argparse.ArgumentParser(description="Registro de resultados de publicaciones.")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("agregar"); a.add_argument("id_video"); a.add_argument("variante")
    a.add_argument("--plataforma", required=True); a.add_argument("--fecha", required=True)
    a.add_argument("--gancho", default=""); a.add_argument("--musica", default=""); a.add_argument("--duracion", default="")
    a.add_argument("--url", default=""); a.add_argument("--nota", default="")
    m = sp.add_parser("medir"); m.add_argument("id_video"); m.add_argument("variante"); m.add_argument("plataforma")
    for n in ("vistas-24h", "vistas-7d", "guardados", "compartidos", "seguidores"):
        m.add_argument(f"--{n}", type=int)
    r = sp.add_parser("resumen"); r.add_argument("--por", default="gancho", choices=["gancho", "variante", "plataforma", "musica"])
    o = ap.parse_args(argv)
    filas = leer(ruta)
    try:
        if o.cmd == "agregar":
            escribir(agregar(filas, o.id_video, o.variante, o.plataforma, o.fecha, o.gancho, o.musica, o.duracion, o.url, o.nota), ruta)
            print(f"ok {o.id_video} {o.variante.upper()} {o.plataforma.lower()} agregado")
        elif o.cmd == "medir":
            escribir(medir(filas, o.id_video, o.variante, o.plataforma, vistas_24h=o.vistas_24h, vistas_7d=o.vistas_7d,
                           guardados=o.guardados, compartidos=o.compartidos, seguidores_nuevos=o.seguidores), ruta)
            print(f"ok {o.id_video} {o.variante.upper()} {o.plataforma.lower()} medido")
        else:
            res = resumen(filas, o.por)
            if not res:
                print("sin publicaciones medidas todavía"); return 0
            for g, n, v, i in res:
                aviso = "  (menos de 3: no concluir)" if n < 3 else ""
                print(f"{g[:50]:50s} n={n:<3d} vistas≈{v:,.0f}  guardados+compartidos≈{i:,.0f}{aviso}")
    except (ValueError, KeyError) as e:
        print(f"error: {e.args[0]}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
