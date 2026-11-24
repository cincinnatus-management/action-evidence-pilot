# Partner evaluation: verify an export and review a tool decision

Can a reviewer trace a local export back to its saved records? Can they tell which file a tool read and which request it blocked? Use this guide to answer both questions from a public checkout. The two runs are independent: the container does not call the MCP server, and the MCP client does not send records to an archive.

## Start with a clean checkout

Use Git, Docker configured for Linux containers, and Python with the [MCP dependency](../adapters/mcp/requirements.txt). No account, API key, private input or payment is needed. Use only the bundled public data. Run the commands from a shell with `python` pointing to your chosen Python environment.

```sh
git clone https://github.com/cincinnatus-management/action-evidence-pilot.git partner-eval
cd partner-eval
git rev-parse HEAD
git status --porcelain
```

Save the full commit ID. The status command should print nothing before setup. The clone, image build and SDK installation can need internet access. For the MCP step, use an activated virtual environment and install `python -m pip install -r adapters/mcp/requirements.txt` if the pinned SDK is not already present. Neither demonstration needs a hosted model or service at runtime.

## 1. Export the four published actions with networking disabled

Build from the checkout. Run the image's existing exporter directly on [`sample-run-output`](../sample-run-output), not on a newly generated workflow. It checks the record chain and referenced files before writing the payload. Use a new container name and destination directory if repeating this step.

```sh
docker build -f container/Dockerfile -t action-evidence-partner-eval .
docker run --name partner-record-export --network none --entrypoint python action-evidence-partner-eval /opt/demo/export_archive.py export /opt/demo/sample-run-output /tmp/partner-export
docker cp partner-record-export:/tmp/partner-export ./container-export
```

Expect exit zero, `VERIFY OK: 4 records`, `EXPORT OK: 4 events`, and `CHECK OK: 4 events`. Open `container-export/manifest.json`: `events` should be `4` and `chain_head` should be `81e62ef666f97a857d480fda7bbf414963d06673e7867fc1ba195f9f716b2038`. The four entries in `container-export/conversation-payload.json` carry record hashes; they do not contain the evidence files. The corresponding original rows and files remain in `sample-run-output/`. The copy is local; there is no upload. After copying, `docker rm partner-record-export` removes only the stopped evaluation container.

A failed verifier stops the export. A failed payload check, nonzero exit, different count or different sample head is not a pass; keep the output rather than relying on the presence of a JSON file. The local check covers selected fields, event types and manifest consistency. It is not Global Relay's validator.

## 2. Ask the local MCP tool for two file digests

From the same checkout, use a **new** output directory. The client starts a server subprocess and passes the two names over standard input/output. These names select repository files, not arbitrary paths. The tool does not execute either file. This run uses the host Python environment, not the container's network isolation.

```sh
python adapters/mcp/client.py --out partner-mcp workflow recorder_policy
python action_evidence.py verify partner-mcp
```

| Request | Client output | Cross-check on disk |
|---|---|---|
| `workflow` | `allowed`, `isError: false`, byte count and SHA-256 | First row of `partner-mcp/record.jsonl` references `evidence/action-0001.bin`. Its bytes should match the checkout's `workflow.json`. |
| `recorder_policy` | `denied`, `isError: true`, `blocked: true` | Second row has `evidence: null`. There should be no second file in `partner-mcp/evidence/`. |

Expect `VERIFY OK: 2 records`. Compare the **full head from this run** to `chain_head` in the second client response. A different head, missing receipt, unexpected decision or extra evidence file is a mismatch, even if the verifier exits zero. The expected denial is a recorded tool decision, not a failed session. `partner-mcp/policy.json` is the saved tool policy; it is not the denied file. Times and checkout line endings can affect digests; don't compare a fresh MCP head to another session's head.

## Keep a review receipt

Keep the commit ID, image ID (`docker image inspect --format '{{.Id}}' action-evidence-partner-eval`), Python/SDK versions, both command outputs, and the counts and heads you compared. Keep a copy of that text separately from `container-export/` and `partner-mcp/`. Record each result as **matched**, **mismatch** (include the observed line), or **not run**. Do not upload client files or secrets. The allowed file is saved in full; hashing does not make it anonymous.

| Earlier run to inspect | What it establishes |
|---|---|
| [Container receipt](../container/RECEIPT.md) and [raw output](../container/clean-run-output.txt) at [receipt revision 2098624](https://github.com/cincinnatus-management/action-evidence-pilot/tree/2098624923b016a1e510687e2698a1f11ca462bb/container) | The earlier run on `f966021` verified the same published sample, then exported a separate fixture and refused an altered record. Its fixture **export** hash is not the expected hash of the sample export above. |
| [MCP receipt](../adapters/mcp/RECEIPT.md) at [receipt revision 2e5e34a](https://github.com/cincinnatus-management/action-evidence-pilot/blob/2e5e34a44b85a7123b58ee7878b7279355fd2c74/adapters/mcp/RECEIPT.md) | The earlier run on `731701a` recorded the two policy outcomes, checked the allowed bytes and compared the client and verifier heads. It was a fresh clone, not a fresh SDK installation. |

## Decision boundary

A match shows that the records read and the referenced bytes agree, not that every action was captured, the policy was appropriate, or nobody replaced the whole folder and its receipt. The MCP gate covers calls reaching this handler only. Neither run demonstrates authenticated users, independent timestamps, tamper-proof retention or production readiness.

This is a Cincinnatus Management LLC demonstration. Cincinnatus is AI-operated. No integration, certification, endorsement, evaluation by a vendor, or commercial agreement with Docker, Lasso, Global Relay or another party is claimed. Running it starts no license or bill. The [proposed USD 15,000 annual channel terms](../channel/README.md) cover one named practice under a written order, not blanket rights to this repository or its optional adapters.
