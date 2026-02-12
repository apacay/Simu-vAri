# -*- coding: utf-8 -*-
"""
Punto de entrada para ejecutar múltiples corridas de la simulación (benchmark).

Ejecuta un número configurable de runs con los mismos parámetros, extrae métricas
agregadas (media, desv. estándar, percentiles) y genera gráficos de distribuciones
y series temporales.

Uso:
  python run_benchmark.py --runs 20
  python run_benchmark.py --runs 50 --dias 3653 --implementaciones 30 --marketing 2000
  python run_benchmark.py -r 10 -T 1826 -N 30 -M 2000 --seed 42 -g
"""

import argparse
import json
import sys
from pathlib import Path

# Permitir ejecutar desde la raíz del proyecto
sys.path.insert(0, ".")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark: ejecuta N corridas de la simulación y genera métricas/gráficos agregados."
    )
    parser.add_argument(
        "--runs", "-r",
        type=int,
        default=10,
        help="Número de corridas a ejecutar (default: 10)",
    )
    parser.add_argument(
        "--dias", "-T",
        type=int,
        default=3653,
        help="Días totales a simular por corrida (default: 3653)",
    )
    parser.add_argument(
        "--implementaciones", "-N",
        type=int,
        default=30,
        help="Frecuencia de implementaciones en días (default: 30)",
    )
    parser.add_argument(
        "--marketing", "-M",
        type=float,
        default=2000,
        help="Presupuesto mensual de marketing (500-4500, default: 2000)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Semilla para reproducibilidad (opcional)",
    )
    parser.add_argument(
        "--graficos", "-g",
        action="store_true",
        help="Generar gráficos de distribuciones y series agregadas",
    )
    parser.add_argument(
        "--output-graficos",
        type=str,
        default="graficos_benchmark",
        help="Directorio de salida para gráficos (default: graficos_benchmark)",
    )
    parser.add_argument(
        "--output-metricas",
        type=str,
        default=None,
        help="Archivo JSON para guardar métricas agregadas (ej: metricas.json)",
    )
    parser.add_argument(
        "--silencioso", "-q",
        action="store_true",
        help="No imprimir progreso por corrida",
    )
    args = parser.parse_args()

    n_runs = max(1, args.runs)
    T_FINAL = max(1, args.dias)
    N = max(1, args.implementaciones)
    M = max(500, min(4500, args.marketing))

    from simulacion.benchmark import ejecutar_benchmark, agregar_metricas, generar_graficos_benchmark

    print("=" * 60)
    print("BENCHMARK DE SIMULACIÓN")
    print("=" * 60)
    print(f"Corridas: {n_runs}")
    print(f"Parámetros: T_FINAL={T_FINAL}, N={N}, M={M}")
    if args.seed is not None:
        print(f"Seed: {args.seed} (reproducible)")
    print()

    resultados = ejecutar_benchmark(
        n_runs=n_runs,
        T_FINAL=T_FINAL,
        N=N,
        M=M,
        verbose=not args.silencioso,
        seed=args.seed,
    )

    agregado = agregar_metricas(resultados)
    stats = agregado["estadisticas"]

    # Imprimir resumen
    print()
    print("MÉTRICAS AGREGADAS")
    print("-" * 40)
    if "beneficio_final" in stats and stats["beneficio_final"]:
        s = stats["beneficio_final"]
        print(f"Beneficio final:")
        print(f"  Media:   {s['media']:,.2f} créditos")
        print(f"  Std:    {s['std']:,.2f}")
        print(f"  Min:    {s['min']:,.2f}")
        print(f"  Max:    {s['max']:,.2f}")
    if "equilibrio_dia" in stats and stats["equilibrio_dia"]:
        s = stats["equilibrio_dia"]
        print(f"Día de equilibrio (cuando aplica):")
        print(f"  Media:   {s['media']:.0f} días")
        print(f"  Min:    {s['min']:.0f}")
        print(f"  Max:    {s['max']:.0f}")
    print(f"Equilibrio alcanzado: {stats.get('equilibrio_porcentaje', 0):.1f}% de las corridas")
    if "mejor_trimestre_beneficio" in stats and stats["mejor_trimestre_beneficio"]:
        s = stats["mejor_trimestre_beneficio"]
        print(f"Mejor trimestre (beneficio): Media {s['media']:,.2f} créditos")
    if "suscripciones_final" in stats and stats["suscripciones_final"]:
        s = stats["suscripciones_final"]
        print(f"Suscripciones finales: Media {s['media']:.1f} ± {s['std']:.1f}")
    print("=" * 60)

    if args.graficos:
        generar_graficos_benchmark(agregado, output_dir=args.output_graficos)
        print(f"\nGráficos guardados en: {args.output_graficos}/")

    if args.output_metricas:
        # Serializar para JSON (sin metricas_semanales completas para no inflar)
        export = {
            "n_runs": agregado["n_runs"],
            "parametros": agregado["parametros"],
            "estadisticas": stats,
            "metricas_por_run": [
                {
                    "beneficio_final": m.beneficio_final,
                    "equilibrio_dia": m.equilibrio_dia,
                    "mejor_trimestre_beneficio": m.mejor_trimestre_beneficio,
                    "suscripciones_final": m.suscripciones_final,
                    "prepagos_final": m.prepagos_final,
                }
                for m in agregado["metricas_por_run"]
            ],
        }
        Path(args.output_metricas).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_metricas, "w", encoding="utf-8") as f:
            json.dump(export, f, indent=2, ensure_ascii=False)
        print(f"Métricas exportadas a: {args.output_metricas}")

    return agregado


if __name__ == "__main__":
    main()
