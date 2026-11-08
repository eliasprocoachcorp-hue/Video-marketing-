"""scripts/registro.py — se corre con: python3 -m unittest discover -s tests"""
import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import registro as R  # noqa: E402


class Registro(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ruta = Path(self.tmp.name) / "registro.csv"
        R.escribir([], self.ruta)

    def tearDown(self):
        self.tmp.cleanup()

    def correr(self, *args):
        return R.main(list(args), ruta=self.ruta)

    def test_agregar_medir_y_leer(self):
        self.assertEqual(self.correr("agregar", "gyno-001", "a", "--plataforma", "Instagram", "--fecha", "2026-11-10",
                                     "--tipo-gancho", "Pregunta", "--gancho", "¿Más testosterona y pechos?", "--duracion", "58"), 0)
        self.assertEqual(self.correr("medir", "gyno-001", "A", "instagram", "--vistas-24h", "1200", "--guardados", "40"), 0)
        f = R.leer(self.ruta)[0][0]
        self.assertEqual((f["variante"], f["plataforma"], f["tipo_gancho"], f["vistas_24h"], f["guardados"]),
                         ("A", "instagram", "pregunta", "1200", "40"))

    def test_no_duplica_aunque_cambien_espacios_o_mayusculas(self):
        self.correr("agregar", "v1", "A", "--plataforma", "instagram", "--fecha", "2026-11-10")
        self.assertEqual(self.correr("agregar", " v1 ", "a", "--plataforma", "INSTAGRAM ", "--fecha", "2026-11-11"), 1)
        self.assertEqual(self.correr("medir", "v1", "B", "instagram", "--vistas-24h", "5"), 1)
        self.assertEqual(self.correr("medir", "v1", "A", "instagram", "--vistas-24h", "-5"), 1)
        self.assertEqual(len(R.leer(self.ruta)[0]), 1)

    def test_reglas_de_entrada(self):
        self.assertEqual(self.correr("agregar", "v2", "A", "--plataforma", "tiktok", "--fecha", "2026-11-10", "--duracion", "95"), 1, "P-037")
        self.assertEqual(self.correr("agregar", "v2", "A", "--plataforma", "tiktok", "--fecha", "2026-11-10", "--tipo-gancho", "raro"), 1)
        self.assertEqual(self.correr("agregar", "v2", "A", "--plataforma", "tiktok", "--fecha", "2026-11-10", "--duracion", "90"), 0)

    def test_fila_incompleta_y_columna_a_mano_no_rompen(self):
        self.ruta.write_text(",".join(R.CAMPOS) + ",mi_columna\nv3,B\nv4,A,dato,,,,instagram,2026-11-01,,10,,,,,,hola\n", encoding="utf-8")
        self.assertEqual(self.correr("medir", "v4", "A", "instagram", "--vistas-7d", "500"), 0)
        filas, columnas = R.leer(self.ruta)
        self.assertIn("mi_columna", columnas)
        self.assertEqual([f["id_video"] for f in filas], ["v3", "v4"])
        self.assertEqual(filas[1]["mi_columna"], "hola")
        self.assertEqual(self.correr("resumen"), 0)

    def test_resumen_separa_7_dias_de_24_horas(self):
        filas = [
            {"tipo_gancho": "pregunta", "vistas_24h": "100", "vistas_7d": "900", "guardados": "10", "compartidos": "5"},
            {"tipo_gancho": "pregunta", "vistas_24h": "300", "vistas_7d": "", "guardados": "", "compartidos": ""},
            {"tipo_gancho": "dato", "vistas_24h": "50", "vistas_7d": "200", "guardados": "1", "compartidos": "1"},
            {"tipo_gancho": "sin medir", "vistas_24h": "", "vistas_7d": ""},
        ]
        res = R.resumen(filas)
        self.assertEqual([r["grupo"] for r in res], ["pregunta", "dato"])        # la fila sin números no cuenta
        p = res[0]
        self.assertEqual((p["n"], p["n_7d"], p["vistas_7d"], p["n_24h"], p["vistas_24h"]), (2, 1, 900.0, 2, 200.0))
        self.assertEqual(p["interaccion"], 7.5)


if __name__ == "__main__":
    unittest.main()
