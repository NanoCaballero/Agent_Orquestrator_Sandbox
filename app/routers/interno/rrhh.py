from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db_internal import get_internal_db
from app.models_internal import RhEmpleado, RhNominaMensual, RhCentroCosto

router = APIRouter(prefix="/interno/rrhh", tags=["Interno - RRHH / Nómina"])


@router.get("/empleados", summary="Directorio de empleados internos del banco")
def listar_empleados(
    area: Optional[str] = Query(None, description="RETAIL|CORPORATIVO|TESORERIA|TI|RIESGO|RRHH|AUDITORIA|JURIDICO"),
    status: Optional[str] = Query(None, description="ACTIVO|BAJA"),
    nivel: Optional[int] = Query(None, description="1=director ... 8=operativo"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RhEmpleado)
    if area:
        q = q.filter(RhEmpleado.area == area.upper())
    if status:
        q = q.filter(RhEmpleado.status == status.upper())
    if nivel:
        q = q.filter(RhEmpleado.nivel == nivel)
    return q.order_by(RhEmpleado.nivel, RhEmpleado.nombre).all()


@router.get("/empleados/{empleado_id}", summary="Detalle de un empleado")
def detalle_empleado(empleado_id: str, db: Session = Depends(get_internal_db)):
    emp = db.query(RhEmpleado).filter(RhEmpleado.id == empleado_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Empleado {empleado_id} no encontrado")
    return emp


@router.get("/nomina/{periodo}", summary="Nómina mensual (YYYY-MM)")
def nomina_periodo(periodo: str, db: Session = Depends(get_internal_db)):
    registros = db.query(RhNominaMensual).filter(RhNominaMensual.periodo == periodo).all()
    if not registros:
        raise HTTPException(status_code=404, detail=f"Sin nómina para período {periodo}")
    total_bruto = round(sum(r.sueldo_bruto for r in registros), 2)
    total_neto = round(sum(r.neto for r in registros), 2)
    total_isr = round(sum(r.isr for r in registros), 2)
    return {
        "periodo": periodo,
        "total_empleados": len(registros),
        "total_bruto": total_bruto,
        "total_isr_retenido": total_isr,
        "total_neto_pagado": total_neto,
        "registros": registros,
    }


@router.get("/centros-costo", summary="Centros de costo — presupuesto vs gasto real")
def centros_costo(db: Session = Depends(get_internal_db)):
    centros = db.query(RhCentroCosto).all()
    return [
        {
            "id": c.id,
            "nombre": c.nombre,
            "area": c.area,
            "director": c.director,
            "presupuesto_anual": c.presupuesto_anual,
            "gasto_acumulado": c.gasto_acumulado,
            "disponible": round(c.presupuesto_anual - c.gasto_acumulado, 2),
            "ejercido_pct": round(c.gasto_acumulado / c.presupuesto_anual * 100, 1),
            "empleados_activos": c.empleados_activos,
        }
        for c in centros
    ]
