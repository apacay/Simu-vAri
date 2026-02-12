# -*- coding: utf-8 -*-
"""
Algoritmo principal de la simulación: bucle de días, trabajos diarios,
implementaciones, calendarización, procesos mensuales, equilibrio y mejor trimestre.
Basado en: Algoritmo Principal - Simulación Plataforma Técnica.md
"""

import math
import random
from typing import Dict, Any

from . import config as cfg
from .estado import EstadoSimulacion, MejorTrimestre
from . import llegada


def calcular_trabajos_asiduos(est: EstadoSimulacion) -> int:
    """Trabajos del día de clientes asiduos (media proporcional a asiduos)."""
    asiduos = est.Asiduos_Suscripcion + est.Asiduos_Prepago
    media = asiduos * cfg.TRABAJO_POR_ASIDUO_DIA
    media = max(1.0, media)
    p = cfg.TRABAJOS_BINOMIAL_NEG_P
    r_efectivo = max(1.0, media * p / (1 - p))
    base = cfg.binomial_negativa(r_efectivo, p)
    return max(cfg.TRABAJOS_DIARIOS_MIN_ABS, min(cfg.TRABAJOS_DIARIOS_MAX_ABS, base))


def calcular_clientes_nuevos_hoy(est: EstadoSimulacion) -> int:
    """Clientes nuevos del día según presupuesto de marketing."""
    creditos_restantes = est.PRESUPUESTO_MKT_MENSUAL - est.CREDITOS_MKT_GASTADOS_MES
    max_nuevos_posibles = max(0, int(creditos_restantes / cfg.COSTO_MKT_POR_CLIENTE_NUEVO))
    if max_nuevos_posibles <= 0:
        return 0
    media_dia = est.PRESUPUESTO_MKT_MENSUAL / (cfg.DIAS_POR_MES * cfg.COSTO_MKT_POR_CLIENTE_NUEVO)
    nuevos = cfg.poisson(media_dia)
    return min(nuevos, max_nuevos_posibles)


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


def reiniciar_tps_dia(est: EstadoSimulacion) -> None:
    """Al inicio de cada día, reinicia TPS[] (todos los técnicos libres)."""
    est.TPS_Dev = [cfg.HIGH_VALUE] * est.Tecnicos_Dev
    est.TPS_AppsIT = [cfg.HIGH_VALUE] * est.Tecnicos_AppsIT


def incorporar_contrataciones(est: EstadoSimulacion) -> None:
    """Incorporar técnicos cuya fecha de llegada es hoy."""
    incorporados_dev = 0
    incorporados_apps_it = 0
    pendientes = []
    for (dia_inc, n_dev, n_apps_it) in est.contrataciones_pendientes:
        if dia_inc <= est.T:
            incorporados_dev += n_dev
            incorporados_apps_it += n_apps_it
        else:
            pendientes.append((dia_inc, n_dev, n_apps_it))
    est.contrataciones_pendientes = pendientes
    if incorporados_dev > 0 or incorporados_apps_it > 0:
        est.Tecnicos_Dev += incorporados_dev
        est.Tecnicos_AppsIT += incorporados_apps_it
        reiniciar_tps_dia(est)


def ejecutar_ciclo_contratacion(est: EstadoSimulacion) -> None:
    """Cada 3 semanas: calcular contrataciones según trabajos perdidos, incorporación en +3 semanas."""
    ciclo_dias = cfg.SEMANAS_CICLO_CONTRATACION * cfg.DIAS_POR_SEMANA
    if est.T < 2 or (est.T - 1) % ciclo_dias != 0:
        return
    perdidos = est.trabajos_perdidos_por_tipo
    n_devs = max(0, round(perdidos["DESARROLLO"] * cfg.FACTOR_DEVS_POR_TRABAJO_DESARROLLO_PERDIDO))
    n_apps_it = max(0, round(
        (perdidos["APPS"] + perdidos["IT"]) * cfg.FACTOR_APPS_IT_POR_TRABAJO_APPS_IT_PERDIDO
    ))
    if n_devs > 0 or n_apps_it > 0:
        dia_inc = est.T + cfg.SEMANAS_CICLO_CONTRATACION * cfg.DIAS_POR_SEMANA
        est.contrataciones_pendientes.append((dia_inc, n_devs, n_apps_it))
    est.trabajos_perdidos_por_tipo = {"APPS": 0, "IT": 0, "DESARROLLO": 0}


def aplicar_rotacion_tecnicos(est: EstadoSimulacion) -> None:
    """Cada semana: aplicar probabilidad de baja por técnico."""
    if (est.T % cfg.DIAS_POR_SEMANA) != 0:
        return
    bajas_dev = cfg.binomial(est.Tecnicos_Dev, cfg.PROB_ROTACION_TECNICO_SEMANAL)
    bajas_apps_it = cfg.binomial(est.Tecnicos_AppsIT, cfg.PROB_ROTACION_TECNICO_SEMANAL)
    if bajas_dev > 0 or bajas_apps_it > 0:
        est.Tecnicos_Dev = max(1, est.Tecnicos_Dev - bajas_dev)
        est.Tecnicos_AppsIT = max(1, est.Tecnicos_AppsIT - bajas_apps_it)
        reiniciar_tps_dia(est)


def cobrar_suscripciones(est: EstadoSimulacion) -> None:
    """Cobro mensual de suscripciones y bajas por no renovación (Binomial)."""
    if est.Disconformes_Suscripcion > 0:
        no_renovaciones = cfg.binomial(est.Disconformes_Suscripcion, cfg.PROB_NO_RENOVACION_DISCONFORME)
        no_renovaciones = min(no_renovaciones, est.Suscripciones_Totales)
        est.perdidas_semana["suscripcion_no_renovacion"] += no_renovaciones
        est.Suscripciones_Totales -= no_renovaciones
        est.PE_con_paquetes -= no_renovaciones
        total_susc = est.Asiduos_Suscripcion + est.CE_Suscripcion
        if total_susc > 0:
            prop_asiduos = est.Asiduos_Suscripcion / total_susc
            bajas_asiduos = min(est.Asiduos_Suscripcion, cfg.binomial(no_renovaciones, prop_asiduos))
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


def capturar_metricas_semana(est: EstadoSimulacion) -> Dict[str, Any]:
    """
    Captura snapshot semanal del estado para gráficos.
    Calcula porcentajes de satisfacción y métricas financieras.
    """
    semana = est.T // cfg.DIAS_POR_SEMANA
    beneficio_acum = _beneficio_acumulado(est)

    # Satisfacción prepago (Disconformes_Prepago <= Prepagos_Totales por diseño)
    if est.Prepagos_Totales > 0:
        disconformes_prep = min(est.Disconformes_Prepago, est.Prepagos_Totales)
        prepago_satisfechos_pct = (est.Prepagos_Totales - disconformes_prep) / est.Prepagos_Totales * 100
        prepago_insatisfechos_pct = disconformes_prep / est.Prepagos_Totales * 100
    else:
        prepago_satisfechos_pct = 0.0
        prepago_insatisfechos_pct = 0.0

    # Satisfacción suscripción (cap por diseño)
    if est.Suscripciones_Totales > 0:
        disconformes_susc = min(est.Disconformes_Suscripcion, est.Suscripciones_Totales)
        suscripcion_satisfechos_pct = (
            est.Suscripciones_Totales - disconformes_susc
        ) / est.Suscripciones_Totales * 100
        suscripcion_insatisfechos_pct = disconformes_susc / est.Suscripciones_Totales * 100
    else:
        suscripcion_satisfechos_pct = 0.0
        suscripcion_insatisfechos_pct = 0.0

    # Satisfacción general (clientes con paquetes; cap total_disconformes <= total_paquetes)
    total_paquetes = est.Suscripciones_Totales + est.Prepagos_Totales
    total_disconformes = min(
        est.Disconformes_Asiduos + est.Disconformes_CE,
        total_paquetes,
    )
    if total_paquetes > 0:
        general_satisfechos_pct = (total_paquetes - total_disconformes) / total_paquetes * 100
        general_insatisfechos_pct = total_disconformes / total_paquetes * 100
    else:
        general_satisfechos_pct = 0.0
        general_insatisfechos_pct = 0.0

    perdidas = dict(est.perdidas_semana)
    # Reset para la próxima semana
    est.perdidas_semana = {
        "suscripcion_no_renovacion": 0,
        "prepago_no_renovacion": 0,
        "prepago_abandono_insatisfecho": 0,
        "trabajo_aislado_insatisfecho": 0,
        "calendarizacion_sin_tecnico": 0,
    }

    return {
        "semana": semana,
        "dia": est.T,
        "perdidas": perdidas,
        "perdidas_total": sum(perdidas.values()),
        "satisfaccion": {
            "prepago_satisfechos_pct": prepago_satisfechos_pct,
            "prepago_insatisfechos_pct": prepago_insatisfechos_pct,
            "suscripcion_satisfechos_pct": suscripcion_satisfechos_pct,
            "suscripcion_insatisfechos_pct": suscripcion_insatisfechos_pct,
            "general_satisfechos_pct": general_satisfechos_pct,
            "general_insatisfechos_pct": general_insatisfechos_pct,
        },
        "clientes": {
            "suscripciones_totales": est.Suscripciones_Totales,
            "prepagos_totales": est.Prepagos_Totales,
            "trabajo_aislado": est.PE_Trabajo_Aislado,
            "pe_con_paquetes": est.PE_con_paquetes,
        },
        "beneficios": {
            "trabajos": est.BENEFICIO_NETO_TRABAJOS,
            "prepago": est.BENEFICIO_NETO_PREPAGO,
            "suscripcion": est.BENEFICIO_NETO_SUSCRIPCION,
            "total_acumulado": beneficio_acum,
        },
        "costos": {
            "desarrollo": est.COSTOS_DESARROLLO,
            "marketing": est.COSTO_MKT,
            "tecnicos": est.COSTOS_TECNICOS,
            "resarcimiento": est.COSTOS_RESARCIMIENTO,
        },
    }


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
        reiniciar_tps_dia(est)
        incorporar_contrataciones(est)
        ejecutar_ciclo_contratacion(est)
        aplicar_rotacion_tecnicos(est)

        trabajos_asiduos = calcular_trabajos_asiduos(est)
        clientes_nuevos = calcular_clientes_nuevos_hoy(est)
        TD = trabajos_asiduos + clientes_nuevos
        TDN = math.ceil(TD * cfg.PROP_HORARIO_LABORAL)
        TDOFF = math.floor(TD * cfg.PROP_FUERA_HORARIO)
        es_inestable = verificar_implementacion(est)
        calcular_ajuste_calendarizacion(est)

        es_dia_semana = (est.T % cfg.DIAS_POR_SEMANA) <= 4
        total_arrivals = TDN + TDOFF if es_dia_semana else TDOFF
        orden_llegadas = [True] * clientes_nuevos + [False] * trabajos_asiduos
        random.shuffle(orden_llegadas)
        if len(orden_llegadas) < total_arrivals:
            orden_llegadas.extend([False] * (total_arrivals - len(orden_llegadas)))
        else:
            orden_llegadas = orden_llegadas[:total_arrivals]

        idx_orden = 0

        # EaE: llegadas TDN en horario laboral (solo días de semana)
        if es_dia_semana and TDN > 0:
            minutos_dia = cfg.MINUTOS_DIA_APPS_IT
            inicio_dia = (est.T - 1) * minutos_dia
            reloj = inicio_dia
            tpll = reloj + cfg.generar_inter_arribo(
                cfg.lambda_por_minuto_en_hora(TDN, 0)
            )
            procesados = 0
            while procesados < TDN:
                reloj = tpll
                minuto_del_dia = reloj - inicio_dia
                hora_actual = min(cfg.HORAS_LABORALES - 1, max(0, int(minuto_del_dia // cfg.MINUTOS_POR_HORA)))
                lam = cfg.lambda_por_minuto_en_hora(TDN, hora_actual)
                lam = max(lam, 1e-6)
                tpll = reloj + cfg.generar_inter_arribo(lam)
                es_nuevo = orden_llegadas[idx_orden]
                idx_orden += 1
                llegada.procesar_llegada_cliente(
                    est, es_inestable, es_horario_laboral=True, es_dia_semana=True,
                    reloj=reloj,
                    forzar_tipo="nuevo" if es_nuevo else "preexistente",
                )
                procesados += 1

        # Batch: llegadas TDOFF fuera de horario (días de semana) o todas (fin de semana)
        n_batch = TDOFF if es_dia_semana else total_arrivals
        for j in range(n_batch):
            if idx_orden >= len(orden_llegadas):
                break
            es_nuevo = orden_llegadas[idx_orden]
            idx_orden += 1
            llegada.procesar_llegada_cliente(
                est, es_inestable, es_horario_laboral=False, es_dia_semana=es_dia_semana,
                minuto_arrivo=0,
                forzar_tipo="nuevo" if es_nuevo else "preexistente",
            )

        # Pago a desarrolladores al principio de cada mes (día 1, 31, 61, ...)
        if ((est.T - 1) % cfg.DIAS_POR_MES) == 0:
            pagar_desarrollos(est)
        # Fin de mes: cobro suscripciones y reposición de créditos MKT
        if (est.T % cfg.DIAS_POR_MES) == 0:
            cobrar_suscripciones(est)
            reponer_creditos_mkt(est)

        if est.T_EQUILIBRIO is None:
            verificar_equilibrio(est)

        est.beneficio_acumulado_por_dia.append(_beneficio_acumulado(est))

        if (est.T % cfg.DIAS_POR_SEMANA) == 0:
            est.metricas_semanales.append(capturar_metricas_semana(est))

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
    print()
    print("Técnicos (estado final):")
    print(f"  - Devs: {est.Tecnicos_Dev}")
    print(f"  - Apps/IT: {est.Tecnicos_AppsIT}")
    print("=" * 50)
