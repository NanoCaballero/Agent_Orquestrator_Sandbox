import os
import xml.etree.ElementTree as ET
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

router = APIRouter(prefix="/kyc", tags=["KYC / Identidad (XML)"])

_XML_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed", "kyc.xml")


def _parse_cliente_xml(element: ET.Element) -> dict:
    def text(tag: str):
        el = element.find(tag)
        return el.text if el is not None else None

    lugar = element.find("lugar_nacimiento")
    documentos = []
    for doc in element.findall("documentos/documento"):
        documentos.append({
            "tipo": doc.get("tipo"),
            "numero": doc.get("numero"),
            "vigencia": doc.get("vigencia"),
            "status": doc.get("status"),
        })

    return {
        "curp": text("curp"),
        "rfc": text("rfc"),
        "nombre_completo": text("nombre_completo"),
        "fecha_nacimiento": text("fecha_nacimiento"),
        "lugar_nacimiento": {
            "municipio": lugar.findtext("municipio") if lugar is not None else None,
            "estado": lugar.findtext("estado") if lugar is not None else None,
            "pais": lugar.findtext("pais") if lugar is not None else None,
        },
        "estado_civil": text("estado_civil"),
        "ocupacion": text("ocupacion"),
        "nivel_riesgo": text("nivel_riesgo"),
        "pep": text("pep") == "true",
        "documentos": documentos,
        "ultima_verificacion": text("ultima_verificacion"),
        "proxima_revision": text("proxima_revision"),
    }


@router.get(
    "/{curp}",
    summary="Consultar identidad KYC por CURP",
    description=(
        "Consulta el registro de identidad de un cliente desde el sistema KYC. "
        "Fuente: archivo XML (simula sistema de identidad externo). "
        "Por defecto responde en `application/xml`; usa `?format=json` para JSON."
    ),
)
def consultar_kyc(curp: str, format: str = Query("xml", description="xml | json")):
    tree = ET.parse(_XML_PATH)
    root = tree.getroot()

    for cliente_el in root.findall("cliente"):
        curp_el = cliente_el.find("curp")
        if curp_el is not None and curp_el.text == curp:
            if format == "json":
                return _parse_cliente_xml(cliente_el)
            # Return the raw XML fragment
            xml_bytes = ET.tostring(cliente_el, encoding="unicode")
            return Response(
                content=f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_bytes}',
                media_type="application/xml",
            )

    raise HTTPException(status_code=404, detail=f"CURP {curp} no encontrado en sistema KYC")
