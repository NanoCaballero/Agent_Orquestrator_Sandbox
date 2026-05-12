import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Cuenta, Pago
from app.schemas import PagoServicioRequest, PagoServicioResponse
from app.services.auditoria import log_operacion

router = APIRouter(prefix="/pagos", tags=["Pagos de Servicios"])

SERVICIOS_VALIDOS = {"CFE", "AGUA", "TELMEX", "PREDIAL", "IZZI", "SKY", "TOTALPLAY"}


@router.post(
    "/servicios",
    response_model=PagoServicioResponse,
    status_code=201,
    summary="Pagar un servicio (CFE, AGUA, TELMEX, PREDIAL, etc.)",
)
def pagar_servicio(req: PagoServicioRequest, db: Session = Depends(get_db)):
    servicio = req.servicio.upper()
    if servicio not in SERVICIOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Servicio '{req.servicio}' no válido. Opciones: {sorted(SERVICIOS_VALIDOS)}",
        )

    cuenta = db.query(Cuenta).filter(Cuenta.numero == req.cuenta).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail=f"Cuenta {req.cuenta} no encontrada")

    if cuenta.saldo < req.monto:
        raise HTTPException(
            status_code=422,
            detail=f"Saldo insuficiente. Disponible: {cuenta.saldo:.2f} MXN",
        )

    now = datetime.now(tz=timezone.utc)
    pago_id = str(uuid.uuid4())
    folio = f"BNR-{servicio[:3]}-{now.strftime('%Y%m%d')}-{pago_id[:8].upper()}"

    cuenta.saldo = round(cuenta.saldo - req.monto, 2)
    pago = Pago(
        id=pago_id,
        cuenta_id=cuenta.id,
        servicio=servicio,
        referencia=req.referencia,
        monto=req.monto,
        fecha=now,
    )
    db.add(pago)
    db.commit()

    log_operacion("PAGO_SERVICIO", req.cuenta, req.monto, f"servicio={servicio} ref={req.referencia}")

    return PagoServicioResponse(
        id=pago_id,
        cuenta=req.cuenta,
        servicio=servicio,
        referencia=req.referencia,
        monto=req.monto,
        fecha=now,
        folio_confirmacion=folio,
    )


@router.get(
    "/servicios/{cuenta}",
    summary="Historial de pagos de servicios de una cuenta",
)
def historial_pagos(cuenta: str, db: Session = Depends(get_db)):
    cta = db.query(Cuenta).filter(Cuenta.numero == cuenta).first()
    if not cta:
        raise HTTPException(status_code=404, detail=f"Cuenta {cuenta} no encontrada")

    pagos = db.query(Pago).filter(Pago.cuenta_id == cta.id).order_by(Pago.fecha.desc()).all()
    return [
        {
            "id": p.id,
            "servicio": p.servicio,
            "referencia": p.referencia,
            "monto": p.monto,
            "fecha": p.fecha.isoformat(),
        }
        for p in pagos
    ]
