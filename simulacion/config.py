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
COSTO_DESARROLLO_MENSUAL = 3250
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

# --- Tipo de trabajo: probabilidades y distribuciones ---
PROB_APPS = 0.52
PROB_IT = 0.43   # 0.52 + 0.43 = 0.95, resto desarrollo
# Apps: Normal(15, 35) minutos, 1.0 crédito/min
# IT: Normal(5, 40) minutos, 1.25 créditos/min
# Desarrollo: Uniforme(2, 20) horas, 30 créditos/hora
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
PROB_ARREPENTIMIENTO_CALENDARIZADO = 0.50
PROB_FALTA_REUNION = 0.05
PROB_DISCONFORMIDAD_SI_FALTA = 0.30

# --- Satisfacción ---
PROB_INSATISFACCION_BASE = 0.015
PROB_CONECTIVIDAD_POBRE = 0.05
PROB_INESTABILIDAD_IMPLEMENTACION = 0.30
PROB_INSATISFACCION_CALENDARIZADO = 0.10

# --- Gestión de pago (insatisfactorio) ---
PROB_NO_COBRAR_NO_DESARROLLO = 0.90
PROB_COBRAR_DESARROLLO = 0.50

# --- Renovaciones ---
PROB_NO_RENOVACION_DISCONFORME = 0.70
PROB_NO_RENOVACION_PREPAGO_DISCONFORME = 0.70

# --- Conversión trabajo aislado → paquete ---
PROB_CONVERSION_TA_A_PAQUETE = 0.05
PROB_ASIDUO_TRAS_CONVERSION = 0.30

# --- Implementaciones ---
PORCENTAJE_DIAS_INESTABILIDAD = 0.15


def normal_truncada(media: float, std: float, min_val: float = 0, max_val: float = None) -> float:
    """Muestra de distribución normal (truncada si se indica)."""
    import random
    x = random.gauss(media, std)
    if max_val is None:
        max_val = float("inf")
    return max(min_val, min(max_val, x))


def uniforme(a: float, b: float) -> float:
    """Muestra de distribución uniforme en [a, b]."""
    import random
    return a + (b - a) * random.random()
