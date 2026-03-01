# -*- coding: utf-8 -*-
"""
Benchmark de los 3 casos más relevantes del informe a 10 años:
- Cost-effective: 50-50 / Trimestrales / MKT 500
- Equilibrio más rápido: 0-100 / Trimestrales / MKT 2500
- Menos efectivo: 100-0 / Semanales / MKT 500

Ejecuta 5 años por caso (cost-effective: 6 años para capturar equilibrio tardío) y 1000 corridas.
Genera: boxplot, serie_beneficio_acumulado, y gráficos de ejemplo
(perdidas_clientes, resultado_neto, satisfaccion_general) de una corrida representativa.

Uso:
  python run_benchmark_casos_relevantes.py
  python run_benchmark_casos_relevantes.py --runs 500 --workers 4  # Más rápido
"""

import argparse
import os
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, ".")

# Años por defecto
DIAS_5_ANOS = 365 * 5   # 1825 días
DIAS_6_ANOS = 365 * 6   # 2190 días (cost-effective necesita más tiempo para capturar equilibrio tardío)

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


def _calcular_equilibrio_serie(agregado: dict) -> dict:
    """
    Calcula el punto de equilibrio más temprano y más tardío desde la serie
    beneficio_acumulado (media ± 1σ).
    - Más temprano: primera semana donde Media+1σ cruza cero (caso optimista)
    - Más tardío: primera semana donde Media-1σ cruza cero (caso pesimista)
    """
    series = agregado.get("series_agregadas", {}).get("beneficio_acumulado", [])
    if not series:
        return {"semana_mas_temprano": None, "semana_mas_tardio": None}

    semana_temprano = None
    semana_tardio = None
    for w, s in enumerate(series):
        media = s.get("media", 0)
        std = s.get("std", 0)
        upper = media + std
        lower = media - std
        if semana_temprano is None and upper >= 0:
            semana_temprano = w
        if semana_tardio is None and lower >= 0:
            semana_tardio = w
        if semana_temprano is not None and semana_tardio is not None:
            break
    return {"semana_mas_temprano": semana_temprano, "semana_mas_tardio": semana_tardio}


def _actualizar_informe_equilibrios(output_base: Path) -> None:
    """Actualiza el informe HTML con los puntos de equilibrio de cada caso."""
    import json
    informe_path = output_base.parent / "INFORME_HALLAZGOS_COMPLETO.html"
    if not informe_path.exists():
        return

    reemplazos = []
    for caso in CASOS_RELEVANTES:
        info_path = output_base / caso["id"] / "equilibrio_info.json"
        if not info_path.exists():
            continue
        with open(info_path, encoding="utf-8") as f:
            info = json.load(f)
        temprano = info.get("semana_mas_temprano")
        tardio = info.get("semana_mas_tardio")
        if temprano is not None and tardio is not None:
            texto_eq = f" Punto de equilibrio: semana {temprano} (más temprano) – semana {tardio} (más tardío)."
        else:
            texto_eq = " Punto de equilibrio: no alcanzado en el periodo."
        reemplazos.append((caso["id"], texto_eq))

    with open(informe_path, "r", encoding="utf-8") as f:
        html = f.read()

    for caso_id, texto_eq in reemplazos:
        # Buscar el figcaption de serie_beneficio_acumulado para este caso
        patron = (
            f'<figcaption><strong>Figura {{11|12|13}}b.</strong> '
            f'Beneficio acumulado medio ± desv. estándar</figcaption>'
        )
        # Mapeo caso -> número de figura
        fig_map = {"cost_effective": "11", "equilibrio_antes": "12", "menos_efectivo": "13"}
        num = fig_map.get(caso_id)
        if num:
            old = f'<figcaption><strong>Figura {num}b.</strong> Beneficio acumulado medio ± desv. estándar</figcaption>'
            new = f'<figcaption><strong>Figura {num}b.</strong> Beneficio acumulado medio ± desv. estándar.{texto_eq}</figcaption>'
            if old in html and new not in html:
                html = html.replace(old, new, 1)

    with open(informe_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nInforme actualizado: {informe_path}")


CASOS_RELEVANTES = [
    {
        "id": "cost_effective",
        "nombre": "Cost-effective (50-50 / Trim / MKT 500)",
        "ab": 0.5,
        "N": 90,
        "M": 500,
        "dias": DIAS_6_ANOS,  # 6 años para capturar equilibrio más tardío
    },
    {
        "id": "equilibrio_antes",
        "nombre": "Equilibrio más rápido (0-100 / Trim / MKT 2500)",
        "ab": 0.0,
        "N": 90,
        "M": 2500,
        "dias": DIAS_5_ANOS,
    },
    {
        "id": "menos_efectivo",
        "nombre": "Menos efectivo (100-0 / Sem / MKT 500)",
        "ab": 1.0,
        "N": 7,
        "M": 500,
        "dias": DIAS_5_ANOS,
    },
]


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark de 3 casos relevantes: 5 años, N corridas."
    )
    parser.add_argument("--runs", "-r", type=int, default=1000,
                        help="Corridas por caso (default: 1000)")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Workers en paralelo (default: 1)")
    parser.add_argument("--seed", "-s", type=int, default=42,
                        help="Semilla para reproducibilidad")
    parser.add_argument("--output-dir", "-o", default="benchmark_10_anos/casos_5_anos",
                        help="Directorio de salida (default: benchmark_10_anos/casos_5_anos)")
    args = parser.parse_args()

    output_base = Path(args.output_dir)
    output_base.mkdir(parents=True, exist_ok=True)

    from simulacion.benchmark import (
        ejecutar_benchmark,
        agregar_metricas,
        generar_graficos_benchmark,
    )
    from simulacion.graficos import generar_graficos

    print("=" * 70)
    print("BENCHMARK CASOS RELEVANTES")
    print("=" * 70)
    print(f"Corridas por caso: {args.runs}")
    print(f"Total simulaciones: {len(CASOS_RELEVANTES) * args.runs}")
    print()

    for i, caso in enumerate(CASOS_RELEVANTES):
        T_FINAL = caso["dias"]
        print(f"\n[{i+1}/{len(CASOS_RELEVANTES)}] {caso['nombre']}")
        print(f"  AB={caso['ab']}, N={caso['N']}, M={caso['M']}, {T_FINAL} días ({T_FINAL//365} años)")

        if args.workers > 1:
            from multiprocessing import Pool

            worker_args = [
                (j, T_FINAL, caso["N"], caso["M"], caso["ab"], args.seed + i * 10000)
                for j in range(args.runs)
            ]
            chunksz = max(1, args.runs // (args.workers * 4))
            with Pool(args.workers) as pool:
                resultados = list(pool.imap_unordered(_run_single_worker, worker_args, chunksize=chunksz))
        else:
            resultados = ejecutar_benchmark(
                n_runs=args.runs,
                T_FINAL=T_FINAL,
                N=caso["N"],
                M=caso["M"],
                prob_suscripcion_nuevo=caso["ab"],
                verbose=False,
                seed=args.seed + i * 10000,
                progress_interval=max(1, args.runs // 20),
            )

        agregado = agregar_metricas(resultados)

        # Directorio de salida para este caso
        caso_dir = output_base / caso["id"]
        caso_dir.mkdir(parents=True, exist_ok=True)

        # 1. Gráficos de benchmark agregado (boxplot, serie_beneficio_acumulado)
        generar_graficos_benchmark(agregado, output_dir=str(caso_dir))

        # Calcular puntos de equilibrio (más temprano y más tardío) desde la serie ±1σ
        equilibrio_info = _calcular_equilibrio_serie(agregado)
        equilibrio_info["caso_id"] = caso["id"]
        equilibrio_info["caso_nombre"] = caso["nombre"]
        with open(caso_dir / "equilibrio_info.json", "w", encoding="utf-8") as f:
            import json
            json.dump(equilibrio_info, f, indent=2, ensure_ascii=False)

        # 2. Gráficos de ejemplo (una corrida representativa: la más cercana a la mediana)
        metricas = agregado["metricas_por_run"]
        beneficios = [m.beneficio_final for m in metricas]
        mediana_val = sorted(beneficios)[len(beneficios) // 2]
        mediana_idx = min(range(len(beneficios)), key=lambda k: abs(beneficios[k] - mediana_val))
        estado_ejemplo = resultados[mediana_idx]

        ejemplo_dir = caso_dir / "ejemplo"
        ejemplo_dir.mkdir(parents=True, exist_ok=True)
        generar_graficos(estado_ejemplo, output_dir=str(ejemplo_dir))

        print(f"  Gráficos guardados en: {caso_dir}/")
        if equilibrio_info.get("semana_mas_temprano") is not None:
            print(f"  Equilibrio: más temprano semana {equilibrio_info['semana_mas_temprano']}, "
                  f"más tardío semana {equilibrio_info['semana_mas_tardio']}")
        else:
            print(f"  Equilibrio: no alcanzado en el periodo")

    # Actualizar informe HTML con los puntos de equilibrio
    _actualizar_informe_equilibrios(output_base)

    print("\n" + "=" * 70)
    print("BENCHMARK CASOS RELEVANTES COMPLETADO")
    print("=" * 70)
    print(f"Salida: {output_base}/")
    print("\nGráficos generados por caso:")
    print("  - boxplot_beneficio_final.png")
    print("  - serie_beneficio_acumulado.png")
    print("  - ejemplo/perdidas_clientes.png")
    print("  - ejemplo/resultado_neto.png")
    print("  - ejemplo/satisfaccion_general.png")


if __name__ == "__main__":
    main()
