# -*- coding: utf-8 -*-
"""
Estado global de la simulación. Contadores de clientes, financieros y métricas.
"""

from dataclasses import dataclass
from typing import Optional, List


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

        # --- Métricas ---
        self.T_EQUILIBRIO: Optional[int] = None
        self.MEJOR_TRIMESTRE = MejorTrimestre()
        self.beneficio_acumulado_por_dia: List[float] = []

    def scoring_IA_actual(self) -> float:
        """Scoring para intervalo de arribos: (Asiduos_Suscripcion + Asiduos_Prepago)*2 + PE_con_paquetes - (Asiduos_Suscripcion + Asiduos_Prepago)."""
        asiduos = self.Asiduos_Suscripcion + self.Asiduos_Prepago
        return asiduos * 2 + self.PE_con_paquetes - asiduos

    def total_asiduos(self) -> int:
        return self.Asiduos_Suscripcion + self.Asiduos_Prepago

    def total_ce(self) -> int:
        return self.CE_Suscripcion + self.CE_Prepago
