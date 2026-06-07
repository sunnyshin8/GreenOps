import json
import os
import sys
import time
import subprocess
import requests

# -------------------------------------------------
# ✨ USER‑CONFIGURATION
# -------------------------------------------------

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

MCP_TOKEN    = os.environ.get("MCP_TOKEN", "")
HEC_ENDPOINT = os.environ.get("HEC_ENDPOINT", "http://localhost:8088/services/collector")
HEC_TOKEN    = os.environ.get("HEC_TOKEN", "")

if not MCP_TOKEN or not HEC_TOKEN:
    print("[ERROR] MCP_TOKEN or HEC_TOKEN is missing. Please set them in a .env file.")
    sys.exit(1)
# -------------------------------------------------

def fetch_feed_mcp():
    """Call the Bright Data MCP locally via stdio and use the discover tool."""
    print("[INFO] Starting local Bright Data MCP process...")
    proc = subprocess.Popen(
        ["npx.cmd" if os.name == "nt" else "npx", "-y", "@brightdata/mcp"],
        env={**os.environ, "API_TOKEN": MCP_TOKEN},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def send_req(req):
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()

    # 1. Initialize MCP
    send_req({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "fetch", "version": "1.0"}
        }
    })

    results = []
    
    # 2. Wait for responses and call the tool
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        
        try:
            msg = json.loads(line)
        except:
            continue
            
        if msg.get("id") == 1:
            # Send initialized notification
            send_req({
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # Call 'discover' tool to search for sustainability news
            send_req({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "discover",
                    "arguments": {
                        "query": "sustainability green computing energy efficiency data center renewable energy",
                        "num_results": 50
                    }
                }
            })
            
        if msg.get("id") == 2:
            # We got our search results
            try:
                tool_result = msg.get("result", {}).get("content", [])
                for content in tool_result:
                    if content.get("type") == "text":
                        # The text is a JSON string of results
                        parsed_text = json.loads(content["text"])
                        if isinstance(parsed_text, list):
                            results.extend(parsed_text)
            except Exception as e:
                print(f"[ERROR] Failed to parse tool result: {e}", file=sys.stderr)
            
            proc.kill()
            break
                
    return results

def send_to_splunk(events):
    """Push a list of dicts to Splunk HEC."""
    hec_headers = {"Authorization": f"Splunk {HEC_TOKEN}"}
    for ev in events:
        payload = {
            "event": ev,
            "sourcetype": "sustainability_feed",
            "host": "brightdata_mcp"
        }
        r = requests.post(HEC_ENDPOINT, headers=hec_headers,
                          json=payload, timeout=10)
        if r.status_code != 200:
            print(f"[WARN] HEC rejected event: {r.text}", file=sys.stderr)

def main(poll_interval=300):
    """Continuously poll the local MCP server (default every 5 min)."""
    while True:
        try:
            data = fetch_feed_mcp()
            events = data if isinstance(data, list) else [data]
            if events:
                send_to_splunk(events)
                print(f"[INFO] Sent {len(events)} events to Splunk at {time.strftime('%X')}")
            else:
                print(f"[WARN] No events retrieved at {time.strftime('%X')}")
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            
        print(f"[INFO] Sleeping for {poll_interval} seconds...")
        time.sleep(poll_interval)

if __name__ == "__main__":
    interval = int(os.getenv("POLL_SECONDS", "300"))
    main(poll_interval=interval)
