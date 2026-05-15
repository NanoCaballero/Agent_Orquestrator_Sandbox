from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db_internal import get_internal_db
from app.models_internal import RsgAlertaFraude, RsgVarDiario, RsgLimiteContraparte

router = APIRouter(prefix="/interno/riesgos", tags=["Interno - Riesgos y Fraude"])


@router.get("/alertas", summary="Alertas de fraude y riesgo operacional")
def listar_alertas(
    status: Optional[str] = Query(None, description="ABIERTA|INVESTIGANDO|CERRADA|FALSO_POSITIVO"),
    tipo: Optional[str] = Query(None, description="MONTO_INUSUAL|PATRON_GEOGRAFICO|VELOCIDAD|LISTA_NEGRA"),
    cuenta: Optional[str] = Query(None, description="Número de cuenta"),
    min_score: Optional[float] = Query(None, description="Score mínimo de riesgo (0-100)"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RsgAlertaFraude)
    if status:
        q = q.filter(RsgAlertaFraude.status == status.upper())
    if tipo:
        q = q.filter(RsgAlertaFraude.tipo_alerta == tipo.upper())
    if cuenta:
        q = q.filter(RsgAlertaFraude.cuenta_numero == cuenta)
    if min_score is not None:
        q = q.filter(RsgAlertaFraude.score_riesgo >= min_score)
    alertas = q.order_by(RsgAlertaFraude.fecha.desc()).all()
    return {
        "total": len(alertas),
        "abiertas": sum(1 for a in alertas if a.status == "ABIERTA"),
        "en_investigacion": sum(1 for a in alertas if a.status == "INVESTIGANDO"),
        "alertas": alertas,
    }


@router.get("/var", summary="VaR diario del portafolio de mercado")
def var_historico(
    desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    solo_breach: bool = Query(False, description="Solo días con breach del límite"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RsgVarDiario)
    if desde:
        q = q.filter(RsgVarDiario.fecha >= desde)
    if hasta:
        q = q.filter(RsgVarDiario.fecha <= hasta)
    if solo_breach:
        q = q.filter(RsgVarDiario.breach == True)
    registros = q.order_by(RsgVarDiario.fecha).all()
    breaches = sum(1 for r in registros if r.breach)
    return {
        "total_dias": len(registros),
        "dias_con_breach": breaches,
        "tasa_breach_pct": round(breaches / len(registros) * 100, 1) if registros else 0,
        "registros": registros,
    }


@router.get("/contrapartes", summary="Límites de exposición por contraparte")
def limites_contrapartes(
    tipo: Optional[str] = Query(None, description="BANCO|GOBIERNO|EMPRESA"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(RsgLimiteContraparte)
    if tipo:
        q = q.filter(RsgLimiteContraparte.tipo == tipo.upper())
    contrapartes = q.order_by(RsgLimiteContraparte.tipo, RsgLimiteContraparte.contraparte).all()
    return [
        {
            "contraparte": c.contraparte,
            "tipo": c.tipo,
            "calificacion": c.calificacion_externa,
            "limite_aprobado": c.limite_aprobado,
            "exposicion_actual": c.exposicion_actual,
            "headroom": c.headroom,
            "utilizacion_pct": round(c.exposicion_actual / c.limite_aprobado * 100, 1),
            "ultima_revision": c.ultima_revision,
            "vencimiento_linea": c.vencimiento_linea,
        }
        for c in contrapartes
    ]
