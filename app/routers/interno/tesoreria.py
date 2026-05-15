from __future__ import annotations
import csv, os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db_internal import get_internal_db
from app.models_internal import TryPosicionDiaria, TryInstrumento, TryOperacionMesa

router = APIRouter(prefix="/interno/tesoreria", tags=["Interno - Tesorería"])

_TASAS_CSV = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "seed", "internal", "tasas_referencia.csv"
)


@router.get("/posicion", summary="Posición de liquidez diaria")
def posicion_liquidez(
    fecha: Optional[str] = Query(None, description="YYYY-MM-DD; omitir para el día más reciente"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(TryPosicionDiaria)
    if fecha:
        pos = q.filter(TryPosicionDiaria.fecha == fecha).first()
        if not pos:
            raise HTTPException(status_code=404, detail=f"Sin posición para {fecha}")
        return pos
    return q.order_by(TryPosicionDiaria.fecha.desc()).first()


@router.get("/posicion/historico", summary="Historial de posición de liquidez")
def posicion_historico(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_internal_db),
):
    q = db.query(TryPosicionDiaria)
    if desde:
        q = q.filter(TryPosicionDiaria.fecha >= desde)
    if hasta:
        q = q.filter(TryPosicionDiaria.fecha <= hasta)
    return q.order_by(TryPosicionDiaria.fecha).all()


@router.get("/instrumentos", summary="Portafolio vigente de inversiones en valores")
def portafolio_instrumentos(
    emisora: Optional[str] = Query(None, description="CETES|BONM|UDIBONO|BONDESD"),
    clasificacion: Optional[str] = Query(None),
    db: Session = Depends(get_internal_db),
):
    q = db.query(TryInstrumento)
    if emisora:
        q = q.filter(TryInstrumento.emisora == emisora.upper())
    if clasificacion:
        q = q.filter(TryInstrumento.clasificacion == clasificacion.upper())
    return q.all()


@router.get("/operaciones", summary="Operaciones de mesa de dinero")
def operaciones_mesa(
    tipo: Optional[str] = Query(None, description="REPO|PRESTAMO_IB|COMPRA_CETES|VENTA_BONOS"),
    status: Optional[str] = Query(None, description="ACTIVA|VENCIDA|CANCELADA"),
    db: Session = Depends(get_internal_db),
):
    q = db.query(TryOperacionMesa)
    if tipo:
        q = q.filter(TryOperacionMesa.tipo == tipo.upper())
    if status:
        q = q.filter(TryOperacionMesa.status == status.upper())
    return q.order_by(TryOperacionMesa.fecha_inicio.desc()).all()


@router.get(
    "/tasas-referencia",
    summary="Tasas de referencia Banxico (TIIE, CETES) — fuente CSV",
    description="Lee el archivo CSV de tasas de referencia simuladas de Banxico.",
)
def tasas_referencia(
    format: str = Query("json", description="json | csv"),
):
    with open(_TASAS_CSV, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    if format == "csv":
        from fastapi.responses import PlainTextResponse
        import io
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        return PlainTextResponse(out.getvalue(), media_type="text/csv")

    for r in rows:
        for k, v in r.items():
            if k != "fecha" and k != "fuente":
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
    return rows
