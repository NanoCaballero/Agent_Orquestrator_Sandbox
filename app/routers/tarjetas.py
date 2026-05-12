import json
import os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/tarjetas", tags=["Tarjetas (JSON)"])

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed", "tarjetas.json")


def _load_tarjetas() -> list:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["tarjetas"]


@router.get(
    "/{numero}",
    summary="Consultar tarjeta de crédito por número (fuente: JSON)",
    description="Devuelve datos completos de la tarjeta incluyendo límites, puntos, historial de pagos y últimos consumos. Fuente: archivo tarjetas.json (simula sistema de tarjetas separado).",
)
def consultar_tarjeta(numero: str):
    numero_limpio = numero.replace(" ", "").replace("-", "")
    tarjetas = _load_tarjetas()
    for t in tarjetas:
        t_num = t["numero"].replace(" ", "").replace("-", "")
        if t_num == numero_limpio:
            return t
    raise HTTPException(status_code=404, detail=f"Tarjeta {numero} no encontrada")


@router.get(
    "/cliente/{rfc}",
    summary="Listar tarjetas de un cliente por RFC",
)
def tarjetas_por_cliente(rfc: str):
    tarjetas = _load_tarjetas()
    resultado = [t for t in tarjetas if t.get("cliente_rfc") == rfc]
    if not resultado:
        raise HTTPException(status_code=404, detail=f"No hay tarjetas para RFC {rfc}")
    return {"rfc": rfc, "tarjetas": resultado}
