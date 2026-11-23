# From demonstration to a client evidence folder

Use the demo to decide whether the record is useful. Do not put a live client workflow into it unchanged. The channel [terms](README.md) cover use by the practice; the practice remains responsible for the client deployment.

## Run it without client data

From a terminal with Git and Python 3, start in an unused directory:

```text
git clone https://github.com/cincinnatus-management/action-evidence-pilot.git
cd action-evidence-pilot
git checkout --detach 532b9bac9ee30b926f29678406a3318faa2559a5
python action_evidence.py verify sample-run-output
python action_evidence.py run --out my-run
python action_evidence.py verify my-run
```

The first verification works locally on the published folder. Generating a fresh folder makes public network requests; use a new output directory. Check the action results as well as the final line: an allowed request with a network error can still have a consistent record. The [clean-run receipt](VERIFICATION.md) gives actual results for comparison. A fresh chain head is not expected to match the sample.

## Divide the work before capture

| Step | Responsible party and decision |
|---|---|
| Define the boundary | The practice and client name the workflow, agent, action entry points and actions that bypass the recorder. List approved destinations, request fields and response bytes allowed to be retained. Obtain permission from the data owner. If sensitive material cannot be excluded before writing, do not run that workflow. |
| Install and control | The practice maps the approved action path into the recorder in the client's environment, selects or builds the integration separately, sets its own rates, and restricts filesystem and network access. The demo is a specific read-only workflow, not an agent-wide sandbox or a ready-made production integration. |
| Capture and reconcile | For an authorized run, retain the policy, rate inputs, recorder revision, `record.jsonl`, referenced `evidence/` files and `summary.json`. The practice compares observed decisions, results and action count with the agreed workflow. A denied request is not an executed action; cost from reference rates is an estimate, not a supplier invoice. |
| Hand over and retain | Give the client its authorized folder and verifier instructions. Separately retain the expected record count and chain head in a location the recorder cannot rewrite; compare both on later checks. Agree who controls access, encryption, retention and disposal. Do not send raw records to Cincinnatus for routine support. |

## What a pass means

`verify` recomputes the hashes of the records it reads, checks links to preceding records, and checks referenced evidence bytes. It does **not** validate `summary.json`, independently authenticate an actor or timestamp, or establish that every relevant action passed through the recorder. Without a separately trusted head and count it does not establish completeness. It does not decide whether a policy was appropriate, a cost was billed, an AI answer was right or a client complied with a standard. Assurance judgments and sign-off stay with the practice.

**Technical basis:** pinned [recorder and verifier](https://github.com/cincinnatus-management/action-evidence-pilot/blob/532b9bac9ee30b926f29678406a3318faa2559a5/action_evidence.py#L46-L123), [demo workflow](https://github.com/cincinnatus-management/action-evidence-pilot/blob/532b9bac9ee30b926f29678406a3318faa2559a5/workflow.json), [permission policy](https://github.com/cincinnatus-management/action-evidence-pilot/blob/532b9bac9ee30b926f29678406a3318faa2559a5/policy.json) and [reference rates](https://github.com/cincinnatus-management/action-evidence-pilot/blob/532b9bac9ee30b926f29678406a3318faa2559a5/rates.json). Operational steps above are proposed deployment responsibilities, not claims of an existing client installation.
