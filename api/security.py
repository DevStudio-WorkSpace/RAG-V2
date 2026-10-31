# -*- coding: utf-8 -*-
"""Autenticación por API key con roles para la API de búsqueda visual.

Reglas:
  - Los endpoints de búsqueda exigen una API key de cliente o administrador.
  - Los endpoints de indexación/administración exigen la API key de administrador.
  - Si las claves no están configuradas, los endpoints protegidos fallan
    cerrados con 503 (nunca quedan públicos por accidente).
  - Las claves nunca se registran en logs ni se devuelven en respuestas.

Variables de entorno:
  API_CLIENT_KEY   clave para el cliente principal (frontend/proxy).
  API_CLIENT_KEYS  claves adicionales por cliente, formato "nombre:clave,...".
  API_ADMIN_KEY    clave para tareas de indexación y administración.
"""

from __future__ import annotations

import logging
import re
import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status
from pydantic import SecretStr

from core.config import settings

logger = logging.getLogger(__name__)

API_KEY_HEADER = "X-API-Key"
ROLE_CLIENT = "client"
ROLE_ADMIN = "admin"

_CLIENT_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_WWW_AUTH = {"WWW-Authenticate": 'ApiKey realm="sublitex"'}


def _valor(secret: SecretStr) -> str:
    """Extrae y normaliza el valor de una clave sin exponerlo en logs."""
    return secret.get_secret_value().strip()


def _coincide(valor: str, esperado: str) -> bool:
    """Comparación en tiempo constante y tolerante a caracteres no ASCII."""
    if not esperado:
        return False
    return secrets.compare_digest(
        valor.encode("utf-8"),
        esperado.encode("utf-8"),
    )


def _client_keys() -> list[tuple[str, str]]:
    """Devuelve las claves de cliente válidas como pares (nombre, clave).

    `API_CLIENT_KEY` se conserva como cliente "default". Las claves adicionales
    se declaran en `API_CLIENT_KEYS` con formato "nombre:clave,otro:clave".
    Los nombres se usan solo para identificar al cliente en la respuesta de la
    dependencia; nunca se registran las claves.
    """
    claves: list[tuple[str, str]] = []
    nombres: set[str] = set()

    default = _valor(settings.API_CLIENT_KEY)
    if default:
        claves.append(("default", default))
        nombres.add("default")

    raw = _valor(settings.API_CLIENT_KEYS)
    if not raw:
        return claves

    for indice, item in enumerate(raw.split(","), start=1):
        item = item.strip()
        if not item:
            continue

        nombre, separador, clave = item.partition(":")
        if not separador:
            nombre = f"client{indice}"
            clave = item

        nombre = nombre.strip()
        clave = clave.strip()
        if not nombre or not clave:
            logger.warning("Entrada vacía en API_CLIENT_KEYS ignorada.")
            continue
        if not _CLIENT_NAME_RE.fullmatch(nombre):
            logger.warning(
                f"Nombre de cliente inválido en API_CLIENT_KEYS ignorado: {nombre!r}"
            )
            continue
        if nombre in nombres:
            logger.warning(
                f"Nombre de cliente duplicado en API_CLIENT_KEYS ignorado: {nombre!r}"
            )
            continue

        claves.append((nombre, clave))
        nombres.add(nombre)

    return claves


def _rol_de_key(key: str) -> tuple[str, str | None] | None:
    """Devuelve (rol, nombre_cliente) para una API key, o None si no es válida.

    Si una misma clave está configurada como cliente y como administrador, se
    concede solo el rol de menor privilegio (cliente) para no elevar permisos
    por un error de configuración.
    """
    admin_key = _valor(settings.API_ADMIN_KEY)
    claves_cliente = _client_keys()

    admin_coincide = bool(admin_key) and _coincide(key, admin_key)
    cliente_coincide: str | None = None
    for nombre, cliente_key in claves_cliente:
        if _coincide(key, cliente_key):
            cliente_coincide = nombre

    if cliente_coincide is not None:
        return ROLE_CLIENT, cliente_coincide
    if admin_coincide:
        return ROLE_ADMIN, None
    return None


def _autenticar(x_api_key: str | None, rol_requerido: str) -> str:
    admin_key = _valor(settings.API_ADMIN_KEY)
    claves_cliente = _client_keys()

    if not admin_key and not claves_cliente:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Autenticación no configurada: defina API_CLIENT_KEY o "
                "API_CLIENT_KEYS y API_ADMIN_KEY en el servidor."
            ),
        )

    if rol_requerido == ROLE_ADMIN and not admin_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_ADMIN_KEY no configurada en el servidor.",
        )

    key = (x_api_key or "").strip()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el header X-API-Key.",
            headers=_WWW_AUTH,
        )

    identidad = _rol_de_key(key)
    if identidad is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida.",
            headers=_WWW_AUTH,
        )

    rol, nombre_cliente = identidad
    if rol_requerido == ROLE_ADMIN and rol != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador para esta operación.",
        )

    if rol == ROLE_ADMIN:
        return ROLE_ADMIN
    return f"{ROLE_CLIENT}:{nombre_cliente}"


def require_client(
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER)] = None,
) -> str:
    """Dependencia FastAPI: exige una API key de cliente o administrador."""
    return _autenticar(x_api_key, ROLE_CLIENT)


def require_admin(
    x_api_key: Annotated[str | None, Header(alias=API_KEY_HEADER)] = None,
) -> str:
    """Dependencia FastAPI: exige la API key de administrador."""
    return _autenticar(x_api_key, ROLE_ADMIN)


def advertencias_config_seguridad() -> list[str]:
    """Lista advertencias de configuración sin incluir valores secretos."""
    claves_cliente = _client_keys()
    admin_key = _valor(settings.API_ADMIN_KEY)
    avisos: list[str] = []

    if not claves_cliente:
        avisos.append(
            "API_CLIENT_KEY/API_CLIENT_KEYS no configuradas: el frontend/proxy "
            "no podrá autenticarse y recibirá 503."
        )
    if not admin_key:
        avisos.append(
            "API_ADMIN_KEY no configurada: la indexación responderá 503."
        )
    if admin_key:
        nombres_iguales = [
            nombre
            for nombre, clave in claves_cliente
            if _coincide(clave, admin_key)
        ]
        if nombres_iguales:
            avisos.append(
                "Hay claves de cliente iguales a API_ADMIN_KEY "
                f"({', '.join(nombres_iguales)}): use claves distintas para "
                "separar el rol cliente del administrador."
            )
    if not settings.cors_origins_list:
        avisos.append(
            "CORS_ORIGINS no contiene orígenes válidos: el navegador no podrá "
            "llamar a la API desde el frontend."
        )

    return avisos
