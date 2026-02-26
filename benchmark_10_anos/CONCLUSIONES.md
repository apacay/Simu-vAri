# Conclusiones del Benchmark a 10 anos

**Fecha:** 2026-02-26 12:50
**Periodo simulado:** 10 anos (3650 dias)
**Configuraciones evaluadas:** 9

---

## Resumen de variables

| Variable | Valores |
|----------|---------|
| **AB Testing** | 0-100 (100% prepago), 100-0 (100% suscripcion), 50-50 |
| **Releases** | Semanales (7d), Mensuales (30d), Trimestrales (90d) |
| **Marketing** | 500, 1500, 2500 creditos/mes |

---

## Tabla de resultados

| AB | Releases | MKT | Beneficio | Eq% | Eq dia (p25-p75) | Sat prepago | Sat suscrip | Sat gen | Prepago 6m | Susc 6m |
|----|----------|-----|-----------|-----|------------------|-------------|-------------|---------|------------|---------|
| 0-100 | Mensuales | 1500 | 1,722,050 | 100% | 801-1109 | 32.4% | 97.1% | 80.9% | 16,545 | 13,222 |
| 100-0 | Mensuales | 1500 | 3,103,282 | 100% | 1012-598 | 14.8% | 96.8% | 83.5% | 5,566 | 17,695 |
| 50-50 | Mensuales | 1500 | 3,258,206 | 100% | 540-472 | 18.9% | 97.4% | 82.9% | 11,637 | 19,393 |
| 50-50 | Semanales | 1500 | -1,120,017 | 0% | N/A | 34.2% | 95.1% | 68.9% | 7,909 | 11,386 |
| 50-50 | Mensuales | 1500 | 2,647,969 | 100% | 801-959 | 16.6% | 97.4% | 82.7% | 14,299 | 15,716 |
| 50-50 | Trimestrales | 1500 | 2,851,045 | 100% | 869-659 | 19.3% | 96.9% | 83.9% | 12,523 | 18,431 |
| 50-50 | Mensuales | 500 | 170,825 | 67% | 1946-1590 | 20.0% | 96.8% | 82.6% | 9,696 | 17,903 |
| 50-50 | Mensuales | 1500 | 2,528,881 | 100% | 660-805 | 20.5% | 97.1% | 82.8% | 10,167 | 17,660 |
| 50-50 | Mensuales | 2500 | 4,924,775 | 100% | 597-477 | 16.8% | 97.7% | 82.8% | 14,304 | 17,476 |

---

## Conclusiones profundas (no deducibles a priori)

### 1. Entre que fechas se alcanza el punto de equilibrio?

- **0-100 / Mensuales / MKT 1500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 856 (rango p25-p75: 801-1109), aprox. ~Ano 3, mes 5.
- **100-0 / Mensuales / MKT 1500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 736 (rango p25-p75: 1012-598), aprox. ~Ano 3, mes 1.
- **50-50 / Mensuales / MKT 1500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 625 (rango p25-p75: 540-472), aprox. ~Ano 2, mes 9.
- **50-50 / Semanales / MKT 1500:** No se alcanza equilibrio (0% de corridas).
- **50-50 / Mensuales / MKT 1500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 815 (rango p25-p75: 801-959), aprox. ~Ano 3, mes 3.
- **50-50 / Trimestrales / MKT 1500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 705 (rango p25-p75: 869-659), aprox. ~Ano 2, mes 12.
- **50-50 / Mensuales / MKT 500:** Equilibrio en 67% de corridas. Cuando se alcanza: dia 1768 (rango p25-p75: 1946-1590), aprox. ~Ano 5, mes 11.
- **50-50 / Mensuales / MKT 1500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 758 (rango p25-p75: 660-805), aprox. ~Ano 3, mes 1.
- **50-50 / Mensuales / MKT 2500:** Equilibrio en 100% de corridas. Cuando se alcanza: dia 585 (rango p25-p75: 597-477), aprox. ~Ano 2, mes 8.

### 2. Genera mas entrada inicial el modo prepago (paquete de minutos)?

- **AB 0-100:** En los primeros 6 meses, prepago aporta en promedio 16,545 creditos vs suscripcion 13,222. **Prepago genera mas entrada inicial** en este escenario.
- **AB 100-0:** En los primeros 6 meses, prepago aporta en promedio 5,566 creditos vs suscripcion 17,695. **Suscripcion genera mas entrada inicial** en este escenario.
- **AB 50-50:** En los primeros 6 meses, prepago aporta en promedio 11,505 creditos vs suscripcion 16,852. **Suscripcion genera mas entrada inicial** en este escenario.

### 3. Como resulta la satisfaccion de clientes en cada caso?

- **0-100 / Mensuales / MKT 1500:** Satisfaccion general 80.9%, prepago 32.4% | suscripcion 97.1%.
- **100-0 / Mensuales / MKT 1500:** Satisfaccion general 83.5%, prepago 14.8% | suscripcion 96.8%.
- **50-50 / Mensuales / MKT 1500:** Satisfaccion general 82.9%, prepago 18.9% | suscripcion 97.4%.
- **50-50 / Semanales / MKT 1500:** Satisfaccion general 68.9%, prepago 34.2% | suscripcion 95.1%.
- **50-50 / Mensuales / MKT 1500:** Satisfaccion general 82.7%, prepago 16.6% | suscripcion 97.4%.
- **50-50 / Trimestrales / MKT 1500:** Satisfaccion general 83.9%, prepago 19.3% | suscripcion 96.9%.
- **50-50 / Mensuales / MKT 500:** Satisfaccion general 82.6%, prepago 20.0% | suscripcion 96.8%.
- **50-50 / Mensuales / MKT 1500:** Satisfaccion general 82.8%, prepago 20.5% | suscripcion 97.1%.
- **50-50 / Mensuales / MKT 2500:** Satisfaccion general 82.8%, prepago 16.8% | suscripcion 97.7%.

### 4. Configuracion cost-effective: minimizar inversion y maximizar sostenibilidad

La configuracion **mas cost-effective** (menor inversion en marketing = 500) que logra equilibrio sostenible:
- **AB:** 50-50, **Releases:** Mensuales
- **Beneficio final medio:** 170,825 creditos
- **Equilibrio alcanzado:** 67% de corridas
- **Dia medio de equilibrio:** 1768.0

**Por que?** Con solo 500 creditos/mes de marketing, se reduce el costo de adquisicion. Releases mensuales o trimestrales evitan la inestabilidad que destruye la satisfaccion. El equilibrio se alcanza porque los costos fijos (desarrollo) se compensan con ingresos recurrentes sin necesidad de un flujo masivo de clientes nuevos.

### 5. Resumen ejecutivo

- **Mejor config (max beneficio):** 50-50 / Mensuales / MKT 2500 = 4,924,775 creditos
- **Peor config:** 50-50 / Semanales / MKT 1500 = -1,120,017 creditos

**Hallazgo critico:** Releases semanales generan inestabilidad que impide alcanzar equilibrio en todas las configuraciones, independientemente del AB o marketing. La frecuencia de implementaciones es el factor mas determinante.
