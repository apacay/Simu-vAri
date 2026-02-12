# -*- coding: utf-8 -*-
"""
Estado global de la simulación. Contadores de clientes, financieros y métricas.
Incluye modelo de técnicos con TPLL, TPS[], HIGH_VALUE.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple

from . import config as cfg


@dataclass
class MejorTrimestre:
    """Mejor trimestre (120 días) por beneficio."""
    inicio: int = 0
    fin: int = 0
    beneficio: float = float("-inf")


class EstadoSimulacion:
    """
    Estado único de la simulación. Todos los módulos reciben y modifican
    esta instancia para mantener consistencia.
    """

    def __init__(self, T_FINAL: int, N: int, M: float):
        # Parámetros de control
        self.T_FINAL = T_FINAL
        self.DIAS_IMPLEMENTACION = N
        self.PRESUPUESTO_MKT_MENSUAL = M
        self.T = 0

        # --- Contadores de clientes (valores iniciales del enunciado) ---
        self.PE_Trabajo_Aislado = 940
        self.Asiduos_Suscripcion = 14
        self.Asiduos_Prepago = 3
        self.CE_Suscripcion = 47 - 14   # 33
        self.CE_Prepago = 13 - 3        # 10
        self.PE_con_paquetes = 60
        self.Suscripciones_Totales = 47
        self.Prepagos_Totales = 13
        self.Disconformes_Asiduos = 0
        self.Disconformes_CE = 0
        self.Disconformes_Prepago = 0
        self.Disconformes_Suscripcion = 0

        # --- Financieros ---
        self.CREDITOS_ENTRANTES = 0.0
        self.COSTO_MKT = 0.0
        self.CREDITOS_MKT_GASTADOS_MES = 0.0
        self.COSTOS_TECNICOS = 0.0
        self.COSTOS_RESARCIMIENTO = 0.0
        self.COSTOS_DESARROLLO = 0.0
        self.BENEFICIO_NETO_TRABAJOS = 0.0
        self.BENEFICIO_NETO_PREPAGO = 0.0
        self.BENEFICIO_NETO_SUSCRIPCION = 0.0
        self.BENEFICIO_NETO_TOTAL = 0.0

        # --- Prepago (bloque global) ---
        self.creditos_prepago_global = 460

        # --- Implementaciones ---
        self.ULTIMO_DIA_IMPLEMENTACION = 0
        self.DIAS_INESTABILIDAD_RESTANTES = 0

        # --- Ajuste calendarización ---
        self.scoring_IA_semana_anterior = 77
        self.ajuste_prob_calendarizacion = 0.0

        # --- Modelo de técnicos (TPLL, TPS[], HIGH_VALUE) ---
        self.TPLL = 0.0                      # Tiempo Próxima Llegada (minutos desde inicio)
        self.reloj_minutos = 0                # Reloj en minutos acumulados
        self.Tecnicos_Dev = 2                 # Cantidad inicial de devs
        self.Tecnicos_AppsIT = 5              # Cantidad inicial de técnicos Apps/IT
        self.TPS_Dev: List[float] = []        # TPS[i] por cada Dev; HIGH_VALUE = libre
        self.TPS_AppsIT: List[float] = []    # TPS[i] por cada técnico Apps/IT
        self._inicializar_tps()
        self.trabajos_perdidos_por_tipo: Dict[str, int] = {
            "APPS": 0, "IT": 0, "DESARROLLO": 0
        }
        self.contrataciones_pendientes: List[Tuple[int, int, int]] = []  # (dia, n_devs, n_apps_it)

        # --- Métricas ---
        self.T_EQUILIBRIO: Optional[int] = None
        self.MEJOR_TRIMESTRE = MejorTrimestre()
        self.beneficio_acumulado_por_dia: List[float] = []
        self.metricas_semanales: List[Dict[str, Any]] = []
        # Pérdidas de clientes por semana (se reinicia cada semana)
        self.perdidas_semana: Dict[str, int] = {
            "suscripcion_no_renovacion": 0,
            "prepago_no_renovacion": 0,
            "prepago_abandono_insatisfecho": 0,  # Abandono inmediato (minutos sin consumir)
            "trabajo_aislado_insatisfecho": 0,
            "calendarizacion_sin_tecnico": 0,  # Por falta de disponibilidad
        }

    def _inicializar_tps(self) -> None:
        """Inicializa TPS[] con HIGH_VALUE (todos libres)."""
        self.TPS_Dev = [cfg.HIGH_VALUE] * self.Tecnicos_Dev
        self.TPS_AppsIT = [cfg.HIGH_VALUE] * self.Tecnicos_AppsIT

    def scoring_IA_actual(self) -> float:
        """Scoring para intervalo de arribos: (Asiduos_Suscripcion + Asiduos_Prepago)*2 + PE_con_paquetes - (Asiduos_Suscripcion + Asiduos_Prepago)."""
        asiduos = self.Asiduos_Suscripcion + self.Asiduos_Prepago
        return asiduos * 2 + self.PE_con_paquetes - asiduos

    def total_asiduos(self) -> int:
        return self.Asiduos_Suscripcion + self.Asiduos_Prepago

    def total_ce(self) -> int:
        return self.CE_Suscripcion + self.CE_Prepago
