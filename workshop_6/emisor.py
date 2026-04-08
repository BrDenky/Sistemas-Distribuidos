"""
Paso 5 - EMISOR: Envía mensaje.xml al receptor por HTTP
Sistemas Distribuidos - Laboratorio XML

Uso:
    python emisor.py
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

RECEPTOR_URL = "http://localhost:8080/registro"
XML_PATH     = "mensaje.xml"


def enviar_mensaje(xml_path: str, url: str) -> None:
    print("=" * 55)
    print("   EMISOR - Registro de Productos")
    print("=" * 55)

    # --- 1. Leer el archivo XML ---
    print(f"\n[1] Leyendo mensaje: {xml_path}")
    try:
        with open(xml_path, "rb") as f:
            xml_data = f.read()
        print(f"    ✔ Mensaje leído ({len(xml_data)} bytes)")
    except FileNotFoundError:
        print(f"    ✘ Archivo no encontrado: {xml_path}")
        return

    # --- 2. Construir y enviar la petición HTTP POST ---
    print(f"\n[2] Enviando mensaje a: {url}")
    print(f"    Timestamp: {datetime.now().isoformat()}")

    req = urllib.request.Request(
        url,
        data=xml_data,
        headers={"Content-Type": "application/xml; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status   = response.status
            respuesta = json.loads(response.read().decode("utf-8"))

        print(f"\n[3] Respuesta del receptor:")
        print(f"    HTTP Status : {status}")
        print(f"    Válido      : {'✔ SÍ' if respuesta.get('valido') else '✘ NO'}")
        print(f"    Mensaje     : {respuesta.get('mensaje')}")

        if respuesta.get("resumen"):
            r = respuesta["resumen"]
            print(f"\n[4] Confirmación de datos recibidos:")
            print(f"    ID Mensaje  : {r.get('id_mensaje')}")
            print(f"    Proveedor   : {r.get('proveedor')}")
            print(f"    Producto    : {r.get('producto')}")
            print(f"    Código      : {r.get('codigo')}")
            print(f"    Precio      : {r.get('precio')} {r.get('moneda')}")
            print(f"    Stock       : {r.get('stock')} unidades")

        if respuesta.get("errores"):
            print(f"\n    Errores de validación:")
            for err in respuesta["errores"]:
                print(f"      → {err}")

    except urllib.error.HTTPError as e:
        print(f"    ✘ Error HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"    ✘ No se pudo conectar al receptor: {e.reason}")
        print(f"      ¿Está corriendo receptor.py en el puerto 8080?")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    enviar_mensaje(XML_PATH, RECEPTOR_URL)