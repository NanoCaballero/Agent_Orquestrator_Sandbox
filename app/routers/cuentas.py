from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.db import get_db
from app.models import Cuenta, Transaccion
from app.schemas import SaldoResponse, MovimientoResponse, CuentaDetalleResponse
from app.services.auditoria import log_operacion

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


def _get_cuenta_or_404(numero: str, db: Session) -> Cuenta:
    c = db.query(Cuenta).filter(Cuenta.numero == numero).first()
    if not c:
        raise HTTPException(status_code=404, detail=f"Cuenta {numero} no encontrada")
    return c


@router.get(
    "/{numero}/saldo",
    response_model=SaldoResponse,
    summary="Consultar saldo de una cuenta",
    openapi_extra={
        "x-examples": {
            "cuenta-premium": {"value": {"numero": "0001000001"}},
            "cuenta-inversion": {"value": {"numero": "0001000005"}},
        }
    },
)
def consultar_saldo(numero: str, db: Session = Depends(get_db)):
    cuenta = _get_cuenta_or_404(numero, db)
    log_operacion("CONSULTA_SALDO", numero)
    return SaldoResponse(numero=cuenta.numero, tipo=cuenta.tipo, saldo=cuenta.saldo, moneda=cuenta.moneda)


@router.get(
    "/{numero}/movimientos",
    response_model=List[MovimientoResponse],
    summary="Obtener movimientos de una cuenta",
)
def consultar_movimientos(
    numero: str,
    desde: Optional[datetime] = Query(None, description="Fecha inicio ISO8601"),
    hasta: Optional[datetime] = Query(None, description="Fecha fin ISO8601"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    cuenta = _get_cuenta_or_404(numero, db)

    query = db.query(Transaccion).filter(
        (Transaccion.cuenta_origen_id == cuenta.id) | (Transaccion.cuenta_destino_id == cuenta.id)
    )
    if desde:
        query = query.filter(Transaccion.fecha >= desde)
    if hasta:
        query = query.filter(Transaccion.fecha <= hasta)

    txs = query.order_by(Transaccion.fecha.desc()).limit(limit).all()
    log_operacion("CONSULTA_MOVIMIENTOS", numero, detalle=f"total={len(txs)}")

    result = []
    for tx in txs:
        contraparte = None
        if tx.cuenta_origen_id == cuenta.id and tx.cuenta_destino:
            contraparte = tx.cuenta_destino.numero
        elif tx.cuenta_destino_id == cuenta.id and tx.cuenta_origen:
            contraparte = tx.cuenta_origen.numero

        result.append(MovimientoResponse(
            id=tx.id,
            tipo=tx.tipo,
            concepto=tx.concepto,
            monto=tx.monto,
            fecha=tx.fecha,
            status=tx.status,
            cuenta_contraparte=contraparte,
        ))
    return result


@router.get(
    "/{numero}",
    response_model=CuentaDetalleResponse,
    summary="Datos completos de cuenta + cliente + sucursal",
)
def detalle_cuenta(numero: str, db: Session = Depends(get_db)):
    cuenta = _get_cuenta_or_404(numero, db)
    cliente = cuenta.cliente
    sucursal = cliente.sucursal
    log_operacion("CONSULTA_DETALLE_CUENTA", numero)
    return CuentaDetalleResponse(
        numero=cuenta.numero,
        tipo=cuenta.tipo,
        saldo=cuenta.saldo,
        moneda=cuenta.moneda,
        abierta_en=cuenta.abierta_en,
        cliente_nombre=cliente.nombre,
        cliente_rfc=cliente.rfc,
        cliente_segmento=cliente.segmento,
        sucursal_nombre=sucursal.nombre,
        sucursal_ciudad=sucursal.ciudad,
    )
