from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from app.db_internal import get_internal_db
from app.models_internal import CrdCredito, CrdAmortizacion, CrdCalificacion

router = APIRouter(prefix="/interno/credito", tags=["Interno - Cartera de Crédito"])


@router.get("/portafolio", summary="Resumen de la cartera total de crédito")
def resumen_portafolio(db: Session = Depends(get_internal_db)):
    creditos = db.query(CrdCredito).all()
    total_original = sum(c.monto_original for c in creditos)
    total_insoluto = sum(c.saldo_insoluto for c in creditos)
    por_tipo = {}
    por_status = {}
    for c in creditos:
        por_tipo[c.tipo] = por_tipo.get(c.tipo, 0) + c.saldo_insoluto
        por_status[c.status] = por_status.get(c.status, 0) + 1
    return {
        "total_creditos": len(creditos),
        "monto_original_total": round(total_original, 2),
        "saldo_insoluto_total": round(total_insoluto, 2),
        "por_tipo": {k: round(v, 2) for k, v in por_tipo.items()},
        "por_status": por_status,
        "morosidad_pct": round(
            sum(c.saldo_insoluto for c in creditos if c.status in ("VENCIDO","CASTIGADO"))
            / total_insoluto * 100, 2
        ) if total_insoluto else 0,
    }


@router.get("/calificacion", summary="Cartera por bucket IFRS 9")
def cartera_por_bucket(
    bucket: Optional[str] = Query(None, description="A|B1|B2|C1|C2|D|E"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(CrdCalificacion)
    if bucket:
        q = q.filter(CrdCalificacion.bucket_ifrs9 == bucket.upper())
    cals = q.all()
    return {
        "total": len(cals),
        "provision_total": round(sum(c.provision_requerida for c in cals), 2),
        "detalle": cals,
    }


@router.get("/cliente/{cliente_id}", summary="Créditos de un cliente (por ID interno)")
def creditos_cliente(cliente_id: str, db: Session = Depends(get_internal_db)):
    creditos = db.query(CrdCredito).filter(CrdCredito.cliente_id == cliente_id).all()
    if not creditos:
        raise HTTPException(status_code=404, detail=f"Sin créditos para {cliente_id}")
    return creditos


@router.get("/{credito_id}", summary="Detalle de crédito + tabla de amortización")
def detalle_credito(credito_id: str, db: Session = Depends(get_internal_db)):
    credito = db.query(CrdCredito).filter(CrdCredito.id == credito_id).first()
    if not credito:
        raise HTTPException(status_code=404, detail=f"Crédito {credito_id} no encontrado")
    amortizaciones = (
        db.query(CrdAmortizacion)
        .filter(CrdAmortizacion.credito_id == credito_id)
        .order_by(CrdAmortizacion.numero_pago)
        .all()
    )
    calificacion = db.query(CrdCalificacion).filter(CrdCalificacion.credito_id == credito_id).first()
    return {"credito": credito, "amortizaciones": amortizaciones, "calificacion": calificacion}
