import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Cuenta, Transaccion
from app.schemas import TransferenciaRequest, TransferenciaResponse

MX_TZ_OFFSET = -6  # UTC-6 (CST)


def ejecutar_transferencia(req: TransferenciaRequest, db: Session) -> TransferenciaResponse:
    origen = db.query(Cuenta).filter(Cuenta.numero == req.origen).first()
    if not origen:
        raise HTTPException(status_code=404, detail=f"Cuenta origen {req.origen} no encontrada")

    destino = db.query(Cuenta).filter(Cuenta.numero == req.destino).first()
    if not destino:
        raise HTTPException(status_code=404, detail=f"Cuenta destino {req.destino} no encontrada")

    if origen.saldo < req.monto:
        raise HTTPException(
            status_code=422,
            detail=f"Saldo insuficiente. Disponible: {origen.saldo:.2f} MXN, solicitado: {req.monto:.2f} MXN",
        )

    now = datetime.now(tz=timezone.utc)
    tx_id = str(uuid.uuid4())

    origen.saldo = round(origen.saldo - req.monto, 2)
    destino.saldo = round(destino.saldo + req.monto, 2)

    tx = Transaccion(
        id=tx_id,
        cuenta_origen_id=origen.id,
        cuenta_destino_id=destino.id,
        monto=req.monto,
        tipo="SPEI",
        concepto=req.concepto,
        fecha=now,
        status="COMPLETADO",
    )
    db.add(tx)
    db.commit()

    return TransferenciaResponse(
        id=tx_id,
        origen=req.origen,
        destino=req.destino,
        monto=req.monto,
        concepto=req.concepto,
        fecha=now,
        status="COMPLETADO",
    )
