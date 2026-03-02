import os
import glob
import re
import time
import csv
from typing import Dict, List, Optional, Any
from ecl_poc import Entity, EntityType, Relationship, RelationshipType, ExtractionResult

try:
    from city_coords import GEO_LOOKUP
except ImportError:
    GEO_LOOKUP = {}

# Store revenue opportunity data
TOWER_REVENUE_OPPORTUNITY: Dict[str, float] = {}

def load_structural_capacity_data(base_dir: str):
    """Loads revenue opportunity data from structural_capacity.csv."""
    csv_filepath = os.path.join(base_dir, "slides/structural_capacity.csv")
    if not os.path.exists(csv_filepath):
        print(f"Warning: structural_capacity.csv not found at {csv_filepath}")
        return

    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tower_id = row.get("tower_id")
            revenue_str = row.get("revenue_opportunity_monthly")
            if tower_id and revenue_str:
                try:
                    TOWER_REVENUE_OPPORTUNITY[tower_id] = float(revenue_str.replace('$', '').replace(',', ''))
                except ValueError:
                    print(f"Warning: Could not parse revenue_opportunity_monthly for tower {tower_id}: {revenue_str}")

def parse_lease_file(filepath: str) -> Dict:
    with open(filepath, 'r') as f:
        content = f.read()
        
    data = {"filepath": filepath}
    
    # Extract Sublicense ID
    match = re.search(r'\*\*Sublicense ID:\*\* (.*?)\s*\n', content)
    if match: data["sublicense_id"] = match.group(1).strip()
    
    # Extract Tower Site ID
    match = re.search(r'\*\*Tower Site ID:\*\* (.*?)\s*\n', content)
    if match: data["tower_id"] = match.group(1).strip()
    
    # Extract Licensee Name
    match = re.search(r'\*\*LICENSEE:\*\*\s*\n(.*?)\s*\n', content)
    if match: data["tenant_name"] = match.group(1).strip()
    
    # Extract Monthly Rent
    match = re.search(r'\*\*3\.1 Monthly Rent\.\*\* \*\*\$(.*?)/month\*\*', content)
    if match: 
        try:
            data["monthly_rent"] = float(match.group(1).replace(',', ''))
        except ValueError:
            data["monthly_rent"] = 0.0
            
    # Extract City Location
    match = re.search(r'WHEREAS, Licensor operates tower \*\*.*?\*\* in (.*?);', content)
    if match: data["city_location"] = match.group(1).strip()

    # Extract Outstanding/Unpaid Balance (Lost Revenue)
    balance_match = re.search(r"(?:Outstanding|Unpaid) balance[^$]*\$([\d,]+\.\d{2})", content, re.IGNORECASE)
    if balance_match:
        try:
            data["lost_revenue"] = float(balance_match.group(1).replace(",", ""))
        except ValueError:
            data["lost_revenue"] = 0.0
    else:
        data["lost_revenue"] = 0.0
            
    return data

def build_portfolio_graph() -> ExtractionResult:
    """
    Batch parses all 750+ tenant lease markdown files, extracts key metrics,
    and wires them into an ECL ExtractionResult graph.
    """
    start_time = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(base_dir, "contracts/tenant_leases/*.md"))
    
    load_structural_capacity_data(base_dir)

    entities: Dict[str, Entity] = {}
    relationships: List[Relationship] = []
    
    total_rent = 0.0
    total_lost_revenue = 0.0
    total_revenue_opportunity = 0.0
    
    # Aggregate city-level data
    city_summary: Dict[str, Dict[str, Any]] = {}

    for f in files:
        data = parse_lease_file(f)
        sub_id = data.get("sublicense_id")
        tower_id = data.get("tower_id")
        tenant = data.get("tenant_name")
        rent = data.get("monthly_rent", 0.0)
        lost_revenue = data.get("lost_revenue", 0.0)
        city_str = data.get("city_location", "")
        
        if not sub_id or not tower_id or not tenant:
            continue
            
        total_rent += rent
        total_lost_revenue += lost_revenue
            
        # 1. Lease Node
        lease_node_id = f"lease_{sub_id}"
        if lease_node_id not in entities:
            entities[lease_node_id] = Entity(
                id=lease_node_id,
                name=f"Lease {sub_id}",
                type=EntityType.CONTRACT,
                source_expert="LeaseIngestor",
                confidence=1.0,
                properties={"_discovered_type": "Tenant Sublicense", "monthly_rent": rent, "lost_revenue": lost_revenue}
            )
            
        # 2. Tower Node
        tower_node_id = f"tower_{tower_id}"
        if tower_node_id not in entities:
            
            # Map location
            lat, lon = None, None
            if city_str in GEO_LOOKUP:
                lat, lon = GEO_LOOKUP[city_str]
            
            # Get revenue opportunity from CSV
            revenue_opportunity = TOWER_REVENUE_OPPORTUNITY.get(tower_id, 0.0)
            total_revenue_opportunity += revenue_opportunity

            entities[tower_node_id] = Entity(
                id=tower_node_id,
                name=tower_id,
                type=EntityType.TOWER,
                source_expert="LeaseIngestor",
                confidence=1.0,
                properties={
                    "_discovered_type": "Cell Tower",
                    "location": city_str,
                    "latitude": lat,
                    "longitude": lon,
                    "revenue_opportunity_monthly": revenue_opportunity
                }
            )
            
        # 3. Tenant Node
        tenant_node_id = f"tenant_{hash(tenant)}"
        if tenant_node_id not in entities:
            # We use an organization type
            entities[tenant_node_id] = Entity(
                id=tenant_node_id,
                name=tenant,
                type=EntityType.COMPANY,
                source_expert="LeaseIngestor",
                confidence=1.0,
                properties={"_discovered_type": "Carrier / Telecom"}
            )
            
        # Edge: Tenant -> Lease
        relationships.append(Relationship(
            source_id=tenant_node_id,
            target_id=lease_node_id,
            type=RelationshipType.HAS_CONTRACT,
            confidence=1.0,
            properties={"_discovered_type": "Execution"}
        ))
        
        # Edge: Lease -> Tower
        relationships.append(Relationship(
            source_id=lease_node_id,
            target_id=tower_node_id,
            type=RelationshipType.ADAPTIVE,
            confidence=1.0,
            properties={"_discovered_type": "LOCATED_AT"}
        ))

    proc_time = int((time.time() - start_time) * 1000)
    
    # Store aggregate stats in a meta-entity so we can display them easily
    # (Just a trick to pass global context up to the UI if we want it)

    entities_json = []
    for e in entities.values():
        e_dict = dict(e.__dict__)
        e_dict["type"] = e.type.value
        entities_json.append(e_dict)
        
    rels_json = []
    for r in relationships:
        r_dict = dict(r.__dict__)
        r_dict["type"] = r.type.value
        rels_json.append(r_dict)
        
    return {
        "entities": entities_json,
        "relationships": rels_json,
        "total_entities": len(entities),
        "total_relationships": len(relationships),
        "processing_time_ms": proc_time,
        "engine": "BatchRegexIngestor",
        "total_rent": total_rent,
        "reasoning": f"Batch ingested {len(files)} lease documents. Total Monthly Rent: ${total_rent:,.2f}"
    }

if __name__ == "__main__":
    result = build_portfolio_graph()
    print(f"Entities: {result['total_entities']}")
    print(f"Relationships: {result['total_relationships']}")
    print(result['reasoning'])
