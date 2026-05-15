"""Tests for internal bank systems (/interno/*)"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db_internal import InternalBase, get_internal_db
from app.main import app

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_INTERNAL_DB = "sqlite:///./test_internal.db"
test_internal_engine = create_engine(TEST_INTERNAL_DB, connect_args={"check_same_thread": False})
TestInternalSession = sessionmaker(autocommit=False, autoflush=False, bind=test_internal_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_internal_db():
    import app.db_internal as db_mod
    original_engine = db_mod.internal_engine
    original_session = db_mod.InternalSessionLocal

    db_mod.internal_engine = test_internal_engine
    db_mod.InternalSessionLocal = TestInternalSession
    InternalBase.metadata.create_all(bind=test_internal_engine)

    from seed.seed_internal_db import seed_internal
    seed_internal()

    yield

    db_mod.internal_engine = original_engine
    db_mod.InternalSessionLocal = original_session
    if os.path.exists("test_internal.db"):
        os.remove("test_internal.db")


@pytest.fixture
def client(setup_internal_db):
    def override():
        db = TestInternalSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_internal_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_internal_db, None)


# ── GL ────────────────────────────────────────────────────────────────────────

def test_gl_catalogo_completo(client):
    r = client.get("/interno/gl/cuentas")
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 50
    codigos = {c["codigo"] for c in data}
    assert "1100" in codigos
    assert "4100" in codigos


def test_gl_catalogo_filtro_tipo(client):
    r = client.get("/interno/gl/cuentas?tipo=ACTIVO")
    assert r.status_code == 200
    assert all(c["tipo"] == "ACTIVO" for c in r.json())


def test_gl_cuenta_detalle(client):
    r = client.get("/interno/gl/cuentas/1400")
    assert r.status_code == 200
    data = r.json()
    assert data["cuenta"]["nombre"] == "Cartera de Crédito"
    assert len(data["subcuentas"]) > 0


def test_gl_cuenta_inexistente(client):
    assert client.get("/interno/gl/cuentas/9999").status_code == 404


def test_gl_asientos(client):
    r = client.get("/interno/gl/asientos?limit=10")
    assert r.status_code == 200
    assert len(r.json()) <= 10


def test_gl_balanza(client):
    r = client.get("/interno/gl/balanza?mes=3&anio=2026")
    assert r.status_code == 200
    data = r.json()
    assert "total_cargos" in data
    assert "cuadra" in data


# ── Tesorería ─────────────────────────────────────────────────────────────────

def test_tesoreria_posicion_reciente(client):
    r = client.get("/interno/tesoreria/posicion")
    assert r.status_code == 200
    data = r.json()
    assert "saldo_banxico" in data
    assert data["ratio_liquidez_pct"] > 0


def test_tesoreria_posicion_fecha(client):
    r = client.get("/interno/tesoreria/posicion?fecha=2026-04-01")
    assert r.status_code == 200


def test_tesoreria_instrumentos(client):
    r = client.get("/interno/tesoreria/instrumentos")
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_tesoreria_instrumentos_filtro(client):
    r = client.get("/interno/tesoreria/instrumentos?emisora=CETES")
    assert r.status_code == 200
    assert all(i["emisora"] == "CETES" for i in r.json())


def test_tesoreria_operaciones(client):
    r = client.get("/interno/tesoreria/operaciones?status=ACTIVA")
    assert r.status_code == 200
    assert all(o["status"] == "ACTIVA" for o in r.json())


def test_tesoreria_tasas_json(client):
    r = client.get("/interno/tesoreria/tasas-referencia")
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert "tiie_28d" in data[0]


def test_tesoreria_tasas_csv(client):
    r = client.get("/interno/tesoreria/tasas-referencia?format=csv")
    assert r.status_code == 200
    assert "tiie_28d" in r.text


# ── Crédito ───────────────────────────────────────────────────────────────────

def test_credito_portafolio(client):
    r = client.get("/interno/credito/portafolio")
    assert r.status_code == 200
    data = r.json()
    assert data["total_creditos"] == 25
    assert data["saldo_insoluto_total"] > 0
    assert "por_tipo" in data


def test_credito_detalle(client):
    r = client.get("/interno/credito/CRD-001")
    assert r.status_code == 200
    data = r.json()
    assert data["credito"]["tipo"] == "HIPOTECARIO"
    assert len(data["amortizaciones"]) > 0
    assert data["calificacion"]["bucket_ifrs9"] == "A"


def test_credito_inexistente(client):
    assert client.get("/interno/credito/CRD-999").status_code == 404


def test_credito_calificacion_bucket(client):
    r = client.get("/interno/credito/calificacion?bucket=A")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    assert all(c["bucket_ifrs9"] == "A" for c in data["detalle"])


def test_credito_cliente(client):
    r = client.get("/interno/credito/cliente/CLI-001")
    assert r.status_code == 200
    assert len(r.json()) >= 1


# ── RRHH ──────────────────────────────────────────────────────────────────────

def test_rrhh_empleados(client):
    r = client.get("/interno/rrhh/empleados")
    assert r.status_code == 200
    assert len(r.json()) == 50


def test_rrhh_empleados_filtro_area(client):
    r = client.get("/interno/rrhh/empleados?area=TI")
    assert r.status_code == 200
    assert all(e["area"] == "TI" for e in r.json())


def test_rrhh_nomina(client):
    r = client.get("/interno/rrhh/nomina/2026-03")
    assert r.status_code == 200
    data = r.json()
    assert data["total_empleados"] == 50
    assert data["total_bruto"] > 0


def test_rrhh_nomina_no_existe(client):
    assert client.get("/interno/rrhh/nomina/2020-01").status_code == 404


def test_rrhh_centros_costo(client):
    r = client.get("/interno/rrhh/centros-costo")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 8
    assert all("ejercido_pct" in c for c in data)


# ── Activos Fijos ─────────────────────────────────────────────────────────────

def test_activos_inventario(client):
    r = client.get("/interno/activos")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 60
    assert data["valor_libro_total"] > 0


def test_activos_filtro_tipo(client):
    r = client.get("/interno/activos?tipo=ATM")
    assert r.status_code == 200
    assert all(a["tipo"] == "ATM" for a in r.json()["activos"])


def test_activos_depreciacion(client):
    r = client.get("/interno/activos/AFX-001/depreciacion")
    assert r.status_code == 200
    data = r.json()
    assert len(data["depreciacion"]) > 0


def test_activos_mantenimientos_pendientes(client):
    r = client.get("/interno/activos/mantenimientos-pendientes")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Riesgos ───────────────────────────────────────────────────────────────────

def test_riesgos_alertas(client):
    r = client.get("/interno/riesgos/alertas")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 18
    assert "abiertas" in data


def test_riesgos_alertas_filtro_status(client):
    r = client.get("/interno/riesgos/alertas?status=ABIERTA")
    assert r.status_code == 200
    assert all(a["status"] == "ABIERTA" for a in r.json()["alertas"])


def test_riesgos_var(client):
    r = client.get("/interno/riesgos/var")
    assert r.status_code == 200
    data = r.json()
    assert data["total_dias"] == 90


def test_riesgos_contrapartes(client):
    r = client.get("/interno/riesgos/contrapartes")
    assert r.status_code == 200
    assert len(r.json()) > 0
    assert all("utilizacion_pct" in c for c in r.json())


# ── Regulatorio ───────────────────────────────────────────────────────────────

def test_regulatorio_icap(client):
    r = client.get("/interno/regulatorio/icap")
    assert r.status_code == 200
    data = r.json()
    assert data["ultimo_icap_pct"] > 10.5
    assert len(data["serie_historica"]) == 12


def test_regulatorio_lcr(client):
    r = client.get("/interno/regulatorio/lcr")
    assert r.status_code == 200
    data = r.json()
    assert data["ultimo_lcr_pct"] > 100
    assert len(data["serie_historica"]) == 12


def test_regulatorio_reportes(client):
    r = client.get("/interno/regulatorio/reportes")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 72


# ── Organigrama ───────────────────────────────────────────────────────────────

def test_org_estructura(client):
    r = client.get("/interno/org/estructura")
    assert r.status_code == 200
    data = r.json()
    assert "direccion_general" in data
    assert len(data["direccion_general"]["subdirecciones"]) >= 5


def test_org_buscar_area(client):
    r = client.get("/interno/org/area/Mesa de Dinero")
    assert r.status_code == 200
    assert len(r.json()) > 0


def test_org_area_no_encontrada(client):
    assert client.get("/interno/org/area/AreaQueNoExiste12345").status_code == 404


def test_org_direcciones(client):
    r = client.get("/interno/org/direcciones")
    assert r.status_code == 200
    assert len(r.json()) >= 7
