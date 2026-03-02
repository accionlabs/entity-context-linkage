import re

with open("telecom_reit/sample_data.py", "r") as f:
    text = f.read()

pattern = r'''            "structural_requirements": \{
                "max_vertical_load_lbs": (\d+),
                "max_horizontal_load_sqft": (\d+),
                "ice_loading_requirement": "(.*?)"(?:,)?
            \},'''

replacement = r'''            "structural_requirements": {
                "compliance_standard": "ANSI/TIA-222-H and ASCE 7-16",
                "max_vertical_load_lbs": \1,
                "max_horizontal_load_sqft": \2,
                "environmental_loads": {
                    "basic_wind_speed_mph": 105,
                    "ice_loading_requirement": "\3",
                    "seismic_design_category": "Site Class D"
                },
                "capacity_limits": {
                    "member_stress_ratio_max": 0.95,
                    "foundation_utilization_max": 0.90
                }
            },'''

new_text = re.sub(pattern, replacement, text)

with open("telecom_reit/sample_data.py", "w") as f:
    f.write(new_text)

print(f"Replaced {len(text) - len(new_text)} characters.")
