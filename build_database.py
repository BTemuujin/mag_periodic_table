"""
Script to generate the complete magnetic_elements_db.json dataset for all 118 elements.
Includes:
- Atomic data (number, symbol, name, standard atomic weight, group, period)
- Radioactivity status (Tc, Pm, and Z >= 84)
- USGS Critical Minerals (2022 official list of 50 mineral commodities)
- Magnetic Classification:
    * Diamagnet (White)
    * Paramagnet (Yellow)
    * Ferromagnet (Tc >= 290 K) (Blue)
    * Antiferromagnet (Tn >= 290 K) (Green)
    * Low-temperature magnetic ordering (Tn/Tc < 290 K) (Light Green)
- Specific magnetic transition temperature in Kelvin (if applicable)
"""

import json

# Define the 50 USGS Critical Minerals (2022 Final List)
USGS_CRITICAL_MINERALS = {
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

# Raw data table for all 118 elements:
# (Z, Symbol, Name, AtomicWeight, Period, Group, Category)
RAW_ELEMENTS = [
    (1, "H", "Hydrogen", "1.008", 1, 1, "Nonmetal"),
    (2, "He", "Helium", "4.0026", 1, 18, "Noble Gas"),
    (3, "Li", "Lithium", "6.94", 2, 1, "Alkali Metal"),
    (4, "Be", "Beryllium", "9.0122", 2, 2, "Alkaline Earth Metal"),
    (5, "B", "Boron", "10.81", 2, 13, "Metalloid"),
    (6, "C", "Carbon", "12.011", 2, 14, "Nonmetal"),
    (7, "N", "Nitrogen", "14.007", 2, 15, "Nonmetal"),
    (8, "O", "Oxygen", "15.999", 2, 16, "Nonmetal"),
    (9, "F", "Fluorine", "18.998", 2, 17, "Halogen"),
    (10, "Ne", "Neon", "20.180", 2, 18, "Noble Gas"),
    (11, "Na", "Sodium", "22.990", 3, 1, "Alkali Metal"),
    (12, "Mg", "Magnesium", "24.305", 3, 2, "Alkaline Earth Metal"),
    (13, "Al", "Aluminum", "26.982", 3, 13, "Post-Transition Metal"),
    (14, "Si", "Silicon", "28.085", 3, 14, "Metalloid"),
    (15, "P", "Phosphorus", "30.974", 3, 15, "Nonmetal"),
    (16, "S", "Sulfur", "32.06", 3, 16, "Nonmetal"),
    (17, "Cl", "Chlorine", "35.45", 3, 17, "Halogen"),
    (18, "Ar", "Argon", "39.95", 3, 18, "Noble Gas"),
    (19, "K", "Potassium", "39.098", 4, 1, "Alkali Metal"),
    (20, "Ca", "Calcium", "40.078", 4, 2, "Alkaline Earth Metal"),
    (21, "Sc", "Scandium", "44.956", 4, 3, "Transition Metal"),
    (22, "Ti", "Titanium", "47.867", 4, 4, "Transition Metal"),
    (23, "V", "Vanadium", "50.942", 4, 5, "Transition Metal"),
    (24, "Cr", "Chromium", "51.996", 4, 6, "Transition Metal"),
    (25, "Mn", "Manganese", "54.938", 4, 7, "Transition Metal"),
    (26, "Fe", "Iron", "55.845", 4, 8, "Transition Metal"),
    (27, "Co", "Cobalt", "58.933", 4, 9, "Transition Metal"),
    (28, "Ni", "Nickel", "58.693", 4, 10, "Transition Metal"),
    (29, "Cu", "Copper", "63.546", 4, 11, "Transition Metal"),
    (30, "Zn", "Zinc", "65.38", 4, 12, "Post-Transition Metal"),
    (31, "Ga", "Gallium", "69.723", 4, 13, "Post-Transition Metal"),
    (32, "Ge", "Germanium", "72.630", 4, 14, "Metalloid"),
    (33, "As", "Arsenic", "74.922", 4, 15, "Metalloid"),
    (34, "Se", "Selenium", "78.971", 4, 16, "Nonmetal"),
    (35, "Br", "Bromine", "79.904", 4, 17, "Halogen"),
    (36, "Kr", "Krypton", "83.798", 4, 18, "Noble Gas"),
    (37, "Rb", "Rubidium", "85.468", 5, 1, "Alkali Metal"),
    (38, "Sr", "Strontium", "87.62", 5, 2, "Alkaline Earth Metal"),
    (39, "Y", "Yttrium", "88.906", 5, 3, "Transition Metal"),
    (40, "Zr", "Zirconium", "91.224", 5, 4, "Transition Metal"),
    (41, "Nb", "Niobium", "92.906", 5, 5, "Transition Metal"),
    (42, "Mo", "Molybdenum", "95.95", 5, 6, "Transition Metal"),
    (43, "Tc", "Technetium", "[98]", 5, 7, "Transition Metal"),
    (44, "Ru", "Ruthenium", "101.07", 5, 8, "Transition Metal"),
    (45, "Rh", "Rhodium", "102.91", 5, 9, "Transition Metal"),
    (46, "Pd", "Palladium", "106.42", 5, 10, "Transition Metal"),
    (47, "Ag", "Silver", "107.87", 5, 11, "Transition Metal"),
    (48, "Cd", "Cadmium", "112.41", 5, 12, "Post-Transition Metal"),
    (49, "In", "Indium", "114.82", 5, 13, "Post-Transition Metal"),
    (50, "Sn", "Tin", "118.71", 5, 14, "Post-Transition Metal"),
    (51, "Sb", "Antimony", "121.76", 5, 15, "Metalloid"),
    (52, "Te", "Tellurium", "127.60", 5, 16, "Metalloid"),
    (53, "I", "Iodine", "126.90", 5, 17, "Halogen"),
    (54, "Xe", "Xenon", "131.29", 5, 18, "Noble Gas"),
    (55, "Cs", "Cesium", "132.91", 6, 1, "Alkali Metal"),
    (56, "Ba", "Barium", "137.33", 6, 2, "Alkaline Earth Metal"),
    (57, "La", "Lanthanum", "138.91", 6, 3, "Lanthanide"),
    (58, "Ce", "Cerium", "140.12", 6, 3, "Lanthanide"),
    (59, "Pr", "Praseodymium", "140.91", 6, 3, "Lanthanide"),
    (60, "Nd", "Neodymium", "144.24", 6, 3, "Lanthanide"),
    (61, "Pm", "Promethium", "[145]", 6, 3, "Lanthanide"),
    (62, "Sm", "Samarium", "150.36", 6, 3, "Lanthanide"),
    (63, "Eu", "Europium", "151.96", 6, 3, "Lanthanide"),
    (64, "Gd", "Gadolinium", "157.25", 6, 3, "Lanthanide"),
    (65, "Tb", "Terbium", "158.93", 6, 3, "Lanthanide"),
    (66, "Dy", "Dysprosium", "162.50", 6, 3, "Lanthanide"),
    (67, "Ho", "Holmium", "164.93", 6, 3, "Lanthanide"),
    (68, "Er", "Erbium", "167.26", 6, 3, "Lanthanide"),
    (69, "Tm", "Thulium", "168.93", 6, 3, "Lanthanide"),
    (70, "Yb", "Ytterbium", "173.05", 6, 3, "Lanthanide"),
    (71, "Lu", "Lutetium", "174.97", 6, 3, "Lanthanide"),
    (72, "Hf", "Hafnium", "178.49", 6, 4, "Transition Metal"),
    (73, "Ta", "Tantalum", "180.95", 6, 5, "Transition Metal"),
    (74, "W", "Tungsten", "183.84", 6, 6, "Transition Metal"),
    (75, "Re", "Rhenium", "186.21", 6, 7, "Transition Metal"),
    (76, "Os", "Osmium", "190.23", 6, 8, "Transition Metal"),
    (77, "Ir", "Iridium", "192.22", 6, 9, "Transition Metal"),
    (78, "Pt", "Platinum", "195.08", 6, 10, "Transition Metal"),
    (79, "Au", "Gold", "196.97", 6, 11, "Transition Metal"),
    (80, "Hg", "Mercury", "200.59", 6, 12, "Post-Transition Metal"),
    (81, "Tl", "Thallium", "204.38", 6, 13, "Post-Transition Metal"),
    (82, "Pb", "Lead", "207.2", 6, 14, "Post-Transition Metal"),
    (83, "Bi", "Bismuth", "208.98", 6, 15, "Post-Transition Metal"),
    (84, "Po", "Polonium", "[209]", 6, 16, "Post-Transition Metal"),
    (85, "At", "Astatine", "[210]", 6, 17, "Halogen"),
    (86, "Rn", "Radon", "[222]", 6, 18, "Noble Gas"),
    (87, "Fr", "Francium", "[223]", 7, 1, "Alkali Metal"),
    (88, "Ra", "Radium", "[226]", 7, 2, "Alkaline Earth Metal"),
    (89, "Ac", "Actinium", "[227]", 7, 3, "Actinide"),
    (90, "Th", "Thorium", "232.04", 7, 3, "Actinide"),
    (91, "Pa", "Protactinium", "231.04", 7, 3, "Actinide"),
    (92, "U", "Uranium", "238.03", 7, 3, "Actinide"),
    (93, "Np", "Neptunium", "[237]", 7, 3, "Actinide"),
    (94, "Pu", "Plutonium", "[244]", 7, 3, "Actinide"),
    (95, "Am", "Americium", "[243]", 7, 3, "Actinide"),
    (96, "Cm", "Curium", "[247]", 7, 3, "Actinide"),
    (97, "Bk", "Berkelium", "[247]", 7, 3, "Actinide"),
    (98, "Cf", "Californium", "[251]", 7, 3, "Actinide"),
    (99, "Es", "Einsteinium", "[252]", 7, 3, "Actinide"),
    (100, "Fm", "Fermium", "[257]", 7, 3, "Actinide"),
    (101, "Md", "Mendelevium", "[258]", 7, 3, "Actinide"),
    (102, "No", "Nobelium", "[259]", 7, 3, "Actinide"),
    (103, "Lr", "Lawrencium", "[266]", 7, 3, "Actinide"),
    (104, "Rf", "Rutherfordium", "[267]", 7, 4, "Transition Metal"),
    (105, "Db", "Dubnium", "[270]", 7, 5, "Transition Metal"),
    (106, "Sg", "Seaborgium", "[269]", 7, 6, "Transition Metal"),
    (107, "Bh", "Bohrium", "[270]", 7, 7, "Transition Metal"),
    (108, "Hs", "Hassium", "[270]", 7, 8, "Transition Metal"),
    (109, "Mt", "Meitnerium", "[278]", 7, 9, "Transition Metal"),
    (110, "Ds", "Darmstadtium", "[281]", 7, 10, "Transition Metal"),
    (111, "Rg", "Roentgenium", "[281]", 7, 11, "Transition Metal"),
    (112, "Cn", "Copernicium", "[285]", 7, 12, "Post-Transition Metal"),
    (113, "Nh", "Nihonium", "[286]", 7, 13, "Post-Transition Metal"),
    (114, "Fl", "Flerovium", "[289]", 7, 14, "Post-Transition Metal"),
    (115, "Mc", "Moscovium", "[289]", 7, 15, "Post-Transition Metal"),
    (116, "Lv", "Livermorium", "[293]", 7, 16, "Post-Transition Metal"),
    (117, "Ts", "Tennessine", "[293]", 7, 17, "Halogen"),
    (118, "Og", "Oganesson", "[294]", 7, 18, "Noble Gas")
]

MAGNETIC_PROPERTIES = {
    # --- Ferromagnets (T_C >= 290 K) ---
    "Fe": {
        "classification": "Ferromagnet (T_C >= 290 K)",
        "transition_temp_k": 1043.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 1043 K",
        "ordering_type": "Ferromagnetic"
    },
    "Co": {
        "classification": "Ferromagnet (T_C >= 290 K)",
        "transition_temp_k": 1388.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 1388 K",
        "ordering_type": "Ferromagnetic"
    },
    "Ni": {
        "classification": "Ferromagnet (T_C >= 290 K)",
        "transition_temp_k": 627.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 627 K",
        "ordering_type": "Ferromagnetic"
    },
    "Gd": {
        "classification": "Ferromagnet (T_C >= 290 K)",
        "transition_temp_k": 292.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 292 K",
        "ordering_type": "Ferromagnetic"
    },

    # --- Antiferromagnet (T_N >= 290 K) ---
    "Cr": {
        "classification": "Antiferromagnet (T_N >= 290 K)",
        "transition_temp_k": 311.0,
        "transition_type": "Neel",
        "transition_str": "T_N = 311 K",
        "ordering_type": "Antiferromagnetic"
    },

    # --- Low-Temperature Magnetic Ordering (T_N/T_C < 290 K) ---
    "Mn": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 100.0,
        "transition_type": "Neel",
        "transition_str": "T_N = 100 K",
        "ordering_type": "Antiferromagnetic"
    },
    "Ce": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 12.5,
        "transition_type": "Neel",
        "transition_str": "T_N = 12.5 K",
        "ordering_type": "Antiferromagnetic"
    },
    "Nd": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 19.9,
        "transition_type": "Neel",
        "transition_str": "T_N = 19.9 K",
        "ordering_type": "Antiferromagnetic"
    },
    "Sm": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 14.8,
        "transition_type": "Neel",
        "transition_str": "T_N = 14.8 K",
        "ordering_type": "Antiferromagnetic"
    },
    "Eu": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 90.0,
        "transition_type": "Neel",
        "transition_str": "T_N = 90 K",
        "ordering_type": "Antiferromagnetic (Helical)"
    },
    "Tb": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 221.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 221 K",
        "ordering_type": "Ferromagnetic (T_N = 229 K)"
    },
    "Dy": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 85.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 85 K",
        "ordering_type": "Ferromagnetic (T_N = 179 K)"
    },
    "Ho": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 20.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 20 K",
        "ordering_type": "Ferromagnetic (T_N = 132 K)"
    },
    "Er": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 19.0,
        "transition_type": "Curie",
        "transition_str": "T_C = 19 K",
        "ordering_type": "Ferromagnetic (T_N = 85 K)"
    },
    "Tm": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 56.0,
        "transition_type": "Neel",
        "transition_str": "T_N = 56 K",
        "ordering_type": "Antiferromagnetic (T_C = 32 K)"
    },
    "Cm": {
        "classification": "Low-temperature magnetic ordering",
        "transition_temp_k": 52.0,
        "transition_type": "Neel",
        "transition_str": "T_N = 52 K",
        "ordering_type": "Antiferromagnetic"
    }
}

DIAMAGNETS = {
    "H", "He", "Be", "B", "C", "N", "F", "Ne",
    "Si", "P", "S", "Cl", "Ar",
    "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
    "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe",
    "Yb",
    "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn",
    "No",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
}

def determine_magnetic_props(symbol):
    if symbol in MAGNETIC_PROPERTIES:
        return MAGNETIC_PROPERTIES[symbol]
    if symbol in DIAMAGNETS:
        return {
            "classification": "Diamagnet",
            "transition_temp_k": None,
            "transition_type": None,
            "transition_str": None,
            "ordering_type": "Diamagnetic"
        }
    return {
        "classification": "Paramagnet",
        "transition_temp_k": None,
        "transition_type": None,
        "transition_str": None,
        "ordering_type": "Paramagnetic"
    }

def is_element_radioactive(z):
    return (z == 43) or (z == 61) or (z >= 84)

def build_database(output_path=None):
    elements_db = []
    for z, sym, name, mass, period, group, category in RAW_ELEMENTS:
        mag = determine_magnetic_props(sym)
        is_rad = is_element_radioactive(z)
        is_crit = sym in USGS_CRITICAL_MINERALS
        crit_name = USGS_CRITICAL_MINERALS.get(sym, None)
        
        entry = {
            "atomic_number": z,
            "symbol": sym,
            "name": name,
            "atomic_mass": mass,
            "period": period,
            "group": group,
            "category": category,
            "radioactive": is_rad,
            "usgs_critical_mineral": is_crit,
            "usgs_commodity_name": crit_name,
            "magnetic_classification": mag["classification"],
            "magnetic_ordering_type": mag["ordering_type"],
            "transition_temperature_k": mag["transition_temp_k"],
            "transition_temperature_type": mag["transition_type"],
            "transition_temperature_str": mag["transition_str"]
        }
        elements_db.append(entry)
    
    if output_path is None:
        from pathlib import Path
        output_path = Path(__file__).resolve().parent / "magnetic_elements_db.json"
    else:
        from pathlib import Path
        output_path = Path(output_path).resolve()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(elements_db, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully generated {output_path} with {len(elements_db)} elements.")
    
    class_counts = {}
    crit_count = 0
    rad_count = 0
    ordered_count = 0
    for e in elements_db:
        c = e["magnetic_classification"]
        class_counts[c] = class_counts.get(c, 0) + 1
        if e["usgs_critical_mineral"]:
            crit_count += 1
        if e["radioactive"]:
            rad_count += 1
        if e["transition_temperature_k"] is not None:
            ordered_count += 1
            print(f"  {e['symbol']:2s} ({e['name']:14s}, Z={e['atomic_number']:3d}): {e['magnetic_classification']} -> {e['transition_temperature_str']}")
            
    print("\nSummary Statistics:")
    print(f"Total elements: {len(elements_db)}")
    print(f"USGS Critical Minerals: {crit_count} (Expected: 50)")
    print(f"Radioactive elements: {rad_count} (Expected: 37)")
    print(f"Elements with transition temperatures: {ordered_count}")
    print("Classifications count:")
    for k, v in class_counts.items():
        print(f"  {k}: {v}")

    return elements_db

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate magnetic_elements_db.json for all 118 elements.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output JSON path (default: relative to script)")
    args = parser.parse_args()
    build_database(output_path=args.output)

