from __future__ import annotations
import json, os
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/interno/org", tags=["Interno - Organigrama"])

_ORG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "seed", "internal", "org_chart.json"
)


def _load_org():
    with open(_ORG_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("/estructura", summary="Organigrama completo del banco")
def estructura_organizacional():
    return _load_org()


@router.get("/area/{nombre}", summary="Buscar área por nombre (parcial)")
def buscar_area(nombre: str):
    org = _load_org()
    nombre_lower = nombre.lower()
    resultados = []
    for subdir in org["direccion_general"]["subdirecciones"]:
        for area in subdir.get("areas", []):
            if nombre_lower in area["nombre"].lower():
                resultados.append({
                    "direccion": subdir["nombre"],
                    "director_direccion": subdir["director"],
                    **area,
                })
    if not resultados:
        raise HTTPException(status_code=404, detail=f"No se encontraron áreas con '{nombre}'")
    return resultados


@router.get("/direcciones", summary="Listar subdirecciones / direcciones del banco")
def listar_direcciones():
    org = _load_org()
    return [
        {
            "nombre": s["nombre"],
            "director": s["director"],
            "correo": s["correo"],
            "num_areas": len(s.get("areas", [])),
        }
        for s in org["direccion_general"]["subdirecciones"]
    ]
