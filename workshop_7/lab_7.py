# Script para pruebas JSONO Transfer Lab

# Ejecuta y mide ambas actividades del laboratorio
# Actividad 1 - Con JSON Schema
    # Componentes: API Gateway (Máquina con IP 192.168.0.106) -> Gesture Detector (Máquina con IP 192.168.0.108)
    # Servicio: POST /gestures
    # Valida el request y el response contra schemas formales (Draft-7).
    # Mide: bytes transferidos, latencia total, overhead de procesamiento.

# Actividad 2 - Sin JSON Schema predefinido
    # Componentes: API Gateway (Máquina con IP 192.168.0.106) -> Physics Engine (Máquina con IP 192.168.0.108)
    # Servicio: GET /particles
    # Sin validación formal. JSON libre aceptado tal como llega.
    # Mide: bytes transferidos, latencia total, overhead de procesamiento.


import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error


# Configuración por defecto
DEFAULT_HOST       = "localhost"
DEFAULT_PORT       = 8000
DEFAULT_ITERATIONS = 10


# Payloads de prueba

# Request VÁLIDO — debe pasar el schema
VALID_GESTURE_PAYLOAD = {
    "client_id": "lab_client_01",
    "gesture": "swipe_right",
    "landmarks": [
        {"x": 0.5,  "y": 0.5,  "z": 0.0},   # 0  Muñeca
        {"x": 0.52, "y": 0.45, "z": -0.01},  # 1
        {"x": 0.54, "y": 0.40, "z": -0.02},  # 2
        {"x": 0.56, "y": 0.35, "z": -0.03},  # 3
        {"x": 0.58, "y": 0.30, "z": -0.04},  # 4  Pulgar
        {"x": 0.53, "y": 0.32, "z": -0.01},  # 5
        {"x": 0.55, "y": 0.27, "z": -0.02},  # 6
        {"x": 0.57, "y": 0.23, "z": -0.03},  # 7
        {"x": 0.59, "y": 0.20, "z": -0.04},  # 8  Índice
        {"x": 0.51, "y": 0.33, "z": -0.01},  # 9
        {"x": 0.53, "y": 0.28, "z": -0.02},  # 10
        {"x": 0.55, "y": 0.24, "z": -0.03},  # 11
        {"x": 0.50, "y": 0.34, "z": -0.01},  # 12 Medio
        {"x": 0.52, "y": 0.29, "z": -0.02},  # 13
        {"x": 0.54, "y": 0.25, "z": -0.03},  # 14
        {"x": 0.49, "y": 0.35, "z": -0.01},  # 15 Anular
        {"x": 0.51, "y": 0.30, "z": -0.02},  # 16
        {"x": 0.53, "y": 0.26, "z": -0.03},  # 17
        {"x": 0.48, "y": 0.36, "z": -0.01},  # 18 Meñique
        {"x": 0.50, "y": 0.31, "z": -0.02},  # 19
        {"x": 0.52, "y": 0.27, "z": -0.03},  # 20
    ],
    "timestamp": None,  # Se genera automáticamente en el servidor
}

# Request INVÁLIDO — debe ser rechazado por el schema (falta client_id)
INVALID_GESTURE_PAYLOAD = {
    "gesture": "swipe_right",
    "landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0}],
    # client_id AUSENTE  →  schema error
}


# HTTP helper sin dependencias externas
# POST JSON y retorna (response_dict, request_bytes, response_bytes, latency_ms)
def http_post(url: str, data: dict, timeout: float = 10.0) -> Dict[str, Any]:
    body     = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req      = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw        = resp.read()
            latency_ms = (time.perf_counter() - t0) * 1000
            return {
                "ok":             True,
                "status":         resp.status,
                "data":           json.loads(raw),
                "request_bytes":  len(body),
                "response_bytes": len(raw),
                "latency_ms":     round(latency_ms, 3),
            }
    except urllib.error.HTTPError as e:
        raw        = e.read()
        latency_ms = (time.perf_counter() - t0) * 1000
        return {
            "ok":             False,
            "status":         e.code,
            "data":           json.loads(raw) if raw else {},
            "request_bytes":  len(body),
            "response_bytes": len(raw),
            "latency_ms":     round(latency_ms, 3),
        }

# GET y retorna (response_dict, response_bytes, latency_ms)
def http_get(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    t0  = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw        = resp.read()
            latency_ms = (time.perf_counter() - t0) * 1000
            return {
                "ok":             True,
                "status":         resp.status,
                "data":           json.loads(raw),
                "request_bytes":  0,
                "response_bytes": len(raw),
                "latency_ms":     round(latency_ms, 3),
            }
    except urllib.error.HTTPError as e:
        raw        = e.read()
        latency_ms = (time.perf_counter() - t0) * 1000
        return {
            "ok":             False,
            "status":         e.code,
            "data":           json.loads(raw) if raw else {},
            "request_bytes":  0,
            "response_bytes": len(raw),
            "latency_ms":     round(latency_ms, 3),
        }


# Runners de cada actividad
# Actividad 1 — CON JSON Schema
# Endpoint: POST /gestures
# Componentes: API Gateway → Gesture Detector
def run_activity1(base_url: str, iterations: int) -> Dict[str, Any]:
    print("\n" + "═" * 70)
    print("  ACTIVITY 1 — POST /gestures  (API Gateway → Gesture Detector)")
    print("  Con validación JSON Schema formal (Draft-7)")
    print("═" * 70)

    url     = f"{base_url}/gestures"
    results = []

    # 1a. Prueba con payload VÁLIDO
    print(f"\n  ► Prueba 1a: Payload VÁLIDO — {iterations} iteraciones")
    valid_runs = []
    for i in range(iterations):
        payload = {**VALID_GESTURE_PAYLOAD, "timestamp": time.time()}
        r = http_post(url, payload)
        valid_runs.append(r)
        schema_ok = r["data"].get("metrics", {}).get("schema_validated", "?")
        print(
            f"    [{i+1:02d}] Status={r['status']} | "
            f"req={r['request_bytes']}B resp={r['response_bytes']}B | "
            f"latency={r['latency_ms']}ms | schema={schema_ok}"
        )
        time.sleep(0.1)  # Evitar flood

    # 1b. Prueba con payload INVÁLIDO
    print(f"\n  ► Prueba 1b: Payload INVÁLIDO (falta client_id) — 3 iteraciones")
    invalid_runs = []
    for i in range(3):
        r = http_post(url, INVALID_GESTURE_PAYLOAD)
        invalid_runs.append(r)
        rejected = r["status"] == 422
        print(
            f"    [{i+1}] Status={r['status']} | "
            f"Rechazado correctamente = {'✅ SÍ' if rejected else '❌ NO'}"
        )
        time.sleep(0.1)

    # Calcular estadísticas
    ok_runs     = [r for r in valid_runs if r["ok"]]
    lats        = [r["latency_ms"]    for r in ok_runs]
    req_bytes   = [r["request_bytes"] for r in ok_runs]
    resp_bytes  = [r["response_bytes"] for r in ok_runs]

    stats = {
        "activity":           "1 — Con JSON Schema",
        "service":            "POST /gestures (API Gateway → Gesture Detector)",
        "schema_id":          "urn:distributed3d:gesture-request:v1",
        "iterations":         iterations,
        "successful_runs":    len(ok_runs),
        "invalid_rejected":   sum(1 for r in invalid_runs if r["status"] == 422),
        "avg_request_bytes":  round(sum(req_bytes)  / len(req_bytes),  1) if req_bytes  else 0,
        "avg_response_bytes": round(sum(resp_bytes) / len(resp_bytes), 1) if resp_bytes else 0,
        "avg_latency_ms":     round(sum(lats) / len(lats), 3)              if lats      else 0,
        "min_latency_ms":     round(min(lats), 3)                          if lats      else 0,
        "max_latency_ms":     round(max(lats), 3)                          if lats      else 0,
        "total_bytes_in":     sum(req_bytes),
        "total_bytes_out":    sum(resp_bytes),
        "valid_runs":         valid_runs,
        "invalid_runs":       invalid_runs,
    }

    print(f"\n   Resumen Activity 1:")
    print(f"     Runs exitosos    : {stats['successful_runs']}/{iterations}")
    print(f"     Inválidos rechaz.: {stats['invalid_rejected']}/3  ✅")
    print(f"     Bytes req (prom) : {stats['avg_request_bytes']} B")
    print(f"     Bytes resp (prom): {stats['avg_response_bytes']} B")
    print(f"     Latencia prom    : {stats['avg_latency_ms']} ms")
    print(f"     Latencia min/max : {stats['min_latency_ms']}ms / {stats['max_latency_ms']}ms")
    print(f"     Total transferido: req={stats['total_bytes_in']}B, resp={stats['total_bytes_out']}B")

    return stats

# Actividad 2 - Sin JSON Schema predefinido
# Endpoint: GET /particles
# Componentes: API Gateway → Physics Engine (→ PostgreSQL Replica)
def run_activity2(base_url: str, iterations: int) -> Dict[str, Any]:
    print("\n" + "═" * 70)
    print("  ACTIVITY 2 — GET /particles  (API Gateway → Physics Engine)")
    print("  Sin validación de schema — JSON libre")
    print("═" * 70)

    url  = f"{base_url}/particles"
    runs = []

    print(f"\n  ► {iterations} iteraciones")
    for i in range(iterations):
        r = http_get(url)
        runs.append(r)
        particle_count = r["data"].get("particles", []) if r["ok"] else []
        n_parts = len(particle_count) if isinstance(particle_count, list) else "?"
        print(
            f"    [{i+1:02d}] Status={r['status']} | "
            f"resp={r['response_bytes']}B | "
            f"latency={r['latency_ms']}ms | "
            f"partículas={n_parts}"
        )
        time.sleep(0.1)

    ok_runs    = [r for r in runs if r["ok"]]
    lats       = [r["latency_ms"]     for r in ok_runs]
    resp_bytes = [r["response_bytes"] for r in ok_runs]

    stats = {
        "activity":           "2 — Sin JSON Schema",
        "service":            "GET /particles (API Gateway → Physics Engine → PostgreSQL Replica)",
        "schema_id":          None,
        "iterations":         iterations,
        "successful_runs":    len(ok_runs),
        "avg_request_bytes":  0,   # GET no lleva body
        "avg_response_bytes": round(sum(resp_bytes) / len(resp_bytes), 1) if resp_bytes else 0,
        "avg_latency_ms":     round(sum(lats) / len(lats), 3)              if lats      else 0,
        "min_latency_ms":     round(min(lats), 3)                          if lats      else 0,
        "max_latency_ms":     round(max(lats), 3)                          if lats      else 0,
        "total_bytes_in":     0,
        "total_bytes_out":    sum(resp_bytes),
        "runs":               runs,
    }

    print(f"\n   Resumen Activity 2:")
    print(f"     Runs exitosos    : {stats['successful_runs']}/{iterations}")
    print(f"     Bytes req (prom) : {stats['avg_request_bytes']} B  (GET, sin body)")
    print(f"     Bytes resp (prom): {stats['avg_response_bytes']} B")
    print(f"     Latencia prom    : {stats['avg_latency_ms']} ms")
    print(f"     Latencia min/max : {stats['min_latency_ms']}ms / {stats['max_latency_ms']}ms")
    print(f"     Total transferido: resp={stats['total_bytes_out']}B")

    return stats

# Verifica que el API Gatewar esté disponible antes de lanzar las pruebas
def check_gateway(base_url: str) -> bool:
    print(f"\n  Verificando conectividad con {base_url}/health ...")
    r = http_get(f"{base_url}/health")
    if r["ok"]:
        print(f"  ✅ API Gateway disponible — status={r['data'].get('status')}")
        return True
    print(f"  ❌ API Gateway NO disponible (status={r['status']})")
    return False

# Obtiene las métricas del servidor (capturadas por el middleware)
def fetch_server_metrics(base_url: str) -> Optional[Dict]:
    r = http_get(f"{base_url}/metrics")
    return r["data"] if r["ok"] else None

# Guarda los resultados completos en un archivo JSON
def save_results(results: Dict, output_dir: Path) -> Path:
    output_dir.mkdir(exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = output_dir / f"results_{ts}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return out_file

# Imprime una tabla comparativa entre Activity 1 y Activity 2
def print_comparison(act1: Dict, act2: Dict) -> None:
    print("\n" + "═" * 70)
    print("  TABLA COMPARATIVA — Activity 1 vs Activity 2")
    print("═" * 70)
    print(f"\n  {'Métrica':<30} {'Activity 1 (schema)':<25} {'Activity 2 (libre)'}")
    print("  " + "─" * 66)
    rows = [
        ("Servicio",             "POST /gestures",                  "GET /particles"),
        ("Validación schema",    "✅ SÍ (Draft-7)",                 "❌ NO"),
        ("Iteraciones",          str(act1["iterations"]),           str(act2["iterations"])),
        ("Bytes req (prom)",     f"{act1['avg_request_bytes']} B",  f"{act2['avg_request_bytes']} B"),
        ("Bytes resp (prom)",    f"{act1['avg_response_bytes']} B", f"{act2['avg_response_bytes']} B"),
        ("Latencia prom",        f"{act1['avg_latency_ms']} ms",    f"{act2['avg_latency_ms']} ms"),
        ("Latencia mín",         f"{act1['min_latency_ms']} ms",    f"{act2['min_latency_ms']} ms"),
        ("Latencia máx",         f"{act1['max_latency_ms']} ms",    f"{act2['max_latency_ms']} ms"),
        ("Total bytes IN",       f"{act1['total_bytes_in']} B",     f"{act2['total_bytes_in']} B"),
        ("Total bytes OUT",      f"{act1['total_bytes_out']} B",    f"{act2['total_bytes_out']} B"),
        ("Inválidos rechazados", f"{act1.get('invalid_rejected',0)}/3", "N/A"),
    ]
    for label, v1, v2 in rows:
        print(f"  {label:<30} {v1:<25} {v2}")
    print()



# Main
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Laboratorio JSON Transfer — Sistema Distribuido 3D",
    )
    parser.add_argument("--host",       default=DEFAULT_HOST,       help="IP o hostname del API Gateway")
    parser.add_argument("--port",       default=DEFAULT_PORT,  type=int, help="Puerto del API Gateway")
    parser.add_argument("--iterations", default=DEFAULT_ITERATIONS, type=int,
                        help="Número de iteraciones por actividad")
    parser.add_argument("--output",     default="lab",              help="Directorio de salida para resultados")
    args = parser.parse_args()

    base_url   = f"http://{args.host}:{args.port}"
    output_dir = Path(args.output)

    print("\n" + "═" * 70)
    print("  LABORATORIO — JSON Transfer in Distributed Systems")
    print("  Sistema Distribuido de Simulación 3D + Visión Computacional")
    print(f"  Objetivo    : {base_url}")
    print(f"  Iteraciones : {args.iterations} por actividad")
    print(f"  Timestamp   : {datetime.now().isoformat()}")
    print("═" * 70)

    # Verificar conectividad
    if not check_gateway(base_url):
        print("\n Asegúrate de que Docker Compose esté corriendo:")
        print("      docker-compose up --build")
        sys.exit(1)

    # Limpiar métricas previas del servidor
    print("\n Limpiando métricas del servidor...")
    try:
        req = urllib.request.Request(f"{base_url}/metrics", method="DELETE")
        urllib.request.urlopen(req, timeout=5)
        print(" Métricas reiniciadas")
    except Exception as e:
        print(f" No se pudieron limpiar métricas: {e}")

    # Ejecutar actividades
    act1 = run_activity1(base_url, args.iterations)
    time.sleep(0.5)
    act2 = run_activity2(base_url, args.iterations)

    # Tabla comparativa
    print_comparison(act1, act2)

    # Métricas del servidor (middleware)
    print(" Métricas del servidor (middleware API Gateway):")
    server_metrics = fetch_server_metrics(base_url)
    if server_metrics and "summary" in server_metrics:
        s = server_metrics["summary"]
        print(f"     Total requests procesados : {s.get('total_requests', '?')}")
        print(f"     Latencia promedio (servidor): {s.get('avg_latency_ms', '?')} ms")
        print(f"     Procesamiento promedio      : {s.get('avg_processing_ms', '?')} ms")
        print(f"     Bytes totales IN            : {s.get('total_bytes_in', '?')} B")
        print(f"     Bytes totales OUT           : {s.get('total_bytes_out', '?')} B")
        print(f"     Con schema (%)              : {s.get('schema_validated_pct', '?')}%")
    else:
        print("     (No disponible)")

    # Guardar resultados
    results = {
        "meta": {
            "timestamp":    datetime.now().isoformat(),
            "gateway_url":  base_url,
            "iterations":   args.iterations,
        },
        "activity1": act1,
        "activity2": act2,
        "server_metrics": server_metrics,
    }
    # Limpiar objetos no-serializables antes de guardar
    for act in [results["activity1"], results["activity2"]]:
        act.pop("valid_runs",   None)
        act.pop("invalid_runs", None)
        act.pop("runs",         None)

    out_file = save_results(results, output_dir)
    print(f"\n Resultados guardados en: {out_file}")
    print("\n Laboratorio completado.\n")


if __name__ == "__main__":
    main()
