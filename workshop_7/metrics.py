"""
shared/metrics.py
=================
Fase Lab — Middleware y utilidades para medir métricas de transferencia de datos
entre microservicios del sistema distribuido.

Métricas capturadas:
  - request_bytes  : Tamaño del payload de entrada (bytes)
  - response_bytes : Tamaño del payload de salida  (bytes)
  - latency_ms     : Tiempo total de la operación  (ms) — ida y vuelta desde el gateway
  - processing_ms  : Tiempo de procesamiento interno del microservicio (ms)
                     (excluye la transferencia de red, incluye lógica + DB + RabbitMQ)

Uso en FastAPI:
    from shared.metrics import MetricsMiddleware, measure
    app.add_middleware(MetricsMiddleware)

    @app.post("/process")
    async def my_endpoint(data: dict):
        with measure("mi_operacion") as m:
            result = heavy_computation(data)
        return {**result, "processing_ms": m.elapsed_ms}
"""

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generator, List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Estructuras de datos
# ─────────────────────────────────────────────────────────────

@dataclass
class RequestMetrics:
    """Métricas capturadas para una petición HTTP individual."""
    path: str
    method: str
    request_bytes: int = 0
    response_bytes: int = 0
    latency_ms: float = 0.0        # Tiempo total (desde req hasta última byte de response)
    processing_ms: float = 0.0     # Tiempo del handler (sin contar lectura del body)
    status_code: int = 0
    timestamp: float = field(default_factory=time.time)
    service: str = "unknown"
    validation_errors: List[str] = field(default_factory=list)
    schema_validated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path":              self.path,
            "method":            self.method,
            "request_bytes":     self.request_bytes,
            "response_bytes":    self.response_bytes,
            "latency_ms":        round(self.latency_ms, 3),
            "processing_ms":     round(self.processing_ms, 3),
            "status_code":       self.status_code,
            "timestamp":         self.timestamp,
            "service":           self.service,
            "schema_validated":  self.schema_validated,
            "validation_errors": self.validation_errors,
        }


@dataclass
class Timer:
    """Objeto retornado por el context manager `measure()`."""
    name: str
    _start: float = field(default_factory=time.perf_counter)
    elapsed_ms: float = 0.0

    def stop(self) -> float:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
        return self.elapsed_ms


# ─────────────────────────────────────────────────────────────
# Registro en memoria (ring-buffer simple, sin dependencias)
# ─────────────────────────────────────────────────────────────

class MetricsRegistry:
    """Almacena las últimas N métricas en memoria para consulta vía /metrics."""

    def __init__(self, max_entries: int = 500):
        self._entries: List[RequestMetrics] = []
        self._max = max_entries

    def record(self, m: RequestMetrics) -> None:
        if len(self._entries) >= self._max:
            self._entries.pop(0)
        self._entries.append(m)

    def summary(self) -> Dict[str, Any]:
        if not self._entries:
            return {"total_requests": 0}

        latencies    = [e.latency_ms    for e in self._entries]
        proc_times   = [e.processing_ms for e in self._entries]
        req_sizes    = [e.request_bytes  for e in self._entries]
        resp_sizes   = [e.response_bytes for e in self._entries]

        return {
            "total_requests":      len(self._entries),
            "avg_latency_ms":      round(sum(latencies)  / len(latencies), 3),
            "max_latency_ms":      round(max(latencies), 3),
            "min_latency_ms":      round(min(latencies), 3),
            "avg_processing_ms":   round(sum(proc_times) / len(proc_times), 3),
            "avg_request_bytes":   round(sum(req_sizes)  / len(req_sizes), 1),
            "avg_response_bytes":  round(sum(resp_sizes) / len(resp_sizes), 1),
            "total_bytes_in":      sum(req_sizes),
            "total_bytes_out":     sum(resp_sizes),
            "schema_validated_pct": round(
                sum(1 for e in self._entries if e.schema_validated) / len(self._entries) * 100, 1
            ),
        }

    def recent(self, n: int = 20) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._entries[-n:]]


# Instancia global compartida dentro de un proceso
_registry = MetricsRegistry()


def get_registry() -> MetricsRegistry:
    return _registry


# ─────────────────────────────────────────────────────────────
# Middleware FastAPI / Starlette
# ─────────────────────────────────────────────────────────────

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware que intercepta TODAS las peticiones HTTP e inyecta métricas.

    Para cada request mide:
      - Bytes del body de entrada
      - Bytes del body de salida
      - Latencia total (request → response)
      - Tiempo de procesamiento del handler (sin tiempo de lectura del body)

    Añade la cabecera X-Metrics-JSON a cada response con las métricas crudas.
    También registra cada petición en el MetricsRegistry global para el endpoint /metrics.
    """

    def __init__(self, app, service_name: str = "unknown"):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        t_start = time.perf_counter()

        # ── Medir body de entrada ──────────────────────────────
        try:
            body_bytes = await request.body()
            request_bytes = len(body_bytes)
        except Exception:
            request_bytes = 0

        # ── Ejecutar el handler ────────────────────────────────
        t_handler_start = time.perf_counter()
        response = await call_next(request)
        processing_ms = (time.perf_counter() - t_handler_start) * 1000

        # ── Capturar la response body ──────────────────────────
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        response_bytes = len(resp_body)

        # ── Calcular latencia total ────────────────────────────
        latency_ms = (time.perf_counter() - t_start) * 1000

        # ── Registrar ─────────────────────────────────────────
        m = RequestMetrics(
            path=request.url.path,
            method=request.method,
            request_bytes=request_bytes,
            response_bytes=response_bytes,
            latency_ms=latency_ms,
            processing_ms=processing_ms,
            status_code=response.status_code,
            service=self.service_name,
        )
        _registry.record(m)

        logger.info(
            "[METRICS] %s %s | in=%dB out=%dB | latency=%.2fms proc=%.2fms | %d",
            request.method, request.url.path,
            request_bytes, response_bytes,
            latency_ms, processing_ms,
            response.status_code,
        )

        # ── Reconstruir response con la cabecera de métricas ──
        headers = dict(response.headers)
        headers["X-Metrics-JSON"] = json.dumps({
            "request_bytes":   request_bytes,
            "response_bytes":  response_bytes,
            "latency_ms":      round(latency_ms, 3),
            "processing_ms":   round(processing_ms, 3),
        })

        return Response(
            content=resp_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )


# ─────────────────────────────────────────────────────────────
# Context manager para medir bloques de código internos
# ─────────────────────────────────────────────────────────────

@contextmanager
def measure(name: str = "block") -> Generator[Timer, None, None]:
    """
    Context manager para medir el tiempo de ejecución de un bloque de código.

    Ejemplo:
        with measure("db_query") as t:
            rows = await db.fetch_all_particles()
        logger.info("DB query took %.2f ms", t.elapsed_ms)
    """
    timer = Timer(name=name)
    try:
        yield timer
    finally:
        timer.stop()
        logger.debug("[TIMER] %s took %.3f ms", name, timer.elapsed_ms)


# ─────────────────────────────────────────────────────────────
# Utilidades de serialización para el script de laboratorio
# ─────────────────────────────────────────────────────────────

def payload_size(data: Any) -> int:
    """Calcula el tamaño en bytes de un objeto serializado como JSON UTF-8."""
    return len(json.dumps(data, ensure_ascii=False).encode("utf-8"))


def format_metrics_report(metrics_list: List[Dict[str, Any]]) -> str:
    """Formatea una lista de métricas como tabla de texto para el reporte."""
    if not metrics_list:
        return "Sin métricas disponibles."

    header = (
        f"{'#':<4} {'Endpoint':<35} {'Req(B)':<9} {'Resp(B)':<9} "
        f"{'Latency(ms)':<13} {'Proc(ms)':<12} {'Status':<7} {'Schema'}"
    )
    sep = "─" * len(header)
    rows = [header, sep]

    for i, m in enumerate(metrics_list, 1):
        validated = "✅" if m.get("schema_validated") else "──"
        rows.append(
            f"{i:<4} {m.get('path',''):<35} {m.get('request_bytes',0):<9} "
            f"{m.get('response_bytes',0):<9} {m.get('latency_ms',0):<13.2f} "
            f"{m.get('processing_ms',0):<12.2f} {m.get('status_code',0):<7} {validated}"
        )

    return "\n".join(rows)
