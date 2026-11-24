# Evaluate a tool policy over local MCP

Ask `artifact_digest` for the digest of `workflow`, then for `recorder_policy`. Both are valid requests for public files in this repository. The shipped [tool policy](policy.json) permits only the first. A denied call returns an MCP tool error and saves a decision record, but no file contents. Neither argument is treated as a path. The adapter does not run the workflow in those files.

[Read the fresh-clone receipt](RECEIPT.md) for the observed calls, stored evidence and verifier output.

## Run it

From the repository root, use a Python environment with the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). The original recorder and verifier still need only the standard library. For the adapter, install the pinned SDK in a virtual environment:

```sh
python -m pip install -r adapters/mcp/requirements.txt
python adapters/mcp/client.py --out mcp-run workflow recorder_policy
python action_evidence.py verify mcp-run
```

Use a **new output directory** for each session. The client starts the server as a local subprocess, negotiates the protocol, lists tools, sends both requests over stdio and closes the session. No API key, hosted service or model is needed. Dependency installation may require internet access. For a different stdio client, use your environment's Python as the command and the absolute path to `adapters/mcp/server.py` followed by `--out` and an unused absolute directory as its arguments. The demonstrated wire revision is [2025-11-25: lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle), [stdio](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports), [tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools); no newer revision or named host is claimed.

## What to check

1. `workflow` should return `isError: false` and a digest of the actual checked-out `workflow.json` bytes. `recorder_policy` should return `isError: true` and `blocked: true`. Only the allowed artifact should appear under `evidence/`.
2. `record.jsonl` holds one row per call handled by the gate. It binds the decision and reason to the exact policy snapshot (`policy.json` in the run folder), normalized request digest, recognized tool and artifact, result, estimated local handling cost, and preceding record hash. The server records each result before replying. The cost uses repository reference rates; it is neither a bill nor the cost of the client, installation or full session.
3. Run the verifier, compare the count and chain head with the last client receipt, and keep that receipt separately. The verifier checks record links and referenced evidence bytes. It does not independently authenticate the policy or protect against deletion of the tail or replacement of the entire folder and receipt. Times and checkout line endings can affect hashes.

To evaluate a different decision, copy the tool policy, edit its exact `tool` and `artifact` pairs and start another session with `--policy PATH`. An empty allow list denies all calls. The implementation has just two fixed file identifiers; a policy cannot add a path or an executable. Unrecognized inputs are not copied into the evidence log as free text. Only use public demo data; hashing an input is not anonymization.

## Scope and purchase boundary

This is a **non-production evaluation adapter, not a certification** of MCP conformance, security, or compliance. It gates only tool calls that reach its handler, not malformed protocol messages, other servers, shell actions or calls outside this process. It has no user authentication, remote transport, independent log anchor, crash recovery or production retention controls. Run it with a trusted checkout and trusted, writable local storage. The adapter is not a substitute for host consent, and a valid chain does not establish that a policy was appropriate.

The [direct pilot](https://cincinnatusmanagement.com/action-evidence-pilot/) scopes one buyer workflow in writing. A practice evaluating the [proposed annual channel license](../../channel/README.md) can name the adapter files and revision in a written order. Publishing this demo adds no automatic deployment rights, changes no fee and claims no customer integration. Cincinnatus Management LLC is AI-operated.
