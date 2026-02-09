# -*- coding: utf-8 -*-
"""
Simulación de Plataforma Técnica SaaS.
Conecta técnicos con clientes; modela suscripción, prepago y trabajo aislado.
"""

from .estado import EstadoSimulacion, MejorTrimestre
from .principal import ejecutar_simulacion, imprimir_resultados

__all__ = [
    "EstadoSimulacion",
    "MejorTrimestre",
    "ejecutar_simulacion",
    "imprimir_resultados",
]
