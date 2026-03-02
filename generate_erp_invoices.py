#!/usr/bin/env python3
"""
Generate realistic ERP invoice/billing data from contract CSVs.

Reads:
  - slides/crown_castle_ground_leases.csv
  - slides/crown_castle_tenant_leases.csv

Writes:
  - slides/erp_invoices.csv

~15-20% of invoices contain intentional discrepancies that the
reconciliation engine should flag.
"""

import csv
import os
import random
import hashlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GL_CSV = os.path.join(SCRIPT_DIR, "slides", "crown_castle_ground_leases.csv")
TL_CSV = os.path.join(SCRIPT_DIR, "slides", "crown_castle_tenant_leases.csv")
OUT_CSV = os.path.join(SCRIPT_DIR, "slides", "erp_invoices.csv")

# ERP system names to add variety
ERP_SYSTEMS = ["SAP S/4HANA", "Oracle EBS R12", "Oracle Cloud ERP",
               "SAP ECC 6.0", "Workday Financials"]

GL_ACCOUNTS = {
    "ground_rent": ["6110-001", "6110-002", "6110-100"],
    "tenant_revenue": ["4210-001", "4210-050", "4210-100"],
}

COST_CENTERS = [
    "CC-NORTHEAST", "CC-SOUTHEAST", "CC-MIDWEST",
    "CC-SOUTHWEST", "CC-WEST", "CC-NATIONAL",
]

# Carrier name variants for intentional mismatches
CARRIER_TYPOS = {
    "AT&T": ["AT&T", "AT&T Mobility", "ATT", "AT & T", "At&t Mobility LLC"],
    "T-Mobile": ["T-Mobile", "T-Mobile US", "TMobile", "T Mobile", "Sprint/T-Mobile"],
    "Verizon": ["Verizon", "Verizon Wireless", "VZW", "Cellco Partnership"],
    "DISH Wireless": ["DISH Wireless", "DISH", "Dish Network", "DISH Wireless LLC"],
    "US Cellular": ["US Cellular", "U.S. Cellular", "USCC", "United States Cellular"],
    "C Spire": ["C Spire", "C-Spire", "CSpire", "Cellular South"],
}

# State → region mapping for cost centers
STATE_REGIONS = {
    "CT": "CC-NORTHEAST", "MA": "CC-NORTHEAST", "NJ": "CC-NORTHEAST",
    "NY": "CC-NORTHEAST", "PA": "CC-NORTHEAST", "MD": "CC-NORTHEAST",
    "VA": "CC-NORTHEAST",
    "AL": "CC-SOUTHEAST", "FL": "CC-SOUTHEAST", "GA": "CC-SOUTHEAST",
    "KY": "CC-SOUTHEAST", "LA": "CC-SOUTHEAST", "NC": "CC-SOUTHEAST",
    "SC": "CC-SOUTHEAST", "TN": "CC-SOUTHEAST",
    "IA": "CC-MIDWEST", "IL": "CC-MIDWEST", "IN": "CC-MIDWEST",
    "MI": "CC-MIDWEST", "MN": "CC-MIDWEST", "MO": "CC-MIDWEST",
    "OH": "CC-MIDWEST", "WI": "CC-MIDWEST",
    "OK": "CC-SOUTHWEST", "TX": "CC-SOUTHWEST",
    "AZ": "CC-SOUTHWEST", "CO": "CC-SOUTHWEST",
    "CA": "CC-WEST", "OR": "CC-WEST", "WA": "CC-WEST",
}


def _seed(val):
    return int(hashlib.md5(val.encode()).hexdigest()[:8], 16)


def _invoice_id(rng):
    """Generate an ERP-style invoice ID."""
    prefix = rng.choice(["INV", "AP-INV", "BILL", "SI", "PO-INV"])
    num = rng.randint(100000, 999999)
    return f"{prefix}-{num}"


def _po_number(rng):
    prefix = rng.choice(["PO", "REQ", "PR"])
    return f"{prefix}-{rng.randint(400000, 999999)}"


def generate_ground_lease_invoices(rows):
    """Generate rent payment invoices for ground leases (AP side — Summit pays landlord)."""
    invoices = []

    for row in rows:
        cid = row["contract_id"]
        tid = row["tower_id"]
        monthly = float(row["monthly_rent_usd"])
        esc_pct = float(row["escalation_pct"])
        status = row["lease_status"]
        start_str = row["lease_start_date"]
        state = row["state"]
        ownership = row["ownership_type"]
        landowner = row["landowner_type"]

        # Skip owned sites — no rent to pay
        if ownership == "Owned" or monthly <= 0:
            continue

        rng = random.Random(_seed(cid))
        erp = rng.choice(ERP_SYSTEMS)
        cost_center = STATE_REGIONS.get(state, "CC-NATIONAL")
        gl_acct = rng.choice(GL_ACCOUNTS["ground_rent"])

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
        except ValueError:
            continue

        # Generate last 12 months of invoices (recent billing history)
        base_date = datetime(2025, 3, 1)  # "current" period
        years_since_start = max(0, (base_date - start_date).days / 365.25)

        # Expected current monthly with escalation
        expected_monthly = monthly * ((1 + esc_pct / 100) ** int(years_since_start))

        # Decide what kind of discrepancy (if any) this contract gets
        discrepancy = None
        if rng.random() < 0.18:  # ~18% have issues
            disc_roll = rng.random()
            if disc_roll < 0.25:
                discrepancy = "missed_escalation"
            elif disc_roll < 0.45:
                discrepancy = "amount_mismatch"
            elif disc_roll < 0.60:
                discrepancy = "over_escalation"
            elif disc_roll < 0.75:
                discrepancy = "duplicate"
            elif disc_roll < 0.88:
                discrepancy = "tower_id_typo"
            else:
                discrepancy = "wrong_gl"

        # Special case: billing on terminated contracts
        if status in ("Terminated", "Pending Termination") and rng.random() < 0.4:
            discrepancy = "billing_terminated"

        for month_offset in range(12):
            inv_date = base_date - relativedelta(months=month_offset)
            period = inv_date.strftime("%Y-%m")

            # Compute the invoice amount
            if discrepancy == "missed_escalation":
                # Still billing the original rate — didn't escalate
                inv_amount = monthly
            elif discrepancy == "amount_mismatch":
                # Off by a small random amount (data entry error)
                inv_amount = expected_monthly * rng.uniform(0.92, 1.08)
            elif discrepancy == "over_escalation":
                # Applied escalation twice
                inv_amount = expected_monthly * (1 + esc_pct / 100)
            elif discrepancy == "wrong_gl":
                # Amount is correct but GL is wrong
                inv_amount = expected_monthly
                gl_acct = rng.choice(GL_ACCOUNTS["tenant_revenue"])  # wrong account!
            else:
                inv_amount = expected_monthly

            inv_amount = round(inv_amount, 2)

            tower_ref = tid
            if discrepancy == "tower_id_typo" and month_offset < 3:
                # Typo in last 3 months
                parts = list(tid)
                idx = rng.randint(len(tid) - 3, len(tid) - 1)
                parts[idx] = str(rng.randint(0, 9))
                tower_ref = "".join(parts)

            contract_ref = cid
            if discrepancy == "tower_id_typo" and month_offset == 0:
                # Also mess up contract ref on latest
                contract_ref = cid[:-1] + rng.choice("0123456789ABCDEF")

            pay_status = rng.choice(["Paid", "Paid", "Paid", "Paid",
                                      "Pending", "Cleared"])
            if status == "Terminated":
                pay_status = rng.choice(["Disputed", "On Hold", "Pending"])

            notes = ""
            if discrepancy == "billing_terminated":
                # Most months won't have a note — that's the problem
                if month_offset == 0 and rng.random() < 0.3:
                    notes = "Contract terminated - pending AP review"
            elif discrepancy == "missed_escalation" and month_offset == 0:
                notes = ""  # No note — they don't know it's wrong
            elif discrepancy == "amount_mismatch" and month_offset < 2:
                if rng.random() < 0.2:
                    notes = "Rate adjusted per landlord request"

            inv = {
                "invoice_id": _invoice_id(rng),
                "erp_system": erp,
                "invoice_type": "AP",
                "contract_ref": contract_ref,
                "tower_ref": tower_ref,
                "vendor_or_tenant": landowner.replace("{city}", row["city"]).replace("{state}", state),
                "invoice_date": inv_date.strftime("%Y-%m-%d"),
                "billing_period": period,
                "invoiced_amount_usd": inv_amount,
                "expected_amount_usd": round(expected_monthly, 2),
                "payment_status": pay_status,
                "gl_account": gl_acct,
                "cost_center": cost_center,
                "po_number": _po_number(rng),
                "lease_status_at_billing": status,
                "discrepancy_planted": discrepancy or "",
                "notes": notes,
            }
            invoices.append(inv)

            # Duplicate invoice
            if discrepancy == "duplicate" and month_offset in (1, 4):
                dup = inv.copy()
                dup["invoice_id"] = _invoice_id(rng)
                dup["notes"] = ""
                invoices.append(dup)

        # For ~3% of active leases, skip generating invoices (unbilled)
        # This is handled by simply not generating invoices for some contracts
        # — already built in by the 18% branch above

    return invoices


def generate_tenant_lease_invoices(rows):
    """Generate revenue invoices for tenant leases (AR side — carrier pays Summit)."""
    invoices = []

    for row in rows:
        cid = row["contract_id"]
        tid = row["tower_id"]
        carrier = row["tenant_carrier"]
        monthly = float(row["monthly_revenue_usd"])
        esc_pct = float(row["escalation_pct"])
        status = row["lease_status"]
        start_str = row["lease_start_date"]
        state = row["state"]
        outstanding = float(row["outstanding_obligation_usd"])

        rng = random.Random(_seed(cid + "_tl"))
        erp = rng.choice(ERP_SYSTEMS)
        cost_center = STATE_REGIONS.get(state, "CC-NATIONAL")
        gl_acct = rng.choice(GL_ACCOUNTS["tenant_revenue"])

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
        except ValueError:
            continue

        base_date = datetime(2025, 3, 1)
        years_since_start = max(0, (base_date - start_date).days / 365.25)
        expected_monthly = monthly * ((1 + esc_pct / 100) ** int(years_since_start))

        # Skip ~3% of active contracts entirely (unbilled)
        if status == "Active" and rng.random() < 0.03:
            continue

        # Don't generate invoices for terminated leases (usually)
        if status == "Terminated" and rng.random() < 0.7:
            continue

        # Discrepancy assignment
        discrepancy = None
        if rng.random() < 0.16:
            disc_roll = rng.random()
            if disc_roll < 0.30:
                discrepancy = "missed_escalation"
            elif disc_roll < 0.50:
                discrepancy = "amount_mismatch"
            elif disc_roll < 0.65:
                discrepancy = "carrier_name"
            elif disc_roll < 0.78:
                discrepancy = "duplicate"
            elif disc_roll < 0.90:
                discrepancy = "over_escalation"
            else:
                discrepancy = "wrong_gl"

        if status == "Suspended" and rng.random() < 0.5:
            discrepancy = "billing_suspended"

        # Choose carrier name (sometimes wrong)
        carrier_name = carrier
        if discrepancy == "carrier_name":
            variants = CARRIER_TYPOS.get(carrier, [carrier])
            carrier_name = rng.choice([v for v in variants if v != carrier] or variants)

        for month_offset in range(12):
            inv_date = base_date - relativedelta(months=month_offset)
            period = inv_date.strftime("%Y-%m")

            if discrepancy == "missed_escalation":
                inv_amount = monthly  # original rate
            elif discrepancy == "amount_mismatch":
                inv_amount = expected_monthly * rng.uniform(0.90, 1.12)
            elif discrepancy == "over_escalation":
                inv_amount = expected_monthly * (1 + esc_pct / 100)
            elif discrepancy == "wrong_gl":
                inv_amount = expected_monthly
                gl_acct = rng.choice(GL_ACCOUNTS["ground_rent"])  # swapped!
            else:
                inv_amount = expected_monthly

            inv_amount = round(inv_amount, 2)

            pay_status = rng.choice(["Received", "Received", "Received",
                                      "Pending", "Cleared", "Applied"])
            if status == "Suspended":
                pay_status = rng.choice(["Past Due", "In Collections", "Disputed"])
            if outstanding > 0 and month_offset < 3:
                pay_status = rng.choice(["Past Due", "Partial", "Disputed"])

            notes = ""
            if discrepancy == "billing_suspended" and month_offset == 0:
                if rng.random() < 0.4:
                    notes = "Service suspended - billing continues per contract"
            if outstanding > 0 and month_offset == 0:
                notes = f"Outstanding balance: ${outstanding:,.2f}"

            inv = {
                "invoice_id": _invoice_id(rng),
                "erp_system": erp,
                "invoice_type": "AR",
                "contract_ref": cid,
                "tower_ref": tid,
                "vendor_or_tenant": carrier_name,
                "invoice_date": inv_date.strftime("%Y-%m-%d"),
                "billing_period": period,
                "invoiced_amount_usd": inv_amount,
                "expected_amount_usd": round(expected_monthly, 2),
                "payment_status": pay_status,
                "gl_account": gl_acct,
                "cost_center": cost_center,
                "po_number": _po_number(rng),
                "lease_status_at_billing": status,
                "discrepancy_planted": discrepancy or "",
                "notes": notes,
            }
            invoices.append(inv)

            if discrepancy == "duplicate" and month_offset in (2, 5):
                dup = inv.copy()
                dup["invoice_id"] = _invoice_id(rng)
                dup["notes"] = "System-generated duplicate"
                invoices.append(dup)

    return invoices


def main():
    # Load ground leases
    gl_rows = []
    with open(GL_CSV, "r") as f:
        for row in csv.DictReader(f):
            gl_rows.append(row)

    # Load tenant leases
    tl_rows = []
    with open(TL_CSV, "r") as f:
        for row in csv.DictReader(f):
            tl_rows.append(row)

    print(f"📊 Loaded {len(gl_rows)} ground leases, {len(tl_rows)} tenant leases")

    gl_invoices = generate_ground_lease_invoices(gl_rows)
    tl_invoices = generate_tenant_lease_invoices(tl_rows)

    all_invoices = gl_invoices + tl_invoices
    random.shuffle(all_invoices)

    # Write CSV
    fieldnames = [
        "invoice_id", "erp_system", "invoice_type", "contract_ref",
        "tower_ref", "vendor_or_tenant", "invoice_date", "billing_period",
        "invoiced_amount_usd", "expected_amount_usd", "payment_status",
        "gl_account", "cost_center", "po_number", "lease_status_at_billing",
        "discrepancy_planted", "notes",
    ]

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_invoices)

    # Stats
    disc_counts = {}
    for inv in all_invoices:
        d = inv["discrepancy_planted"] or "clean"
        disc_counts[d] = disc_counts.get(d, 0) + 1

    ap_count = sum(1 for i in all_invoices if i["invoice_type"] == "AP")
    ar_count = sum(1 for i in all_invoices if i["invoice_type"] == "AR")

    print(f"\n✅ Generated {len(all_invoices)} ERP invoices → {OUT_CSV}")
    print(f"   AP (ground rent payments): {ap_count}")
    print(f"   AR (tenant revenue):       {ar_count}")
    print(f"\n📋 Discrepancy breakdown:")
    for d, c in sorted(disc_counts.items(), key=lambda x: -x[1]):
        pct = c / len(all_invoices) * 100
        print(f"   {d:25s} {c:5d}  ({pct:.1f}%)")


if __name__ == "__main__":
    main()
