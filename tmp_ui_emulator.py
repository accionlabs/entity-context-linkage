import sys
import os
import json
sys.path.append("/Users/yakarteek/Code/Accion/Summit/ECL")

from ecl_app import run_extraction

text = """TOWER SITE INSPECTION REPORT
Tower ID: T-789 | Location: 40.6892° N, 74.0445° W | Type: Monopole | Height: 150ft

=== SECTION A: TENANT CONTRACTS ===

Contract #1001 - Company: Verizon Wireless
  Status: Active | Occupancy: 45% | Monthly Revenue: $5,000
  Lease Term: 2020-2030 | Auto-Renew: Yes
  Payment Status: Current | Outstanding: $0

Contract #1002 - Company: T-Mobile
  Status: Active | Occupancy: 30% | Monthly Revenue: $4,200
  Lease Term: 2021-2031 | Auto-Renew: Yes
  Payment Status: Current | Outstanding: $0"""

print("Running run_extraction as the UI would...")
try:
    result = run_extraction(
        text=text,
        use_llm=True,
        model="llama3:8b",
        confidence=0.7,
        hallucination_mode="strict",
        extraction_mode="Adaptive LLM (Any Document)"
    )
    print("\n--- RESULT ---")
    print(json.dumps(result, indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()

if os.path.exists("ecl_debug.log"):
    print("\n--- ECL DEBUG LOG ---")
    with open("ecl_debug.log") as f:
        print(f.read())
