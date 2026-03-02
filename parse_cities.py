import glob
import re
from collections import Counter

files = glob.glob("contracts/tenant_leases/*.md")
cities = []

for f in files:
    with open(f, 'r') as file:
        content = file.read()
        match = re.search(r'WHEREAS, Licensor operates tower \*\*.*?\*\* in (.*?);', content)
        if match:
            cities.append(match.group(1).strip())

counter = Counter(cities)
    
