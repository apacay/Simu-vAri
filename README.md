# Simulación de Plataforma Técnica SaaS

Simulación por eventos discretos (día a día) de una plataforma que conecta técnicos con clientes. Incluye tres modalidades de pago (suscripción, prepago, trabajo aislado), satisfacción probabilística, calendarización e implementaciones periódicas.

## Requisitos

- Python 3.8 o superior (solo biblioteca estándar).

## Estructura del proyecto

```
Ariel/
├── simulacion/
│   ├── __init__.py
│   ├── config.py      # Constantes y parámetros
│   ├── estado.py      # Estado global (contadores, financiero)
│   ├── llegada.py     # Flujo de llegada de cliente (tipo, trabajo, pago, satisfacción)
│   └── principal.py   # Bucle principal, mensuales, equilibrio, mejor trimestre
├── run_simulacion.py  # Punto de entrada
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

Ejemplos:

```bash
python run_simulacion.py -T 180 -N 14 -M 3000
python run_simulacion.py --dias 365 --marketing 4500 -q
```

## Uso desde código

```python
from simulacion import ejecutar_simulacion, imprimir_resultados

estado = ejecutar_simulacion(T_FINAL=365, N=30, M=2000, verbose=True)
# o sin imprimir:
estado = ejecutar_simulacion(365, 30, 2000, verbose=False)
print(estado.BENEFICIO_NETO_TRABAJOS, estado.T_EQUILIBRIO)
```

## Resumen del modelo

- **Clientes:** Nuevos (con presupuesto MKT) vs preexistentes (PE). Proporción según scoring IA.
- **Tipos:** Cost-Effective (asiduo / no asiduo) y Trabajo Aislado.
- **Pago:** Suscripción (10/mes, 15% descuento), Prepago (354.2, bloque global 460), Trabajo aislado (variable).
- **Trabajos:** Apps (52%), IT (43%), Desarrollo (5%); duración y costo según documento.
- **Calendarización:** Probabilidad según horario y día; arrepentimiento 50%, falta 5%.
- **Satisfacción:** Base + conectividad + inestabilidad (post-implementación) + calendarizado.
- **Mensual:** Cobro suscripciones, no renovación de disconformes (70%), reponer MKT, pagar desarrollos (3250).
- **Métricas:** Día de equilibrio (primer día con beneficio acumulado > 0), mejor trimestre (120 días).

Basado en los documentos: *Llegada de Cliente*, *Algoritmo Principal* y *Propuesta de TP Final - Simulación de Plataforma Técnica SaaS*.
