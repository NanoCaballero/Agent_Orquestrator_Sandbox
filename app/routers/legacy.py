import csv
import io
import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/legacy", tags=["Legacy / Mainframe (CSV)"])

_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "seed", "movimientos_legacy.csv")


def _read_csv_rows() -> list[dict]:
    with open(_CSV_PATH, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@router.get(
    "/movimientos",
    summary="Movimientos históricos del mainframe legacy",
    description=(
        "Lee directamente el archivo CSV de mainframe. "
        "Por defecto devuelve texto CSV; usa `?format=json` para JSON. "
        "Filtra por `cuenta` (número de cuenta) y/o `anio` (año 4 dígitos)."
    ),
)
def movimientos_legacy(
    cuenta: str = Query(None, description="Número de cuenta (10 dígitos)"),
    anio: int = Query(None, description="Año del movimiento, ej. 2025"),
    format: str = Query("csv", description="Formato de respuesta: csv | json"),
):
    rows = _read_csv_rows()

    if cuenta:
        rows = [r for r in rows if r.get("cuenta_numero") == cuenta]
    if anio:
        rows = [r for r in rows if r.get("fecha", "").startswith(str(anio))]

    if not rows:
        if format == "json":
            return []
        return PlainTextResponse("cuenta_numero,fecha,descripcion,cargo,abono,saldo_posterior,referencia,canal\n")

    if format == "json":
        for r in rows:
            r["cargo"] = float(r["cargo"]) if r.get("cargo") else None
            r["abono"] = float(r["abono"]) if r.get("abono") else None
            r["saldo_posterior"] = float(r["saldo_posterior"]) if r.get("saldo_posterior") else None
        return rows

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return PlainTextResponse(output.getvalue(), media_type="text/csv")
