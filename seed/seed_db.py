"""
Seed script — creates bank.db and populates it with realistic Banorte mock data.
Run from bank-simulator/: python seed/seed_db.py
"""
import sys
import os
import uuid
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine, Base
from app.models import Sucursal, Cliente, Cuenta, Transaccion, Pago

random.seed(42)


def rand_date(start_days_ago: int, end_days_ago: int = 0) -> datetime:
    days = random.randint(end_days_ago, start_days_ago)
    return datetime(2026, 5, 11) - timedelta(days=days)


SUCURSALES = [
    ("SUC-001", "Banorte Centro Histórico", "Ciudad de México", "CDMX", "06000"),
    ("SUC-002", "Banorte Santa Fe", "Ciudad de México", "CDMX", "05349"),
    ("SUC-003", "Banorte San Pedro Garza García", "San Pedro Garza García", "Nuevo León", "66220"),
    ("SUC-004", "Banorte Chapultepec", "Guadalajara", "Jalisco", "44100"),
    ("SUC-005", "Banorte Monterrey Centro", "Monterrey", "Nuevo León", "64000"),
]

CLIENTES = [
    # id, nombre, curp, rfc, email, telefono, sucursal_id, segmento
    ("CLI-001", "Juan García López",       "GALJ850315HDFRCN01", "GALJ850315HDF", "juan.garcia@mail.com",       "5551234001", "SUC-001", "Premium"),
    ("CLI-002", "María Rodríguez Martínez","ROMM920610MDFDRR01", "ROMM920610GDF", "maria.rodriguez@mail.com",   "5551234002", "SUC-001", "Basico"),
    ("CLI-003", "Carlos Hernández Pérez",  "HEPC780225HNLRRL01", "HEPC780225NLE", "carlos.hernandez@mail.com",  "8181234003", "SUC-003", "PYME"),
    ("CLI-004", "Ana Sofía Gómez Torres",  "GOTA951118MJCMRN01", "GOTA951118JNE", "ana.gomez@mail.com",         "3331234004", "SUC-004", "Premium"),
    ("CLI-005", "Roberto Jiménez Cruz",    "JICR680730HSLRMB01", "JICR680730SLJ", "roberto.jimenez@mail.com",   "6671234005", "SUC-005", "Basico"),
    ("CLI-006", "Laura Martínez Fuentes",  "MAFL901205MDGRNR01", "MAFL901205DGO", "laura.martinez@mail.com",    "6181234006", "SUC-005", "Basico"),
    ("CLI-007", "Diego Sánchez Vargas",    "SAVD870914HJCNRG01", "SAVD870914JNE", "diego.sanchez@mail.com",     "3331234007", "SUC-004", "PYME"),
    ("CLI-008", "Valentina López Morales", "LOMV991230MDFPRL01", "LOMV991230MDF", "valentina.lopez@mail.com",   "5551234008", "SUC-002", "Basico"),
    ("CLI-009", "Andrés Torres Ruiz",      "TORA820512HQRNDR01", "TORA820512QRO", "andres.torres@mail.com",     "4421234009", "SUC-003", "Premium"),
    ("CLI-010", "Fernanda Ramírez Ortiz",  "RAOF930816MDFRMR01", "RAOF930816GDF", "fernanda.ramirez@mail.com",  "5551234010", "SUC-001", "Basico"),
    ("CLI-011", "Miguel Flores Díaz",      "FODM750329HNLRLG01", "FODM750329NLE", "miguel.flores@mail.com",     "8181234011", "SUC-003", "PYME"),
    ("CLI-012", "Isabel Castillo Herrera", "CAHI881115MJCSSL01", "CAHI881115JNE", "isabel.castillo@mail.com",   "3331234012", "SUC-004", "Basico"),
    ("CLI-013", "Alejandro Morales Vega",  "MOVA910403HSLRLJ01", "MOVA910403SLJ", "alejandro.morales@mail.com", "6671234013", "SUC-005", "Premium"),
    ("CLI-014", "Daniela Gutiérrez Mendoza","GUMD960718MDGRNN01","GUMD960718DGO", "daniela.gutierrez@mail.com", "6181234014", "SUC-005", "Basico"),
    ("CLI-015", "Emilio Reyes Quintero",   "REQE831224HDFYSL01", "REQE831224GDF", "emilio.reyes@mail.com",      "5551234015", "SUC-001", "PYME"),
    ("CLI-016", "Sofía Mendoza Guerrero",  "MEGS970505MNLNNF01", "MEGS970505NLE", "sofia.mendoza@mail.com",     "8181234016", "SUC-003", "Basico"),
    ("CLI-017", "Héctor Aguilar Peña",     "AGPH720810HQRLRC01", "AGPH720810QRO", "hector.aguilar@mail.com",    "4421234017", "SUC-004", "PYME"),
    ("CLI-018", "Paola Vargas Delgado",    "VADP890930MDFRLR01", "VADP890930MDF", "paola.vargas@mail.com",      "5551234018", "SUC-002", "Basico"),
    # empresas (sin CURP)
    ("CLI-019", "Innovación Digital SA de CV", None, "IDSA150601ABC", "contacto@innovacion.mx",   "5551234019", "SUC-002", "PYME"),
    ("CLI-020", "Constructora Norte SRL",       None, "CNO1930801XYZ", "finanzas@constructoranorte.mx", "8181234020", "SUC-003", "PYME"),
]

# (id, cliente_id, numero, tipo, saldo_inicial, moneda)
CUENTAS = [
    ("CTA-001", "CLI-001", "0001000001", "CHEQUES",   15000.00, "MXN"),
    ("CTA-002", "CLI-001", "0001000002", "AHORRO",    85000.00, "MXN"),
    ("CTA-003", "CLI-002", "0001000003", "CHEQUES",    8500.00, "MXN"),
    ("CTA-004", "CLI-003", "0001000004", "CHEQUES",   42000.00, "MXN"),
    ("CTA-005", "CLI-003", "0001000005", "INVERSION", 320000.00,"MXN"),
    ("CTA-006", "CLI-004", "0001000006", "CHEQUES",   25000.00, "MXN"),
    ("CTA-007", "CLI-004", "0001000007", "AHORRO",   180000.00, "MXN"),
    ("CTA-008", "CLI-005", "0001000008", "CHEQUES",    5200.00, "MXN"),
    ("CTA-009", "CLI-006", "0001000009", "CHEQUES",    9800.00, "MXN"),
    ("CTA-010", "CLI-007", "0001000010", "CHEQUES",   67000.00, "MXN"),
    ("CTA-011", "CLI-007", "0001000011", "INVERSION", 450000.00,"MXN"),
    ("CTA-012", "CLI-008", "0001000012", "CHEQUES",    3100.00, "MXN"),
    ("CTA-013", "CLI-009", "0001000013", "CHEQUES",   95000.00, "MXN"),
    ("CTA-014", "CLI-009", "0001000014", "AHORRO",   250000.00, "MXN"),
    ("CTA-015", "CLI-010", "0001000015", "CHEQUES",   12000.00, "MXN"),
    ("CTA-016", "CLI-011", "0001000016", "CHEQUES",   38000.00, "MXN"),
    ("CTA-017", "CLI-011", "0001000017", "INVERSION", 600000.00,"MXN"),
    ("CTA-018", "CLI-012", "0001000018", "CHEQUES",    4500.00, "MXN"),
    ("CTA-019", "CLI-013", "0001000019", "CHEQUES",   55000.00, "MXN"),
    ("CTA-020", "CLI-013", "0001000020", "AHORRO",   120000.00, "MXN"),
    ("CTA-021", "CLI-014", "0001000021", "CHEQUES",    6700.00, "MXN"),
    ("CTA-022", "CLI-015", "0001000022", "CHEQUES",   28000.00, "MXN"),
    ("CTA-023", "CLI-015", "0001000023", "INVERSION", 150000.00,"MXN"),
    ("CTA-024", "CLI-016", "0001000024", "CHEQUES",    2800.00, "MXN"),
    ("CTA-025", "CLI-017", "0001000025", "CHEQUES",   44000.00, "MXN"),
    ("CTA-026", "CLI-018", "0001000026", "CHEQUES",    7200.00, "MXN"),
    ("CTA-027", "CLI-019", "0001000027", "CHEQUES",  250000.00, "MXN"),
    ("CTA-028", "CLI-019", "0001000028", "INVERSION",1500000.00,"MXN"),
    ("CTA-029", "CLI-020", "0001000029", "CHEQUES",  380000.00, "MXN"),
    ("CTA-030", "CLI-020", "0001000030", "INVERSION",2200000.00,"MXN"),
]

CONCEPTOS_CREDITO = [
    "DEPOSITO NOMINA", "TRANSFERENCIA RECIBIDA SPEI", "DEPOSITO EFECTIVO SUCURSAL",
    "COBRO FACTURA CLIENTE", "DEVOLUCION", "INTERES MENSUAL", "AGUINALDO",
    "BONO TRIMESTRAL", "DEPOSITO CHEQUE", "ABONO PRESTAMO",
]
CONCEPTOS_DEBITO = [
    "PAGO RENTA", "RETIRO CAJERO ATM", "COMPRA SUPERMERCADO", "PAGO TARJETA CREDITO",
    "PAGO TELMEX", "PAGO CFE", "PAGO AGUA SACMEX", "TRANSFERENCIA ENVIADA SPEI",
    "COMPRA GASOLINERA", "PAGO HIPOTECA", "COMPRA RESTAURANT", "PAGO SEGURO",
    "COMPRA EN LINEA AMAZON", "COBRO COMISION", "PAGO PREDIAL",
]


def _build_cta_index(session) -> dict:
    return {c.id: c for c in session.query(Cuenta).all()}


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from app.db import SessionLocal
    session = SessionLocal()

    try:
        for s in SUCURSALES:
            session.add(Sucursal(id=s[0], nombre=s[1], ciudad=s[2], estado=s[3], codigo_postal=s[4]))

        for c in CLIENTES:
            session.add(Cliente(
                id=c[0], nombre=c[1], curp=c[2], rfc=c[3],
                email=c[4], telefono=c[5], sucursal_id=c[6], segmento=c[7],
            ))

        cta_map = {}
        for ct in CUENTAS:
            cta = Cuenta(
                id=ct[0], cliente_id=ct[1], numero=ct[2], tipo=ct[3],
                saldo=ct[4], moneda=ct[5], abierta_en=rand_date(1800, 365),
            )
            session.add(cta)
            cta_map[ct[0]] = {"numero": ct[2], "saldo": ct[4]}

        session.flush()

        # 200 transacciones distribuidas en últimos 90 días
        cta_ids = [ct[0] for ct in CUENTAS]
        for _ in range(200):
            tipo = random.choice(["DEPOSITO", "RETIRO", "SPEI", "PAGO"])
            origen_id = random.choice(cta_ids)
            destino_id = None
            if tipo == "SPEI":
                destino_id = random.choice([c for c in cta_ids if c != origen_id])
                concepto = "TRANSFERENCIA SPEI " + random.choice(["NOMINA", "FACTURA", "PAGO SERVICIO"])
            elif tipo == "DEPOSITO":
                concepto = random.choice(CONCEPTOS_CREDITO)
            else:
                concepto = random.choice(CONCEPTOS_DEBITO)

            monto = round(random.uniform(100, 15000), 2)
            session.add(Transaccion(
                id=str(uuid.uuid4()),
                cuenta_origen_id=origen_id if tipo in ("RETIRO", "SPEI", "PAGO") else None,
                cuenta_destino_id=destino_id if tipo == "SPEI" else (origen_id if tipo == "DEPOSITO" else None),
                monto=monto,
                tipo=tipo,
                concepto=concepto,
                fecha=rand_date(90),
                status="COMPLETADO",
            ))

        # 30 pagos de servicios
        servicios = ["CFE", "AGUA", "TELMEX", "PREDIAL"]
        for _ in range(30):
            cta_id = random.choice(cta_ids)
            servicio = random.choice(servicios)
            session.add(Pago(
                id=str(uuid.uuid4()),
                cuenta_id=cta_id,
                servicio=servicio,
                referencia=f"{servicio}-{random.randint(100000, 999999)}",
                monto=round(random.uniform(200, 8000), 2),
                fecha=rand_date(90),
            ))

        session.commit()
        print(f"✓ bank.db creada con {len(SUCURSALES)} sucursales, {len(CLIENTES)} clientes, "
              f"{len(CUENTAS)} cuentas, 200 transacciones, 30 pagos.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    seed()
