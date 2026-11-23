#!/usr/bin/env python3
"""Cincinnatus action-evidence recorder (demo).

Runs a list of agent actions inside a written permission policy and writes one
hash-chained record per action: who/what was asked, whether the policy allowed
it, what it cost, what came back, and the SHA-256 of the evidence.
Standard library only. Usage:

    python action_evidence.py run  [--out DIR]      run the demo workflow
    python action_evidence.py verify DIR             re-check a record folder
"""
import hashlib, json, os, sys, time, urllib.request, urllib.parse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def cost_usd(seconds, rates, model_tokens_in=0, model_tokens_out=0):
    """Cost of one action = machine time + model tokens. Every term is shown."""
    kwh = rates["machine_watts"] / 1000.0 * seconds / 3600.0
    power = kwh * rates["usd_per_kwh"] * rates["cooling_multiplier"]
    wear = seconds / 3600.0 * rates["hardware_usd_per_hour"]
    net = seconds / 3600.0 * rates["internet_usd_per_hour"]
    model = (model_tokens_in * rates["model_usd_per_1m_in"] + model_tokens_out * rates["model_usd_per_1m_out"]) / 1e6
    return {
        "seconds": round(seconds, 3),
        "power_usd": round(power, 8),
        "hardware_wear_usd": round(wear, 8),
        "internet_usd": round(net, 8),
        "model_usd": round(model, 8),
        "total_usd": round(power + wear + net + model, 8),
    }


def allowed(action, policy):
    """Return (ok, reason). Deny by default."""
    if action["type"] == "http_get":
        u = urllib.parse.urlparse(action["url"])
        for rule in policy["allow"]["http_get"]:
            if u.scheme == "https" and u.netloc == rule["host"] and u.path.startswith(rule["path_prefix"]):
                return True, "matched allow rule %s%s" % (rule["host"], rule["path_prefix"])
        return False, "no allow rule for %s%s" % (u.netloc, u.path)
    if action["type"] == "write_file":
        return False, "write_file is not in the allow list (read-only policy)"
    return False, "action type %r not in policy" % action["type"]


def run(out):
    policy = json.load(open(os.path.join(HERE, "policy.json")))
    rates = json.load(open(os.path.join(HERE, "rates.json")))
    actions = json.load(open(os.path.join(HERE, "workflow.json")))
    os.makedirs(os.path.join(out, "evidence"), exist_ok=True)
    chain, prev = [], "0" * 64
    for i, a in enumerate(actions, 1):
        t0 = time.time()
        ok, reason = allowed(a, policy)
        rec = {"seq": i, "at": now(), "agent": policy["agent"], "action": a,
               "policy_id": policy["policy_id"], "policy_sha256": sha(canon(policy)),
               "decision": "allowed" if ok else "denied", "decision_reason": reason}
        if ok:
            req = urllib.request.Request(a["url"], headers={"User-Agent": "cincinnatus-action-evidence/1", "Accept": "application/json, text/html"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    body = r.read(policy["max_bytes"])
                    rec["result"] = {"status": r.status, "bytes": len(body)}
                path = os.path.join(out, "evidence", "action-%02d.bin" % i)
                open(path, "wb").write(body)
                rec["evidence"] = {"file": "evidence/action-%02d.bin" % i, "sha256": sha(body)}
            except Exception as e:  # recorded, not hidden
                rec["result"] = {"error": type(e).__name__ + ": " + str(e)[:200]}
                rec["evidence"] = None
        else:
            rec["result"] = {"blocked": True}
            rec["evidence"] = None
        rec["cost"] = cost_usd(time.time() - t0, rates)
        rec["prev_hash"] = prev
        rec["record_hash"] = sha(canon({k: v for k, v in rec.items() if k != "record_hash"}))
        prev = rec["record_hash"]
        chain.append(rec)
    with open(os.path.join(out, "record.jsonl"), "w") as f:
        for rec in chain:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
    summary = {
        "actions": len(chain),
        "allowed": sum(r["decision"] == "allowed" for r in chain),
        "denied": sum(r["decision"] == "denied" for r in chain),
        "total_cost_usd": round(sum(r["cost"]["total_usd"] for r in chain), 8),
        "chain_head": prev,
    }
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=2)
    print(json.dumps(summary, indent=2))
    verify(out)


def verify(out):
    prev, n, bad = "0" * 64, 0, []
    for line in open(os.path.join(out, "record.jsonl")):
        rec = json.loads(line)
        n += 1
        if rec["prev_hash"] != prev:
            bad.append("seq %d: chain link broken" % rec["seq"])
        if sha(canon({k: v for k, v in rec.items() if k != "record_hash"})) != rec["record_hash"]:
            bad.append("seq %d: record altered" % rec["seq"])
        ev = rec.get("evidence")
        if ev:
            p = os.path.join(out, ev["file"])
            if not os.path.exists(p) or sha(open(p, "rb").read()) != ev["sha256"]:
                bad.append("seq %d: evidence file altered or missing" % rec["seq"])
        prev = rec["record_hash"]
    if bad:
        print("VERIFY FAILED:"); [print("  -", b) for b in bad]; sys.exit(1)
    print("VERIFY OK: %d records, chain head %s" % (n, prev))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "run":
        out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "run-output"
        run(out)
    elif len(sys.argv) == 3 and sys.argv[1] == "verify":
        verify(sys.argv[2])
    else:
        print(__doc__)
