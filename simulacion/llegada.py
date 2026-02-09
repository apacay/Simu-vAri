# -*- coding: utf-8 -*-
"""
Flujo de llegada de cliente: tipo de cliente, trabajo, calendarización,
atención, satisfacción, gestión de pago y conversiones.
Basado en: Llegada de Cliente.md
"""

import random
import math
from typing import Tuple, Optional

from . import config as cfg
from .estado import EstadoSimulacion


# --- Constantes de tipos (strings) ---
TIPO_CLIENTE_CE = "COST_EFFECTIVE"
TIPO_CLIENTE_TA = "TRABAJO_AISLADO"
TIPO_PAGO_SUSCRIPCION = "SUSCRIPCION"
TIPO_PAGO_PREPAGO = "PREPAGO"
TIPO_PAGO_TA = "TRABAJO_AISLADO"
TRABAJO_APPS = "APPS"
TRABAJO_IT = "IT"
TRABAJO_DESARROLLO = "DESARROLLO"


def determinar_tipo_pago_paquete(est: EstadoSimulacion, es_asiduo: bool) -> str:
    """Determina SUSCRIPCION o PREPAGO según proporción actual de asiduos/CE."""
    if es_asiduo:
        total = est.Asiduos_Suscripcion + est.Asiduos_Prepago
        if total <= 0:
            return TIPO_PAGO_SUSCRIPCION
        prob_suscripcion = est.Asiduos_Suscripcion / total
    else:
        ce_susc = est.CE_Suscripcion
        ce_prep = est.CE_Prepago
        total = ce_susc + ce_prep
        if total <= 0:
            return TIPO_PAGO_SUSCRIPCION
        prob_suscripcion = ce_susc / total
    return TIPO_PAGO_SUSCRIPCION if random.random() < prob_suscripcion else TIPO_PAGO_PREPAGO


def _determinar_trabajo() -> Tuple[str, float, float]:
    """Devuelve (tipo_trabajo, duracion, costo_por_unidad). Duración en minutos salvo Desarrollo en horas."""
    r = random.random()
    if r < cfg.PROB_APPS:
        duracion = cfg.normal_truncada(cfg.DURACION_APPS_MEDIA, cfg.DURACION_APPS_STD, 0)
        return TRABAJO_APPS, duracion, cfg.COSTO_APPS_POR_MIN
    if r < cfg.PROB_APPS + cfg.PROB_IT:
        duracion = cfg.normal_truncada(cfg.DURACION_IT_MEDIA, cfg.DURACION_IT_STD, 0)
        return TRABAJO_IT, duracion, cfg.COSTO_IT_POR_MIN
    duracion_h = cfg.uniforme(cfg.DESARROLLO_HORAS_MIN, cfg.DESARROLLO_HORAS_MAX)
    return TRABAJO_DESARROLLO, duracion_h, cfg.COSTO_DESARROLLO_POR_HORA


def procesar_llegada_cliente(
    est: EstadoSimulacion,
    es_inestable: bool,
    es_horario_laboral: bool,
    es_dia_semana: bool,
) -> None:
    """
    Flujo completo de una llegada: tipo cliente, trabajo, asignación, atención, pago, conversiones.
    """
    # Variables de esta llegada (no persistidas como estado global)
    es_nuevo = False
    tipo_cliente = TIPO_CLIENTE_TA
    tipo_pago = TIPO_PAGO_TA
    es_asiduo = False
    esta_conforme = True
    se_calendariza = False
    cliente_se_arrepiente = False
    cliente_falta = False
    trabajo_insatisfactorio = False
    se_cobra_cliente = True
    creditos_trabajo = 0.0
    duracion = 0.0
    costo_por_unidad = 0.0
    tipo_trabajo = TRABAJO_APPS

    # ----- 1. DETERMINACIÓN TIPO DE CLIENTE (Nuevo vs PE) -----
    scoring_IA = (est.Asiduos_Suscripcion + est.Asiduos_Prepago) * 2 + max(
        0,
        est.PE_con_paquetes - (est.Asiduos_Suscripcion + est.Asiduos_Prepago),
    )
    # En el doc: scoring_IA = (Asiduos_Suscripcion + Asiduos_Prepago)*2 + PE_con_paquetes - (Asiduos_Suscripcion + Asiduos_Prepago)
    scoring_IA = est.scoring_IA_actual()

    if scoring_IA <= cfg.SCORING_UMBRAL_PE:
        prob_preexistente = cfg.PROB_PREEXISTENTE_BASE
    else:
        exceso = scoring_IA - cfg.SCORING_UMBRAL_PE
        incremento = min(
            cfg.INCREMENTO_PROB_PE_MAX,
            math.floor(exceso / 30) * cfg.INCREMENTO_PROB_PE_POR_30,
        )
        prob_preexistente = min(cfg.PROB_PREEXISTENTE_MAX, cfg.PROB_PREEXISTENTE_BASE + incremento)
    prob_nuevo = 1.0 - prob_preexistente

    if random.random() < prob_preexistente:
        # ----- CLIENTE PREEXISTENTE -----
        peso_asiduos = (est.Asiduos_Suscripcion + est.Asiduos_Prepago) * 5
        peso_ce_na = (est.CE_Suscripcion + est.CE_Prepago) - (est.Asiduos_Suscripcion + est.Asiduos_Prepago)
        peso_ce_na = max(0, peso_ce_na)
        peso_aislados = est.PE_Trabajo_Aislado / 10.0
        peso_total = peso_asiduos + peso_ce_na + peso_aislados
        if peso_total <= 0:
            peso_total = 1.0
        random_prop = random.random() * peso_total

        if random_prop < peso_asiduos:
            tipo_cliente = TIPO_CLIENTE_CE
            es_asiduo = True
        elif random_prop < peso_asiduos + peso_ce_na:
            tipo_cliente = TIPO_CLIENTE_CE
            es_asiduo = False
        else:
            tipo_cliente = TIPO_CLIENTE_TA
            es_asiduo = False

        if tipo_cliente == TIPO_CLIENTE_TA:
            tipo_pago = TIPO_PAGO_TA
        else:
            tipo_pago = determinar_tipo_pago_paquete(est, es_asiduo)

        # Estado de conformidad (solo PE)
        if tipo_cliente == TIPO_CLIENTE_TA:
            esta_conforme = True
        elif es_asiduo:
            total_asiduos = est.Asiduos_Suscripcion + est.Asiduos_Prepago
            if total_asiduos > 0:
                prob_disconforme = est.Disconformes_Asiduos / total_asiduos
                esta_conforme = random.random() >= prob_disconforme
            else:
                esta_conforme = True
        else:
            total_ce = est.CE_Suscripcion + est.CE_Prepago
            if total_ce > 0:
                prob_disconforme = est.Disconformes_CE / total_ce
                esta_conforme = random.random() >= prob_disconforme
            else:
                esta_conforme = True
    else:
        # ----- CLIENTE NUEVO -----
        if est.CREDITOS_MKT_GASTADOS_MES >= est.PRESUPUESTO_MKT_MENSUAL:
            return  # Cliente se arrepiente, no llega
        est.COSTO_MKT += cfg.COSTO_MKT_POR_CLIENTE_NUEVO
        est.CREDITOS_MKT_GASTADOS_MES += cfg.COSTO_MKT_POR_CLIENTE_NUEVO
        es_nuevo = True
        esta_conforme = True

        rce = random.random()
        if rce < 0.90:
            tipo_cliente = TIPO_CLIENTE_TA
            es_asiduo = False
        elif rce < 0.97:
            tipo_cliente = TIPO_CLIENTE_CE
            es_asiduo = False
        else:
            tipo_cliente = TIPO_CLIENTE_CE
            es_asiduo = True
        # Tipo de pago para nuevo se define en procesar_cobro (A/B 50/50)

    # ----- 2. DETERMINACIÓN TIPO DE TRABAJO -----
    tipo_trabajo, duracion, costo_por_unidad = _determinar_trabajo()
    if tipo_trabajo == TRABAJO_DESARROLLO:
        creditos_trabajo = duracion * costo_por_unidad  # horas
    else:
        creditos_trabajo = duracion * costo_por_unidad  # minutos

    # ----- 3. ASIGNACIÓN DE TÉCNICO Y CALENDARIZACIÓN -----
    if es_horario_laboral and es_dia_semana:
        prob_calendarizar_base = cfg.PROB_CALENDARIZAR_HORARIO_LABORAL
    else:
        prob_calendarizar_base = cfg.PROB_CALENDARIZAR_FUERA_HORARIO
    prob_calendarizar = max(0.0, min(1.0, prob_calendarizar_base + est.ajuste_prob_calendarizacion))

    if random.random() < prob_calendarizar:
        se_calendariza = True
        if random.random() < cfg.PROB_ARREPENTIMIENTO_CALENDARIZADO:
            return  # Arrepentimiento, fin del flujo
        if random.random() < cfg.PROB_FALTA_REUNION:
            cliente_falta = True
            est.CREDITOS_ENTRANTES += cfg.PENALIZACION_FALTA_REUNION
            est.BENEFICIO_NETO_TRABAJOS += cfg.PENALIZACION_FALTA_REUNION * cfg.BENEFICIO_NETO_PORCENTAJE
            if random.random() < cfg.PROB_DISCONFORMIDAD_SI_FALTA:
                if es_asiduo:
                    est.Disconformes_Asiduos += 1
                elif tipo_cliente == TIPO_CLIENTE_CE:
                    est.Disconformes_CE += 1
                    if tipo_pago == TIPO_PAGO_PREPAGO:
                        est.Disconformes_Prepago += 1
                    elif tipo_pago == TIPO_PAGO_SUSCRIPCION:
                        est.Disconformes_Suscripcion += 1
            return
    else:
        se_calendariza = False

    # ----- 4. ATENCIÓN DEL TRABAJO Y SATISFACCIÓN -----
    prob_insat = cfg.PROB_INSATISFACCION_BASE + cfg.PROB_CONECTIVIDAD_POBRE
    if es_inestable:
        prob_insat += cfg.PROB_INESTABILIDAD_IMPLEMENTACION
    if se_calendariza:
        prob_insat += cfg.PROB_INSATISFACCION_CALENDARIZADO
    trabajo_insatisfactorio = random.random() < prob_insat

    # ----- 5. GESTIÓN DE PAGOS Y ATENCIÓN AL CLIENTE -----
    if trabajo_insatisfactorio:
        if tipo_trabajo != TRABAJO_DESARROLLO:
            se_cobra_cliente = random.random() >= cfg.PROB_NO_COBRAR_NO_DESARROLLO
        else:
            se_cobra_cliente = random.random() < cfg.PROB_COBRAR_DESARROLLO
        beneficio_trabajo = creditos_trabajo * cfg.BENEFICIO_NETO_PORCENTAJE

        if es_asiduo:
            if not se_cobra_cliente:
                est.BENEFICIO_NETO_TRABAJOS -= creditos_trabajo
            else:
                est.BENEFICIO_NETO_TRABAJOS += beneficio_trabajo
            est.Disconformes_Asiduos += 1
        else:
            if not se_cobra_cliente:
                if tipo_pago != TIPO_PAGO_PREPAGO:
                    if random.random() < 0.50:
                        pass  # Queda conforme
                    else:
                        if tipo_cliente == TIPO_CLIENTE_CE:
                            est.Disconformes_CE += 1
                            est.Disconformes_Suscripcion += 1
                        elif tipo_pago == TIPO_PAGO_TA:
                            est.PE_Trabajo_Aislado = max(0, est.PE_Trabajo_Aislado - 1)
                else:
                    if tipo_cliente == TIPO_CLIENTE_CE:
                        est.Disconformes_CE += 1
                        est.Disconformes_Prepago += 1
            else:
                if tipo_cliente == TIPO_CLIENTE_CE:
                    est.Disconformes_CE += 1
                    if tipo_pago == TIPO_PAGO_PREPAGO:
                        est.Disconformes_Prepago += 1
                    elif tipo_pago == TIPO_PAGO_SUSCRIPCION:
                        est.Disconformes_Suscripcion += 1

        if se_cobra_cliente:
            _procesar_cobro(
                est, creditos_trabajo, es_nuevo, tipo_cliente, tipo_pago, es_asiduo,
                trabajo_insatisfactorio, se_cobra_cliente,
            )
    else:
        se_cobra_cliente = True
        beneficio_trabajo = creditos_trabajo * cfg.BENEFICIO_NETO_PORCENTAJE
        est.BENEFICIO_NETO_TRABAJOS += beneficio_trabajo
        _procesar_cobro(
            est, creditos_trabajo, es_nuevo, tipo_cliente, tipo_pago, es_asiduo,
            trabajo_insatisfactorio, se_cobra_cliente,
        )
        # Recuperación: si estaba disconforme, ahora conforme
        if not esta_conforme:
            if es_asiduo:
                est.Disconformes_Asiduos = max(0, est.Disconformes_Asiduos - 1)
            elif tipo_cliente == TIPO_CLIENTE_CE:
                est.Disconformes_CE = max(0, est.Disconformes_CE - 1)
                if tipo_pago == TIPO_PAGO_SUSCRIPCION:
                    est.Disconformes_Suscripcion = max(0, est.Disconformes_Suscripcion - 1)
                elif tipo_pago == TIPO_PAGO_PREPAGO:
                    est.Disconformes_Prepago = max(0, est.Disconformes_Prepago - 1)

    # Para nuevos CE el tipo de pago se asigna en _procesar_cobro; para PE ya está
    # Aquí llamamos _procesar_cobro con tipo_pago actual (para PE es correcto; para nuevo CE se sobrescribe dentro)
    # Ya lo llamamos arriba. Falta: conversiones finales (TA satisfecho → paquete)
    if not es_nuevo and tipo_cliente == TIPO_CLIENTE_TA and not trabajo_insatisfactorio:
        if random.random() < cfg.PROB_CONVERSION_TA_A_PAQUETE:
            tipo_pago_conv = determinar_tipo_pago_paquete(est, False)
            if tipo_pago_conv == TIPO_PAGO_PREPAGO:
                est.CREDITOS_ENTRANTES += cfg.PRECIO_RENOVACION_PREPAGO
                est.BENEFICIO_NETO_PREPAGO += cfg.PRECIO_RENOVACION_PREPAGO
                _crear_prepago(est, False)
            else:
                est.CREDITOS_ENTRANTES += cfg.PRECIO_SUSCRIPCION_MENSUAL
                est.BENEFICIO_NETO_SUSCRIPCION += cfg.PRECIO_SUSCRIPCION_MENSUAL
                _crear_suscripcion(est, False)
            if random.random() < cfg.PROB_ASIDUO_TRAS_CONVERSION:
                _marcar_como_asiduo(est, tipo_pago_conv)
            est.PE_Trabajo_Aislado = max(0, est.PE_Trabajo_Aislado - 1)
    return


def _procesar_cobro(
    est: EstadoSimulacion,
    creditos_trabajo: float,
    es_nuevo: bool,
    tipo_cliente: str,
    tipo_pago: str,
    es_asiduo: bool,
    trabajo_insatisfactorio: bool,
    se_cobra_cliente: bool,
) -> None:
    if trabajo_insatisfactorio and not se_cobra_cliente:
        return

    if es_nuevo:
        if tipo_cliente == TIPO_CLIENTE_CE:
            if random.random() < 0.50:
                tipo_pago = TIPO_PAGO_SUSCRIPCION
                est.CREDITOS_ENTRANTES += cfg.PRECIO_SUSCRIPCION_MENSUAL
                est.BENEFICIO_NETO_SUSCRIPCION += cfg.PRECIO_SUSCRIPCION_MENSUAL
                _crear_suscripcion(est, es_asiduo)
                descuento = cfg.DESCUENTO_SUSCRIPCION
                creditos_con_descuento = creditos_trabajo * (1 - descuento)
                est.BENEFICIO_NETO_SUSCRIPCION += creditos_con_descuento * cfg.BENEFICIO_NETO_PORCENTAJE
            else:
                tipo_pago = TIPO_PAGO_PREPAGO
                est.CREDITOS_ENTRANTES += cfg.PRECIO_RENOVACION_PREPAGO
                est.BENEFICIO_NETO_PREPAGO += cfg.PRECIO_RENOVACION_PREPAGO
                _crear_prepago(est, es_asiduo)
                _consumir_creditos_prepago(
                    est, creditos_trabajo, trabajo_insatisfactorio, se_cobra_cliente,
                    es_asiduo, TIPO_CLIENTE_CE, TIPO_PAGO_PREPAGO,
                )
        else:
            est.CREDITOS_ENTRANTES += creditos_trabajo
            _agregar_a_PE_trabajo_aislado(est)
    else:
        if tipo_pago == TIPO_PAGO_SUSCRIPCION:
            descuento = cfg.DESCUENTO_SUSCRIPCION
            creditos_con_descuento = creditos_trabajo * (1 - descuento)
            est.BENEFICIO_NETO_SUSCRIPCION += creditos_con_descuento * cfg.BENEFICIO_NETO_PORCENTAJE
        elif tipo_pago == TIPO_PAGO_PREPAGO:
            _consumir_creditos_prepago(
                est, creditos_trabajo, trabajo_insatisfactorio, se_cobra_cliente,
                es_asiduo, tipo_cliente, tipo_pago,
            )
        else:
            est.CREDITOS_ENTRANTES += creditos_trabajo


def _consumir_creditos_prepago(
    est: EstadoSimulacion,
    creditos_trabajo: float,
    es_insatisfactorio: bool,
    se_cobra: bool,
    es_asiduo: bool = False,
    tipo_cliente: str = TIPO_CLIENTE_CE,
    tipo_pago: str = TIPO_PAGO_PREPAGO,
) -> None:
    """Consumo del bloque global de prepago."""
    if not es_insatisfactorio or se_cobra:
        if est.creditos_prepago_global >= creditos_trabajo:
            est.creditos_prepago_global -= creditos_trabajo
            costo_tecnico = creditos_trabajo * cfg.FACTOR_COSTO_TECNICO_PREPAGO
            est.BENEFICIO_NETO_PREPAGO -= costo_tecnico
        else:
            creditos_disponibles = est.creditos_prepago_global
            creditos_faltantes = creditos_trabajo - creditos_disponibles
            est.creditos_prepago_global = 0
            costo_tecnico_prepago = creditos_disponibles * cfg.FACTOR_COSTO_TECNICO_PREPAGO
            est.BENEFICIO_NETO_PREPAGO -= costo_tecnico_prepago
            if es_insatisfactorio and se_cobra:
                est.CREDITOS_ENTRANTES += creditos_faltantes
                est.BENEFICIO_NETO_TRABAJOS += creditos_faltantes * cfg.BENEFICIO_NETO_PORCENTAJE
            else:
                est.CREDITOS_ENTRANTES += cfg.PRECIO_RENOVACION_PREPAGO
                est.BENEFICIO_NETO_PREPAGO += cfg.PRECIO_RENOVACION_PREPAGO
                est.creditos_prepago_global = cfg.CREDITOS_PREPAGO_BLOQUE - creditos_faltantes
                costo_tecnico_nuevo = creditos_faltantes * cfg.FACTOR_COSTO_TECNICO_PREPAGO
                est.BENEFICIO_NETO_PREPAGO -= costo_tecnico_nuevo
        if est.creditos_prepago_global <= 0:
            _renovar_bloque_prepago(est)
    else:
        if random.random() < 0.50:
            # Queda satisfecho por no cobrar; limpiar disconformidad
            if es_asiduo:
                est.Disconformes_Asiduos = max(0, est.Disconformes_Asiduos - 1)
            elif tipo_cliente == TIPO_CLIENTE_CE:
                est.Disconformes_CE = max(0, est.Disconformes_CE - 1)
                est.Disconformes_Prepago = max(0, est.Disconformes_Prepago - 1)


def _renovar_bloque_prepago(est: EstadoSimulacion) -> None:
    """Renovación del bloque prepago cuando se agota."""
    if est.Prepagos_Totales <= 0:
        est.creditos_prepago_global = cfg.CREDITOS_PREPAGO_BLOQUE
        return
    if est.Disconformes_Prepago > 0:
        prob_era_disconforme = est.Disconformes_Prepago / est.Prepagos_Totales
        if random.random() < prob_era_disconforme and random.random() < cfg.PROB_NO_RENOVACION_PREPAGO_DISCONFORME:
            est.PE_con_paquetes -= 1
            est.Prepagos_Totales -= 1
            prop_asiduo = est.Asiduos_Prepago / est.Prepagos_Totales if est.Prepagos_Totales > 0 else 0
            if random.random() < prop_asiduo:
                est.Asiduos_Prepago = max(0, est.Asiduos_Prepago - 1)
                est.Disconformes_Asiduos = max(0, est.Disconformes_Asiduos - 1)
            else:
                est.CE_Prepago = max(0, est.CE_Prepago - 1)
            est.Disconformes_CE = max(0, est.Disconformes_CE - 1)
            est.Disconformes_Prepago = max(0, est.Disconformes_Prepago - 1)
            est.creditos_prepago_global = cfg.CREDITOS_PREPAGO_BLOQUE
            return
    est.CREDITOS_ENTRANTES += cfg.PRECIO_RENOVACION_PREPAGO
    est.BENEFICIO_NETO_PREPAGO += cfg.PRECIO_RENOVACION_PREPAGO
    est.creditos_prepago_global = cfg.CREDITOS_PREPAGO_BLOQUE


def _crear_suscripcion(est: EstadoSimulacion, es_asiduo: bool) -> None:
    est.Suscripciones_Totales += 1
    est.PE_con_paquetes += 1
    if es_asiduo:
        est.Asiduos_Suscripcion += 1
    else:
        est.CE_Suscripcion += 1


def _crear_prepago(est: EstadoSimulacion, es_asiduo: bool) -> None:
    """Solo actualiza contadores. El bloque global de prepago es único y no se incrementa aquí."""
    est.Prepagos_Totales += 1
    est.PE_con_paquetes += 1
    if es_asiduo:
        est.Asiduos_Prepago += 1
    else:
        est.CE_Prepago += 1


def _agregar_a_PE_trabajo_aislado(est: EstadoSimulacion) -> None:
    # Cliente nuevo TA se cuenta como PE trabajo aislado para futuras llegadas
    est.PE_Trabajo_Aislado += 1


def _marcar_como_asiduo(est: EstadoSimulacion, tipo_pago: str) -> None:
    if tipo_pago == TIPO_PAGO_SUSCRIPCION:
        est.Asiduos_Suscripcion += 1
        est.CE_Suscripcion = max(0, est.CE_Suscripcion - 1)
    else:
        est.Asiduos_Prepago += 1
        est.CE_Prepago = max(0, est.CE_Prepago - 1)
