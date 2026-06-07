import json

file_path = r'c:\Users\asus\Downloads\gdlk2\7_7.json'

with open(file_path, 'r', encoding='utf-8') as f:
    dashboard = json.load(f)

# Add Data Sources
dashboard['dataSources'].update({
    "ds_green_computing": {
        "type": "ds.search",
        "options": {
            "query": 'index=brightdata sourcetype=sustainability_feed category="Green Computing" | table published_date, title, source, url | sort - published_date | head 10',
            "queryParameters": {"earliest": "$time.earliest$", "latest": "$time.latest$"}
        }
    },
    "ds_energy_efficiency": {
        "type": "ds.search",
        "options": {
            "query": 'index=brightdata sourcetype=sustainability_feed category="Energy Efficiency" | table published_date, title, source, url | sort - published_date | head 10',
            "queryParameters": {"earliest": "$time.earliest$", "latest": "$time.latest$"}
        }
    },
    "ds_sustainability_reports": {
        "type": "ds.search",
        "options": {
            "query": 'index=brightdata sourcetype=sustainability_feed category="Data Center Sustainability" | table published_date, title, source, summary, url | sort - published_date',
            "queryParameters": {"earliest": "$time.earliest$", "latest": "$time.latest$"}
        }
    },
    "ds_carbon_reduction": {
        "type": "ds.search",
        "options": {
            "query": 'index=brightdata sourcetype=sustainability_feed category="Carbon Reduction" | stats count by source | sort - count',
            "queryParameters": {"earliest": "$time.earliest$", "latest": "$time.latest$"}
        }
    },
    "ds_renewable_energy": {
        "type": "ds.search",
        "options": {
            "query": 'index=brightdata sourcetype=sustainability_feed category="Renewable Energy" | table published_date, title, source, url | sort - published_date | head 10',
            "queryParameters": {"earliest": "$time.earliest$", "latest": "$time.latest$"}
        }
    }
})

# Add Visualizations
dashboard['visualizations'].update({
    "viz_green_computing": {
        "type": "splunk.table",
        "dataSources": {"primary": "ds_green_computing"},
        "title": "Green Computing Articles",
        "options": {"backgroundColor": "#ffffff"},
        "eventHandlers": [
            {
                "type": "drilldown.customUrl",
                "options": {"url": "$row.url.value$", "newTab": True}
            }
        ]
    },
    "viz_energy_efficiency": {
        "type": "splunk.table",
        "dataSources": {"primary": "ds_energy_efficiency"},
        "title": "Energy Efficiency News",
        "options": {"backgroundColor": "#ffffff"},
        "eventHandlers": [
            {
                "type": "drilldown.customUrl",
                "options": {"url": "$row.url.value$", "newTab": True}
            }
        ]
    },
    "viz_sustainability_reports": {
        "type": "splunk.table",
        "dataSources": {"primary": "ds_sustainability_reports"},
        "title": "Data Center Sustainability Reports",
        "options": {"backgroundColor": "#ffffff"},
        "eventHandlers": [
            {
                "type": "drilldown.customUrl",
                "options": {"url": "$row.url.value$", "newTab": True}
            }
        ]
    },
    "viz_carbon_reduction": {
        "type": "splunk.bar",
        "dataSources": {"primary": "ds_carbon_reduction"},
        "title": "Carbon Reduction Initiatives by Source",
        "options": {"backgroundColor": "#ffffff", "seriesColors": ["#6daa45"]}
    },
    "viz_renewable_energy": {
        "type": "splunk.table",
        "dataSources": {"primary": "ds_renewable_energy"},
        "title": "Renewable Energy Technology Updates",
        "options": {"backgroundColor": "#ffffff"},
        "eventHandlers": [
            {
                "type": "drilldown.customUrl",
                "options": {"url": "$row.url.value$", "newTab": True}
            }
        ]
    }
})

# Update Layout Structure
if "layout_XZ0YBGNa" in dashboard["layout"]["layoutDefinitions"]:
    # Dashboard Studio requires grid or absolute. Let's make it absolute.
    dashboard["layout"]["layoutDefinitions"]["layout_XZ0YBGNa"] = {
        "type": "absolute",
        "options": {
            "width": 1440,
            "height": 1000,
            "display": "auto-scale",
            "backgroundColor": "#f4f6f8"
        },
        "structure": [
            {
                "item": "viz_green_computing",
                "type": "block",
                "position": {"x": 20, "y": 20, "w": 700, "h": 300}
            },
            {
                "item": "viz_energy_efficiency",
                "type": "block",
                "position": {"x": 740, "y": 20, "w": 680, "h": 300}
            },
            {
                "item": "viz_sustainability_reports",
                "type": "block",
                "position": {"x": 20, "y": 340, "w": 1400, "h": 300}
            },
            {
                "item": "viz_carbon_reduction",
                "type": "block",
                "position": {"x": 20, "y": 660, "w": 700, "h": 300}
            },
            {
                "item": "viz_renewable_energy",
                "type": "block",
                "position": {"x": 740, "y": 660, "w": 680, "h": 300}
            }
        ]
    }

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(dashboard, f, indent=4)

print("Updated 7_7.json successfully.")
