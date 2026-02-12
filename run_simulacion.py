# -*- coding: utf-8 -*-
"""
Punto de entrada para ejecutar la simulación de la Plataforma Técnica SaaS.

Uso:
  python run_simulacion.py [T_FINAL] [N] [M]
  python run_simulacion.py --dias 3653 --implementaciones 30 --marketing 2000

Parámetros:
  T_FINAL : Días a simular (default 3653).
  N       : Frecuencia de implementaciones en días (default 30).
  M       : Presupuesto mensual de marketing, 500-4500 (default 2000).
"""

import argparse
import sys

# Permitir ejecutar desde la raíz del proyecto
sys.path.insert(0, ".")


def main():
    parser = argparse.ArgumentParser(
        description="Simulación de Plataforma Técnica SaaS (trabajos diarios, clientes PE/nuevos, suscripción/prepago/TA)."
    )
    parser.add_argument(
        "--dias", "-T",
        type=int,
        default=3653,
        help="Días totales a simular (T_FINAL)",
    )
    parser.add_argument(
        "--implementaciones", "-N",
        type=int,
        default=30,
        help="Frecuencia de implementaciones en días (cada N días)",
    )
    parser.add_argument(
        "--marketing", "-M",
        type=float,
        default=2000,
        help="Presupuesto mensual de marketing (500-4500 créditos)",
    )
    parser.add_argument(
        "--silencioso", "-q",
        action="store_true",
        help="No imprimir resultados al final",
    )
    parser.add_argument(
        "--graficos", "-g",
        action="store_true",
        help="Generar gráficos de métricas semana a semana",
    )
    parser.add_argument(
        "--output-graficos",
        type=str,
        default="graficos",
        help="Directorio de salida para los gráficos PNG (default: graficos)",
    )
    args = parser.parse_args()

    T_FINAL = max(1, args.dias)
    N = max(1, args.implementaciones)
    M = max(500, min(4500, args.marketing))

    from simulacion.principal import ejecutar_simulacion

    estado = ejecutar_simulacion(T_FINAL=T_FINAL, N=N, M=M, verbose=not args.silencioso)

    if args.graficos:
        from simulacion.graficos import generar_graficos
        generar_graficos(estado, output_dir=args.output_graficos)
        if not args.silencioso:
            print(f"\nGráficos guardados en: {args.output_graficos}/")

    return estado


if __name__ == "__main__":
    main()
