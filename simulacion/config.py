# -*- coding: utf-8 -*-
"""
Constantes y parámetros de la simulación de Plataforma Técnica SaaS.
Basado en: Propuesta de TP Final - Simulación de Plataforma Técnica SaaS.
"""

import math

# --- Parámetros de control ---
DIAS_POR_MES = 30
DIAS_POR_SEMANA = 7
DIAS_TRIMESTRE = 120
COSTO_DESARROLLO_MENSUAL = 16000
COSTO_MKT_POR_CLIENTE_NUEVO = 25
CREDITOS_PREPAGO_BLOQUE = 460
PRECIO_RENOVACION_PREPAGO = 354.2
PRECIO_SUSCRIPCION_MENSUAL = 10
PENALIZACION_FALTA_REUNION = 12
BENEFICIO_NETO_PORCENTAJE = 0.40  # 40% para la empresa
DESCUENTO_SUSCRIPCION = 0.15
FACTOR_COSTO_TECNICO_PREPAGO = 0.77 * 0.60  # créditos_trabajo * 0.77 * 0.60

# --- Límites presupuesto marketing ---
PRESUPUESTO_MKT_MIN = 500
PRESUPUESTO_MKT_MAX = 4500

# --- Trabajos diarios (base) ---
TRABAJOS_DIARIOS_MIN_BASE = 5
TRABAJOS_DIARIOS_MAX_BASE = 30
SCORING_BASE_TRABAJOS = 60
# Demanda proporcional a asiduos + marketing
TRABAJO_POR_ASIDUO_DIA = 1.0
TRABAJOS_DIARIOS_MIN_ABS = 1
TRABAJOS_DIARIOS_MAX_ABS = 200
INCREMENTO_MINIMO_POR_60_EXCESO = 5
INCREMENTO_MAXIMO_POR_30_EXCESO = 5

# --- Proporción horario laboral (días de semana) ---
PROP_HORARIO_LABORAL = 0.95
PROP_FUERA_HORARIO = 0.05

# --- Scoring y proporción nuevos vs PE ---
SCORING_UMBRAL_PE = 60
PROB_PREEXISTENTE_BASE = 0.20
PROB_NUEVO_BASE = 0.80
PROB_PREEXISTENTE_MAX = 0.70
INCREMENTO_PROB_PE_POR_30 = 0.01
INCREMENTO_PROB_PE_MAX = 0.50

# --- Límites explícitos de distribuciones (sin infinito) ---
INTER_ARRIBO_MAX_MINUTOS = 120   # Máx 2h entre llegadas (horas valle)
DURACION_APPS_MAX_MINUTOS = 120  # ~2h máximo trabajo APPS
DURACION_IT_MAX_MINUTOS = 120    # ~2h máximo trabajo IT

# --- Tipo de trabajo: Dirichlet (variabilidad día a día) ---
# Concentración: mayor = menos dispersión (más cerca de las medias)
# Media esperada: APPS ≈ 52%, IT ≈ 43%, DEV ≈ 5%
CONCENTRACION_TIPO_TRABAJO = 50
DIRICHLET_ALPHA_APPS = 26.0
DIRICHLET_ALPHA_IT = 21.5
DIRICHLET_ALPHA_DEV = 2.5
# Apps: Normal(15, 35) min truncada [0, 120], 1.0 crédito/min
# IT: Normal(5, 40) min truncada [0, 120], 1.25 créditos/min
# Desarrollo: Binomial negativa rango [2, 20] horas, 30 créditos/hora
DURACION_APPS_MEDIA = 15
DURACION_APPS_STD = 35
DURACION_IT_MEDIA = 5
DURACION_IT_STD = 40
DESARROLLO_HORAS_MIN = 2
DESARROLLO_HORAS_MAX = 20
COSTO_APPS_POR_MIN = 1.0
COSTO_IT_POR_MIN = 1.25
COSTO_DESARROLLO_POR_HORA = 30.0

# --- Calendarización ---
PROB_CALENDARIZAR_HORARIO_LABORAL = 0.05
PROB_CALENDARIZAR_FUERA_HORARIO = 0.65
PROB_ARREPENTIMIENTO_CALENDARIZADO = 0.60   # 60% (más realista)
PROB_FALTA_REUNION = 0.05
PROB_DISCONFORMIDAD_SI_FALTA = 0.50        # 50%

# --- Satisfacción ---
PROB_INSATISFACCION_BASE = 0.035       # 3.5% (más realista)
PROB_CONECTIVIDAD_POBRE = 0.10        # 10%
PROB_INESTABILIDAD_IMPLEMENTACION = 0.45   # 45%
PROB_INSATISFACCION_CALENDARIZADO = 0.17  # 17%

# --- Gestión de pago (insatisfactorio) ---
PROB_NO_COBRAR_NO_DESARROLLO = 0.85       # 85% (más realista)
PROB_COBRAR_DESARROLLO = 0.50

# --- Renovaciones ---
PROB_NO_RENOVACION_DISCONFORME = 0.80     # 80%
PROB_NO_RENOVACION_PREPAGO_DISCONFORME = 0.80  # 80%
# Abandono inmediato: prepago disconforme con trabajo insatisfactorio (no cobrado) puede irse sin consumir minutos
PROB_ABANDONO_PREPAGO_DISCONFORME = 0.60  # 60%

# --- Conversión trabajo aislado → paquete ---
PROB_CONVERSION_TA_A_PAQUETE = 0.05
PROB_ASIDUO_TRAS_CONVERSION = 0.30

# --- Cliente no cobrado (trabajo insatisfactorio) ---
PROB_CONFORME_SI_NO_COBRA_NO_PREPAGO = 0.50   # Suscripción/TA: queda conforme si no se cobra
PROB_RECUPERACION_POR_NO_COBRAR_PREPAGO = 0.50  # Prepago disconforme: no cobrar lo recupera
PROB_TIPO_PAGO_SUSCRIPCION_CLIENTE_NUEVO_CE = 0.50  # A/B test: nuevo CE elige suscripción vs prepago

# --- Concentraciones Beta por evento (mayor = menos dispersión) ---
CONCENTRACION_BETA_CONFORME_SI_NO_COBRA = 6   # Reacción humana impredecible
CONCENTRACION_BETA_RECUPERACION_PREPAGO = 7   # Gesto recuperación; algo más consistente
CONCENTRACION_BETA_TIPO_PAGO_NUEVO_CE = 10    # A/B test 50/50

# --- Implementaciones ---
PORCENTAJE_DIAS_INESTABILIDAD = 0.15

# --- Técnicos (modelo explícito TPLL/TPS/High Value) ---
HIGH_VALUE = float("inf")   # Indica técnico libre en TPS[]
TIPO_TECNICO_DEV = "DEV"
TIPO_TECNICO_APPS_IT = "APPS_IT"
MINUTOS_DIA_DEV = 360       # 6 horas/día
MINUTOS_DIA_APPS_IT = 480   # 8 horas/día
SEMANAS_CICLO_CONTRATACION = 3
PROB_ROTACION_TECNICO_SEMANAL = 0.01   # 1% por técnico por semana
FACTOR_DEVS_POR_TRABAJO_DESARROLLO_PERDIDO = 0.15  # ~1 dev cada 7 trabajos perdidos
FACTOR_APPS_IT_POR_TRABAJO_APPS_IT_PERDIDO = 0.12  # ~1 técnico cada 8 trabajos perdidos

# --- Binomial negativa (demanda de trabajos) ---
TRABAJOS_BINOMIAL_NEG_R = 5.0    # Parámetro r (dispersion)
TRABAJOS_BINOMIAL_NEG_P = 0.20   # Parámetro p (ajustar para media deseada)

# --- Binomial negativa: duración Desarrollo (reemplaza Uniforme) ---
DESARROLLO_BINOMIAL_NEG_R = 5.0   # r
DESARROLLO_BINOMIAL_NEG_P = 0.35  # p → media ≈ 9, duración media ≈ 11h

# --- EaE: inter-arribos y pesos horarios ---
# Pesos bimodal: picos 10-12 y 14-16 (horas 2-3 y 5-6 en 0-indexed)
PESOS_HORARIOS = (0.10, 0.14, 0.16, 0.12, 0.10, 0.14, 0.14, 0.10)
MINUTOS_POR_HORA = 60
HORAS_LABORALES = 8


def generar_inter_arribo(lambda_per_minuto: float, max_minutos: float = None) -> float:
    """
    Muestra de Exponencial(1/lambda). Tiempo hasta la próxima llegada en minutos.
    lambda_per_minuto: llegadas por minuto (tasa).
    max_minutos: límite superior; si no se indica, usa INTER_ARRIBO_MAX_MINUTOS.
    """
    import random
    if max_minutos is None:
        max_minutos = INTER_ARRIBO_MAX_MINUTOS
    if lambda_per_minuto <= 0:
        return max_minutos
    x = -math.log(1.0 - random.random()) / lambda_per_minuto
    return min(x, max_minutos)


def lambda_por_minuto_en_hora(tdn: int, hora: int) -> float:
    """
    Tasa de llegadas por minuto en la hora dada.
    Reparte TDN según PESOS_HORARIOS para obtener lambda en esa hora.
    """
    if tdn <= 0 or hora < 0 or hora >= HORAS_LABORALES:
        return 0.0
    peso = PESOS_HORARIOS[hora]
    suma_pesos = sum(PESOS_HORARIOS)
    llegadas_esperadas_hora = tdn * (peso / suma_pesos)
    return llegadas_esperadas_hora / MINUTOS_POR_HORA


def normal_truncada(media: float, std: float, min_val: float, max_val: float) -> float:
    """Muestra de distribución normal truncada en [min_val, max_val]."""
    import random
    x = random.gauss(media, std)
    return max(min_val, min(max_val, x))


def duracion_desarrollo_horas() -> float:
    """
    Duración de trabajo Desarrollo en horas [DESARROLLO_HORAS_MIN, DESARROLLO_HORAS_MAX].
    Usa binomial negativa en lugar de uniforme (más realista).
    """
    span = DESARROLLO_HORAS_MAX - DESARROLLO_HORAS_MIN
    x = binomial_negativa(DESARROLLO_BINOMIAL_NEG_R, DESARROLLO_BINOMIAL_NEG_P, max_val=int(span))
    return DESARROLLO_HORAS_MIN + min(x, span)


def binomial(n: int, p: float) -> int:
    """Muestra de Binomial(n, p) usando suma de Bernoulli."""
    import random
    return sum(1 for _ in range(n) if random.random() < p)


def prob_efectiva_beta(media: float, concentracion: float = 10.0) -> float:
    """
    Probabilidad efectiva con variabilidad (Beta). Media aproximada 'media'.
    concentracion alto = menos dispersión.
    """
    import random
    alpha = media * concentracion
    beta = (1.0 - media) * concentracion
    return random.betavariate(max(0.01, alpha), max(0.01, beta))


def poisson(lam: float) -> int:
    """
    Muestra de distribución Poisson(lambda).
    Para lambda grande usa aproximación normal.
    """
    import random
    if lam <= 0:
        return 0
    if lam > 100:
        x = random.gauss(lam, math.sqrt(lam))
        return max(0, int(round(x)))
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= L:
            return k - 1


def binomial_negativa(r: float, p: float, max_val: int = None) -> int:
    """
    Muestra de distribución binomial negativa (número de fracasos antes de r éxitos).
    media = r*(1-p)/p. Para conteos con sobredispersión.
    max_val: límite superior; si no se indica, usa TRABAJOS_DIARIOS_MAX_ABS.
    """
    import random
    if max_val is None:
        max_val = TRABAJOS_DIARIOS_MAX_ABS
    r_int = max(1, int(r))
    exitos = 0
    fracasos = 0
    while exitos < r_int:
        if random.random() < p:
            exitos += 1
        else:
            fracasos += 1
            if fracasos >= max_val:
                return max_val
    return min(fracasos, max_val)


def dirichlet_3(alpha1: float, alpha2: float, alpha3: float) -> tuple:
    """
    Muestra de distribución Dirichlet(alpha1, alpha2, alpha3).
    Devuelve (p1, p2, p3) donde p1 + p2 + p3 = 1.
    Implementación sin numpy usando Gamma.
    """
    import random
    g1 = random.gammavariate(max(0.01, alpha1), 1)
    g2 = random.gammavariate(max(0.01, alpha2), 1)
    g3 = random.gammavariate(max(0.01, alpha3), 1)
    total = g1 + g2 + g3
    return g1 / total, g2 / total, g3 / total
