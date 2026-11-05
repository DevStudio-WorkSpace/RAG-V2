#!/usr/bin/env python3
"""Alertas de disponibilidad, latencia y errores del buscador visual.

Consulta periodicamente los endpoints del sistema y notifica por webhook SOLO
cuando cambia el estado (OK -> fallo o fallo -> OK), de modo que un cron cada
1-5 minutos no genere ruido. Pensado para ejecutarse sin dependencias extra:
solo biblioteca estandar de Python.

Comprobaciones:
  1. API /health: HTTP 200, ``desfase_detectado: false`` y, opcionalmente,
     minimos de productos/embeddings y latencia maxima.
  2. Qdrant /readyz: opcional, se activa definiendo ``ALERT_QDRANT_READYZ_URL``.
  3. Busqueda sintetica ``POST /search/image``: opcional, se activa definiendo
     ``ALERT_SEARCH_URL`` y ``ALERT_SEARCH_IMAGE``; detecta errores HTTP y
     latencia real del endpoint.

Uso:
    python3 scripts/health_alert.py
    python3 scripts/health_alert.py --dry-run --verbose
    python3 scripts/health_alert.py --force-notify   # prueba de notificacion

Codigos de salida:
    0  todas las comprobaciones OK (o cambio ya notificado)
    1  hay al menos una comprobacion fallando
    2  error de configuracion (URL invalida, formato de webhook desconocido...)
    3  no se pudo entregar la notificacion (el estado no se actualiza y se
       reintenta en la siguiente ejecucion)

Seguridad: la URL del webhook, el token de Telegram y la clave de la API nunca
se imprimen ni se guardan en el archivo de estado.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import socket
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = BASE_DIR / ".env"
DEFAULT_STATE_FILE = BASE_DIR / ".alert_state.json"

WEBHOOK_FORMATS = ("generic", "discord", "slack", "telegram")
ALLOWED_ENV_PREFIXES = ("ALERT_", "HEALTH_")

EXIT_OK = 0
EXIT_ALERTA = 1
EXIT_CONFIG = 2
EXIT_NOTIFICACION = 3


# --------------------------------------------------------------------------- #
# Configuracion
# --------------------------------------------------------------------------- #
@dataclass
class Config:
    health_url: str = "http://127.0.0.1:8000/health"
    health_timeout: float = 10.0
    max_health_ms: int = 0
    min_products: int = 0
    min_embeddings: int = 0
    qdrant_readyz_url: str = ""
    search_url: str = ""
    search_image: Path | None = None
    search_modelo: str = "clip"
    search_timeout: float = 120.0
    api_key: str = ""
    max_search_ms: int = 0
    webhook_url: str = ""
    webhook_format: str = "generic"
    webhook_timeout: float = 10.0
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    state_file: Path = DEFAULT_STATE_FILE
    dry_run: bool = False
    force_notify: bool = False
    verbose: bool = False

    def secrets(self) -> List[str]:
        """Valores que nunca deben aparecer en logs ni en mensajes."""
        return [
            self.webhook_url,
            self.telegram_bot_token,
            self.api_key,
        ]


class ConfigError(Exception):
    """Configuracion invalida."""


class ProbeError(Exception):
    """Comprobacion que no pudo completarse (red, DNS, timeout...)."""


def _load_env_file(path: Path) -> Dict[str, str]:
    """Lee un .env sencillo (KEY=VALUE) sin sobrescribir el entorno real."""
    valores: Dict[str, str] = {}
    if not path.is_file():
        return valores
    try:
        contenido = path.read_text(encoding="utf-8")
    except OSError:
        return valores
    for linea in contenido.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        if linea.startswith("export "):
            linea = linea[len("export "):].strip()
        clave, _, valor = linea.partition("=")
        clave = clave.strip()
        if not clave:
            continue
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in ("'", '"'):
            valor = valor[1:-1]
        valores[clave] = valor
    return valores


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _env_int(name: str, default: int) -> int:
    valor = _env(name)
    if not valor:
        return default
    try:
        numero = int(float(valor))
    except ValueError as exc:
        raise ConfigError(f"{name} debe ser un numero entero") from exc
    if numero < 0:
        raise ConfigError(f"{name} no puede ser negativo")
    return numero


def _env_float(name: str, default: float) -> float:
    valor = _env(name)
    if not valor:
        return default
    try:
        numero = float(valor)
    except ValueError as exc:
        raise ConfigError(f"{name} debe ser un numero") from exc
    if numero <= 0:
        raise ConfigError(f"{name} debe ser mayor que cero")
    return numero


def _validate_url(nombre: str, url: str) -> str:
    if not url:
        return ""
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ConfigError(f"{nombre} debe empezar con http:// o https://")
    return url


def cargar_config(args: argparse.Namespace) -> Config:
    env_file = Path(args.env_file).expanduser() if args.env_file else DEFAULT_ENV_FILE
    for clave, valor in _load_env_file(env_file).items():
        if clave.startswith(ALLOWED_ENV_PREFIXES) and clave not in os.environ:
            os.environ[clave] = valor

    cfg = Config(
        health_url=_validate_url("HEALTH_URL", _env("HEALTH_URL", "http://127.0.0.1:8000/health")),
        health_timeout=_env_float("HEALTH_TIMEOUT", 10.0),
        max_health_ms=_env_int("ALERT_MAX_HEALTH_MS", 0),
        min_products=_env_int("ALERT_MIN_PRODUCTS", 0),
        min_embeddings=_env_int("ALERT_MIN_EMBEDDINGS", 0),
        qdrant_readyz_url=_validate_url("ALERT_QDRANT_READYZ_URL", _env("ALERT_QDRANT_READYZ_URL")),
        search_url=_validate_url("ALERT_SEARCH_URL", _env("ALERT_SEARCH_URL")),
        search_modelo=_env("ALERT_SEARCH_MODELO", "clip") or "clip",
        search_timeout=_env_float("ALERT_SEARCH_TIMEOUT", 120.0),
        api_key=_env("ALERT_API_KEY"),
        max_search_ms=_env_int("ALERT_MAX_SEARCH_MS", 0),
        webhook_url=_validate_url("ALERT_WEBHOOK_URL", _env("ALERT_WEBHOOK_URL")),
        webhook_format=(_env("ALERT_WEBHOOK_FORMAT", "generic") or "generic").lower(),
        webhook_timeout=_env_float("ALERT_WEBHOOK_TIMEOUT", 10.0),
        telegram_bot_token=_env("ALERT_TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_env("ALERT_TELEGRAM_CHAT_ID"),
        dry_run=bool(args.dry_run),
        force_notify=bool(args.force_notify),
        verbose=bool(args.verbose),
    )

    state_env = _env("ALERT_STATE_FILE")
    if state_env:
        ruta_estado = Path(state_env).expanduser()
        if not ruta_estado.is_absolute():
            ruta_estado = BASE_DIR / ruta_estado
        cfg.state_file = ruta_estado
    else:
        cfg.state_file = DEFAULT_STATE_FILE

    imagen_env = _env("ALERT_SEARCH_IMAGE")
    if imagen_env:
        ruta = Path(imagen_env).expanduser()
        if not ruta.is_absolute():
            ruta = BASE_DIR / ruta
        cfg.search_image = ruta

    if not cfg.health_url:
        raise ConfigError("HEALTH_URL no puede estar vacia")

    if cfg.webhook_format not in WEBHOOK_FORMATS:
        raise ConfigError(
            "ALERT_WEBHOOK_FORMAT debe ser uno de: " + ", ".join(WEBHOOK_FORMATS)
        )

    if cfg.search_url and cfg.search_image is None:
        raise ConfigError(
            "ALERT_SEARCH_URL requiere ALERT_SEARCH_IMAGE (ruta de una imagen de prueba)"
        )
    if cfg.search_image is not None and not cfg.search_image.is_file():
        raise ConfigError(
            f"ALERT_SEARCH_IMAGE no existe: {cfg.search_image}"
        )

    if cfg.webhook_format == "telegram" and cfg.webhook_url:
        raise ConfigError(
            "Con ALERT_WEBHOOK_FORMAT=telegram no se usa ALERT_WEBHOOK_URL; "
            "configure ALERT_TELEGRAM_BOT_TOKEN y ALERT_TELEGRAM_CHAT_ID"
        )
    if cfg.webhook_format == "telegram" and not (
        cfg.telegram_bot_token and cfg.telegram_chat_id
    ):
        raise ConfigError(
            "ALERT_WEBHOOK_FORMAT=telegram requiere ALERT_TELEGRAM_BOT_TOKEN "
            "y ALERT_TELEGRAM_CHAT_ID"
        )
    if cfg.webhook_format != "telegram" and not cfg.webhook_url:
        # Sin webhook no es un error: se informa por stdout (util en cron).
        cfg.webhook_url = ""

    return cfg


# --------------------------------------------------------------------------- #
# Utilidades HTTP
# --------------------------------------------------------------------------- #
@dataclass
class Probe:
    nombre: str
    ok: bool
    detalle: str
    latencia_ms: float = 0.0


def _sanitizar(texto: str, secretos: Sequence[str]) -> str:
    for secreto in secretos:
        if secreto:
            texto = texto.replace(secreto, "***")
    return texto


def _peticion(
    url: str,
    timeout: float,
    *,
    data: Optional[bytes] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[int, bytes, float]:
    """GET/POST simple. Devuelve (status, cuerpo, milisegundos).

    Los codigos HTTP de error (4xx/5xx) se devuelven como resultado normal;
    solo los fallos de red/DNS/timeout lanzan ProbeError.
    """
    metodo = "POST" if data is not None else "GET"
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=metodo)
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            cuerpo = resp.read()
            return resp.status, cuerpo, (time.perf_counter() - inicio) * 1000.0
    except urllib.error.HTTPError as exc:
        try:
            cuerpo = exc.read()
        except Exception:
            cuerpo = b""
        return exc.code, cuerpo, (time.perf_counter() - inicio) * 1000.0
    except Exception as exc:  # noqa: BLE001 - se traduce a ProbeError
        raise ProbeError(f"sin respuesta ({type(exc).__name__})") from exc


def _multipart(
    campos: Dict[str, str], campo_archivo: str, ruta: Path
) -> Tuple[bytes, str]:
    frontera = f"----sublitex{uuid.uuid4().hex}"
    partes: List[bytes] = []
    for nombre, valor in campos.items():
        partes.append(
            (
                f"--{frontera}\r\n"
                f'Content-Disposition: form-data; name="{nombre}"\r\n\r\n'
                f"{valor}\r\n"
            ).encode("utf-8")
        )
    tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
    partes.append(
        (
            f"--{frontera}\r\n"
            f'Content-Disposition: form-data; name="{campo_archivo}"; '
            f'filename="{ruta.name}"\r\n'
            f"Content-Type: {tipo}\r\n\r\n"
        ).encode("utf-8")
    )
    partes.append(ruta.read_bytes())
    partes.append(f"\r\n--{frontera}--\r\n".encode("utf-8"))
    return b"".join(partes), f"multipart/form-data; boundary={frontera}"


# --------------------------------------------------------------------------- #
# Comprobaciones
# --------------------------------------------------------------------------- #
def comprobar_salud(cfg: Config) -> Probe:
    try:
        status, cuerpo, ms = _peticion(cfg.health_url, cfg.health_timeout)
    except ProbeError as exc:
        return Probe("api_health", False, str(exc))

    if status != 200:
        return Probe("api_health", False, f"HTTP {status}", ms)

    try:
        datos: Any = json.loads(cuerpo.decode("utf-8", "replace"))
    except ValueError:
        return Probe("api_health", False, "respuesta no es JSON", ms)

    if not isinstance(datos, dict):
        return Probe("api_health", False, "respuesta JSON inesperada", ms)

    problemas: List[str] = []
    if datos.get("status") not in (None, "ok"):
        problemas.append(f"status={datos.get('status')!r}")
    if datos.get("desfase_detectado") is not False:
        problemas.append(
            f"desfase_detectado={datos.get('desfase_detectado')!r} (debe ser false)"
        )
    if cfg.min_products:
        productos = datos.get("products")
        if not isinstance(productos, (int, float)) or productos < cfg.min_products:
            problemas.append(
                f"products={productos!r} < minimo {cfg.min_products}"
            )
    if cfg.min_embeddings:
        embeddings = datos.get("embeddings")
        if not isinstance(embeddings, (int, float)) or embeddings < cfg.min_embeddings:
            problemas.append(
                f"embeddings={embeddings!r} < minimo {cfg.min_embeddings}"
            )
    if cfg.max_health_ms and ms > cfg.max_health_ms:
        problemas.append(f"latencia {ms:.0f} ms > {cfg.max_health_ms} ms")

    detalle = "; ".join(problemas) if problemas else "salud correcta"
    return Probe("api_health", not problemas, detalle, ms)


def comprobar_qdrant(cfg: Config) -> Probe:
    try:
        status, _, ms = _peticion(cfg.qdrant_readyz_url, cfg.health_timeout)
    except ProbeError as exc:
        return Probe("qdrant_readyz", False, str(exc))
    if status != 200:
        return Probe("qdrant_readyz", False, f"HTTP {status}", ms)
    return Probe("qdrant_readyz", True, "readiness correcta", ms)


def comprobar_busqueda(cfg: Config) -> Probe:
    if cfg.search_image is None:
        return Probe("busqueda_sintetica", False, "falta ALERT_SEARCH_IMAGE")

    try:
        cuerpo, tipo_contenido = _multipart(
            {"modelo": cfg.search_modelo}, "file", cfg.search_image
        )
    except OSError as exc:
        return Probe("busqueda_sintetica", False, f"imagen ilegible ({type(exc).__name__})")

    headers = {"Content-Type": tipo_contenido}
    if cfg.api_key:
        headers["X-API-Key"] = cfg.api_key

    try:
        status, respuesta, ms = _peticion(
            cfg.search_url, cfg.search_timeout, data=cuerpo, headers=headers
        )
    except ProbeError as exc:
        return Probe("busqueda_sintetica", False, str(exc))

    if status != 200:
        return Probe("busqueda_sintetica", False, f"HTTP {status}", ms)

    try:
        datos = json.loads(respuesta.decode("utf-8", "replace"))
    except ValueError:
        return Probe("busqueda_sintetica", False, "respuesta no es JSON", ms)

    resultados = datos.get("resultados") if isinstance(datos, dict) else datos
    problemas: List[str] = []
    if not isinstance(resultados, list) or not resultados:
        problemas.append("respuesta sin resultados")
    if cfg.max_search_ms and ms > cfg.max_search_ms:
        problemas.append(f"latencia {ms:.0f} ms > {cfg.max_search_ms} ms")

    detalle = "; ".join(problemas) if problemas else "busqueda correcta"
    return Probe("busqueda_sintetica", not problemas, detalle, ms)


def ejecutar_comprobaciones(cfg: Config) -> List[Probe]:
    comprobaciones = [comprobar_salud]
    if cfg.qdrant_readyz_url:
        comprobaciones.append(comprobar_qdrant)
    if cfg.search_url:
        comprobaciones.append(comprobar_busqueda)

    resultados: List[Probe] = []
    for comprobacion in comprobaciones:
        try:
            resultados.append(comprobacion(cfg))
        except Exception as exc:  # noqa: BLE001 - una comprobacion no debe romper el resto
            resultados.append(
                Probe(comprobacion.__name__, False, f"error inesperado ({type(exc).__name__})")
            )
    return resultados


# --------------------------------------------------------------------------- #
# Notificacion
# --------------------------------------------------------------------------- #
def _mensaje(cfg: Config, estado: str, resultados: Sequence[Probe]) -> str:
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if estado == "fail":
        cabecera = "[ALERTA] Buscador visual: servicio degradado"
    else:
        cabecera = "[OK] Buscador visual: servicio recuperado"
    lineas = [cabecera, f"Hora: {ahora}", f"Host: {socket.gethostname()}"]
    for r in resultados:
        icono = "OK" if r.ok else "FALLO"
        lineas.append(f"- {r.nombre}: {icono} - {r.detalle} ({r.latencia_ms:.0f} ms)")
    return _sanitizar("\n".join(lineas), cfg.secrets())


def _destino_notificacion(cfg: Config) -> Tuple[str, Dict[str, str]]:
    """Devuelve (url, headers) del webhook segun el formato configurado."""
    if cfg.webhook_format == "telegram":
        url = f"https://api.telegram.org/bot{cfg.telegram_bot_token}/sendMessage"
        return url, {"Content-Type": "application/json"}
    return cfg.webhook_url, {"Content-Type": "application/json"}


def enviar_notificacion(cfg: Config, texto: str) -> Tuple[bool, str]:
    """Envia el mensaje. Devuelve (ok, detalle_sin_secretos)."""
    if not cfg.webhook_url and cfg.webhook_format != "telegram":
        return False, "ALERT_WEBHOOK_URL no configurada"

    url, headers = _destino_notificacion(cfg)

    if cfg.webhook_format == "discord":
        payload: Dict[str, Any] = {"content": texto}
    elif cfg.webhook_format == "slack":
        payload = {"text": texto}
    elif cfg.webhook_format == "telegram":
        payload = {
            "chat_id": cfg.telegram_chat_id,
            "text": texto,
            "disable_web_page_preview": True,
        }
    else:
        payload = {"text": texto}

    cuerpo = json.dumps(payload).encode("utf-8")
    try:
        status, respuesta, _ = _peticion(
            url, cfg.webhook_timeout, data=cuerpo, headers=headers
        )
    except ProbeError as exc:
        return False, _sanitizar(f"no se pudo contactar el webhook ({exc})", cfg.secrets())

    if not 200 <= status < 300:
        return False, f"el webhook respondio HTTP {status}"

    if cfg.webhook_format == "telegram":
        try:
            datos = json.loads(respuesta.decode("utf-8", "replace"))
        except ValueError:
            return False, "respuesta de Telegram no es JSON"
        if not isinstance(datos, dict) or not datos.get("ok"):
            return False, "Telegram rechazo el mensaje"

    return True, "notificacion enviada"


# --------------------------------------------------------------------------- #
# Estado (para avisar solo en cambios)
# --------------------------------------------------------------------------- #
def cargar_estado(ruta: Path) -> Optional[Dict[str, Any]]:
    if not ruta.is_file():
        return None
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(datos, dict) or datos.get("status") not in ("ok", "fail"):
        return None
    return datos


def guardar_estado(ruta: Path, estado: str, resultados: Sequence[Probe]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        ruta.parent.chmod(0o700)
    except OSError:
        pass
    contenido = {
        "version": 1,
        "status": estado,
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": [
            {"nombre": r.nombre, "ok": r.ok, "detalle": r.detalle,
             "latencia_ms": round(r.latencia_ms, 1)}
            for r in resultados
        ],
    }
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        temporal.chmod(0o600)
    except OSError:
        pass
    temporal.replace(ruta)


# --------------------------------------------------------------------------- #
# Principal
# --------------------------------------------------------------------------- #
def _imprimir(texto: str) -> None:
    try:
        print(texto, flush=True)
    except UnicodeEncodeError:
        print(texto.encode("ascii", "replace").decode("ascii"), flush=True)


def guardar_estado_seguro(cfg: Config, estado: str, resultados: Sequence[Probe]) -> None:
    """Guarda el estado sin impedir que el aviso se muestre o se envie."""
    try:
        guardar_estado(cfg.state_file, estado, resultados)
    except OSError as exc:
        _imprimir(
            f"[AVISO] No se pudo guardar el estado ({type(exc).__name__}); "
            "el proximo aviso podria repetirse."
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Alertas de salud, latencia y errores del buscador visual."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="comprueba y muestra el mensaje sin enviarlo")
    parser.add_argument("--force-notify", action="store_true",
                        help="envia una notificacion aunque no haya cambio de estado")
    parser.add_argument("--verbose", action="store_true",
                        help="muestra el detalle de cada comprobacion")
    parser.add_argument("--env-file", default="",
                        help="ruta alternativa al .env (por defecto <raiz>/.env)")
    args = parser.parse_args(argv)

    try:
        cfg = cargar_config(args)
    except ConfigError as exc:
        _imprimir(f"[CONFIG] {exc}")
        return EXIT_CONFIG

    resultados = ejecutar_comprobaciones(cfg)
    estado = "ok" if all(r.ok for r in resultados) else "fail"

    if cfg.verbose or estado == "fail":
        for r in resultados:
            _imprimir(
                f"{r.nombre}: {'OK' if r.ok else 'FALLO'} - {r.detalle} "
                f"({r.latencia_ms:.0f} ms)"
            )

    previo = cargar_estado(cfg.state_file)
    estado_previo = (previo or {}).get("status")

    # Primer arranque en OK: no se notifica nada (no hay cambio real).
    if estado_previo is None and estado == "ok":
        cambio = False
    else:
        cambio = estado_previo != estado

    notificar = cambio or cfg.force_notify

    if not notificar:
        _imprimir(f"Estado: {estado} (sin cambios; no se notifica)")
        guardar_estado_seguro(cfg, estado, resultados)
        return EXIT_OK if estado == "ok" else EXIT_ALERTA

    mensaje = _mensaje(cfg, estado, resultados)

    if cfg.dry_run:
        _imprimir("[DRY-RUN] Notificacion que se enviaria:")
        _imprimir(mensaje)
        return EXIT_OK if estado == "ok" else EXIT_ALERTA

    # Sin webhook configurado el aviso se escribe en stdout (cron/systemd lo
    # puede redirigir a su propio log). No es un error de entrega.
    if not cfg.webhook_url and cfg.webhook_format != "telegram":
        _imprimir("[STDOUT] Webhook no configurado; aviso:")
        _imprimir(mensaje)
        guardar_estado_seguro(cfg, estado, resultados)
        return EXIT_OK if estado == "ok" else EXIT_ALERTA

    ok, detalle = enviar_notificacion(cfg, mensaje)
    if not ok:
        # No se guarda el estado: el aviso se reintenta en la proxima ejecucion.
        _imprimir(f"[NOTIFICACION] {detalle}")
        _imprimir("Aviso pendiente:")
        _imprimir(mensaje)
        _imprimir("Estado no actualizado; se reintentara en la siguiente ejecucion.")
        return EXIT_NOTIFICACION

    _imprimir(f"[NOTIFICACION] {detalle}")
    guardar_estado_seguro(cfg, estado, resultados)
    _imprimir(f"Estado: {estado}")
    return EXIT_OK if estado == "ok" else EXIT_ALERTA


if __name__ == "__main__":
    sys.exit(main())
