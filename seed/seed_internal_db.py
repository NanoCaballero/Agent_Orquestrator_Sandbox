"""
Seed script — crea internal.db con datos internos del banco.
Run from bank-simulator/: python seed/seed_internal_db.py
"""
import sys, os, uuid, random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db_internal import internal_engine, InternalBase, InternalSessionLocal
from app.models_internal import (
    GlCatalogoCuentas, GlAsiento, GlPartida,
    TryPosicionDiaria, TryInstrumento, TryOperacionMesa,
    CrdCredito, CrdAmortizacion, CrdCalificacion,
    RhEmpleado, RhNominaMensual, RhCentroCosto,
    AfxInventario, AfxDepreciacion, AfxMantenimiento,
    RsgAlertaFraude, RsgVarDiario, RsgLimiteContraparte,
    RegIcapHistorico, RegLcrHistorico, RegReporteEnviado,
)

random.seed(99)
TODAY = date(2026, 5, 15)


def d(days_ago=0):
    return (TODAY - timedelta(days=days_ago)).isoformat()


def dt(days_ago=0):
    return datetime(2026, 5, 15) - timedelta(days=days_ago)


# ── GL Catálogo ────────────────────────────────────────────────────────────────

GL_CATALOGO = [
    # (codigo, nombre, tipo, nivel, codigo_padre, naturaleza)
    ("1", "ACTIVO", "ACTIVO", 1, None, "DEUDORA"),
    ("1100", "Disponibilidades", "ACTIVO", 2, "1", "DEUDORA"),
    ("1101", "Caja", "ACTIVO", 3, "1100", "DEUDORA"),
    ("1102", "Depósitos en Banxico", "ACTIVO", 3, "1100", "DEUDORA"),
    ("1103", "Depósitos en Bancos Nacionales", "ACTIVO", 3, "1100", "DEUDORA"),
    ("1104", "Depósitos en Bancos Extranjeros", "ACTIVO", 3, "1100", "DEUDORA"),
    ("1105", "Metales Amonedados", "ACTIVO", 3, "1100", "DEUDORA"),
    ("1200", "Inversiones en Valores", "ACTIVO", 2, "1", "DEUDORA"),
    ("1201", "CETES - Títulos para Negociar", "ACTIVO", 3, "1200", "DEUDORA"),
    ("1202", "Bonos M - Títulos para Negociar", "ACTIVO", 3, "1200", "DEUDORA"),
    ("1203", "UDIBONOs - Disponibles para Venta", "ACTIVO", 3, "1200", "DEUDORA"),
    ("1204", "BondesD - Mantenidos a Vencimiento", "ACTIVO", 3, "1200", "DEUDORA"),
    ("1205", "Acciones y ETFs", "ACTIVO", 3, "1200", "DEUDORA"),
    ("1300", "Deudores por Reporto", "ACTIVO", 2, "1", "DEUDORA"),
    ("1301", "Deudores por Reporto - Títulos Gubernamentales", "ACTIVO", 3, "1300", "DEUDORA"),
    ("1302", "Deudores por Reporto - Títulos Bancarios", "ACTIVO", 3, "1300", "DEUDORA"),
    ("1400", "Cartera de Crédito", "ACTIVO", 2, "1", "DEUDORA"),
    ("1401", "Cartera Vigente - Créditos Hipotecarios", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1402", "Cartera Vigente - Créditos al Consumo Personal", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1403", "Cartera Vigente - Créditos PYME", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1404", "Cartera Vigente - Créditos Automotriz", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1410", "Cartera Vencida - Créditos Hipotecarios", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1411", "Cartera Vencida - Créditos al Consumo Personal", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1412", "Cartera Vencida - Créditos PYME", "ACTIVO", 3, "1400", "DEUDORA"),
    ("1450", "Estimación Preventiva para Riesgos Crediticios", "ACTIVO", 3, "1400", "ACREEDORA"),
    ("1500", "Otras Cuentas por Cobrar", "ACTIVO", 2, "1", "DEUDORA"),
    ("1501", "Impuestos por Recuperar (IVA Acreditable)", "ACTIVO", 3, "1500", "DEUDORA"),
    ("1502", "Deudores Diversos", "ACTIVO", 3, "1500", "DEUDORA"),
    ("1503", "Préstamos a Empleados", "ACTIVO", 3, "1500", "DEUDORA"),
    ("1600", "Bienes Muebles e Inmuebles", "ACTIVO", 2, "1", "DEUDORA"),
    ("1601", "Edificios y Locales (Sucursales)", "ACTIVO", 3, "1600", "DEUDORA"),
    ("1602", "Mobiliario y Equipo de Oficina", "ACTIVO", 3, "1600", "DEUDORA"),
    ("1603", "Equipo de Cómputo y Servidores", "ACTIVO", 3, "1600", "DEUDORA"),
    ("1604", "Vehículos Blindados", "ACTIVO", 3, "1600", "DEUDORA"),
    ("1605", "ATMs y Dispositivos de Autoservicio", "ACTIVO", 3, "1600", "DEUDORA"),
    ("1610", "Depreciación Acumulada - Edificios", "ACTIVO", 3, "1600", "ACREEDORA"),
    ("1611", "Depreciación Acumulada - Mobiliario", "ACTIVO", 3, "1600", "ACREEDORA"),
    ("1612", "Depreciación Acumulada - Cómputo", "ACTIVO", 3, "1600", "ACREEDORA"),
    ("1613", "Depreciación Acumulada - Vehículos", "ACTIVO", 3, "1600", "ACREEDORA"),
    ("1614", "Depreciación Acumulada - ATMs", "ACTIVO", 3, "1600", "ACREEDORA"),
    ("1700", "Otros Activos", "ACTIVO", 2, "1", "DEUDORA"),
    ("1701", "Activos Intangibles (Software)", "ACTIVO", 3, "1700", "DEUDORA"),
    ("1702", "Gastos de Instalación", "ACTIVO", 3, "1700", "DEUDORA"),
    ("2", "PASIVO", "PASIVO", 1, None, "ACREEDORA"),
    ("2100", "Captación Tradicional", "PASIVO", 2, "2", "ACREEDORA"),
    ("2101", "Depósitos a la Vista (Cuentas de Cheques)", "PASIVO", 3, "2100", "ACREEDORA"),
    ("2102", "Depósitos de Ahorro", "PASIVO", 3, "2100", "ACREEDORA"),
    ("2103", "Depósitos a Plazo Fijo", "PASIVO", 3, "2100", "ACREEDORA"),
    ("2104", "Pagarés con Rendimiento Liquidable al Vencimiento", "PASIVO", 3, "2100", "ACREEDORA"),
    ("2200", "Préstamos Interbancarios y de Otros Organismos", "PASIVO", 2, "2", "ACREEDORA"),
    ("2201", "Préstamos de Banxico (Ventanilla)", "PASIVO", 3, "2200", "ACREEDORA"),
    ("2202", "Préstamos de Bancos Nacionales (Overnight)", "PASIVO", 3, "2200", "ACREEDORA"),
    ("2203", "Préstamos de Bancos Extranjeros", "PASIVO", 3, "2200", "ACREEDORA"),
    ("2204", "Financiamiento NAFIN/FIRA/FOVI", "PASIVO", 3, "2200", "ACREEDORA"),
    ("2300", "Acreedores por Reporto", "PASIVO", 2, "2", "ACREEDORA"),
    ("2301", "Reportos con Títulos Gubernamentales", "PASIVO", 3, "2300", "ACREEDORA"),
    ("2400", "Otras Cuentas por Pagar", "PASIVO", 2, "2", "ACREEDORA"),
    ("2401", "IVA Trasladado por Pagar", "PASIVO", 3, "2400", "ACREEDORA"),
    ("2402", "ISR por Pagar", "PASIVO", 3, "2400", "ACREEDORA"),
    ("2403", "IMSS e INFONAVIT por Pagar", "PASIVO", 3, "2400", "ACREEDORA"),
    ("2404", "Proveedores y Acreedores Diversos", "PASIVO", 3, "2400", "ACREEDORA"),
    ("2405", "Nómina por Pagar", "PASIVO", 3, "2400", "ACREEDORA"),
    ("2500", "Obligaciones Subordinadas", "PASIVO", 2, "2", "ACREEDORA"),
    ("2501", "Obligaciones Subordinadas de Conversión Obligatoria", "PASIVO", 3, "2500", "ACREEDORA"),
    ("3", "CAPITAL", "CAPITAL", 1, None, "ACREEDORA"),
    ("3100", "Capital Social", "CAPITAL", 2, "3", "ACREEDORA"),
    ("3101", "Capital Social Fijo", "CAPITAL", 3, "3100", "ACREEDORA"),
    ("3102", "Prima en Emisión de Acciones", "CAPITAL", 3, "3100", "ACREEDORA"),
    ("3200", "Reservas de Capital", "CAPITAL", 2, "3", "ACREEDORA"),
    ("3201", "Reserva Legal", "CAPITAL", 3, "3200", "ACREEDORA"),
    ("3202", "Otras Reservas Estatutarias", "CAPITAL", 3, "3200", "ACREEDORA"),
    ("3300", "Resultado de Ejercicios Anteriores", "CAPITAL", 2, "3", "ACREEDORA"),
    ("3301", "Resultado de Ejercicios Anteriores", "CAPITAL", 3, "3300", "ACREEDORA"),
    ("3400", "Resultado Neto del Ejercicio", "CAPITAL", 2, "3", "ACREEDORA"),
    ("3401", "Resultado Neto del Ejercicio", "CAPITAL", 3, "3400", "ACREEDORA"),
    ("4", "INGRESOS", "INGRESO", 1, None, "ACREEDORA"),
    ("4100", "Ingresos por Intereses", "INGRESO", 2, "4", "ACREEDORA"),
    ("4101", "Intereses de Cartera Hipotecaria", "INGRESO", 3, "4100", "ACREEDORA"),
    ("4102", "Intereses de Cartera al Consumo", "INGRESO", 3, "4100", "ACREEDORA"),
    ("4103", "Intereses de Cartera PYME", "INGRESO", 3, "4100", "ACREEDORA"),
    ("4104", "Intereses de Inversiones en Valores", "INGRESO", 3, "4100", "ACREEDORA"),
    ("4105", "Intereses de Reportos (activo)", "INGRESO", 3, "4100", "ACREEDORA"),
    ("4200", "Comisiones y Tarifas Cobradas", "INGRESO", 2, "4", "ACREEDORA"),
    ("4201", "Comisiones por Manejo de Cuenta", "INGRESO", 3, "4200", "ACREEDORA"),
    ("4202", "Comisiones por Transferencias SPEI", "INGRESO", 3, "4200", "ACREEDORA"),
    ("4203", "Comisiones por Tarjeta de Crédito", "INGRESO", 3, "4200", "ACREEDORA"),
    ("4204", "Comisiones por Seguros Bancarios", "INGRESO", 3, "4200", "ACREEDORA"),
    ("4300", "Resultado por Intermediación", "INGRESO", 2, "4", "ACREEDORA"),
    ("4301", "Resultado Cambiario", "INGRESO", 3, "4300", "ACREEDORA"),
    ("4302", "Valuación de Instrumentos Financieros", "INGRESO", 3, "4300", "ACREEDORA"),
    ("4303", "Resultado en Venta de Valores", "INGRESO", 3, "4300", "ACREEDORA"),
    ("4400", "Otros Ingresos Operativos", "INGRESO", 2, "4", "ACREEDORA"),
    ("4401", "Recuperaciones de Cartera Castigada", "INGRESO", 3, "4400", "ACREEDORA"),
    ("4402", "Ingresos por Arrendamiento de Inmuebles", "INGRESO", 3, "4400", "ACREEDORA"),
    ("5", "EGRESOS", "EGRESO", 1, None, "DEUDORA"),
    ("5100", "Gastos por Intereses", "EGRESO", 2, "5", "DEUDORA"),
    ("5101", "Intereses por Captación (vista y ahorro)", "EGRESO", 3, "5100", "DEUDORA"),
    ("5102", "Intereses por Depósitos a Plazo", "EGRESO", 3, "5100", "DEUDORA"),
    ("5103", "Intereses por Préstamos Interbancarios", "EGRESO", 3, "5100", "DEUDORA"),
    ("5104", "Intereses por Reportos (pasivo)", "EGRESO", 3, "5100", "DEUDORA"),
    ("5200", "Estimación Preventiva para Riesgos Crediticios (gasto)", "EGRESO", 2, "5", "DEUDORA"),
    ("5201", "Cargo a Resultados - Estimación Preventiva", "EGRESO", 3, "5200", "DEUDORA"),
    ("5300", "Gastos de Administración y Promoción", "EGRESO", 2, "5", "DEUDORA"),
    ("5301", "Sueldos y Salarios", "EGRESO", 3, "5300", "DEUDORA"),
    ("5302", "Cuotas IMSS e INFONAVIT (patrón)", "EGRESO", 3, "5300", "DEUDORA"),
    ("5303", "Rentas y Arrendamientos", "EGRESO", 3, "5300", "DEUDORA"),
    ("5304", "Servicios Tecnológicos y Telecomunicaciones", "EGRESO", 3, "5300", "DEUDORA"),
    ("5305", "Depreciación del Ejercicio", "EGRESO", 3, "5300", "DEUDORA"),
    ("5306", "Publicidad y Mercadotecnia", "EGRESO", 3, "5300", "DEUDORA"),
    ("5307", "Honorarios Legales y Consultores", "EGRESO", 3, "5300", "DEUDORA"),
    ("5308", "Gastos de Viaje y Representación", "EGRESO", 3, "5300", "DEUDORA"),
    ("5400", "Impuestos y PTU", "EGRESO", 2, "5", "DEUDORA"),
    ("5401", "ISR Corriente", "EGRESO", 3, "5400", "DEUDORA"),
    ("5402", "PTU del Ejercicio", "EGRESO", 3, "5400", "DEUDORA"),
]

# ── RH empleados ──────────────────────────────────────────────────────────────

EMPLEADOS = [
    ("EMP-001","Marcos Alejandro Villanueva Ríos","Director General",1,"DIRECCION_GENERAL","SUC-001","2015-03-01",650000,"CONFIANZA"),
    ("EMP-002","Carmen Sofía Ibáñez Morales","Directora Banca Retail",2,"RETAIL","SUC-001","2017-06-15",420000,"CONFIANZA"),
    ("EMP-003","Alejandro Bermúdez Castillo","Director Banca Corporativa",2,"CORPORATIVO","SUC-001","2016-01-10",430000,"CONFIANZA"),
    ("EMP-004","Francisco Javier Leal Nájera","Director Tesorería",2,"TESORERIA","SUC-001","2018-04-20",410000,"CONFIANZA"),
    ("EMP-005","Pablo Medina Vargas","Director TI",2,"TI","SUC-002","2019-09-01",400000,"CONFIANZA"),
    ("EMP-006","Isabel Contreras Rueda","Directora Riesgos",2,"RIESGO","SUC-001","2017-11-01",415000,"CONFIANZA"),
    ("EMP-007","Teresa Ramírez Aguilar","Directora Finanzas",2,"AUDITORIA","SUC-001","2016-07-15",405000,"CONFIANZA"),
    ("EMP-008","Mariana Solís Aguilera","Directora RRHH",2,"RRHH","SUC-001","2018-02-28",360000,"CONFIANZA"),
    ("EMP-009","Sofía Menéndez Arce","Gerente Mesa de Dinero",3,"TESORERIA","SUC-001","2020-01-15",280000,"CONFIANZA"),
    ("EMP-010","Carlos Reyes Gutiérrez","Gerente ALCO",3,"TESORERIA","SUC-001","2019-08-01",270000,"CONFIANZA"),
    ("EMP-011","Roberto Castañeda López","Gerente Contabilidad",3,"AUDITORIA","SUC-001","2018-05-10",250000,"CONFIANZA"),
    ("EMP-012","Andrés Flores Mondragón","Gerente Riesgo Crédito",3,"RIESGO","SUC-001","2020-03-01",260000,"CONFIANZA"),
    ("EMP-013","Diana Pacheco Villalba","Gerente Riesgo Mercado",3,"RIESGO","SUC-001","2021-01-10",255000,"CONFIANZA"),
    ("EMP-014","Claudia Espinoza Méndez","Gerente Fraude y Seguridad",3,"RIESGO","SUC-002","2019-06-15",245000,"CONFIANZA"),
    ("EMP-015","Laura Jiménez Salazar","Gerente Infraestructura TI",3,"TI","SUC-002","2020-08-01",240000,"CONFIANZA"),
    ("EMP-016","Miguel Ángel Herrera Orozco","Gerente Desarrollo SW",3,"TI","SUC-002","2021-03-15",235000,"CONFIANZA"),
    ("EMP-017","Eduardo Ríos Garza","Gerente Captación",3,"RETAIL","SUC-001","2019-04-01",220000,"CONFIANZA"),
    ("EMP-018","Patricia Sánchez Vela","Gerente Crédito Consumo",3,"RETAIL","SUC-001","2020-07-01",215000,"CONFIANZA"),
    ("EMP-019","Roberto Fuentes Pérez","Gerente Sucursales CDMX",3,"RETAIL","SUC-001","2018-11-01",210000,"CONFIANZA"),
    ("EMP-020","Adriana Guzmán Torres","Gerente Sucursales MTY/GDL",3,"RETAIL","SUC-003","2019-02-15",205000,"CONFIANZA"),
    ("EMP-021","Ana Lucía Moreno Castro","Operadora Mesa Derivados",4,"TESORERIA","SUC-001","2022-01-10",150000,"BASE"),
    ("EMP-022","José Luis Garza Salinas","Analista Riesgo Crédito",5,"RIESGO","SUC-001","2022-06-01",120000,"BASE"),
    ("EMP-023","Fernanda Ávila Cruz","Gerente Ciberseguridad",3,"TI","SUC-002","2021-09-01",230000,"CONFIANZA"),
    ("EMP-024","Ricardo Ochoa Blanco","Gerente IA y Datos",3,"TI","SUC-002","2022-01-15",225000,"CONFIANZA"),
    ("EMP-025","Gabriela Núñez Salinas","Gerente Presupuestos",3,"AUDITORIA","SUC-001","2019-10-01",200000,"CONFIANZA"),
    ("EMP-026","Hugo Martínez Becerra","Gerente Rel. Inversionistas",3,"AUDITORIA","SUC-001","2020-05-15",195000,"CONFIANZA"),
    ("EMP-027","Enrique Guerrero Haro","Gerente Nómina",3,"RRHH","SUC-001","2018-09-01",185000,"CONFIANZA"),
    ("EMP-028","Daniela Vázquez Ponce","Gerente Atracción Talento",3,"RRHH","SUC-001","2021-04-01",180000,"CONFIANZA"),
    ("EMP-029","Arturo Pedraza Ibarra","Gerente Cumplimiento CNBV",3,"JURIDICO","SUC-001","2017-08-15",220000,"CONFIANZA"),
    ("EMP-030","Sandra Montes Cervantes","Gerente Legal",3,"JURIDICO","SUC-001","2018-12-01",215000,"CONFIANZA"),
    ("EMP-031","Jorge Villalpando Soto","Analista Tesorería",5,"TESORERIA","SUC-001","2023-02-01",95000,"BASE"),
    ("EMP-032","Mónica Herrera Díaz","Analista Contabilidad",5,"AUDITORIA","SUC-001","2023-03-15",88000,"BASE"),
    ("EMP-033","Iván Torres Méndez","Desarrollador Senior",5,"TI","SUC-002","2022-08-01",135000,"BASE"),
    ("EMP-034","Lucía Ramírez Peña","Desarrolladora Junior",6,"TI","SUC-002","2024-01-15",75000,"BASE"),
    ("EMP-035","Carlos Mendoza Blanco","Especialista Ciberseguridad",5,"TI","SUC-002","2023-06-01",115000,"BASE"),
    ("EMP-036","Verónica Salinas Ruiz","Ejecutiva Cuenta Corporativa",5,"CORPORATIVO","SUC-001","2021-11-01",140000,"BASE"),
    ("EMP-037","Pablo Arredondo Cruz","Ejecutivo PYME",5,"CORPORATIVO","SUC-003","2022-04-15",110000,"BASE"),
    ("EMP-038","Teresa Gutiérrez Vega","Cajera Principal",6,"RETAIL","SUC-001","2019-07-01",65000,"BASE"),
    ("EMP-039","Ramón Espinoza Morales","Asesor Financiero",6,"RETAIL","SUC-002","2020-10-15",72000,"BASE"),
    ("EMP-040","Norma Castillo Ibáñez","Promotora de Crédito",6,"RETAIL","SUC-004","2021-05-01",68000,"BASE"),
    ("EMP-041","Ernesto Pacheco Leal","Analista Fraude",5,"RIESGO","SUC-002","2023-01-10",102000,"BASE"),
    ("EMP-042","Sofía Reyes Garza","Científica de Datos",5,"TI","SUC-002","2023-09-15",128000,"BASE"),
    ("EMP-043","Mario Fuentes Aguilar","Administrador Sistemas",5,"TI","SUC-002","2022-11-01",105000,"BASE"),
    ("EMP-044","Elena Vega Mendoza","Coordinadora Capacitación",5,"RRHH","SUC-001","2021-08-01",95000,"BASE"),
    ("EMP-045","Raúl Bermúdez Soto","Operador ATM / Efectivo",7,"RETAIL","SUC-003","2020-03-15",58000,"BASE"),
    ("EMP-046","Diana Cruz Medina","Ejecutiva Banca Privada",4,"CORPORATIVO","SUC-001","2020-06-01",180000,"CONFIANZA"),
    ("EMP-047","Alberto Vargas Flores","Auditor Interno Senior",4,"AUDITORIA","SUC-001","2019-01-15",165000,"CONFIANZA"),
    ("EMP-048","Claudia Nava Ortiz","Abogada Corporativa",5,"JURIDICO","SUC-001","2022-07-01",125000,"BASE"),
    ("EMP-049","Fernando Medina Ríos","Analista Regulatorio CNBV",5,"JURIDICO","SUC-001","2023-04-01",108000,"BASE"),
    ("EMP-050","Karina Solís Peña","Asistente Dirección General",6,"DIRECCION_GENERAL","SUC-001","2021-02-15",82000,"BASE"),
]

CENTROS_COSTO = [
    ("CC-001","Banca Retail CDMX","RETAIL","Carmen Sofía Ibáñez Morales",650000000,498000000,425),
    ("CC-002","Banca Retail MTY/GDL","RETAIL","Adriana Guzmán Torres",350000000,268000000,290),
    ("CC-003","Banca Corporativa","CORPORATIVO","Alejandro Bermúdez Castillo",210000000,162000000,135),
    ("CC-004","Tesorería y Mercados","TESORERIA","Francisco Javier Leal Nájera",95000000,72000000,45),
    ("CC-005","Tecnología e Innovación","TI","Pablo Medina Vargas",620000000,478000000,325),
    ("CC-006","Riesgos y Fraude","RIESGO","Isabel Contreras Rueda",180000000,138000000,125),
    ("CC-007","Recursos Humanos","RRHH","Mariana Solís Aguilera",75000000,58000000,55),
    ("CC-008","Finanzas, Auditoría y Juridico","AUDITORIA","Teresa Ramírez Aguilar",120000000,92000000,85),
]

INSTRUMENTOS_TRY = [
    ("INS-001","CETES","BI260521",28,9.01,500000000,498250000,99.65,"2026-04-23","2026-05-21","NEGOCIACION"),
    ("INS-002","CETES","BI260716",91,9.05,300000000,293850000,97.95,"2026-04-16","2026-07-16","NEGOCIACION"),
    ("INS-003","CETES","BI261015",182,9.08,200000000,191200000,95.60,"2026-04-16","2026-10-15","DISPONIBLE_VENTA"),
    ("INS-004","CETES","BI270415",364,9.12,150000000,138150000,92.10,"2026-04-15","2027-04-15","DISPONIBLE_VENTA"),
    ("INS-005","BONM","M 8.5 181127",3650,8.95,1000000000,1028500000,102.85,"2024-11-28","2027-11-18","DISPONIBLE_VENTA"),
    ("INS-006","BONM","M 7.75 141127",4380,8.90,800000000,812000000,101.50,"2023-11-14","2027-11-14","DISPONIBLE_VENTA"),
    ("INS-007","BONM","M 8.0 290528",5475,8.85,500000000,517500000,103.50,"2025-05-29","2028-05-29","VENCIMIENTO"),
    ("INS-008","UDIBONO","SI 3.5 181135",3285,3.85,2000000000,1960000000,98.00,"2025-12-19","2035-12-18","VENCIMIENTO"),
    ("INS-009","BONDESD","LD 26-06-30",1095,9.10,600000000,594000000,99.00,"2025-06-27","2026-06-26","NEGOCIACION"),
    ("INS-010","BONDESD","LD 25-12-30",1825,9.05,400000000,392000000,98.00,"2025-12-26","2026-12-25","NEGOCIACION"),
]

OPERACIONES_MESA = [
    ("OP-001","REPO","BBVA México",500000000,9.05,"2026-05-12","2026-05-19","ACTIVA","Jorge Villalpando"),
    ("OP-002","REPO","Santander México",300000000,9.03,"2026-05-13","2026-05-20","ACTIVA","Ana Lucía Moreno"),
    ("OP-003","PRESTAMO_IB","Banamex",1000000000,9.10,"2026-05-14","2026-05-15","ACTIVA","Sofía Menéndez"),
    ("OP-004","COMPRA_CETES","Banxico (mercado primario)",200000000,9.01,"2026-05-13","2026-06-10","ACTIVA","Jorge Villalpando"),
    ("OP-005","VENTA_BONOS","HSBC México",150000000,8.92,"2026-05-10","2026-05-10","VENCIDA","Ana Lucía Moreno"),
    ("OP-006","REPO","Scotiabank",250000000,9.02,"2026-05-08","2026-05-15","ACTIVA","Sofía Menéndez"),
    ("OP-007","PRESTAMO_IB","Inbursa",800000000,9.08,"2026-05-01","2026-05-08","VENCIDA","Jorge Villalpando"),
    ("OP-008","COMPRA_CETES","Banxico (mercado primario)",350000000,9.00,"2026-04-30","2026-05-28","ACTIVA","Ana Lucía Moreno"),
    ("OP-009","REPO","Banbajío",120000000,9.04,"2026-05-14","2026-05-21","ACTIVA","Sofía Menéndez"),
    ("OP-010","VENTA_BONOS","Afore XXI Banorte",500000000,8.88,"2026-05-05","2026-05-05","VENCIDA","Ana Lucía Moreno"),
    ("OP-011","PRESTAMO_IB","Banorte (otorgado a CIBanco)",400000000,9.12,"2026-05-13","2026-05-20","ACTIVA","Sofía Menéndez"),
    ("OP-012","COMPRA_CETES","Accival Casa de Bolsa",180000000,9.03,"2026-05-12","2026-08-10","ACTIVA","Jorge Villalpando"),
]

CREDITOS = [
    ("CRD-001","CLI-001","HIPOTECARIO",2500000,2180000,9.5,240,18250,"2022-03-15","2042-03-15",0,"VIGENTE"),
    ("CRD-002","CLI-002","PERSONAL",150000,62000,18.0,36,5550,"2024-05-01","2027-05-01",0,"VIGENTE"),
    ("CRD-003","CLI-003","PYME",800000,650000,12.5,60,18020,"2022-11-10","2027-11-10",0,"VIGENTE"),
    ("CRD-004","CLI-003","PYME",500000,500000,13.0,48,13530,"2026-01-15","2030-01-15",0,"VIGENTE"),
    ("CRD-005","CLI-004","HIPOTECARIO",3800000,3720000,8.9,300,33820,"2025-08-01","2050-08-01",0,"VIGENTE"),
    ("CRD-006","CLI-005","PERSONAL",80000,28000,22.0,24,4210,"2024-05-20","2026-05-20",15,"VENCIDO"),
    ("CRD-007","CLI-006","AUTOMOTRIZ",320000,195000,11.0,48,8260,"2023-04-01","2027-04-01",0,"VIGENTE"),
    ("CRD-008","CLI-007","PYME",1200000,980000,11.5,60,26470,"2022-09-15","2027-09-15",0,"VIGENTE"),
    ("CRD-009","CLI-008","PERSONAL",50000,50000,24.0,36,1950,"2026-03-01","2029-03-01",0,"VIGENTE"),
    ("CRD-010","CLI-009","HIPOTECARIO",5000000,4850000,9.0,360,45200,"2025-10-01","2055-10-01",0,"VIGENTE"),
    ("CRD-011","CLI-010","PERSONAL",200000,145000,16.5,48,5790,"2023-08-01","2027-08-01",0,"VIGENTE"),
    ("CRD-012","CLI-011","PYME",2000000,1800000,10.5,72,37520,"2021-06-15","2027-06-15",0,"VIGENTE"),
    ("CRD-013","CLI-012","AUTOMOTRIZ",180000,42000,13.5,36,6120,"2023-05-01","2026-05-01",45,"VENCIDO"),
    ("CRD-014","CLI-013","HIPOTECARIO",4200000,4100000,8.75,300,37350,"2025-12-01","2050-12-01",0,"VIGENTE"),
    ("CRD-015","CLI-014","PERSONAL",100000,65000,20.0,36,3730,"2024-05-01","2027-05-01",0,"VIGENTE"),
    ("CRD-016","CLI-015","PYME",600000,320000,12.0,48,15840,"2023-05-10","2027-05-10",0,"VIGENTE"),
    ("CRD-017","CLI-016","PERSONAL",40000,12000,25.0,24,2110,"2025-05-15","2027-05-15",0,"VIGENTE"),
    ("CRD-018","CLI-017","PYME",900000,220000,11.5,60,19840,"2021-05-01","2026-05-01",120,"CASTIGADO"),
    ("CRD-019","CLI-018","AUTOMOTRIZ",250000,198000,12.0,60,5560,"2024-05-01","2029-05-01",0,"VIGENTE"),
    ("CRD-020","CLI-019","PYME",5000000,4200000,10.0,84,83900,"2023-05-01","2030-05-01",0,"VIGENTE"),
    ("CRD-021","CLI-019","PYME",3000000,2900000,10.5,60,64410,"2025-05-01","2030-05-01",0,"VIGENTE"),
    ("CRD-022","CLI-020","PYME",8000000,7500000,9.5,120,104200,"2023-11-01","2033-11-01",0,"VIGENTE"),
    ("CRD-023","CLI-020","HIPOTECARIO",6000000,5900000,8.5,300,52620,"2025-11-01","2050-11-01",0,"VIGENTE"),
    ("CRD-024","CLI-001","AUTOMOTRIZ",550000,385000,10.5,60,11870,"2023-05-01","2028-05-01",0,"VIGENTE"),
    ("CRD-025","CLI-004","PERSONAL",300000,280000,15.0,36,10400,"2025-11-01","2028-11-01",0,"VIGENTE"),
]

CALIFICACIONES = [
    ("CAL-001","CRD-001","A",0.5,45.0,4905.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-002","CRD-002","B1",3.0,45.0,837.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-003","CRD-003","A",1.0,45.0,2925.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-004","CRD-004","A",0.8,45.0,1800.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-005","CRD-005","A",0.4,45.0,6696.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-006","CRD-006","C2",35.0,60.0,5880.0,"2026-04-30","Analista Andrés Flores"),
    ("CAL-007","CRD-007","A",1.5,45.0,1317.5,"2026-04-30","Sistema IFRS9"),
    ("CAL-008","CRD-008","A",0.9,45.0,3969.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-009","CRD-009","B1",2.0,45.0,450.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-010","CRD-010","A",0.3,45.0,6547.5,"2026-04-30","Sistema IFRS9"),
    ("CAL-011","CRD-011","A",1.2,45.0,783.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-012","CRD-012","A",0.7,45.0,5670.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-013","CRD-013","D",60.0,65.0,16380.0,"2026-04-30","Analista Andrés Flores"),
    ("CAL-014","CRD-014","A",0.4,45.0,7380.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-015","CRD-015","B1",2.5,45.0,731.25,"2026-04-30","Sistema IFRS9"),
    ("CAL-016","CRD-016","A",1.0,45.0,1440.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-017","CRD-017","B2",8.0,50.0,480.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-018","CRD-018","E",100.0,75.0,165000.0,"2026-04-30","Analista Andrés Flores"),
    ("CAL-019","CRD-019","A",1.5,45.0,1336.5,"2026-04-30","Sistema IFRS9"),
    ("CAL-020","CRD-020","A",0.6,45.0,11340.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-021","CRD-021","A",0.7,45.0,9135.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-022","CRD-022","A",0.5,45.0,16875.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-023","CRD-023","A",0.4,45.0,10620.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-024","CRD-024","A",1.2,45.0,2079.0,"2026-04-30","Sistema IFRS9"),
    ("CAL-025","CRD-025","B1",2.0,45.0,2520.0,"2026-04-30","Sistema IFRS9"),
]

ACTIVOS = [
    ("AFX-001","SUCURSAL","Sucursal Centro Histórico - Piso 1","Madero 12 PB","Ciudad de México","2010-03-01",8500000,4800000,40,"OPERATIVO"),
    ("AFX-002","SUCURSAL","Sucursal Santa Fe - Local 201","Av. Santa Fe 505","Ciudad de México","2015-08-15",6200000,4030000,40,"OPERATIVO"),
    ("AFX-003","SUCURSAL","Sucursal San Pedro Garza García","Av. Humberto Lobo 555","San Pedro Garza García","2012-06-01",5800000,3190000,40,"OPERATIVO"),
    ("AFX-004","SUCURSAL","Sucursal Chapultepec GDL","Av. Chapultepec 15","Guadalajara","2013-11-01",5200000,2730000,40,"OPERATIVO"),
    ("AFX-005","SUCURSAL","Sucursal Monterrey Centro","Av. Constitución 300","Monterrey","2011-04-15",4900000,2450000,40,"OPERATIVO"),
    ("AFX-006","ATM","ATM Aeropuerto CDMX Terminal 1","AICM T1 Nivel Salidas","Ciudad de México","2020-01-15",180000,120600,10,"OPERATIVO"),
    ("AFX-007","ATM","ATM Aeropuerto CDMX Terminal 2","AICM T2 Nivel Llegadas","Ciudad de México","2020-01-15",180000,120600,10,"OPERATIVO"),
    ("AFX-008","ATM","ATM Perisur Centro Comercial","Perisur P1 Zona Bancaria","Ciudad de México","2019-06-01",165000,104950,10,"OPERATIVO"),
    ("AFX-009","ATM","ATM Santa Fe Plaza Mayor","P. Mayor L-B12","Ciudad de México","2021-03-01",170000,127500,10,"OPERATIVO"),
    ("AFX-010","ATM","ATM Liverpool Pedregal","Liverpool Pedregal PB","Ciudad de México","2018-09-01",160000,88000,10,"OPERATIVO"),
    ("AFX-011","ATM","ATM OXXO Insurgentes Sur","OXXO #4521 Insurgentes","Ciudad de México","2022-05-01",145000,120833,10,"OPERATIVO"),
    ("AFX-012","ATM","ATM Walmart Santa Fe","Walmart Santa Fe Caja 40","Ciudad de México","2021-11-01",160000,117333,10,"OPERATIVO"),
    ("AFX-013","ATM","ATM Forum Monterrey","Forum MTY Planta Alta","Monterrey","2020-08-01",168000,109200,10,"OPERATIVO"),
    ("AFX-014","ATM","ATM Gran Plaza GDL","Gran Plaza GDL Nivel 1","Guadalajara","2019-12-01",162000,94500,10,"OPERATIVO"),
    ("AFX-015","ATM","ATM Galerias Monterrey","Galerías MTY Zona Central","Monterrey","2021-07-15",165000,123750,10,"OPERATIVO"),
    ("AFX-016","ATM","ATM Farmacia Guadalajara GDL","Farm. Gdl #0091","Guadalajara","2023-02-01",155000,142083,10,"OPERATIVO"),
    ("AFX-017","ATM","ATM Hospital Zambrano MTY","H. Zambrano Hellion Lobby","Monterrey","2022-10-01",170000,142083,10,"MANTENIMIENTO"),
    ("AFX-018","ATM","ATM Metro Insurgentes CDMX","Metro Insurgentes Andén 2","Ciudad de México","2018-04-01",158000,71100,10,"OPERATIVO"),
    ("AFX-019","ATM","ATM Universidad UNAM","UNAM Rectoría Planta Baja","Ciudad de México","2017-09-01",150000,52500,10,"OPERATIVO"),
    ("AFX-020","ATM","ATM Aeropuerto MTY Nacional","AIT T1 Zona Check-In","Monterrey","2021-05-01",172000,129000,10,"OPERATIVO"),
    ("AFX-021","ATM","ATM Costco Santa Fe","Costco SF Exit","Ciudad de México","2022-08-01",165000,130417,10,"OPERATIVO"),
    ("AFX-022","ATM","ATM Cinépolis Galerias","Cinépolis GVA Lobby","Ciudad de México","2023-05-01",155000,148208,10,"OPERATIVO"),
    ("AFX-023","ATM","ATM Soriana Constitución MTY","Soriana MTY #34","Monterrey","2020-03-15",160000,104000,10,"OPERATIVO"),
    ("AFX-024","ATM","ATM Office Depot Perisur","OD Perisur PB","Ciudad de México","2024-01-15",162000,161325,10,"OPERATIVO"),
    ("AFX-025","ATM","ATM Sam's Club Cuautitlán","Sam's CUT Caja","Ciudad de México","2023-09-01",158000,149383,10,"OPERATIVO"),
    ("AFX-026","ATM","ATM UDEM Monterrey","UDEM Campus Sur","Monterrey","2022-04-01",163000,132438,10,"OPERATIVO"),
    ("AFX-027","ATM","ATM Plaza Patria GDL","P. Patria Nivel 2","Guadalajara","2021-10-01",165000,123750,10,"OPERATIVO"),
    ("AFX-028","ATM","ATM Liverpool GDL Andares","Liverpool Andares PA","Guadalajara","2023-01-15",168000,161700,10,"OPERATIVO"),
    ("AFX-029","ATM","ATM ITESO GDL","ITESO Campus","Guadalajara","2024-03-01",155000,155000,10,"OPERATIVO"),
    ("AFX-030","ATM","ATM Walmart Av. López MTY","Walmart LM #88","Monterrey","2020-11-01",160000,106667,10,"BAJA"),
    ("AFX-031","SERVIDOR","Servidor IBM Power10 - Core Bancario Principal","DataCenter CDMX Rack-A1","Ciudad de México","2022-01-15",12500000,9375000,8,"OPERATIVO"),
    ("AFX-032","SERVIDOR","Servidor IBM Power10 - Core Bancario Respaldo","DataCenter CDMX Rack-A2","Ciudad de México","2022-01-15",12500000,9375000,8,"OPERATIVO"),
    ("AFX-033","SERVIDOR","Servidor Dell PowerEdge - SPEI Gateway","DataCenter CDMX Rack-B1","Ciudad de México","2023-03-01",4800000,3960000,5,"OPERATIVO"),
    ("AFX-034","SERVIDOR","Servidor Dell PowerEdge - Base de Datos Oracle","DataCenter CDMX Rack-B2","Ciudad de México","2021-06-15",6200000,3875000,8,"OPERATIVO"),
    ("AFX-035","SERVIDOR","Servidor HPE Proliant - Middleware","DataCenter CDMX Rack-C1","Ciudad de México","2023-08-01",3500000,3062500,5,"OPERATIVO"),
    ("AFX-036","SERVIDOR","Servidor HPE Proliant - Seguridad Perimetral","DataCenter MTY Rack-D1","Monterrey","2022-09-01",3200000,2266667,5,"OPERATIVO"),
    ("AFX-037","SERVIDOR","Servidor Pure Storage FlashArray - Almacenamiento","DataCenter CDMX Rack-E1","Ciudad de México","2024-02-01",9800000,9391667,6,"OPERATIVO"),
    ("AFX-038","SERVIDOR","Servidor VMware vSAN - Virtualización","DataCenter CDMX Rack-F1","Ciudad de México","2021-11-15",5500000,3437500,8,"OPERATIVO"),
    ("AFX-039","SERVIDOR","Servidor Juniper - Red Core","DataCenter CDMX Rack-G1","Ciudad de México","2023-05-15",2800000,2450000,5,"OPERATIVO"),
    ("AFX-040","SERVIDOR","Servidor Cisco UCS - ATM Concentrator","DataCenter MTY Rack-H1","Monterrey","2022-07-01",2200000,1650000,5,"OPERATIVO"),
    ("AFX-041","SERVIDOR","Servidor Lenovo ThinkSystem - Analytics","DataCenter CDMX Rack-I1","Ciudad de México","2024-04-15",4200000,4200000,6,"OPERATIVO"),
    ("AFX-042","SERVIDOR","Servidor IBM - Backup y Recuperación","DataCenter GDL Rack-A1","Guadalajara","2023-10-01",3800000,3483333,6,"OPERATIVO"),
    ("AFX-043","SERVIDOR","Servidor Dell - Ambiente QA/Testing","DataCenter CDMX Rack-J1","Ciudad de México","2021-03-01",1800000,945000,8,"OPERATIVO"),
    ("AFX-044","SERVIDOR","Servidor HPE - Monitoreo y Observabilidad","DataCenter CDMX Rack-K1","Ciudad de México","2024-01-10",2500000,2430556,5,"OPERATIVO"),
    ("AFX-045","SERVIDOR","Servidor Cisco - Firewall NextGen","DataCenter CDMX Rack-L1","Ciudad de México","2023-07-01",3100000,2841667,5,"MANTENIMIENTO"),
    ("AFX-046","SERVIDOR","Servidor Dell - Dev/Staging","DataCenter CDMX Rack-M1","Ciudad de México","2022-05-01",1200000,800000,5,"OPERATIVO"),
    ("AFX-047","SERVIDOR","Servidor HPE - Correo Corporativo","DataCenter MTY Rack-B1","Monterrey","2020-08-15",1500000,625000,8,"OPERATIVO"),
    ("AFX-048","SERVIDOR","Servidor IBM - Reporteo Regulatorio","DataCenter CDMX Rack-N1","Ciudad de México","2023-12-01",2900000,2658333,5,"OPERATIVO"),
    ("AFX-049","SERVIDOR","Servidor Lenovo - ERP SAP","DataCenter CDMX Rack-O1","Ciudad de México","2021-09-01",8500000,5312500,8,"OPERATIVO"),
    ("AFX-050","SERVIDOR","Servidor HPE - Contingencia DR Site","DataCenter GDL Rack-B1","Guadalajara","2022-11-15",4500000,3375000,6,"OPERATIVO"),
    ("AFX-051","BLINDADO","Vehículo Blindado Kenworth T370 #1","Base Operativa CDMX Norte","Ciudad de México","2021-06-01",1850000,1080833,10,"OPERATIVO"),
    ("AFX-052","BLINDADO","Vehículo Blindado Kenworth T370 #2","Base Operativa CDMX Sur","Ciudad de México","2021-06-01",1850000,1080833,10,"OPERATIVO"),
    ("AFX-053","BLINDADO","Vehículo Blindado Ford F-350 #3","Base Operativa MTY","Monterrey","2020-03-15",980000,490000,10,"OPERATIVO"),
    ("AFX-054","BLINDADO","Vehículo Blindado Ford F-350 #4","Base Operativa GDL","Guadalajara","2019-11-01",980000,392000,10,"OPERATIVO"),
    ("AFX-055","BLINDADO","Vehículo Blindado RAM 3500 #5 (baja)","Desincorporado","Ciudad de México","2015-04-01",850000,0,10,"BAJA"),
    ("AFX-056","MOBILIARIO","Mobiliario Ejecutivo Sucursal Centro","Sucursal Centro Histórico","Ciudad de México","2018-06-01",450000,105000,15,"OPERATIVO"),
    ("AFX-057","MOBILIARIO","Equipamiento Cajas Teller Sucursal SF","Sucursal Santa Fe","Ciudad de México","2020-09-15",380000,152000,10,"OPERATIVO"),
    ("AFX-058","MOBILIARIO","Bóveda Acero Diebold Centro","Sucursal Centro Histórico","Ciudad de México","2010-03-01",2200000,440000,30,"OPERATIVO"),
    ("AFX-059","MOBILIARIO","Bóveda Acero Diebold MTY","Sucursal Monterrey Centro","Monterrey","2011-04-15",2100000,378000,30,"OPERATIVO"),
    ("AFX-060","MOBILIARIO","Generador Eléctrico DataCenter CDMX","DataCenter CDMX","Ciudad de México","2022-03-01",1200000,900000,15,"OPERATIVO"),
]

ALERTAS_FRAUDE = [
    ("ALR-001","0001000008",dt(45),"MONTO_INUSUAL",78.5,15000,"Depósito en efectivo inusual para el perfil","CERRADA","Ernesto Pacheco","Operación legítima verificada con cliente"),
    ("ALR-002","0001000003",dt(38),"VELOCIDAD",65.0,8500,"3 retiros ATM en 90 minutos en diferentes colonias","FALSO_POSITIVO","Ernesto Pacheco","Cliente viajaba por la ciudad, verificado"),
    ("ALR-003","0001000012",dt(31),"PATRON_GEOGRAFICO",82.3,3100,"Compra en línea desde IP extranjera (Colombia)","INVESTIGANDO","Ernesto Pacheco",None),
    ("ALR-004","0001000024",dt(28),"MONTO_INUSUAL",91.0,2800,"Transferencia SPEI de monto cercano a límite de reporte","ABIERTA",None,None),
    ("ALR-005","0001000006",dt(22),"VELOCIDAD",73.0,25000,"Múltiples transferencias en menos de 10 minutos","CERRADA","Ernesto Pacheco","Autorizado por el cliente para pago de proveedores"),
    ("ALR-006","0001000015",dt(18),"LISTA_NEGRA",95.5,12000,"Receptor en lista de entidades monitoreadas OFAC","INVESTIGANDO","Ernesto Pacheco",None),
    ("ALR-007","0001000001",dt(15),"PATRON_GEOGRAFICO",69.0,15000,"Consumo tarjeta débito en otro país sin aviso de viaje","CERRADA","Ernesto Pacheco","Cliente confirmó uso legítimo, estaba de viaje"),
    ("ALR-008","0001000018",dt(12),"MONTO_INUSUAL",84.2,7200,"Retiro máximo diario por 5 días consecutivos","INVESTIGANDO","Ernesto Pacheco",None),
    ("ALR-009","0001000009",dt(10),"VELOCIDAD",77.8,9800,"Transacciones fraccionadas (structuring) detectadas","ABIERTA",None,None),
    ("ALR-010","0001000027",dt(8),"MONTO_INUSUAL",88.0,250000,"Transferencia empresarial a cuenta sin historial previo","INVESTIGANDO","Ernesto Pacheco",None),
    ("ALR-011","0001000003",dt(7),"LISTA_NEGRA",62.0,3500,"Beneficiario relacionado con alerta SITI","ABIERTA",None,None),
    ("ALR-012","0001000021",dt(5),"PATRON_GEOGRAFICO",71.5,6700,"Operación desde dispositivo nunca antes registrado","ABIERTA",None,None),
    ("ALR-013","0001000008",dt(4),"MONTO_INUSUAL",55.0,3800,"Cambio en patrón de gastos (categoría nueva)","FALSO_POSITIVO","Ernesto Pacheco","Cambio de hábitos verificado"),
    ("ALR-014","0001000029",dt(3),"VELOCIDAD",80.1,380000,"30 transacciones salientes en 2 horas","INVESTIGANDO","Ernesto Pacheco",None),
    ("ALR-015","0001000004",dt(2),"LISTA_NEGRA",93.2,42000,"Contraparte SPEI en lista negra SAT","ABIERTA",None,None),
    ("ALR-016","0001000013",dt(1),"MONTO_INUSUAL",66.8,95000,"Depósito en efectivo no justificado","ABIERTA",None,None),
    ("ALR-017","0001000022",dt(1),"PATRON_GEOGRAFICO",75.3,28000,"Acceso desde VPN en jurisdicción de alto riesgo","ABIERTA",None,None),
    ("ALR-018","0001000026",dt(0),"VELOCIDAD",69.0,7200,"Carga de nómina a 50 cuentas en 3 minutos","INVESTIGANDO","Ernesto Pacheco",None),
]

CONTRAPARTES = [
    ("BBVA México","BANCO","AA",5000000000,3200000000,1800000000,"2026-01-15","2027-01-15"),
    ("Citibanamex","BANCO","AA-",4000000000,2800000000,1200000000,"2026-01-15","2027-01-15"),
    ("Santander México","BANCO","A+",3500000000,1500000000,2000000000,"2026-01-15","2027-01-15"),
    ("HSBC México","BANCO","A",2500000000,980000000,1520000000,"2026-01-15","2027-01-15"),
    ("Scotiabank México","BANCO","A",2000000000,1200000000,800000000,"2026-01-15","2027-01-15"),
    ("Inbursa","BANCO","A-",1500000000,800000000,700000000,"2026-01-15","2027-01-15"),
    ("Banbajío","BANCO","BBB+",800000000,400000000,400000000,"2026-01-15","2027-01-15"),
    ("CIBanco","BANCO","BBB",500000000,380000000,120000000,"2026-03-01","2027-03-01"),
    ("Gobierno Federal (SHCP)","GOBIERNO","AAA",50000000000,32000000000,18000000000,"2026-01-15","2031-01-15"),
    ("Banxico","GOBIERNO","AAA",30000000000,15000000000,15000000000,"2026-01-15","2036-01-15"),
    ("NAFIN","GOBIERNO","AAA",5000000000,2100000000,2900000000,"2026-01-15","2027-01-15"),
    ("FIRA","GOBIERNO","AA+",2000000000,850000000,1150000000,"2026-01-15","2027-01-15"),
    ("Accival Casa de Bolsa","EMPRESA","A",1000000000,620000000,380000000,"2026-01-15","2027-01-15"),
    ("Afore XXI Banorte","EMPRESA","AA",8000000000,5200000000,2800000000,"2026-01-15","2028-01-15"),
    ("Afore Sura México","EMPRESA","A+",3000000000,1800000000,1200000000,"2026-01-15","2027-01-15"),
    ("JPMorgan Chase (NY)","BANCO","AA+",2000000000,0,2000000000,"2026-01-15","2027-01-15"),
    ("Citibank N.A. (NY)","BANCO","AA",1500000000,0,1500000000,"2026-01-15","2027-01-15"),
]


def seed_internal():
    InternalBase.metadata.drop_all(bind=internal_engine)
    InternalBase.metadata.create_all(bind=internal_engine)
    session = InternalSessionLocal()

    try:
        # GL Catálogo
        for row in GL_CATALOGO:
            session.add(GlCatalogoCuentas(
                codigo=row[0], nombre=row[1], tipo=row[2], nivel=row[3],
                codigo_padre=row[4], naturaleza=row[5], activa=True,
            ))

        # GL Asientos + Partidas (500 asientos)
        usuarios_gl = ["rcasta01", "mnunez01", "hmart01", "icontrera01", "treyes01"]
        centros = ["CC-001","CC-002","CC-003","CC-004","CC-005","CC-006","CC-007","CC-008"]
        pares_cuentas = [
            ("1103","2101"),("4101","1401"),("5301","2405"),("5303","2404"),
            ("1201","2301"),("4201","2101"),("5102","2201"),("1102","1103"),
            ("4102","1402"),("5201","1450"),("5305","1612"),("4104","1201"),
        ]
        for i in range(500):
            asiento_id = f"AST-{2026000+i}"
            days_ago = random.randint(0, 89)
            cargo_cuenta, abono_cuenta = random.choice(pares_cuentas)
            monto = round(random.uniform(50000, 5000000), 2)
            session.add(GlAsiento(
                id=asiento_id,
                fecha=dt(days_ago),
                concepto=random.choice([
                    "Registro de ingresos por intereses cartera",
                    "Pago de nómina quincenal",
                    "Depreciación mensual activos fijos",
                    "Provisión estimación preventiva IFRS9",
                    "Captación depósitos a la vista",
                    "Liquidación de inversiones CETES",
                    "Comisiones por servicios bancarios",
                    "Pago de préstamo interbancario overnight",
                    "Registro operación SPEI masiva",
                    "Ajuste por valuación instrumentos",
                ]),
                usuario_captura=random.choice(usuarios_gl),
                centro_costo=random.choice(centros),
                status=random.choice(["APLICADO"]*9 + ["PENDIENTE"]),
                referencia_sistema=None,
            ))
            session.add(GlPartida(
                id=f"PRT-{2026000+i}-D",
                asiento_id=asiento_id, cuenta_codigo=cargo_cuenta,
                tipo="CARGO", monto=monto, centro_costo=random.choice(centros),
            ))
            session.add(GlPartida(
                id=f"PRT-{2026000+i}-A",
                asiento_id=asiento_id, cuenta_codigo=abono_cuenta,
                tipo="ABONO", monto=monto, centro_costo=random.choice(centros),
            ))

        # Tesorería — Posición diaria (90 días)
        for i in range(90):
            fecha = (TODAY - timedelta(days=89-i)).isoformat()
            saldo_banxico = round(random.uniform(8e9, 15e9), 2)
            overnight = round(random.uniform(2e9, 6e9), 2)
            ratio = round(random.uniform(105, 145), 2)
            session.add(TryPosicionDiaria(
                fecha=fecha,
                saldo_banxico=saldo_banxico,
                disponible_spei=round(saldo_banxico * 0.35, 2),
                inversion_overnight=overnight,
                creditos_interbancarios_recibidos=round(random.uniform(1e9, 4e9), 2),
                creditos_interbancarios_otorgados=round(random.uniform(0.5e9, 2e9), 2),
                ratio_liquidez_pct=ratio,
                alerta_liquidez=ratio < 110,
            ))

        for row in INSTRUMENTOS_TRY:
            session.add(TryInstrumento(
                id=row[0], emisora=row[1], serie=row[2], plazo_dias=row[3],
                tasa_rendimiento=row[4], valor_nominal=row[5], valor_mercado=row[6],
                precio_sucio=row[7], fecha_compra=row[8], fecha_vencimiento=row[9],
                clasificacion=row[10],
            ))

        for row in OPERACIONES_MESA:
            session.add(TryOperacionMesa(
                id=row[0], tipo=row[1], contraparte=row[2], monto=row[3],
                tasa=row[4], fecha_inicio=row[5], fecha_vencimiento=row[6],
                status=row[7], operador=row[8],
            ))

        # Crédito
        for row in CREDITOS:
            session.add(CrdCredito(
                id=row[0], cliente_id=row[1], tipo=row[2], monto_original=row[3],
                saldo_insoluto=row[4], tasa_anual=row[5], plazo_meses=row[6],
                pago_mensual=row[7], fecha_apertura=row[8], fecha_vencimiento=row[9],
                dias_vencido=row[10], status=row[11],
            ))

        # Amortizaciones (~300 — 12 pagos por crédito para primeros 25)
        for crd in CREDITOS:
            credito_id = crd[0]
            pago_mensual = crd[7]
            for num in range(1, 13):
                pagado = num <= 8
                session.add(CrdAmortizacion(
                    id=str(uuid.uuid4()),
                    credito_id=credito_id,
                    numero_pago=num,
                    fecha_pago=f"2026-{num:02d}-15" if num <= 12 else f"2027-{num-12:02d}-15",
                    capital=round(pago_mensual * 0.6, 2),
                    intereses=round(pago_mensual * 0.38, 2),
                    iva_intereses=round(pago_mensual * 0.038 * 0.16, 2),
                    total=round(pago_mensual, 2),
                    pagado=pagado,
                    fecha_pago_real=f"2026-{num:02d}-14" if pagado else None,
                    monto_pagado=round(pago_mensual, 2) if pagado else None,
                ))

        for row in CALIFICACIONES:
            session.add(CrdCalificacion(
                id=row[0], credito_id=row[1], bucket_ifrs9=row[2],
                probabilidad_incumplimiento=row[3], perdida_dado_incumplimiento=row[4],
                provision_requerida=row[5], fecha_calificacion=row[6], calificador=row[7],
            ))

        # RRHH
        for row in EMPLEADOS:
            session.add(RhEmpleado(
                id=row[0], nombre=row[1], puesto=row[2], nivel=row[3],
                area=row[4], sucursal_id=row[5], fecha_ingreso=row[6],
                sueldo_bruto=row[7], status="ACTIVO", tipo_contrato=row[8],
            ))

        # Nómina — 6 meses
        periodos = ["2025-12","2026-01","2026-02","2026-03","2026-04","2026-05"]
        for emp in EMPLEADOS:
            bruto = emp[7]
            for periodo in periodos:
                isr = round(bruto * 0.30, 2)
                imss = round(bruto * 0.0245, 2)
                infonavit = round(bruto * 0.05, 2)
                neto = round(bruto - isr - imss - infonavit, 2)
                session.add(RhNominaMensual(
                    id=str(uuid.uuid4()),
                    empleado_id=emp[0], periodo=periodo,
                    sueldo_bruto=bruto, isr=isr, imss=imss,
                    infonavit=infonavit, neto=neto,
                    fecha_pago=f"{periodo}-15",
                    banco_deposito="BANORTE",
                ))

        for row in CENTROS_COSTO:
            session.add(RhCentroCosto(
                id=row[0], nombre=row[1], area=row[2], director=row[3],
                presupuesto_anual=row[4], gasto_acumulado=row[5], empleados_activos=row[6],
            ))

        # Activos Fijos
        for row in ACTIVOS:
            session.add(AfxInventario(
                id=row[0], tipo=row[1], descripcion=row[2], numero_serie=None,
                ubicacion=row[3], ciudad=row[4], fecha_adquisicion=row[5],
                valor_original=row[6], valor_libro=row[7],
                vida_util_anios=row[8], status=row[9],
            ))
            # 3 años de depreciación mensual
            for anio in range(2023, 2026):
                dep_mensual = round(row[6] / row[8] / 12, 2)
                dep_acum = 0
                for mes in range(1, 13):
                    dep_acum = round(dep_acum + dep_mensual, 2)
                    session.add(AfxDepreciacion(
                        id=str(uuid.uuid4()),
                        activo_id=row[0], anio=anio, mes=mes,
                        depreciacion_mensual=dep_mensual,
                        depreciacion_acumulada=dep_acum,
                        valor_libro_fin=round(row[6] - dep_acum, 2),
                    ))

        # Mantenimientos
        proveedores = ["IBM Services México","Dell EMC México","Prosegur","G4S México","Diebold Nixdorf","Siemens México","Brinks México"]
        for activo_row in ACTIVOS[:20]:
            session.add(AfxMantenimiento(
                id=str(uuid.uuid4()),
                activo_id=activo_row[0],
                tipo_mantenimiento=random.choice(["PREVENTIVO","PREVENTIVO","CORRECTIVO"]),
                fecha=d(random.randint(10, 90)),
                costo=round(random.uniform(5000, 80000), 2),
                proveedor=random.choice(proveedores),
                descripcion="Mantenimiento programado según contrato de soporte",
                proxima_revision=d(-random.randint(30, 180)),
                status=random.choice(["COMPLETADO","COMPLETADO","PENDIENTE"]),
            ))

        # Riesgos — Alertas fraude
        for row in ALERTAS_FRAUDE:
            session.add(RsgAlertaFraude(
                id=row[0], cuenta_numero=row[1], fecha=row[2],
                tipo_alerta=row[3], score_riesgo=row[4],
                monto_sospechoso=row[5], descripcion=row[6],
                status=row[7], analista=row[8], resolucion=row[9],
            ))

        # VaR diario 90 días
        portafolio = 52000000000
        limite_var = 800000000
        for i in range(90):
            fecha = (TODAY - timedelta(days=89-i)).isoformat()
            v95 = round(random.uniform(250e6, 700e6), 2)
            v99 = round(v95 * 1.45, 2)
            v_stress = round(v99 * 1.8, 2)
            session.add(RsgVarDiario(
                fecha=fecha, var_95=v95, var_99=v99, var_estresado=v_stress,
                portafolio_mxn=portafolio, limite_var=limite_var,
                breach=v99 > limite_var, metodologia="HISTORICA",
            ))

        for row in CONTRAPARTES:
            session.add(RsgLimiteContraparte(
                contraparte=row[0], tipo=row[1], calificacion_externa=row[2],
                limite_aprobado=row[3], exposicion_actual=row[4],
                headroom=row[5], ultima_revision=row[6], vencimiento_linea=row[7],
            ))

        # Regulatorio — ICAP y LCR (12 meses)
        meses = [
            "2025-05-31","2025-06-30","2025-07-31","2025-08-31",
            "2025-09-30","2025-10-31","2025-11-30","2025-12-31",
            "2026-01-31","2026-02-28","2026-03-31","2026-04-30",
        ]
        tier1_base = 95000000000
        apr_base = 780000000000
        for fecha in meses:
            tier1 = round(tier1_base * random.uniform(0.98, 1.02), 2)
            tier2 = round(tier1 * 0.12, 2)
            apr = round(apr_base * random.uniform(0.97, 1.03), 2)
            icap = round((tier1 + tier2) / apr * 100, 2)
            session.add(RegIcapHistorico(
                fecha=fecha, tier1_capital=tier1, tier2_capital=tier2,
                capital_total=round(tier1+tier2, 2), activos_ponderados_riesgo=apr,
                icap_pct=icap, limite_minimo_pct=10.5, cumple=icap >= 10.5,
            ))
            hqla = round(random.uniform(180e9, 240e9), 2)
            salidas = round(random.uniform(120e9, 160e9), 2)
            lcr = round(hqla / salidas * 100, 2)
            session.add(RegLcrHistorico(
                fecha=fecha, activos_liquidos_hqla=hqla,
                salidas_netas_30d=salidas, lcr_pct=lcr,
                limite_minimo_pct=100.0, cumple=lcr >= 100,
            ))

        tipos_reporte = [
            ("R01A","Reporte de Captación Tradicional"),
            ("R04B","Reporte de Cartera de Crédito"),
            ("R10","Reporte de Capitalización (ICAP)"),
            ("R21A","Reporte de Liquidez (LCR/NSFR)"),
            ("R22","Reporte de Operaciones con Derivados"),
            ("A-01","Reporte de Prevención de Lavado de Dinero"),
        ]
        for i, fecha in enumerate(meses):
            for tipo, desc in tipos_reporte:
                session.add(RegReporteEnviado(
                    id=str(uuid.uuid4()),
                    tipo_reporte=tipo, descripcion=desc,
                    periodo=fecha[:7],
                    fecha_envio=datetime.strptime(fecha, "%Y-%m-%d") + timedelta(days=15),
                    status=random.choice(["ACEPTADO","ACEPTADO","ACEPTADO","ENVIADO","OBSERVACIONES"]),
                    folio_cnbv=f"CNBV-{tipo}-{fecha[:7].replace('-','')}-{random.randint(10000,99999)}",
                    observaciones=None,
                ))

        session.commit()

        counts = {
            "gl_catalogo_cuentas": len(GL_CATALOGO),
            "gl_asientos": 500,
            "gl_partidas": 1000,
            "try_posicion_diaria": 90,
            "try_instrumentos": len(INSTRUMENTOS_TRY),
            "try_operaciones_mesa": len(OPERACIONES_MESA),
            "crd_creditos": len(CREDITOS),
            "crd_amortizaciones": len(CREDITOS) * 12,
            "crd_calificacion": len(CALIFICACIONES),
            "rh_empleados": len(EMPLEADOS),
            "rh_nomina": len(EMPLEADOS) * 6,
            "rh_centros_costo": len(CENTROS_COSTO),
            "afx_inventario": len(ACTIVOS),
            "afx_depreciacion": len(ACTIVOS) * 36,
            "afx_mantenimiento": 20,
            "rsg_alertas_fraude": len(ALERTAS_FRAUDE),
            "rsg_var_diario": 90,
            "rsg_contrapartes": len(CONTRAPARTES),
            "reg_icap": len(meses),
            "reg_lcr": len(meses),
            "reg_reportes": len(meses) * len(tipos_reporte),
        }
        print("✓ internal.db creada con datos internos de Banorte:")
        for table, count in counts.items():
            print(f"  {table}: {count} registros")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    seed_internal()
