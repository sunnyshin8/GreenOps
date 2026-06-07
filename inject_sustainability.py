import json

def add_sustainability_panels(dashboard_path):
    with open(dashboard_path, 'r') as f:
        data = json.load(f)

    # Add data sources
    queries = {
        "ds_green_computing": "search index=main sourcetype=sustainability_feed \"green computing\" | table _time title description url",
        "ds_energy_efficiency": "search index=main sourcetype=sustainability_feed \"energy efficiency\" | table _time title description url",
        "ds_sustainability_reports": "search index=main sourcetype=sustainability_feed \"sustainability\" | table _time title description url",
        "ds_carbon_reduction": "search index=main sourcetype=sustainability_feed \"carbon\" | table _time title description url",
        "ds_renewable_energy": "search index=main sourcetype=sustainability_feed \"renewable\" | table _time title description url"
    }

    for ds_name, query in queries.items():
        data["dataSources"][ds_name] = {
            "type": "ds.search",
            "options": {
                "query": query,
                "queryParameters": {
                    "earliest": "$global_time.earliest$",
                    "latest": "$global_time.latest$"
                }
            }
        }

    # Add visualizations
    viz_map = {
        "viz_green_computing": ("ds_green_computing", "Green Computing Articles"),
        "viz_energy_efficiency": ("ds_energy_efficiency", "Energy Efficiency News"),
        "viz_sustainability_reports": ("ds_sustainability_reports", "Data Center Sustainability Reports"),
        "viz_carbon_reduction": ("ds_carbon_reduction", "Carbon Reduction Initiatives"),
        "viz_renewable_energy": ("ds_renewable_energy", "Renewable Energy Technology Updates")
    }

    for viz_name, (ds_name, title) in viz_map.items():
        data["visualizations"][viz_name] = {
            "type": "splunk.table",
            "dataSources": {
                "primary": ds_name
            },
            "title": title,
            "options": {
                "count": 5
            }
        }

    # Add to layout
    layout_name = "layout_XZ0YBGNa"
    if layout_name not in data.get("layout", {}).get("globalInputs", []):
        if "layout" in data and "structure" in data["layout"]:
            for item in data["layout"]["structure"]:
                if isinstance(item, dict) and item.get("id") == layout_name:
                    # Found the tab! Add our panels here
                    if "children" not in item:
                        item["children"] = []
                    item["children"].extend([
                        {"type": "block", "children": [{"type": "element", "elementId": "viz_green_computing"}]},
                        {"type": "block", "children": [{"type": "element", "elementId": "viz_energy_efficiency"}]},
                        {"type": "block", "children": [{"type": "element", "elementId": "viz_sustainability_reports"}]},
                        {"type": "block", "children": [{"type": "element", "elementId": "viz_carbon_reduction"}]},
                        {"type": "block", "children": [{"type": "element", "elementId": "viz_renewable_energy"}]}
                    ])
                    break

    with open(dashboard_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    add_sustainability_panels("C:/Users/asus/Downloads/gdlk2/7_7.json")
    print("Added sustainability panels to 7_7.json")
