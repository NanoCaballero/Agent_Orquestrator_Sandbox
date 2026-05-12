from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import TransferenciaRequest, TransferenciaResponse
from app.services.transferencia_service import ejecutar_transferencia

router = APIRouter(prefix="/transferencias", tags=["Transferencias"])


@router.post(
    "",
    response_model=TransferenciaResponse,
    status_code=201,
    summary="Ejecutar transferencia SPEI simulada entre cuentas",
)
def transferir(req: TransferenciaRequest, db: Session = Depends(get_db)):
    """
    Transfiere monto de cuenta origen a destino de forma atómica.
    Retorna HTTP 422 si saldo insuficiente, 404 si alguna cuenta no existe.
    """
    return ejecutar_transferencia(req, db)
