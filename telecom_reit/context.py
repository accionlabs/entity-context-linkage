"""
Telecom REIT Context Assembly
==============================
Merges extracted entities from contracts, drone, billing, and operations
into a unified tower-centric 360° context view — the 'C' in ECL.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from telecom_reit.models import Entity, EntityType, EntitySource, Context


@dataclass
class TowerContext:
    """Assembled 360° context for a single tower site."""
    tower_id: str
    tower_entity: Optional[Entity] = None

    # Contract context
    contracted_tenants: List[str] = field(default_factory=list)
    total_contracted_equipment: int = 0
    total_monthly_rent: float = 0.0
    contract_equipment_list: List[Dict[str, Any]] = field(default_factory=list)

    # Drone/physical context
    total_detected_equipment: int = 0
    avg_detection_confidence: float = 0.0
    drone_equipment_list: List[Dict[str, Any]] = field(default_factory=list)

    # Financial context
    total_monthly_billed: float = 0.0
    total_billed_equipment: int = 0
    billed_tenants: List[str] = field(default_factory=list)

    # Operational context
    work_orders: List[Entity] = field(default_factory=list)
    inspections: List[Entity] = field(default_factory=list)

    # Computed health indicators
    physical_reconciliation_status: str = "UNKNOWN"
    financial_reconciliation_status: str = "UNKNOWN"

    def compute_health(self):
        """Compute reconciliation status from assembled data."""
        # Physical reconciliation
        if self.total_detected_equipment > self.total_contracted_equipment:
            self.physical_reconciliation_status = "PHYSICAL_EXCESS"
        elif self.total_detected_equipment < self.total_contracted_equipment:
            self.physical_reconciliation_status = "PHYSICAL_DEFICIT"
        else:
            self.physical_reconciliation_status = "PHYSICAL_MATCH"

        # Financial reconciliation (5% tolerance)
        if self.total_monthly_rent == 0:
            self.financial_reconciliation_status = "NO_CONTRACT"
        elif self.total_monthly_billed < self.total_monthly_rent * 0.95:
            self.financial_reconciliation_status = "UNDERBILLED"
        elif self.total_monthly_billed > self.total_monthly_rent * 1.05:
            self.financial_reconciliation_status = "OVERBILLED"
        else:
            self.financial_reconciliation_status = "BILLING_MATCH"


def assemble_tower_context(extracted: dict) -> Dict[str, TowerContext]:
    """
    Assemble a TowerContext for each tower from all extracted entities.

    Args:
        extracted: Dict with keys 'towers', 'contracts', 'drone', 'billing',
                   'work_orders', 'inspections' — each a list of Entity objects.

    Returns:
        Dict mapping tower_id to TowerContext.
    """
    contexts: Dict[str, TowerContext] = {}

    # Initialize from tower entities
    for tower in extracted.get("towers", []):
        tid = tower.attributes.get("tower_id", tower.entity_id)
        ctx = TowerContext(tower_id=tid, tower_entity=tower)
        contexts[tid] = ctx

    # Aggregate contract data
    for contract in extracted.get("contracts", []):
        tid = contract.attributes.get("tower_id")
        if not tid:
            continue
        if tid not in contexts:
            contexts[tid] = TowerContext(tower_id=tid)

        ctx = contexts[tid]
        tenant = contract.attributes.get("tenant_name", "Unknown")
        if tenant not in ctx.contracted_tenants:
            ctx.contracted_tenants.append(tenant)

        rent = contract.attributes.get("monthly_rent", 0)
        # Only count active leases toward financial context
        status = contract.attributes.get("status", "active")
        if status == "active":
            ctx.total_monthly_rent += rent

        manifest = contract.attributes.get("equipment_manifest", [])
        for equip in manifest:
            qty = equip.get("quantity", 1)
            ctx.total_contracted_equipment += qty
            ctx.contract_equipment_list.append({
                "tenant": tenant,
                "type": equip.get("type"),
                "model": equip.get("model"),
                "quantity": qty,
                "height_ft": equip.get("rad_center_height_ft"),
                "sector": equip.get("sector"),
            })

    # Aggregate drone data
    for drone in extracted.get("drone", []):
        tid = drone.attributes.get("tower_id")
        if not tid or tid not in contexts:
            continue

        ctx = contexts[tid]
        count = drone.attributes.get("count", 1)
        ctx.total_detected_equipment += count
        ctx.drone_equipment_list.append({
            "type": drone.attributes.get("detected_type"),
            "count": count,
            "height_ft": drone.attributes.get("position_height_ft"),
            "sector": drone.attributes.get("sector"),
            "condition": drone.attributes.get("condition"),
            "confidence": drone.confidence,
        })

    # Compute average drone confidence per tower
    for tid, ctx in contexts.items():
        if ctx.drone_equipment_list:
            total_conf = sum(d.get("confidence", 0) for d in ctx.drone_equipment_list)
            ctx.avg_detection_confidence = total_conf / len(ctx.drone_equipment_list)

    # Aggregate billing data
    for bill in extracted.get("billing", []):
        tid = bill.attributes.get("tower_id")
        if not tid or tid not in contexts:
            continue

        ctx = contexts[tid]
        amount = bill.attributes.get("billed_amount", 0)
        ctx.total_monthly_billed += amount
        ctx.total_billed_equipment += bill.attributes.get("billed_equipment_count", 0)

        tenant = bill.attributes.get("tenant_name", "Unknown")
        if tenant not in ctx.billed_tenants:
            ctx.billed_tenants.append(tenant)

    # Attach work orders and inspections
    for wo in extracted.get("work_orders", []):
        tid = wo.attributes.get("tower_id")
        if tid and tid in contexts:
            contexts[tid].work_orders.append(wo)

    for insp in extracted.get("inspections", []):
        tid = insp.attributes.get("tower_id")
        if tid and tid in contexts:
            contexts[tid].inspections.append(insp)

    # Compute health indicators
    for ctx in contexts.values():
        ctx.compute_health()

    return contexts
