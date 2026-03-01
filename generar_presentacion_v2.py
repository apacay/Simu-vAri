#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_presentacion_v2.py
Presentación HTML profesional y autocontenida para la Simulación SaaS - UTN FRBA.
Todas las imágenes se embeben en base64 para portabilidad.

Uso:
    python generar_presentacion_v2.py
    Luego abrir presentacion_saas.html en el navegador (F11 para pantalla completa).
"""

import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()


def embed_img(rel_path: str):
    p = BASE_DIR / rel_path
    if not p.exists():
        print(f"  ⚠  No encontrada: {p}")
        return None
    data = base64.b64encode(p.read_bytes()).decode()
    suffix = p.suffix.lower().lstrip(".")
    mime = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "svg": "image/svg+xml",
    }.get(suffix, "image/png")
    return f"data:{mime};base64,{data}"


def img_tag(rel_path: str, alt: str = "") -> str:
    src = embed_img(rel_path)
    if src is None:
        return f'<div class="img-missing">⚠ {rel_path}</div>'
    return f'<img src="{src}" alt="{alt}">'


# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy:    #1e3a8a;
  --navy2:   #1e40af;
  --blue:    #2563eb;
  --light-b: #dbeafe;
  --green:   #059669;
  --light-g: #d1fae5;
  --amber:   #d97706;
  --light-a: #fef3c7;
  --red:     #dc2626;
  --light-r: #fee2e2;
  --slate:   #334155;
  --text:    #0f172a;
  --text2:   #475569;
  --bg:      #f1f5f9;
  --white:   #ffffff;
  --border:  #cbd5e1;
}

html, body {
  width: 100%; height: 100%;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #0f172a;
  overflow: hidden;
}

/* ── Presentación ── */
#pres {
  width: 100vw; height: 100vh;
  position: relative;
  overflow: hidden;
}

.slide {
  position: absolute; inset: 0;
  display: none;
  background: var(--bg);
  flex-direction: column;
}
.slide.active { display: flex; }

/* ── Barra de progreso ── */
#progress {
  position: fixed; top: 0; left: 0;
  height: 4px;
  background: linear-gradient(90deg, #60a5fa, #34d399);
  transition: width 0.4s ease;
  z-index: 100;
}

/* ── Contador de diapositivas ── */
#counter {
  position: fixed; bottom: 14px; right: 20px;
  font-size: 13px; color: rgba(255,255,255,0.5);
  z-index: 100; letter-spacing: 0.5px;
}

/* ── Navegación ── */
.nav-btn {
  position: fixed;
  top: 50%; transform: translateY(-50%);
  width: 42px; height: 42px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50%;
  color: white; font-size: 18px;
  cursor: pointer; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
  user-select: none;
}
.nav-btn:hover { background: rgba(255,255,255,0.28); }
#btn-prev { left: 14px; }
#btn-next { right: 14px; }

/* ════════════════════════════════════════
   PORTADA
   ════════════════════════════════════════ */
.slide-cover {
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 50%, #0c1445 100%);
  align-items: center; justify-content: center;
  text-align: center; padding: 40px;
}
.cover-logo {
  font-size: 13px; letter-spacing: 3px; text-transform: uppercase;
  color: #93c5fd; margin-bottom: 28px;
  padding: 6px 18px; border: 1px solid #3b82f6;
  border-radius: 20px; display: inline-block;
}
.cover-title {
  font-size: clamp(32px, 5vw, 54px);
  font-weight: 800; color: #ffffff;
  line-height: 1.15; margin-bottom: 20px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.4);
}
.cover-subtitle {
  font-size: clamp(16px, 2.2vw, 22px);
  color: #93c5fd; margin-bottom: 40px;
}
.cover-subtitle strong { color: #60a5fa; }
.cover-team {
  font-size: 15px; color: #94a3b8; margin-bottom: 50px;
}
.cover-team .sep { margin: 0 10px; color: #3b82f6; }
.cover-stats {
  display: flex; gap: 32px; justify-content: center; flex-wrap: wrap;
}
.cover-stat {
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 14px; padding: 20px 30px;
  min-width: 140px;
}
.stat-num {
  display: block;
  font-size: clamp(28px, 3.5vw, 40px);
  font-weight: 800; color: #60a5fa;
}
.stat-lbl {
  display: block;
  font-size: 12px; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 1px;
  margin-top: 4px;
}

/* ════════════════════════════════════════
   SLIDE COMÚN
   ════════════════════════════════════════ */
.slide-header {
  background: linear-gradient(90deg, var(--navy) 0%, var(--navy2) 100%);
  padding: 18px 40px;
  display: flex; align-items: center; gap: 16px;
  flex-shrink: 0;
}
.slide-header h2 {
  font-size: clamp(20px, 2.8vw, 30px);
  font-weight: 700; color: #ffffff;
  letter-spacing: -0.3px;
}
.slide-tag {
  font-size: 12px; color: #93c5fd;
  background: rgba(255,255,255,0.12);
  padding: 4px 12px; border-radius: 12px;
  white-space: nowrap; margin-left: auto;
}

.slide-body {
  flex: 1; padding: 24px 40px;
  overflow: hidden; display: flex; flex-direction: column;
}

/* ════════════════════════════════════════
   DOS COLUMNAS
   ════════════════════════════════════════ */
.two-col {
  flex-direction: row !important;
  gap: 28px;
}
.two-col .col { flex: 1; display: flex; flex-direction: column; gap: 16px; }
.two-col .col.img-col { justify-content: center; }
/* Hacer que cards y question-box llenen el espacio disponible en two-col */
.two-col .col > .card        { flex: 1; }
.two-col .col > .question-box { flex: 1; }

/* ════════════════════════════════════════
   CARDS
   ════════════════════════════════════════ */
.card {
  background: var(--white);
  border-radius: 12px; padding: 22px 24px;
  border-left: 4px solid transparent;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.card h3 { font-size: 24px; margin-bottom: 10px; color: var(--text); }
.card p, .card ul { font-size: 20px; color: var(--text2); line-height: 1.6; }
.card ul { padding-left: 20px; }
.card li { margin-bottom: 6px; }
.card .card-icon { font-size: 32px; margin-bottom: 10px; }

.card-blue  { border-left-color: var(--blue); background: #eff6ff; }
.card-green { border-left-color: var(--green); background: #f0fdf4; }
.card-amber { border-left-color: var(--amber); background: #fffbeb; }
.card-red   { border-left-color: var(--red);   background: #fef2f2; }

/* Caja de pregunta */
.question-box {
  background: linear-gradient(135deg, #1e3a8a, #1e40af);
  border-radius: 12px; padding: 24px;
  color: white;
}
.question-box h3 { font-size: 24px; margin-bottom: 12px; color: #93c5fd; }
.question-box p  { font-size: 20px; line-height: 1.7; }
.question-box strong { color: #60a5fa; }
.question-icon { font-size: 36px; margin-bottom: 12px; }

/* ════════════════════════════════════════
   MODELO - SLIDE 3
   ════════════════════════════════════════ */
.model-diagram {
  flex: 1; display: flex; flex-direction: column; gap: 16px;
}
.model-delta {
  background: linear-gradient(90deg, #1e3a8a, #1e40af);
  border-radius: 10px; padding: 12px 24px;
  display: flex; align-items: center; gap: 16px;
  align-self: flex-start;
}
.delta-symbol { font-size: 34px; font-weight: 800; color: #ffffff; }
.delta-label  { font-size: 18px; color: #93c5fd; text-transform: uppercase; letter-spacing: 1px; }
.events-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: 1fr 1fr;
  gap: 12px; flex: 1;
  align-items: stretch;
}
.event-box {
  border-radius: 10px; padding: 16px 12px;
  display: flex; flex-direction: column; align-items: center;
  justify-content: center;
  text-align: center; gap: 10px;
  font-size: 19px; font-weight: 500; color: var(--text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.07);
}
.event-icon { font-size: 32px; }
.event-blue  { background: #eff6ff; border: 1px solid #bfdbfe; }
.event-green { background: #f0fdf4; border: 1px solid #bbf7d0; }
.event-amber { background: #fffbeb; border: 1px solid #fde68a; }

.model-state {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  padding: 14px 18px;
  background: var(--white); border-radius: 8px;
  border: 1px solid var(--border);
}
.state-label { font-size: 18px; font-weight: 600; color: var(--text2); margin-right: 6px; }
.state-pill  {
  font-size: 18px; padding: 6px 14px;
  background: var(--light-b); color: var(--navy);
  border-radius: 20px; font-weight: 500;
}

/* ════════════════════════════════════════
   VARIABLES - SLIDE 4
   ════════════════════════════════════════ */
.vars-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; flex: 1;
}
.var-card {
  background: var(--white); border-radius: 14px; padding: 22px;
  display: flex; flex-direction: column; gap: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  border-top: 4px solid var(--navy);
}
.var-letter {
  font-size: 38px; font-weight: 900; color: var(--navy);
  line-height: 1;
}
.var-name  { font-size: 16px; font-weight: 700; color: var(--text); }
.var-values { display: flex; flex-wrap: wrap; gap: 8px; }
.val-chip {
  font-size: 12px; padding: 5px 12px;
  border-radius: 20px; font-weight: 600;
}
.val-red   { background: var(--light-r); color: var(--red); }
.val-blue  { background: var(--light-b); color: var(--navy2); }
.val-green { background: var(--light-g); color: var(--green); }
.val-amber { background: var(--light-a); color: var(--amber); }
.var-hint { font-size: 12px; color: var(--text2); font-style: italic; margin-top: auto; }

.formula-box {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  background: var(--navy); color: white;
  border-radius: 10px; padding: 14px 24px;
  font-size: 16px; font-weight: 500; flex-wrap: wrap;
}
.formula-box strong { color: #93c5fd; font-size: 18px; }
.formula-result { color: #34d399 !important; font-size: 22px !important; }

/* ════════════════════════════════════════
   SLIDES DE IMAGEN
   ════════════════════════════════════════ */
.img-slide-body {
  align-items: center; justify-content: center; gap: 12px;
  padding: 16px 40px !important;
}
.img-container {
  flex: 1; display: flex; align-items: center; justify-content: center;
  overflow: hidden; max-height: 100%;
}
.img-container img {
  max-width: 100%; max-height: 100%;
  object-fit: contain; border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.img-missing {
  padding: 40px; background: #fee2e2; color: #dc2626;
  border-radius: 8px; font-size: 14px;
}
.img-legend {
  display: flex; gap: 20px; align-items: center;
  font-size: 13px; color: var(--text2);
  padding: 8px 16px; background: var(--white);
  border-radius: 8px; border: 1px solid var(--border);
}
.legend-green { color: var(--green); font-weight: 600; }
.legend-red   { color: var(--red); font-weight: 600; }

.insight-banner {
  background: #fef3c7; border-left: 4px solid var(--amber);
  border-radius: 8px; padding: 12px 18px;
  display: flex; align-items: center; gap: 10px;
  font-size: 14px; color: #78350f;
}
.insight-icon { font-size: 20px; }

/* ════════════════════════════════════════
   HALLAZGO - SLIDE RELEASES
   ════════════════════════════════════════ */
.finding-card {
  background: var(--white); border-radius: 12px; padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex; flex-direction: column; gap: 8px; flex: 1;
}
.finding-card h3 { font-size: 16px; font-weight: 700; color: var(--text); }
.finding-card p  { font-size: 13px; color: var(--text2); line-height: 1.6; }
.finding-icon { font-size: 28px; }
.finding-stat {
  font-size: 48px; font-weight: 900; line-height: 1; margin: 4px 0;
}
.finding-stat-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text2); }
.finding-red  { border-top: 4px solid var(--red); }
.finding-red .finding-stat   { color: var(--red); }
.finding-green { border-top: 4px solid var(--green); }
.finding-green .finding-stat { color: var(--green); }

.img-col { flex: 1.1; }
.img-caption {
  font-size: 12px; color: var(--text2); text-align: center;
  font-style: italic; margin-top: 6px;
}

/* ════════════════════════════════════════
   TRES CASOS
   ════════════════════════════════════════ */
.three-col-imgs {
  flex-direction: row !important; gap: 16px !important;
  padding: 16px 32px !important;
}
.img-case {
  flex: 1; display: flex; flex-direction: column; gap: 8px;
  align-items: center;
}
.img-case .img-container { max-height: 380px; width: 100%; }
.img-case-label {
  font-size: 13px; font-weight: 700; padding: 5px 14px;
  border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;
}
.label-green { background: var(--light-g); color: var(--green); }
.label-blue  { background: var(--light-b); color: var(--navy2); }
.label-red   { background: var(--light-r); color: var(--red); }
.img-case-meta { font-size: 12px; color: var(--text2); font-style: italic; }

/* ════════════════════════════════════════
   CONFIG COST-EFFECTIVE
   ════════════════════════════════════════ */
.recommend-box {
  background: linear-gradient(135deg, #0f172a, #1e3a8a);
  border-radius: 14px; padding: 24px;
  color: white; display: flex; flex-direction: column; gap: 16px;
  flex: 1;
}
.recommend-title {
  font-size: clamp(15px, 1.8vw, 20px); font-weight: 800;
  color: #60a5fa; letter-spacing: -0.3px;
}
.recommend-metrics {
  display: grid; grid-template-columns: 1fr 1fr; gap: 14px;
}
.metric {
  background: rgba(255,255,255,0.08);
  border-radius: 10px; padding: 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.metric-val { font-size: 26px; font-weight: 800; }
.metric-val.green { color: #34d399; }
.metric-val.blue  { color: #60a5fa; }
.metric-val.amber { color: #fbbf24; }
.metric-lbl { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.recommend-why {
  font-size: 13px; color: #cbd5e1; line-height: 1.7;
  border-top: 1px solid rgba(255,255,255,0.12);
  padding-top: 14px;
}
.recommend-why strong { color: #93c5fd; }

/* ════════════════════════════════════════
   COMPARACIÓN MEJOR vs PEOR
   ════════════════════════════════════════ */
.comparison-banner {
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  padding: 12px 20px;
  background: var(--white); border-radius: 10px;
  border: 1px solid var(--border);
}
.comp-item {
  display: flex; flex-direction: column; gap: 2px;
  flex: 1; border-radius: 8px; padding: 10px 14px;
}
.comp-item.comp-green { background: var(--light-g); }
.comp-item.comp-red   { background: var(--light-r); }
.comp-label { font-size: 12px; color: var(--text2); }
.comp-val   { font-size: 22px; font-weight: 800; }
.comp-item.comp-green .comp-val { color: var(--green); }
.comp-item.comp-red   .comp-val { color: var(--red); }
.comp-divider {
  font-size: 20px; font-weight: 800; color: var(--text2);
  padding: 0 6px;
}
.comp-diff {
  width: 100%; text-align: center; font-size: 13px; color: var(--text2);
  border-top: 1px solid var(--border); padding-top: 8px; margin-top: 4px;
}
.comp-diff strong { color: var(--text); }

/* ════════════════════════════════════════
   CONCLUSIONES
   ════════════════════════════════════════ */
.conclusions-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; flex: 1;
}
.conclusion-card {
  background: var(--white); border-radius: 12px; padding: 18px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.07);
  display: flex; flex-direction: column; gap: 8px;
  position: relative; overflow: hidden;
}
.conclusion-num {
  position: absolute; top: 14px; right: 14px;
  font-size: 36px; font-weight: 900; color: var(--border);
  line-height: 1;
}
.conclusion-icon { font-size: 26px; }
.conclusion-card h3 { font-size: 15px; font-weight: 700; color: var(--text); padding-right: 44px; }
.conclusion-card p  { font-size: 13px; color: var(--text2); line-height: 1.6; }

.conclusion-highlight {
  background: linear-gradient(90deg, var(--navy), var(--navy2));
  color: white; border-radius: 10px; padding: 14px 20px;
  font-size: 14px; line-height: 1.7; margin-top: 4px;
}
.conclusion-highlight strong { color: #93c5fd; }

/* ════════════════════════════════════════
   SLIDE FINAL
   ════════════════════════════════════════ */
.slide-final {
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 50%, #0c1445 100%);
  align-items: center; justify-content: center;
  text-align: center;
}
.final-content {
  display: flex; flex-direction: column; align-items: center; gap: 20px;
}
.final-icon {
  width: 100px; height: 100px; border-radius: 50%;
  background: rgba(96, 165, 250, 0.15);
  border: 3px solid #3b82f6;
  display: flex; align-items: center; justify-content: center;
  font-size: 52px; font-weight: 900; color: #60a5fa;
  line-height: 1;
}
.final-title {
  font-size: clamp(40px, 7vw, 72px);
  font-weight: 900; color: #ffffff;
}
.final-team {
  font-size: 16px; color: #94a3b8;
}
.final-team .sep { margin: 0 10px; color: #3b82f6; }
.final-subject {
  font-size: 13px; letter-spacing: 2px; text-transform: uppercase;
  color: #475569;
}

/* ════════════════════════════════════════
   HINTS DE NAVEGACIÓN
   ════════════════════════════════════════ */
#hint {
  position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
  font-size: 11px; color: rgba(255,255,255,0.3); letter-spacing: 0.5px;
  z-index: 100; pointer-events: none;
}
"""

# ──────────────────────────────────────────────────────────────────────────────
# JS
# ──────────────────────────────────────────────────────────────────────────────
JS = """
(function() {
  const slides   = document.querySelectorAll('.slide');
  const progress = document.getElementById('progress');
  const counter  = document.getElementById('counter');
  const hint     = document.getElementById('hint');
  const total    = slides.length;
  let current    = 0;

  function show(idx) {
    slides.forEach(s => s.classList.remove('active'));
    slides[idx].classList.add('active');
    current = idx;
    const pct = total > 1 ? (idx / (total - 1)) * 100 : 100;
    progress.style.width = pct + '%';
    counter.textContent  = (idx + 1) + ' / ' + total;
    if (hint) hint.style.opacity = idx === 0 ? '1' : '0';
  }

  function next() { if (current < total - 1) show(current + 1); }
  function prev() { if (current > 0)          show(current - 1); }

  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') { e.preventDefault(); next(); }
    if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')                    { e.preventDefault(); prev(); }
  });

  document.getElementById('btn-next').addEventListener('click', next);
  document.getElementById('btn-prev').addEventListener('click', prev);

  // Swipe en touch
  let tx = 0;
  document.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive:true });
  document.addEventListener('touchend',   e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (dx < -50) next(); else if (dx > 50) prev();
  }, { passive:true });

  show(0);
})();
"""


# ──────────────────────────────────────────────────────────────────────────────
# SLIDES
# ──────────────────────────────────────────────────────────────────────────────
def build_slides() -> list:
    slides = []

    # ── 1. PORTADA ────────────────────────────────────────────────────────────
    slides.append("""
    <div class="slide slide-cover">
      <div class="cover-logo">UTN FRBA &nbsp;·&nbsp; Ingeniería en Sistemas &nbsp;·&nbsp; Simulación</div>
      <h1 class="cover-title">Simulación de Plataforma SaaS<br>de Soporte Técnico</h1>
      <p class="cover-subtitle">Benchmark de viabilidad económica a <strong>10 años</strong></p>
      <div class="cover-team">
        <span>Claudio Sonntag (120580-8)</span>
        <span class="sep">·</span>
        <span>Ariel Pacay (121237-0)</span>
        <span class="sep">·</span>
        <span>Alison Reynoso (156899-1)</span>
      </div>
      <div class="cover-stats">
        <div class="cover-stat">
          <span class="stat-num">27</span>
          <span class="stat-lbl">Configuraciones</span>
        </div>
        <div class="cover-stat">
          <span class="stat-num">5.000</span>
          <span class="stat-lbl">Corridas c/u</span>
        </div>
        <div class="cover-stat">
          <span class="stat-num">135.000</span>
          <span class="stat-lbl">Escenarios</span>
        </div>
        <div class="cover-stat">
          <span class="stat-num">10 años</span>
          <span class="stat-lbl">Horizonte simulado</span>
        </div>
      </div>
    </div>
    """)

    # ── 2. EL NEGOCIO ─────────────────────────────────────────────────────────
    slides.append("""
    <div class="slide">
      <div class="slide-header">
        <h2>El Negocio y la Pregunta</h2>
      </div>
      <div class="slide-body two-col">
        <div class="col">
          <div class="card card-blue">
            <div class="card-icon">🏢</div>
            <h3>Plataforma SaaS de Soporte</h3>
            <p>Conecta <strong>técnicos</strong> con <strong>clientes</strong> que necesitan soporte técnico bajo demanda. Tres tipos de trabajo: Apps (52%), IT (43%), Desarrollo (5%).</p>
          </div>
          <div class="card card-green">
            <div class="card-icon">💳</div>
            <h3>Dos modelos de ingresos</h3>
            <ul>
              <li><strong>Suscripción</strong> — tarifa mensual recurrente</li>
              <li><strong>Prepago</strong> — paquetes de minutos por adelantado</li>
            </ul>
          </div>
        </div>
        <div class="col">
          <div class="question-box">
            <div class="question-icon">❓</div>
            <h3>Pregunta de investigación</h3>
            <p>¿Qué combinación de <strong>frecuencia de releases</strong>, <strong>presupuesto de marketing</strong> y <strong>mix de modelos de pago</strong> maximiza la viabilidad económica a largo plazo?</p>
          </div>
          <div class="card card-amber">
            <div class="card-icon">🔬</div>
            <h3>¿Por qué simulación?</h3>
            <p>Permite explorar <strong>135.000 escenarios</strong> que serían imposibles de experimentar en la realidad sin costos ni riesgos.</p>
          </div>
        </div>
      </div>
    </div>
    """)

    # ── 3. MODELO ─────────────────────────────────────────────────────────────
    slides.append("""
    <div class="slide">
      <div class="slide-header">
        <h2>Modelo de Simulación por Eventos Discretos</h2>
      </div>
      <div class="slide-body">
        <div class="model-diagram">
          <div class="model-delta">
            <span class="delta-symbol">Δt &nbsp;=&nbsp; 1 día</span>
            <span class="delta-label">avance discreto · 3.650 pasos por corrida</span>
          </div>
          <div class="events-grid">
            <div class="event-box event-blue">
              <span class="event-icon">👥</span>
              <span>Contratación / Renuncia de técnicos</span>
            </div>
            <div class="event-box event-green">
              <span class="event-icon">📥</span>
              <span>Llegada de clientes nuevos</span>
            </div>
            <div class="event-box event-amber">
              <span class="event-icon">🔧</span>
              <span>Atención de tickets</span>
            </div>
            <div class="event-box event-blue">
              <span class="event-icon">🚀</span>
              <span>Implementación de releases</span>
            </div>
            <div class="event-box event-green">
              <span class="event-icon">💵</span>
              <span>Cobro de suscripciones</span>
            </div>
            <div class="event-box event-amber">
              <span class="event-icon">💸</span>
              <span>Pago de sueldos</span>
            </div>
            <div class="event-box event-blue">
              <span class="event-icon">🔄</span>
              <span>Renovación de prepagos</span>
            </div>
            <div class="event-box event-green">
              <span class="event-icon">📊</span>
              <span>Churn y satisfacción de usuarios</span>
            </div>
          </div>
        </div>
        <div class="model-state">
          <span class="state-label">Estado:</span>
          <span class="state-pill">T (reloj)</span>
          <span class="state-pill">Clientes por modalidad</span>
          <span class="state-pill">Técnicos activos</span>
          <span class="state-pill">Créditos disponibles</span>
          <span class="state-pill">Satisfacción acumulada</span>
          <span class="state-pill">Fecha último release</span>
        </div>
      </div>
    </div>
    """)

    # ── 4. VARIABLES ──────────────────────────────────────────────────────────
    slides.append("""
    <div class="slide">
      <div class="slide-header">
        <h2>Variables de Control — Espacio de Configuraciones</h2>
      </div>
      <div class="slide-body">
        <div class="vars-grid">
          <div class="var-card">
            <div class="var-letter">N</div>
            <div class="var-name">Frecuencia de Releases</div>
            <div class="var-values">
              <span class="val-chip val-red">7 d — Semanal</span>
              <span class="val-chip val-blue">30 d — Mensual</span>
              <span class="val-chip val-green">90 d — Trimestral</span>
            </div>
            <div class="var-hint">Cada deploy introduce inestabilidad temporal en la plataforma</div>
          </div>
          <div class="var-card">
            <div class="var-letter">M</div>
            <div class="var-name">Presupuesto de Marketing</div>
            <div class="var-values">
              <span class="val-chip val-blue">500 cr/mes</span>
              <span class="val-chip val-blue">1.500 cr/mes</span>
              <span class="val-chip val-blue">2.500 cr/mes</span>
            </div>
            <div class="var-hint">Mayor inversión acelera adquisición de nuevos clientes</div>
          </div>
          <div class="var-card">
            <div class="var-letter">AB</div>
            <div class="var-name">Mix Suscripción / Prepago</div>
            <div class="var-values">
              <span class="val-chip val-green">0-100 (100% Prepago)</span>
              <span class="val-chip val-blue">50-50 (Híbrido)</span>
              <span class="val-chip val-amber">100-0 (100% Suscripción)</span>
            </div>
            <div class="var-hint">Proporción de clientes en cada modalidad de pago</div>
          </div>
        </div>
        <div class="formula-box">
          3 releases &nbsp;×&nbsp; 3 marketing &nbsp;×&nbsp; 3 AB testing &nbsp;=&nbsp;
          <strong>27 configs.</strong>
          &nbsp;×&nbsp; <strong>5.000 corridas</strong>
          &nbsp;×&nbsp; <strong>3.650 días</strong>
          &nbsp;=&nbsp; <strong class="formula-result">135.000 escenarios</strong>
        </div>
      </div>
    </div>
    """)

    # ── 5. HEATMAP ────────────────────────────────────────────────────────────
    heatmap = img_tag("benchmark_10_anos/comparacion_heatmap_beneficio.png", "Heatmap beneficio")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Resultados Globales — Beneficio Neto a 10 Años</h2>
        <span class="slide-tag">media de 5.000 corridas por configuración</span>
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">
          {heatmap}
        </div>
        <div class="img-legend">
          <span class="legend-green">■ Verde = ganancia</span>
          <span class="legend-red">■ Rojo = pérdida</span>
          <span class="legend-gray">valores en créditos</span>
        </div>
      </div>
    </div>
    """)

    # ── 6. TOP / BOTTOM ───────────────────────────────────────────────────────
    top_bottom = img_tag("benchmark_10_anos/comparacion_top_bottom.png", "Top y bottom configs")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Las 10 Mejores y 10 Peores Configuraciones</h2>
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">
          {top_bottom}
        </div>
        <div class="insight-banner">
          <span class="insight-icon">💡</span>
          <span>Las configuraciones con <strong>Releases Semanales</strong> dominan consistentemente el fondo del ranking, sin importar el marketing ni el modelo de pago.</span>
        </div>
      </div>
    </div>
    """)

    # ── 7. HALLAZGO CRÍTICO ───────────────────────────────────────────────────
    dia_eq = img_tag("benchmark_10_anos/dia_equilibrio_por_release.png", "Día equilibrio por release")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Hallazgo Crítico: La Frecuencia de Releases lo Decide Todo</h2>
      </div>
      <div class="slide-body two-col">
        <div class="col">
          <div class="finding-card finding-red">
            <div class="finding-icon">❌</div>
            <h3>Releases Semanales</h3>
            <div class="finding-stat">0%</div>
            <div class="finding-stat-label">de corridas alcanzan equilibrio</div>
            <p>La inestabilidad repetida destruye satisfacción e impide la rentabilidad en <em>todas</em> las configuraciones. Beneficio medio: <strong style="color:#dc2626">−1.100.000 créditos</strong>.</p>
          </div>
          <div class="finding-card finding-green">
            <div class="finding-icon">✅</div>
            <h3>Mensual / Trimestral</h3>
            <div class="finding-stat">74–100%</div>
            <div class="finding-stat-label">de corridas alcanzan equilibrio</div>
            <p>La plataforma estable permite que los ingresos recurrentes superen los costos. Beneficio medio: <strong style="color:#059669">+2.300.000–2.600.000</strong>.</p>
          </div>
        </div>
        <div class="col img-col" style="display:flex; flex-direction:column; justify-content:center;">
          <div class="img-container">
            {dia_eq}
          </div>
          <p class="img-caption">Día medio al punto de equilibrio según frecuencia de release</p>
        </div>
      </div>
    </div>
    """)

    # ── 8. TRES CASOS ─────────────────────────────────────────────────────────
    eq_antes = img_tag(
        "benchmark_10_anos/casos_5_anos/equilibrio_antes/serie_beneficio_acumulado.png",
        "Equilibrio rápido")
    cost_eff = img_tag(
        "benchmark_10_anos/casos_5_anos/cost_effective/serie_beneficio_acumulado.png",
        "Cost-effective")
    menos_ef = img_tag(
        "benchmark_10_anos/casos_5_anos/menos_efectivo/serie_beneficio_acumulado.png",
        "Menos efectivo")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Zoom: Tres Casos Representativos</h2>
        <span class="slide-tag">serie de beneficio acumulado · media ± 1σ · 1.000 corridas · 5 años</span>
      </div>
      <div class="slide-body three-col-imgs">
        <div class="img-case">
          <span class="img-case-label label-green">Equilibrio más rápido</span>
          <div class="img-container">{eq_antes}</div>
          <span class="img-case-meta">0-100 · Trimestral · MKT 2500 — día ~433</span>
        </div>
        <div class="img-case">
          <span class="img-case-label label-blue">Cost-Effective</span>
          <div class="img-container">{cost_eff}</div>
          <span class="img-case-meta">50-50 · Trimestral · MKT 500 — día ~1268</span>
        </div>
        <div class="img-case">
          <span class="img-case-label label-red">Menos Efectivo Viable</span>
          <div class="img-container">{menos_ef}</div>
          <span class="img-case-meta">100-0 · Semanal · MKT 500 — no alcanza eq.</span>
        </div>
      </div>
    </div>
    """)

    # ── 9. CONFIG COST-EFFECTIVE ──────────────────────────────────────────────
    eq_config = img_tag("benchmark_10_anos/equilibrio_por_config.png", "Tasa equilibrio por config")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Configuración Recomendada: Cost-Effective</h2>
      </div>
      <div class="slide-body two-col">
        <div class="col">
          <div class="recommend-box">
            <div class="recommend-title">50-50 &nbsp;·&nbsp; Releases Trimestrales &nbsp;·&nbsp; Marketing 500</div>
            <div class="recommend-metrics">
              <div class="metric">
                <span class="metric-val green">242k</span>
                <span class="metric-lbl">créditos de beneficio</span>
              </div>
              <div class="metric">
                <span class="metric-val green">90%</span>
                <span class="metric-lbl">corridas con equilibrio</span>
              </div>
              <div class="metric">
                <span class="metric-val amber">~3,5 años</span>
                <span class="metric-lbl">tiempo al equilibrio</span>
              </div>
              <div class="metric">
                <span class="metric-val blue">84,2%</span>
                <span class="metric-lbl">satisfacción de clientes</span>
              </div>
            </div>
            <div class="recommend-why">
              <strong>¿Por qué funciona?</strong> Con solo 500 cr/mes de marketing, los costos de adquisición son mínimos. Los releases trimestrales garantizan estabilidad. Los ingresos recurrentes (suscripción) compensan sin necesidad de flujo masivo de clientes nuevos.
            </div>
          </div>
        </div>
        <div class="col img-col" style="display:flex; flex-direction:column; justify-content:center;">
          <div class="img-container">{eq_config}</div>
          <p class="img-caption">% de corridas que alcanzan equilibrio por configuración</p>
        </div>
      </div>
    </div>
    """)

    # ── 10. MEJOR vs PEOR ─────────────────────────────────────────────────────
    mejor_peor = img_tag("benchmark_10_anos/mejor_vs_peor_config.png", "Mejor vs peor")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Brecha entre Mejor y Peor Configuración</h2>
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">{mejor_peor}</div>
        <div class="comparison-banner">
          <div class="comp-item comp-green">
            <span class="comp-label">🏆 Mejor — 50-50 · Trimestral · MKT 2500</span>
            <span class="comp-val">+5.116.487 cr.</span>
          </div>
          <div class="comp-divider">vs</div>
          <div class="comp-item comp-red">
            <span class="comp-label">💀 Peor — 100-0 · Semanal · MKT 500</span>
            <span class="comp-val">−1.598.935 cr.</span>
          </div>
          <div class="comp-diff">Diferencia total: <strong>6,7 millones de créditos</strong></div>
        </div>
      </div>
    </div>
    """)

    # ── 11. CONCLUSIONES ──────────────────────────────────────────────────────
    slides.append("""
    <div class="slide">
      <div class="slide-header">
        <h2>Conclusiones</h2>
      </div>
      <div class="slide-body">
        <div class="conclusions-grid">
          <div class="conclusion-card">
            <div class="conclusion-num">01</div>
            <div class="conclusion-icon">🚨</div>
            <h3>Releases semanales = inviabilidad garantizada</h3>
            <p>0% de corridas alcanzan equilibrio. La inestabilidad repetida destruye la satisfacción y el valor en <em>todas</em> las configuraciones, sin importar el marketing.</p>
          </div>
          <div class="conclusion-card">
            <div class="conclusion-num">02</div>
            <div class="conclusion-icon">✅</div>
            <h3>Mensual o Trimestral: 74%–100% de viabilidad</h3>
            <p>La estabilidad operativa es más determinante que el modelo de negocio. Cambiar de semanal a trimestral aporta en promedio <strong>+3,7M créditos</strong>.</p>
          </div>
          <div class="conclusion-card">
            <div class="conclusion-num">03</div>
            <div class="conclusion-icon">💡</div>
            <h3>El mix 50-50 maximiza el beneficio</h3>
            <p>El modelo híbrido equilibra entrada inicial (prepago) con recurrencia (suscripción). Mejor config: <strong>+5,1M créditos</strong>, equilibrio en 100% de corridas.</p>
          </div>
          <div class="conclusion-card">
            <div class="conclusion-num">04</div>
            <div class="conclusion-icon">📈</div>
            <h3>Trade-off marketing: velocidad vs riesgo</h3>
            <p>Mayor inversión acelera el equilibrio (MKT 2500 → ~1,3 años vs MKT 500 → ~3,5 años), pero el costo cost-effective con MKT 500 alcanza 90% de viabilidad.</p>
          </div>
        </div>
        <div class="conclusion-highlight">
          <strong>Mensaje clave:</strong> la calidad operativa (frecuencia de releases) supera en importancia a la estrategia comercial (AB testing y presupuesto de marketing). Un producto estable con marketing bajo supera consistentemente a uno inestable con inversión alta.
        </div>
      </div>
    </div>
    """)

    # ── 12. PREGUNTAS ─────────────────────────────────────────────────────────
    slides.append("""
    <div class="slide slide-final">
      <div class="final-content">
        <div class="final-icon">?</div>
        <h1 class="final-title">¿Preguntas?</h1>
        <div class="final-team">
          <span>Claudio Sonntag</span>
          <span class="sep">·</span>
          <span>Ariel Pacay</span>
          <span class="sep">·</span>
          <span>Alison Reynoso</span>
        </div>
        <div class="final-subject">Simulación &nbsp;—&nbsp; UTN FRBA &nbsp;—&nbsp; 2026</div>
      </div>
    </div>
    """)

    return slides


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print("Generando presentación...")
    slides = build_slides()
    slides_html = "\n".join(slides)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Simulación SaaS — UTN FRBA</title>
  <style>{CSS}</style>
</head>
<body>
  <div id="progress" style="width:0%"></div>
  <div id="counter"></div>
  <div id="hint">← → Navegar &nbsp;·&nbsp; Space avanzar &nbsp;·&nbsp; F11 pantalla completa</div>

  <button class="nav-btn" id="btn-prev" title="Anterior">&#8592;</button>
  <button class="nav-btn" id="btn-next" title="Siguiente">&#8594;</button>

  <div id="pres">
{slides_html}
  </div>

  <script>{JS}</script>
</body>
</html>"""

    out = BASE_DIR / "presentacion_saas.html"
    out.write_text(html, encoding="utf-8")
    print(f"\nOK - Presentacion generada: {out}")
    print(f"  Diapositivas: {len(slides)}")
    print(f"  Tamano:       {out.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\n  Abrir en el navegador y presionar F11 para pantalla completa.")
    print("  Navegar con flechas <- -> o barra espaciadora.")


if __name__ == "__main__":
    main()
