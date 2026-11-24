# Procurement Replay Pack

This scripted demonstration uses a Python standard library verifier to check four bundled action records and their referenced response files offline after a public GitHub clone.

## Replay the recorded run

Use Git and Python 3. No GitHub account, package installation, model key, client data or payment is needed. From a terminal, run:

```text
git clone https://github.com/cincinnatus-management/action-evidence-pilot.git
cd action-evidence-pilot
git rev-parse HEAD
python action_evidence.py verify sample-run-output
```

Only the clone needs a network connection. The last command checks the saved evidence; it does not repeat the HTTP requests or run an AI model. If your system calls Python 3 `python3`, use that instead of `python`.

Expect exit code `0` and this line:

```text
VERIFY OK: 4 records, chain head 81e62ef666f97a857d480fda7bbf414963d06673e7867fc1ba195f9f716b2038
```

Record the commit printed by Git and compare both the record count and the full chain head. The chain head is the fingerprint at the end of the linked records. A `VERIFY OK` line with a different count or head is not a match for this sample. Keep the known count and head separately if you need to check the same evidence later.

## Read the evidence

The [record](../sample-run-output/record.jsonl) is dated 2026-11-23 UTC and has one line per requested action. The repository includes the [workflow](../workflow.json), [permission rules](../policy.json), [sample summary](../sample-run-output/summary.json), and the response files under `sample-run-output/evidence/`.

| Record | Requested action | Recorded outcome |
| --- | --- | --- |
| 1 | Read public GitHub metadata for `python/cpython` | Allowed; HTTP 200; response bytes saved and hashed |
| 2 | Read public GitHub metadata for `torvalds/linux` | Allowed; HTTP 200; response bytes saved and hashed |
| 3 | Read from an unlisted host | Denied; marked blocked; no response file |
| 4 | Write a file | Denied; marked blocked; no response file |

The records show the request, timestamp, demo agent label, policy ID and digest, decision, reason, outcome and estimated cost. The verifier checks the record hashes, their links and the digests of referenced evidence. Read the outcomes separately: even an allowed request that ended in a network error can have a valid record. The verifier does not recalculate decisions from the policy or validate `summary.json` or the reference-rate cost estimates.

## What the Canada guide asks for

The Treasury Board of Canada Secretariat’s [Guide on the Use of Agentic Artificial Intelligence](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-agentic-artificial-antelligence.html) gives guidance to federal departments and agencies. These are points of comparison, not a conformity assessment.

| Guide topic | What this sample shows | What it does not show |
| --- | --- | --- |
| [Section 4: Principles for responsible use](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-agentic-artificial-antelligence.html#toc4) calls for clear limits on what agents may do. | A fixed workflow records allow or deny decisions under a written read-only policy. | An agent-wide sandbox or proof that every action goes through the recorder. |
| [Section 5, during use, (g): Log key actions and decisions](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-agentic-artificial-antelligence.html#toc5-2) calls for recording tools, actions, approvals, and key inputs and outputs. | The sample records action types, inputs, times, rule decisions and outcomes, with hashes for the two retained responses. | Human approvals, independently authenticated identities or timestamps, or a full audit trail. |
| [Section 4: Recoverability](https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/generative-ai/guide-use-agentic-artificial-antelligence.html#toc4-2) calls for full logging in a system the agent cannot change. | A reviewer can check internal consistency and compare the sample to a separately trusted count and chain head. | The demo writes ordinary local files. The verifier alone does not establish completeness or rule out replacement of the whole record and its evidence. The pack does not show protected logging, live monitoring, a stop control or recovery. |

This demonstration does not establish conformity with the guide or show Government of Canada approval, endorsement or certification. It does not show a customer deployment or production assurance.
