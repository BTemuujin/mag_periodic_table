#!/usr/bin/env python3
"""
build_all.py

Master Build Pipeline for the Magnetic Periodic Table Project.
Executes the reproducible, end-to-end scientific pipeline:

  1. build_database.py
     Generates base elemental dataset with IUPAC symbols, atomic weights,
     radioactivity, USGS Critical Minerals, and magnetic ground-state classifications.
  2. validate_database.py (--mode base)
     Performs IUPAC symbol/name consistency, USGS 50-commodity check, and radioactivity check.
  3. enrich_database.py
     Enriches elements with crystal systems, space groups, lattice parameters,
     electron configurations, and vetted Materials Project elemental ground-state IDs.
  4. validate_database.py (--mode crystallography)
     Verifies subshell electron configuration sums (sum == Z), crystal parameters, and MP IDs.
  5. enrich_magnetic_data.py
     Adds quantum term symbols, Landé g-factors, free-atom vs. bulk-ordered moments,
     molar susceptibilities, Curie-Weiss temperatures, and technological alloy roles.
  6. validate_database.py (--mode enriched)
     Ensures all 118 records have complete quantum parameters, physical susceptibility signs,
     and verified technological role counts.
  7. build_interactive_table.py
     Generates the interactive single-page web app with 3D crystal lattice & spin visualizer.
  8. generate_magnetic_table.py
     Renders the publication-grade 300-DPI periodic table graphic (PNG).

Usage:
  python3 build_all.py
  python3 build_all.py --skip-image
  python3 build_all.py --skip-validation
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent

def run_step(description: str, cmd: list, env=None) -> None:
    print(f"\n{'='*70}")
    print(f"▶ STEP: {description}")
    print(f"  Command: {' '.join(str(c) for c in cmd)}")
    print(f"{'='*70}")
    t0 = time.time()
    res = subprocess.run(cmd, cwd=WORKSPACE_DIR, env=env)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"\n❌ [FAILED] Step '{description}' failed with exit code {res.returncode}")
        sys.exit(res.returncode)
    print(f"✔ [DONE] Completed in {elapsed:.2f}s")

def main():
    parser = argparse.ArgumentParser(
        description="Execute complete Magnetic Periodic Table build pipeline."
    )
    parser.add_argument(
        "--skip-image",
        action="store_true",
        help="Skip rendering the high-resolution Matplotlib PNG image"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip intermediate and final scientific validation audits"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove intermediate JSON files prior to building"
    )
    args = parser.parse_args()

    base_db = WORKSPACE_DIR / "magnetic_elements_db.json"
    cryst_db = WORKSPACE_DIR / "magnetic_elements_crystallography.json"
    enriched_db = WORKSPACE_DIR / "magnetic_elements_enriched.json"
    html_out = WORKSPACE_DIR / "interactive_table.html"
    png_out = WORKSPACE_DIR / "magnetic_periodic_table.png"

    if args.clean:
        print("Cleaning generated files...")
        for p in [cryst_db, enriched_db, html_out, png_out]:
            if p.exists():
                p.unlink()
                print(f"  Removed: {p.name}")

    start_total = time.time()

    # Step 1: Base database
    run_step(
        "Generate Base Magnetic Elements Database",
        [sys.executable, "build_database.py", "-o", str(base_db)]
    )

    # Step 2: Validate base database
    if not args.skip_validation:
        run_step(
            "Validate Base Database",
            [sys.executable, "validate_database.py", "--mode", "base", str(base_db)]
        )

    # Step 3: Enrich crystallography
    run_step(
        "Enrich Elements with Crystallography & Electronic Configurations",
        [sys.executable, "enrich_database.py", "-i", str(base_db), "-o", str(cryst_db)]
    )

    # Step 4: Validate crystallography
    if not args.skip_validation:
        run_step(
            "Validate Crystallography & Electronic Configuration Database",
            [sys.executable, "validate_database.py", "--mode", "crystallography", str(cryst_db)]
        )

    # Step 5: Enrich quantum & advanced magnetism
    run_step(
        "Enrich Elements with Quantum Parameters & Technological Roles",
        [sys.executable, "enrich_magnetic_data.py", "-i", str(cryst_db), "-o", str(enriched_db)]
    )

    # Step 6: Validate enriched database
    if not args.skip_validation:
        run_step(
            "Validate Fully Enriched Database",
            [sys.executable, "validate_database.py", "--mode", "enriched", str(enriched_db)]
        )

    # Step 7: Build interactive web application
    run_step(
        "Build Interactive Web Application (interactive_table.html)",
        [sys.executable, "build_interactive_table.py", "-i", str(enriched_db), "-o", str(html_out)]
    )

    # Step 8: Generate high-resolution graphic
    if not args.skip_image:
        run_step(
            "Render Publication-Grade Periodic Table PNG (300 DPI)",
            [sys.executable, "generate_magnetic_table.py", "-i", str(enriched_db), "-o", str(png_out)]
        )

    total_elapsed = time.time() - start_total
    print(f"\n{'='*70}")
    print(f"🎉 BUILD PIPELINE COMPLETED SUCCESSFULLY in {total_elapsed:.2f}s!")
    print(f"  - Database:    {enriched_db.name} ({enriched_db.stat().st_size / 1024:.1f} KB)")
    print(f"  - Web App:     {html_out.name} & index.html ({html_out.stat().st_size / 1024:.1f} KB)")
    if not args.skip_image and png_out.exists():
        print(f"  - PNG Graphic: {png_out.name} ({png_out.stat().st_size / (1024*1024):.2f} MB)")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
