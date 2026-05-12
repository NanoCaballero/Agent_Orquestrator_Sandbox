from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Sucursal, Cliente, Cuenta
from app.schemas import SucursalResponse, ClienteResponse

router = APIRouter(prefix="/catalogo", tags=["Catálogo"])


@router.get(
    "/sucursales",
    response_model=List[SucursalResponse],
    summary="Listar todas las sucursales Banorte del simulador",
)
def listar_sucursales(db: Session = Depends(get_db)):
    return [
        SucursalResponse(id=s.id, nombre=s.nombre, ciudad=s.ciudad, estado=s.estado, codigo_postal=s.codigo_postal)
        for s in db.query(Sucursal).all()
    ]


@router.get(
    "/clientes/{rfc}",
    response_model=ClienteResponse,
    summary="Consultar cliente por RFC + sus cuentas",
)
def consultar_cliente(rfc: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.rfc == rfc).first()
    if not cliente:
        raise HTTPException(status_code=404, detail=f"Cliente con RFC {rfc} no encontrado")

    return ClienteResponse(
        id=cliente.id,
        nombre=cliente.nombre,
        curp=cliente.curp,
        rfc=cliente.rfc,
        email=cliente.email,
        telefono=cliente.telefono,
        segmento=cliente.segmento,
        sucursal=cliente.sucursal.nombre,
        cuentas=[c.numero for c in cliente.cuentas],
    )
