#!/usr/bin/env python3
"""
validate_database.py

Comprehensive Scientific and Structural Validation Suite for Magnetic Periodic Table Data.
Verifies:
  1. Atomic numbers (strictly 1 to 118, unique, continuous, no gaps)
  2. Symbols and names (strictly matching independent IUPAC standard for all 118 elements)
  3. Electronic configurations (NO ellipses '...', full electron subshell sum strictly == Z)
  4. USGS Critical Minerals:
     - Independent reference mapping of all 50 commodities (2022 Final List)
     - Element-by-element verification of 'usgs_critical_mineral' flag and 'usgs_commodity_name'
  5. Radioactive elements (strictly 37: Tc (43), Pm (61), and all Z >= 84)
  6. Magnetic classifications & transition temperatures consistency:
     - Ferromagnet (T_C >= 290 K) must have T_C >= 290
     - Antiferromagnet (T_N >= 290 K) must have T_N >= 290
     - Low-temperature ordering must have T < 290
     - Paramagnets / Diamagnets must have transition_temp == None
  7. Materials Project Ground States:
     - Audited mapping of chemical formula to verified elemental material_id
     - Valid URL construction (https://materialsproject.org/materials/mp-XXXX)
     - No mismatched IDs belonging to different elements
  8. Crystallography completeness (space group 1..230, positive lattice parameters a,b,c,alpha,beta,gamma)
  9. Advanced quantum & macroscopic magnetism:
     - Term symbol (valid non-empty string, Russell-Saunders notation)
     - Landé g-factor (0.0 <= g_J <= 5.0, consistent with LS coupling)
     - Neutral gas-atom effective moments and bulk-solid saturation moments strictly distinguished
     - Plausible Curie-Weiss temperatures (-2000 K <= theta_CW <= 2500 K)
     - Plausible saturation magnetization (0.05 T <= M_s <= 4.0 T across elements; <= 3.5 T for RT ferromagnets)
     - Magnetic susceptibility sign consistency (chi_m < 0 for diamagnets, chi_m > 0 for paramagnets)
     - Spin polarization (0 <= P <= 100%)
     - Technological roles: 8 Hard, 5 Soft, 5 Magnetocaloric, 5 Additive, 95 Standard
  10. Property-level provenance and physical plausibility ranges.
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path


# =========================================================================
# INDEPENDENT SCIENTIFIC REFERENCE STANDARDS
# =========================================================================

# IUPAC standard elements (Z: (Symbol, Name))
IUPAC_STANDARD_ELEMENTS = {
    1: ("H", "Hydrogen"), 2: ("He", "Helium"), 3: ("Li", "Lithium"), 4: ("Be", "Beryllium"),
    5: ("B", "Boron"), 6: ("C", "Carbon"), 7: ("N", "Nitrogen"), 8: ("O", "Oxygen"),
    9: ("F", "Fluorine"), 10: ("Ne", "Neon"), 11: ("Na", "Sodium"), 12: ("Mg", "Magnesium"),
    13: ("Al", "Aluminum"), 14: ("Si", "Silicon"), 15: ("P", "Phosphorus"), 16: ("S", "Sulfur"),
    17: ("Cl", "Chlorine"), 18: ("Ar", "Argon"), 19: ("K", "Potassium"), 20: ("Ca", "Calcium"),
    21: ("Sc", "Scandium"), 22: ("Ti", "Titanium"), 23: ("V", "Vanadium"), 24: ("Cr", "Chromium"),
    25: ("Mn", "Manganese"), 26: ("Fe", "Iron"), 27: ("Co", "Cobalt"), 28: ("Ni", "Nickel"),
    29: ("Cu", "Copper"), 30: ("Zn", "Zinc"), 31: ("Ga", "Gallium"), 32: ("Ge", "Germanium"),
    33: ("As", "Arsenic"), 34: ("Se", "Selenium"), 35: ("Br", "Bromine"), 36: ("Kr", "Krypton"),
    37: ("Rb", "Rubidium"), 38: ("Sr", "Strontium"), 39: ("Y", "Yttrium"), 40: ("Zr", "Zirconium"),
    41: ("Nb", "Niobium"), 42: ("Mo", "Molybdenum"), 43: ("Tc", "Technetium"), 44: ("Ru", "Ruthenium"),
    45: ("Rh", "Rhodium"), 46: ("Pd", "Palladium"), 47: ("Ag", "Silver"), 48: ("Cd", "Cadmium"),
    49: ("In", "Indium"), 50: ("Sn", "Tin"), 51: ("Sb", "Antimony"), 52: ("Te", "Tellurium"),
    53: ("I", "Iodine"), 54: ("Xe", "Xenon"), 55: ("Cs", "Cesium"), 56: ("Ba", "Barium"),
    57: ("La", "Lanthanum"), 58: ("Ce", "Cerium"), 59: ("Pr", "Praseodymium"), 60: ("Nd", "Neodymium"),
    61: ("Pm", "Promethium"), 62: ("Sm", "Samarium"), 63: ("Eu", "Europium"), 64: ("Gd", "Gadolinium"),
    65: ("Tb", "Terbium"), 66: ("Dy", "Dysprosium"), 67: ("Ho", "Holmium"), 68: ("Er", "Erbium"),
    69: ("Tm", "Thulium"), 70: ("Yb", "Ytterbium"), 71: ("Lu", "Lutetium"), 72: ("Hf", "Hafnium"),
    73: ("Ta", "Tantalum"), 74: ("W", "Tungsten"), 75: ("Re", "Rhenium"), 76: ("Os", "Osmium"),
    77: ("Ir", "Iridium"), 78: ("Pt", "Platinum"), 79: ("Au", "Gold"), 80: ("Hg", "Mercury"),
    81: ("Tl", "Thallium"), 82: ("Pb", "Lead"), 83: ("Bi", "Bismuth"), 84: ("Po", "Polonium"),
    85: ("At", "Astatine"), 86: ("Rn", "Radon"), 87: ("Fr", "Francium"), 88: ("Ra", "Radium"),
    89: ("Ac", "Actinium"), 90: ("Th", "Thorium"), 91: ("Pa", "Protactinium"), 92: ("U", "Uranium"),
    93: ("Np", "Neptunium"), 94: ("Pu", "Plutonium"), 95: ("Am", "Americium"), 96: ("Cm", "Curium"),
    97: ("Bk", "Berkelium"), 98: ("Cf", "Californium"), 99: ("Es", "Einsteinium"), 100: ("Fm", "Fermium"),
    101: ("Md", "Mendelevium"), 102: ("No", "Nobelium"), 103: ("Lr", "Lawrencium"), 104: ("Rf", "Rutherfordium"),
    105: ("Db", "Dubnium"), 106: ("Sg", "Seaborgium"), 107: ("Bh", "Bohrium"), 108: ("Hs", "Hassium"),
    109: ("Mt", "Meitnerium"), 110: ("Ds", "Darmstadtium"), 111: ("Rg", "Roentgenium"), 112: ("Cn", "Copernicium"),
    113: ("Nh", "Nihonium"), 114: ("Fl", "Flerovium"), 115: ("Mc", "Moscovium"), 116: ("Lv", "Livermorium"),
    117: ("Ts", "Tennessine"), 118: ("Og", "Oganesson")
}

# 50 USGS 2022 Critical Minerals: symbol -> official commodity name (independent reference)
USGS_CRITICAL_REFERENCE = {
    "Al": "Aluminum",
    "Sb": "Antimony",
    "As": "Arsenic",
    "Ba": "Barite (Barium)",
    "Be": "Beryllium",
    "Bi": "Bismuth",
    "Ce": "Cerium",
    "Cs": "Cesium",
    "Cr": "Chromium",
    "Co": "Cobalt",
    "Dy": "Dysprosium",
    "Er": "Erbium",
    "Eu": "Europium",
    "F": "Fluorspar (Fluorine)",
    "Gd": "Gadolinium",
    "Ga": "Gallium",
    "Ge": "Germanium",
    "C": "Graphite (Carbon)",
    "Hf": "Hafnium",
    "Ho": "Holmium",
    "In": "Indium",
    "Ir": "Iridium",
    "La": "Lanthanum",
    "Li": "Lithium",
    "Lu": "Lutetium",
    "Mg": "Magnesium",
    "Mn": "Manganese",
    "Nd": "Neodymium",
    "Ni": "Nickel",
    "Nb": "Niobium",
    "Pd": "Palladium",
    "Pt": "Platinum",
    "Pr": "Praseodymium",
    "Rh": "Rhodium",
    "Rb": "Rubidium",
    "Ru": "Ruthenium",
    "Sm": "Samarium",
    "Sc": "Scandium",
    "Ta": "Tantalum",
    "Te": "Tellurium",
    "Tb": "Terbium",
    "Tm": "Thulium",
    "Sn": "Tin",
    "Ti": "Titanium",
    "W": "Tungsten",
    "V": "Vanadium",
    "Yb": "Ytterbium",
    "Y": "Yttrium",
    "Zn": "Zinc",
    "Zr": "Zirconium"
}

# Audited Materials Project Elemental Ground-State IDs
# Each ID has been checked to ensure its chemical formula corresponds strictly to the elemental ground state.
AUDITED_MP_ELEMENTAL_IDS = {
    "H": "mp-24504", "He": "mp-11880", "Li": "mp-135", "Be": "mp-87", "B": "mp-444",
    "C": "mp-48", "N": "mp-11867", "O": "mp-25377", "F": "mp-10875", "Ne": "mp-11881",
    "Na": "mp-10172", "Mg": "mp-153", "Al": "mp-134", "Si": "mp-149", "P": "mp-130",
    "S": "mp-96", "Cl": "mp-22851", "Ar": "mp-11882", "K": "mp-10183", "Ca": "mp-122",
    "Sc": "mp-60", "Ti": "mp-72", "V": "mp-83", "Cr": "mp-90", "Mn": "mp-35",
    "Fe": "mp-13", "Co": "mp-102", "Ni": "mp-23", "Cu": "mp-30", "Zn": "mp-79",
    "Ga": "mp-142", "Ge": "mp-32", "As": "mp-11", "Se": "mp-14", "Br": "mp-23154",
    "Kr": "mp-11883", "Rb": "mp-10194", "Sr": "mp-139", "Y": "mp-112", "Zr": "mp-131",
    "Nb": "mp-76", "Mo": "mp-129", "Tc": "mp-107", "Ru": "mp-33", "Rh": "mp-74",
    "Pd": "mp-2", "Ag": "mp-124", "Cd": "mp-94", "In": "mp-85", "Sn": "mp-117",
    "Sb": "mp-104", "Te": "mp-19", "I": "mp-23214", "Xe": "mp-11884", "Cs": "mp-1",
    "Ba": "mp-125", "La": "mp-26", "Ce": "mp-28", "Pr": "mp-38", "Nd": "mp-123",
    "Sm": "mp-68", "Eu": "mp-20071", "Gd": "mp-155", "Tb": "mp-18", "Dy": "mp-1057889",
    "Hf": "mp-100", "Ta": "mp-50", "W": "mp-91", "Re": "mp-8", "Os": "mp-49",
    "Ir": "mp-101", "Pt": "mp-126", "Au": "mp-81", "Hg": "mp-95", "Tl": "mp-82",
    "Pb": "mp-133", "Bi": "mp-23155", "Th": "mp-37", "U": "mp-44"
}

# Valid classifications
VALID_CLASSIFICATIONS = {
    "Diamagnet",
    "Paramagnet",
    "Ferromagnet (T_C >= 290 K)",
    "Antiferromagnet (T_N >= 290 K)",
    "Low-temperature magnetic ordering"
}

# Approved Technological Roles in Functional Alloys & Magnets
VALID_TECH_ROLES = {
    "Hard Magnetic Vector",
    "Soft Magnetic Core",
    "Magnetocaloric Active Element",
    "Magnetic Phase Stabilizer / Additive",
    "No primary commercial magnetic alloy role documented",
    "Magnetically Inert Matrix",
    # Extended descriptive names:
    "Constituent in Hard Permanent Magnets & High-Anisotropy Alloys",
    "Constituent in Soft Magnetic Alloys & High-Permeability Cores",
    "Magnetocaloric Material / Phase Transition Constituent",
    "Magnetically Inert Matrix / Substrate"
}

# Role mapping canonicalization
ROLE_CANONICAL = {
    "Hard Magnetic Vector": "hard",
    "Constituent in Hard Permanent Magnets & High-Anisotropy Alloys": "hard",
    "Soft Magnetic Core": "soft",
    "Constituent in Soft Magnetic Alloys & High-Permeability Cores": "soft",
    "Magnetocaloric Active Element": "mce",
    "Magnetocaloric Material / Phase Transition Constituent": "mce",
    "Magnetic Phase Stabilizer / Additive": "additive",
    "No primary commercial magnetic alloy role documented": "standard",
    "Magnetically Inert Matrix": "standard",
    "Magnetically Inert Matrix / Substrate": "standard"
}

EXPECTED_CANONICAL_COUNTS = {
    "hard": 8,
    "soft": 5,
    "mce": 5,
    "additive": 5,
    "standard": 95
}

# Independent Fixtures for Anomalous Ground-State Configurations
INDEPENDENT_ANOMALOUS_CONFIGS = {
    "Cr": "[Ar] 3d⁵ 4s¹",
    "Cu": "[Ar] 3d¹⁰ 4s¹",
    "Nb": "[Kr] 4d⁴ 5s¹",
    "Mo": "[Kr] 4d⁵ 5s¹",
    "Ru": "[Kr] 4d⁷ 5s¹",
    "Rh": "[Kr] 4d⁸ 5s¹",
    "Pd": "[Kr] 4d¹⁰",
    "Ag": "[Kr] 4d¹⁰ 5s¹",
    "La": "[Xe] 5d¹ 6s²",
    "Ce": "[Xe] 4f¹ 5d¹ 6s²",
    "Gd": "[Xe] 4f⁷ 5d¹ 6s²",
    "Pt": "[Xe] 4f¹⁴ 5d⁹ 6s¹",
    "Au": "[Xe] 4f¹⁴ 5d¹⁰ 6s¹"
}

# Independent Fixtures for Canonical Materials Project Elemental Ground States
INDEPENDENT_MP_FIXTURES = {
    "Fe": {"mp_id": "mp-13", "formula": "Fe", "crystal_system": "BCC", "space_group_symbol": "Im-3m"},
    "Co": {"mp_id": "mp-102", "formula": "Co", "crystal_system": "HCP", "space_group_symbol": "P6_3/mmc"},
    "Ni": {"mp_id": "mp-23", "formula": "Ni", "crystal_system": "FCC", "space_group_symbol": "Fm-3m"},
    "Cr": {"mp_id": "mp-90", "formula": "Cr", "crystal_system": "BCC", "space_group_symbol": "Im-3m"},
    "Cu": {"mp_id": "mp-30", "formula": "Cu", "crystal_system": "FCC", "space_group_symbol": "Fm-3m"},
    "Al": {"mp_id": "mp-134", "formula": "Al", "crystal_system": "FCC", "space_group_symbol": "Fm-3m"},
    "Si": {"mp_id": "mp-149", "formula": "Si", "crystal_system": "Diamond cubic", "space_group_symbol": "Fd-3m"},
    "Ti": {"mp_id": "mp-72", "formula": "Ti", "crystal_system": "HCP", "space_group_symbol": "P6_3/mmc"},
    "Gd": {"mp_id": "mp-155", "formula": "Gd", "crystal_system": "HCP", "space_group_symbol": "P6_3/mmc"},
    "Nd": {"mp_id": "mp-123", "formula": "Nd", "crystal_system": "DHCP", "space_group_symbol": "P6_3/mmc"},
    "Pt": {"mp_id": "mp-126", "formula": "Pt", "crystal_system": "FCC", "space_group_symbol": "Fm-3m"},
    "Au": {"mp_id": "mp-81", "formula": "Au", "crystal_system": "FCC", "space_group_symbol": "Fm-3m"},
    "Bi": {"mp_id": "mp-23155", "formula": "Bi", "crystal_system": "Rhombohedral", "space_group_symbol": "R-3m"}
}

GAS_SYMBOLS_AT_298K = {"H", "He", "N", "O", "F", "Ne", "Cl", "Ar", "Kr", "Xe", "Rn"}
LIQUID_SYMBOLS_AT_298K = {"Br", "Hg"}

RECOGNIZED_BIBLIOGRAPHIC_SOURCES = {
    "NIST ASD / Russell-Saunders LS-coupling",
    "Ashcroft & Mermin / Kittel / Coey (Magnetism and Magnetic Materials)",
    "Crangle & Goodman (1971) / Kittel Solid State Physics / Landolt-Börnstein Group III",
    "CRC Handbook of Chemistry & Physics (97th ed.) / Landolt-Börnstein",
    "CRC Handbook of Chemistry & Physics (97th ed.) / Landolt-Börnstein Group III",
    "Landolt-Börnstein Group III / Kittel Introduction to Solid State Physics",
    "Bozorth (Ferromagnetism) / Coey (Magnetism and Magnetic Materials)",
    "Landolt-Börnstein / Bozorth",
    "Soulen et al. (1998) / Meservey & Tedrow (1994) / Coey (2010)",
    "Meservey & Tedrow / Soulen et al. (Science 1998)",
    "Coey, J.M.D., Magnetism and Magnetic Materials (Cambridge Univ. Press); Buschow, K.H.J., Handbook of Magnetic Materials",
    "Coey (2010) / Herbst (1991) / Buschow (1997) / Gutfleisch et al. (2011)",
    "Domain hysteresis regime",
}

SUBSHELL_CAPACITIES = {"s": 2, "p": 6, "d": 10, "f": 14, "g": 18}
L_CHAR_TO_NUM = {"S": 0, "P": 1, "D": 2, "F": 3, "G": 4, "H": 5, "I": 6, "K": 7, "L": 8, "M": 9}


def validate_electron_subshells(full_cfg: str, expected_z: int):
    """
    Validates full electron configuration:
    - Verifies subshell orbital capacities (s<=2, p<=6, d<=10, f<=14).
    - Ensures no duplicate subshells exist.
    - Ensures sum of orbital electrons strictly equals expected atomic number Z.
    """
    sup_map = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5, "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}
    tokens = full_cfg.strip().split()
    seen_subshells = set()
    total = 0
    errs = []
    for tok in tokens:
        m = re.match(r"^(\d+)([spdfg])(\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹]+)$", tok)
        if not m:
            errs.append(f"Unrecognized subshell token '{tok}' in full configuration: '{full_cfg}'")
            continue
        n = int(m.group(1))
        sub = m.group(2)
        exp_str = m.group(3)
        cnt = int("".join(str(sup_map[c]) for c in exp_str)) if exp_str[0] in sup_map else int(exp_str)

        max_cap = SUBSHELL_CAPACITIES.get(sub, 99)
        if cnt < 1 or cnt > max_cap:
            errs.append(f"Subshell '{tok}' violates orbital capacity: has {cnt} electrons, max is {max_cap}")

        sub_id = f"{n}{sub}"
        if sub_id in seen_subshells:
            errs.append(f"Duplicate subshell '{sub_id}' found in configuration: '{full_cfg}'")
        seen_subshells.add(sub_id)
        total += cnt

    if total != expected_z:
        errs.append(f"Sum of electrons ({total}) does not match atomic number Z={expected_z} in '{full_cfg}'")
    return errs


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


def sum_electron_configuration(full_cfg: str) -> int:
    """Calculates sum of orbital electrons in configuration."""
    errs = validate_electron_subshells(full_cfg, 0)
    # Just calculate total
    sup_map = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5, "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}
    total = 0
    for tok in full_cfg.strip().split():
        m = re.match(r"^\d+[spdfg](\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹]+)$", tok)
        if m:
            exp_str = m.group(1)
            total += int("".join(str(sup_map[c]) for c in exp_str)) if exp_str[0] in sup_map else int(exp_str)
    return total


def validate_database_file(file_path: str, mode: str = "enriched") -> bool:
    """
    Validates a database JSON file.
    mode: 'base' | 'crystallography' | 'enriched'
    """
    path = Path(file_path).resolve()
    print("=" * 78)
    print(f"RUNNING SCIENTIFIC VALIDATION AUDIT (Mode: {mode.upper()}): {path.name}")
    print(f"Target Path: {path}")
    print("=" * 78)

    if not path.exists():
        raise FileNotFoundError(f"Database file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    warnings = []

    # 1. Element Count
    if len(data) != 118:
        errors.append(f"Total element count must be 118, found {len(data)}")

    seen_z = set()
    seen_sym = set()
    seen_mp = set()

    critical_count = 0
    radioactive_count = 0
    canonical_role_counts = {"hard": 0, "soft": 0, "mce": 0, "additive": 0, "standard": 0}

    is_cryst_mode = mode in ("crystallography", "enriched")
    is_enriched_mode = (mode == "enriched")

    for elem in data:
        z = elem.get("atomic_number")
        sym = elem.get("symbol")
        name = elem.get("name")

        # Basic identity checks against IUPAC standard
        if z is None or not isinstance(z, int) or z < 1 or z > 118:
            errors.append(f"Invalid atomic number: {z}")
            continue

        if z in seen_z:
            errors.append(f"Duplicate atomic number Z={z}")
        seen_z.add(z)

        expected_sym, expected_name = IUPAC_STANDARD_ELEMENTS[z]
        if sym != expected_sym:
            errors.append(f"Symbol mismatch for Z={z}: got '{sym}', expected IUPAC standard '{expected_sym}'")
        if name != expected_name:
            errors.append(f"Name mismatch for Z={z}: got '{name}', expected IUPAC standard '{expected_name}'")

        if sym in seen_sym:
            errors.append(f"Duplicate chemical symbol: {sym}")
        seen_sym.add(sym)

        # 2. Radioactivity Audit
        is_rad = elem.get("radioactive")
        expected_rad = (z == 43 or z == 61 or z >= 84)
        if is_rad != expected_rad:
            errors.append(f"Radioactivity mismatch for {sym} (Z={z}): got {is_rad}, expected {expected_rad}")
        if is_rad:
            radioactive_count += 1

        # 3. USGS Critical Minerals Audit (Element-by-Element verification against independent reference)
        is_crit = elem.get("usgs_critical_mineral")
        comm_name = elem.get("usgs_commodity_name")
        if sym in USGS_CRITICAL_REFERENCE:
            if not is_crit:
                errors.append(f"{sym} is on the USGS 2022 Critical Minerals list but 'usgs_critical_mineral' is {is_crit}")
            expected_comm = USGS_CRITICAL_REFERENCE[sym]
            if comm_name != expected_comm:
                errors.append(f"{sym} USGS commodity mismatch: got '{comm_name}', expected '{expected_comm}'")
            critical_count += 1
        else:
            if is_crit:
                errors.append(f"{sym} is NOT on the USGS 2022 Critical Minerals list but 'usgs_critical_mineral' is True")
            if comm_name is not None:
                errors.append(f"{sym} is not a critical mineral but has commodity name '{comm_name}' (expected None)")

        # 4. Magnetic Classification Consistency
        mag_class = elem.get("magnetic_classification")
        if mag_class not in VALID_CLASSIFICATIONS:
            errors.append(f"Unknown magnetic classification for {sym}: '{mag_class}'")

        t_k = elem.get("transition_temperature_k")
        t_type = elem.get("transition_temperature_type")

        if mag_class == "Ferromagnet (T_C >= 290 K)":
            if t_k is None or t_k < 290.0:
                errors.append(f"Ferromagnet {sym} must have Tc >= 290 K, got {t_k}")
            if t_type not in ("Curie", "Tc"):
                errors.append(f"Ferromagnet {sym} transition type must be 'Curie', got '{t_type}'")

        elif mag_class == "Antiferromagnet (T_N >= 290 K)":
            if t_k is None or t_k < 290.0:
                errors.append(f"Antiferromagnet {sym} must have Tn >= 290 K, got {t_k}")
            if t_type not in ("Neel", "Tn"):
                errors.append(f"Antiferromagnet {sym} transition type must be 'Neel', got '{t_type}'")

        elif mag_class == "Low-temperature magnetic ordering":
            if t_k is None or t_k >= 290.0:
                errors.append(f"Low-temp magnetic element {sym} must have T < 290 K, got {t_k}")
            if t_type not in ("Curie", "Neel", "Tc", "Tn"):
                errors.append(f"Low-temp magnetic element {sym} transition type must be Curie or Neel, got '{t_type}'")

        elif mag_class in ("Diamagnet", "Paramagnet"):
            if t_k is not None:
                errors.append(f"{mag_class} {sym} must have transition_temperature_k = None, got {t_k}")

        # Crystallography & Structural Mode Checks
        if is_cryst_mode:
            # 5. Crystallography
            cryst = elem.get("crystallography")
            if not cryst:
                errors.append(f"Missing crystallography block for {sym}")
            else:
                sg_num = cryst.get("space_group_number")
                if sg_num is None or not (1 <= sg_num <= 230):
                    errors.append(f"Invalid space group number for {sym}: {sg_num}")
                lat = cryst.get("lattice_parameters", {})
                for param in ("a", "b", "c", "alpha", "beta", "gamma"):
                    val = lat.get(param)
                    if val is None or not isinstance(val, (int, float)) or val <= 0:
                        errors.append(f"Invalid lattice parameter {param}={val} for {sym}")

            # 6. Electron Configuration Audit (Full subshell sum strictly == Z, capacities, no duplicates)
            elec = elem.get("electronic_configuration")
            if not elec:
                errors.append(f"Missing electronic_configuration for {sym}")
            else:
                full_cfg = elec.get("full", "")
                if "..." in full_cfg:
                    errors.append(f"Full electron configuration contains ellipsis '...' for {sym}: '{full_cfg}'")
                sub_errs = validate_electron_subshells(full_cfg, z)
                for se in sub_errs:
                    errors.append(f"{sym} (Z={z}): {se}")

                # Check independent ground-state anomaly fixture if present
                if sym in INDEPENDENT_ANOMALOUS_CONFIGS:
                    expected_abbrev = INDEPENDENT_ANOMALOUS_CONFIGS[sym]
                    if elec.get("abbreviated") != expected_abbrev:
                        errors.append(f"Ground-state configuration anomaly mismatch for {sym}: expected '{expected_abbrev}', got '{elec.get('abbreviated')}'")

                val_elec = elec.get("valence_electrons")
                if val_elec is None or not (1 <= val_elec <= 18):
                    errors.append(f"Invalid valence electrons for {sym}: {val_elec}")

            # 7. Materials Project Coverage & Fixtures Audit
            mp = elem.get("materials_project")
            if is_cryst_mode or is_enriched_mode:
                if sym in AUDITED_MP_ELEMENTAL_IDS:
                    vetted_id = AUDITED_MP_ELEMENTAL_IDS[sym]
                    if not mp or not mp.get("material_id"):
                        errors.append(f"Materials Project coverage missing for {sym}: expected audited '{vetted_id}', got null/missing")
                    else:
                        mp_id = mp.get("material_id")
                        if not re.match(r"^mp-\d+$", mp_id):
                            errors.append(f"Malformed Materials Project ID for {sym}: '{mp_id}'")
                        if mp_id != vetted_id:
                            errors.append(f"Materials Project ID mismatch for {sym}: got '{mp_id}', expected vetted '{vetted_id}'")
                        mp_formula = mp.get("formula")
                        if mp_formula != sym:
                            errors.append(f"Materials Project formula mismatch for {sym}: got '{mp_formula}', expected '{sym}'")
                        if mp_id in seen_mp:
                            errors.append(f"Duplicate Materials Project ID '{mp_id}' assigned to {sym}")
                        seen_mp.add(mp_id)
                        expected_url = f"https://materialsproject.org/materials/{mp_id}"
                        mp_url = mp.get("url")
                        if mp_url != expected_url:
                            errors.append(f"URL mismatch for {sym}: got '{mp_url}', expected '{expected_url}'")
                        # Independent fixture check
                        if sym in INDEPENDENT_MP_FIXTURES:
                            fix = INDEPENDENT_MP_FIXTURES[sym]
                            if mp_id != fix["mp_id"]:
                                errors.append(f"Materials Project ground-state ID mismatch for {sym}: expected fixture '{fix['mp_id']}', got '{mp_id}'")
                            if cryst.get("crystal_system") != fix["crystal_system"]:
                                errors.append(f"Materials Project ground-state crystal system mismatch for {sym}: expected '{fix['crystal_system']}', got '{cryst.get('crystal_system')}'")
                            if cryst.get("space_group_symbol") != fix["space_group_symbol"]:
                                errors.append(f"Materials Project ground-state space group mismatch for {sym}: expected '{fix['space_group_symbol']}', got '{cryst.get('space_group_symbol')}'")
                else:
                    if mp and mp.get("material_id") is not None:
                        errors.append(f"Unexpected Materials Project ID '{mp.get('material_id')}' assigned to non-audited element {sym}")

            # 8. Physical Properties Range Checks
            phys = elem.get("physical_properties")
            if phys:
                density = phys.get("density_g_cm3")
                if density is not None and (density <= 0 or density > 45.0):
                    errors.append(f"Unphysical density for {sym}: {density} g/cm³")
                mp_k = phys.get("melting_point_k")
                bp_k = phys.get("boiling_point_k")
                if mp_k is not None and mp_k <= 0:
                    errors.append(f"Unphysical melting point for {sym}: {mp_k} K")
                if bp_k is not None and bp_k <= 0:
                    errors.append(f"Unphysical boiling point for {sym}: {bp_k} K")
                if mp_k is not None and bp_k is not None and mp_k > bp_k + 5.0:
                    warnings.append(f"Melting point > boiling point for {sym} (sublimation): mp={mp_k} K, bp={bp_k} K")

        # 9. Enriched Mode: Strict requirement of Advanced Magnetism across ALL 118 elements
        if is_enriched_mode:
            adv = elem.get("advanced_magnetism")
            if not adv:
                errors.append(f"Strict validation error: Element {sym} (Z={z}) is missing 'advanced_magnetism' block")
            else:
                q = adv.get("quantum", {})
                term = q.get("term_symbol")
                if not term or not isinstance(term, str):
                    errors.append(f"Missing or invalid term_symbol for {sym}")
                else:
                    parsed = parse_rs_term(term)
                    if not parsed:
                        errors.append(f"Invalid Russell-Saunders term symbol syntax for {sym}: '{term}'")
                    else:
                        mult, S, L_char, L, J = parsed
                        if J == 0:
                            g_expected = 0.0
                        else:
                            g_expected = 1.0 + (J * (J + 1.0) + S * (S + 1.0) - L * (L + 1.0)) / (2.0 * J * (J + 1.0))

                        g_j = q.get("lande_g_factor")
                        if g_j is None or not (0.0 <= g_j <= 5.0):
                            errors.append(f"Invalid Landé g-factor for {sym}: {g_j}")
                        else:
                            tol = 0.35 if z in (92, 93) else 0.05
                            if abs(g_j - g_expected) > tol:
                                errors.append(f"Landé g-factor inconsistency for {sym} (Z={z}): recorded {g_j}, expected {g_expected:.3f} from term {term} (tol={tol})")

                            expected_neutral_mu = round(g_j * (J * (J + 1.0))**0.5, 2) if J > 0 else 0.0
                            recorded_neutral_mu = q.get("neutral_atom_moment_mu_B", q.get("free_atom_moment_mu_B"))
                            if recorded_neutral_mu is not None and abs(recorded_neutral_mu - expected_neutral_mu) > 0.05:
                                errors.append(f"Neutral atom moment inconsistency for {sym}: recorded {recorded_neutral_mu} μ_B, expected {expected_neutral_mu} μ_B")

                # Magnetic Ordering & Moment Invariants
                bulk_mu = q.get("bulk_ordered_moment_mu_B", elem.get("bulk_ordered_moment_mu_B"))
                if mag_class in ("Ferromagnet (T_C >= 290 K)", "Antiferromagnet (T_N >= 290 K)", "Low-temperature magnetic ordering"):
                    if bulk_mu is None or not (0.05 <= bulk_mu <= 15.0):
                        errors.append(f"Magnetically ordered element {sym} ({mag_class}) requires bulk_ordered_moment_mu_B (0.05 to 15.0 μ_B), got {bulk_mu}")
                else:
                    if bulk_mu is not None:
                        errors.append(f"Non-ordered element {sym} ({mag_class}) must have bulk_ordered_moment_mu_B = None, got {bulk_mu}")

                t_dict = adv.get("thermodynamic", {})
                cw_temp = t_dict.get("curie_weiss_temp_K", elem.get("curie_weiss_temp_K"))
                if cw_temp is not None and not (-2000.0 <= cw_temp <= 2500.0):
                    errors.append(f"Unphysical Curie-Weiss temp for {sym}: {cw_temp} K")

                ms_t = t_dict.get("saturation_magnetization_T", elem.get("saturation_magnetization_T"))
                if ms_t is not None and not (0.05 <= ms_t <= 4.0):
                    errors.append(f"Unphysical saturation magnetization for {sym}: {ms_t} T")
                if mag_class == "Ferromagnet (T_C >= 290 K)":
                    if ms_t is None or not (0.05 <= ms_t <= 3.5):
                        errors.append(f"Room-temperature ferromagnet {sym} requires saturation magnetization (0.05 <= M_s <= 3.5 T), got {ms_t}")

                # Susceptibility Sign Checks
                chi_m = t_dict.get("molar_susceptibility_298K", elem.get("molar_susceptibility_298K"))
                if mag_class == "Diamagnet":
                    if chi_m is None or chi_m >= 0.0:
                        errors.append(f"Diamagnet {sym} must have negative molar susceptibility (chi_m < 0), got {chi_m}")
                elif mag_class == "Paramagnet":
                    if chi_m is None or chi_m <= 0.0:
                        errors.append(f"Paramagnet {sym} must have positive molar susceptibility (chi_m > 0), got {chi_m}")
                elif mag_class == "Ferromagnet (T_C >= 290 K)":
                    if sym in ("Fe", "Co", "Ni") and chi_m is not None:
                        errors.append(f"Room-temperature ferromagnet {sym} below T_C must not define single linear chi_m at 298 K (domain hysteresis regime), got {chi_m}")

                sp_dict = adv.get("spintronics", {})
                spin_p = sp_dict.get("spin_polarization_percent", elem.get("spin_polarization_percent"))
                if spin_p is not None and not (0.0 <= spin_p <= 100.0):
                    errors.append(f"Unphysical spin polarization for {sym}: {spin_p}%")

                role = adv.get("technological", {}).get("magnet_role", elem.get("magnet_role"))
                if role not in VALID_TECH_ROLES:
                    errors.append(f"Invalid technological role for {sym}: '{role}'")
                else:
                    canon = ROLE_CANONICAL.get(role)
                    if canon:
                        canonical_role_counts[canon] += 1

                # 11. Property-Level Provenance & Measurement Conditions Audit
                prov = adv.get("provenance_and_conditions")
                if not prov or not isinstance(prov, dict):
                    errors.append(f"Missing provenance_and_conditions block for {sym}")
                else:
                    req_prov_keys = [
                        "neutral_atom_ground_state",
                        "free_ion_state",
                        "bulk_ordered_moment_mu_B",
                        "molar_susceptibility_298K",
                        "curie_weiss_temp_K",
                        "saturation_magnetization_T",
                        "magnetocrystalline_anisotropy_J_m3",
                        "spin_polarization_percent",
                        "technological_role"
                    ]
                    for rpk in req_prov_keys:
                        if rpk not in prov:
                            errors.append(f"Missing provenance block entry '{rpk}' for {sym}")
                        else:
                            pentry = prov[rpk]
                            if not isinstance(pentry, dict):
                                errors.append(f"Provenance entry '{rpk}' for {sym} must be an object")
                            elif not pentry.get("physical_scope"):
                                errors.append(f"Missing physical_scope in provenance '{rpk}' for {sym}")

                    # Verify citations for asserted properties
                    if q.get("bulk_ordered_moment_mu_B") is not None:
                        if not prov.get("bulk_ordered_moment_mu_B", {}).get("source"):
                            errors.append(f"Uncited bulk ordered moment in provenance for {sym}")
                    if t_dict.get("molar_susceptibility_298K") is not None:
                        if not prov.get("molar_susceptibility_298K", {}).get("source"):
                            errors.append(f"Uncited molar susceptibility in provenance for {sym}")
                    if t_dict.get("saturation_magnetization_T") is not None:
                        if not prov.get("saturation_magnetization_T", {}).get("source"):
                            errors.append(f"Uncited saturation magnetization in provenance for {sym}")
                    if not prov.get("technological_role", {}).get("source"):
                        errors.append(f"Uncited technological role in provenance for {sym}")

                    # Verify physical_scope fidelity for molar_susceptibility_298K
                    chi_prov = prov.get("molar_susceptibility_298K", {})
                    actual_scope = chi_prov.get("physical_scope")
                    if sym in GAS_SYMBOLS_AT_298K:
                        if actual_scope != "gas_phase_at_298K":
                            errors.append(f"Physical scope mismatch for gas element {sym}: expected 'gas_phase_at_298K', got '{actual_scope}'")
                    elif sym in LIQUID_SYMBOLS_AT_298K:
                        if actual_scope != "liquid_phase_at_298K":
                            errors.append(f"Physical scope mismatch for liquid element {sym}: expected 'liquid_phase_at_298K', got '{actual_scope}'")
                    elif sym == "Gd":
                        if actual_scope != "bulk_solid_paramagnetic_at_298K":
                            errors.append(f"Physical scope mismatch for Gd (T_C=292 K < 298.15 K): expected 'bulk_solid_paramagnetic_at_298K', got '{actual_scope}'")
                    elif sym in ("Fe", "Co", "Ni"):
                        if actual_scope != "bulk_solid_ferromagnetic_domain_state":
                            errors.append(f"Physical scope mismatch for ferromagnetic {sym}: expected 'bulk_solid_ferromagnetic_domain_state', got '{actual_scope}'")

                    # Verify physical_scope fidelity for saturation_magnetization_T
                    ms_prov = prov.get("saturation_magnetization_T", {})
                    actual_ms_scope = ms_prov.get("physical_scope")
                    if sym in ("Fe", "Co", "Ni"):
                        if actual_ms_scope != "bulk_solid_ferromagnetic_at_298K":
                            errors.append(f"Saturation scope mismatch for room-temp ferromagnet {sym}: expected 'bulk_solid_ferromagnetic_at_298K', got '{actual_ms_scope}'")
                    elif t_dict.get("saturation_magnetization_T") is not None:
                        if actual_ms_scope != "bulk_solid_ferromagnetic_cryogenic_at_4.2K":
                            errors.append(f"Saturation scope mismatch for cryogenic ferromagnet {sym}: expected 'bulk_solid_ferromagnetic_cryogenic_at_4.2K', got '{actual_ms_scope}'")

                    # Verify recognized bibliographic sources
                    for prop_k, prop_dict in prov.items():
                        src = prop_dict.get("source")
                        if src is not None and src not in RECOGNIZED_BIBLIOGRAPHIC_SOURCES:
                            errors.append(f"Unrecognized bibliographic source in provenance for {sym} [{prop_k}]: '{src}'")

    # Check overall aggregate statistics
    if len(seen_z) != 118:
        errors.append(f"Missing atomic numbers: found {len(seen_z)} / 118")

    if radioactive_count != 37:
        errors.append(f"Expected exactly 37 radioactive elements, found {radioactive_count}")

    if critical_count != 50:
        errors.append(f"Expected exactly 50 USGS critical minerals, found {critical_count}")

    if is_cryst_mode or is_enriched_mode:
        if len(seen_mp) != len(AUDITED_MP_ELEMENTAL_IDS):
            errors.append(f"Materials Project coverage incomplete: expected {len(AUDITED_MP_ELEMENTAL_IDS)} audited elemental entries, but found {len(seen_mp)}")

    if is_enriched_mode:
        for c_role, exp_cnt in EXPECTED_CANONICAL_COUNTS.items():
            actual_cnt = canonical_role_counts.get(c_role, 0)
            if actual_cnt != exp_cnt:
                errors.append(f"Technological role '{c_role}' count mismatch: expected {exp_cnt}, found {actual_cnt}")

    # Output results
    print(f"Elements audited:       {len(seen_z)} / 118")
    print(f"USGS Critical Minerals: {critical_count} / 50 verified")
    print(f"Radioactive Elements:   {radioactive_count} / 37 verified")
    if is_cryst_mode:
        print(f"Vetted MP IDs assigned: {len(seen_mp)}")
    if is_enriched_mode:
        print(f"Technological Roles:    Hard={canonical_role_counts['hard']}, Soft={canonical_role_counts['soft']}, MCE={canonical_role_counts['mce']}, Additive={canonical_role_counts['additive']}, Standard={canonical_role_counts['standard']}")

    if warnings:
        print(f"\n[WARNINGS] ({len(warnings)} found):")
        for w in warnings[:10]:
            print(f"  • {w}")

    if errors:
        print(f"\n[FAILED] Scientific audit identified {len(errors)} error(s):")
        for err in errors[:25]:
            print(f"  ✗ {err}")
        if len(errors) > 25:
            print(f"  ... and {len(errors) - 25} more error(s)")
        print("=" * 78)
        return False

    print("\n[PASS] All structural, schema, and specified scientific consistency checks passed successfully!")
    print("=" * 78)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate scientific integrity of magnetic elements database.")
    parser.add_argument("file", nargs="?", default=None, help="JSON file to validate")
    parser.add_argument("--mode", choices=["base", "crystallography", "enriched"], default=None,
                        help="Validation mode: 'base', 'crystallography', or 'enriched'")
    parser.add_argument("--base", action="store_true", help="Alias for --mode base")
    parser.add_argument("--crystallography", action="store_true", help="Alias for --mode crystallography")
    parser.add_argument("--enriched", action="store_true", help="Alias for --mode enriched")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent

    # Determine mode
    mode = "enriched"
    if args.base:
        mode = "base"
    elif args.crystallography:
        mode = "crystallography"
    elif args.enriched:
        mode = "enriched"
    elif args.mode:
        mode = args.mode

    # Determine file
    if args.file:
        target_path = Path(args.file)
        if not target_path.is_absolute():
            target_path = script_dir / target_path
    else:
        if mode == "base":
            target_path = script_dir / "magnetic_elements_db.json"
        elif mode == "crystallography":
            target_path = script_dir / "magnetic_elements_crystallography.json"
        else:
            target_path = script_dir / "magnetic_elements_enriched.json"

    success = validate_database_file(str(target_path), mode=mode)
    sys.exit(0 if success else 1)
