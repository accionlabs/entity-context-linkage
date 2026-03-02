# Entity-Context-Linkage (ECL) Framework
> **Enterprise-Grade Knowledge Extraction & 9-Way Transaction Reconciliation**

ECL is a sophisticated Mixture-of-Experts (MoE) extraction pipeline designed to transform massive volumes of unstructured enterprise data into high-fidelity, actionable knowledge graphs. By integrating multi-modal semantic extraction with a rigorous 9-way reconciliation engine, ECL identifies financial leakage, operational risks, and hidden revenue opportunities at scale.

---

## 🚀 Vision
ECL addresses the "dark data" problem—the 80% of enterprise information trapped in PDFs and documents that traditional ETL processes ignore. It provides AI agents with a structured, traceable, and private memory layer (FalkorDB), enabling complex reasoning with $0 cloud LLM overhead.

## 🏗 System Architecture

The ECL framework orchestrates a seamless flow from raw data to business intelligence:

```mermaid
graph TD
    raw[Unstructured Documents] --> moe[MoE Expert Pipeline]
    moe --> vald[Validation & Hallucination Guard]
    vald --> llm[Ollama / Local LLM Inference]
    llm --> graph[(FalkorDB Knowledge Graph)]
    
    data[8 Heterogeneous Data Sources] --> recon[9-Way Reconciliation Engine]
    recon --> dash[Impact Dashboard - $47.3M ROI]
    
    graph --> mcp[MCP Tool Orchestration]
    mcp --> agents[AI Reasoning Agents]
```

### Infrastructure Layers
| Layer | Core Components & Responsibilities |
|-------|------------------------------------|
| **Semantic Extraction** | Specialized experts: `ContractExpert`, `EquipmentExpert`, `FinancialRiskExpert`, `OpportunityExpert`, `HealthcareExpert`. |
| **Integrity Layer** | Source-text validation, entity grounding, and confidence guardrails (Threshold ≥ 0.70). |
| **Knowledge Core** | [FalkorDB](https://falkordb.com/) backed graph store; providing high-performance Cypher queries on typed entities. |
| **Reconciliation** | Cross-referencing engine resolving discrepancies across Physical, Contractual, and Financial records. |
| **Orchestration** | Model Context Protocol (MCP) toolset: `get_tower_context`, `find_opportunities`, `assess_risk`. |
| **Interface** | ECL Studio (Streamlit) for real-time extraction monitoring and reconciliation insights. |

---

## 🔍 9-Way Reconciliation Engine
The crown jewel of the ECL framework is its capability to reconcile 8 disparate data sources across 9 critical business dimensions.

| Domain | Reconciliation Pattern | Objective | Detected Impact |
|:-------|:-----------------------|:----------|:----------------|
| **Asset** | Physical ↔ Contract | Identify unbilled equipment and "zombie" lease components. | High |
| **Revenue** | Physical ↔ Invoice | Audit sector underbilling and power pass-through expenses. | Critical |
| **Engineering** | RF Design ↔ As-Built | Detect tilt/azimuth drift and equipment model mismatches. | Technical |
| **Safety** | Structural Load | Compare actual weight/wind-load against registered capacity. | Compliance |
| **Finance** | Escalation ↔ Invoice | Audit CPI index application and missed annual escalations. | Major |
| **Operations** | Mod App ↔ Change ↔ Invoice | Ensure billing triggers immediately upon hardware modifications. | High |
| **Compliance** | Rev-Share ↔ Revenue | Validate gross revenue share formulas and tenant carveouts. | Legal |
| **Security** | Site Access ↔ Mod App | Correlate physical site visits with authorized work orders. | Security |
| **Tax** | Property Tax Pass-Through | Ensure jurisdiction-specific taxes are recovered from tenants. | Recovery |

**Quantified Performance:**  
*Based on simulated portfolio optimization:* **2,810 Discrepancies Handled** | **$47.3M Estimated Annual Savings**

---

## 🛠 Project Structure

```text
.
├── core/                     # Core Extraction Engine
│   ├── ecl_poc.py            # MoE Expert Orchestrator
│   ├── ecl_llm.py            # Local LLM (Ollama) Integration
│   ├── ecl_falkordb.py       # Graph Persistence Layer
│   └── ecl_tracing.py        # Audit Trail & Pipeline Tracing
├── reconciliation/           # Reconciliation & Simulation Suite
│   ├── reconcile_contracts.py # 9-Way Cross-Reference Engine
│   ├── generate_contracts.py  # synthetic Lease Generator (1,250 docs)
│   └── generate_erp_invoices.py # Financial Data Generator
├── platform/                 # User Interface & API
│   ├── ecl_app.py            # ECL Studio (Streamlit Dashboard)
│   ├── ecl_server.py         # Application Backend
│   └── ecl_connectors.py     # SharePoint & Dynamics 365 Integration
├── telecom_reit/             # Domain-Specific REIT Pipeline
├── assets/                   # Presentation & Documentation
└── tests/                    # Robustness Verification (44/44 Passing)
```

---

## 🚦 Getting Started

### 1. Environment Preparation
Ensure you have Python 3.10+ and the following services active:
- **Ollama**: Running locally with `llama3:8b`
- **FalkorDB**: Active on `localhost:6379`

### 2. Installation & Execution
```bash
# Install dependencies
pip install -r requirements.txt

# Execute base extraction pipeline
python ecl_poc.py

# Launch the visual intelligence suite
streamlit run ecl_app.py
```

### 3. Data Simulation & Reconciliation
```bash
# Generate synthetic datasets
python generate_erp_invoices.py
python generate_tower_ops_data.py

# Run the reconciliation engine
python reconcile_contracts.py
```

---

## 🛡 Security & Differentiators
- **100% Data Residency**: No data leaves your infrastructure; all inference is local.
- **Explainable AI**: Every graph node includes a source-text "trace" for manual auditing.
- **Deterministic Validation**: Hallucination guards ensure that extracted entities exist in the source document.
- **Horizontal Scalability**: Distributed MoE experts allow for parallel document processing.

---

## 📜 License
© 2026 **Accion Labs**. Proprietary and Confidential. All rights reserved.
Unauthorised distribution or duplication is strictly prohibited.
