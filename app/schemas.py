from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SaldoResponse(BaseModel):
    numero: str
    tipo: str
    saldo: float
    moneda: str


class MovimientoResponse(BaseModel):
    id: str
    tipo: str
    concepto: str
    monto: float
    fecha: datetime
    status: str
    cuenta_contraparte: Optional[str] = None


class CuentaDetalleResponse(BaseModel):
    numero: str
    tipo: str
    saldo: float
    moneda: str
    abierta_en: datetime
    cliente_nombre: str
    cliente_rfc: str
    cliente_segmento: str
    sucursal_nombre: str
    sucursal_ciudad: str


class TransferenciaRequest(BaseModel):
    origen: str = Field(..., description="Número de cuenta origen (10 dígitos)")
    destino: str = Field(..., description="Número de cuenta destino (10 dígitos)")
    monto: float = Field(..., gt=0, description="Monto en MXN")
    concepto: str = Field(..., min_length=3, max_length=100)


class TransferenciaResponse(BaseModel):
    id: str
    origen: str
    destino: str
    monto: float
    concepto: str
    fecha: datetime
    status: str


class PagoServicioRequest(BaseModel):
    cuenta: str = Field(..., description="Número de cuenta origen")
    servicio: str = Field(..., description="CFE | AGUA | TELMEX | PREDIAL")
    referencia: str = Field(..., description="Referencia del servicio")
    monto: float = Field(..., gt=0)


class PagoServicioResponse(BaseModel):
    id: str
    cuenta: str
    servicio: str
    referencia: str
    monto: float
    fecha: datetime
    folio_confirmacion: str


class ClienteResponse(BaseModel):
    id: str
    nombre: str
    curp: Optional[str]
    rfc: str
    email: str
    telefono: str
    segmento: str
    sucursal: str
    cuentas: List[str]


class SucursalResponse(BaseModel):
    id: str
    nombre: str
    ciudad: str
    estado: str
    codigo_postal: str


class FxResponse(BaseModel):
    par: str
    compra: float
    venta: float
    fecha_hora: str
    fuente: str
