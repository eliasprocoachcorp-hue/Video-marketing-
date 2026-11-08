#!/usr/bin/env python3
"""Registro de resultados de cada publicación (registro.csv). Salida corta; no publica nada ni llama a ninguna red.

    python3 scripts/registro.py agregar <id_video> <variante> --plataforma instagram --fecha 2026-11-10 \\
        [--tipo-gancho pregunta] [--gancho "…"] [--musica …] [--duracion 58] [--url …] [--nota …]
    python3 scripts/registro.py medir <id_video> <variante> <plataforma> --vistas-24h 1200 [--vistas-7d 5400 --guardados 80 --compartidos 30 --seguidores 12]
    python3 scripts/registro.py resumen [--por tipo_gancho|variante|plataforma|musica|gancho]

- agregar: una fila nueva (sin números todavía); falla si ya existe la misma (id_video, variante, plataforma) o si
           la duración pasa de 90 s (P-037 de Video-factory).
- medir:   llena los números de esa fila (los mira el coach en la app de cada red y los dicta).
- resumen: por grupo, promedio de vistas a 7 días y a 24 h POR SEPARADO (con cuántas filas tiene cada uno) y de
           guardados+compartidos. Solo describe: qué gancho conviene lo decide el coach. Con menos de 3 lo avisa.

tipo_gancho es una etiqueta corta para poder comparar (pregunta, dato, historia, promesa, contraste, otro);
gancho es la frase literal. Una fila por variante y plataforma; Video-factory/videos/ledger.csv sigue siendo una
fila por video.
"""
import argparse, csv, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "registro.csv"
CAMPOS = ["id_video", "variante", "tipo_gancho", "gancho", "musica", "duracion_s", "plataforma", "fecha", "url",
          "vistas_24h", "vistas_7d", "guardados", "compartidos", "seguidores_nuevos", "nota"]
TIPOS_GANCHO = ["pregunta", "dato", "historia", "promesa", "contraste", "otro"]
MAX_DURACION_S = 90


def _limpia(fila):
    f = {k.strip(): (v or "").strip() for k, v in fila.items() if k is not None}
    f["id_video"] = f.get("id_video", "")
    f["variante"] = f.get("variante", "").upper()
    f["plataforma"] = f.get("plataforma", "").lower()
    f["tipo_gancho"] = f.get("tipo_gancho", "").lower()
    return f


def leer(ruta=REGISTRO):
    """(filas, columnas). Filas incompletas quedan con campos vacíos; columnas agregadas a mano se conservan."""
    if not Path(ruta).exists():
        return [], list(CAMPOS)
    with open(ruta, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        columnas = [c.strip() for c in (r.fieldnames or [])]
        filas = [_limpia(x) for x in r]
    extra = [c for c in columnas if c and c not in CAMPOS]
    return filas, CAMPOS + extra


def escribir(filas, ruta=REGISTRO, columnas=None):
    columnas = columnas or list(CAMPOS)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas, lineterminator="\n")
        w.writeheader()
        for fila in filas:
            w.writerow({k: fila.get(k, "") for k in columnas})


def _clave(f):
    return (f["id_video"].strip(), f["variante"].strip().upper(), f["plataforma"].strip().lower())


def agregar(filas, id_video, variante, plataforma, fecha, gancho="", musica="", duracion="", url="", nota="", tipo_gancho=""):
    if str(duracion).strip():
        if float(duracion) > MAX_DURACION_S:
            raise ValueError(f"{duracion} s pasa del máximo de {MAX_DURACION_S} s (P-037)")
    tipo = tipo_gancho.strip().lower()
    if tipo and tipo not in TIPOS_GANCHO:
        raise ValueError(f"tipo de gancho «{tipo}»: usar uno de {', '.join(TIPOS_GANCHO)}")
    nueva = _limpia({"id_video": id_video, "variante": variante, "plataforma": plataforma, "fecha": fecha, "tipo_gancho": tipo,
                     "gancho": gancho, "musica": musica, "duracion_s": str(duracion), "url": url, "nota": nota})
    if any(_clave(f) == _clave(nueva) for f in filas):
        raise ValueError(f"ya existe {nueva['id_video']} {nueva['variante']} en {nueva['plataforma']}")
    return filas + [nueva]


def medir(filas, id_video, variante, plataforma, **numeros):
    clave = (id_video.strip(), variante.strip().upper(), plataforma.strip().lower())
    for f in filas:
        if _clave(f) == clave:
            for k, v in numeros.items():
                if v is not None:
                    if int(v) < 0:
                        raise ValueError(f"{k} no puede ser negativo")
                    f[k] = str(int(v))
            return filas
    raise KeyError(f"no está en el registro: {' '.join(clave)}")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _prom(xs):
    return (sum(xs) / len(xs)) if xs else None


def resumen(filas, por="tipo_gancho"):
    """[{grupo, n, n_7d, vistas_7d, n_24h, vistas_24h, interaccion}], de más a menos vistas (7 d si hay; si no, 24 h)."""
    grupos = {}
    for f in filas:
        v7, v24 = _num(f.get("vistas_7d")), _num(f.get("vistas_24h"))
        if v7 is None and v24 is None:
            continue
        g = grupos.setdefault((f.get(por) or "").strip() or "(sin dato)", {"v7": [], "v24": [], "inter": []})
        if v7 is not None:
            g["v7"].append(v7)
        if v24 is not None:
            g["v24"].append(v24)
        g["inter"].append((_num(f.get("guardados")) or 0) + (_num(f.get("compartidos")) or 0))
    out = [{"grupo": k, "n": len(v["inter"]), "n_7d": len(v["v7"]), "vistas_7d": _prom(v["v7"]),
            "n_24h": len(v["v24"]), "vistas_24h": _prom(v["v24"]), "interaccion": _prom(v["inter"])} for k, v in grupos.items()]
    return sorted(out, key=lambda r: -(r["vistas_7d"] if r["vistas_7d"] is not None else (r["vistas_24h"] or 0)))


def main(argv=None, ruta=REGISTRO):
    ap = argparse.ArgumentParser(description="Registro de resultados de publicaciones.")
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("agregar"); a.add_argument("id_video"); a.add_argument("variante")
    a.add_argument("--plataforma", required=True); a.add_argument("--fecha", required=True)
    a.add_argument("--tipo-gancho", default=""); a.add_argument("--gancho", default=""); a.add_argument("--musica", default="")
    a.add_argument("--duracion", default=""); a.add_argument("--url", default=""); a.add_argument("--nota", default="")
    m = sp.add_parser("medir"); m.add_argument("id_video"); m.add_argument("variante"); m.add_argument("plataforma")
    for n in ("vistas-24h", "vistas-7d", "guardados", "compartidos", "seguidores"):
        m.add_argument(f"--{n}", type=int)
    r = sp.add_parser("resumen"); r.add_argument("--por", default="tipo_gancho", choices=["tipo_gancho", "variante", "plataforma", "musica", "gancho"])
    o = ap.parse_args(argv)
    filas, columnas = leer(ruta)
    try:
        if o.cmd == "agregar":
            filas = agregar(filas, o.id_video, o.variante, o.plataforma, o.fecha, o.gancho, o.musica, o.duracion, o.url, o.nota, o.tipo_gancho)
            escribir(filas, ruta, columnas)
            print(f"ok {o.id_video} {o.variante.strip().upper()} {o.plataforma.strip().lower()} agregado")
        elif o.cmd == "medir":
            escribir(medir(filas, o.id_video, o.variante, o.plataforma, vistas_24h=o.vistas_24h, vistas_7d=o.vistas_7d,
                           guardados=o.guardados, compartidos=o.compartidos, seguidores_nuevos=o.seguidores), ruta, columnas)
            print(f"ok {o.id_video} {o.variante.strip().upper()} {o.plataforma.strip().lower()} medido")
        else:
            res = resumen(filas, o.por)
            if not res:
                print("sin publicaciones medidas todavía"); return 0
            fmt = lambda v: "—" if v is None else f"{v:,.0f}"
            for g in res:
                aviso = "  (menos de 3: no concluir)" if g["n"] < 3 else ""
                print(f"{g['grupo'][:40]:40s} n={g['n']:<3d} 7d≈{fmt(g['vistas_7d'])} (n={g['n_7d']})  24h≈{fmt(g['vistas_24h'])} "
                      f"(n={g['n_24h']})  guardados+compartidos≈{fmt(g['interaccion'])}{aviso}")
    except (ValueError, KeyError) as e:
        print(f"error: {e.args[0]}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
