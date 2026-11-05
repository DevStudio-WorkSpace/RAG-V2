#!/usr/bin/env python3
"""Mide latencias reales del endpoint FastAPI respaldado por Qdrant."""

import argparse
import asyncio
import math
import mimetypes
import os
import sys
import time
from pathlib import Path

import httpx


def percentile(samples: list[float], percentile_value: float) -> float:
    ordered = sorted(samples)
    rank = max(1, math.ceil(percentile_value * len(ordered)))
    return ordered[rank - 1]


async def run_load_test(args: argparse.Namespace) -> int:
    image_path = Path(args.image)
    if not image_path.is_file():
        raise FileNotFoundError(f"No existe la imagen de prueba: {image_path}")
    if args.requests < 1 or args.concurrency < 1 or args.warmup < 0:
        raise ValueError("requests/concurrency deben ser > 0 y warmup >= 0")

    image = image_path.read_bytes()
    content_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
    headers = {}
    api_key = os.getenv("API_CLIENT_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key

    timeout = httpx.Timeout(args.timeout)
    limits = httpx.Limits(
        max_connections=args.concurrency,
        max_keepalive_connections=args.concurrency,
    )
    async with httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        headers=headers,
    ) as client:
        request_data = {
            "modo": "auto",
            "modelo": "clip",
        }

        for _ in range(args.warmup):
            response = await client.post(
                args.url,
                data=request_data,
                files={"file": (image_path.name, image, content_type)},
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"Warmup devolvió HTTP {response.status_code}: "
                    f"{response.text[:300]}"
                )

        semaphore = asyncio.Semaphore(args.concurrency)
        latencies: list[float] = []
        failures: list[str] = []

        async def send_request(index: int):
            async with semaphore:
                started = time.perf_counter()
                try:
                    response = await client.post(
                        args.url,
                        data=request_data,
                        files={"file": (image_path.name, image, content_type)},
                    )
                    elapsed = (time.perf_counter() - started) * 1000
                    if response.status_code == 200:
                        latencies.append(elapsed)
                    else:
                        failures.append(f"#{index}: HTTP {response.status_code}")
                except httpx.HTTPError as error:
                    failures.append(f"#{index}: {type(error).__name__}: {error}")

        started = time.perf_counter()
        await asyncio.gather(
            *(send_request(index) for index in range(1, args.requests + 1))
        )
        wall_seconds = time.perf_counter() - started

    print(f"URL: {args.url}")
    print(
        f"Solicitudes: {args.requests}; concurrencia: {args.concurrency}; "
        f"éxitos: {len(latencies)}; errores: {len(failures)}"
    )
    if latencies:
        print(f"p50: {percentile(latencies, 0.50):.1f} ms")
        print(f"p95: {percentile(latencies, 0.95):.1f} ms")
        print(f"Throughput: {len(latencies) / wall_seconds:.2f} solicitudes/s")
    if failures:
        for failure in failures[:10]:
            print(f"ERROR {failure}", file=sys.stderr)
        if len(failures) > 10:
            print(f"... y {len(failures) - 10} errores más", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000/search/image",
        help="URL del endpoint de búsqueda",
    )
    parser.add_argument("--image", required=True, help="Imagen real para la consulta")
    parser.add_argument("--requests", type=int, default=50, help="Peticiones medidas")
    parser.add_argument("--concurrency", type=int, default=10, help="Peticiones simultáneas")
    parser.add_argument("--warmup", type=int, default=2, help="Peticiones de calentamiento")
    parser.add_argument("--timeout", type=float, default=180, help="Timeout por petición (s)")
    args = parser.parse_args()
    return asyncio.run(run_load_test(args))


if __name__ == "__main__":
    raise SystemExit(main())
