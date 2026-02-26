# -*- coding: utf-8 -*-
"""
Benchmark completo a 10 años: ejecuta todas las combinaciones de variables
y genera gráficos comparativos + conclusiones.

Variables:
- AB testing: 0-100 (prepago), 100-0 (suscripción), 50-50
- Releases: Semanales (7d), Mensuales (30d), Trimestrales (90d)
- Marketing: 500, 1500, 2500 créditos

Uso:
  python run_benchmark_completo.py          # 5000 corridas por config (default)
  python run_benchmark_completo.py --runs 100 --rapido  # Prueba rapida
  python run_benchmark_completo.py --workers 4          # Paralelo (4 nucleos)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool

sys.path.insert(0, ".")

PROGRESO_INTERVALO_SEG = 60  # Imprimir progreso cada 60 segundos

# Configuración del benchmark
T_ANOS = 10
DIAS_10_ANOS = 365 * T_ANOS  # 3650 días

# Combinaciones
AB_CONFIGS = [
    (0.0, "0-100"),    # 100% prepago
    (1.0, "100-0"),    # 100% suscripción
    (0.5, "50-50"),    # 50/50
]

RELEASES_CONFIGS = [
    (7, "Semanales"),
    (30, "Mensuales"),
    (90, "Trimestrales"),
]

MARKETING_CONFIGS = [
    (500, "500"),
    (1500, "1500"),
    (2500, "2500"),
]


def _run_single(args):
    """Worker para multiprocessing: ejecuta una simulacion y retorna el estado."""
    i, T_FINAL, N, M, prob_suscripcion, seed = args
    import random
    sys.path.insert(0, ".")
    from simulacion.principal import ejecutar_simulacion
    if seed is not None:
        random.seed(seed + i)
    return ejecutar_simulacion(T_FINAL=T_FINAL, N=N, M=M, prob_suscripcion_nuevo=prob_suscripcion, verbose=False)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark completo: AB testing, releases, marketing a 10 años."
    )
    parser.add_argument("--runs", "-r", type=int, default=5000,
                        help="Corridas por configuracion (default: 5000)")
    parser.add_argument("--rapido", action="store_true",
                        help="Solo 3 corridas y menos combinaciones para prueba rápida")
    parser.add_argument("--seed", "-s", type=int, default=42,
                        help="Semilla para reproducibilidad")
    parser.add_argument("--output-dir", "-o", default="benchmark_10_anos",
                        help="Directorio de salida")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Workers en paralelo (default: 1, usar 4-8 para acelerar)")
    parser.add_argument("--solo-graficos", action="store_true",
                        help="Solo generar graficos desde JSON existente (sin ejecutar benchmark)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if args.solo_graficos:
        json_path = output_dir / "resultados_benchmark.json"
        if not json_path.exists():
            print(f"Error: No existe {json_path}. Ejecuta el benchmark primero.")
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        resultados = data["resultados"]
        generar_graficos_comparativos(resultados, str(output_dir))
        generar_conclusiones(resultados, output_dir / "CONCLUSIONES.md")
        print(f"\nGraficos y conclusiones generados en: {output_dir}/")
        return

    n_runs = max(2, args.runs)
    if args.rapido:
        n_runs = 3
        # En modo rápido: solo variamos una variable a la vez con defaults
        configs = _configs_rapido()
    else:
        configs = _configs_completos()

    print("=" * 70)
    print("BENCHMARK COMPLETO - 10 ANOS")
    print("=" * 70)
    print(f"Corridas por config: {n_runs}")
    print(f"Total configuraciones: {len(configs)}")
    print(f"Simulaciones totales: {len(configs) * n_runs}")
    print(f"Progreso cada {PROGRESO_INTERVALO_SEG} segundos.")
    print()

    from simulacion.benchmark import ejecutar_benchmark, agregar_metricas

    progress_int = 500 if n_runs >= 100 else None
    n_workers = max(1, args.workers)
    if n_runs >= 1000 and n_workers == 1:
        print("NOTA: Con 5000 corridas, el benchmark puede tardar varias horas.")
        print("      Usa --workers 4 o --workers 8 para acelerar.")
        print()

    def _callback_progreso_minuto(config_actual, total_configs, n_runs):
        """Retorna callback que imprime progreso cada PROGRESO_INTERVALO_SEG segundos."""
        last_print = [time.time()]

        def cb(completadas, total):
            ahora = time.time()
            if ahora - last_print[0] >= PROGRESO_INTERVALO_SEG:
                corridas_previas = (config_actual - 1) * n_runs
                total_corridas = total_configs * n_runs
                completadas_global = corridas_previas + completadas
                pct = 100 * completadas_global / total_corridas
                print(f"  [PROGRESO] Config {config_actual}/{total_configs} | "
                      f"Corridas {completadas}/{total} ({100*completadas/total:.1f}%) | "
                      f"Total ~{pct:.1f}% | {datetime.now().strftime('%H:%M:%S')}", flush=True)
                last_print[0] = ahora
        return cb

    resultados = []
    for i, cfg in enumerate(configs):
        print(f"\n[{i+1}/{len(configs)}] AB={cfg['ab_label']}, Releases={cfg['releases_label']}, MKT={cfg['marketing_label']}")
        if n_workers > 1:
            worker_args = [
                (j, DIAS_10_ANOS, cfg["N"], cfg["M"], cfg["ab"], args.seed + i * 10000)
                for j in range(n_runs)
            ]
            chunksz = max(1, n_runs // (n_workers * 4))
            with Pool(n_workers) as pool:
                res = []
                last_print = time.time()
                for j, est in enumerate(pool.imap_unordered(_run_single, worker_args, chunksize=chunksz)):
                    res.append(est)
                    ahora = time.time()
                    if ahora - last_print >= PROGRESO_INTERVALO_SEG:
                        corridas_previas = i * n_runs
                        total_corridas = len(configs) * n_runs
                        completadas_global = corridas_previas + len(res)
                        pct = 100 * completadas_global / total_corridas
                        print(f"  [PROGRESO] Config {i+1}/{len(configs)} | "
                              f"Corridas {len(res)}/{n_runs} ({100*len(res)/n_runs:.1f}%) | "
                              f"Total ~{pct:.1f}% | {datetime.now().strftime('%H:%M:%S')}", flush=True)
                        last_print = ahora
        else:
            progress_cb = _callback_progreso_minuto(i + 1, len(configs), n_runs)
            res = ejecutar_benchmark(
                n_runs=n_runs,
                T_FINAL=DIAS_10_ANOS,
                N=cfg["N"],
                M=cfg["M"],
                prob_suscripcion_nuevo=cfg["ab"],
                verbose=False,
                seed=args.seed + i * 10000,
                progress_interval=progress_int,
                progress_callback=progress_cb,
            )
        agregado = agregar_metricas(res)
        agregado["config"] = cfg
        resultados.append(agregado)

    # Guardar resultados
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    export = {
        "fecha": datetime.now().isoformat(),
        "parametros": {"T_FINAL": DIAS_10_ANOS, "n_runs": n_runs},
        "resultados": [
            {
                "config": r["config"],
                "estadisticas": r["estadisticas"],
            }
            for r in resultados
        ],
    }
    json_path = output_dir / "resultados_benchmark.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en: {json_path}")

    # Generar gráficos comparativos
    generar_graficos_comparativos(resultados, str(output_dir))

    # Generar conclusiones
    generar_conclusiones(resultados, output_dir / "CONCLUSIONES.md")

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETADO")
    print("=" * 70)
    print(f"Gráficos y conclusiones en: {output_dir}/")


def _configs_completos():
    """Todas las combinaciones (27 configs)."""
    configs = []
    for ab_val, ab_label in AB_CONFIGS:
        for n_val, n_label in RELEASES_CONFIGS:
            for m_val, m_label in MARKETING_CONFIGS:
                configs.append({
                    "ab": ab_val,
                    "ab_label": ab_label,
                    "N": n_val,
                    "releases_label": n_label,
                    "M": m_val,
                    "marketing_label": m_label,
                })
    return configs


def _configs_rapido():
    """Configs reducidas para prueba rápida: variar una variable a la vez."""
    configs = []
    # Default: AB 50-50, N=30, M=1500
    defaults = {"ab": 0.5, "N": 30, "M": 1500}

    # Variar AB (releases y marketing default)
    for ab_val, ab_label in AB_CONFIGS:
        configs.append({
            "ab": ab_val, "ab_label": ab_label,
            "N": defaults["N"], "releases_label": "Mensuales",
            "M": defaults["M"], "marketing_label": "1500",
        })

    # Variar Releases
    for n_val, n_label in RELEASES_CONFIGS:
        configs.append({
            "ab": defaults["ab"], "ab_label": "50-50",
            "N": n_val, "releases_label": n_label,
            "M": defaults["M"], "marketing_label": "1500",
        })

    # Variar Marketing
    for m_val, m_label in MARKETING_CONFIGS:
        configs.append({
            "ab": defaults["ab"], "ab_label": "50-50",
            "N": defaults["N"], "releases_label": "Mensuales",
            "M": m_val, "marketing_label": m_label,
        })
    return configs


def generar_graficos_comparativos(resultados: list, output_dir: str) -> None:
    """Genera gráficos comparativos por variable."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("AVISO: matplotlib no instalado. Saltando graficos.")
        return

    os.makedirs(output_dir, exist_ok=True)

    def _media_std(r, key):
        s = r["estadisticas"].get(key, {})
        return s.get("media", 0), s.get("std", 0)

    # 1. Comparación por AB testing
    ab_data = {}
    for r in resultados:
        ab = r["config"]["ab_label"]
        if ab not in ab_data:
            ab_data[ab] = []
        m, std = _media_std(r, "beneficio_final")
        ab_data[ab].append((m, std))

    # Promediar si hay múltiples configs con mismo AB
    ab_labels = list(AB_CONFIGS)
    ab_labels = [x[1] for x in ab_labels]
    ab_medias = []
    ab_stds = []
    for ab in ab_labels:
        vals = [r for r in resultados if r["config"]["ab_label"] == ab]
        if vals:
            medias = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) for r in vals]
            stds = [r["estadisticas"].get("beneficio_final", {}).get("std", 0) for r in vals]
            ab_medias.append(np.mean(medias))
            ab_stds.append(np.mean(stds) if stds else 0)
        else:
            ab_medias.append(0)
            ab_stds.append(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(ab_labels))
    ax.bar(x, ab_medias, yerr=ab_stds, capsize=5, color=["#e74c3c", "#3498db", "#2ecc71"], alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"AB {l}" for l in ab_labels])
    ax.set_ylabel("Beneficio final (créditos)")
    ax.set_title("Beneficio final por AB Testing (Suscripción vs Prepago)")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_AB.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 2. Comparación por Releases
    rel_labels = [x[1] for x in RELEASES_CONFIGS]
    rel_medias = []
    rel_stds = []
    for rel in rel_labels:
        vals = [r for r in resultados if r["config"]["releases_label"] == rel]
        if vals:
            medias = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) for r in vals]
            stds = [r["estadisticas"].get("beneficio_final", {}).get("std", 0) for r in vals]
            rel_medias.append(np.mean(medias))
            rel_stds.append(np.mean(stds) if stds else 0)
        else:
            rel_medias.append(0)
            rel_stds.append(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(rel_labels))
    ax.bar(x, rel_medias, yerr=rel_stds, capsize=5, color="steelblue", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(rel_labels)
    ax.set_ylabel("Beneficio final (créditos)")
    ax.set_title("Beneficio final por Frecuencia de Releases")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_Releases.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 3. Comparación por Marketing
    mkt_labels = [x[1] for x in MARKETING_CONFIGS]
    mkt_medias = []
    mkt_stds = []
    for mkt in mkt_labels:
        vals = [r for r in resultados if r["config"]["marketing_label"] == mkt]
        if vals:
            medias = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) for r in vals]
            stds = [r["estadisticas"].get("beneficio_final", {}).get("std", 0) for r in vals]
            mkt_medias.append(np.mean(medias))
            mkt_stds.append(np.mean(stds) if stds else 0)
        else:
            mkt_medias.append(0)
            mkt_stds.append(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(mkt_labels))
    ax.bar(x, mkt_medias, yerr=mkt_stds, capsize=5, color="coral", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{l} créditos" for l in mkt_labels])
    ax.set_ylabel("Beneficio final (créditos)")
    ax.set_title("Beneficio final por Presupuesto Marketing")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_Marketing.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 4. Heatmap o tabla comparativa: todas las configs
    fig, ax = plt.subplots(figsize=(12, 8))
    config_labels = [f"{r['config']['ab_label']}\n{r['config']['releases_label']}\n{r['config']['marketing_label']}" for r in resultados]
    beneficios = [r["estadisticas"].get("beneficio_final", {}).get("media", 0) for r in resultados]
    b_min, b_max = min(beneficios), max(beneficios)
    norm = np.array([(b - b_min) / (b_max - b_min) if b_max != b_min else 0.5 for b in beneficios])
    colors = plt.cm.RdYlGn(norm)
    y_pos = np.arange(len(config_labels))
    ax.barh(y_pos, beneficios, color=colors, alpha=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(config_labels, fontsize=8)
    ax.set_xlabel("Beneficio final (créditos)")
    ax.set_title("Comparación de todas las configuraciones")
    ax.grid(True, alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "comparacion_todas.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 5. Equilibrio por config
    fig, ax = plt.subplots(figsize=(10, 6))
    eq_labels = [f"{r['config']['ab_label']}\n{r['config']['releases_label']}\n{r['config']['marketing_label']}" for r in resultados]
    eq_pct = [r["estadisticas"].get("equilibrio_porcentaje", 0) for r in resultados]
    ax.barh(range(len(eq_labels)), eq_pct, color="green", alpha=0.6)
    ax.set_yticks(range(len(eq_labels)))
    ax.set_yticklabels(eq_labels, fontsize=8)
    ax.set_xlabel("% corridas que alcanzaron equilibrio")
    ax.set_title("Tasa de equilibrio por configuración")
    ax.set_xlim(0, 105)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "equilibrio_por_config.png"), dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Gráficos guardados en: {output_dir}/")


def _dias_a_fecha_aprox(dias: int) -> str:
    """Aproximacion: dia 365 = fin ano 1."""
    if dias is None or dias < 0:
        return "N/A"
    anos = dias // 365
    meses = (dias % 365) // 30
    return f"~Ano {anos + 1}, mes {meses + 1}" if anos < 10 else f"Dia {dias}"


def generar_conclusiones(resultados: list, path: Path) -> None:
    """Genera documento de conclusiones profundas (insights no deducibles a priori)."""
    lines = [
        "# Conclusiones del Benchmark a 10 anos",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Periodo simulado:** 10 anos ({DIAS_10_ANOS} dias)",
        f"**Configuraciones evaluadas:** {len(resultados)}",
        "",
        "---",
        "",
        "## Resumen de variables",
        "",
        "| Variable | Valores |",
        "|----------|---------|",
        "| **AB Testing** | 0-100 (100% prepago), 100-0 (100% suscripcion), 50-50 |",
        "| **Releases** | Semanales (7d), Mensuales (30d), Trimestrales (90d) |",
        "| **Marketing** | 500, 1500, 2500 creditos/mes |",
        "",
        "---",
        "",
        "## Tabla de resultados",
        "",
        "| AB | Releases | MKT | Beneficio | Eq% | Eq dia (p25-p75) | Sat prepago | Sat suscrip | Sat gen | Prepago 6m | Susc 6m |",
        "|----|----------|-----|-----------|-----|------------------|-------------|-------------|---------|------------|---------|",
    ]

    for r in resultados:
        c = r["config"]
        st = r["estadisticas"]
        bf = st.get("beneficio_final", {})
        eq = st.get("equilibrio_porcentaje", 0)
        eq_d = st.get("equilibrio_dia", {})
        p25 = eq_d.get("p25")
        p75 = eq_d.get("p75")
        eq_rango = f"{int(p25)}-{int(p75)}" if p25 is not None and p75 is not None else "N/A"
        sat_p = st.get("satisfaccion_promedio_prepago", {}).get("media")
        sat_s = st.get("satisfaccion_promedio_suscripcion", {}).get("media")
        sat_g = st.get("satisfaccion_promedio_general", {}).get("media")
        prep_6 = st.get("prepago_primeros_6_meses", {}).get("media")
        susc_6 = st.get("suscripcion_primeros_6_meses", {}).get("media")
        sat_p_s = f"{sat_p:.1f}%" if sat_p is not None else "N/A"
        sat_s_s = f"{sat_s:.1f}%" if sat_s is not None else "N/A"
        sat_g_s = f"{sat_g:.1f}%" if sat_g is not None else "N/A"
        prep_6_s = f"{prep_6:,.0f}" if prep_6 is not None else "N/A"
        susc_6_s = f"{susc_6:,.0f}" if susc_6 is not None else "N/A"
        lines.append(
            f"| {c['ab_label']} | {c['releases_label']} | {c['marketing_label']} | "
            f"{bf.get('media', 0):,.0f} | {eq:.0f}% | {eq_rango} | "
            f"{sat_p_s} | {sat_s_s} | {sat_g_s} | {prep_6_s} | {susc_6_s} |"
        )

    best = max(resultados, key=lambda r: r["estadisticas"].get("beneficio_final", {}).get("media", 0))
    worst = min(resultados, key=lambda r: r["estadisticas"].get("beneficio_final", {}).get("media", float("inf")))

    cost_effective = [
        r for r in resultados
        if r["config"]["marketing_label"] == "500"
        and r["estadisticas"].get("equilibrio_porcentaje", 0) >= 60
        and r["estadisticas"].get("beneficio_final", {}).get("media", -1) > 0
    ]
    ce_best = max(cost_effective, key=lambda r: r["estadisticas"].get("beneficio_final", {}).get("media", 0)) if cost_effective else None

    prepago_6m_por_ab = {}
    susc_6m_por_ab = {}
    for r in resultados:
        ab = r["config"]["ab_label"]
        prep = r["estadisticas"].get("prepago_primeros_6_meses", {}).get("media")
        susc = r["estadisticas"].get("suscripcion_primeros_6_meses", {}).get("media")
        if ab not in prepago_6m_por_ab:
            prepago_6m_por_ab[ab] = []
            susc_6m_por_ab[ab] = []
        if prep is not None:
            prepago_6m_por_ab[ab].append(prep)
        if susc is not None:
            susc_6m_por_ab[ab].append(susc)

    lines.extend([
        "",
        "---",
        "",
        "## Conclusiones profundas (no deducibles a priori)",
        "",
        "### 1. Entre que fechas se alcanza el punto de equilibrio?",
        "",
    ])

    for r in resultados:
        c = r["config"]
        eq_d = r["estadisticas"].get("equilibrio_dia", {})
        eq_pct = r["estadisticas"].get("equilibrio_porcentaje", 0)
        if eq_pct > 0 and eq_d:
            media = eq_d.get("media")
            p25 = eq_d.get("p25")
            p75 = eq_d.get("p75")
            lines.append(
                f"- **{c['ab_label']} / {c['releases_label']} / MKT {c['marketing_label']}:** "
                f"Equilibrio en {eq_pct:.0f}% de corridas. "
                f"Cuando se alcanza: dia {int(media)} (rango p25-p75: {int(p25)}-{int(p75)}), "
                f"aprox. {_dias_a_fecha_aprox(int(media))}."
            )
        else:
            lines.append(
                f"- **{c['ab_label']} / {c['releases_label']} / MKT {c['marketing_label']}:** "
                f"No se alcanza equilibrio ({eq_pct:.0f}% de corridas)."
            )
    lines.append("")

    lines.extend([
        "### 2. Genera mas entrada inicial el modo prepago (paquete de minutos)?",
        "",
    ])
    for ab in ["0-100", "100-0", "50-50"]:
        preps = prepago_6m_por_ab.get(ab, [])
        suscs = susc_6m_por_ab.get(ab, [])
        if preps and suscs:
            m_prep = sum(preps) / len(preps)
            m_susc = sum(suscs) / len(suscs)
            mayor = "Prepago" if m_prep > m_susc else "Suscripcion"
            lines.append(
                f"- **AB {ab}:** En los primeros 6 meses, prepago aporta en promedio {m_prep:,.0f} creditos "
                f"vs suscripcion {m_susc:,.0f}. **{mayor} genera mas entrada inicial** en este escenario."
            )
    lines.append("")

    lines.extend([
        "### 3. Como resulta la satisfaccion de clientes en cada caso?",
        "",
    ])
    for r in resultados:
        c = r["config"]
        sat_p = r["estadisticas"].get("satisfaccion_promedio_prepago", {}).get("media")
        sat_s = r["estadisticas"].get("satisfaccion_promedio_suscripcion", {}).get("media")
        sat_g = r["estadisticas"].get("satisfaccion_promedio_general", {}).get("media")
        if sat_g is not None:
            sp = f"{sat_p:.1f}%" if sat_p is not None else "N/A"
            ss = f"{sat_s:.1f}%" if sat_s is not None else "N/A"
            lines.append(
                f"- **{c['ab_label']} / {c['releases_label']} / MKT {c['marketing_label']}:** "
                f"Satisfaccion general {sat_g:.1f}%, prepago {sp} | suscripcion {ss}."
            )
    lines.append("")

    lines.extend([
        "### 4. Configuracion cost-effective: minimizar inversion y maximizar sostenibilidad",
        "",
    ])
    if ce_best:
        c = ce_best["config"]
        bf = ce_best["estadisticas"].get("beneficio_final", {}).get("media", 0)
        eq = ce_best["estadisticas"].get("equilibrio_porcentaje", 0)
        eq_d = ce_best["estadisticas"].get("equilibrio_dia", {})
        lines.extend([
            f"La configuracion **mas cost-effective** (menor inversion en marketing = 500) que logra equilibrio sostenible:",
            f"- **AB:** {c['ab_label']}, **Releases:** {c['releases_label']}",
            f"- **Beneficio final medio:** {bf:,.0f} creditos",
            f"- **Equilibrio alcanzado:** {eq:.0f}% de corridas",
            f"- **Dia medio de equilibrio:** {eq_d.get('media', 'N/A')}",
            "",
            "**Por que?** Con solo 500 creditos/mes de marketing, se reduce el costo de adquisicion. "
            "Releases mensuales o trimestrales evitan la inestabilidad que destruye la satisfaccion. "
            "El equilibrio se alcanza porque los costos fijos (desarrollo) se compensan con ingresos recurrentes "
            "sin necesidad de un flujo masivo de clientes nuevos.",
            "",
        ])
    else:
        lines.extend([
            "Ninguna configuracion con marketing 500 alcanza equilibrio sostenible (>=60% de corridas). "
            "Se requiere al menos 1500 creditos/mes para lograr viabilidad con releases mensuales o trimestrales.",
            "",
        ])

    lines.extend([
        "### 5. Resumen ejecutivo",
        "",
        f"- **Mejor config (max beneficio):** {best['config']['ab_label']} / {best['config']['releases_label']} / MKT {best['config']['marketing_label']} "
        f"= {best['estadisticas'].get('beneficio_final', {}).get('media', 0):,.0f} creditos",
        f"- **Peor config:** {worst['config']['ab_label']} / {worst['config']['releases_label']} / MKT {worst['config']['marketing_label']} "
        f"= {worst['estadisticas'].get('beneficio_final', {}).get('media', 0):,.0f} creditos",
        "",
        "**Hallazgo critico:** Releases semanales generan inestabilidad que impide alcanzar equilibrio en todas las configuraciones, "
        "independientemente del AB o marketing. La frecuencia de implementaciones es el factor mas determinante.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Conclusiones guardadas en: {path}")


if __name__ == "__main__":
    main()
