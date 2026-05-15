from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from app.db_internal import get_internal_db
from app.models_internal import GlCatalogoCuentas, GlAsiento, GlPartida

router = APIRouter(prefix="/interno/gl", tags=["Interno - Contabilidad GL"])


@router.get("/cuentas", summary="Catálogo de cuentas CNBV")
def catalogo_cuentas(
    tipo: Optional[str] = Query(None, description="ACTIVO|PASIVO|CAPITAL|INGRESO|EGRESO"),
    nivel: Optional[int] = Query(None, description="1=grupo, 2=subgrupo, 3=cuenta, 4=subcuenta"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(GlCatalogoCuentas).filter(GlCatalogoCuentas.activa == True)
    if tipo:
        q = q.filter(GlCatalogoCuentas.tipo == tipo.upper())
    if nivel:
        q = q.filter(GlCatalogoCuentas.nivel == nivel)
    return q.order_by(GlCatalogoCuentas.codigo).all()


@router.get("/cuentas/{codigo}", summary="Cuenta contable + subcuentas hijas")
def detalle_cuenta(codigo: str, db: Session = Depends(get_internal_db)):
    cuenta = db.query(GlCatalogoCuentas).filter(GlCatalogoCuentas.codigo == codigo).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail=f"Cuenta {codigo} no encontrada")
    hijas = db.query(GlCatalogoCuentas).filter(GlCatalogoCuentas.codigo_padre == codigo).all()
    return {"cuenta": cuenta, "subcuentas": hijas}


@router.get("/asientos", summary="Asientos contables del período")
def listar_asientos(
    desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    status: Optional[str] = Query(None, description="APLICADO|PENDIENTE|RECHAZADO"),
    centro_costo: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_internal_db),
):
    q = db.query(GlAsiento)
    if desde:
        q = q.filter(GlAsiento.fecha >= desde)
    if hasta:
        q = q.filter(GlAsiento.fecha <= hasta)
    if status:
        q = q.filter(GlAsiento.status == status.upper())
    if centro_costo:
        q = q.filter(GlAsiento.centro_costo == centro_costo)
    return q.order_by(GlAsiento.fecha.desc()).limit(limit).all()


@router.get("/asientos/{asiento_id}/partidas", summary="Partidas de un asiento (doble entrada)")
def partidas_asiento(asiento_id: str, db: Session = Depends(get_internal_db)):
    asiento = db.query(GlAsiento).filter(GlAsiento.id == asiento_id).first()
    if not asiento:
        raise HTTPException(status_code=404, detail=f"Asiento {asiento_id} no encontrado")
    partidas = db.query(GlPartida).filter(GlPartida.asiento_id == asiento_id).all()
    return {"asiento": asiento, "partidas": partidas}


@router.get("/balanza", summary="Balanza de comprobación por período")
def balanza_comprobacion(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2024, le=2030),
    db: Session = Depends(get_internal_db),
):
    prefix = f"{anio}-{mes:02d}"
    asientos_ids = [
        r[0] for r in db.query(GlAsiento.id)
        .filter(GlAsiento.fecha.like(f"{prefix}%"), GlAsiento.status == "APLICADO")
        .all()
    ]
    if not asientos_ids:
        return {"periodo": prefix, "lineas": [], "total_cargos": 0, "total_abonos": 0}

    rows = (
        db.query(
            GlPartida.cuenta_codigo,
            GlPartida.tipo,
            func.sum(GlPartida.monto).label("total"),
        )
        .filter(GlPartida.asiento_id.in_(asientos_ids))
        .group_by(GlPartida.cuenta_codigo, GlPartida.tipo)
        .all()
    )

    lineas: dict = {}
    for cuenta_codigo, tipo, total in rows:
        if cuenta_codigo not in lineas:
            lineas[cuenta_codigo] = {"cuenta": cuenta_codigo, "cargos": 0.0, "abonos": 0.0}
        if tipo == "CARGO":
            lineas[cuenta_codigo]["cargos"] = round(total, 2)
        else:
            lineas[cuenta_codigo]["abonos"] = round(total, 2)

    sorted_lineas = sorted(lineas.values(), key=lambda x: x["cuenta"])
    total_cargos = round(sum(l["cargos"] for l in sorted_lineas), 2)
    total_abonos = round(sum(l["abonos"] for l in sorted_lineas), 2)

    return {
        "periodo": prefix,
        "lineas": sorted_lineas,
        "total_cargos": total_cargos,
        "total_abonos": total_abonos,
        "cuadra": abs(total_cargos - total_abonos) < 0.01,
    }
