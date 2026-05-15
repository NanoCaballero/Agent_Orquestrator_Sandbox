from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text
from app.db_internal import InternalBase


# ── GL — Contabilidad General ─────────────────────────────────────────────────

class GlCatalogoCuentas(InternalBase):
    __tablename__ = "gl_catalogo_cuentas"
    codigo = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)       # ACTIVO|PASIVO|CAPITAL|INGRESO|EGRESO|ORDEN
    nivel = Column(Integer, nullable=False)     # 1=grupo, 2=subgrupo, 3=cuenta, 4=subcuenta
    codigo_padre = Column(String, nullable=True)
    naturaleza = Column(String, nullable=False) # DEUDORA|ACREEDORA
    activa = Column(Boolean, default=True)


class GlAsiento(InternalBase):
    __tablename__ = "gl_asientos"
    id = Column(String, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    concepto = Column(String, nullable=False)
    usuario_captura = Column(String, nullable=False)
    centro_costo = Column(String, nullable=True)
    status = Column(String, nullable=False, default="APLICADO")  # APLICADO|PENDIENTE|RECHAZADO
    referencia_sistema = Column(String, nullable=True)  # ej. TX-uuid de bank.db


class GlPartida(InternalBase):
    __tablename__ = "gl_partidas"
    id = Column(String, primary_key=True)
    asiento_id = Column(String, nullable=False)
    cuenta_codigo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)       # CARGO|ABONO
    monto = Column(Float, nullable=False)
    centro_costo = Column(String, nullable=True)


# ── TRY — Tesorería ───────────────────────────────────────────────────────────

class TryPosicionDiaria(InternalBase):
    __tablename__ = "try_posicion_diaria"
    fecha = Column(String, primary_key=True)   # YYYY-MM-DD
    saldo_banxico = Column(Float, nullable=False)
    disponible_spei = Column(Float, nullable=False)
    inversion_overnight = Column(Float, nullable=False)
    creditos_interbancarios_recibidos = Column(Float, nullable=False)
    creditos_interbancarios_otorgados = Column(Float, nullable=False)
    ratio_liquidez_pct = Column(Float, nullable=False)
    alerta_liquidez = Column(Boolean, default=False)


class TryInstrumento(InternalBase):
    __tablename__ = "try_instrumentos"
    id = Column(String, primary_key=True)
    emisora = Column(String, nullable=False)          # CETES|BONM|UDIBONO|BONDESD
    serie = Column(String, nullable=False)
    plazo_dias = Column(Integer, nullable=False)
    tasa_rendimiento = Column(Float, nullable=False)  # pct anual
    valor_nominal = Column(Float, nullable=False)
    valor_mercado = Column(Float, nullable=False)
    precio_sucio = Column(Float, nullable=False)
    fecha_compra = Column(String, nullable=False)
    fecha_vencimiento = Column(String, nullable=False)
    clasificacion = Column(String, nullable=False)    # NEGOCIACION|DISPONIBLE_VENTA|VENCIMIENTO


class TryOperacionMesa(InternalBase):
    __tablename__ = "try_operaciones_mesa"
    id = Column(String, primary_key=True)
    tipo = Column(String, nullable=False)         # REPO|PRESTAMO_IB|COMPRA_CETES|VENTA_BONOS
    contraparte = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    tasa = Column(Float, nullable=False)
    fecha_inicio = Column(String, nullable=False)
    fecha_vencimiento = Column(String, nullable=False)
    status = Column(String, nullable=False)       # ACTIVA|VENCIDA|CANCELADA
    operador = Column(String, nullable=False)


# ── CRD — Cartera de Crédito ──────────────────────────────────────────────────

class CrdCredito(InternalBase):
    __tablename__ = "crd_creditos"
    id = Column(String, primary_key=True)
    # cliente_id references bank.db clientes — no FK constraint across DBs
    cliente_id = Column(String, nullable=False)
    tipo = Column(String, nullable=False)         # HIPOTECARIO|PERSONAL|PYME|AUTOMOTRIZ
    monto_original = Column(Float, nullable=False)
    saldo_insoluto = Column(Float, nullable=False)
    tasa_anual = Column(Float, nullable=False)
    plazo_meses = Column(Integer, nullable=False)
    pago_mensual = Column(Float, nullable=False)
    fecha_apertura = Column(String, nullable=False)
    fecha_vencimiento = Column(String, nullable=False)
    dias_vencido = Column(Integer, default=0)
    status = Column(String, nullable=False)       # VIGENTE|VENCIDO|CASTIGADO|LIQUIDADO


class CrdAmortizacion(InternalBase):
    __tablename__ = "crd_amortizaciones"
    id = Column(String, primary_key=True)
    credito_id = Column(String, nullable=False)
    numero_pago = Column(Integer, nullable=False)
    fecha_pago = Column(String, nullable=False)
    capital = Column(Float, nullable=False)
    intereses = Column(Float, nullable=False)
    iva_intereses = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    pagado = Column(Boolean, default=False)
    fecha_pago_real = Column(String, nullable=True)
    monto_pagado = Column(Float, nullable=True)


class CrdCalificacion(InternalBase):
    __tablename__ = "crd_calificacion_cartera"
    id = Column(String, primary_key=True)
    credito_id = Column(String, nullable=False)
    bucket_ifrs9 = Column(String, nullable=False)   # A|B1|B2|C1|C2|D|E
    probabilidad_incumplimiento = Column(Float, nullable=False)  # pct
    perdida_dado_incumplimiento = Column(Float, nullable=False)  # pct
    provision_requerida = Column(Float, nullable=False)
    fecha_calificacion = Column(String, nullable=False)
    calificador = Column(String, nullable=False)


# ── RH — Recursos Humanos / Nómina ───────────────────────────────────────────

class RhEmpleado(InternalBase):
    __tablename__ = "rh_empleados"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    puesto = Column(String, nullable=False)
    nivel = Column(Integer, nullable=False)    # 1=director, 8=operativo
    area = Column(String, nullable=False)
    sucursal_id = Column(String, nullable=True)  # ref bank.db sucursales
    fecha_ingreso = Column(String, nullable=False)
    sueldo_bruto = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="ACTIVO")  # ACTIVO|BAJA
    tipo_contrato = Column(String, nullable=False)  # BASE|CONFIANZA|HONORARIOS


class RhNominaMensual(InternalBase):
    __tablename__ = "rh_nomina_mensual"
    id = Column(String, primary_key=True)
    empleado_id = Column(String, nullable=False)
    periodo = Column(String, nullable=False)      # YYYY-MM
    sueldo_bruto = Column(Float, nullable=False)
    isr = Column(Float, nullable=False)
    imss = Column(Float, nullable=False)
    infonavit = Column(Float, nullable=False)
    neto = Column(Float, nullable=False)
    fecha_pago = Column(String, nullable=False)
    banco_deposito = Column(String, nullable=False)


class RhCentroCosto(InternalBase):
    __tablename__ = "rh_centros_costo"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    area = Column(String, nullable=False)  # RETAIL|CORPORATIVO|TESORERIA|TI|RIESGO|RRHH|AUDITORIA|JURIDICO
    director = Column(String, nullable=False)
    presupuesto_anual = Column(Float, nullable=False)
    gasto_acumulado = Column(Float, nullable=False)
    empleados_activos = Column(Integer, nullable=False)


# ── AFX — Activos Fijos ───────────────────────────────────────────────────────

class AfxInventario(InternalBase):
    __tablename__ = "afx_inventario"
    id = Column(String, primary_key=True)
    tipo = Column(String, nullable=False)         # SUCURSAL|ATM|SERVIDOR|BLINDADO|MOBILIARIO
    descripcion = Column(String, nullable=False)
    numero_serie = Column(String, nullable=True)
    ubicacion = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    fecha_adquisicion = Column(String, nullable=False)
    valor_original = Column(Float, nullable=False)
    valor_libro = Column(Float, nullable=False)
    vida_util_anios = Column(Integer, nullable=False)
    status = Column(String, nullable=False)       # OPERATIVO|MANTENIMIENTO|BAJA


class AfxDepreciacion(InternalBase):
    __tablename__ = "afx_depreciacion"
    id = Column(String, primary_key=True)
    activo_id = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    depreciacion_mensual = Column(Float, nullable=False)
    depreciacion_acumulada = Column(Float, nullable=False)
    valor_libro_fin = Column(Float, nullable=False)


class AfxMantenimiento(InternalBase):
    __tablename__ = "afx_mantenimiento"
    id = Column(String, primary_key=True)
    activo_id = Column(String, nullable=False)
    tipo_mantenimiento = Column(String, nullable=False)  # PREVENTIVO|CORRECTIVO|EMERGENCIA
    fecha = Column(String, nullable=False)
    costo = Column(Float, nullable=False)
    proveedor = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    proxima_revision = Column(String, nullable=False)
    status = Column(String, nullable=False)  # COMPLETADO|PENDIENTE|EN_PROCESO


# ── RSG — Riesgos y Fraude ────────────────────────────────────────────────────

class RsgAlertaFraude(InternalBase):
    __tablename__ = "rsg_alertas_fraude"
    id = Column(String, primary_key=True)
    cuenta_numero = Column(String, nullable=False)  # ref bank.db cuentas
    fecha = Column(DateTime, nullable=False)
    tipo_alerta = Column(String, nullable=False)    # MONTO_INUSUAL|PATRON_GEOGRAFICO|VELOCIDAD|LISTA_NEGRA
    score_riesgo = Column(Float, nullable=False)    # 0-100
    monto_sospechoso = Column(Float, nullable=True)
    descripcion = Column(Text, nullable=True)
    status = Column(String, nullable=False)         # ABIERTA|INVESTIGANDO|CERRADA|FALSO_POSITIVO
    analista = Column(String, nullable=True)
    resolucion = Column(Text, nullable=True)


class RsgVarDiario(InternalBase):
    __tablename__ = "rsg_var_diario"
    fecha = Column(String, primary_key=True)
    var_95 = Column(Float, nullable=False)
    var_99 = Column(Float, nullable=False)
    var_estresado = Column(Float, nullable=False)
    portafolio_mxn = Column(Float, nullable=False)
    limite_var = Column(Float, nullable=False)
    breach = Column(Boolean, default=False)
    metodologia = Column(String, nullable=False, default="HISTORICA")


class RsgLimiteContraparte(InternalBase):
    __tablename__ = "rsg_limites_contraparte"
    contraparte = Column(String, primary_key=True)
    tipo = Column(String, nullable=False)            # BANCO|GOBIERNO|EMPRESA
    calificacion_externa = Column(String, nullable=True)  # AAA, AA+, etc.
    limite_aprobado = Column(Float, nullable=False)
    exposicion_actual = Column(Float, nullable=False)
    headroom = Column(Float, nullable=False)
    ultima_revision = Column(String, nullable=False)
    vencimiento_linea = Column(String, nullable=False)


# ── REG — Regulatorio / CNBV ─────────────────────────────────────────────────

class RegIcapHistorico(InternalBase):
    __tablename__ = "reg_icap_historico"
    fecha = Column(String, primary_key=True)    # YYYY-MM-DD (último día del mes)
    tier1_capital = Column(Float, nullable=False)
    tier2_capital = Column(Float, nullable=False)
    capital_total = Column(Float, nullable=False)
    activos_ponderados_riesgo = Column(Float, nullable=False)
    icap_pct = Column(Float, nullable=False)
    limite_minimo_pct = Column(Float, nullable=False, default=10.5)
    cumple = Column(Boolean, nullable=False)


class RegLcrHistorico(InternalBase):
    __tablename__ = "reg_lcr_historico"
    fecha = Column(String, primary_key=True)
    activos_liquidos_hqla = Column(Float, nullable=False)
    salidas_netas_30d = Column(Float, nullable=False)
    lcr_pct = Column(Float, nullable=False)
    limite_minimo_pct = Column(Float, nullable=False, default=100.0)
    cumple = Column(Boolean, nullable=False)


class RegReporteEnviado(InternalBase):
    __tablename__ = "reg_reportes_enviados"
    id = Column(String, primary_key=True)
    tipo_reporte = Column(String, nullable=False)  # R01A|R04B|R10|R21A|etc.
    descripcion = Column(String, nullable=False)
    periodo = Column(String, nullable=False)        # YYYY-MM
    fecha_envio = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)         # ENVIADO|ACEPTADO|OBSERVACIONES|RECHAZADO
    folio_cnbv = Column(String, nullable=True)
    observaciones = Column(Text, nullable=True)
