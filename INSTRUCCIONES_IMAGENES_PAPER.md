# Instrucciones: Imágenes para el Paper

Reemplazar cada placeholder en el documento Word por la imagen correspondiente.

## Ubicación base

Todas las rutas son relativas a la raíz del proyecto **Ariel**.

---

## Lista completa de placeholders

### Benchmark 10 años (27 configuraciones × 5000 corridas)

| # | Placeholder en el documento | Archivo exacto |
|---|-----------------------------|----------------|
| 1 | `[PLACEHOLDER FIGURA 1 ...]` | `benchmark_10_anos/comparacion_AB.png` |
| 2 | `[PLACEHOLDER FIGURA 2 ...]` | `benchmark_10_anos/comparacion_Releases.png` |
| 3 | `[PLACEHOLDER FIGURA 3 ...]` | `benchmark_10_anos/mejor_vs_peor_config.png` |
| 4 | `[PLACEHOLDER FIGURA 4 ...]` | `benchmark_10_anos/equilibrio_por_config.png` |
| 5 | `[PLACEHOLDER FIGURA 5 ...]` | `benchmark_10_anos/satisfaccion_por_release.png` |
| 6 | `[PLACEHOLDER FIGURA 6 ...]` | `benchmark_10_anos/entrada_inicial_prepago_vs_suscripcion.png` |

### Casos 5 años (3 casos × 1000 corridas)

| # | Placeholder en el documento | Archivo exacto |
|---|-----------------------------|----------------|
| 7 | `[PLACEHOLDER FIGURA 7 ...]` | `benchmark_10_anos/casos_5_anos/equilibrio_antes/serie_beneficio_acumulado.png` |
| 8 | `[PLACEHOLDER FIGURA 8 ...]` | `benchmark_10_anos/casos_5_anos/cost_effective/serie_beneficio_acumulado.png` |
| 9 | `[PLACEHOLDER FIGURA 9 ...]` | `benchmark_10_anos/casos_5_anos/menos_efectivo/serie_beneficio_acumulado.png` |
| 10 | `[PLACEHOLDER FIGURA 10 ...]` | `benchmark_10_anos/casos_5_anos/menos_efectivo/ejemplo/perdidas_clientes.png` |
| 11 | `[PLACEHOLDER FIGURA 11 ...]` | `benchmark_10_anos/casos_5_anos/cost_effective/ejemplo/satisfaccion_general.png` |
| 12 | `[PLACEHOLDER FIGURA 12 ...]` | `graficos_benchmark/caso_extremo_mkt10000/serie_beneficio_acumulado.png` |

---

## Descripción de cada figura

| Fig | Descripción |
|-----|-------------|
| 1 | Beneficio final por tipo de AB Testing (Suscripción vs Prepago) |
| 2 | Beneficio final por frecuencia de releases (factor crítico) |
| 3 | Comparación mejor vs peor configuración |
| 4 | Porcentaje de corridas que alcanzaron equilibrio por configuración |
| 5 | Satisfacción de usuarios por frecuencia de releases |
| 6 | Ingresos primeros 6 meses: Prepago vs Suscripción por AB Testing |
| 7 | Serie beneficio acumulado. Equilibrio más rápido (0-100/Trim/MKT2500). Cruce semana 49-75 |
| 8 | Serie beneficio acumulado. Cost-effective (50-50/Trim/MKT500). Cruce semana 119-307 |
| 9 | Serie beneficio acumulado. Menos efectivo (100-0/Sem/MKT500). Sin equilibrio |
| 10 | Pérdidas de clientes por razón. Caso menos efectivo: motivos del fracaso |
| 11 | Evolución satisfacción general. Caso cost-effective viable |
| 12 | Serie beneficio acumulado. Caso extremo (50-50/Trim/MKT 10.000). Equilibrio ~7 meses |

---

## Cómo reemplazar en Word

1. Buscar en el documento: `[PLACEHOLDER FIGURA`
2. Seleccionar todo el texto del placeholder (incluyendo la línea con el path)
3. **Insertar** → **Imagen** → **Desde archivo**
4. Navegar a la ruta indicada (ej: `Ariel/benchmark_10_anos/comparacion_AB.png`)
5. Eliminar el texto del placeholder, conservando solo el pie de figura
6. Ajustar tamaño de la imagen (centrar, ancho de columna para formato 2 columnas)

---

## Imágenes adicionales disponibles (opcional)

- `benchmark_10_anos/comparacion_Marketing.png`
- `benchmark_10_anos/comparacion_todas.png`
- `benchmark_10_anos/usuarios_finales_por_config.png`
- `benchmark_10_anos/dia_equilibrio_por_release.png`
- `benchmark_10_anos/casos_5_anos/*/boxplot_beneficio_final.png`
- `benchmark_10_anos/casos_5_anos/*/histograma_equilibrio.png`
- `benchmark_10_anos/casos_5_anos/*/ejemplo/resultado_neto.png`
- `graficos_benchmark/caso_extremo_mkt10000/histograma_beneficio_final.png`
- `graficos_benchmark/caso_extremo_mkt10000/histograma_equilibrio.png`
- `graficos_benchmark/caso_extremo_mkt10000/metricas_agregadas.png`

---

## Formato recomendado

- Preferible imágenes en blanco y negro (según formato UTN)
- Centrar figuras que abarquen toda la página
- Figuras de ancho de columna para formato de 2 columnas
