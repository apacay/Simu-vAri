#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exporta presentacion_saas_v2.html a PDF.
Cada slide se convierte en una página del PDF.

Requisitos:
    pip install playwright img2pdf
    playwright install chromium

Uso:
    python exportar_presentacion_pdf.py
"""

import asyncio
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
HTML_PATH = BASE_DIR / "presentacion_saas_v2.html"
PDF_PATH = BASE_DIR / "presentacion_saas_v2.pdf"

# Tamaño viewport para captura (16:9, buena resolución)
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Instala playwright: pip install playwright")
        print("Luego: playwright install chromium")
        return 1

    try:
        import img2pdf
    except ImportError:
        print("Instala img2pdf: pip install img2pdf")
        return 1

    if not HTML_PATH.exists():
        print(f"Error: No se encuentra {HTML_PATH}")
        return 1

    print(f"Exportando {HTML_PATH.name} -> {PDF_PATH.name} ...")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
        )

        await page.goto(f"file://{HTML_PATH.resolve().as_posix()}")
        await page.wait_for_load_state("networkidle")

        # Ocultar elementos de navegación para la captura
        await page.add_style_tag(
            content="""
            #progress, #counter, #hint, .nav-btn { display: none !important; }
            """
        )

        # Contar slides
        n_slides = await page.evaluate(
            "document.querySelectorAll('.slide').length"
        )

        temp_dir = Path(tempfile.mkdtemp())
        img_paths = []

        for i in range(n_slides):
            # Mostrar solo el slide i
            await page.evaluate(
                f"""
                document.querySelectorAll('.slide').forEach((s, idx) => {{
                    s.classList.toggle('active', idx === {i});
                }});
                """
            )
            await page.wait_for_timeout(100)

            img_path = temp_dir / f"slide_{i:03d}.png"
            await page.screenshot(path=str(img_path), type="png")
            img_paths.append(img_path)

        await browser.close()

    # Combinar imágenes en un solo PDF
    with open(PDF_PATH, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in img_paths]))

    # Limpiar temporales
    for p in img_paths:
        p.unlink(missing_ok=True)
    temp_dir.rmdir()

    print(f"Listo: {PDF_PATH} ({n_slides} páginas)")
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
