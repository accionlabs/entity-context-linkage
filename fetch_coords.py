import json
import urllib.request
import urllib.parse
import time
from parse_cities import cities, counter

unique_cities = list(counter.keys())
coords_dict = {}

print(f"Fetching coords for {len(unique_cities)} cities...")

for city in unique_cities:
    query = urllib.parse.quote(city)
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'ECL-Demo-App'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                coords_dict[city] = [lat, lon]
                print(f"'{city}': [{lat}, {lon}],")
            else:
                print(f"# Not found: {city}")
    except Exception as e:
        print(f"# Error on {city}: {e}")
        
    time.sleep(1) # Be nice to nominatim API

with open("city_coords.py", "w") as f:
    f.write("GEO_LOOKUP = {\n")
    for c, coords in coords_dict.items():
        f.write(f"    '{c}': {coords},\n")
    f.write("}\n")
    
print("Saved to city_coords.py")
