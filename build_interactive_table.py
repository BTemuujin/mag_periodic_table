#!/usr/bin/env python3
"""
build_interactive_table.py

Compiles interactive_table.html:
- Visual fidelity matching magnetic_periodic_table.png (18-column grid, f-block, Box 1, Box 2)
- Filter and search toolbar
- Slide-out element drawer with 4 tabs
- TAB 2 (Crystallography) features an INTERACTIVE SCHEMATIC 3D CRYSTAL STRUCTURE & MAGNETIC SPIN VIEWER:
  * Schematic 3D Unit Cell with atomic spheres, lattice wireframe, and chemical coordination bonds (idealized pedagogical orientation model)
  * Magnetic Spin Vectors:
    - Ferromagnets (Fe, Co, Ni, Gd, Dy, Tb, Ho, Er): Directional 3D arrows pointing parallel along [001] in Electric Cyan
    - Antiferromagnets (Cr, Mn, Ce, Nd, Sm, Eu, Tm, Cm): Antiparallel 3D arrows on alternating sublattices (Cyan Up / Coral Down)
    - Paramagnets & Diamagnets: Crystal lattice without magnetic spin vectors
  * Interactive OrbitControls (rotate, zoom, pan, auto-rotate)
  * Fullscreen 3D Modal ("⛶ Fullscreen") with extensive metadata & lattice inspection
  * Self-contained embedded dataset (Zero-CORS data) with WebGL 3D visualizer and offline Canvas 2D fallback (Three.js and KaTeX loaded from CDN when online)
"""

import json
import os
import argparse
from pathlib import Path

def generate_html(
    enriched_json_path=None,
    output_html_path=None
):
    base_dir = Path(__file__).resolve().parent
    if enriched_json_path is None:
        enriched_candidate = base_dir / "magnetic_elements_enriched.json"
        base_candidate = base_dir / "magnetic_elements_db.json"
        enriched_json_path = enriched_candidate if enriched_candidate.exists() else base_candidate
    else:
        enriched_json_path = Path(enriched_json_path).resolve()

    if output_html_path is None:
        output_html_path = base_dir / "interactive_table.html"
    else:
        output_html_path = Path(output_html_path).resolve()

    with open(enriched_json_path, "r", encoding="utf-8") as f:
        elements_data = json.load(f)

    json_str = json.dumps(elements_data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Magnetic Periodic Table of the Elements - Interactive Web App with 3D Crystal Spins</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <!-- Three.js & OrbitControls for interactive 3D WebGL crystal visualization -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <!-- KaTeX for crisp mathematical and quantum physics formula rendering -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
  <style>
    :root {{
      --bg-page: #F8FAFC;
      --bg-card: #FFFFFF;
      --text-main: #0F172A;
      --text-muted: #64748B;
      --border-card: #E2E8F0;
      
      /* Legend / Magnetic Colors matching magnetic_periodic_table.png */
      --color-dia: #FFFFFF;
      --border-dia: #94A3B8;
      --text-dia: #0F172A;

      --color-para: #FEF08A;
      --border-para: #CA8A04;
      --text-para: #713F12;

      --color-ferro: #2563EB;
      --border-ferro: #1D4ED8;
      --text-ferro: #FFFFFF;

      --color-afm: #16A34A;
      --border-afm: #14532D;
      --text-afm: #FFFFFF;

      --color-lowt: #86EFAC;
      --border-lowt: #15803D;
      --text-lowt: #14532D;

      --color-star: #DC2626;
      --stripe-light: rgba(148, 163, 184, 0.40);
      --stripe-dark: rgba(255, 255, 255, 0.35);
      
      --drawer-width: 520px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg-page);
      color: var(--text-main);
      padding: 24px;
      line-height: 1.4;
      overflow-x: auto;
    }}

    .container {{
      max-width: 1720px;
      margin: 0 auto;
    }}

    /* HEADER BANNER */
    .header-banner {{
      background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
      color: #FFFFFF;
      border-radius: 12px;
      padding: 22px 28px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.12);
    }}

    .header-banner h1 {{
      font-size: 28px;
      font-weight: 900;
      letter-spacing: -0.5px;
      text-transform: uppercase;
      background: linear-gradient(90deg, #FFFFFF, #93C5FD);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 6px;
    }}

    .header-banner p {{
      color: #94A3B8;
      font-size: 14.5px;
      font-weight: 500;
    }}

    .header-banner .badge-suite {{
      display: flex;
      gap: 10px;
    }}

    .header-badge {{
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12.5px;
      font-weight: 600;
      color: #E2E8F0;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    /* TOP INFOGRAPHIC CARDS: BOX 1 & BOX 2 */
    .info-boxes-grid {{
      display: grid;
      grid-template-columns: 1fr 1.35fr;
      gap: 20px;
      margin-bottom: 20px;
    }}

    .info-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: 12px;
      padding: 18px 22px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }}

    .info-card-title {{
      font-size: 13.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: #334155;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .info-card-title span.tag {{
      background: #E2E8F0;
      color: #1E293B;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
    }}

    /* BOX 1: SAMPLE CELL */
    .sample-cell-wrapper {{
      display: flex;
      align-items: center;
      gap: 28px;
    }}

    .sample-cell-interactive {{
      position: relative;
      width: 130px;
      height: 140px;
      border: 2px solid var(--border-lowt);
      background-color: var(--color-lowt);
      color: var(--text-lowt);
      border-radius: 10px;
      padding: 8px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(22, 163, 74, 0.2);
      transition: all 0.2s ease;
      flex-shrink: 0;
    }}

    .sample-cell-interactive:hover {{
      transform: translateY(-3px) scale(1.04);
      box-shadow: 0 8px 20px rgba(22, 163, 74, 0.3);
    }}

    .sample-top-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .sample-num {{
      font-size: 14px;
      font-weight: 700;
    }}

    .sample-star {{
      color: var(--color-star);
      font-size: 18px;
      line-height: 1;
    }}

    .sample-sym {{
      font-size: 34px;
      font-weight: 800;
      text-align: center;
      margin-top: -2px;
      margin-bottom: -2px;
    }}

    .sample-weight {{
      font-size: 12px;
      text-align: center;
      font-weight: 500;
    }}

    .sample-temp {{
      font-size: 12px;
      font-weight: 700;
      text-align: center;
      background: rgba(0, 0, 0, 0.08);
      padding: 2px 4px;
      border-radius: 4px;
    }}

    .sample-temp sub {{
      font-size: 9px;
      vertical-align: sub;
    }}

    .sample-callouts {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 14px;
      font-size: 12.5px;
    }}

    .callout-item {{
      display: flex;
      align-items: center;
      gap: 7px;
    }}

    .callout-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #2563EB;
      flex-shrink: 0;
    }}

    .callout-item strong {{
      color: #0F172A;
    }}

    .sample-note {{
      grid-column: span 2;
      margin-top: 4px;
      padding-top: 6px;
      border-top: 1px dashed #CBD5E1;
      font-size: 11.5px;
      color: #475569;
    }}

    /* BOX 2: LEGEND */
    .legend-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      background: #F1F5F9;
      border: 1px solid #E2E8F0;
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      user-select: none;
    }}

    .legend-item:hover {{
      background: #E2E8F0;
      border-color: #CBD5E1;
      transform: translateY(-1px);
    }}

    .legend-item.active {{
      outline: 2px solid #2563EB;
      background: #DBEAFE;
    }}

    .legend-swatch {{
      width: 24px;
      height: 24px;
      border-radius: 6px;
      flex-shrink: 0;
      border: 1.5px solid;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
    }}

    .swatch-dia {{
      background-color: var(--color-dia);
      border-color: var(--border-dia);
    }}

    .swatch-para {{
      background-color: var(--color-para);
      border-color: var(--border-para);
    }}

    .swatch-ferro {{
      background-color: var(--color-ferro);
      border-color: var(--border-ferro);
      color: #FFFFFF;
    }}

    .swatch-afm {{
      background-color: var(--color-afm);
      border-color: var(--border-afm);
      color: #FFFFFF;
    }}

    .swatch-lowt {{
      background-color: var(--color-lowt);
      border-color: var(--border-lowt);
      color: var(--text-lowt);
    }}

    .swatch-radioactive {{
      background: repeating-linear-gradient(45deg, #FFFFFF, #FFFFFF 3px, rgba(148, 163, 184, 0.5) 3px, rgba(148, 163, 184, 0.5) 6px);
      border-color: #94A3B8;
    }}

    .swatch-star {{
      background: #FEE2E2;
      border-color: #F87171;
      color: var(--color-star);
      font-size: 14px;
    }}

    /* FILTER & SEARCH TOOLBAR */
    .toolbar-container {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: 12px;
      padding: 12px 18px;
      margin-bottom: 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }}

    .toolbar-left {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }}

    .filter-btn {{
      background: #F1F5F9;
      color: #334155;
      border: 1px solid #CBD5E1;
      padding: 6px 13px;
      border-radius: 20px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .filter-btn:hover {{
      background: #E2E8F0;
      color: #0F172A;
    }}

    .filter-btn.active {{
      background: #0F172A;
      color: #FFFFFF;
      border-color: #0F172A;
      box-shadow: 0 2px 6px rgba(15, 23, 42, 0.2);
    }}

    .filter-btn .count-tag {{
      background: rgba(0, 0, 0, 0.1);
      padding: 1px 6px;
      border-radius: 10px;
      font-size: 11px;
    }}

    .filter-btn.active .count-tag {{
      background: rgba(255, 255, 255, 0.25);
      color: #FFFFFF;
    }}

    .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .custom-select {{
      padding: 7px 12px;
      border: 1px solid #CBD5E1;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 500;
      background-color: #FFFFFF;
      color: #1E293B;
      cursor: pointer;
      outline: none;
    }}

    .custom-select:focus {{
      border-color: #2563EB;
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }}

    .search-box {{
      position: relative;
      display: flex;
      align-items: center;
    }}

    .search-input {{
      padding: 7px 12px 7px 32px;
      border: 1px solid #CBD5E1;
      border-radius: 8px;
      font-size: 13px;
      width: 220px;
      outline: none;
      transition: all 0.2s ease;
    }}

    .search-input:focus {{
      width: 280px;
      border-color: #2563EB;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }}

    .search-icon {{
      position: absolute;
      left: 10px;
      color: #94A3B8;
      font-size: 14px;
      pointer-events: none;
    }}

    .reset-btn {{
      background: transparent;
      border: none;
      color: #64748B;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      padding: 6px 10px;
      border-radius: 6px;
    }}

    .reset-btn:hover {{
      color: #DC2626;
      background: #FEE2E2;
    }}

    .filter-stats {{
      font-size: 12px;
      font-weight: 600;
      color: #64748B;
      white-space: nowrap;
    }}

    /* PERIODIC TABLE GRID */
    .table-container {{
      background: var(--bg-card);
      border: 1px solid var(--border-card);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
      position: relative;
    }}

    .periodic-table {{
      display: grid;
      grid-template-columns: repeat(18, minmax(0, 1fr));
      gap: 4px;
    }}

    /* ELEMENT CELL */
    .element-cell {{
      position: relative;
      border: 1.5px solid;
      border-radius: 6px;
      padding: 4px 3px 3px 3px;
      min-height: 82px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      cursor: pointer;
      transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.2s ease;
      user-select: none;
    }}

    .element-cell:hover {{
      transform: translateY(-3px) scale(1.06);
      z-index: 10;
      box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
    }}

    .element-cell.dimmed {{
      opacity: 0.14 !important;
      filter: grayscale(80%);
      pointer-events: none;
      transform: scale(0.96);
    }}

    .element-cell.active-highlight {{
      box-shadow: 0 0 0 3px #0F172A, 0 6px 16px rgba(0, 0, 0, 0.25);
      z-index: 5;
    }}

    /* Magnetic Styling */
    .element-cell.type-dia {{
      background-color: var(--color-dia);
      border-color: var(--border-dia);
      color: var(--text-dia);
    }}

    .element-cell.type-para {{
      background-color: var(--color-para);
      border-color: var(--border-para);
      color: var(--text-para);
    }}

    .element-cell.type-ferro {{
      background-color: var(--color-ferro);
      border-color: var(--border-ferro);
      color: var(--text-ferro);
    }}

    .element-cell.type-afm {{
      background-color: var(--color-afm);
      border-color: var(--border-afm);
      color: var(--text-afm);
    }}

    .element-cell.type-lowt {{
      background-color: var(--color-lowt);
      border-color: var(--border-lowt);
      color: var(--text-lowt);
    }}

    /* Radioactive diagonal hatch stripes */
    .element-cell.radioactive.type-dia {{
      background-image: repeating-linear-gradient(45deg, transparent, transparent 4px, var(--stripe-light) 4px, var(--stripe-light) 8px);
    }}
    .element-cell.radioactive.type-para {{
      background-image: repeating-linear-gradient(45deg, transparent, transparent 4px, var(--stripe-light) 4px, var(--stripe-light) 8px);
    }}
    .element-cell.radioactive.type-ferro,
    .element-cell.radioactive.type-afm {{
      background-image: repeating-linear-gradient(45deg, transparent, transparent 4px, var(--stripe-dark) 4px, var(--stripe-dark) 8px);
    }}
    .element-cell.radioactive.type-lowt {{
      background-image: repeating-linear-gradient(45deg, transparent, transparent 4px, var(--stripe-light) 4px, var(--stripe-light) 8px);
    }}

    .cell-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      line-height: 1;
    }}

    .cell-num {{
      font-size: 10px;
      font-weight: 700;
      opacity: 0.9;
    }}

    .cell-star {{
      color: var(--color-star);
      font-size: 13px;
      line-height: 1;
      font-weight: bold;
    }}

    .cell-sym {{
      font-size: 19px;
      font-weight: 800;
      text-align: center;
      letter-spacing: -0.5px;
      margin: 1px 0;
    }}

    .cell-weight {{
      font-size: 8.5px;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      opacity: 0.85;
      font-weight: 500;
    }}

    .cell-temp {{
      font-size: 8.5px;
      font-weight: 700;
      text-align: center;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
      padding-top: 2px;
      margin-top: 2px;
    }}

    .cell-temp sub {{
      font-size: 7px;
      vertical-align: sub;
    }}

    .element-cell.type-ferro .cell-temp,
    .element-cell.type-afm .cell-temp {{
      border-top-color: rgba(255, 255, 255, 0.25);
    }}

    /* Placeholder cells for Lanthanide / Actinide inline blocks */
    .placeholder-cell {{
      background: #F1F5F9;
      border: 1.5px dashed #94A3B8;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 9.5px;
      font-weight: 700;
      color: #475569;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      padding: 4px;
    }}

    .placeholder-cell:hover {{
      background: #E2E8F0;
      color: #0F172A;
    }}

    /* Gap row between main table and f-block */
    .grid-separator {{
      grid-column: span 18;
      height: 18px;
    }}

    /* Series Label Cells in F-Block */
    .series-label-cell {{
      grid-column: span 3;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 14px;
      font-size: 12.5px;
      font-weight: 700;
      color: #475569;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}

    /* SLIDE-OUT DRAWER / MODAL */
    .drawer-overlay {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(15, 23, 42, 0.45);
      backdrop-filter: blur(4px);
      z-index: 1000;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.25s ease, visibility 0.25s ease;
    }}

    .drawer-overlay.open {{
      opacity: 1;
      visibility: visible;
    }}

    .drawer {{
      position: fixed;
      top: 0;
      right: 0;
      width: var(--drawer-width);
      max-width: 95vw;
      height: 100vh;
      background: #FFFFFF;
      box-shadow: -10px 0 30px rgba(0, 0, 0, 0.2);
      z-index: 1001;
      transform: translateX(100%);
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}

    .drawer.open {{
      transform: translateX(0);
    }}

    /* Drawer Header */
    .drawer-header {{
      padding: 18px 22px;
      border-bottom: 1px solid #E2E8F0;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      position: relative;
    }}

    .drawer-header-content {{
      display: flex;
      gap: 16px;
      align-items: center;
    }}

    .drawer-elem-badge {{
      width: 72px;
      height: 76px;
      border-radius: 10px;
      border: 2px solid;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    /* Drawer badge classification color mapping */
    .drawer-elem-badge.type-dia {{
      background-color: var(--color-dia);
      border-color: var(--border-dia);
      color: var(--text-dia);
    }}
    .drawer-elem-badge.type-para {{
      background-color: var(--color-para);
      border-color: var(--border-para);
      color: var(--text-para);
    }}
    .drawer-elem-badge.type-ferro {{
      background-color: var(--color-ferro);
      border-color: var(--border-ferro);
      color: var(--text-ferro);
    }}
    .drawer-elem-badge.type-afm {{
      background-color: var(--color-afm);
      border-color: var(--border-afm);
      color: var(--text-afm);
    }}
    .drawer-elem-badge.type-lowt {{
      background-color: var(--color-lowt);
      border-color: var(--border-lowt);
      color: var(--text-lowt);
    }}
    .drawer-elem-badge.radioactive.type-dia,
    .drawer-elem-badge.radioactive.type-para,
    .drawer-elem-badge.radioactive.type-lowt {{
      background-image: repeating-linear-gradient(45deg, transparent, transparent 4px, var(--stripe-light) 4px, var(--stripe-light) 8px);
    }}
    .drawer-elem-badge.radioactive.type-ferro,
    .drawer-elem-badge.radioactive.type-afm {{
      background-image: repeating-linear-gradient(45deg, transparent, transparent 4px, var(--stripe-dark) 4px, var(--stripe-dark) 8px);
    }}

    .drawer-elem-badge .badge-num {{
      font-size: 11px;
      font-weight: 700;
    }}

    .drawer-elem-badge .badge-sym {{
      font-size: 30px;
      font-weight: 900;
      line-height: 1;
      margin-top: 1px;
    }}

    /* Physical disclaimer and scope banner */
    .schematic-disclaimer-card {{
      margin-top: 10px;
      padding: 10px 14px;
      background: #FFFBEB;
      border: 1px solid #FDE68A;
      border-left: 4px solid #F59E0B;
      border-radius: 6px;
      font-size: 11.5px;
      line-height: 1.45;
      color: #78350F;
    }}
    .disclaimer-header {{
      font-weight: 700;
      color: #92400E;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .drawer-elem-meta h2 {{
      font-size: 22px;
      font-weight: 800;
      color: #0F172A;
      margin-bottom: 3px;
    }}

    .drawer-elem-meta p {{
      font-size: 13px;
      color: #64748B;
      font-weight: 500;
    }}

    .drawer-close-btn {{
      background: #F1F5F9;
      border: none;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      color: #475569;
      transition: all 0.15s ease;
    }}

    .drawer-close-btn:hover {{
      background: #E2E8F0;
      color: #0F172A;
    }}

    .drawer-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 6px;
    }}

    .badge-tag {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .badge-tag.critical {{
      background: #FEE2E2;
      color: #B91C1C;
      border: 1px solid #FCA5A5;
    }}

    .badge-tag.radioactive {{
      background: #FEF3C7;
      color: #92400E;
      border: 1px solid #FCD34D;
    }}

    .badge-tag.mag-state {{
      background: #EFF6FF;
      color: #1D4ED8;
      border: 1px solid #BFDBFE;
    }}

    /* Drawer Tabs */
    .drawer-nav {{
      display: flex;
      border-bottom: 1px solid #E2E8F0;
      background: #F8FAFC;
      overflow-x: auto;
      scrollbar-width: thin;
    }}

    .tab-btn {{
      flex: 1 0 auto;
      padding: 11px 10px;
      font-size: 11.5px;
      font-weight: 700;
      color: #64748B;
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}

    .tab-btn:hover {{
      color: #0F172A;
      background: #F1F5F9;
    }}

    .tab-btn.active {{
      color: #2563EB;
      border-bottom-color: #2563EB;
      background: #FFFFFF;
    }}

    /* Drawer Content Body */
    .drawer-body {{
      padding: 18px 22px;
      overflow-y: auto;
      flex: 1;
    }}

    .tab-pane {{
      display: none;
    }}

    .tab-pane.active {{
      display: block;
      animation: fadeIn 0.2s ease;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* 3D CRYSTAL & SPIN VIEWER CARD */
    .crystal-3d-card {{
      background: #0B0F19;
      border: 1px solid #1E293B;
      border-radius: 10px;
      padding: 12px;
      margin-bottom: 18px;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
      color: #F8FAFC;
    }}

    .crystal-3d-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .crystal-3d-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12.5px;
      font-weight: 700;
      color: #E2E8F0;
    }}

    .spin-pill {{
      font-size: 10.5px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .spin-pill.ferro {{
      background: rgba(6, 182, 212, 0.15);
      color: #38BDF8;
      border: 1px solid rgba(56, 189, 248, 0.4);
    }}

    .spin-pill.afm {{
      background: rgba(244, 63, 94, 0.15);
      color: #FB7185;
      border: 1px solid rgba(251, 113, 133, 0.4);
    }}

    .spin-pill.none {{
      background: rgba(148, 163, 184, 0.15);
      color: #94A3B8;
      border: 1px solid rgba(148, 163, 184, 0.3);
    }}

    .crystal-btn-group {{
      display: flex;
      align-items: center;
      gap: 5px;
    }}

    .c-tool-btn {{
      background: #1E293B;
      color: #E2E8F0;
      border: 1px solid #334155;
      padding: 4px 9px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .c-tool-btn:hover {{
      background: #334155;
      color: #FFFFFF;
    }}

    .c-tool-btn.active {{
      background: #2563EB;
      border-color: #3B82F6;
      color: #FFFFFF;
    }}

    .c-tool-btn.primary {{
      background: #0284C7;
      border-color: #38BDF8;
      color: #FFFFFF;
    }}

    .c-tool-btn.primary:hover {{
      background: #0369A1;
    }}

    .canvas-3d-wrapper {{
      width: 100%;
      height: 270px;
      background: radial-gradient(circle at center, #111827 0%, #030712 100%);
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      cursor: grab;
      border: 1px solid #1E293B;
    }}

    .canvas-3d-wrapper:active {{
      cursor: grabbing;
    }}

    .canvas-3d-wrapper canvas {{
      width: 100% !important;
      height: 100% !important;
      display: block;
    }}

    .crystal-3d-caption {{
      margin-top: 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: #94A3B8;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .crystal-spin-legend {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .legend-indicator {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}

    .legend-dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      display: inline-block;
    }}

    .legend-dot.spin-up {{
      background-color: #06B6D4;
      box-shadow: 0 0 6px rgba(6, 182, 212, 0.7);
    }}

    .legend-dot.spin-down {{
      background-color: #F43F5E;
      box-shadow: 0 0 6px rgba(244, 63, 94, 0.7);
    }}

    .legend-dot.spin-none {{
      background-color: #64748B;
    }}

    .crystal-controls-hint {{
      font-size: 10.5px;
      color: #64748B;
    }}

    /* FULLSCREEN 3D MODAL */
    .crystal-modal-overlay {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(3, 7, 18, 0.85);
      backdrop-filter: blur(8px);
      z-index: 2000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}

    .crystal-modal-overlay.open {{
      display: flex;
    }}

    .crystal-modal-content {{
      width: 92vw;
      max-width: 1280px;
      height: 88vh;
      background: #0B0F19;
      border: 1px solid #1E293B;
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
      overflow: hidden;
    }}

    .crystal-modal-header {{
      padding: 16px 24px;
      border-bottom: 1px solid #1E293B;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #0F172A;
    }}

    .modal-header-meta h3 {{
      font-size: 18px;
      font-weight: 800;
      color: #F8FAFC;
    }}

    .modal-header-meta p {{
      font-size: 12.5px;
      color: #94A3B8;
      margin-top: 2px;
    }}

    .modal-header-controls {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .modal-close-btn {{
      background: #1E293B;
      border: 1px solid #334155;
      color: #94A3B8;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      transition: all 0.15s ease;
      margin-left: 6px;
    }}

    .modal-close-btn:hover {{
      background: #334155;
      color: #FFFFFF;
    }}

    .crystal-modal-body {{
      flex: 1;
      width: 100%;
      background: radial-gradient(circle at center, #111827 0%, #030712 100%);
      position: relative;
      cursor: grab;
    }}

    .crystal-modal-body:active {{
      cursor: grabbing;
    }}

    .crystal-modal-footer {{
      padding: 14px 24px;
      border-top: 1px solid #1E293B;
      background: #0F172A;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12.5px;
      color: #94A3B8;
    }}

    .modal-spin-note strong {{
      color: #38BDF8;
    }}

    .modal-footer-stats {{
      font-family: 'JetBrains Mono', monospace;
      color: #CBD5E1;
      font-size: 12px;
    }}

    /* Data presentation cards */
    .data-group {{
      margin-bottom: 20px;
    }}

    .data-group-title {{
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: #475569;
      margin-bottom: 10px;
      border-bottom: 1px solid #F1F5F9;
      padding-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .prop-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 7px 0;
      border-bottom: 1px dashed #F1F5F9;
      font-size: 13px;
    }}

    .prop-row:last-child {{
      border-bottom: none;
    }}

    .prop-name {{
      color: #64748B;
      font-weight: 500;
    }}

    .prop-val {{
      font-weight: 600;
      color: #0F172A;
      text-align: right;
    }}

    .prop-val.highlight {{
      color: #2563EB;
      font-weight: 700;
    }}

    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}

    /* QUANTUM & ADVANCED MAGNETISM STYLES */
    .quantum-hero-card {{
      background: linear-gradient(135deg, #0F172A, #1E293B);
      border-radius: 10px;
      padding: 14px 18px;
      margin-bottom: 16px;
      color: #F8FAFC;
      border: 1px solid #334155;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }}

    .role-badge-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .role-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #94A3B8;
    }}

    .role-badge {{
      font-size: 11.5px;
      font-weight: 800;
      padding: 3px 10px;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}

    .role-badge.role-hard {{
      background: rgba(168, 85, 247, 0.2);
      color: #C084FC;
      border: 1px solid #A855F7;
    }}

    .role-badge.role-soft {{
      background: rgba(16, 185, 129, 0.2);
      color: #34D399;
      border: 1px solid #10B981;
    }}

    .role-badge.role-mce {{
      background: rgba(245, 158, 11, 0.2);
      color: #FBBF24;
      border: 1px solid #F59E0B;
    }}

    .role-badge.role-inert {{
      background: rgba(148, 163, 184, 0.2);
      color: #CBD5E1;
      border: 1px solid #64748B;
    }}

    .role-explanation {{
      font-size: 12px;
      line-height: 1.5;
      color: #CBD5E1;
      margin: 0;
    }}

    .math-highlight-row {{
      background: #F8FAFC;
      border-radius: 6px;
      padding: 8px 10px;
      margin: 4px 0;
      border-bottom: 1px solid #E2E8F0 !important;
    }}

    .math-inline {{
      display: inline-block;
      vertical-align: middle;
    }}

    .term-symbol-display {{
      font-size: 16px;
      color: #1D4ED8;
      font-weight: 700;
    }}

    /* Materials Project Link Card */
    .mp-banner {{
      background: linear-gradient(135deg, #1E293B, #0F172A);
      color: #FFFFFF;
      border-radius: 10px;
      padding: 14px 18px;
      margin-top: 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .mp-banner-text h4 {{
      font-size: 13.5px;
      font-weight: 700;
      color: #F8FAFC;
    }}

    .mp-banner-text p {{
      font-size: 11.5px;
      color: #94A3B8;
    }}

    .mp-btn {{
      background: #2563EB;
      color: #FFFFFF;
      text-decoration: none;
      padding: 7px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      transition: background 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}

    .mp-btn:hover {{
      background: #1D4ED8;
    }}

    /* Drawer Footer Navigation */
    .drawer-footer {{
      padding: 14px 20px;
      border-top: 1px solid #E2E8F0;
      background: #F8FAFC;
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }}

    .drawer-nav-btn {{
      flex: 1;
      background: #FFFFFF;
      border: 1px solid #CBD5E1;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      color: #334155;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .drawer-nav-btn:hover {{
      background: #F1F5F9;
      border-color: #94A3B8;
      color: #0F172A;
    }}

    /* Pill list */
    .pill-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      justify-content: flex-end;
    }}

    .pill {{
      background: #E2E8F0;
      color: #334155;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
    }}

    /* FOOTER */
    .page-footer {{
      margin-top: 24px;
      text-align: center;
      font-size: 12.5px;
      color: #94A3B8;
    }}

    .page-footer a {{
      color: #2563EB;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>

<div class="container">

  <!-- HEADER BANNER -->
  <header class="header-banner">
    <div>
      <h1>Magnetic Periodic Table</h1>
      <p>Magnetic Ground States, Critical Transition Temperatures, USGS Critical Minerals & Radioactivity</p>
    </div>
    <div class="badge-suite">
      <div class="header-badge">
        <span>★</span> 50 USGS Critical Minerals
      </div>
      <div class="header-badge">
        <span>///</span> 37 Radioactive Elements
      </div>
      <div class="header-badge">
        <span>16</span> Ordered Magnets
      </div>
    </div>
  </header>

  <!-- TOP INFOGRAPHIC BOXES: HOW TO READ & LEGEND -->
  <section class="info-boxes-grid">
    
    <!-- BOX 1: HOW TO READ EACH ELEMENT CELL -->
    <div class="info-card">
      <div class="info-card-title">
        <span>Box 1: How to Read Each Element Cell</span>
        <span class="tag">Click to preview Dy</span>
      </div>
      <div class="sample-cell-wrapper">
        <div class="sample-cell-interactive" id="sample-dy-cell" title="Click to view detailed drawer for Dysprosium">
          <div class="sample-top-row">
            <span class="sample-num">66</span>
            <span class="sample-star">★</span>
          </div>
          <div class="sample-sym">Dy</div>
          <div class="sample-weight">162.50</div>
          <div class="sample-temp">T<sub>C</sub> = 85 K</div>
        </div>
        <div class="sample-callouts">
          <div class="callout-item">
            <div class="callout-dot"></div>
            <div><strong>Atomic Number</strong> (Z=66)</div>
          </div>
          <div class="callout-item">
            <div class="callout-dot"></div>
            <div><strong>Critical Mineral:</strong> Red Star (★)</div>
          </div>
          <div class="callout-item">
            <div class="callout-dot"></div>
            <div><strong>Element Symbol:</strong> Dy</div>
          </div>
          <div class="callout-item">
            <div class="callout-dot"></div>
            <div><strong>Standard Atomic Weight</strong></div>
          </div>
          <div class="callout-item" style="grid-column: span 2;">
            <div class="callout-dot"></div>
            <div><strong>Transition Temp:</strong> Curie (T<sub>C</sub>) / Néel (T<sub>N</sub>) in Kelvin</div>
          </div>
          <div class="sample-note">
            Radioactive elements (Z ≥ 84, Tc, Pm) are shaded with diagonal hatch stripes.
          </div>
        </div>
      </div>
    </div>

    <!-- BOX 2: LEGEND & MAGNETIC CLASSIFICATION -->
    <div class="info-card">
      <div class="info-card-title">
        <span>Box 2: Legend & Magnetic Classification</span>
        <span class="tag">Click category to filter</span>
      </div>
      <div class="legend-grid">
        <div class="legend-item" data-filter="diamagnet">
          <div class="legend-swatch swatch-dia"></div>
          <div>Diamagnet</div>
        </div>
        <div class="legend-item" data-filter="paramagnet">
          <div class="legend-swatch swatch-para"></div>
          <div>Paramagnet</div>
        </div>
        <div class="legend-item" data-filter="ferro">
          <div class="legend-swatch swatch-ferro"></div>
          <div>Ferromagnet [T<sub>C</sub> ≥ 290 K]</div>
        </div>
        <div class="legend-item" data-filter="afm">
          <div class="legend-swatch swatch-afm"></div>
          <div>Antiferromagnet [T<sub>N</sub> ≥ 290 K]</div>
        </div>
        <div class="legend-item" data-filter="lowt">
          <div class="legend-swatch swatch-lowt"></div>
          <div>Low-Temp Magnetic [&lt; 290 K]</div>
        </div>
        <div class="legend-item" data-filter="critical">
          <div class="legend-swatch swatch-star">★</div>
          <div>USGS Critical Mineral</div>
        </div>
        <div class="legend-item" data-filter="radioactive" style="grid-column: span 3;">
          <div class="legend-swatch swatch-radioactive">///</div>
          <div>Radioactive Element (No stable isotopes: Z ≥ 84, Tc, Pm)</div>
        </div>
      </div>
    </div>

  </section>

  <!-- FILTER & SEARCH TOOLBAR -->
  <section class="toolbar-container">
    <div class="toolbar-left">
      <button class="filter-btn active" data-filter="all">All Elements <span class="count-tag">118</span></button>
      <button class="filter-btn" data-filter="critical">★ Critical Minerals <span class="count-tag">50</span></button>
      <button class="filter-btn" data-filter="ferro">Ferromagnets [T<sub>C</sub> ≥ 290 K] <span class="count-tag">4</span></button>
      <button class="filter-btn" data-filter="afm">Antiferromagnets [T<sub>N</sub> ≥ 290 K] <span class="count-tag">1</span></button>
      <button class="filter-btn" data-filter="lowt">Low-Temp Magnetic <span class="count-tag">11</span></button>
      <button class="filter-btn" data-filter="radioactive">Radioactive <span class="count-tag">37</span></button>
    </div>
    <div class="toolbar-right">
      <select class="custom-select" id="role-filter">
        <option value="all">Tech Role: All (118)</option>
        <option value="Hard Magnetic Vector">Hard Magnetic Vector (8)</option>
        <option value="Soft Magnetic Core">Soft Magnetic Core (5)</option>
        <option value="Magnetocaloric Active Element">Magnetocaloric Active (5)</option>
        <option value="Magnetic Phase Stabilizer / Additive">Phase Stabilizer / Additive (5)</option>
        <option value="No primary commercial magnetic alloy role documented">No Commercial Magnetic Role (95)</option>
      </select>

      <select class="custom-select" id="crystal-filter">
        <option value="all">Crystal System: All</option>
        <option value="BCC">BCC</option>
        <option value="FCC">FCC</option>
        <option value="HCP">HCP</option>
        <option value="DHCP">DHCP</option>
        <option value="Diamond cubic">Diamond cubic</option>
        <option value="Rhombohedral">Rhombohedral</option>
        <option value="Orthorhombic">Orthorhombic</option>
        <option value="Tetragonal">Tetragonal (inc. BCT)</option>
        <option value="Monoclinic">Monoclinic</option>
        <option value="Hexagonal">Hexagonal</option>
        <option value="Simple cubic">Simple cubic</option>
        <option value="Cubic complex">Cubic complex</option>
      </select>

      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" class="search-input" id="search-input" placeholder="Search symbol, name, Z..." autocomplete="off">
      </div>

      <button class="reset-btn" id="reset-filters-btn" title="Reset all filters">Reset</button>
      <span class="filter-stats" id="filter-stats-text">Showing 118 of 118</span>
    </div>
  </section>

  <!-- 18-COLUMN PERIODIC TABLE -->
  <main class="table-container">
    <div class="periodic-table" id="periodic-table-grid">
      <!-- Cells dynamically populated by JavaScript -->
    </div>
  </main>

  <footer class="page-footer">
    <p>Magnetic Periodic Table Web Application &bull; Pair Programming with Antigravity &bull; Enriched with USGS, NIST, PubChem & Materials Project</p>
  </footer>

</div>

<!-- SLIDE-OUT DRAWER OVERLAY -->
<div class="drawer-overlay" id="drawer-overlay"></div>

<!-- SLIDE-OUT DRAWER -->
<aside class="drawer" id="element-drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-name">
  
  <header class="drawer-header">
    <div class="drawer-header-content">
      <div class="drawer-elem-badge" id="drawer-badge">
        <span class="badge-num" id="drawer-z">26</span>
        <span class="badge-sym" id="drawer-sym">Fe</span>
      </div>
      <div class="drawer-elem-meta">
        <h2 id="drawer-name">Iron</h2>
        <p><span id="drawer-mass">55.845</span> &bull; Period <span id="drawer-period">4</span>, Group <span id="drawer-group">8</span></p>
        <div class="drawer-tags" id="drawer-tag-container">
          <!-- Badges dynamically added -->
        </div>
      </div>
    </div>
    <button class="drawer-close-btn" id="drawer-close-btn" title="Close (Esc)">&times;</button>
  </header>

  <!-- Tabs Navigation -->
  <nav class="drawer-nav">
    <button class="tab-btn active" data-tab="tab-overview">Overview</button>
    <button class="tab-btn" data-tab="tab-quantum">Quantum &amp; Advanced Magnetism</button>
    <button class="tab-btn" data-tab="tab-crystal">Crystallography &amp; 3D</button>
    <button class="tab-btn" data-tab="tab-electronic">Electronic &amp; Chemical</button>
    <button class="tab-btn" data-tab="tab-physical">Physical / Thermal</button>
  </nav>

  <!-- Tabs Content Body -->
  <div class="drawer-body">
    
    <!-- TAB 1: OVERVIEW & GENERAL -->
    <div class="tab-pane active" id="tab-overview">
      <div class="data-group">
        <div class="data-group-title">🧲 Magnetic Ordering &amp; Ground State</div>
        <div class="prop-row">
          <span class="prop-name">Magnetic Classification</span>
          <span class="prop-val highlight" id="drawer-mag-class">Ferromagnet</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Ordering Type</span>
          <span class="prop-val" id="drawer-mag-order">Ferromagnetic</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Critical Transition Temp</span>
          <span class="prop-val highlight" id="drawer-mag-temp">T<sub>C</sub> = 1043 K (769.85 °C)</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Ordering Nature</span>
          <span class="prop-val" id="drawer-mag-desc">Long-range ferromagnetism at room temperature</span>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">★ USGS Strategic &amp; Critical Mineral Status</div>
        <div class="prop-row">
          <span class="prop-name">Official Critical Mineral</span>
          <span class="prop-val" id="drawer-usgs-status">Yes (2022 Final List)</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">USGS Commodity Group</span>
          <span class="prop-val" id="drawer-usgs-commodity">Rare Earth Element</span>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">☢ Nuclear &amp; Radioactivity Status</div>
        <div class="prop-row">
          <span class="prop-name">Radioactive</span>
          <span class="prop-val" id="drawer-radioactive-status">No (Stable Primordial Isotopes)</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Stability Assessment</span>
          <span class="prop-val" id="drawer-radioactive-desc">Naturally occurring stable ground state</span>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">📋 Periodic Classification</div>
        <div class="prop-row">
          <span class="prop-name">Chemical Family / Category</span>
          <span class="prop-val" id="drawer-category">Transition Metal</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Periodic Location</span>
          <span class="prop-val" id="drawer-period-group">Period 4, Group 8 (d-block)</span>
        </div>
      </div>
    </div>

    <!-- TAB 2: QUANTUM & ADVANCED MAGNETISM -->
    <div class="tab-pane" id="tab-quantum">
      
      <!-- Technological Role Hero Card -->
      <div class="quantum-hero-card">
        <div class="role-badge-row">
          <span class="role-label">Alloy / Material Role</span>
          <span class="role-badge role-soft" id="drawer-quantum-role-badge">Soft Magnetic Core</span>
        </div>
        <div style="margin-top: 6px; margin-bottom: 6px; font-size: 11.5px; color: #94A3B8;">
          <span>Intrinsic Elemental State: <strong id="drawer-intrinsic-state" style="color: #38BDF8;">Ferromagnet</strong></span>
        </div>
        <p class="role-explanation" id="drawer-quantum-role-desc">High saturation magnetization and low coercive field; ideal for transformer laminations, magnetic shielding, and electric motor stator cores.</p>
      </div>

      <!-- Quantum & Microscopic Group -->
      <div class="data-group">
        <div class="data-group-title">🔬 Quantum &amp; Microscopic Parameters</div>
        
        <div class="prop-row math-highlight-row">
          <span class="prop-name">Ground-State Term Symbol (<span class="math-inline" data-latex="{{}}^{{2S+1}}L_J"></span>)</span>
          <span class="prop-val term-symbol-display mono" id="drawer-q-term-symbol"></span>
        </div>
        
        <div class="prop-row">
          <span class="prop-name">Landé <span class="math-inline" data-latex="g"></span>-factor (<span class="math-inline" data-latex="g_J"></span>)</span>
          <span class="prop-val mono highlight" id="drawer-q-lande-g">1.500</span>
        </div>

        <div class="prop-row">
          <span class="prop-name">Neutral Gas Atom Moment (<span class="math-inline" data-latex="\\\\mu_{{\\\\mathrm{{eff}}}}"></span>, Hund's rules)</span>
          <span class="prop-val mono highlight" id="drawer-q-free-atom-moment">6.71 μ<sub>B</sub></span>
        </div>

        <div class="prop-row">
          <span class="prop-name">Bulk Ordered Moment (<span class="math-inline" data-latex="\\\\mu_{{\\\\mathrm{{ord}}}}"></span> at 0 K)</span>
          <span class="prop-val mono highlight" id="drawer-q-bulk-ordered-moment">2.22 μ<sub>B</sub></span>
        </div>

        <div class="prop-row" id="drawer-q-free-ion-row" style="display: none; flex-direction: column; align-items: flex-start; gap: 4px;">
          <span class="prop-name">Free Ion State (Condensed Matter / Salts)</span>
          <span class="prop-val mono" id="drawer-q-free-ion-state" style="font-size: 11.5px; text-align: left; line-height: 1.4; color: #E2E8F0;"></span>
        </div>
      </div>

      <!-- Thermodynamic & Macroscopic Magnetism Group -->
      <div class="data-group">
        <div class="data-group-title">🌡 Thermodynamic &amp; Macroscopic Magnetism</div>
        
        <div class="prop-row">
          <span class="prop-name">Molar Susceptibility (<span class="math-inline" data-latex="\\\\chi_m"></span> at 298 K)</span>
          <span class="prop-val mono" id="drawer-q-molar-chi">+1.20 × 10³ cm³/mol</span>
        </div>

        <div class="prop-row">
          <span class="prop-name">Curie-Weiss Temp (<span class="math-inline" data-latex="\\\\theta_{{\\\\mathrm{{CW}}}}"></span>)</span>
          <span class="prop-val mono" id="drawer-q-curie-weiss">1093.0 K (+819.85 °C)</span>
        </div>

        <div class="prop-row">
          <span class="prop-name">Saturation Magnetization (<span class="math-inline" data-latex="M_s"></span>)</span>
          <span class="prop-val mono" id="drawer-q-saturation-mag">2.15 T</span>
        </div>

        <div class="prop-row">
          <span class="prop-name">Magnetocrystalline Anisotropy (<span class="math-inline" data-latex="K_1"></span>)</span>
          <span class="prop-val mono" id="drawer-q-anisotropy">4.80 × 10⁴ J/m³</span>
        </div>
      </div>

      <!-- Spintronics & Microscopic Interactions Group -->
      <div class="data-group">
        <div class="data-group-title">⚡ Spintronics &amp; Exchange Interactions</div>
        
        <div class="prop-row">
          <span class="prop-name">Spin Polarization at <span class="math-inline" data-latex="E_{{\\\\mathrm{{F}}}}"></span> (<span class="math-inline" data-latex="P"></span>)</span>
          <span class="prop-val mono highlight" id="drawer-q-spin-polarization">44.0 %</span>
        </div>

        <div class="prop-row" style="flex-direction: column; align-items: flex-start; gap: 4px;">
          <span class="prop-name">Primary Exchange Interaction</span>
          <span class="prop-val" style="font-size: 12.5px; text-align: left; color: #0F172A; font-weight: 600;" id="drawer-q-exchange-interaction">Direct Exchange / Itinerant d-band Coupling</span>
        </div>
      </div>

    </div>

    <!-- TAB 3: CRYSTALLOGRAPHY WITH 3D VIEWER -->
    <div class="tab-pane" id="tab-crystal">
      
      <!-- INTERACTIVE 3D CRYSTAL & SPIN VIEWER CARD -->
      <div class="crystal-3d-card">
        <div class="crystal-3d-toolbar">
          <div class="crystal-3d-title">
            <span>🔬 Schematic Lattice &amp; Spin Vector Model (Illustrative)</span>
            <span class="spin-pill ferro" id="drawer-spin-badge">Ferromagnetic</span>
          </div>
          <div class="crystal-btn-group">
            <button class="c-tool-btn" id="drawer-btn-spins" title="Toggle magnetic spin arrows">🧲 Spins: ON</button>
            <button class="c-tool-btn" id="drawer-btn-box" title="Toggle unit cell wireframe">📦 Box: ON</button>
            <button class="c-tool-btn" id="drawer-btn-rotate" title="Toggle auto-rotation">🔄 Rotate: ON</button>
            <button class="c-tool-btn" id="drawer-btn-reset" title="Reset camera">↺ Reset</button>
            <button class="c-tool-btn primary" id="drawer-btn-expand" title="Expand Fullscreen 3D View">⛶ Fullscreen</button>
          </div>
        </div>

        <div class="canvas-3d-wrapper" id="drawer-canvas-container">
          <!-- 3D Canvas mounts here -->
        </div>

        <div class="crystal-3d-caption">
          <div class="crystal-spin-legend" id="drawer-spin-legend">
            <span class="legend-indicator" id="drawer-legend-up"><span class="legend-dot spin-up"></span> <span>Spin Up (&uarr;)</span></span>
            <span class="legend-indicator" id="drawer-legend-down"><span class="legend-dot spin-down"></span> <span>Spin Down (&darr;)</span></span>
            <span class="legend-indicator" id="drawer-legend-none" style="display:none;"><span class="legend-dot spin-none"></span> <span>Crystal Only (No Ordered Spins)</span></span>
          </div>
          <div class="crystal-controls-hint">
            <span>🖱 Drag: Rotate</span> &bull; <span>Scroll: Zoom</span> &bull; <span>Right-drag: Pan</span>
          </div>
        </div>

        <div class="schematic-disclaimer-card">
          <div class="disclaimer-header">⚠️ Schematic Model Scope &amp; Physical Assumptions</div>
          <div class="disclaimer-body">
            This 3D viewer displays an <strong>illustrative schematic unit cell</strong> with aspect ratios approximated where supported (BCC, FCC, HCP, Tetragonal, Orthorhombic) based on experimental lattice parameters (<em>a, b, c</em>). Collinear spin vectors represent idealized dipole orientations. Real magnetic ground states in complex elements (e.g. incommensurate spin-density waves in Cr, multi-sublattice 58-atom structures in &alpha;-Mn, or helical/cone spirals in Dy, Ho, Tb, Er) involve modulated propagation vectors <strong>k</strong> beyond single-cell collinear models. For paramagnets and diamagnets, only the atomic lattice is rendered without ordered dipoles.
          </div>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">💎 Crystal Structure &amp; Space Group</div>
        <div class="prop-row">
          <span class="prop-name">Crystal System</span>
          <span class="prop-val highlight" id="drawer-c-sys">BCC</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Space Group Symbol</span>
          <span class="prop-val mono" id="drawer-sg-sym">Im-3m</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Space Group Number</span>
          <span class="prop-val mono" id="drawer-sg-num">229</span>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">📐 Lattice Parameters (Å &amp; Degrees)</div>
        <div class="prop-row">
          <span class="prop-name">Lattice Constants (a, b, c)</span>
          <span class="prop-val mono" id="drawer-lattice-abc">a=2.87 Å, b=2.87 Å, c=2.87 Å</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Angles (α, β, γ)</span>
          <span class="prop-val mono" id="drawer-lattice-angles">α=90°, β=90°, γ=90°</span>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">🌐 Materials Project Ground State Reference</div>
        <div class="prop-row">
          <span class="prop-name">Materials Project ID</span>
          <span class="prop-val mono highlight" id="drawer-mp-id">mp-13</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Computed Density</span>
          <span class="prop-val" id="drawer-mp-rho">7.87 g/cm³</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Calculated Band Gap</span>
          <span class="prop-val" id="drawer-mp-eg">0.0 eV (Metallic)</span>
        </div>
        
        <div class="mp-banner" id="drawer-mp-banner">
          <div class="mp-banner-text">
            <h4>Materials Project Ground State</h4>
            <p id="drawer-mp-caption">Computed DFT Structure &amp; DOS</p>
          </div>
          <a href="#" target="_blank" rel="noopener noreferrer" class="mp-btn" id="drawer-mp-link">
            Explore MP ↗
          </a>
        </div>
      </div>
    </div>

    <!-- TAB 3: ELECTRONIC & CHEMICAL -->
    <div class="tab-pane" id="tab-electronic">
      <div class="data-group">
        <div class="data-group-title">⚡ Electron Configuration</div>
        <div class="prop-row">
          <span class="prop-name">Abbreviated Configuration</span>
          <span class="prop-val mono highlight" id="drawer-elec-abbrev">[Ar] 3d⁶ 4s²</span>
        </div>
        <div class="prop-row" style="flex-direction: column; align-items: flex-start; gap: 4px;">
          <span class="prop-name">Full Configuration</span>
          <span class="prop-val mono" style="font-size: 11.5px; text-align: left;" id="drawer-elec-full">1s² 2s² 2p⁶ 3s² 3p⁶ 3d⁶ 4s²</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Valence Electrons</span>
          <span class="prop-val" id="drawer-valence-count">8</span>
        </div>
      </div>

      <div class="data-group">
        <div class="data-group-title">⚛ Chemical &amp; Bonding Properties</div>
        <div class="prop-row">
          <span class="prop-name">Pauling Electronegativity</span>
          <span class="prop-val" id="drawer-electronegativity">1.83</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Bonding Preference</span>
          <span class="prop-val" id="drawer-bonding-pref">Metallic</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Common Oxidation States</span>
          <span class="prop-val">
            <span class="pill-list" id="drawer-ox-states">
              <span class="pill">+2</span><span class="pill">+3</span>
            </span>
          </span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Atomic Radius</span>
          <span class="prop-val" id="drawer-atomic-radius">156 pm</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Covalent Radius</span>
          <span class="prop-val" id="drawer-covalent-radius">132 pm</span>
        </div>
      </div>
    </div>

    <!-- TAB 4: PHYSICAL / THERMAL -->
    <div class="tab-pane" id="tab-physical">
      <div class="data-group">
        <div class="data-group-title">🌡 Thermodynamic &amp; State Constants</div>
        <div class="prop-row">
          <span class="prop-name">Standard State (STP)</span>
          <span class="prop-val" id="drawer-std-state">Solid</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Density (at STP)</span>
          <span class="prop-val highlight" id="drawer-density">7.874 g/cm³</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Melting Point</span>
          <span class="prop-val" id="drawer-melting-pt">1811 K (1537.85 °C)</span>
        </div>
        <div class="prop-row">
          <span class="prop-name">Boiling Point</span>
          <span class="prop-val" id="drawer-boiling-pt">3134 K (2860.85 °C)</span>
        </div>
      </div>
    </div>

  </div>

  <!-- Drawer Footer: Prev / Next Navigation -->
  <footer class="drawer-footer">
    <button class="drawer-nav-btn" id="drawer-prev-btn">&larr; Previous Element</button>
    <button class="drawer-nav-btn" id="drawer-next-btn">Next Element &rarr;</button>
  </footer>

</aside>

<!-- FULLSCREEN 3D CRYSTAL & SPIN MODAL -->
<div class="crystal-modal-overlay" id="crystal-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-elem-title">
  <div class="crystal-modal-content">
    <div class="crystal-modal-header">
      <div class="modal-header-meta">
        <h3 id="modal-elem-title">Iron (Fe) &bull; Schematic Lattice Structure &amp; Magnetic Spins</h3>
        <p id="modal-elem-subtitle">Space Group: Im-3m (#229) &bull; Ferromagnetic Ground State (T<sub>C</sub> = 1043 K)</p>
      </div>
      <div class="modal-header-controls">
        <button class="c-tool-btn" id="modal-btn-spins">🧲 Spins: ON</button>
        <button class="c-tool-btn" id="modal-btn-box">📦 Box: ON</button>
        <button class="c-tool-btn" id="modal-btn-rotate">🔄 Rotate: ON</button>
        <button class="c-tool-btn" id="modal-btn-reset">↺ Reset View</button>
        <button class="modal-close-btn" id="modal-close-btn" title="Close Fullscreen (Esc)">&times;</button>
      </div>
    </div>
    <div class="crystal-modal-body" id="modal-canvas-container">
      <!-- Fullscreen WebGL canvas injected here -->
    </div>
    <div class="crystal-modal-footer">
      <div id="modal-spin-description" class="modal-spin-note">
        <strong>Magnetic Configuration:</strong> Long-range ferromagnetic ordering with all moments aligned along [001].
      </div>
      <div class="modal-footer-stats" id="modal-lattice-stats">
        a = 2.87 Å, b = 2.87 Å, c = 2.87 Å &bull; α = 90°, β = 90°, γ = 90°
      </div>
      <div class="schematic-disclaimer-card" style="margin-top: 6px; width: 100%;">
        <div class="disclaimer-header">⚠️ Schematic Model Scope &amp; Physical Assumptions</div>
        <div class="disclaimer-body">
          Illustrative schematic unit cell model with aspect ratios approximated where supported based on experimental lattice parameters. Spin vectors represent idealized collinear dipoles. Complex multi-k or incommensurate spin arrangements (Cr SDW, helical rare earths) are presented schematically.
        </div>
      </div>
    </div>
  </div>
</div>

<!-- EMBEDDED ENRICHED DATABASE SCRIPT -->
<script id="embedded-elements-data" type="application/json">
{json_str}
</script>

<script>
/**
 * Interactive Magnetic Periodic Table Client Application
 * Includes Interactive 3D Crystal Structure & Magnetic Spin Vector Engine
 */
(function() {{
  let elementsData = [];
  let currentElementIndex = 25; // Default to Iron (Z=26, idx 25)
  let activeFilter = 'all';
  let activeCrystal = 'all';
  let activeRole = 'all';
  let searchQuery = '';

  // 3D Viewers
  let drawerCrystalViewer = null;
  let modalCrystalViewer = null;

  // DOM Elements
  const gridContainer = document.getElementById('periodic-table-grid');
  const drawer = document.getElementById('element-drawer');
  const overlay = document.getElementById('drawer-overlay');
  const closeBtn = document.getElementById('drawer-close-btn');
  const prevBtn = document.getElementById('drawer-prev-btn');
  const nextBtn = document.getElementById('drawer-next-btn');
  const sampleDyCell = document.getElementById('sample-dy-cell');
  const searchInput = document.getElementById('search-input');
  const crystalFilter = document.getElementById('crystal-filter');
  const roleFilter = document.getElementById('role-filter');
  const resetFiltersBtn = document.getElementById('reset-filters-btn');
  const filterStatsText = document.getElementById('filter-stats-text');

  // Modal DOM
  const modalOverlay = document.getElementById('crystal-modal-overlay');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const drawerExpandBtn = document.getElementById('drawer-btn-expand');

  // =========================================================================
  // 3D CRYSTAL & MAGNETIC SPIN ENGINE
  // =========================================================================
  
  // Element Color Palette for 3D Atoms
  function getElementColor(elem) {{
    const z = elem.atomic_number;
    const cat = elem.category || '';
    if (z === 26) return 0x8D99AE; // Fe (Slate iron)
    if (z === 24) return 0x38BDF8; // Cr (Chrome cyan)
    if (z === 27) return 0x2563EB; // Co (Cobalt blue)
    if (z === 28) return 0x0EA5E9; // Ni (Nickel)
    if (z === 25) return 0x8B5CF6; // Mn (Manganese purple)
    if (z === 64) return 0x10B981; // Gd (Emerald)
    if (z === 66) return 0x34D399; // Dy (Dysprosium)
    if (z === 29) return 0xD97706; // Cu (Copper)
    if (z === 79) return 0xF59E0B; // Au (Gold)
    if (z === 47) return 0xE2E8F0; // Ag (Silver)
    if (z === 6)  return 0x334155; // C (Graphite)
    if (z === 14) return 0x38BDF8; // Si (Silicon)
    if (z === 92) return 0x15803D; // U (Uranium green)
    if (cat.includes('Transition')) return 0x64748B;
    if (cat.includes('Lanthanide')) return 0x059669;
    if (cat.includes('Actinide')) return 0x047857;
    if (cat.includes('Alkali')) return 0xEF4444;
    if (cat.includes('Alkaline')) return 0xF97316;
    if (cat.includes('Noble')) return 0x818CF8;
    if (cat.includes('Halogen')) return 0x14B8A6;
    if (cat.includes('Nonmetal')) return 0x10B981;
    return 0x94A3B8;
  }}

  // Determine magnetic spin configuration with element-specific physical nuances
  function getElementSpinConfig(elem) {{
    const z = elem.atomic_number;
    const magClass = elem.magnetic_classification || '';
    const tempStr = elem.transition_temperature_str || '';
    const isFerro = magClass.startsWith('Ferromagnet') || tempStr.startsWith('T_C');
    const isAfm = magClass.startsWith('Antiferromagnet') || tempStr.startsWith('T_N');

    if (z === 24) {{
      return {{
        type: 'afm',
        label: 'Antiferromagnetic (SDW Modulated)',
        badgeClass: 'afm',
        desc: 'Incommensurate spin-density wave (SDW) antiferromagnetism along ⟨100⟩ with sinusoidal moment modulation (T_N = 311 K). Displayed with illustrative antiparallel sublattice vectors.'
      }};
    }} else if (z === 25) {{
      return {{
        type: 'afm',
        label: 'Antiferromagnetic (58-atom Complex)',
        badgeClass: 'afm',
        desc: 'Complex non-collinear antiferromagnetism within the 58-atom cubic α-Mn unit cell (T_N = 95 K). Rendered schematically on high-symmetry sites.'
      }};
    }} else if (z === 66 || z === 67 || z === 65 || z === 68) {{
      return {{
        type: 'ferro',
        label: 'Helical / Spiral → Ferromagnetic',
        badgeClass: 'ferro',
        desc: `Exhibits incommensurate helical / conical spin structures below T_N, locking into collinear ferromagnetism at cryogenic temperatures (${{tempStr}}). Rendered schematically.`
      }};
    }} else if (isFerro) {{
      return {{
        type: 'ferro',
        label: 'Ferromagnetic (Collinear Spontaneous)',
        badgeClass: 'ferro',
        desc: `Spontaneous long-range ferromagnetic ordering (${{tempStr}}). Dipole moments align parallel below Curie temperature.`
      }};
    }} else if (isAfm) {{
      return {{
        type: 'afm',
        label: 'Antiferromagnetic (Alternating Sublattices)',
        badgeClass: 'afm',
        desc: `Spontaneous long-range antiferromagnetic ordering (${{tempStr}}). Magnetic moments form alternating antiparallel sublattices (Sublattice A ↑ vs Sublattice B ↓).`
      }};
    }} else if (magClass.startsWith('Paramagnet')) {{
      return {{
        type: 'paramagnet',
        label: 'Paramagnetic (No Ordered Spins)',
        badgeClass: 'none',
        desc: 'Paramagnetic state: Unpaired atomic dipoles undergo continuous thermal fluctuations without spontaneous long-range ordering.'
      }};
    }} else {{
      return {{
        type: 'diamagnet',
        label: 'Diamagnetic (Paired Shells)',
        badgeClass: 'none',
        desc: 'Diamagnetic state: All electron shells are paired with zero net intrinsic magnetic moment.'
      }};
    }}
  }}

  // 3D Geometry Builder for various Crystal Systems (schematic lattice representation with aspect-ratio-scaled dimensions)
  function buildCrystalGeometry(elem) {{
    const cSys = (elem.crystallography && elem.crystallography.crystal_system) || 'BCC';
    const lp = (elem.crystallography && elem.crystallography.lattice_parameters) || {{}};
    const a0 = Math.max(0.5, Math.min(20.0, Number(lp.a) || 3.5));
    const b0 = Math.max(0.5, Math.min(20.0, Number(lp.b) || a0));
    const c0 = Math.max(0.5, Math.min(20.0, Number(lp.c) || a0));

    // Base unit cell scale and proportional aspect ratios bounded to visual viewing limits
    const baseL = 2.4;
    const aspectY = Math.max(0.65, Math.min(1.9, b0 / a0));
    const aspectZ = Math.max(0.65, Math.min(2.3, c0 / a0));
    const Lx = baseL;
    const Ly = baseL * aspectY;
    const Lz = baseL * aspectZ;
    const L = baseL;

    const spinConfig = getElementSpinConfig(elem);
    const atomColor = getElementColor(elem);
    const atoms = [];
    const bonds = [];
    const boxLines = [];

    // Helper: Add Atom
    function addAtom(x, y, z, spinDir) {{
      let sDir = null;
      let sColor = 0x06B6D4; // Cyan up
      if (spinConfig.type === 'ferro') {{
        sDir = [0, 0, 1];
        sColor = 0x06B6D4;
      }} else if (spinConfig.type === 'afm') {{
        if (spinDir !== null && spinDir !== undefined) {{
          sDir = spinDir;
          sColor = (spinDir[2] > 0) ? 0x06B6D4 : 0xF43F5E; // Cyan Up, Coral Down
        }}
      }}
      atoms.push({{ x, y, z, color: atomColor, spinDir: sDir, spinColor: sColor }});
    }}

    // Helper: Add Box line segment
    function addBoxLine(x1, y1, z1, x2, y2, z2) {{
      boxLines.push([x1, y1, z1, x2, y2, z2]);
    }}

    // Helper: Compute automatic bonds between atoms
    function autoBonds(cutoff) {{
      for (let i = 0; i < atoms.length; i++) {{
        for (let j = i + 1; j < atoms.length; j++) {{
          const dx = atoms[i].x - atoms[j].x;
          const dy = atoms[i].y - atoms[j].y;
          const dz = atoms[i].z - atoms[j].z;
          const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
          if (dist > 0.1 && dist <= cutoff) {{
            bonds.push([i, j]);
          }}
        }}
      }}
    }}

    // Helper: Box 12 edges for rectangular prism
    function makePrismBox(lx, ly, lz) {{
      const hx = lx / 2, hy = ly / 2, hz = lz / 2;
      // Bottom face
      addBoxLine(-hx, -hy, -hz,  hx, -hy, -hz);
      addBoxLine( hx, -hy, -hz,  hx,  hy, -hz);
      addBoxLine( hx,  hy, -hz, -hx,  hy, -hz);
      addBoxLine(-hx,  hy, -hz, -hx, -hy, -hz);
      // Top face
      addBoxLine(-hx, -hy,  hz,  hx, -hy,  hz);
      addBoxLine( hx, -hy,  hz,  hx,  hy,  hz);
      addBoxLine( hx,  hy,  hz, -hx,  hy,  hz);
      addBoxLine(-hx,  hy,  hz, -hx, -hy,  hz);
      // 4 Vertical Pillars
      addBoxLine(-hx, -hy, -hz, -hx, -hy,  hz);
      addBoxLine( hx, -hy, -hz,  hx, -hy,  hz);
      addBoxLine( hx,  hy, -hz,  hx,  hy,  hz);
      addBoxLine(-hx,  hy, -hz, -hx,  hy,  hz);
    }}

    // 1. BCC (Body-Centered Cubic / Pseudo-cubic)
    if (cSys === 'BCC') {{
      makePrismBox(Lx, Ly, Lz);
      const hx = Lx / 2, hy = Ly / 2, hz = Lz / 2;
      // 8 corners: In AFM (like Cr, Eu), corners are Spin UP
      const corners = [
        [-hx, -hy, -hz], [hx, -hy, -hz], [hx, hy, -hz], [-hx, hy, -hz],
        [-hx, -hy,  hz], [hx, -hy,  hz], [hx, hy,  hz], [-hx, hy,  hz]
      ];
      corners.forEach(p => addAtom(p[0], p[1], p[2], [0, 0, 1]));
      // 1 Body-center: In AFM, center is Spin DOWN
      addAtom(0, 0, 0, [0, 0, -1]);
      autoBonds(Math.max(Lx, Ly, Lz) * 0.9);
    }}
    // 2. FCC (Face-Centered Cubic)
    else if (cSys === 'FCC') {{
      makePrismBox(Lx, Ly, Lz);
      const hx = Lx / 2, hy = Ly / 2, hz = Lz / 2;
      // 8 corners
      const corners = [
        [-hx, -hy, -hz], [hx, -hy, -hz], [hx, hy, -hz], [-hx, hy, -hz],
        [-hx, -hy,  hz], [hx, -hy,  hz], [hx, hy,  hz], [-hx, hy,  hz]
      ];
      corners.forEach(p => addAtom(p[0], p[1], p[2], [0, 0, 1]));
      // 6 face centers: In Ce (AFM), face centers form antiparallel sublattices
      const faces = [
        [  0,   0, -hz], [  0,   0,  hz],
        [  0, -hy,   0], [  0,  hy,   0],
        [-hx,   0,   0], [ hx,   0,   0]
      ];
      faces.forEach(p => addAtom(p[0], p[1], p[2], [0, 0, -1]));
      autoBonds(Math.max(Lx, Ly, Lz) * 0.75);
    }}
    // 3. HCP (Hexagonal Close-Packed) & Hexagonal
    else if (cSys === 'HCP' || cSys === 'Hexagonal') {{
      const R = 1.35;
      const caRatio = Math.max(1.3, Math.min(3.2, c0 / a0));
      const H = R * caRatio;
      const hH = H / 2;
      // Hexagonal wireframe
      for (let i = 0; i < 6; i++) {{
        const a1 = (i * Math.PI) / 3;
        const a2 = ((i + 1) * Math.PI) / 3;
        const x1 = R * Math.cos(a1), y1 = R * Math.sin(a1);
        const x2 = R * Math.cos(a2), y2 = R * Math.sin(a2);
        // Bottom ring
        addBoxLine(x1, y1, -hH, x2, y2, -hH);
        // Top ring
        addBoxLine(x1, y1,  hH, x2, y2,  hH);
        // Vertical pillars
        addBoxLine(x1, y1, -hH, x1, y1,  hH);
      }}
      // Bottom basal plane: 6 vertices + 1 center (Spin UP)
      for (let i = 0; i < 6; i++) {{
        const a = (i * Math.PI) / 3;
        addAtom(R * Math.cos(a), R * Math.sin(a), -hH, [0, 0, 1]);
      }}
      addAtom(0, 0, -hH, [0, 0, 1]);

      // Top basal plane: 6 vertices + 1 center (Spin UP)
      for (let i = 0; i < 6; i++) {{
        const a = (i * Math.PI) / 3;
        addAtom(R * Math.cos(a), R * Math.sin(a), hH, [0, 0, 1]);
      }}
      addAtom(0, 0, hH, [0, 0, 1]);

      // Mid plane: 3 interior atoms forming equilateral triangle (In Tm AFM: Spin DOWN)
      const rMid = R * 0.577;
      for (let i = 0; i < 3; i++) {{
        const a = Math.PI / 6 + (i * 2 * Math.PI) / 3;
        addAtom(rMid * Math.cos(a), rMid * Math.sin(a), 0, [0, 0, -1]);
      }}
      autoBonds(R * 1.05);
    }}
    // 4. DHCP (Double Hexagonal Close-Packed: Nd, Cm, etc.)
    else if (cSys === 'DHCP') {{
      const R = 1.35;
      const H = 2.8;
      const hH = H / 2;
      for (let i = 0; i < 6; i++) {{
        const a1 = (i * Math.PI) / 3;
        const a2 = ((i + 1) * Math.PI) / 3;
        addBoxLine(R*Math.cos(a1), R*Math.sin(a1), -hH, R*Math.cos(a2), R*Math.sin(a2), -hH);
        addBoxLine(R*Math.cos(a1), R*Math.sin(a1),  hH, R*Math.cos(a2), R*Math.sin(a2),  hH);
        addBoxLine(R*Math.cos(a1), R*Math.sin(a1), -hH, R*Math.cos(a1), R*Math.sin(a1),  hH);
      }}
      // 4 Layers along Z: A (z = -hH), B (z = -hH/3), A (z = hH/3), C (z = hH)
      // Alternating spins for AFM (Nd, Cm)
      const layers = [
        {{ z: -hH, spin: [0, 0, 1] }},
        {{ z: -hH/3, spin: [0, 0, -1] }},
        {{ z:  hH/3, spin: [0, 0, 1] }},
        {{ z:  hH, spin: [0, 0, -1] }}
      ];
      layers.forEach((lyr, idx) => {{
        if (idx % 2 === 0) {{
          for (let i = 0; i < 6; i++) {{
            const a = (i * Math.PI) / 3;
            addAtom(R * Math.cos(a), R * Math.sin(a), lyr.z, lyr.spin);
          }}
          addAtom(0, 0, lyr.z, lyr.spin);
        }} else {{
          const rMid = R * 0.577;
          for (let i = 0; i < 3; i++) {{
            const a = Math.PI / 6 + (i * 2 * Math.PI) / 3;
            addAtom(rMid * Math.cos(a), rMid * Math.sin(a), lyr.z, lyr.spin);
          }}
        }}
      }});
      autoBonds(R * 1.05);
    }}
    // 5. Diamond Cubic (C, Si, Ge)
    else if (cSys === 'Diamond cubic') {{
      makePrismBox(L, L, L);
      const h = L / 2;
      // FCC corners + faces
      const fcc = [
        [-h,-h,-h], [h,-h,-h], [h,h,-h], [-h,h,-h],
        [-h,-h, h], [h,-h, h], [h,h, h], [-h,h, h],
        [0,0,-h], [0,0,h], [0,-h,0], [0,h,0], [-h,0,0], [h,0,0]
      ];
      fcc.forEach(p => addAtom(p[0], p[1], p[2], null));
      // 4 interior tetrahedral sites
      const q = L / 4;
      const tetra = [
        [-q, -q, -q], [q, q, -q], [-q, q, q], [q, -q, q]
      ];
      tetra.forEach(p => addAtom(p[0], p[1], p[2], null));
      autoBonds(L * 0.48);
    }}
    // 6. Cubic Complex (alpha-Mn)
    else if (cSys === 'Cubic complex') {{
      makePrismBox(L, L, L);
      const h = L / 2;
      // BCC outer frame (Spin Up)
      const corners = [
        [-h,-h,-h], [h,-h,-h], [h,h,-h], [-h,h,-h],
        [-h,-h, h], [h,-h, h], [h,h, h], [-h,h, h]
      ];
      corners.forEach(p => addAtom(p[0], p[1], p[2], [0, 0, 1]));
      // Inner tetrahedral cluster (Spin Down for AFM Mn)
      const q = L / 3.2;
      const inner = [
        [-q,-q,-q], [q,q,-q], [-q,q,q], [q,-q,q], [0,0,0]
      ];
      inner.forEach(p => addAtom(p[0], p[1], p[2], [0, 0, -1]));
      autoBonds(L * 0.7);
    }}
    // 7. Rhombohedral (Bi, Sb, As, Sm)
    else if (cSys === 'Rhombohedral') {{
      const hx = L * 0.45, hy = L * 0.45, hz = L * 0.55;
      makePrismBox(hx*2, hy*2, hz*2);
      // Rhombohedral corners + interior layers
      const pts = [
        [-hx, -hy, -hz], [hx, -hy, -hz], [hx, hy, -hz], [-hx, hy, -hz],
        [-hx, -hy,  hz], [hx, -hy,  hz], [hx, hy,  hz], [-hx, hy,  hz],
        [0, 0, 0], [0, 0, -hz/2], [0, 0, hz/2]
      ];
      pts.forEach((p, i) => addAtom(p[0], p[1], p[2], (i % 2 === 0) ? [0, 0, 1] : [0, 0, -1]));
      autoBonds(L * 0.7);
    }}
    // 8. Tetragonal / BCT / Orthorhombic / Monoclinic / Simple Cubic
    else {{
      makePrismBox(Lx, Ly, Lz);
      const hx = Lx / 2, hy = Ly / 2, hz = Lz / 2;
      const pts = [
        [-hx, -hy, -hz], [hx, -hy, -hz], [hx, hy, -hz], [-hx, hy, -hz],
        [-hx, -hy,  hz], [hx, -hy,  hz], [hx, hy,  hz], [-hx, hy,  hz]
      ];
      if (cSys === 'BCT') {{
        pts.push([0, 0, 0]);
      }}
      pts.forEach(p => addAtom(p[0], p[1], p[2], null));
      autoBonds(Math.max(Lx, Ly, Lz) * 0.85);
    }}

    return {{ atoms, bonds, boxLines, spinConfig }};
  }}

  // 3D VIEWER CLASS (Three.js WebGL with Canvas 2D projection fallback)
  class CrystalViewer {{
    constructor(containerId, isModal = false) {{
      this.container = document.getElementById(containerId);
      this.isModal = isModal;
      this.currentElem = null;
      this.showSpins = true;
      this.showBox = true;
      this.autoRotate = true;
      this.useThree = (typeof THREE !== 'undefined');

      this.init();
    }}

    init() {{
      if (this.useThree) {{
        try {{
          this.initThree();
        }} catch (err) {{
          console.warn("WebGL initialization failed, falling back to 2D Canvas:", err);
          this.useThree = false;
          this.initCanvasFallback();
        }}
      }} else {{
        this.initCanvasFallback();
      }}
    }}

    initThree() {{
      const width = this.container.clientWidth || 400;
      const height = this.container.clientHeight || 260;

      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
      this.camera.position.set(0, 2.2, 5.8);

      this.renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.shadowMap.enabled = false;
      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);

      if (typeof THREE.OrbitControls !== 'undefined') {{
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08;
        this.controls.autoRotate = this.autoRotate;
        this.controls.autoRotateSpeed = 1.8;
      }}

      // Lights
      const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.75);
      this.scene.add(ambientLight);

      const dirLight1 = new THREE.DirectionalLight(0xFFFFFF, 0.9);
      dirLight1.position.set(6, 10, 8);
      this.scene.add(dirLight1);

      const dirLight2 = new THREE.DirectionalLight(0x38BDF8, 0.35);
      dirLight2.position.set(-6, -4, -6);
      this.scene.add(dirLight2);

      // Groups
      this.rootGroup = new THREE.Group();
      this.atomsGroup = new THREE.Group();
      this.bondsGroup = new THREE.Group();
      this.boxGroup = new THREE.Group();
      this.spinsGroup = new THREE.Group();

      this.rootGroup.add(this.atomsGroup);
      this.rootGroup.add(this.bondsGroup);
      this.rootGroup.add(this.boxGroup);
      this.rootGroup.add(this.spinsGroup);
      this.scene.add(this.rootGroup);

      this.animate = this.animate.bind(this);
      this.isAnimating = false;
    }}

    startAnimation() {{
      if (this.useThree) {{
        if (!this.isAnimating) {{
          this.isAnimating = true;
          requestAnimationFrame(this.animate);
        }}
      }} else if (this.canvas && this.autoRotate) {{
        this.startCanvasAutoRotate();
      }}
    }}

    stopAnimation() {{
      this.isAnimating = false;
      this.stopCanvasAutoRotate();
    }}

    disposeGroup(grp) {{
      while (grp.children.length > 0) {{
        const obj = grp.children[0];
        grp.remove(obj);
        obj.traverse((child) => {{
          if (child.geometry) {{
            child.geometry.dispose();
          }}
          if (child.material) {{
            if (Array.isArray(child.material)) {{
              child.material.forEach(m => m.dispose());
            }} else {{
              child.material.dispose();
            }}
          }}
        }});
      }}
    }}

    animate() {{
      if (!this.isAnimating) return;
      requestAnimationFrame(this.animate);

      if (this.controls) {{
        this.controls.update();
      }}
      if (this.renderer && this.scene && this.camera) {{
        this.renderer.render(this.scene, this.camera);
      }}
    }}

    resize() {{
      if (!this.container) return;
      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      if (width > 0 && height > 0) {{
        if (this.useThree && this.renderer && this.camera) {{
          this.camera.aspect = width / height;
          this.camera.updateProjectionMatrix();
          this.renderer.setSize(width, height);
        }} else if (this.canvas && this.currentElem) {{
          this.renderCanvasFallback(this.currentElem);
        }}
      }}
    }}

    loadElement(elem) {{
      this.currentElem = elem;
      if (!this.useThree) {{
        this.renderCanvasFallback(elem);
        return;
      }}

      // Clear existing geometry with full VRAM GPU resource disposal
      this.disposeGroup(this.atomsGroup);
      this.disposeGroup(this.bondsGroup);
      this.disposeGroup(this.boxGroup);
      this.disposeGroup(this.spinsGroup);

      const geom = buildCrystalGeometry(elem);

      // 1. Build Atoms
      const sphereGeom = new THREE.SphereGeometry(0.24, 24, 20);
      geom.atoms.forEach(at => {{
        const mat = new THREE.MeshStandardMaterial({{
          color: at.color,
          metalness: 0.45,
          roughness: 0.3
        }});
        const mesh = new THREE.Mesh(sphereGeom, mat);
        mesh.position.set(at.x, at.y, at.z);
        this.atomsGroup.add(mesh);

        // 2. Build Magnetic Spin Vectors (Arrows)
        if (at.spinDir) {{
          const arrowGroup = this.createSpinArrowMesh(at.spinDir, at.spinColor);
          arrowGroup.position.set(at.x, at.y, at.z);
          this.spinsGroup.add(arrowGroup);
        }}
      }});

      // 3. Build Bonds
      const bondMat = new THREE.MeshStandardMaterial({{
        color: 0x64748B,
        metalness: 0.3,
        roughness: 0.5
      }});
      geom.bonds.forEach(([i, j]) => {{
        const p1 = new THREE.Vector3(geom.atoms[i].x, geom.atoms[i].y, geom.atoms[i].z);
        const p2 = new THREE.Vector3(geom.atoms[j].x, geom.atoms[j].y, geom.atoms[j].z);
        const bondMesh = this.createBondMesh(p1, p2, 0.05, bondMat);
        this.bondsGroup.add(bondMesh);
      }});

      // 4. Build Unit Cell Wireframe Box
      const lineMat = new THREE.LineBasicMaterial({{
        color: 0x94A3B8,
        transparent: true,
        opacity: 0.65,
        linewidth: 1.5
      }});
      const boxGeo = new THREE.BufferGeometry();
      const posArr = [];
      geom.boxLines.forEach(l => {{
        posArr.push(l[0], l[1], l[2], l[3], l[4], l[5]);
      }});
      boxGeo.setAttribute('position', new THREE.Float32BufferAttribute(posArr, 3));
      const boxMesh = new THREE.LineSegments(boxGeo, lineMat);
      this.boxGroup.add(boxMesh);

      // Visibility states
      this.spinsGroup.visible = this.showSpins;
      this.boxGroup.visible = this.showBox;

      // Reset camera
      this.camera.position.set(0, 2.0, 5.8);
      if (this.controls) {{
        this.controls.target.set(0, 0, 0);
        this.controls.update();
      }}

      this.resize();
    }}

    createSpinArrowMesh(dirArr, colorHex) {{
      const group = new THREE.Group();
      const dir = new THREE.Vector3(dirArr[0], dirArr[1], dirArr[2]).normalize();
      const totalLen = 0.85;
      const shaftLen = totalLen * 0.68;
      const shaftRadius = 0.045;
      const headLen = totalLen * 0.32;
      const headRadius = 0.12;

      // Shaft
      const shaftGeom = new THREE.CylinderGeometry(shaftRadius, shaftRadius, shaftLen, 12);
      const shaftMat = new THREE.MeshStandardMaterial({{
        color: colorHex,
        emissive: colorHex,
        emissiveIntensity: 0.4,
        roughness: 0.2,
        metalness: 0.5
      }});
      const shaft = new THREE.Mesh(shaftGeom, shaftMat);
      shaft.position.set(0, shaftLen / 2 + 0.24, 0); // Originates just above atom sphere

      // Cone Head
      const coneGeom = new THREE.ConeGeometry(headRadius, headLen, 16);
      const coneMat = new THREE.MeshStandardMaterial({{
        color: colorHex,
        emissive: colorHex,
        emissiveIntensity: 0.6,
        roughness: 0.15,
        metalness: 0.6
      }});
      const cone = new THREE.Mesh(coneGeom, coneMat);
      cone.position.set(0, shaftLen + headLen / 2 + 0.24, 0);

      group.add(shaft);
      group.add(cone);

      // Orient arrow towards direction
      group.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
      return group;
    }}

    createBondMesh(p1, p2, radius, material) {{
      const dir = new THREE.Vector3().subVectors(p2, p1);
      const len = dir.length();
      const geom = new THREE.CylinderGeometry(radius, radius, len, 8);
      const mesh = new THREE.Mesh(geom, material);
      mesh.position.copy(p1).addScaledVector(dir, 0.5);
      mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());
      return mesh;
    }}

    toggleSpins(btn) {{
      this.showSpins = !this.showSpins;
      if (this.spinsGroup) this.spinsGroup.visible = this.showSpins;
      if (this.canvas && this.currentElem) this.renderCanvasFallback(this.currentElem);
      if (btn) btn.textContent = this.showSpins ? '🧲 Spins: ON' : '🧲 Spins: OFF';
    }}

    toggleBox(btn) {{
      this.showBox = !this.showBox;
      if (this.boxGroup) this.boxGroup.visible = this.showBox;
      if (this.canvas && this.currentElem) this.renderCanvasFallback(this.currentElem);
      if (btn) btn.textContent = this.showBox ? '📦 Box: ON' : '📦 Box: OFF';
    }}

    toggleAutoRotate(btn) {{
      this.autoRotate = !this.autoRotate;
      if (this.controls) this.controls.autoRotate = this.autoRotate;
      if (this.canvas && !this.useThree) {{
        if (this.autoRotate) {{
          this.startCanvasAutoRotate();
        }} else {{
          this.stopCanvasAutoRotate();
        }}
      }}
      if (btn) btn.textContent = this.autoRotate ? '🔄 Rotate: ON' : '🔄 Rotate: OFF';
    }}

    startCanvasAutoRotate() {{
      if (this.canvasAnimId) cancelAnimationFrame(this.canvasAnimId);
      const loop = () => {{
        if (!this.autoRotate || this.useThree) return;
        const isVisible = this.container && this.container.offsetParent !== null && this.container.clientHeight > 0;
        if (isVisible && this.currentElem) {{
          this.rotY += 0.01;
          this.renderCanvasFallback(this.currentElem);
        }}
        this.canvasAnimId = requestAnimationFrame(loop);
      }};
      this.canvasAnimId = requestAnimationFrame(loop);
    }}

    stopCanvasAutoRotate() {{
      if (this.canvasAnimId) {{
        cancelAnimationFrame(this.canvasAnimId);
        this.canvasAnimId = null;
      }}
    }}

    resetCamera() {{
      if (this.camera) {{
        this.camera.position.set(0, 2.0, 5.8);
      }}
      if (this.controls) {{
        this.controls.target.set(0, 0, 0);
        this.controls.update();
      }}
      if (this.canvas) {{
        this.rotX = 0.3;
        this.rotY = 0.5;
        this.zoom = 55;
        if (this.currentElem) this.renderCanvasFallback(this.currentElem);
      }}
    }}

    // Fallback 2D Canvas Projection (if Three.js CDN blocked or offline)
    initCanvasFallback() {{
      this.canvas = document.createElement('canvas');
      this.container.innerHTML = '';
      this.container.appendChild(this.canvas);
      this.ctx = this.canvas.getContext('2d');
      this.rotX = 0.3;
      this.rotY = 0.5;
      this.zoom = 55;

      let isDragging = false;
      let lastX = 0, lastY = 0;
      this.canvas.addEventListener('mousedown', e => {{
        isDragging = true; lastX = e.clientX; lastY = e.clientY;
      }});
      window.addEventListener('mouseup', () => isDragging = false);
      window.addEventListener('mousemove', e => {{
        if (!isDragging) return;
        this.rotY += (e.clientX - lastX) * 0.01;
        this.rotX += (e.clientY - lastY) * 0.01;
        lastX = e.clientX; lastY = e.clientY;
        if (this.currentElem) this.renderCanvasFallback(this.currentElem);
      }});
      this.canvas.addEventListener('wheel', e => {{
        e.preventDefault();
        this.zoom = Math.max(20, Math.min(120, this.zoom - e.deltaY * 0.05));
        if (this.currentElem) this.renderCanvasFallback(this.currentElem);
      }});
    }}

    renderCanvasFallback(elem) {{
      if (!this.canvas) return;
      const w = this.container.clientWidth || 400;
      const h = this.container.clientHeight || 260;
      this.canvas.width = w; this.canvas.height = h;
      const ctx = this.ctx;
      ctx.clearRect(0, 0, w, h);

      const geom = buildCrystalGeometry(elem);
      const cx = w / 2, cy = h / 2;

      // Project 3D coordinate to 2D viewport
      const project = (x, y, z) => {{
        // Rotate around Y-axis
        const cosY = Math.cos(this.rotY), sinY = Math.sin(this.rotY);
        const x1 = x * cosY - z * sinY;
        const z1 = x * sinY + z * cosY;
        // Rotate around X-axis
        const cosX = Math.cos(this.rotX), sinX = Math.sin(this.rotX);
        const y2 = y * cosX - z1 * sinX;
        const z2 = y * sinX + z1 * cosX;
        return {{ px: cx + x1 * this.zoom, py: cy - y2 * this.zoom, depth: z2 }};
      }};

      // Draw Box lines
      if (this.showBox) {{
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
        ctx.lineWidth = 1.2;
        geom.boxLines.forEach(l => {{
          const p1 = project(l[0], l[1], l[2]);
          const p2 = project(l[3], l[4], l[5]);
          ctx.beginPath();
          ctx.moveTo(p1.px, p1.py);
          ctx.lineTo(p2.px, p2.py);
          ctx.stroke();
        }});
      }}

      // Draw Bonds
      ctx.strokeStyle = 'rgba(100, 116, 139, 0.45)';
      ctx.lineWidth = 2.5;
      geom.bonds.forEach(([i, j]) => {{
        const p1 = project(geom.atoms[i].x, geom.atoms[i].y, geom.atoms[i].z);
        const p2 = project(geom.atoms[j].x, geom.atoms[j].y, geom.atoms[j].z);
        ctx.beginPath();
        ctx.moveTo(p1.px, p1.py);
        ctx.lineTo(p2.px, p2.py);
        ctx.stroke();
      }});

      // Sort atoms by depth for proper z-ordering
      const sorted = geom.atoms.map((at, idx) => ({{ ...at, ...project(at.x, at.y, at.z) }}));
      sorted.sort((a, b) => a.depth - b.depth);

      // Draw atoms & 3D projected spin vectors
      sorted.forEach(at => {{
        // Atom sphere / circle
        const r = Math.max(8, this.zoom * 0.22);
        const grad = ctx.createRadialGradient(at.px - r*0.3, at.py - r*0.3, r*0.1, at.px, at.py, r);
        grad.addColorStop(0, '#FFFFFF');
        grad.addColorStop(0.5, '#' + at.color.toString(16).padStart(6, '0'));
        grad.addColorStop(1, '#0F172A');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(at.px, at.py, r, 0, Math.PI * 2);
        ctx.fill();

        // Spin Vector Arrow (Projected in true 3D perspective along rotated lattice orientation)
        if (this.showSpins && at.spinDir) {{
          const sx = at.spinDir[0];
          const sy = at.spinDir[1];
          const sz = at.spinDir[2];
          const tipLen = 0.72;
          const tip3D_x = at.x + sx * tipLen;
          const tip3D_y = at.y + sy * tipLen;
          const tip3D_z = at.z + sz * tipLen;
          const pTip = project(tip3D_x, tip3D_y, tip3D_z);

          const colorHex = '#' + at.spinColor.toString(16).padStart(6, '0');
          ctx.strokeStyle = colorHex;
          ctx.fillStyle = colorHex;
          ctx.lineWidth = 3;

          // Shaft
          ctx.beginPath();
          ctx.moveTo(at.px, at.py);
          ctx.lineTo(pTip.px, pTip.py);
          ctx.stroke();

          // Arrowhead oriented along projected vector
          const angle = Math.atan2(pTip.py - at.py, pTip.px - at.px);
          const headLen = Math.max(5, this.zoom * 0.12);
          ctx.beginPath();
          ctx.moveTo(pTip.px, pTip.py);
          ctx.lineTo(pTip.px - headLen * Math.cos(angle - Math.PI / 6), pTip.py - headLen * Math.sin(angle - Math.PI / 6));
          ctx.lineTo(pTip.px - headLen * Math.cos(angle + Math.PI / 6), pTip.py - headLen * Math.sin(angle + Math.PI / 6));
          ctx.closePath();
          ctx.fill();
        }}
      }});
    }}
  }}

  // =========================================================================
  // APPLICATION STARTUP & AUTHORITATIVE DATA LOADING
  // =========================================================================

  function loadData() {{
    const el = document.getElementById('embedded-elements-data');
    if (!el || !el.textContent) {{
      console.error('Embedded elements dataset #embedded-elements-data not found.');
      return;
    }}
    elementsData = JSON.parse(el.textContent);

    initDynamicFilterCounts();

    // Initialize 3D Viewers
    drawerCrystalViewer = new CrystalViewer('drawer-canvas-container', false);
    modalCrystalViewer = new CrystalViewer('modal-canvas-container', true);

    initTable();
    initViewerControls();
    renderStaticMath();
  }}

  // Dynamically calculate and display counts for filters and roles
  function initDynamicFilterCounts() {{
    const counts = {{
      all: elementsData.length,
      ferro: 0,
      afm: 0,
      lowt: 0,
      para: 0,
      dia: 0,
      critical: 0,
      radioactive: 0
    }};
    const roleCounts = {{}};

    elementsData.forEach(elem => {{
      const catClass = getCategoryClass(elem.magnetic_classification);
      if (catClass === 'type-ferro') counts.ferro++;
      else if (catClass === 'type-afm') counts.afm++;
      else if (catClass === 'type-lowt') counts.lowt++;
      else if (catClass === 'type-para') counts.para++;
      else counts.dia++;

      if (elem.usgs_critical_mineral) counts.critical++;
      if (elem.radioactive) counts.radioactive++;

      const role = (elem.magnet_role || 'No primary commercial magnetic alloy role documented');
      roleCounts[role] = (roleCounts[role] || 0) + 1;
    }});

    // Update filter buttons count tags
    document.querySelectorAll('.filter-btn').forEach(btn => {{
      const f = btn.dataset.filter;
      const countSpan = btn.querySelector('.count-tag');
      if (countSpan && counts[f] !== undefined) {{
        countSpan.textContent = counts[f];
      }}
    }});

    // Update role filter options dynamically with counts
    if (roleFilter) {{
      const currentVal = roleFilter.value;
      const canonicalRoles = [
        {{ key: 'Hard Magnetic Vector', label: 'Hard Magnetic Vector' }},
        {{ key: 'Soft Magnetic Core', label: 'Soft Magnetic Core' }},
        {{ key: 'Magnetocaloric Active Element', label: 'Magnetocaloric Active' }},
        {{ key: 'Magnetic Phase Stabilizer / Additive', label: 'Phase Stabilizer / Additive' }},
        {{ key: 'No primary commercial magnetic alloy role documented', label: 'No Commercial Magnetic Role' }}
      ];
      let opts = `<option value="all">Tech Role: All (${{elementsData.length}})</option>`;
      canonicalRoles.forEach(r => {{
        const cnt = roleCounts[r.key] || 0;
        opts += `<option value="${{r.key}}">${{r.label}} (${{cnt}})</option>`;
      }});
      roleFilter.innerHTML = opts;
      roleFilter.value = currentVal || 'all';
    }}
  }}

  // Map category to CSS class
  function getCategoryClass(classification) {{
    if (!classification) return 'type-dia';
    if (classification.startsWith('Ferromagnet')) return 'type-ferro';
    if (classification.startsWith('Antiferromagnet')) return 'type-afm';
    if (classification.startsWith('Low-temperature')) return 'type-lowt';
    if (classification.startsWith('Paramagnet')) return 'type-para';
    return 'type-dia';
  }}

  // Format transition temp with HTML subscripts (T_C -> T<sub>C</sub>)
  function formatTempHtml(tempStr) {{
    if (!tempStr) return '';
    return tempStr
      .replace(/T_C/g, 'T<sub>C</sub>')
      .replace(/T_N/g, 'T<sub>N</sub>')
      .replace(/TC/g, 'T<sub>C</sub>')
      .replace(/TN/g, 'T<sub>N</sub>');
  }}

  // Render Periodic Table Grid
  function initTable() {{
    gridContainer.innerHTML = '';
    const zMap = new Map();
    elementsData.forEach(e => zMap.set(e.atomic_number, e));

    for (let period = 1; period <= 7; period++) {{
      for (let col = 1; col <= 18; col++) {{
        if (period === 1) {{
          if (col === 1) renderCell(zMap.get(1));
          else if (col === 18) renderCell(zMap.get(2));
          else renderEmptyCell();
        }} else if (period === 2) {{
          if (col <= 2) renderCell(zMap.get(period === 2 && col === 1 ? 3 : 4));
          else if (col >= 13) renderCell(zMap.get(col - 8));
          else renderEmptyCell();
        }} else if (period === 3) {{
          if (col <= 2) renderCell(zMap.get(period === 3 && col === 1 ? 11 : 12));
          else if (col >= 13) renderCell(zMap.get(col));
          else renderEmptyCell();
        }} else if (period === 4) {{
          renderCell(zMap.get(18 + col));
        }} else if (period === 5) {{
          renderCell(zMap.get(36 + col));
        }} else if (period === 6) {{
          if (col <= 2) renderCell(zMap.get(54 + col));
          else if (col === 3) renderPlaceholder('57–71', 'La–Lu', 'lanthanides');
          else renderCell(zMap.get(71 + (col - 3)));
        }} else if (period === 7) {{
          if (col <= 2) renderCell(zMap.get(86 + col));
          else if (col === 3) renderPlaceholder('89–103', 'Ac–Lr', 'actinides');
          else renderCell(zMap.get(103 + (col - 3)));
        }}
      }}
    }}

    const sep = document.createElement('div');
    sep.className = 'grid-separator';
    gridContainer.appendChild(sep);

    // Lanthanides row
    const laLabel = document.createElement('div');
    laLabel.className = 'series-label-cell';
    laLabel.innerHTML = '★ Lanthanides (57–71)';
    gridContainer.appendChild(laLabel);
    for (let z = 57; z <= 71; z++) {{
      renderCell(zMap.get(z));
    }}

    // Actinides row
    const acLabel = document.createElement('div');
    acLabel.className = 'series-label-cell';
    acLabel.innerHTML = '★★ Actinides (89–103)';
    gridContainer.appendChild(acLabel);
    for (let z = 89; z <= 103; z++) {{
      renderCell(zMap.get(z));
    }}

    applyFilters();
  }}

  function renderEmptyCell() {{
    const cell = document.createElement('div');
    cell.style.visibility = 'hidden';
    gridContainer.appendChild(cell);
  }}

  function renderPlaceholder(range, symbols, series) {{
    const cell = document.createElement('div');
    cell.className = 'placeholder-cell';
    cell.setAttribute('role', 'button');
    cell.setAttribute('tabindex', '0');
    cell.setAttribute('aria-label', `${{series === 'lanthanides' ? 'Lanthanides' : 'Actinides'}} series ${{range}}`);
    cell.innerHTML = `<div>${{range}}</div><div>${{symbols}}</div>`;
    const openSeries = () => {{
      const targetZ = (series === 'lanthanides') ? 57 : 89;
      openDrawerByZ(targetZ);
    }};
    cell.addEventListener('click', openSeries);
    cell.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter' || e.key === ' ') {{
        e.preventDefault();
        openSeries();
      }}
    }});
    gridContainer.appendChild(cell);
  }}

  function renderCell(elem) {{
    if (!elem) return;
    const catClass = getCategoryClass(elem.magnetic_classification);
    const isRadio = elem.radioactive;
    const isCritical = elem.usgs_critical_mineral;
    const tempHtml = formatTempHtml(elem.transition_temperature_str);

    const cell = document.createElement('div');
    cell.className = `element-cell ${{catClass}} ${{isRadio ? 'radioactive' : ''}}`;
    cell.id = `elem-cell-${{elem.atomic_number}}`;
    cell.setAttribute('role', 'button');
    cell.setAttribute('tabindex', '0');
    cell.setAttribute('aria-label', `${{elem.name}} (${{elem.symbol}}), atomic number ${{elem.atomic_number}}, ${{elem.magnetic_classification}}`);
    cell.dataset.z = elem.atomic_number;
    cell.dataset.symbol = elem.symbol.toLowerCase();
    cell.dataset.name = elem.name.toLowerCase();
    cell.dataset.critical = isCritical;
    cell.dataset.radioactive = isRadio;
    cell.dataset.classification = catClass;
    cell.dataset.crystalsystem = (elem.crystallography && elem.crystallography.crystal_system) || '';
    cell.dataset.role = elem.magnet_role || '';

    cell.innerHTML = `
      <div class="cell-top">
        <span class="cell-num">${{elem.atomic_number}}</span>
        ${{isCritical ? '<span class="cell-star" title="USGS Critical Mineral (2022)">★</span>' : ''}}
      </div>
      <div class="cell-sym">${{elem.symbol}}</div>
      <div class="cell-weight">${{elem.atomic_mass}}</div>
      ${{tempHtml ? `<div class="cell-temp">${{tempHtml}}</div>` : '<div class="cell-temp" style="opacity:0;">-</div>'}}
    `;

    const openElem = () => openDrawerByZ(elem.atomic_number);
    cell.addEventListener('click', openElem);
    cell.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter' || e.key === ' ') {{
        e.preventDefault();
        openElem();
      }}
    }});
    gridContainer.appendChild(cell);
  }}

  // FILTERING LOGIC
  function applyFilters() {{
    let visibleCount = 0;
    const q = searchQuery.trim().toLowerCase();

    const cells = document.querySelectorAll('.element-cell');
    cells.forEach(cell => {{
      const z = cell.dataset.z;
      const sym = cell.dataset.symbol;
      const name = cell.dataset.name;
      const isCrit = cell.dataset.critical === 'true';
      const isRadio = cell.dataset.radioactive === 'true';
      const catClass = cell.dataset.classification;
      const cSys = cell.dataset.crystalsystem;
      const cRole = cell.dataset.role;

      let matchFilter = false;
      if (activeFilter === 'all') matchFilter = true;
      else if (activeFilter === 'critical') matchFilter = isCrit;
      else if (activeFilter === 'radioactive') matchFilter = isRadio;
      else if (activeFilter === 'ferro') matchFilter = (catClass === 'type-ferro');
      else if (activeFilter === 'afm') matchFilter = (catClass === 'type-afm');
      else if (activeFilter === 'lowt') matchFilter = (catClass === 'type-lowt');
      else if (activeFilter === 'diamagnet') matchFilter = (catClass === 'type-dia');
      else if (activeFilter === 'paramagnet') matchFilter = (catClass === 'type-para');

      let matchCrystal = false;
      if (activeCrystal === 'all') {{
        matchCrystal = true;
      }} else if (activeCrystal === 'Tetragonal') {{
        matchCrystal = (cSys === 'Tetragonal' || cSys === 'BCT');
      }} else {{
        matchCrystal = (cSys === activeCrystal);
      }}

      let matchRole = (activeRole === 'all') || (cRole === activeRole);

      let matchSearch = true;
      if (q) matchSearch = (sym.startsWith(q) || name.includes(q) || z === q);

      const isMatch = matchFilter && matchCrystal && matchRole && matchSearch;
      if (isMatch) {{
        cell.classList.remove('dimmed');
        visibleCount++;
      }} else {{
        cell.classList.add('dimmed');
      }}
    }});

    filterStatsText.textContent = `Showing ${{visibleCount}} of 118`;
  }}

  // Filter Buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.legend-item').forEach(l => l.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      applyFilters();
    }});
  }});

  // Legend Items Filter with Keyboard Accessibility
  document.querySelectorAll('.legend-item').forEach(item => {{
    const filterKey = item.dataset.filter;
    item.setAttribute('role', 'button');
    item.setAttribute('tabindex', '0');
    item.setAttribute('aria-label', 'Filter by ' + filterKey);
    const toggleLegend = () => {{
      document.querySelectorAll('.legend-item').forEach(l => l.classList.remove('active'));
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));

      if (activeFilter === filterKey) {{
        activeFilter = 'all';
        document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
      }} else {{
        item.classList.add('active');
        activeFilter = filterKey;
        const matchingBtn = document.querySelector(`.filter-btn[data-filter="${{filterKey}}"]`);
        if (matchingBtn) matchingBtn.classList.add('active');
      }}
      applyFilters();
    }};
    item.addEventListener('click', toggleLegend);
    item.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter' || e.key === ' ') {{
        e.preventDefault();
        toggleLegend();
      }}
    }});
  }});

  roleFilter.addEventListener('change', (e) => {{
    activeRole = e.target.value;
    applyFilters();
  }});

  crystalFilter.addEventListener('change', (e) => {{
    activeCrystal = e.target.value;
    applyFilters();
  }});

  searchInput.addEventListener('input', (e) => {{
    searchQuery = e.target.value;
    applyFilters();
  }});

  resetFiltersBtn.addEventListener('click', () => {{
    activeFilter = 'all';
    activeCrystal = 'all';
    activeRole = 'all';
    searchQuery = '';
    searchInput.value = '';
    crystalFilter.value = 'all';
    roleFilter.value = 'all';
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.legend-item').forEach(l => l.classList.remove('active'));
    document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
    applyFilters();
  }});

  sampleDyCell.setAttribute('role', 'button');
  sampleDyCell.setAttribute('tabindex', '0');
  sampleDyCell.setAttribute('aria-label', 'Inspect Dysprosium (sample cell)');
  const openSampleDy = () => openDrawerByZ(66);
  sampleDyCell.addEventListener('click', openSampleDy);
  sampleDyCell.addEventListener('keydown', (e) => {{
    if (e.key === 'Enter' || e.key === ' ') {{
      e.preventDefault();
      openSampleDy();
    }}
  }});

  // =========================================================================
  // DRAWER & 3D VIEWER LOGIC
  // =========================================================================

  const mainAppContainer = document.querySelector('.container');
  let lastFocusedElement = null;
  let modalLastFocused = null;

  function trapFocus(e, container) {{
    if (e.key !== 'Tab') return;
    const focusable = Array.from(container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )).filter(el => !el.hasAttribute('disabled') && el.offsetParent !== null);
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey) {{
      if (document.activeElement === first) {{
        last.focus();
        e.preventDefault();
      }}
    }} else {{
      if (document.activeElement === last) {{
        first.focus();
        e.preventDefault();
      }}
    }}
  }}

  drawer.addEventListener('keydown', (e) => {{
    if (drawer.classList.contains('open') && !modalOverlay.classList.contains('open')) {{
      trapFocus(e, drawer);
    }}
  }});

  modalOverlay.addEventListener('keydown', (e) => {{
    if (modalOverlay.classList.contains('open')) {{
      trapFocus(e, modalOverlay);
    }}
  }});

  function isCrystalTabActive() {{
    const pane = document.getElementById('tab-crystal');
    return pane && pane.classList.contains('active');
  }}

  function openDrawerByZ(z) {{
    const idx = elementsData.findIndex(e => e.atomic_number === z);
    if (idx !== -1) {{
      lastFocusedElement = document.activeElement;
      currentElementIndex = idx;
      populateDrawer(elementsData[idx]);
      drawer.classList.add('open');
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      if (mainAppContainer) mainAppContainer.setAttribute('inert', '');

      // Load into 3D viewer & ONLY start animation loop if crystal tab is currently active!
      if (drawerCrystalViewer) {{
        drawerCrystalViewer.loadElement(elementsData[idx]);
        if (isCrystalTabActive()) {{
          drawerCrystalViewer.startAnimation();
          setTimeout(() => {{
            drawerCrystalViewer.resize();
          }}, 320);
        }} else {{
          drawerCrystalViewer.stopAnimation();
        }}
      }}
      closeBtn.focus();
    }}
  }}

  function closeDrawer() {{
    drawer.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
    if (mainAppContainer) mainAppContainer.removeAttribute('inert');
    if (drawerCrystalViewer) drawerCrystalViewer.stopAnimation();
    if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {{
      lastFocusedElement.focus();
    }}
  }}

  closeBtn.addEventListener('click', closeDrawer);
  overlay.addEventListener('click', closeDrawer);

  window.addEventListener('keydown', (e) => {{
    if (e.key === 'Escape') {{
      if (modalOverlay.classList.contains('open')) {{
        closeModal();
      }} else if (drawer.classList.contains('open')) {{
        closeDrawer();
      }}
    }}
  }});

  prevBtn.addEventListener('click', () => {{
    currentElementIndex = (currentElementIndex - 1 + elementsData.length) % elementsData.length;
    const elem = elementsData[currentElementIndex];
    populateDrawer(elem);
    if (drawerCrystalViewer) drawerCrystalViewer.loadElement(elem);
  }});

  nextBtn.addEventListener('click', () => {{
    currentElementIndex = (currentElementIndex + 1) % elementsData.length;
    const elem = elementsData[currentElementIndex];
    populateDrawer(elem);
    if (drawerCrystalViewer) drawerCrystalViewer.loadElement(elem);
  }});

  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab).classList.add('active');

      // If switching to crystallography tab, start animation & resize 3D viewer!
      if (btn.dataset.tab === 'tab-crystal' && drawerCrystalViewer) {{
        drawerCrystalViewer.startAnimation();
        setTimeout(() => {{
          drawerCrystalViewer.resize();
        }}, 50);
      }} else if (drawerCrystalViewer) {{
        drawerCrystalViewer.stopAnimation();
      }}
    }});
  }});

  // Populate Drawer Fields
  function populateDrawer(elem) {{
    const catClass = getCategoryClass(elem.magnetic_classification);
    const spinConfig = getElementSpinConfig(elem);

    // Badge
    const badge = document.getElementById('drawer-badge');
    badge.className = `drawer-elem-badge ${{catClass}} ${{elem.radioactive ? 'radioactive' : ''}}`;
    document.getElementById('drawer-z').textContent = elem.atomic_number;
    document.getElementById('drawer-sym').textContent = elem.symbol;
    document.getElementById('drawer-name').textContent = elem.name;
    document.getElementById('drawer-mass').textContent = `Atomic Mass: ${{elem.atomic_mass}} u`;
    document.getElementById('drawer-period').textContent = elem.period;
    document.getElementById('drawer-group').textContent = elem.group;

    // Badges in Header
    const tagContainer = document.getElementById('drawer-tag-container');
    tagContainer.innerHTML = '';

    const magTag = document.createElement('span');
    magTag.className = 'badge-tag mag-state';
    magTag.textContent = elem.magnetic_classification;
    tagContainer.appendChild(magTag);

    if (elem.usgs_critical_mineral) {{
      const critTag = document.createElement('span');
      critTag.className = 'badge-tag critical';
      critTag.innerHTML = `★ Critical Mineral${{elem.usgs_commodity_name ? ': ' + elem.usgs_commodity_name : ''}}`;
      tagContainer.appendChild(critTag);
    }}

    if (elem.radioactive) {{
      const radTag = document.createElement('span');
      radTag.className = 'badge-tag radioactive';
      radTag.innerHTML = `☢ Radioactive`;
      tagContainer.appendChild(radTag);
    }}

    // TAB 1: Overview & Magnetic
    document.getElementById('drawer-mag-class').textContent = elem.magnetic_classification;
    document.getElementById('drawer-mag-order').textContent = elem.magnetic_ordering_type || 'None / Not ordered';
    
    const tempHtml = formatTempHtml(elem.transition_temperature_str);
    if (tempHtml) {{
      const tKelvin = elem.transition_temperature_k;
      const tCelsius = (tKelvin !== null) ? (tKelvin - 273.15).toFixed(2) + ' °C' : '';
      document.getElementById('drawer-mag-temp').innerHTML = `${{tempHtml}} (${{tCelsius}})`;
    }} else {{
      document.getElementById('drawer-mag-temp').textContent = 'No critical magnetic transition';
    }}

    let descText = 'Maintains magnetic ground state without critical ordering.';
    if (elem.magnetic_classification.startsWith('Ferromagnet')) {{
      descText = 'Exhibits spontaneous long-range ferromagnetic ordering with Curie temperature at or above room temperature.';
    }} else if (elem.magnetic_classification.startsWith('Antiferromagnet')) {{
      descText = 'Exhibits long-range antiferromagnetic sub-lattice ordering with Néel temperature at or above room temperature.';
    }} else if (elem.magnetic_classification.startsWith('Low-temperature')) {{
      descText = 'Exhibits spontaneous magnetic ordering (ferromagnetic, antiferromagnetic, or helical) only below room temperature (T < 290 K).';
    }} else if (elem.magnetic_classification.startsWith('Paramagnet')) {{
      descText = 'Atoms possess net unpaired magnetic dipole moments that align parallel to an external applied magnetic field.';
    }} else if (elem.magnetic_classification.startsWith('Diamagnet')) {{
      descText = 'All electron shells are paired, yielding zero net magnetic dipole moment; weakly repelled by magnetic fields.';
    }}
    document.getElementById('drawer-mag-desc').textContent = descText;

    // USGS
    document.getElementById('drawer-usgs-status').textContent = elem.usgs_critical_mineral 
      ? 'Listed in official 2022 USGS Critical Minerals inventory' 
      : 'Not currently designated as a USGS Critical Mineral';
    document.getElementById('drawer-usgs-commodity').textContent = elem.usgs_commodity_name || 'N/A';

    // Radioactive
    document.getElementById('drawer-radioactive-status').textContent = elem.radioactive 
      ? 'Radioactive: No stable primordial isotopes exist (Z ≥ 84, Tc, Pm)' 
      : 'Stable: Possesses at least one stable primordial isotope';
    document.getElementById('drawer-radioactive-desc').textContent = elem.radioactive 
      ? 'All known isotopes undergo radioactive alpha, beta, or spontaneous decay.' 
      : 'Standard terrestrial elemental state with stable nuclear configuration.';

    // Category / Period
    document.getElementById('drawer-category').textContent = elem.category;
    document.getElementById('drawer-period-group').textContent = `Period ${{elem.period}}, Group ${{elem.group}}`;

    // TAB 2: Quantum & Advanced Magnetism
    const role = elem.magnet_role || 'No primary commercial magnetic alloy role documented';
    const roleBadge = document.getElementById('drawer-quantum-role-badge');
    const roleDesc = document.getElementById('drawer-quantum-role-desc');
    const intrinsicStateEl = document.getElementById('drawer-intrinsic-state');
    
    roleBadge.textContent = role;
    if (intrinsicStateEl) {{
      intrinsicStateEl.textContent = elem.magnetic_classification || 'Non-magnetic';
    }}

    if (role === 'Hard Magnetic Vector') {{
      roleBadge.className = 'role-badge role-hard';
    }} else if (role === 'Soft Magnetic Core') {{
      roleBadge.className = 'role-badge role-soft';
    }} else if (role === 'Magnetocaloric Active Element') {{
      roleBadge.className = 'role-badge role-mce';
    }} else if (role === 'Magnetic Phase Stabilizer / Additive') {{
      roleBadge.className = 'role-badge role-soft';
    }} else {{
      roleBadge.className = 'role-badge role-inert';
    }}

    if (elem.alloy_function_rationale) {{
      roleDesc.textContent = elem.alloy_function_rationale;
    }} else if (elem.functional_alloy_contributions && elem.functional_alloy_contributions.length > 0 && elem.functional_alloy_contributions[0] !== 'No primary commercial magnetic alloy role documented') {{
      roleDesc.textContent = elem.functional_alloy_contributions.join(' • ');
    }} else if (role === 'Hard Magnetic Vector') {{
      roleDesc.textContent = 'High uniaxial magnetocrystalline anisotropy (K₁) or large orbital angular momentum; essential for permanent magnets (Nd-Fe-B, Sm-Co), high-density magnetic recording media, and coercive pinning vectors.';
    }} else if (role === 'Soft Magnetic Core') {{
      roleDesc.textContent = 'High magnetic permeability, low coercivity, and minimal hysteresis loss; the premier active constituent in transformer cores, electric motor stators, inductors, and electromagnetic shielding.';
    }} else if (role === 'Magnetocaloric Active Element') {{
      roleDesc.textContent = 'Undergoes giant isothermal magnetic entropy change (ΔS_mag) and adiabatic temperature change (ΔT_ad) under applied fields; primary working material for room-temperature or cryogenic magnetic refrigeration.';
    }} else {{
      roleDesc.textContent = 'No primary commercial magnetic alloy role documented for pure element matrix; serves as standard diamagnetic, paramagnetic, or structural constituent without intrinsic ferromagnet/superconducting functionality.';
    }}

    // Term symbol
    const termEl = document.getElementById('drawer-q-term-symbol');
    if (typeof katex !== 'undefined' && elem.term_symbol) {{
      try {{
        termEl.innerHTML = katex.renderToString(elem.term_symbol, {{ throwOnError: false }});
      }} catch (e) {{
        termEl.textContent = elem.term_symbol_clean || elem.term_symbol;
      }}
    }} else {{
      termEl.textContent = elem.term_symbol_clean || elem.term_symbol || 'N/A';
    }}

    // Landé g-factor
    const gVal = elem.lande_g_factor;
    document.getElementById('drawer-q-lande-g').textContent = (gVal !== null && gVal !== undefined) ? gVal.toFixed(3) : 'N/A';

    // Moments
    const muUnit = (typeof katex !== 'undefined') ? katex.renderToString('\\\\mu_B', {{ throwOnError: false }}) : 'μ<sub>B</sub>';

    // Neutral Gas Atom Moment (Hund's rules)
    const neutralMu = (elem.neutral_atom_moment_mu_B !== undefined && elem.neutral_atom_moment_mu_B !== null) 
      ? elem.neutral_atom_moment_mu_B 
      : (elem.free_atom_moment_mu_B !== undefined && elem.free_atom_moment_mu_B !== null
          ? elem.free_atom_moment_mu_B
          : elem.atomic_moment_mu_B);
    const freeEl = document.getElementById('drawer-q-free-atom-moment');
    if (freeEl) {{
      if (neutralMu !== null && neutralMu !== undefined) {{
        freeEl.innerHTML = `${{neutralMu.toFixed(2)}} ${{muUnit}}`;
      }} else {{
        freeEl.textContent = 'N/A';
      }}
    }}

    // Bulk ordered moment
    const bulkMu = elem.bulk_ordered_moment_mu_B;
    const bulkEl = document.getElementById('drawer-q-bulk-ordered-moment');
    if (bulkEl) {{
      if (bulkMu !== null && bulkMu !== undefined) {{
        bulkEl.innerHTML = `${{bulkMu.toFixed(2)}} ${{muUnit}}`;
      }} else {{
        bulkEl.textContent = 'None (No spontaneous ordering)';
      }}
    }}

    // Free Ion State (Condensed Matter / Salts)
    const freeIonRow = document.getElementById('drawer-q-free-ion-row');
    const freeIonEl = document.getElementById('drawer-q-free-ion-state');
    if (freeIonRow && freeIonEl) {{
      if (elem.free_ion_state) {{
        freeIonRow.style.display = 'flex';
        const ionSpecies = elem.free_ion_state.species || '';
        const ionTerm = elem.free_ion_state.term_symbol || '';
        const ionMu = elem.free_ion_state.effective_moment_mu_B !== undefined ? `${{elem.free_ion_state.effective_moment_mu_B}} μ_B` : '';
        const ionNotes = elem.free_ion_state.notes || '';
        freeIonEl.innerHTML = `<span style="color: #38BDF8; font-weight: 600;">${{ionSpecies}}</span> &bull; Term: ${{ionTerm}} &bull; ${{ionMu}}<br><span style="color: #94A3B8; font-size: 11px;">${{ionNotes}}</span>`;
      }} else {{
        freeIonRow.style.display = 'none';
      }}
    }}

    // Molar susceptibility
    const chiVal = elem.molar_susceptibility_298K;
    document.getElementById('drawer-q-molar-chi').innerHTML = formatChi(chiVal, elem);

    // Curie-Weiss temperature
    const thetaVal = elem.curie_weiss_temp_K;
    if (thetaVal !== null && thetaVal !== undefined) {{
      const c = (thetaVal - 273.15).toFixed(1);
      const sign = thetaVal > 273.15 ? '+' : '';
      document.getElementById('drawer-q-curie-weiss').innerHTML = `${{thetaVal.toFixed(1)}} K (${{sign}}${{c}} °C)`;
    }} else {{
      document.getElementById('drawer-q-curie-weiss').textContent = 'None / Non-Curie-Weiss';
    }}

    // Saturation magnetization
    const msVal = elem.saturation_magnetization_T;
    const msCond = elem.saturation_magnetization_condition;
    if (msVal !== null && msVal !== undefined) {{
      document.getElementById('drawer-q-saturation-mag').innerHTML = `${{msVal.toFixed(2)}} T <span style="font-size:11px; color:#94A3B8; margin-left:4px;">(${{msCond || 'bulk solid'}})</span>`;
    }} else {{
      document.getElementById('drawer-q-saturation-mag').textContent = 'None (Not spontaneously magnetized)';
    }}

    // Magnetocrystalline anisotropy
    const k1Val = elem.magnetocrystalline_anisotropy_J_m3;
    if (k1Val !== null && k1Val !== undefined) {{
      const exp = k1Val.toExponential(2);
      const parts = exp.split('e');
      const coeff = parts[0];
      const p = parseInt(parts[1], 10);
      const sign = k1Val > 0 ? '+' : '';
      document.getElementById('drawer-q-anisotropy').innerHTML = `${{sign}}${{coeff}} &times; 10<sup>${{p}}</sup> J/m³`;
    }} else {{
      document.getElementById('drawer-q-anisotropy').textContent = 'None / Negligible';
    }}

    // Spin polarization
    const pVal = elem.spin_polarization_percent;
    if (pVal !== null && pVal > 0) {{
      document.getElementById('drawer-q-spin-polarization').textContent = `${{pVal.toFixed(1)}} %`;
    }} else {{
      document.getElementById('drawer-q-spin-polarization').textContent = '0.0 % (Unpolarized / non-magnetic)';
    }}

    // Exchange interaction
    document.getElementById('drawer-q-exchange-interaction').textContent = elem.exchange_interaction || 'N/A';

    // 3D VIEWER STATUS & LEGEND IN TAB 3
    const spinBadge = document.getElementById('drawer-spin-badge');
    spinBadge.className = `spin-pill ${{spinConfig.badgeClass}}`;
    spinBadge.textContent = spinConfig.label;

    const legUp = document.getElementById('drawer-legend-up');
    const legDown = document.getElementById('drawer-legend-down');
    const legNone = document.getElementById('drawer-legend-none');

    if (spinConfig.type === 'ferro') {{
      legUp.style.display = 'inline-flex';
      legDown.style.display = 'none';
      legNone.style.display = 'none';
    }} else if (spinConfig.type === 'afm') {{
      legUp.style.display = 'inline-flex';
      legDown.style.display = 'inline-flex';
      legNone.style.display = 'none';
    }} else {{
      legUp.style.display = 'none';
      legDown.style.display = 'none';
      legNone.style.display = 'inline-flex';
    }}

    // TAB 2: Crystallography
    const cryst = elem.crystallography || {{}};
    const lp = cryst.lattice_parameters || {{}};
    document.getElementById('drawer-c-sys').textContent = cryst.crystal_system || 'Unspecified';
    document.getElementById('drawer-sg-sym').textContent = cryst.space_group_symbol || 'N/A';
    document.getElementById('drawer-sg-num').textContent = cryst.space_group_number || 'N/A';
    document.getElementById('drawer-lattice-abc').textContent = 
      `a=${{lp.a || '-'}} Å, b=${{lp.b || '-'}} Å, c=${{lp.c || '-'}} Å`;
    document.getElementById('drawer-lattice-angles').textContent = 
      `α=${{lp.alpha || '-'}}°, β=${{lp.beta || '-'}}°, γ=${{lp.gamma || '-'}}°`;

    // Materials Project
    const mp = elem.materials_project || {{}};
    document.getElementById('drawer-mp-id').textContent = mp.material_id || 'N/A';
    document.getElementById('drawer-mp-rho').textContent = mp.computed_density_g_cm3 ? `${{mp.computed_density_g_cm3}} g/cm³` : 'N/A';
    document.getElementById('drawer-mp-eg').textContent = (mp.band_gap_ev !== null && mp.band_gap_ev !== undefined) ? `${{mp.band_gap_ev}} eV` : 'N/A';
    
    const mpLink = document.getElementById('drawer-mp-link');
    const mpBanner = document.getElementById('drawer-mp-banner');
    if (mp.url) {{
      mpLink.href = mp.url;
      mpLink.style.display = 'inline-flex';
      mpBanner.style.display = 'flex';
      document.getElementById('drawer-mp-caption').textContent = `${{elem.name}} Ground State (${{mp.material_id}})`;
    }} else {{
      mpLink.style.display = 'none';
      mpBanner.style.display = 'none';
    }}

    // TAB 3: Electronic & Chemical
    const elec = elem.electronic_configuration || {{}};
    document.getElementById('drawer-elec-abbrev').innerHTML = elec.abbreviated ? formatConfigSup(elec.abbreviated) : 'N/A';
    document.getElementById('drawer-elec-full').innerHTML = elec.full ? formatConfigSup(elec.full) : 'N/A';
    document.getElementById('drawer-valence-count').textContent = elec.valence_electrons !== undefined ? elec.valence_electrons : 'N/A';

    const chem = elem.chemical_bonding || {{}};
    document.getElementById('drawer-electronegativity').textContent = chem.electronegativity_pauling ? `${{chem.electronegativity_pauling}} (Pauling scale)` : 'N/A';
    document.getElementById('drawer-bonding-pref').textContent = chem.bonding_preference || 'N/A';
    document.getElementById('drawer-atomic-radius').textContent = chem.atomic_radius_pm ? `${{chem.atomic_radius_pm}} pm` : 'N/A';
    document.getElementById('drawer-covalent-radius').textContent = chem.covalent_radius_pm ? `${{chem.covalent_radius_pm}} pm` : 'N/A';

    const oxContainer = document.getElementById('drawer-ox-states');
    oxContainer.innerHTML = '';
    if (chem.common_oxidation_states && chem.common_oxidation_states.length > 0) {{
      chem.common_oxidation_states.forEach(st => {{
        const p = document.createElement('span');
        p.className = 'pill';
        p.textContent = (st > 0) ? `+${{st}}` : `${{st}}`;
        oxContainer.appendChild(p);
      }});
    }} else {{
      oxContainer.innerHTML = '<span class="pill">0</span>';
    }}

    // TAB 4: Physical
    const phys = elem.physical_properties || {{}};
    document.getElementById('drawer-std-state').textContent = phys.standard_state || 'Solid';
    document.getElementById('drawer-density').textContent = phys.density_g_cm3 ? `${{phys.density_g_cm3}} g/cm³` : 'N/A';
    document.getElementById('drawer-melting-pt').textContent = phys.melting_point_k ? `${{phys.melting_point_k}} K (${{phys.melting_point_c}} °C)` : 'N/A';
    document.getElementById('drawer-boiling-pt').textContent = phys.boiling_point_k ? `${{phys.boiling_point_k}} K (${{phys.boiling_point_c}} °C)` : 'N/A';

    // Prev / Next button labels
    const prevElem = elementsData[(currentElementIndex - 1 + elementsData.length) % elementsData.length];
    const nextElem = elementsData[(currentElementIndex + 1) % elementsData.length];
    prevBtn.textContent = `← ${{prevElem.symbol}} (${{prevElem.name}})`;
    nextBtn.textContent = `${{nextElem.symbol}} (${{nextElem.name}}) →`;
  }}

  // Format electron config superscripts
  function formatConfigSup(str) {{
    return str.replace(/([spdfg])([0-9]+)/g, '$1<sup>$2</sup>');
  }}

  // Format scientific notation for magnetic susceptibility
  function formatChi(val, elem) {{
    if (val === null || val === undefined) {{
      if (elem && (elem.magnetic_classification.startsWith('Ferromagnet') || (elem.transition_temperature_str && elem.transition_temperature_str.startsWith('T_C')))) {{
        return '<span style="font-size:11px;color:#92400E;" title="Non-linear susceptibility due to domain wall hysteresis below Curie temperature">Undefined (Ferromagnet below T<sub>C</sub>: domain wall hysteresis)</span>';
      }}
      return 'N/A';
    }}
    let note = '';
    if (elem) {{
      if (elem.symbol === 'Gd') {{
        note = ' <span style="font-size:11px;color:#94A3B8;">(paramagnetic at 298 K; T<sub>C</sub> = 292 K)</span>';
      }} else if (['H', 'He', 'N', 'O', 'F', 'Ne', 'Cl', 'Ar', 'Kr', 'Xe', 'Rn'].includes(elem.symbol)) {{
        note = ' <span style="font-size:11px;color:#94A3B8;">(gas phase at 298 K)</span>';
      }} else if (['Br', 'Hg'].includes(elem.symbol)) {{
        note = ' <span style="font-size:11px;color:#94A3B8;">(liquid phase at 298 K)</span>';
      }}
    }}
    if (Math.abs(val) >= 100 || Math.abs(val) < 0.001) {{
      const exp = val.toExponential(2);
      const parts = exp.split('e');
      const coeff = parts[0];
      const p = parseInt(parts[1], 10);
      const sign = val > 0 ? '+' : '';
      return `${{sign}}${{coeff}} &times; 10<sup>${{p}}</sup> cm³/mol${{note}}`;
    }}
    const sign = val > 0 ? '+' : '';
    return `${{sign}}${{val.toFixed(4)}} cm³/mol${{note}}`;
  }}

  // Render static KaTeX math elements with offline HTML fallback
  function renderStaticMath() {{
    const mathFallback = {{
      '^{{2S+1}}L_J': '<sup>2<i>S</i>+1</sup><i>L</i><sub><i>J</i></sub>',
      'g': '<i>g</i>',
      'g_J': '<i>g</i><sub><i>J</i></sub>',
      '\\\\mu': '&mu;',
      '\\\\mu_B': '&mu;<sub>B</sub>',
      '\\\\chi_m': '&chi;<sub>m</sub>',
      '\\\\theta_{{\\\\mathrm{{CW}}}}': '&theta;<sub>CW</sub>',
      'M_s': '<i>M</i><sub>s</sub>',
      'K_1': '<i>K</i><sub>1</sub>',
      'E_{{\\\\mathrm{{F}}}}': '<i>E</i><sub>F</sub>',
      'P': '<i>P</i>'
    }};

    document.querySelectorAll('.math-inline').forEach(el => {{
      const latex = el.dataset.latex;
      if (!latex) return;
      if (typeof katex !== 'undefined') {{
        try {{
          el.innerHTML = katex.renderToString(latex, {{ throwOnError: false }});
          return;
        }} catch (e) {{
          // Fall through to HTML fallback
        }}
      }}
      el.innerHTML = mathFallback[latex] || latex;
    }});
  }}

  // =========================================================================
  // 3D VIEWER INTERACTION CONTROLS
  // =========================================================================

  function initViewerControls() {{
    // Drawer Viewer Controls
    const btnSpins = document.getElementById('drawer-btn-spins');
    const btnBox = document.getElementById('drawer-btn-box');
    const btnRotate = document.getElementById('drawer-btn-rotate');
    const btnReset = document.getElementById('drawer-btn-reset');

    btnSpins.addEventListener('click', () => drawerCrystalViewer.toggleSpins(btnSpins));
    btnBox.addEventListener('click', () => drawerCrystalViewer.toggleBox(btnBox));
    btnRotate.addEventListener('click', () => drawerCrystalViewer.toggleAutoRotate(btnRotate));
    btnReset.addEventListener('click', () => drawerCrystalViewer.resetCamera());

    // Modal Viewer Controls
    const mBtnSpins = document.getElementById('modal-btn-spins');
    const mBtnBox = document.getElementById('modal-btn-box');
    const mBtnRotate = document.getElementById('modal-btn-rotate');
    const mBtnReset = document.getElementById('modal-btn-reset');

    mBtnSpins.addEventListener('click', () => modalCrystalViewer.toggleSpins(mBtnSpins));
    mBtnBox.addEventListener('click', () => modalCrystalViewer.toggleBox(mBtnBox));
    mBtnRotate.addEventListener('click', () => modalCrystalViewer.toggleAutoRotate(mBtnRotate));
    mBtnReset.addEventListener('click', () => modalCrystalViewer.resetCamera());

    // Expand to Fullscreen Modal
    drawerExpandBtn.addEventListener('click', openModal);
    modalCloseBtn.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {{
      if (e.target === modalOverlay) closeModal();
    }});
  }}

  function openModal() {{
    const elem = elementsData[currentElementIndex];
    if (!elem) return;
    modalLastFocused = document.activeElement;

    const cryst = elem.crystallography || {{}};
    const lp = cryst.lattice_parameters || {{}};
    const spinConfig = getElementSpinConfig(elem);

    document.getElementById('modal-elem-title').innerHTML = 
      `${{elem.name}} (${{elem.symbol}}) &bull; ${{cryst.crystal_system || 'Crystal'}} Lattice Structure &amp; Magnetic Spins`;
    document.getElementById('modal-elem-subtitle').innerHTML = 
      `Space Group: ${{cryst.space_group_symbol || 'N/A'}} (#${{cryst.space_group_number || '-'}}) &bull; ${{elem.magnetic_classification}} ${{elem.transition_temperature_str ? '(' + formatTempHtml(elem.transition_temperature_str) + ')' : ''}}`;
    
    document.getElementById('modal-spin-description').innerHTML = 
      `<strong>Magnetic Configuration:</strong> ${{spinConfig.desc}}`;
    
    document.getElementById('modal-lattice-stats').innerHTML = 
      `a = ${{lp.a || '-'}} Å, b = ${{lp.b || '-'}} Å, c = ${{lp.c || '-'}} Å &bull; α = ${{lp.alpha || '-'}}°, β = ${{lp.beta || '-'}}°, γ = ${{lp.gamma || '-'}}°`;

    modalOverlay.classList.add('open');
    if (drawer) drawer.setAttribute('inert', '');
    if (drawerCrystalViewer) drawerCrystalViewer.stopAnimation();
    if (modalCrystalViewer) {{
      modalCrystalViewer.startAnimation();
      modalCrystalViewer.loadElement(elem);
      setTimeout(() => {{
        modalCrystalViewer.resize();
      }}, 80);
    }}
    modalCloseBtn.focus();
  }}

  function closeModal() {{
    modalOverlay.classList.remove('open');
    if (drawer) drawer.removeAttribute('inert');
    if (modalCrystalViewer) modalCrystalViewer.stopAnimation();
    if (drawerCrystalViewer && isCrystalTabActive()) {{
      drawerCrystalViewer.startAnimation();
    }}
    if (modalLastFocused && typeof modalLastFocused.focus === 'function') {{
      modalLastFocused.focus();
    }}
  }}

  // Window resize handler to keep 3D WebGL canvases in sync with layout
  window.addEventListener('resize', () => {{
    if (drawer.classList.contains('open') && drawerCrystalViewer) {{
      drawerCrystalViewer.resize();
    }}
    if (modalOverlay.classList.contains('open') && modalCrystalViewer) {{
      modalCrystalViewer.resize();
    }}
  }});

  // Startup
  loadData();
}})();
</script>

</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Generated interactive table at: {output_html_path}")
    print(f"✓ File size: {len(html_content.encode('utf-8')) / 1024:.1f} KB")

    # Automatically keep index.html in sync for GitHub Pages root entrypoint
    index_html_path = output_html_path.parent / "index.html"
    if output_html_path.name != "index.html":
        if index_html_path.is_symlink():
            index_html_path.unlink()
        with open(index_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✓ Synchronized GitHub Pages entry point at: {index_html_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build interactive Magnetic Periodic Table web application.")
    parser.add_argument("-i", "--input", default=None, help="Input enriched JSON file (default: magnetic_elements_enriched.json)")
    parser.add_argument("-o", "--output", default=None, help="Output HTML file (default: interactive_table.html)")
    args = parser.parse_args()
    generate_html(enriched_json_path=args.input, output_html_path=args.output)
