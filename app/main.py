from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base
from app.db_internal import internal_engine, InternalBase
from app.routers import cuentas, transferencias, tarjetas, legacy, kyc, pagos, fx, catalogo
from app.routers.interno import gl, tesoreria, credito, rrhh, activos, riesgos, regulatorio, org

Base.metadata.create_all(bind=engine)
InternalBase.metadata.create_all(bind=internal_engine)

app = FastAPI(
    title="Banorte Bank Simulator",
    description=(
        "Backend Python que simula las APIs de un banco para probar tools del Agent Orchestration Platform. "
        "Datos externos: SQLite bank.db (cuentas/transacciones), JSON (tarjetas), CSV (mainframe), XML (KYC). "
        "Datos internos (/interno/*): SQLite internal.db — GL, Tesorería, Crédito, RRHH, Activos Fijos, Riesgos, Regulatorio CNBV, Organigrama."
    ),
    version="1.0.0",
    contact={"name": "Equipo Fantasy Labs", "email": "nanocaballeroz@gmail.com"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cuentas.router)
app.include_router(transferencias.router)
app.include_router(tarjetas.router)
app.include_router(legacy.router)
app.include_router(kyc.router)
app.include_router(pagos.router)
app.include_router(fx.router)
app.include_router(catalogo.router)

# Sistemas internos del banco
app.include_router(gl.router)
app.include_router(tesoreria.router)
app.include_router(credito.router)
app.include_router(rrhh.router)
app.include_router(activos.router)
app.include_router(riesgos.router)
app.include_router(regulatorio.router)
app.include_router(org.router)


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "bank-simulator", "version": "1.0.0"}
