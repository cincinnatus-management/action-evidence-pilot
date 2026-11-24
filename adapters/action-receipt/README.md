# Verify four signed policy decisions

This evaluation adds Ed25519 signatures to a fresh run of the existing recorder. A buyer can check that the supplied key signed each policy decision, that the decisions are in order, and that the source log and saved response bytes match what was signed. The signed object is a **bare action receipt**, not a SCITT Transparency Receipt. The format is taken from [draft-noa-scitt-ai-agent-receipt-01 §§3–5](https://datatracker.ietf.org/doc/html/draft-noa-scitt-ai-agent-receipt-01#section-4.2), an individual Internet-Draft. This is neither IETF approval nor certification. See [field mapping and limits](MAPPING.md).

## Check the published run offline

Clone `https://github.com/cincinnatus-management/action-evidence-pilot.git`. From its root, use Python 3 in a virtual environment with `python -m pip install PyNaCl==1.6.2`. Only setup and generating new network observations require network access. Verification reads local files. Run:

```
python adapters/action-receipt/receipt.py verify adapters/action-receipt/example b77f6ca85dfebad0c0db4143dac3dd4180f8abdd59dcb275ff2f04c65ce0790c sha256:b36c4804987cac357642854043316a095b9ea6b6494c8edcea479b6f1f0eeb40
```

Expected first line: `VERIFIED 4 bare receipts | draft-noa-scitt-ai-agent-receipt-01 | pinned key and head | sha256:b36c4804987cac357642854043316a095b9ea6b6494c8edcea479b6f1f0eeb40`. `example/receipts.jsonl` is the signed output. The original evidence is alongside it. The plain recorder summary is not a signed receipt.

## Generate your own run

```
python adapters/action-receipt/receipt.py generate my-new-run
```

Use a new directory. The adapter invokes the original four requests under the bundled policy, then signs the recorded decisions. It prints `PIN (retain separately):` followed by a public key and a terminal hash. Use both values, in that order, with `python adapters/action-receipt/receipt.py verify my-new-run PUBLIC_KEY TERMINAL_HASH`. Two decisions allow public reads; the unlisted host and file write are blocked. If a permitted fetch fails, its error remains in the source log; `ALLOWED` still means permission, not success. Keys, timestamps, responses and hashes vary across runs. No private key is saved. Don't use this example for confidential inputs; public argument hashes do not hide guessable values.

## What to trust

Keep the key and head outside the bundle. For the published example the pins above come from this repository: use an independently trusted revision or channel before relying on them. A party able to replace both the bundle and the pins can substitute another run. The signature binds the adapter's account of a decision, not a person's identity, an independent outcome, or whether the agent was correct. There is no trusted clock, pre-action witness or external log checkpoint. This evaluation does not change the terms of the [existing pilot](https://cincinnatusmanagement.com/action-evidence-pilot/).
