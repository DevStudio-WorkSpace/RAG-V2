"""
tests/test_sublitex.py
----------------------
Cobertura del contrato de datos Sublitex (SECCION 00) y de la politica
CDR SOLO LECTURA. Ejecutar con:

    python -m unittest discover -s tests

Formato de codigo oficial (SECCION 00 / Tarea 1 "El cargador"):
SBX-NN-NNNN (^SBX-\\d{2}-\\d{4}$): NN = carpeta de origen (01..99),
NNNN = correlativo dentro de la carpeta (0001..9999). Ej.: SBX-03-0147.
El numero de carpeta del codigo DEBE coincidir con la columna
carpeta_origen y resolverse con la hoja Listas.
"""

import csv
import os
import shutil
import sys
import tempfile
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.cdr_seguridad import (
    ErrorCDRProtegido,
    borrar_cdr,
    copiar_cdr,
    modificar_cdr,
    mover_cdr,
    renombrar_cdr,
    sobrescribir_cdr,
    verificar_cdr_inmutable,
)
from core.sublitex import (
    COLUMNAS_PLANILLA,
    ErrorCodigo,
    ErrorTrazabilidad,
    carpeta_real,
    descomponer_codigo,
    enriquecer_registro,
    generar_codigo,
    leer_mapa,
    leer_planilla,
    localizar_cdr_por_codigo,
    validar_codigo,
    validar_registro,
)

COLUMNAS = COLUMNAS_PLANILLA


class TestCodigos(unittest.TestCase):

    def test_generar_codigo_formato_esperado(self):
        self.assertEqual(generar_codigo(3, 147), "SBX-03-0147")
        self.assertEqual(generar_codigo(3, 1), "SBX-03-0001")
        self.assertEqual(generar_codigo(12, 1025), "SBX-12-1025")
        self.assertTrue(validar_codigo("SBX-03-0147"))

    def test_generar_codigo_bordes_y_errores(self):
        self.assertEqual(generar_codigo(99, 9999), "SBX-99-9999")
        self.assertEqual(generar_codigo(1, 1), "SBX-01-0001")
        with self.assertRaises(ErrorCodigo):
            generar_codigo(0, 1)
        with self.assertRaises(ErrorCodigo):
            generar_codigo(100, 1)
        with self.assertRaises(ErrorCodigo):
            generar_codigo(3, 0)
        with self.assertRaises(ErrorCodigo):
            generar_codigo(3, 10000)
        with self.assertRaises(ErrorCodigo):
            generar_codigo("tres", 1)

    def test_descomponer_codigo_devuelve_carpeta_y_correlativo(self):
        self.assertEqual(descomponer_codigo("SBX-03-0147"), (3, 147))
        self.assertEqual(descomponer_codigo("SBX-12-1025"), (12, 1025))

    def test_codigo_sbx_03_0147_valido(self):
        self.assertTrue(validar_codigo("SBX-03-0147"))

    def test_codigos_invalidos_incluidos_formatos_antiguos(self):
        for malo in (
            "SBX-00001",
            "SBX-0147",
            "SBX-3-147",
            "SBX-03-147",
            "SBX-000147",
            "SBX-03-0147.png",
            "sbx-03-0147",
            "SBX_03_0147",
            "Argentina.png",
            "SBX-03-014A",
            "SBX-03-0147-extra",
            "camiseta03",
        ):
            self.assertFalse(validar_codigo(malo), malo)
            with self.assertRaises(ErrorCodigo):
                descomponer_codigo(malo)


class TestTrazabilidad(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="test_sublitex_")
        cls.carpeta_cdr = os.path.join(cls.tmp, "Drive", "Carpeta-03")
        os.makedirs(cls.carpeta_cdr, exist_ok=True)
        cls.cdr_original = os.path.join(cls.carpeta_cdr, "046.cdr")
        with open(cls.cdr_original, "wb") as f:
            f.write(b"DATOS-CDR-ORIGINAL-046")
        cls.planilla_csv = os.path.join(cls.tmp, "Control de exportacion.csv")
        cls.mapa_csv = os.path.join(cls.tmp, "listas.csv")
        cls._escribir_fixtures()
        cls.lectura_csv = leer_planilla(cls.planilla_csv)
        cls.filas = cls.lectura_csv["filas"]
        cls.mapa_csv_map = leer_mapa(None, "Listas", cls.mapa_csv)
        cls.xlsx = cls._generar_xlsx()

    @classmethod
    def _escribir_fixtures(cls):
        filas = [
            ["SBX-03-0001", "03", "046.cdr", "tipo", "deporte", "ocasion", "estado", "a", "2026-10-07"],
            ["SBX-03-0002", "03", "047.cdr", "tipo", "deporte", "ocasion", "estado", "b", "2026-10-07"],
            ["SBX-04-0002", "04", "002.cdr", "tipo", "deporte", "ocasion", "estado", "c", "2026-10-07"],
        ]
        with open(cls.planilla_csv, "w", encoding="utf-8-sig", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(COLUMNAS)
            escritor.writerows(filas)
        with open(cls.mapa_csv, "w", encoding="utf-8-sig", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(["numero", "carpeta"])
            escritor.writerow(["03", cls.carpeta_cdr])

    @classmethod
    def _generar_xlsx(cls):
        from openpyxl import Workbook

        ruta = os.path.join(cls.tmp, "Control de exportacion.xlsx")
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Control de exportación"
        hoja.append(COLUMNAS)
        hoja.append(["SBX-03-0001", "03", "046.cdr", "tipo", "deporte", "ocasion", "estado", "a", "2026-10-07"])
        listas = libro.create_sheet("Listas")
        listas.append(["numero", "carpeta"])
        listas.append(["03", cls.carpeta_cdr])
        libro.save(ruta)
        return ruta

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _fila(self, codigo):
        for fila in self.filas:
            if fila.get("codigo") == codigo:
                return fila
        self.fail("No esta la fila para {}".format(codigo))

    def test_lectura_planilla_9_columnas(self):
        self.assertEqual(self.lectura_csv["columnas"], COLUMNAS)
        self.assertEqual(len(self.filas), 3)

    def test_carpeta_origen_y_archivo_original_se_conservan(self):
        registro = enriquecer_registro(self._fila("SBX-03-0001"), self.mapa_csv_map, png="SBX-03-0001.png")
        self.assertEqual(registro["codigo"], "SBX-03-0001")
        self.assertEqual(registro["carpeta_origen"], "03")
        self.assertEqual(registro["archivo_original"], "046.cdr")
        self.assertEqual(registro["carpeta_real"], self.carpeta_cdr)
        self.assertEqual(registro["ruta_cdr"], self.cdr_original)
        self.assertEqual(registro["png"], "SBX-03-0001.png")

    def test_carpeta_de_la_columna_coincide_con_el_codigo(self):
        registro = enriquecer_registro(self._fila("SBX-03-0002"), self.mapa_csv_map)
        self.assertEqual(registro["carpeta_origen"], "03")
        self.assertEqual(registro["ruta_cdr"], os.path.join(self.carpeta_cdr, "047.cdr"))

    def test_codigo_y_carpeta_origen_desparejas_se_rechazan(self):
        fila_despareja = dict(self._fila("SBX-03-0001"))
        fila_despareja["carpeta_origen"] = "04"
        problemas = validar_registro(fila_despareja, self.mapa_csv_map)
        self.assertTrue(any("no coincide" in e for e in problemas))
        with self.assertRaises(ErrorTrazabilidad):
            enriquecer_registro(fila_despareja, self.mapa_csv_map)

    def test_localizar_cdr_desde_codigo(self):
        resultado = localizar_cdr_por_codigo("SBX-03-0001", self.filas, self.mapa_csv_map)
        self.assertEqual(resultado["codigo"], "SBX-03-0001")
        self.assertEqual(resultado["ruta_cdr"], self.cdr_original)

    def test_validacion_cadena_completa(self):
        self.assertEqual(validar_registro(self._fila("SBX-03-0001"), self.mapa_csv_map), [])
        incomplete = dict(self._fila("SBX-03-0001"))
        incomplete["archivo_original"] = ""
        self.assertTrue(any("archivo_original" in e for e in validar_registro(incomplete, self.mapa_csv_map)))
        sin_mapa = dict(self._fila("SBX-03-0001"))
        problemas = validar_registro(sin_mapa, None)
        self.assertTrue(any("mapa" in e for e in problemas))

    def test_registro_incompleto_se_rechaza_sin_inventar(self):
        fila_incompleta = self._fila("SBX-03-0001").copy()
        fila_incompleta["archivo_original"] = ""
        with self.assertRaises(ErrorTrazabilidad) as cm:
            enriquecer_registro(fila_incompleta, self.mapa_csv_map)
        self.assertIn("archivo_original", str(cm.exception))

    def test_registro_fuera_del_mapa_se_rechaza(self):
        fila_fuera = self._fila("SBX-04-0002")
        with self.assertRaises(ErrorTrazabilidad):
            enriquecer_registro(fila_fuera, self.mapa_csv_map)
        self.assertEqual(carpeta_real(self.mapa_csv_map, "04"), "")

    def test_mapa_desde_hoja_listas_xlsx(self):
        mapa = leer_mapa(self.xlsx, "Listas", None)
        self.assertEqual(mapa["origen"], "hoja 'Listas'")
        self.assertEqual(mapa["entradas"].get("03"), self.carpeta_cdr)

    def test_mapas_poco_normalizados(self):
        self.assertEqual(carpeta_real({"03": self.carpeta_cdr}, "3"), self.carpeta_cdr)


class TestSeguridadCDR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="test_cdr_")
        cls.original = os.path.join(cls.tmp, "046.cdr")
        with open(cls.original, "wb") as f:
            f.write(b"CDR-INMUTABLE")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_operaciones_prohibidas(self):
        destino = os.path.join(self.tmp, "renombrado.cdr")
        for operacion in (
            lambda: renombrar_cdr(self.original, destino),
            lambda: mover_cdr(self.original, os.path.join(self.tmp, "moved")),
            lambda: borrar_cdr(self.original),
            lambda: sobrescribir_cdr(self.original, b"otro"),
            lambda: modificar_cdr(self.original),
        ):
            with self.assertRaises(ErrorCDRProtegido):
                operacion()

    def test_original_intacto_desde_el_inicio(self):
        self.assertTrue(os.path.isfile(self.original))
        with open(self.original, "rb") as f:
            self.assertEqual(f.read(), b"CDR-INMUTABLE")

    def test_copia_verificada_y_original_intacto(self):
        copia = copiar_cdr(self.original, os.path.join(self.tmp, "trabajo", "046_copia.cdr"))
        self.assertTrue(verificar_cdr_inmutable(self.original, copia))
        self.assertEqual(os.path.getmtime(self.original), os.path.getmtime(copia))
        self.assertTrue(os.path.isfile(self.original))


if __name__ == "__main__":
    unittest.main()