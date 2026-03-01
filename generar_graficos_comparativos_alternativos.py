# -*- coding: utf-8 -*-
"""
Genera gráficos comparativos alternativos desde resultados_benchmark.json existente.
NO ejecuta la simulación: solo lee el JSON y crea visualizaciones más legibles.

Alternativas al gráfico comparacion_todas.png (demasiado denso en eje Y):
1. Heatmaps: Beneficio por AB × Releases, uno por cada presupuesto Marketing
2. Top 10 y Bottom 10: Solo las mejores y peores configuraciones
3. Comparativo ordenado: Barras ordenadas por beneficio (legible)

Uso:
  python generar_graficos_comparativos_alternativos.py
  python generar_graficos_comparativos_alternativos.py --output benchmark_10_anos
"""

import argparse
import json
import os
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


AB_LABELS = ["0-100", "100-0", "50-50"]
RELEASES_LABELS = ["Semanales", "Mensuales", "Trimestrales"]
MARKETING_LABELS = ["500", "1500", "2500"]


def cargar_resultados(json_path: Path) -> list:
    """Carga resultados desde JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["resultados"]


def generar_heatmaps_beneficio(resultados: list, output_dir: str) -> None:
    """
    Heatmaps AB × Releases, uno por cada presupuesto de Marketing.
    Cada celda muestra el beneficio medio en millones de créditos.
    """
    beneficio_dict = {}
    for r in resultados:
        ab = r["config"]["ab_label"]
        rel = r["config"]["releases_label"]
        mkt = r["config"]["marketing_label"]
        bf = r["estadisticas"].get("beneficio_final", {}).get("media", 0)
        beneficio_dict[(ab, rel, mkt)] = bf / 1e6  # en millones

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    vmin = min(beneficio_dict.values())
    vmax = max(beneficio_dict.values())
    # Centrar colormap en 0 si hay positivos y negativos
    if vmin < 0 < vmax:
        vabs = max(abs(vmin), abs(vmax))
        vmin, vmax = -vabs, vabs

    for idx, mkt in enumerate(MARKETING_LABELS):
        ax = axes[idx]
        mat = np.array([
            [beneficio_dict.get((ab, rel, mkt), 0) for rel in RELEASES_LABELS]
            for ab in AB_LABELS
        ])
        im = ax.imshow(mat, cmap="RdYlGn", vmin=vmin, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(RELEASES_LABELS)))
        ax.set_xticklabels(RELEASES_LABELS)
        ax.set_yticks(range(len(AB_LABELS)))
        ax.set_yticklabels([f"AB {l}" for l in AB_LABELS])
        ax.set_title(f"Marketing {mkt} créditos/mes")
        if idx == 0:
            ax.set_ylabel("AB Testing")
        ax.set_xlabel("Frecuencia releases")
        for i in range(len(AB_LABELS)):
            for j in range(len(RELEASES_LABELS)):
                val = mat[i, j]
                txt = f"{val:.1f}M" if abs(val) >= 1 else f"{val:.2f}M"
                color = "black" if 0.3 < (val - vmin) / (vmax - vmin) < 0.7 else "white"
                ax.text(j, i, txt, ha="center", va="center", fontsize=10, color=color)

    fig.suptitle("Beneficio final (millones de créditos) por configuración", fontsize=12, y=1.02)
    fig.colorbar(im, ax=axes, shrink=0.6, label="Beneficio (M créditos)")
    plt.subplots_adjust(top=0.88)
    fig.savefig(os.path.join(output_dir, "comparacion_heatmap_beneficio.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> comparacion_heatmap_beneficio.png")


def generar_top_bottom(resultados: list, output_dir: str, n: int = 10) -> None:
    """
    Gráfico de barras horizontales: Top N y Bottom N configuraciones.
    Etiquetas legibles porque solo hay 2*N barras.
    """
    sorted_res = sorted(
        resultados,
        key=lambda r: r["estadisticas"].get("beneficio_final", {}).get("media", 0),
        reverse=True
    )
    top = sorted_res[:n]
    bottom = sorted_res[-n:]

    def _label(r):
        c = r["config"]
        return f"{c['ab_label']} / {c['releases_label']} / MKT{c['marketing_label']}"

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    colors_top = plt.cm.Greens(np.linspace(0.4, 0.9, n))
    colors_bot = plt.cm.Reds(np.linspace(0.4, 0.9, n))

    # Top N
    ax1 = axes[0]
    labels_top = [_label(r) for r in top]
    vals_top = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) / 1e6 for r in top]
    y_pos = np.arange(len(labels_top))
    ax1.barh(y_pos, vals_top, color=colors_top, alpha=0.85)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels_top, fontsize=9)
    ax1.set_xlabel("Beneficio final (millones créditos)")
    ax1.set_title(f"Top {n} configuraciones (mayor beneficio)")
    ax1.grid(True, alpha=0.3, axis="x")
    ax1.axvline(0, color="black", linewidth=0.5)

    # Bottom N
    ax2 = axes[1]
    labels_bot = [_label(r) for r in bottom]
    vals_bot = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) / 1e6 for r in bottom]
    y_pos = np.arange(len(labels_bot))
    ax2.barh(y_pos, vals_bot, color=colors_bot, alpha=0.85)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels_bot, fontsize=9)
    ax2.set_xlabel("Beneficio final (millones créditos)")
    ax2.set_title(f"Bottom {n} configuraciones (menor beneficio)")
    ax2.grid(True, alpha=0.3, axis="x")
    ax2.axvline(0, color="black", linewidth=0.5)

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_top_bottom.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> comparacion_top_bottom.png")


def generar_por_marketing(resultados: list, output_dir: str) -> None:
    """
    Tres gráficos: uno por presupuesto Marketing.
    Cada uno muestra AB × Releases (9 barras) con etiquetas legibles.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    for idx, mkt in enumerate(MARKETING_LABELS):
        ax = axes[idx]
        vals = [r for r in resultados if r["config"]["marketing_label"] == mkt]
        labels = [f"{r['config']['ab_label']}\n{r['config']['releases_label']}" for r in vals]
        beneficios = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) / 1e6 for r in vals]
        colors = ["#2ecc71" if b >= 0 else "#e74c3c" for b in beneficios]
        x = np.arange(len(labels))
        ax.bar(x, beneficios, color=colors, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=15)
        ax.set_ylabel("Beneficio (M créditos)")
        ax.set_title(f"Marketing {mkt} créditos/mes")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.grid(True, alpha=0.3, axis="y")

    fig.suptitle("Beneficio final por AB × Releases (desglose por Marketing)", fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_por_marketing.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> comparacion_por_marketing.png")


def generar_por_releases(resultados: list, output_dir: str) -> None:
    """
    Tres gráficos: uno por frecuencia de releases.
    Cada uno muestra AB × Marketing (9 barras).
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    for idx, rel in enumerate(RELEASES_LABELS):
        ax = axes[idx]
        vals = [r for r in resultados if r["config"]["releases_label"] == rel]
        labels = [f"{r['config']['ab_label']}\nMKT{r['config']['marketing_label']}" for r in vals]
        beneficios = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) / 1e6 for r in vals]
        colors = ["#2ecc71" if b >= 0 else "#e74c3c" for b in beneficios]
        x = np.arange(len(labels))
        ax.bar(x, beneficios, color=colors, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=15)
        ax.set_ylabel("Beneficio (M créditos)")
        ax.set_title(f"Releases {rel}")
        ax.axhline(0, color="black", linewidth=0.5)
        ax.grid(True, alpha=0.3, axis="y")

    fig.suptitle("Beneficio final por AB × Marketing (desglose por Releases)", fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_por_releases.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  -> comparacion_por_releases.png")


def main():
    parser = argparse.ArgumentParser(
        description="Genera gráficos comparativos alternativos desde JSON (sin re-ejecutar simulación)."
    )
    parser.add_argument("--output", "-o", default="benchmark_10_anos",
                        help="Directorio con resultados_benchmark.json y salida de gráficos")
    parser.add_argument("--top-n", type=int, default=10,
                        help="Número de configs en Top/Bottom (default: 10)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    json_path = output_dir / "resultados_benchmark.json"
    if not json_path.exists():
        print(f"Error: No existe {json_path}")
        print("Ejecuta primero el benchmark o indica el directorio correcto con --output")
        return 1

    if not HAS_MATPLOTLIB:
        print("Error: matplotlib no instalado. Instala con: pip install matplotlib")
        return 1

    print("Cargando resultados...")
    resultados = cargar_resultados(json_path)
    print(f"  {len(resultados)} configuraciones cargadas")
    print("\nGenerando gráficos alternativos:")

    generar_heatmaps_beneficio(resultados, str(output_dir))
    generar_top_bottom(resultados, str(output_dir), n=args.top_n)
    generar_por_marketing(resultados, str(output_dir))
    generar_por_releases(resultados, str(output_dir))

    print(f"\nGráficos guardados en: {output_dir}/")
    return 0


if __name__ == "__main__":
    exit(main())
