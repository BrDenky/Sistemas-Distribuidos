# Validación Local
# Verificamos un mensaje XML en local antes de enviarlo por la red

from lxml import etree


def validar_xml(xml_path: str, xsd_path: str) -> bool:
    print("   VALIDADOR XML - Registro de Productos")

    # Cargamos y parseamos el XSD
    print(f"\n[1] Cargando esquema: {xsd_path}")
    try:
        with open(xsd_path, "rb") as f:
            xsd_doc = etree.parse(f)
        esquema = etree.XMLSchema(xsd_doc)
        print(" Esquema XSD cargado correctamente")
    except Exception as e:
        print(f" Error al cargar el esquema: {e}")
        return False

    # Cargamos y parseamos el XML
    print(f"\n[2] Cargando mensaje:  {xml_path}")
    try:
        with open(xml_path, "rb") as f:
            xml_doc = etree.parse(f)
        print(" XML bien formado (sintaxis correcta)")
    except etree.XMLSyntaxError as e:
        print(f" XML mal formado: {e}")
        return False

    # Validamos XML contra el XSD
    print(f"\n[3] Validando mensaje contra el esquema...")
    es_valido = esquema.validate(xml_doc)

    if es_valido:
        print(" El mensaje es VÁLIDO según el esquema XSD")
    else:
        print(" El mensaje NO es válido. Errores encontrados:")
        for error in esquema.error_log:
            print(f" Línea {error.line}: {error.message}")

    # Mostramos resumen de campos extraídos
    if es_valido:
        print("\n[4] Resumen del mensaje recibido:")
        ns = {"tns": "http://lab.distribuidos/productos/v1"}
        root = xml_doc.getroot()

        def get(xpath):
            el = root.find(xpath, ns)
            return el.text if el is not None else "N/A"

        print(f"    ID Mensaje  : {get('tns:Metadatos/tns:IDMensaje')}")
        print(f"    Fecha Envío : {get('tns:Metadatos/tns:FechaEnvio')}")
        print(f"    Proveedor   : {get('tns:Proveedor/tns:Nombre')}")
        print(f"    RUC         : {get('tns:Proveedor/tns:RUC')}")
        print(f"    Producto    : {get('tns:Producto/tns:Nombre')}")
        print(f"    Código      : {get('tns:Producto/tns:Codigo')}")
        print(f"    Categoría   : {get('tns:Producto/tns:Categoria')}")
        precio  = get('tns:Producto/tns:Precio/tns:Valor')
        moneda  = get('tns:Producto/tns:Precio/tns:Moneda')
        print(f"    Precio      : {precio} {moneda}")
        print(f"    Stock       : {get('tns:Producto/tns:Stock')} unidades")

    print("\n" + "=" * 55)
    return es_valido


if __name__ == "__main__":
    resultado = validar_xml("mensaje.xml", "esquema.xsd")
    exit(0 if resultado else 1)