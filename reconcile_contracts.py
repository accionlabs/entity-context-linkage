#!/usr/bin/env python3
"""
Comprehensive Tower Operations Reconciliation Engine — Summit.

9 Cross-Reference Reconciliation Use Cases:

  UC1: Physical Inventory ↔ Tenant Contract
  UC2: Physical Inventory ↔ Invoice Line Items
  UC3: RF Design Specs ↔ Physical As-Built
  UC4: Structural Load ↔ Actual Load on Tower
  UC5: Escalation Schedule ↔ Invoice History
  UC6: Modification Applications ↔ Physical Changes ↔ Invoice Updates
  UC7: Ground Lease Revenue Share ↔ Actual Tenant Revenue
  UC8: Site Access Logs ↔ Mod Applications ↔ Physical Changes
  UC9: Tax Assessment ↔ Pass-Through Invoices ↔ Physical Footprint

Additional cross-cuts:
  - DISH default exposure ($3.5B recovery)
  - Renewal/termination deadline tracking
  - Legacy system migration errors

Can be run standalone or imported by ecl_app.py.
"""

import csv
import os
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES = os.path.join(SCRIPT_DIR, "slides")

GL_CSV     = os.path.join(SLIDES, "crown_castle_ground_leases.csv")
TL_CSV     = os.path.join(SLIDES, "crown_castle_tenant_leases.csv")
INV_CSV    = os.path.join(SLIDES, "erp_invoices.csv")
AUDIT_CSV  = os.path.join(SLIDES, "tower_physical_audits.csv")
RF_CSV     = os.path.join(SLIDES, "rf_design_specs.csv")
STRUCT_CSV = os.path.join(SLIDES, "structural_capacity.csv")
MOD_CSV    = os.path.join(SLIDES, "modification_applications.csv")
ACCESS_CSV = os.path.join(SLIDES, "site_access_logs.csv")
TAX_CSV    = os.path.join(SLIDES, "tax_assessments.csv")


# ─── Data classes ─────────────────────────────────────────────────────────

@dataclass
class ContractRecord:
    contract_id: str
    tower_id: str
    contract_type: str
    monthly_amount: float
    escalation_pct: float
    lease_status: str
    start_date: str
    end_date: str
    term_years: int
    city: str
    state: str
    carrier: str = ""
    landowner_type: str = ""
    ownership_type: str = ""
    termination_notice_days: int = 180
    antenna_count: int = 0
    equipment_cabinet: bool = False
    dish_default_status: str = "N/A"
    sprint_merger_impact: bool = False
    outstanding_obligation: float = 0.0
    divestiture_impacted: bool = False


@dataclass
class Discrepancy:
    severity: str       # "🔴 Critical", "🟡 Warning", "🟢 Info"
    use_case: str       # UC1-UC9
    category: str       # "Co-location", "Billing", "RF/SLA", etc.
    disc_type: str      # specific type
    description: str
    contract_id: str
    tower_id: str
    invoice_id: str = ""
    contract_amount: float = 0.0
    invoiced_amount: float = 0.0
    delta: float = 0.0
    billing_period: str = ""
    est_annual_impact: float = 0.0


@dataclass
class ReconciliationResult:
    total_contracts: int = 0
    total_invoices: int = 0
    total_audits: int = 0
    total_rf_specs: int = 0
    total_structural: int = 0
    total_mod_apps: int = 0
    total_access_logs: int = 0
    total_tax_records: int = 0
    matched_contracts: int = 0
    unmatched_contracts: int = 0
    total_discrepancies: int = 0
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    total_invoice_value: float = 0.0
    total_expected_value: float = 0.0
    total_delta: float = 0.0
    est_total_annual_impact: float = 0.0
    discrepancies: List[Discrepancy] = field(default_factory=list)
    summary_by_type: Dict[str, int] = field(default_factory=dict)
    summary_by_category: Dict[str, int] = field(default_factory=dict)
    summary_by_use_case: Dict[str, int] = field(default_factory=dict)
    unbilled_contracts: List[str] = field(default_factory=list)
    dish_active_count: int = 0
    dish_defaulted_count: int = 0
    dish_total_exposure: float = 0.0
    contracts_expiring_soon: int = 0
    auto_renewal_risk: int = 0
    undersold_towers: int = 0
    undersold_monthly_opportunity: float = 0.0


VALID_GL_AP = {"6110-001", "6110-002", "6110-100"}
VALID_GL_AR = {"4210-001", "4210-050", "4210-100"}


# ─── Generic CSV loader ──────────────────────────────────────────────────

def _load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return list(csv.DictReader(f))


# ─── Specialized loaders ─────────────────────────────────────────────────

def load_contracts() -> Dict[str, ContractRecord]:
    contracts = {}
    for row in _load_csv(GL_CSV):
        if row["ownership_type"] == "Owned":
            continue
        monthly = float(row["monthly_rent_usd"])
        if monthly <= 0:
            continue
        contracts[row["contract_id"]] = ContractRecord(
            contract_id=row["contract_id"], tower_id=row["tower_id"],
            contract_type="ground_lease", monthly_amount=monthly,
            escalation_pct=float(row["escalation_pct"]),
            lease_status=row["lease_status"], start_date=row["lease_start_date"],
            end_date=row.get("initial_term_end_date", ""),
            term_years=int(row.get("initial_term_years", 0)),
            city=row["city"], state=row["state"],
            landowner_type=row.get("landowner_type", ""),
            ownership_type=row.get("ownership_type", ""),
            termination_notice_days=int(row.get("termination_notice_days", 180)),
        )

    for row in _load_csv(TL_CSV):
        contracts[row["contract_id"]] = ContractRecord(
            contract_id=row["contract_id"], tower_id=row["tower_id"],
            contract_type="tenant_lease",
            monthly_amount=float(row["monthly_revenue_usd"]),
            escalation_pct=float(row["escalation_pct"]),
            lease_status=row["lease_status"], start_date=row["lease_start_date"],
            end_date=row.get("lease_end_date", ""),
            term_years=int(row.get("term_years", 0)),
            city=row["city"], state=row["state"],
            carrier=row.get("tenant_carrier", ""),
            antenna_count=int(row.get("antenna_count", 0)),
            equipment_cabinet=row.get("equipment_cabinet", "False") == "True",
            dish_default_status=row.get("dish_default_status", "N/A"),
            sprint_merger_impact=row.get("sprint_merger_impact", "False") == "True",
            outstanding_obligation=float(row.get("outstanding_obligation_usd", 0)),
            divestiture_impacted=row.get("divestiture_impacted", "False") == "True",
        )
    return contracts


def load_invoices():
    rows = _load_csv(INV_CSV)
    return [{
        "invoice_id": r["invoice_id"], "erp_system": r["erp_system"],
        "invoice_type": r["invoice_type"], "contract_ref": r["contract_ref"],
        "tower_ref": r["tower_ref"], "vendor_or_tenant": r["vendor_or_tenant"],
        "invoice_date": r["invoice_date"], "billing_period": r["billing_period"],
        "invoiced_amount": float(r["invoiced_amount_usd"]),
        "expected_amount": float(r["expected_amount_usd"]),
        "payment_status": r["payment_status"], "gl_account": r["gl_account"],
        "cost_center": r["cost_center"], "notes": r.get("notes", ""),
    } for r in rows]


load_audits    = lambda: _load_csv(AUDIT_CSV)
load_rf_specs  = lambda: _load_csv(RF_CSV)
load_structural = lambda: _load_csv(STRUCT_CSV)
load_mod_apps  = lambda: _load_csv(MOD_CSV)
load_access    = lambda: _load_csv(ACCESS_CSV)
load_tax       = lambda: _load_csv(TAX_CSV)


# ─── Main reconciliation ─────────────────────────────────────────────────

def reconcile(contracts=None, invoices=None, audits=None,
              rf_specs=None, structural=None, mod_apps=None,
              access_logs=None, tax_records=None) -> ReconciliationResult:

    if contracts is None:  contracts = load_contracts()
    if invoices is None:   invoices = load_invoices()
    if audits is None:     audits = load_audits()
    if rf_specs is None:   rf_specs = load_rf_specs()
    if structural is None: structural = load_structural()
    if mod_apps is None:   mod_apps = load_mod_apps()
    if access_logs is None: access_logs = load_access()
    if tax_records is None: tax_records = load_tax()

    r = ReconciliationResult()
    r.total_contracts = len(contracts)
    r.total_invoices = len(invoices)
    r.total_audits = len(audits)
    r.total_rf_specs = len(rf_specs)
    r.total_structural = len(structural)
    r.total_mod_apps = len(mod_apps)
    r.total_access_logs = len(access_logs)
    r.total_tax_records = len(tax_records)

    _add = r.discrepancies.append  # shorthand

    # ━━━ UC1: Physical Inventory ↔ Tenant Contract ━━━━━━━━━━━━━━━━━━━━━━

    for a in audits:
        dt = a.get("discrepancy_type", "none")
        if dt == "none":
            continue

        impact = float(a.get("est_annual_revenue_impact_usd", 0))
        uc = "UC1"
        cat = "Co-location"

        if dt == "unauthorized_carrier":
            _add(Discrepancy(
                severity="🔴 Critical", use_case=uc, category=cat,
                disc_type="Unauthorized Carrier on Tower",
                description=f"[{a['audit_id']}] {a.get('unauthorized_carrier', 'Unknown')} equipment on {a['tower_id']} — no contract. {a.get('physical_antennas_found','?')} antennas found vs {a.get('contracted_antennas','?')} contracted.",
                contract_id="", tower_id=a["tower_id"], est_annual_impact=impact,
            ))
        elif dt == "extra_antennas":
            _add(Discrepancy(
                severity="🟡 Warning", use_case=uc, category=cat,
                disc_type="Unbilled Equipment (Antennas)",
                description=f"[{a['audit_id']}] {int(a['physical_antennas_found'])-int(a['contracted_antennas'])} extra antennas on {a['tower_id']} — contracted: {a['contracted_antennas']}, found: {a['physical_antennas_found']}",
                contract_id="", tower_id=a["tower_id"], est_annual_impact=impact,
            ))
        elif dt == "extra_cabinet":
            _add(Discrepancy(
                severity="🟡 Warning", use_case=uc, category=cat,
                disc_type="Unbilled Equipment (Cabinet)",
                description=f"[{a['audit_id']}] Extra cabinet on {a['tower_id']}. Ground space unbilled.",
                contract_id="", tower_id=a["tower_id"], est_annual_impact=impact,
            ))
        elif dt == "upgraded_equipment":
            _add(Discrepancy(
                severity="🟡 Warning", use_case=uc, category=cat,
                disc_type="Unauthorized Equipment Upgrade",
                description=f"[{a['audit_id']}] Equipment upgrade without amendment on {a['tower_id']}. {a.get('finding_notes','')}",
                contract_id="", tower_id=a["tower_id"], est_annual_impact=impact,
            ))
        elif dt == "missing_equipment":
            _add(Discrepancy(
                severity="🟢 Info", use_case=uc, category=cat,
                disc_type="Missing Contracted Equipment",
                description=f"[{a['audit_id']}] Equipment absent from {a['tower_id']} — may be overpaying for unused capacity",
                contract_id="", tower_id=a["tower_id"], est_annual_impact=impact,
            ))
        elif dt == "terminated_still_present":
            _add(Discrepancy(
                severity="🟡 Warning", use_case=uc, category=cat,
                disc_type="Zombie Tenant Equipment",
                description=f"[{a['audit_id']}] Terminated lease equipment still on {a['tower_id']} — blocking new tenant revenue",
                contract_id="", tower_id=a["tower_id"], est_annual_impact=impact,
            ))

    # ━━━ UC2: Physical Inventory ↔ Invoice Line Items ━━━━━━━━━━━━━━━━━━━

    # Cross-reference audit findings with invoices — if audit shows extra
    # equipment but invoices don't reflect it, it's underbilling.
    audited_towers = {a["tower_id"]: a for a in audits}
    inv_by_tower = defaultdict(list)
    for inv in invoices:
        inv_by_tower[inv["tower_ref"]].append(inv)

    for tower_id, audit in audited_towers.items():
        phys_ant = int(audit.get("physical_antennas_found", 0))
        contr_ant = int(audit.get("contracted_antennas", 0))
        if phys_ant > contr_ant and contr_ant > 0:
            tower_invoices = inv_by_tower.get(tower_id, [])
            if tower_invoices:
                total_invoiced = sum(i["invoiced_amount"] for i in tower_invoices)
                ratio = phys_ant / contr_ant if contr_ant else 1
                underbilled = total_invoiced * (ratio - 1)
                if underbilled > 100:
                    _add(Discrepancy(
                        severity="🔴 Critical", use_case="UC2", category="Billing",
                        disc_type="Invoice ↔ Physical Mismatch",
                        description=f"Invoices for {tower_id} based on {contr_ant} antennas but {phys_ant} physically present — est. underbilling ${underbilled:,.0f}/yr",
                        contract_id="", tower_id=tower_id,
                        est_annual_impact=underbilled,
                    ))

    # ━━━ UC3: RF Design Specs ↔ Physical As-Built ━━━━━━━━━━━━━━━━━━━━━━━

    for spec in rf_specs:
        dt = spec.get("discrepancy_type", "none")
        if dt == "none":
            continue
        sla = spec.get("sla_risk", "False")
        sev = "🟡 Warning" if str(sla) == "True" else "🟢 Info"

        if dt == "tilt_deviation":
            _add(Discrepancy(
                severity=sev, use_case="UC3", category="RF / SLA",
                disc_type="Antenna Tilt Deviation",
                description=f"{spec['carrier']} on {spec['tower_id']}: tilt designed {spec['planned_tilt_deg']}° but measured {spec['actual_tilt_deg']}° — coverage degradation risk",
                contract_id=spec.get("contract_id", ""), tower_id=spec["tower_id"],
            ))
        elif dt == "azimuth_rotation":
            _add(Discrepancy(
                severity=sev, use_case="UC3", category="RF / SLA",
                disc_type="Antenna Azimuth Rotation",
                description=f"{spec['carrier']} on {spec['tower_id']}: azimuth planned {spec['planned_azimuth_a_deg']}° but measured {spec['actual_azimuth_a_deg']}° — interference or coverage gap",
                contract_id=spec.get("contract_id", ""), tower_id=spec["tower_id"],
            ))
        elif dt == "height_deviation":
            _add(Discrepancy(
                severity=sev, use_case="UC3", category="RF / SLA",
                disc_type="Mount Height Deviation",
                description=f"{spec['carrier']} on {spec['tower_id']}: RAD center at {spec['actual_mount_height_ft']}ft vs planned {spec['planned_mount_height_ft']}ft",
                contract_id=spec.get("contract_id", ""), tower_id=spec["tower_id"],
            ))
        elif dt == "model_mismatch":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC3", category="RF / SLA",
                disc_type="Antenna Model Mismatch",
                description=f"{spec['carrier']} on {spec['tower_id']}: approved {spec['planned_antenna_model']} but installed {spec['actual_antenna_model']}",
                contract_id=spec.get("contract_id", ""), tower_id=spec["tower_id"],
            ))
        elif dt == "mount_conflict":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC3", category="RF / SLA",
                disc_type="Mount Position Conflict",
                description=f"{spec['carrier']} on {spec['tower_id']}: equipment on mount allocated to different tenant",
                contract_id=spec.get("contract_id", ""), tower_id=spec["tower_id"],
            ))

    # ━━━ UC4: Structural Load ↔ Actual Load ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    for s in structural:
        dt = s.get("discrepancy_type", "none")
        if dt == "none":
            continue

        opp = float(s.get("revenue_opportunity_monthly", 0))

        if dt == "over_capacity_tenants":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC4", category="Structural",
                disc_type="Tower Over Capacity",
                description=f"{s['tower_id']}: {s['current_tenants']} tenants but structural limit is {s['max_tenant_capacity']} — safety and compliance risk. Utilization: {s['utilization_pct']}%",
                contract_id="", tower_id=s["tower_id"],
            ))
        elif dt == "near_structural_limit":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC4", category="Structural",
                disc_type="Near Structural Limit",
                description=f"{s['tower_id']}: wind load at {s['utilization_pct']}% of capacity ({s['current_wind_load_sqft']}/{s['max_wind_load_sqft']} sqft). No room for additional equipment.",
                contract_id="", tower_id=s["tower_id"],
            ))
        elif dt == "undersold_capacity":
            _add(Discrepancy(
                severity="🟢 Info", use_case="UC4", category="Structural",
                disc_type="Undersold Tower Capacity",
                description=f"{s['tower_id']}: {s['available_slots']} open tenant slot(s), utilization only {s['utilization_pct']}%. Potential ${opp:,.0f}/mo additional revenue.",
                contract_id="", tower_id=s["tower_id"],
                est_annual_impact=opp * 12,
            ))
            r.undersold_towers += 1
            r.undersold_monthly_opportunity += opp
        elif dt == "outdated_analysis":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC4", category="Structural",
                disc_type="Outdated Structural Analysis",
                description=f"{s['tower_id']}: last analysis on {s['last_structural_analysis_date']}. Equipment may have changed since — structural risk unknown.",
                contract_id="", tower_id=s["tower_id"],
            ))

    # ━━━ UC5: Escalation Schedule ↔ Invoice History ━━━━━━━━━━━━━━━━━━━━━

    inv_by_contract = defaultdict(list)
    for inv in invoices:
        inv_by_contract[inv["contract_ref"]].append(inv)
        r.total_invoice_value += inv["invoiced_amount"]
        r.total_expected_value += inv["expected_amount"]

    contracts_with_invoices = set()

    for cref, cinvs in inv_by_contract.items():
        contract = contracts.get(cref)
        if not contract:
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC5", category="Migration",
                disc_type="Orphaned Invoice",
                description=f"Invoice references {cref} — not in contract master. Possible migration error.",
                contract_id=cref, tower_id=cinvs[0]["tower_ref"],
                invoice_id=cinvs[0]["invoice_id"],
                est_annual_impact=cinvs[0]["invoiced_amount"] * 12,
            ))
            continue

        contracts_with_invoices.add(cref)
        seen = {}
        for inv in cinvs:
            # Duplicate
            if inv["billing_period"] in seen:
                prev = seen[inv["billing_period"]]
                if abs(inv["invoiced_amount"] - prev["invoiced_amount"]) < 0.01:
                    _add(Discrepancy(
                        severity="🟡 Warning", use_case="UC5", category="Billing",
                        disc_type="Duplicate Invoice",
                        description=f"Duplicate for {inv['billing_period']}: {inv['invoice_id']} + {prev['invoice_id']} (${inv['invoiced_amount']:,.2f} each)",
                        contract_id=cref, tower_id=inv["tower_ref"],
                        invoice_id=inv["invoice_id"],
                        invoiced_amount=inv["invoiced_amount"],
                        billing_period=inv["billing_period"],
                        est_annual_impact=inv["invoiced_amount"],
                    ))
            seen[inv["billing_period"]] = inv

            # Amount / escalation
            if inv["expected_amount"] > 0:
                delta = inv["invoiced_amount"] - inv["expected_amount"]
                pct = abs(delta) / inv["expected_amount"] * 100

                if pct > 5.0:
                    _add(Discrepancy(
                        severity="🔴 Critical" if pct > 10 else "🟡 Warning",
                        use_case="UC5", category="Escalation",
                        disc_type="Amount Mismatch",
                        description=f"Invoice ${inv['invoiced_amount']:,.2f} vs expected ${inv['expected_amount']:,.2f} ({pct:+.1f}% off) for {inv['billing_period']}",
                        contract_id=cref, tower_id=inv["tower_ref"],
                        invoice_id=inv["invoice_id"],
                        contract_amount=inv["expected_amount"],
                        invoiced_amount=inv["invoiced_amount"],
                        delta=round(delta, 2), billing_period=inv["billing_period"],
                        est_annual_impact=abs(delta) * 12,
                    ))

                if abs(inv["invoiced_amount"] - contract.monthly_amount) < 1.0 and pct > 3.0:
                    _add(Discrepancy(
                        severity="🔴 Critical", use_case="UC5", category="Escalation",
                        disc_type="Missed Escalation",
                        description=f"Billing at original ${contract.monthly_amount:,.2f} vs escalated ${inv['expected_amount']:,.2f} ({contract.escalation_pct}%/yr not applied)",
                        contract_id=cref, tower_id=inv["tower_ref"],
                        invoice_id=inv["invoice_id"],
                        contract_amount=inv["expected_amount"],
                        invoiced_amount=inv["invoiced_amount"],
                        delta=round(delta, 2), billing_period=inv["billing_period"],
                        est_annual_impact=abs(delta) * 12,
                    ))

            # Billing on terminated
            if contract.lease_status in ("Terminated", "Pending Termination"):
                _add(Discrepancy(
                    severity="🔴 Critical", use_case="UC5", category="Billing",
                    disc_type="Billing on Terminated",
                    description=f"Invoice {inv['invoice_id']} for {contract.lease_status} contract — should have ceased",
                    contract_id=cref, tower_id=inv["tower_ref"],
                    invoice_id=inv["invoice_id"],
                    invoiced_amount=inv["invoiced_amount"],
                    billing_period=inv["billing_period"],
                    est_annual_impact=inv["invoiced_amount"] * 12,
                ))

            # GL validation
            if inv["invoice_type"] == "AP" and inv["gl_account"] not in VALID_GL_AP:
                _add(Discrepancy(
                    severity="🟡 Warning", use_case="UC5", category="Migration",
                    disc_type="Wrong GL Account",
                    description=f"AP posted to {inv['gl_account']} — expected 6110-xxx",
                    contract_id=cref, tower_id=inv["tower_ref"],
                    invoice_id=inv["invoice_id"], billing_period=inv["billing_period"],
                ))
            elif inv["invoice_type"] == "AR" and inv["gl_account"] not in VALID_GL_AR:
                _add(Discrepancy(
                    severity="🟡 Warning", use_case="UC5", category="Migration",
                    disc_type="Wrong GL Account",
                    description=f"AR posted to {inv['gl_account']} — expected 4210-xxx",
                    contract_id=cref, tower_id=inv["tower_ref"],
                    invoice_id=inv["invoice_id"], billing_period=inv["billing_period"],
                ))

            # Tower ID mismatch
            if contract.tower_id != inv["tower_ref"]:
                _add(Discrepancy(
                    severity="🟡 Warning", use_case="UC5", category="Migration",
                    disc_type="Tower ID Mismatch",
                    description=f"Invoice tower {inv['tower_ref']} ≠ contract tower {contract.tower_id}",
                    contract_id=cref, tower_id=inv["tower_ref"],
                    invoice_id=inv["invoice_id"], billing_period=inv["billing_period"],
                ))

    # Unbilled
    for cid, c in contracts.items():
        if cid not in contracts_with_invoices:
            if c.lease_status in ("Active", "Pending Renewal", "Under Renegotiation"):
                _add(Discrepancy(
                    severity="🔴 Critical", use_case="UC5", category="Billing",
                    disc_type="Unbilled Contract",
                    description=f"Active contract {cid} ({c.lease_status}) has NO invoices",
                    contract_id=cid, tower_id=c.tower_id,
                    contract_amount=c.monthly_amount,
                    est_annual_impact=c.monthly_amount * 12,
                ))
                r.unbilled_contracts.append(cid)

    # ━━━ UC6: Mod Applications ↔ Physical ↔ Invoice ━━━━━━━━━━━━━━━━━━━━

    for m in mod_apps:
        dt = m.get("discrepancy_type", "none")
        if dt == "none":
            continue
        rate_change = float(m.get("monthly_rate_change_usd", 0))

        if dt == "billing_not_updated":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC6", category="Mod / Change",
                disc_type="Mod Complete — Billing Not Updated",
                description=f"[{m['mod_id']}] {m['carrier']} {m['mod_type']} on {m['tower_id']} installed but billing not updated — ${rate_change:,.0f}/mo revenue leakage",
                contract_id=m.get("contract_id", ""), tower_id=m["tower_id"],
                est_annual_impact=rate_change * 12,
            ))
        elif dt == "not_installed":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC6", category="Mod / Change",
                disc_type="Mod Billed — Not Installed",
                description=f"[{m['mod_id']}] {m['carrier']} {m['mod_type']} approved and billed but not physically installed on {m['tower_id']} — tenant overcharged",
                contract_id=m.get("contract_id", ""), tower_id=m["tower_id"],
                est_annual_impact=rate_change * 12,
            ))
        elif dt == "no_mod_application":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC6", category="Mod / Change",
                disc_type="Unauthorized Modification",
                description=f"[{m['mod_id']}] Equipment change on {m['tower_id']} without approved mod application — compliance violation",
                contract_id=m.get("contract_id", ""), tower_id=m["tower_id"],
                est_annual_impact=rate_change * 12,
            ))
        elif dt == "non_conformance":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC6", category="Mod / Change",
                disc_type="Installation Non-Conformance",
                description=f"[{m['mod_id']}] {m['carrier']} install on {m['tower_id']} doesn't match approved plans — wind load/interference risk",
                contract_id=m.get("contract_id", ""), tower_id=m["tower_id"],
            ))

    # ━━━ UC7: Revenue Share ↔ Actual Tenant Revenue ━━━━━━━━━━━━━━━━━━━━

    # Group tenant revenue by tower
    tenant_revenue_by_tower = defaultdict(float)
    tenant_count_by_tower = defaultdict(int)
    for cid, c in contracts.items():
        if c.contract_type == "tenant_lease" and c.lease_status in ("Active", "Pending Renewal"):
            tenant_revenue_by_tower[c.tower_id] += c.monthly_amount
            tenant_count_by_tower[c.tower_id] += 1

    # Ground leases with rev-share potential
    for cid, c in contracts.items():
        if c.contract_type != "ground_lease":
            continue
        tower_rev = tenant_revenue_by_tower.get(c.tower_id, 0)
        tower_tenants = tenant_count_by_tower.get(c.tower_id, 0)
        if tower_rev <= 0:
            continue
        if c.divestiture_impacted:
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC7", category="Revenue Share",
                disc_type="Divestiture Rev-Share Impact",
                description=f"Ground lease {cid} ({c.tower_id}) flagged for divestiture — verify fiber revenue excluded from rev-share post-Zayo carveout",
                contract_id=cid, tower_id=c.tower_id,
                est_annual_impact=tower_rev * 0.05 * 12,
            ))

    # ━━━ UC8: Site Access ↔ Mod Applications ↔ Physical ━━━━━━━━━━━━━━━━

    for log in access_logs:
        dt = log.get("discrepancy_type", "none")
        if dt == "none":
            continue

        if dt == "no_approved_mod":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC8", category="Site Access",
                disc_type="Access Without Approved Mod",
                description=f"[{log['access_id']}] {log['carrier']} access on {log['tower_id']} for '{log['purpose']}' — no matching mod application",
                contract_id="", tower_id=log["tower_id"],
            ))
        elif dt == "unauthorized_access":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC8", category="Site Access",
                disc_type="Unauthorized Site Access",
                description=f"[{log['access_id']}] Unidentified access on {log['tower_id']} ({log['access_date']}) — no work order, contractor, or appointment",
                contract_id="", tower_id=log["tower_id"],
            ))

    # ━━━ UC9: Tax Assessment ↔ Pass-Through ↔ Physical ━━━━━━━━━━━━━━━━━

    for t in tax_records:
        dt = t.get("discrepancy_type", "none")
        if dt == "none":
            continue

        tax_delta = float(t.get("pass_through_delta_usd", 0))

        if dt == "pass_through_not_invoiced":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC9", category="Tax",
                disc_type="Tax Not Passed Through",
                description=f"{t['tower_id']}: ${float(t['annual_property_tax_usd']):,.0f} annual tax with NO pass-through invoice — Summit absorbing",
                contract_id="", tower_id=t["tower_id"],
                est_annual_impact=float(t["annual_property_tax_usd"]),
            ))
        elif dt == "wrong_assessment_basis":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC9", category="Tax",
                disc_type="Pass-Through on Old Assessment",
                description=f"{t['tower_id']}: pass-through ${float(t['pass_through_invoiced_usd']):,.0f} vs actual tax ${float(t['annual_property_tax_usd']):,.0f} — stale assessment basis",
                contract_id="", tower_id=t["tower_id"],
                est_annual_impact=abs(tax_delta),
            ))
        elif dt == "tenant_count_stale":
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC9", category="Tax",
                disc_type="Tax Assessment Tenant Count Stale",
                description=f"{t['tower_id']}: assessed for {t['assessed_tenant_count']} tenants but {t['actual_tenant_count']} active — reassessment needed",
                contract_id="", tower_id=t["tower_id"],
            ))
        elif dt == "decommissioned_exemption":
            _add(Discrepancy(
                severity="🟢 Info", use_case="UC9", category="Tax",
                disc_type="Stale Tax Exemption",
                description=f"{t['tower_id']}: tax exemption filed for decommissioned equipment — inaccuracy risk",
                contract_id="", tower_id=t["tower_id"],
            ))

    # ━━━ Deadline tracking + DISH exposure ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    today = datetime(2025, 3, 15)
    for cid, c in contracts.items():
        if not c.end_date:
            continue
        try:
            end_dt = datetime.strptime(c.end_date, "%Y-%m-%d")
        except ValueError:
            continue
        days = (end_dt - today).days
        notice = c.termination_notice_days or 180

        if 0 < days <= notice and c.lease_status in ("Active", "Pending Renewal"):
            _add(Discrepancy(
                severity="🟡 Warning", use_case="UC5", category="Deadlines",
                disc_type="Expiring Within Notice Window",
                description=f"{cid} expires in {days}d ({c.end_date}), within {notice}d notice period",
                contract_id=cid, tower_id=c.tower_id,
                est_annual_impact=c.monthly_amount * 12 * 0.05,
            ))
            r.contracts_expiring_soon += 1

        if days < 0 and c.lease_status == "Active":
            _add(Discrepancy(
                severity="🔴 Critical", use_case="UC5", category="Deadlines",
                disc_type="Expired — Auto-Renewed",
                description=f"{cid} expired {abs(days)}d ago but still Active — auto-renewed at existing terms?",
                contract_id=cid, tower_id=c.tower_id,
                est_annual_impact=c.monthly_amount * 12 * 0.03,
            ))
            r.auto_renewal_risk += 1

        # DISH
        if c.carrier == "DISH Wireless":
            r.dish_active_count += 1
            if c.dish_default_status not in ("N/A", ""):
                r.dish_defaulted_count += 1
                r.dish_total_exposure += c.outstanding_obligation
                _add(Discrepancy(
                    severity="🔴 Critical", use_case="UC5", category="DISH Default",
                    disc_type="DISH Default Exposure",
                    description=f"DISH {cid}: {c.dish_default_status}, outstanding ${c.outstanding_obligation:,.2f}",
                    contract_id=cid, tower_id=c.tower_id,
                    est_annual_impact=c.monthly_amount * 12,
                ))

    # ━━━ Summarize ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    r.matched_contracts = len(contracts_with_invoices)
    r.unmatched_contracts = r.total_contracts - r.matched_contracts
    r.total_delta = round(r.total_invoice_value - r.total_expected_value, 2)

    for d in r.discrepancies:
        r.summary_by_type[d.disc_type] = r.summary_by_type.get(d.disc_type, 0) + 1
        r.summary_by_category[d.category] = r.summary_by_category.get(d.category, 0) + 1
        r.summary_by_use_case[d.use_case] = r.summary_by_use_case.get(d.use_case, 0) + 1
        r.est_total_annual_impact += d.est_annual_impact
        if "Critical" in d.severity:
            r.critical_count += 1
        elif "Warning" in d.severity:
            r.warning_count += 1
        else:
            r.info_count += 1

    r.total_discrepancies = len(r.discrepancies)
    return r


# ─── CLI report ───────────────────────────────────────────────────────────

USE_CASE_LABELS = {
    "UC1": "Physical ↔ Contract", "UC2": "Physical ↔ Invoice",
    "UC3": "RF Design ↔ As-Built", "UC4": "Structural Load",
    "UC5": "Escalation ↔ Invoice", "UC6": "Mod App ↔ Change ↔ Invoice",
    "UC7": "Rev-Share ↔ Tenant Rev", "UC8": "Site Access ↔ Mod App",
    "UC9": "Tax ↔ Pass-Through",
}

def print_report(r: ReconciliationResult):
    print("\n" + "=" * 74)
    print("  Summit — 9-WAY CROSS-REFERENCE RECONCILIATION REPORT")
    print("=" * 74)

    print(f"\n📊 DATA SOURCES LOADED")
    print(f"   Contracts:          {r.total_contracts:,}")
    print(f"   ERP Invoices:       {r.total_invoices:,}")
    print(f"   Tower Audits:       {r.total_audits:,}")
    print(f"   RF Design Specs:    {r.total_rf_specs:,}")
    print(f"   Structural Records: {r.total_structural:,}")
    print(f"   Mod Applications:   {r.total_mod_apps:,}")
    print(f"   Site Access Logs:   {r.total_access_logs:,}")
    print(f"   Tax Assessments:    {r.total_tax_records:,}")

    print(f"\n💰 FINANCIAL SUMMARY")
    print(f"   Invoice value:         ${r.total_invoice_value:,.2f}")
    print(f"   Expected value:        ${r.total_expected_value:,.2f}")
    print(f"   Net delta:             ${r.total_delta:+,.2f}")
    print(f"   Est. annual impact:    ${r.est_total_annual_impact:,.0f}")

    print(f"\n⚠️  TOTAL DISCREPANCIES: {r.total_discrepancies}")
    print(f"   🔴 Critical:  {r.critical_count}")
    print(f"   🟡 Warning:   {r.warning_count}")
    print(f"   🟢 Info:      {r.info_count}")

    print(f"\n📋 BY USE CASE:")
    for uc, count in sorted(r.summary_by_use_case.items()):
        label = USE_CASE_LABELS.get(uc, uc)
        print(f"   {uc}: {label:30s} {count:5d}")

    print(f"\n📋 BY CATEGORY:")
    for cat, count in sorted(r.summary_by_category.items(), key=lambda x: -x[1]):
        print(f"   {cat:25s} {count:5d}")

    if r.dish_active_count:
        print(f"\n📡 DISH: {r.dish_defaulted_count} defaulted / {r.dish_active_count} total, exposure ${r.dish_total_exposure:,.0f}")
    if r.undersold_towers:
        print(f"\n🏗️ UNDERSOLD: {r.undersold_towers} towers, ${r.undersold_monthly_opportunity:,.0f}/mo opportunity")
    if r.contracts_expiring_soon or r.auto_renewal_risk:
        print(f"\n⏰ DEADLINES: {r.contracts_expiring_soon} expiring soon, {r.auto_renewal_risk} auto-renewed")


def main():
    r = reconcile()
    print_report(r)


if __name__ == "__main__":
    main()
