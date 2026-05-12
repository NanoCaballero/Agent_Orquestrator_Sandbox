import logging

logger = logging.getLogger("bank-simulator.audit")


def log_operacion(operacion: str, cuenta: str, monto=None, detalle: str = ""):
    msg = f"[AUDIT] {operacion} | cuenta={cuenta}"
    if monto is not None:
        msg += f" | monto={monto:.2f}"
    if detalle:
        msg += f" | {detalle}"
    logger.info(msg)
