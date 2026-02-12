# -*- coding: utf-8 -*-
"""
Generación de gráficos semana a semana para la simulación.
Muestra satisfacción (prepago, suscripción, general) y métricas principales.
"""

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .estado import EstadoSimulacion


def generar_graficos(est: "EstadoSimulacion", output_dir: str = "graficos") -> None:
    """
    Genera gráficos PNG a partir de las métricas semanales capturadas.
    Crea el directorio de salida si no existe.
    Requiere: pip install matplotlib
    """
    try:
        import matplotlib
    except ImportError:
        raise ImportError(
            "Se requiere matplotlib para generar gráficos. Instálalo con: pip install matplotlib"
        ) from None
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not est.metricas_semanales:
        return

    os.makedirs(output_dir, exist_ok=True)
    semanas = [m["semana"] for m in est.metricas_semanales]

    # Configuración de estilo
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["axes.grid"] = True

    # 1. Satisfacción prepago
    prep_sat = [m["satisfaccion"]["prepago_satisfechos_pct"] for m in est.metricas_semanales]
    prep_insat = [m["satisfaccion"]["prepago_insatisfechos_pct"] for m in est.metricas_semanales]
    _grafico_satisfaccion(
        semanas, prep_sat, prep_insat,
        "Satisfacción Prepago (Semana a Semana)",
        "Satisfechos", "Insatisfechos",
        os.path.join(output_dir, "satisfaccion_prepago.png"),
    )

    # 2. Satisfacción suscripción
    susc_sat = [m["satisfaccion"]["suscripcion_satisfechos_pct"] for m in est.metricas_semanales]
    susc_insat = [m["satisfaccion"]["suscripcion_insatisfechos_pct"] for m in est.metricas_semanales]
    _grafico_satisfaccion(
        semanas, susc_sat, susc_insat,
        "Satisfacción Suscripción (Semana a Semana)",
        "Satisfechos", "Insatisfechos",
        os.path.join(output_dir, "satisfaccion_suscripcion.png"),
    )

    # 3. Satisfacción general
    gen_sat = [m["satisfaccion"]["general_satisfechos_pct"] for m in est.metricas_semanales]
    gen_insat = [m["satisfaccion"]["general_insatisfechos_pct"] for m in est.metricas_semanales]
    _grafico_satisfaccion(
        semanas, gen_sat, gen_insat,
        "Satisfacción General - Clientes con Paquetes (Semana a Semana)",
        "Satisfechos", "Insatisfechos",
        os.path.join(output_dir, "satisfaccion_general.png"),
    )

    # 4. Gráfico de beneficios
    fig, ax = plt.subplots(figsize=(10, 6))
    trabajos = [m["beneficios"]["trabajos"] for m in est.metricas_semanales]
    prepago = [m["beneficios"]["prepago"] for m in est.metricas_semanales]
    suscripcion = [m["beneficios"]["suscripcion"] for m in est.metricas_semanales]
    total = [m["beneficios"]["total_acumulado"] for m in est.metricas_semanales]

    ax.plot(semanas, trabajos, marker="o", markersize=4, label="Trabajos")
    ax.plot(semanas, prepago, marker="s", markersize=4, label="Prepago")
    ax.plot(semanas, suscripcion, marker="^", markersize=4, label="Suscripción")
    ax.plot(semanas, total, marker="D", markersize=4, label="Total acumulado", linewidth=2)

    ax.set_xlabel("Semana")
    ax.set_ylabel("Beneficio (créditos)")
    ax.set_title("Beneficios Netos (Semana a Semana)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "beneficios.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 5. Gráfico de costos
    fig, ax = plt.subplots(figsize=(10, 6))
    desarrollo = [m["costos"]["desarrollo"] for m in est.metricas_semanales]
    marketing = [m["costos"]["marketing"] for m in est.metricas_semanales]
    tecnicos = [m["costos"]["tecnicos"] for m in est.metricas_semanales]
    resarcimiento = [m["costos"]["resarcimiento"] for m in est.metricas_semanales]

    ax.plot(semanas, desarrollo, marker="o", markersize=4, label="Desarrollo")
    ax.plot(semanas, marketing, marker="s", markersize=4, label="Marketing")
    ax.plot(semanas, tecnicos, marker="^", markersize=4, label="Técnicos")
    ax.plot(semanas, resarcimiento, marker="D", markersize=4, label="Resarcimiento")

    ax.set_xlabel("Semana")
    ax.set_ylabel("Costo (créditos)")
    ax.set_title("Costos Acumulados (Semana a Semana)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "costos.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 6. Gráfico de clientes
    fig, ax = plt.subplots(figsize=(10, 6))
    susc_tot = [m["clientes"]["suscripciones_totales"] for m in est.metricas_semanales]
    prep_tot = [m["clientes"]["prepagos_totales"] for m in est.metricas_semanales]
    trabajo_aislado = [m["clientes"]["trabajo_aislado"] for m in est.metricas_semanales]
    pe_paquetes = [m["clientes"]["pe_con_paquetes"] for m in est.metricas_semanales]

    ax.plot(semanas, susc_tot, marker="o", markersize=4, label="Suscripciones")
    ax.plot(semanas, prep_tot, marker="s", markersize=4, label="Prepagos")
    ax.plot(semanas, trabajo_aislado, marker="^", markersize=4, label="Trabajo Aislado")
    ax.plot(semanas, pe_paquetes, marker="D", markersize=4, label="PE con paquetes")

    ax.set_xlabel("Semana")
    ax.set_ylabel("Cantidad")
    ax.set_title("Clientes por Tipo (Semana a Semana)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "clientes.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 7. Gráfico combinado de satisfacción (subplots)
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    axes[0].plot(semanas, prep_sat, "g-", marker="o", markersize=4, label="Satisfechos")
    axes[0].plot(semanas, prep_insat, "r-", marker="s", markersize=4, label="Insatisfechos")
    axes[0].set_ylabel("%")
    axes[0].set_title("Prepago")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(semanas, susc_sat, "g-", marker="o", markersize=4, label="Satisfechos")
    axes[1].plot(semanas, susc_insat, "r-", marker="s", markersize=4, label="Insatisfechos")
    axes[1].set_ylabel("%")
    axes[1].set_title("Suscripción")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(semanas, gen_sat, "g-", marker="o", markersize=4, label="Satisfechos")
    axes[2].plot(semanas, gen_insat, "r-", marker="s", markersize=4, label="Insatisfechos")
    axes[2].set_xlabel("Semana")
    axes[2].set_ylabel("%")
    axes[2].set_title("General (clientes con paquetes)")
    axes[2].legend(loc="best")
    axes[2].grid(True, alpha=0.3)

    fig.suptitle("Satisfacción de Clientes (Semana a Semana)", fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "satisfaccion_combinado.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 8. Gráfico de resultado neto (acumulado con línea de equilibrio)
    total_acum = [m["beneficios"]["total_acumulado"] for m in est.metricas_semanales]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(semanas, total_acum, color="steelblue", linewidth=2, label="Resultado neto acumulado")
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=1.5, label="Equilibrio (cero)")
    ax.fill_between(semanas, total_acum, 0, where=[v >= 0 for v in total_acum], alpha=0.3, color="green")
    ax.fill_between(semanas, total_acum, 0, where=[v < 0 for v in total_acum], alpha=0.3, color="red")
    ax.set_xlabel("Semana")
    ax.set_ylabel("Créditos (acumulado)")
    ax.set_title("Resultado Neto Acumulado (Semana a Semana)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "resultado_neto.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # 9. Gráfico de pérdidas de clientes por razón y total
    _grafico_perdidas_clientes(est.metricas_semanales, output_dir)


def _grafico_perdidas_clientes(metricas_semanales: list, output_dir: str) -> None:
    import matplotlib.pyplot as plt

    if not metricas_semanales or "perdidas" not in metricas_semanales[0]:
        return

    semanas = [m["semana"] for m in metricas_semanales]
    susc = [m["perdidas"].get("suscripcion_no_renovacion", 0) for m in metricas_semanales]
    prep = [m["perdidas"].get("prepago_no_renovacion", 0) for m in metricas_semanales]
    prep_abandono = [m["perdidas"].get("prepago_abandono_insatisfecho", 0) for m in metricas_semanales]
    ta = [m["perdidas"].get("trabajo_aislado_insatisfecho", 0) for m in metricas_semanales]
    cal_sin_tec = [m["perdidas"].get("calendarizacion_sin_tecnico", 0) for m in metricas_semanales]
    total = [m["perdidas_total"] for m in metricas_semanales]

    fig, axes = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

    # Subplot 1: pérdidas por razón (líneas)
    ax1 = axes[0]
    ax1.plot(semanas, susc, marker="o", markersize=4, label="Suscripción (no renovación)")
    ax1.plot(semanas, prep, marker="s", markersize=4, label="Prepago (no renovación)")
    ax1.plot(semanas, prep_abandono, marker="x", markersize=4, label="Prepago (abandono insatisfecho)")
    ax1.plot(semanas, ta, marker="^", markersize=4, label="Trabajo aislado (insatisfecho)")
    ax1.plot(semanas, cal_sin_tec, marker="d", markersize=4, label="Calendarización sin técnico")
    ax1.set_ylabel("Clientes perdidos")
    ax1.set_title("Pérdidas de Clientes por Razón (Semana a Semana)")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(bottom=0)

    # Subplot 2: total de pérdidas semanales
    ax2 = axes[1]
    ax2.bar(semanas, total, 0.6, color="darkred", alpha=0.7, label="Total pérdidas")
    ax2.set_xlabel("Semana")
    ax2.set_ylabel("Total clientes perdidos")
    ax2.set_title("Total de Pérdidas de Clientes por Semana")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig(
        os.path.join(output_dir, "perdidas_clientes.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()


def _grafico_satisfaccion(
    semanas: list,
    satisfechos: list,
    insatisfechos: list,
    titulo: str,
    label_sat: str,
    label_insat: str,
    path: str,
) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(semanas, satisfechos, "g-", marker="o", markersize=4, label=label_sat)
    ax.plot(semanas, insatisfechos, "r-", marker="s", markersize=4, label=label_insat)
    ax.set_xlabel("Semana")
    ax.set_ylabel("Porcentaje (%)")
    ax.set_title(titulo)
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
