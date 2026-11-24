# Read an action receipt in self-hosted Phoenix

Can a reviewer tell a denied action from a completed read after the receipt leaves the recorder? Yes, for this public receipt and Phoenix 22.0.1. The existing [OTLP mapper](../opentelemetry/README.md) produces one span. This separate demo sends the original binary payload to a local Phoenix server, then asks Phoenix for the stored span. No Phoenix account, paid service, API key or model is needed. Installation needs access to the Python packages.

## Run it on Windows

From the root of a checkout containing this guide, use Python 3.12 and `uv`. The dependency list records the Windows environment used here. Use an output directory that does not already exist.

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe --only-binary :all: -r adapters/phoenix/windows-py312.txt
.venv/Scripts/python.exe adapters/phoenix/local_proof.py phoenix-run
```

The script verifies `prospective/example`, checks the projected bytes against their published SHA-256, starts Phoenix with a new local store and loopback ports, then posts the payload to `/v1/traces` with `Content-Type: application/x-protobuf`. The `x-project-name` header routes it to `action-evidence-local` without changing the projection. A `200` only acknowledges the request. The script waits for `GET /v1/projects/action-evidence-local/spans`, saves the response in `phoenix-run/readback.json`, compares it with the projected span, and stops its server. `receipt.pb`, the store and the log remain in `phoenix-run` for inspection. The script has no remote destination or private-receipt option.

## What to look for in the readback

| Sequence | What Phoenix returns | Why it matters |
|---|---|---|
| 0 | Session start | Opens the recorded sequence. |
| 1 | Deny `action-02.bin` | A decision, not a completed read. |
| 2 | Allow `action-01.bin` | Shares the policy digest with the deny. |
| 3 | Read `action-01.bin`, 5,996 bytes | Its `cincinnatus.authorization_record_id` equals the allow's `cincinnatus.record_id`, not the deny's. The result digest is present, not the file contents. |
| 4 | Session end | Carries the count and session digest. |

A successful run compares the trace and span IDs, span bounds and projected span attributes, and each event's name, order, timestamp and attributes. Phoenix reports its OpenInference span kind as `UNKNOWN`. The source is a generic OTLP `INTERNAL` span, not a model or tool call. This is a field-level check, not a claim that Phoenix returns the original protobuf or all resource and instrumentation-scope metadata.

## When to use it

Use the projection if your team already runs Phoenix and wants to review which read a policy authorized. Keep the original receipt, result, trusted verifier and any independently saved decision head: Phoenix displays the recorder's evidence; it does not enforce policy, authenticate authorship or independently witness the read. Before considering real records, review who can read project data and backups, retention, and whether filenames, reasons, IDs and linkable hashes may leave the recorder. This disposable loopback configuration is not a production deployment guide.

Phoenix is separately licensed under [Elastic License 2.0](https://github.com/Arize-ai/phoenix/blob/ed7154638bf53e7559a711a60d705f31ab0412e6/LICENSE). This demonstration uses a buyer-operated local copy; it does not offer Phoenix as a hosted or managed service or grant rights to resell it. ELv2 restricts providing third parties hosted or managed access to a substantial set of its features. See also the official [local server guide](https://arize.com/docs/phoenix/self-hosting/deployment-options/terminal), [OTLP project routing](https://github.com/Arize-ai/phoenix/blob/ed7154638bf53e7559a711a60d705f31ab0412e6/docs/phoenix/release-notes/05-2026/05-08-2026-otlp-project-header.mdx), and [HTTP ingestion handler](https://github.com/Arize-ai/phoenix/blob/ed7154638bf53e7559a711a60d705f31ab0412e6/src/phoenix/server/api/routers/v1/traces.py). This result covers the pinned local server and published receipt only. It does not establish Arize endorsement, partner status, hosted-service compatibility or a customer deployment.
