#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_pdf_v4.py
Convierte la presentacion v4 a PDF usando Playwright (Chromium headless).
Cada slide queda en una pagina 4:3 (1024x768) con fondo completo.

Uso:
    python generar_pdf_v4.py
    Genera: presentacion_saas_v4.pdf
"""

import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

try:
    import generar_presentacion_v4 as v4
except ImportError as e:
    print(f"Error importando v4: {e}")
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────────────
# CSS que sobreescribe el layout de presentacion para impresion plana 4:3
# ──────────────────────────────────────────────────────────────────────────────
PRINT_CSS = """
@page {
  size: 1024px 768px;
  margin: 0;
}

html, body {
  overflow: visible !important;
  background: white !important;
  width: 1024px !important;
}

#pres {
  position: static !important;
  width: 1024px !important;
  height: auto !important;
  overflow: visible !important;
}

/* Todos los slides visibles, uno por pagina */
.slide {
  display: flex !important;
  position: relative !important;
  width: 1024px !important;
  height: 768px !important;
  page-break-after: always !important;
  break-after: page !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
}
.slide:last-child {
  page-break-after: avoid !important;
  break-after: avoid !important;
}

/* Ocultar controles de navegacion */
#progress, #counter, #hint,
.nav-btn { display: none !important; }

/* Asegurar que el footer de logo se muestre */
.slide-footer {
  display: flex !important;
}

/* La portada y slide final mantienen su fondo */
.slide-cover,
.slide-final {
  background: linear-gradient(145deg, #0f172a 0%, #1e3a8a 55%, #0c1445 100%) !important;
}
"""


async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Error: playwright no instalado. Ejecutar: pip install playwright")
        print("       playwright install chromium")
        sys.exit(1)

    print("Generando HTML de impresion (4:3)...")
    slides = v4.build_slides()
    slides_html = "\n".join(slides)
    n_slides = len(slides)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Simulacion SaaS v4 - PDF</title>
  <style>{v4.CSS}</style>
  <style>{PRINT_CSS}</style>
</head>
<body>
<div id="pres">
{slides_html}
</div>
</body>
</html>"""

    # Archivo HTML intermedio (se borra al final)
    tmp = BASE_DIR / "_tmp_pdf_print.html"
    tmp.write_text(html, encoding="utf-8")

    out = BASE_DIR / "presentacion_saas_v4.pdf"

    print(f"Iniciando Chromium ({n_slides} slides, 4:3)...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # viewport igual al tamano de pagina para que 100vw/vh den bien
            page = await browser.new_page(
                viewport={"width": 1024, "height": 768}
            )
            await page.goto(tmp.as_uri())
            # Esperar que las imagenes base64 terminen de renderizar
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(800)

            await page.pdf(
                path=str(out),
                width="1024px",
                height="768px",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            await browser.close()
    finally:
        tmp.unlink(missing_ok=True)

    size_mb = out.stat().st_size / 1024 / 1024
    print(f"OK - PDF generado: {out}")
    print(f"  Paginas: {n_slides}")
    print(f"  Tamano:  {size_mb:.1f} MB")


if __name__ == "__main__":
    asyncio.run(main())
