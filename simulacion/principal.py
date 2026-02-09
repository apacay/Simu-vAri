# -*- coding: utf-8 -*-
"""
Algoritmo principal de la simulación: bucle de días, trabajos diarios,
implementaciones, calendarización, procesos mensuales, equilibrio y mejor trimestre.
Basado en: Algoritmo Principal - Simulación Plataforma Técnica.md
"""

import math
from . import config as cfg
from .estado import EstadoSimulacion, MejorTrimestre
from . import llegada


def calcular_trabajos_diarios(est: EstadoSimulacion) -> float:
    """Calcula el número de trabajos del día con distribución normal."""
    scoring_IA = est.scoring_IA_actual()
    minimo = cfg.TRABAJOS_DIARIOS_MIN_BASE
    maximo = cfg.TRABAJOS_DIARIOS_MAX_BASE
    if scoring_IA > cfg.SCORING_BASE_TRABAJOS:
        exceso = scoring_IA - cfg.SCORING_BASE_TRABAJOS
        minimo += math.floor(exceso / 60) * cfg.INCREMENTO_MINIMO_POR_60_EXCESO
        maximo += math.floor(exceso / 30) * cfg.INCREMENTO_MAXIMO_POR_30_EXCESO
    media = (minimo + maximo) / 2.0
    std = (maximo - minimo) / 4.0
    return round(cfg.normal_truncada(media, std, minimo, maximo))


def verificar_implementacion(est: EstadoSimulacion) -> bool:
    """True si hoy hay implementación o aún hay inestabilidad de una anterior."""
    T = est.T
    N = est.DIAS_IMPLEMENTACION
    if (T - est.ULTIMO_DIA_IMPLEMENTACION) >= N:
        est.ULTIMO_DIA_IMPLEMENTACION = T
        est.DIAS_INESTABILIDAD_RESTANTES = math.ceil(N * cfg.PORCENTAJE_DIAS_INESTABILIDAD)
        return True
    if est.DIAS_INESTABILIDAD_RESTANTES > 0:
        est.DIAS_INESTABILIDAD_RESTANTES -= 1
        return True
    return False


def calcular_ajuste_calendarizacion(est: EstadoSimulacion) -> None:
    """Cada 7 días actualiza el ajuste de probabilidad de calendarización."""
    if (est.T % cfg.DIAS_POR_SEMANA) != 0:
        return
    scoring_actual = est.scoring_IA_actual()
    if est.scoring_IA_semana_anterior > 0:
        porcentaje_cambio = (scoring_actual - est.scoring_IA_semana_anterior) / est.scoring_IA_semana_anterior
    else:
        porcentaje_cambio = 0.0
    est.ajuste_prob_calendarizacion = porcentaje_cambio / 5.0
    est.scoring_IA_semana_anterior = scoring_actual


def llegadas_diarias_ON(est: EstadoSimulacion, es_inestable: bool) -> None:
    """Una llegada en horario laboral, día de semana."""
    llegada.procesar_llegada_cliente(est, es_inestable, es_horario_laboral=True, es_dia_semana=True)


def llegadas_diarias_OFF(est: EstadoSimulacion, es_inestable: bool) -> None:
    """Una llegada fuera de horario. es_dia_semana según si es Lun-Vie o no."""
    es_dia_semana = (est.T % cfg.DIAS_POR_SEMANA) <= 4
    llegada.procesar_llegada_cliente(est, es_inestable, es_horario_laboral=False, es_dia_semana=es_dia_semana)


def cobrar_suscripciones(est: EstadoSimulacion) -> None:
    """Cobro mensual de suscripciones y bajas por no renovación (70% disconformes)."""
    if est.Disconformes_Suscripcion > 0:
        no_renovaciones = round(est.Disconformes_Suscripcion * cfg.PROB_NO_RENOVACION_DISCONFORME)
        no_renovaciones = min(no_renovaciones, est.Suscripciones_Totales)
        est.Suscripciones_Totales -= no_renovaciones
        est.PE_con_paquetes -= no_renovaciones
        total_susc = est.Asiduos_Suscripcion + est.CE_Suscripcion
        if total_susc > 0:
            prop_asiduos = est.Asiduos_Suscripcion / total_susc
            bajas_asiduos = min(est.Asiduos_Suscripcion, round(no_renovaciones * prop_asiduos))
            bajas_ce = no_renovaciones - bajas_asiduos
            bajas_ce = min(bajas_ce, est.CE_Suscripcion)
            bajas_asiduos = no_renovaciones - bajas_ce
            est.Asiduos_Suscripcion -= bajas_asiduos
            est.CE_Suscripcion -= bajas_ce
            est.Disconformes_Asiduos = max(0, est.Disconformes_Asiduos - bajas_asiduos)
            est.Disconformes_CE = max(0, est.Disconformes_CE - bajas_ce)
            est.Disconformes_Suscripcion = max(0, est.Disconformes_Suscripcion - bajas_ce)
    ingresos = est.Suscripciones_Totales * cfg.PRECIO_SUSCRIPCION_MENSUAL
    est.CREDITOS_ENTRANTES += ingresos
    est.BENEFICIO_NETO_SUSCRIPCION += ingresos


def reponer_creditos_mkt(est: EstadoSimulacion) -> None:
    """Reinicio mensual del gasto de marketing."""
    est.CREDITOS_MKT_GASTADOS_MES = 0.0


def pagar_desarrollos(est: EstadoSimulacion) -> None:
    """Costo fijo mensual de desarrollo."""
    est.COSTOS_DESARROLLO += cfg.COSTO_DESARROLLO_MENSUAL
    est.BENEFICIO_NETO_TOTAL -= cfg.COSTO_DESARROLLO_MENSUAL


def _beneficio_acumulado(est: EstadoSimulacion) -> float:
    """Beneficio neto acumulado (ingresos netos - costos)."""
    return (
        est.BENEFICIO_NETO_TRABAJOS
        + est.BENEFICIO_NETO_PREPAGO
        + est.BENEFICIO_NETO_SUSCRIPCION
        - est.COSTOS_DESARROLLO
        - est.COSTO_MKT
    )


def verificar_equilibrio(est: EstadoSimulacion) -> None:
    """Marca T_EQUILIBRIO el primer día con beneficio acumulado > 0."""
    if est.T_EQUILIBRIO is not None:
        return
    if _beneficio_acumulado(est) > 0:
        est.T_EQUILIBRIO = est.T


def calcular_mejor_trimestre(est: EstadoSimulacion) -> None:
    """Actualiza MEJOR_TRIMESTRE si el último trimestre (120 días) supera el mejor."""
    T = est.T
    if T < cfg.DIAS_TRIMESTRE or len(est.beneficio_acumulado_por_dia) < T:
        return
    inicio = T - cfg.DIAS_TRIMESTRE + 1  # primer día del trimestre
    beneficio_antes = est.beneficio_acumulado_por_dia[T - cfg.DIAS_TRIMESTRE - 1] if T > cfg.DIAS_TRIMESTRE else 0.0
    beneficio_ahora = est.beneficio_acumulado_por_dia[T - 1]
    beneficio_trimestre = beneficio_ahora - beneficio_antes
    if beneficio_trimestre > est.MEJOR_TRIMESTRE.beneficio:
        est.MEJOR_TRIMESTRE = MejorTrimestre(inicio=inicio, fin=T, beneficio=beneficio_trimestre)


def ejecutar_simulacion(T_FINAL: int, N: int, M: float, verbose: bool = True) -> EstadoSimulacion:
    """
    Ejecuta la simulación hasta el día T_FINAL.
    N: frecuencia de implementaciones (días).
    M: presupuesto mensual de marketing (500-4500).
    """
    est = EstadoSimulacion(T_FINAL=T_FINAL, N=N, M=M)
    while est.T < est.T_FINAL:
        est.T += 1
        TD = calcular_trabajos_diarios(est)
        TDN = math.ceil(TD * cfg.PROP_HORARIO_LABORAL)
        TDOFF = math.floor(TD * cfg.PROP_FUERA_HORARIO)
        es_inestable = verificar_implementacion(est)
        calcular_ajuste_calendarizacion(est)

        if (est.T % cfg.DIAS_POR_SEMANA) <= 4:
            for _ in range(TDN):
                llegadas_diarias_ON(est, es_inestable)
            for _ in range(TDOFF):
                llegadas_diarias_OFF(est, es_inestable)
        else:
            for _ in range(TDOFF):
                llegadas_diarias_OFF(est, es_inestable)

        if (est.T % cfg.DIAS_POR_MES) == 0:
            cobrar_suscripciones(est)
            reponer_creditos_mkt(est)
            pagar_desarrollos(est)

        if est.T_EQUILIBRIO is None:
            verificar_equilibrio(est)

        est.beneficio_acumulado_por_dia.append(_beneficio_acumulado(est))
        if (est.T % cfg.DIAS_TRIMESTRE) == 0 and est.T >= cfg.DIAS_TRIMESTRE:
            calcular_mejor_trimestre(est)

    # Mejor trimestre: ventana móvil de 120 días sobre el historial
    n = len(est.beneficio_acumulado_por_dia)
    for i in range(cfg.DIAS_TRIMESTRE, n + 1):
        beneficio_antes = est.beneficio_acumulado_por_dia[i - cfg.DIAS_TRIMESTRE - 1] if i > cfg.DIAS_TRIMESTRE else 0.0
        beneficio_ahora = est.beneficio_acumulado_por_dia[i - 1]
        beneficio_trimestre = beneficio_ahora - beneficio_antes
        if beneficio_trimestre > est.MEJOR_TRIMESTRE.beneficio:
            est.MEJOR_TRIMESTRE = MejorTrimestre(
                inicio=i - cfg.DIAS_TRIMESTRE + 1,
                fin=i,
                beneficio=beneficio_trimestre,
            )

    if verbose:
        imprimir_resultados(est)
    return est


def imprimir_resultados(est: EstadoSimulacion) -> None:
    """Imprime resumen de resultados de la simulación."""
    print("=" * 50)
    print("RESULTADOS DE LA SIMULACIÓN")
    print("=" * 50)
    print()
    print("Parámetros:")
    print(f"  - Días simulados: {est.T_FINAL}")
    print(f"  - Frecuencia implementaciones (N): {est.DIAS_IMPLEMENTACION}")
    print(f"  - Presupuesto MKT mensual (M): {est.PRESUPUESTO_MKT_MENSUAL}")
    print()
    print("Beneficios netos:")
    print(f"  - Trabajos: {est.BENEFICIO_NETO_TRABAJOS:.2f}")
    print(f"  - Prepago: {est.BENEFICIO_NETO_PREPAGO:.2f}")
    print(f"  - Suscripción: {est.BENEFICIO_NETO_SUSCRIPCION:.2f}")
    total = _beneficio_acumulado(est)
    print(f"  - Total (acum.): {total:.2f}")
    print()
    if est.T_EQUILIBRIO is not None:
        print(f"Equilibrio alcanzado en día: {est.T_EQUILIBRIO}")
    else:
        print("No se alcanzó el equilibrio")
    print()
    print("Mejor trimestre (120 días):")
    if est.MEJOR_TRIMESTRE.beneficio > float("-inf"):
        print(f"  - Días: {est.MEJOR_TRIMESTRE.inicio} a {est.MEJOR_TRIMESTRE.fin}")
        print(f"  - Beneficio: {est.MEJOR_TRIMESTRE.beneficio:.2f}")
    else:
        print("  - No hay ventana completa de 120 días en esta corrida.")
    print()
    print("Estado final de clientes:")
    print(f"  - PE Trabajo Aislado: {est.PE_Trabajo_Aislado}")
    print(f"  - Suscripciones: {est.Suscripciones_Totales}")
    print(f"    - Asiduos: {est.Asiduos_Suscripcion}")
    print(f"    - No asiduos (CE): {est.CE_Suscripcion}")
    print(f"  - Prepagos: {est.Prepagos_Totales}")
    print(f"    - Asiduos: {est.Asiduos_Prepago}")
    print(f"    - No asiduos (CE): {est.CE_Prepago}")
    print(f"  - Disconformes: Asiduos={est.Disconformes_Asiduos}, CE={est.Disconformes_CE}, Prepago={est.Disconformes_Prepago}, Suscripción={est.Disconformes_Suscripcion}")
    print("=" * 50)
