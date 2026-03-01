#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_presentacion_v3.py
Version mejorada: fuentes grandes, espacio aprovechado, logo UTN/FRBA, titulo correcto slide modelo.

Uso:
    python generar_presentacion_v3.py
    Abrir presentacion_saas_v3.html en el navegador (F11 pantalla completa).
    Navegar con flechas <- -> o barra espaciadora.
"""

import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

# ──────────────────────────────────────────────────────────────────────────────
# Logo UTN FRBA — PNG real embebido en base64
# ──────────────────────────────────────────────────────────────────────────────
_LOGO_PATH = Path(r"C:\Users\aripa\Downloads\logo_utn.png")

def _logo_b64() -> str:
    """Retorna data URI del logo PNG, o cadena vacía si no existe."""
    if not _LOGO_PATH.exists():
        print(f"  WARN: logo no encontrado en {_LOGO_PATH}")
        return ""
    return "data:image/png;base64," + base64.b64encode(_LOGO_PATH.read_bytes()).decode()

def logo_img(height: int, style: str = "") -> str:
    """Tag <img> del logo en el tamaño pedido."""
    src = _logo_b64()
    if not src:
        return ""
    extra = f' style="{style}"' if style else ""
    return f'<img src="{src}" alt="UTN FRBA" height="{height}"{extra}>'


def embed_img(rel_path: str):
    p = BASE_DIR / rel_path
    if not p.exists():
        print(f"  WARN: No encontrada: {p}")
        return None
    data = base64.b64encode(p.read_bytes()).decode()
    suffix = p.suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "svg": "image/svg+xml"}.get(suffix, "image/png")
    return f"data:{mime};base64,{data}"


def img_tag(rel_path: str, alt: str = "") -> str:
    src = embed_img(rel_path)
    if src is None:
        return f'<div class="img-missing">Imagen no encontrada: {rel_path}</div>'
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

#pres {
  width: 100vw; height: 100vh;
  position: relative; overflow: hidden;
}

.slide {
  position: absolute; inset: 0;
  display: none; background: var(--bg);
  flex-direction: column;
}
.slide.active { display: flex; }

/* ── Barra de progreso ── */
#progress {
  position: fixed; top: 0; left: 0; height: 5px;
  background: linear-gradient(90deg, #60a5fa, #34d399);
  transition: width 0.4s ease; z-index: 100;
}

/* ── Contador ── */
#counter {
  position: fixed; bottom: 14px; right: 20px;
  font-size: 15px; color: rgba(255,255,255,0.5);
  z-index: 100; letter-spacing: 0.5px;
}

/* ── Botones nav ── */
.nav-btn {
  position: fixed; top: 50%; transform: translateY(-50%);
  width: 46px; height: 46px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50%; color: white; font-size: 20px;
  cursor: pointer; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s; user-select: none;
}
.nav-btn:hover { background: rgba(255,255,255,0.28); }
#btn-prev { left: 14px; }
#btn-next { right: 14px; }

/* ── Hint ── */
#hint {
  position: fixed; bottom: 14px; left: 50%; transform: translateX(-50%);
  font-size: 13px; color: rgba(255,255,255,0.3); letter-spacing: 0.5px;
  z-index: 100; pointer-events: none; transition: opacity 0.5s;
}

/* ════════════════════════════════════════
   HEADER COMUN
   ════════════════════════════════════════ */
.slide-header {
  background: linear-gradient(90deg, var(--navy) 0%, var(--navy2) 100%);
  padding: 16px 36px;
  display: flex; align-items: center; gap: 20px;
  flex-shrink: 0;
}
.slide-header h2 {
  font-size: clamp(22px, 2.8vw, 32px);
  font-weight: 700; color: #ffffff; letter-spacing: -0.3px;
  flex: 1;
}
.header-logo { height: 42px; width: auto; flex-shrink: 0; }
.slide-tag {
  font-size: 18px; color: #93c5fd;
  background: rgba(255,255,255,0.12);
  padding: 5px 14px; border-radius: 12px;
  white-space: nowrap;
}

/* ── Cuerpo comun ── */
.slide-body {
  flex: 1; padding: 22px 36px;
  overflow: hidden; display: flex; flex-direction: column;
  gap: 16px;
}

/* ── Footer con logo (slides normales) ── */
.slide-footer {
  display: flex; align-items: center; justify-content: flex-end;
  padding: 8px 32px 10px;
  border-top: 1px solid var(--border);
  background: var(--white); flex-shrink: 0;
}
.slide-footer svg { height: 30px; width: auto; }

/* ════════════════════════════════════════
   PORTADA
   ════════════════════════════════════════ */
.slide-cover {
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 55%, #0c1445 100%);
  align-items: center; justify-content: center;
  text-align: center; padding: 36px 48px; gap: 0;
}
.cover-logo-wrap { margin-bottom: 22px; }
.cover-logo-wrap svg { height: 52px; width: auto; }
.cover-badge {
  font-size: 14px; letter-spacing: 3px; text-transform: uppercase;
  color: #93c5fd; margin-bottom: 22px;
  padding: 6px 20px; border: 1px solid #3b82f6;
  border-radius: 20px; display: inline-block;
}
.cover-title {
  font-size: clamp(34px, 5vw, 58px);
  font-weight: 800; color: #ffffff;
  line-height: 1.15; margin-bottom: 16px;
  text-shadow: 0 2px 20px rgba(0,0,0,0.4);
}
.cover-subtitle {
  font-size: clamp(18px, 2.2vw, 24px);
  color: #93c5fd; margin-bottom: 28px;
}
.cover-subtitle strong { color: #60a5fa; }
.cover-team {
  font-size: 20px; color: #94a3b8; margin-bottom: 36px;
}
.cover-team .sep { margin: 0 10px; color: #3b82f6; }
.cover-stats {
  display: flex; gap: 24px; justify-content: center; flex-wrap: wrap;
}
.cover-stat {
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 14px; padding: 18px 28px; min-width: 140px;
}
.stat-num {
  display: block; font-size: clamp(28px, 3.5vw, 42px);
  font-weight: 800; color: #60a5fa;
}
.stat-lbl {
  display: block; font-size: 16px; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 1px; margin-top: 4px;
}

/* ════════════════════════════════════════
   DOS COLUMNAS
   ════════════════════════════════════════ */
.two-col {
  flex-direction: row !important; gap: 24px;
}
/* cada columna ocupa todo el alto */
.two-col .col { flex: 1; display: flex; flex-direction: column; gap: 16px; }
/* cards y question-box se estiran para llenar */
.two-col .col > .card         { flex: 1; }
.two-col .col > .question-box { flex: 1; }
.two-col .col.img-col { justify-content: center; }

/* ════════════════════════════════════════
   CARDS
   ════════════════════════════════════════ */
.card {
  background: var(--white);
  border-radius: 12px; padding: 22px 24px;
  border-left: 5px solid transparent;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  display: flex; flex-direction: column; gap: 8px;
}
.card h3        { font-size: 24px; font-weight: 700; color: var(--text); }
.card p,
.card ul        { font-size: 24px; color: var(--text2); line-height: 1.6; }
.card ul        { padding-left: 22px; }
.card li        { margin-bottom: 6px; }
.card .card-icon { font-size: 32px; }

.card-blue  { border-left-color: var(--blue);  background: #eff6ff; }
.card-green { border-left-color: var(--green); background: #f0fdf4; }
.card-amber { border-left-color: var(--amber); background: #fffbeb; }
.card-red   { border-left-color: var(--red);   background: #fef2f2; }

/* Caja de pregunta */
.question-box {
  background: linear-gradient(135deg, #1e3a8a, #1e40af);
  border-radius: 12px; padding: 24px;
  color: white; display: flex; flex-direction: column; gap: 10px;
}
.question-icon          { font-size: 36px; }
.question-box h3        { font-size: 24px; color: #93c5fd; }
.question-box p         { font-size: 20px; line-height: 1.7; }
.question-box strong    { color: #60a5fa; }

/* ════════════════════════════════════════
   SLIDE MODELO (Delta T / EaE)
   ════════════════════════════════════════ */
.model-diagram { flex: 1; display: flex; flex-direction: column; gap: 14px; }

.model-delta {
  background: linear-gradient(90deg, #0f172a, #1e3a8a);
  border-radius: 10px; padding: 14px 28px;
  display: flex; align-items: center; gap: 20px;
  flex-shrink: 0;
}
.delta-symbol { font-size: 32px; font-weight: 900; color: #ffffff; font-style: italic; }
.delta-label  { font-size: 18px; color: #93c5fd; letter-spacing: 0.5px; }

.events-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: 1fr 1fr;
  gap: 12px; flex: 1; align-items: stretch;
}
.event-box {
  border-radius: 10px; padding: 14px 10px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; gap: 10px;
  font-size: 23px; font-weight: 500; color: var(--text);
  box-shadow: 0 1px 3px rgba(0,0,0,0.07);
  line-height: 1.3;
}
.event-icon   { font-size: 32px; }
.event-blue   { background: #eff6ff; border: 1px solid #bfdbfe; }
.event-green  { background: #f0fdf4; border: 1px solid #bbf7d0; }
.event-amber  { background: #fffbeb; border: 1px solid #fde68a; }

.model-state {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
  padding: 14px 18px;
  background: var(--white); border-radius: 8px;
  border: 1px solid var(--border); flex-shrink: 0;
}
.state-label { font-size: 22px; font-weight: 700; color: var(--text2); margin-right: 4px; }
.state-pill  {
  font-size: 21px; padding: 7px 18px;
  background: var(--light-b); color: var(--navy);
  border-radius: 20px; font-weight: 500;
}

/* ════════════════════════════════════════
   VARIABLES
   ════════════════════════════════════════ */
.vars-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  grid-template-rows: 1fr;
  gap: 20px; flex: 1;
}
.var-card {
  background: var(--white); border-radius: 14px; padding: 26px 24px;
  display: flex; flex-direction: column; gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  border-top: 5px solid var(--navy);
}
.var-letter { font-size: 52px; font-weight: 900; color: var(--navy); line-height: 1; }
.var-name   { font-size: 26px; font-weight: 700; color: var(--text); }
.var-values { display: flex; flex-wrap: wrap; gap: 10px; }
.val-chip {
  font-size: 21px; padding: 8px 18px;
  border-radius: 20px; font-weight: 600;
}
.val-red   { background: var(--light-r); color: var(--red); }
.val-blue  { background: var(--light-b); color: var(--navy2); }
.val-green { background: var(--light-g); color: var(--green); }
.val-amber { background: var(--light-a); color: var(--amber); }
.var-hint  { font-size: 22px; color: var(--text2); font-style: italic; margin-top: auto; }

.formula-box {
  display: flex; align-items: center; justify-content: center; gap: 14px;
  background: var(--navy); color: white;
  border-radius: 10px; padding: 18px 28px;
  font-size: 22px; font-weight: 500; flex-wrap: wrap; flex-shrink: 0;
}
.formula-box strong { color: #93c5fd; font-size: 26px; }
.formula-result     { color: #34d399 !important; font-size: 32px !important; }

/* ════════════════════════════════════════
   SLIDES DE IMAGEN
   ════════════════════════════════════════ */
.img-slide-body {
  align-items: center; justify-content: center; gap: 14px;
  padding: 14px 36px !important;
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
  border-radius: 8px; font-size: 18px;
}
.img-legend {
  display: flex; gap: 24px; align-items: center;
  font-size: 22px; color: var(--text2);
  padding: 10px 20px; background: var(--white);
  border-radius: 8px; border: 1px solid var(--border);
  flex-shrink: 0;
}
.legend-green { color: var(--green); font-weight: 600; }
.legend-red   { color: var(--red);   font-weight: 600; }

.insight-banner {
  background: #fef3c7; border-left: 5px solid var(--amber);
  border-radius: 8px; padding: 16px 22px;
  display: flex; align-items: center; gap: 14px;
  font-size: 24px; color: #78350f; flex-shrink: 0;
}
.insight-icon { font-size: 28px; flex-shrink: 0; }

/* ════════════════════════════════════════
   HALLAZGO CRITICO
   ════════════════════════════════════════ */
.finding-card {
  background: var(--white); border-radius: 12px; padding: 14px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex; flex-direction: column; gap: 5px; flex: 1; min-height: 0; overflow: hidden;
}
.finding-card h3    { font-size: 22px; font-weight: 700; color: var(--text); line-height: 1.2; }
.finding-card p     { font-size: 18px; color: var(--text2); line-height: 1.4; }
.finding-icon       { font-size: 24px; }
.finding-stat       { font-size: 44px; font-weight: 900; line-height: 1; margin: 0; }
.finding-stat-label { font-size: 20px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text2); }
.finding-red   { border-top: 5px solid var(--red); }
.finding-red   .finding-stat { color: var(--red); }
.finding-green { border-top: 5px solid var(--green); }
.finding-green .finding-stat { color: var(--green); }

.img-col { flex: 1.1; display: flex; flex-direction: column; justify-content: center; }
.img-caption {
  font-size: 22px; color: var(--text2); text-align: center;
  font-style: italic; margin-top: 8px;
}

/* ════════════════════════════════════════
   TRES CASOS
   ════════════════════════════════════════ */
.three-body {
  flex-direction: row !important;
  align-items: stretch !important;
  gap: 18px !important;
  padding: 14px 28px !important;
}
.img-case {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; gap: 10px;
}
.img-case .img-container { flex: 1; width: 100%; }
.img-case-label {
  font-size: 22px; font-weight: 700; padding: 8px 20px;
  border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px;
  flex-shrink: 0;
}
.label-green { background: var(--light-g); color: var(--green); }
.label-blue  { background: var(--light-b); color: var(--navy2); }
.label-red   { background: var(--light-r); color: var(--red); }
.img-case-meta { font-size: 22px; color: var(--text2); font-style: italic; flex-shrink: 0; text-align: center; }

.cases-subtitle {
  text-align: center; font-size: 22px; color: var(--text2);
  padding: 10px 28px 12px; font-style: italic;
  border-top: 1px solid var(--border);
  background: var(--white); flex-shrink: 0;
}

/* ════════════════════════════════════════
   COST-EFFECTIVE
   ════════════════════════════════════════ */
.recommend-box {
  background: linear-gradient(135deg, #0f172a, #1e3a8a);
  border-radius: 14px; padding: 26px;
  color: white; display: flex; flex-direction: column; gap: 18px;
  flex: 1;
}
.recommend-title {
  font-size: clamp(22px, 2.5vw, 30px); font-weight: 800;
  color: #60a5fa; letter-spacing: -0.3px;
}
.recommend-metrics {
  display: grid; grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 16px; flex: 1;
}
.metric {
  background: rgba(255,255,255,0.09);
  border-radius: 10px; padding: 16px;
  display: flex; flex-direction: column; gap: 6px;
}
.metric-val        { font-size: 42px; font-weight: 800; }
.metric-val.green  { color: #34d399; }
.metric-val.blue   { color: #60a5fa; }
.metric-val.amber  { color: #fbbf24; }
.metric-lbl        { font-size: 21px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
.recommend-why {
  font-size: 23px; color: #cbd5e1; line-height: 1.7;
  border-top: 1px solid rgba(255,255,255,0.12);
  padding-top: 16px; flex-shrink: 0;
}
.recommend-why strong { color: #93c5fd; }

/* ════════════════════════════════════════
   WHY CARD (columna derecha cost-effective)
   ════════════════════════════════════════ */
.why-card {
  background: var(--white); border-radius: 14px; padding: 24px 28px;
  display: flex; flex-direction: column; gap: 14px; flex: 1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.why-card h3 { font-size: 22px; font-weight: 700; color: var(--text); }
.why-ul {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 10px; flex: 1;
}
.why-ul li {
  font-size: 20px; color: var(--text2); line-height: 1.4;
  padding-left: 26px; position: relative;
}
.why-ul li::before {
  content: "✓"; position: absolute; left: 0; color: var(--green); font-weight: 700;
}
.why-risk {
  background: #fff7ed; border-left: 4px solid var(--amber);
  border-radius: 8px; padding: 12px 16px;
  font-size: 19px; color: #92400e; line-height: 1.5; flex-shrink: 0;
}

/* ════════════════════════════════════════
   EQ CALLOUTS (slide tasa equilibrio)
   ════════════════════════════════════════ */
.eq-callouts { display: flex; gap: 18px; flex-shrink: 0; }
.eq-callout {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px;
  border-radius: 10px; padding: 14px 18px; text-align: center;
}
.eq-callout-val { font-size: 36px; font-weight: 900; line-height: 1; }
.eq-callout-lbl { font-size: 19px; color: var(--text2); line-height: 1.4; }
.eq-red   { background: var(--light-r); }
.eq-red   .eq-callout-val { color: var(--red); }
.eq-amber { background: #fef3c7; }
.eq-amber .eq-callout-val { color: #b45309; }
.eq-green { background: var(--light-g); }
.eq-green .eq-callout-val { color: var(--green); }

/* ════════════════════════════════════════
   MEJOR vs PEOR
   ════════════════════════════════════════ */
.comparison-banner {
  display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
  padding: 16px 22px;
  background: var(--white); border-radius: 10px;
  border: 1px solid var(--border); flex-shrink: 0;
}
.comp-item        { display: flex; flex-direction: column; gap: 4px; flex: 1; border-radius: 8px; padding: 12px 16px; }
.comp-item.comp-green { background: var(--light-g); }
.comp-item.comp-red   { background: var(--light-r); }
.comp-label       { font-size: 21px; color: var(--text2); }
.comp-val         { font-size: 30px; font-weight: 800; }
.comp-item.comp-green .comp-val { color: var(--green); }
.comp-item.comp-red   .comp-val { color: var(--red);   }
.comp-divider     { font-size: 26px; font-weight: 800; color: var(--text2); padding: 0 8px; }
.comp-diff        {
  width: 100%; text-align: center; font-size: 22px; color: var(--text2);
  border-top: 1px solid var(--border); padding-top: 10px; margin-top: 4px;
}
.comp-diff strong { color: var(--text); }

/* ════════════════════════════════════════
   CONCLUSIONES
   ════════════════════════════════════════ */
.conclusions-grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  grid-template-rows: 1fr 1fr;
  gap: 16px; flex: 1; align-content: stretch;
}
.conclusion-card {
  background: var(--white); border-radius: 12px; padding: 20px 22px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.07);
  display: flex; flex-direction: column; gap: 8px;
  position: relative; overflow: hidden;
}
.conclusion-num {
  position: absolute; top: 14px; right: 16px;
  font-size: 40px; font-weight: 900; color: var(--border); line-height: 1;
}
.conclusion-icon    { font-size: 32px; }
.conclusion-card h3 { font-size: 22px; font-weight: 700; color: var(--text); padding-right: 48px; }
.conclusion-card p  { font-size: 23px; color: var(--text2); line-height: 1.6; }

.conclusion-highlight {
  background: linear-gradient(90deg, var(--navy), var(--navy2));
  color: white; border-radius: 10px; padding: 16px 22px;
  font-size: 24px; line-height: 1.7; flex-shrink: 0;
}
.conclusion-highlight strong { color: #93c5fd; }

/* ════════════════════════════════════════
   SLIDE FINAL
   ════════════════════════════════════════ */
.slide-final {
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 55%, #0c1445 100%);
  align-items: center; justify-content: center; text-align: center;
}
.final-content { display: flex; flex-direction: column; align-items: center; gap: 22px; }
.final-logo-wrap { margin-bottom: 4px; }
.final-logo-wrap svg { height: 54px; width: auto; }
.final-icon {
  width: 110px; height: 110px; border-radius: 50%;
  background: rgba(96,165,250,0.15); border: 3px solid #3b82f6;
  display: flex; align-items: center; justify-content: center;
  font-size: 58px; font-weight: 900; color: #60a5fa; line-height: 1;
}
.final-title  { font-size: clamp(44px, 7vw, 76px); font-weight: 900; color: #ffffff; }
.final-team   { font-size: 18px; color: #94a3b8; }
.final-team .sep { margin: 0 10px; color: #3b82f6; }
.final-subject {
  font-size: 14px; letter-spacing: 2px; text-transform: uppercase; color: #475569;
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
    progress.style.width = (total > 1 ? idx / (total-1) : 1) * 100 + '%';
    counter.textContent  = (idx+1) + ' / ' + total;
    if (hint) hint.style.opacity = idx === 0 ? '1' : '0';
  }

  function next() { if (current < total-1) show(current+1); }
  function prev() { if (current > 0)       show(current-1); }

  document.addEventListener('keydown', e => {
    if (e.key==='ArrowRight'||e.key===' '||e.key==='ArrowDown') { e.preventDefault(); next(); }
    if (e.key==='ArrowLeft' ||e.key==='ArrowUp')                { e.preventDefault(); prev(); }
  });
  document.getElementById('btn-next').addEventListener('click', next);
  document.getElementById('btn-prev').addEventListener('click', prev);

  let tx = 0;
  document.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, {passive:true});
  document.addEventListener('touchend',   e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (dx < -50) next(); else if (dx > 50) prev();
  }, {passive:true});

  show(0);
})();
"""

# helpers generados en tiempo de ejecucion (PNG embebido)
def FOOTER() -> str:
    return f'<div class="slide-footer">{logo_img(32)}</div>'

def HEADER_LOGO() -> str:
    # fondo blanco con radio para que el logo sea visible sobre el header azul
    return f'<span class="header-logo">{logo_img(40, "background:white;border-radius:6px;padding:2px 6px;")}</span>'


# ──────────────────────────────────────────────────────────────────────────────
# SLIDES
# ──────────────────────────────────────────────────────────────────────────────
def build_slides() -> list:
    slides = []

    # logos pre-calculados para reutilizar
    _footer      = FOOTER()
    _header_logo = HEADER_LOGO()
    _logo_cover  = logo_img(80, "background:white;border-radius:10px;padding:4px 14px;")
    _logo_final  = logo_img(54, "background:white;border-radius:8px;padding:3px 10px;")

    # ── 1. PORTADA ────────────────────────────────────────────────────────────
    slides.append(f"""
    <div class="slide slide-cover">
      <div class="cover-logo-wrap">{_logo_cover}</div>
      <div class="cover-badge">Ingenieria en Sistemas &nbsp;·&nbsp; Simulacion &nbsp;·&nbsp; UTN FRBA</div>
      <h1 class="cover-title">Simulacion de Plataforma SaaS<br>de Soporte Tecnico</h1>
      <p class="cover-subtitle">Benchmark de viabilidad economica a <strong>10 a&ntilde;os</strong></p>
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
          <span class="stat-num">10 a&ntilde;os</span>
          <span class="stat-lbl">Horizonte simulado</span>
        </div>
      </div>
    </div>
    """)

    # ── 2. EL NEGOCIO ─────────────────────────────────────────────────────────
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>El Negocio y la Pregunta</h2>
        {_header_logo}
      </div>
      <div class="slide-body two-col">
        <div class="col">
          <div class="card card-blue">
            <div class="card-icon">&#x1F3E2;</div>
            <h3>Plataforma SaaS de Soporte</h3>
            <p>Conecta <strong>tecnicos</strong> con <strong>clientes</strong> que necesitan soporte tecnico bajo demanda. Tres tipos de trabajo: Apps (52%), IT (43%), Desarrollo (5%).</p>
          </div>
          <div class="card card-green">
            <div class="card-icon">&#x1F4B3;</div>
            <h3>Dos modelos de ingresos</h3>
            <ul>
              <li><strong>Suscripcion</strong> &mdash; tarifa mensual recurrente</li>
              <li><strong>Prepago</strong> &mdash; paquetes de minutos por adelantado</li>
            </ul>
          </div>
        </div>
        <div class="col">
          <div class="question-box">
            <div class="question-icon">&#x2753;</div>
            <h3>Pregunta de investigacion</h3>
            <p>&iquest;Que combinacion de <strong>frecuencia de releases</strong>, <strong>presupuesto de marketing</strong> y <strong>mix de modelos de pago</strong> maximiza la viabilidad economica a largo plazo?</p>
          </div>
          <div class="card card-amber">
            <div class="card-icon">&#x1F52C;</div>
            <h3>&iquest;Por que simulacion?</h3>
            <p>Permite explorar <strong>135.000 escenarios</strong> que serian imposibles de experimentar en la realidad sin costos ni riesgos.</p>
          </div>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 3. MODELO (titulo corregido) ──────────────────────────────────────────
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Modelo &Delta;T Constante &mdash; Flujo Evento a Evento (EaE) por dia</h2>
        {_header_logo}
      </div>
      <div class="slide-body">
        <div class="model-diagram">
          <div class="model-delta">
            <span class="delta-symbol">&Delta;t = 1 dia</span>
            <span class="delta-label">detalle diario &nbsp;&middot;&nbsp; EaE dentro del paso &nbsp;&middot;&nbsp; 3.650 dias por corrida</span>
          </div>
          <div class="events-grid">
            <div class="event-box event-blue">
              <span class="event-icon">&#x1F465;</span>
              <span>Contratacion / Renuncia de tecnicos</span>
            </div>
            <div class="event-box event-green">
              <span class="event-icon">&#x1F4E5;</span>
              <span>Llegada de clientes nuevos</span>
            </div>
            <div class="event-box event-amber">
              <span class="event-icon">&#x1F527;</span>
              <span>Atencion de tickets</span>
            </div>
            <div class="event-box event-blue">
              <span class="event-icon">&#x1F680;</span>
              <span>Implementacion de releases</span>
            </div>
            <div class="event-box event-green">
              <span class="event-icon">&#x1F4B5;</span>
              <span>Cobro de suscripciones</span>
            </div>
            <div class="event-box event-amber">
              <span class="event-icon">&#x1F4B8;</span>
              <span>Pago de sueldos</span>
            </div>
            <div class="event-box event-blue">
              <span class="event-icon">&#x1F504;</span>
              <span>Renovacion de prepagos</span>
            </div>
            <div class="event-box event-green">
              <span class="event-icon">&#x1F4CA;</span>
              <span>Churn y satisfaccion de usuarios</span>
            </div>
          </div>
        </div>
        <div class="model-state">
          <span class="state-label">Variables de estado:</span>
          <span class="state-pill">T (reloj)</span>
          <span class="state-pill">Clientes por modalidad</span>
          <span class="state-pill">Tecnicos activos</span>
          <span class="state-pill">Creditos disponibles</span>
          <span class="state-pill">Satisfaccion acumulada</span>
          <span class="state-pill">Fecha ultimo release</span>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 4. VARIABLES ──────────────────────────────────────────────────────────
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Variables de Control &mdash; Espacio de Configuraciones</h2>
        {_header_logo}
      </div>
      <div class="slide-body">
        <div class="vars-grid">
          <div class="var-card">
            <div class="var-letter">N</div>
            <div class="var-name">Frecuencia de Releases</div>
            <div class="var-values">
              <span class="val-chip val-red">7 d &mdash; Semanal</span>
              <span class="val-chip val-blue">30 d &mdash; Mensual</span>
              <span class="val-chip val-green">90 d &mdash; Trimestral</span>
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
            <div class="var-hint">Mayor inversion acelera la adquisicion de clientes</div>
          </div>
          <div class="var-card">
            <div class="var-letter">AB</div>
            <div class="var-name">Mix Suscripcion / Prepago</div>
            <div class="var-values">
              <span class="val-chip val-green">0-100 (100% Prepago)</span>
              <span class="val-chip val-blue">50-50 (Hibrido)</span>
              <span class="val-chip val-amber">100-0 (100% Suscripcion)</span>
            </div>
            <div class="var-hint">Proporcion de clientes en cada modalidad de pago</div>
          </div>
        </div>
        <div class="formula-box">
          3 releases &nbsp;&times;&nbsp; 3 marketing &nbsp;&times;&nbsp; 3 AB testing &nbsp;=&nbsp;
          <strong>27 configs.</strong>
          &nbsp;&times;&nbsp; <strong>5.000 corridas</strong>
          &nbsp;&times;&nbsp; <strong>3.650 dias</strong>
          &nbsp;=&nbsp; <strong class="formula-result">135.000 escenarios</strong>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 5. HEATMAP ────────────────────────────────────────────────────────────
    heatmap = img_tag("benchmark_10_anos/comparacion_heatmap_beneficio.png", "Heatmap beneficio")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Resultados Globales &mdash; Beneficio Neto a 10 Anos</h2>
        <span class="slide-tag">media de 5.000 corridas por configuracion</span>
        {_header_logo}
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">{heatmap}</div>
        <div class="img-legend">
          <span class="legend-green">&#9632; Verde = ganancia</span>
          <span class="legend-red">&#9632; Rojo = perdida</span>
          <span>valores en creditos</span>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 6. TOP / BOTTOM ───────────────────────────────────────────────────────
    top_bottom = img_tag("benchmark_10_anos/comparacion_top_bottom.png", "Top bottom configs")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Las 10 Mejores y 10 Peores Configuraciones</h2>
        {_header_logo}
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">{top_bottom}</div>
        <div class="insight-banner">
          <span class="insight-icon">&#x1F4A1;</span>
          <span>Las configuraciones con <strong>Releases Semanales</strong> dominan el fondo del ranking, sin importar el marketing ni el modelo de pago.</span>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 7. HALLAZGO CRITICO ───────────────────────────────────────────────────
    dia_eq = img_tag("benchmark_10_anos/dia_equilibrio_por_release.png", "Dia equilibrio por release")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Hallazgo Critico: La Frecuencia de Releases lo Decide Todo</h2>
        {_header_logo}
      </div>
      <div class="slide-body two-col">
        <div class="col">
          <div class="finding-card finding-red">
            <div class="finding-icon">&#x274C;</div>
            <h3>Releases Semanales</h3>
            <div class="finding-stat">0%</div>
            <div class="finding-stat-label">de corridas alcanzan equilibrio</div>
            <p>La inestabilidad destruye satisfaccion e impide la rentabilidad en <em>toda</em> configuracion evaluada. Beneficio medio: <strong style="color:#dc2626">&minus;1.100.000 creditos</strong>.</p>
          </div>
          <div class="finding-card finding-green">
            <div class="finding-icon">&#x2705;</div>
            <h3>Mensual / Trimestral</h3>
            <div class="finding-stat">74&ndash;100%</div>
            <div class="finding-stat-label">de corridas alcanzan equilibrio</div>
            <p>La plataforma estable permite ingresos recurrentes que superan los costos. Beneficio medio: <strong style="color:#059669">+2.300.000&ndash;2.600.000</strong>.</p>
          </div>
        </div>
        <div class="col img-col">
          <div class="img-container">{dia_eq}</div>
          <p class="img-caption">Dia medio al punto de equilibrio segun frecuencia de release</p>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 8. TRES CASOS ─────────────────────────────────────────────────────────
    eq_antes = img_tag(
        "benchmark_10_anos/casos_5_anos/equilibrio_antes/serie_beneficio_acumulado.png",
        "Equilibrio rapido")
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
        {_header_logo}
      </div>
      <div class="slide-body three-body">
        <div class="img-case">
          <span class="img-case-label label-green">Equilibrio mas rapido</span>
          <div class="img-container">{eq_antes}</div>
          <span class="img-case-meta">0-100 &middot; Trimestral &middot; MKT 2500 &mdash; dia ~433</span>
        </div>
        <div class="img-case">
          <span class="img-case-label label-blue">Cost-Effective</span>
          <div class="img-container">{cost_eff}</div>
          <span class="img-case-meta">50-50 &middot; Trimestral &middot; MKT 500 &mdash; dia ~1268</span>
        </div>
        <div class="img-case">
          <span class="img-case-label label-red">Menos Efectivo Viable</span>
          <div class="img-container">{menos_ef}</div>
          <span class="img-case-meta">100-0 &middot; Semanal &middot; MKT 500 &mdash; no alcanza eq.</span>
        </div>
      </div>
      <div class="cases-subtitle">
        Serie de beneficio acumulado &nbsp;&middot;&nbsp; Media &plusmn; 1&sigma; &nbsp;&middot;&nbsp; 1.000 corridas &nbsp;&middot;&nbsp; 5 a&ntilde;os
      </div>
      {_footer}
    </div>
    """)

    # ── 9a. COST-EFFECTIVE (bloque azul) ──────────────────────────────────────
    eq_config = img_tag("benchmark_10_anos/equilibrio_por_config.png", "Tasa equilibrio")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Configuracion Recomendada: Cost-Effective</h2>
        {_header_logo}
      </div>
      <div class="slide-body two-col">
        <div class="col">
          <div class="recommend-box">
            <div class="recommend-title">50-50 &nbsp;&middot;&nbsp; Releases Trimestrales &nbsp;&middot;&nbsp; Marketing 500</div>
            <div class="recommend-metrics">
              <div class="metric">
                <span class="metric-val green">242k</span>
                <span class="metric-lbl">creditos de beneficio</span>
              </div>
              <div class="metric">
                <span class="metric-val green">90%</span>
                <span class="metric-lbl">corridas con equilibrio</span>
              </div>
              <div class="metric">
                <span class="metric-val amber">~3,5 a&ntilde;os</span>
                <span class="metric-lbl">tiempo al equilibrio</span>
              </div>
              <div class="metric">
                <span class="metric-val blue">84,2%</span>
                <span class="metric-lbl">satisfaccion de clientes</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col">
          <div class="why-card">
            <h3>&iquest;Por que funciona a bajo costo?</h3>
            <ul class="why-ul">
              <li>Solo 500&nbsp;cr/mes de marketing: costo de adquisicion minimo</li>
              <li>Releases trimestrales garantizan estabilidad y evitan churn prematuro</li>
              <li>Modelo hibrido 50-50: entrada de caja (prepago) + recurrencia (suscripcion)</li>
              <li>Ingresos recurrentes compensan el crecimiento lento sin escala masiva</li>
            </ul>
            <div class="why-risk">
              &#x26A0; <strong>Riesgo residual:</strong> ~10% de escenarios no alcanzan equilibrio &mdash; requiere mayor tolerancia al plazo.
            </div>
          </div>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 9b. TASA DE EQUILIBRIO ────────────────────────────────────────────────
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Tasa de Equilibrio por Configuracion (27 escenarios)</h2>
        {_header_logo}
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">{eq_config}</div>
        <div class="eq-callouts">
          <div class="eq-callout eq-red">
            <span class="eq-callout-val">0%</span>
            <span class="eq-callout-lbl">Todas las configs con<br><strong>Releases Semanales</strong></span>
          </div>
          <div class="eq-callout eq-amber">
            <span class="eq-callout-val">74&ndash;90%</span>
            <span class="eq-callout-lbl">No-semanales con<br><strong>Marketing 500</strong></span>
          </div>
          <div class="eq-callout eq-green">
            <span class="eq-callout-val">100%</span>
            <span class="eq-callout-lbl">No-semanales con<br><strong>Marketing 1500+</strong></span>
          </div>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 10. MEJOR vs PEOR ─────────────────────────────────────────────────────
    mejor_peor = img_tag("benchmark_10_anos/mejor_vs_peor_config.png", "Mejor vs peor")
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Brecha entre Mejor y Peor Configuracion</h2>
        {_header_logo}
      </div>
      <div class="slide-body img-slide-body">
        <div class="img-container">{mejor_peor}</div>
        <div class="comparison-banner">
          <div class="comp-item comp-green">
            <span class="comp-label">&#x1F3C6; Mejor &mdash; 50-50 &middot; Trimestral &middot; MKT 2500</span>
            <span class="comp-val">+5.116.487 cr.</span>
          </div>
          <div class="comp-divider">vs</div>
          <div class="comp-item comp-red">
            <span class="comp-label">&#x1F480; Peor &mdash; 100-0 &middot; Semanal &middot; MKT 500</span>
            <span class="comp-val">&minus;1.598.935 cr.</span>
          </div>
          <div class="comp-diff">Diferencia total: <strong>6,7 millones de creditos</strong></div>
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 11. CONCLUSIONES ──────────────────────────────────────────────────────
    slides.append(f"""
    <div class="slide">
      <div class="slide-header">
        <h2>Conclusiones</h2>
        {_header_logo}
      </div>
      <div class="slide-body">
        <div class="conclusions-grid">
          <div class="conclusion-card">
            <div class="conclusion-num">01</div>
            <div class="conclusion-icon">&#x1F6A8;</div>
            <h3>Releases semanales = inviabilidad garantizada</h3>
            <p>0% de corridas alcanzan equilibrio. La inestabilidad repetida destruye valor en <em>todas</em> las configuraciones, sin importar marketing ni modelo de pago.</p>
          </div>
          <div class="conclusion-card">
            <div class="conclusion-num">02</div>
            <div class="conclusion-icon">&#x2705;</div>
            <h3>Mensual o Trimestral: 74%&ndash;100% de viabilidad</h3>
            <p>La estabilidad operativa es mas determinante que el modelo de negocio. Cambiar de semanal a trimestral aporta en promedio <strong>+3,7M creditos</strong>.</p>
          </div>
          <div class="conclusion-card">
            <div class="conclusion-num">03</div>
            <div class="conclusion-icon">&#x1F4A1;</div>
            <h3>El mix 50-50 maximiza el beneficio</h3>
            <p>El modelo hibrido equilibra entrada inicial (prepago) con recurrencia (suscripcion). Mejor config: <strong>+5,1M creditos</strong>, equilibrio en 100% de corridas.</p>
          </div>
          <div class="conclusion-card">
            <div class="conclusion-num">04</div>
            <div class="conclusion-icon">&#x1F4C8;</div>
            <h3>Trade-off marketing: velocidad vs riesgo</h3>
            <p>Mayor inversion acelera el equilibrio (MKT 2500 &rarr; ~1,3 a&ntilde;os vs MKT 500 &rarr; ~3,5 a&ntilde;os), pero MKT 500 alcanza 90% de viabilidad con costo minimo.</p>
          </div>
        </div>
        <div class="conclusion-highlight">
          <strong>Mensaje clave:</strong> la calidad operativa (frecuencia de releases) supera en importancia a la estrategia comercial. Un producto estable con marketing bajo supera consistentemente a uno inestable con inversion alta.
        </div>
      </div>
      {_footer}
    </div>
    """)

    # ── 12. PREGUNTAS ─────────────────────────────────────────────────────────
    slides.append(f"""
    <div class="slide slide-final">
      <div class="final-content">
        <div class="final-logo-wrap">{_logo_final}</div>
        <div class="final-icon">?</div>
        <h1 class="final-title">&iquest;Preguntas?</h1>
        <div class="final-team">
          <span>Claudio Sonntag</span>
          <span class="sep">&middot;</span>
          <span>Ariel Pacay</span>
          <span class="sep">&middot;</span>
          <span>Alison Reynoso</span>
        </div>
        <div class="final-subject">Simulacion &nbsp;&mdash;&nbsp; UTN FRBA &nbsp;&mdash;&nbsp; 2026</div>
      </div>
    </div>
    """)

    return slides


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print("Generando presentacion v3...")
    slides = build_slides()
    slides_html = "\n".join(slides)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Simulacion SaaS v3 -- UTN FRBA</title>
  <style>{CSS}</style>
</head>
<body>
  <div id="progress" style="width:0%"></div>
  <div id="counter"></div>
  <div id="hint">flechas o espacio para navegar &nbsp;|&nbsp; F11 pantalla completa</div>

  <button class="nav-btn" id="btn-prev" title="Anterior">&#8592;</button>
  <button class="nav-btn" id="btn-next" title="Siguiente">&#8594;</button>

  <div id="pres">
{slides_html}
  </div>

  <script>{JS}</script>
</body>
</html>"""

    out = BASE_DIR / "presentacion_saas_v3.html"
    out.write_text(html, encoding="utf-8")
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"OK - Generada: {out}")
    print(f"  Diapositivas: {len(slides)}")
    print(f"  Tamano: {size_mb:.1f} MB")
    print(f"  Abrir en navegador + F11 para pantalla completa.")


if __name__ == "__main__":
    main()
