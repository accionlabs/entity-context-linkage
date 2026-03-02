"""
Telecom REIT Sample Data
=========================
Realistic tower lease contracts, drone detections, and ERP billing records
for demo and testing. Based on current industry market data (2024-2026).

Towers:
  TR-4521  Urban rooftop, Houston TX — 3 carriers, full match
  TR-8803  Suburban monopole, Charlotte NC — 1 active + 1 DISH defaulted
  TR-6150  Rural lattice, West Texas — 1 carrier + unauthorized equipment
"""

from telecom_reit.models import Entity, EntitySource, EntityType


# =============================================================================
# TOWER DEFINITIONS
# =============================================================================

TOWER_ENTITIES = [
    Entity(
        entity_id="tower_TR-4521",
        entity_type=EntityType.TOWER,
        source=EntitySource.CCISITES,
        attributes={
            "tower_id": "TR-4521",
            "location": "29.7604° N, 95.3698° W",
            "city": "Houston",
            "state": "TX",
            "tower_type": "Rooftop",
            "height_ft": 160,
            "structural_capacity_tenants": 4,
            "current_tenants": 3,
            "faa_registration": "ASR-1042567",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="tower_TR-8803",
        entity_type=EntityType.TOWER,
        source=EntitySource.CCISITES,
        attributes={
            "tower_id": "TR-8803",
            "location": "35.2271° N, 80.8431° W",
            "city": "Charlotte",
            "state": "NC",
            "tower_type": "Monopole",
            "height_ft": 150,
            "structural_capacity_tenants": 3,
            "current_tenants": 2,
            "faa_registration": "ASR-2087431",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="tower_TR-6150",
        entity_type=EntityType.TOWER,
        source=EntitySource.CCISITES,
        attributes={
            "tower_id": "TR-6150",
            "location": "31.9973° N, 102.0779° W",
            "city": "Midland",
            "state": "TX",
            "tower_type": "Lattice",
            "height_ft": 200,
            "structural_capacity_tenants": 4,
            "current_tenants": 1,
            "faa_registration": "ASR-3156892",
        },
        confidence=1.0,
    ),
]


# =============================================================================
# CONTRACT / LEASE ENTITIES (Extracted from PDF)
# =============================================================================

CONTRACT_ENTITIES = [
    # ─── Tower TR-4521: Verizon ───
    Entity(
        entity_id="lease_TR-4521_verizon",
        entity_type=EntityType.LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-4521",
            "tenant_name": "Verizon Wireless",
            "lease_type": "carrier_lease",
            "lease_number": "VZ-2019-04521-A",
            "status": "active",
            "monthly_rent": 4800.00,
            "annual_escalator_pct": 3.0,
            "escalator_type": "fixed",
            "commencement_date": "2019-01-15",
            "expiration_date": "2029-01-14",
            "renewal_terms": "3 successive 5-year auto-renewal periods",
            "equipment_manifest": [
                {"type": "panel_antenna", "model": "Ericsson AIR 6449", "quantity": 12,
                 "rad_center_height_ft": 142, "sector": "A/B/C", "mounting_type": "face_mount",
                 "dimensions_inches": "39x20x8", "weight_lbs": 42.0},
                {"type": "rru", "model": "Ericsson Radio 4415", "quantity": 6,
                 "rad_center_height_ft": 140, "sector": "A/B/C", "mounting_type": "standoff",
                 "dimensions_inches": "20x12x7", "weight_lbs": 26.0},
                {"type": "cabinet", "model": "Purcell Systems 16RU", "quantity": 2,
                 "rad_center_height_ft": None, "sector": None, "mounting_type": "ground",
                 "dimensions_inches": "72x36x36", "weight_lbs": 650.0},
            ],
            "special_conditions": [
                "Right of first refusal on additional tower space",
                "Carrier responsible for structural analysis updates every 3 years",
            ],
            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": 2800,
                "max_horizontal_load_sqft": 45,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "1.0 inch radial",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },
        },
        confidence=0.94,
        raw_reference="s3://reit-data-lake/contracts/TR-4521/VZ-2019-04521-A.pdf",
    ),

    # ─── Tower TR-4521: T-Mobile ───
    Entity(
        entity_id="lease_TR-4521_tmobile",
        entity_type=EntityType.LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-4521",
            "tenant_name": "T-Mobile US",
            "lease_type": "carrier_lease",
            "lease_number": "TM-2021-04521-B",
            "status": "active",
            "monthly_rent": 3950.00,
            "annual_escalator_pct": 2.5,
            "escalator_type": "fixed",
            "commencement_date": "2021-06-01",
            "expiration_date": "2031-05-31",
            "renewal_terms": "4 successive 5-year auto-renewal periods",
            "equipment_manifest": [
                {"type": "panel_antenna", "model": "Nokia AEHC", "quantity": 9,
                 "rad_center_height_ft": 130, "sector": "A/B/C", "mounting_type": "face_mount",
                 "dimensions_inches": "38x18x8", "weight_lbs": 38.0},
                {"type": "rru", "model": "Nokia AEQE", "quantity": 9,
                 "rad_center_height_ft": 128, "sector": "A/B/C", "mounting_type": "standoff",
                 "dimensions_inches": "19x11x6", "weight_lbs": 22.0},
                {"type": "cabinet", "model": "Charles Industries CUBE", "quantity": 1,
                 "rad_center_height_ft": None, "sector": None, "mounting_type": "ground",
                 "dimensions_inches": "72x30x30", "weight_lbs": 480.0},
            ],
            "special_conditions": [
                "Co-location agreement with shared ice bridge access",
            ],
            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": 2200,
                "max_horizontal_load_sqft": 38,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "1 inch radial",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },
        },
        confidence=0.92,
        raw_reference="s3://reit-data-lake/contracts/TR-4521/TM-2021-04521-B.pdf",
    ),

    # ─── Tower TR-4521: AT&T ───
    Entity(
        entity_id="lease_TR-4521_att",
        entity_type=EntityType.LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-4521",
            "tenant_name": "AT&T Mobility",
            "lease_type": "carrier_lease",
            "lease_number": "ATT-2020-04521-C",
            "status": "active",
            "monthly_rent": 4200.00,
            "annual_escalator_pct": 3.0,
            "escalator_type": "hybrid",
            "commencement_date": "2020-03-01",
            "expiration_date": "2030-02-28",
            "renewal_terms": "3 successive 5-year auto-renewal periods",
            "equipment_manifest": [
                {"type": "panel_antenna", "model": "CommScope FFHH-65C-R3", "quantity": 9,
                 "rad_center_height_ft": 120, "sector": "alpha/beta/gamma", "mounting_type": "face_mount",
                 "dimensions_inches": "72x12x7", "weight_lbs": 44.0},
                {"type": "rru", "model": "Samsung MT6402", "quantity": 6,
                 "rad_center_height_ft": 118, "sector": "alpha/beta/gamma", "mounting_type": "side_arm",
                 "dimensions_inches": "18x14x8", "weight_lbs": 30.0},
                {"type": "cabinet", "model": "Bard MC4002-A", "quantity": 2,
                 "rad_center_height_ft": None, "sector": None, "mounting_type": "ground",
                 "dimensions_inches": "78x36x36", "weight_lbs": 720.0},
            ],
            "special_conditions": [
                "CPI escalator with 3% floor, 5% ceiling",
                "Generator access shared with Verizon per Amendment #2",
            ],
            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": 2600,
                "max_horizontal_load_sqft": 42,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "1 inch radial",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },
        },
        confidence=0.91,
        raw_reference="s3://reit-data-lake/contracts/TR-4521/ATT-2020-04521-C.pdf",
    ),

    # ─── Tower TR-8803: Verizon (Active) ───
    Entity(
        entity_id="lease_TR-8803_verizon",
        entity_type=EntityType.LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-8803",
            "tenant_name": "Verizon Wireless",
            "lease_type": "carrier_lease",
            "lease_number": "VZ-2020-08803-A",
            "status": "active",
            "monthly_rent": 2800.00,
            "annual_escalator_pct": 3.0,
            "escalator_type": "fixed",
            "commencement_date": "2020-01-01",
            "expiration_date": "2030-12-31",
            "renewal_terms": "2 successive 5-year auto-renewal periods",
            "equipment_manifest": [
                {"type": "panel_antenna", "model": "Ericsson AIR 3246", "quantity": 6,
                 "rad_center_height_ft": 135, "sector": "A/B/C", "mounting_type": "face_mount",
                 "dimensions_inches": "38x14x7", "weight_lbs": 35.0},
                {"type": "rru", "model": "Ericsson Radio 2217", "quantity": 3,
                 "rad_center_height_ft": 133, "sector": "A/B/C", "mounting_type": "standoff",
                 "dimensions_inches": "17x10x5", "weight_lbs": 18.0},
                {"type": "cabinet", "model": "Purcell Systems 12RU", "quantity": 1,
                 "rad_center_height_ft": None, "sector": None, "mounting_type": "ground",
                 "dimensions_inches": "60x30x30", "weight_lbs": 420.0},
            ],
            "special_conditions": [],
            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": 1800,
                "max_horizontal_load_sqft": 30,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "0.5 inch radial",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },
        },
        confidence=0.93,
        raw_reference="s3://reit-data-lake/contracts/TR-8803/VZ-2020-08803-A.pdf",
    ),

    # ─── Tower TR-8803: DISH (DEFAULTED) ───
    Entity(
        entity_id="lease_TR-8803_dish",
        entity_type=EntityType.LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-8803",
            "tenant_name": "DISH Wireless",
            "lease_type": "carrier_lease",
            "lease_number": "DISH-2022-08803-B",
            "status": "defaulted",
            "monthly_rent": 1950.00,
            "annual_escalator_pct": 2.0,
            "escalator_type": "fixed",
            "commencement_date": "2022-01-01",
            "expiration_date": "2027-12-31",
            "renewal_terms": "2 successive 5-year auto-renewal periods",
            "default_details": {
                "days_overdue": 90,
                "outstanding_amount": 5850.00,
                "last_payment_date": "2025-11-01",
                "default_notice_sent": "2026-01-15",
                "cure_period_expires": "2026-02-14",
            },
            "equipment_manifest": [
                {"type": "panel_antenna", "model": "JMA MX08F-65-CDL", "quantity": 3,
                 "rad_center_height_ft": 110, "sector": "A/B/C", "mounting_type": "face_mount",
                 "dimensions_inches": "36x12x6", "weight_lbs": 28.0},
                {"type": "rru", "model": "JMA TEKO DAS", "quantity": 3,
                 "rad_center_height_ft": 108, "sector": "A/B/C", "mounting_type": "standoff",
                 "dimensions_inches": "15x10x6", "weight_lbs": 16.0},
                {"type": "microwave_dish", "model": "Andrew VHLP2-18", "quantity": 1,
                 "rad_center_height_ft": 105, "sector": None, "mounting_type": "side_arm",
                 "dimensions_inches": "24dia x 14", "weight_lbs": 22.0},
            ],
            "special_conditions": [
                "Equipment removal required within 90 days of lease termination",
                "Landlord retains right to remove at tenant's expense after cure period",
            ],
            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": 1400,
                "max_horizontal_load_sqft": 22,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "0.5 inch radial",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },
        },
        confidence=0.95,
        raw_reference="s3://reit-data-lake/contracts/TR-8803/DISH-2022-08803-B.pdf",
    ),

    # ─── Tower TR-6150: T-Mobile (Active) ───
    Entity(
        entity_id="lease_TR-6150_tmobile",
        entity_type=EntityType.LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-6150",
            "tenant_name": "T-Mobile US",
            "lease_type": "carrier_lease",
            "lease_number": "TM-2023-06150-A",
            "status": "active",
            "monthly_rent": 1200.00,
            "annual_escalator_pct": 2.0,
            "escalator_type": "fixed",
            "commencement_date": "2023-01-01",
            "expiration_date": "2033-12-31",
            "renewal_terms": "3 successive 5-year auto-renewal periods",
            "equipment_manifest": [
                {"type": "panel_antenna", "model": "Nokia AirScale ABIA", "quantity": 6,
                 "rad_center_height_ft": 180, "sector": "A/B/C", "mounting_type": "face_mount",
                 "dimensions_inches": "40x20x8", "weight_lbs": 40.0},
                {"type": "rru", "model": "Nokia AEQS", "quantity": 3,
                 "rad_center_height_ft": 178, "sector": "A/B/C", "mounting_type": "standoff",
                 "dimensions_inches": "18x12x7", "weight_lbs": 24.0},
                {"type": "generator", "model": "Generac 22kW", "quantity": 1,
                 "rad_center_height_ft": None, "sector": None, "mounting_type": "ground",
                 "dimensions_inches": "48x25x29", "weight_lbs": 508.0},
            ],
            "special_conditions": [
                "Backup generator shared with future co-location tenants",
                "30-day prior notice required for structural modifications",
            ],
            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": 2000,
                "max_horizontal_load_sqft": 35,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "1 inch radial",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },
        },
        confidence=0.90,
        raw_reference="s3://reit-data-lake/contracts/TR-6150/TM-2023-06150-A.pdf",
    ),

    # ─── Tower TR-6150: Ground Lease ───
    Entity(
        entity_id="ground_lease_TR-6150",
        entity_type=EntityType.GROUND_LEASE,
        source=EntitySource.CONTRACT_PDF,
        attributes={
            "tower_id": "TR-6150",
            "tenant_name": "Telecom REIT (Lessee)",
            "landlord": "Johnson Ranch LLC",
            "lease_type": "ground_lease",
            "lease_number": "GL-2018-06150",
            "status": "active",
            "monthly_rent": 800.00,
            "annual_escalator_pct": 0.0,
            "escalator_type": "fixed_periodic",
            "escalator_details": "15% increase every 5 years",
            "commencement_date": "2018-01-01",
            "expiration_date": "2043-12-31",
            "renewal_terms": "2 successive 5-year auto-renewal periods",
            "leased_area_sqft": 2500,
            "special_conditions": [
                "Landlord retains agricultural use rights outside compound",
                "Road maintenance shared 50/50",
                "Annual property tax reimbursement capped at $2,400",
            ],
        },
        confidence=0.96,
        raw_reference="s3://reit-data-lake/contracts/TR-6150/GL-2018-06150.pdf",
    ),
]


# =============================================================================
# DRONE DETECTION ENTITIES
# =============================================================================

DRONE_ENTITIES = [
    # ─── Tower TR-4521: All equipment matches contract ───
    Entity(
        entity_id="drone_TR-4521_antenna_vz",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-4521",
            "detected_type": "panel_antenna",
            "count": 12,
            "position_height_ft": 142,
            "sector": "A/B/C",
            "condition": "good",
            "image_ref": "s3://reit-data-lake/drone/TR-4521/20260115_142ft_panoramic.jpg",
        },
        confidence=0.94,
    ),
    Entity(
        entity_id="drone_TR-4521_rru_vz",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-4521",
            "detected_type": "rru",
            "count": 6,
            "position_height_ft": 140,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.92,
    ),
    Entity(
        entity_id="drone_TR-4521_antenna_tmo",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-4521",
            "detected_type": "panel_antenna",
            "count": 9,
            "position_height_ft": 130,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.91,
    ),
    Entity(
        entity_id="drone_TR-4521_rru_tmo",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-4521",
            "detected_type": "rru",
            "count": 9,
            "position_height_ft": 128,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.90,
    ),
    Entity(
        entity_id="drone_TR-4521_antenna_att",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-4521",
            "detected_type": "panel_antenna",
            "count": 9,
            "position_height_ft": 120,
            "sector": "alpha/beta/gamma",
            "condition": "good",
        },
        confidence=0.89,
    ),
    Entity(
        entity_id="drone_TR-4521_rru_att",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-4521",
            "detected_type": "rru",
            "count": 6,
            "position_height_ft": 118,
            "sector": "alpha/beta/gamma",
            "condition": "good",
        },
        confidence=0.88,
    ),

    # ─── Tower TR-8803: DISH equipment still present + corrosion ───
    Entity(
        entity_id="drone_TR-8803_antenna_vz",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-8803",
            "detected_type": "panel_antenna",
            "count": 6,
            "position_height_ft": 135,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.93,
    ),
    Entity(
        entity_id="drone_TR-8803_rru_vz",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-8803",
            "detected_type": "rru",
            "count": 3,
            "position_height_ft": 133,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.91,
    ),
    Entity(
        entity_id="drone_TR-8803_antenna_dish",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-8803",
            "detected_type": "panel_antenna",
            "count": 3,
            "position_height_ft": 110,
            "sector": "A/B/C",
            "condition": "degraded",
            "observation": "Mounting hardware shows surface oxidation",
        },
        confidence=0.88,
    ),
    Entity(
        entity_id="drone_TR-8803_rru_dish",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-8803",
            "detected_type": "rru",
            "count": 3,
            "position_height_ft": 108,
            "sector": "A/B/C",
            "condition": "degraded",
        },
        confidence=0.86,
    ),
    Entity(
        entity_id="drone_TR-8803_dish_mw",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-8803",
            "detected_type": "microwave_dish",
            "count": 1,
            "position_height_ft": 105,
            "sector": None,
            "condition": "corroded",
            "observation": "Dish mounting bracket corroded; alignment drift detected",
            "image_ref": "s3://reit-data-lake/drone/TR-8803/20260120_105ft_south.jpg",
        },
        confidence=0.91,
    ),

    # ─── Tower TR-6150: Unauthorized equipment detected ───
    Entity(
        entity_id="drone_TR-6150_antenna_tmo",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-6150",
            "detected_type": "panel_antenna",
            "count": 6,
            "position_height_ft": 180,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.92,
    ),
    Entity(
        entity_id="drone_TR-6150_rru_tmo",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_JSON,
        attributes={
            "tower_id": "TR-6150",
            "detected_type": "rru",
            "count": 3,
            "position_height_ft": 178,
            "sector": "A/B/C",
            "condition": "good",
        },
        confidence=0.90,
    ),
    Entity(
        entity_id="drone_TR-6150_unauthorized_antenna",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_IMAGE,
        attributes={
            "tower_id": "TR-6150",
            "detected_type": "panel_antenna",
            "count": 2,
            "position_height_ft": 160,
            "sector": "unknown",
            "condition": "operational",
            "observation": "Two panel antennas at 160ft with no matching lease contract. "
                           "Cable runs trace to unlabeled ground cabinet.",
            "image_ref": "s3://reit-data-lake/drone/TR-6150/20260118_160ft_west.jpg",
        },
        confidence=0.87,
    ),
    Entity(
        entity_id="drone_TR-6150_unauthorized_cabinet",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_IMAGE,
        attributes={
            "tower_id": "TR-6150",
            "detected_type": "cabinet",
            "count": 1,
            "position_height_ft": None,
            "sector": None,
            "condition": "operational",
            "observation": "Unlabeled ground cabinet, lock appears non-standard. "
                           "No matching equipment in any active lease.",
        },
        confidence=0.85,
    ),
    Entity(
        entity_id="drone_TR-6150_meter_tampered",
        entity_type=EntityType.EQUIPMENT,
        source=EntitySource.DRONE_IMAGE,
        attributes={
            "tower_id": "TR-6150",
            "detected_type": "meter",
            "count": 1,
            "position_height_ft": None,
            "sector": None,
            "condition": "tampered",
            "observation": "Utility meter seal broken; possible unauthorized power tap.",
        },
        confidence=0.82,
    ),
]


# =============================================================================
# BILLING / ERP ENTITIES
# =============================================================================

BILLING_ENTITIES = [
    # TR-4521 — all current
    Entity(
        entity_id="billing_TR-4521_verizon_202601",
        entity_type=EntityType.BILLING_RECORD,
        source=EntitySource.ORACLE_TX,
        attributes={
            "tower_id": "TR-4521",
            "tenant_name": "Verizon Wireless",
            "billed_amount": 4800.00,
            "billing_period": "2026-01",
            "billed_equipment_count": 20,
            "payment_status": "paid",
            "payment_date": "2026-01-03",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="billing_TR-4521_tmobile_202601",
        entity_type=EntityType.BILLING_RECORD,
        source=EntitySource.ORACLE_TX,
        attributes={
            "tower_id": "TR-4521",
            "tenant_name": "T-Mobile US",
            "billed_amount": 3950.00,
            "billing_period": "2026-01",
            "billed_equipment_count": 19,
            "payment_status": "paid",
            "payment_date": "2026-01-05",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="billing_TR-4521_att_202601",
        entity_type=EntityType.BILLING_RECORD,
        source=EntitySource.ORACLE_TX,
        attributes={
            "tower_id": "TR-4521",
            "tenant_name": "AT&T Mobility",
            "billed_amount": 4200.00,
            "billing_period": "2026-01",
            "billed_equipment_count": 17,
            "payment_status": "paid",
            "payment_date": "2026-01-04",
        },
        confidence=1.0,
    ),

    # TR-8803 — Verizon paid, DISH not billed (suspended)
    Entity(
        entity_id="billing_TR-8803_verizon_202601",
        entity_type=EntityType.BILLING_RECORD,
        source=EntitySource.ORACLE_TX,
        attributes={
            "tower_id": "TR-8803",
            "tenant_name": "Verizon Wireless",
            "billed_amount": 2800.00,
            "billing_period": "2026-01",
            "billed_equipment_count": 10,
            "payment_status": "paid",
            "payment_date": "2026-01-02",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="billing_TR-8803_dish_202601",
        entity_type=EntityType.BILLING_RECORD,
        source=EntitySource.ORACLE_TX,
        attributes={
            "tower_id": "TR-8803",
            "tenant_name": "DISH Wireless",
            "billed_amount": 0.00,
            "billing_period": "2026-01",
            "billed_equipment_count": 0,
            "payment_status": "suspended",
            "outstanding_balance": 5850.00,
            "notes": "Billing suspended per default notice DISH-2022-08803-B",
        },
        confidence=1.0,
    ),

    # TR-6150 — T-Mobile paid
    Entity(
        entity_id="billing_TR-6150_tmobile_202601",
        entity_type=EntityType.BILLING_RECORD,
        source=EntitySource.ORACLE_TX,
        attributes={
            "tower_id": "TR-6150",
            "tenant_name": "T-Mobile US",
            "billed_amount": 1200.00,
            "billing_period": "2026-01",
            "billed_equipment_count": 10,
            "payment_status": "paid",
            "payment_date": "2026-01-06",
        },
        confidence=1.0,
    ),
]


# =============================================================================
# WORK ORDER / INSPECTION ENTITIES
# =============================================================================

WORK_ORDER_ENTITIES = [
    Entity(
        entity_id="wo_TR-8803_removal",
        entity_type=EntityType.WORK_ORDER,
        source=EntitySource.JDE_ERP,
        attributes={
            "tower_id": "TR-8803",
            "work_order_id": "WO-2026-0142",
            "wo_type": "EQUIPMENT_REMOVAL",
            "status": "pending_approval",
            "created_date": "2026-02-15",
            "completed_date": None,
            "estimated_cost": 18500.00,
            "description": "Remove defaulted DISH Wireless equipment per lease termination",
            "assigned_crew": "Southeast Tower Services",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="wo_TR-6150_investigation",
        entity_type=EntityType.WORK_ORDER,
        source=EntitySource.JDE_ERP,
        attributes={
            "tower_id": "TR-6150",
            "work_order_id": "WO-2026-0156",
            "wo_type": "INVESTIGATION",
            "status": "scheduled",
            "created_date": "2026-02-18",
            "scheduled_date": "2026-03-01",
            "estimated_cost": 4200.00,
            "description": "Investigate unauthorized equipment at 160ft and tampered meter",
            "assigned_crew": "West Texas Tower Services",
        },
        confidence=1.0,
    ),
]


INSPECTION_ENTITIES = [
    Entity(
        entity_id="inspection_TR-4521_q1",
        entity_type=EntityType.INSPECTION,
        source=EntitySource.SERVICENOW,
        attributes={
            "tower_id": "TR-4521",
            "inspection_id": "INS-2026-TR4521-Q1",
            "inspection_type": "routine_quarterly",
            "inspection_date": "2026-01-15",
            "findings": "All equipment operational. No structural concerns. Light cleaning needed on ice bridge.",
            "inspector": "J. Martinez, PE",
            "pass_fail": "PASS",
        },
        confidence=1.0,
    ),
    Entity(
        entity_id="inspection_TR-8803_special",
        entity_type=EntityType.INSPECTION,
        source=EntitySource.SERVICENOW,
        attributes={
            "tower_id": "TR-8803",
            "inspection_id": "INS-2026-TR8803-SP",
            "inspection_type": "special_default_assessment",
            "inspection_date": "2026-01-20",
            "findings": (
                "DISH equipment at 105-110ft showing corrosion. Microwave dish mount bracket "
                "has visible rust and alignment drift. Recommended immediate removal to prevent "
                "structural risk. Verizon equipment at 133-135ft in good condition."
            ),
            "inspector": "R. Thompson, PE",
            "pass_fail": "CONDITIONAL",
        },
        confidence=1.0,
    ),
]


# =============================================================================
# SAMPLE DOCUMENT TEXT (for Streamlit demo)
# =============================================================================

TELECOM_REIT_SAMPLE_DOCUMENT = """STRUCTURAL ANALYSIS & SITE RECONCILIATION REPORT
Prepared by: Telecom REIT Asset Management Division & Internal Engineering
Report Date: 2026-02-20 | Classification: CONFIDENTIAL

═══════════════════════════════════════════════════════════════════════════════

=== EXECUTIVE SUMMARY & REGULATORY COMPLIANCE ===
SITE: TR-8803 | Location: 35.2271° N, 80.8431° W (Charlotte, NC)
Type: 150ft Monopole | FAA Registration: ASR-2087431
Compliance Standard: ANSI/TIA-222-H, ASCE 7-16, 2018 IBC
Analysis Platform: tnxTower v8.1

Overall Tower Stress Ratio: 92.4% (PASS - Near Capacity)
Foundation Capacity Utilization: 78.1% (PASS)

─── SECTION A: ACTIVE LEASES & EQUIPMENT INVENTORY ──────────────────────────

Contract #VZ-2020-08803-A — Tenant: Verizon Wireless
  Status: Active | Payment: Current | Monthly Revenue: $2,800/mo
  Escalator: 3.0% annual (fixed)
  Term: 2020-01-01 through 2030-12-31 | Renewals: 2×5yr auto
  Equipment: 6x Ericsson AIR 3246 (Panel Antennas), 3x RRU, 1x Cabinet
  Rad Center: 135ft | Sectors: A/B/C
  Structural Load Allocation: 47% Occupancy

Contract #DISH-2022-08803-B — Tenant: DISH Wireless
  Status: DEFAULTED — 90 days overdue | Outstanding: $5,850.00
  Monthly Revenue: $1,950/mo (SUSPENDED since 2025-11-01)
  Cure Period Expires: 2026-02-14 (EXPIRED)
  Equipment: 3x JMA Panel Antennas, 3x RRU, 1x Microwave Dish
  Rad Center: 110ft | Sectors: A/B/C
  Structural Load Allocation: 23% Occupancy

─── SECTION B: DRONE INSPECTION (2026-01-20) ────────────────────────────────

Inspection Type: Special Default Assessment & Structural Audit
Inspector: R. Thompson, PE

Verizon Equipment (135ft):
  Equipment Status: Operational
  Condition: 6 panel antennas and 3 RRU in good condition. 
  Mounting Hardware: Bolts secure, no oxidation.
  Wind Load Profile: Within specified 30 sq-ft allocation.

DISH Equipment (105-110ft):
  Equipment Status: Degraded
  Condition: 3 panel antennas and 3 RRU showing degraded structural integrity.
  Mounting Hardware: Surface oxidation observed on antenna mounts. 
  Microwave Dish: CORROSION DETECTED on mount bracket; alignment drift observed.
  Engineering Recommendation: Immediate removal required to prevent structural risk to the tower and mitigate progressive connection failure under ASCE 7 ice loading criteria.

─── SECTION C: FINANCIAL RISK & CAPACITY OUTLOOK ─────────────────────────────

Net Operating Income: $33,600 (Verizon active only)
Annual at Risk: $23,400 (DISH defaulted)
Estimated Equipment Removal Cost: $18,500

Net Recovery & Structural Capacity Scenario:
  Remove DISH equipment: -$18,500 (WO-2026-0142: Pending Approval)
  Reclaim tower capacity (23% wind load cross-sectional area freed)
  Tower Stress Ratio drops from 92.4% to ~69% (providing margin for 5G upgrades)
  Potential new tenant revenue: $3,500/mo (market rate)
  Annual upside from replacement tenant: $42,000
"""
