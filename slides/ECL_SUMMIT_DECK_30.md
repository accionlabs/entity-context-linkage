# 🎤 ECL: The New ETL — 30-Slide Presentation Deck
## Accion Labs 12th Annual Innovation Summit 2026
### Field CTO Presentation | Feb 26-28, Grand Hyatt Goa

> **Deck Theme**: Dark navy background, electric blue (#00D4FF) + neon green (#39FF14) accents.
> Bold sans-serif (Inter/Outfit). 60% visual, 40% text. ~40 min total.

---

# ACT 1 — THE PROBLEM (Slides 1–8, ~8 min)

---

## SLIDE 1: Title Slide
**Time: 0:30 | Running: 0:30**

### Slide Content
```
ECL: The New ETL
Entity-Context-Linking for Enterprise AI Agents

[Your Name] — Field CTO, Accion Labs
Accion Labs Innovation Summit 2026

"From AI Promise to Measurable Impact"
```

### Visual Guidance
Hero image: Tower silhouette with glowing graph nodes overlaid (tower → contract → risk → opportunity). Accion Labs logo bottom-right. Faint grid/circuit-board background.

### Speaker Notes
> "Good morning everyone. I'm [Name], Field CTO at Accion Labs.
>
> Today I want to show you something that changes how we think about data engineering in the AI era.
>
> We call it **ECL — Entity-Context-Linking**. Think of it as 'The New ETL.'
>
> By the end of this session, you'll see a live demo — documents becoming AI-queryable knowledge graphs in seconds, with 3 real tower sites reconciled across contracts, drone inspections, and billing — and every decision traced and auditable."

**[Advance slide]**

---

## SLIDE 2: The Agent Era Is Here
**Time: 0:45 | Running: 1:15**

### Slide Content
```
65+ Enterprise AI Agents in Production

Insurance   → FNOL Claims Processing
Lending     → Loan Review & Risk Scoring
Telecom     → Contract + Drone → Revenue Recovery
Banking     → KYC Compliance
Government  → Permitting & Regulation Linking

But 70% hallucinate without proper context.
```

### Visual Guidance
Grid of industry icons (insurance shield, bank column, tower, government building). Red alert badge: "70% hallucination rate".

### Speaker Notes
> "The agent era isn't coming — it's here.
>
> We have 65+ enterprise AI agents live in production. Insurance claims, loan reviews, telecom operations, KYC compliance.
>
> But here's the uncomfortable truth: **70% of these agents hallucinate** when they don't have the right context.
>
> Why? Because we're still feeding them data the old way — flat tables, vector embeddings, and hope.
>
> In telecom alone, we'll show you how one agent can reconcile contracts against drone inspections across 3 tower sites and find $23,400 in annual revenue at risk — all in under 3 seconds."

---

## SLIDE 3: ETL's Hidden Limitation
**Time: 1:00 | Running: 2:15**

### Slide Content
```
ETL = Facts for Humans
✅ Aggregates, BI, Dashboards
✅ Clean structured pipelines
❌ 80% Unstructured Data Ignored
   Contracts • Drone Images • Emails • Logs

Agents don't need averages.
They need: Entities + Relationships + Context
```

### Visual Guidance
Pie chart: 80% unstructured (red/dark) vs 20% structured (green/bright). Icons for contracts, drone images, emails floating in the 80% zone.

### Speaker Notes
> "ETL has served us well for 30 years. It creates clean, structured data for dashboards.
>
> But **80% of enterprise data is unstructured.** Contracts, drone inspection reports, email threads, meeting notes. ETL ignores all of this.
>
> An AI agent doesn't just need aggregated metrics. It needs to understand that 'Verizon has an active lease on Tower TR-8803 paying $2,800/month, but DISH is in default with $5,850 outstanding and their equipment is corroding on the tower.'
>
> That's **entity-relationship context** — and that's what ECL extracts."

---

## SLIDE 4: The IDP Illusion — "Can't We Just Extract?"
**Time: 1:15 | Running: 3:30**

### Slide Content
```
"We Have OCR, IDP, and LLMs... Why Do We Need ECL?"

Extraction ≠ Understanding

[Step 1]        [Step 2]        [Step 3]        [GAP ⚠️]       [Step 4]
OCR/IDP    →   LLM Extract  →  Vector/RAG  →   ???        →   ECL Graph
"Characters"   "Fields"        "Similarity"    "No Links"     "Entities +
                                                               Relationships"

95% of Enterprise AI Pilots Fail to Deliver ROI
```

### Visual Guidance
Ascending staircase with gap/cliff before ECL. Each step labeled. Red warning on the gap.

### Speaker Notes
> "Someone's going to ask — and fairly: 'We already have OCR, IDP tools, even LLMs that extract from PDFs. Why do we need ECL?'
>
> Let me walk through four levels of extraction maturity:
>
> **Level 1: OCR/IDP** — Reads characters, extracts pre-defined fields. Works on invoices. But OCR drops to 60% accuracy on real scans. It reads 'DISH Wireless' and '$1,950' but has zero idea that DISH is a defaulted tenant who owes back-rent and their equipment is still corroding on the tower.
>
> **Level 2: LLM Extraction** — Much better. GPT-4 can pull structured fields from a contract. But it hallucinates — confident, fluent answers not grounded in the document. You can't build compliance decisions on that.
>
> **Level 3: Vector/RAG** — Embed everything, retrieve similar chunks. Powerful for search. But it loses structure and can't do multi-hop: 'This drone image shows corroded equipment → it belongs to DISH → DISH is in default → there's $5,850 outstanding → this is a removal opportunity.' Vectors don't traverse.
>
> **Level 4: ECL** — This is the leap. You're not just extracting data points. You're building an explicit graph that an agent traverses to say: 'Here's your removal + upsell opportunity, with evidence.'
>
> That's the gap. Extraction gives you puzzle pieces. ECL assembles the picture."

---

## SLIDE 5: The Hallucination Problem
**Time: 0:45 | Running: 4:15**

### Slide Content
```
RAG/Embeddings Fail at Scale

Semantic similarity ≠ Truth
No multi-hop reasoning:
  Drone Image → Corroded Dish
    → DISH Contract #08803-B
      → 90 Days Overdue → $5,850
        → Removal Opportunity

Context performance drops 50% at 32K tokens
40% of Enterprise AI Projects Fail
```

### Visual Guidance
Left: scattered vector dots (chaos). Right: clean graph traversal (tower → contract → default → opportunity). Arrow showing the "multi-hop" path.

### Speaker Notes
> "This is why RAG and embeddings aren't enough.
>
> Semantic similarity is NOT truth. Just because two sentences have similar embeddings doesn't mean one can answer a question about the other.
>
> More critically — embeddings can't do **multi-hop reasoning**. They can't connect: 'This drone image shows a corroded microwave dish' → 'it belongs to DISH Wireless contract #08803-B' → 'DISH is 90 days overdue with $5,850 outstanding' → 'this is a removal + re-leasing opportunity.'
>
> That chain requires a **graph**. And it requires **confidence scores and validation** so you know which facts are real and which are hallucinated. That's what ECL builds."

---

## SLIDE 6: Introducing ECL
**Time: 1:00 | Running: 5:15**

### Slide Content
```
ECL: Entity → Context → Link

  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ EXTRACT  │───▶│ CONTEXT  │───▶│  LINK    │
  │          │    │          │    │          │
  │ Entities │    │ 360° View│    │ Graph DB │
  │ from PDF,│    │ per tower│    │ Traversal│
  │ Drone,   │    │ site     │    │ by AI    │
  │ ERP      │    │          │    │ Agents   │
  └──────────┘    └──────────┘    └──────────┘
       ▲               ▲               ▲
   MoE Experts    Context Assembly   FalkorDB
   Confidence     Health Indicators  MCP Tools
   Guardrails     Reconciliation     Audit Trail
```

### Visual Guidance
Three connected hexagons or circles flowing left to right. Icons for each stage. Neon green flow arrows.

### Speaker Notes
> "So what is ECL? Three steps:
>
> **Step 1: EXTRACT** — We use 6 specialized MoE experts. Each one knows its domain: contracts, equipment, financials, risks, opportunities, and now tower reconciliation. Every entity gets a confidence score and is validated against the source text.
>
> **Step 2: CONTEXT** — We assemble a 360° view per tower site. Contracts + drone detections + billing records + work orders + inspections. We compute physical reconciliation status, financial reconciliation status, and health indicators.
>
> **Step 3: LINK** — We persist everything in a graph database with full audit trail. AI agents can traverse the graph via MCP tools — and every answer is traceable back to the source document, the expert who extracted it, and the confidence score.
>
> This is what Sanjeev Mohan defined in 2025 as the next evolution of data engineering. We've built it."

---

## SLIDE 7: ETL vs ECL — The Comparison
**Time: 0:45 | Running: 6:00**

### Slide Content
```
| Dimension        | ETL (Humans)           | ECL (Agents)                |
|------------------|------------------------|-----------------------------|
| Data Type        | 20% Structured         | 80% Unstructured + Struct   |
| Output           | Facts, Metrics         | Entities, Relationships     |
| Reasoning        | Aggregates             | Multi-hop Graph Traversal   |
| Consumer         | Dashboards, BI         | AI Agents, MCP Tools        |
| Context          | None                   | 360° Entity Context         |
| Auditability     | Log files              | Traced to Source + Expert   |

ETL + ECL = Complete Enterprise AI Stack
```

### Visual Guidance
Side-by-side comparison. Warehouse icon (left) vs graph icon (right). "+" sign bridging them at bottom.

### Speaker Notes
> "Here's the key difference:
>
> ETL moves **facts for humans**. ECL extracts **context for agents**.
>
> ETL gives you: 'Total revenue is $8,750 per month.'
>
> ECL tells you: 'Tower TR-8803 has 2 tenants. Verizon is paying $2,800/month and is current. DISH was paying $1,950/month but is 90 days overdue with $5,850 in arrears. Their equipment is corroding. Removal cost estimate: $18,500. Available capacity after removal: 30%. Charlotte market demand is HIGH — replacement tenant could bring $2,200-$3,500/month.'
>
> One is a number. The other is **traceable, confidence-scored intelligence**.
>
> And critically — they're **complementary, not competitive**. You need both."

---

## SLIDE 8: Why Now? — Market Convergence
**Time: 0:45 | Running: 6:45**

### Slide Content
```
Why ECL Is Happening Now

LLMs        ──────── Entity extraction at scale
Graph DBs   ──────── FalkorDB, Neo4j, Neptune
MCP         ──────── Standard agent tool protocol
$602B       ──────── Hyperscaler AI CapEx in 2026

Knowledge Graph Market:
$1.5B (2024) → $25.7B (2032) | 37% CAGR

$1 Trillion Context Graph Opportunity
    — Foundation Capital, 2026
```

### Visual Guidance
Four converging arrows pointing to center "ECL" node. Market size growth bar chart at bottom.

### Speaker Notes
> "We're not alone in seeing this. Four forces have converged:
>
> LLMs can now extract entities from unstructured documents at scale. Graph databases like FalkorDB and Neo4j make relationship traversal fast. MCP gives agents a standard protocol to query context. And hyperscalers are spending $602 *billion* on AI infrastructure in 2026.
>
> Foundation Capital calls context graphs a **trillion-dollar opportunity**. The knowledge graph market is growing at 37% CAGR.
>
> Companies like Lyzr AI just signed a $380K contract for 'contract data extraction.' The exact use case we'll demo today — for $0 in LLM cost."

---

# ACT 2 — THE SOLUTION (Slides 9–18, ~14 min)

---

## SLIDE 9: Three-Layer Architecture
**Time: 0:45 | Running: 7:30**

### Slide Content
```
Enterprise AI Data Stack

┌─────────────────────────────────────────┐
│  DECISIONS    Agent APIs • MCP Tools    │ ← AI Agents
├─────────────────────────────────────────┤
│  CONTEXT      ECL Graph • FalkorDB     │ ← Entities + Relationships
├─────────────────────────────────────────┤
│  FACTS        ETL Warehouse • BI       │ ← Structured Metrics
└─────────────────────────────────────────┘
```

### Visual Guidance
Stacked horizontal layers. Bottom = dark blue (warehouse). Middle = electric blue (graph). Top = neon green (agents). Each layer gets progressively brighter.

### Speaker Notes
> "Here's the full picture — three layers:
>
> **Layer 1: Facts** — Your existing ETL/warehouse. Structured metrics. Not going away.
>
> **Layer 2: Context** — ECL's entity graph in FalkorDB. Entities extracted from contracts, drone reports, billing. Linked with confidence scores, health indicators, reconciliation status.
>
> **Layer 3: Decisions** — Agent APIs and MCP tools that traverse the graph. Every query returns traceable, explainable answers.
>
> ETL provides facts; ECL provides context; agents make decisions."

---

## SLIDE 10: Where ECL Wins — 6 Cross-Industry Patterns
**Time: 1:15 | Running: 8:15**

### Slide Content
```
ECL Solves Problems Other Approaches Can't

Industry                    ECL Use Case                          The Multi-Hop Chain
─────────────────────────   ────────────────────────────────────  ─────────────────────────────────────
🏥 Pharma Distribution      Contract ↔ Chargeback ↔ 340B Recon   Contract PDF → pricing tier → chargeback
                                                                  → 340B registration EXPIRED → $2.3M invalid

🧒 Childcare / Education    License ↔ Credential ↔ Enrollment    Licensing PDF → staff credential → CPR cert
                                                                  EXPIRED 45 days → state code §402.3 violation

🧬 Clinical Diagnostics     Protocol ↔ Specimen ↔ Regulatory     Protocol PDF v2.1 → Amendment 3 changed
                                                                  window to 48h → specimen processed at 61h → flag

📡 Media Intelligence       Brief ↔ Pitch ↔ Coverage Attribution  Campaign brief → 45 journalists pitched →
                                                                  12 covered → only 3 hit key message → 25%

🏭 Medical Devices          510(k) ↔ Predicate ↔ Complaint Link  Device X-200 complaints → shares predicate
                                                                  with Z-300 → 0 complaints but same risk → CAPA

🏦 Global Banking           KYC Questionnaire ↔ Sanctions ↔ UBO  KYC PDF → "Ahmed Al-Rashid" → sanctions alias
                                                                  "A. Rashid" → Cyprus holding co → 0.87 match

Common Thread: Unstructured Docs + Entity Extraction + Multi-Hop + Audit Trail
```

### Visual Guidance
6-row matrix layout. Left column: industry icon + label. Center: the ECL use case as a flow. Right: the multi-hop chain rendered as a mini graph path with colored nodes. Each row is color-coded by industry. Bottom bar highlights the common thread in accent color.

### Speaker Notes
> "Let me show you where ECL wins — across 6 very different industries.
>
> **Pharma distribution** — Thousands of contracts with negotiated pricing tiers, rebate thresholds, and 340B compliance terms. All buried in PDFs. A chargeback dispute arrives, and an agent traverses: contract → pricing tier → 340B registration → *expired 6 months ago* → $2.3 million in invalid chargebacks. That's a graph traversal problem, not a dashboard problem.
>
> **Childcare and education** — 1,500 centers, 50 different state regulatory formats. Licensing PDFs, health inspections, staff credentials. An agent finds: staff member's infant CPR certification expired 45 days ago, but they're assigned to the infant room. State code violation. No human caught it because the data lives in 3 different document types.
>
> **Clinical diagnostics** — Protocol amendments arrive as PDFs. Specimen handling windows change from 72 hours to 48 hours in Amendment 3. A specimen gets processed at 61 hours — compliant under the old version, non-compliant under the new one. The agent traces the amendment chain and flags it before the FDA submission.
>
> **Media intelligence** — Campaign briefs, pitch emails, published coverage. An agent links the original brief's key messages to actual journalist coverage. 45 pitched, 12 covered, only 3 included the sustainability message. 25% pull-through. That attribution chain lives across unstructured documents.
>
> **Medical devices** — 510(k) submissions cite predicate devices. Device X-200 has 14 complaints about connector failure. It shares a predicate with Z-300, which has zero complaints but the *exact same connector design*. The agent traverses the predicate chain and recommends proactive CAPA. That's preventive regulatory intelligence.
>
> **Global banking** — KYC questionnaires, sanctions lists, corporate registry filings. An agent resolves: 'Ahmed Al-Rashid' in the KYC PDF → 'A. Rashid' on the sanctions list → 'Al-Rashid Holdings' in the Cyprus registry → 0.87 confidence match → escalate with full evidence chain.
>
> **The common thread**: every one of these starts with **unstructured documents**, requires **entity extraction**, depends on **multi-hop relationship traversal**, and demands an **audit trail**. That's ECL's sweet spot."

---

## SLIDE 11: Healthcare Example — Extract
**Time: 0:45 | Running: 9:00**

### Slide Content
```
ECL Example 1: Healthcare Patient Journey

Clinical Note Input:
  "Patient John Smith, diabetic, prescribed Metformin 500mg
   by Dr. Jane Doe on 2026-01-15. ICD-10: E11.9"

ECL Extraction → 5 Typed Entities:
  👤 Patient: John Smith
  💊 Medication: Metformin 500mg
  🏥 Diagnosis: E11.9 (Type 2 Diabetes)
  👨‍⚕️ Doctor: Dr. Jane Doe
  📅 Date: 2026-01-15
```

### Visual Guidance
Left: clinical note text. Right: extracted entity cards with icons and types.

### Speaker Notes
> "Let's see ECL in action with two industries. First, healthcare.
>
> A clinical note — unstructured text. ECL extracts 5 typed entities: patient, medication with dosage, ICD-10 diagnosis code, prescribing physician, date.
>
> This isn't just text extraction — each entity gets a type, confidence score, and source reference."

---

## SLIDE 12: Healthcare Example — Build & Link
**Time: 0:45 | Running: 9:45**

### Slide Content
```
ECL Healthcare Graph:

  [John Smith] ──TAKES──▶ [Metformin 500mg]
       │                        │
       │──HAS_DIAGNOSIS──▶ [E11.9 Diabetes]
       │
       └──PRESCRIBED_BY──▶ [Dr. Jane Doe]

Agent Query: "What medications is this diabetic patient on?"
Answer: Metformin 500mg (confidence: 0.94, source: clinical note)
```

### Visual Guidance
Graph visualization with colored nodes (patient=blue, medication=green, diagnosis=red, doctor=purple). Cypher query output below.

### Speaker Notes
> "Now ECL builds the graph. Patient John Smith TAKES Metformin, HAS_DIAGNOSIS Diabetes, PRESCRIBED_BY Dr. Jane Doe.
>
> An AI agent can now traverse this: 'What medications is this diabetic patient on?' The answer comes with confidence score and source reference — not hallucinated.
>
> This is a simple example. Now let me show you the industrial-strength version."

---

## SLIDE 13: Tower Lease Reconciliation — The Opportunity ⭐
**Time: 1:00 | Running: 10:45**

### Slide Content
```
Tower Lease Reconciliation — Agentic AI Demo
⚠️ SIMULATED DATA — DEMO MODE

Summit Portfolio:
  ~40,000 towers · $3.9B revenue · 4 major carriers
  DISH $220M churn hole · Zayo fiber divestiture

Industry Benchmark: 2-5% Revenue Leakage
  At Summit scale: 1% = $39M annually

This demo mirrors real patterns using synthetic data.
The engine is production-grade. The data is simulated.
```

### Visual Guidance
Executive briefing layout. Summit tower silhouettes. Dollar impact highlighted in large accent font. Blue "SIMULATED" badge.

### Speaker Notes
> "Let me now show you the reconciliation engine. I want to be transparent upfront — the data is simulated.
>
> We generated 1,250 realistic lease contracts modeled on publicly available Summit lease terms, 12,074 ERP invoices with planted discrepancies, tower physical audits, RF design specs, structural capacity analyses, modification applications, site access logs, and tax assessments.
>
> The patterns are real. The discrepancy rates match industry benchmarks. Summit manages 40,000 towers generating $3.9 billion in revenue. Industry data shows 2-5% leakage from unbilled co-locations, missed escalations, and billing errors.
>
> At their scale, even **1% recovery = $39 million annually**."

---

## SLIDE 14: 9-Way Cross-Reference Patterns ⭐
**Time: 1:00 | Running: 11:45**

### Slide Content
```
9 Cross-Reference Reconciliation Patterns

UC  Cross-Reference                    Data Sources                What It Catches
──  ───────────────────────────────    ─────────────────────────   ────────────────────────
1   Physical ↔ Tenant Contract         Digital twin ↔ Lease mgmt  Unbilled antennas, zombies
2   Physical ↔ Invoice Lines           Digital twin ↔ Billing     Sector underbilling
3   RF Design ↔ Physical As-Built      Engineering ↔ Twin         Tilt/azimuth drift
4   Structural Load ↔ Actual           Bentley iQ ↔ Twin          Over-capacity, undersold
5   Escalation ↔ Invoice History       Lease mgmt ↔ Billing       CPI errors, missed escal.
6   Mod App ↔ Physical ↔ Invoice       Workflow ↔ Twin ↔ Billing  Billing not updated
7   Rev-Share ↔ Tenant Revenue         Ground lease ↔ Billing     Formula errors
8   Site Access ↔ Mod Applications     Field ops ↔ Workflow       Unauthorized access
9   Tax Assessment ↔ Pass-Through      County records ↔ Billing   Tax not passed through

8 data sources · 9 patterns · 2,810 discrepancies · $47.3M impact
```

### Visual Guidance
9-row table with data source arrows. Each UC has an icon. Bottom bar shows aggregate metrics in accent color.

### Speaker Notes
> "We run 9 distinct cross-reference patterns, each connecting different data sources.
>
> **UC1** — the drone sees 6 antennas but the contract covers only 4. That's unbilled equipment.
>
> **UC3** — the RF design says antenna tilt should be 4 degrees, but it's physically mounted at 7. That's SLA risk.
>
> **UC4** — 141 towers have structural capacity for more tenants, but the asset database thinks they're full. That's $7.1 million per year in revenue sitting on the table.
>
> **UC5** — this is the biggest dollar finding. CPI escalation not applied since 2022who. The error compounds every year. 2,123 billing discrepancies.
>
> **UC8** — someone accessed the tower. No work order, no mod application on file. 194 suspicious entries."

---

## SLIDE 15: Reconciliation Dashboard — Live Demo ⭐⭐
**Time: 1:30 | Running: 13:15**

### Slide Content
```
[LIVE DEMO — ECL Studio → 💰 Invoice Recon tab]

Results (simulated data):
  2,810 Discrepancies Found
  $47.3M Estimated Annual Impact
  1,791 🔴 Critical · 864 🟡 Warning · 155 🟢 Info

  DISH: 49 defaulted contracts · $66.7M total exposure
  141 undersold towers · $593K/mo revenue opportunity
  266 auto-renewed contracts needing review
  22 expiring within notice window

Filters: Use Case · Severity · Category · Type
Export: Full CSV report downloadable
```

### Visual Guidance
Screenshot of ECL Studio Invoice Recon tab showing metrics, charts, and data table. "SIMULATED" badge at top.

### Speaker Notes
> "Watch this. I click one button. 8 data sources, 9 cross-reference patterns, 2,810 discrepancies found in about 3 seconds.
>
> $47.3 million in estimated annual impact — at a simulated scale of about 1,000 contracts. Summit has 40,000 towers. Scale the math.
>
> 141 undersold towers — that's not savings, that's $7.1 million per year in revenue they're not capturing because the asset database says those towers are full. They're not.
>
> DISH: 49 defaulted contracts, $66.7 million in total exposure. Timely, given the $3.5 billion recovery effort.
>
> And every finding is filterable — by use case, severity, category, type. You can drill into UC5 escalation errors and see exactly which contracts have CPI clauses that weren't applied."

---

## SLIDE 16: What's Real vs. Hypothetical ⭐
**Time: 0:45 | Running: 14:00**

### Slide Content
```
What's Real vs. What's Simulated

✅ REAL (runs live)                    ⚠️ SIMULATED (mirrors production)
──────────────────────                ──────────────────────────────────
Entity extraction engine               Contract text content (1,250 docs)
MoE expert routing                     ERP invoice data (12,074 records)
Confidence scoring                     Tower audit findings (235)
Pipeline tracing + audit trail         RF, structural, tax data
FalkorDB graph persistence             Dollar amounts, discrepancy rates
9-way reconciliation logic             Carrier names, tower IDs
ECL Studio UI + filters                
CSV export                             

In production: connect to Oracle/SAP, MRI/Yardi, 5x5 digital twin, county DBs
4-week engagement to go live with real data
```

### Visual Guidance
Two-column layout. Left (green check): real capabilities. Right (amber triangle): simulated data. Bridge arrow showing "4 weeks to production."

### Speaker Notes
> "Let me be crystal clear about what you just saw.
>
> **The engine is real.** The entity extraction runs a live LLM. The reconciliation logic processes 8 data sources across 9 patterns. The graph persistence, the tracing, the UI — all production-grade. 40 automated tests passing.
>
> **The data is simulated.** We generated realistic contracts, invoices, and audit findings modeled on publicly available Summit lease structures. The discrepancy rates match industry benchmarks.
>
> In a 4-week engagement, we'd connect this to your actual ERP, lease management, and 5x5 digital twin APIs. Same engine, real data, real dollars."

---

## SLIDE 17: The Context Graph — Everything Connected
**Time: 0:45 | Running: 14:45**

### Slide Content
```
ECL Context Graph: TR-8803

                    [Tower TR-8803]
                    Monopole | 150ft
                   /     |      \
          [Verizon]   [DISH⚠️]   [Ground Lease]
           Active     DEFAULTED    Johnson Ranch
           $2,800/mo  $1,950/mo    $800/mo
            /    \       |    \
     [6 Antennas] [3 RRU] [3 Ant] [MW Dish🔴]
      Good  ✅    Good ✅  Oxidized  CORRODED
            \                    /
         [Billing ✅]    [Billing ⚠️ SUSPENDED]
          Paid $2,800      Outstanding $5,850
                    \       /
              [WO-2026-0142]
              DISH Removal — $18,500
```

### Visual Guidance
Graph visualization with hub-and-spoke from tower node. Color-coded: green (healthy), yellow (warning), red (critical). Relationship labels on edges.

### Speaker Notes
> "This is what the graph looks like for one tower — TR-8803. Every node is an entity. Every edge is a relationship. Every piece is traced back to its source.
>
> The tower connects to its tenants. Each tenant connects to their equipment. Equipment connects to drone observations. Billing connects to payment status. Work orders connect to the actions needed.
>
> An AI agent can traverse this graph and answer: 'What towers have defaulted equipment needing removal?' — and get TR-8803 with DISH, the corroded microwave dish, $5,850 outstanding, and the pending work order. All grounded, all traceable, zero hallucination."

---

## SLIDE 18: ECL Powers 65 Agent Use Cases
**Time: 0:45 | Running: 15:30**

### Slide Content
```
ECL Enables Enterprise AI Agents Across Industries

Insurance    KYC Agent traverses borrower graph
             Claims Agent links FNOL → policy → coverage → payout

Finance      CapEx Classifier links invoices → assets → depreciation
             Revenue Agent traverses contract → billing → recognition

Telecom      Tower Agent reconciles contract → drone → billing
             Lease Agent automates amendments from ECL signals

Lending      Loan Review Agent traverses credit → employment → property
             Risk Agent links borrower → collateral → market

Government   Permitting Agent links application → regulation → status
             Compliance Agent traverses audit trail → violation → action

All powered by ECL graphs. All traceable. All explainable.
```

### Visual Guidance
Industry icons in a 2×5 grid. Each with agent name and the ECL graph path it traverses.

### Speaker Notes
> "This isn't just telecom. ECL powers agents across every industry.
>
> In insurance, a KYC agent traverses the borrower's full graph — contracts, payments, calls, tickets — and assesses risk. In finance, a CapEx classifier links invoices to assets to depreciation schedules — that's a $1M tax savings use case.
>
> In lending, a loan review agent traverses credit, employment, and property graphs. In government, a permitting agent links applications to regulations.
>
> The pattern is the same: **agents need context graphs, not flat data**. ECL provides them."

---

# ACT 3 — THE LANDSCAPE (Slides 19–22, ~5 min)

---

## SLIDE 19: Market Convergence Ecosystem
**Time: 1:15 | Running: 16:45**

### Slide Content
```
ECL Market: 5 Layers Racing Inward

[Outer Ring] ISV Agent Platforms
  Salesforce AgentForce • ServiceNow NowAssist • Microsoft Copilot
  "Partial context, walled gardens"

[Ring 4] ETL Incumbents Pivoting
  Informatica • Fivetran • Palantir • dbt
  "Adding context to pipelines"

[Ring 3] Hyperscaler AI Platforms
  AWS Neptune • Azure Cosmos • GCP Vertex
  "$602B CapEx fueling graph infra"

[Ring 2] Graph DB Infrastructure
  Neo4j • FalkorDB • Memgraph • Databricks GraphRAG
  "The ECL engines"

[Center] Context-Native Startups
  TrustGraph • Glean • Stardog • Tamr
  "ECL-first = highest ROI"

↗ Accion Labs: Cuts across ALL rings
  "Vendor-neutral ECL architects"
```

### Visual Guidance
Concentric rings diagram (bullseye). Color-coded: Red (ISV) → Orange (ETL) → Purple (hyperscaler) → Blue (graph DB) → Green (startups). Gold arrow for Accion Labs cutting across all rings.

### Speaker Notes
> "Every ring is racing inward toward ECL.
>
> Startups like TrustGraph and Glean build context graphs natively. Graph databases like Neo4j and FalkorDB provide the engines. Hyperscalers are spending $602 billion to fund graph infrastructure. ETL vendors like Informatica — now part of Salesforce — are pivoting to add context capabilities.
>
> And at the outer ring, ISVs like Salesforce AgentForce and ServiceNow NowAssist claim you don't need ECL because their platforms 'have it built in.'
>
> **Spoiler: they don't.** And that's where we come in. Accion Labs is the **vendor-neutral ECL architect** who builds graphs on FalkorDB or Neo4j, integrates Informatica or Databricks pipelines, and exposes context to AgentForce or Copilot via MCP."

---

## SLIDE 20: ISV Claims vs. Reality
**Time: 1:00 | Running: 17:45**

### Slide Content
```
"You Don't Need ECL" — And Why They're Wrong

ISV Claim                    ECL Reality (Our POC Proof)
─────────────────────────    ────────────────────────────────────
"RAG is enough"              Vectors can't multi-hop:
                             Drone → Contract → Default → $5,850

"Built-in Data Graphs"       Salesforce Data Graphs = table views
                             No Cypher traversal across drone/contract

"CRM-native context"         Can't ingest drone images + JDE contracts
                             ECL extracts multimodal entities

"Simplicity & speed"         Our MoE handles messy 80% unstructured
                             Their RAG needs 10+ curated KB articles

AgentForce: CRM RAG + workflows   = 70% reliable
         + ECL Graph: cross-system = 95%+
```

### Visual Guidance
Split screen: Left (ISV claims in red) vs Right (ECL reality in green). POC screenshot overlay.

### Speaker Notes
> "ISVs make four claims about why you don't need ECL. Let me address each with our POC:
>
> **'RAG is enough'** — Vector search found 'dish' and 'defaulted' in the same document. But it can't traverse: drone image shows corroded dish → DISH contract #08803-B → 90 days overdue → $5,850 outstanding. Our graph traverses it instantly.
>
> **'Built-in Data Graphs'** — Salesforce Data Graphs are table views, not knowledge graphs. No native Cypher traversal across drone data and contracts.
>
> **'CRM-native context'** — Salesforce indexes YOUR knowledge base. It can't ingest drone inspection JSON plus JDE contracts plus Oracle billing. ECL extracts from all of them.
>
> Salesforce even admits — they partnered with Informatica because 'context is the new currency.' They know they need ECL. We build it."

---

## SLIDE 21: ECL Effort in AI Projects
**Time: 0:45 | Running: 18:30**

### Slide Content
```
60-70% of Enterprise AI Budget = ECL Work

Phase                    Effort    ECL Focus              Cost Range
─────────────────────    ──────    ─────────────────────  ──────────
Data/Context Prep         40-50%   Entity extraction      $60-200K
ECL Pipeline Build        20-25%   Relationships, graph   $30-100K
Governance/Retrieval      10-15%   Provenance, access     $15-50K
Model + Integration       20-25%   Agent tools, MCP       $30-150K

ETL was 80% of data projects.
ECL is 60-70% of AI projects.
Data engineers → Context architects.
```

### Visual Guidance
Donut chart: 60-70% ECL (blue/green gradient) vs 30% model/integration (gray). Cost callouts.

### Speaker Notes
> "Here's the business reality: 60 to 70 percent of enterprise AI project effort is context and ECL work. Data prep, entity extraction, graph ontology, governance.
>
> Only 20-25% is model fine-tuning and integration.
>
> This is the same shift we saw with ETL: 80% of classic data projects was pipeline work. Now 60-70% of AI projects is context work.
>
> Data engineers are becoming **context architects**. The ones who learn graph skills, Cypher, ontology design — they're the most valuable people on the team."

---

## SLIDE 22: The 2026 Data Engineer
**Time: 0:45 | Running: 19:15**

### Slide Content
```
Data Engineer 2.0: Context Architect

Old Skills (keep)           New Skills (add)
─────────────────           ──────────────────
SQL, Python                 Cypher, GQL
ETL Pipelines               ECL Pipelines
Data Warehousing            Knowledge Graphs
BI Dashboards               Agent Tool Design (MCP)
Data Quality                Entity Validation + Confidence
Schema Design               Graph Ontology Design
                            Hallucination Guards
                            Pipeline Tracing

Market Signal: Data engineering jobs growing
              25% faster than AI specialist roles
```

### Visual Guidance
Two-column layout. Evolution graphic: wrench icon → architect icon. Job growth stat highlighted.

### Speaker Notes
> "This changes our role as data engineers.
>
> We're not just building pipelines anymore. We're becoming **Context Architects**.
>
> The skills stack: graph databases, Cypher queries, MoE expert design, MCP tools, agent tracing, hallucination controls, confidence guardrails.
>
> And the market knows it — data engineering jobs are growing 25% faster than pure AI specialist roles."

---

# ACT 4 — IMPLEMENTATION & CLOSE (Slides 23–30, ~10 min)

---

## SLIDE 23: Governance, Risk & Trust
**Time: 0:45 | Running: 20:00**

### Slide Content
```
Enterprise-Grade Governance Built In

Node-Level Access Control (ABAC)
  → Role-based visibility on entities and relationships

Provenance & Lineage
  → Every entity traced to source document + extraction expert

Confidence Guardrails
  → Minimum threshold (default 0.70), rejected entities logged

Hallucination Guard
  → Entity names validated against source text

Full Audit Trail
  → JSON trace per pipeline: expert, model, duration, results

Retention Policies
  → Auto-purge per governance policy (default: 365 days)
```

### Visual Guidance
Shield icon with 6 governance features radiating outward. Lock icons, checkmarks.

### Speaker Notes
> "Enterprise means governance. ECL has it built in — not bolted on.
>
> **Node-level access control** — attribute-based, so different roles see different entities.
>
> **Provenance** — every entity traces back to the source document, the expert that extracted it, the model version, and the confidence score.
>
> **Confidence guardrails** — we set a threshold. Below 0.70? Rejected and logged. Not silently discarded — logged, so you can audit why.
>
> **Hallucination guard** — entity names are validated against the source text. If the LLM generates an entity that doesn't appear in the document, we flag it.
>
> And a **full audit trail** — JSON trace files for every pipeline run. When the auditor asks 'how did you arrive at this recommendation?' — we show them the trace."

---

## SLIDE 24: Phased Roadmap
**Time: 1:00 | Running: 21:00**

### Slide Content
```
Implementation Roadmap: 4 Phases

Phase 1: Strengthen ETL Foundation (Weeks 1-4)
  Solidify schemas, data quality, monitoring
  Audit unstructured data landscape

Phase 2: Pilot ECL on ONE Domain (Weeks 5-12)
  Pick highest-value domain (e.g., tower reconciliation)
  Build MoE experts, extract entities, create graph
  Measure vs. ETL-only baseline

Phase 3: Deploy Agent with ECL+ETL (Weeks 13-20)
  Build MCP tools, expose graph to agents
  Deploy copilot using both warehouse + graph
  Add tracing, governance, confidence guardrails

Phase 4: Expand & Automate (Ongoing)
  Additional domains, cross-domain linking
  Automated anomaly detection from graph
  Self-healing data quality via ECL feedback loops
```

### Visual Guidance
Timeline graphic: 4 connected arrows left to right. Milestone markers at each phase.

### Speaker Notes
> "Don't try to graph everything. That's the #1 mistake.
>
> **Phase 1** — strengthen your ETL foundation. Clean schemas, data quality, monitoring. You need a solid warehouse before you add a context layer on top.
>
> **Phase 2** — pick ONE domain. For telecom, it's tower reconciliation. For insurance, it's claims processing. Build your MoE experts, extract entities, create the graph. **Measure against your ETL-only baseline.**
>
> **Phase 3** — deploy an agent that uses both the warehouse AND the graph. MCP tools, tracing, governance. This is where ROI starts compounding.
>
> **Phase 4** — expand to additional domains. Cross-domain linking. Automated anomaly detection.
>
> We can have you at Phase 2 in 12 weeks."

---

## SLIDE 25: Avoid "Graph Everything"
**Time: 0:45 | Running: 21:45**

### Slide Content
```
Common ECL Failure Modes

❌ "Graph Everything" — Start with highest-value domain
❌ No ETL foundation — ECL augments, doesn't replace
❌ Over-complex ontology — Start simple, evolve
❌ Ignore governance — Ungoverned graphs = liability
❌ Skip measurement — Always compare vs. baseline

✅ Focus Areas for Maximum ROI:
   Revenue recovery    → Telecom tower reconciliation
   Fraud detection     → Cross-system pattern matching
   Contract analytics  → Obligation + amendment tracking
   Customer 360        → Support + billing + contract graph
   Compliance          → Regulation → policy → evidence linking
```

### Visual Guidance
Left column: red X marks with anti-patterns. Right column: green checkmarks with focus areas.

### Speaker Notes
> "A word of caution: don't try to graph everything.
>
> Start with your highest-value domain. For telecom, it's escalation reconciliation — purely data-driven, no drone needed, $10-50M annually. Then layer in co-location audits for the highest dollar recovery.
>
> Our POC found $47.3 million in annual impact from a simulated portfolio of ~1,000 contracts. Scale to Summit's 40,000 towers — the math speaks for itself.
>
> Keep the ontology simple at first. You don't need 500 entity types on day one."

---

## SLIDE 26: ROI & Economics
**Time: 1:00 | Running: 22:45**

### Slide Content
```
ECL ROI: The Numbers

Manual Process              ECL Automation
──────────────────          ──────────────────
20 min / document            3 seconds
40,000 hours / year          500 hours
$3M labor cost               $37K
15% missed opportunities     0% (graph traversal)
+ $380K Lyzr license         $0 (local LLM)

Annual Impact:
  Labor savings:           $2.96M
  Missed opportunities:    $1.2M
  Vendor savings:          $380K
  ─────────────────────────────
  Total:                   $4.54M / year

POC ROI: 300-500% in 12 months
```

### Visual Guidance
Two columns with dramatic comparison. Dollar figures in large neon green font. Bar chart comparing costs.

### Speaker Notes
> "Let's talk numbers.
>
> A human analyst takes 20 minutes per document. At enterprise scale — 10,000 towers, 120,000 documents per year — that's 40,000 labor hours annually.
>
> With ECL: 3 seconds per document. 500 hours total.
>
> That's **$2.96 million in labor savings**.
>
> Then the reconciliation engine: $47.3 million in discrepancies found across 9 data sources — escalation errors, unbilled equipment, undersold towers, DISH default exposure.
>
> **Plus** you save $380K that you would have paid an ISV like Lyzr for the same use case.
>
> Total: **$47M+ per year at scale.** POC pays for itself in weeks."

---

## SLIDE 27: Where the Market Is Heading
**Time: 0:45 | Running: 23:30**

### Slide Content
```
Knowledge Graph Market: Explosive Growth

$1.5B (2024) → $25.7B (2032) | 37% CAGR

Context Graph = "$1 Trillion Opportunity"
    — Foundation Capital

Key Signals:
  • Neo4j joins Linux Foundation AI & Data
  • AWS launches Neptune GraphRAG + Strands SDK
  • Databricks adds GraphRAG to Lakehouse
  • Informatica acquired by Salesforce (context = currency)
  • GQL becomes first new DB query language since SQL (1987)

The integrator who stitches context
across heterogeneous systems wins.
```

### Visual Guidance
Growth chart from $1.5B to $25.7B. Vendor logos along a timeline. Quote callout from Foundation Capital.

### Speaker Notes
> "The market is sending clear signals.
>
> Knowledge graphs growing at 37% CAGR to $25.7 billion by 2032. Foundation Capital calls context graphs a trillion-dollar opportunity.
>
> Neo4j joined the Linux Foundation. AWS launched Neptune GraphRAG. Databricks added GraphRAG to the Lakehouse. Informatica was acquired by Salesforce precisely because 'context is the new currency.'
>
> GQL became the first new database query language since SQL in 1987. That's how significant this shift is.
>
> The winner won't be the vendor that sees one workflow deeply. It'll be the **integrator who stitches context across all systems.** That's our position."

---

## SLIDE 28: Accion Labs' ECL Capability
**Time: 0:45 | Running: 24:15**

### Slide Content
```
Accion Labs: Your ECL Architecture Partner

🏗️ ARCHITECTURE  — Design ontology, select graph DB, plan data flows
🔧 BUILD         — MoE experts, extraction pipelines, entity validation
🔗 INTEGRATE     — Connect ECL to your ETL, ERP, IoT, document stores
🛡️ GOVERN        — Provenance, confidence guardrails, retention policies
📊 MANAGED       — Ongoing optimization, new domains, agent expansion

Our ECL Stack:
  Local LLM (Ollama)  → $0/yr vs $380K cloud
  FalkorDB            → Graph DB (Redis-compatible)
  MCP Tools           → Standard agent protocol
  40 Automated Tests  → Production-grade
  ECL Studio          → Low-code for business users
```

### Visual Guidance
5 service pillars as horizontal bars. Tech stack icons below. Accion Labs gold branding.

### Speaker Notes
> "Accion Labs brings this to you with five capabilities:
>
> We **architect** your ontology and data flows. We **build** the MoE experts and extraction pipelines. We **integrate** ECL with your existing ETL, ERP, and document stores. We **govern** with provenance, guardrails, and retention policies. And we provide **managed services** for ongoing optimization.
>
> Our stack is battle-tested: 40 automated tests passing, ECL Studio with reconciliation dashboard, local LLM, 9-way cross-reference engine that surfaced $47.3M in impact across 2,810 discrepancies. From simulated data — but the engine is ready for real."

---

## SLIDE 29: Call to Action
**Time: 0:45 | Running: 25:00**

### Slide Content
```
Start Your ECL Journey

Step 1: AUDIT (Week 1-2)
  We assess your unstructured data landscape
  Identify highest-value ECL domain

Step 2: PILOT (Week 3-12)
  Build ECL for one domain
  Measure vs. ETL-only baseline
  Deliver working graph + agent tools

Step 3: SCALE (Week 13+)
  Expand to additional domains
  Cross-domain linking
  Full agent integration

POC in 2 Weeks → ROI in 90 Days → $4.5M+ Annual Impact

"Let's build your context graph."
```

### Visual Guidance
Three ascending steps graphic. Timeline with milestone markers. CTA in large bold font at bottom.

### Speaker Notes
> "If this resonates, here's how we start:
>
> **Step 1: Audit** — We spend two weeks assessing your unstructured data landscape and identifying the highest-value domain for ECL. This is free.
>
> **Step 2: Pilot** — We build ECL for one domain. Connect to your real ERP, lease management, and 5x5 data. You get a working graph, reconciliation engine, and measurable results. 12 weeks.
>
> **Step 3: Scale** — We expand to additional domains, additional reconciliation patterns, and full agent integration.
>
> **POC in 2 weeks. Production in 4. $47M+ annual impact at Summit scale.**
>
> I'll be around after the session — let's discuss your context graph needs."

---

## SLIDE 30: Monday Morning Takeaways ☀️
**Time: 1:00 | Running: 26:00**

### Slide Content
```
Monday Morning Takeaways
5 things you can do THIS WEEK

☐ 1. CLONE THE REPO (10 min)
     git clone github.com/thedataengineer/EKG
     pip install -r requirements.txt && python test_ecl.py
     → See 40/40 tests pass. You have a working ECL engine.

☐ 2. AUDIT YOUR 80% (1 hour)
     List every unstructured data source your team ignores today:
     contracts, emails, PDFs, inspection reports, logs.
     → That's your ECL opportunity map.

☐ 3. PICK YOUR FIRST GRAPH (30 min)
     Choose the ONE domain where relationships matter most:
     Contract ↔ Invoice? Claim ↔ Policy? Borrower ↔ Collateral?
     → Start with 3 entity types and 2 relationships. Not 50.

☐ 4. RUN A LOCAL LLM (15 min)
     brew install ollama && ollama pull llama3:8b
     → You now have $0/query entity extraction on your laptop.

☐ 5. MEASURE YOUR BASELINE (1 hour)
     How long does a human take to extract entities from one document?
     Multiply × annual volume. That's your ROI denominator.
     → Bring this number to the POC kickoff.
```

### Visual Guidance
Checklist layout with checkbox icons. Each item has a time estimate badge. Morning sunrise gradient at top. Practical, action-oriented — no fluff.

### Speaker Notes
> "Before Q&A — five things you can do Monday morning. Not next quarter. Monday.
>
> **One:** Clone our repo. It's open source. Run the tests — 40 out of 40 pass. You have a working ECL engine on your laptop in 10 minutes.
>
> **Two:** Audit your 80 percent. Walk to your team and ask: 'What unstructured data do we ignore?' Contracts, inspection reports, emails, logs. Write them down. That's your ECL opportunity map.
>
> **Three:** Pick one graph. Don't try to model everything. Start with 3 entity types and 2 relationship types. Contract links to Invoice. Claim links to Policy. That's enough to prove value.
>
> **Four:** Run a local LLM. Ollama installs in one command. Pull llama3:8b. You now have zero-cost entity extraction on your laptop.
>
> **Five:** Measure your baseline. How long does a human take to review one document? Multiply by your annual volume. That gives you the denominator for your ROI calculation. Bring that number to our POC kickoff.
>
> These aren't strategic initiatives. These are things you can do before lunch on Monday."

---

## SLIDE 31: Thank You & Q&A
**Time: Open | Running: 25:00+**

### Slide Content
```
Thank You

[Your Name]
Field CTO, Accion Labs

📧  [email]
🔗  github.com/thedataengineer/EKG

Resources:
  [QR Code] → ECL Whitepaper
  [QR Code] → GitHub: Live POC Code
  [QR Code] → Book a Workshop

"Data engineering's strategic moment —
 build context infrastructure now."

Q&A
```

### Visual Guidance
Clean layout. Three QR codes in a row. Portrait photo. Accion Labs branding. Dark background with subtle graph node pattern.

### Speaker Notes
> "Thank you all.
>
> The code is open-source on GitHub — you can run the full POC today. Local LLM, local graph, zero cost.
>
> I'm here for the rest of the summit. Grab me for a deeper dive, a live demo on your data, or to schedule a workshop.
>
> **Questions?**"

---

# APPENDIX — PRESENTATION LOGISTICS

## Emergency Fallbacks

| If...                    | Then...                                              |
|--------------------------|------------------------------------------------------|
| Ollama is slow/down      | Run `ecl_poc.py` (regex experts, still works)        |
| FalkorDB is down         | Show reconciliation dashboard in Streamlit            |
| Streamlit won't start    | Run `python3 reconcile_contracts.py` in terminal      |
| Invoice data missing     | Run generators: `python3 generate_erp_invoices.py && python3 generate_tower_ops_data.py` |
| Network issues           | All runs locally — no network needed                 |
| Need Lyzr comparison     | Open `ECL_ARCHITECTURE.html` in browser              |

## Key Talking Points (Memorize)

1. **"80% of enterprise data is unstructured"** — ETL ignores it
2. **"9 cross-reference patterns, 8 data sources"** — comprehensive reconciliation
3. **"2,810 discrepancies, $47.3M impact — in 3 seconds"** — the demo impact
4. **"2-5% leakage × $3.9B = $39-195M/yr"** — Summit math
5. **"Simulated data, real engine"** — transparent about what's demo vs production
6. **"141 undersold towers = $7.1M/yr opportunity"** — revenue, not just savings
7. **"DISH: $66.7M exposure, 49 defaulted"** — timely headline
8. **"$0 vs $380K per year"** — cost kill shot vs Lyzr
9. **"60-70% of AI budget = context work"** — data engineers are context architects
10. **"POC in 2 weeks, production in 4"** — call to action

## Timing Checklist

| Section                           | Target   | Running Total |
|-----------------------------------|----------|---------------|
| Title + Intro (Slide 1)          | 0:30     | 0:30          |
| Problem Statement (Slides 2-5)   | 3:45     | 4:15          |
| ETL vs ECL + Why Now (Slides 6-8)| 2:30     | 6:45          |
| Architecture (Slides 9-10)       | 1:30     | 8:15          |
| Healthcare Example (Slides 11-12)| 1:30     | 9:45          |
| **Reconciliation POC (Slides 13-16)** | **4:15** | **14:00** |
| Context + Agents (Slides 17-18)  | 1:30     | 15:30         |
| Market Landscape (Slides 19-22)  | 3:45     | 19:15         |
| Implementation (Slides 23-26)    | 3:30     | 22:45         |
| Close + CTA (Slides 27-30)       | 2:15     | 25:00         |
| **Q&A Buffer**                    | **15:00**| **40:00**     |

## Demo Script (During Slides 13-16)

```bash
# Pre-flight (before session starts)
docker run -p 6379:6379 falkordb/falkordb
ollama serve
cd /Users/yakarteek/Code/Accion/Summit/ECL
pyenv shell ecl-demo

# Generate data if not present
python3 generate_erp_invoices.py
python3 generate_tower_audits.py
python3 generate_tower_ops_data.py

# Launch
streamlit run ecl_app.py

# Verify
python3 test_ecl.py              # 40/40 passed
python3 reconcile_contracts.py   # 2,810 discrepancies, $47.3M

# During demo:
# 1. Open Streamlit → Click "📋 Load Sample"
# 2. Click "⚡ Extract Entities" → show live extraction
# 3. Switch to "💰 Invoice Recon" tab
# 4. Point out SIMULATED DATA badge
# 5. Expand "Why This Matters" → show impact matrix
# 6. Expand "9 Cross-Reference Patterns" → walk through table
# 7. Click "🔄 Run 9-Way Cross-Reference Reconciliation"
# 8. Show: 2,810 discrepancies, $47.3M impact, DISH, undersold
# 9. Filter by UC5 → drill into escalation errors
# 10. Download CSV → "hand this to a portfolio manager"
```
