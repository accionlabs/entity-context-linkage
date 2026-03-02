#!/usr/bin/env python3
"""
Generate supplementary tower operations data for the full 9-use-case
reconciliation framework.

Reads tenant and ground lease CSVs, then generates:
  1. slides/rf_design_specs.csv        — planned RF configurations
  2. slides/structural_capacity.csv    — tower load analysis
  3. slides/modification_applications.csv — tenant mod requests
  4. slides/site_access_logs.csv       — field access records
  5. slides/tax_assessments.csv        — county property tax records

Each dataset includes intentional discrepancies (~12-18%) vs the
physical audit data and contract/invoice records.
"""

import csv
import os
import random
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GL_CSV  = os.path.join(SCRIPT_DIR, "slides", "crown_castle_ground_leases.csv")
TL_CSV  = os.path.join(SCRIPT_DIR, "slides", "crown_castle_tenant_leases.csv")
AUDIT_CSV = os.path.join(SCRIPT_DIR, "slides", "tower_physical_audits.csv")
OUT_DIR = os.path.join(SCRIPT_DIR, "slides")

ANTENNA_MODELS = {
    "AT&T":          ["CommScope FFHH-65C-R3", "Ericsson AIR 6449", "Nokia AirScale ABIA"],
    "T-Mobile":      ["Ericsson AIR 6449 B41", "Nokia AAFIA", "CommScope SBNHH-1D65C"],
    "Verizon":       ["CommScope FFHH-65C-R3-V2", "Samsung MT6407", "Ericsson AIR 3246"],
    "DISH Wireless":  ["Nokia AAHQA", "Ericsson AIR 3219"],
    "US Cellular":   ["CommScope NHH-65C-R2B", "Andrew DBXLH-6565C-VTM"],
    "C Spire":       ["CommScope NHH-45C-R1A", "Kathrein 80010951"],
}


def _seed(val):
    return int(hashlib.md5(val.encode()).hexdigest()[:8], 16)


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  ✅ {len(rows):,} records → {os.path.basename(path)}")


# ───────────────────────────────────────────────────────────────────────────
# Load source data
# ───────────────────────────────────────────────────────────────────────────

def load_source_data():
    tenants_by_tower = defaultdict(list)
    with open(TL_CSV, "r") as f:
        for row in csv.DictReader(f):
            tenants_by_tower[row["tower_id"]].append(row)

    tower_meta = {}
    with open(GL_CSV, "r") as f:
        for row in csv.DictReader(f):
            tower_meta[row["tower_id"]] = row

    audits = {}
    if os.path.exists(AUDIT_CSV):
        with open(AUDIT_CSV, "r") as f:
            for row in csv.DictReader(f):
                audits[row["tower_id"]] = row

    return tenants_by_tower, tower_meta, audits


# ───────────────────────────────────────────────────────────────────────────
# UC3: RF Design Specs
# ───────────────────────────────────────────────────────────────────────────

def generate_rf_specs(tenants_by_tower, tower_meta):
    records = []
    for tower_id, tenants in tenants_by_tower.items():
        meta = tower_meta.get(tower_id, {})
        tower_height = int(meta.get("tower_height_ft", 150))

        for tenant in tenants:
            if tenant["lease_status"] == "Terminated":
                continue

            rng = random.Random(_seed(tenant["contract_id"] + "_rf"))
            carrier = tenant["tenant_carrier"]
            mount_height = int(tenant.get("mount_height_ft", tower_height - 30))
            antenna_count = int(tenant.get("antenna_count", 3))
            sectors = max(1, antenna_count // 3) if antenna_count >= 3 else 1

            # Planned configuration
            planned_tilt = round(rng.uniform(2.0, 8.0), 1)
            planned_azimuth_a = rng.randint(0, 359)
            planned_azimuth_b = (planned_azimuth_a + 120) % 360
            planned_azimuth_c = (planned_azimuth_a + 240) % 360
            planned_model = rng.choice(ANTENNA_MODELS.get(carrier, ["Generic Panel"]))

            # Actual (with discrepancies ~15%)
            discrepancy = "none"
            actual_tilt = planned_tilt
            actual_azimuth_a = planned_azimuth_a
            actual_height = mount_height
            actual_model = planned_model

            if rng.random() < 0.15:
                disc_roll = rng.random()
                if disc_roll < 0.30:
                    discrepancy = "tilt_deviation"
                    actual_tilt = planned_tilt + rng.uniform(2.0, 5.0)
                elif disc_roll < 0.55:
                    discrepancy = "azimuth_rotation"
                    actual_azimuth_a = (planned_azimuth_a + rng.randint(10, 25)) % 360
                elif disc_roll < 0.75:
                    discrepancy = "height_deviation"
                    actual_height = mount_height - rng.randint(5, 15)
                elif disc_roll < 0.90:
                    discrepancy = "model_mismatch"
                    alt_models = [m for m in ANTENNA_MODELS.get(carrier, []) if m != planned_model]
                    actual_model = rng.choice(alt_models) if alt_models else planned_model + " (upgraded)"
                else:
                    discrepancy = "mount_conflict"

            records.append({
                "tower_id": tower_id,
                "contract_id": tenant["contract_id"],
                "carrier": carrier,
                "sectors": sectors,
                "planned_mount_height_ft": mount_height,
                "actual_mount_height_ft": actual_height,
                "planned_tilt_deg": planned_tilt,
                "actual_tilt_deg": round(actual_tilt, 1),
                "planned_azimuth_a_deg": planned_azimuth_a,
                "actual_azimuth_a_deg": actual_azimuth_a,
                "planned_antenna_model": planned_model,
                "actual_antenna_model": actual_model,
                "design_date": (datetime(2024, 1, 1) + timedelta(days=rng.randint(0, 365))).strftime("%Y-%m-%d"),
                "last_survey_date": (datetime(2025, 1, 1) + timedelta(days=rng.randint(0, 89))).strftime("%Y-%m-%d"),
                "discrepancy_type": discrepancy,
                "sla_risk": discrepancy in ("tilt_deviation", "azimuth_rotation", "height_deviation"),
            })

    _write_csv(os.path.join(OUT_DIR, "rf_design_specs.csv"), records,
               list(records[0].keys()) if records else [])
    return records


# ───────────────────────────────────────────────────────────────────────────
# UC4: Structural Capacity
# ───────────────────────────────────────────────────────────────────────────

def generate_structural_capacity(tenants_by_tower, tower_meta):
    records = []
    for tower_id, tenants in tenants_by_tower.items():
        meta = tower_meta.get(tower_id, {})
        rng = random.Random(_seed(tower_id + "_struct"))

        tower_type = meta.get("tower_type", "Monopole")
        tower_height = int(meta.get("tower_height_ft", 150))

        # Structural capacity depends on tower type
        if tower_type == "Guyed Tower":
            max_tenants = rng.randint(5, 8)
            max_wind_load_sqft = rng.uniform(80, 150)
        elif tower_type == "Lattice":
            max_tenants = rng.randint(4, 6)
            max_wind_load_sqft = rng.uniform(60, 120)
        elif tower_type == "Rooftop":
            max_tenants = rng.randint(2, 4)
            max_wind_load_sqft = rng.uniform(30, 60)
        else:  # Monopole
            max_tenants = rng.randint(3, 5)
            max_wind_load_sqft = rng.uniform(40, 90)

        active_tenants = [t for t in tenants if t["lease_status"] not in ("Terminated",)]
        current_tenants = len(set(t["tenant_carrier"] for t in active_tenants))
        total_antennas = sum(int(t["antenna_count"]) for t in active_tenants)

        # Wind load per antenna ~ 2-4 sqft
        current_wind_load = total_antennas * rng.uniform(2.0, 4.0)
        utilization_pct = round(current_wind_load / max_wind_load_sqft * 100, 1) if max_wind_load_sqft else 0

        discrepancy = "none"
        if current_tenants > max_tenants:
            discrepancy = "over_capacity_tenants"
        elif utilization_pct > 95:
            discrepancy = "near_structural_limit"
        elif utilization_pct < 40 and current_tenants < max_tenants - 1:
            discrepancy = "undersold_capacity"
        elif rng.random() < 0.08:
            discrepancy = "outdated_analysis"

        last_analysis = (datetime(2023, 1, 1) + timedelta(days=rng.randint(0, 730))).strftime("%Y-%m-%d")

        records.append({
            "tower_id": tower_id,
            "tower_type": tower_type,
            "tower_height_ft": tower_height,
            "tia_standard": rng.choice(["TIA-222-H", "TIA-222-G", "TIA-222-F"]),
            "max_tenant_capacity": max_tenants,
            "current_tenants": current_tenants,
            "available_slots": max(0, max_tenants - current_tenants),
            "max_wind_load_sqft": round(max_wind_load_sqft, 1),
            "current_wind_load_sqft": round(current_wind_load, 1),
            "utilization_pct": utilization_pct,
            "total_antennas": total_antennas,
            "last_structural_analysis_date": last_analysis,
            "analysis_stale": (datetime(2025, 3, 15) - datetime.strptime(last_analysis, "%Y-%m-%d")).days > 365,
            "discrepancy_type": discrepancy,
            "revenue_opportunity_monthly": round(rng.uniform(2500, 6000), 2) if discrepancy == "undersold_capacity" else 0,
        })

    _write_csv(os.path.join(OUT_DIR, "structural_capacity.csv"), records,
               list(records[0].keys()) if records else [])
    return records


# ───────────────────────────────────────────────────────────────────────────
# UC6: Modification Applications
# ───────────────────────────────────────────────────────────────────────────

def generate_mod_applications(tenants_by_tower, tower_meta):
    records = []
    MOD_TYPES = ["Antenna Swap", "Add Sector", "Equipment Upgrade", "RRU Replacement",
                 "Generator Install", "Cabinet Addition", "Height Change", "5G Overlay"]

    for tower_id, tenants in tenants_by_tower.items():
        rng = random.Random(_seed(tower_id + "_mod"))

        for tenant in tenants:
            if tenant["lease_status"] == "Terminated":
                continue

            # ~40% of active tenants have had a mod application
            if rng.random() > 0.40:
                continue

            carrier = tenant["tenant_carrier"]
            mod_type = rng.choice(MOD_TYPES)
            submit_date = datetime(2024, 1, 1) + timedelta(days=rng.randint(0, 400))
            approval_date = submit_date + timedelta(days=rng.randint(14, 90))
            install_date = approval_date + timedelta(days=rng.randint(30, 120))

            discrepancy = "none"
            billing_updated = True
            physically_installed = True
            mod_approved = True

            disc_roll = rng.random()
            if disc_roll < 0.06:
                discrepancy = "billing_not_updated"
                billing_updated = False
            elif disc_roll < 0.10:
                discrepancy = "not_installed"
                physically_installed = False
            elif disc_roll < 0.14:
                discrepancy = "no_mod_application"
                mod_approved = False
            elif disc_roll < 0.17:
                discrepancy = "non_conformance"

            records.append({
                "mod_id": f"MOD-{tower_id[-6:]}-{rng.randint(1000,9999)}",
                "tower_id": tower_id,
                "contract_id": tenant["contract_id"],
                "carrier": carrier,
                "mod_type": mod_type,
                "submitted_date": submit_date.strftime("%Y-%m-%d"),
                "approved_date": approval_date.strftime("%Y-%m-%d") if mod_approved else "",
                "install_date": install_date.strftime("%Y-%m-%d") if physically_installed else "",
                "mod_approved": mod_approved,
                "physically_installed": physically_installed,
                "billing_updated": billing_updated,
                "monthly_rate_change_usd": round(rng.uniform(200, 1500), 2),
                "discrepancy_type": discrepancy,
                "notes": {
                    "none": "",
                    "billing_not_updated": f"Mod completed but billing system not updated — revenue leakage",
                    "not_installed": f"Mod approved and billing updated but equipment never installed — tenant overcharged",
                    "no_mod_application": f"Equipment change detected on tower without approved modification application",
                    "non_conformance": f"Installation does not match approved plans — wind load or interference risk",
                }.get(discrepancy, ""),
            })

    _write_csv(os.path.join(OUT_DIR, "modification_applications.csv"), records,
               list(records[0].keys()) if records else [])
    return records


# ───────────────────────────────────────────────────────────────────────────
# UC8: Site Access Logs
# ───────────────────────────────────────────────────────────────────────────

def generate_site_access_logs(tenants_by_tower, tower_meta, mod_records):
    records = []
    CONTRACTORS = ["Summit Field Ops", "MasTec", "Ericsson Services",
                   "Nokia Deployment", "CommScope Install", "Black & Veatch",
                   "SAI Group", "Vertical Bridge Services", "Unknown"]
    ACCESS_PURPOSES = ["Equipment Install", "Routine Maintenance", "Emergency Repair",
                       "Antenna Swap", "Decommission", "Inspection", "Generator Service"]

    mod_by_tower = defaultdict(list)
    for m in mod_records:
        mod_by_tower[m["tower_id"]].append(m)

    for tower_id, tenants in tenants_by_tower.items():
        rng = random.Random(_seed(tower_id + "_access"))
        mods = mod_by_tower.get(tower_id, [])

        # Generate access logs — mix of legitimate and suspicious
        num_accesses = rng.randint(2, 8)
        for i in range(num_accesses):
            access_date = datetime(2024, 6, 1) + timedelta(days=rng.randint(0, 270))
            carrier = rng.choice([t["tenant_carrier"] for t in tenants] or ["Summit"])
            contractor = rng.choice(CONTRACTORS)
            purpose = rng.choice(ACCESS_PURPOSES)

            discrepancy = "none"
            has_matching_mod = any(
                m["carrier"] == carrier and m.get("install_date") and
                abs((access_date - datetime.strptime(m["install_date"], "%Y-%m-%d")).days) < 30
                for m in mods
            )

            if not has_matching_mod and purpose in ("Equipment Install", "Antenna Swap") and rng.random() < 0.20:
                discrepancy = "no_approved_mod"
            elif rng.random() < 0.04:
                discrepancy = "unauthorized_access"
                contractor = "Unknown"
                purpose = "Unknown"

            records.append({
                "access_id": f"ACC-{tower_id[-6:]}-{access_date.strftime('%Y%m%d')}-{i+1}",
                "tower_id": tower_id,
                "access_date": access_date.strftime("%Y-%m-%d"),
                "carrier": carrier,
                "contractor": contractor,
                "purpose": purpose,
                "duration_hours": round(rng.uniform(1, 12), 1),
                "has_matching_mod_application": has_matching_mod,
                "discrepancy_type": discrepancy,
                "notes": {
                    "none": "",
                    "no_approved_mod": "Site access for equipment work but no approved modification application on file",
                    "unauthorized_access": "Unidentified access — no work order, contractor, or appointment found",
                }.get(discrepancy, ""),
            })

    _write_csv(os.path.join(OUT_DIR, "site_access_logs.csv"), records,
               list(records[0].keys()) if records else [])
    return records


# ───────────────────────────────────────────────────────────────────────────
# UC9: Tax Assessments
# ───────────────────────────────────────────────────────────────────────────

def generate_tax_assessments(tenants_by_tower, tower_meta):
    records = []
    for tower_id, meta in tower_meta.items():
        rng = random.Random(_seed(tower_id + "_tax"))

        if meta.get("ownership_type") == "Owned":
            continue  # No pass-through for owned sites

        state = meta.get("state", "TX")
        city = meta.get("city", "Austin")
        tenants = tenants_by_tower.get(tower_id, [])
        active_tenants = [t for t in tenants if t["lease_status"] not in ("Terminated",)]
        tenant_count = len(set(t["tenant_carrier"] for t in active_tenants))

        # Tax assessment based on improvements
        base_land_value = rng.uniform(20000, 150000)
        improvement_value = tenant_count * rng.uniform(15000, 45000) + rng.uniform(50000, 200000)
        total_assessed = round(base_land_value + improvement_value, 2)
        tax_rate_pct = rng.uniform(0.8, 3.5)
        annual_tax = round(total_assessed * tax_rate_pct / 100, 2)

        # Pass-through invoice — should equal annual_tax but may not
        pass_through_invoiced = annual_tax
        discrepancy = "none"
        disc_roll = rng.random()
        if disc_roll < 0.05:
            discrepancy = "pass_through_not_invoiced"
            pass_through_invoiced = 0
        elif disc_roll < 0.10:
            discrepancy = "wrong_assessment_basis"
            pass_through_invoiced = round(annual_tax * rng.uniform(0.6, 0.85), 2)
        elif disc_roll < 0.14:
            discrepancy = "tenant_count_stale"
        elif disc_roll < 0.17:
            discrepancy = "decommissioned_exemption"

        records.append({
            "tower_id": tower_id,
            "city": city,
            "state": state,
            "county_jurisdiction": f"{city} County",
            "assessment_year": 2025,
            "base_land_value_usd": round(base_land_value, 2),
            "improvement_value_usd": round(improvement_value, 2),
            "total_assessed_value_usd": total_assessed,
            "tax_rate_pct": round(tax_rate_pct, 2),
            "annual_property_tax_usd": annual_tax,
            "assessed_tenant_count": tenant_count if discrepancy != "tenant_count_stale" else max(1, tenant_count - rng.randint(1, 2)),
            "actual_tenant_count": tenant_count,
            "pass_through_invoiced_usd": pass_through_invoiced,
            "pass_through_delta_usd": round(pass_through_invoiced - annual_tax, 2),
            "discrepancy_type": discrepancy,
            "notes": {
                "none": "",
                "pass_through_not_invoiced": "Property tax increase not passed through to tenant — Summit absorbing cost",
                "wrong_assessment_basis": "Pass-through calculated on old assessment value — not reflecting improvements",
                "tenant_count_stale": "Assessment based on outdated tenant count — potential reassessment needed",
                "decommissioned_exemption": "Tax exemption on file for equipment that has been decommissioned",
            }.get(discrepancy, ""),
        })

    _write_csv(os.path.join(OUT_DIR, "tax_assessments.csv"), records,
               list(records[0].keys()) if records else [])
    return records


# ───────────────────────────────────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────────────────────────────────

def main():
    print("🏗️  Generating supplementary tower operations data...")
    tenants_by_tower, tower_meta, audits = load_source_data()
    print(f"   Source: {sum(len(v) for v in tenants_by_tower.values())} tenants across {len(tenants_by_tower)} towers\n")

    rf = generate_rf_specs(tenants_by_tower, tower_meta)
    struct = generate_structural_capacity(tenants_by_tower, tower_meta)
    mods = generate_mod_applications(tenants_by_tower, tower_meta)
    access = generate_site_access_logs(tenants_by_tower, tower_meta, mods)
    tax = generate_tax_assessments(tenants_by_tower, tower_meta)

    # Print summary stats
    stats = {
        "RF Design Specs": (rf, "discrepancy_type"),
        "Structural Capacity": (struct, "discrepancy_type"),
        "Mod Applications": (mods, "discrepancy_type"),
        "Site Access Logs": (access, "discrepancy_type"),
        "Tax Assessments": (tax, "discrepancy_type"),
    }
    print(f"\n📋 Discrepancy summary:")
    total_disc = 0
    for name, (data, key) in stats.items():
        disc = sum(1 for r in data if r.get(key, "none") != "none")
        total_disc += disc
        pct = disc / len(data) * 100 if data else 0
        print(f"   {name:25s} {disc:4d} / {len(data):4d} ({pct:.1f}%)")
    print(f"   {'TOTAL':25s} {total_disc:4d}")


if __name__ == "__main__":
    main()
