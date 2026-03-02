"""
Telecom REIT Adapter
=====================
Bridges the Telecom REIT ECL types into the existing ecl_poc.py types
so they can participate in the MoE Orchestrator and graph builder.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Any
from dataclasses import asdict

from ecl_poc import (
    Entity as ECLEntity,
    Relationship as ECLRelationship,
    ExtractionResult,
    EntityType as ECLEntityType,
    RelationshipType as ECLRelationshipType,
    BaseExpert,
)
from telecom_reit.models import Entity as TREntity, LinkageType
from telecom_reit.pipeline import TelecomREITPipeline


# ─── Type Mapping ───

_ENTITY_TYPE_MAP = {
    "tower": ECLEntityType.TOWER,
    "tenant": ECLEntityType.COMPANY,
    "equipment": ECLEntityType.EQUIPMENT,
    "lease": ECLEntityType.CONTRACT,
    "billing_record": ECLEntityType.FINANCIAL,
    "work_order": ECLEntityType.EQUIPMENT,
    "inspection": ECLEntityType.EQUIPMENT,
    "ground_lease": ECLEntityType.CONTRACT,
    "amendment": ECLEntityType.CONTRACT,
}

_LINKAGE_TO_REL_MAP = {
    LinkageType.UNAUTHORIZED_EQUIPMENT: ECLRelationshipType.HAS_EQUIPMENT,
    LinkageType.MISSING_EQUIPMENT: ECLRelationshipType.HAS_EQUIPMENT,
    LinkageType.EXCESS_EQUIPMENT: ECLRelationshipType.HAS_EQUIPMENT,
    LinkageType.DEFICIT_EQUIPMENT: ECLRelationshipType.HAS_EQUIPMENT,
    LinkageType.DEFAULTED_EQUIPMENT: ECLRelationshipType.HAS_EQUIPMENT,
    LinkageType.MATCHED: ECLRelationshipType.HAS_EQUIPMENT,
}


def tr_entity_to_ecl_entity(tr_entity: TREntity) -> ECLEntity:
    """Convert a Telecom REIT Entity to an ecl_poc Entity."""
    ecl_type = _ENTITY_TYPE_MAP.get(
        tr_entity.entity_type.value,
        ECLEntityType.EQUIPMENT,
    )

    # Build a descriptive name
    attrs = tr_entity.attributes
    if tr_entity.entity_type.value == "lease":
        name = f"Lease: {attrs.get('tenant_name', '')} @ {attrs.get('tower_id', '')}"
    elif tr_entity.entity_type.value == "tower":
        name = f"Tower {attrs.get('tower_id', tr_entity.entity_id)}"
    elif tr_entity.entity_type.value == "equipment":
        name = (f"{attrs.get('detected_type', attrs.get('type', 'Equipment'))} "
                f"@ {attrs.get('tower_id', '')}")
    elif tr_entity.entity_type.value == "billing_record":
        name = f"Billing: {attrs.get('tenant_name', '')} {attrs.get('billing_period', '')}"
    elif tr_entity.entity_type.value == "ground_lease":
        name = f"Ground Lease: {attrs.get('landlord', '')} @ {attrs.get('tower_id', '')}"
    else:
        name = tr_entity.entity_id

    return ECLEntity(
        id=tr_entity.entity_id,
        type=ecl_type,
        name=name,
        properties={
            **tr_entity.attributes,
            "source_system": tr_entity.source.value,
        },
        source_expert="TelecomREITReconciliationExpert",
        confidence=tr_entity.confidence,
    )


class TelecomREITReconciliationExpert(BaseExpert):
    """
    MoE Expert that wraps the Telecom REIT ECL pipeline.
    Runs the full E→C→L pipeline and returns results as ExtractionResult
    compatible with the existing MoE orchestrator.
    """

    def __init__(self):
        super().__init__("TelecomREITReconciliationExpert")

    def extract(self, text: str, context: Dict = None) -> ExtractionResult:
        """
        Run the Telecom REIT pipeline and convert results to ECL format.
        The 'text' parameter is accepted for MoE interface compatibility but
        the pipeline uses its own sample data for demonstration.
        """
        result = ExtractionResult(expert_name=self.name)

        # Run pipeline
        pipeline = TelecomREITPipeline()
        pipeline_result = pipeline.run_pipeline(verbose=False)

        # Convert tower entities
        for tower in pipeline_result.extracted.get("towers", []):
            ecl_entity = tr_entity_to_ecl_entity(tower)
            result.entities.append(ecl_entity)

        # Convert contract/lease entities
        for contract in pipeline_result.extracted.get("contracts", []):
            ecl_entity = tr_entity_to_ecl_entity(contract)
            result.entities.append(ecl_entity)

            # Create tower → contract relationship
            tid = contract.attributes.get("tower_id")
            if tid:
                result.relationships.append(ECLRelationship(
                    source_id=f"tower_{tid}",
                    target_id=contract.entity_id,
                    type=ECLRelationshipType.HAS_CONTRACT,
                    properties={
                        "tenant": contract.attributes.get("tenant_name"),
                        "status": contract.attributes.get("status"),
                    },
                    confidence=contract.confidence,
                ))

        # Convert key linkage findings to risk/opportunity entities
        for linkage in pipeline_result.linkage_result.all_linkages:
            if linkage.linkage_type == LinkageType.MATCHED:
                continue  # Skip matched — no action needed

            severity_val = linkage.severity

            if linkage.linkage_type == LinkageType.UNAUTHORIZED_EQUIPMENT:
                risk = ECLEntity(
                    id=f"risk_{linkage.linkage_id}",
                    type=ECLEntityType.RISK,
                    name=f"Unauthorized Equipment: {linkage.target_entity.attributes.get('type', 'unknown')}",
                    properties={
                        "risk_type": "UNAUTHORIZED_EQUIPMENT",
                        "severity": severity_val,
                        "tower_id": linkage.target_entity.attributes.get("tower_id"),
                        "recommended_action": linkage.recommended_action,
                        **linkage.delta,
                    },
                    source_expert=self.name,
                    confidence=linkage.confidence,
                )
                result.entities.append(risk)

            elif linkage.linkage_type == LinkageType.DEFAULTED_EQUIPMENT:
                risk = ECLEntity(
                    id=f"risk_{linkage.linkage_id}",
                    type=ECLEntityType.RISK,
                    name=f"Defaulted Equipment: {linkage.delta.get('tenant', 'Unknown')}",
                    properties={
                        "risk_type": "DEFAULTED_EQUIPMENT",
                        "severity": severity_val,
                        "tower_id": linkage.source_entity.attributes.get("tower_id"),
                        "tenant": linkage.delta.get("tenant"),
                        "condition": linkage.delta.get("condition"),
                        "revenue_impact": linkage.revenue_impact,
                        "recommended_action": linkage.recommended_action,
                    },
                    source_expert=self.name,
                    confidence=linkage.confidence,
                )
                result.entities.append(risk)

            elif linkage.linkage_type in (LinkageType.EXCESS_EQUIPMENT, LinkageType.DEFICIT_EQUIPMENT):
                opp = ECLEntity(
                    id=f"opportunity_{linkage.linkage_id}",
                    type=ECLEntityType.OPPORTUNITY,
                    name=f"Reconciliation: {linkage.linkage_type.value}",
                    properties={
                        "opportunity_type": "AMENDMENT_NEEDED",
                        "severity": severity_val,
                        "tower_id": linkage.source_entity.attributes.get("tower_id"),
                        "recommended_action": linkage.recommended_action,
                        **linkage.delta,
                    },
                    source_expert=self.name,
                    confidence=linkage.confidence,
                )
                result.entities.append(opp)

        # Add three-way reconciliation summary as financial entities
        for tw in pipeline_result.linkage_result.three_way:
            if tw["overall_tower_health"] != "CLEAN":
                fin = ECLEntity(
                    id=f"reconciliation_{tw['tower_id']}",
                    type=ECLEntityType.FINANCIAL,
                    name=f"Reconciliation: {tw['tower_id']} ({tw['overall_tower_health']})",
                    properties={
                        "tower_id": tw["tower_id"],
                        "overall_health": tw["overall_tower_health"],
                        "physical_status": tw["physical_reconciliation_status"],
                        "financial_status": tw["financial_reconciliation_status"],
                        "monthly_rent": tw["total_monthly_rent"],
                        "monthly_billed": tw["total_monthly_billed"],
                        "billing_delta": tw["billing_delta"],
                        "annual_underbilling": tw["annual_underbilling_impact"],
                    },
                    source_expert=self.name,
                    confidence=0.95,
                )
                result.entities.append(fin)

        result.reasoning = (
            f"Telecom REIT ECL pipeline: "
            f"{pipeline_result.summary.get('total_entities_extracted', 0)} entities extracted across "
            f"{pipeline_result.summary.get('towers_analyzed', 0)} towers, "
            f"{pipeline_result.summary.get('total_linkages', 0)} linkages discovered "
            f"({pipeline_result.summary.get('high_severity_linkages', 0)} HIGH severity), "
            f"${pipeline_result.summary.get('total_revenue_impact', 0):,.0f} revenue impact."
        )

        return result
