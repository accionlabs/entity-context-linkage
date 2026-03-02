import os
import glob
import re
from typing import Dict, List

def parse_lease_file(filepath: str) -> Dict:
    with open(filepath, 'r') as f:
        content = f.read()
        
    data = {"filepath": filepath}
    
    # Extract basic info
    match = re.search(r'\*\*Sublicense ID:\*\* (.*?)\s*\n', content)
    if match: data["sublicense_id"] = match.group(1).strip()
    
    match = re.search(r'\*\*Tower Site ID:\*\* (.*?)\s*\n', content)
    if match: data["tower_id"] = match.group(1).strip()
    
    match = re.search(r'\*\*LICENSEE:\*\*\s*\n(.*?)\s*\n', content)
    if match: data["tenant_name"] = match.group(1).strip()
    
    match = re.search(r'\*\*3\.1 Monthly Rent\.\*\* \*\*\$(.*?)/month\*\*', content)
    if match: data["monthly_rent"] = float(match.group(1).replace(',', ''))
    
    return data

def main():
    files = glob.glob("contracts/tenant_leases/*.md")
    print(f"Found {len(files)} lease files.")
    
    parsed_data = []
    for f in files[:5]: # Parse first 5 as a test
        parsed_data.append(parse_lease_file(f))
        
    for data in parsed_data:
        print(f"Parsed: {data.get('sublicense_id')} | Tower: {data.get('tower_id')} | Tenant: {data.get('tenant_name')} | Rent: ${data.get('monthly_rent')}")

if __name__ == "__main__":
    main()
