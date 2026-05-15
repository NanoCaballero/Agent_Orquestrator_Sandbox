from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db_internal import get_internal_db
from app.models_internal import RegIcapHistorico, RegLcrHistorico, RegReporteEnviado

router = APIRouter(prefix="/interno/regulatorio", tags=["Interno - Regulatorio CNBV"])


@router.get("/icap", summary="Histórico del Índice de Capitalización (ICAP)")
def icap_historico(
    desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RegIcapHistorico)
    if desde:
        q = q.filter(RegIcapHistorico.fecha >= desde)
    if hasta:
        q = q.filter(RegIcapHistorico.fecha <= hasta)
    registros = q.order_by(RegIcapHistorico.fecha).all()
    ultimo = registros[-1] if registros else None
    return {
        "ultimo_icap_pct": ultimo.icap_pct if ultimo else None,
        "limite_minimo_pct": 10.5,
        "cumple_actualmente": ultimo.cumple if ultimo else None,
        "serie_historica": registros,
    }


@router.get("/lcr", summary="Histórico del Coeficiente de Cobertura de Liquidez (LCR)")
def lcr_historico(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RegLcrHistorico)
    if desde:
        q = q.filter(RegLcrHistorico.fecha >= desde)
    if hasta:
        q = q.filter(RegLcrHistorico.fecha <= hasta)
    registros = q.order_by(RegLcrHistorico.fecha).all()
    ultimo = registros[-1] if registros else None
    return {
        "ultimo_lcr_pct": ultimo.lcr_pct if ultimo else None,
        "limite_minimo_pct": 100.0,
        "cumple_actualmente": ultimo.cumple if ultimo else None,
        "serie_historica": registros,
    }


@router.get("/reportes", summary="Reportes enviados a la CNBV")
def reportes_cnbv(
    tipo: Optional[str] = Query(None, description="R01A|R04B|R10|R21A|R22|A-01"),
    status: Optional[str] = Query(None, description="ENVIADO|ACEPTADO|OBSERVACIONES|RECHAZADO"),
    periodo: Optional[str] = Query(None, description="YYYY-MM"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RegReporteEnviado)
    if tipo:
        q = q.filter(RegReporteEnviado.tipo_reporte == tipo)
    if status:
        q = q.filter(RegReporteEnviado.status == status.upper())
    if periodo:
        q = q.filter(RegReporteEnviado.periodo == periodo)
    reportes = q.order_by(RegReporteEnviado.fecha_envio.desc()).all()
    return {
        "total": len(reportes),
        "con_observaciones": sum(1 for r in reportes if r.status == "OBSERVACIONES"),
        "aceptados": sum(1 for r in reportes if r.status == "ACEPTADO"),
        "reportes": reportes,
    }
