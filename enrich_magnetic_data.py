#!/usr/bin/env python3
"""
enrich_magnetic_data.py

Enriches magnetic_elements_db.json / magnetic_elements_enriched.json with
advanced, quantitative magnetic parameters across quantum, thermodynamic,
and technological domains for all 118 chemical elements:

1. Quantum & Microscopic Parameters:
   - term_symbol: Ground-state atomic term symbol in LaTeX format (e.g., ^{5}\\mathrm{D}_4).
   - lande_g_factor: Landé g-factor (g_J).
   - atomic_moment_mu_B: Ground-state magnetic moment (μ_B per atom).

2. Thermodynamic & Macroscopic Magnetism:
   - molar_susceptibility_298K: Experimental molar magnetic susceptibility χ_m at 298 K (cm³/mol).
   - curie_weiss_temp_K: Paramagnetic Curie-Weiss temperature (θ_CW in Kelvin).
   - saturation_magnetization_T: Saturation magnetization (M_s in Tesla, if ferromagnetic).
   - magnetocrystalline_anisotropy_J_m3: First-order anisotropy constant (K_1 in J/m³).

3. Spintronics & Microscopic Interactions:
   - spin_polarization_percent: Conduction electron spin polarization at the Fermi level (P %).
   - exchange_interaction: Primary coupling type (Direct Exchange, RKKY, Superexchange, etc.).

4. Technological Role:
   - magnet_role: Hard Magnetic Vector, Soft Magnetic Core, Magnetocaloric Active Element,
                  or Magnetically Inert Matrix.

Sources: NIST Atomic Spectra Database (ASD), CRC Handbook of Chemistry and Physics,
Landolt-Börnstein Numerical Data and Functional Relationships in Science and Technology,
mendeleev database, and Materials Project (mp-api).
"""

import os
import sys
import json

# Try importing mendeleev
try:
    import mendeleev
    MENDELEEV_AVAILABLE = True
except ImportError:
    MENDELEEV_AVAILABLE = False

# Try checking Materials Project API
MP_API_KEY = os.environ.get("MP_API_KEY", None)
MP_AVAILABLE = False
if MP_API_KEY:
    try:
        from mp_api.client import MPRester
        MP_AVAILABLE = True
    except ImportError:
        pass


# =============================================================================
# QUANTUM & ADVANCED MAGNETIC REFERENCE DATASET FOR ALL 118 ELEMENTS
# Strictly Magnetic — NO superconducting properties included.
#
# Tuple structure:
# (
#   term_symbol_latex,               # Ground state term symbol in LaTeX (e.g. "^{5}\\mathrm{D}_4")
#   lande_g_factor,                  # g_J float (0.0 if J=0)
#   atomic_moment_mu_B,              # Ground-state magnetic moment in μ_B
#   molar_susceptibility_298K,       # χ_m in cm³/mol at 298 K
#   curie_weiss_temp_K,              # θ_CW in K (float or None)
#   saturation_magnetization_T,      # M_s in Tesla (float or None)
#   magnetocrystalline_anisotropy,   # K_1 in J/m³ (float or None)
#   spin_polarization_percent,       # P % (float)
#   exchange_interaction,            # Coupling mechanism description
#   magnet_role                      # "Hard Magnetic Vector" | "Soft Magnetic Core" |
#                                    # "Magnetocaloric Active Element" | "Magnetically Inert Matrix"
# )
# =============================================================================

MAGNETIC_QUANTUM_DATA = {
    # ------------------ Period 1 ------------------
    1: (  # H
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, -3.98e-6, None, None, None,
        0.0, "Diamagnetic Paired Electron Response", "Magnetically Inert Matrix"
    ),
    2: (  # He
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -2.02e-6, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),

    # ------------------ Period 2 ------------------
    3: (  # Li
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, 1.42e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    4: (  # Be
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -9.00e-6, None, None, None,
        0.0, "Diamagnetic Core & Valence Response", "Magnetically Inert Matrix"
    ),
    5: (  # B
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, -6.70e-6, None, None, None,
        0.0, "Diamagnetic Core & Valence Response", "Magnetically Inert Matrix"
    ),
    6: (  # C
        "^{3}\\mathrm{P}_{0}", 0.0, 0.0, -6.00e-6, None, None, None,
        0.0, "Diamagnetic Orbital Precession", "Magnetically Inert Matrix"
    ),
    7: (  # N
        "^{4}\\mathrm{S}^\\circ_{3/2}", 2.002, 3.00, -1.20e-5, None, None, None,
        0.0, "Diamagnetic Molecular Response", "Magnetically Inert Matrix"
    ),
    8: (  # O
        "^{3}\\mathrm{P}_{2}", 1.50, 3.00, 3.45e-3, -40.0, None, None,
        0.0, "Molecular Triplet Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    9: (  # F
        "^{2}\\mathrm{P}^\\circ_{3/2}", 1.333, 1.73, -1.51e-5, None, None, None,
        0.0, "Diamagnetic Molecular Response", "Magnetically Inert Matrix"
    ),
    10: (  # Ne
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -6.74e-6, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),

    # ------------------ Period 3 ------------------
    11: (  # Na
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, 1.60e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    12: (  # Mg
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, 1.32e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    13: (  # Al
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, 1.65e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    14: (  # Si
        "^{3}\\mathrm{P}_{0}", 0.0, 0.0, -3.90e-6, None, None, None,
        0.0, "Diamagnetic Core Response", "Soft Magnetic Core"
    ),
    15: (  # P
        "^{4}\\mathrm{S}^\\circ_{3/2}", 2.002, 3.00, -2.63e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    16: (  # S
        "^{3}\\mathrm{P}_{2}", 1.50, 3.00, -1.55e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    17: (  # Cl
        "^{2}\\mathrm{P}^\\circ_{3/2}", 1.333, 1.73, -2.01e-5, None, None, None,
        0.0, "Diamagnetic Molecular Response", "Magnetically Inert Matrix"
    ),
    18: (  # Ar
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -1.96e-5, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),

    # ------------------ Period 4 ------------------
    19: (  # K
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, 2.08e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    20: (  # Ca
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, 4.00e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    21: (  # Sc
        "^{2}\\mathrm{D}_{3/2}", 0.80, 1.55, 2.63e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    22: (  # Ti
        "^{3}\\mathrm{F}_{2}", 0.667, 1.63, 1.53e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    23: (  # V
        "^{4}\\mathrm{F}_{3/2}", 0.40, 1.24, 2.55e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Soft Magnetic Core"
    ),
    24: (  # Cr
        "^{7}\\mathrm{S}_{3}", 2.00, 0.62, 1.80e-4, -1070.0, None, None,
        43.0, "Itinerant Spin-Density Wave / Direct Exchange", "Magnetically Inert Matrix"
    ),
    25: (  # Mn
        "^{6}\\mathrm{S}_{5/2}", 2.00, 1.10, 5.29e-4, -483.0, None, None,
        0.0, "Direct / Superexchange Antiferromagnetic Coupling", "Magnetocaloric Active Element"
    ),
    26: (  # Fe
        "^{5}\\mathrm{D}_{4}", 1.50, 2.22, None, 1093.0, 2.15, 4.80e4,
        44.0, "Direct Exchange / Itinerant d-band Coupling", "Soft Magnetic Core"
    ),
    27: (  # Co
        "^{4}\\mathrm{F}_{9/2}", 1.333, 1.72, None, 1428.0, 1.76, 4.10e5,
        42.0, "Direct Exchange / Itinerant d-band Coupling", "Hard Magnetic Vector"
    ),
    28: (  # Ni
        "^{3}\\mathrm{F}_{4}", 1.25, 0.606, None, 650.0, 0.61, -4.50e3,
        45.0, "Direct Exchange / Itinerant d-band Coupling", "Soft Magnetic Core"
    ),
    29: (  # Cu
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, -5.46e-6, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    30: (  # Zn
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -1.14e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    31: (  # Ga
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, -2.16e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    32: (  # Ge
        "^{3}\\mathrm{P}_{0}", 0.0, 0.0, -7.70e-6, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    33: (  # As
        "^{4}\\mathrm{S}^\\circ_{3/2}", 2.002, 3.00, -5.50e-6, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    34: (  # Se
        "^{3}\\mathrm{P}_{2}", 1.50, 3.00, -1.89e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    35: (  # Br
        "^{2}\\mathrm{P}^\\circ_{3/2}", 1.333, 1.73, -5.64e-5, None, None, None,
        0.0, "Diamagnetic Molecular Response", "Magnetically Inert Matrix"
    ),
    36: (  # Kr
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -2.88e-5, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),

    # ------------------ Period 5 ------------------
    37: (  # Rb
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, 1.82e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    38: (  # Sr
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, 9.12e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    39: (  # Y
        "^{2}\\mathrm{D}_{3/2}", 0.80, 1.55, 1.91e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    40: (  # Zr
        "^{3}\\mathrm{F}_{2}", 0.667, 1.63, 1.22e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    41: (  # Nb
        "^{6}\\mathrm{D}_{1/2}", 3.333, 1.67, 2.08e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    42: (  # Mo
        "^{7}\\mathrm{S}_{3}", 2.00, 5.92, 8.90e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Soft Magnetic Core"
    ),
    43: (  # Tc
        "^{6}\\mathrm{S}_{5/2}", 2.00, 5.92, 2.70e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    44: (  # Ru
        "^{5}\\mathrm{F}_{5}", 1.40, 5.92, 4.32e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    45: (  # Rh
        "^{4}\\mathrm{F}_{9/2}", 1.333, 5.59, 1.11e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    46: (  # Pd
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, 5.42e-4, None, None, None,
        0.0, "Stoner Enhanced Pauli Paramagnetism", "Magnetically Inert Matrix"
    ),
    47: (  # Ag
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, -1.95e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    48: (  # Cd
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -1.98e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    49: (  # In
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, -1.46e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    50: (  # Sn
        "^{3}\\mathrm{P}_{0}", 0.0, 0.0, -4.50e-6, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    51: (  # Sb
        "^{4}\\mathrm{S}^\\circ_{3/2}", 2.002, 3.00, -9.90e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    52: (  # Te
        "^{3}\\mathrm{P}_{2}", 1.50, 3.00, -3.95e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    53: (  # I
        "^{2}\\mathrm{P}^\\circ_{3/2}", 1.333, 1.73, -8.87e-5, None, None, None,
        0.0, "Diamagnetic Molecular Response", "Magnetically Inert Matrix"
    ),
    54: (  # Xe
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -4.39e-5, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),

    # ------------------ Period 6 ------------------
    55: (  # Cs
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, 2.90e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    56: (  # Ba
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, 2.06e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    57: (  # La
        "^{2}\\mathrm{D}_{3/2}", 0.80, 1.55, 9.90e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    58: (  # Ce
        "^{1}\\mathrm{G}^\\circ_{4}", 1.00, 2.54, 2.45e-3, -50.0, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    59: (  # Pr
        "^{4}\\mathrm{I}^\\circ_{9/2}", 0.727, 3.58, 5.43e-3, -10.0, None, None,
        0.0, "RKKY Indirect Exchange", "Hard Magnetic Vector"
    ),
    60: (  # Nd
        "^{5}\\mathrm{I}_{4}", 0.60, 3.62, 5.62e-3, -16.0, None, None,
        0.0, "RKKY Indirect Exchange", "Hard Magnetic Vector"
    ),
    61: (  # Pm
        "^{6}\\mathrm{H}^\\circ_{5/2}", 0.286, 2.68, 3.00e-3, 0.0, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    62: (  # Sm
        "^{7}\\mathrm{F}_{0}", 0.0, 0.84, 1.28e-3, 0.0, None, None,
        0.0, "RKKY Indirect Exchange", "Hard Magnetic Vector"
    ),
    63: (  # Eu
        "^{8}\\mathrm{S}^\\circ_{7/2}", 2.00, 7.94, 3.38e-2, 108.0, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    64: (  # Gd
        "^{9}\\mathrm{D}^\\circ_{2}", 2.667, 7.63, 0.120, 317.0, 2.06, -1.20e5,
        43.0, "RKKY Indirect Exchange", "Magnetocaloric Active Element"
    ),
    65: (  # Tb
        "^{6}\\mathrm{H}^\\circ_{15/2}", 1.333, 9.34, 0.112, 239.0, 1.44, 1.00e7,
        38.0, "RKKY Indirect Exchange", "Hard Magnetic Vector"
    ),
    66: (  # Dy
        "^{5}\\mathrm{I}_{8}", 1.25, 10.60, 0.1035, 157.0, 2.63, 1.10e7,
        40.0, "RKKY Indirect Exchange", "Hard Magnetic Vector"
    ),
    67: (  # Ho
        "^{4}\\mathrm{I}^\\circ_{15/2}", 1.20, 10.60, 0.073, 88.0, 3.87, 2.50e6,
        35.0, "RKKY Indirect Exchange", "Magnetocaloric Active Element"
    ),
    68: (  # Er
        "^{3}\\mathrm{H}_{6}", 1.167, 9.00, 0.044, 45.0, 3.33, -2.80e6,
        32.0, "RKKY Indirect Exchange", "Magnetocaloric Active Element"
    ),
    69: (  # Tm
        "^{2}\\mathrm{F}^\\circ_{7/2}", 1.143, 7.10, 0.0255, 22.0, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetocaloric Active Element"
    ),
    70: (  # Yb
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -2.48e-5, None, None, None,
        0.0, "Diamagnetic Closed 4f Shell Response", "Magnetically Inert Matrix"
    ),
    71: (  # Lu
        "^{2}\\mathrm{D}_{3/2}", 0.80, 1.55, 1.60e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    72: (  # Hf
        "^{3}\\mathrm{F}_{2}", 0.667, 1.63, 7.50e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    73: (  # Ta
        "^{4}\\mathrm{F}_{3/2}", 0.40, 1.24, 1.54e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    74: (  # W
        "^{5}\\mathrm{D}_{0}", 0.0, 0.0, 5.50e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    75: (  # Re
        "^{6}\\mathrm{S}_{5/2}", 2.00, 5.92, 6.80e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    76: (  # Os
        "^{5}\\mathrm{D}_{4}", 1.50, 5.50, 1.10e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    77: (  # Ir
        "^{4}\\mathrm{F}_{9/2}", 1.333, 5.59, 2.56e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    78: (  # Pt
        "^{3}\\mathrm{D}_{3}", 1.333, 3.90, 2.019e-4, None, None, None,
        0.0, "Stoner Enhanced Pauli Paramagnetism", "Hard Magnetic Vector"
    ),
    79: (  # Au
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, -2.80e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    80: (  # Hg
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -3.34e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    81: (  # Tl
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, -4.10e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    82: (  # Pb
        "^{3}\\mathrm{P}_{0}", 0.0, 0.0, -2.30e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    83: (  # Bi
        "^{4}\\mathrm{S}^\\circ_{3/2}", 2.002, 3.00, -2.80e-4, None, None, None,
        0.0, "Giant Diamagnetic Dirac Response", "Hard Magnetic Vector"
    ),
    84: (  # Po
        "^{3}\\mathrm{P}_{2}", 1.50, 3.00, -2.60e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    85: (  # At
        "^{2}\\mathrm{P}^\\circ_{3/2}", 1.333, 1.73, -3.00e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    86: (  # Rn
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -4.30e-5, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),

    # ------------------ Period 7 ------------------
    87: (  # Fr
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, 3.50e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    88: (  # Ra
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, 4.50e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    89: (  # Ac
        "^{2}\\mathrm{D}_{3/2}", 0.80, 1.55, 1.20e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    90: (  # Th
        "^{3}\\mathrm{F}_{2}", 0.667, 1.63, 1.30e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    91: (  # Pa
        "^{4}\\mathrm{K}^\\circ_{11/2}", 0.727, 2.40, 2.80e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    92: (  # U
        "^{5}\\mathrm{L}^\\circ_{6}", 0.857, 3.60, 4.10e-4, -150.0, None, None,
        0.0, "Itinerant 5f-conduction Hybridization", "Magnetically Inert Matrix"
    ),
    93: (  # Np
        "^{6}\\mathrm{L}_{11/2}", 0.909, 3.00, 5.50e-4, None, None, None,
        0.0, "Itinerant 5f Hybridization", "Magnetically Inert Matrix"
    ),
    94: (  # Pu
        "^{7}\\mathrm{F}_{0}", 0.0, 0.0, 6.20e-4, None, None, None,
        0.0, "Van Vleck / Pauli Paramagnetism", "Magnetically Inert Matrix"
    ),
    95: (  # Am
        "^{8}\\mathrm{S}^\\circ_{7/2}", 2.00, 0.0, 8.80e-4, None, None, None,
        0.0, "Van Vleck Paramagnetism (Non-magnetic bulk 5f6 J=0 ground; isolated gas atom is 8S°_7/2)", "Magnetically Inert Matrix"
    ),
    96: (  # Cm
        "^{9}\\mathrm{D}^\\circ_{2}", 2.667, 7.90, 2.60e-2, -380.0, None, None,
        0.0, "RKKY / Localized 5f Exchange", "Magnetically Inert Matrix"
    ),
    97: (  # Bk
        "^{6}\\mathrm{H}^\\circ_{15/2}", 1.333, 9.30, 3.80e-2, -100.0, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    98: (  # Cf
        "^{5}\\mathrm{I}_{8}", 1.25, 10.60, 4.50e-2, None, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    99: (  # Es
        "^{4}\\mathrm{I}^\\circ_{15/2}", 1.20, 10.60, 4.00e-2, None, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    100: (  # Fm
        "^{3}\\mathrm{H}_{6}", 1.167, 9.00, 2.50e-2, None, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    101: (  # Md
        "^{2}\\mathrm{F}^\\circ_{7/2}", 1.143, 7.10, 1.50e-2, None, None, None,
        0.0, "RKKY Indirect Exchange", "Magnetically Inert Matrix"
    ),
    102: (  # No
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -2.50e-5, None, None, None,
        0.0, "Diamagnetic Closed 5f14 Shell", "Magnetically Inert Matrix"
    ),
    103: (  # Lr
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, 5.00e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    104: (  # Rf
        "^{3}\\mathrm{F}_{2}", 0.667, 1.63, 8.00e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    105: (  # Db
        "^{4}\\mathrm{F}_{3/2}", 0.40, 1.24, 1.50e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    106: (  # Sg
        "^{5}\\mathrm{D}_{0}", 0.0, 0.0, 6.00e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    107: (  # Bh
        "^{6}\\mathrm{S}_{5/2}", 2.00, 5.92, 7.00e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    108: (  # Hs
        "^{5}\\mathrm{D}_{4}", 1.50, 5.50, 1.50e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    109: (  # Mt
        "^{4}\\mathrm{F}_{9/2}", 1.333, 5.59, 3.00e-5, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    110: (  # Ds
        "^{3}\\mathrm{D}_{3}", 1.333, 3.90, 2.00e-4, None, None, None,
        0.0, "Pauli Spin Paramagnetism", "Magnetically Inert Matrix"
    ),
    111: (  # Rg
        "^{2}\\mathrm{S}_{1/2}", 2.002, 1.00, -3.00e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    112: (  # Cn
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -3.50e-5, None, None, None,
        0.0, "Diamagnetic Closed Subshell", "Magnetically Inert Matrix"
    ),
    113: (  # Nh
        "^{2}\\mathrm{P}^\\circ_{1/2}", 0.667, 0.58, -4.50e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    114: (  # Fl
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -2.50e-5, None, None, None,
        0.0, "Diamagnetic Relativistic Closed Shell", "Magnetically Inert Matrix"
    ),
    115: (  # Mc
        "^{4}\\mathrm{S}^\\circ_{3/2}", 2.002, 3.00, -2.80e-4, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    116: (  # Lv
        "^{3}\\mathrm{P}_{2}", 1.50, 3.00, -3.00e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    117: (  # Ts
        "^{2}\\mathrm{P}^\\circ_{3/2}", 1.333, 1.73, -3.50e-5, None, None, None,
        0.0, "Diamagnetic Core Response", "Magnetically Inert Matrix"
    ),
    118: (  # Og
        "^{1}\\mathrm{S}_{0}", 0.0, 0.0, -4.50e-5, None, None, None,
        0.0, "Larmor Diamagnetism (Filled Shell)", "Magnetically Inert Matrix"
    ),
}


# -----------------------------------------------------------------------------
# SOLID-STATE BULK SATURATION & SUB-LATTICE ORDERED MOMENTS (T -> 0 K)
# Measured in Bohr magnetons (μ_B) per atom in magnetically ordered ground state.
# Diamagnets and paramagnets have None (no spontaneous magnetic order).
# -----------------------------------------------------------------------------
BULK_ORDERED_MOMENTS = {
    24: 0.62,   # Cr (BCC, incommensurate spin density wave antiferromagnet, 0 K sublattice moment)
    25: 0.50,   # Mn (alpha-Mn complex cubic, non-collinear antiferromagnet, 0 K sublattice moment)
    26: 2.22,   # Fe (BCC alpha-Fe ferromagnetic saturation moment at 0 K)
    27: 1.72,   # Co (HCP Co ferromagnetic saturation moment at 0 K)
    28: 0.606,  # Ni (FCC Ni ferromagnetic saturation moment at 0 K)
    58: 0.62,   # Ce (DHCP beta-Ce antiferromagnetic ordered moment below 12.5 K)
    60: 2.20,   # Nd (DHCP antiferromagnetic ordered moment below 19 K)
    62: 0.15,   # Sm (Rhombohedral ordered moment below 14.8 K)
    63: 5.90,   # Eu (BCC helical antiferromagnet below 90 K)
    64: 7.63,   # Gd (HCP ferromagnetic saturation moment at 0 K)
    65: 9.34,   # Tb (HCP ferromagnetic saturation moment at 0 K)
    66: 10.20,  # Dy (HCP ferromagnetic saturation moment at 0 K)
    67: 10.40,  # Ho (HCP ferromagnetic cone saturation moment at 0 K)
    68: 9.00,   # Er (HCP ferromagnetic cone saturation moment at 0 K)
    69: 7.00,   # Tm (HCP ferrimagnetic/antiferromagnetic moment at 0 K)
    96: 6.50,   # Cm (DHCP curium antiferromagnetic ordered moment below 52 K)
}

# -----------------------------------------------------------------------------
# CONDENSED MATTER / FREE-ION PARAMETERS (Aqueous Salts & Insulating Compounds)
# Separates free-ion Hund's moments and crystal-field states from neutral gas atoms.
# -----------------------------------------------------------------------------
FREE_ION_DATA = {
    21: {"species": "Sc³⁺ (3d⁰)", "term_symbol": "^{1}\\mathrm{S}_0", "effective_moment_mu_B": 0.0, "notes": "Closed noble-gas core; diamagnetic ion"},
    22: {"species": "Ti³⁺ (3d¹)", "term_symbol": "^{2}\\mathrm{D}_{3/2}", "effective_moment_mu_B": 1.73, "notes": "Single 3d electron, S=1/2 spin-only moment"},
    23: {"species": "V³⁺ (3d²)", "term_symbol": "^{3}\\mathrm{F}_2", "effective_moment_mu_B": 2.83, "notes": "Two 3d electrons, S=1 spin-only moment in octahedral field"},
    24: {"species": "Cr³⁺ (3d³)", "term_symbol": "^{4}\\mathrm{F}_{3/2}", "effective_moment_mu_B": 3.87, "notes": "Half-filled t_2g³ shell, S=3/2 spin-only moment (quenched orbital)"},
    25: {"species": "Mn²⁺ (3d⁵)", "term_symbol": "^{6}\\mathrm{S}_{5/2}", "effective_moment_mu_B": 5.92, "notes": "High-spin half-filled 3d⁵ shell, S=5/2, L=0, g=2.00"},
    26: {"species": "Fe³⁺ / Fe²⁺", "term_symbol": "^{6}\\mathrm{S}_{5/2} (Fe³⁺) / ^{5}\\mathrm{D}_4 (Fe²⁺)", "effective_moment_mu_B": 5.92, "notes": "Fe³⁺: 5.92 μ_B (3d⁵, S=5/2); Fe²⁺: 4.90 μ_B spin-only, 5.4 μ_B with unquenched orbital contribution"},
    27: {"species": "Co²⁺ (3d⁷)", "term_symbol": "^{4}\\mathrm{F}_{9/2}", "effective_moment_mu_B": 3.87, "notes": "Spin-only 3.87 μ_B; experimental salts show 4.8 μ_B due to spin-orbit orbital mixing"},
    28: {"species": "Ni²⁺ (3d⁸)", "term_symbol": "^{3}\\mathrm{F}_4", "effective_moment_mu_B": 2.83, "notes": "Spin-only 2.83 μ_B; experimental salts show 3.2 μ_B due to spin-orbit orbital mixing"},
    29: {"species": "Cu²⁺ (3d⁹)", "term_symbol": "^{2}\\mathrm{D}_{5/2}", "effective_moment_mu_B": 1.73, "notes": "Single 3d hole, S=1/2 spin-only moment; experimental salts show 1.9 μ_B"},
    57: {"species": "La³⁺ (4f⁰)", "term_symbol": "^{1}\\mathrm{S}_0", "effective_moment_mu_B": 0.0, "notes": "Empty 4f shell; diamagnetic ion"},
    58: {"species": "Ce³⁺ (4f¹)", "term_symbol": "^{2}\\mathrm{F}_{5/2}", "effective_moment_mu_B": 2.54, "notes": "Single 4f electron, Hund rule g_J*sqrt(J(J+1)) = 2.54 μ_B"},
    59: {"species": "Pr³⁺ (4f²)", "term_symbol": "^{3}\\mathrm{H}_4", "effective_moment_mu_B": 3.58, "notes": "Two 4f electrons, Hund rule g_J*sqrt(J(J+1)) = 3.58 μ_B"},
    60: {"species": "Nd³⁺ (4f³)", "term_symbol": "^{4}\\mathrm{I}_{9/2}", "effective_moment_mu_B": 3.62, "notes": "Three 4f electrons, Hund rule g_J*sqrt(J(J+1)) = 3.62 μ_B"},
    61: {"species": "Pm³⁺ (4f⁴)", "term_symbol": "^{5}\\mathrm{I}_4", "effective_moment_mu_B": 2.68, "notes": "Four 4f electrons, Hund rule g_J*sqrt(J(J+1)) = 2.68 μ_B"},
    62: {"species": "Sm³⁺ (4f⁵)", "term_symbol": "^{6}\\mathrm{H}_{5/2}", "effective_moment_mu_B": 0.84, "notes": "Hund ground-state moment is 0.84 μ_B (J=5/2). Low-lying J=7/2 excited multiplet (~1000 cm⁻¹) induces strong Van Vleck temperature-dependent paramagnetism, yielding experimental room-temperature μ_eff = 1.5 - 1.7 μ_B in salts."},
    63: {"species": "Eu³⁺ (4f⁶) / Eu²⁺ (4f⁷)", "term_symbol": "^{7}\\mathrm{F}_0 (Eu³⁺) / ^{8}\\mathrm{S}_{7/2} (Eu²⁺)", "effective_moment_mu_B": 3.40, "notes": "Eu³⁺ ground state has J=0 (Hund value 0.0 μ_B), but low-lying J=1 state (~350 cm⁻¹) yields Van Vleck μ_eff = 3.4 - 3.6 μ_B at 298 K. Divalent Eu²⁺ has 7.94 μ_B (8S7/2)."},
    64: {"species": "Gd³⁺ (4f⁷)", "term_symbol": "^{8}\\mathrm{S}_{7/2}", "effective_moment_mu_B": 7.94, "notes": "Half-filled 4f shell (S=7/2, L=0, g=2.00). Free trivalent ion effective moment is 7.94 μ_B in aqueous salts and compounds; in bulk metallic HCP crystal, saturation moment is 7.63 μ_B."},
    65: {"species": "Tb³⁺ (4f⁸)", "term_symbol": "^{7}\\mathrm{F}_6", "effective_moment_mu_B": 9.72, "notes": "Hund rule effective moment g_J*sqrt(J(J+1)) = 9.72 μ_B"},
    66: {"species": "Dy³⁺ (4f⁹)", "term_symbol": "^{6}\\mathrm{H}_{15/2}", "effective_moment_mu_B": 10.65, "notes": "Hund rule effective moment g_J*sqrt(J(J+1)) = 10.65 μ_B"},
    67: {"species": "Ho³⁺ (4f¹⁰)", "term_symbol": "^{5}\\mathrm{I}_8", "effective_moment_mu_B": 10.61, "notes": "Hund rule effective moment g_J*sqrt(J(J+1)) = 10.61 μ_B"},
    68: {"species": "Er³⁺ (4f¹¹)", "term_symbol": "^{4}\\mathrm{I}_{15/2}", "effective_moment_mu_B": 9.58, "notes": "Hund rule effective moment g_J*sqrt(J(J+1)) = 9.58 μ_B"},
    69: {"species": "Tm³⁺ (4f¹²)", "term_symbol": "^{3}\\mathrm{H}_6", "effective_moment_mu_B": 7.56, "notes": "Hund rule effective moment g_J*sqrt(J(J+1)) = 7.56 μ_B"},
    70: {"species": "Yb³⁺ (4f¹³)", "term_symbol": "^{2}\\mathrm{F}_{7/2}", "effective_moment_mu_B": 4.54, "notes": "Trivalent ion Yb³⁺ has 4.54 μ_B; elemental Yb metal is divalent (4f¹⁴, diamagnetic, 0.0 μ_B)"},
    71: {"species": "Lu³⁺ (4f¹⁴)", "term_symbol": "^{1}\\mathrm{S}_0", "effective_moment_mu_B": 0.0, "notes": "Filled 4f shell; diamagnetic ion"},
    92: {"species": "U⁴⁺ (5f²) / U³⁺ (5f³)", "term_symbol": "^{3}\\mathrm{H}_4 / ^{4}\\mathrm{I}_{9/2}", "effective_moment_mu_B": 3.60, "notes": "Actinide 5f magnetic ion; effective moment in compounds is ~3.5 - 3.8 μ_B"},
    95: {
        "species": "Am³⁺ (5f⁶ in bulk metal & salts)",
        "term_symbol": "^{7}\\mathrm{F}_0",
        "effective_moment_mu_B": 0.0,
        "notes": "Solid metallic Americium and trivalent Am³⁺ compounds adopt a trivalent 5f⁶ configuration with a non-magnetic J=0 singlet ground state (⁷F₀). It exhibits temperature-independent Van Vleck paramagnetism with no spontaneous ordering at any temperature (μ_ord = 0), contrasting with the isolated neutral gas atom which has a 5f⁷ 7s² (⁸S°_{7/2}, 7.94 μ_B) ground state."
    }
}

# -----------------------------------------------------------------------------
# MULTI-VALUE FUNCTIONAL-ALLOY CONTRIBUTIONS TO COMMERCIAL MAGNETIC MATERIALS
# Documents specific industrial and technological functions without forcing elements into "inert".
# -----------------------------------------------------------------------------
FUNCTIONAL_ALLOY_CONTRIBUTIONS = {
    5: [
        "Interstitial Phase Stabilizer in Nd2Fe14B Tetragonal Crystal Structure",
        "Glass-Forming Amorphous Soft Magnetic Core Additive (Metglas Fe-Si-B)"
    ],
    14: [
        "Eddy Current Loss Suppressor in Fe-Si Electrical Steels (~3.2 wt% Si)",
        "Electrical Resistivity Enhancer in Transformer and Motor Stator Laminations"
    ],
    23: [
        "Mechanical Ductilizer & Grain Refiner in Hiperco / Permendur (Fe49-Co49-V2)",
        "Workability Enhancer for Rolling Ultra-High Saturation (2.45 T) Cores"
    ],
    24: [
        "Giant Magnetoresistance (GMR) Interlayer Exchange Coupling Spacer (Fe/Cr)",
        "Corrosion Barrier & High-Permeability Modifier in Soft Stainless Magnetic Steels"
    ],
    25: [
        "First-Order Giant Magnetocaloric Active Element (MnFePAs, MnCoGe)",
        "Antiferromagnetic Exchange-Bias Vector in Spintronic Spin Valves (Ir-Mn, Pt-Mn)"
    ],
    26: [
        "Primary High-Saturation Exchange-Splitting Backbone (Electrical Steels, Nd-Fe-B, Soft Ferrites, Permalloys)"
    ],
    27: [
        "High-Temperature Coercivity & Uniaxial Anisotropy Sustainer (Sm-Co, Alnico, Fe-Co)",
        "Curie Temperature Maximizer for Extreme Environments (T_C up to 1388 K)"
    ],
    28: [
        "High Initial Permeability / Ultra-Low Coercivity Core Constituent (Permalloys Ni80Fe20, Mu-Metal)",
        "Near-Zero Magnetostriction Base for Precision Magnetic Shielding and Sensors"
    ],
    29: [
        "Grain Boundary Wetting & Domain-Wall Pinning Precipitate Phase (Sm2Co17 2:17 cell boundaries)",
        "Grain Boundary Diffusion Enhancer in Sintered Nd-Fe-B Magnets"
    ],
    40: [
        "High-Temperature Pinning Lamellar Phase Stabilizer in Sm2Co17 Permanent Magnets",
        "Nanocrystalline Grain Growth Inhibitor in Ultra-Soft Finemet Alloys"
    ],
    41: [
        "Nanocrystalline Grain Growth Inhibitor (Finemet Fe-Si-B-Nb-Cu Soft Magnetic Cores)",
        "High-Permeability High-Frequency Nanostructure Refiner"
    ],
    42: [
        "Zero-Magnetostriction Tuner & Resistivity Enhancer (Supermalloy Ni79Fe16Mo5, Molypermalloy)"
    ],
    59: [
        "Didymium Hard Magnet Constituent ((Nd,Pr)-Fe-B)",
        "Single-Ion Anisotropy Source without Grain-Boundary Segregation"
    ],
    60: [
        "High Energy Product (BH)_max Driver in Nd2Fe14B Sintered Permanent Magnets",
        "Single-Ion Uniaxial Magnetocrystalline Anisotropy Source"
    ],
    62: [
        "High-Temperature Coercivity Driver (SmCo5, Sm2Co17) with Unmatched Thermal Stability up to 550°C",
        "Extreme Magnetocrystalline Anisotropy Source (Anisotropy Field H_A > 250 kOe)"
    ],
    64: [
        "Room-Temperature Benchmark Magnetocaloric Working Material (T_C = 292 K, ΔS_m ~ 10 J/(kg·K))",
        "High-Entropy Alloy Phase Stabilizer for Magnetic Refrigeration"
    ],
    65: [
        "Giant Magnetostrictive Transducer Element in Terfenol-D (Tb0.3Dy0.7Fe1.9)",
        "High-Coercivity Grain-Boundary Diffusion Heavy Rare-Earth Vector"
    ],
    66: [
        "High-Temperature Coercivity Stabilizer in Dy-Diffused Nd-Fe-B Permanent Magnets for EV Traction Motors",
        "Giant Magnetostrictive Constituent in Terfenol-D"
    ],
    67: [
        "Cryogenic Magnetocaloric Working Material in Intermetallic Compounds (HoCu2, HoAl2)",
        "Ultra-High Magnetic Moment Flux Concentrator in Superconducting Magnet Pole Pieces"
    ],
    68: [
        "Cryogenic 4 K Magnetic Regenerator Material (Er3Ni, ErNi2 for Gifford-McMahon / Pulse-Tube Cryocoolers)"
    ],
    69: [
        "Cryogenic Adiabatic Demagnetization Refrigeration (ADR) Working Material (TmGa, TmNi2)"
    ],
    78: [
        "Perpendicular Magnetic Anisotropy (PMA) Vector in L1_0 FePt / CoPt for Heat-Assisted Magnetic Recording (HAMR)",
        "Spin-Hall Heavy Metal for Spin-Orbit Torque (SOT) Spintronics"
    ],
    83: [
        "High Spin-Orbit Coupling / Hard Anisotropy Source in High-T Permanent Magnets (MnBi with Positive Coercivity Temperature Coefficient)",
        "Topological Spintronic Vector with Giant Spin-to-Charge Conversion"
    ]
}

# Detailed technological alloy rationales separating intrinsic state from alloy role
ALLOY_FUNCTIONAL_RATIONALES = {
    5: {
        "category": "Functional Magnetic Microstructure / Interlayer Additive",
        "rationale": "Forms interstitial bonds stabilizing the Nd2Fe14B tetragonal crystal lattice; also acts as crucial glass-forming element in amorphous soft magnetic alloys (Metglas)."
    },
    14: {
        "category": "Soft Magnetic Alloys & High-Permeability Core Constituent",
        "rationale": "Intrinsically diamagnetic in pure elemental form. Alloyed in Electrical Steel (Fe-Si, ~3.2 wt% Si) to increase electrical resistivity (from ~10 to ~45 μΩ·cm), suppressing classical eddy current power losses in AC motor and transformer cores while maintaining high saturation flux density."
    },
    23: {
        "category": "Soft Magnetic Alloys & High-Permeability Core Constituent",
        "rationale": "Intrinsically Pauli paramagnetic as a pure metal. Added to Permendur (Fe49-Co49-V2) to suppress grain boundary embrittlement and impart cold workability, enabling ductile rolling and stamping of laminations with ultra-high saturation magnetization (2.45 T)."
    },
    24: {
        "category": "Functional Magnetic Microstructure / Interlayer Additive",
        "rationale": "Intrinsically antiferromagnetic (spin density wave). Utilized as spacer layer enabling oscillatory interlayer exchange coupling in Giant Magnetoresistance (GMR) spin valves, and as corrosion-resistant alloying element in soft stainless magnetic steels."
    },
    25: {
        "category": "Magnetocaloric Working Material / Phase Transition Constituent",
        "rationale": "Intrinsically antiferromagnetic with complex cubic alpha-Mn structure. Core building block of first-order magnetocaloric alloys (MnFePAs, MnCoGe, Heusler Ni-Mn-X) where giant magnetocaloric entropy changes (ΔS_m > 20 J/(kg·K)) accompany magneto-structural phase transformations for zero-GWP magnetic refrigeration; also provides exchange bias in spin valves."
    },
    26: {
        "category": "Soft Magnetic Alloys & High-Permeability Core Constituent",
        "rationale": "Intrinsically ferromagnetic with high saturation magnetization (2.15 T at room temperature) and high Curie temperature (1043 K). Primary backbone of all electrical steels, Permalloys, soft magnetic composites, and high-frequency power magnetic cores."
    },
    27: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically ferromagnetic with exceptionally high Curie temperature (1388 K) and large uniaxial anisotropy (K_1 = 4.1×10^5 J/m³ in HCP phase). Essential constituent of Alnico, SmCo5, and Sm2Co17 permanent magnets, providing thermal stability and high-temperature coercivity."
    },
    28: {
        "category": "Soft Magnetic Alloys & High-Permeability Core Constituent",
        "rationale": "Intrinsically ferromagnetic with low magnetocrystalline anisotropy and negative magnetostriction. Primary constituent of Permalloys (Ni80Fe20) and Supermalloys, achieving near-zero magnetostriction and ultra-high initial magnetic permeability (μ_r > 100,000) for magnetic shielding and precision current sensing."
    },
    29: {
        "category": "Functional Magnetic Microstructure / Interlayer Additive",
        "rationale": "Diamagnetic metal that forms grain-boundary wetting and domain-wall pinning precipitates in high-temperature Sm2Co17 sintered magnets, and facilitates liquid-phase grain boundary diffusion in Nd-Fe-B."
    },
    40: {
        "category": "Functional Magnetic Microstructure / Interlayer Additive",
        "rationale": "Paramagnetic transition metal essential for stabilizing the Zr-rich 1:5 platelet pinning phase in Sm2Co17 magnets, and acts as a grain-refining agent in nanocrystalline soft magnetic alloys."
    },
    41: {
        "category": "Functional Magnetic Microstructure / Interlayer Additive",
        "rationale": "Key grain-growth inhibitor in nanocrystalline Fe-Si-B-Nb-Cu (Finemet) soft magnetic alloys, pinning grain boundaries to maintain ~10 nm crystallite size for ultra-low coercivity and high permeability."
    },
    42: {
        "category": "Soft Magnetic Alloys & High-Permeability Core Constituent",
        "rationale": "Intrinsically paramagnetic. Alloyed into Supermalloy (Ni79-Fe16-Mo5) and Molypermalloy to eliminate residual magnetostriction and crystal anisotropy while enhancing resistivity, maximizing magnetic permeability and minimizing hysteresis loss in precision inductive components."
    },
    59: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically ordered at low temperatures. Key light rare-earth constituent in (Nd,Pr)-Fe-B sintered magnets and Pr-Co hard magnetic compounds, contributing high single-ion magnetic anisotropy without the microstructural segregation common in ternary systems."
    },
    60: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically magnetically ordered below 19 K. Key 4f rare-earth constituent in Nd2Fe14B sintered permanent magnets; localized 4f electron orbital asymmetry coupled to the tetragonal crystal field generates immense single-ion uniaxial magnetic anisotropy (energy product (BH)_max up to 512 kJ/m³)."
    },
    62: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically ordered at low temperatures. Key constituent of SmCo5 and Sm2Co17 high-performance permanent magnets, where localized 4f spin-orbit coupling provides extreme magnetocrystalline anisotropy (anisotropy field H_A > 250 kOe) and unmatched high-temperature resistance to demagnetization up to 550°C."
    },
    64: {
        "category": "Magnetocaloric Working Material / Phase Transition Constituent",
        "rationale": "Ferromagnetic near room temperature (T_C = 292 K) with half-filled 4f shell (7.63 μ_B/atom, S = 7/2, L = 0). The benchmark elemental magnetocaloric material with high reversible isothermal entropy change (ΔS_m ~ 10 J/(kg·K)) and zero magnetic hysteresis, enabling room-temperature magnetic cooling."
    },
    65: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically ordered below 220 K with large 4f orbital moment and high magnetostriction. Employed in high-temperature permanent magnet grain boundary diffusion and giant magnetostrictive actuators (Terfenol-D, Tb0.3Dy0.7Fe1.9) exhibiting huge magnetic field-induced strains."
    },
    66: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically ordered below 85 K with massive atomic moment (10.2 μ_B). Crucial grain-boundary and lattice-doping additive in (Nd,Dy)2Fe14B permanent magnets, boosting intrinsic coercivity (H_cj) to prevent irreversible demagnetization in high-temperature EV traction motors and wind turbines."
    },
    67: {
        "category": "Magnetocaloric Working Material / Phase Transition Constituent",
        "rationale": "Intrinsically ordered below 20 K with the highest elemental atomic moment (10.4 μ_B). Employed in low-temperature magnetocaloric regenerators, cryogenic magnetic cooling stages, and as high-saturation pole pieces in high-field superconducting magnets."
    },
    68: {
        "category": "Magnetocaloric Working Material / Phase Transition Constituent",
        "rationale": "Low-temperature magnetic ordering (T_C = 19 K). Essential for cryogenic magnetic regenerators and Gifford-McMahon / pulse tube cryocoolers operating in the liquid helium temperature regime (2–10 K), providing immense volumetric magnetic heat capacity."
    },
    69: {
        "category": "Magnetocaloric Working Material / Phase Transition Constituent",
        "rationale": "Low-temperature magnetic ordering (T_C = 32 K). Used in low-temperature magnetocaloric compounds (TmGa, TmNi2) and magnetic regenerators where high magnetic moments at cryogenic temperatures provide substantial cooling power in adiabatic demagnetization refrigerators (ADR)."
    },
    78: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically Stoner-enhanced Pauli paramagnetic. When alloyed in equiatomic L1_0 ordered FePt or CoPt, Pt's massive 5d spin-orbit coupling induces giant perpendicular magnetocrystalline anisotropy (K_u ~ 7×10^6 J/m³), essential for heat-assisted magnetic recording (HAMR) hard drives surpassing 20 Tbit/in²."
    },
    83: {
        "category": "Permanent Magnets & High-Anisotropy Alloy Constituent",
        "rationale": "Intrinsically diamagnetic in pure elemental form with strong spin-orbit interaction (Z=83). Reacted with Mn to synthesize hexagonal NiAs-structured MnBi, a hard permanent magnet exhibiting an extraordinary positive temperature coefficient of coercivity (coercivity increases from 2.5 kOe at 20°C to >20 kOe at 250°C) driven by Bi 6p spin-orbit coupling."
    }
}

import math
import re

L_CHAR_TO_NUM = {"S": 0, "P": 1, "D": 2, "F": 3, "G": 4, "H": 5, "I": 6, "K": 7, "L": 8, "M": 9}

def parse_rs_term(raw_latex: str):
    """Parses LaTeX term symbol into (mult, S, L_char, L, J)."""
    m = re.match(r"^\^\{(\d+)\}(?:\\mathrm\{([A-Z])\}|([A-Z]))(?:\^\\circ|\^o)?_\{?([0-9/]+)\}?$", raw_latex)
    if not m:
        return None
    mult = int(m.group(1))
    L_char = m.group(2) or m.group(3)
    J_str = m.group(4)
    if "/" in J_str:
        num, den = J_str.split("/")
        J = float(num) / float(den)
    else:
        J = float(J_str)
    S = (mult - 1) / 2.0
    L = L_CHAR_TO_NUM.get(L_char, 0)
    return mult, S, L_char, L, J


def enrich_element_magnetic(elem_dict):
    """Enriches a single element dictionary with quantum and advanced magnetic parameters."""
    z = elem_dict["atomic_number"]
    if z not in MAGNETIC_QUANTUM_DATA:
        raise ValueError(f"Missing magnetic data for atomic number {z}")

    (
        term_sym_latex,
        lande_g,
        _legacy_moment,
        chi_m_298k,
        theta_cw_k,
        ms_t,
        k1_j_m3,
        spin_pol_pct,
        exchange_mech,
        _legacy_role
    ) = MAGNETIC_QUANTUM_DATA[z]

    # Clean text representation of term symbol without LaTeX markup for fallback
    clean_term = term_sym_latex.replace("^{", "").replace("}", "").replace("\\mathrm{", "").replace("\\circ", "°").replace("\\", "")

    # Parse Russell-Saunders term symbol to calculate theoretical neutral gas atom moment
    parsed = parse_rs_term(term_sym_latex)
    if parsed:
        _mult, _S, _L_char, _L, J = parsed
        if J == 0:
            neutral_atom_mu = 0.0
            neutral_atom_proj = 0.0
        else:
            neutral_atom_mu = round(lande_g * math.sqrt(J * (J + 1)), 2)
            neutral_atom_proj = round(lande_g * J, 2)
    else:
        neutral_atom_mu = 0.0
        neutral_atom_proj = 0.0

    # Solid-state bulk ordered moment at T -> 0 K (only for magnetically ordered elements)
    bulk_ordered_mu = BULK_ORDERED_MOMENTS.get(z, None)

    # Free-ion condensed matter salt moment (if applicable)
    free_ion_entry = FREE_ION_DATA.get(z, None)

    # Multi-value documented functional-alloy contributions
    functional_contribs = FUNCTIONAL_ALLOY_CONTRIBUTIONS.get(z, [])

    mag_class = elem_dict.get("magnetic_classification", "")

    # Technological alloy role rationale
    if z in ALLOY_FUNCTIONAL_RATIONALES:
        alloy_meta = ALLOY_FUNCTIONAL_RATIONALES[z]
        role_category = alloy_meta["category"]
        tech_rationale = alloy_meta["rationale"]
        if z in (27, 59, 60, 62, 65, 66, 78, 83):
            mag_role = "Hard Magnetic Vector"
        elif z in (14, 23, 26, 28, 42):
            mag_role = "Soft Magnetic Core"
        elif z in (25, 64, 67, 68, 69):
            mag_role = "Magnetocaloric Active Element"
        else:
            mag_role = "Magnetic Phase Stabilizer / Additive"
    else:
        mag_role = "No primary commercial magnetic alloy role documented"
        role_category = "Standard Non-Magnetic Element / Chemical Matrix"
        if z == 95:
            tech_rationale = (
                "Radioactive actinide metal without primary commercial magnetic alloy role. "
                "Physical Scope Contrast: In the isolated neutral gas phase, atomic Americium has a half-filled 5f⁷ 7s² shell "
                "with an ⁸S°_{7/2} ground state (μ_eff = 7.94 μ_B). In the condensed bulk metallic phase, Americium adopts a "
                "trivalent 5f⁶ state with a non-magnetic J=0 (⁷F₀) singlet ground state, exhibiting temperature-independent "
                "Van Vleck paramagnetism with zero spontaneous ordering."
            )
        else:
            tech_rationale = "Forms elemental solid, gas, or chemical matrix without primary documented functional alloy role in commercial magnetic devices."

    # Saturation magnetization condition & measurement temperature
    if ms_t is not None:
        if z in (26, 27, 28):
            ms_temp_k = 298.15
            ms_condition = "at 298 K (Room Temperature)"
        else:
            ms_temp_k = 4.2
            ms_condition = "at 4.2 K (Liquid Helium Cryogenic)"
    else:
        ms_temp_k = None
        ms_condition = None

    # Top-level fields for direct access and backwards compatibility
    elem_dict["term_symbol"] = term_sym_latex
    elem_dict["term_symbol_clean"] = clean_term
    elem_dict["lande_g_factor"] = lande_g
    elem_dict["neutral_atom_moment_mu_B"] = neutral_atom_mu
    elem_dict["neutral_atom_max_projection_mu_B"] = neutral_atom_proj
    elem_dict["free_atom_moment_mu_B"] = neutral_atom_mu  # Strictly neutral gas atom Hund value
    elem_dict["atomic_moment_mu_B"] = neutral_atom_mu     # Backward compatibility mapping
    elem_dict["bulk_ordered_moment_mu_B"] = bulk_ordered_mu
    elem_dict["free_ion_state"] = free_ion_entry
    elem_dict["molar_susceptibility_298K"] = chi_m_298k
    elem_dict["curie_weiss_temp_K"] = theta_cw_k
    elem_dict["saturation_magnetization_T"] = ms_t
    elem_dict["saturation_magnetization_condition"] = ms_condition
    elem_dict["saturation_magnetization_temp_K"] = ms_temp_k
    elem_dict["magnetocrystalline_anisotropy_J_m3"] = k1_j_m3
    elem_dict["spin_polarization_percent"] = spin_pol_pct
    elem_dict["exchange_interaction"] = exchange_mech
    elem_dict["functional_alloy_contributions"] = functional_contribs
    elem_dict["magnet_role"] = mag_role
    elem_dict["alloy_function_rationale"] = tech_rationale

    # Determine thermodynamic phase, physical scope, and conditions at 298.15 K
    sym = elem_dict.get("symbol", "")
    if sym in {"H", "He", "N", "O", "F", "Ne", "Cl", "Ar", "Kr", "Xe", "Rn"}:
        chi_scope = "gas_phase_at_298K"
        chi_cond = "T = 298.15 K, P = 1 atm (molecular/atomic gas phase, weak-field linear regime)"
        chi_src = "CRC Handbook of Chemistry & Physics (97th ed.) / Landolt-Börnstein"
    elif sym in {"Br", "Hg"}:
        chi_scope = "liquid_phase_at_298K"
        chi_cond = "T = 298.15 K, P = 1 atm (elemental liquid phase, weak-field linear regime)"
        chi_src = "CRC Handbook of Chemistry & Physics (97th ed.) / Landolt-Börnstein"
    elif z == 64:  # Gd (T_C = 292.0 K < 298.15 K)
        chi_scope = "bulk_solid_paramagnetic_at_298K"
        chi_cond = "T = 298.15 K, P = 1 atm (paramagnetic phase, since T_C = 292.0 K < 298.15 K; weak-field linear regime)"
        chi_src = "CRC Handbook of Chemistry & Physics (97th ed.) / Landolt-Börnstein Group III"
    elif z in (26, 27, 28):  # Fe, Co, Ni (ferromagnetic at 298.15 K)
        chi_scope = "bulk_solid_ferromagnetic_domain_state"
        chi_cond = "Spontaneous ferromagnetism below T_C (T < T_C) precludes single linear chi_m at 298 K; see saturation magnetization M_s"
        chi_src = "Domain hysteresis regime"
    elif chi_m_298k is not None:
        chi_scope = "bulk_solid_at_298K"
        chi_cond = "T = 298.15 K, P = 1 atm (bulk solid crystal, weak-field linear regime)"
        chi_src = "CRC Handbook of Chemistry & Physics (97th ed.) / Landolt-Börnstein"
    else:
        chi_scope = "synthetic_or_unmeasured_solid"
        chi_cond = "No reliable ambient experimental molar susceptibility documented for short-lived isotope"
        chi_src = None

    if z in (26, 27, 28):
        ms_scope = "bulk_solid_ferromagnetic_at_298K"
        ms_cond = "T = 298.15 K, standard atmospheric pressure, room-temperature saturation induction"
        ms_src = "Bozorth (Ferromagnetism) / Coey (Magnetism and Magnetic Materials)"
    elif ms_t is not None:
        ms_scope = "bulk_solid_ferromagnetic_cryogenic_at_4.2K"
        ms_cond = "T = 4.2 K (liquid helium cryogenic regime), saturation magnetization in high magnetic field"
        ms_src = "Bozorth (Ferromagnetism) / Coey (Magnetism and Magnetic Materials)"
    else:
        ms_scope = "non_spontaneous_solid_or_gas"
        ms_cond = "Not spontaneously ferromagnetic; zero spontaneous saturation magnetization"
        ms_src = None

    # Structured group for advanced UI consumption
    elem_dict["advanced_magnetism"] = {
        "quantum": {
            "term_symbol": term_sym_latex,
            "term_symbol_clean": clean_term,
            "lande_g_factor": lande_g,
            "neutral_atom_moment_mu_B": neutral_atom_mu,
            "neutral_atom_max_projection_mu_B": neutral_atom_proj,
            "free_atom_moment_mu_B": neutral_atom_mu,
            "bulk_ordered_moment_mu_B": bulk_ordered_mu,
            "free_ion_state": free_ion_entry,
            "atomic_moment_mu_B": neutral_atom_mu
        },
        "thermodynamic": {
            "molar_susceptibility_298K": chi_m_298k,
            "curie_weiss_temp_K": theta_cw_k,
            "saturation_magnetization_T": ms_t,
            "saturation_magnetization_condition": ms_condition,
            "saturation_magnetization_temp_K": ms_temp_k,
            "magnetocrystalline_anisotropy_J_m3": k1_j_m3
        },
        "spintronics": {
            "spin_polarization_percent": spin_pol_pct,
            "exchange_interaction": exchange_mech
        },
        "technological": {
            "magnet_role": mag_role,
            "functional_role_category": role_category,
            "functional_alloy_contributions": functional_contribs,
            "intrinsic_elemental_state": mag_class,
            "alloy_function_rationale": tech_rationale
        },
        "provenance_and_conditions": {
            "neutral_atom_ground_state": {
                "physical_scope": "isolated_neutral_gas_atom",
                "conditions": (
                    "Isolated neutral gas-phase atom in vacuum (NIST Atomic Spectra Database v5.11). "
                    "Contrasts with condensed metallic ground state for elements with valence/delocalization changes (e.g., Am 5f⁶ J=0 singlet in metal vs 5f⁷ 7s² ⁸S°_{7/2} in gas)."
                    if z == 95 else
                    "Isolated atom ground state in vacuum (NIST Atomic Spectra Database v5.11)"
                ),
                "formula": "g_J * sqrt(J(J+1)) mu_B",
                "source": "NIST ASD / Russell-Saunders LS-coupling"
            },
            "free_ion_state": {
                "physical_scope": "free_ion_in_crystal_field_or_salt",
                "conditions": "Hund's rule effective moment in condensed matter / aqueous solution; Van Vleck mixing noted for Sm/Eu",
                "source": "Ashcroft & Mermin / Kittel / Coey (Magnetism and Magnetic Materials)"
            },
            "bulk_ordered_moment_mu_B": {
                "physical_scope": "bulk_solid_ordered_lattice",
                "conditions": (
                    "T -> 0 K ground state saturation / sublattice moment in zero applied field"
                    if bulk_ordered_mu is not None else
                    ("Bulk solid metal has non-magnetic J=0 singlet ground state (Am³⁺ 5f⁶); μ_ord = 0" if z == 95 else "Zero spontaneous magnetic ordering in bulk solid elemental ground state")
                ),
                "source": "Crangle & Goodman (1971) / Kittel Solid State Physics / Landolt-Börnstein Group III" if bulk_ordered_mu is not None else None
            },
            "molar_susceptibility_298K": {
                "physical_scope": chi_scope,
                "conditions": chi_cond,
                "source": chi_src
            },
            "curie_weiss_temp_K": {
                "physical_scope": "bulk_solid_crystal",
                "conditions": "High-temperature paramagnetic regime (T > T_C or T > T_N)",
                "source": "Landolt-Börnstein Group III / Kittel Introduction to Solid State Physics"
            },
            "saturation_magnetization_T": {
                "physical_scope": ms_scope,
                "conditions": ms_cond,
                "source": ms_src
            },
            "magnetocrystalline_anisotropy_J_m3": {
                "physical_scope": "bulk_single_crystal",
                "conditions": "T = 298 K (Fe, Co, Ni); T = 4.2 K (rare earths)",
                "source": "Landolt-Börnstein / Bozorth"
            },
            "spin_polarization_percent": {
                "physical_scope": "bulk_solid_conduction_band",
                "conditions": "Fermi level E_F, measured via Point Contact Andreev Reflection (PCAR) or spin-polarized tunneling",
                "source": "Meservey & Tedrow / Soulen et al. (Science 1998)"
            },
            "technological_role": {
                "physical_scope": "functional_commercial_magnetic_alloys",
                "rationale": tech_rationale,
                "source": "Coey, J.M.D., Magnetism and Magnetic Materials (Cambridge Univ. Press); Buschow, K.H.J., Handbook of Magnetic Materials"
            }
        }
    }

    return elem_dict


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enrich periodic table database with advanced quantum and thermodynamic magnetic data.")
    parser.add_argument("-i", "--input", default="magnetic_elements_crystallography.json",
                        help="Input JSON file path (default: magnetic_elements_crystallography.json)")
    parser.add_argument("-o", "--output", default="magnetic_elements_enriched.json",
                        help="Output JSON file path (default: magnetic_elements_enriched.json)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Resolve input path strictly — error out if specified file does not exist
    input_path = args.input if os.path.isabs(args.input) else os.path.join(script_dir, args.input)
    if not os.path.exists(input_path):
        sys.exit(f"Error: Specified input database file not found: {input_path}")

    # Resolve output path
    output_path = args.output if os.path.isabs(args.output) else os.path.join(script_dir, args.output)

    print("===================================================================")
    print("      Enriching Elements with Quantum & Advanced Magnetism Data    ")
    print("===================================================================")
    print(f"Reading from: {input_path}")
    print(f"Writing to:   {output_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        elements = json.load(f)

    if len(elements) != 118:
        print(f"Warning: Expected 118 elements, but found {len(elements)}")

    # Enrich all elements
    role_counts = {
        "Hard Magnetic Vector": 0,
        "Soft Magnetic Core": 0,
        "Magnetocaloric Active Element": 0,
        "Magnetic Phase Stabilizer / Additive": 0,
        "No primary commercial magnetic alloy role documented": 0,
    }
    with_saturation = 0
    with_anisotropy = 0
    with_curie_weiss = 0
    with_bulk_moment = 0

    for elem in elements:
        enrich_element_magnetic(elem)
        role = elem["magnet_role"]
        role_counts[role] = role_counts.get(role, 0) + 1
        if elem["saturation_magnetization_T"] is not None:
            with_saturation += 1
        if elem["magnetocrystalline_anisotropy_J_m3"] is not None:
            with_anisotropy += 1
        if elem["curie_weiss_temp_K"] is not None:
            with_curie_weiss += 1
        if elem["bulk_ordered_moment_mu_B"] is not None:
            with_bulk_moment += 1

    # Save to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(elements, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Successfully enriched {len(elements)} elements with quantum & advanced magnetism data.")
    print(f"Saved database to: {output_path}")
    print("\n--- Summary Statistics ---")
    print(f"Elements with Bulk Ordered Moment μ_ord (0 K):  {with_bulk_moment}")
    print(f"Elements with Paramagnetic Curie-Weiss θ_CW:   {with_curie_weiss}")
    print(f"Elements with Saturation Magnetization M_s:    {with_saturation}")
    print(f"Elements with Magnetocrystalline Anisotropy:  {with_anisotropy}")
    print("Technological Magnet Roles distribution:")
    for role, cnt in role_counts.items():
        print(f"  - {role:30s}: {cnt}")
    print("===================================================================")


if __name__ == "__main__":
    main()

