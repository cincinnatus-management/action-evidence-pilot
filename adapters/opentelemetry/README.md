# Read a pre-execution decision as an OpenTelemetry trace

**Mapping 1.0.0** takes one closed `cincinnatus.prospective/1` receipt and writes one binary OTLP `ExportTraceServiceRequest` to a new file. It runs the [original verifier](../../prospective/README.md) on a private snapshot first. The trace is an index into the verified evidence, not a replacement for it. Nothing is sent to a collector or partner.

## Reproduce the published example

From the repository root, use a fresh Python 3.14 environment. Install the pinned bindings once; both commands after installation work offline. Choose a new output filename on each run.

```sh
python -m pip install -r adapters/opentelemetry/requirements.txt
python adapters/opentelemetry/project.py prospective/example receipt.pb
python adapters/opentelemetry/inspect_trace.py receipt.pb
```

The separate reader uses the OpenTelemetry protobuf type, not the mapper or the source receipt. Expect a `cincinnatus.receipt_session` span with five ordered events: start, deny `action-02.bin`, allow `action-01.bin`, read 5,996 bytes from `action-01.bin`, end. Match `authorization_record_id` on the read to `record_id` on the allow, not to the deny. Add `--full` to the reader command to inspect every field. With the published example and pinned encoder, the output file's SHA-256 is `5c8d2fd542e92365f441dce5c452a31436e4583329b12274601a50420754de59`.

To observe timing rather than replay it, follow the [paused recorder procedure](../../prospective/README.md). Keep the decision head outside the run directory **before** releasing the read. After close, supply that directory to `project.py` in place of `prospective/example` and add `--decision-head YOUR_SAVED_HASH`. A prefix alone is not exportable as a completed session. New runs have new identities and timestamps; do not expect the example checksum.

## Mapping contract

The [GenAI execute-tool convention](https://github.com/open-telemetry/semantic-conventions-genai/blob/ae8214a8f3a98786071736855093b74621174dc4/docs/gen-ai/execute-tool.md) describes tool execution. Here the recorder gates its own file read: there is no observed GenAI caller, model, provider or tool call. This uses the generic [OTLP trace message](https://github.com/open-telemetry/opentelemetry-proto/blob/v1.11.1/opentelemetry/proto/trace/v1/trace.proto), not `gen_ai.*`. The separate MCP replay is not an input to this mapping.

| Receipt or mapping input | Trace field and interpretation |
|---|---|
| One verified, closed session | One root `INTERNAL` span, status unset. A deny is a policy outcome, not a span error. `service.name` is the mapper's fixed label for the recorder; scope `cincinnatus.prospective.projection`, version `1.0.0`. No parent span or external context is inferred. |
| `session_id`; first `record_id` | UUID bytes become the 16-byte trace ID; first eight bytes of the opening record UUID become the span ID. These are replay identifiers, not upstream trace context. Full session UUID and input `detail.schema` remain string span attributes. |
| `timestamp`, `event` | First and last timestamps bound the session, **not** read latency. Each row yields one event named `cincinnatus.` + its event name at its recorded UTC time, converted exactly to Unix nanoseconds. Source precision is microseconds; use sequence to break ties. |
| Every row | Event attributes `cincinnatus.seq` (integer), `phase`, `record_id`, and, where present, `parent_record_id` and `prev_hash`. `record_sha256` hashes the original row bytes without the newline. All custom keys, including span and detail keys, have the `cincinnatus.` prefix. |
| `session_start.detail` | `recorder`, `recording_mode`, `policy_sha256`; policy body omitted. |
| `policy_decision.detail` | `operation`, `artifact`, `decision`, `reason`, `policy_sha256`. Neither decision attests to a completed read. |
| `read_result.detail` | `operation`, `artifact`, `authorization_record_id`, `status`, `bytes` (integer), `sha256` (result digest). Never the result bytes. |
| `session_end.detail` | `record_count` (integer), `session_hash` (digest of preceding raw record digests, not the hash of the close row). All attributes not identified as integers are strings. |

## Buyer evaluation

- **2021.AI — governance review:** Can a reviewer identify the policy digest used for both decisions, then follow the read back to its authorization and the exact source row? Compare `record_sha256` with the original trail. A dashboard that only says “allowed” loses the distinction between permission and execution.
- **Openlayer — monitoring and evidence:** Can an evaluator count two policy decisions but only one completed read, retain the link to the allow record, and show no read result linked to the deny? If an import drops event attributes, it is insufficient for that evaluation. The same payload and reader are enough to assess the field requirements before building an importer.

Neither vendor was used to ingest this trace. This is not a native integration or OpenTelemetry certification. The recorder is local and self-reported; a closed chain does not authenticate the author, attest to host-wide enforcement, or independently prove wall-clock ordering. Keep the original receipt, result, trusted checkout and any separately observed decision head. Before sharing telemetry beyond this public example, review artifact names, reasons, IDs and digest linkability against the recipient's retention and access policy.
