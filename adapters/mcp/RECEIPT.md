# Fresh-clone receipt: local MCP tool calls

Cincinnatus Management LLC, 2026-11-24 05:38 UTC. We cloned the public repository and checked out [731701a](https://github.com/cincinnatus-management/action-evidence-pilot/commit/731701aecdb7b2585bb90288cfb28ddd0ed5fd66). The working tree was clean before the run. This was a fresh checkout, not a fresh Python installation: the host had Python 3.14.7 and `mcp` 1.30.0 installed.

```sh
git clone https://github.com/cincinnatus-management/action-evidence-pilot.git replay-clone
cd replay-clone
git checkout --detach 731701aecdb7b2585bb90288cfb28ddd0ed5fd66
python adapters/mcp/client.py --out mcp-run workflow recorder_policy
python action_evidence.py verify mcp-run
```

The client connected over stdio, negotiated `2025-11-25` and listed `artifact_digest`.

| Call | Argument | Tool response | Saved evidence |
|---|---|---|---|
| 1 | `workflow` | Allowed, `isError: false`, 484 bytes | `evidence/action-0001.bin`, identical to the checked-out `workflow.json` |
| 2 | `recorder_policy` | Denied, `isError: true`, `blocked: true` | None |

The two stored rows matched the digest of the saved policy. The evidence directory contained only the first call's file. The last client receipt and the repository verifier reported the same head:

```text
VERIFY OK: 2 records, chain head a25a671afc6f8a1e88bb8f4d4a42464940dfdf954d2f6d1069e44f41e2f7736a
```

Compare the client and verifier in **your** run; timestamps make the head change. See the [adapter guide](README.md) for setup, licensing scope and limits. This is not a production deployment or a certification.
