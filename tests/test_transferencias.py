import pytest


def test_transferencia_exitosa(client):
    saldo_antes = client.get("/cuentas/0001000001/saldo").json()["saldo"]

    r = client.post("/transferencias", json={
        "origen": "0001000001",
        "destino": "0001000003",
        "monto": 100.00,
        "concepto": "prueba transferencia",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "COMPLETADO"
    assert data["monto"] == 100.00

    saldo_despues = client.get("/cuentas/0001000001/saldo").json()["saldo"]
    assert round(saldo_despues, 2) == round(saldo_antes - 100.00, 2)


def test_transferencia_saldo_insuficiente(client):
    r = client.post("/transferencias", json={
        "origen": "0001000001",
        "destino": "0001000003",
        "monto": 999999999.00,
        "concepto": "transferencia imposible",
    })
    assert r.status_code == 422
    assert "Saldo insuficiente" in r.json()["detail"]


def test_transferencia_cuenta_origen_inexistente(client):
    r = client.post("/transferencias", json={
        "origen": "0000000000",
        "destino": "0001000003",
        "monto": 500.00,
        "concepto": "test",
    })
    assert r.status_code == 404


def test_transferencia_cuenta_destino_inexistente(client):
    r = client.post("/transferencias", json={
        "origen": "0001000001",
        "destino": "0000000000",
        "monto": 500.00,
        "concepto": "test",
    })
    assert r.status_code == 404


def test_pago_servicio_exitoso(client):
    r = client.post("/pagos/servicios", json={
        "cuenta": "0001000002",
        "servicio": "CFE",
        "referencia": "CFE-123456789",
        "monto": 850.00,
    })
    assert r.status_code == 201
    data = r.json()
    assert data["servicio"] == "CFE"
    assert "folio_confirmacion" in data
    assert data["folio_confirmacion"].startswith("BNR-CFE-")


def test_pago_servicio_invalido(client):
    r = client.post("/pagos/servicios", json={
        "cuenta": "0001000002",
        "servicio": "NETFLIX",
        "referencia": "ABC-123",
        "monto": 219.00,
    })
    assert r.status_code == 400
