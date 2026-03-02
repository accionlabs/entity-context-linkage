#!/usr/bin/env python3
"""
Generate simulated tower physical audit data (drone + field inspections).

Cross-references tenant lease CSVs and produces what a site auditor would
actually find on each tower — with intentional discrepancies vs contracted
equipment (~15% towers have issues).

Writes:
  - slides/tower_physical_audits.csv
"""

import csv
import os
import random
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TL_CSV = os.path.join(SCRIPT_DIR, "slides", "crown_castle_tenant_leases.csv")
GL_CSV = os.path.join(SCRIPT_DIR, "slides", "crown_castle_ground_leases.csv")
OUT_CSV = os.path.join(SCRIPT_DIR, "slides", "tower_physical_audits.csv")

# Equipment models by carrier — same as generate_contracts.py
ANTENNA_MODELS = {
    "AT&T": ["CommScope FFHH-65C-R3", "Ericsson AIR 6449", "Nokia AirScale ABIA"],
    "T-Mobile": ["Ericsson AIR 6449 B41", "Nokia AAFIA", "CommScope SBNHH-1D65C"],
    "Verizon": ["CommScope FFHH-65C-R3-V2", "Samsung MT6407", "Ericsson AIR 3246"],
    "DISH Wireless": ["Nokia AAHQA", "Ericsson AIR 3219"],
    "US Cellular": ["CommScope NHH-65C-R2B", "Andrew DBXLH-6565C-VTM"],
    "C Spire": ["CommScope NHH-45C-R1A", "Kathrein 80010951"],
}

# Unknown/unauthorized carriers
ROGUE_CARRIERS = ["WilsonPro", "SureCall", "Geoverse", "Anterix", "Ligado"]

AUDIT_TYPES = ["Drone Inspection", "Field Audit", "Structural Engineering Visit",
               "Annual Compliance Check", "Insurance Inspection"]

INSPECTORS = [
    "J. Martinez — SBA Engineering", "K. Patel — Vertical Bridge Inspections",
    "M. Thompson — Summit QA", "R. Chen — SAI Group",
    "A. Williams — Black & Veatch", "L. Garcia — Terracon Consultants",
    "D. Kim — WSP USA", "S. Johnson — Summit Field Ops",
]


def _seed(val):
    return int(hashlib.md5(val.encode()).hexdigest()[:8], 16)


def main():
    # Load tenant leases grouped by tower
    tenants_by_tower = defaultdict(list)
    with open(TL_CSV, "r") as f:
        for row in csv.DictReader(f):
            tenants_by_tower[row["tower_id"]].append(row)

    # Load ground leases for tower metadata
    tower_meta = {}
    with open(GL_CSV, "r") as f:
        for row in csv.DictReader(f):
            tower_meta[row["tower_id"]] = row

    audits = []
    towers_audited = set()

    for tower_id, tenants in tenants_by_tower.items():
        rng = random.Random(_seed(tower_id + "_audit"))
        meta = tower_meta.get(tower_id, {})

        # Only audit ~60% of towers (realistic — not all towers audited every year)
        if rng.random() > 0.60:
            continue

        towers_audited.add(tower_id)

        audit_date = datetime(2025, 1, 1) + timedelta(days=rng.randint(0, 89))
        audit_type = rng.choice(AUDIT_TYPES)
        inspector = rng.choice(INSPECTORS)
        city = meta.get("city", tenants[0].get("city", "Unknown"))
        state = meta.get("state", tenants[0].get("state", "??"))
        tower_type = meta.get("tower_type", "Monopole")
        tower_height = meta.get("tower_height_ft", "150")

        # Calculate contracted totals
        contracted_antennas = sum(int(t["antenna_count"]) for t in tenants
                                  if t["lease_status"] not in ("Terminated",))
        contracted_cabinets = sum(1 for t in tenants
                                  if t["equipment_cabinet"] == "True"
                                  and t["lease_status"] not in ("Terminated",))
        active_carriers = [t["tenant_carrier"] for t in tenants
                          if t["lease_status"] not in ("Terminated",)]
        contracted_carriers = len(set(active_carriers))

        # Decide discrepancy type
        discrepancy = "none"
        disc_roll = rng.random()

        if disc_roll < 0.04:
            discrepancy = "unauthorized_carrier"
        elif disc_roll < 0.08:
            discrepancy = "extra_antennas"
        elif disc_roll < 0.11:
            discrepancy = "extra_cabinet"
        elif disc_roll < 0.14:
            discrepancy = "upgraded_equipment"
        elif disc_roll < 0.16:
            discrepancy = "missing_equipment"
        elif disc_roll < 0.18:
            discrepancy = "terminated_still_present"

        # Compute physical findings
        physical_antennas = contracted_antennas
        physical_cabinets = contracted_cabinets
        physical_carriers = contracted_carriers
        unauthorized_carrier = ""
        finding_notes = "No discrepancies observed."
        severity = "PASS"
        est_monthly_impact = 0.0

        if discrepancy == "unauthorized_carrier":
            unauthorized_carrier = rng.choice(ROGUE_CARRIERS)
            physical_antennas += rng.randint(2, 6)
            physical_cabinets += 1
            physical_carriers += 1
            finding_notes = (f"Unauthorized equipment detected: {unauthorized_carrier} — "
                           f"{physical_antennas - contracted_antennas} antennas, "
                           f"1 cabinet installed without lease amendment. "
                           f"No contract on file for this carrier.")
            severity = "CRITICAL"
            est_monthly_impact = rng.uniform(2500, 8000)

        elif discrepancy == "extra_antennas":
            extra = rng.randint(1, 4)
            physical_antennas += extra
            carrier = rng.choice(active_carriers) if active_carriers else "Unknown"
            finding_notes = (f"{extra} additional antenna(s) found at RAD center "
                           f"attributed to {carrier} — not in current equipment manifest. "
                           f"Likely upgrade without amendment. Structural load may exceed analysis.")
            severity = "WARNING"
            est_monthly_impact = extra * rng.uniform(400, 900)

        elif discrepancy == "extra_cabinet":
            physical_cabinets += 1
            carrier = rng.choice(active_carriers) if active_carriers else "Unknown"
            finding_notes = (f"Additional ground equipment cabinet found — attributed to {carrier}. "
                           f"Not in current lease scope. Ground space consumption ~{rng.randint(60,120)} sq ft unbilled.")
            severity = "WARNING"
            est_monthly_impact = rng.uniform(300, 700)

        elif discrepancy == "upgraded_equipment":
            carrier = rng.choice(active_carriers) if active_carriers else "Unknown"
            old_model = rng.choice(ANTENNA_MODELS.get(carrier, ["Old Panel"]))
            finding_notes = (f"Equipment upgrade detected for {carrier}: antennas replaced with "
                           f"larger {rng.choice(['massive MIMO', '5G Active Antenna', '8T8R'])} units — "
                           f"increased wind load and power draw. Original contract specifies {old_model}. "
                           f"No modification application on file.")
            severity = "WARNING"
            est_monthly_impact = rng.uniform(500, 2000)

        elif discrepancy == "missing_equipment":
            missing = rng.randint(1, 3)
            physical_antennas = max(0, physical_antennas - missing)
            carrier = rng.choice(active_carriers) if active_carriers else "Unknown"
            finding_notes = (f"{missing} antenna(s) contracted for {carrier} not physically present. "
                           f"Equipment may have been decommissioned without lease amendment — "
                           f"verify if overpaying for unused capacity.")
            severity = "INFO"
            est_monthly_impact = -missing * rng.uniform(300, 700)  # negative = we're overpaying

        elif discrepancy == "terminated_still_present":
            # Equipment from terminated lease still on tower
            terminated = [t for t in tenants if t["lease_status"] == "Terminated"]
            if terminated:
                term_carrier = terminated[0]["tenant_carrier"]
                term_antennas = int(terminated[0]["antenna_count"])
                physical_antennas += term_antennas
                finding_notes = (f"Equipment from TERMINATED lease ({terminated[0]['contract_id']}) "
                               f"still physically present: {term_antennas} antennas for {term_carrier}. "
                               f"Removal deadline may have passed. "
                               f"Blocking potential new tenant revenue on these slots.")
                severity = "WARNING"
                est_monthly_impact = rng.uniform(1000, 4000)
            else:
                discrepancy = "none"
                finding_notes = "No discrepancies observed."

        audit = {
            "audit_id": f"AUD-{tower_id[-6:]}-{audit_date.strftime('%Y%m')}",
            "tower_id": tower_id,
            "city": city,
            "state": state,
            "tower_type": tower_type,
            "tower_height_ft": tower_height,
            "audit_date": audit_date.strftime("%Y-%m-%d"),
            "audit_type": audit_type,
            "inspector": inspector,
            "contracted_carriers": contracted_carriers,
            "physical_carriers_found": physical_carriers,
            "contracted_antennas": contracted_antennas,
            "physical_antennas_found": physical_antennas,
            "contracted_cabinets": contracted_cabinets,
            "physical_cabinets_found": physical_cabinets,
            "discrepancy_type": discrepancy,
            "severity": severity,
            "unauthorized_carrier": unauthorized_carrier,
            "finding_notes": finding_notes,
            "est_monthly_revenue_impact_usd": round(est_monthly_impact, 2),
            "est_annual_revenue_impact_usd": round(est_monthly_impact * 12, 2),
        }
        audits.append(audit)

    # Write CSV
    fieldnames = list(audits[0].keys()) if audits else []
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audits)

    # Stats
    total = len(audits)
    disc_counts = defaultdict(int)
    total_impact = 0.0
    for a in audits:
        disc_counts[a["discrepancy_type"]] += 1
        total_impact += a["est_annual_revenue_impact_usd"]

    print(f"✅ Generated {total} tower audit records → {OUT_CSV}")
    print(f"   Towers in portfolio: {len(tenants_by_tower)}")
    print(f"   Towers audited:      {total}")
    print(f"\n📋 Findings:")
    for dtype, count in sorted(disc_counts.items(), key=lambda x: -x[1]):
        label = dtype if dtype != "none" else "clean (no issues)"
        print(f"   {label:30s} {count:4d}")
    print(f"\n💰 Est. annual revenue impact: ${total_impact:,.0f}")


if __name__ == "__main__":
    main()
