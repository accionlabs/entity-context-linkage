"""
Telecom REIT ECL Platform Package
==================================
ECL-powered reconciliation and intelligence for Telecom REIT tower operations.
Architecture: Entity-Context-Linkage (ECL) as the unifying intelligence layer.

Modules:
  models      — Domain data models (Entity, Context, Linkage, enums)
  sample_data — Realistic tower lease contracts and drone/ERP data
  extraction  — Simulated extraction pipelines
  context     — Tower-centric 360° context assembly
  linkage     — Cross-source reconciliation engine
  pipeline    — Full E→C→L orchestration
  adapter     — Bridge to ecl_poc types and MoE interface
"""

from telecom_reit.models import (
    EntitySource, EntityType, LinkageType,
    Entity, Context, Linkage,
)
from telecom_reit.pipeline import TelecomREITPipeline
from telecom_reit.adapter import TelecomREITReconciliationExpert

__all__ = [
    "EntitySource", "EntityType", "LinkageType",
    "Entity", "Context", "Linkage",
    "TelecomREITPipeline",
    "TelecomREITReconciliationExpert",
]
