"""
Paso 5 - RECEPTOR: Recibe el mensaje XML, lo valida contra el XSD y responde
Sistemas Distribuidos - Laboratorio XML

Uso:
    python receptor.py
    (Escucha en http://localhost:8080/registro)
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from lxml import etree

PUERTO   = 8080
XSD_PATH = "esquema.xsd"

# Cargar el esquema una sola vez al iniciar el servidor
with open(XSD_PATH, "rb") as f:
    _xsd_doc = etree.parse(f)
ESQUEMA = etree.XMLSchema(_xsd_doc)


def extraer_resumen(xml_doc) -> dict:
    """Extrae los campos principales del XML para la respuesta."""
    ns   = {"tns": "http://lab.distribuidos/productos/v1"}
    root = xml_doc.getroot()

    def get(xpath):
        el = root.find(xpath, ns)
        return el.text if el is not None else "N/A"

    return {
        "id_mensaje": get("tns:Metadatos/tns:IDMensaje"),
        "proveedor":  get("tns:Proveedor/tns:Nombre"),
        "producto":   get("tns:Producto/tns:Nombre"),
        "codigo":     get("tns:Producto/tns:Codigo"),
        "precio":     get("tns:Producto/tns:Precio/tns:Valor"),
        "moneda":     get("tns:Producto/tns:Precio/tns:Moneda"),
        "stock":      get("tns:Producto/tns:Stock"),
    }


class ReceptorHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """Sobreescribir para tener logs más limpios."""
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    def do_POST(self):
        if self.path != "/registro":
            self._responder(404, {"valido": False, "mensaje": "Ruta no encontrada"})
            return

        print("\n" + "-" * 45)
        print(f"  Mensaje recibido desde {self.client_address[0]}")

        # --- 1. Leer el cuerpo de la petición ---
        length   = int(self.headers.get("Content-Length", 0))
        xml_data = self.rfile.read(length)
        print(f"  Bytes recibidos: {len(xml_data)}")

        # --- 2. Verificar que está bien formado ---
        try:
            xml_doc = etree.fromstring(xml_data)
            xml_doc = etree.ElementTree(xml_doc)
            print("  ✔ XML bien formado")
        except etree.XMLSyntaxError as e:
            print(f"  ✘ XML mal formado: {e}")
            self._responder(400, {
                "valido":  False,
                "mensaje": "XML mal formado",
                "errores": [str(e)]
            })
            return

        # --- 3. Validar contra el esquema XSD ---
        es_valido = ESQUEMA.validate(xml_doc)
        errores   = [f"Línea {e.line}: {e.message}" for e in ESQUEMA.error_log]

        if es_valido:
            print("  ✔ XML válido según el esquema XSD")
            resumen = extraer_resumen(xml_doc)
            print(f"  Producto registrado: {resumen['codigo']} - {resumen['producto']}")
            self._responder(200, {
                "valido":  True,
                "mensaje": "Producto registrado exitosamente",
                "resumen": resumen
            })
        else:
            print("  ✘ XML inválido según el esquema XSD")
            for err in errores:
                print(f"    → {err}")
            self._responder(422, {
                "valido":  False,
                "mensaje": "El XML no cumple el esquema XSD",
                "errores": errores
            })

    def _responder(self, status: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    servidor = HTTPServer(("localhost", PUERTO), ReceptorHandler)
    print("=" * 55)
    print("   RECEPTOR - Registro de Productos")
    print("=" * 55)
    print(f"\n  Escuchando en http://localhost:{PUERTO}/registro")
    print(f"  Esquema cargado: {XSD_PATH}")
    print(f"  Presiona Ctrl+C para detener\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")