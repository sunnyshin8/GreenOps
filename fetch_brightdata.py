import json
import os
import sys
import time
import subprocess
import requests

# -------------------------------------------------
# ✨ USER‑CONFIGURATION
# -------------------------------------------------
MCP_TOKEN    = "f4c4808a-cd7b-4959-b161-9abc9ab32819"                         # ← YOUR API token
HEC_ENDPOINT = "http://localhost:8088/services/collector"          # Adjust if HEC runs on a different host/port
HEC_TOKEN    = "d38a3acc-7f39-424f-bb3b-b9396657caeb"                        # ← HEC token you created in Splunk
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
