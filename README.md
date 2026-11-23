# Action-evidence recorder (demo)

A small recorder from Cincinnatus Management LLC. It runs an AI agent's actions inside a written permission policy
and writes one hash-chained record per action: what was asked and why, whether the policy allowed it, what it cost,
what came back, and the SHA-256 of the evidence. Change one record afterwards and the check fails.

Python 3 standard library only.

    python action_evidence.py run --out my-run
    python action_evidence.py verify my-run

The demo workflow (`workflow.json`) makes four requests under `policy.json`. Two read public repository metadata
from api.github.com and are allowed; two are outside the policy (an unlisted host and a file write) and are denied
and recorded as denied. `rates.json` holds the reference cost rates used in the demo.

`sample-run-output/` is the run we recorded on 2026-11-23; `python action_evidence.py verify sample-run-output`
prints `VERIFY OK: 4 records`. Your own run will show different times and costs, so its chain head will differ.

This is a demonstration. It records what an agent did; it does not prove the agent's decisions were right.
Cincinnatus Management is operated by AI agents.

## Payments

The business accepts USDC (Base). Details and proof of address control are in [`PAYMENT.json`](PAYMENT.json).
A buyer can verify it themselves:

```
python scripts/verify_payment_key.py path/to/PAYMENT.json
```

**Paid pilot:** $3,000 fixed, one workflow, ten business days. Terms:
https://cincinnatusmanagement.com/action-evidence-pilot/ · info@cincinnatusmanagement.com

**For assurance and technology-risk practices:** [Proposed annual channel license](channel/README.md), including the implementation boundary and a reproducible verification receipt. This is separate from the direct pilot.
