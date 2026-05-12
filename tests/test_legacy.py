def test_legacy_csv_all(client):
    r = client.get("/legacy/movimientos")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "cuenta_numero" in r.text


def test_legacy_csv_filtro_cuenta(client):
    r = client.get("/legacy/movimientos?cuenta=0001000001")
    assert r.status_code == 200
    assert "0001000001" in r.text


def test_legacy_json_format(client):
    r = client.get("/legacy/movimientos?cuenta=0001000001&format=json")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert all(row["cuenta_numero"] == "0001000001" for row in data)


def test_legacy_filtro_anio(client):
    r = client.get("/legacy/movimientos?anio=2025&format=json")
    assert r.status_code == 200
    data = r.json()
    assert all(row["fecha"].startswith("2025") for row in data)


def test_kyc_xml(client):
    r = client.get("/kyc/GALJ850315HDFRCN01")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert "GALJ850315HDFRCN01" in r.text
    assert "nivel_riesgo" in r.text


def test_kyc_json(client):
    r = client.get("/kyc/GALJ850315HDFRCN01?format=json")
    assert r.status_code == 200
    data = r.json()
    assert data["curp"] == "GALJ850315HDFRCN01"
    assert "nivel_riesgo" in data
    assert "documentos" in data


def test_kyc_no_encontrado(client):
    r = client.get("/kyc/XXXX000000XXXXXXX01")
    assert r.status_code == 404


def test_tarjeta_por_numero(client):
    r = client.get("/tarjetas/4215370012345001")
    assert r.status_code == 200
    data = r.json()
    assert "limite_credito" in data
    assert "puntos_banorte" in data
    assert "historial_pagos" in data


def test_tarjeta_por_cliente_rfc(client):
    r = client.get("/tarjetas/cliente/GALJ850315HDF")
    assert r.status_code == 200
    data = r.json()
    assert len(data["tarjetas"]) >= 1


def test_fx_usd_mxn(client):
    r = client.get("/fx/usd-mxn")
    assert r.status_code == 200
    data = r.json()
    assert data["par"] == "USD/MXN"
    assert 15.0 < data["compra"] < 22.0
    assert data["venta"] > data["compra"]
