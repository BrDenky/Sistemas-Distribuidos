# API Gateway - Intermediario entre el cliente y los microservicios
# Fase Lab: Integración de JSON Schema (Activity 1) + Métricas (Activities 1 & 2)
import httpx
import json
import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Modelos compartidos entre microservicios
from shared.models import GestureEvent, HealthResponse

# ── [LAB] Schemas formales y métricas ────────────────────────────────────────
from shared.schemas import (
    validate_gesture_request,
    GESTURE_REQUEST_SCHEMA,
    GESTURE_RESPONSE_SCHEMA,
)
from shared.metrics import MetricsMiddleware, get_registry, payload_size
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creamos Instancia Principal
app = FastAPI(
    title="API Gateway — Sistema Distribuido 3D",
    description=(
        "Punto de entrada centralizado que enruta tráfico a los microservicios. "
        "Fase Lab: Validación JSON Schema + Métricas de transferencia."
    ),
    version="1.1.0",
)

# ── [LAB] Middleware de métricas (debe registrarse ANTES que CORS) ────────────
app.add_middleware(MetricsMiddleware, service_name="api_gateway")
# ─────────────────────────────────────────────────────────────────────────────

# Configuración de CORS - Acceso abierto para que cualquier origen pueda conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direcciones internas de los microservicios (corriendo en Docker)
GESTURE_DETECTOR_URL = "http://gesture_detector:8001"
PHYSICS_ENGINE_URL   = "http://physics_engine:8002"
STATE_RENDERER_URL   = "http://state_renderer:8003"


# ═══════════════════════════════════════════════════════════════
# Endpoints del API Gateway
# ═══════════════════════════════════════════════════════════════

# Health Check — Verifica que el API Gateway esté funcionando
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        service="api_gateway",
        status="ok",
        timestamp=time.time(),
    )


# Health Check — Verifica el estado de todos los microservicios registrados
@app.get("/health/services", tags=["Health"])
async def services_health():
    services = {
        "gesture_detector": GESTURE_DETECTOR_URL,
        "physics_engine":   PHYSICS_ENGINE_URL,
        "state_renderer":   STATE_RENDERER_URL,
    }
    results = {}
    async with httpx.AsyncClient(timeout=3.0) as client:
        for name, url in services.items():
            try:
                resp = await client.get(f"{url}/health")
                results[name] = resp.json()
            except Exception as e:
                results[name] = {"status": "unreachable", "error": str(e)}
    return results


# ── [LAB] ACTIVIDAD 1: Gestos con validación JSON Schema ─────────────────────
# Recibe un evento de gesto, lo valida contra el schema formal y lo reenvía
# al Gesture Detector. Mide bytes, latencia y overhead de procesamiento.
@app.post("/gestures", tags=["Gestures"])
async def receive_gesture(request: Request, event: GestureEvent):
    """
    **[Activity 1 — Con JSON Schema]**

    Recibe un gesto del cliente, valida el payload contra `GESTURE_REQUEST_SCHEMA`
    y lo enruta al Gesture Detector. Retorna la respuesta del detector junto con
    métricas de transferencia embebidas.
    """
    t_start = time.perf_counter()

    # ── 1. Obtener el body crudo para medir bytes y validar schema ────────────
    raw_body = await request.body()
    request_bytes = len(raw_body)

    try:
        raw_dict = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON mal formado")

    # ── 2. Validación formal contra JSON Schema (Activity 1) ─────────────────
    schema_errors = validate_gesture_request(raw_dict)
    schema_valid  = len(schema_errors) == 0

    if not schema_valid:
        logger.warning("[SCHEMA] Request inválido: %s", schema_errors)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "JSON Schema validation failed",
                "schema_id": GESTURE_REQUEST_SCHEMA["$id"],
                "errors": schema_errors,
            },
        )
    logger.info("[SCHEMA] Request validado correctamente contra %s", GESTURE_REQUEST_SCHEMA["$id"])

    # ── 3. Reenviar al Gesture Detector ──────────────────────────────────────
    t_proxy_start = time.perf_counter()
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(
                f"{GESTURE_DETECTOR_URL}/process",
                json=event.model_dump(),
            )
            resp.raise_for_status()
            response_data = resp.json()
        except httpx.RequestError as e:
            logger.error(f"Error contactando gesture_detector: {e}")
            raise HTTPException(status_code=503, detail="Gesture Detector no disponible")

    proxy_ms = (time.perf_counter() - t_proxy_start) * 1000

    # ── 4. Inyectar métricas en la respuesta ─────────────────────────────────
    response_bytes = payload_size(response_data)
    latency_ms     = (time.perf_counter() - t_start) * 1000

    metrics = {
        "request_bytes":   request_bytes,
        "response_bytes":  response_bytes,
        "latency_ms":      round(latency_ms, 3),
        "processing_ms":   round(proxy_ms, 3),
        "schema_validated": schema_valid,
        "schema_id":        GESTURE_REQUEST_SCHEMA["$id"],
    }
    logger.info("[METRICS/gestures] %s", metrics)

    return {**response_data, "metrics": metrics}
# ─────────────────────────────────────────────────────────────────────────────


# Estado — Obtiene el estado del mundo (sin schema — Activity 2 base)
@app.get("/state", tags=["State"])
async def get_world_state():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{STATE_RENDERER_URL}/state")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            logger.error(f"Error contactando state_renderer: {e}")
            raise HTTPException(status_code=503, detail="State Renderer no disponible")


# ── [LAB] ACTIVIDAD 2: Física sin JSON Schema predefinido ────────────────────
# Enruta al Physics Engine para leer partículas en formato libre (sin schema).
# Idéntica medición de métricas que Activity 1, pero sin validación formal.
@app.get("/particles", tags=["Physics"])
async def get_particles_free():
    """
    **[Activity 2 — Sin JSON Schema]**

    Lee el estado de las partículas directamente desde el Physics Engine
    (que a su vez lee desde la réplica de PostgreSQL). No valida contra un
    schema predefinido — el JSON se acepta tal como llega.
    Métricas incluidas en la respuesta para comparación con Activity 1.
    """
    t_start = time.perf_counter()

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{PHYSICS_ENGINE_URL}/particles")
            resp.raise_for_status()
            response_data = resp.json()
        except httpx.RequestError as e:
            logger.error(f"Error contactando physics_engine: {e}")
            raise HTTPException(status_code=503, detail="Physics Engine no disponible")

    latency_ms     = (time.perf_counter() - t_start) * 1000
    response_bytes = payload_size(response_data)

    metrics = {
        "request_bytes":    0,   # GET no tiene body
        "response_bytes":   response_bytes,
        "latency_ms":       round(latency_ms, 3),
        "processing_ms":    round(latency_ms, 3),
        "schema_validated": False,   # Activity 2: sin schema
        "schema_id":        None,
    }
    logger.info("[METRICS/particles] %s", metrics)

    return {**response_data, "metrics": metrics}
# ─────────────────────────────────────────────────────────────────────────────


# Física — Envía datos al Physics Engine para calcular nuevas posiciones
@app.post("/physics/update", tags=["Physics"])
async def trigger_physics_update(data: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(
                f"{PHYSICS_ENGINE_URL}/update",
                json=data,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            logger.error(f"Error contactando physics_engine: {e}")
            raise HTTPException(status_code=503, detail="Physics Engine no disponible")


# ── [LAB] Endpoints de Schemas y Métricas ────────────────────────────────────

@app.get("/schemas/gesture-request", tags=["Lab — Schemas"])
async def get_gesture_request_schema():
    """Devuelve el JSON Schema formal del request de gestos (Activity 1)."""
    return GESTURE_REQUEST_SCHEMA


@app.get("/schemas/gesture-response", tags=["Lab — Schemas"])
async def get_gesture_response_schema():
    """Devuelve el JSON Schema formal del response de gestos (Activity 1)."""
    return GESTURE_RESPONSE_SCHEMA


@app.get("/metrics", tags=["Lab — Métricas"])
async def get_metrics():
    """
    Devuelve el resumen estadístico de todas las peticiones procesadas
    y las últimas 20 entradas del registro de métricas.
    Útil para el reporte del laboratorio.
    """
    registry = get_registry()
    return {
        "summary": registry.summary(),
        "recent_requests": registry.recent(20),
    }


@app.delete("/metrics", tags=["Lab — Métricas"])
async def reset_metrics():
    """Reinicia el registro de métricas (útil entre pruebas del laboratorio)."""
    get_registry()._entries.clear()
    return {"status": "metrics_reset", "timestamp": time.time()}
# ─────────────────────────────────────────────────────────────────────────────
