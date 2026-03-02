"""
Telecom REIT Extraction Module
================================
Simulated extraction pipelines that return sample data.
In production, these would use Databricks/Spark with ai_query and ai_parse_document.
"""

from typing import List
from telecom_reit.models import Entity
from telecom_reit.sample_data import (
    TOWER_ENTITIES,
    CONTRACT_ENTITIES,
    DRONE_ENTITIES,
    BILLING_ENTITIES,
    WORK_ORDER_ENTITIES,
    INSPECTION_ENTITIES,
)


def extract_towers() -> List[Entity]:
    """Extract tower site entities from the tower sites database."""
    return list(TOWER_ENTITIES)


def extract_contracts() -> List[Entity]:
    """
    Extract contract/lease entities from PDF documents.
    Production: Databricks ai_parse_document + ai_query with CONTRACT_EXTRACTION_PROMPT.
    Demo: Returns realistic sample data.
    """
    return list(CONTRACT_ENTITIES)


def extract_drone_data() -> List[Entity]:
    """
    Extract equipment detection entities from drone imagery.
    Production: PRSW JSON from Snowflake + CV classification on raw images.
    Demo: Returns realistic sample data.
    """
    return list(DRONE_ENTITIES)


def extract_billing() -> List[Entity]:
    """
    Extract billing record entities from Oracle/ERP.
    Production: Glue-cataloged parquet from Golden Gate replication.
    Demo: Returns realistic sample data.
    """
    return list(BILLING_ENTITIES)


def extract_work_orders() -> List[Entity]:
    """
    Extract work order entities from JDE ERP.
    Production: Parquet from S3 Bronze layer.
    Demo: Returns realistic sample data.
    """
    return list(WORK_ORDER_ENTITIES)


def extract_inspections() -> List[Entity]:
    """
    Extract inspection entities from ServiceNow.
    Production: Parquet from S3 Bronze layer.
    Demo: Returns realistic sample data.
    """
    return list(INSPECTION_ENTITIES)


def extract_all() -> dict:
    """Run all extraction pipelines and return categorized results."""
    return {
        "towers": extract_towers(),
        "contracts": extract_contracts(),
        "drone": extract_drone_data(),
        "billing": extract_billing(),
        "work_orders": extract_work_orders(),
        "inspections": extract_inspections(),
    }
