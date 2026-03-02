
# =============================================================================
# Summit AI PLATFORM — ECL-POWERED RECONCILIATION & BEYOND
# =============================================================================
# Maps to: 6-Paradigm Vision Doc + Lyzr Replacement Scope + Contract-Drone MVP
# Architecture: AWS Glue (ingestion) → Databricks (AI/ML) → Snowflake (serving)
# Core Pattern: Entity-Context-Linkage (ECL) as the unifying intelligence layer
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 0: ECL FRAMEWORK — The Engine That Powers Everything
# ─────────────────────────────────────────────────────────────────────────────
#
# Entity-Context-Linkage (ECL) is the 3-step pattern that replaces Lyzr:
#   E → Extract entities from ANY source (PDF, drone image, Oracle, JSON)
#   C → Build context around each entity (history, relationships, attributes)
#   L → Link entities across sources to discover gaps, opportunities, risks
#
# For Contract-Drone Reconciliation:
#   E: Lease PDF → [tower_id, tenant, equipment, rent, escalator]
#      Drone Image → [tower_id, detected_equipment, position, confidence]
#      Oracle/JDE → [tower_id, billing, GL codes, work orders]
#   C: Each tower gets a unified context: what SHOULD be there (contract),
#      what IS there (drone), what we're BILLING for (ERP)
#   L: Cross-source linkage reveals: unauthorized equipment, missing equipment,
#      billing errors, DISH default equipment still on towers, upsell targets
#
# This same ECL pattern scales to ALL 6 paradigms in the vision doc.
# ─────────────────────────────────────────────────────────────────────────────


# =============================================================================
# MODULE 1: ECL CORE — Entity Extraction, Context Assembly, Linkage Engine
# =============================================================================

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json
from datetime import datetime


# ─── Entity Types ───

class EntitySource(Enum):
    CONTRACT_PDF = "contract_pdf"
    DRONE_IMAGE = "drone_image"
    DRONE_JSON = "drone_json"       # PRSW JSON already in Snowflake
    ORACLE_TX = "oracle_transactional"
    ORACLE_GEO = "oracle_geospatial"
    JDE_ERP = "jde_erp"
    SERVICENOW = "servicenow"
    SITE_TRACKER = "sitetracker"
    CCISITES = "ccisites"
    DIGITAL_TWIN_5x5 = "5x5_3d_model"
    MERCURY = "mercury_demand"
    SURVEY123 = "survey123"


class EntityType(Enum):
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


class LinkageType(Enum):
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
    # Knowledge links
    TRIBAL_KNOWLEDGE = "tribal_knowledge"
    DECISION_PRECEDENT = "decision_precedent"


@dataclass
class Entity:
    """Core ECL entity — extracted from any source."""
    entity_id: str
    entity_type: EntityType
    source: EntitySource
    attributes: Dict[str, Any]
    confidence: float = 1.0
    extracted_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    raw_reference: Optional[str] = None  # S3 path, DB row ref, image path


@dataclass
class Context:
    """Assembled context around an entity — merges multiple sources."""
    context_id: str
    primary_entity: Entity
    related_entities: List[Entity] = field(default_factory=list)
    temporal_context: Dict[str, Any] = field(default_factory=dict)  # history
    spatial_context: Dict[str, Any] = field(default_factory=dict)   # location/geo
    financial_context: Dict[str, Any] = field(default_factory=dict) # billing/rent
    operational_context: Dict[str, Any] = field(default_factory=dict) # WOs, inspections


@dataclass
class Linkage:
    """Cross-source link — the discovery output of ECL."""
    linkage_id: str
    linkage_type: LinkageType
    source_entity: Entity
    target_entity: Entity
    delta: Dict[str, Any]  # what's different
    severity: str  # HIGH / MEDIUM / LOW
    confidence: float
    revenue_impact: Optional[float] = None
    recommended_action: Optional[str] = None
    evidence: List[str] = field(default_factory=list)  # S3 paths, doc refs


# =============================================================================
# MODULE 2: ENTITY EXTRACTION — Replaces Lyzr's Scope
# =============================================================================
# Covers all 6 Lyzr success criteria:
#   1. Agentic Platform Capabilities → Multi-agent extraction squad
#   2. Architecture & Integration → Plugs into CCI's Oracle/AWS/Snowflake
#   3. Security & Data Controls → Runs in VPC, Unity Catalog governance
#   4. Explainability & Auditability → Every extraction logged with confidence
#   5. Performance & Throughput → Batch (Glue) + streaming (Databricks)
#   6. Enterprise Readiness → MLflow model registry, Delta Lake ACID
# =============================================================================


# ─── 2A: Contract PDF Extraction (Lyzr's primary use case) ───

# Databricks notebook cell
CONTRACT_EXTRACTION_PROMPT = """
You are an expert telecom lease analyst. Extract structured data from this
tower lease document. Return ONLY valid JSON matching this schema:

{
  "tower_id": "string — CCI site ID (e.g., 'CCI-TX-12345')",
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

# --- Databricks Pipeline: Contract Extraction ---

def extract_contracts_pipeline():
    """
    Reads Glue-landed contract PDFs from S3 Bronze,
    parses with ai_parse_document, extracts with ai_query.
    """
    # Read from Glue-cataloged bronze (S3)
    raw_contracts = spark.read.format("binaryFile").load(
        "s3://cci-data-lake/bronze/contracts/"
    )

    # Step E1: Parse PDF → text/markdown
    parsed = raw_contracts.selectExpr(
        "path AS file_path",
        "ai_parse_document(content, 'text') AS parsed_text"
    )

    # Step E2: LLM extraction → structured JSON
    from pyspark.sql import functions as F

    extracted = parsed.withColumn(
        "extracted_json",
        F.expr(f"""
            ai_query(
                'databricks-meta-llama-3-3-70b-instruct',
                CONCAT('{CONTRACT_EXTRACTION_PROMPT}', '\n\nDOCUMENT:\n', parsed_text)
            )
        """)
    )

    # Step E3: Parse JSON → typed columns
    from pyspark.sql.types import *

    equipment_schema = ArrayType(StructType([
        StructField("type", StringType()),
        StructField("model", StringType()),
        StructField("quantity", IntegerType()),
        StructField("rad_center_height_ft", FloatType()),
        StructField("sector", StringType()),
        StructField("mounting_type", StringType()),
        StructField("dimensions_inches", StringType()),
        StructField("weight_lbs", FloatType()),
    ]))

    contract_entities = (
        extracted
        .withColumn("data", F.from_json("extracted_json", schema="""
            tower_id STRING,
            tenant_name STRING,
            lease_type STRING,
            equipment_manifest ARRAY<STRUCT<
                type: STRING, model: STRING, quantity: INT,
                rad_center_height_ft: FLOAT, sector: STRING,
                mounting_type: STRING, dimensions_inches: STRING,
                weight_lbs: FLOAT
            >>,
            financial_terms STRUCT<
                monthly_rent: DECIMAL(12,2),
                annual_escalator_pct: DECIMAL(5,4),
                escalator_type: STRING,
                commencement_date: DATE,
                expiration_date: DATE,
                renewal_terms: STRING
            >,
            amendments ARRAY<STRUCT<
                amendment_number: INT,
                effective_date: DATE,
                summary: STRING,
                rent_adjustment: DECIMAL(12,2)
            >>,
            special_conditions ARRAY<STRING>,
            structural_requirements STRUCT<
                max_vertical_load_lbs: FLOAT,
                max_horizontal_load_sqft: FLOAT,
                ice_loading_requirement: STRING
            >
        """))
        .select("file_path", "data.*")
        .withColumn("extraction_confidence", F.lit(0.85))
        .withColumn("source", F.lit(EntitySource.CONTRACT_PDF.value))
        .withColumn("extracted_at", F.current_timestamp())
    )

    contract_entities.write.mode("overwrite").saveAsTable(
        "crown_castle.ecl.contract_entities"
    )

    # Explode equipment for per-item reconciliation
    (contract_entities
        .select("tower_id", "tenant_name", "lease_type",
                F.explode("equipment_manifest").alias("equip"),
                "financial_terms", "source", "extracted_at")
        .select("tower_id", "tenant_name", "lease_type",
                "equip.*", "financial_terms.*", "source", "extracted_at")
        .write.mode("overwrite")
        .saveAsTable("crown_castle.ecl.contract_equipment")
    )

    return contract_entities


# ─── 2B: Drone Data Extraction ───

def extract_drone_entities():
    """
    Two paths:
    1. PRSW JSON already in Snowflake → read via Lakehouse Federation
    2. Drone images in S3 → CV classification in Databricks
    """

    # Path 1: Read PRSW JSON from Snowflake (already ingested per ACES deck)
    prsw_data = (
        spark.read
        .format("snowflake")
        .options(**{
            "sfUrl": "crown_castle.snowflakecomputing.com",
            "sfDatabase": "TOWER_DWH",
            "sfSchema": "DRONE_DATA",
            "sfWarehouse": "ANALYTICS_WH",
            "dbtable": "PRSW_JSON_PAYLOAD"
        })
        .load()
    )

    # Normalize PRSW JSON to equipment detections
    from pyspark.sql import functions as F

    drone_structured = (
        prsw_data
        .withColumn("tower_id", F.col("site_id"))
        .withColumn("detected_equipment", F.from_json(
            F.col("equipment_payload"),
            "ARRAY<STRUCT<type: STRING, confidence: FLOAT, "
            "position_height_ft: FLOAT, sector: STRING, "
            "bounding_box: STRING, image_ref: STRING>>"
        ))
        .select("tower_id", F.explode("detected_equipment").alias("det"))
        .select(
            "tower_id",
            F.col("det.type").alias("detected_type"),
            F.col("det.confidence"),
            F.col("det.position_height_ft"),
            F.col("det.sector"),
            F.col("det.bounding_box"),
            F.col("det.image_ref"),
        )
        .withColumn("source", F.lit(EntitySource.DRONE_JSON.value))
        .withColumn("extracted_at", F.current_timestamp())
    )

    drone_structured.write.mode("overwrite").saveAsTable(
        "crown_castle.ecl.drone_equipment_prsw"
    )

    # Path 2: CV classification on raw drone images (for imagery not yet in PRSW)
    raw_images = spark.read.format("binaryFile").load(
        "s3://cci-data-lake/bronze/drone-captures/"
    )

    # Classify using registered MLflow model
    drone_cv = raw_images.selectExpr(
        "path AS image_path",
        "regexp_extract(path, '.*/([A-Z0-9-]+)/[^/]+$', 1) AS tower_id",
        """ai_query(
            'crown_castle.ecl.tower_equipment_classifier',
            content
        ) AS classification"""
    ).withColumn("source", F.lit(EntitySource.DRONE_IMAGE.value))

    drone_cv.write.mode("overwrite").saveAsTable(
        "crown_castle.ecl.drone_equipment_cv"
    )

    # Merge both drone sources
    spark.sql("""
        CREATE OR REPLACE TABLE crown_castle.ecl.drone_equipment AS
        SELECT tower_id, detected_type, confidence,
               position_height_ft, sector, source, extracted_at
        FROM crown_castle.ecl.drone_equipment_prsw
        UNION ALL
        SELECT tower_id,
               classification.predicted_type AS detected_type,
               classification.confidence,
               NULL AS position_height_ft,
               NULL AS sector,
               source, current_timestamp() AS extracted_at
        FROM crown_castle.ecl.drone_equipment_cv
    """)


# ─── 2C: ERP/Operational Extraction (Oracle, JDE, ServiceNow) ───

def extract_operational_entities():
    """
    Read from Glue-cataloged operational data (already replicated via Golden Gate).
    """
    from pyspark.sql import functions as F

    # Oracle Transactional — billing records
    billing = (
        spark.read.format("parquet")
        .load("s3://cci-data-lake/bronze/oracle-tx/billing/")
        .select(
            F.col("SITE_ID").alias("tower_id"),
            F.col("TENANT_ID").alias("tenant_id"),
            F.col("TENANT_NAME").alias("tenant_name"),
            F.col("MONTHLY_BILLED_AMT").alias("billed_amount"),
            F.col("BILLING_PERIOD").alias("billing_period"),
            F.col("EQUIPMENT_COUNT").alias("billed_equipment_count"),
        )
        .withColumn("source", F.lit(EntitySource.ORACLE_TX.value))
    )
    billing.write.mode("overwrite").saveAsTable(
        "crown_castle.ecl.billing_entities"
    )

    # JDE ERP — GL data, work orders
    work_orders = (
        spark.read.format("parquet")
        .load("s3://cci-data-lake/bronze/jde/work-orders/")
        .select(
            F.col("SITE_NUMBER").alias("tower_id"),
            F.col("WO_NUMBER").alias("work_order_id"),
            F.col("WO_TYPE").alias("wo_type"),
            F.col("STATUS").alias("wo_status"),
            F.col("CREATED_DATE").alias("created_date"),
            F.col("COMPLETED_DATE").alias("completed_date"),
            F.col("COST").alias("wo_cost"),
        )
        .withColumn("source", F.lit(EntitySource.JDE_ERP.value))
    )
    work_orders.write.mode("overwrite").saveAsTable(
        "crown_castle.ecl.work_order_entities"
    )

    # ServiceNow — field service / inspections
    inspections = (
        spark.read.format("parquet")
        .load("s3://cci-data-lake/bronze/servicenow/inspections/")
        .select(
            F.col("site_id").alias("tower_id"),
            F.col("inspection_id"),
            F.col("inspection_type"),
            F.col("inspection_date"),
            F.col("findings"),
            F.col("inspector"),
        )
        .withColumn("source", F.lit(EntitySource.SERVICENOW.value))
    )
    inspections.write.mode("overwrite").saveAsTable(
        "crown_castle.ecl.inspection_entities"
    )


# =============================================================================
# MODULE 3: CONTEXT ASSEMBLY — Tower-Centric 360° View
# =============================================================================

def assemble_tower_context():
    """
    For each tower_id, merge all extracted entities into a unified context.
    This is the 'C' in ECL — the foundation for all downstream use cases.
    """

    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.tower_context AS

    WITH contract_summary AS (
        SELECT tower_id,
            COLLECT_SET(tenant_name) AS contracted_tenants,
            COUNT(*) AS total_contracted_equipment,
            SUM(financial_terms.monthly_rent) AS total_monthly_rent,
            COLLECT_LIST(STRUCT(type, model, quantity, rad_center_height_ft,
                                sector, mounting_type)) AS contract_equipment_list
        FROM crown_castle.ecl.contract_equipment
        GROUP BY tower_id
    ),

    drone_summary AS (
        SELECT tower_id,
            COUNT(*) AS total_detected_equipment,
            AVG(confidence) AS avg_detection_confidence,
            COLLECT_LIST(STRUCT(detected_type, confidence,
                                position_height_ft, sector)) AS drone_equipment_list
        FROM crown_castle.ecl.drone_equipment
        WHERE confidence >= 0.70
        GROUP BY tower_id
    ),

    billing_summary AS (
        SELECT tower_id,
            SUM(billed_amount) AS total_monthly_billed,
            SUM(billed_equipment_count) AS total_billed_equipment,
            COLLECT_SET(tenant_name) AS billed_tenants
        FROM crown_castle.ecl.billing_entities
        WHERE billing_period = DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM')
        GROUP BY tower_id
    ),

    wo_summary AS (
        SELECT tower_id,
            COUNT(*) AS total_work_orders_12mo,
            SUM(CASE WHEN wo_type = 'EMERGENCY' THEN 1 ELSE 0 END) AS emergency_wos,
            SUM(wo_cost) AS total_wo_cost_12mo
        FROM crown_castle.ecl.work_order_entities
        WHERE created_date >= ADD_MONTHS(CURRENT_DATE(), -12)
        GROUP BY tower_id
    )

    SELECT
        COALESCE(c.tower_id, d.tower_id, b.tower_id) AS tower_id,

        -- Contract context
        c.contracted_tenants,
        c.total_contracted_equipment,
        c.total_monthly_rent,
        c.contract_equipment_list,

        -- Drone/physical context
        d.total_detected_equipment,
        d.avg_detection_confidence,
        d.drone_equipment_list,

        -- Financial context
        b.total_monthly_billed,
        b.total_billed_equipment,
        b.billed_tenants,

        -- Operational context
        w.total_work_orders_12mo,
        w.emergency_wos,
        w.total_wo_cost_12mo,

        -- Computed health indicators
        CASE
            WHEN d.total_detected_equipment > c.total_contracted_equipment
            THEN 'PHYSICAL_EXCESS'
            WHEN d.total_detected_equipment < c.total_contracted_equipment
            THEN 'PHYSICAL_DEFICIT'
            ELSE 'PHYSICAL_MATCH'
        END AS physical_reconciliation_status,

        CASE
            WHEN b.total_monthly_billed < c.total_monthly_rent * 0.95
            THEN 'UNDERBILLED'
            WHEN b.total_monthly_billed > c.total_monthly_rent * 1.05
            THEN 'OVERBILLED'
            ELSE 'BILLING_MATCH'
        END AS financial_reconciliation_status,

        CURRENT_TIMESTAMP() AS context_assembled_at

    FROM contract_summary c
    FULL OUTER JOIN drone_summary d ON c.tower_id = d.tower_id
    FULL OUTER JOIN billing_summary b ON COALESCE(c.tower_id, d.tower_id) = b.tower_id
    LEFT JOIN wo_summary w ON COALESCE(c.tower_id, d.tower_id, b.tower_id) = w.tower_id
    """)


# =============================================================================
# MODULE 4: LINKAGE ENGINE — Cross-Source Discovery
# =============================================================================

def run_linkage_engine():
    """
    The 'L' in ECL — joins contract, drone, and billing to discover:
    1. Unauthorized equipment (DISH default, rogue installs)
    2. Missing equipment (contracted but not physically present)
    3. Billing discrepancies (billed ≠ contracted ≠ observed)
    4. Revenue opportunities (upsell, amendment candidates)
    """

    # ─── Linkage 1: Contract vs Drone (Core MVP) ───

    # Equipment type mapping: contract terms → CV detection labels
    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.equipment_type_map AS
    SELECT * FROM VALUES
        ('panel_antenna',  'panel_antenna',  'ANTENNA'),
        ('antenna',        'panel_antenna',  'ANTENNA'),
        ('rru',            'rru',            'RADIO'),
        ('remote_radio',   'rru',            'RADIO'),
        ('microwave_dish', 'microwave_dish', 'MICROWAVE'),
        ('dish',           'microwave_dish', 'MICROWAVE'),
        ('cabinet',        'cabinet',        'GROUND_EQUIPMENT'),
        ('cable_tray',     'cable_tray',     'CABLING'),
        ('coax_run',       'cable_tray',     'CABLING'),
        ('generator',      'generator',      'POWER'),
        ('meter',          'meter',          'POWER'),
        ('ice_bridge',     'ice_bridge',     'STRUCTURE')
    AS t(contract_type, drone_type, equipment_category)
    """)

    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.linkage_contract_vs_drone AS

    WITH contract_agg AS (
        SELECT ce.tower_id, ce.tenant_name,
            m.drone_type AS normalized_type,
            m.equipment_category,
            SUM(ce.quantity) AS contract_count
        FROM crown_castle.ecl.contract_equipment ce
        LEFT JOIN crown_castle.ecl.equipment_type_map m
            ON LOWER(ce.type) = m.contract_type
        GROUP BY ce.tower_id, ce.tenant_name, m.drone_type, m.equipment_category
    ),

    drone_agg AS (
        SELECT tower_id,
            detected_type AS normalized_type,
            COUNT(*) AS drone_count,
            AVG(confidence) AS avg_confidence
        FROM crown_castle.ecl.drone_equipment
        WHERE confidence >= 0.70
        GROUP BY tower_id, detected_type
    )

    SELECT
        COALESCE(c.tower_id, d.tower_id) AS tower_id,
        c.tenant_name,
        COALESCE(c.normalized_type, d.normalized_type) AS equipment_type,
        c.equipment_category,
        c.contract_count,
        d.drone_count,
        d.avg_confidence,
        COALESCE(d.drone_count, 0) - COALESCE(c.contract_count, 0) AS delta,

        CASE
            WHEN c.contract_count IS NULL THEN 'UNAUTHORIZED_EQUIPMENT'
            WHEN d.drone_count IS NULL THEN 'MISSING_EQUIPMENT'
            WHEN d.drone_count > c.contract_count THEN 'EXCESS_EQUIPMENT'
            WHEN d.drone_count < c.contract_count THEN 'DEFICIT_EQUIPMENT'
            ELSE 'MATCHED'
        END AS linkage_type,

        CASE
            WHEN c.contract_count IS NULL THEN 'HIGH'
            WHEN d.drone_count IS NULL THEN 'HIGH'
            WHEN ABS(COALESCE(d.drone_count,0) - COALESCE(c.contract_count,0)) >= 3
                THEN 'HIGH'
            WHEN ABS(COALESCE(d.drone_count,0) - COALESCE(c.contract_count,0)) >= 1
                THEN 'MEDIUM'
            ELSE 'LOW'
        END AS severity,

        CURRENT_TIMESTAMP() AS linkage_created_at

    FROM contract_agg c
    FULL OUTER JOIN drone_agg d
        ON c.tower_id = d.tower_id
        AND c.normalized_type = d.normalized_type
    """)

    # ─── Linkage 2: DISH Default Equipment Detection ───

    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.linkage_dish_default AS
    SELECT
        d.tower_id,
        d.detected_type AS equipment_type,
        d.drone_count,
        'DISH_DEFAULT_EQUIPMENT' AS linkage_type,
        'HIGH' AS severity,
        'Equipment from defaulted DISH contract still physically on tower. '
        || 'Action: Schedule removal or negotiate with replacement tenant.' AS
            recommended_action
    FROM (
        SELECT tower_id, detected_type, COUNT(*) AS drone_count
        FROM crown_castle.ecl.drone_equipment
        WHERE confidence >= 0.70
        GROUP BY tower_id, detected_type
    ) d
    INNER JOIN crown_castle.ecl.contract_entities ce
        ON d.tower_id = ce.tower_id
    WHERE LOWER(ce.tenant_name) LIKE '%dish%'
      AND (ce.financial_terms.expiration_date < CURRENT_DATE()
           OR ce.lease_type = 'terminated')
    """)

    # ─── Linkage 3: Three-Way Reconciliation (Contract vs Drone vs Billing) ───

    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.linkage_three_way AS
    SELECT
        tc.tower_id,
        tc.physical_reconciliation_status,
        tc.financial_reconciliation_status,
        tc.total_contracted_equipment,
        tc.total_detected_equipment,
        tc.total_monthly_rent,
        tc.total_monthly_billed,
        tc.total_monthly_billed - tc.total_monthly_rent AS billing_delta,

        CASE
            WHEN tc.physical_reconciliation_status != 'PHYSICAL_MATCH'
             AND tc.financial_reconciliation_status != 'BILLING_MATCH'
            THEN 'CRITICAL'
            WHEN tc.physical_reconciliation_status != 'PHYSICAL_MATCH'
              OR tc.financial_reconciliation_status != 'BILLING_MATCH'
            THEN 'ATTENTION'
            ELSE 'CLEAN'
        END AS overall_tower_health,

        -- Revenue impact
        CASE
            WHEN tc.total_monthly_billed < tc.total_monthly_rent
            THEN (tc.total_monthly_rent - tc.total_monthly_billed) * 12
            ELSE 0
        END AS annual_underbilling_impact,

        tc.total_work_orders_12mo,
        tc.emergency_wos

    FROM crown_castle.ecl.tower_context tc
    """)


# =============================================================================
# MODULE 5: USE CASE EXPANSION — Same ECL, Different Outputs
# =============================================================================

# ─── Use Case 2: Revenue Intelligence (Paradigm 2) ───

def ecl_revenue_intelligence():
    """
    ECL applied to revenue: extract carrier signals, build market context,
    link to tower availability for proactive opportunity scoring.
    Maps to Paradigm 2 from vision doc.
    """
    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.revenue_opportunities AS
    SELECT
        tc.tower_id,
        tc.contracted_tenants,
        tc.total_contracted_equipment,
        tc.total_detected_equipment,

        -- Towers with physical capacity (fewer detected than structural max)
        CASE
            WHEN tc.total_detected_equipment < 9  -- avg tower holds 3 tenants x 3 sectors
            THEN 'HAS_CAPACITY'
            ELSE 'AT_CAPACITY'
        END AS capacity_status,

        -- DISH vacancy = immediate upsell opportunity
        CASE
            WHEN ARRAY_CONTAINS(tc.contracted_tenants, 'DISH Wireless')
             AND tc.financial_reconciliation_status IN ('UNDERBILLED', 'BILLING_MATCH')
            THEN 'DISH_VACANCY_OPPORTUNITY'
            ELSE NULL
        END AS dish_opportunity,

        -- Amendment candidate: more equipment detected than contracted
        CASE
            WHEN tc.physical_reconciliation_status = 'PHYSICAL_EXCESS'
            THEN 'AMENDMENT_NEEDED'
            ELSE NULL
        END AS amendment_opportunity

    FROM crown_castle.ecl.tower_context tc
    WHERE tc.physical_reconciliation_status != 'PHYSICAL_MATCH'
       OR ARRAY_CONTAINS(tc.contracted_tenants, 'DISH Wireless')
    """)


# ─── Use Case 3: Lease Management Automation (Paradigm 3) ───

def ecl_lease_automation():
    """
    ECL applied to lease lifecycle: extract expiration signals,
    build renewal context, link to market rates for negotiation.
    Maps to Paradigm 3 from vision doc.
    """
    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.lease_renewal_queue AS
    SELECT
        ce.tower_id,
        ce.tenant_name,
        ce.financial_terms.expiration_date,
        ce.financial_terms.monthly_rent,
        ce.financial_terms.annual_escalator_pct,
        ce.financial_terms.renewal_terms,
        DATEDIFF(ce.financial_terms.expiration_date, CURRENT_DATE()) AS days_to_expiry,

        -- Link to tower context for negotiation leverage
        tc.total_detected_equipment,
        tc.total_work_orders_12mo,

        CASE
            WHEN DATEDIFF(ce.financial_terms.expiration_date, CURRENT_DATE()) <= 90
            THEN 'URGENT'
            WHEN DATEDIFF(ce.financial_terms.expiration_date, CURRENT_DATE()) <= 180
            THEN 'UPCOMING'
            ELSE 'PLANNED'
        END AS renewal_priority

    FROM crown_castle.ecl.contract_entities ce
    LEFT JOIN crown_castle.ecl.tower_context tc ON ce.tower_id = tc.tower_id
    WHERE ce.financial_terms.expiration_date >= CURRENT_DATE()
    ORDER BY days_to_expiry ASC
    """)


# ─── Use Case 4: Knowledge Graph / Institutional Memory (Paradigm 6) ───

def ecl_knowledge_graph_export():
    """
    Export ECL entities and linkages as Neo4j-ready Cypher for the
    institutional memory knowledge graph. Maps to Paradigm 6.
    """
    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.kg_nodes AS

    -- Tower nodes
    SELECT tower_id AS node_id, 'Tower' AS label,
        TO_JSON(STRUCT(tower_id, contracted_tenants,
                       total_contracted_equipment)) AS properties
    FROM crown_castle.ecl.tower_context

    UNION ALL

    -- Tenant nodes
    SELECT DISTINCT tenant_name AS node_id, 'Tenant' AS label,
        TO_JSON(STRUCT(tenant_name)) AS properties
    FROM crown_castle.ecl.contract_equipment

    UNION ALL

    -- Equipment nodes
    SELECT CONCAT(tower_id, '-', type, '-', sector) AS node_id,
        'Equipment' AS label,
        TO_JSON(STRUCT(tower_id, type, model, quantity,
                       rad_center_height_ft, sector)) AS properties
    FROM crown_castle.ecl.contract_equipment
    """)

    spark.sql("""
    CREATE OR REPLACE TABLE crown_castle.ecl.kg_edges AS

    -- Tower → Tenant (LEASES_TO)
    SELECT DISTINCT tower_id AS source, tenant_name AS target,
        'LEASES_TO' AS relationship,
        TO_JSON(STRUCT(monthly_rent)) AS properties
    FROM crown_castle.ecl.contract_equipment

    UNION ALL

    -- Tower → Equipment (HAS_EQUIPMENT / contract)
    SELECT tower_id AS source,
        CONCAT(tower_id, '-', type, '-', sector) AS target,
        'HAS_CONTRACTED_EQUIPMENT' AS relationship,
        TO_JSON(STRUCT(quantity, source)) AS properties
    FROM crown_castle.ecl.contract_equipment

    UNION ALL

    -- Linkage edges (discrepancies)
    SELECT tower_id AS source,
        equipment_type AS target,
        linkage_type AS relationship,
        TO_JSON(STRUCT(delta, severity, avg_confidence)) AS properties
    FROM crown_castle.ecl.linkage_contract_vs_drone
    WHERE linkage_type != 'MATCHED'
    """)


# =============================================================================
# MODULE 6: EXECUTIVE VIEWS & ALERTS
# =============================================================================

def create_executive_views():
    """Dashboard-ready views for Power BI / Databricks SQL."""

    # Portfolio health scorecard
    spark.sql("""
    CREATE OR REPLACE VIEW crown_castle.ecl.v_portfolio_health AS
    SELECT
        overall_tower_health,
        COUNT(*) AS tower_count,
        SUM(annual_underbilling_impact) AS total_annual_impact,
        AVG(total_work_orders_12mo) AS avg_work_orders
    FROM crown_castle.ecl.linkage_three_way
    GROUP BY overall_tower_health
    """)

    # DISH default exposure
    spark.sql("""
    CREATE OR REPLACE VIEW crown_castle.ecl.v_dish_exposure AS
    SELECT
        tower_id, equipment_type, drone_count,
        recommended_action
    FROM crown_castle.ecl.linkage_dish_default
    ORDER BY drone_count DESC
    """)

    # Top 50 revenue recovery towers
    spark.sql("""
    CREATE OR REPLACE VIEW crown_castle.ecl.v_top_recovery AS
    SELECT tower_id, billing_delta,
        annual_underbilling_impact,
        physical_reconciliation_status,
        financial_reconciliation_status,
        total_contracted_equipment,
        total_detected_equipment
    FROM crown_castle.ecl.linkage_three_way
    WHERE overall_tower_health = 'CRITICAL'
    ORDER BY annual_underbilling_impact DESC
    LIMIT 50
    """)

    # ECL linkage summary (all use cases)
    spark.sql("""
    CREATE OR REPLACE VIEW crown_castle.ecl.v_ecl_linkage_summary AS
    SELECT linkage_type, severity,
        COUNT(*) AS occurrences,
        COUNT(DISTINCT tower_id) AS towers_affected,
        SUM(ABS(delta)) AS total_equipment_delta
    FROM crown_castle.ecl.linkage_contract_vs_drone
    GROUP BY linkage_type, severity
    ORDER BY
        CASE severity WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
        occurrences DESC
    """)


# =============================================================================
# MODULE 7: ORCHESTRATION — Run the Full ECL Pipeline
# =============================================================================

def run_ecl_pipeline():
    """Master orchestrator — runs all ECL stages in sequence."""

    print("=" * 70)
    print("  Summit ECL PIPELINE — Contract-Drone Reconciliation + Beyond")
    print("=" * 70)

    print("\n[1/7] Extracting contract entities from lease PDFs...")
    extract_contracts_pipeline()

    print("[2/7] Extracting drone entities (PRSW JSON + CV)...")
    extract_drone_entities()

    print("[3/7] Extracting operational entities (Oracle, JDE, ServiceNow)...")
    extract_operational_entities()

    print("[4/7] Assembling tower context (360° view)...")
    assemble_tower_context()

    print("[5/7] Running linkage engine (reconciliation + discovery)...")
    run_linkage_engine()

    print("[6/7] Generating use case outputs...")
    ecl_revenue_intelligence()      # Paradigm 2
    ecl_lease_automation()          # Paradigm 3
    ecl_knowledge_graph_export()    # Paradigm 6

    print("[7/7] Creating executive views...")
    create_executive_views()

    print("\n" + "=" * 70)
    print("  ✅ ECL PIPELINE COMPLETE")
    print("=" * 70)
    print("\nTables created in crown_castle.ecl:")
    tables = [
        "contract_entities", "contract_equipment",
        "drone_equipment_prsw", "drone_equipment_cv", "drone_equipment",
        "billing_entities", "work_order_entities", "inspection_entities",
        "tower_context",
        "equipment_type_map",
        "linkage_contract_vs_drone", "linkage_dish_default", "linkage_three_way",
        "revenue_opportunities", "lease_renewal_queue",
        "kg_nodes", "kg_edges",
    ]
    for t in tables:
        print(f"  📦 {t}")
    print("\nViews:")
    views = [
        "v_portfolio_health", "v_dish_exposure",
        "v_top_recovery", "v_ecl_linkage_summary"
    ]
    for v in views:
        print(f"  📊 {v}")


# =============================================================================
# ENTRYPOINT
# =============================================================================
if __name__ == "__main__":
    run_ecl_pipeline()
