#!/usr/bin/env python3
"""
generate_interactive_preview.py

Generates interactive_preview.png:
A crisp, high-resolution visual glance of the live interactive web application
for display in the GitHub README.
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def create_preview(output_path="interactive_preview.png"):
    base_dir = Path(__file__).resolve().parent
    with open(base_dir / "magnetic_elements_enriched.json", "r", encoding="utf-8") as f:
        elements = json.load(f)

    elem_map = {e["symbol"]: e for e in elements}

    # Grid positions for standard 18-col periodic table
    grid_coords = {
        "H": (1, 1), "He": (1, 18),
        "Li": (2, 1), "Be": (2, 2), "B": (2, 13), "C": (2, 14), "N": (2, 15), "O": (2, 16), "F": (2, 17), "Ne": (2, 18),
        "Na": (3, 1), "Mg": (3, 2), "Al": (3, 13), "Si": (3, 14), "P": (3, 15), "S": (3, 16), "Cl": (3, 17), "Ar": (3, 18),
        "K": (4, 1), "Ca": (4, 2), "Sc": (4, 3), "Ti": (4, 4), "V": (4, 5), "Cr": (4, 6), "Mn": (4, 7), "Fe": (4, 8), "Co": (4, 9), "Ni": (4, 10), "Cu": (4, 11), "Zn": (4, 12), "Ga": (4, 13), "Ge": (4, 14), "As": (4, 15), "Se": (4, 16), "Br": (4, 17), "Kr": (4, 18),
        "Rb": (5, 1), "Sr": (5, 2), "Y": (5, 3), "Zr": (5, 4), "Nb": (5, 5), "Mo": (5, 6), "Tc": (5, 7), "Ru": (5, 8), "Rh": (5, 9), "Pd": (5, 10), "Ag": (5, 11), "Cd": (5, 12), "In": (5, 13), "Sn": (5, 14), "Sb": (5, 15), "Te": (5, 16), "I": (5, 17), "Xe": (5, 18),
        "Cs": (6, 1), "Ba": (6, 2), "La": (6, 3), "Hf": (6, 4), "Ta": (6, 5), "W": (6, 6), "Re": (6, 7), "Os": (6, 8), "Ir": (6, 9), "Pt": (6, 10), "Au": (6, 11), "Hg": (6, 12), "Tl": (6, 13), "Pb": (6, 14), "Bi": (6, 15), "Po": (6, 16), "At": (6, 17), "Rn": (6, 18),
        "Fr": (7, 1), "Ra": (7, 2), "Ac": (7, 3), "Rf": (7, 4), "Db": (7, 5), "Sg": (7, 6), "Bh": (7, 7), "Hs": (7, 8), "Mt": (7, 9), "Ds": (7, 10), "Rg": (7, 11), "Cn": (7, 12), "Nh": (7, 13), "Fl": (7, 14), "Mc": (7, 15), "Lv": (7, 16), "Ts": (7, 17), "Og": (7, 18),
    }
    # Lanthanides
    lanths = ["Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
    for i, sym in enumerate(lanths):
        grid_coords[sym] = (8.5, 4 + i)
    # Actinides
    acts = ["Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"]
    for i, sym in enumerate(acts):
        grid_coords[sym] = (9.7, 4 + i)

    color_map = {
        "Ferromagnet (T_C >= 290 K)": ("#2563EB", "#FFFFFF"),
        "Antiferromagnet (T_N >= 290 K)": ("#16A34A", "#FFFFFF"),
        "Low-temperature magnetic ordering": ("#86EFAC", "#14532D"),
        "Paramagnet": ("#FEF08A", "#713F12"),
        "Diamagnet": ("#FFFFFF", "#0F172A")
    }

    fig = plt.figure(figsize=(19.2, 10.8), dpi=120)
    fig.patch.set_facecolor('#0B0F19')

    # Main 2D axis
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    ax.axis('off')

    # 1. Browser Title Bar Mockup
    ax.add_patch(patches.Rectangle((0, 1020), 1920, 60, facecolor='#111827', edgecolor='#1F2937', linewidth=1))
    # Traffic light dots
    ax.add_patch(patches.Circle((35, 1050), 7, facecolor='#EF4444'))
    ax.add_patch(patches.Circle((60, 1050), 7, facecolor='#F59E0B'))
    ax.add_patch(patches.Circle((85, 1050), 7, facecolor='#10B981'))
    # URL pill
    ax.add_patch(patches.FancyBboxPatch((130, 1032), 750, 36, boxstyle="round,pad=3,rounding_size=8",
                                       facecolor='#1F2937', edgecolor='#374151', linewidth=1))
    ax.text(150, 1050, 'https://btemuujin.github.io/mag_periodic_table/', color='#93C5FD', fontsize=12,
            fontfamily='monospace', va='center')
    ax.add_patch(patches.FancyBboxPatch((810, 1038), 55, 24, boxstyle="round,pad=2,rounding_size=6",
                                       facecolor='#065F46', edgecolor='#10B981', linewidth=1))
    ax.text(837, 1050, 'LIVE', color='#A7F3D0', fontsize=10, weight='bold', ha='center', va='center')

    # 2. Web App Header
    ax.text(40, 975, 'Magnetic Periodic Table of the Elements', color='#F8FAFC', fontsize=22, weight='bold')
    ax.text(40, 948, 'Interactive Web Application with 3D WebGL Crystal Spins & Quantum Magnetism Inspection',
            color='#94A3B8', fontsize=12)

    # 3. Interactive Filter Toolbar
    pills = [
        ("All (118)", '#2563EB', '#FFFFFF', True),
        ("Ferromagnet (4)", '#1E293B', '#93C5FD', False),
        ("Antiferromagnet (1)", '#1E293B', '#86EFAC', False),
        ("Low-T Ordering (11)", '#1E293B', '#86EFAC', False),
        ("★ USGS Critical (50)", '#1E293B', '#FCA5A5', False),
        ("Paramagnet (55)", '#1E293B', '#FEF08A', False),
        ("Diamagnet (47)", '#1E293B', '#E2E8F0', False),
    ]
    cur_x = 40
    for label, bg, fg, is_active in pills:
        pw = len(label) * 8.5 + 24
        edge = '#60A5FA' if is_active else '#334155'
        ax.add_patch(patches.FancyBboxPatch((cur_x, 902), pw, 32, boxstyle="round,pad=2,rounding_size=8",
                                           facecolor=bg, edgecolor=edge, linewidth=1.5 if is_active else 1))
        ax.text(cur_x + pw/2, 918, label, color=fg, fontsize=11, weight='bold' if is_active else 'normal',
                ha='center', va='center')
        cur_x += pw + 12

    # Search bar pill
    ax.add_patch(patches.FancyBboxPatch((1040, 902), 240, 32, boxstyle="round,pad=2,rounding_size=8",
                                       facecolor='#1E293B', edgecolor='#334155', linewidth=1))
    ax.text(1055, 918, 'Search element (e.g. Dy, Fe)...', color='#64748B', fontsize=11, va='center')

    # 4. Periodic Table Grid
    grid_left = 30
    grid_top = 860
    cell_w = 66
    cell_h = 66
    gap_x = 4
    gap_y = 4

    for sym, (row, col) in grid_coords.items():
        elem = elem_map.get(sym)
        if not elem:
            continue
        cx = grid_left + (col - 1) * (cell_w + gap_x)
        cy = grid_top - (row - 1) * (cell_h + gap_y) - cell_h

        bg_col, text_col = color_map.get(elem["magnetic_classification"], ('#FFFFFF', '#000000'))
        is_selected = (sym == "Dy")

        # Cell background
        edge = '#38BDF8' if is_selected else ('#FFFFFF' if elem.get("radioactive") else '#334155')
        lw = 3 if is_selected else 1
        ax.add_patch(patches.Rectangle((cx, cy), cell_w, cell_h, facecolor=bg_col, edgecolor=edge, linewidth=lw))

        # Selection glow for Dy
        if is_selected:
            ax.add_patch(patches.Rectangle((cx-3, cy-3), cell_w+6, cell_h+6, fill=False, edgecolor='#38BDF8', linewidth=2.5))

        # Atomic number
        ax.text(cx + 5, cy + cell_h - 12, str(elem["atomic_number"]), color=text_col, fontsize=8, weight='bold')

        # Critical mineral star
        if elem.get("usgs_critical_mineral"):
            ax.text(cx + cell_w - 12, cy + cell_h - 12, '★', color='#DC2626', fontsize=10, weight='bold')

        # Symbol
        ax.text(cx + cell_w/2, cy + cell_h/2 - 2, sym, color=text_col, fontsize=14, weight='bold', ha='center', va='center')

        # Transition temp or atomic mass
        sub = ""
        tt = elem.get("transition_temperature_k")
        tt_type = elem.get("transition_temperature_type")
        if tt is not None and tt_type:
            sub = f"{tt_type}={int(tt)}K"
        else:
            try:
                sub = f"{float(elem['atomic_mass']):.1f}"
            except (ValueError, TypeError):
                sub = str(elem.get('atomic_mass', ''))
        ax.text(cx + cell_w/2, cy + 8, sub, color=text_col, fontsize=7, ha='center', va='center')

    # F-block labels
    ax.text(grid_left + 2*(cell_w+gap_x) + cell_w/2, grid_top - 7.5*(cell_h+gap_y) - cell_h/2, "Lanthanides",
            color='#94A3B8', fontsize=10, weight='bold', ha='center', va='center')
    ax.text(grid_left + 2*(cell_w+gap_x) + cell_w/2, grid_top - 8.7*(cell_h+gap_y) - cell_h/2, "Actinides",
            color='#94A3B8', fontsize=10, weight='bold', ha='center', va='center')

    # 5. Right Slide-out Drawer: Inspecting Dysprosium (Dy, Z=66)
    drawer_x = 1310
    drawer_w = 580
    drawer_y = 30
    drawer_h = 960

    # Drawer shadow & background
    ax.add_patch(patches.Rectangle((drawer_x-10, drawer_y), 10, drawer_h, facecolor='#000000', alpha=0.4))
    ax.add_patch(patches.Rectangle((drawer_x, drawer_y), drawer_w, drawer_h, facecolor='#111827',
                                  edgecolor='#374151', linewidth=1.5))

    # Drawer Header
    ax.add_patch(patches.Rectangle((drawer_x, drawer_y + drawer_h - 100), drawer_w, 100, facecolor='#1F2937'))
    ax.text(drawer_x + 30, drawer_y + drawer_h - 40, '66  Dy  Dysprosium', color='#F8FAFC', fontsize=22, weight='bold')
    ax.text(drawer_x + drawer_w - 40, drawer_y + drawer_h - 40, '✕', color='#94A3B8', fontsize=18, ha='center')

    # Badges
    b_y = drawer_y + drawer_h - 80
    ax.add_patch(patches.FancyBboxPatch((drawer_x + 30, b_y), 160, 24, boxstyle="round,pad=2,rounding_size=6",
                                       facecolor='#14532D', edgecolor='#86EFAC', linewidth=1))
    ax.text(drawer_x + 110, b_y + 12, 'Low-T Ordering (TC=85K)', color='#86EFAC', fontsize=9, weight='bold', ha='center', va='center')

    ax.add_patch(patches.FancyBboxPatch((drawer_x + 200, b_y), 130, 24, boxstyle="round,pad=2,rounding_size=6",
                                       facecolor='#7F1D1D', edgecolor='#EF4444', linewidth=1))
    ax.text(drawer_x + 265, b_y + 12, '★ USGS Critical', color='#FCA5A5', fontsize=9, weight='bold', ha='center', va='center')

    ax.add_patch(patches.FancyBboxPatch((drawer_x + 340, b_y), 165, 24, boxstyle="round,pad=2,rounding_size=6",
                                       facecolor='#1E3A8A', edgecolor='#60A5FA', linewidth=1))
    ax.text(drawer_x + 422, b_y + 12, 'Hard Magnetic Vector', color='#93C5FD', fontsize=9, weight='bold', ha='center', va='center')

    # Tab bar
    tab_y = drawer_y + drawer_h - 140
    tabs = ["Overview", "Crystallography & 3D Spins ★", "Quantum", "Economics"]
    t_x = drawer_x + 20
    for i, t in enumerate(tabs):
        active = (i == 1)
        tw = len(t) * 7.5 + 14
        if active:
            ax.add_patch(patches.FancyBboxPatch((t_x, tab_y), tw, 30, boxstyle="round,pad=2,rounding_size=6",
                                               facecolor='#374151', edgecolor='#38BDF8', linewidth=1.5))
            ax.text(t_x + tw/2, tab_y + 15, t, color='#38BDF8', fontsize=10, weight='bold', ha='center', va='center')
        else:
            ax.text(t_x + tw/2, tab_y + 15, t, color='#94A3B8', fontsize=10, ha='center', va='center')
        t_x += tw + 8

    # Inset 3D Viewer Area
    view_x = drawer_x + 30
    view_y = drawer_y + 440
    view_w = drawer_w - 60
    view_h = 350
    ax.add_patch(patches.Rectangle((view_x, view_y), view_w, view_h, facecolor='#030712', edgecolor='#374151', linewidth=1.5))
    ax.text(view_x + 15, view_y + view_h - 22, 'INTERACTIVE 3D CRYSTAL & MAGNETIC SPIN VIEWER', color='#38BDF8', fontsize=10, weight='bold')
    ax.text(view_x + view_w - 15, view_y + view_h - 22, '[Fullscreen]  •  Auto-Rotate: ON', color='#94A3B8', fontsize=9, ha='right')

    # Overlay badge on 3D viewer
    ax.add_patch(patches.FancyBboxPatch((view_x + 15, view_y + 15), 320, 26, boxstyle="round,pad=2,rounding_size=6",
                                       facecolor='#111827', edgecolor='#374151', alpha=0.9))
    ax.text(view_x + 25, view_y + 28, 'HCP (Hexagonal Close-Packed)  •  P6_3/mmc (#194)', color='#E2E8F0', fontsize=9, va='center')

    # Draw 3D Unit Cell inset via 3D projection
    ax3d = fig.add_axes([view_x/1920, view_y/1080, view_w/1920, view_h/1080], projection='3d')
    ax3d.set_facecolor('#030712')
    ax3d.patch.set_alpha(0.0)

    # HCP geometry
    a = 1.0
    c = 1.6
    angles = np.linspace(0, 2*np.pi, 7)
    x_bot = a * np.cos(angles)
    y_bot = a * np.sin(angles)
    z_bot = np.zeros_like(x_bot)

    x_top = x_bot
    y_top = y_bot
    z_top = np.ones_like(x_top) * c

    # Draw hexagonal bases
    ax3d.plot(x_bot, y_bot, z_bot, color='#475569', linewidth=1.5)
    ax3d.plot(x_top, y_top, z_top, color='#475569', linewidth=1.5)

    # Vertical prism edges
    for i in range(6):
        ax3d.plot([x_bot[i], x_top[i]], [y_bot[i], y_top[i]], [0, c], color='#475569', linewidth=1.2, linestyle=':')

    # Internal atoms
    int_x = [0.0, a/np.sqrt(3)*np.cos(np.pi/6), -a/np.sqrt(3)*np.cos(np.pi/6)]
    int_y = [0.0, a/np.sqrt(3)*np.sin(np.pi/6), a/np.sqrt(3)*np.sin(np.pi/6)]
    int_z = [0.0, c/2, c/2]

    # Plot atoms
    ax3d.scatter(x_bot[:6], y_bot[:6], z_bot[:6], s=140, color='#38BDF8', edgecolors='#FFFFFF', depthshade=True)
    ax3d.scatter(x_top[:6], y_top[:6], z_top[:6], s=140, color='#38BDF8', edgecolors='#FFFFFF', depthshade=True)
    ax3d.scatter(int_x, int_y, int_z, s=160, color='#60A5FA', edgecolors='#FFFFFF', depthshade=True)

    # Magnetic Spin Vectors (Directional Cyan arrows pointing along c-axis)
    arrow_len = 0.55
    for i in range(6):
        ax3d.quiver(x_top[i], y_top[i], z_top[i], 0, 0, arrow_len, color='#06B6D4', linewidth=2.5, arrow_length_ratio=0.35)
    for ix, iy, iz in zip(int_x, int_y, int_z):
        ax3d.quiver(ix, iy, iz, 0, 0, arrow_len, color='#06B6D4', linewidth=2.5, arrow_length_ratio=0.35)

    ax3d.set_xlim(-1.3, 1.3)
    ax3d.set_ylim(-1.3, 1.3)
    ax3d.set_zlim(-0.2, c + 0.8)
    ax3d.view_init(elev=22, azim=38)
    ax3d.axis('off')

    # Key Data Cards Below 3D Viewer in Drawer
    card_y = drawer_y + 40
    card_h = 370
    ax.add_patch(patches.Rectangle((view_x, card_y), view_w, card_h, facecolor='#1F2937', edgecolor='#374151', linewidth=1))

    ax.text(view_x + 20, card_y + card_h - 25, 'ADVANCED QUANTUM & MAGNETIC PARAMETERS', color='#F8FAFC', fontsize=11, weight='bold')

    props = [
        ("Russell–Saunders Term", "⁵I₈  (S = 5/2, L = 5, J = 8)", "#E2E8F0"),
        ("Landé g_J Factor", "1.333  (Theoretical Free Ion)", "#E2E8F0"),
        ("Theoretical Atomic Moment μ_eff", "10.65 μ_B  (Free Ion Ground State)", "#38BDF8"),
        ("Low-T Saturation Magnetization M_s", "2.40 Tesla  (at 4.2 K cryogenic)", "#38BDF8"),
        ("Spontaneous Ordering Temp", "T_C = 85 K  (Helimagnetic above 85 K, T_N=179 K)", "#86EFAC"),
        ("Bulk Ordered Moment μ_ord", "10.2 μ_B / atom  (0 K ferromagnetic state)", "#38BDF8"),
        ("Materials Project Ground State", "mp-114  (HCP, Space Group 194)", "#93C5FD"),
        ("Technological Alloy Role", "Hard Magnetic Vector (High-temp Nd-Fe-B)", "#FDE047"),
    ]

    py = card_y + card_h - 55
    for label, val, val_col in props:
        ax.text(view_x + 20, py, label, color='#94A3B8', fontsize=10)
        ax.text(view_x + view_w - 20, py, val, color=val_col, fontsize=10, weight='bold', ha='right')
        py -= 38
        if py > card_y + 10:
            ax.plot([view_x + 15, view_x + view_w - 15], [py + 12, py + 12], color='#374151', linewidth=0.8, linestyle=':')

    plt.savefig(output_path, facecolor='#0B0F19', edgecolor='none')
    plt.close()
    print(f"✓ Generated interactive preview at: {output_path}")

if __name__ == "__main__":
    create_preview()
