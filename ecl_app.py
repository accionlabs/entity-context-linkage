"""
ECL Studio — Streamlit Edition
================================
Low-code builder for Entity-Context-Linking extraction pipeline.
Run: /Users/yakarteek/.pyenv/versions/ecl-demo/bin/streamlit run ecl_app.py
"""

import streamlit as st
import time
import json
import re
import os
import sys
from datetime import datetime
from dataclasses import asdict

# Ensure ECL modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ecl_poc import (
    Entity, Relationship, ExtractionResult, EntityType, RelationshipType,
    MoEOrchestrator, ContextGraphBuilder, HealthcareExpert,
)
from ecl_tracing import (
    ExtractionTrace, PipelineTrace, hash_text, save_trace,
    validate_entity, apply_confidence_filter, MIN_CONFIDENCE,
    get_prompt_version, PROMPT_VERSIONS,
)
from ecl_connectors import ConnectorRegistry
from ecl_governance import GovernanceEngine

# Telecom REIT integration
try:
    from telecom_reit.adapter import TelecomREITReconciliationExpert
    from telecom_reit.pipeline import TelecomREITPipeline
    from telecom_reit.sample_data import TELECOM_REIT_SAMPLE_DOCUMENT
    TELECOM_REIT_AVAILABLE = True
except ImportError:
    TELECOM_REIT_AVAILABLE = False

# Try LLM module
try:
    from ecl_llm import LLMMoEOrchestrator, OllamaClient
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Invoice reconciliation
try:
    from reconcile_contracts import load_contracts, load_invoices, reconcile
    RECON_AVAILABLE = True
except ImportError:
    RECON_AVAILABLE = False


# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECL Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.97));
        border: 1px solid rgba(99,102,241,0.35);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 8px rgba(99,102,241,0.1);
    }
    [data-testid="stMetricLabel"] {
        color: #e2e8f0 !important;
    }
    [data-testid="stMetricLabel"] label,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span,
    [data-testid="stMetricLabel"] div {
        color: #e2e8f0 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 900 !important;
        color: #ffffff !important;
    }
    [data-testid="stMetricValue"] div {
        color: #ffffff !important;
    }
    [data-testid="stMetricDelta"] {
        color: #a5b4fc !important;
    }
    [data-testid="stMetricDelta"] span,
    [data-testid="stMetricDelta"] div {
        color: #a5b4fc !important;
    }
    [data-testid="stMetricDelta"] svg {
        fill: #a5b4fc !important;
    }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    hr { border-color: rgba(99,102,241,0.2) !important; }
    /* Progress bar columns (Confidence) */
    [data-testid="stDataFrame"] [role="progressbar"] > div {
        background-color: #6366f1 !important;
    }
    [data-testid="stDataFrame"] [role="progressbar"] {
        background-color: rgba(99,102,241,0.2) !important;
    }
    /* Slider track */
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="progressbar"] > div {
        background-color: #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Ollama check ───────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def check_ollama():
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        resp = urllib.request.urlopen(req, timeout=2)
        data = json.loads(resp.read())
        models = [m["name"] for m in data.get("models", [])]
        return True, models
    except Exception:
        return False, []


# ── Expert definitions ─────────────────────────────────────────────────────
EXPERT_DEFS = [
    {"name": "ContractExpert", "domain": "Contracts & Agreements", "icon": "📄"},
    {"name": "EquipmentExpert", "domain": "Equipment & Assets", "icon": "⚙️"},
    {"name": "FinancialRiskExpert", "domain": "Financial Risks", "icon": "💰"},
    {"name": "OpportunityExpert", "domain": "Business Opportunities", "icon": "🎯"},
    {"name": "HealthcareExpert", "domain": "Healthcare Records", "icon": "🏥"},
    {"name": "TelecomREITReconciliationExpert", "domain": "Tower Reconciliation", "icon": "🏗️"},
]


# ── Sample document ────────────────────────────────────────────────────────
SAMPLE_DOC = """STRUCTURAL ANALYSIS REPORT 
Tower ID: T-789 | Location: 40.6892° N, 74.0445° W | Type: 150-ft Guyed Mast
Date of Analysis: February 25, 2026 | Engineer of Record: Summit Engineering

=== EXECUTIVE SUMMARY & REGULATORY COMPLIANCE ===
This report summarizes the structural evaluation of the existing 150-ft Guyed Mast to support proposed 
telecommunication equipment modifications. 
Compliance Standard: ANSI/TIA-222-H, ASCE 7-16, and 2018 IBC (International Building Code).
Risk Category: II | Topographic Category: 1

Overall Tower Stress Ratio: 86.4% (PASS)
Foundation Capacity Utilization: 71.2% (PASS)

=== SECTION A: ENVIRONMENTAL LOAD ANALYSIS ===
Analysis Platform: tnxTower v8.1.1
Basic Wind Speed (3-sec gust): 105 mph (without ice)
Concurrent Wind & Ice: 50 mph wind with 1.0 inch radial ice accumulation
Seismic Design Parameters (Site Class D): Ss = 0.180g, S1 = 0.055g

=== SECTION B: MEMBER CAPACITY & STRESS RATIOS ===
The structural components have been evaluated for capacity under load combinations:
- Leg Members (A572-50 Steel): 74.5% Utilization (Adequate)
- Diagonal Bracing (A36 Steel): 86.4% Utilization (Adequate - Controlling Component)
- Horizontal Bracing: 45.2% Utilization (Adequate)
- Guy Wire Tension (1-1/4" EHS): 12.5% of Breaking Strength (Acceptable)
- Bolted Connections (A325): 68.1% Capacity (Adequate)
- Foundation Anchors (Concrete): 71.2% Capacity (Adequate)

=== SECTION C: EQUIPMENT INVENTORY & APPERTUNANCES ===
Existing Contract #1001 - Verizon Wireless (Occupancy: 45%)
- 3x Ericsson AIR 6449 (Band 77, 5G NR) | Elev: 145 ft
- 6x Nokia AEQE Remote Radio Units (Power: 1,200W/unit)

Existing Contract #1002 - T-Mobile (Occupancy: 30%)
- 3x RFS APXVAARR24_43-U-NA20 | Elev: 130 ft

=== SECTION D: MAINTENANCE & SAFETY ASSESSMENT ===
Occupational Safety: Tower equipped with certified climbing facility (fall arrest cable installed).
Vulnerability Analysis: Guy anchor rods show minor surface oxidation; 
Recomendation: Wire rope inspection required by Q3 2026.
Available Capacity: Structural reinforcement required if total cross-sectional wind area exceeds 14 sq-ft.
"""


# ── Extraction logic (mirrors ecl_server._run_extraction) ──────────────────
def run_extraction(text: str, use_llm: bool, model: str, confidence_threshold: float,
                   hallucination_mode: str = "strict", adaptive: bool = False):
    """Run MoE extraction pipeline. Same logic as ecl_server.py."""
    start_time = time.time()

    # Choose orchestrator
    if use_llm and LLM_AVAILABLE:
        orchestrator = LLMMoEOrchestrator(model=model,
                                          hallucination_mode=hallucination_mode,
                                          adaptive=adaptive)
        results = orchestrator.extract_all(text)
    else:
        orchestrator = MoEOrchestrator()
        results = orchestrator.extract_all(text)

    # Build graph
    graph_builder = ContextGraphBuilder()
    graph_builder.add_extraction_results(results)

    # ── Cross-Entity Relationship Generation ───────────────────
    # In adaptive mode, the LLM already returns relationships — skip hardcoded wiring
    if not adaptive:
        # Detect tower ID from document to create a root node
        tower_match = re.search(
            r'(?:Tower\s*(?:ID|Site)?[:\s]*|SITE[:\s]*)([A-Z0-9][\w-]+)',
            text, re.IGNORECASE
        )
        tower_id = tower_match.group(1).strip() if tower_match else None

        if tower_id:
            # Create tower root node if it doesn't already exist
            tower_node_id = f"tower_{tower_id.lower().replace('-', '_')}"
            if tower_node_id not in graph_builder.nodes:
                from ecl_poc import Entity as _Entity, EntityType as _ET
                tower_entity = _Entity(
                    id=tower_node_id,
                    type=_ET.TOWER,
                    name=f"Tower {tower_id}",
                    properties={"tower_id": tower_id},
                    source_expert="auto",
                    confidence=1.0,
                )
                graph_builder.nodes[tower_node_id] = tower_entity

            # Wire relationships from every entity to the tower
            for eid, entity in graph_builder.nodes.items():
                if eid == tower_node_id:
                    continue
                if entity.type == EntityType.CONTRACT:
                    graph_builder.edges.append(Relationship(
                        eid, tower_node_id, RelationshipType.OCCUPIES, confidence=0.95))
                elif entity.type == EntityType.EQUIPMENT:
                    graph_builder.edges.append(Relationship(
                        eid, tower_node_id, RelationshipType.INSTALLED_ON, confidence=0.88))
                elif entity.type == EntityType.RISK:
                    graph_builder.edges.append(Relationship(
                        tower_node_id, eid, RelationshipType.HAS_RISK, confidence=0.90))
                elif entity.type == EntityType.OPPORTUNITY:
                    graph_builder.edges.append(Relationship(
                        tower_node_id, eid, RelationshipType.HAS_OPPORTUNITY, confidence=0.90))
                elif entity.type == EntityType.FINANCIAL:
                    graph_builder.edges.append(Relationship(
                        tower_node_id, eid, RelationshipType.AFFECTS, confidence=0.85))

        # Link equipment to their owning companies (cross-expert)
        company_nodes = {e.name.lower(): e for e in graph_builder.nodes.values()
                         if e.type == EntityType.COMPANY}
        for eid, entity in graph_builder.nodes.items():
            if entity.type == EntityType.EQUIPMENT:
                owner = entity.properties.get("company", "")
                if owner and owner.lower() in company_nodes:
                    graph_builder.edges.append(Relationship(
                        company_nodes[owner.lower()].id, eid,
                        RelationshipType.HAS_EQUIPMENT, confidence=0.85))

        # Link risks to affected contracts/companies (cross-expert)
        for eid, entity in graph_builder.nodes.items():
            if entity.type == EntityType.RISK:
                affected = entity.properties.get("affected_entity", "")
                if affected:
                    for cid, centity in graph_builder.nodes.items():
                        if (centity.type in (EntityType.CONTRACT, EntityType.COMPANY)
                                and affected.lower() in centity.name.lower()):
                            graph_builder.edges.append(Relationship(
                                eid, cid, RelationshipType.AFFECTS, confidence=0.85))
                            break


    # Serialize entities
    entities = []
    for eid, entity in graph_builder.nodes.items():
        entities.append({
            "id": entity.id,
            "type": entity.properties.get("_discovered_type", entity.type.value),
            "name": entity.name,
            "confidence": entity.confidence,
            "source_expert": entity.source_expert,
            "properties": entity.properties,
        })

    # Serialize relationships
    relationships = []
    for rel in graph_builder.edges:
        relationships.append({
            "source": rel.source_id,
            "target": rel.target_id,
            "type": rel.type.value,
            "confidence": rel.confidence,
        })

    elapsed_ms = (time.time() - start_time) * 1000

    # Expert breakdown
    expert_results = {}
    for expert_name, extraction in results.items():
        expert_results[expert_name] = {
            "entities": len(extraction.entities),
            "relationships": len(extraction.relationships),
            "reasoning": extraction.reasoning,
        }

    return {
        "entities": entities,
        "relationships": relationships,
        "expert_results": expert_results,
        "total_entities": len(entities),
        "total_relationships": len(relationships),
        "processing_time_ms": round(elapsed_ms),
        "engine": model if use_llm else "regex",
        "confidence_threshold": confidence_threshold,
    }


# ── Session state init ─────────────────────────────────────────────────────
if "doc_text" not in st.session_state:
    st.session_state["doc_text"] = ""
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ ECL Studio")
    st.caption("Low-Code Entity Extraction Builder")
    st.divider()

    app_view = st.radio(
        "Dashboard Mode",
        ["📄 Single Document", "🌐 Portfolio Analytics (750 Leases)"],
        label_visibility="collapsed"
    )
    st.divider()

    # ── Status ──
    ollama_ok, models = check_ollama()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🟢 **Ollama**" if ollama_ok else "🔴 **Ollama**")
    with col2:
        st.markdown(f"📡 `{len(models)}` models")
    st.caption(f"LLM Module: {'✅ Loaded' if LLM_AVAILABLE else '❌ Not found'}")

    st.divider()

    # ── Experts ──
    st.markdown("### 🧠 Extraction Experts")
    enabled_experts = []
    for exp in EXPERT_DEFS:
        enabled = st.checkbox(
            f"{exp['icon']} {exp['name']}",
            value=(exp["name"] != "HealthcareExpert"),
            key=f"expert_{exp['name']}",
        )
        if enabled:
            enabled_experts.append(exp["name"])

    st.divider()

    # ── Config ──
    st.markdown("### ⚙️ Configuration")
    confidence = st.slider(
        "Confidence Threshold",
        min_value=0.0, max_value=1.0, value=0.70, step=0.05, format="%.2f",
    )

    halluc_mode = st.selectbox(
        "Hallucination Guard",
        ["🛡️ Strict (reject ungrounded)", "⚠️ Moderate (warn + keep)", "🔓 Off (accept all)"],
        help="Controls how aggressively the hallucination guard filters LLM-extracted entities. "
             "Strict rejects entities not grounded in source text. "
             "Moderate keeps them with reduced confidence. "
             "Off accepts all LLM output.",
    )
    halluc_mode_key = {"🛡️ Strict (reject ungrounded)": "strict",
                       "⚠️ Moderate (warn + keep)": "moderate",
                       "🔓 Off (accept all)": "off"}[halluc_mode]

    mode = st.selectbox(
        "Extraction Mode",
        ["Regex Experts (Fast)", "LLM Experts (Ollama)", "Adaptive LLM (Any Document)"],
    )
    use_llm = mode in ("LLM Experts (Ollama)", "Adaptive LLM (Any Document)")
    use_adaptive = (mode == "Adaptive LLM (Any Document)")

    model_options = models if models else ["llama3:8b", "mistral:7b", "gemma2:9b"]
    model = st.selectbox("LLM Model", model_options, disabled=(not use_llm))

    st.divider()

    # ── Connectors ──
    st.markdown("### 🔌 Connectors")
    for name, online in [("FileSystem (Local)", True), ("SharePoint", False),
                          ("Dynamics 365", False), ("ServiceNow", False)]:
        st.markdown(f"{'🟢' if online else '🟡'} {name}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════════════════

if app_view == "🌐 Portfolio Analytics (750 Leases)":
    st.markdown("# 🌐 Global Lease Portfolio")
    st.info("Batch aggregating 750 tenant sublicensing agreements...")
    
    # Initialize session state for the parsed portfolio
    if "portfolio_data" not in st.session_state:
        st.session_state.portfolio_data = None
    
    if st.button("Render Portfolio Graph", type="primary"):
        with st.spinner("Batch processing 750 leases..."):
            from ecl_lease_ingestor import build_portfolio_graph
            
            # Cache to prevent reloading on dropdown change
            st.session_state.portfolio_data = build_portfolio_graph()
            
    # If we have parsed the data, render the UI metrics and tabs
    if st.session_state.portfolio_data:
        res = st.session_state.portfolio_data
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Lease Entities", f"{res['total_entities']:,}")
        m2.metric("Total Relationships", f"{res['total_relationships']:,}")
        m3.metric("Monthly Rent", f"${res['total_rent']:,.2f}")
        m4.metric("Processing Time", f"{res['processing_time_ms']} ms")
        
        entities, relationships = res["entities"], res["relationships"]
        try:
                from streamlit_agraph import agraph, Node, Edge, Config
                colors = {
                    "ASSET": "#3b82f6", "COMPANY": "#8b5cf6",
                    "CONTRACT": "#f59e0b", "MONETARY": "#10b981",
                    "EQUIPMENT": "#6366f1", "RISK": "#f87171",
                    "OPPORTUNITY": "#f97316", "PERSON": "#ec4899",
                    "TOWER": "#3b82f6", "FINANCIAL_METRIC": "#10b981",
                }
                nodes = []
                seen = set()
                for ent in entities:
                    name = ent["name"]
                    etype = ent.get("type", "Other")
                    if name not in seen:
                        nodes.append(Node(
                            id=name, label=name, size=25,
                            color=colors.get(etype, "#64748b"),
                            font={"color": "#e2e8f0", "size": 14},
                        ))
                        seen.add(name)

                edges = []
                for rel in relationships:
                    src_name = next((e["name"] for e in entities if e["id"] == rel.get("source_id", rel.get("source"))), rel.get("source_id", rel.get("source")))
                    tgt_name = next((e["name"] for e in entities if e["id"] == rel.get("target_id", rel.get("target"))), rel.get("target_id", rel.get("target")))
                    if src_name in seen and tgt_name in seen:
                        edges.append(Edge(
                            source=src_name, target=tgt_name,
                            label=rel.get("type", ""), color="#475569",
                        ))

                config = Config(
                    width=900, height=600, directed=True,
                    physics=True, hierarchical=False,
                    nodeHighlightBehavior=True, highlightColor="#f59e0b",
                )

                # Group into UI tabs
                st.divider()
                tab_portfolio, tab_map = st.tabs(["🕸️ Network Topology", "🗺️ Geographic Map"])
                
                with tab_portfolio:
                    agraph(nodes=nodes, edges=edges, config=config)
                    
                with tab_map:
                    # Metric toggle selector
                    st.caption("Select a business metric to project onto the geographic topology:")
                    metric_choice = st.selectbox("Metric to Map", [
                        "🟠 Core Monthly Rent", 
                        "🟢 Room to Sell (Capacity Revenue Opportunity)", 
                        "🔴 At Risk / Lost Revenue (Arrears & Defaults)"
                    ])
                    
                    # Filter for entities that have valid coordinates
                    geo_data = []
                    for ent in entities:
                        props = ent.get("properties", {})
                        if props.get("latitude") and props.get("longitude"):
                            geo_data.append({
                                "city": props.get("location"),
                                "lat": props.get("latitude"),
                                "lon": props.get("longitude"),
                                "rent": props.get("monthly_rent", 0.0),
                                "lost": props.get("lost_revenue", 0.0),
                                "capacity": props.get("capacity_revenue", 0.0)
                            })
                    
                    if geo_data:
                        import pandas as pd
                        import pydeck as pdk
                        
                        df = pd.DataFrame(geo_data)
                        
                        # Determine mapping logic based on dropdown selection
                        if "Room to Sell" in metric_choice:
                            elev_col = 'capacity'
                            color = [34, 197, 94, 160]   # Green
                            tooltip_label = "Capacity Opportunity"
                        elif "At Risk" in metric_choice:
                            elev_col = 'lost'
                            color = [239, 68, 68, 160]   # Red
                            tooltip_label = "Lost/At-Risk Revenue"
                        else:
                            elev_col = 'rent'
                            color = [245, 158, 11, 160]  # Orange
                            tooltip_label = "Monthly Rent"

                        # A simple hexbin or scatterplot for towers
                        st.pydeck_chart(pdk.Deck(
                            map_style=None,
                            initial_view_state=pdk.ViewState(
                                latitude=39.8283, # Center of US
                                longitude=-98.5795,
                                zoom=3,
                                pitch=45,
                            ),
                            layers=[
                                pdk.Layer(
                                    'ColumnLayer',
                                    data=df,
                                    get_position='[lon, lat]',
                                    get_elevation=elev_col,
                                    elevation_scale=5,
                                    radius=20000,
                                    get_fill_color=color,
                                    pickable=True,
                                    auto_highlight=True,
                                )
                            ],
                            tooltip={
                                "html": f"<b>{{city}}</b><br/>{tooltip_label}: ${{ {elev_col} }}",
                                "style": {"color": "white"}
                            }
                        ))
                    else:
                        st.info("No geographic coordinates found in the dataset.")

        except ImportError:
            st.warning("Install `streamlit-agraph` and `pydeck` for full visualization.")
    st.stop()


st.markdown("# 📄 Document Input")

# ── Load Ground Lease helper ──
def _load_lease_docs():
    """Load original lease + 2 amendments as a combined multi-document input."""
    base = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(base, "sample_documents")
    files = [
        ("DOCUMENT 1 OF 3 — ORIGINAL GROUND LEASE AGREEMENT", "crown_castle_ground_lease.md"),
        ("DOCUMENT 2 OF 3 — FIRST AMENDMENT", "crown_castle_amendment_1.md"),
        ("DOCUMENT 3 OF 3 — SECOND AMENDMENT", "crown_castle_amendment_2.md"),
    ]
    parts = []
    for header, fname in files:
        fpath = os.path.join(docs_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "r") as f:
                parts.append(f"{'='*70}\n{header}\nSource File: {fname}\n{'='*70}\n\n{f.read()}")
    return "\n\n".join(parts) if parts else "Ground lease documents not found."

# Buttons BEFORE the text_area (avoids session_state widget conflict)
if TELECOM_REIT_AVAILABLE:
    col_btn1, col_btn2, col_btn3, col_btn4, col_spacer = st.columns([1, 1, 1.2, 1.4, 1.4])
else:
    col_btn1, col_btn2, col_btn4, col_spacer = st.columns([1, 1, 1.4, 2.6])
    col_btn3 = None
with col_btn1:
    load_sample = st.button("📋 Load Sample", width="stretch")
with col_btn2:
    clear = st.button("🗑️ Clear", width="stretch")
if col_btn3 is not None:
    with col_btn3:
        load_tr_sample = st.button("🏗️ Load Tower Report", width="stretch")
else:
    load_tr_sample = False
with col_btn4:
    load_lease = st.button("📄 Load Ground Lease", width="stretch")

if load_sample:
    st.session_state["doc_text"] = SAMPLE_DOC
if clear:
    st.session_state["doc_text"] = ""
if load_tr_sample:
    st.session_state["doc_text"] = TELECOM_REIT_SAMPLE_DOCUMENT
if load_lease:
    st.session_state["doc_text"] = _load_lease_docs()

# Text area bound to session state
doc_text = st.text_area(
    "Paste your document text here",
    value=st.session_state["doc_text"],
    height=250,
    placeholder="Paste a tower inspection report, contract, medical record, or financial document...",
)
# Sync back
st.session_state["doc_text"] = doc_text

st.metric("Characters", len(doc_text))

# Extract button
extract_clicked = st.button(
    "⚡ Extract Entities",
    type="primary",
    width="stretch",
    disabled=(len(doc_text.strip()) == 0),
)

# ── Run extraction ──
if extract_clicked and doc_text.strip():
    with st.spinner("🔄 Running MoE extraction pipeline..."):
        result = run_extraction(doc_text, use_llm, model, confidence,
                                hallucination_mode=halluc_mode_key,
                                adaptive=use_adaptive)

    # Also run Telecom REIT pipeline if that expert is enabled
    if TELECOM_REIT_AVAILABLE and "TelecomREITReconciliationExpert" in enabled_experts:
        with st.spinner("🏗️ Running Telecom REIT reconciliation pipeline..."):
            tr_pipeline = TelecomREITPipeline()
            tr_result = tr_pipeline.run_pipeline(verbose=False)
            st.session_state["tr_result"] = tr_result

    st.session_state["last_result"] = result

# ── Show results ──
if st.session_state["last_result"]:
    result = st.session_state["last_result"]
    entities = result["entities"]
    relationships = result["relationships"]

    st.divider()

    # Metric cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Entities", result["total_entities"])
    m2.metric("Relationships", result["total_relationships"])
    m3.metric("Processing", f"{result['processing_time_ms']}ms")
    m4.metric("Engine", result["engine"])

    st.divider()

    # Tabs
    tab_table, tab_graph, tab_recon, tab_invoice, tab_trace = st.tabs([
        "📊 Entity Table", "🕸️ Graph Preview", "🏗️ Reconciliation",
        "💰 Invoice Recon", "📋 Pipeline Trace"
    ])

    # ─── Entity Table ────────────────────────────────────────────────
    with tab_table:
        if entities:
            import pandas as pd
            df = pd.DataFrame([
                {
                    "Entity": e["name"],
                    "Type": e["type"],
                    "Confidence": e["confidence"],
                    "Expert": e["source_expert"],
                    "Properties": json.dumps(e.get("properties", {}), default=str)[:80],
                }
                for e in entities
            ])
            df = df.sort_values("Confidence", ascending=False).reset_index(drop=True)

            st.dataframe(
                df,
                column_config={
                    "Confidence": st.column_config.ProgressColumn(
                        "Confidence", min_value=0.0, max_value=1.0, format="%.2f",
                    ),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Expert": st.column_config.TextColumn("Expert", width="medium"),
                },
                width="stretch",
                hide_index=True,
            )

            # Download
            st.download_button(
                "📥 Download CSV",
                df.to_csv(index=False),
                "ecl_entities.csv",
                "text/csv",
            )
        else:
            st.info("No entities extracted above confidence threshold.")

    # ─── Graph Preview ───────────────────────────────────────────────
    with tab_graph:
        if entities:
            try:
                from streamlit_agraph import agraph, Node, Edge, Config

                colors = {
                    "ASSET": "#3b82f6", "ORGANIZATION": "#8b5cf6",
                    "CONTRACT": "#f59e0b", "MONETARY": "#10b981",
                    "EQUIPMENT": "#6366f1", "RISK": "#f87171",
                    "OPPORTUNITY": "#f97316", "PERSON": "#ec4899",
                    "TOWER": "#3b82f6", "FINANCIAL_METRIC": "#10b981",
                }

                nodes = []
                seen = set()
                for ent in entities:
                    name = ent["name"]
                    etype = ent["type"]
                    if name not in seen:
                        nodes.append(Node(
                            id=name, label=name, size=25,
                            color=colors.get(etype, "#64748b"),
                            font={"color": "#e2e8f0", "size": 14},
                        ))
                        seen.add(name)

                edges = []
                for rel in relationships:
                    src_name = next((e["name"] for e in entities if e["id"] == rel["source"]), rel["source"])
                    tgt_name = next((e["name"] for e in entities if e["id"] == rel["target"]), rel["target"])
                    if src_name in seen and tgt_name in seen:
                        edges.append(Edge(
                            source=src_name, target=tgt_name,
                            label=rel.get("type", ""), color="#475569",
                        ))

                config = Config(
                    width=900, height=400, directed=True,
                    physics=True, hierarchical=False,
                    nodeHighlightBehavior=True, highlightColor="#f59e0b",
                )

                agraph(nodes=nodes, edges=edges, config=config)

            except ImportError:
                st.warning("Install `streamlit-agraph` for graph visualization.")
        else:
            st.info("Run an extraction to see the graph.")

    # ─── Reconciliation Dashboard ────────────────────────────────────
    with tab_recon:
        tr_result = st.session_state.get("tr_result")
        if tr_result and TELECOM_REIT_AVAILABLE:
            st.markdown("### 🏗️ Tower Reconciliation Dashboard")
            st.caption("Cross-source reconciliation: Contract vs Drone vs Billing")

            three_way = tr_result.linkage_result.three_way

            # Tower health scorecard
            if three_way:
                st.markdown("#### Tower Health Scorecard")
                health_cols = st.columns(len(three_way))
                for i, tw in enumerate(three_way):
                    health = tw["overall_tower_health"]
                    icon = "🟢" if health == "CLEAN" else "🟡" if health == "ATTENTION" else "🔴"
                    with health_cols[i]:
                        st.metric(
                            f"{icon} {tw['tower_id']}",
                            health,
                            f"${tw['total_monthly_rent']:,.0f}/mo"
                        )

                st.divider()

                # Reconciliation table
                st.markdown("#### Equipment Reconciliation")
                import pandas as pd
                recon_data = []
                for tw in three_way:
                    recon_data.append({
                        "Tower": tw["tower_id"],
                        "Contracted Equip": tw["total_contracted_equipment"],
                        "Detected (Drone)": tw["total_detected_equipment"],
                        "Delta": tw["total_detected_equipment"] - tw["total_contracted_equipment"],
                        "Physical Status": tw["physical_reconciliation_status"],
                        "Financial Status": tw["financial_reconciliation_status"],
                        "Monthly Rent": f"${tw['total_monthly_rent']:,.0f}",
                        "Monthly Billed": f"${tw['total_monthly_billed']:,.0f}",
                        "Health": tw["overall_tower_health"],
                    })
                recon_df = pd.DataFrame(recon_data)
                st.dataframe(recon_df, width="stretch", hide_index=True)

                st.divider()

                # Linkage findings
                st.markdown("#### Linkage Findings")
                linkages = tr_result.linkage_result.all_linkages
                non_matched = [l for l in linkages if l.linkage_type.value != "matched"]
                if non_matched:
                    for link in non_matched:
                        sev_icon = "🔴" if link.severity == "HIGH" else "🟡" if link.severity == "MEDIUM" else "🟢"
                        with st.expander(
                            f"{sev_icon} [{link.severity}] {link.linkage_type.value} — "
                            f"{link.source_entity.attributes.get('tower_id', '')}",
                            expanded=(link.severity == "HIGH"),
                        ):
                            st.markdown(f"**Type:** `{link.linkage_type.value}`")
                            st.markdown(f"**Severity:** {link.severity}")
                            st.markdown(f"**Confidence:** {link.confidence:.2f}")
                            if link.recommended_action:
                                st.markdown(f"**Action:** {link.recommended_action}")
                            if link.revenue_impact:
                                st.markdown(f"**Revenue Impact:** ${link.revenue_impact:,.0f}/yr")
                            st.json(link.delta)
                else:
                    st.success("All towers fully reconciled — no discrepancies found.")

                # Revenue impact summary
                total_impact = tr_result.linkage_result.total_revenue_impact
                if total_impact != 0:
                    st.divider()
                    st.markdown("#### Revenue Impact Summary")
                    st.metric("Total Revenue Impact", f"${total_impact:,.0f}/yr")
                    st.metric("HIGH Severity Issues", tr_result.linkage_result.high_severity_count)
        else:
            if TELECOM_REIT_AVAILABLE:
                st.info("Enable the 🏗️ TelecomREITReconciliationExpert and run an extraction to see reconciliation data.")
            else:
                st.warning("Telecom REIT module not available. Check the telecom_reit package installation.")

    # ─── Invoice Reconciliation ──────────────────────────────────────
    with tab_invoice:
        if RECON_AVAILABLE:
            from reconcile_contracts import load_audits

            # ── Executive Context ──────────────────────────────────
            st.markdown("### 💰 Tower Lease Reconciliation — Agentic AI Demo")

            st.info(
                "🎯 **SIMULATED DATA — DEMO MODE**\n\n"
                "This reconciliation runs against **realistic but synthetic data** generated to mirror "
                "Summit's portfolio (~40,000 towers, $3.9B revenue). The contract structures, "
                "escalation clauses, tenant configurations, and discrepancy patterns are modeled on "
                "publicly available Summit lease terms and industry benchmarks.\n\n"
                "In production, this engine would connect to live ERP (Oracle/SAP), lease management "
                "(MRI/Yardi), 5x5 digital twin feeds, and county tax databases via ECL connectors."
            )

            with st.expander("📊 **Why This Matters — The Summit Opportunity**", expanded=False):
                st.markdown("""
**$3.9B revenue** · **~40,000 towers** · **DISH $220M churn hole** · **Zayo fiber divestiture in progress**

Industry data shows **2–5% revenue leakage** from unbilled co-locations, missed escalations, and
billing errors. At Summit's scale, even **1% recovery = ~$39M annually**.

| # | Reconciliation Pattern | Est. Annual Impact | Automation |
|---|---|---|---|
| 1 | Unauthorized co-locations (physical vs contracted) | $39M–$195M | High (drone + AI) |
| 2 | Escalation errors (contract vs invoice math) | $10M–$50M | Very High |
| 3 | DISH default cleanup ($3.5B recovery) | $220M churn | Medium |
| 4 | Revenue sharing miscalculations | $5M–$20M | Very High |
| 5 | Post-divestiture migration errors | $5M–$15M | High |

**This demo shows how ECL's entity extraction + agentic reconciliation can automate these checks.**
                """)

            with st.expander("🔗 **9 Cross-Reference Patterns We Demonstrate**", expanded=False):
                st.markdown("""
| UC | Cross-Reference | Data Sources | What It Catches |
|---|---|---|---|
| UC1 | Physical Inventory ↔ Tenant Contract | Digital twin ↔ Lease mgmt | Unbilled antennas, zombie tenants |
| UC2 | Physical Inventory ↔ Invoice Lines | Digital twin ↔ Billing | Sector underbilling, power pass-through |
| UC3 | RF Design ↔ Physical As-Built | Engineering ↔ Digital twin | Tilt/azimuth drift, model mismatches |
| UC4 | Structural Load ↔ Actual | Bentley iQ ↔ Digital twin | Over-capacity, undersold towers |
| UC5 | Escalation ↔ Invoice History | Lease mgmt ↔ Billing | CPI errors, missed escalations |
| UC6 | Mod Apps ↔ Physical ↔ Invoice | Workflow ↔ Twin ↔ Billing | Billing not updated after mods |
| UC7 | Rev-Share ↔ Tenant Revenue | Ground lease ↔ Billing | Formula errors, Zayo carveout |
| UC8 | Site Access ↔ Mod Apps | Field ops ↔ Workflow | Unauthorized site access |
| UC9 | Tax Assessment ↔ Pass-Through | County records ↔ Billing | Tax not passed through |
                """)

            st.divider()

            # ── Run Button ─────────────────────────────────────────
            if st.button("🔄 Run 9-Way Cross-Reference Reconciliation", key="run_recon"):
                with st.spinner("Reconciling 8 data sources across 9 cross-reference patterns..."):
                    recon_result = reconcile()
                    st.session_state["recon_result"] = recon_result

            recon_result = st.session_state.get("recon_result")
            if recon_result:
                st.markdown("---")
                st.markdown("#### 📈 Reconciliation Results")
                st.caption(
                    f"⚠️ Simulated: {recon_result.total_contracts:,} contracts · "
                    f"{recon_result.total_invoices:,} invoices · "
                    f"{recon_result.total_audits:,} audits · "
                    f"{recon_result.total_rf_specs:,} RF · "
                    f"{recon_result.total_structural:,} structural · "
                    f"{recon_result.total_mod_apps:,} mods · "
                    f"{recon_result.total_access_logs:,} access · "
                    f"{recon_result.total_tax_records:,} tax"
                )

                # Row 1: headline metrics
                rc1, rc2, rc3, rc4, rc5 = st.columns(5)
                rc1.metric("Discrepancies", f"{recon_result.total_discrepancies:,}",
                          delta=f"{recon_result.critical_count} critical", delta_color="inverse")
                rc2.metric("Est. Annual Impact", f"${recon_result.est_total_annual_impact:,.0f}")
                rc3.metric("Net Invoice Delta", f"${recon_result.total_delta:+,.0f}")
                rc4.metric("Matched / Total", f"{recon_result.matched_contracts}/{recon_result.total_contracts}")
                rc5.metric("Unbilled", f"{len(recon_result.unbilled_contracts)}")

                # Row 2: DISH + Deadlines
                if recon_result.dish_active_count > 0 or recon_result.contracts_expiring_soon > 0:
                    dc1, dc2, dc3, dc4 = st.columns(4)
                    dc1.metric("📡 DISH Contracts", recon_result.dish_active_count)
                    dc2.metric("📡 DISH Defaulted", recon_result.dish_defaulted_count)
                    dc3.metric("⏰ Expiring Soon", recon_result.contracts_expiring_soon)
                    dc4.metric("⏰ Auto-Renewed", recon_result.auto_renewal_risk)

                # Row 3: Undersold + structural
                if hasattr(recon_result, 'undersold_towers') and recon_result.undersold_towers > 0:
                    uc1, uc2 = st.columns(2)
                    uc1.metric("🏗️ Undersold Towers", recon_result.undersold_towers)
                    uc2.metric("🏗️ Monthly Opportunity", f"${recon_result.undersold_monthly_opportunity:,.0f}")

                st.divider()

                import plotly.express as px

                # Category breakdown
                if recon_result.summary_by_category:
                    ch1, ch2 = st.columns(2)
                    with ch1:
                        cat_data = [{"Category": k, "Count": v} for k, v in
                                    sorted(recon_result.summary_by_category.items(), key=lambda x: -x[1])]
                        fig = px.pie(cat_data, values="Count", names="Category",
                                    title="By Category",
                                    color_discrete_sequence=["#f87171", "#f59e0b", "#3b82f6",
                                                              "#8b5cf6", "#10b981", "#ec4899"])
                        fig.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            font_color="#e2e8f0", height=300,
                        )
                        st.plotly_chart(fig, width="stretch")

                    with ch2:
                        type_data = [{"Type": k, "Count": v} for k, v in
                                     sorted(recon_result.summary_by_type.items(), key=lambda x: -x[1])[:10]]
                        fig2 = px.bar(type_data, x="Type", y="Count", color="Type",
                                     title="Top 10 Discrepancy Types",
                                     color_discrete_sequence=["#f87171", "#f59e0b", "#3b82f6",
                                                               "#8b5cf6", "#10b981", "#ec4899",
                                                               "#6366f1", "#14b8a6", "#f43f5e", "#a855f7"])
                        fig2.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            font_color="#e2e8f0", showlegend=False, height=300,
                        )
                        st.plotly_chart(fig2, width="stretch")

                # Filters — 4 columns for UC/severity/category/type
                fc1, fc2, fc3, fc4 = st.columns(4)
                with fc1:
                    uc_choices = list(recon_result.summary_by_use_case.keys()) if hasattr(recon_result, 'summary_by_use_case') else []
                    uc_filter = st.multiselect(
                        "Use Case", uc_choices, default=uc_choices, key="uc_filter")
                with fc2:
                    sev_filter = st.multiselect(
                        "Severity", ["🔴 Critical", "🟡 Warning", "🟢 Info"],
                        default=["🔴 Critical", "🟡 Warning"], key="sev_filter")
                with fc3:
                    cat_choices = list(recon_result.summary_by_category.keys())
                    cat_filter = st.multiselect(
                        "Category", cat_choices, default=cat_choices, key="cat_filter")
                with fc4:
                    type_choices = list(recon_result.summary_by_type.keys())
                    type_filter = st.multiselect(
                        "Type", type_choices, default=type_choices, key="type_filter")

                # Discrepancy table
                import pandas as pd
                filtered = [d for d in recon_result.discrepancies
                           if d.severity in sev_filter
                           and d.category in cat_filter
                           and d.disc_type in type_filter
                           and (not uc_filter or d.use_case in uc_filter)]

                if filtered:
                    df = pd.DataFrame([{
                        "UC": d.use_case,
                        "Sev": d.severity,
                        "Category": d.category,
                        "Type": d.disc_type,
                        "Contract": d.contract_id or "—",
                        "Tower": d.tower_id,
                        "Invoice": d.invoice_id or "—",
                        "Period": d.billing_period or "—",
                        "Invoiced": f"${d.invoiced_amount:,.2f}" if d.invoiced_amount else "—",
                        "Expected": f"${d.contract_amount:,.2f}" if d.contract_amount else "—",
                        "Delta": f"${d.delta:+,.2f}" if d.delta else "—",
                        "Impact/yr": f"${d.est_annual_impact:,.0f}" if d.est_annual_impact else "—",
                        "Description": d.description,
                    } for d in filtered[:200]])

                    st.dataframe(df, width="stretch", height=400)
                    st.caption(f"Showing {len(df)} of {len(filtered)} discrepancies")

                    st.download_button(
                        "📥 Download Full Report CSV",
                        pd.DataFrame([{
                            "severity": d.severity, "category": d.category,
                            "type": d.disc_type, "contract_id": d.contract_id,
                            "tower_id": d.tower_id, "invoice_id": d.invoice_id,
                            "period": d.billing_period, "invoiced": d.invoiced_amount,
                            "expected": d.contract_amount, "delta": d.delta,
                            "est_annual_impact": d.est_annual_impact,
                            "description": d.description,
                        } for d in recon_result.discrepancies]).to_csv(index=False),
                        "reconciliation_report.csv", "text/csv",
                    )
                else:
                    st.success("No discrepancies match the selected filters.")
            else:
                st.info("Click **Run Full Reconciliation** to match contracts against ERP invoices and tower audits — covering all 8 reconciliation use cases.")
        else:
            st.warning("Reconciliation module not available. Ensure `reconcile_contracts.py` is present.")

    # ─── Pipeline Trace ──────────────────────────────────────────────
    with tab_trace:
        st.markdown(f"**Pipeline completed in `{result['processing_time_ms']}ms`**")

        expert_results = result.get("expert_results", {})
        for exp_name, stats in expert_results.items():
            with st.expander(
                f"{'🟢' if stats['entities'] > 0 else '⚪'} {exp_name} — "
                f"{stats['entities']} entities, {stats['relationships']} rels",
                expanded=(stats['entities'] > 0),
            ):
                st.markdown(f"- **Entities**: {stats['entities']}")
                st.markdown(f"- **Relationships**: {stats['relationships']}")
                st.markdown(f"- **Reasoning**: {stats['reasoning']}")

        # Expert breakdown chart
        if expert_results:
            st.divider()
            st.markdown("#### Expert Breakdown")
            import plotly.express as px
            exp_data = [
                {"Expert": k, "Entities": v["entities"], "Relationships": v["relationships"]}
                for k, v in expert_results.items()
            ]
            fig = px.bar(
                exp_data, x="Expert", y="Entities", color="Expert",
                color_discrete_sequence=["#6366f1", "#3b82f6", "#10b981", "#f59e0b", "#f87171"],
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                showlegend=False, height=300,
            )
            st.plotly_chart(fig, width="stretch")

    # ── Raw JSON ──
    st.divider()
    with st.expander("📥 Raw JSON Output"):
        st.json(result)
