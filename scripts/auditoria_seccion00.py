"""
auditoria_seccion00.py
----------------------
Auditoria de SOLO LECTURA del contrato de datos de la SECCION 00 (Sublitex).

Reglas que verifica:
  codigo   : ^SBX-\\d{5}$          (SBX-XXXXX, consecutivo global de 5 digitos)
  archivo  : SBX-XXXXX.png
  planilla : "Control de exportacion" con las 9 columnas:
             codigo, carpeta_origen, archivo_original, tipo, deporte,
             ocasion, estado, quien, fecha
  mapa     : hoja/CSV "Listas" -> numero de carpeta -> carpeta real del Drive

Cadenas de trazabilidad que audita:
  PNG -> codigo -> carpeta_origen + archivo_original -> CDR original

Entradas (NUNCA se modifican, NUNCA se renombran, NUNCA se borran):
  --png_dir    carpeta con los PNG exportados por el equipo de diseno
  --planilla   CSV o XLSX de Control de exportacion
  --hoja       nombre de la hoja del mapa de carpetas (defecto: Listas)
  --mapa       CSV alternativo del mapa numero -> carpeta (si no hay hoja)

Salida (unico archivo que se escribe):
  --salida     informe Markdown generado por esta auditoria

Prohibido por la SECCION 00 y por lo tanto fuera del alcance de este script:
  generar embeddings, tocar el indice de Aimari, products.csv, los PNG,
  los CDR o la planilla original.

Uso:
    python scripts/auditoria_seccion00.py
    python scripts/auditoria_seccion00.py --png_dir data/imagenes_normalized
    python scripts/auditoria_seccion00.py --planilla "ruta/Control de exportacion.xlsx"
    python scripts/auditoria_seccion00.py --salida docs/SECCION_00_REPORTE.md
"""

import argparse
import os
import sys
from collections import Counter

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.sublitex import (
    COLUMNAS_PLANILLA,
    ErrorTrazabilidad,
    HOJA_LISTAS,
    REGEX_CODIGO,
    leer_mapa,
    leer_planilla,
)

COLUMNAS_ESPERADAS = list(COLUMNAS_PLANILLA)

FIRMA_PNG = b"\x89PNG\r\n\x1a\n"
FIRMA_JPG = b"\xff\xd8\xff"

CANDIDATAS_PNG = [
    "data/imagenes_sublitex",
    "data/png_sublitex",
    "data/sublitex_png",
    "data/imagenes_normalized",
]
CANDIDATAS_PLANILLA = [
    "data/control_exportacion.csv",
    "data/Control de exportacion.csv",
    "data/Control de exportación.csv",
    "control_exportacion.csv",
    "Control de exportacion.csv",
    "Control de exportación.csv",
    "data/control_exportacion.xlsx",
    "data/Control de exportacion.xlsx",
    "data/Control de exportación.xlsx",
    "control_exportacion.xlsx",
]


def reconfigurar_consola():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def resolver_png_dir(argumento):
    if argumento:
        return argumento, [argumento]
    probadas = [os.path.join(BASE_DIR, c) for c in CANDIDATAS_PNG]
    for ruta in probadas:
        if os.path.isdir(ruta):
            return ruta, probadas
    return probadas[0], probadas


def resolver_planilla(argumento):
    if argumento:
        return argumento, [argumento]
    probadas = [os.path.join(BASE_DIR, c) for c in CANDIDATAS_PLANILLA]
    for ruta in probadas:
        if os.path.isfile(ruta):
            return ruta, probadas
    return None, probadas


def leer_firma(ruta, cantidad=8):
    try:
        with open(ruta, "rb") as f:
            return f.read(cantidad)
    except OSError:
        return b""


def auditar_pngs(ruta_png):
    resultado = {
        "ruta": ruta_png,
        "existe": os.path.isdir(ruta_png),
        "total": 0,
        "png": 0,
        "validos": [],
        "invalidos": [],
        "duplicados": [],
        "no_png_real": [],
        "extensiones": Counter(),
    }
    if not resultado["existe"]:
        return resultado

    nombres = sorted(e.name for e in os.scandir(ruta_png) if e.is_file())
    resultado["total"] = len(nombres)
    bases = Counter()
    for nombre in nombres:
        base, extension = os.path.splitext(nombre)
        extension = extension.lower()
        resultado["extensiones"][extension or "(sin extension)"] += 1
        bases[base.lower()] += 1
        coincide = bool(REGEX_CODIGO.match(base))
        es_png = extension == ".png"
        if coincide and es_png:
            firma = leer_firma(os.path.join(ruta_png, nombre), 8)
            if firma == FIRMA_PNG:
                resultado["validos"].append(base)
            else:
                resultado["no_png_real"].append(nombre)
                resultado["invalidos"].append(nombre)
        else:
            resultado["invalidos"].append(nombre)

    resultado["png"] = sum(1 for n in nombres if n.lower().endswith(".png"))
    resultado["duplicados"] = sorted(b for b, c in bases.items() if c > 1)
    resultado["validos"].sort()
    return resultado


def auditar_planilla(columnas, filas):
    faltantes = [c for c in COLUMNAS_ESPERADAS if c not in columnas]
    sobrantes = [c for c in columnas if c and c not in COLUMNAS_ESPERADAS]
    vacios = {c: 0 for c in COLUMNAS_ESPERADAS if c in columnas}
    codigos = []
    invalidos = []
    numeros = set()

    for indice, fila in enumerate(filas, start=2):
        for columna in vacios:
            if not str(fila.get(columna, "") or "").strip():
                vacios[columna] += 1
        codigo = str(fila.get("codigo", "") or "").strip()
        if not codigo:
            continue
        codigos.append((codigo, indice))
        if not REGEX_CODIGO.match(codigo):
            invalidos.append((codigo, indice))
        carpeta = str(fila.get("carpeta_origen", "") or "").strip()
        if carpeta:
            numeros.add(_normar_numero(carpeta))

    conteo = Counter(c for c, _ in codigos)
    duplicados = sorted(c for c, n in conteo.items() if n > 1)
    return {
        "columnas": columnas,
        "faltantes": faltantes,
        "sobrantes": sobrantes,
        "filas": len(filas),
        "codigos": codigos,
        "unicos": len(conteo),
        "vacios": vacios,
        "invalidos": invalidos,
        "duplicados": duplicados,
        "numeros": numeros,
        "carpetas": numeros,
    }


def _normar_numero(numero):
    """Rellena a 2 digitos un numero de carpeta (3 -> 03) para cruzar con el mapa."""
    numero = str(numero or "").strip()
    if numero.isdigit() and len(numero) == 1:
        return numero.zfill(2)
    return numero


def cruzar(pngs, planilla, filas, mapa):
    codigos_png = set(pngs["validos"])
    codigos_planilla = {c for c, _ in planilla["codigos"] if REGEX_CODIGO.match(c)}
    cruces = {
        "png_con_fila": sorted(codigos_png & codigos_planilla),
        "png_sin_fila": sorted(codigos_png - codigos_planilla),
        "fila_sin_png": sorted(codigos_planilla - codigos_png),
        "carpeta_vacia": [],
        "archivo_vacio": [],
        "carpeta_no_verificable": [],
    }
    mapa_usado = mapa["entradas"] if mapa else None
    for indice, fila in enumerate(filas, start=2):
        codigo = str(fila.get("codigo", "") or "").strip()
        carpeta = str(fila.get("carpeta_origen", "") or "").strip()
        original = str(fila.get("archivo_original", "") or "").strip()
        if not codigo:
            continue
        if not carpeta:
            cruces["carpeta_vacia"].append((codigo, indice))
        if not original:
            cruces["archivo_vacio"].append((codigo, indice))
        if not REGEX_CODIGO.match(codigo):
            continue
        if mapa_usado is None:
            cruces["carpeta_no_verificable"].append((codigo, indice))
            continue
        if not carpeta:
            continue
        if _normar_numero(carpeta) not in mapa_usado:
            cruces["carpeta_no_verificable"].append((codigo, indice))
    return cruces


def auditar_mapa(mapa, numeros_planilla):
    if mapa is None:
        return None
    entradas = mapa["entradas"]
    numeros_mapa = {n for n in entradas if n}
    try:
        enteros = sorted(int(n) for n in numeros_mapa if str(n).isdigit())
        faltantes = [n for n in range(enteros[0], enteros[-1] + 1) if n not in enteros] if enteros else []
    except ValueError:
        faltantes = []
    return {
        "entradas": entradas,
        "repetidos": mapa["repetidos"],
        "vacios": mapa["vacios"],
        "faltantes": faltantes,
        "en_planilla_no_mapa": sorted(numeros_planilla - numeros_mapa),
        "en_mapa_no_planilla": sorted(numeros_mapa - numeros_planilla, key=lambda x: (len(x), x)),
    }


def clasificar(pngs, planilla, mapa_info, cruces, ruta_planilla):
    problemas = []

    def add(severidad, archivo, fila, codigo, problema, impacto, solucion):
        problemas.append({
            "severidad": severidad,
            "archivo": archivo,
            "fila": fila,
            "codigo": codigo,
            "problema": problema,
            "impacto": impacto,
            "solucion": solucion,
        })

    if not pngs["existe"]:
        add("CRÍTICO", pngs["ruta"], "", "", "No existe la carpeta de PNG de Sublitex.",
            "La cadena imagen -> codigo no puede iniciarse; la Tarea 1 no tiene insumo.",
            "Solicitar al equipo de diseno la carpeta real de exportacion (no renombrar nada).")
    elif not pngs["validos"]:
        add("CRÍTICO", pngs["ruta"], "", "",
            f"Ningun archivo cumple SBX-XXXXX.png ({pngs['total']} archivos revisados).",
            "El cargador rechazaria el 100% de los archivos; no hay codigo que unir a la planilla.",
            "Pedir la exportacion con la nomenclatura oficial o generar copias renombradas en OTRA carpeta.")

    if ruta_planilla is None:
        add("CRÍTICO", "Control de exportacion", "", "",
            "No se encontro la planilla Control de exportacion.",
            "carpeta_origen y archivo_original son irrecuperables: la cadena hacia el CDR se rompe.",
            "Solicitar el XLSX/CSV original al equipo; no inventar columnas ni filas.")
    else:
        if planilla and planilla["faltantes"]:
            add("ALTO", ruta_planilla, "", "",
                f"Faltan columnas requeridas: {', '.join(planilla['faltantes'])}.",
                "El catálogo no puede guardar los campos obligatorios del contrato de datos.",
                "Confirmar con el coordinador si la planilla real trae esas columnas.")
        if planilla:
            for codigo, fila in planilla["invalidos"]:
                add("ALTO", ruta_planilla, str(fila), codigo,
                    "Codigo que no cumple SBX-XXXXX.",
                    "El codigo no se puede cruzar con el nombre del PNG ni con el mapa de carpetas.",
                    "Reportar la fila; no corregirla automaticamente.")
            for codigo in planilla["duplicados"]:
                add("ALTO", ruta_planilla, "", codigo,
                    "Codigo repetido en la planilla.",
                    "El join PNG <-> planilla puede quedarse con la ultima fila y ocultar datos.",
                    "Reportar la lista completa de repetidos; no borrar filas.")
            if planilla["vacios"].get("carpeta_origen"):
                add("ALTO", ruta_planilla, "", "",
                    f"{planilla['vacios']['carpeta_origen']} filas con carpeta_origen vacio.",
                    "Sin carpeta_origen no se localiza el CDR original.",
                    "Reportar filas; completarlas con el equipo de diseno.")
            if planilla["vacios"].get("archivo_original"):
                add("ALTO", ruta_planilla, "", "",
                    f"{planilla['vacios']['archivo_original']} filas con archivo_original vacio.",
                    "Sin archivo_original no se localiza el CDR original.",
                    "Reportar filas; completarlas con el equipo de diseno.")

    if cruces:
        for codigo in cruces["png_sin_fila"]:
            add("ALTO", pngs["ruta"], "", codigo,
                "PNG valido sin fila en la planilla.",
                "Imagen publicada sin carpeta_origen/archivo_original: no se puede rastrear al CDR.",
                "Reportar el codigo; pedir que lo anoten en la planilla.")
        for codigo in cruces["fila_sin_png"]:
            add("MEDIO", ruta_planilla or "Control de exportacion", "", codigo,
                "Fila de planilla sin PNG correspondiente.",
                "Registro que no se puede indexar hasta que se exporte la imagen.",
                "Reportar el codigo; pedir la exportacion del PNG.")
        for codigo, indice in cruces["carpeta_vacia"]:
            add("ALTO", ruta_planilla, str(indice), codigo,
                "Fila con carpeta_origen vacio.",
                "Cadena imagen -> codigo -> carpeta_origen rota.",
                "Reportar la fila; no completarla por cuenta propia.")
        for codigo, indice in cruces["archivo_vacio"]:
            add("ALTO", ruta_planilla, str(indice), codigo,
                "Fila con archivo_original vacio.",
                "Cadena imagen -> codigo -> archivo_original rota.",
                "Reportar la fila; no completarla por cuenta propia.")
        if cruces["carpeta_no_verificable"]:
            add("MEDIO", ruta_planilla or "Control de exportacion", "", "",
                f"{len(cruces['carpeta_no_verificable'])} filas con carpeta_origen no resuelta en el mapa Listas.",
                "Sin carpeta real no se localiza el CDR original de esos codigos.",
                "Proporcionar la hoja Listas o el CSV del mapa, o corregir la columna carpeta_origen.")

    if planilla and planilla["faltantes"] == [] and planilla["sobrantes"]:
        add("BAJO", ruta_planilla, "", "",
            f"Columnas fuera del contrato de 9: {', '.join(planilla['sobrantes'])}.",
            "No rompe la cadena, pero conviene documentarlas.",
            "Documentar en el README de la Tarea 1.")

    if mapa_info:
        for numero in mapa_info["repetidos"]:
            add("MEDIO", "Mapa de carpetas (Listas)", "", numero,
                "Numero de carpeta repetido en el mapa.",
                "La traduccion numero -> carpeta real queda ambigua.",
                "Reportar el duplicado; no reemplazar entradas.")
        for numero, fila in mapa_info["vacios"]:
            add("MEDIO", "Mapa de carpetas (Listas)", str(fila), numero,
                "Entrada del mapa sin carpeta real.",
                "No se puede traducir el numero de carpeta_origen a una carpeta del Drive.",
                "Reportar la entrada vacia.")
        for numero in mapa_info["en_planilla_no_mapa"]:
            add("MEDIO", "Mapa de carpetas (Listas)", "", numero,
                f"La carpeta {numero} aparece en la planilla pero no en el mapa.",
                "No se puede resolver la carpeta real de esos codigos.",
                "Reportar la carpeta faltante al coordinador.")
        for numero in mapa_info["en_mapa_no_planilla"]:
            add("BAJO", "Mapa de carpetas (Listas)", "", numero,
                f"La carpeta {numero} esta en el mapa pero no se usa en la planilla.",
                "Entrada sin uso; solo es ruido documental.",
                "Documentar, no borrar.")

    if pngs["no_png_real"]:
        for nombre in pngs["no_png_real"]:
            add("ALTO", os.path.join(pngs["ruta"], nombre), "", "",
                "Archivo con extension .png que no tiene la firma PNG real.",
                "Puede fallar al abrirse en el pipeline de vision.",
                "Reportar el archivo; no renombrarlo ni borrarlo.")
    for nombre in pngs["invalidos"]:
        if nombre in pngs["no_png_real"]:
            continue
        if nombre.lower().endswith(".png"):
            add("ALTO", os.path.join(pngs["ruta"], nombre), "", "",
                "PNG con nombre que no cumple SBX-XXXXX.",
                "El cargador lo rechaza; queda fuera del indice.",
                "Reportar el nombre; no renombrar el original.")
        else:
            add("BAJO", os.path.join(pngs["ruta"], nombre), "", "",
                "Archivo que no es PNG (extension distinta).",
                "La especificacion pide PNG exportados del CDR.",
                "Pedir la exportacion en PNG o documentar la variante.")
    for base in pngs["duplicados"]:
        add("MEDIO", pngs["ruta"], "", base,
            "Nombre de base duplicado (mayusculas/minusculas).",
            "Ambiguedad al cruzar codigo <-> archivo en sistemas de archivos case-insensitive.",
            "Reportar los archivos implicados.")

    orden = {"CRÍTICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3}
    problemas.sort(key=lambda p: (orden[p["severidad"]], p["archivo"]))
    return problemas


def construir_informe(contexto):
    pngs = contexto["pngs"]
    planilla = contexto["planilla"]
    mapa_info = contexto["mapa_info"]
    cruces = contexto["cruces"]
    problemas = contexto["problemas"]
    ruta_planilla = contexto["ruta_planilla"]
    origen_mapa = contexto["origen_mapa"]

    lineas = []
    linea = lineas.append

    linea("# SECCION 00 — REPORTE DE AUDITORIA (generado)")
    linea("")
    linea(f"- Fecha: {contexto['fecha']}")
    linea(f"- Script: `scripts/auditoria_seccion00.py` (solo lectura)")
    linea(f"- Salida: `{contexto['salida']}`")
    linea("")
    linea("## 1. Regla del codigo")
    linea("")
    linea("`SBX-XXXXX` — expresion regular exacta: `^SBX-\\d{5}$` (consecutivo global).")
    linea("")
    linea("Validos: `SBX-00001`, `SBX-00147`, `SBX-08340`, `SBX-11000`, `SBX-99999`.")
    linea("")
    linea("Invalidos: `SBX-0001`, `SBX-03-0147`, `SBX-000147`, `SBX_00001`, "
          "`SBX-00001-extra`, `XXX-00001`, `SBX-AB-XYZ`, `00001`, `01_0001`.")
    linea("")
    linea("> Formato definitivo (ratificado): `SBX-XXXXX`, segun la Ficha 05-B oficial "
          "(`ids: Los codigos SBX-00001`) y la escala de ~11.000 disenos (001, 002, ...).")
    linea("> El numero de carpeta NO va en el codigo: se lee de la columna "
          "`carpeta_origen` de la planilla y se resuelve con la hoja `Listas`. "
          "El formato `SBX-NN-NNNN` (carpeta-correlativo) queda DESCARTADO por no "
          "tener respaldo en ningun documento oficial.")
    linea("")
    linea("## 2. Regla del archivo")
    linea("")
    linea("`SBX-XXXXX.png` — la validacion se hace sobre el nombre base "
          "(`os.path.splitext`), mas la extension `.png` exacta y la firma binaria PNG.")
    linea("")

    linea("## 3. Planilla encontrada")
    linea("")
    if ruta_planilla:
        linea(f"- Ruta: `{ruta_planilla}`")
        linea(f"- Formato / hoja: {contexto['formato']}")
        linea(f"- Hoja Listas: {origen_mapa}")
    else:
        linea("- Ruta: **NO DISPONIBLE** (no se encontro la planilla Control de exportacion).")
        linea("- Formato: NO DISPONIBLE")
        linea("- Hoja principal: NO DISPONIBLE")
        linea(f"- Hoja Listas: {origen_mapa}")
        linea("")
        linea("Rutas candidatas consultadas:")
        for ruta in contexto["planilla_probadas"]:
            linea(f"- `{ruta}`")
    linea("")

    linea("## 4. Columnas encontradas")
    linea("")
    if planilla:
        linea("| Columna esperada | Presente |")
        linea("| --- | --- |")
        for columna in COLUMNAS_ESPERADAS:
            estado = "si" if columna in planilla["columnas"] else "**NO**"
            linea(f"| {columna} | {estado} |")
        linea("")
        linea(f"Columnas leidas: {', '.join(planilla['columnas']) or '(ninguna)'}")
        linea("")
        if planilla["faltantes"]:
            linea(f"**No coinciden.** Faltan: {', '.join(planilla['faltantes'])}")
        else:
            linea("Coinciden exactamente con las 9 columnas del contrato.")
    else:
        linea("NO DISPONIBLE (sin planilla no hay columnas que comparar).")
    linea("")

    linea("## 5. Mapa de carpetas")
    linea("")
    if mapa_info:
        linea(f"Fuente: {origen_mapa}")
        linea("")
        linea("| Numero de carpeta | Carpeta real |")
        linea("| --- | --- |")
        for numero, carpeta in mapa_info["entradas"].items():
            linea(f"| {numero} | {carpeta or '**VACIO**'} |")
        linea("")
        linea(f"- Entradas: {len(mapa_info['entradas'])}")
        linea(f"- Numeros duplicados: {', '.join(mapa_info['repetidos']) or 'ninguno'}")
        linea(f"- Numeros faltantes en el rango: {', '.join(str(n) for n in mapa_info['faltantes']) or 'ninguno'}")
        linea(f"- Entradas con carpeta vacia: {len(mapa_info['vacios'])}")
    else:
        linea(f"**NO DISPONIBLE** — {origen_mapa}.")
        linea("")
        linea("No se inventa el valor de `03` ni de ninguna otra carpeta.")
    linea("")

    linea("## 6. PNG encontrados")
    linea("")
    linea(f"- Ruta: `{pngs['ruta']}`" + ("" if pngs["existe"] else " (**no existe**)"))
    if not pngs["existe"]:
        linea("")
        linea("Rutas candidatas consultadas:")
        for ruta in contexto["png_probadas"]:
            linea(f"- `{ruta}`")
    linea(f"- Cantidad total de archivos: {pngs['total']}")
    linea(f"- Cantidad de archivos con extension .png: {pngs['png']}")
    linea(f"- Cantidad validos (`SBX-XXXXX.png` + firma PNG): {len(pngs['validos'])}")
    linea(f"- Cantidad invalidos: {len(pngs['invalidos'])}")
    if pngs["extensiones"]:
        ext = ", ".join(f"{e}={n}" for e, n in sorted(pngs["extensiones"].items()))
        linea(f"- Extensiones: {ext}")
    if pngs["no_png_real"]:
        linea(f"- Con extension .png pero sin firma PNG real: {len(pngs['no_png_real'])}")
    if pngs["duplicados"]:
        linea(f"- Bases duplicadas: {', '.join(pngs['duplicados'])}")
    linea("")

    linea("## 7. Cruce PNG <-> planilla")
    linea("")
    if planilla and pngs["validos"]:
        linea(f"- PNG valido + fila encontrada: {len(cruces['png_con_fila'])}")
        linea(f"- PNG valido + fila inexistente: {len(cruces['png_sin_fila'])}")
        linea(f"- PNG invalidos: {len(pngs['invalidos'])}")
        linea(f"- Fila de planilla sin PNG: {len(cruces['fila_sin_png'])}")
        linea(f"- Codigos duplicados en la planilla: {len(planilla['duplicados'])}")
        linea(f"- Filas con carpeta_origen vacio: {len(cruces['carpeta_vacia'])}")
        linea(f"- Filas con archivo_original vacio: {len(cruces['archivo_vacio'])}")
        for etiqueta, clave in (
            ("PNG valido + fila encontrada", "png_con_fila"),
            ("PNG valido + fila inexistente", "png_sin_fila"),
            ("Fila de planilla sin PNG", "fila_sin_png"),
        ):
            if cruces[clave]:
                linea("")
                linea(f"**{etiqueta}:**")
                for codigo in cruces[clave]:
                    linea(f"- {codigo}")
    else:
        linea("**Cruce no ejecutable:** faltan PNG validos, planilla o ambos.")
        linea("")
        linea("| Metrica | Resultado |")
        linea("| --- | --- |")
        linea(f"| PNG valido + fila encontrada | {'0' if pngs['validos'] else '0 (sin PNG validos)'} |")
        linea(f"| PNG valido + fila inexistente | 0 |")
        linea(f"| PNG invalidos | {len(pngs['invalidos'])} |")
        linea("| Fila de planilla sin PNG | n/a (sin planilla) |")
        linea("| Codigo duplicado | n/a (sin planilla) |")
        linea("| carpeta_origen vacio | n/a (sin planilla) |")
        linea("| archivo_original vacio | n/a (sin planilla) |")
    linea("")

    linea("## 8. Problemas encontrados")
    linea("")
    if not problemas:
        linea("Ningun problema detectado.")
    else:
        totales = Counter(p["severidad"] for p in problemas)
        linea("Resumen: " + ", ".join(
            f"{sev}={totales[sev]}" for sev in ("CRÍTICO", "ALTO", "MEDIO", "BAJO") if totales[sev]))
        linea("")
        for sev in ("CRÍTICO", "ALTO", "MEDIO", "BAJO"):
            grupo = [p for p in problemas if p["severidad"] == sev]
            if not grupo:
                continue
            linea(f"### {sev} ({len(grupo)})")
            linea("")
            for p in grupo:
                ubicacion = p["archivo"]
                if p["fila"]:
                    ubicacion += f" (fila {p['fila']})"
                if p["codigo"]:
                    ubicacion += f" [codigo {p['codigo']}]"
                linea(f"- **{ubicacion}** — {p['problema']}")
                linea(f"  - Impacto: {p['impacto']}")
                linea(f"  - Solucion propuesta: {p['solucion']}")
            linea("")
    linea("")

    linea("## 9. Cadena de trazabilidad")
    linea("")
    eslabones = [
        ("PNG -> codigo", bool(pngs["validos"])),
        ("codigo -> planilla", bool(planilla and planilla["codigos"])),
        ("planilla -> carpeta_origen", bool(planilla and not planilla["vacios"].get("carpeta_origen"))),
        ("planilla -> archivo_original", bool(planilla and not planilla["vacios"].get("archivo_original"))),
        ("carpeta_origen -> CDR (mapa Listas)", bool(mapa_info)),
    ]
    linea("| Eslabon | Disponible |")
    linea("| --- | --- |")
    for nombre, ok in eslabones:
        linea(f"| {nombre} | {'SI' if ok else '**NO**'} |")
    linea("")
    if all(ok for _, ok in eslabones):
        linea("**La cadena PNG -> codigo -> carpeta_origen -> archivo_original -> CDR es trazable.**")
    else:
        linea("**La cadena NO es trazable todavia.** Faltan los insumos marcados arriba; "
              "no se completan con datos inventados.")
    linea("")

    linea("## 10. Recomendacion para la Tarea 1")
    linea("")
    linea("El cargador debera consumir, en este orden y sin romper la cadena:")
    linea("")
    linea("1. Carpeta de PNG `SBX-XXXXX.png`, validada con `^SBX-\\d{5}$`; "
          "los inválidos se reportan, no se corrigen ni se ignoran en silencio.")
    linea("2. Planilla Control de exportacion como fuente unica de `carpeta_origen` "
          "y `archivo_original`, unida por `codigo`; todo PNG sin fila y toda fila "
          "sin PNG se lista en un archivo aparte.")
    linea("3. Hoja/CSV Listas como mapa `numero -> carpeta real` para llegar al CDR; "
          "mientras no exista, `carpeta_origen` se conserva literal de la planilla.")
    linea("4. Catalogo de salida con `codigo + carpeta_origen + archivo_original` en una "
          "coleccion/npy NUEVA, con el mismo modelo del buscador y con la verificacion "
          "`len(vectores) == len(ids)`.")
    linea("")

    linea("## Problemas bloqueantes actuales")
    linea("")
    criticos = [p for p in problemas if p["severidad"] == "CRÍTICO"]
    if criticos:
        for p in criticos:
            linea(f"- **CRITICO** — {p['problema']} Impacto: {p['impacto']}")
    else:
        linea("- Ninguno.")
    linea("")
    return "\n".join(lineas) + "\n"


def main():
    reconfigurar_consola()
    parser = argparse.ArgumentParser(
        description="Auditoria de solo lectura del contrato de datos de la SECCION 00 (Sublitex)."
    )
    parser.add_argument("--png_dir", type=str, default=None,
                        help="Carpeta con los PNG exportados (por defecto: busca en data/)")
    parser.add_argument("--planilla", type=str, default=None,
                        help="Ruta al CSV/XLSX del Control de exportacion")
    parser.add_argument("--hoja", type=str, default=HOJA_LISTAS,
                        help="Nombre de la hoja del mapa de carpetas (defecto: Listas)")
    parser.add_argument("--mapa", type=str, default=None,
                        help="CSV alternativo del mapa numero -> carpeta")
    parser.add_argument("--salida", type=str,
                        default=os.path.join(BASE_DIR, "docs", "SECCION_00_REPORTE.md"),
                        help="Ruta del informe Markdown a generar")
    parser.add_argument("--sin_salida", action="store_true",
                        help="No escribir el informe, solo imprimir el resumen")
    args = parser.parse_args()

    ruta_png, png_probadas = resolver_png_dir(args.png_dir)
    ruta_planilla, planilla_probadas = resolver_planilla(args.planilla)

    columnas, filas, formato = ([], [], "NO DISPONIBLE")
    if ruta_planilla:
        try:
            lectura = leer_planilla(ruta_planilla)
            columnas = lectura["columnas"]
            filas = lectura["filas"]
            formato = lectura["formato"]
        except Exception as e:
            print(f"No se pudo leer la planilla {ruta_planilla}: {e}")
            ruta_planilla = None

    mapa = None
    origen_mapa = "NO DISPONIBLE"
    if ruta_planilla is not None or args.mapa is not None:
        try:
            mapa = leer_mapa(ruta_planilla, args.hoja, args.mapa)
            origen_mapa = mapa.get("origen", "")
        except ErrorTrazabilidad as e:
            mapa = None
            origen_mapa = str(e)
    else:
        origen_mapa = "NO DISPONIBLE (sin planilla XLSX ni CSV del mapa)"

    pngs = auditar_pngs(ruta_png)
    planilla = auditar_planilla(columnas, filas) if ruta_planilla else None
    mapa_info = auditar_mapa(mapa, planilla["numeros"] if planilla else set())
    cruces = cruzar(pngs, planilla, filas, mapa) if planilla else None
    if cruces is None:
        cruces = {
            "png_con_fila": [], "png_sin_fila": [], "fila_sin_png": [],
            "carpeta_vacia": [], "archivo_vacio": [],
            "carpeta_no_verificable": [],
        }
    problemas = clasificar(pngs, planilla, mapa_info, cruces, ruta_planilla)

    import datetime
    contexto = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "salida": args.salida,
        "pngs": pngs,
        "planilla": planilla,
        "mapa_info": mapa_info,
        "cruces": cruces,
        "problemas": problemas,
        "ruta_planilla": ruta_planilla,
        "planilla_probadas": planilla_probadas,
        "png_probadas": png_probadas,
        "formato": formato,
        "origen_mapa": origen_mapa,
    }
    informe = construir_informe(contexto)

    if not args.sin_salida:
        os.makedirs(os.path.dirname(os.path.abspath(args.salida)), exist_ok=True)
        with open(args.salida, "w", encoding="utf-8") as f:
            f.write(informe)

    totales = Counter(p["severidad"] for p in problemas)
    print("== SECCION 00 · AUDITORIA (solo lectura) ==")
    print(f"PNG dir      : {pngs['ruta']}{'' if pngs['existe'] else '  [NO EXISTE]'}")
    print(f"Archivos     : {pngs['total']}  (validos SBX-XXXXX.png: {len(pngs['validos'])})")
    print(f"Planilla     : {ruta_planilla or '[NO ENCONTRADA]'}")
    if planilla:
        print(f"Filas        : {planilla['filas']}  (codigos unicos: {planilla['unicos']})")
        print(f"Columnas     : {', '.join(planilla['columnas']) or '(ninguna)'}")
    print(f"Mapa         : {origen_mapa}")
    if mapa_info:
        print(f"Entradas     : {len(mapa_info['entradas'])}")
    if planilla and pngs["validos"]:
        print(f"Cruce        : {len(cruces['png_con_fila'])} con fila, "
              f"{len(cruces['png_sin_fila'])} sin fila, "
              f"{len(cruces['fila_sin_png'])} filas sin PNG")
    print("Problemas    : " + ", ".join(
        f"{s}={totales[s]}" for s in ("CRÍTICO", "ALTO", "MEDIO", "BAJO") if totales[s]) or "ninguno")
    if not args.sin_salida:
        print(f"Informe      : {args.salida}")


if __name__ == "__main__":
    main()
