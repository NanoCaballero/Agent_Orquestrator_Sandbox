from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Sucursal(Base):
    __tablename__ = "sucursales"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    codigo_postal = Column(String, nullable=False)
    clientes = relationship("Cliente", back_populates="sucursal")


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    curp = Column(String, unique=True, nullable=True)
    rfc = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    sucursal_id = Column(String, ForeignKey("sucursales.id"), nullable=False)
    segmento = Column(String, nullable=False)  # PYME | Premium | Basico
    sucursal = relationship("Sucursal", back_populates="clientes")
    cuentas = relationship("Cuenta", back_populates="cliente")


class Cuenta(Base):
    __tablename__ = "cuentas"
    id = Column(String, primary_key=True)
    cliente_id = Column(String, ForeignKey("clientes.id"), nullable=False)
    numero = Column(String, unique=True, nullable=False)
    tipo = Column(String, nullable=False)  # CHEQUES | AHORRO | INVERSION
    saldo = Column(Float, nullable=False, default=0.0)
    moneda = Column(String, nullable=False, default="MXN")
    abierta_en = Column(DateTime, nullable=False)
    cliente = relationship("Cliente", back_populates="cuentas")
    transacciones_origen = relationship("Transaccion", foreign_keys="Transaccion.cuenta_origen_id", back_populates="cuenta_origen")
    transacciones_destino = relationship("Transaccion", foreign_keys="Transaccion.cuenta_destino_id", back_populates="cuenta_destino")
    pagos = relationship("Pago", back_populates="cuenta")


class Transaccion(Base):
    __tablename__ = "transacciones"
    id = Column(String, primary_key=True)
    cuenta_origen_id = Column(String, ForeignKey("cuentas.id"), nullable=True)
    cuenta_destino_id = Column(String, ForeignKey("cuentas.id"), nullable=True)
    monto = Column(Float, nullable=False)
    tipo = Column(String, nullable=False)  # DEPOSITO | RETIRO | SPEI | PAGO
    concepto = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="COMPLETADO")
    cuenta_origen = relationship("Cuenta", foreign_keys=[cuenta_origen_id], back_populates="transacciones_origen")
    cuenta_destino = relationship("Cuenta", foreign_keys=[cuenta_destino_id], back_populates="transacciones_destino")


class Pago(Base):
    __tablename__ = "pagos"
    id = Column(String, primary_key=True)
    cuenta_id = Column(String, ForeignKey("cuentas.id"), nullable=False)
    servicio = Column(String, nullable=False)  # CFE | AGUA | TELMEX | PREDIAL
    referencia = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)
    cuenta = relationship("Cuenta", back_populates="pagos")
