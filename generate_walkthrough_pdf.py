#!/usr/bin/env python3
"""Generate a Proof-of-Walkthrough PDF for the ECL 9-Way Reconciliation Demo."""

import os
from fpdf import FPDF

ARTIFACTS = "/Users/yakarteek/.gemini/antigravity/brain/d16f359d-0a00-49a6-9412-3cb221f93fc7"
OUT = "/Users/yakarteek/Code/Accion/Summit/ECL/slides/ECL_Reconciliation_Walkthrough.pdf"

SCREENSHOTS = [
    ("01_ecl_studio_home_1771896947463.png",        "Step 1: ECL Studio - Home Page"),
    ("02_sample_loaded_1771896955088.png",           "Step 2: Sample Tower Report Loaded"),
    ("03_extraction_complete_1771896986017.png",     "Step 3: Live Entity Extraction Complete"),
    ("04_recon_tab_intro_retry_1771897127003.png",   "Step 4: Invoice Recon Tab - Simulated Data Banner"),
    ("05_recon_results_1771897169537.png",           "Step 5: 9-Way Reconciliation Results - $47.3M Impact"),
    ("06_recon_table_final_1771897276071.png",       "Step 6: Discrepancy Table and Charts"),
]


class WalkthroughPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "ECL: The New ETL - Proof of Walkthrough", align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Accion Labs Innovation Summit 2026  |  Page {self.page_no()}/{{nb}}", align="C")


def build_pdf():
    pdf = WalkthroughPDF(orientation="L", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- TITLE PAGE ---
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 15, "ECL: The New ETL", align="C", new_x="LEFT", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 12, "9-Way Cross-Reference Reconciliation", align="C", new_x="LEFT", new_y="NEXT")
    pdf.cell(0, 12, "Proof of Walkthrough", align="C", new_x="LEFT", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Accion Labs Innovation Summit 2026", align="C", new_x="LEFT", new_y="NEXT")
    pdf.cell(0, 10, "February 23, 2026", align="C", new_x="LEFT", new_y="NEXT")

    # --- EXECUTIVE SUMMARY ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 12, "Executive Summary", new_x="LEFT", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(40, 40, 40)
    lines = [
        "This document provides visual proof of the ECL (Entity-Context-Linking) platform's",
        "9-way cross-reference reconciliation engine, demonstrated live in ECL Studio.",
        "",
        "The demo shows two capabilities:",
        "",
        "1. LIVE ENTITY EXTRACTION - ECL extracts entities from unstructured tower lease",
        "   contracts using a local LLM (Ollama), with confidence scoring, MoE expert routing,",
        "   and full pipeline tracing. This runs in real-time with zero cloud cost.",
        "",
        "2. SIMULATED RECONCILIATION - The engine cross-references 8 data sources across",
        "   9 use case patterns, surfacing 2,810 discrepancies with $47.3M estimated annual",
        "   impact. Data is synthetic but mirrors Summit (~40,000 towers, $3.9B revenue).",
    ]
    for line in lines:
        pdf.cell(0, 6, line, new_x="LEFT", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Key Metrics", new_x="LEFT", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)

    metrics = [
        ("Total Discrepancies", "2,810"),
        ("Estimated Annual Impact", "$47,251,300"),
        ("DISH Default Exposure", "$66.7M (49 contracts)"),
        ("Undersold Towers", "141 ($593K/mo opportunity)"),
        ("Contracts Expiring Soon", "22"),
        ("Auto-Renewal Risk", "266 contracts"),
        ("Data Sources", "8 (contracts, invoices, audits, RF, structural, mods, access, tax)"),
        ("Cross-Reference Patterns", "9 (UC1-UC9)"),
    ]

    for label, value in metrics:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(70, 7, f"  {label}:")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, value, new_x="LEFT", new_y="NEXT")

    # --- 9 USE CASES ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 12, "9 Cross-Reference Use Cases", new_x="LEFT", new_y="NEXT")
    pdf.ln(5)

    use_cases = [
        ("UC1", "Physical Inventory vs Tenant Contract", "45", "Unbilled antennas, zombie tenants"),
        ("UC2", "Physical Inventory vs Invoice Lines", "22", "Sector underbilling"),
        ("UC3", "RF Design vs Physical As-Built", "107", "Tilt/azimuth drift, model mismatches"),
        ("UC4", "Structural Load vs Actual", "230", "Over-capacity, 141 undersold towers"),
        ("UC5", "Escalation vs Invoice History", "2,123", "CPI errors, missed escalations"),
        ("UC6", "Mod App vs Physical vs Invoice", "38", "Billing not updated after mods"),
        ("UC7", "Rev-Share vs Tenant Revenue", "-", "Divestiture rev-share flagged"),
        ("UC8", "Site Access vs Mod Applications", "194", "Unauthorized site access"),
        ("UC9", "Tax Assessment vs Pass-Through", "51", "Tax not passed through to tenants"),
    ]

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(30, 30, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(20, 8, "UC", border=1, fill=True, align="C")
    pdf.cell(90, 8, "Cross-Reference Pattern", border=1, fill=True)
    pdf.cell(25, 8, "Findings", border=1, fill=True, align="C")
    pdf.cell(0, 8, "What It Catches", border=1, fill=True, new_x="LEFT", new_y="NEXT")

    pdf.set_text_color(40, 40, 40)
    for i, (uc, pattern, findings, catches) in enumerate(use_cases):
        pdf.set_fill_color(240, 240, 250) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(20, 7, uc, border=1, fill=True, align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 7, pattern, border=1, fill=True)
        pdf.cell(25, 7, findings, border=1, fill=True, align="C")
        pdf.cell(0, 7, catches, border=1, fill=True, new_x="LEFT", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 8, "What is Real vs. Simulated", new_x="LEFT", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(35, 7, "  REAL (Live):")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, "Entity extraction, MoE routing, confidence scoring, tracing, FalkorDB, recon logic, UI", new_x="LEFT", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(35, 7, "  SIMULATED:")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, "1,250 contracts, 12,074 invoices, 235 audits, RF/structural/tax data, dollar amounts", new_x="LEFT", new_y="NEXT")

    # --- SCREENSHOT PAGES ---
    for fname, caption in SCREENSHOTS:
        path = os.path.join(ARTIFACTS, fname)
        if not os.path.exists(path):
            print(f"  Warning: Missing: {fname}")
            continue

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(30, 30, 80)
        pdf.cell(0, 12, caption, new_x="LEFT", new_y="NEXT")
        pdf.ln(3)

        usable_w = pdf.w - 2 * pdf.l_margin
        usable_h = pdf.h - pdf.get_y() - 25
        pdf.image(path, x=pdf.l_margin, w=usable_w, h=usable_h)

    # --- CLOSING PAGE ---
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 12, "Ready for Production", align="C", new_x="LEFT", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "POC in 2 weeks  |  Production data in 4 weeks  |  $47M+ annual impact at scale", align="C", new_x="LEFT", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Simulated data, real engine. The patterns mirror Summit portfolio.", align="C", new_x="LEFT", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 80)
    pdf.cell(0, 10, "Accion Labs  |  ECL: The New ETL", align="C", new_x="LEFT", new_y="NEXT")

    pdf.output(OUT)
    sz = os.path.getsize(OUT)
    print(f"\nPDF saved: {OUT}")
    print(f"   Pages: {pdf.page_no()}")
    print(f"   Size: {sz:,} bytes ({sz/1024:.0f} KB)")


if __name__ == "__main__":
    build_pdf()
