# Simulación de Plataforma Técnica SaaS

Simulación por eventos discretos (día a día) de una plataforma que conecta técnicos con clientes. Incluye tres modalidades de pago (suscripción, prepago, trabajo aislado), satisfacción probabilística, calendarización e implementaciones periódicas.

**Documentación completa:** [Wiki](https://github.com/apacay/Simu-vAri/wiki) · [Uso](https://github.com/apacay/Simu-vAri/wiki/Uso) · [API](https://github.com/apacay/Simu-vAri/wiki/API) · [Arquitectura](https://github.com/apacay/Simu-vAri/wiki/Arquitectura) · [Métricas](https://github.com/apacay/Simu-vAri/wiki/Métricas) · [Glosario](https://github.com/apacay/Simu-vAri/wiki/Glosario)

## Requisitos

- Python 3.8 o superior. Ver [Instalación · Requisitos](https://github.com/apacay/Simu-vAri/wiki/Instalaci%C3%B3n#requisitos) para detalles.

## Estructura del proyecto

```
Ariel/
├── simulacion/
│   ├── __init__.py
│   ├── benchmark.py   # Benchmark: múltiples corridas, métricas agregadas
│   ├── config.py      # Constantes y parámetros
│   ├── estado.py      # Estado global (contadores, técnicos TPLL/TPS)
│   ├── graficos.py    # Gráficos de métricas semana a semana
│   ├── llegada.py     # Flujo de llegada (tipo, trabajo, asignación técnico, pago)
│   └── principal.py   # Bucle principal, contratación, rotación, equilibrio
├── graficos/            # PNG generados con run_simulacion --graficos
├── graficos_benchmark/  # PNG generados con run_benchmark --graficos
├── run_simulacion.py    # Punto de entrada (una corrida)
├── run_benchmark.py     # Benchmark: N corridas con métricas y gráficos
├── requirements.txt
└── README.md
```

## Cómo ejecutar

```bash
python run_simulacion.py --dias 365 --implementaciones 30 --marketing 2000 --ab-suscripcion 0.50
```

Parámetros principales: `--dias` (-T), `--implementaciones` (-N), `--marketing` (-M), `--ab-suscripcion`. Ver [Uso · Parámetros](https://github.com/apacay/Simu-vAri/wiki/Uso#par%C3%A1metros) para la tabla completa.

## Benchmark (múltiples corridas)

```bash
python run_benchmark.py --runs 20 --ab-suscripcion 0.70 --graficos
```

Ejecuta N corridas, agrega métricas y genera gráficos. Ver [Uso · Benchmark](https://github.com/apacay/Simu-vAri/wiki/Uso#benchmark-m%C3%BAtiples-corridas) para parámetros (`--runs`, `--output-metricas`, etc.).

## Uso desde código

```python
from simulacion.principal import ejecutar_simulacion
estado = ejecutar_simulacion(T_FINAL=365, N=30, M=2000, prob_suscripcion_nuevo=0.50, verbose=True)
print(estado.BENEFICIO_NETO_TRABAJOS, estado.T_EQUILIBRIO)
```

Ver [API](https://github.com/apacay/Simu-vAri/wiki/API): [atributos del estado](https://github.com/apacay/Simu-vAri/wiki/API#atributos-del-estado), [benchmark](https://github.com/apacay/Simu-vAri/wiki/API#benchmark), [funciones de distribución](https://github.com/apacay/Simu-vAri/wiki/API#funciones-de-distribuci%C3%B3n).

## Datos, variables de estado y resultado

Clasificación, listado de variables y relación eventos→estado: [Arquitectura · Clasificación](https://github.com/apacay/Simu-vAri/wiki/Arquitectura#clasificaci%C3%B3n-de-variables). Detalle: [Métricas principales](https://github.com/apacay/Simu-vAri/wiki/M%C3%A9tricas#m%C3%A9tricas-principales).

## Resumen del modelo

- **Clientes:** Nuevos (con presupuesto [MKT](https://github.com/apacay/Simu-vAri/wiki/Glosario)) vs preexistentes ([PE](https://github.com/apacay/Simu-vAri/wiki/Glosario)). Proporción según scoring IA.
- **Tipos:** [CE](https://github.com/apacay/Simu-vAri/wiki/Glosario) (asiduo / no asiduo) y [TA](https://github.com/apacay/Simu-vAri/wiki/Glosario).
- **Pago:** Suscripción (10/mes, 15% descuento), Prepago (354.2, bloque global 460), Trabajo aislado (variable). Clientes nuevos eligen suscripción vs prepago según `--ab-suscripcion` (default 50/50).
- **Trabajos:** Apps/IT/Desarrollo con proporciones variables por día (Dirichlet α=26,21.5,2.5; media esperada ≈52%/43%/5%); duración y costo según [Configuración · Duraciones](https://github.com/apacay/Simu-vAri/wiki/Configuraci%C3%B3n#duraciones).
- **Calendarización:** Probabilidad según horario y día; arrepentimiento 60%, falta 5%. Además, **calendarización por falta de disponibilidad** cuando no hay técnicos libres.
- **Satisfacción:** Base + conectividad + inestabilidad (post-implementación) + calendarizado.
- **Mensual:** Cobro suscripciones, no renovación de disconformes (80%), reponer [MKT](https://github.com/apacay/Simu-vAri/wiki/Glosario), pagar desarrollos.
- **Métricas:** Día de equilibrio (primer día con beneficio acumulado > 0), mejor trimestre (120 días).

## Modelo de técnicos

[TPLL](https://github.com/apacay/Simu-vAri/wiki/Glosario), [TPS](https://github.com/apacay/Simu-vAri/wiki/Glosario), [HIGH_VALUE](https://github.com/apacay/Simu-vAri/wiki/Glosario). Tipos [Dev](https://github.com/apacay/Simu-vAri/wiki/Glosario) y [Apps/IT](https://github.com/apacay/Simu-vAri/wiki/Glosario). Ver [Modelo de Técnicos](https://github.com/apacay/Simu-vAri/wiki/Modelo-de-T%C3%A9cnicos#conceptos-tplltps).

## Glosario y distribuciones

[Listado completo de acrónimos](https://github.com/apacay/Simu-vAri/wiki/Glosario) (SaaS, PE, CE, TA, MKT, TPLL, TPS, TDN, TDOFF, EaE, IT, Dev, Apps/IT). [Demanda y FDP](https://github.com/apacay/Simu-vAri/wiki/Modelo-Conceptual#2-fdp-utilizadas).
