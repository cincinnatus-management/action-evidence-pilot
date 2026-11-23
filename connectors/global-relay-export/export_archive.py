#!/usr/bin/env python3
"""Map a Cincinnatus action-evidence record folder to a Global Relay Open Connector
Conversation API v1.6 payload (LOCAL FILE ONLY - nothing is sent anywhere).

    python export_archive.py export RECORD_DIR OUT_DIR [--initiator-email E] [--initiator-name N]
    python export_archive.py check  OUT_DIR

Not a certified or production connector. No Global Relay credentials are used.
Standard library only.
"""
import hashlib, json, os, sys, uuid, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import action_evidence as ae  # the recorder; its verify() runs before any export

NS = uuid.UUID("6f1c2d0e-0000-5000-8000-00c1c1c1c1c1")  # fixed namespace -> repeatable ids
SPEC = "Global Relay Open Connector Conversation API v1.6 (public OpenAPI, /v2/conversations)"
EVENT_ENUM = {"File_transfer", "Invitation", "Message", "Admin_event", "User_joined", "User_left",
              "Message_edited", "Message_deleted", "User_removed", "User_event", "Reaction",
              "Meeting_event", "Context_reply"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(record_dir):
    with open(os.path.join(record_dir, "record.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def to_ms(iso):
    return int(datetime.datetime.fromisoformat(iso).timestamp() * 1000)


def message(rec):
    a = rec["action"]
    lines = ["Action-evidence record %d" % rec["seq"],
             "Agent: %s" % rec["agent"],
             "Action: %s %s" % (a.get("type"), a.get("url", a.get("path", ""))),
             "Policy: %s (sha256 %s)" % (rec["policy_id"], rec["policy_sha256"]),
             "Decision: %s - %s" % (rec["decision"], rec["decision_reason"]),
             "Result: %s" % json.dumps(rec["result"], sort_keys=True),
             "Cost USD: %.8f" % rec["cost"]["total_usd"]]
    ev = rec.get("evidence")
    lines.append("Evidence sha256: %s (%s)" % (ev["sha256"], ev["file"]) if ev else "Evidence: none")
    lines += ["Previous record hash: %s" % rec["prev_hash"], "Record hash: %s" % rec["record_hash"]]
    return "\n".join(lines)


def export(record_dir, out, email, name):
    ae.verify(record_dir)  # refuses to export a tampered folder (exits 1)
    recs = load(record_dir)
    head = recs[-1]["record_hash"]
    agent = recs[0]["agent"]
    agent_user = {"displayName": name or agent, "corporateEmail": email,
                  "companyName": "Cincinnatus Management LLC", "userType": "initiator", "identityType": "Bot"}
    policy_user = {"displayName": "Policy %s" % recs[0]["policy_id"],
                   "corporateEmail": email.replace("@", "+policy@", 1),
                   "companyName": "Cincinnatus Management LLC", "userType": "recipient", "identityType": "Bot"}
    payload = {
        "requestInfo": {"requestId": str(uuid.uuid5(NS, "req:" + head))},
        "conversationOverview": {
            "conversationId": str(uuid.uuid5(NS, "conv:" + head)),
            "initiatorName": agent_user["displayName"], "initiatorEmail": email,
            "title": "AI agent action-evidence log (%d actions)" % len(recs),
            "description": "Hash-chained record of actions taken by an AI agent under a written permission policy.",
            "isExternal": False, "isPrivate": True,
            "initialParticipants": [agent_user, policy_user],
            "conversationProperties": [
                {"name": "ChainHead", "value": head, "xheader": True, "hidden": False},
                {"name": "PolicyId", "value": recs[0]["policy_id"], "xheader": True, "hidden": False},
                {"name": "Source", "value": "cincinnatus-action-evidence", "xheader": True, "hidden": False}]},
        "conversationEvents": [{"eventTime": to_ms(r["at"]), "eventType": "Message",
                                "participants": [agent_user if r["decision"] == "allowed" else policy_user],
                                "content": {"textType": "plain", "message": message(r)}} for r in recs]}
    os.makedirs(out, exist_ok=True)
    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    with open(os.path.join(out, "conversation-payload.json"), "wb") as f:
        f.write(body)
    with open(os.path.join(record_dir, "record.jsonl"), "rb") as f:
        src_hash = sha(f.read())
    manifest = {"spec": SPEC,
                "status": "local export only; not submitted, not certified, not a production connector",
                "events": len(recs), "chain_head": head, "payload_sha256": sha(body),
                "source_record_sha256": src_hash,
                "not_mapped": ["evidence files (would need Files endpoint upload + fileKey; hashes carried in text instead)"]}
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("EXPORT OK: %d events -> %s (payload sha256 %s)" % (len(recs), out, manifest["payload_sha256"]))
    check(out)


def check(out):
    """Structural check of the payload against required fields/enums of the v1.6 public schema."""
    with open(os.path.join(out, "conversation-payload.json"), "rb") as f:
        body = f.read()
    with open(os.path.join(out, "manifest.json")) as f:
        m = json.load(f)
    p = json.loads(body)
    bad = []
    if sha(body) != m["payload_sha256"]:
        bad.append("payload hash differs from manifest")
    for k in ("requestInfo", "conversationOverview"):
        if k not in p:
            bad.append("missing " + k)
    ov = p.get("conversationOverview", {})
    for k in ("conversationId", "initiatorEmail", "initiatorName"):
        if not ov.get(k):
            bad.append("overview missing " + k)
    for u in ov.get("initialParticipants", []):
        for k in ("displayName", "corporateEmail"):
            if not u.get(k):
                bad.append("participant missing " + k)
    for pr in ov.get("conversationProperties", []):
        if "name" not in pr or "value" not in pr:
            bad.append("property needs name+value")
    for i, e in enumerate(p.get("conversationEvents", [])):
        if e.get("eventType") not in EVENT_ENUM:
            bad.append("event %d bad eventType" % i)
        t = e.get("eventTime")
        if not isinstance(t, int) or t < 631152000000:
            bad.append("event %d bad eventTime" % i)
        if not e.get("content", {}).get("message"):
            bad.append("event %d no message" % i)
    if len(p.get("conversationEvents", [])) != m["events"]:
        bad.append("event count != manifest")
    if bad:
        print("CHECK FAILED:")
        for b in bad:
            print("  -", b)
        sys.exit(1)
    print("CHECK OK: %d events, required fields/enums of %s present" % (m["events"], SPEC))


if __name__ == "__main__":
    a = sys.argv[1:]

    def opt(n, d):
        return a[a.index(n) + 1] if n in a else d

    if len(a) >= 3 and a[0] == "export":
        export(a[1], a[2], opt("--initiator-email", "action-evidence-agent@example.invalid"), opt("--initiator-name", None))
    elif len(a) == 2 and a[0] == "check":
        check(a[1])
    else:
        print(__doc__)
