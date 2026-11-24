"""Local MCP stdio gate for the repository's own public files."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
import time

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from action_evidence import canon, cost_usd, now, sha

TOOL = "artifact_digest"
FILES = {"workflow": ROOT / "workflow.json", "recorder_policy": ROOT / "policy.json"}
SCHEMA = {"type": "object", "properties": {"artifact": {"type": "string", "enum": list(FILES)}},
          "required": ["artifact"], "additionalProperties": False}


def load_policy(path):
    policy = json.loads(path.read_bytes())
    if (not isinstance(policy, dict) or set(policy) != {"policy_id", "allow"}
            or not isinstance(policy["policy_id"], str) or not policy["policy_id"]
            or not isinstance(policy["allow"], list)):
        raise ValueError("expected a policy_id and an allow list")
    for rule in policy["allow"]:
        if rule not in [{"tool": TOOL, "artifact": key} for key in FILES]:
            raise ValueError("unknown allow rule")
    return policy


async def serve(out, policy_path):
    policy = load_policy(policy_path)
    rates = json.loads((ROOT / "rates.json").read_bytes())
    out.mkdir()  # Never append a second session to an existing run.
    (out / "evidence").mkdir()
    (out / "policy.json").write_bytes(canon(policy))
    server = Server("cincinnatus-action-evidence")
    seq, prev, healthy = 0, "0" * 64, True

    @server.list_tools()
    async def list_tools():
        return [types.Tool(name=TOOL, description="Hash a bundled public artifact if local policy permits.", inputSchema=SCHEMA)]

    # Check the complete argument shape inside the gate so schema denials get recorded too.
    @server.call_tool(validate_input=False)
    async def call(name, arguments):
        nonlocal seq, prev, healthy
        if not healthy:
            raise RuntimeError("recording unavailable; start a new run")
        start = time.monotonic()
        key = arguments.get("artifact")
        known = isinstance(key, str) and key in FILES
        if name != TOOL:
            reason = "unknown tool"
        elif set(arguments) != {"artifact"} or not known:
            reason = "invalid arguments"
        elif {"tool": name, "artifact": key} not in policy["allow"]:
            reason = "no matching allow rule"
        else:
            reason = "matched exact tool and artifact"
        allowed = reason == "matched exact tool and artifact"
        n = seq + 1
        action = {"type": "mcp.tools/call", "tool": TOOL if name == TOOL else "<unknown>",
                  "artifact": key if known else None,
                  "request_sha256": sha(canon({"name": name, "arguments": arguments}))}
        evidence = None
        result = {"blocked": True}
        # No await in the read-and-append section: one writer in this event loop.
        try:
            if allowed:
                try:
                    body = FILES[key].read_bytes()
                except OSError:
                    result = {"error": "could not read bundled artifact"}
                else:
                    rel = "evidence/action-%04d.bin" % n
                    (out / rel).write_bytes(body)
                    evidence = {"file": rel, "sha256": sha(body)}
                    result = {"bytes": len(body), "sha256": evidence["sha256"]}
            rec = {"seq": n, "at": now(), "agent": "local-mcp-adapter", "action": action,
                   "policy_id": policy["policy_id"], "policy_sha256": sha(canon(policy)),
                   "decision": "allowed" if allowed else "denied", "decision_reason": reason,
                   "result": result, "evidence": evidence, "cost": cost_usd(time.monotonic() - start, rates),
                   "prev_hash": prev}
            rec["record_hash"] = sha(canon(rec))
            with (out / "record.jsonl").open("ab") as f:
                f.write(canon(rec) + b"\n")
                f.flush()
                os.fsync(f.fileno())
        except OSError:
            healthy = False
            raise RuntimeError("evidence write failed; retire this run") from None
        seq, prev = n, rec["record_hash"]
        reply = {"seq": seq, "decision": rec["decision"], "reason": reason, "result": result, "chain_head": prev}
        return types.CallToolResult(isError=not allowed or "error" in result,
                                    content=[types.TextContent(type="text", text=json.dumps(reply))])

    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=HERE / "policy.json")
    args = parser.parse_args()
    asyncio.run(serve(args.out, args.policy))
