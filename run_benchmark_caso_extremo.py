# -*- coding: utf-8 -*-
"""
Benchmark caso extremo: inversión de marketing 10000, 5 años, 1000 corridas.
Genera serie_beneficio_acumulado.png y demás gráficos de benchmark.

Uso:
  python run_benchmark_caso_extremo.py
  python run_benchmark_caso_extremo.py --runs 500 --workers 4  # Más rápido
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, ".")

DIAS_5_ANOS = 365 * 5  # 1825 días


def _run_single_worker(worker_args):
    """Worker para multiprocessing."""
    j, T_FINAL, N, M, prob_suscripcion, seed = worker_args
    import random
    sys.path.insert(0, ".")
    from simulacion.principal import ejecutar_simulacion
    if seed is not None:
        random.seed(seed + j)
    return ejecutar_simulacion(
        T_FINAL=T_FINAL, N=N, M=M,
        prob_suscripcion_nuevo=prob_suscripcion, verbose=False
    )


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark caso extremo: MKT 10000, 5 años."
    )
    parser.add_argument("--runs", "-r", type=int, default=1000,
                        help="Corridas (default: 1000)")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Workers en paralelo (default: 1)")
    parser.add_argument("--output-dir", "-o", default="graficos_benchmark/caso_extremo_mkt10000",
                        help="Directorio de salida")
    parser.add_argument("--seed", "-s", type=int, default=42,
                        help="Semilla para reproducibilidad")
    args = parser.parse_args()

    T_FINAL = DIAS_5_ANOS
    N = 90  # Trimestrales (como cost-effective)
    M = 10000  # Caso extremo: inversión marketing muy alta
    prob_suscripcion = 0.50  # 50-50

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    from simulacion.benchmark import (
        ejecutar_benchmark,
        agregar_metricas,
        generar_graficos_benchmark,
    )

    print("=" * 70)
    print("BENCHMARK CASO EXTREMO: MKT 10000, 5 AÑOS")
    print("=" * 70)
    print(f"Corridas: {args.runs}")
    print(f"Workers: {args.workers}")
    print(f"Parámetros: T_FINAL={T_FINAL} días, N={N}, M={M}, AB={prob_suscripcion}")
    print(f"Salida: {output_dir}/")
    print()

    if args.workers > 1:
        from multiprocessing import Pool
        worker_args = [
            (j, T_FINAL, N, M, prob_suscripcion, args.seed)
            for j in range(args.runs)
        ]
        chunksz = max(1, args.runs // (args.workers * 4))
        with Pool(args.workers) as pool:
            resultados = list(pool.imap_unordered(_run_single_worker, worker_args, chunksize=chunksz))
    else:
        resultados = ejecutar_benchmark(
            n_runs=args.runs,
            T_FINAL=T_FINAL,
            N=N,
            M=M,
            prob_suscripcion_nuevo=prob_suscripcion,
            verbose=True,
            seed=args.seed,
            progress_interval=max(1, args.runs // 20),
        )

    agregado = agregar_metricas(resultados)
    generar_graficos_benchmark(agregado, output_dir=str(output_dir))

    stats = agregado["estadisticas"]
    if stats.get("beneficio_final"):
        s = stats["beneficio_final"]
        print(f"\nBeneficio final: media={s['media']:,.0f}, std={s['std']:,.0f}")

    print("\n" + "=" * 70)
    print("Gráficos guardados en:", output_dir)
    print("  - serie_beneficio_acumulado.png")
    print("  - boxplot_beneficio_final.png")
    print("  - histograma_beneficio_final.png")
    print("  - metricas_agregadas.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
