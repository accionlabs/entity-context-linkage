# CoPilot Slide Generation Prompts
## ECL: The New ETL — Summit Presentation (Updated Feb 25, 2026)

Use these prompts in **Microsoft CoPilot for PowerPoint** to generate slides. After generation, use **Designer** suggestions to polish layouts, then replace placeholder images with assets from the `slides/` folder.

> **Adapted from Plus AI prompts.** Slides 12B–13B cover 9-way reconciliation engine demo. Slide 14 includes $47.3M impact. Slide 16 includes reconciliation ROI.

> [!TIP]
> **CoPilot workflow:** Paste each prompt into the CoPilot sidebar → review the generated slide → click **Designer** for layout options → swap in your assets. For multi-element slides, you may need to issue follow-up instructions like *"Add a table to this slide with..."* or *"Add a callout box that says..."*

---

## SLIDE 1: Title Slide
**CoPilot Prompt:**
```
Add a slide with the title "ECL: The New ETL" and subtitle "Entity-Context-Linking for Enterprise AI Agents". Include the speaker name [Your Name] - Field CTO, Accion Labs and the event name Accion Labs Innovation Summit 2026. Use a dark professional theme with blue and purple gradient accents.
```
**Follow-up:** *"Add a subtle graph network pattern to the background."*
**Image:** Replace background with `slide1_hero.png`

---

## SLIDE 2: The Agent Era is Here
**CoPilot Prompt:**
```
Add a slide titled "The Agent Era is Here" with a large header that says "65+ Enterprise AI Agents Live". Add three bullet points with industry examples: Insurance — FNOL to Claims Processing, Lending — Loan review to Risk scoring, Telecom — Contract plus Drone to Opportunities. At the bottom add a warning callout that says "But 70% hallucinate without proper context".
```
**Follow-up:** *"Make the warning callout stand out with a red or amber highlight."*

---

## SLIDE 3: ETL's Hidden Limitation
**CoPilot Prompt:**
```
Add a slide titled "ETL's Hidden Limitation" with subtitle "ETL = Facts for Humans. ECL = Context for Agents." Create a two-column layout. Left column with green checkmarks: Aggregates, BI Dashboards, Reports. Right column with red X marks: 80% Unstructured Data Ignored — Contracts, Drone Images, Logs. Add a bottom callout: "Agents need: Entities + Relationships + Lineage".
```
**Image:** Replace chart placeholder with `slide3_pie_chart.png`

---

## SLIDE 4: The Hallucination Problem
**CoPilot Prompt:**
```
Add a slide titled "RAG & Embeddings Fail at Enterprise Scale" with these bullet points: Semantic similarity does not equal Truth, No multi-hop reasoning such as Drone to Contract to Risk, No confidence scores or lineage, 40% of Enterprise AI Projects Fail according to Gartner. Add a bottom callout: "ECL = Structured, Grounded, Traceable Context".
```
**Image:** Replace diagram with `slide4_hallucination_chart.png`

---

## SLIDE 5: Introducing ECL Workflow
**CoPilot Prompt:**
```
Add a slide titled "ECL Workflow" showing a 3-step horizontal process with arrows. Step 1 EXTRACT: MoE Domain Experts covering Contracts, Equipment, Finance, and Opportunities. Step 2 CONTEXT: Entity-Relationship Graph with typed nodes, weighted edges, and confidence scores. Step 3 LINK: AI-Queryable Knowledge Graph with MCP tools, agent functions, and audit trail. Below the steps add the text "Every extraction is traced, validated, and confidence-scored".
```
**Follow-up:** *"Use a SmartArt process layout for the three steps."*
**Image:** Replace with `slide5_ecl_workflow.png`

---

## SLIDE 6: ETL vs ECL
**CoPilot Prompt:**
```
Add a slide titled "ETL vs ECL" with a comparison table. Left column header "ETL (Humans)" with rows: Facts/Metrics, Aggregates, 20% Structured, Dashboards, No audit trail, No confidence. Right column header "ECL (Agents)" with rows: Entities/Relationships, Multi-hop Reasoning, 80% Unstructured, MCP Tools + Agents, Full pipeline tracing, Confidence guardrails. Highlight the ECL column in an accent color.
```
**Image:** Replace with `slide6_etl_vs_ecl.png`

---

## SLIDE 7: The 2026 Data Engineer
**CoPilot Prompt:**
```
Add a slide titled "Data Engineer 2.0" showing an evolution from left to right. Left side: Pipeline Builder with ETL, SQL, Dashboards. Right side: Context Architect with ECL, Graph, MoE, MCP. Add a callout for new skills: "Graph DBs, Cypher, MoE Patterns, Agent Integration, Tracing". Include the stat "Job Growth: 25% faster than AI specialists".
```
**Follow-up:** *"Use a SmartArt arrow or chevron to show transformation from left to right."*
**Image:** Replace with `slide7_engineer_evolution.png`

---

## SLIDE 8: Why Now? Market Convergence
**CoPilot Prompt:**
```
Add a slide titled "Market Race to Context" with a 4-quadrant layout. Quadrant 1 Startups: TrustGraph, Glean, Lyzr AI. Quadrant 2 Hyperscalers: AWS and Azure Knowledge Graphs. Quadrant 3 ETL Vendors: Informatica and Fivetran pivoting. Quadrant 4 Open Source: Neo4j, FalkorDB, LangChain. Add callout: "$7T AI opportunity — Context is the missing layer". Add differentiator: "ECL = Only solution that's local, $0 LLM cost, with MoE extraction".
```
**Image:** Replace with `slide8_market_matrix.png`

---

## SLIDE 9: Enterprise AI Data Stack
**CoPilot Prompt:**
```
Add a slide titled "Enterprise AI Data Stack" with a 6-layer architecture diagram stacked bottom to top. Layer 1 DATA SOURCES: Databases, APIs, Documents, IoT/Sensors, Images. Layer 2 INGESTION: ETL + ECL Connectors for SharePoint, Dynamics 365, ServiceNow, FileSystem. Layer 3 EXTRACTION: MoE Experts with Confidence Guardrails and Entity Validation. Layer 4 KNOWLEDGE: FalkorDB Graph + Tracing + Governance. Layer 5 ORCHESTRATION: MCP Tools + Agent APIs + Audit Trail. Layer 6 CONSUMPTION: ECL Studio + AI Agents + Copilots + Dashboards. Add a vertical arrow labeled "Raw Data → Traceable Intelligence". Highlight layers 3 and 4 as the "ECL Zone".
```
**Follow-up:** *"Use different accent colors for each layer."*
**Image:** Replace with `slide9_6layer_architecture.png`

---

## SLIDE 10: ECL Technical Stack
**CoPilot Prompt:**
```
Add a slide titled "ECL Technical Stack" with a horizontal pipeline flow: Documents → MoE Extraction (5 experts) → Entity Validation → Confidence Filter → FalkorDB Graph → MCP Tools → AI Agent. Below the flow list these modules: ecl_tracing.py for Audit Trail, ecl_connectors.py for Enterprise Adapters, ecl_governance.py for Retention Policies, ecl_studio.html for Low-Code Builder. Add callout: "29/29 tests passing | Zero external dependencies".
```
**Image:** Replace with `slide10_tech_stack.png`

---

## SLIDE 11: ECL Studio — Low-Code Builder ⭐ NEW
**CoPilot Prompt:**
```
Add a slide titled "ECL Studio — No-Code Extraction" with a screenshot layout. Describe the app UI: left sidebar with expert toggles, confidence slider, and model selector. Center area with document input and a Load Sample button. Right panel with pipeline trace and graph preview. Key features: Toggle experts on/off with no code, Adjust confidence threshold with slider, Choose LLM model from dropdown, One-click extraction with live results. Add callout: "Non-technical users can extract in seconds".
```
**Notes:** Insert screenshot of ECL Studio from http://localhost:8765

---

## SLIDES 12–13: LIVE DEMO
**CoPilot Prompt:**
```
Add a slide titled "Live Demo: Contract Data Extraction" showing a before-and-after. Input: Tower Report with 6,233 characters. Processing: 4 MoE Experts + Confidence Guardrails + Entity Validation. Output: 23 Nodes, 22 Edges, Full Audit Trail. Results grid: 8 Opportunities Detected, 10 Risks Flagged, 0 Hallucinations (validated), 15 seconds total. Add callout: "Every entity traced, validated, confidence-scored".
```
**Image:** Replace with `slide11_demo_input.png`

---

## SLIDE 12B: 9-Way Cross-Reference Reconciliation ⭐ NEW
**CoPilot Prompt:**
```
Add a slide titled "9-Way Cross-Reference Reconciliation" with subtitle "SIMULATED DATA — DEMO MODE". Add header metrics: 2,810 discrepancies, $47.3M impact, 8 data sources. Create a table with 9 rows for use cases: UC1 Physical vs Contract finding Unbilled antennas and zombie tenants. UC2 Physical vs Invoice finding Sector underbilling. UC3 RF Design vs As-Built finding Tilt and azimuth drift. UC4 Structural Load finding Over-capacity and undersold towers. UC5 Escalation vs Invoice finding CPI errors and missed escalations. UC6 Mod Apps vs Physical vs Invoice finding Billing not updated. UC7 Rev-Share vs Tenant Revenue finding Formula errors. UC8 Site Access vs Mod Apps finding Unauthorized access. UC9 Tax Assessment vs Pass-Through finding Tax not passed through. Add a blue info badge: "Simulated data mirrors Summit portfolio at scale".
```

---

## SLIDE 13B: Reconciliation Dashboard ⭐ NEW
**CoPilot Prompt:**
```
Add a slide titled "Reconciliation Dashboard — Live Demo" with a dashboard-style layout. Show 5 headline metric cards: Discrepancies, Impact, Delta, Matched, Unbilled. Add a DISH exposure and deadline alert row. Add undersold towers metric showing $593K/mo opportunity. Show a category pie chart covering Escalation, Billing, Structural, and RF/SLA. Add a Top 10 discrepancy types bar chart. Include a filterable data table with UC, Severity, Category, and Type selectors. Key callouts: 141 undersold towers equals $7.1M/yr revenue opportunity, DISH has 49 defaulted contracts and $66.7M exposure, 266 auto-renewed contracts needing review.
```
**Notes:** Insert screenshot from http://localhost:8501 Invoice Recon tab

---

## SLIDE 14: Demo Results
**CoPilot Prompt:**
```
Add a slide titled "ECL Extraction + Reconciliation Results" with a stats grid of 8 items: 36 Graph Nodes (live extraction), 15 Relationships, 2,810 Discrepancies (9-way reconciliation), $47.3M Est. Annual Impact, 141 Undersold Towers, 49 DISH Defaulted Contracts, 6 MCP Tools Available, 0 Hallucinated Entities. Split into two sections labeled "Live" for extraction and "Simulated" for reconciliation with badges. Add quote: "Simulated data, real engine. Production-grade reconciliation."
```

---

## SLIDE 15: ECL vs Lyzr — Why We Win ⭐ NEW
**CoPilot Prompt:**
```
Add a slide titled "ECL vs Lyzr AI" with a two-column comparison table. Rows: Extraction — ECL has 5 MoE Experts vs Lyzr has Generic RAG. Knowledge — ECL has Typed Graph with FalkorDB vs Lyzr has Vector Embeddings. LLM Cost — ECL is $0 with Local Ollama vs Lyzr is $380K+ per year. Data Security — ECL is 100% On-Premise vs Lyzr is Cloud SaaS. Agent Tracing — both have it. Hallucination Controls — both have it. Low-Code Builder — ECL has ECL Studio vs Lyzr has Config UI. Vendor Lock-in — ECL has None as it is OSS vs Lyzr requires Annual Contract. Add score: "ECL wins 9 of 10 criteria". Add bottom banner: "Save $480K+ Year 1". Highlight the ECL column in green.
```

---

## SLIDE 16: Enterprise ROI
**CoPilot Prompt:**
```
Add a slide titled "Enterprise ROI" with a comparison table. Manual Process column: 20 min per document, 40,000 hours per year, $3M labor cost, 2-5% leakage, No cross-referencing. ECL Automation column: 3 seconds, 500 hours, $37K, Auto-detected, 9-way reconciliation. Add large callout: "$47.3M Annual Impact (at Summit scale)". Add sub-callout: "Plus $480K saved vs Lyzr".
```

---

## SLIDE 17: Vision Statement
**CoPilot Prompt:**
```
Add a slide with a centered quote: "ECL transforms documents into AI-queryable context graphs. It's not ETL — it's Entity-Context-Linking for the agentic era." Below the quote add 6 differentiators with checkmarks: Hybrid AI — Rules + LLM + Graph, Enterprise-Ready — Tracing Guardrails Governance, RAG-Ready — Grounded not hallucinated, Agent-Native — MCP tools built in, Low-Code — ECL Studio for non-technical users, $0 LLM Cost — Local Ollama with no cloud lock-in.
```

---

## SLIDE 18: Call to Action
**CoPilot Prompt:**
```
Add a closing slide titled "Build Your ECL Graph with Accion Labs" with three callouts: POC in 2 Weeks, ROI in 3 Months, $0 LLM Cost — No cloud spend. Add a contact information section and a QR code placeholder. Add "Questions?" at the bottom.
```

---

## CoPilot Tips & Best Practices

| Tip | Details |
|-----|---------|
| **Multi-step prompts** | CoPilot works best with focused instructions. If a slide is complex, generate the base layout first, then use follow-up prompts to add tables, callouts, or diagrams. |
| **Designer integration** | After CoPilot generates a slide, click **Designer** in the ribbon to get AI-powered layout suggestions. |
| **Image replacement** | Use **Insert → Pictures** to swap placeholder areas with assets from the `slides/` folder. |
| **Theme consistency** | Set your dark theme template *before* generating slides so CoPilot inherits the styling. |
| **Tables** | For comparison tables, prompt CoPilot to create the table first, then manually adjust column widths and formatting. |
| **SmartArt** | For process flows and architecture diagrams, ask CoPilot to use SmartArt — it produces better structured visuals. |

---

## Image Asset Mapping

| Slide | Asset File | Status |
|-------|------------|--------|
| 1 | `slide1_hero.png` | ✅ Existing |
| 3 | `slide3_pie_chart.png` | ✅ Existing |
| 4 | `slide4_hallucination_chart.png` | ✅ Existing |
| 5 | `slide5_ecl_workflow.png` | ✅ Existing |
| 6 | `slide6_etl_vs_ecl.png` | ✅ Existing |
| 7 | `slide7_engineer_evolution.png` | ✅ Existing |
| 8 | `slide8_market_matrix.png` | ✅ Existing |
| 9 | `slide9_6layer_architecture.png` | 🔄 Needs regen (new layers) |
| 10 | `slide10_tech_stack.png` | 🔄 Needs regen (new modules) |
| 11 | ECL Studio screenshot | 🆕 Screenshot from localhost:8765 |
| 12 | `slide11_demo_input.png` | ✅ Existing |
| 15 | ECL vs Lyzr | 🆕 Use ECL_ARCHITECTURE.html |
