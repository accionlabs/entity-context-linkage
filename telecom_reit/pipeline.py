"""
Telecom REIT Pipeline Orchestrator
====================================
Runs the full E→C→L pipeline and returns structured results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from telecom_reit.extraction import extract_all
from telecom_reit.context import assemble_tower_context, TowerContext
from telecom_reit.linkage import run_full_linkage, LinkageResult


@dataclass
class PipelineResult:
    """Complete output from the Telecom REIT ECL pipeline."""
    extracted: Dict[str, List[Any]] = field(default_factory=dict)
    tower_contexts: Dict[str, TowerContext] = field(default_factory=dict)
    linkage_result: LinkageResult = field(default_factory=LinkageResult)
    summary: Dict[str, Any] = field(default_factory=dict)


class TelecomREITPipeline:
    """
    Master orchestrator for the Telecom REIT ECL pipeline.

    Runs:
      1. Entity Extraction (contracts, drone, billing, work orders, inspections)
      2. Context Assembly (per-tower 360° view)
      3. Linkage Engine (reconciliation, defaulted equipment, three-way)
    """

    def run_pipeline(self, verbose: bool = False) -> PipelineResult:
        """Run the full ECL pipeline and return results."""
        result = PipelineResult()

        # ─── Step 1: Extract ───
        if verbose:
            print("\n[1/3] Extracting entities...")
        result.extracted = extract_all()

        entity_counts = {k: len(v) for k, v in result.extracted.items()}
        total_entities = sum(entity_counts.values())

        if verbose:
            for source, count in entity_counts.items():
                print(f"  [{source}] {count} entities")

        # ─── Step 2: Context Assembly ───
        if verbose:
            print("\n[2/3] Assembling tower context...")
        result.tower_contexts = assemble_tower_context(result.extracted)

        if verbose:
            for tid, ctx in result.tower_contexts.items():
                print(f"  [{tid}] {ctx.total_contracted_equipment} contracted, "
                      f"{ctx.total_detected_equipment} detected, "
                      f"physical={ctx.physical_reconciliation_status}, "
                      f"financial={ctx.financial_reconciliation_status}")

        # ─── Step 3: Linkage Engine ───
        if verbose:
            print("\n[3/3] Running linkage engine...")
        result.linkage_result = run_full_linkage(
            contracts=result.extracted.get("contracts", []),
            drone_detections=result.extracted.get("drone", []),
            tower_contexts=result.tower_contexts,
        )

        if verbose:
            print(f"  Total linkages: {result.linkage_result.total_linkages}")
            print(f"  HIGH severity: {result.linkage_result.high_severity_count}")
            print(f"  Revenue impact: ${result.linkage_result.total_revenue_impact:,.0f}")

        # ─── Summary ───
        result.summary = {
            "total_entities_extracted": total_entities,
            "entity_breakdown": entity_counts,
            "towers_analyzed": len(result.tower_contexts),
            "total_linkages": result.linkage_result.total_linkages,
            "high_severity_linkages": result.linkage_result.high_severity_count,
            "total_revenue_impact": result.linkage_result.total_revenue_impact,
            "three_way_reconciliation": result.linkage_result.three_way,
            "tower_health": {
                row["tower_id"]: row["overall_tower_health"]
                for row in result.linkage_result.three_way
            },
        }

        return result
