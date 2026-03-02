"""
Telecom REIT Linkage Engine
============================
Cross-source reconciliation — the 'L' in ECL.
Discovers discrepancies between contracts, drone observations, and billing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from telecom_reit.models import (
    Entity, EntityType, EntitySource, Linkage, LinkageType,
    EQUIPMENT_TYPE_MAP,
)
from telecom_reit.context import TowerContext


@dataclass
class LinkageResult:
    """Complete output from the linkage engine."""
    contract_vs_drone: List[Linkage] = field(default_factory=list)
    defaulted_equipment: List[Linkage] = field(default_factory=list)
    three_way: List[Dict[str, Any]] = field(default_factory=list)
    all_linkages: List[Linkage] = field(default_factory=list)

    @property
    def total_linkages(self) -> int:
        return len(self.all_linkages)

    @property
    def high_severity_count(self) -> int:
        return sum(1 for l in self.all_linkages if l.severity == "HIGH")

    @property
    def total_revenue_impact(self) -> float:
        return sum(l.revenue_impact or 0 for l in self.all_linkages)


def _normalize_type(equip_type: str) -> tuple:
    """Normalize an equipment type to (drone_type, category)."""
    key = equip_type.lower().strip()
    return EQUIPMENT_TYPE_MAP.get(key, (key, "OTHER"))


def run_contract_vs_drone_linkage(
    contracts: List[Entity],
    drone_detections: List[Entity],
) -> List[Linkage]:
    """
    Compare contracted equipment against drone-detected equipment per tower.
    Returns linkages for: UNAUTHORIZED, MISSING, EXCESS, DEFICIT, MATCHED.
    """
    linkages = []

    # Aggregate contract equipment by (tower_id, normalized_type)
    contract_agg: Dict[tuple, Dict[str, Any]] = {}
    for contract in contracts:
        tid = contract.attributes.get("tower_id")
        tenant = contract.attributes.get("tenant_name", "Unknown")
        manifest = contract.attributes.get("equipment_manifest", [])

        for equip in manifest:
            norm_type, category = _normalize_type(equip.get("type", ""))
            key = (tid, norm_type)
            if key not in contract_agg:
                contract_agg[key] = {
                    "tower_id": tid, "tenant": tenant,
                    "normalized_type": norm_type, "category": category,
                    "contract_count": 0,
                }
            contract_agg[key]["contract_count"] += equip.get("quantity", 1)

    # Aggregate drone detections by (tower_id, normalized_type)
    drone_agg: Dict[tuple, Dict[str, Any]] = {}
    for det in drone_detections:
        tid = det.attributes.get("tower_id")
        det_type = det.attributes.get("detected_type", "")
        norm_type, category = _normalize_type(det_type)
        key = (tid, norm_type)
        if key not in drone_agg:
            drone_agg[key] = {
                "tower_id": tid,
                "normalized_type": norm_type, "category": category,
                "drone_count": 0,
                "avg_confidence": 0.0,
                "confidences": [],
            }
        count = det.attributes.get("count", 1)
        drone_agg[key]["drone_count"] += count
        drone_agg[key]["confidences"].append(det.confidence)

    # Compute average confidence
    for key, agg in drone_agg.items():
        confs = agg.pop("confidences", [])
        agg["avg_confidence"] = sum(confs) / len(confs) if confs else 0.0

    # Compare: find all keys from both sides
    all_keys = set(contract_agg.keys()) | set(drone_agg.keys())

    link_id = 0
    for key in sorted(all_keys):
        tid, norm_type = key
        c = contract_agg.get(key)
        d = drone_agg.get(key)

        contract_count = c["contract_count"] if c else 0
        drone_count = d["drone_count"] if d else 0
        delta = drone_count - contract_count

        # Determine linkage type
        if c is None:
            ltype = LinkageType.UNAUTHORIZED_EQUIPMENT
            severity = "HIGH"
            action = (
                f"Unauthorized {norm_type} detected on tower {tid}. "
                f"No matching lease contract found. Schedule investigation."
            )
        elif d is None:
            ltype = LinkageType.MISSING_EQUIPMENT
            severity = "HIGH"
            action = (
                f"Contracted {norm_type} not detected by drone on tower {tid}. "
                f"Verify: equipment may have been removed without authorization."
            )
        elif delta > 0:
            ltype = LinkageType.EXCESS_EQUIPMENT
            severity = "HIGH" if abs(delta) >= 3 else "MEDIUM"
            action = f"Excess {norm_type} on tower {tid}: {delta} more than contracted."
        elif delta < 0:
            ltype = LinkageType.DEFICIT_EQUIPMENT
            severity = "MEDIUM" if abs(delta) >= 2 else "LOW"
            action = f"Deficit {norm_type} on tower {tid}: {abs(delta)} fewer than contracted."
        else:
            ltype = LinkageType.MATCHED
            severity = "LOW"
            action = None

        # Create placeholder entities for source/target
        src = Entity(
            entity_id=f"contract_{tid}_{norm_type}",
            entity_type=EntityType.EQUIPMENT,
            source=EntitySource.CONTRACT_PDF,
            attributes={"tower_id": tid, "type": norm_type, "count": contract_count},
            confidence=c.get("avg_confidence", 0.9) if c else 0.0,
        )
        tgt = Entity(
            entity_id=f"drone_{tid}_{norm_type}",
            entity_type=EntityType.EQUIPMENT,
            source=EntitySource.DRONE_JSON,
            attributes={"tower_id": tid, "type": norm_type, "count": drone_count},
            confidence=d.get("avg_confidence", 0.0) if d else 0.0,
        )

        linkages.append(Linkage(
            linkage_id=f"link_cvd_{link_id:04d}",
            linkage_type=ltype,
            source_entity=src,
            target_entity=tgt,
            delta={"contract_count": contract_count, "drone_count": drone_count, "difference": delta},
            severity=severity,
            confidence=min(src.confidence, tgt.confidence) if tgt.confidence > 0 else src.confidence,
            recommended_action=action,
        ))
        link_id += 1

    return linkages


def detect_defaulted_equipment(
    contracts: List[Entity],
    drone_detections: List[Entity],
) -> List[Linkage]:
    """
    Find equipment from defaulted/terminated leases that is still physically on towers.
    """
    linkages = []

    # Find defaulted contracts
    defaulted = [
        c for c in contracts
        if c.attributes.get("status") in ("defaulted", "terminated")
    ]

    for contract in defaulted:
        tid = contract.attributes.get("tower_id")
        tenant = contract.attributes.get("tenant_name", "Unknown")

        # Check if drone detected equipment at the contract's height range
        manifest = contract.attributes.get("equipment_manifest", [])
        contracted_heights = set()
        for equip in manifest:
            h = equip.get("rad_center_height_ft")
            if h:
                contracted_heights.add(h)

        # Find drone detections near those heights
        matching_drone = [
            d for d in drone_detections
            if d.attributes.get("tower_id") == tid
            and d.attributes.get("position_height_ft") in contracted_heights
        ]

        if matching_drone:
            for det in matching_drone:
                linkages.append(Linkage(
                    linkage_id=f"link_default_{tid}_{det.entity_id}",
                    linkage_type=LinkageType.DEFAULTED_EQUIPMENT,
                    source_entity=contract,
                    target_entity=det,
                    delta={
                        "tenant": tenant,
                        "status": contract.attributes.get("status"),
                        "detected_type": det.attributes.get("detected_type"),
                        "condition": det.attributes.get("condition"),
                    },
                    severity="HIGH",
                    confidence=det.confidence,
                    revenue_impact=contract.attributes.get("monthly_rent", 0) * -12,
                    recommended_action=(
                        f"Equipment from defaulted {tenant} lease still on tower {tid}. "
                        f"Condition: {det.attributes.get('condition', 'unknown')}. "
                        f"Action: Schedule removal or negotiate with replacement tenant."
                    ),
                    evidence=[
                        det.attributes.get("image_ref", ""),
                        contract.raw_reference or "",
                    ],
                ))

    return linkages


def run_three_way_reconciliation(
    tower_contexts: Dict[str, "TowerContext"],
) -> List[Dict[str, Any]]:
    """
    Three-way reconciliation: Contract vs Drone vs Billing.
    Returns summary per tower with overall health status.
    """
    results = []

    for tid, ctx in tower_contexts.items():
        billing_delta = ctx.total_monthly_billed - ctx.total_monthly_rent

        # Determine overall health
        phys_ok = ctx.physical_reconciliation_status == "PHYSICAL_MATCH"
        fin_ok = ctx.financial_reconciliation_status == "BILLING_MATCH"

        if not phys_ok and not fin_ok:
            health = "CRITICAL"
        elif not phys_ok or not fin_ok:
            health = "ATTENTION"
        else:
            health = "CLEAN"

        # Revenue impact
        annual_underbilling = 0
        if ctx.total_monthly_billed < ctx.total_monthly_rent:
            annual_underbilling = (ctx.total_monthly_rent - ctx.total_monthly_billed) * 12

        results.append({
            "tower_id": tid,
            "physical_reconciliation_status": ctx.physical_reconciliation_status,
            "financial_reconciliation_status": ctx.financial_reconciliation_status,
            "total_contracted_equipment": ctx.total_contracted_equipment,
            "total_detected_equipment": ctx.total_detected_equipment,
            "total_monthly_rent": ctx.total_monthly_rent,
            "total_monthly_billed": ctx.total_monthly_billed,
            "billing_delta": billing_delta,
            "overall_tower_health": health,
            "annual_underbilling_impact": annual_underbilling,
            "work_order_count": len(ctx.work_orders),
        })

    return results


def run_full_linkage(
    contracts: List[Entity],
    drone_detections: List[Entity],
    tower_contexts: Dict[str, "TowerContext"],
) -> LinkageResult:
    """Run all linkage analyses and return combined results."""
    result = LinkageResult()

    result.contract_vs_drone = run_contract_vs_drone_linkage(contracts, drone_detections)
    result.defaulted_equipment = detect_defaulted_equipment(contracts, drone_detections)
    result.three_way = run_three_way_reconciliation(tower_contexts)

    result.all_linkages = result.contract_vs_drone + result.defaulted_equipment

    return result
