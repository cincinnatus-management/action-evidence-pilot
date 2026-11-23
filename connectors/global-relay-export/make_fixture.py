#!/usr/bin/env python3
"""Build a local record folder (same format as action_evidence.py run) from offline fixtures. No network."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import action_evidence as ae

out = sys.argv[1]
policy = {"policy_id": "fixture-readonly-v1", "agent": "fixture-agent",
          "allow": {"http_get": [{"host": "api.github.com", "path_prefix": "/repos/example/"}]}, "max_bytes": 100000}
rates = {"machine_watts": 65, "usd_per_kwh": 0.12, "cooling_multiplier": 1.3, "hardware_usd_per_hour": 0.01,
         "internet_usd_per_hour": 0.005, "model_usd_per_1m_in": 3.0, "model_usd_per_1m_out": 15.0}
actions = [{"type": "http_get", "url": "https://api.github.com/repos/example/one"},
           {"type": "http_get", "url": "https://evil.example.net/x"},
           {"type": "write_file", "path": "notes.txt"},
           {"type": "http_get", "url": "https://api.github.com/repos/example/two"}]
bodies = {1: b'{"name":"one","fixture":true}', 4: b'{"name":"two","fixture":true}'}
os.makedirs(os.path.join(out, "evidence"), exist_ok=True)
chain, prev = [], "0" * 64
for i, a in enumerate(actions, 1):
    ok, reason = ae.allowed(a, policy)
    rec = {"seq": i, "at": ae.now(), "agent": policy["agent"], "action": a, "policy_id": policy["policy_id"],
           "policy_sha256": ae.sha(ae.canon(policy)), "decision": "allowed" if ok else "denied",
           "decision_reason": reason}
    if ok:
        b = bodies[i]
        with open(os.path.join(out, "evidence", "action-%02d.bin" % i), "wb") as f:
            f.write(b)
        rec["result"] = {"status": 200, "bytes": len(b)}
        rec["evidence"] = {"file": "evidence/action-%02d.bin" % i, "sha256": ae.sha(b)}
    else:
        rec["result"] = {"blocked": True}
        rec["evidence"] = None
    rec["cost"] = ae.cost_usd(0.25 * i, rates)
    rec["prev_hash"] = prev
    rec["record_hash"] = ae.sha(ae.canon({k: v for k, v in rec.items() if k != "record_hash"}))
    prev = rec["record_hash"]
    chain.append(rec)
with open(os.path.join(out, "record.jsonl"), "w") as f:
    for r in chain:
        f.write(json.dumps(r, sort_keys=True) + "\n")
print("FIXTURE OK: %d records, head %s" % (len(chain), prev))
