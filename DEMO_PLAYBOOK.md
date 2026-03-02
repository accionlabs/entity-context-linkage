# 🎯 ECL Demo Playbook — Summit Presentation (Updated Feb 23, 2026)

> **Updated:** Now includes 9-way cross-reference reconciliation (2,810 discrepancies, $47.3M impact), simulated data framing, 1,250 generated contracts, ERP invoice matching, and expanded demo flow.

---

## Pre-Demo Setup

### Step 0: Start Docker Desktop
```bash
# Open Docker Desktop and wait for daemon to be ready
open -a Docker
echo "⏳ Waiting for Docker daemon..."
while ! docker info > /dev/null 2>&1; do sleep 2; done
echo "✅ Docker is running"
```

### Step 1: Start Services
```bash
# Terminal 1: FalkorDB — check if container exists, start or create
if docker ps --format '{{.Names}}' | grep -q falkordb; then
  echo "✅ FalkorDB already running"
elif docker ps -a --format '{{.Names}}' | grep -q falkordb; then
  docker start falkordb
  echo "✅ FalkorDB container restarted"
else
  docker run -d --name falkordb -p 6379:6379 falkordb/falkordb
  echo "✅ FalkorDB container created"
fi

# Terminal 2: Ollama (Local LLM Inference)
ollama serve
```

### Step 2: Generate Data (if not already present)
```bash
# Terminal 3:
cd /Users/yakarteek/Code/Accion/Summit/ECL
eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)" && pyenv activate ecl-demo
python generate_erp_invoices.py       # → 12,074 invoices
python generate_tower_audits.py       # → 235 tower audits
python generate_tower_ops_data.py     # → RF, structural, mods, access, tax
```

### Step 3: Launch ECL Studio
```bash
# Terminal 4: Streamlit
/Users/yakarteek/.pyenv/versions/ecl-demo/bin/streamlit run ecl_app.py
# → Opens at http://localhost:8501
```

### Pre-Flight Checks
```bash
# Verify everything works
/Users/yakarteek/.pyenv/versions/ecl-demo/bin/python test_ecl.py           # Should show: 40/40 passed
/Users/yakarteek/.pyenv/versions/ecl-demo/bin/python reconcile_contracts.py # Should show: 2,810 discrepancies, $47.3M impact
curl -s localhost:8501/healthz                                              # Should show: ok (Streamlit health)
```

### Pre-Load Data
1. Open Streamlit at `http://localhost:8501`
2. Click **📋 Load Sample** to stage the sample document
3. Run extraction to populate tabs
4. Click **💰 Invoice Recon** tab — verify "SIMULATED DATA — DEMO MODE" badge appears

---

## Act 1: The Problem (30 sec)

> *"Traditional ETL moves data. ECL extracts meaning and makes it AI-queryable — with every decision traced."*

**Show:** The document input area with the Tower Report loaded

**Key stats:**
- Summit: 40,000 towers, $3.9B revenue
- 2-5% revenue leakage from unbilled co-locations, missed escalations, billing errors
- At Summit scale: **1% recovery = $39M/year**

**Pitch:**
> *"An analyst needs 2 weeks and a site visit per tower. ECL cross-references 8 data sources across 9 reconciliation patterns — and finds $47 million in impact. In seconds."*

---

## Act 2: Live Entity Extraction (1 min)

**[Open Streamlit → http://localhost:8501]**

> *"First, let me show you what's real. ECL extracts entities from unstructured contracts using a local LLM — no cloud, $0 cost."*

### Demo Flow:
1. **Click '📋 Load Sample'** → Tower lease data loads
2. **Click '⚡ Extract Entities'** → Watch extraction run (6 MoE experts, ~15 sec)
3. **Show Entity Table** → Extracted entities with confidence scores
4. **Show Graph Preview** → Visual knowledge graph
5. **Show Pipeline Trace** → Full audit trail, every step traceable

> *"36 entities, 15 linkages, 8 HIGH severity findings — in 3 seconds of pipeline time. Everything traced and auditable."*

---

## Act 3: Tower Lease Reconciliation ⭐⭐ (3 min)

**[Switch to '💰 Invoice Recon' tab]**

> *"Now the reconciliation. Let me be transparent — the data you're about to see is simulated. We generated 1,250 realistic lease contracts from Summit portfolio data, 12,074 ERP invoices with planted discrepancies, tower audits, RF specs, structural analyses, mod applications, and tax assessments."*

**[Point to the blue "SIMULATED DATA — DEMO MODE" box]**

> *"We label it clearly. The patterns are real — modeled on actual Summit lease structures. The engine that finds discrepancies is very real. The data is synthetic."*

### Demo Flow:
1. **Expand '📊 Why This Matters'** → Show the impact-to-effort matrix
2. **Expand '🔗 9 Cross-Reference Patterns'** → Walk through the UC table
3. **Click '🔄 Run 9-Way Cross-Reference Reconciliation'** → Watch it run (~3 sec)

### Dashboard Walk-Through:
- **2,810 discrepancies** — "This is what the engine found across 9 patterns"
- **$47.3M estimated annual impact** — "At 1,000 contracts. Scale to 40K."
- **141 undersold towers** — "Not just savings — $7.1M/yr in uncaptured revenue"
- **DISH: 49 defaulted, $66.7M exposure** — "Timely given the $3.5B recovery"

### Highlight 3 Use Cases:
1. **UC1 (Physical ↔ Contract):** "Drone sees 6 antennas, contract says 4. 45 unbilled equipment findings."
2. **UC5 (Escalation ↔ Invoice):** "CPI escalation not applied since 2022. The error compounds every year. 2,123 findings."
3. **UC4 (Structural):** "141 towers have capacity for additional tenants but the asset database says they're full. That's a pipeline problem, not a tower problem."

> *"A portfolio manager sees this in 3 seconds. Not 2 weeks. And every finding is traced to the source."*

---

## Act 4: What's Real vs. Hypothetical ⭐ (1 min)

**This is the credibility beat — be transparent:**

| What's Real | What's Simulated |
|-------------|------------------|
| Entity extraction engine (runs live with local LLM) | Contract text content (1,250 generated) |
| MoE expert routing and confidence scoring | ERP invoice data (12,074 generated) |
| 9-way reconciliation logic | Tower audit findings |
| Graph persistence in FalkorDB | RF, structural, tax assessment data |
| ECL Studio UI | Dollar amounts and discrepancy rates |
| Pipeline tracing and audit trail | Carrier names and tower IDs |

> *"The engine is production-grade. The data mirrors real-world patterns. In a 4-week engagement, we'd connect to your actual ERP, lease management, and 5x5 digital twin APIs."*

---

## Act 5: ECL vs ISVs — Why We Win (1 min)

> *"Salesforce AgentForce, ServiceNow NowAssist, Microsoft Copilot — they all claim you don't need ECL."*

**Hit these three points:**

1. **Multi-hop**: "Their RAG can't cross-reference 9 data sources. Our graph does it instantly."
2. **Cross-system**: "They're CRM-centric. We integrate contracts + drone + Oracle billing + tax records + site access."
3. **Cost**: "Lyzr AI charges $380K/year. We run on local Ollama — **$0**."

> *"ECL is the missing context layer AgentForce builds on. We architect it."*

---

## Act 6: ROI & Call to Action (30 sec)

| Manual Process       | ECL Pipeline          |
|---------------------|-----------------------|
| 20 min / document   | 3 seconds             |
| 40,000 hours/year   | 500 hours             |
| $3M labor cost      | $37K                  |
| 2-5% revenue leakage | Automated detection  |
| + $380K ISV license | $0 (local LLM)        |

**Total Annual Impact: $47.3M+ (at scale)**

> *"POC in 2 weeks. Production data connection in 4 weeks. $47M+ annual impact at Summit scale. Let's build your context graph."*

---

## Key Terminology

| Term | Definition | ECL Application |
|------|------------|-----------------| 
| **MoE** | Mixture of Experts | 6 domain experts (Contract, Equipment, Financial, Risk, Opportunity, TelecomREIT) |
| **9-Way Recon** | Cross-referencing 9 data source pairs | Physical↔Contract, Invoice↔Billing, RF↔As-Built, etc. |
| **MCP** | Model Context Protocol | 6+ tools: get_tower_context, find_opportunities, assess_risk |
| **ECL** | Entity-Context-Linking | Extract entities → Build context → Link in graph → Reconcile |
| **Three-Way Reconciliation** | Contract × Drone × Billing comparison | Physical + financial + RF status per tower |
| **Hallucination Guard** | Validating LLM outputs against source | Entity names checked against source text |
| **Knowledge Graph** | Network of typed entities and relationships | FalkorDB with confidence-scored nodes/edges |

---

## Emergency Fallbacks

| If...                    | Then...                                           |
|--------------------------|---------------------------------------------------|
| Ollama down              | Use regex experts — entity extraction still works  |
| FalkorDB down            | Reconciliation dashboard doesn't need graph        |
| Streamlit won't start    | Run `python3 reconcile_contracts.py` in terminal   |
| Invoice data missing     | Run generators: `python3 generate_erp_invoices.py && python3 generate_tower_audits.py && python3 generate_tower_ops_data.py` |
| All fails                | Open `ECL_ARCHITECTURE.html` + pre-captured screenshots |

---

## Assets

| Asset | Purpose |
|-------|---------|
| `ecl_app.py` | Streamlit UI with reconciliation dashboard |
| `reconcile_contracts.py` | 9-way reconciliation engine (also runs CLI) |
| `generate_erp_invoices.py` | ERP invoice generator (12,074 records) |
| `generate_tower_audits.py` | Tower physical audit generator (235 records) |
| `generate_tower_ops_data.py` | RF + structural + mods + access + tax (3,570 records) |
| `telecom_reit/` | Full ECL pipeline package (7 modules) |
| `ecl_server.py` | REST API backend |
| `ECL_ARCHITECTURE.html` | Competitive comparison page |
| `slides/ECL_SUMMIT_DECK_30.md` | Full 30-slide deck with talk track |
| `slides/SPEAKER_NOTES.md` | Condensed speaker notes |
| `slides/PLUSAI_PROMPTS.md` | Slide generation prompts |
| `DEMO_PLAYBOOK.md` | This playbook |
| `test_ecl.py` | Test suite (40/40 passing) |
