#!/usr/bin/env python3
"""
Generate Summit contract documents (Markdown) from CSV data.

Reads:
  - slides/crown_castle_ground_leases.csv  → ground lease contracts
  - slides/crown_castle_tenant_leases.csv  → tenant license agreements

Writes to:
  - contracts/ground_leases/<contract_id>.md
  - contracts/tenant_leases/<contract_id>.md

IMPORTANT: These contracts intentionally contain inconsistencies in
formatting, terminology, section numbering, and clause inclusion —
mirroring the real-world chaos that ECL is designed to reconcile.
"""

import csv
import os
import random
import hashlib
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GL_CSV = os.path.join(SCRIPT_DIR, "slides", "crown_castle_ground_leases.csv")
TL_CSV = os.path.join(SCRIPT_DIR, "slides", "crown_castle_tenant_leases.csv")
GL_OUT = os.path.join(SCRIPT_DIR, "contracts", "ground_leases")
TL_OUT = os.path.join(SCRIPT_DIR, "contracts", "tenant_leases")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LANDOWNER_NAMES = {
    "Private Individual": [
        "Robert J. Mitchell", "Sarah K. O'Brien", "David and Linda Chen",
        "Margaret A. Thornton", "James W. Patterson", "Patricia L. Foster",
        "William R. Hawkins", "Elizabeth M. Rodriguez", "Thomas P. Callahan",
        "Nancy J. Whitfield", "George & Helen Braxton",
    ],
    "Municipality": [
        "City of {city}", "Town of {city}", "{city} Municipal Government",
    ],
    "County Government": [
        "{city} County Government", "County of {city}",
        "Board of Supervisors, {city} County",
    ],
    "School District": [
        "{city} Unified School District", "{city} Independent School District",
        "{city} Public Schools", "Board of Education, {city}",
    ],
    "Church/Religious Org": [
        "First Baptist Church of {city}", "St. Mary's Catholic Parish",
        "Grace Community Church", "Temple Beth Shalom of {city}",
        "Calvary Presbyterian Church",
    ],
    "State DOT": [
        "{state} Department of Transportation",
        "{state} Dept. of Transportation",
        "DOT — State of {state}",
    ],
    "Federal Agency": [
        "U.S. General Services Administration",
        "U.S. Department of the Interior",
        "General Services Admin.",
    ],
    "Agricultural Land Trust": [
        "{city} Agricultural Preservation Trust",
        "{state} Farmland Trust",
        "{city} Land Conservation Trust",
    ],
    "Commercial Property Owner": [
        "{city} Commerce Center LLC", "Apex Property Holdings",
        "National Realty Partners LLC", "Landmark Commercial Properties",
        "{city} Industrial Park Associates",
    ],
    "Tribal Authority": [
        "{state} Tribal Land Authority", "Native American Heritage Trust",
    ],
    "Summit (Owned)": [
        "Summit USA Inc. (Self-Owned)",
    ],
}

CARRIER_LEGAL = {
    "AT&T": "AT&T Mobility LLC",
    "T-Mobile": "T-Mobile USA Inc.",
    "Verizon": "Cellco Partnership d/b/a Verizon Wireless",
    "DISH Wireless": "DISH Network Corporation d/b/a DISH Wireless",
    "US Cellular": "United States Cellular Corporation",
    "C Spire": "C Spire Wireless d/b/a Cellular South",
}

CARRIER_HQ = {
    "AT&T": "208 S. Akard St., Dallas, TX 75202",
    "T-Mobile": "12920 SE 38th St., Bellevue, WA 98006",
    "Verizon": "One Verizon Way, Basking Ridge, NJ 07920",
    "DISH Wireless": "9601 S. Meridian Blvd., Englewood, CO 80112",
    "US Cellular": "8410 W. Bryn Mawr Ave., Chicago, IL 60631",
    "C Spire": "1018 Highland Colony Pkwy, Ridgeland, MS 39157",
}

ANTENNA_MODELS = {
    "AT&T": ["CommScope FFHH-65C-R3", "Ericsson AIR 6449", "Nokia AirScale ABIA",
             "RFS APXVAARR13_43-U-NA20"],
    "T-Mobile": ["Ericsson AIR 6449 B41", "Nokia AAFIA", "CommScope SBNHH-1D65C",
                 "RFS APX16DWV-14406-CA"],
    "Verizon": ["CommScope FFHH-65C-R3-V2", "Samsung MT6407", "Ericsson AIR 3246",
                "JMA MX08FRO612-65X"],
    "DISH Wireless": ["Nokia AAHQA", "Ericsson AIR 3219", "Samsung DUS-1FAE"],
    "US Cellular": ["CommScope NHH-65C-R2B", "Andrew DBXLH-6565C-VTM"],
    "C Spire": ["CommScope NHH-45C-R1A", "Kathrein 80010951"],
}

RRU_MODELS = {
    "AT&T": "Ericsson Radio 4449 B2/B66",
    "T-Mobile": "Nokia AirScale AAHF B41/B71",
    "Verizon": "Nokia AirScale AAHF B2/B4/B66",
    "DISH Wireless": "Nokia AAHQA B71",
    "US Cellular": "Ericsson Radio 2219 B5/B12",
    "C Spire": "Nokia AirScale AAIA B2/B25",
}


def _seed(cid):
    """Deterministic seed from contract ID."""
    return int(hashlib.md5(cid.encode()).hexdigest()[:8], 16)


def _fmt_date(d, style=0):
    """Format date with inconsistent styles."""
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        return d
    if style == 0:
        return dt.strftime("%B %d, %Y")         # "March 15, 2028"
    elif style == 1:
        return dt.strftime("%b. %d, %Y")         # "Mar. 15, 2028"
    elif style == 2:
        return dt.strftime("%m/%d/%Y")            # "03/15/2028"
    elif style == 3:
        return dt.strftime("%d %B %Y")            # "15 March 2028"
    elif style == 4:
        return dt.strftime("%B %d, %Y").replace(" 0", " ")  # strip leading 0
    else:
        return dt.strftime("%Y-%m-%d")            # ISO


def _pick_landowner(landowner_type, city, state, rng):
    templates = LANDOWNER_NAMES.get(landowner_type, ["Unknown Property Owner"])
    tpl = rng.choice(templates)
    return tpl.format(city=city, state=state)


# ---------------------------------------------------------------------------
# Ground Lease Generator — WITH INCONSISTENCIES
# ---------------------------------------------------------------------------

# Different "styles" for section headers — some use Article, some Section,
# some just bold numbers, some use roman numerals
_GL_SECTION_STYLES = [
    ("## ARTICLE {n}: {title}", "**{n}.{s}"),        # Article 1: TERM ... 1.1
    ("## Section {n} — {title}", "**{n}.{s}"),        # Section 1 — TERM
    ("## {n}. {title}", "**{n}.{s}"),                 # 1. TERM
    ("### ARTICLE {roman}. {title}", "**{roman}.{s}"),  # ARTICLE I. TERM
    ("## Part {n}: {title}", "**({alpha})**"),         # Part 1: TERM ... (a)
]

_ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
          7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
          13: "XIII", 14: "XIV"}

_ALPHA = "abcdefghijklmnopqrstuvwxyz"

# Different title phrasings for the same concept
_TITLE_VARIANTS = {
    "premises": ["LEASED PREMISES", "PREMISES", "THE PROPERTY", "SITE DESCRIPTION",
                  "DESCRIPTION OF LEASED AREA"],
    "term": ["TERM", "LEASE TERM", "DURATION", "TERM OF AGREEMENT",
             "LEASE DURATION AND RENEWAL"],
    "rent": ["RENT AND PAYMENT TERMS", "RENT", "COMPENSATION",
             "MONTHLY RENT", "RENTAL PAYMENTS", "FINANCIAL TERMS"],
    "use": ["USE OF LEASED PREMISES", "PERMITTED USE", "USE OF PROPERTY",
            "AUTHORIZED USE", "USE RESTRICTIONS"],
    "construction": ["CONSTRUCTION AND INSTALLATION", "CONSTRUCTION",
                     "IMPROVEMENTS", "TOWER CONSTRUCTION", "BUILDING RIGHTS"],
    "termination": ["TERMINATION RIGHTS", "TERMINATION",
                    "EARLY TERMINATION", "CANCELLATION PROVISIONS",
                    "TERMINATION AND DEFAULT"],
    "insurance": ["INSURANCE AND INDEMNIFICATION", "INSURANCE",
                  "LIABILITY AND INSURANCE", "RISK MANAGEMENT"],
    "environmental": ["ENVIRONMENTAL MATTERS", "ENVIRONMENTAL COMPLIANCE",
                      "ENVIRONMENTAL", "HAZARDOUS MATERIALS"],
    "general": ["GENERAL PROVISIONS", "MISCELLANEOUS", "GENERAL TERMS",
                "ADDITIONAL PROVISIONS", "BOILERPLATE"],
}

# Different intro phrasings
_INTRO_VARIANTS = [
    '**THIS GROUND LEASE AGREEMENT** ("Agreement") is entered into as of {date} ("Effective Date"), by and between:',
    '**THIS GROUND LEASE** ("Lease") is made and entered into this {date}, by and between the following parties:',
    '**GROUND LEASE AGREEMENT** — This Agreement dated {date} (the "Commencement Date") is between:',
    'This GROUND LEASE AGREEMENT (hereinafter referred to as the "Agreement") is entered into effective {date}, between:',
    '**LEASE AGREEMENT** for wireless communications tower site, effective as of {date}, between the undersigned parties:',
    'THIS LEASE made {date} between the Lessor and Lessee identified below:',
]

# Random extra clauses that appear in some contracts but not others
_EXTRA_CLAUSES = [
    """
**{sec} Right of First Refusal.** In the event Lessor receives a bona fide offer to purchase the Property, Lessee shall have a right of first refusal to purchase the Property on the same terms. Lessee must exercise this right within thirty (30) days of receipt of written notice from Lessor.
""",
    """
**{sec} Quiet Enjoyment.** Lessor covenants and warrants that Lessee shall peaceably and quietly hold, occupy, and enjoy the Leased Premises during the term of this Lease without hindrance or interference from Lessor or any person claiming through Lessor.
""",
    """
**{sec} Memorandum of Lease.** The parties shall execute and record a short-form memorandum of this Agreement in the land records of the county where the Property is situated, to give constructive notice of Lessee's interest.
""",
    """
**{sec} Force Majeure.** Neither party shall be liable for delays due to acts of God, war, terrorism, pandemic, labor disputes, or governmental action, provided that payment obligations are not excused by this clause.
""",
    """
**{sec} Lessee's Right to Cure.** In the event of any default by Lessor under any mortgage or deed of trust encumbering the Property, Lessee shall have the right, but not the obligation, to cure such default on Lessor's behalf, and any amounts so paid shall be credited against future rent.
""",
    """
**{sec} Hazard Insurance.** Lessor shall maintain fire and extended coverage insurance on all structures other than Lessee's improvements, with coverage limits reasonably satisfactory to Lessee.
""",
    """
**{sec} Estoppel Certificates.** Each party agrees, within twenty (20) days after request, to execute an estoppel certificate confirming the status of this Agreement, the rent payable, and whether any defaults exist.
""",
    """
**{sec} Non-Disturbance.** Lessor shall use commercially reasonable efforts to obtain from any mortgagee or ground lessor a non-disturbance agreement in favor of Lessee, providing that Lessee's rights under this Agreement will not be disturbed so long as Lessee is not in default.
""",
    """
**{sec} Access and Parking.** Lessee, its employees, agents and contractors shall have unrestricted vehicular and pedestrian access to the Premises on a 24 hour / 7 day a week basis over existing roads, lanes and pathways.
""",
    """
**{sec} Signage.** Lessee may, at Lessee's sole cost, install identification signage on the Leased Premises in compliance with applicable ordinances and subject to Lessor's prior written approval, which shall not be unreasonably withheld.
""",
]


def generate_ground_lease(row, idx):
    cid = row["contract_id"]
    rng = random.Random(_seed(cid))

    tid = row["tower_id"]
    city = row["city"]
    state = row["state"]
    tower_type = row["tower_type"]
    tower_height = row["tower_height_ft"]
    zone = row["zone_type"]
    ownership = row["ownership_type"]
    landowner_type = row["landowner_type"]
    start = row["lease_start_date"]
    initial_end = row["initial_term_end_date"]
    max_expiry = row["max_lease_expiry"]
    init_years = row["initial_term_years"]
    renewals = row["renewal_terms"]
    renewal_years = row["renewal_term_years"]
    monthly_rent = float(row["monthly_rent_usd"])
    annual_rent = float(row["annual_rent_usd"])
    esc_pct = float(row["escalation_pct"])
    esc_type = row["escalation_type"]
    term_notice = int(row["termination_notice_days"])
    exclusive = row["exclusive_use_clause"] == "True"
    status = row["lease_status"]
    divestiture = row["divestiture_impacted"] == "True"

    is_owned = ownership == "Owned"
    if is_owned:
        # ~30% of owned sites get a brief memo, rest get a one-liner record
        if rng.random() < 0.3:
            return _gen_owned_memo_long(cid, tid, city, state, tower_type,
                                        tower_height, zone, start, status,
                                        divestiture, rng)
        else:
            return _gen_owned_memo_short(cid, tid, city, state, tower_type,
                                         tower_height, zone, start, status,
                                         divestiture, rng)

    landowner_name = _pick_landowner(landowner_type, city, state, rng)

    # --- Pick inconsistent style choices ---
    date_style = rng.randint(0, 4)
    sec_style_idx = rng.randint(0, len(_GL_SECTION_STYLES) - 1)
    sec_header_tpl, sub_tpl = _GL_SECTION_STYLES[sec_style_idx]
    intro_tpl = rng.choice(_INTRO_VARIANTS)

    # Some contracts use "Lessor/Lessee", others use "Landlord/Tenant",
    # others use "Owner/Operator"
    party_style = rng.choice([
        ("Lessor", "Lessee"),
        ("Landlord", "Tenant"),
        ("Landowner", "Lessee"),
        ("Owner", "Operator"),
        ("Lessor", "Lessee"),  # weighted toward standard
        ("Lessor", "Lessee"),
    ])
    p_lessor, p_lessee = party_style

    # Whether to include certain optional sections
    include_environmental = rng.random() > 0.25
    include_construction = rng.random() > 0.15
    include_assignment = rng.random() > 0.4
    include_taxes = rng.random() > 0.35
    num_extra_clauses = rng.randint(0, 3)

    # Some contracts put the title differently
    title = rng.choice([
        "# GROUND LEASE AGREEMENT",
        "# GROUND LEASE",
        "# LEASE AGREEMENT — TOWER SITE",
        "# LAND LEASE AGREEMENT",
        "# SITE LEASE AGREEMENT",
        "# WIRELESS TOWER GROUND LEASE",
    ])

    # Some contracts include contract ID at top, some bury it, some omit
    id_placement = rng.choice(["top", "bottom", "none"])

    # Section counter
    sec_n = [0]
    def _sec(topic):
        sec_n[0] += 1
        n = sec_n[0]
        t = rng.choice(_TITLE_VARIANTS.get(topic, [topic.upper()]))
        return sec_header_tpl.format(n=n, title=t, roman=_ROMAN.get(n, str(n)))

    def _sub(s):
        n = sec_n[0]
        return sub_tpl.format(n=n, s=s, roman=_ROMAN.get(n, str(n)),
                              alpha=_ALPHA[s-1] if s <= 26 else str(s))

    # Start building
    parts = []
    parts.append(title)
    parts.append("")
    if id_placement == "top":
        parts.append(f"**Contract ID:** {cid}  ")
        parts.append(f"**Tower Site:** {tid}")
        parts.append("")

    # Intro
    formatted_date = _fmt_date(start, date_style)
    parts.append(intro_tpl.format(date=formatted_date))
    parts.append("")

    # Party block — different formatting styles
    if rng.random() > 0.5:
        parts.append(f"**{p_lessor.upper()}:**  ")
        parts.append(f"{landowner_name}  ")
        parts.append(f"{city}, {state}  ")
        parts.append(f'("{p_lessor}")')
        parts.append("")
        parts.append(f"**{p_lessee.upper()}:**  ")
        parts.append("Summit USA Inc.  ")
        parts.append("2000 Corporate Drive  ")
        parts.append('Canonsburg, PA 15317  ')
        parts.append(f'("{p_lessee}" or "Summit")')
    else:
        # Table style
        parts.append(f"| Party | Name | Address |")
        parts.append(f"|-------|------|---------|")
        parts.append(f"| {p_lessor} | {landowner_name} | {city}, {state} |")
        parts.append(f"| {p_lessee} | Summit USA Inc. | 2000 Corporate Drive, Canonsburg, PA 15317 |")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Recitals — some contracts include them, some skip
    if rng.random() > 0.3:
        recital_header = rng.choice(["## RECITALS", "## BACKGROUND", "## WHEREAS",
                                      "## PREAMBLE"])
        parts.append(recital_header)
        parts.append("")
        parts.append(f"WHEREAS, {p_lessor} is the owner of certain real property located in {city}, {state};")
        parts.append("")
        parts.append(f"WHEREAS, {p_lessee} desires to lease a portion of the Property for wireless communications infrastructure;")
        parts.append("")
        if rng.random() > 0.5:
            parts.append(f"WHEREAS, the parties have agreed on the terms set forth herein;")
            parts.append("")
        parts.append("NOW, THEREFORE, the parties agree as follows:")
        parts.append("")
        parts.append("---")
        parts.append("")

    # === SECTION: PREMISES ===
    parts.append(_sec("premises"))
    parts.append("")
    if rng.random() > 0.5:
        parts.append(f"{_sub(1)} Premises.** {p_lessor} hereby leases to {p_lessee} a portion of the Property for a **{tower_type}** tower, maximum height **{tower_height} feet**, in a **{zone}** zone. See **Exhibit B**.")
    else:
        parts.append(f"{_sub(1)} Description.** The leased area consists of sufficient space for a {tower_type} tower structure ({tower_height} ft) and associated equipment compound, located within a {zone} area in {city}, {state}.")
    parts.append("")
    # Some contracts include tower site ID here
    if rng.random() > 0.5:
        parts.append(f"{_sub(2)} Tower Site Identifier.** {tid}")
        parts.append("")
    # Access clause — sometimes present, sometimes not
    if rng.random() > 0.3:
        access_wording = rng.choice([
            f"{_sub(3 if rng.random() > 0.5 else 2)} Access.** {p_lessee} shall have 24/7 access to the Premises via existing roads.",
            f"{_sub(3 if rng.random() > 0.5 else 2)} Ingress/Egress.** {p_lessee} and its agents shall have unrestricted access to the Leased Premises at all times.",
            f"{_sub(3 if rng.random() > 0.5 else 2)} Access Rights.** Continuous access is granted over the Property for construction, maintenance, and operation purposes.",
        ])
        parts.append(access_wording)
        parts.append("")
    parts.append("---")
    parts.append("")

    # === SECTION: TERM ===
    parts.append(_sec("term"))
    parts.append("")
    # Different ways to express the term
    if rng.random() > 0.5:
        parts.append(f"{_sub(1)} Initial Term.** {init_years} years, from {_fmt_date(start, date_style)} to {_fmt_date(initial_end, rng.randint(0,4))}.")
    else:
        parts.append(f"{_sub(1)} Initial Term.** The initial term of this {'Agreement' if rng.random() > 0.5 else 'Lease'} shall be **{init_years} years**, commencing on {_fmt_date(start, date_style)} and expiring on {_fmt_date(initial_end, date_style)}.")
    parts.append("")
    parts.append(f"{_sub(2)} Renewal.** {'Automatically renews' if rng.random() > 0.5 else 'This Lease shall automatically renew'} for {renewals} additional terms of {renewal_years} years each{', unless either party provides written notice of non-renewal' if rng.random() > 0.5 else ''}.")
    parts.append("")
    # Some mention max expiry, some don't
    if rng.random() > 0.4:
        parts.append(f"{_sub(3)} Maximum Term.** The lease may extend through {_fmt_date(max_expiry, rng.randint(0,3))} including all renewal periods.")
        parts.append("")
    parts.append("---")
    parts.append("")

    # === SECTION: RENT ===
    parts.append(_sec("rent"))
    parts.append("")
    # Different ways to express rent
    rent_format = rng.choice(["prose", "table", "list"])
    if rent_format == "prose":
        parts.append(f"{_sub(1)} {'Base Rent' if rng.random() > 0.3 else 'Monthly Rent'}.** {p_lessee} shall pay {'base rent of' if rng.random() > 0.5 else 'monthly rent in the amount of'} **${monthly_rent:,.2f} per month** (${annual_rent:,.2f}{' per annum' if rng.random() > 0.5 else ' annually'}).")
    elif rent_format == "table":
        parts.append(f"{_sub(1)} Rent Schedule.**")
        parts.append("")
        parts.append("| Item | Amount |")
        parts.append("|------|--------|")
        parts.append(f"| Monthly Rent | ${monthly_rent:,.2f} |")
        parts.append(f"| Annual Rent | ${annual_rent:,.2f} |")
        parts.append(f"| Escalation | {esc_pct}% ({esc_type}) |")
    else:
        parts.append(f"{_sub(1)} Rent.**")
        parts.append(f"- Monthly: ${monthly_rent:,.2f}")
        parts.append(f"- Annual: ${annual_rent:,.2f}")
    parts.append("")

    if esc_pct > 0:
        esc_wording = rng.choice([
            f"{_sub(2)} Escalation.** Rent increases {esc_pct}% annually ({esc_type}).",
            f"{_sub(2)} Annual Increase.** Beginning on the first anniversary, rent escalates by {esc_pct}% per year. Escalation type: {esc_type}.",
            f"{_sub(2)} Rent Adjustment.** On each anniversary of the Effective Date, the Base Rent shall be adjusted upward by {esc_pct}% of the then-current rent amount. Method: {esc_type}.",
            f"{_sub(2)} CPI / Fixed Escalation.** The rent shall increase annually by {esc_pct}% ({esc_type}). No decrease shall apply in any year.",
        ])
        parts.append(esc_wording)
        parts.append("")

    # Some contracts include a payment method clause
    if rng.random() > 0.5:
        parts.append(f"{_sub(3)} Payment.** {'Rent is due on the first of each month' if rng.random() > 0.5 else 'Payments shall be made in advance on the 1st day of each calendar month'}, by {'check, wire transfer, or ACH' if rng.random() > 0.5 else 'electronic funds transfer to an account designated by ' + p_lessor}.")
        parts.append("")

    parts.append("---")
    parts.append("")

    # === SECTION: USE ===
    parts.append(_sec("use"))
    parts.append("")
    parts.append(f"{_sub(1)} Permitted Use.** {rng.choice(['The Premises shall be used solely for', p_lessee + ' may use the Leased Premises exclusively for', 'Permitted uses include'])} wireless communications equipment including {tower_type} tower ({tower_height} ft), antenna arrays, equipment {'shelters' if rng.random() > 0.5 else 'cabinets'}, and backup power.")
    parts.append("")
    if exclusive:
        excl_wording = rng.choice([
            f"{_sub(2)} Exclusive Use.** {p_lessee} has exclusive wireless communications rights on the Property.",
            f"{_sub(2)} Exclusivity.** {p_lessor} shall not permit any third party to install competing wireless equipment without {p_lessee}'s consent.",
            f"{_sub(2)} Exclusive Rights.** During the term, {p_lessor} grants {p_lessee} the exclusive right to install and operate wireless infrastructure on the Property. {p_lessor} will not enter into agreements with other wireless operators without {p_lessee}'s prior written approval.",
        ])
        parts.append(excl_wording)
        parts.append("")

    parts.append("---")
    parts.append("")

    # === OPTIONAL: CONSTRUCTION ===
    if include_construction:
        parts.append(_sec("construction"))
        parts.append("")
        parts.append(f"{_sub(1)} Right to Construct.** {p_lessee} may construct a {tower_type} structure (up to {tower_height} ft) per applicable codes{' including TIA-222-H' if rng.random() > 0.6 else ''}.")
        parts.append("")
        if rng.random() > 0.5:
            parts.append(f"{_sub(2)} Permits.** {p_lessee} {'is responsible for' if rng.random() > 0.5 else 'shall obtain'} all necessary permits and approvals.")
            parts.append("")
        # Some mention co-location, some don't
        if rng.random() > 0.6:
            parts.append(f"{_sub(3)} Co-Location.** {p_lessee} may sublicense tower space to wireless carriers under separate agreements.")
            parts.append("")
        parts.append("---")
        parts.append("")

    # === SECTION: TERMINATION ===
    parts.append(_sec("termination"))
    parts.append("")
    # Inconsistent notice period formatting
    notice_fmt = rng.choice([
        f"{term_notice} days'",
        f"{term_notice}-day",
        f"{term_notice} calendar days'",
        f"one hundred eighty (180) days'" if term_notice == 180 else f"{term_notice} days'",
        f"ninety (90) days'" if term_notice == 90 else f"{term_notice} days'",
    ])
    parts.append(f"{_sub(1)} {p_lessee}'s Right.** {p_lessee} may terminate upon {notice_fmt} prior written notice.")
    parts.append("")
    if rng.random() > 0.3:
        parts.append(f"{_sub(2)} {p_lessor}'s Rights.** {p_lessor} may terminate only for material breach uncured after {'sixty (60)' if rng.random() > 0.5 else '60'} days written notice, or abandonment for {'twelve (12)' if rng.random() > 0.5 else '12'} continuous months.")
        parts.append("")
    parts.append("---")
    parts.append("")

    # === SECTION: INSURANCE ===
    parts.append(_sec("insurance"))
    parts.append("")
    # Different insurance limit formats
    if rng.random() > 0.5:
        parts.append(f"{_sub(1)} Insurance.** {p_lessee} shall maintain CGL insurance: ${'2,000,000' if rng.random() > 0.4 else '1,000,000'} per occurrence / ${'5,000,000' if rng.random() > 0.4 else '3,000,000'} aggregate. {p_lessor} named as additional insured.")
    else:
        parts.append(f"{_sub(1)} Required Coverage.**")
        parts.append(f"- General Liability: $2M per occurrence")
        parts.append(f"- Property Insurance: replacement cost of {p_lessee}'s improvements")
        parts.append(f"- Workers' Comp: per statutory requirements")
    parts.append("")
    if rng.random() > 0.5:
        parts.append(f"{_sub(2)} Indemnification.** {p_lessee} shall indemnify and hold harmless {p_lessor} from claims arising from {p_lessee}'s operations.")
        parts.append("")
    parts.append("---")
    parts.append("")

    # === OPTIONAL: ENVIRONMENTAL ===
    if include_environmental:
        parts.append(_sec("environmental"))
        parts.append("")
        parts.append(f"{_sub(1)} {'Hazmat' if rng.random() > 0.7 else 'Environmental'} Compliance.** {p_lessor} represents the Property is free of contamination. {p_lessee} shall comply with all environmental laws.")
        parts.append("")
        parts.append("---")
        parts.append("")

    # === OPTIONAL: TAXES ===
    if include_taxes:
        sec_n[0] += 1
        n = sec_n[0]
        parts.append(f"## {'TAXES AND UTILITIES' if rng.random() > 0.5 else 'TAX OBLIGATIONS'}")
        parts.append("")
        parts.append(f"{p_lessor} pays real property taxes. {p_lessee} pays personal property taxes on its equipment and all utility costs for its operations.")
        parts.append("")
        parts.append("---")
        parts.append("")

    # === OPTIONAL: ASSIGNMENT ===
    if include_assignment:
        sec_n[0] += 1
        n = sec_n[0]
        parts.append(f"## {'ASSIGNMENT' if rng.random() > 0.5 else 'TRANSFER AND SUBLETTING'}")
        parts.append("")
        parts.append(f"{p_lessee} may assign this {'Agreement' if rng.random() > 0.5 else 'Lease'} without {p_lessor}'s consent to affiliates, successors, or entities acquiring substantially all of {p_lessee}'s assets.")
        parts.append("")
        parts.append("---")
        parts.append("")

    # === GENERAL PROVISIONS (sometimes present, sometimes not) ===
    if rng.random() > 0.3:
        parts.append(_sec("general"))
        parts.append("")
        parts.append(f"- **Governing Law:** {state}")
        parts.append(f"- **Notices:** Written, via certified mail or overnight courier")
        if rng.random() > 0.5:
            parts.append(f"- **Entire Agreement:** This constitutes the entire agreement")
        if rng.random() > 0.6:
            parts.append(f"- **Severability:** Invalid provisions do not affect remainder")
        parts.append("")

    # === EXTRA RANDOM CLAUSES ===
    if num_extra_clauses > 0:
        extras = rng.sample(_EXTRA_CLAUSES, min(num_extra_clauses, len(_EXTRA_CLAUSES)))
        for extra in extras:
            sec_n[0] += 1
            parts.append(extra.format(sec=f"{sec_n[0]}.1"))
            parts.append("")

    # === STATUS NOTE (some include, some don't) ===
    if status != "Active" or rng.random() > 0.7:
        parts.append(f"> **Lease Status:** {status}")
        parts.append("")

    if divestiture:
        div_note = rng.choice([
            f"> ⚠️ This lease is flagged for Summit's portfolio divestiture review.",
            f"**NOTE:** Divestiture-impacted property. See internal memo CC-DIV-{cid[-6:]}.",
            f"*This site has been identified in the FY2025 divestiture candidate list.*",
        ])
        parts.append(div_note)
        parts.append("")

    # === SIGNATURE BLOCK (varies) ===
    parts.append("---")
    parts.append("")
    sig_style = rng.choice(["formal", "simple", "table"])
    if sig_style == "formal":
        parts.append(f"**IN WITNESS WHEREOF**, the parties have executed this {'Agreement' if rng.random() > 0.5 else 'Lease'} as of the date first written above.")
        parts.append("")
        parts.append(f"**{p_lessor.upper()}:**  ")
        parts.append(f"\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_  ")
        parts.append(f"{landowner_name}  ")
        parts.append(f"Date: \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_")
        parts.append("")
        parts.append(f"**{p_lessee.upper()}:**  ")
        parts.append(f"**Summit USA INC.**  ")
        parts.append(f"By: \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_  ")
        parts.append(f"Title: \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_  ")
        parts.append(f"Date: \\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_")
    elif sig_style == "simple":
        parts.append(f"Signed: {landowner_name} ({p_lessor}) / Summit USA Inc. ({p_lessee})")
        parts.append(f"Date: {_fmt_date(start, date_style)}")
    else:
        parts.append("| Party | Signature | Date |")
        parts.append("|-------|-----------|------|")
        parts.append(f"| {landowner_name} | ________________ | ____________ |")
        parts.append(f"| Summit USA Inc. | ________________ | ____________ |")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Exhibit list (varies)
    if rng.random() > 0.3:
        parts.append(rng.choice(["## EXHIBITS", "**Exhibits:**", "### Attached Exhibits"]))
        parts.append("")
        parts.append(f"**Exhibit A:** Legal Description of Property  ")
        parts.append(f"**Exhibit B:** Site Plan ({tower_type}, {tower_height} ft)  ")
        if rng.random() > 0.5:
            parts.append(f"**Exhibit C:** Insurance Requirements")
        if rng.random() > 0.7:
            parts.append(f"**Exhibit D:** Environmental Assessment Summary")

    # Contract ID at bottom if placed there
    if id_placement == "bottom":
        parts.append("")
        parts.append(f"---")
        parts.append(f"*Internal Ref: {cid} | Site: {tid}*")

    return "\n".join(parts)


def _gen_owned_memo_long(cid, tid, city, state, tower_type, tower_height,
                          zone, start, status, divestiture, rng):
    date_style = rng.randint(0, 3)
    return f"""# TOWER SITE OWNERSHIP RECORD — Summit OWNED

**Record ID:** {cid}  
**Tower Site ID:** {tid}

---

## PROPERTY SUMMARY

| Field | Value |
|-------|-------|
| **Ownership** | Summit USA Inc. (Fee Simple) |
| **Location** | {city}, {state} |
| **Tower Type** | {tower_type} |
| **Tower Height** | {tower_height} ft |
| **Zone** | {zone} |
| **Acquired** | {_fmt_date(start, date_style)} |
| **Status** | {status} |

---

This tower site is **wholly owned** by Summit. No external ground lease obligation exists. Summit holds title in fee simple, eliminating ongoing landowner rent obligations.

- No monthly ground rent payable
- Tower co-location revenue retained 100% by Summit
- Property taxes paid directly by Summit
{"- **⚠️ DIVESTITURE FLAG:** Site under portfolio review." if divestiture else ""}

---
*Recorded: Summit Asset Management, {_fmt_date(start, date_style)}*
"""


def _gen_owned_memo_short(cid, tid, city, state, tower_type, tower_height,
                           zone, start, status, divestiture, rng):
    date_style = rng.randint(0, 4)
    fmt = rng.choice(["paragraph", "list", "oneliner"])
    if fmt == "paragraph":
        return f"""# CC-Owned Site: {tid}

{cid} — Summit-owned {tower_type} ({tower_height} ft) in {city}, {state} ({zone}). Acquired {_fmt_date(start, date_style)}. Status: {status}. No ground lease — fee simple ownership.{" Divestiture candidate." if divestiture else ""}
"""
    elif fmt == "list":
        return f"""# Site Ownership Record

- **ID:** {cid}
- **Tower:** {tid}
- **Type:** {tower_type}, {tower_height} ft
- **Location:** {city}, {state} ({zone})
- **Ownership:** Summit (Fee Simple)
- **Since:** {_fmt_date(start, date_style)}
- **Status:** {status}
{"- **Divestiture:** Yes" if divestiture else ""}
"""
    else:
        return f"""{cid} | {tid} | {city}, {state} | {tower_type} {tower_height}ft | CC-Owned | {_fmt_date(start, date_style)} | {status}{" | DIVEST" if divestiture else ""}
"""


# ---------------------------------------------------------------------------
# Tenant Lease Generator — lighter inconsistencies (more standardized under MLAs)
# ---------------------------------------------------------------------------

def generate_tenant_lease(row, idx):
    cid = row["contract_id"]
    rng = random.Random(_seed(cid))
    tid = row["tower_id"]
    mla = row["mla_reference"]
    carrier = row["tenant_carrier"]
    start = row["lease_start_date"]
    end = row["lease_end_date"]
    term_years = row["term_years"]
    monthly = float(row["monthly_revenue_usd"])
    annual = float(row["annual_revenue_usd"])
    esc = float(row["escalation_pct"])
    antennas = int(row["antenna_count"])
    height = int(row["mount_height_ft"])
    cabinet = row["equipment_cabinet"] == "True"
    ground_sqft = int(row["ground_space_sqft"])
    fiber = row["fiber_transport_included"] == "True"
    status = row["lease_status"]
    sprint_impact = row["sprint_merger_impact"] == "True"
    dish_default = row.get("dish_default_status", "N/A")
    force_majeure = row["force_majeure_claimed"] == "True"
    outstanding = float(row["outstanding_obligation_usd"])
    divestiture = row["divestiture_impacted"] == "True"
    city = row["city"]
    state = row["state"]
    zone = row["zone_type"]

    legal_name = CARRIER_LEGAL.get(carrier, carrier)
    hq = CARRIER_HQ.get(carrier, "Corporate Headquarters")
    date_style = rng.randint(0, 3)

    antenna_model = rng.choice(ANTENNA_MODELS.get(carrier, ["Generic Panel Antenna"]))
    rru_model = RRU_MODELS.get(carrier, "Standard RRU")

    sectors = max(1, antennas // 3) if antennas >= 3 else 1
    rru_count = sectors

    tower_rent = round(monthly * 0.55, 2)
    ground_rent = round(monthly * 0.25, 2)
    power_rent = round(monthly * 0.20, 2)

    # Title variation
    title_word = rng.choice(["LICENSE", "LEASE", "SUBLICENSE"])
    title = f"# TOWER SITE {title_word} AGREEMENT — {carrier.upper()}"

    # Some contracts call it "Commencement Date", others "Effective Date"
    date_name = rng.choice(["Commencement Date", "Effective Date", "Start Date"])

    # Some use "License Fee", others "Monthly Rent", others "Site Fee"
    fee_name = rng.choice(["License Fee", "Monthly Rent", "Site Fee", "Monthly Fee"])

    status_clause = ""
    if status == "Suspended":
        status_clause = f"""
---

## {"SUSPENSION NOTICE" if rng.random() > 0.5 else "LICENSE SUSPENSION"}

> **{"⚠️ " if rng.random() > 0.5 else ""}THIS {title_word} IS CURRENTLY SUSPENDED**

**Reason:** {dish_default if dish_default != "N/A" else "Operational Suspension"}
{"**Force Majeure:** Licensee has filed a force majeure claim." if force_majeure else ""}
{"**Outstanding Balance:** $" + f"{outstanding:,.2f}" if outstanding > 0 else ""}
"""
    elif status == "Terminated":
        status_clause = f"""
---

## TERMINATION RECORD

> This {title_word} Agreement has been **TERMINATED**.

**Reason:** {dish_default if dish_default != "N/A" else "Expiry or voluntary termination"}
{"**Unpaid balance at termination:** $" + f"{outstanding:,.2f}" if outstanding > 0 else ""}
Equipment removal deadline: 180 days from termination date.
"""

    sprint_clause = ""
    if sprint_impact:
        sprint_clause = rng.choice([
            "\n**Sprint Merger Note.** This license originated with Sprint Corp. Rights assumed by T-Mobile per FCC merger approval (April 2020). Equipment consolidation applies.\n",
            "\n> *Note: Originally a Sprint Corporation lease. Transferred to T-Mobile USA Inc. following the Sprint/T-Mobile merger. See FCC Order DA 19-1127.*\n",
            "\n**MERGER IMPACT:** Sprint → T-Mobile transition. All obligations transferred per Post-Merger Integration Plan.\n",
        ])

    # Build the contract
    parts = []
    parts.append(title)
    parts.append("")
    parts.append(f"**{title_word.title()} ID:** {cid}  ")
    parts.append(f"**Tower Site ID:** {tid}  ")
    parts.append(f"**MLA Reference:** {mla}")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Intro
    parts.append(f'**THIS TOWER SITE {title_word} AGREEMENT** ("{title_word.title()} Agreement") is entered into as of {_fmt_date(start, date_style)} ("{date_name}"), by and between:')
    parts.append("")
    parts.append("**LICENSOR:**  ")
    parts.append("Summit USA Inc.  ")
    parts.append("2000 Corporate Drive  ")
    parts.append('Canonsburg, PA 15317  ')
    parts.append('("Summit" or "Licensor")')
    parts.append("")
    parts.append("**LICENSEE:**  ")
    parts.append(f"{legal_name}  ")
    parts.append(f"{hq}  ")
    parts.append(f'("{carrier}" or "Licensee")')
    parts.append("")
    parts.append("---")
    parts.append("")

    # Recitals — some contracts include, some abbreviate
    if rng.random() > 0.2:
        parts.append("## RECITALS")
        parts.append("")
        parts.append(f"WHEREAS, Licensor operates tower **{tid}** in {city}, {state};")
        parts.append("")
        parts.append(f"WHEREAS, Licensee desires to install equipment pursuant to **{mla}**;")
        parts.append("")
        parts.append("NOW, THEREFORE, the parties agree:")
        parts.append("")
        parts.append("---")
        parts.append("")

    # Equipment section
    sec_label = rng.choice(["ARTICLE", "SECTION", "Part"])
    parts.append(f"## {sec_label} 1: LICENSED SPACE")
    parts.append("")
    parts.append(f"**1.1 Tower Space.** {rng.choice(['Space for', 'Licensor grants', 'Licensee receives'])} up to **{antennas} antenna(s)** at **{height} ft** RAD center, and **{rru_count} RRU(s)**.")

    if ground_sqft > 0 or cabinet:
        gnd = f"{ground_sqft} sq ft ground space" if ground_sqft > 0 else "standard ground area"
        cab = " with equipment cabinet" if cabinet else ""
        parts.append(f"- **Ground Space:** {gnd}{cab}")
    parts.append("")

    # Equipment table — sometimes present, sometimes just a list
    if rng.random() > 0.35:
        parts.append("**1.2 Equipment Manifest:**")
        parts.append("")
        parts.append("| Item | Qty | Model | Location |")
        parts.append("|------|-----|-------|----------|")
        parts.append(f"| Panel Antenna | {antennas} | {antenna_model} | {height}ft, {sectors} sector(s) |")
        parts.append(f"| RRU | {rru_count} | {rru_model} | {height}ft |")
        if cabinet:
            parts.append(f"| Cabinet | 1 | Outdoor enclosure | Ground |")
        if fiber:
            parts.append(f"| Fiber | 1 | 12-strand SM OS2 | Tower to cabinet |")
        parts.append(f"| Coax | {antennas} | {'1-5/8\"' if rng.random() > 0.5 else '7/8\"'} feedline | Tower to ground |")
    else:
        parts.append("**1.2 Equipment:**")
        parts.append(f"- {antennas}x {antenna_model} at {height} ft")
        parts.append(f"- {rru_count}x {rru_model}")
        if cabinet: parts.append(f"- 1x equipment cabinet ({ground_sqft} sq ft pad)")
        if fiber: parts.append(f"- Fiber transport included")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Term
    parts.append(f"## {sec_label} 2: TERM")
    parts.append("")
    parts.append(f"**2.1 Term.** {term_years} years, from {_fmt_date(start, date_style)} to {_fmt_date(end, rng.randint(0,3))}.")
    parts.append("")
    parts.append(f"**2.2 Zone:** {zone} | **Status:** {status}")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Fees
    parts.append(f"## {sec_label} 3: {fee_name.upper()}S")
    parts.append("")
    parts.append(f"**3.1 {fee_name}.** **${monthly:,.2f}/month** (${annual:,.2f}/year).")
    parts.append("")
    parts.append(f"**3.2 Escalation.** {esc}% annually.")
    parts.append("")

    # Fee breakdown — sometimes included
    if rng.random() > 0.4:
        parts.append(f"**3.3 Breakdown:**")
        parts.append(f"- Antenna space: ${tower_rent:,.2f}/mo")
        parts.append(f"- Ground space: ${ground_rent:,.2f}/mo")
        parts.append(f"- Power/utilities: ${power_rent:,.2f}/mo")
        parts.append("")
    parts.append("---")
    parts.append("")

    # Maintenance — sometimes detailed, sometimes brief
    parts.append(f"## {sec_label} 4: INSTALLATION & MAINTENANCE")
    parts.append("")
    if rng.random() > 0.5:
        parts.append("All installations per TIA-222-H, OSHA 1926.502, FCC 47 CFR 1.1310, and local codes. 24/7 maintenance access. Quarterly inspections required.")
    else:
        parts.append(f"**4.1 Standards.** Per TIA-222-H, FCC limits, and Licensor specs.")
        parts.append(f"**4.2 Access.** 24/7 for maintenance and emergencies.")
        parts.append(f"**4.3 Inspections.** Quarterly visual; annual RF verification.")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Insurance
    parts.append(f"## {sec_label} 5: INSURANCE")
    parts.append("")
    ins_limit = rng.choice(["$5,000,000", "$5M", "5,000,000"])
    parts.append(f"CGL: {ins_limit} per occurrence. Licensor as additional insured. Licensee indemnifies Licensor from all claims.")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Interference & Termination
    parts.append(f"## {sec_label} 6: INTERFERENCE")
    parts.append("")
    parts.append("Licensee shall not cause interference to prior installations. Priority based on installation date.")
    parts.append("")
    parts.append("---")
    parts.append("")

    parts.append(f"## {sec_label} 7: TERMINATION")
    parts.append("")
    parts.append("Licensee may terminate on 180 days' notice. Equipment removal within 180 days of termination. Nonpayment after 30 days' notice = default.")
    parts.append("")

    if status_clause:
        parts.append(status_clause)

    if sprint_clause:
        parts.append(sprint_clause)

    if divestiture:
        parts.append(rng.choice([
            "> Divestiture-impacted license. Licensee will be notified of ownership changes.\n",
            "**Note:** This site is under Summit portfolio divestiture review.\n",
        ]))

    # Signature
    parts.append("---")
    parts.append("")
    parts.append("**LICENSOR:** Summit USA Inc.  ")
    parts.append("By: \\_\\_\\_\\_ / Date: \\_\\_\\_\\_")
    parts.append("")
    parts.append(f"**LICENSEE:** {legal_name.upper()}  ")
    parts.append("By: \\_\\_\\_\\_ / Date: \\_\\_\\_\\_")
    parts.append("")
    parts.append("---")
    parts.append(f"*Exhibits: Site Plan ({tid}), Equipment Layout, MLA ({mla})*")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(GL_OUT, exist_ok=True)
    os.makedirs(TL_OUT, exist_ok=True)

    # Ground Leases
    gl_count = 0
    with open(GL_CSV, "r") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            cid = row["contract_id"]
            content = generate_ground_lease(row, idx)
            with open(os.path.join(GL_OUT, f"{cid}.md"), "w") as out:
                out.write(content)
            gl_count += 1

    print(f"✅ Generated {gl_count} ground lease contracts → {GL_OUT}/")

    # Tenant Leases
    tl_count = 0
    with open(TL_CSV, "r") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            cid = row["contract_id"]
            content = generate_tenant_lease(row, idx)
            with open(os.path.join(TL_OUT, f"{cid}.md"), "w") as out:
                out.write(content)
            tl_count += 1

    print(f"✅ Generated {tl_count} tenant lease contracts → {TL_OUT}/")
    print(f"\n📄 Total contracts generated: {gl_count + tl_count}")


if __name__ == "__main__":
    main()
