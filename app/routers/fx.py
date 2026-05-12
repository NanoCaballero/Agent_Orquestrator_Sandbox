import random
from datetime import date, datetime, timezone
from fastapi import APIRouter

from app.schemas import FxResponse

router = APIRouter(prefix="/fx", tags=["Tipo de Cambio (FX)"])

# Base rates — vary slightly day-to-day via seeded random
_BASE_COMPRA = 17.15
_BASE_VENTA = 17.35


def _tasa_del_dia(base: float, seed_offset: int) -> float:
    today = date.today()
    rng = random.Random(today.toordinal() + seed_offset)
    delta = rng.uniform(-0.25, 0.25)
    return round(base + delta, 4)


@router.get(
    "/usd-mxn",
    response_model=FxResponse,
    summary="Tipo de cambio USD/MXN del día (simulado)",
    description="Devuelve compra y venta del dólar para hoy. El valor varía día a día con una semilla determinista para reproducibilidad.",
)
def tipo_cambio_usd_mxn():
    return FxResponse(
        par="USD/MXN",
        compra=_tasa_del_dia(_BASE_COMPRA, 0),
        venta=_tasa_del_dia(_BASE_VENTA, 1),
        fecha_hora=datetime.now(tz=timezone.utc).isoformat(),
        fuente="Banorte Simulador (mock)",
    )


@router.get(
    "/eur-mxn",
    response_model=FxResponse,
    summary="Tipo de cambio EUR/MXN del día (simulado)",
)
def tipo_cambio_eur_mxn():
    return FxResponse(
        par="EUR/MXN",
        compra=_tasa_del_dia(18.50, 2),
        venta=_tasa_del_dia(18.80, 3),
        fecha_hora=datetime.now(tz=timezone.utc).isoformat(),
        fuente="Banorte Simulador (mock)",
    )
