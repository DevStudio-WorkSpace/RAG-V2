"""
core.cdr_seguridad
------------------
Regla ABSOLUTA del proyecto: los CDR originales son SOLO LECTURA.

Ningun proceso del proyecto puede renombrar, mover, borrar, sobrescribir ni
modificar un CDR original. El reordenamiento de los originales queda
reservado al FINAL de la Fase 1 / Tarea 2, solo cuando los datos esten
verificados y mediante un programa especifico que use este mismo modulo con
la autorizacion explicita (permitido=True).

Este modulo ofrece:
  - Operaciones protegidas que SIEMPRE lanzan ErrorCDRProtegido sin tocar el
    archivo (renombrar_cdr, mover_cdr, borrar_cdr, sobrescribir_cdr,
    modificar_cdr).
  - Operaciones seguras que SI estan permitidas (copiar_cdr a un destino de
    trabajo, verificar_cdr_inmutable para comprobar que una copia no difiere).
  - Tan pronto como el reordenamiento tenga su programa autorizado, ese
    programa usara mover_cdr(..., permitido=True); el resto del proyecto
    seguira bloqueado.
"""

import hashlib
import os
import shutil


class ErrorCDRProtegido(Exception):
    """Operacion sobre un CDR original bloqueada por la politica SOLO LECTURA."""


def es_cdr(ruta):
    """True si el nombre termina en .cdr (evita proteger otros formatos)."""
    return str(ruta or "").lower().endswith(".cdr")


def _bloquear(operacion):
    raise ErrorCDRProtegido(
        "Operacion '{}' bloqueada: los CDR originales son SOLO LECTURA. "
        "El reordenamiento esta reservado al final de la Fase 1 / Tarea 2 "
        "con datos verificados.".format(operacion)
    )


def renombrar_cdr(origen, destino, permitido=False):
    """Prohibido por defecto. Solo el programa autorizado de reordenamiento
    (con datos ya verificados) puede hacerlo con permitido=True."""
    if not permitido:
        _bloquear("renombrar_cdr")
    if not os.path.isfile(origen):
        raise FileNotFoundError(origen)
    if os.path.exists(destino):
        raise ErrorCDRProtegido(
            "No se puede renombrar {}: el destino {} ya existe.".format(origen, destino)
        )
    os.rename(origen, destino)
    return destino


def mover_cdr(origen, destino, permitido=False):
    """Prohibido por defecto (mover un CDR original cambia su ubicacion)."""
    if not permitido:
        _bloquear("mover_cdr")
    if not os.path.isfile(origen):
        raise FileNotFoundError(origen)
    caja = os.path.dirname(destino)
    if caja:
        os.makedirs(caja, exist_ok=True)
    shutil.move(origen, destino)
    return destino


def borrar_cdr(ruta, permitido=False):
    """Prohibido por defecto. Nunca se borra un CDR original."""
    if not permitido:
        _bloquear("borrar_cdr")
    if not os.path.isfile(ruta):
        raise FileNotFoundError(ruta)
    os.remove(ruta)


def sobrescribir_cdr(ruta, contenido, permitido=False):
    """Prohibido por defecto. Nunca se sobrescribe un CDR original."""
    if not permitido:
        _bloquear("sobrescribir_cdr")
    if not es_cdr(ruta):
        raise ErrorCDRProtegido("La politica SOLO LECTURA aplica a archivos CDR.")
    with open(ruta, "wb") as f:
        f.write(contenido)


def modificar_cdr(ruta, permitido=False):
    """Prohibido por defecto. Abrir un CDR original en modo escritura esta
    bloqueado; el proyecto debe trabajar SIEMPRE con copias."""
    if not permitido:
        _bloquear("modificar_cdr")
    return open(ruta, "rb")


def copiar_cdr(origen, destino):
    """Permitida: crea una copia de trabajo SIN tocar el original."""
    if not os.path.isfile(origen):
        raise FileNotFoundError(origen)
    directorio = os.path.dirname(destino)
    if directorio:
        os.makedirs(directorio, exist_ok=True)
    shutil.copy2(origen, destino)
    return destino


def verificar_cdr_inmutable(original, copia):
    """Contrasta el hash del original con el de la copia. Solo lectura."""
    def hash_archivo(ruta):
        digest = hashlib.sha256()
        with open(ruta, "rb") as f:
            for bloque in iter(lambda: f.read(65536), b""):
                digest.update(bloque)
        return digest.hexdigest()

    hash_original = hash_archivo(original)
    hash_copia = hash_archivo(copia)
    return hash_original == hash_copia