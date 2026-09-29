import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app import app

def test_endpoints():
    client = app.test_client()
    print("=" * 65)
    print(" SourceMind: Testing Flask Backend Endpoints")
    print("=" * 65)

    # 1. GET /health
    print("\n[1] Testing GET /health...")
    resp = client.get("/health")
    print(f"    Status: {resp.status_code}")
    print(f"    Body  : {resp.get_json()}")
    assert resp.status_code == 200

    # 2. POST /request with memory_on: False
    print("\n[2] Testing POST /request (memory_on = False)...")
    payload_off = {
        "request_text": "I need 2,000 units of custom fasteners immediately for urgent assembly.",
        "memory_on": False
    }
    resp = client.post("/request", json=payload_off)
    print(f"    Status: {resp.status_code}")
    data_off = resp.get_json()
    print(f"    Model : {data_off.get('model_used')}")
    print(f"    Memories used count: {len(data_off.get('memories_used', []))}")
    print(f"    Vendors returned   : {len(data_off.get('vendors', []))}")
    assert resp.status_code == 200
    assert len(data_off.get("memories_used", [])) == 0

    # 3. POST /request with memory_on: True
    print("\n[3] Testing POST /request (memory_on = True)...")
    payload_on = {
        "request_text": "I need to purchase structural steel tubing on a tight budget, but I cannot tolerate delivery delays.",
        "memory_on": True
    }
    resp = client.post("/request", json=payload_on)
    print(f"    Status: {resp.status_code}")
    data_on = resp.get_json()
    print(f"    Model : {data_on.get('model_used')}")
    print(f"    Memories used count: {len(data_on.get('memories_used', []))}")
    print("    Recalled memories snippet:")
    for m in data_on.get("memories_used", [])[:2]:
        print(f"      - {m[:100]}...")
    print("    Vendor Recommendations:")
    for v in data_on.get("vendors", []):
        print(f"      Rank {v.get('rank')}: {v.get('name')} | Risk: {v.get('risk_assessment')}")
        print(f"        Reason: {v.get('reason')}")
        print(f"        Draft : {v.get('drafted_message')}")
    assert resp.status_code == 200
    assert len(data_on.get("memories_used", [])) > 0

    # 4. POST /outcome
    print("\n[4] Testing POST /outcome...")
    outcome_payload = {
        "vendor": "Apex Industrial Supplies",
        "material": "square steel tubing",
        "price": "$4.10/m",
        "delay_days": 10,
        "quality": "Good",
        "verdict": "Very cheap, but the 10-day delay almost halted line 2.",
        "region": "Midwest"
    }
    resp = client.post("/outcome", json=outcome_payload)
    print(f"    Status: {resp.status_code}")
    print(f"    Body  : {resp.get_json()}")
    assert resp.status_code == 200

    # 5. POST /feedback
    print("\n[5] Testing POST /feedback...")
    feedback_payload = {
        "text": "For critical structural steel, do not recommend Apex unless lead time exceeds 30 days."
    }
    resp = client.post("/feedback", json=feedback_payload)
    print(f"    Status: {resp.status_code}")
    print(f"    Body  : {resp.get_json()}")
    assert resp.status_code == 200

    # 6. GET /insights
    print("\n[6] Testing GET /insights (calling Hindsight reflect)...")
    resp = client.get("/insights")
    print(f"    Status: {resp.status_code}")
    insights_data = resp.get_json()
    print(f"    Insights Snippet: {insights_data.get('insights', '')[:300]}...")
    assert resp.status_code == 200

    # 7. POST /discover (Marketplace)
    print("\n[7] Testing POST /discover (Marketplace bank query)...")
    discover_payload = {
        "request_text": "I need high-grade structural steel tubing with fast delivery."
    }
    resp = client.post("/discover", json=discover_payload)
    print(f"    Status: {resp.status_code}")
    disc_data = resp.get_json()
    print(f"    Marketplace reviews used: {len(disc_data.get('marketplace_memories_used', []))}")
    print(f"    New vendors suggested   : {[s.get('name') for s in disc_data.get('suggestions', [])]}")
    assert resp.status_code == 200
    assert len(disc_data.get("suggestions", [])) > 0

    print("\n" + "=" * 65)
    print("[+] All 6 endpoints (including Marketplace) tested and passed!")
    print("=" * 65)

if __name__ == "__main__":
    test_endpoints()
