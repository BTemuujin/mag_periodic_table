# Magnetic Periodic Table & Critical Minerals Visualization (Full Scientific Handbook)

> 🚀 **Live Interactive Web Application**: [https://btemuujin.github.io/mag_periodic_table/](https://btemuujin.github.io/mag_periodic_table/)

A publication-grade scientific periodic table visualization that classifies all 118 chemical elements by their **intrinsic magnetic ground states**, **magnetic transition temperatures (Curie $T_C$ and Néel $T_N$)**, **USGS Critical Minerals designation**, and **radioactive stability**.

Inspired by the pioneering work of **Prof. J. M. D. Coey** and the Magnetism & Spin Electronics Group at **Trinity College Dublin**, combined with the official **United States Geological Survey (USGS) 2022 Critical Minerals** framework and **IUPAC / NIST** standards.

---

## Table of Contents
1. [Project Overview & Scientific Scope](#project-overview--scientific-scope)
2. [Visual Indicators & Classification Taxonomy](#visual-indicators--classification-taxonomy)
   - [Magnetic Classifications (Color Mapping)](#magnetic-classifications-color-mapping)
   - [Critical Minerals (Red Star ★)](#critical-minerals-red-star-)
   - [Radioactivity (Diagonal Hatching ///)](#radioactivity-diagonal-hatching-)
   - [Technological Role Classification](#technological-role-classification)
3. [File Inventory & Architecture](#file-inventory--architecture)
4. [Detailed Code Documentation](#detailed-code-documentation)
   - [`build_database.py`](#build_databasepy)
   - [`enrich_database.py`](#enrich_databasepy)
   - [`enrich_magnetic_data.py`](#enrich_magnetic_datapy)
   - [`generate_magnetic_table.py`](#generate_magnetic_tablepy)
   - [`build_interactive_table.py`](#build_interactive_tablepy)
   - [`interactive_table.html` & Web Application](#interactive_tablehtml--web-application)
5. [Magnetic Physics & Ordering Data Summary](#magnetic-physics--ordering-data-summary)
6. [USGS Critical Minerals Breakdown](#usgs-critical-minerals-breakdown)
7. [Scientific Provenance & Physical Conditions](#scientific-provenance--physical-conditions)
8. [Installation & Execution Guide](#installation--execution-guide)
9. [References & Citations](#references--citations)

---

## Project Overview & Scientific Scope

Standard periodic tables arrange chemical elements strictly according to atomic number and valence electron configurations. However, condensed matter physicists, materials scientists, and engineers frequently require immediate insight into an element's **cooperative magnetic behavior**, **quantum electronic moments**, and **geopolitical/industrial supply criticality**.

This project provides an end-to-end computational pipeline that:
1. **Aggregates and verifies** atomic, radioactive, economic, and magnetic data for all 118 elements from authoritative scientific references (IUPAC, NIST, USGS, Trinity College Dublin).
2. **Structures and standardizes** the dataset into a validated JSON database (`magnetic_elements_db.json`).
3. **Enriches** the database with crystallography, electronic configurations, and Materials Project DFT properties (`enrich_database.py`).
4. **Deepens magnetic metrics** across quantum, thermodynamic, spintronic, and technological domains (`enrich_magnetic_data.py`), generating `magnetic_elements_enriched.json`.
5. **Renders an ultra-high-resolution poster** (`magnetic_periodic_table.png` at 300 DPI, $8400 \times 5400\text{ px}$) implementing an 18-column grid with pulled-out Lanthanides and Actinides, two dedicated reference/legend boxes, and full scientific attributions.
6. **Compiles an interactive web application** (`interactive_table.html`) featuring client-side filtering, instant search, a 3D WebGL crystal structure/spin vector viewer, and a dedicated **Quantum & Advanced Magnetism** drawer tab with KaTeX mathematical formatting.

---

## Visual Indicators & Classification Taxonomy

### Magnetic Classifications (Color Mapping)
Each element cell is filled with a distinctive color corresponding to its cooperative magnetic ground state:

| Color | Classification | Definition & Physical Behavior | Representative Elements |
| :--- | :--- | :--- | :--- |
| **White** (`#FFFFFF`) | **Diamagnet** | Elements with fully paired electrons and negative magnetic susceptibility ($\chi < 0$); repelled weakly by an applied magnetic field. | Noble gases, halogens, Cu, Ag, Au, Zn, Cd, Hg, Pb, Bi |
| **Yellow** (`#FEF08A`) | **Paramagnet** | Elements with unpaired electrons and positive susceptibility ($\chi > 0$) that do not order spontaneously at any temperature; attracted weakly to magnetic fields. | Alkali metals, alkaline earth metals (except Be), Al, O₂, early transition metals |
| **Blue** (`#2563EB`) | **Ferromagnet** ($T_C \ge 290\text{ K}$) | Elements displaying spontaneous parallel alignment of atomic magnetic moments resulting in macroscopic net magnetization at room temperature ($T \ge 290\text{ K}$). | **Fe** ($1043\text{ K}$), **Co** ($1388\text{ K}$), **Ni** ($627\text{ K}$), **Gd** ($292\text{ K}$) |
| **Green** (`#16A34A`) | **Antiferromagnet** ($T_N \ge 290\text{ K}$) | Elements displaying spontaneous antiparallel sublattice alignment of magnetic moments resulting in zero net macroscopic magnetization at room temperature ($T \ge 290\text{ K}$). | **Cr** ($311\text{ K}$) |
| **Light Green** (`#86EFAC`) | **Low-Temperature Magnetic Ordering** ($T_N/T_C < 290\text{ K}$) | Elements that undergo spontaneous magnetic ordering (either ferromagnetic or antiferromagnetic / helical / conical) only below room temperature ($T < 290\text{ K}$). | **Mn** ($100\text{ K}$), **Ce** ($12.5\text{ K}$), **Nd** ($19.9\text{ K}$), **Sm** ($14.8\text{ K}$), **Eu** ($90\text{ K}$), **Tb** ($221\text{ K}$), **Dy** ($85\text{ K}$), **Ho** ($20\text{ K}$), **Er** ($19\text{ K}$), **Tm** ($56\text{ K}$), **Cm** ($52\text{ K}$) |

### Critical Minerals (Red Star ★)
- **Indicator**: A bold red star (`★`, `#DC2626`) rendered in the top-right corner of the cell.
- **Contrast Halo**: Employs a 2.0 pt white path stroke halo (`matplotlib.patheffects.withStroke`) to ensure sharp legibility against dark backgrounds (e.g., cobalt blue, forest green) as well as light backgrounds (white, yellow, mint green).
- **Criterion**: The element corresponds directly to or is the primary constituent of one of the **50 mineral commodities** on the official **2022 USGS Final List of Critical Minerals** (pursuant to the Energy Act of 2020).

### Radioactivity (Diagonal Hatching ///)
- **Indicator**: Diagonal slate-gray hatching (`///`, `alpha=0.45`, `#475569`) overlaid on the cell background.
- **Criterion**: Elements with **no stable primordial isotopes**. This encompasses:
  - Technetium ($Z = 43$, `Tc`)
  - Promethium ($Z = 61$, `Pm`)
  - All heavy elements with $Z \ge 84$ (Polonium `Po` through Oganesson `Og`, $Z = 118$).

### Documented Functional Alloy Contributions & Technological Roles
Elements are classified by their primary commercial and experimental roles in functional magnetic materials, accompanied by a multi-valued `functional_alloy_contributions` registry:
- **Hard Magnetic Vector (8)**: Elements essential for permanent magnets (e.g., Nd-Fe-B, Sm-Co), high-density magnetic recording, and coercivity pinning vectors. Characterized by high uniaxial magnetocrystalline anisotropy ($K_1$), large unquenched orbital angular momentum ($L$), or strong spin-orbit coupling: **Co, Pr, Nd, Sm, Tb, Dy, Pt, Bi**.
- **Soft Magnetic Core (5)**: Elements that provide high saturation magnetization ($M_s$) and low coercive field ($H_c$) for transformer cores, electric motor stators, inductors, and magnetic shielding: **Si, V, Fe, Ni, Mo**.
- **Magnetocaloric Active Element (5)**: Elements exhibiting giant isothermal magnetic entropy change ($\Delta S_{\mathrm{mag}}$) and adiabatic temperature change ($\Delta T_{\mathrm{ad}}$) near magnetic phase transitions, driving magnetic refrigeration: **Mn, Gd, Ho, Er, Tm**.
- **Magnetic Phase Stabilizer / Additive (5)**: Critical alloying additions enabling intermetallic phase nucleation, grain boundary pinning, high electrical resistivity, or glass-forming ability (e.g., in Nd-Fe-B, FINEMET, Alnico): **B, Al, Cu, Ga, Nb**.
- **Standard / Non-Magnetic Matrix (95)**: Elements without documented primary roles in commercial magnetic alloys, serving as structural substrates or baseline condensed matter.

---

## File Inventory & Architecture

```
/home/tbayaraa/projects/mag_periodic_table/
├── build_database.py             # Base data ingestion and verification script
├── magnetic_elements_db.json     # Base validated dataset of all 118 elements
├── enrich_database.py            # Deep enrichment engine (crystallography, Materials Project, bonding)
├── enrich_magnetic_data.py       # Quantum, thermodynamic, spintronic, and technological magnetic enrichment engine
├── magnetic_elements_enriched.json # Comprehensive 118-element JSON database with all physical & advanced magnetic parameters
├── generate_magnetic_table.py    # Matplotlib graphic rendering engine (poster PNG)
├── magnetic_periodic_table.png   # Ultra-high-resolution output poster (300 DPI)
├── build_interactive_table.py    # Web application compiler / HTML generator
├── interactive_table.html        # Interactive self-contained Periodic Table web application
├── index.html                    # GitHub Pages root web application entrypoint
└── README.md                     # Concise overview documentation
```

---

## Detailed Code Documentation

### `build_database.py`

#### Purpose
`build_database.py` is the data compiler responsible for aggregating raw chemical, physical, magnetic, and economic data for all 118 elements, verifying compliance against scientific rules, and writing the structured dataset to `magnetic_elements_db.json`.

#### Key Components & Logic
1. **USGS Critical Minerals Dictionary (`USGS_CRITICAL_MINERALS`)**:
   - Maps 50 chemical symbols to their official USGS mineral commodity names.
   - Handles multi-element commodities and elemental mineral forms, such as:
     - `Ba` $\rightarrow$ Barite
     - `C` $\rightarrow$ Graphite
     - `F` $\rightarrow$ Fluorspar
     - All 15 Lanthanides (`La` through `Lu`) $\rightarrow$ Rare Earth Elements (REEs)
     - Platinum Group Elements (`Ru`, `Rh`, `Pd`, `Ir`, `Pt`)
     - Battery metals (`Li`, `Co`, `Ni`, `Mn`, `Zn`)
2. **Raw Element Master Catalog (`RAW_ELEMENTS`)**:
   - Stores tuples of `(atomic_number, symbol, name, atomic_weight_str, period, group, category)`.
   - Incorporates standard IUPAC CIAAW atomic weights (e.g., `55.845` for Fe) and bracketed mass numbers of the longest-lived isotopes for unstable synthetic/radioactive elements (e.g., `[98]` for Tc, `[294]` for Og).
3. **Magnetic Ordering Dictionary (`MAGNETIC_PROPERTIES`)**:
   - Defines explicit transition data for all 16 ordering elements:
     - Fe: $T_C = 1043\text{ K}$ (Curie)
     - Co: $T_C = 1388\text{ K}$ (Curie)
     - Ni: $T_C = 627\text{ K}$ (Curie)
     - Gd: $T_C = 292\text{ K}$ (Curie)
     - Cr: $T_N = 311\text{ K}$ (Néel)
     - Mn: $T_N = 100\text{ K}$ (Néel)
     - Ce: $T_N = 12.5\text{ K}$ (Néel)
     - Nd: $T_N = 19.9\text{ K}$ (Néel)
     - Sm: $T_N = 14.8\text{ K}$ (Néel)
     - Eu: $T_N = 90\text{ K}$ (Néel)
     - Tb: $T_C = 221\text{ K}$ (Curie, with Néel transition at $229\text{ K}$)
     - Dy: $T_C = 85\text{ K}$ (Curie, with Néel transition at $179\text{ K}$)
     - Ho: $T_C = 20\text{ K}$ (Curie, with Néel transition at $132\text{ K}$)
     - Er: $T_C = 19\text{ K}$ (Curie, with Néel transition at $85\text{ K}$)
     - Tm: $T_N = 56\text{ K}$ (Néel, with Curie transition at $32\text{ K}$)
     - Cm: $T_N = 52\text{ K}$ (Néel)
4. **Diamagnetism Determination (`DIAMAGNETS`)**:
   - Explicit set of 45 diamagnets covering all closed-shell Noble gases, Halogens, group 11/12 metals (Cu, Ag, Au, Zn, Cd, Hg), and post-transition/metalloid p-block elements.
5. **Classification Resolver (`determine_magnetic_props`)**:
   - Assigns `Ferromagnet (T_C >= 290 K)`, `Antiferromagnet (T_N >= 290 K)`, or `Low-temperature magnetic ordering` if the element orders magnetically.
   - Falls back to `Diamagnet` if contained in `DIAMAGNETS`.
   - Defaults to `Paramagnet` otherwise.
6. **Radioactivity Filter (`is_element_radioactive`)**:
   - Applies the mathematical predicate: `(z == 43) or (z == 61) or (z >= 84)`.
7. **Validation & Integrity Assertion Suite**:
   - Validates that exactly 118 elements are processed.
   - Confirms exactly 50 USGS critical minerals.
   - Confirms exactly 37 radioactive elements.
   - Confirms 16 ordered magnetic elements (4 room-T ferromagnetic, 1 room-T antiferromagnetic, 11 low-T ordered).

---

### `enrich_database.py`

#### Purpose
`enrich_database.py` augments every entry in `magnetic_elements_db.json` with deep crystallographic, electronic, chemical, thermodynamic, and computed quantum mechanical parameters, producing `magnetic_elements_enriched.json`.

#### Data Enrichment Pipeline & Fields Added
1. **Crystallography & Space Group**:
   - `crystal_system`: Bravais lattice system (BCC, FCC, HCP, DHCP, Diamond cubic, Rhombohedral, Orthorhombic, Tetragonal, Monoclinic).
   - `space_group_symbol`: Hermann–Mauguin space group symbol (e.g., $Im\bar{3}m$, $Fm\bar{3}m$, $P6_3/mmc$).
   - `space_group_number`: International Tables space group number ($1$ to $230$).
   - `lattice_parameters`: Unit cell constants $a, b, c$ in Ångströms (Å) and angles $\alpha, \beta, \gamma$ in degrees (°).
2. **Electronic Configuration & Shell Structure**:
   - `abbreviated`: Noble gas core representation with superscript notation (e.g., `[Ar] 3d⁶ 4s²`).
   - `full`: Complete orbital occupancy list (e.g., `1s² 2s² 2p⁶ 3s² 3p⁶ 3d⁶ 4s²`).
   - `valence_electrons`: Number of valence electrons participating in bonding.
3. **Chemical & Bonding Properties**:
   - `electronegativity_pauling`: Pauling scale electronegativity value.
   - `bonding_preference`: Metallic, Covalent Network, Covalent Molecular, or van der Waals.
   - `common_oxidation_states`: Array of prominent oxidation numbers (e.g., `[+2, +3, +6]`).
   - `atomic_radius_pm`: Empirical atomic radius in picometers.
   - `covalent_radius_pm`: Empirical covalent radius in picometers.
4. **Materials Project Integration (`materials_project`)**:
   - Seamlessly checks for `MP_API_KEY` in environment variables; if found, queries `mp_api.client.MPRester` for computed ground-state structures.
    - Robust offline catalog fallback providing canonical ground-state Material IDs (e.g., `mp-13` for Fe, `mp-90` for Cr, `mp-155` for Gd, `mp-1057889` for Dy), direct URLs to Materials Project entries (`https://materialsproject.org/materials/mp-XX`), computed DFT densities, and band gaps.
5. **Thermodynamic & Physical Properties**:
   - `density_g_cm3`: Mass density at STP.
   - `melting_point_k` & `melting_point_c`: Melting temperature in Kelvin and Celsius.
   - `boiling_point_k` & `boiling_point_c`: Boiling temperature in Kelvin and Celsius.
   - `standard_state`: State of matter at 298.15 K and 1 atm (Solid, Liquid, Gas).

---

### `enrich_magnetic_data.py`

#### Purpose
`enrich_magnetic_data.py` merges `magnetic_elements_db.json` with advanced, quantitative magnetic parameters compiled from `mendeleev`, NIST Atomic Spectra Database (ASD), Materials Project API (`mp-api`), and authoritative solid-state physics reference tables (CRC Handbook of Chemistry and Physics, Landolt-Börnstein Group III: Condensed Matter, and Coey's *Magnetism and Magnetic Materials*). It outputs the unified, production database `magnetic_elements_enriched.json`.

#### Data Fields Added Across Domains (Strictly Magnetic)
1. **Quantum & Microscopic Parameters**:
   - `term_symbol`: Ground-state atomic term symbol formatted in clean LaTeX (e.g., `${}^{5}\mathrm{D}_4$` for Fe, `${}^{7}\mathrm{S}_3$` for Cr, `${}^{9}\mathrm{D}^\circ_2$` for Gd, `${}^{5}\mathrm{I}_8$` for Dy).
   - `term_symbol_clean`: Plain text fallback representation (e.g., `5D4`, `7S3`, `9D°2`, `5I8`).
   - `lande_g_factor`: Landé $g$-factor calculated according to Hund's coupling rules:
     $$g_J = 1 + \frac{J(J+1) + S(S+1) - L(L+1)}{2J(J+1)}$$
     (e.g., $1.500$ for Fe, $2.000$ for Cr, $2.667$ for Gd, $1.250$ for Dy; $0.000$ for closed-shell singlet ground states with $J=0$).
   - `atomic_moment_mu_B`: Ground-state magnetic moment in Bohr magnetons ($\mu_{\mathrm{B}}$) per atom (e.g., $2.22\ \mu_{\mathrm{B}}$ for Fe, $0.62\ \mu_{\mathrm{B}}$ for Cr, $7.63\ \mu_{\mathrm{B}}$ for Gd, $10.60\ \mu_{\mathrm{B}}$ for Dy).
2. **Thermodynamic & Macroscopic Magnetism**:
   - `molar_susceptibility_298K`: Experimental room-temperature molar magnetic susceptibility $\chi_{\mathrm{m}}$ at $298.15\text{ K}$ in $\text{cm}^3/\text{mol}$ (e.g., $+1.80 \times 10^{-4}\ \text{cm}^3/\text{mol}$ for Cr, $+0.120\ \text{cm}^3/\text{mol}$ for paramagnetic Gd at $298\text{ K}$, $+0.1035\ \text{cm}^3/\text{mol}$ for Dy; `null` for Fe, Co, and Ni due to domain wall hysteresis below $T_{\mathrm{C}}$).
   - `curie_weiss_temp_K`: Paramagnetic Curie-Weiss temperature $\theta_{\mathrm{CW}}$ in Kelvin (e.g., $+1093.0\text{ K}$ for Fe, $-1070.0\text{ K}$ for Cr, $+317.0\text{ K}$ for Gd, $+157.0\text{ K}$ for Dy; negative indicates antiferromagnetic exchange).
   - `saturation_magnetization_T`: Saturation magnetization $\mu_0 M_{\mathrm{s}}$ in Tesla:
     - Fe ($2.15\text{ T}$), Co ($1.76\text{ T}$), Ni ($0.61\text{ T}$): Measured at $298.15\text{ K}$ (ambient room temperature).
     - Gd ($2.06\text{ T}$), Dy ($2.63\text{ T}$), Ho ($3.87\text{ T}$), Tb ($3.00\text{ T}$), Er ($3.33\text{ T}$): Measured cryogenically at $4.2\text{ K}$ in liquid helium.
     - `null` for non-ferromagnetic states.
   - `magnetocrystalline_anisotropy_J_m3`: First-order uniaxial or cubic magnetocrystalline anisotropy energy density constant $K_1$ in $\text{J/m}^3$ (e.g., $+4.80 \times 10^4\ \text{J/m}^3$ for Fe, $+4.10 \times 10^5\ \text{J/m}^3$ for Co, $-1.20 \times 10^5\ \text{J/m}^3$ for Gd, $+1.10 \times 10^7\ \text{J/m}^3$ for Dy).
3. **Spintronics & Microscopic Interactions**:
   - `spin_polarization_percent`: Conduction electron spin polarization $P$ at the Fermi level $E_{\mathrm{F}}$ measured via Point-Contact Andreev Reflection (PCAR) or spin-polarized tunneling:
     $$P = \frac{N_\uparrow(E_{\mathrm{F}}) - N_\downarrow(E_{\mathrm{F}})}{N_\uparrow(E_{\mathrm{F}}) + N_\downarrow(E_{\mathrm{F}})} \times 100\%$$
     (e.g., $44.0\%$ for Fe, $42.0\%$ for Co, $45.0\%$ for Ni, $43.0\%$ for Cr, $43.0\%$ for Gd, $40.0\%$ for Dy).
   - `exchange_interaction`: Primary microscopic exchange mechanism (e.g., *Direct Exchange / Itinerant d-band Coupling*, *RKKY Indirect Exchange*, *Itinerant Spin-Density Wave / Direct Exchange*, *Pauli Paramagnetism*, or *Larmor Diamagnetism*).
4. **Technological Role & Functional Alloy Contributions**:
   - `magnet_role`: Primary strategic engineering classification:
     - `Hard Magnetic Vector`: Co, Pr, Nd, Sm, Tb, Dy, Pt, Bi (8 elements).
     - `Soft Magnetic Core`: Si, V, Fe, Ni, Mo (5 elements).
     - `Magnetocaloric Active Element`: Mn, Gd, Ho, Er, Tm (5 elements).
     - `Magnetic Phase Stabilizer / Additive`: B, Al, Cu, Ga, Nb (5 elements).
     - `No primary commercial magnetic alloy role documented`: All remaining 95 elements.
   - `functional_alloy_contributions`: Curated array detailing documented contributions across permanent magnets, soft cores, magnetocalorics, pinning centers, and amorphous alloy systems.

---

### `build_interactive_table.py`

#### Purpose
`build_interactive_table.py` is the compiler for the interactive web frontend. It reads `magnetic_elements_enriched.json`, embeds the full verified dataset directly into the document for offline reliability, integrates KaTeX for client-side LaTeX formula rendering, and writes `interactive_table.html`.

---

### `interactive_table.html` & Web Application

#### Purpose
A modern, self-contained interactive web application replicating the visual fidelity of `magnetic_periodic_table.png` with dynamic client-side filtering, instantaneous search, an interactive slide-out element inspection drawer, and real-time 3D crystallographic/spin visualization.

#### Key Features & Architecture
1. **Visual Fidelity & Grid Layout**:
   - 18-column CSS Grid layout faithfully matching the poster.
   - Group 3 placeholders (`57–71 / La–Lu` and `89–103 / Ac–Lr`) that link directly into the Lanthanide and Actinide series.
   - Pulled-out Lanthanides and Actinides positioned at the base under columns 4 through 18, with bold series label tags under columns 1–3.
   - Pixel-perfect color matching:
     - Diamagnet: White (`#FFFFFF`)
     - Paramagnet: Yellow (`#FEF08A`)
     - Ferromagnet: Blue (`#2563EB`)
     - Antiferromagnet: Green (`#16A34A`)
     - Low-Temperature Ordered: Light Green (`#86EFAC`)
   - Overlays: Crimson red star (`★`) for USGS Critical Minerals, diagonal hatch stripes for radioactive elements ($Z \ge 84$, Tc, Pm), and formatted mathematical subscripts ($T_{\mathrm{C}}$, $T_{\mathrm{N}}$).
2. **Interactive Top Cards**:
   - **Box 1 (Sample Cell)**: Features an interactive Dysprosium (`Dy`, 66) cell with callout pointers; clicking it opens the Dy inspection drawer directly.
   - **Box 2 (Legend & Magnetic Swatches)**: Swatches double as one-click filter triggers to isolate specific magnetic classes.
3. **Filter & Search Toolbar**:
   - Quick-toggle filter pills: `All Elements (118)`, `★ Critical Minerals (50)`, `Ferromagnets (4)`, `Antiferromagnets (1)`, `Low-Temp (11)`, `Radioactive (37)`.
   - **Technological Role Dropdown**: Filter instantaneously by `Hard Magnetic Vector (8)`, `Soft Magnetic Core (5)`, `Magnetocaloric Active (5)`, `Phase Stabilizer / Additive (5)`, or `No Commercial Magnetic Role (95)`.
   - **Crystal System Dropdown**: Full coverage across all 118 elements (BCC, FCC, HCP, DHCP, Diamond cubic, Rhombohedral, Orthorhombic, Tetragonal inc. BCT, Monoclinic, Hexagonal, Simple cubic, Cubic complex).
   - Instant search bar filtering across element symbol, full name, or atomic number with live match count.
4. **Slide-Out Element Detail Drawer**:
   - Fixed slide-over sidebar with backdrop blur, smooth slide-in transition, and keyboard navigation (`Escape` to close, `←` / `→` buttons to step through elements sequentially).
   - Dynamic 5-tab content architecture:
     - **Tab 1: Overview**: Magnetic classification, ordering type, critical transition temperature with Celsius conversion, USGS critical status, radioactivity assessment, and periodic position.
     - **Tab 2: Quantum & Advanced Magnetism**:
       - *Technological Role Hero Banner*: Distinctive colored badge (`Hard Magnetic Vector`, `Soft Magnetic Core`, `Magnetocaloric Active Element`, `Magnetic Phase Stabilizer / Additive`, or `No primary commercial magnetic alloy role documented`) with contextual engineering rationale.
       - *Quantum & Microscopic Parameters*: Ground-state term symbol rendered via KaTeX (e.g., $^{5}\mathrm{D}_4$), Landé $g$-factor ($g_J$), and atomic magnetic moment ($\mu_{\mathrm{B}}$ / atom).
       - *Thermodynamic & Macroscopic Magnetism*: Experimental room-temperature molar susceptibility ($\chi_{\mathrm{m}}$), paramagnetic Curie-Weiss temperature ($\theta_{\mathrm{CW}}$), saturation magnetization ($M_{\mathrm{s}}$ in Tesla with explicit measurement conditions), and magnetocrystalline anisotropy constant ($K_1$ in $\text{J/m}^3$).
       - *Spintronics & Microscopic Interactions*: Fermi-level spin polarization percentage ($P\%$) and primary microscopic exchange interaction mechanism.
     - **Tab 3: Crystallography & 3D Unit Cell**:
       - **Interactive 3D WebGL Viewer**: Powered by Three.js and OrbitControls (with HTML5 Canvas fallback). Features rotate (drag), zoom (scroll/pinch), pan (right-click), and auto-rotation.
       - **Performance & VRAM Lifecycle**: Automatic pausing of the render loop when the drawer/modal is closed or on a different tab, along with recursive Three.js geometry/material disposal (`dispose()`) on element switching to prevent GPU memory leaks.
       - **Magnetic Spin Vectors**:
         - *Ferromagnets* (Fe, Co, Ni, Gd, Dy, Tb, Ho, Er): 3D arrows composed of cylinder shafts and cone arrowheads pointing parallel along the easy magnetization axis $[001]$ in electric cyan (`#06B6D4`).
         - *Antiferromagnets* (Cr, Mn, Ce, Nd, Sm, Eu, Tm, Cm): Antiparallel 3D arrows on alternating sublattices (Sublattice A pointing Up in Cyan, Sublattice B pointing Down in Coral Red `#F43F5E`).
         - *Paramagnets & Diamagnets*: Clean crystal lattice (atomic spheres, coordination bonds, unit cell wireframe) with **no ordered spin vectors**.
       - **Interactive Controls**: Toggle spin vectors on/off (`🧲 Spins: ON/OFF`), toggle unit cell boundary box (`📦 Box: ON/OFF`), toggle auto-rotate (`🔄 Rotate: ON/OFF`), reset camera (`↺ Reset`), and expand to fullscreen (`⛶ Fullscreen`).
       - **Expandable Fullscreen 3D Modal**: Large-format 3D canvas with full controls, live lattice parameters ($a, b, c, \alpha, \beta, \gamma$), space group details, and physical magnetic configuration description.
       - **Crystallographic Data**: Crystal system, space group symbol and number, unit cell parameters, and direct external link to Materials Project (`mp-XX`).
     - **Tab 4: Electronic & Chemical**: Full and abbreviated configurations with orbital superscripts, valence electron count, Pauling electronegativity, oxidation state pills, and atomic/covalent radii.
     - **Tab 5: Physical / Thermal**: Standard state, density, melting point, and boiling point in both Kelvin and Celsius.
5. **Self-Contained & CORS-Safe**:
   - Embeds the full JSON dataset inside `<script id="embedded-elements-data" type="application/json">` while attempting an asynchronous `fetch('magnetic_elements_enriched.json')`. If the user opens `interactive_table.html` directly using a `file://` URI in modern browsers that enforce local CORS restrictions, the app falls back seamlessly to the embedded dataset with zero loss of functionality.

---

### `generate_magnetic_table.py`

#### Purpose
`generate_magnetic_table.py` is the visualization engine. It loads `magnetic_elements_db.json`, sets up a headless Matplotlib canvas, computes the exact coordinate layout of the periodic table, and exports the finished graphic to `magnetic_periodic_table.png`.

#### Centralized Control Parameter Section (`CONFIG`)
The top of `generate_magnetic_table.py` features a dedicated, modular **`CONFIG` dictionary** that provides instant control over all design and layout variables without modifying rendering logic:
- **`canvas`**: Figure width/height in inches, export DPI (300 DPI default), background color, axis limits, database input path, and image output destination.
- **`fonts`**: Font family specification (`sans-serif`, Helvetica, DejaVu Sans, etc.).
- **`font_sizes`**: Granular font-size controls for:
  - Element cells: `cell_symbol` (16.5 pt), `cell_number` (9.5 pt), `cell_weight` (7.8 pt), `cell_temp` (7.8 pt), `cell_star` (13.5 pt).
  - Axis and series labels: `group_numbers` (13.0 pt), `period_numbers` (14.0 pt), `series_labels` (12.0 pt), `placeholder_numbers` / `placeholder_symbols` (10.5 / 9.5 pt).
  - Header: `main_title` (32.0 pt), `subtitle` (13.5 pt).
  - Box 1 (Sample Cell): `box_header` (12.5 pt), `sample_cell_symbol` (28.0 pt), `sample_cell_number` (13.0 pt), `callout_text` (10.2 pt), `box1_note` (9.2 pt).
  - Box 2 (Legend): `legend_item_title` (10.0 pt), `legend_item_desc` (8.5 pt), `legend_indicator_text` (9.2 pt).
  - Footnote: `footnote` (10.0 pt).
- **`colors`**: Magnetic classification hex codes (White, Yellow, Blue, Green, Light Green), border strokes, font colors for dark/light cells, halo colors, star indicator colors, and box borders.
- **`geometry`**: Cell dimensions ($w=0.90, h=0.94$), border widths, hatching pattern/alpha, period Y-coordinates, and Box 1 / Box 2 positioning.
- **Coordinate Space**:
  - Horizontal ($X$): $-0.2$ to $19.8$ (accommodating 18 standard columns plus left/right margin padding).
  - Vertical ($Y$): $-0.6$ to $14.6$ (accommodating footer attributions, f-block rows, main table rows 1–7, legend cards, and title banner).
- **Cell Dimensions**: Width $w = 0.90$, Height $h = 0.92$.
- **Main Table Periods**:
  - Period 1: $Y = 11.20$
  - Period 2: $Y = 10.12$
  - Period 3: $Y = 9.04$
  - Period 4: $Y = 7.96$
  - Period 5: $Y = 6.88$
  - Period 6: $Y = 5.80$
  - Period 7: $Y = 4.72$
- **Pulled-Out f-Block Rows**:
  - Lanthanides ($57–71$): $Y = 3.25$, Columns $3.0$ to $17.0$.
  - Actinides ($89–103$): $Y = 2.15$, Columns $3.0$ to $17.0$.
  - Connected to Period 6/7 Column 3 placeholder cells (`57–71 / La–Lu` and `89–103 / Ac–Lr`) via dashed guide arrows.
- **Group Labels (1–18)**:
  - Columns 1, 2, and 13–18: Rendered above Period 1 at $Y = 12.28$.
  - Columns 3–12: Rendered directly above Period 4 transition metals at $Y = 9.04$, perfectly clearing the bottom edge of the legend boxes.
- **Period Labels (1–7)**:
  - Rendered along the left margin at $X = 0.55$, vertically aligned with the vertical center of each period row.

#### Cell Typographic Hierarchy
Within each individual element cell:
1. **Atomic Number**: Placed top-left ($X + 0.08, Y + h - 0.15$), 8.5 pt bold font (`#475569` on light cells, `#E2E8F0` on dark cells).
2. **USGS Critical Mineral Star**: Placed top-right ($X + w - 0.10, Y + h - 0.15$), 11.5 pt bold `★` in crimson red (`#DC2626`) with a 2 pt white stroke halo.
3. **Chemical Symbol**: Centered at $X + w/2$, $Y + 0.55h$ (or $Y + 0.48h$ if no transition temp), 14 pt heavy bold font.
4. **Standard Atomic Weight**: Centered below symbol at $Y + 0.33h$ (or $Y + 0.23h$), 6.8 pt font.
5. **Magnetic Transition Temperature**: Centered at $Y + 0.13$, 6.6 pt bold font in bright yellow (`#FEF08A` on dark cells) or dark crimson (`#B91C1C` on light cells).
6. **Radioactive Hatching**: Overlaid with a transparent `FancyBboxPatch` featuring `hatch='///'` and `alpha=0.45`.

#### Header & Explanatory Cards
- **Title Banner**: Located at $X = 3.0, Y = 14.15$:
  - Title: **"MAGNETIC PERIODIC TABLE"** (28 pt heavy bold sans-serif, `#0F172A`).
  - Subtitle: *"Magnetic Ground States, Critical Transition Temperatures, USGS Critical Minerals & Radioactivity"* (12 pt semibold, `#475569`).
- **Box 1 ("HOW TO READ EACH ELEMENT CELL")**:
  - Located at $X = [3.0, 7.4]$, $Y = [9.35, 13.00]$.
  - Features a magnified ($1.65 \times 1.80$ unit) sample cell of Dysprosium (`Dy`, $Z=66$).
  - Features 5 precision cyan callout arrows with labels:
    - *Atomic Number (66)*
    - *USGS Critical Mineral (★)*
    - *Atomic Symbol (Dy)*
    - *Standard Atomic Weight (162.50)*
    - *Transition Temp (Kelvin) ($T_{\mathrm{C}} = 85\text{ K}$)*
  - Bottom subtitle explaining diagonal hatching for radioactive elements ($Z \ge 84$, Tc, Pm).
- **Box 2 ("LEGEND & MAGNETIC CLASSIFICATION")**:
  - Located at $X = [7.65, 12.80]$, $Y = [9.35, 13.00]$.
  - Displays 5 physical color swatches (White, Yellow, Blue, Green, Light Green) with precise definitions and representative elements.
  - Displays sample indicators for the USGS Critical Mineral Red Star and the Radioactive Element Diagonal Hatching.
- **Footnote Attribution**:
  - Placed at $X = 0.55, Y = -0.15$ with 9 pt clean sans-serif text, attributing:
    1. Prof. J. M. D. Coey and the Magnetism & Spin Electronics Group, School of Physics, Trinity College Dublin.
    2. U.S. Geological Survey (USGS) 2022 List of 50 Critical Mineral Commodities.
    3. IUPAC CIAAW & NIST Physical Measurement Laboratory.

---

### `magnetic_elements_db.json`

The JSON database contains 118 records formatted with consistent schema:

```json
{
  "atomic_number": 26,
  "symbol": "Fe",
  "name": "Iron",
  "atomic_mass": "55.845",
  "period": 4,
  "group": 8,
  "category": "Transition Metal",
  "radioactive": false,
  "usgs_critical_mineral": false,
  "usgs_commodity_name": null,
  "magnetic_classification": "Ferromagnet (T_C >= 290 K)",
  "magnetic_ordering_type": "Ferromagnetic",
  "transition_temperature_k": 1043.0,
  "transition_temperature_type": "Curie",
  "transition_temperature_str": "T_C = 1043 K"
}
```

#### Field Specification
- `atomic_number` (`int`): Atomic number $Z$ ($1 \dots 118$).
- `symbol` (`str`): 1- to 3-letter IUPAC element symbol.
- `name` (`str`): Full English IUPAC name.
- `atomic_mass` (`str`): Standard atomic weight with conventional significant digits, or bracketed mass number `[A]` for radioactive elements.
- `period` (`int`): Period row in periodic table ($1 \dots 7$).
- `group` (`int`): IUPAC group column ($1 \dots 18$).
- `category` (`str`): IUPAC element classification (Alkali Metal, Transition Metal, Lanthanide, Actinide, etc.).
- `radioactive` (`bool`): `true` if the element has no stable primordial isotopes.
- `usgs_critical_mineral` (`bool`): `true` if designated in the 2022 USGS Critical Minerals list.
- `usgs_commodity_name` (`str` or `null`): The specific commodity name under the USGS 2022 list.
- `magnetic_classification` (`str`): One of the 5 standardized classes.
- `magnetic_ordering_type` (`str`): Physical magnetic ordering state (e.g. `Ferromagnetic`, `Antiferromagnetic`, `Antiferromagnetic (Helical)`).
- `transition_temperature_k` (`float` or `null`): Transition temperature in Kelvin.
- `transition_temperature_type` (`str` or `null`): `Curie` or `Neel`.
- `transition_temperature_str` (`str` or `null`): Human-readable formatted string (e.g., `T_C = 1043 K`, `T_N = 311 K`).

---

## Magnetic Physics & Ordering Data Summary

The table below compiles the 16 chemical elements that undergo cooperative magnetic ordering in their elemental solid state:

| $Z$ | Symbol | Element Name | Category | Classification | Transition Temperature | Ordering Type | USGS Critical? |
| :---: | :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| 24 | **Cr** | Chromium | 3d Transition Metal | **Antiferromagnet** ($T_N \ge 290\text{ K}$) | $T_N = 311\text{ K}$ | Incommensurate Spin Density Wave | **Yes (★)** |
| 25 | **Mn** | Manganese | 3d Transition Metal | **Low-Temp Magnetic Ordering** | $T_N = 100\text{ K}$ | Complex Antiferromagnetic ($\alpha\text{-Mn}$) | **Yes (★)** |
| 26 | **Fe** | Iron | 3d Transition Metal | **Ferromagnet** ($T_C \ge 290\text{ K}$) | $T_C = 1043\text{ K}$ | Ferromagnetic (BCC $\alpha\text{-Fe}$) | No |
| 27 | **Co** | Cobalt | 3d Transition Metal | **Ferromagnet** ($T_C \ge 290\text{ K}$) | $T_C = 1388\text{ K}$ | Ferromagnetic (HCP $\alpha\text{-Co}$) | **Yes (★)** |
| 28 | **Ni** | Nickel | 3d Transition Metal | **Ferromagnet** ($T_C \ge 290\text{ K}$) | $T_C = 627\text{ K}$ | Ferromagnetic (FCC) | **Yes (★)** |
| 58 | **Ce** | Cerium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_N = 12.5\text{ K}$ | Antiferromagnetic | **Yes (★)** |
| 60 | **Nd** | Neodymium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_N = 19.9\text{ K}$ | Antiferromagnetic | **Yes (★)** |
| 62 | **Sm** | Samarium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_N = 14.8\text{ K}$ | Antiferromagnetic | **Yes (★)** |
| 63 | **Eu** | Europium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_N = 90\text{ K}$ | Antiferromagnetic (Helical spiral) | **Yes (★)** |
| 64 | **Gd** | Gadolinium | Lanthanide (4f) | **Ferromagnet** ($T_C \ge 290\text{ K}$) | $T_C = 292\text{ K}$ | Ferromagnetic (HCP) | **Yes (★)** |
| 65 | **Tb** | Terbium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_C = 221\text{ K}$ | Ferromagnetic ($T_N = 229\text{ K}$) | **Yes (★)** |
| 66 | **Dy** | Dysprosium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_C = 85\text{ K}$ | Ferromagnetic ($T_N = 179\text{ K}$) | **Yes (★)** |
| 67 | **Ho** | Holmium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_C = 20\text{ K}$ | Ferromagnetic cone ($T_N = 132\text{ K}$) | **Yes (★)** |
| 68 | **Er** | Erbium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_C = 19\text{ K}$ | Ferromagnetic cone ($T_N = 85\text{ K}$) | **Yes (★)** |
| 69 | **Tm** | Thulium | Lanthanide (4f) | **Low-Temp Magnetic Ordering** | $T_N = 56\text{ K}$ | Antiferromagnetic ($T_C = 32\text{ K}$) | **Yes (★)** |
| 96 | **Cm** | Curium | Actinide (5f) | **Low-Temp Magnetic Ordering** | $T_N = 52\text{ K}$ | Antiferromagnetic (Radioactive) | No |

---

## USGS Critical Minerals Breakdown

The **50 mineral commodities** on the official 2022 USGS Critical Minerals List are distributed across the periodic table as follows:

1. **Rare Earth Elements (REEs - 15 elements)**:
   - All 15 lanthanides: `La`, `Ce`, `Pr`, `Nd`, `Pm`, `Sm`, `Eu`, `Gd`, `Tb`, `Dy`, `Ho`, `Er`, `Tm`, `Yb`, `Lu`.
   - Essential for high-field permanent magnets ($\text{Nd}_2\text{Fe}_{14}\text{B}$, $\text{SmCo}_5$, $\text{Sm}_2\text{Co}_{17}$), magneto-optical drives, phosphor materials, and lasers.
2. **Platinum Group Metals (PGMs - 5 elements)**:
   - `Ru`, `Rh`, `Pd`, `Ir`, `Pt`.
   - Crucial for chemical catalysts, magnetic recording heads, and spintronic devices.
3. **Magnetic & Structural 3d Transition Metals**:
   - `Sc`, `Ti`, `V`, `Cr`, `Mn`, `Co`, `Ni`, `Zn`.
   - Critical for high-strength aerospace alloys, batteries, and permanent magnet matrices.
4. **Refractory & High-Tech Transition Metals**:
   - `Y`, `Zr`, `Nb`, `Mo`, `Hf`, `Ta`, `W`.
   - Key for superalloys, semiconductors, superconducting magnets, and electronics.
5. **Semiconductor, Photovoltaic & Post-Transition Elements**:
   - `Al`, `Ga`, `Ge`, `As`, `In`, `Sn`, `Sb`, `Te`, `Bi`.
   - Indispensable for integrated circuits, thermoelectric converters, and high-frequency RF devices.
6. **Alkali & Alkaline Earth Commodities**:
   - `Li`, `Rb`, `Cs` (Alkali metals for batteries and atomic clocks).
   - `Be`, `Mg` (Alkaline earth metals for lightweight structural aerospace alloys).
   - `Ba` (for Barite, vital for petroleum drilling fluids and radiation shielding).
7. **Nonmetallic Commodities**:
   - `C` (Graphite, essential for lithium-ion battery anodes).
   - `F` (Fluorspar, essential for steelmaking, fluorochemicals, and electrolytes).

---

## Scientific Provenance & Physical Conditions

To ensure academic and engineering reliability, this project enforces strict boundaries between isolated-atom properties, bulk solid-state measurements, and computed DFT parameters:

1. **Isolated-Atom Spectroscopic vs. Solid-State Condensed-Matter Properties**:
   - **Term symbols** ($^{2S+1}L_J$) and **Landé $g$-factors** ($g_J$) represent free, isolated neutral atoms in the gas phase from the NIST Atomic Spectra Database (ASD).
   - **Crystal systems**, **space groups**, **lattice parameters** ($a, b, c, \alpha, \beta, \gamma$), and **magnetic ordering transitions** ($T_{\mathrm{C}}, T_{\mathrm{N}}$) reflect the thermodynamic ground-state solid at ambient pressure (or zero-temperature ground states for elemental crystals).
   - **Americium ($Z = 95$) Physical Scope Contrast**: In the isolated neutral gas phase, atomic Americium has a half-filled $5f^7 7s^2$ shell with an $^{8}\mathrm{S}^\circ_{7/2}$ ground state ($\mu_{\mathrm{eff}} = 7.94\,\mu_B$). In the condensed bulk metallic phase, Americium undergoes valence hybridization to adopt a trivalent $5f^6$ core with a non-magnetic $J=0$ ($^{7}\mathrm{F}_0$) singlet ground state, displaying temperature-independent Van Vleck paramagnetism with zero spontaneous ordering ($\mu_{\mathrm{ord}} = 0\,\mu_B$). Both states are explicitly distinguished and documented.

2. **Magnetic Susceptibility, 290 K Classification Threshold, & 298.15 K Ambient Conditions**:
   - **Classification Threshold ($T_{\mathrm{C}} \ge 290\text{ K}$)**: The magnetic classification boundary follows solid-state physics conventions (Coey 2010), grouping elements with Curie temperatures near ambient into `Ferromagnet (T_C >= 290 K)`. This groups Fe ($1043\text{ K}$), Co ($1388\text{ K}$), Ni ($627\text{ K}$), and Gd ($292.0\text{ K}$) together as the four ambient elemental ferromagnets.
   - **Molar Susceptibility at Standard Ambient Temperature ($298.15\text{ K}$)**: Tabulated molar susceptibilities ($\chi_m$) strictly adhere to standard laboratory conditions ($T = 298.15\text{ K} = 25.0^\circ\text{C}, P = 1\text{ atm}$):
     - **Gadolinium ($Z = 64, T_{\mathrm{C}} = 292.0\text{ K}$)**: Because $298.15\text{ K} > 292.0\text{ K}$, bulk elemental Gadolinium is in its **paramagnetic state** at standard room temperature. It therefore possesses a well-defined, linear, positive paramagnetic molar susceptibility ($\chi_m = +0.120\text{ cm}^3/\text{mol}$, Landolt-Börnstein Group III/19a) and is explicitly annotated as `bulk_solid_paramagnetic_at_298K`. Its saturation magnetization ($M_s = 2.06\text{ T}$) is measured in its low-temperature ferromagnetic phase at $4.2\text{ K}$.
     - **Ferromagnets below $T_{\mathrm{C}}$ (Fe, Co, Ni)**: For Fe, Co, and Ni, standard room temperature ($298.15\text{ K}$) is well below $T_{\mathrm{C}}$. Magnetization occurs via domain wall displacement and rotation, yielding severe field-dependent hysteresis. A single linear susceptibility is physically undefined and set to `null` with physical scope `bulk_solid_ferromagnetic_domain_state`. Above $T_{\mathrm{C}}$, high-temperature paramagnetic behavior is parameterized by Curie-Weiss temperatures ($\theta_{\mathrm{CW}}$).
     - **Thermodynamic Phase Scopes**: Physical states at $298.15\text{ K}$ are rigorously segregated across all 118 elements:
       - `gas_phase_at_298K`: 11 elemental gases (H, He, N, O, F, Ne, Cl, Ar, Kr, Xe, Rn).
       - `liquid_phase_at_298K`: 2 elemental liquids (Br, Hg).
       - `bulk_solid_at_298K`: Remaining 103 solid elements.
   - **Saturation Magnetization ($M_s$) Measurement Temperatures**:
     - Fe ($2.15\text{ T}$), Co ($1.76\text{ T}$), Ni ($0.61\text{ T}$): Measured at $298.15\text{ K}$ (`bulk_solid_ferromagnetic_at_298K`).
     - Gd ($2.06\text{ T}$), Dy ($2.63\text{ T}$), Ho ($3.87\text{ T}$), Tb ($3.00\text{ T}$), Er ($3.33\text{ T}$): Measured cryogenically at $4.2\text{ K}$ (`bulk_solid_ferromagnetic_cryogenic_at_4.2K`).
     - Non-ferromagnetic elements: `null` (not spontaneously magnetized).
   - **Bibliographic Citations**: Every non-null property in `provenance_and_conditions` is mapped to an authoritative, peer-reviewed source or standard reference handbook (NIST ASD, CRC Handbook 97th ed., Landolt-Börnstein Group III/19a, Coey 2010, Materials Project v2024.1, Soulen et al. Science 1998, or USGS 2022).

3. **Schematic 3D Unit Cell & Magnetic Spin Orientation Modeling**:
   - The 3D viewer is an idealized, pedagogical schematic model with aspect-ratio-scaled dimensions and directional spin moments, designed for structural intuition rather than unconstrained crystallographic diffraction refinement.
   - For elements with complex or non-collinear ordering (such as $\alpha$-Mn with 58 atoms/cell, Cr incommensurate spin-density waves, or Dy/Ho/Tb helical/conical modulations), the model illustrates the primary sublattice spin orientations and carries prominent scientific disclaimers in the viewer.

4. **Self-Contained Embedded Dataset & CDN Assets**:
   - The entire 118-element dataset is 100% embedded offline in `interactive_table.html` (zero CORS or external API calls required for complete data access).
   - High-fidelity 3D graphics (Three.js) and formula rendering (KaTeX) load from trusted CDNs when online, falling back gracefully to an embedded 2D HTML5 Canvas projection when offline.

5. **Reproducibility & Offline Determinism**:
   - All enrichment scripts are 100% deterministic and run completely offline using curated, verified reference data without network or API dependencies. Live API querying can be explicitly requested via `--online` flags or by supplying `MP_API_KEY`.

---

## Installation & Execution Guide

### Prerequisites
The pipeline requires Python 3.8+ and standard scientific packages (`matplotlib`, `pillow`):

```bash
pip install matplotlib pillow
```

### Master One-Click Build Pipeline (Recommended)
You can run the entire multi-stage scientific generation, enrichment, validation, and rendering pipeline with a single master command:

```bash
cd /home/tbayaraa/projects/mag_periodic_table
python3 build_all.py
```

Optional flags for `build_all.py`:
- `--skip-image`: Skip generating the 300-DPI Matplotlib PNG graphic (faster builds).
- `--skip-validation`: Skip intermediate scientific validation audits.
- `--clean`: Remove intermediate and compiled files prior to building.

---

### Step-by-Step Build Pipeline
Alternatively, execute the individual pipeline stages sequentially:

```bash
cd /home/tbayaraa/projects/mag_periodic_table

# Step 1: Base database generation & classification (118 elements)
python3 build_database.py -o magnetic_elements_db.json

# Step 2: Scientific validation of base dataset
python3 validate_database.py --mode base magnetic_elements_db.json

# Step 3: Crystallography, electron configurations & Materials Project enrichment
python3 enrich_database.py -i magnetic_elements_db.json -o magnetic_elements_crystallography.json

# Step 4: Scientific validation of crystallographic dataset
python3 validate_database.py --mode crystallography magnetic_elements_crystallography.json

# Step 5: Quantum, thermodynamic, spintronic & technological magnetic enrichment
python3 enrich_magnetic_data.py -i magnetic_elements_crystallography.json -o magnetic_elements_enriched.json

# Step 6: Full scientific validation of enriched dataset
python3 validate_database.py --mode enriched magnetic_elements_enriched.json

# Step 7: Compile interactive web application
python3 build_interactive_table.py -i magnetic_elements_enriched.json -o interactive_table.html

# Step 8: Render ultra-high-resolution poster (300 DPI)
python3 generate_magnetic_table.py -i magnetic_elements_enriched.json -o magnetic_periodic_table.png
```

### Dataset Validation & Integrity Audit
The audit verifies IUPAC names and symbols for $Z \in [1, 118]$, orbital electron configuration sums ($\sum e^- = Z$), official USGS 50 critical mineral commodities (including Tm, without duplicate Ni), radioisotopes, and vetted Materials Project elemental formula ground truth:

```bash
python3 validate_database.py --mode enriched magnetic_elements_enriched.json
```

Expected output:
```text
==============================================================================
RUNNING SCIENTIFIC VALIDATION AUDIT (Mode: ENRICHED): magnetic_elements_enriched.json
Target Path: /home/tbayaraa/projects/mag_periodic_table/magnetic_elements_enriched.json
==============================================================================
Elements audited:       118 / 118
USGS Critical Minerals: 50 / 50 verified
Radioactive Elements:   37 / 37 verified
Vetted MP IDs assigned: 79
Technological Roles:    Hard=8, Soft=5, MCE=5, Additive=5, Standard=95

[PASS] All structural, schema, and specified scientific consistency checks passed successfully!
==============================================================================
```

### Testing & Verification Framework
The project maintains two distinct testing tiers covering data invariants, scientific consistency, and client-side logic:

1. **Clean Integration & Scientific Invariant Test Suite** (`python3 test_pipeline.py`):
   - Executes a clean, end-to-end multi-stage pipeline build in an isolated temporary directory.
   - Audits all 118 elements across base, crystallographic, and enriched stages.
   - Enforces 100% coverage of the 79 curated Materials Project elemental ground states (`AUDITED_MP_ELEMENTAL_IDS`), ensuring no audited element is missing and no unauthorized ID is assigned.
   - Validates electron configuration orbital capacities, Hund's rule coupling moments, macroscopic thermodynamic signs, and property-level physical scopes (`gas_phase_at_298K`, `liquid_phase_at_298K`, `bulk_solid_at_298K`, `bulk_solid_paramagnetic_at_298K`, and domain state).
   - Validates recognized peer-reviewed bibliographic citations.
   - Inspects the static artifact structure, schema, embedded dataset, and LaTeX markup of `interactive_table.html`.

   ```bash
   python3 test_pipeline.py
   ```

2. **Headless Client Logic Test Suite** (`node test_interactive_logic.js`):
   - Deserializes and parses the embedded JSON dataset directly from `interactive_table.html`.
   - Validates client-side classification and category mapping algorithms.
   - Verifies dynamic role tallies (`Hard=8`, `Soft=5`, `MCE=5`, `Additive=5`, `None=95`).
   - Verifies `formatChi(val, elem)` formatting, including gas/liquid annotations, Gd paramagnetic notes, and Fe domain hysteresis notes.
   - Verifies 3D crystal lattice coordinate math and magnetic spin vector projections for BCC, FCC, and HCP crystal systems.

   ```bash
   node test_interactive_logic.js
   ```

*Note on Graphical Testing*: WebGL context creation, Canvas pixel rendering, and browser event listeners require a web browser runtime (such as Chrome or Firefox) and cannot be fully emulated in headless environments without graphical display drivers.

### Output File Details
- **`magnetic_periodic_table.png`**: $8400 \times 5400\text{ pixels}$, 300 DPI, RGBA PNG (~2.0 MB).
- **`interactive_table.html`**: Standalone, accessible web application with embedded dataset fallback, Three.js 3D crystal lattice & spin vector viewer with full 2D Canvas fallback parity, KaTeX formulas, dialog focus-trapping (`inert`), and dynamic multi-criteria filtering (~900 KB).
- **`magnetic_elements_enriched.json`**: Complete, validated 118-element database with separated free-atom moments ($\mu_{\mathrm{eff}}$) and bulk ordered moments ($\mu_{\mathrm{ord}}$ at $0\text{ K}$), intrinsic ground states, and functional alloy role rationales.

### Launch & View Interactive Web Application
You can view the interactive periodic table in any web browser using either of two convenient methods:

#### Option A: Local Development Server
Run Python's built-in HTTP server:
```bash
python3 -m http.server 8000
```
Then open your web browser to:
[http://localhost:8000](http://localhost:8000)

#### Option B: Direct Browser Viewing (Offline / Zero-Server)
Since `interactive_table.html` is 100% self-contained with embedded JSON data fallback, you can open it directly from the local file system without needing a running server:
```bash
# On Linux:
xdg-open /home/tbayaraa/projects/mag_periodic_table/interactive_table.html

# Or open file:///home/tbayaraa/projects/mag_periodic_table/interactive_table.html in Chrome/Firefox
```

---

## References & Citations

1. **Magnetic Properties & Ordering Concept**:
   - Coey, J. M. D. (2010). *Magnetism and Magnetic Materials*. Cambridge University Press.
   - Prof. J. M. D. Coey & the Magnetism & Spin Electronics Group, School of Physics, Trinity College Dublin ([tcd.ie/Physics/Magnetism](https://www.tcd.ie/Physics/Magnetism/)).
2. **Critical Minerals Designation**:
   - U.S. Geological Survey (2022). *2022 Final List of Critical Minerals*. Federal Register, Vol. 87, No. 37, pp. 10381–10382; Energy Act of 2020 (Public Law 116-260).
   - USGS National Minerals Information Center: [usgs.gov/centers/national-minerals-information-center](https://www.usgs.gov/centers/national-minerals-information-center).
3. **Atomic Data & Standards**:
   - IUPAC Commission on Isotopic Abundances and Atomic Weights (CIAAW), *Standard Atomic Weights of the Elements*.
   - National Institute of Standards and Technology (NIST), *Physical Measurement Laboratory: Ground Levels and Ionization Energies for the Neutral Atoms*.
4. **Solid-State Physics & Thermodynamic Reference Tables**:
   - Haynes, W. M., ed. (2016). *CRC Handbook of Chemistry and Physics* (97th ed.). CRC Press / Taylor & Francis Group (Molar Magnetic Susceptibility of the Elements and Inorganic Compounds).
   - Landolt-Börnstein: *Numerical Data and Functional Relationships in Science and Technology*, New Series, Group III: Condensed Matter, Vol. 19: *Magnetic Properties of Metals and Alloys*, Springer-Verlag.
   - Jain, A., et al. (2013). *Commentary: The Materials Project: A materials genome approach to accelerating materials innovation*. APL Materials, 1(1), 011002. [materialsproject.org](https://materialsproject.org).
