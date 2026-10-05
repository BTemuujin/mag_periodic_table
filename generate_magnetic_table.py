#!/usr/bin/env python3
"""
generate_magnetic_table.py

Loads magnetic_elements_db.json and renders a high-resolution periodic table image
(magnetic_periodic_table.png) highlighting magnetic properties, USGS Critical Minerals,
and radioactivity.

Features a centralized CONTROL PARAMETERS (CONFIG) section at the top of the file
allowing easy customization of:
  - Font families, styles, and font sizes for all elements and annotations
  - Color palettes (Diamagnet, Paramagnet, Ferromagnet, Antiferromagnet, Low-Temp, etc.)
  - Element cell geometry and dimensions
  - Box dimensions and positions (Sample Cell and Legend)
  - Canvas dimensions and export DPI
"""

import json
import os
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects
from matplotlib.patches import FancyBboxPatch

# =============================================================================
# GENERAL CONTROL PARAMETERS (CONFIGURATION & STYLING)
# Modify this dictionary to customize fonts, font-sizes, colors, layout, and markers
# =============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(SCRIPT_DIR, "magnetic_elements_enriched.json")
if not os.path.exists(DEFAULT_DB):
    DEFAULT_DB = os.path.join(SCRIPT_DIR, "magnetic_elements_db.json")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "magnetic_periodic_table.png")

CONFIG = {
    # -------------------------------------------------------------------------
    # 1. Canvas & Output Settings
    # -------------------------------------------------------------------------
    "canvas": {
        "fig_width_inches": 28.0,
        "fig_height_inches": 18.0,
        "dpi": 300,
        "bg_color": "#F8FAFC",      # Canvas background color
        "xlim": (-0.2, 19.8),
        "ylim": (-0.6, 14.7),
        "db_path": DEFAULT_DB,
        "output_path": DEFAULT_OUTPUT,
    },

    # -------------------------------------------------------------------------
    # 2. Typography & Fonts
    # -------------------------------------------------------------------------
    "fonts": {
        "family": "sans-serif",
    },

    # -------------------------------------------------------------------------
    # 3. Font Sizes (Enlarged for high-legibility publication quality)
    # -------------------------------------------------------------------------
    "font_sizes": {
        # Periodic Table Element Cells
        "cell_symbol": 20,               # Chemical symbol (Fe, Co, Ni...)
        "cell_symbol_small": 18,         # For 3-letter symbols (if any)
        "cell_number": 16,                # Atomic number (Z) in top-left
        "cell_weight": 14,                # Standard atomic weight
        "cell_temp": 14,                # Transition temperature (LaTeX $T_{\mathrm{C}}$, $T_{\mathrm{N}}$)
        "cell_star": 16,                 # Red star icon for critical minerals

        # Grid Axis & Series Labels
        "group_numbers": 16,             # Column numbers (1–18)
        "period_numbers": 16,            # Row numbers (1–7)
        "series_labels": 14,             # "* Lanthanides", "** Actinides"
        "placeholder_numbers": 14,       # "57–71", "89–103" in main table
        "placeholder_symbols": 12,        # "La–Lu", "Ac–Lr" in main table

        # Header Titles
        "main_title": 44.0,                # Banner title "MAGNETIC PERIODIC TABLE"
        "subtitle": 20,                  # Descriptive subtitle

        # Box 1: Sample Cell & How to Read
        "box_header": 16,                # Box 1 & Box 2 title banner
        "sample_cell_symbol": 30.0,        # Sample cell symbol (Dy)
        "sample_cell_number": 16.0,        # Sample cell atomic number (66)
        "sample_cell_weight": 16.0,        # Sample cell atomic weight (162.50)
        "sample_cell_temp": 14.0,          # Sample cell transition temp (T_C = 85 K)
        "sample_cell_star": 16.0,          # Sample cell critical mineral star
        "callout_text": 14,              # Callout annotation labels
        "box1_note": 14,                  # Radioactive hatching explanation note

        # Box 2: Legend & Classification
        "legend_item_title": 16.0,         # Legend classification name
        "legend_item_desc": 14,           # Legend classification description
        "legend_indicator_text": 14,      # Star and hatch indicator explanations

        # Footnote Attributions
        "footnote": 14.0,                  # Footer scientific citations
    },

    # -------------------------------------------------------------------------
    # 4. Color Palette
    # -------------------------------------------------------------------------
    "colors": {
        # Magnetic Classification Face Colors
        "diamagnet": "#FFFFFF",            # White
        "paramagnet": "#FEF08A",           # Yellow (vibrant, accessible)
        "ferromagnet_rt": "#2563EB",       # Blue (Curie T_C >= 290 K)
        "antiferromagnet_rt": "#16A34A",   # Green (Neel T_N >= 290 K)
        "low_temp_ordering": "#86EFAC",    # Light Green (T_N/T_C < 290 K)

        # Cell Borders
        "border_diamagnet": "#94A3B8",
        "border_paramagnet": "#CA8A04",
        "border_ferromagnet": "#1D4ED8",
        "border_antiferromagnet": "#14532D",
        "border_low_temp": "#15803D",

        # Text Colors
        "text_dark": "#0F172A",            # Primary dark text on light backgrounds
        "text_light": "#FFFFFF",           # Light text on dark backgrounds (Fe, Co, Ni...)
        "text_muted": "#475569",           # Atomic weights and subtitles
        "text_muted_light": "#CBD5E1",     # Atomic weights on dark backgrounds
        "temp_dark_bg": "#FEF08A",         # Transition temp on dark blue/green cells
        "temp_light_bg": "#B91C1C",        # Transition temp on light cells (red highlight)
        "header_color": "#0F172A",         # Main title font color
        "axis_number_color": "#64748B",    # Group & period number colors

        # Special Indicators
        "critical_star": "#DC2626",        # USGS Critical Mineral star color
        "critical_star_halo": "#FFFFFF",   # High-contrast halo outline for star
        "radioactive_hatch": "#475569",    # Hatch line color for radioactive elements
        "callout_arrow": "#0284C7",        # Callout arrow color in Box 1
        "box_border": "#CBD5E1",           # Border for Box 1 and Box 2
        "box_bg": "#FFFFFF",               # Background for Box 1 and Box 2
    },

    # -------------------------------------------------------------------------
    # 5. Geometry & Dimensions
    # -------------------------------------------------------------------------
    "geometry": {
        "cell_width": 0.90,
        "cell_height": 0.94,
        "cell_border_width": 1.4,
        "hatch_pattern": "///",
        "hatch_alpha": 0.45,

        # Vertical Row Coordinates (Y)
        "row_y": {
            1: 11.20,
            2: 10.12,
            3: 9.04,
            4: 7.96,
            5: 6.88,
            6: 5.80,
            7: 4.72,
            8: 3.25,   # Lanthanides (pulled out)
            9: 2.15    # Actinides (pulled out)
        },

        # Box 1 & Box 2 Positioning
        "boxes_bottom_y": 9.5,
        "boxes_height": 3.50,
        "box1_x": 3.25,
        "box1_width": 4.5,
        "box2_x": 8,
        "box2_width": 4.5,
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_style_for_classification(classification):
    """Return (facecolor, edgecolor, text_color, is_dark_bg) based on CONFIG."""
    c = CONFIG["colors"]
    if classification in ("Ferromagnet (T_C >= 290 K)", "Ferromagnet (Tc >= 290 K)"):
        return c["ferromagnet_rt"], c["border_ferromagnet"], c["text_light"], True
    elif classification in ("Antiferromagnet (T_N >= 290 K)", "Antiferromagnet (Tn >= 290 K)"):
        return c["antiferromagnet_rt"], c["border_antiferromagnet"], c["text_light"], True
    elif classification == "Low-temperature magnetic ordering":
        return c["low_temp_ordering"], c["border_low_temp"], c["text_dark"], False
    elif classification == "Paramagnet":
        return c["paramagnet"], c["border_paramagnet"], c["text_dark"], False
    else:  # Diamagnet
        return c["diamagnet"], c["border_diamagnet"], c["text_dark"], False

def format_latex_temp(t_str):
    """Format transition temperature string to LaTeX math mode with C/N subscripts ($T_{\\mathrm{C}}$, $T_{\\mathrm{N}}$)."""
    if not t_str:
        return ""
    m = re.search(r"T[_]?([CNcn])\s*=\s*([0-9.]+)\s*K?", t_str)
    if m:
        sub = m.group(1).upper()
        val = m.group(2)
        return rf"$T_{{\mathrm{{{sub}}}}} = {val}\ \mathrm{{K}}$"
    return t_str

def load_elements():
    db_path = CONFIG["canvas"]["db_path"]
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at: {db_path}")
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)

# =============================================================================
# MAIN RENDERING PIPELINE
# =============================================================================

def render_periodic_table():
    elements = load_elements()
    elem_by_z = {e["atomic_number"]: e for e in elements}

    canvas_cfg = CONFIG["canvas"]
    fonts_cfg = CONFIG["fonts"]
    fs = CONFIG["font_sizes"]
    col = CONFIG["colors"]
    geom = CONFIG["geometry"]

    # Initialize high-resolution Matplotlib canvas
    fig = plt.figure(
        figsize=(canvas_cfg["fig_width_inches"], canvas_cfg["fig_height_inches"]),
        dpi=canvas_cfg["dpi"]
    )
    ax = fig.add_subplot(111)

    ax.set_xlim(*canvas_cfg["xlim"])
    ax.set_ylim(*canvas_cfg["ylim"])
    ax.axis("off")

    fig.patch.set_facecolor(canvas_cfg["bg_color"])
    ax.set_facecolor(canvas_cfg["bg_color"])

    cell_w = geom["cell_width"]
    cell_h = geom["cell_height"]
    row_y = geom["row_y"]

    def get_pos(period, col_idx):
        return float(col_idx), row_y[period]

    def get_f_pos(series_idx, col_offset):
        return 3.0 + col_offset, row_y[8 if series_idx == 0 else 9]

    # Group Numbers (1–18) along the top
    for g in range(1, 19):
        gx = g + cell_w / 2.0
        # Columns 1, 2, 13..18 sit above row 1; columns 3..12 sit above row 4
        if 3 <= g <= 12:
            gy = row_y[4] + cell_h + 0.18
        else:
            gy = row_y[1] + cell_h + 0.18
        ax.text(gx, gy, f"{g}", ha="center", va="center",
                fontsize=fs["group_numbers"], fontweight="bold",
                color=col["axis_number_color"], family=fonts_cfg["family"])

    # Period Numbers (1–7) along the left margin
    for p in range(1, 8):
        px = 0.55
        py = row_y[p] + cell_h / 2.0
        ax.text(px, py, f"{p}", ha="center", va="center",
                fontsize=fs["period_numbers"], fontweight="bold",
                color=col["axis_number_color"], family=fonts_cfg["family"])

    # Halo effect for critical mineral red star icon
    star_stroke = [patheffects.withStroke(linewidth=2.2, foreground=col["critical_star_halo"])]

    # -------------------------------------------------------------------------
    # Render all 118 Element Cells
    # -------------------------------------------------------------------------
    for z in range(1, 119):
        elem = elem_by_z[z]
        sym = elem["symbol"]
        mass = elem["atomic_mass"]
        period = elem["period"]
        classification = elem["magnetic_classification"]
        t_str = elem["transition_temperature_str"]
        is_crit = elem["usgs_critical_mineral"]
        is_rad = elem["radioactive"]

        # Grid Coordinates
        if 57 <= z <= 71:
            x, y = get_f_pos(0, z - 57)
        elif 89 <= z <= 103:
            x, y = get_f_pos(1, z - 89)
        else:
            x, y = get_pos(period, elem["group"])

        face_col, border_col, text_col, is_dark = get_style_for_classification(classification)

        # Base Cell Box
        cell_box = FancyBboxPatch(
            (x, y), cell_w, cell_h,
            boxstyle="square,pad=0",
            facecolor=face_col,
            edgecolor=border_col,
            linewidth=geom["cell_border_width"],
            zorder=2
        )
        ax.add_patch(cell_box)

        # Radioactive Diagonal Hatching
        if is_rad:
            hatch_box = FancyBboxPatch(
                (x, y), cell_w, cell_h,
                boxstyle="square,pad=0",
                facecolor="none",
                edgecolor=col["radioactive_hatch"],
                linewidth=0.0,
                hatch=geom["hatch_pattern"],
                alpha=geom["hatch_alpha"],
                zorder=3
            )
            ax.add_patch(hatch_box)

        # Atomic Number (top-left)
        num_color = col["text_muted_light"] if is_dark else col["text_muted"]
        ax.text(x + 0.08, y + cell_h - 0.16, str(z),
                ha="left", va="center",
                fontsize=fs["cell_number"], fontweight="bold",
                color=num_color, family=fonts_cfg["family"], zorder=4)

        # USGS Critical Mineral Red Star (top-right)
        if is_crit:
            ax.text(x + cell_w - 0.10, y + cell_h - 0.16, "★",
                    ha="right", va="center",
                    fontsize=fs["cell_star"], fontweight="bold",
                    color=col["critical_star"], path_effects=star_stroke,
                    family=fonts_cfg["family"], zorder=5)

        # Chemical Symbol (center)
        sym_y = y + cell_h * 0.56 if t_str else y + cell_h * 0.50
        sym_size = fs["cell_symbol"] if len(sym) <= 2 else fs["cell_symbol_small"]
        ax.text(x + cell_w / 2.0, sym_y, sym,
                ha="center", va="center",
                fontsize=sym_size, fontweight="heavy",
                color=text_col, family=fonts_cfg["family"], zorder=4)

        # Atomic Weight (below symbol)
        wt_y = y + cell_h * 0.34 if t_str else y + cell_h * 0.25
        wt_color = col["text_muted_light"] if is_dark else col["text_muted"]
        ax.text(x + cell_w / 2.0, wt_y, str(mass),
                ha="center", va="center",
                fontsize=fs["cell_weight"],
                fontweight="semibold" if is_dark else "normal",
                color=wt_color, family=fonts_cfg["family"], zorder=4)

        # Magnetic Transition Temperature (bottom, if applicable)
        if t_str:
            display_t_str = format_latex_temp(t_str)
            temp_y = y + 0.13
            t_color = col["temp_dark_bg"] if is_dark else col["temp_light_bg"]
            ax.text(x + cell_w / 2.0, temp_y, display_t_str,
                    ha="center", va="center",
                    fontsize=fs["cell_temp"], fontweight="bold",
                    color=t_color, family=fonts_cfg["family"], zorder=4)

    # -------------------------------------------------------------------------
    # Placeholders for Lanthanides and Actinides in Main Table
    # -------------------------------------------------------------------------
    lx, ly = get_pos(6, 3)
    l_ph = FancyBboxPatch((lx, ly), cell_w, cell_h, boxstyle="square,pad=0",
                          facecolor="#F1F5F9", edgecolor="#94A3B8",
                          linewidth=1.2, linestyle="--", zorder=2)
    ax.add_patch(l_ph)
    ax.text(lx + cell_w / 2.0, ly + cell_h * 0.62, "57–71",
            ha="center", va="center",
            fontsize=fs["placeholder_numbers"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"], zorder=4)
    ax.text(lx + cell_w / 2.0, ly + cell_h * 0.35, "La–Lu",
            ha="center", va="center",
            fontsize=fs["placeholder_symbols"], fontweight="semibold",
            color=col["axis_number_color"], family=fonts_cfg["family"], zorder=4)

    ax_p, ay_p = get_pos(7, 3)
    a_ph = FancyBboxPatch((ax_p, ay_p), cell_w, cell_h, boxstyle="square,pad=0",
                          facecolor="#F1F5F9", edgecolor="#94A3B8",
                          linewidth=1.2, linestyle="--", zorder=2)
    ax.add_patch(a_ph)
    ax.text(ax_p + cell_w / 2.0, ay_p + cell_h * 0.62, "89–103",
            ha="center", va="center",
            fontsize=fs["placeholder_numbers"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"], zorder=4)
    ax.text(ax_p + cell_w / 2.0, ay_p + cell_h * 0.35, "Ac–Lr",
            ha="center", va="center",
            fontsize=fs["placeholder_symbols"], fontweight="semibold",
            color=col["axis_number_color"], family=fonts_cfg["family"], zorder=4)

    # Labels for pulled-out rows
    lx_lbl, ly_lbl = get_f_pos(0, 0)
    ax.text(lx_lbl - 0.25, ly_lbl + cell_h / 2.0, "* Lanthanides\n   (57–71)",
            ha="right", va="center",
            fontsize=fs["series_labels"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"])

    ax_lbl, ay_lbl = get_f_pos(1, 0)
    ax.text(ax_lbl - 0.25, ay_lbl + cell_h / 2.0, "** Actinides\n   (89–103)",
            ha="right", va="center",
            fontsize=fs["series_labels"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"])

    # Connectors (subtle dashed arrows from main table placeholders to pulled-out rows)
    ax.annotate("", xy=(lx_lbl - 0.05, ly_lbl + cell_h * 0.6), xytext=(lx + cell_w * 0.25, ly),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.2, linestyle=":"))
    ax.annotate("", xy=(ax_lbl - 0.05, ay_lbl + cell_h * 0.6), xytext=(ax_p + cell_w * 0.25, ay_p),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=1.2, linestyle=":"))

    # -------------------------------------------------------------------------
    # HEADER: TITLE & SUBTITLE
    # -------------------------------------------------------------------------
    title_x = 3.0
    title_y = 14.15
    ax.text(title_x, title_y, "MAGNETIC PERIODIC TABLE",
            ha="left", va="top",
            fontsize=fs["main_title"], fontweight="heavy",
            color=col["header_color"], family=fonts_cfg["family"])
    ax.text(title_x, title_y - 0.52,
            "Magnetic Ground States, Critical Transition Temperatures, USGS Critical Minerals & Radioactivity",
            ha="left", va="top",
            fontsize=fs["subtitle"], fontweight="semibold",
            color=col["text_muted"], family=fonts_cfg["family"])

    # -------------------------------------------------------------------------
    # BOX 1: "HOW TO READ EACH ELEMENT CELL"
    # -------------------------------------------------------------------------
    b1_x = geom["box1_x"]
    b1_y = geom["boxes_bottom_y"]
    b1_w = geom["box1_width"]
    b1_h = geom["boxes_height"]

    box1 = FancyBboxPatch((b1_x, b1_y), b1_w, b1_h,
                          boxstyle="round,pad=0.1,rounding_size=0.15",
                          facecolor=col["box_bg"], edgecolor=col["box_border"],
                          linewidth=1.5, zorder=2)
    ax.add_patch(box1)

    ax.text(b1_x + 0.22, b1_y + b1_h - 0.32, "HOW TO READ EACH ELEMENT CELL",
            fontsize=fs["box_header"], fontweight="heavy",
            color=col["header_color"], family=fonts_cfg["family"], zorder=4)

    # Magnified Sample Cell (Dysprosium, Dy, as exemplar)
    sc_w = 1.70
    sc_h = 1.85
    sc_x = b1_x + 0.30
    sc_y = b1_y + 0.90

    sc_rect = FancyBboxPatch((sc_x, sc_y), sc_w, sc_h, boxstyle="square,pad=0",
                             facecolor=col["low_temp_ordering"],
                             edgecolor=col["border_low_temp"],
                             linewidth=2.0, zorder=3)
    ax.add_patch(sc_rect)

    # Sample cell text & markers
    ax.text(sc_x + 0.12, sc_y + sc_h - 0.22, "66",
            fontsize=fs["sample_cell_number"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"], zorder=4)
    ax.text(sc_x + sc_w - 0.12, sc_y + sc_h - 0.22, "★",
            fontsize=fs["sample_cell_star"], fontweight="bold",
            color=col["critical_star"], path_effects=star_stroke,
            family=fonts_cfg["family"], zorder=5)
    ax.text(sc_x + sc_w / 2.0, sc_y + sc_h * 0.56, "Dy",
            fontsize=fs["sample_cell_symbol"], fontweight="heavy",
            color=col["text_dark"], ha="center", va="center",
            family=fonts_cfg["family"], zorder=4)
    ax.text(sc_x + sc_w / 2.0, sc_y + sc_h * 0.33, "162.50",
            fontsize=fs["sample_cell_weight"], color=col["text_muted"],
            ha="center", va="center", family=fonts_cfg["family"], zorder=4)
    ax.text(sc_x + sc_w / 2.0, sc_y + 0.16, r"$T_{\mathrm{C}} = 85\ \mathrm{K}$",
            fontsize=fs["sample_cell_temp"], fontweight="bold",
            color=col["temp_light_bg"], ha="center", va="center",
            family=fonts_cfg["family"], zorder=4)

    # Callout annotations with arrows
    callouts = [
        ("Atomic Number", (sc_x + 0.12, sc_y + sc_h - 0.10), (b1_x + 2.35, b1_y + b1_h - 0.85)),
        ("USGS Critical Mineral (★)", (sc_x + sc_w - 0.10, sc_y + sc_h - 0.10), (b1_x + 2.35, b1_y + b1_h - 1.35)),
        ("Atomic Symbol", (sc_x + sc_w - 0.20, sc_y + sc_h * 0.56), (b1_x + 2.35, b1_y + b1_h - 1.85)),
        ("Standard Atomic Weight", (sc_x + sc_w - 0.15, sc_y + sc_h * 0.33), (b1_x + 2.35, b1_y + b1_h - 2.35)),
        ("Transition Temp (Kelvin)", (sc_x + sc_w - 0.15, sc_y + 0.16), (b1_x + 2.35, b1_y + b1_h - 2.85)),
    ]

    for label, target, text_pos in callouts:
        ax.annotate(
            label, xy=target, xytext=text_pos,
            textcoords="data",
            fontsize=fs["callout_text"], fontweight="semibold",
            color=col["text_dark"], family=fonts_cfg["family"],
            arrowprops=dict(arrowstyle="->", color=col["callout_arrow"], lw=1.2, shrinkA=2, shrinkB=4),
            va="center", zorder=5
        )

    # Radioactive note in Box 1
    #ax.text(b1_x + 0.22, b1_y + 0.38,
    #        "/// = Radioactive",
    #        fontsize=fs["box1_note"], fontweight="bold",
    #        color=col["text_muted"], family=fonts_cfg["family"], zorder=4)

    # -------------------------------------------------------------------------
    # BOX 2: "LEGEND & MAGNETIC CLASSIFICATION"
    # -------------------------------------------------------------------------
    b2_x = geom["box2_x"]
    b2_y = geom["boxes_bottom_y"]
    b2_w = geom["box2_width"]
    b2_h = geom["boxes_height"]

    box2 = FancyBboxPatch((b2_x, b2_y), b2_w, b2_h,
                          boxstyle="round,pad=0.1,rounding_size=0.15",
                          facecolor=col["box_bg"], edgecolor=col["box_border"],
                          linewidth=1.5, zorder=2)
    ax.add_patch(box2)

    ax.text(b2_x + 0.22, b2_y + b2_h - 0.32, "LEGEND & MAGNETIC CLASSIFICATION",
            fontsize=fs["box_header"], fontweight="heavy",
            color=col["header_color"], family=fonts_cfg["family"], zorder=4)

    legend_items = [
        (col["diamagnet"], col["border_diamagnet"], "Diamagnet"),
        (col["paramagnet"], col["border_paramagnet"], "Paramagnet"),
        (col["ferromagnet_rt"], col["border_ferromagnet"], r"Ferromagnet [$T_{\mathrm{C}} \geq 290\ \mathrm{K}$]"),
        (col["antiferromagnet_rt"], col["border_antiferromagnet"], r"Antiferromagnet [$T_{\mathrm{N}} \geq 290\ \mathrm{K}$]"),
        (col["low_temp_ordering"], col["border_low_temp"], "Low-Temp Magnetic Ordering < 290 K")
    ]

    sw_w = 0.42
    sw_h = 0.26
    sw_x = b2_x + 0.25

    for idx, item in enumerate(legend_items):
        face = item[0]
        edge = item[1]
        title_str = item[2]
        desc_str = item[3] if len(item) > 3 else None

        item_y = b2_y + b2_h - 0.76 - idx * 0.40
        swatch = FancyBboxPatch((sw_x, item_y), sw_w, sw_h, boxstyle="square,pad=0",
                                facecolor=face, edgecolor=edge, linewidth=1.2, zorder=3)
        ax.add_patch(swatch)

        if desc_str:
            ax.text(sw_x + sw_w + 0.14, item_y + sw_h * 0.65, title_str,
                    fontsize=fs["legend_item_title"], fontweight="bold",
                    color=col["text_dark"], family=fonts_cfg["family"], va="center", zorder=4)
            ax.text(sw_x + sw_w + 0.14, item_y + sw_h * 0.15, desc_str,
                    fontsize=fs["legend_item_desc"], fontweight="normal",
                    color=col["text_muted"], family=fonts_cfg["family"], va="center", zorder=4)
        else:
            ax.text(sw_x + sw_w + 0.14, item_y + sw_h / 2.0, title_str,
                    fontsize=fs["legend_item_title"], fontweight="bold",
                    color=col["text_dark"], family=fonts_cfg["family"], va="center", zorder=4)

    # Legend Indicators (Star and Hatch)
    ind_base_y = b2_y + 0.62
    ax.text(b2_x + 0.38, ind_base_y, "★",
            fontsize=16.0, fontweight="bold",
            color=col["critical_star"], path_effects=star_stroke,
            ha="center", va="center", family=fonts_cfg["family"], zorder=4)
    ax.text(b2_x + 0.65, ind_base_y,
            "USGS Critical Mineral (2022)",
            fontsize=fs["legend_indicator_text"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"], va="center", zorder=4)

    h_swatch = FancyBboxPatch((b2_x + 0.22, ind_base_y - 0.34), sw_w, 0.22, boxstyle="square,pad=0",
                              facecolor="#F1F5F9", edgecolor=col["radioactive_hatch"], linewidth=1.0,
                              hatch=geom["hatch_pattern"], zorder=3)
    ax.add_patch(h_swatch)
    ax.text(b2_x + 0.65, ind_base_y - 0.23,
            "Radioactive Element",
            fontsize=fs["legend_indicator_text"], fontweight="bold",
            color=col["text_dark"], family=fonts_cfg["family"], va="center", zorder=4)

    # -------------------------------------------------------------------------
    # FOOTNOTE ATTRIBUTION
    # -------------------------------------------------------------------------
    foot_x = 0.55
    foot_y = -0.15
    footnote_text = (
        "Scientific Attributions & Reference Data:\n"
        "• Magnetic Periodic Table concept & magnetic ground states inspired by Prof. J. M. D. Coey and the Magnetism & Spin Electronics Group, School of Physics, Trinity College Dublin.\n"
        "• Critical Minerals designated according to the official U.S. Geological Survey (USGS) 2022 List of 50 Critical Mineral Commodities (Energy Act of 2020).\n"
        "• Standard atomic weights, isotopic stability, and physical constants based on IUPAC Commission on Isotopic Abundances and Atomic Weights (CIAAW) & NIST Physical Measurement Laboratory."
    )
    ax.text(foot_x, foot_y, footnote_text,
            ha="left", va="top",
            fontsize=fs["footnote"], fontweight="normal",
            color=col["text_muted"], family=fonts_cfg["family"], linespacing=1.4)

    # Save high-resolution periodic table image
    plt.tight_layout()
    plt.savefig(canvas_cfg["output_path"], dpi=canvas_cfg["dpi"],
                facecolor=fig.get_facecolor(), edgecolor="none", bbox_inches="tight")
    plt.close()
    print(f"Successfully generated high-resolution periodic table: {canvas_cfg['output_path']}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Render high-resolution magnetic periodic table PNG.")
    parser.add_argument("-i", "--input", "--db", dest="db", default=None, help="Input database JSON path")
    parser.add_argument("-o", "--output", default=None, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=None, help="Rendering DPI (default: 300)")
    args = parser.parse_args()

    if args.db:
        CONFIG["canvas"]["db_path"] = os.path.abspath(args.db)
    if args.output:
        CONFIG["canvas"]["output_path"] = os.path.abspath(args.output)
    if args.dpi:
        CONFIG["canvas"]["dpi"] = args.dpi

    render_periodic_table()

if __name__ == "__main__":
    main()
