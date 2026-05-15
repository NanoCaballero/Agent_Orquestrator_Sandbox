from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db_internal import get_internal_db
from app.models_internal import AfxInventario, AfxDepreciacion, AfxMantenimiento

router = APIRouter(prefix="/interno/activos", tags=["Interno - Activos Fijos"])

TODAY_STR = date.today().isoformat()


@router.get("", summary="Inventario de activos fijos")
def listar_activos(
    tipo: Optional[str] = Query(None, description="SUCURSAL|ATM|SERVIDOR|BLINDADO|MOBILIARIO"),
    status: Optional[str] = Query(None, description="OPERATIVO|MANTENIMIENTO|BAJA"),
    ciudad: Optional[str] = Query(None),
    db: Session = Depends(get_internal_db),
):
    q = db.query(AfxInventario)
    if tipo:
        q = q.filter(AfxInventario.tipo == tipo.upper())
    if status:
        q = q.filter(AfxInventario.status == status.upper())
    if ciudad:
        q = q.filter(AfxInventario.ciudad.ilike(f"%{ciudad}%"))
    activos = q.order_by(AfxInventario.tipo, AfxInventario.id).all()
    total_valor_libro = round(sum(a.valor_libro for a in activos), 2)
    return {"total": len(activos), "valor_libro_total": total_valor_libro, "activos": activos}


@router.get("/mantenimientos-pendientes", summary="Activos con mantenimiento próximo o pendiente")
def mantenimientos_pendientes(db: Session = Depends(get_internal_db)):
    pendientes = (
        db.query(AfxMantenimiento)
        .filter(AfxMantenimiento.status.in_(["PENDIENTE", "EN_PROCESO"]))
        .order_by(AfxMantenimiento.proxima_revision)
        .all()
    )
    return pendientes


@router.get("/{activo_id}", summary="Detalle de un activo fijo")
def detalle_activo(activo_id: str, db: Session = Depends(get_internal_db)):
    activo = db.query(AfxInventario).filter(AfxInventario.id == activo_id).first()
    if not activo:
        raise HTTPException(status_code=404, detail=f"Activo {activo_id} no encontrado")
    return activo


@router.get("/{activo_id}/depreciacion", summary="Historial de depreciación de un activo")
def depreciacion_activo(
    activo_id: str,
    anio: Optional[int] = Query(None),
    db: Session = Depends(get_internal_db),
):
    activo = db.query(AfxInventario).filter(AfxInventario.id == activo_id).first()
    if not activo:
        raise HTTPException(status_code=404, detail=f"Activo {activo_id} no encontrado")
    q = db.query(AfxDepreciacion).filter(AfxDepreciacion.activo_id == activo_id)
    if anio:
        q = q.filter(AfxDepreciacion.anio == anio)
    deps = q.order_by(AfxDepreciacion.anio, AfxDepreciacion.mes).all()
    return {"activo": activo, "depreciacion": deps}
