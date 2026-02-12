# -*- coding: utf-8 -*-
"""
Benchmark de simulación: ejecuta N corridas con los mismos parámetros,
extrae métricas agregadas y genera gráficos de distribuciones y series.
"""

import os
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from . import config as cfg

if TYPE_CHECKING:
    from .estado import EstadoSimulacion


def _beneficio_acumulado(est: "EstadoSimulacion") -> float:
    """Beneficio neto acumulado (ingresos netos - costos)."""
    return (
        est.BENEFICIO_NETO_TRABAJOS
        + est.BENEFICIO_NETO_PREPAGO
        + est.BENEFICIO_NETO_SUSCRIPCION
        - est.COSTOS_DESARROLLO
        - est.COSTO_MKT
    )


@dataclass
class MetricasResumen:
    """Métricas extraídas de una sola ejecución."""
    beneficio_final: float
    equilibrio_dia: Optional[int]
    mejor_trimestre_beneficio: float
    suscripciones_final: int
    prepagos_final: int
    pe_trabajo_aislado_final: int
    tecnicos_dev_final: int
    tecnicos_apps_it_final: int
    metricas_semanales: List[Dict[str, Any]] = field(default_factory=list)


def extraer_metricas(est: "EstadoSimulacion") -> MetricasResumen:
    """Extrae métricas de resumen de un EstadoSimulacion final."""
    return MetricasResumen(
        beneficio_final=_beneficio_acumulado(est),
        equilibrio_dia=est.T_EQUILIBRIO,
        mejor_trimestre_beneficio=est.MEJOR_TRIMESTRE.beneficio if est.MEJOR_TRIMESTRE.beneficio > float("-inf") else None,
        suscripciones_final=est.Suscripciones_Totales,
        prepagos_final=est.Prepagos_Totales,
        pe_trabajo_aislado_final=est.PE_Trabajo_Aislado,
        tecnicos_dev_final=est.Tecnicos_Dev,
        tecnicos_apps_it_final=est.Tecnicos_AppsIT,
        metricas_semanales=list(est.metricas_semanales),
    )


def _estadisticas(values: List[float]) -> Dict[str, float]:
    """Calcula media, desv. estándar, min, max y percentiles."""
    if not values:
        return {}
    valid = [v for v in values if v is not None]
    if not valid:
        return {}
    return {
        "media": statistics.mean(valid),
        "std": statistics.stdev(valid) if len(valid) > 1 else 0.0,
        "min": min(valid),
        "max": max(valid),
        "p25": float(statistics.quantiles(valid, n=4)[0]) if len(valid) >= 4 else valid[0],
        "p50": statistics.median(valid),
        "p75": float(statistics.quantiles(valid, n=4)[2]) if len(valid) >= 4 else valid[-1],
    }


def ejecutar_benchmark(
    n_runs: int,
    T_FINAL: int,
    N: int,
    M: float,
    verbose: bool = True,
    seed: Optional[int] = None,
) -> List["EstadoSimulacion"]:
    """
    Ejecuta n_runs simulaciones con los mismos parámetros.
    Si seed se proporciona, cada run usa seed + i para reproducibilidad.
    Retorna lista de EstadoSimulacion.
    """
    from .principal import ejecutar_simulacion
    import random

    resultados: List["EstadoSimulacion"] = []
    for i in range(n_runs):
        if seed is not None:
            random.seed(seed + i)
        if verbose:
            print(f"Ejecutando corrida {i + 1}/{n_runs}...")
        est = ejecutar_simulacion(T_FINAL=T_FINAL, N=N, M=M, verbose=False)
        resultados.append(est)
    return resultados


def agregar_metricas(resultados: List["EstadoSimulacion"]) -> Dict[str, Any]:
    """
    Extrae métricas de cada resultado y calcula estadísticas agregadas.
    Retorna un diccionario con métricas por run y estadísticas globales.
    """
    metricas_runs = [extraer_metricas(est) for est in resultados]

    # Valores numéricos para estadísticas
    beneficios = [m.beneficio_final for m in metricas_runs]
    equilibrios = [m.equilibrio_dia for m in metricas_runs if m.equilibrio_dia is not None]
    mejores_trim = [m.mejor_trimestre_beneficio for m in metricas_runs if m.mejor_trimestre_beneficio is not None]
    suscripciones = [m.suscripciones_final for m in metricas_runs]
    prepagos = [m.prepagos_final for m in metricas_runs]

    # Series temporales agregadas (promedio por semana)
    n_semanas = 0
    if metricas_runs and metricas_runs[0].metricas_semanales:
        n_semanas = len(metricas_runs[0].metricas_semanales)

    series_agregadas: Dict[str, List[Dict[str, float]]] = {}
    if n_semanas > 0:
        # total_acumulado por semana
        totales_por_semana: List[List[float]] = [[] for _ in range(n_semanas)]
        for m in metricas_runs:
            for w, ms in enumerate(m.metricas_semanales[:n_semanas]):
                totales_por_semana[w].append(ms["beneficios"]["total_acumulado"])

        series_agregadas["beneficio_acumulado"] = []
        for w in range(n_semanas):
            vals = totales_por_semana[w]
            series_agregadas["beneficio_acumulado"].append(_estadisticas(vals))

    return {
        "n_runs": len(resultados),
        "parametros": {"T_FINAL": resultados[0].T_FINAL, "N": resultados[0].DIAS_IMPLEMENTACION, "M": resultados[0].PRESUPUESTO_MKT_MENSUAL},
        "metricas_por_run": metricas_runs,
        "estadisticas": {
            "beneficio_final": _estadisticas(beneficios),
            "equilibrio_dia": _estadisticas([float(x) for x in equilibrios]) if equilibrios else {},
            "equilibrio_porcentaje": len(equilibrios) / len(resultados) * 100,
            "mejor_trimestre_beneficio": _estadisticas(mejores_trim) if mejores_trim else {},
            "suscripciones_final": _estadisticas(suscripciones),
            "prepagos_final": _estadisticas(prepagos),
        },
        "series_agregadas": series_agregadas,
    }


def generar_graficos_benchmark(agregado: Dict[str, Any], output_dir: str = "graficos_benchmark") -> None:
    """
    Genera gráficos de distribuciones (boxplots, histogramas) y series agregadas.
    """
    try:
        import matplotlib
    except ImportError:
        raise ImportError(
            "Se requiere matplotlib para generar gráficos. Instálalo con: pip install matplotlib"
        ) from None
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(output_dir, exist_ok=True)
    stats = agregado["estadisticas"]
    metricas_runs = agregado["metricas_por_run"]

    # 1. Boxplot de beneficio final
    beneficios = [m.beneficio_final for m in metricas_runs]
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(beneficios, vert=True, patch_artist=True)
    bp["boxes"][0].set_facecolor("lightblue")
    ax.set_ylabel("Beneficio final (créditos)")
    ax.set_title(f"Distribución del beneficio final ({agregado['n_runs']} corridas)")
    ax.set_xticklabels([f"n={agregado['n_runs']}"])
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "boxplot_beneficio_final.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 2. Histograma de beneficio final
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(beneficios, bins=min(30, max(5, len(beneficios) // 3)), color="steelblue", edgecolor="white", alpha=0.8)
    if stats.get("beneficio_final"):
        s = stats["beneficio_final"]
        ax.axvline(s["media"], color="red", linestyle="--", linewidth=2, label=f"Media: {s['media']:.0f}")
    ax.set_xlabel("Beneficio final (créditos)")
    ax.set_ylabel("Frecuencia")
    ax.set_title(f"Histograma de beneficio final ({agregado['n_runs']} corridas)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "histograma_beneficio_final.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 3. Serie temporal: beneficio acumulado (media ± desv. estándar)
    if "beneficio_acumulado" in agregado.get("series_agregadas", {}):
        series = agregado["series_agregadas"]["beneficio_acumulado"]
        semanas = list(range(len(series)))
        medias = [s["media"] for s in series]
        stds = [s["std"] for s in series]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(semanas, medias, color="steelblue", linewidth=2, label="Media")
        ax.fill_between(semanas, [m - st for m, st in zip(medias, stds)], [m + st for m, st in zip(medias, stds)], alpha=0.3, color="steelblue", label="± 1 σ")
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=1)
        ax.set_xlabel("Semana")
        ax.set_ylabel("Beneficio acumulado (créditos)")
        ax.set_title(f"Beneficio acumulado medio ± desv. estándar ({agregado['n_runs']} corridas)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "serie_beneficio_acumulado.png"), dpi=150, bbox_inches="tight")
        plt.close()

    # 4. Resumen de métricas (tabla como imagen o texto)
    # Generar un gráfico de barras comparando métricas clave
    metricas_nombres = [
        ("Beneficio final", "beneficio_final", "media"),
        ("Suscripciones final", "suscripciones_final", "media"),
        ("Prepagos final", "prepagos_final", "media"),
    ]
    labels = []
    means = []
    stds = []
    for nom, key, sub in metricas_nombres:
        if key in stats and stats[key]:
            labels.append(nom)
            means.append(stats[key].get("media", 0))
            stds.append(stats[key].get("std", 0))

    if labels:
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(labels))
        bars = ax.bar(x, means, yerr=stds, capsize=5, color="steelblue", alpha=0.8, edgecolor="navy")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=15, ha="right")
        ax.set_ylabel("Valor (media ± σ)")
        ax.set_title(f"Métricas agregadas ({agregado['n_runs']} corridas)")
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "metricas_agregadas.png"), dpi=150, bbox_inches="tight")
        plt.close()

    # 5. Distribución de día de equilibrio (si hay datos)
    equilibrios = [m.equilibrio_dia for m in metricas_runs if m.equilibrio_dia is not None]
    if equilibrios:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(equilibrios, bins=min(25, max(5, len(equilibrios) // 2)), color="green", edgecolor="white", alpha=0.7)
        ax.set_xlabel("Día de equilibrio")
        ax.set_ylabel("Frecuencia")
        ax.set_title(f"Día en que se alcanza equilibrio ({len(equilibrios)} de {agregado['n_runs']} corridas)")
        ax.grid(True, alpha=0.3, axis="y")
        fig.tight_layout()
        fig.savefig(os.path.join(output_dir, "histograma_equilibrio.png"), dpi=150, bbox_inches="tight")
        plt.close()
