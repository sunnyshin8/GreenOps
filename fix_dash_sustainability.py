import json
import sys

def fix_dashboard(path):
    with open(path, 'r') as f:
        data = json.load(f)
        
    # 1. Add input_time_sus to inputs
    if "inputs" not in data:
        data["inputs"] = {}
    
    data["inputs"]["input_time_sus"] = {
        "type": "input.timerange",
        "title": "Sustainability Time Range",
        "options": {
            "token": "time_sus",
            "defaultValue": "0,now"
        }
    }
    
    # 2. Add the input to layout_XZ0YBGNa
    layouts = data.get("layout", {})
    if "layout_XZ0YBGNa" in layouts:
        structure = layouts["layout_XZ0YBGNa"].get("structure", [])
        # check if it's already there
        exists = any(isinstance(x, dict) and x.get("item") == "input_time_sus" for x in structure)
        if not exists:
            structure.append({
                "item": "input_time_sus",
                "type": "input",
                "position": {
                    "x": 20,
                    "y": 20,
                    "w": 300,
                    "h": 60
                }
            })
            
            # Shift the visualizations down to make room
            for item in structure:
                if isinstance(item, dict) and item.get("item") != "input_time_sus" and "position" in item:
                    item["position"]["y"] += 80
                    
    # 3. Update the queries and tokens
    queries = {
        "ds_green_computing": "search index=* sourcetype=sustainability_feed \"*green*\" | dedup title | table title description link",
        "ds_energy_efficiency": "search index=* sourcetype=sustainability_feed \"*energy*\" | dedup title | table title description link",
        "ds_sustainability_reports": "search index=* sourcetype=sustainability_feed \"*data center*\" OR \"*sustainab*\" | dedup title | table title description link",
        "ds_carbon_reduction": "search index=* sourcetype=sustainability_feed \"*carbon*\" OR \"*emission*\" | dedup title | table title description link",
        "ds_renewable_energy": "search index=* sourcetype=sustainability_feed \"*renewable*\" OR \"*solar*\" OR \"*wind*\" | dedup title | table title description link"
    }

    if "dataSources" in data:
        for ds_name, query in queries.items():
            if ds_name in data["dataSources"]:
                data["dataSources"][ds_name]["options"]["query"] = query
                data["dataSources"][ds_name]["options"]["queryParameters"] = {
                    "earliest": "$time_sus.earliest$",
                    "latest": "$time_sus.latest$"
                }

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    fix_dashboard("C:/Users/asus/Downloads/gdlk2/7_7.json")
    print("Fixed dashboard 7_7.json")
