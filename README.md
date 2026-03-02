# ECL — Entity-Context-Linking

> **Transform 80% of enterprise data that ETL ignores into AI-ready knowledge graphs — then reconcile it across 9 data sources to find revenue leakage.**

ECL is a Mixture-of-Experts (MoE) extraction pipeline that converts unstructured documents into typed entity graphs stored in FalkorDB — enabling AI agents to reason over enterprise knowledge with full traceability and zero cloud LLM cost.

## Architecture

```
Documents → 6 MoE Experts → Validation → Ollama LLM → FalkorDB → MCP Tools → AI Agents
                                                           ↕
8 Data Sources → 9-Way Reconciliation Engine → $47.3M Impact Dashboard
```

| Layer | Components |
|-------|-----------| 
| **Extraction** | ContractExpert, EquipmentExpert, FinancialRiskExpert, OpportunityExpert, HealthcareExpert, TelecomREITReconciliationExpert |
| **Validation** | Hallucination guard, confidence guardrails (≥0.70), entity grounding, pipeline tracing |
| **Knowledge** | FalkorDB graph — typed entities, weighted relationships, Cypher queries |
| **Reconciliation** | 9-way cross-reference engine — Physical↔Contract, Invoice↔Billing, RF↔As-Built, Structural, Escalation, Mod Apps, Rev-Share, Site Access, Tax |
| **Orchestration** | 6 MCP tools — `get_tower_context`, `find_opportunities`, `assess_risk`, `search_entities`, `get_trace` |
| **Consumption** | ECL Studio (Streamlit), reconciliation dashboard, CSV export |

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) running locally with `llama3:8b`
- [FalkorDB](https://www.falkordb.com) running on `localhost:6379`

### Run Extraction
```bash
python3 ecl_poc.py
```

### Launch ECL Studio
```bash
streamlit run ecl_app.py
# → Opens at http://localhost:8501
```

### Generate Reconciliation Data & Run Engine
```bash
python3 generate_erp_invoices.py        # → 12,074 ERP invoices
python3 generate_tower_audits.py        # → 235 tower audits
python3 generate_tower_ops_data.py      # → RF, structural, mods, access, tax
python3 reconcile_contracts.py          # → 2,810 discrepancies, $47.3M impact
```

### Run Tests
```bash
python3 -m pytest test_ecl.py -v        # 40/40 passing
```

## Project Structure

```
ECL/
├── ecl_poc.py                # Core extraction (6 MoE experts)
├── ecl_llm.py                # Ollama LLM integration
├── ecl_falkordb.py           # FalkorDB graph operations
├── ecl_tracing.py            # Agent tracing + audit trail
├── ecl_connectors.py         # Enterprise connectors (SharePoint, Dynamics 365, ServiceNow)
├── ecl_governance.py         # Data governance + retention policies
├── ecl_server.py             # ECL Studio backend
├── ecl_app.py                # ECL Studio (Streamlit) — extraction + reconciliation
│
├── reconcile_contracts.py    # 9-way cross-reference reconciliation engine
├── generate_erp_invoices.py  # ERP invoice generator (12,074 records)
├── generate_tower_audits.py  # Tower physical audit simulator (235 records)
├── generate_tower_ops_data.py # RF, structural, mods, access, tax (3,570 records)
├── generate_contracts.py     # Lease contract document generator (1,250 docs)
│
├── telecom_reit/             # Telecom REIT extraction pipeline (7 modules)
├── contracts/                # Generated lease documents
│   ├── ground_leases/        # 500 ground lease contracts
│   └── tenant_leases/        # 750 tenant lease contracts
├── slides/                   # Presentation assets
│   ├── SPEAKER_NOTES.md      # Speaker script (updated for 9-way recon)
│   ├── PLUSAI_PROMPTS.md     # Slide generation prompts
│   ├── ECL_SUMMIT_DECK_30.md # 30-slide deck
│   └── *.csv                 # Generated reconciliation data
│
├── DEMO_PLAYBOOK.md          # Demo script (6 acts)
├── HEART_BEAT.MD             # Activity log
├── ECL_ARCHITECTURE.html     # ECL vs Lyzr comparison
├── test_ecl.py               # Test suite (40 tests)
└── README.md                 # This file
```

## 9-Way Cross-Reference Reconciliation

The reconciliation engine cross-references 8 data sources across 9 patterns:

| UC | Cross-Reference | What It Catches | Findings |
|----|-----------------|-----------------|----------|
| UC1 | Physical ↔ Contract | Unbilled antennas, zombie tenants | 45 |
| UC2 | Physical ↔ Invoice | Sector underbilling, power pass-through | 22 |
| UC3 | RF Design ↔ As-Built | Tilt/azimuth drift, model mismatches | 107 |
| UC4 | Structural Load | Over-capacity, undersold towers | 230 |
| UC5 | Escalation ↔ Invoice | CPI errors, missed escalations | 2,123 |
| UC6 | Mod App ↔ Change ↔ Invoice | Billing not updated after mods | 38 |
| UC7 | Rev-Share ↔ Tenant Revenue | Formula errors, Zayo carveout | flagged |
| UC8 | Site Access ↔ Mod App | Unauthorized site access | 194 |
| UC9 | Tax ↔ Pass-Through | Tax not passed through to tenants | 51 |

**Total: 2,810 discrepancies · $47.3M estimated annual impact (simulated data)**

> ⚠️ All reconciliation data is synthetic, generated to mirror Summit's portfolio. Patterns and discrepancy rates model real-world industry benchmarks. The engine itself is production-grade.

## Key Differentiators

| Feature | ECL | Traditional RAG |
|---------|-----|-----------------| 
| Extraction | 6 domain-specialized MoE experts | Generic embeddings |
| Knowledge | Typed graph with weighted relationships | Flat vector store |
| Reconciliation | 9-way cross-reference, 8 data sources | None |
| Traceability | Full pipeline trace per entity | None |
| Hallucination | Source-text validation + confidence guardrails | None |
| LLM Cost | $0 (local Ollama) | $$$ (cloud APIs) |
| Data Residency | 100% on-premise | Cloud |

## License

Proprietary — Accion Labs. All rights reserved.
