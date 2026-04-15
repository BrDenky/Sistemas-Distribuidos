"""
shared/schemas.py
=================
Fase Lab — JSON Schemas formales para validación de mensajes entre microservicios.

Actividad 1 del laboratorio:
  - GESTURE_REQUEST_SCHEMA : Schema del REQUEST  (Cliente → API Gateway → Gesture Detector)
  - GESTURE_RESPONSE_SCHEMA: Schema del RESPONSE (Gesture Detector → API Gateway → Cliente)

Uso:
    from shared.schemas import validate_gesture_request, validate_gesture_response
    errors = validate_gesture_request(data)   # [] si es válido
    errors = validate_gesture_response(data)  # [] si es válido
"""

import json
from typing import Any, Dict, List

# ─────────────────────────────────────────────────────────────
# ACTIVIDAD 1 — Par de schemas con validación formal
# Componentes: API Gateway  <──>  Gesture Detector
# ─────────────────────────────────────────────────────────────

# ── REQUEST: lo que el cliente envía al API Gateway ──────────
GESTURE_REQUEST_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "urn:distributed3d:gesture-request:v1",
    "title": "GestureRequest",
    "description": (
        "Evento de gesto enviado por un cliente MediaPipe al API Gateway. "
        "Define la forma exacta que debe tener el JSON antes de ser enrutado "
        "al microservicio Gesture Detector."
    ),
    "type": "object",
    "required": ["client_id", "landmarks"],
    "additionalProperties": False,
    "properties": {
        "client_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 64,
            "description": "Identificador único del cliente que envía el gesto.",
            "examples": ["client_001", "user-abc123"],
        },
        "gesture": {
            "type": "string",
            "enum": [
                "pinch", "grab",
                "swipe_left", "swipe_right",
                "swipe_up", "swipe_down",
                "open_hand", "unknown",
            ],
            "description": (
                "Tipo de gesto pre-clasificado. Si se omite, el Gesture Detector "
                "lo clasificará automáticamente a partir de los landmarks."
            ),
            "default": "unknown",
        },
        "landmarks": {
            "type": "array",
            "description": "Lista de 21 puntos de referencia de la mano (MediaPipe Hand Landmarks).",
            "minItems": 1,
            "maxItems": 21,
            "items": {
                "type": "object",
                "required": ["x", "y", "z"],
                "additionalProperties": False,
                "properties": {
                    "x": {
                        "type": "number",
                        "minimum": -1.0,
                        "maximum": 2.0,
                        "description": "Coordenada X normalizada [0,1] en la imagen.",
                    },
                    "y": {
                        "type": "number",
                        "minimum": -1.0,
                        "maximum": 2.0,
                        "description": "Coordenada Y normalizada [0,1] en la imagen.",
                    },
                    "z": {
                        "type": "number",
                        "description": "Profundidad relativa respecto a la muñeca.",
                    },
                },
            },
        },
        "timestamp": {
            "type": "number",
            "minimum": 0,
            "description": "Epoch Unix (segundos) del momento de captura. Auto-generado si se omite.",
        },
    },
}


# ── RESPONSE: lo que el Gesture Detector devuelve al cliente ─
GESTURE_RESPONSE_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "urn:distributed3d:gesture-response:v1",
    "title": "GestureResponse",
    "description": (
        "Respuesta del Gesture Detector tras clasificar un gesto y solicitar "
        "al Physics Engine que actualice el estado de las partículas 3D."
    ),
    "type": "object",
    "required": ["status", "client_id", "gesture", "queued", "physics"],
    "additionalProperties": False,
    "properties": {
        "status": {
            "type": "string",
            "enum": ["processed", "error"],
            "description": "Estado del procesamiento.",
        },
        "client_id": {
            "type": "string",
            "minLength": 1,
            "description": "Eco del client_id recibido en el request.",
        },
        "gesture": {
            "type": "string",
            "enum": [
                "pinch", "grab",
                "swipe_left", "swipe_right",
                "swipe_up", "swipe_down",
                "open_hand", "unknown",
            ],
            "description": "Gesto clasificado por el microservicio.",
        },
        "queued": {
            "type": "boolean",
            "description": "True si el evento fue publicado exitosamente en RabbitMQ.",
        },
        "physics": {
            "type": "object",
            "description": "Resultado del Physics Engine tras aplicar la física.",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["updated", "error"],
                },
                "version": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Versión del mundo tras la actualización.",
                },
                "particle_count": {
                    "type": "integer",
                    "minimum": 0,
                },
                "persisted": {
                    "type": "boolean",
                    "description": "True si el estado se persistió correctamente en PostgreSQL.",
                },
            },
        },
        "metrics": {
            "type": "object",
            "description": "Métricas de rendimiento añadidas por el middleware (opcional).",
            "properties": {
                "request_bytes":    {"type": "integer"},
                "response_bytes":   {"type": "integer"},
                "latency_ms":       {"type": "number"},
                "processing_ms":    {"type": "number"},
            },
        },
    },
}


# ─────────────────────────────────────────────────────────────
# Validador ligero sin dependencias externas
# (usa jsonschema si está disponible, si no hace validación básica)
# ─────────────────────────────────────────────────────────────

def _validate_with_jsonschema(data: Any, schema: Dict) -> List[str]:
    """Valida usando la librería jsonschema (Draft-7). Retorna lista de errores."""
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        return [f"{' -> '.join(str(p) for p in e.path) or 'root'}: {e.message}" for e in errors]
    except ImportError:
        return _validate_basic(data, schema)


def _validate_basic(data: Any, schema: Dict) -> List[str]:
    """Validación básica sin dependencias: verifica required fields y tipos raíz."""
    errors = []
    if schema.get("type") == "object":
        if not isinstance(data, dict):
            return [f"root: se esperaba un objeto, se recibió {type(data).__name__}"]
        for field in schema.get("required", []):
            if field not in data:
                errors.append(f"root -> {field}: campo requerido ausente")
        props = schema.get("properties", {})
        for key, val in data.items():
            if key in props:
                expected_type = props[key].get("type")
                type_map = {
                    "string": str, "number": (int, float),
                    "integer": int, "boolean": bool,
                    "array": list, "object": dict,
                }
                if expected_type and expected_type in type_map:
                    if not isinstance(val, type_map[expected_type]):
                        errors.append(
                            f"root -> {key}: tipo incorrecto "
                            f"(esperado={expected_type}, recibido={type(val).__name__})"
                        )
    return errors


def validate_gesture_request(data: Any) -> List[str]:
    """
    Valida un payload de request contra GESTURE_REQUEST_SCHEMA.

    Returns:
        Lista vacía [] si los datos son válidos.
        Lista de strings con los errores encontrados si no lo son.
    """
    return _validate_with_jsonschema(data, GESTURE_REQUEST_SCHEMA)


def validate_gesture_response(data: Any) -> List[str]:
    """
    Valida un payload de response contra GESTURE_RESPONSE_SCHEMA.

    Returns:
        Lista vacía [] si los datos son válidos.
        Lista de strings con los errores encontrados si no lo son.
    """
    return _validate_with_jsonschema(data, GESTURE_RESPONSE_SCHEMA)


def schema_to_json(schema: Dict, indent: int = 2) -> str:
    """Serializa un schema a JSON formateado para impresión/logging."""
    return json.dumps(schema, indent=indent, ensure_ascii=False)
