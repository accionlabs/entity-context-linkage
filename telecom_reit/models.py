"""
Telecom REIT ECL Models
========================
Domain-specific data models for the Telecom REIT ECL platform.
Defines entity sources, entity types, linkage types, and the core
Entity / Context / Linkage dataclasses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


# ─── Entity Sources ───

class EntitySource(Enum):
    """Where entities are extracted from."""
    CONTRACT_PDF = "contract_pdf"
    DRONE_IMAGE = "drone_image"
    DRONE_JSON = "drone_json"
    ORACLE_TX = "oracle_transactional"
    ORACLE_GEO = "oracle_geospatial"
    JDE_ERP = "jde_erp"
    SERVICENOW = "servicenow"
    SITE_TRACKER = "sitetracker"
    CCISITES = "tower_sites_db"
    DIGITAL_TWIN = "3d_model"
    MERCURY = "mercury_demand"
    SURVEY123 = "survey123"


# ─── Entity Types ───

class EntityType(Enum):
    """Types of entities in the Telecom REIT domain."""
    TOWER = "tower"
    TENANT = "tenant"
    EQUIPMENT = "equipment"
    LEASE = "lease"
    WORK_ORDER = "work_order"
    INSPECTION = "inspection"
    BILLING_RECORD = "billing_record"
    GROUND_LEASE = "ground_lease"
    AMENDMENT = "amendment"
    REGULATORY_EVENT = "regulatory_event"


# ─── Linkage Types ───

class LinkageType(Enum):
    """Types of cross-source linkages discovered by ECL."""
    # Reconciliation links
    CONTRACT_VS_OBSERVED = "contract_vs_observed"
    BILLED_VS_CONTRACTED = "billed_vs_contracted"
    OBSERVED_VS_BILLED = "observed_vs_billed"
    # Revenue links
    UPSELL_OPPORTUNITY = "upsell_opportunity"
    CHURN_RISK = "churn_risk"
    AMENDMENT_CANDIDATE = "amendment_candidate"
    # Compliance links
    UNAUTHORIZED_EQUIPMENT = "unauthorized_equipment"
    MISSING_EQUIPMENT = "missing_equipment"
    FAA_NONCOMPLIANT = "faa_noncompliant"
    STRUCTURAL_OVERLOAD = "structural_overload"
    # Operational links
    DEFAULTED_EQUIPMENT = "defaulted_equipment"
    EXCESS_EQUIPMENT = "excess_equipment"
    DEFICIT_EQUIPMENT = "deficit_equipment"
    MATCHED = "matched"


# ─── Core Dataclasses ───

@dataclass
class Entity:
    """Core ECL entity — extracted from any source."""
    entity_id: str
    entity_type: EntityType
    source: EntitySource
    attributes: Dict[str, Any]
    confidence: float = 1.0
    extracted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    raw_reference: Optional[str] = None


@dataclass
class Context:
    """Assembled context around an entity — merges multiple sources."""
    context_id: str
    primary_entity: Entity
    related_entities: List[Entity] = field(default_factory=list)
    temporal_context: Dict[str, Any] = field(default_factory=dict)
    spatial_context: Dict[str, Any] = field(default_factory=dict)
    financial_context: Dict[str, Any] = field(default_factory=dict)
    operational_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Linkage:
    """Cross-source link — the discovery output of ECL."""
    linkage_id: str
    linkage_type: LinkageType
    source_entity: Entity
    target_entity: Entity
    delta: Dict[str, Any]
    severity: str  # HIGH / MEDIUM / LOW
    confidence: float
    revenue_impact: Optional[float] = None
    recommended_action: Optional[str] = None
    evidence: List[str] = field(default_factory=list)


# ─── Equipment Type Mapping ───

EQUIPMENT_TYPE_MAP = {
    # contract_type → (normalized_type, category)
    "panel_antenna":  ("panel_antenna",  "ANTENNA"),
    "antenna":        ("panel_antenna",  "ANTENNA"),
    "rru":            ("rru",            "RADIO"),
    "remote_radio":   ("rru",            "RADIO"),
    "microwave_dish": ("microwave_dish", "MICROWAVE"),
    "dish":           ("microwave_dish", "MICROWAVE"),
    "cabinet":        ("cabinet",        "GROUND_EQUIPMENT"),
    "cable_tray":     ("cable_tray",     "CABLING"),
    "coax_run":       ("cable_tray",     "CABLING"),
    "generator":      ("generator",      "POWER"),
    "meter":          ("meter",          "POWER"),
    "ice_bridge":     ("ice_bridge",     "STRUCTURE"),
}


# ─── Contract Extraction Prompt (for Databricks ai_query) ───

CONTRACT_EXTRACTION_PROMPT = """
You are an expert telecom lease analyst. Extract structured data from this
tower lease document. Return ONLY valid JSON matching this schema:

{
  "tower_id": "string — site ID (e.g., 'TR-4521')",
  "tenant_name": "string — carrier or tenant name",
  "lease_type": "ground_lease | carrier_lease | amendment | sublease",
  "equipment_manifest": [
    {
      "type": "panel_antenna | rru | microwave_dish | cabinet | cable_tray |
               generator | meter | ice_bridge | coax_run | fiber_run",
      "model": "string or null",
      "quantity": integer,
      "rad_center_height_ft": float or null,
      "sector": "string — A/B/C/alpha/beta/gamma or null",
      "mounting_type": "face_mount | standoff | side_arm | platform | ground",
      "dimensions_inches": "LxWxD or null",
      "weight_lbs": float or null
    }
  ],
  "financial_terms": {
    "monthly_rent": decimal,
    "annual_escalator_pct": decimal,
    "escalator_type": "fixed | cpi | hybrid",
    "commencement_date": "YYYY-MM-DD",
    "expiration_date": "YYYY-MM-DD",
    "renewal_terms": "string — number and length of renewal options"
  },
  "amendments": [
    {
      "amendment_number": integer,
      "effective_date": "YYYY-MM-DD",
      "summary": "string — what changed",
      "rent_adjustment": decimal or null
    }
  ],
  "special_conditions": ["string — non-standard clauses"],
  "structural_requirements": {
    "max_vertical_load_lbs": float or null,
    "max_horizontal_load_sqft": float or null,
    "ice_loading_requirement": "string or null"
  }
}

If a field cannot be determined, use null. Never guess.
"""
