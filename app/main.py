from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base
from app.routers import cuentas, transferencias, tarjetas, legacy, kyc, pagos, fx, catalogo

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Banorte Bank Simulator",
    description=(
        "Backend Python que simula las APIs de un banco para probar tools del Agent Orchestration Platform. "
        "Expone datos desde múltiples fuentes: SQLite (cuentas/transacciones), "
        "JSON (tarjetas), CSV (mainframe legacy) y XML (KYC/identidad)."
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


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "bank-simulator", "version": "1.0.0"}
