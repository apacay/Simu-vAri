# Simulación de Plataforma Técnica SaaS

Simulación por eventos discretos (día a día) de una plataforma que conecta técnicos con clientes. Incluye tres modalidades de pago (suscripción, prepago, trabajo aislado), satisfacción probabilística, calendarización e implementaciones periódicas.

## Requisitos

- Python 3.8 o superior (solo biblioteca estándar).

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

Desde la raíz del proyecto:

```bash
python run_simulacion.py --dias 365 --implementaciones 30 --marketing 2000
```

Parámetros:

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--dias`, `-T` | Días a simular (T_FINAL) | 365 |
| `--implementaciones`, `-N` | Frecuencia de implementaciones (cada N días) | 30 |
| `--marketing`, `-M` | Presupuesto mensual de marketing (500–4500) | 2000 |
| `--silencioso`, `-q` | No imprimir resultados | - |
| `--graficos`, `-g` | Generar gráficos PNG en `graficos/` | - |

Ejemplos:

```bash
python run_simulacion.py -T 180 -N 14 -M 3000
python run_simulacion.py --dias 365 --marketing 4500 -q
```

## Benchmark (múltiples corridas)

Para ejecutar un número configurable de corridas y obtener métricas agregadas (media, desv. estándar, distribuciones):

```bash
python run_benchmark.py --runs 20 --graficos
python run_benchmark.py -r 50 -T 3653 -N 30 -M 2000 --seed 42 -g
```

Parámetros del benchmark:

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--runs`, `-r` | Número de corridas | 10 |
| `--dias`, `-T` | Días por corrida | 3653 |
| `--implementaciones`, `-N` | Frecuencia implementaciones | 30 |
| `--marketing`, `-M` | Presupuesto marketing | 2000 |
| `--seed`, `-s` | Semilla para reproducibilidad | - |
| `--graficos`, `-g` | Generar gráficos de distribuciones | - |
| `--output-graficos` | Directorio de salida | graficos_benchmark |
| `--output-metricas` | Archivo JSON con métricas | - |
| `--silencioso`, `-q` | Sin progreso por corrida | - |

Gráficos generados: boxplot de beneficio final, histogramas, serie temporal media±σ, barras de métricas agregadas.

## Uso desde código

### Una sola corrida

```python
from simulacion.principal import ejecutar_simulacion

estado = ejecutar_simulacion(T_FINAL=365, N=30, M=2000, verbose=True)
# o sin imprimir:
estado = ejecutar_simulacion(365, 30, 2000, verbose=False)
print(estado.BENEFICIO_NETO_TRABAJOS, estado.T_EQUILIBRIO)
```

### Benchmark (múltiples corridas)

```python
from simulacion.benchmark import ejecutar_benchmark, agregar_metricas, generar_graficos_benchmark

# Ejecutar 20 corridas
resultados = ejecutar_benchmark(n_runs=20, T_FINAL=365, N=30, M=2000, seed=42)

# Extraer métricas agregadas
agregado = agregar_metricas(resultados)
print(agregado["estadisticas"]["beneficio_final"]["media"])

# Generar gráficos
generar_graficos_benchmark(agregado, output_dir="graficos_benchmark")
```

## Resumen del modelo

- **Clientes:** Nuevos (con presupuesto MKT) vs preexistentes (PE). Proporción según scoring IA.
- **Tipos:** Cost-Effective (asiduo / no asiduo) y Trabajo Aislado.
- **Pago:** Suscripción (10/mes, 15% descuento), Prepago (354.2, bloque global 460), Trabajo aislado (variable).
- **Trabajos:** Apps (52%), IT (43%), Desarrollo (5%); duración y costo según documento.
- **Calendarización:** Probabilidad según horario y día; arrepentimiento 60%, falta 5%. Además, **calendarización por falta de disponibilidad** cuando no hay técnicos libres.
- **Satisfacción:** Base + conectividad + inestabilidad (post-implementación) + calendarizado.
- **Mensual:** Cobro suscripciones, no renovación de disconformes (80%), reponer MKT, pagar desarrollos.
- **Métricas:** Día de equilibrio (primer día con beneficio acumulado > 0), mejor trimestre (120 días).

## Modelo de técnicos (TPLL, TPS[], HIGH_VALUE)

La simulación usa conceptos de simulación por eventos discretos para modelar la disponibilidad de técnicos:

| Variable | Significado |
|----------|-------------|
| **TPLL** | Tiempo Próxima Llegada de clientes. Se recalcula en cada llegada. |
| **TPS[]** | Tiempo Próxima Salida: vector de tiempos en que cada técnico se libera. |
| **HIGH_VALUE** | Valor infinito que indica técnico libre (`TPS[i] == HIGH_VALUE` o `TPS[i] <= reloj`). |

### Tipos de técnicos

| Tipo | Capacidad/día | Trabajos que atiende |
|------|---------------|----------------------|
| **Dev** | 6 h (360 min) | DESARROLLO, APPS, IT (si libre puede tomar Apps o IT) |
| **Apps/IT** | 8 h (480 min) | APPS, IT únicamente |

### Flujo al llegar un cliente

1. Se actualiza TPLL y reloj.
2. Se obtiene tipo y duración del trabajo.
3. Se revisa TPS[] para técnicos capaces.
4. Si hay técnico libre: se asigna y `TPS[i] = reloj + duracion`.
5. Si **todos** los técnicos capaces están ocupados: el cliente entra en **calendarización por falta de disponibilidad** (trabajo perdido para contratación).

### Contratación cada 3 semanas

- Se analizan los trabajos perdidos de las **últimas 3 semanas** (o desde inicio si han pasado menos).
- Trabajos DESARROLLO perdidos -> nuevos Devs.
- Trabajos APPS + IT perdidos -> nuevos técnicos Apps/IT.
- Lead time de 3 semanas hasta la incorporación de los técnicos contratados.

### Rotación de técnicos

- Cada semana se aplica `PROB_ROTACION_TECNICO_SEMANAL` por técnico.
- Binomial(n, p) determina las bajas de Devs y técnicos Apps/IT por separado.

## Demanda y distribuciones

- **Demanda de trabajos:** Distribución binomial negativa (mayor variabilidad que Poisson).
- **Probabilidades:** Modelo Beta en lugar de porcentajes fijos (variabilidad realista).
- **Conteos (renovaciones, bajas):** Binomial en lugar de `round(n*p)`.
