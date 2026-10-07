import csv
import json
import os
import tempfile
import unittest

from PIL import Image

from core.adaptador_imagenes import (
    ErrorEvidencia,
    evaluar,
    generar_png,
    leer_evidencia,
    origen_exif,
)
from core.cdr_seguridad import (
    ErrorCDRProtegido,
    borrar_cdr,
    modificar_cdr,
    mover_cdr,
    renombrar_cdr,
    sobrescribir_cdr,
)
from core.sublitex import validar_codigo

MAPA = {"entradas": {"03": "D:/Drive Sublitex/Diseno 03"}}

EVIDENCIA_A = {
    "codigo": "SBX-03-0005",
    "carpeta_origen": "03",
    "archivo_original": "camiseta_0005.cdr",
    "tipo": "camiseta",
    "deporte": "futbol",
    "ocasion": "interclase",
    "estado": "aprobado",
    "quien": "Ana",
    "fecha": "2026-10-01",
}


def _crear_jpg(ruta, artista=None):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    imagen = Image.new("RGB", (8, 8), (200, 30, 30))
    if artista:
        exif = Image.Exif()
        exif[315] = artista
        imagen.save(ruta, "JPEG", exif=exif)
    else:
        imagen.save(ruta, "JPEG")
    return ruta


def _crear_cdr(ruta):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "wb") as f:
        f.write(b"\x00CDR-SUBLITEX-ORIGINAL\x00")
    return ruta


class TestEvidencia(unittest.TestCase):
    def test_leer_evidencia_json_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "evidencia.json")
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump({"A.jpg": EVIDENCIA_A}, f)
            evidencia = leer_evidencia(ruta)
            self.assertEqual(evidencia["A"]["codigo"], "SBX-03-0005")
            self.assertEqual(evidencia["A"]["carpeta_origen"], "03")

    def test_leer_evidencia_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = os.path.join(tmp, "evidencia.csv")
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["imagen_jpg", "codigo", "carpeta_origen", "archivo_original",
                                "tipo", "deporte", "ocasion", "estado", "quien", "fecha"],
                )
                writer.writeheader()
                fila = dict(EVIDENCIA_A)
                fila["imagen_jpg"] = "A.jpg"
                writer.writerow(fila)
            evidencia = leer_evidencia(ruta)
            self.assertEqual(evidencia["A"]["codigo"], "SBX-03-0005")

    def test_leer_evidencia_sin_archivo(self):
        with self.assertRaises(ErrorEvidencia):
            leer_evidencia("no_existe.json")


class TestIntegracionVerificada(unittest.TestCase):
    """Escenarios 1-5: una imagen con evidencia recibe codigo, conserva
    carpeta_origen y archivo_original, localiza su CDR y genera su PNG."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _jpeg(self):
        return _crear_jpg(os.path.join(self.tmp.name, "A.jpg"))

    def test_1_recibe_codigo_sbx_valido(self):
        resultado = evaluar(self._jpeg(), {"A": dict(EVIDENCIA_A)}, MAPA)
        self.assertEqual(resultado["estado"], "verificado")
        self.assertTrue(validar_codigo(resultado["registro"]["codigo"]))
        self.assertEqual(resultado["registro"]["codigo"], "SBX-03-0005")

    def test_2_carpeta_origen_conservada(self):
        resultado = evaluar(self._jpeg(), {"A": dict(EVIDENCIA_A)}, MAPA)
        self.assertEqual(resultado["registro"]["carpeta_origen"], "03")

    def test_3_archivo_original_conservado(self):
        resultado = evaluar(self._jpeg(), {"A": dict(EVIDENCIA_A)}, MAPA)
        self.assertEqual(resultado["registro"]["archivo_original"], "camiseta_0005.cdr")

    def test_4_cdr_localizable(self):
        resultado = evaluar(self._jpeg(), {"A": dict(EVIDENCIA_A)}, MAPA)
        self.assertEqual(
            resultado["registro"]["ruta_cdr"],
            os.path.join("D:/Drive Sublitex/Diseno 03", "camiseta_0005.cdr"),
        )

    def test_5_png_generado_con_codigo_sin_tocar_jpg(self):
        jpg = self._jpeg()
        antes = open(jpg, "rb").read()
        destino = os.path.join(self.tmp.name, "salida")
        png = generar_png(jpg, "SBX-03-0005", destino)
        self.assertEqual(os.path.basename(png), "SBX-03-0005.png")
        self.assertTrue(os.path.isfile(png))
        with open(png, "rb") as f:
            self.assertEqual(f.read(8), b"\x89PNG\r\n\x1a\n")
        self.assertTrue(os.path.isfile(jpg), "el JPG original no se debe destruir")
        self.assertEqual(open(jpg, "rb").read(), antes, "el JPG original no se debe modificar")

    def test_png_rechaza_codigo_no_valido(self):
        with self.assertRaises(ValueError):
            generar_png(self._jpeg(), "SBX-3-0005", self.tmp.name)


class TestIntegracionSinEvidencia(unittest.TestCase):
    """Escenario 6: sin origen verificable NO se inventa codigo ni PNG."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_6_sin_evidencia_no_inventa_codigo_ni_png(self):
        jpg = _crear_jpg(os.path.join(self.tmp.name, "B.jpg"))
        resultado = evaluar(jpg, {}, MAPA)
        self.assertEqual(resultado["estado"], "pendiente")
        self.assertNotIn("codigo", resultado)
        self.assertTrue(resultado["info_faltante"])
        self.assertTrue(
            any("planilla" in texto for texto in resultado["info_faltante"])
        )
        salida = os.path.join(self.tmp.name, "salida")
        pngs = [n for n in os.listdir(salida) if n.lower().endswith(".png")] if os.path.isdir(salida) else []
        self.assertEqual(pngs, [], "no se debe publicar PNG para una imagen pendiente")

    def test_no_asignacion_por_orden(self):
        a = _crear_jpg(os.path.join(self.tmp.name, "X 1.jpg"))
        b = _crear_jpg(os.path.join(self.tmp.name, "X 2.jpg"))
        ra = evaluar(a, {}, MAPA)
        rb = evaluar(b, {}, MAPA)
        self.assertEqual(ra["estado"], "pendiente")
        self.assertEqual(rb["estado"], "pendiente")
        self.assertNotEqual(ra, rb)  # nunca se genera SBX-03-0001, SBX-03-0002 por orden

    def test_evidencia_incompleta_marca_pendiente(self):
        fila = dict(EVIDENCIA_A)
        fila["archivo_original"] = ""
        jpg = _crear_jpg(os.path.join(self.tmp.name, "A.jpg"))
        resultado = evaluar(jpg, {"A": fila}, MAPA)
        self.assertEqual(resultado["estado"], "pendiente")
        self.assertTrue(any("archivo_original" in t for t in resultado["info_faltante"]))

    def test_evidencia_con_codigo_invalido_pendiente(self):
        fila = dict(EVIDENCIA_A)
        fila["codigo"] = "SBX-3-147"
        jpg = _crear_jpg(os.path.join(self.tmp.name, "A.jpg"))
        resultado = evaluar(jpg, {"A": fila}, MAPA)
        self.assertEqual(resultado["estado"], "pendiente")

    def test_evidencia_sin_mapa_de_listas_pendiente(self):
        jpg = _crear_jpg(os.path.join(self.tmp.name, "A.jpg"))
        resultado = evaluar(jpg, {"A": dict(EVIDENCIA_A)}, None)
        self.assertEqual(resultado["estado"], "pendiente")
        self.assertTrue(any("Listas" in t or "mapa" in t for t in resultado["info_faltante"]))


class TestOrigenExif(unittest.TestCase):
    def test_exif_terceros_registrado_como_origen_auxiliar(self):
        with tempfile.TemporaryDirectory() as tmp:
            jpg = _crear_jpg(os.path.join(tmp, "C.jpg"), artista="www.vectorsport.net")
            exif = origen_exif(jpg)
            self.assertEqual(exif["artista"], "www.vectorsport.net")

    def test_exif_sin_datos_no_falla(self):
        with tempfile.TemporaryDirectory() as tmp:
            jpg = _crear_jpg(os.path.join(tmp, "D.jpg"))
            exif = origen_exif(jpg)
            self.assertEqual(exif, {"artista": "", "descripcion": "", "software": ""})


class TestCDRProtegido(unittest.TestCase):
    """Escenario 7: ningun CDR original puede renombrarse, moverse, borrarse
    ni sobrescribirse."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cdr = _crear_cdr(os.path.join(self.tmp.name, "original.cdr"))
        self.contenido = open(self.cdr, "rb").read()

    def test_7a_renombrar_bloqueado(self):
        with self.assertRaises(ErrorCDRProtegido):
            renombrar_cdr(self.cdr, os.path.join(self.tmp.name, "otro.cdr"))
        self.assertEqual(open(self.cdr, "rb").read(), self.contenido)

    def test_7b_mover_bloqueado(self):
        with self.assertRaises(ErrorCDRProtegido):
            mover_cdr(self.cdr, os.path.join(self.tmp.name, "sub", "original.cdr"))
        self.assertTrue(os.path.isfile(self.cdr))

    def test_7c_borrar_bloqueado(self):
        with self.assertRaises(ErrorCDRProtegido):
            borrar_cdr(self.cdr)
        self.assertTrue(os.path.isfile(self.cdr))

    def test_7d_sobrescribir_bloqueado(self):
        with self.assertRaises(ErrorCDRProtegido):
            sobrescribir_cdr(self.cdr, b"malicioso")
        self.assertEqual(open(self.cdr, "rb").read(), self.contenido)

    def test_7e_modificar_bloqueado(self):
        with self.assertRaises(ErrorCDRProtegido):
            modificar_cdr(self.cdr)
        self.assertEqual(open(self.cdr, "rb").read(), self.contenido)

    def test_copia_segura_permitida(self):
        from core.cdr_seguridad import copiar_cdr, verificar_cdr_inmutable

        copia = copiar_cdr(self.cdr, os.path.join(self.tmp.name, "copia.cdr"))
        self.assertTrue(os.path.isfile(self.cdr))
        self.assertTrue(verificar_cdr_inmutable(self.cdr, copia))


if __name__ == "__main__":
    unittest.main()