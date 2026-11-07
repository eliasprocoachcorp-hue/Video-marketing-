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
                                     "--gancho", "¿Más testosterona y pechos?"), 0)
        self.assertEqual(self.correr("medir", "gyno-001", "A", "instagram", "--vistas-24h", "1200", "--guardados", "40"), 0)
        f = R.leer(self.ruta)[0]
        self.assertEqual((f["variante"], f["plataforma"], f["vistas_24h"], f["guardados"]), ("A", "instagram", "1200", "40"))

    def test_no_duplica_ni_mide_lo_que_no_existe(self):
        self.correr("agregar", "v1", "A", "--plataforma", "instagram", "--fecha", "2026-11-10")
        self.assertEqual(self.correr("agregar", "v1", "a", "--plataforma", "INSTAGRAM", "--fecha", "2026-11-11"), 1)
        self.assertEqual(self.correr("medir", "v1", "B", "instagram", "--vistas-24h", "5"), 1)
        self.assertEqual(self.correr("medir", "v1", "A", "instagram", "--vistas-24h", "-5"), 1)
        self.assertEqual(len(R.leer(self.ruta)), 1)

    def test_resumen_prefiere_7_dias_y_ordena(self):
        filas = [
            {"gancho": "pregunta", "vistas_24h": "100", "vistas_7d": "900", "guardados": "10", "compartidos": "5"},
            {"gancho": "pregunta", "vistas_24h": "300", "vistas_7d": "", "guardados": "", "compartidos": ""},
            {"gancho": "dato", "vistas_24h": "50", "vistas_7d": "200", "guardados": "1", "compartidos": "1"},
            {"gancho": "sin medir", "vistas_24h": "", "vistas_7d": ""},
        ]
        res = R.resumen(filas, "gancho")
        self.assertEqual([r[0] for r in res], ["pregunta", "dato"])     # la fila sin números no cuenta
        self.assertEqual(res[0][1:3], (2, 600.0))                       # (900 + 300) / 2
        self.assertEqual(res[0][3], 7.5)


if __name__ == "__main__":
    unittest.main()
