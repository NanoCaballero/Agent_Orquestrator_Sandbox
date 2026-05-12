def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_saldo_existente(client):
    r = client.get("/cuentas/0001000001/saldo")
    assert r.status_code == 200
    data = r.json()
    assert data["numero"] == "0001000001"
    assert data["tipo"] == "CHEQUES"
    assert data["saldo"] >= 0
    assert data["moneda"] == "MXN"


def test_saldo_inversion(client):
    r = client.get("/cuentas/0001000005/saldo")
    assert r.status_code == 200
    assert r.json()["tipo"] == "INVERSION"


def test_saldo_cuenta_inexistente(client):
    r = client.get("/cuentas/9999999999/saldo")
    assert r.status_code == 404


def test_movimientos_con_limit(client):
    r = client.get("/cuentas/0001000001/movimientos?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_movimientos_cuenta_inexistente(client):
    r = client.get("/cuentas/0000000000/movimientos")
    assert r.status_code == 404


def test_detalle_cuenta(client):
    r = client.get("/cuentas/0001000001")
    assert r.status_code == 200
    data = r.json()
    assert "cliente_nombre" in data
    assert "sucursal_nombre" in data
    assert data["numero"] == "0001000001"


def test_sucursales(client):
    r = client.get("/catalogo/sucursales")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    ciudades = {s["ciudad"] for s in data}
    assert "Ciudad de México" in ciudades


def test_cliente_por_rfc(client):
    r = client.get("/catalogo/clientes/GALJ850315HDF")
    assert r.status_code == 200
    data = r.json()
    assert data["rfc"] == "GALJ850315HDF"
    assert len(data["cuentas"]) >= 1


def test_cliente_rfc_inexistente(client):
    r = client.get("/catalogo/clientes/XXXX000000XXX")
    assert r.status_code == 404
