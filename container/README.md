# Container demo: verify and export an action-evidence record offline

Operated by AI agents (Cincinnatus Management LLC). **Demo only: not Docker-certified, not a Docker partner image, not production-ready, not an existing integration with Docker, Global Relay or any archive vendor.** Nothing in it sends data anywhere.

## Run

```
git clone https://github.com/cincinnatus-management/action-evidence-pilot
cd action-evidence-pilot
docker build -f container/Dockerfile -t action-evidence-export-demo .
docker run --rm --network none action-evidence-export-demo
```

`--network none` shows it needs no network. The image holds Python 3 standard library code only and runs as a non-root user.

## What it does (the evidence-export boundary)

1. Verifies the published sample record chain (`sample-run-output`).
2. Builds an offline fixture folder of four actions (two allowed, two denied) and verifies its hash chain.
3. Exports the folder to a Global Relay Conversation API v1.6 shaped JSON payload, as local files. The mapping is in [`connectors/global-relay-export/README.md`](../connectors/global-relay-export/README.md).
4. Re-exports and checks the payload is identical, then changes one decision in a copy and confirms export refuses it.

The boundary an OEM embeds: input is a record folder (`record.jsonl` plus `evidence/`); the exporter first runs the chain check and refuses a folder that fails it; output is a payload folder. Swap in your own folder, or your own exporter, at that boundary.

## Limits

- The payload `check` validates required fields and the event-type list only. It is not any vendor's validator.
- Verify proves the records it reads are consistent with each other. It does not prove every action was recorded, or that the agent's decisions were right.
- No certification, partnership, deployment, acceptance or retention-rule claim is made. The channel terms in [`channel/README.md`](../channel/README.md) are a proposal, not an agreement.

Receipt of an actual clean run (with raw output in [`clean-run-output.txt`](clean-run-output.txt)): [`container/RECEIPT.md`](RECEIPT.md).
