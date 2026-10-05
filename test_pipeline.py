#!/usr/bin/env python3
"""
test_pipeline.py

Clean-build integration test suite for the Magnetic Periodic Table pipeline.
Tests stage-specific JSON schemas, independent scientific fixtures,
and generated HTML assets in an isolated temporary environment.
"""

import json
import math
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_database import (
    AUDITED_MP_ELEMENTAL_IDS,
    GAS_SYMBOLS_AT_298K,
    LIQUID_SYMBOLS_AT_298K,
    RECOGNIZED_BIBLIOGRAPHIC_SOURCES,
)

WORKSPACE_DIR = Path(__file__).resolve().parent

# Independent fixtures for scientific verification
INDEPENDENT_ELEMENT_FIXTURES = {
    # Symbol: (Z, Name, MagClass, SpaceGroup, CrystalSystem, MP_ID, BulkMoment, NeutralAtomTerm, HundMoment)
    "Fe": (26, "Iron", "Ferromagnet (T_C >= 290 K)", "Im-3m", "BCC", "mp-13", 2.22, "^{5}\\mathrm{D}_{4}", 6.71),
    "Co": (27, "Cobalt", "Ferromagnet (T_C >= 290 K)", "P6_3/mmc", "HCP", "mp-102", 1.72, "^{4}\\mathrm{F}_{9/2}", 6.63),
    "Ni": (28, "Nickel", "Ferromagnet (T_C >= 290 K)", "Fm-3m", "FCC", "mp-23", 0.61, "^{3}\\mathrm{F}_{4}", 5.59),
    "Cr": (24, "Chromium", "Antiferromagnet (T_N >= 290 K)", "Im-3m", "BCC", "mp-90", 0.62, "^{7}\\mathrm{S}_{3}", 6.93),
    "Gd": (64, "Gadolinium", "Ferromagnet (T_C >= 290 K)", "P6_3/mmc", "HCP", "mp-155", 7.63, "^{9}\\mathrm{D}^\\circ_{2}", 6.53),
    "Dy": (66, "Dysprosium", "Low-temperature magnetic ordering", "P6_3/mmc", "HCP", "mp-1057889", 10.20, "^{5}\\mathrm{I}_{8}", 10.61),
    "Cu": (29, "Copper", "Diamagnet", "Fm-3m", "FCC", "mp-30", None, "^{2}\\mathrm{S}_{1/2}", 1.73),
    "Bi": (83, "Bismuth", "Diamagnet", "R-3m", "Rhombohedral", "mp-23155", None, "^{4}\\mathrm{S}^\\circ_{3/2}", 3.87),
    "Nd": (60, "Neodymium", "Low-temperature magnetic ordering", "P6_3/mmc", "DHCP", "mp-123", 2.20, "^{5}\\mathrm{I}_{4}", 2.68),
    "Sm": (62, "Samarium", "Low-temperature magnetic ordering", "R-3m", "Rhombohedral", "mp-68", 0.15, "^{7}\\mathrm{F}_{0}", 0.0),
    "Pt": (78, "Platinum", "Paramagnet", "Fm-3m", "FCC", "mp-126", None, "^{3}\\mathrm{D}_{3}", 4.62),
    "Au": (79, "Gold", "Diamagnet", "Fm-3m", "FCC", "mp-81", None, "^{2}\\mathrm{S}_{1/2}", 1.73),
    "Am": (95, "Americium", "Paramagnet", "P6_3/mmc", "DHCP", None, None, "^{8}\\mathrm{S}^\\circ_{7/2}", 7.94),
}

INDEPENDENT_ANOMALOUS_SHELLS = {
    "Cr": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d⁵ 4s¹",
    "Cu": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d¹⁰ 4s¹",
    "Mo": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d¹⁰ 4s² 4p⁶ 4d⁵ 5s¹",
    "Pd": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d¹⁰ 4s² 4p⁶ 4d¹⁰",
    "Ag": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d¹⁰ 4s² 4p⁶ 4d¹⁰ 5s¹",
    "Pt": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d¹⁰ 4s² 4p⁶ 4d¹⁰ 5s² 5p⁶ 4f¹⁴ 5d⁹ 6s¹",
    "Au": "1s² 2s² 2p⁶ 3s² 3p⁶ 3d¹⁰ 4s² 4p⁶ 4d¹⁰ 5s² 5p⁶ 4f¹⁴ 5d¹⁰ 6s¹",
}


class PipelineCleanBuildIntegrationTest(unittest.TestCase):
    """End-to-end clean pipeline execution and schema validation."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir_obj = tempfile.TemporaryDirectory()
        cls.tmp_dir = Path(cls.temp_dir_obj.name)
        cls.base_json = cls.tmp_dir / "magnetic_elements_db.json"
        cls.cryst_json = cls.tmp_dir / "magnetic_elements_crystallography.json"
        cls.enriched_json = cls.tmp_dir / "magnetic_elements_enriched.json"
        cls.html_out = cls.tmp_dir / "index.html"

        # 1. build_database.py
        res = subprocess.run(
            [sys.executable, str(WORKSPACE_DIR / "build_database.py"), "-o", str(cls.base_json)],
            capture_output=True, text=True
        )
        assert res.returncode == 0, f"build_database.py failed:\n{res.stderr}\n{res.stdout}"

        # 2. enrich_database.py
        res = subprocess.run(
            [sys.executable, str(WORKSPACE_DIR / "enrich_database.py"), "-i", str(cls.base_json), "-o", str(cls.cryst_json)],
            capture_output=True, text=True
        )
        assert res.returncode == 0, f"enrich_database.py failed:\n{res.stderr}\n{res.stdout}"

        # 3. enrich_magnetic_data.py
        res = subprocess.run(
            [sys.executable, str(WORKSPACE_DIR / "enrich_magnetic_data.py"), "-i", str(cls.cryst_json), "-o", str(cls.enriched_json)],
            capture_output=True, text=True
        )
        assert res.returncode == 0, f"enrich_magnetic_data.py failed:\n{res.stderr}\n{res.stdout}"

        # 4. build_interactive_table.py
        res = subprocess.run(
            [sys.executable, str(WORKSPACE_DIR / "build_interactive_table.py"), "-i", str(cls.enriched_json), "-o", str(cls.html_out)],
            capture_output=True, text=True
        )
        assert res.returncode == 0, f"build_interactive_table.py failed:\n{res.stderr}\n{res.stdout}"

        # Load datasets
        with open(cls.base_json, "r", encoding="utf-8") as f:
            cls.base_data = json.load(f)
        with open(cls.cryst_json, "r", encoding="utf-8") as f:
            cls.cryst_data = json.load(f)
        with open(cls.enriched_json, "r", encoding="utf-8") as f:
            cls.enriched_data = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir_obj.cleanup()

    def test_01_stage_validators_pass(self):
        """Verify that validate_database.py succeeds for all stages."""
        for mode, path in [
            ("base", self.base_json),
            ("crystallography", self.cryst_json),
            ("enriched", self.enriched_json),
        ]:
            res = subprocess.run(
                [sys.executable, str(WORKSPACE_DIR / "validate_database.py"), "--mode", mode, str(path)],
                capture_output=True, text=True
            )
            self.assertEqual(res.returncode, 0, f"Validator failed on mode {mode}:\n{res.stdout}\n{res.stderr}")
            self.assertIn("[PASS]", res.stdout)

    def test_02_element_counts_and_uniqueness(self):
        """All stages must contain exactly 118 unique elements Z=1..118."""
        for name, dataset in [("base", self.base_data), ("cryst", self.cryst_data), ("enriched", self.enriched_data)]:
            self.assertEqual(len(dataset), 118, f"{name} count != 118")
            z_set = {el["atomic_number"] for el in dataset}
            sym_set = {el["symbol"] for el in dataset}
            self.assertEqual(len(z_set), 118, f"{name} duplicate atomic numbers")
            self.assertEqual(len(sym_set), 118, f"{name} duplicate symbols")
            self.assertEqual(z_set, set(range(1, 119)))

    def test_03_critical_minerals_and_radioactivity(self):
        """Verify 50 USGS critical minerals and 37 radioactive elements."""
        for el in self.base_data:
            z = el["atomic_number"]
            sym = el["symbol"]
            is_rad = el["radioactive"]
            expected_rad = (z == 43 or z == 61 or z >= 84)
            self.assertEqual(is_rad, expected_rad, f"Radioactivity mismatch for {sym} (Z={z})")

        crit_count = sum(1 for el in self.base_data if el.get("usgs_critical_mineral"))
        self.assertEqual(crit_count, 50, f"USGS Critical mineral count != 50 (got {crit_count})")

    def test_04_electron_configuration_subshell_invariants(self):
        """Validate orbital subshell capacities and sum == Z in crystallography stage."""
        sup_map = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5, "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}
        cap = {"s": 2, "p": 6, "d": 10, "f": 14, "g": 18}

        for el in self.cryst_data:
            z = el["atomic_number"]
            sym = el["symbol"]
            cfg = el["electronic_configuration"]["full"]
            tokens = cfg.strip().split()
            seen_shells = set()
            total_elec = 0

            for tok in tokens:
                m = re.match(r"^(\d+)([spdfg])(\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹]+)$", tok)
                self.assertIsNotNone(m, f"Invalid subshell format '{tok}' in {sym}")
                n = int(m.group(1))
                orb = m.group(2)
                exp_str = m.group(3)
                cnt = int("".join(str(sup_map[c]) for c in exp_str)) if exp_str[0] in sup_map else int(exp_str)

                shell_key = f"{n}{orb}"
                self.assertNotIn(shell_key, seen_shells, f"Duplicate subshell '{shell_key}' in {sym}")
                seen_shells.add(shell_key)

                self.assertLessEqual(cnt, cap[orb], f"Subshell capacity exceeded in {sym}: {tok}")
                total_elec += cnt

            self.assertEqual(total_elec, z, f"Electrons {total_elec} != Z={z} in {sym}")

        # Test specific known anomalous configurations
        cryst_map = {el["symbol"]: el for el in self.cryst_data}
        for sym, expected_cfg in INDEPENDENT_ANOMALOUS_SHELLS.items():
            self.assertEqual(cryst_map[sym]["electronic_configuration"]["full"], expected_cfg, f"Anomalous shell mismatch for {sym}")

    def test_05_independent_scientific_fixtures(self):
        """Check independent physical and crystallographic parameters for selected elements."""
        enriched_map = {el["symbol"]: el for el in self.enriched_data}

        for sym, (z, name, mag_class, spg, cryst_sys, mp_id, bulk_mu, rs_term, hund_mu) in INDEPENDENT_ELEMENT_FIXTURES.items():
            el = enriched_map[sym]
            self.assertEqual(el["atomic_number"], z)
            self.assertEqual(el["name"], name)
            self.assertEqual(el["magnetic_classification"], mag_class)

            cryst = el["crystallography"]
            self.assertEqual(cryst["space_group_symbol"], spg)
            self.assertEqual(cryst["crystal_system"], cryst_sys)
            
            mp = el.get("materials_project", {})
            self.assertEqual(mp.get("material_id"), mp_id)

            adv_q = el["advanced_magnetism"]["quantum"]
            self.assertEqual(adv_q["term_symbol"], rs_term)

            # Bulk ordered moment check
            if bulk_mu is not None:
                self.assertAlmostEqual(adv_q["bulk_ordered_moment_mu_B"], bulk_mu, delta=0.02)
            else:
                self.assertIsNone(adv_q["bulk_ordered_moment_mu_B"])

            # Neutral gas-atom moment check
            self.assertAlmostEqual(adv_q["neutral_atom_moment_mu_B"], hund_mu, delta=0.02)

        # Comprehensive Materials Project elemental coverage enforcement
        assigned_mp_count = 0
        for el in self.enriched_data:
            sym = el["symbol"]
            mp = el.get("materials_project", {})
            mp_id = mp.get("material_id") if mp else None
            if sym in AUDITED_MP_ELEMENTAL_IDS:
                expected_mp = AUDITED_MP_ELEMENTAL_IDS[sym]
                self.assertEqual(mp_id, expected_mp, f"Materials Project ID mismatch for {sym}: expected {expected_mp}, got {mp_id}")
                self.assertEqual(mp.get("formula"), sym, f"Materials Project formula mismatch for {sym}")
                self.assertEqual(mp.get("url"), f"https://materialsproject.org/materials/{expected_mp}")
                assigned_mp_count += 1
            else:
                self.assertIsNone(mp_id, f"Non-audited element {sym} should have null Materials Project ID, got {mp_id}")

        self.assertEqual(assigned_mp_count, 79, f"Expected exactly 79 audited MP IDs, found {assigned_mp_count}")
        self.assertEqual(assigned_mp_count, len(AUDITED_MP_ELEMENTAL_IDS))

    def test_06_macroscopic_magnetism_invariants(self):
        """Verify susceptibility signs, saturation magnetization bounds, and ordered moments."""
        for el in self.enriched_data:
            sym = el["symbol"]
            mag_class = el["magnetic_classification"]
            adv_q = el["advanced_magnetism"]["quantum"]
            adv_t = el["advanced_magnetism"]["thermodynamic"]
            chi = adv_t["molar_susceptibility_298K"]
            ms = adv_t["saturation_magnetization_T"]
            bulk_mu = adv_q["bulk_ordered_moment_mu_B"]

            if mag_class == "Diamagnet":
                self.assertIsNotNone(chi, f"Diamagnet {sym} missing susceptibility")
                self.assertLess(chi, 0, f"Diamagnet {sym} must have chi_m < 0, got {chi}")
                self.assertIsNone(ms, f"Diamagnet {sym} should have no Ms")
                self.assertIsNone(bulk_mu, f"Diamagnet {sym} should have no bulk ordered moment")
            elif mag_class == "Paramagnet":
                self.assertIsNotNone(chi, f"Paramagnet {sym} missing susceptibility")
                self.assertGreater(chi, 0, f"Paramagnet {sym} must have chi_m > 0, got {chi}")
                self.assertIsNone(ms, f"Paramagnet {sym} should have no Ms")
                self.assertIsNone(bulk_mu, f"Paramagnet {sym} should have no bulk ordered moment")
            elif "Ferromagnet" in mag_class or "Antiferromagnet" in mag_class:
                self.assertIsNotNone(bulk_mu, f"Ordered element {sym} must have bulk ordered moment")
                self.assertGreater(bulk_mu, 0, f"Ordered element {sym} bulk moment must be > 0")

            if mag_class == "Ferromagnet (T_C >= 290 K)":
                self.assertIsNotNone(ms, f"RT Ferromagnet {sym} requires Ms")
                self.assertTrue(0.05 <= ms <= 3.5, f"RT Ferromagnet {sym} Ms out of range [0.05, 3.5]: {ms}")

            # Check explicit measurement condition metadata on saturation magnetization
            ms_cond = adv_t.get("saturation_magnetization_condition")
            ms_temp = adv_t.get("saturation_magnetization_temp_K")
            if sym in ("Fe", "Co", "Ni"):
                self.assertEqual(ms_cond, "at 298 K (Room Temperature)", f"{sym} condition mismatch")
                self.assertEqual(ms_temp, 298.15, f"{sym} temp mismatch")
            elif ms is not None:
                self.assertEqual(ms_cond, "at 4.2 K (Liquid Helium Cryogenic)", f"{sym} condition mismatch")
                self.assertEqual(ms_temp, 4.2, f"{sym} temp mismatch")
            else:
                self.assertIsNone(ms_cond, f"{sym} with ms=None should not have condition")
                self.assertIsNone(ms_temp, f"{sym} with ms=None should not have temp")

        # Explicit verification of Americium (Z=95) scope distinction
        el_am = [e for e in self.enriched_data if e["symbol"] == "Am"][0]
        self.assertEqual(el_am["magnetic_classification"], "Paramagnet")
        self.assertEqual(el_am["advanced_magnetism"]["quantum"]["term_symbol"], "^{8}\\mathrm{S}^\\circ_{7/2}")
        self.assertEqual(el_am["advanced_magnetism"]["quantum"]["neutral_atom_moment_mu_B"], 7.94)
        self.assertIsNone(el_am["advanced_magnetism"]["quantum"]["bulk_ordered_moment_mu_B"])
        self.assertEqual(el_am["advanced_magnetism"]["quantum"]["free_ion_state"]["term_symbol"], "^{7}\\mathrm{F}_0")
        self.assertEqual(el_am["advanced_magnetism"]["quantum"]["free_ion_state"]["effective_moment_mu_B"], 0.0)

    def test_07_technological_roles_and_alloy_contributions(self):
        """Verify functional alloy role mappings and canonical distribution."""
        canonical_map = {
            "Hard Magnetic Vector": "hard",
            "Soft Magnetic Core": "soft",
            "Magnetocaloric Active Element": "mce",
            "Magnetic Phase Stabilizer / Additive": "additive",
            "No primary commercial magnetic alloy role documented": "standard",
        }
        counts = {"hard": 0, "soft": 0, "mce": 0, "additive": 0, "standard": 0}

        for el in self.enriched_data:
            adv_tech = el["advanced_magnetism"]["technological"]
            role = adv_tech["magnet_role"]
            self.assertIn(role, canonical_map, f"Unknown magnet role '{role}' in {el['symbol']}")
            counts[canonical_map[role]] += 1

            contributions = adv_tech.get("functional_alloy_contributions")
            self.assertIsInstance(contributions, list, f"functional_alloy_contributions missing in {el['symbol']}")
            if role != "No primary commercial magnetic alloy role documented":
                self.assertGreater(len(contributions), 0, f"Expected non-empty functional contributions for role '{role}' in {el['symbol']}")

        self.assertEqual(counts["hard"], 8)
        self.assertEqual(counts["soft"], 5)
        self.assertEqual(counts["mce"], 5)
        self.assertEqual(counts["additive"], 5)
        self.assertEqual(counts["standard"], 95)

    def test_08_html_artifact_integrity(self):
        """
        Static verification of generated HTML artifact structure, schema, and embedded data.
        Note: This is a static markup, serialization, and contract verification test.
        Dynamic browser DOM interactions, event loops, focus trapping, and WebGL context
        initialization are exercised separately in headless runtime environments (Node.js/Playwright).
        """
        self.assertTrue(self.html_out.exists(), "index.html not created")
        self.assertFalse(self.html_out.is_symlink(), "index.html must be a real file, not a symlink")
        size_kb = self.html_out.stat().st_size / 1024
        self.assertGreater(size_kb, 500, f"HTML file size too small: {size_kb:.1f} KB")

        with open(self.html_out, "r", encoding="utf-8") as f:
            html = f.read()

        # Check embedded JSON
        self.assertIn('id="embedded-elements-data"', html)
        m = re.search(r'<script id="embedded-elements-data" type="application/json">(.*?)</script>', html, re.DOTALL)
        self.assertIsNotNone(m, "Embedded elements data block missing")
        parsed = json.loads(m.group(1).strip())
        self.assertEqual(len(parsed), 118, "Embedded dataset does not contain 118 elements")

        # Ensure external fetch does NOT silently override embedded data
        self.assertNotIn("fetch('magnetic_elements_enriched.json')", html)

        # Check Canvas 3D spin vector projection
        self.assertIn("tip3D_x = at.x + sx * tipLen", html)
        self.assertIn("pTip = project(tip3D_x, tip3D_y, tip3D_z)", html)

        # Check that auto-rotate pauses when container is hidden
        self.assertIn("container.offsetParent !== null", html)

        # Check presence of schematic disclaimer
        self.assertIn("Schematic Model Scope &amp; Physical Assumptions", html)

        # Check toolbar role options match actual emitted categories
        self.assertIn('<option value="Hard Magnetic Vector">Hard Magnetic Vector (8)</option>', html)
        self.assertIn('<option value="Soft Magnetic Core">Soft Magnetic Core (5)</option>', html)
        self.assertIn('<option value="Magnetocaloric Active Element">Magnetocaloric Active (5)</option>', html)
        self.assertIn('<option value="Magnetic Phase Stabilizer / Additive">Phase Stabilizer / Additive (5)</option>', html)
        self.assertIn('<option value="No primary commercial magnetic alloy role documented">No Commercial Magnetic Role (95)</option>', html)

        # Check Saturation Magnetization label
        self.assertIn('Saturation Magnetization (<span class="math-inline" data-latex="M_s"></span>)', html)
        self.assertNotIn('Saturation Magnetization (<span class="math-inline" data-latex="M_s"></span> at 0 K)', html)

    def test_09_property_level_provenance(self):
        """Verify presence, physical scope, and citations across all property-level provenance records."""
        req_keys = [
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
        for el in self.enriched_data:
            sym = el["symbol"]
            adv = el.get("advanced_magnetism", {})
            prov = adv.get("provenance_and_conditions")
            self.assertIsNotNone(prov, f"{sym} missing provenance_and_conditions")

            for k in req_keys:
                self.assertIn(k, prov, f"{sym} missing provenance entry '{k}'")
                entry = prov[k]
                self.assertIsInstance(entry, dict, f"{sym} provenance '{k}' must be dict")
                self.assertTrue(entry.get("physical_scope"), f"{sym} missing physical_scope for '{k}'")

            # Check citations for non-null physical values
            q = adv.get("quantum", {})
            t = adv.get("thermodynamic", {})
            if q.get("bulk_ordered_moment_mu_B") is not None:
                self.assertIsNotNone(prov["bulk_ordered_moment_mu_B"].get("source"), f"{sym} un-cited bulk moment")
            if t.get("molar_susceptibility_298K") is not None:
                self.assertIsNotNone(prov["molar_susceptibility_298K"].get("source"), f"{sym} un-cited susceptibility")
            if t.get("saturation_magnetization_T") is not None:
                self.assertIsNotNone(prov["saturation_magnetization_T"].get("source"), f"{sym} un-cited saturation magnetization")
            self.assertIsNotNone(prov["technological_role"].get("source"), f"{sym} un-cited technological role")

            # Verify physical_scope fidelity against thermodynamic state at 298.15 K
            chi_scope = prov["molar_susceptibility_298K"]["physical_scope"]
            if sym in GAS_SYMBOLS_AT_298K:
                self.assertEqual(chi_scope, "gas_phase_at_298K", f"Gas element {sym} scope mismatch")
            elif sym in LIQUID_SYMBOLS_AT_298K:
                self.assertEqual(chi_scope, "liquid_phase_at_298K", f"Liquid element {sym} scope mismatch")
            elif sym == "Gd":
                self.assertEqual(chi_scope, "bulk_solid_paramagnetic_at_298K", "Gd scope mismatch (paramagnetic above T_C=292 K)")
            elif sym in ("Fe", "Co", "Ni"):
                self.assertEqual(chi_scope, "bulk_solid_ferromagnetic_domain_state", f"Ferromagnetic element {sym} scope mismatch")

            # Verify saturation magnetization scope
            ms_scope = prov["saturation_magnetization_T"]["physical_scope"]
            if sym in ("Fe", "Co", "Ni"):
                self.assertEqual(ms_scope, "bulk_solid_ferromagnetic_at_298K")
            elif t.get("saturation_magnetization_T") is not None:
                self.assertEqual(ms_scope, "bulk_solid_ferromagnetic_cryogenic_at_4.2K")

            # Verify bibliographic sources adhere to recognized ontology
            for prop_k, prop_dict in prov.items():
                src = prop_dict.get("source")
                if src is not None:
                    self.assertIn(src, RECOGNIZED_BIBLIOGRAPHIC_SOURCES, f"Unrecognized source for {sym} [{prop_k}]: {src}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
