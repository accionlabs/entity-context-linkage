from ecl_lease_ingestor import build_portfolio_graph
res = build_portfolio_graph()
geo_data = []
for ent in res["entities"]:
    props = ent.get("properties", {})
    if props.get("latitude") and props.get("longitude"):
        geo_data.append({
            "city": props.get("location"),
            "lat": props.get("latitude"),
            "lon": props.get("longitude")
        })
print(f"Total Towers mapped: {len(geo_data)}")
