# Clean-run receipt | public demo only

At 22:57 UTC on 2026-11-23, Cincinnatus ran the public demo from a separate fresh Git clone of [revision 532b9bac](https://github.com/cincinnatus-management/action-evidence-pilot/tree/532b9bac9ee30b926f29678406a3318faa2559a5) with Python 3.14.7. The fresh run used live public GitHub metadata, not client data or the saved sample as input. This was a reproducibility check by the publisher, not a third-party audit, client deployment or acceptance.

| Command | Observed result |
|---|---|
| `python action_evidence.py verify sample-run-output` | Exit 0. `VERIFY OK: 4 records, chain head 81e62ef666f97a857d480fda7bbf414963d06673e7867fc1ba195f9f716b2038` |
| `python action_evidence.py run --out my-run` | Exit 0. Four action records: two allowed reads, both HTTP 200; two denied requests recorded as blocked. |
| `python action_evidence.py verify my-run` | Separate invocation, exit 0. `VERIFY OK: 4 records, chain head 7ce22b69b36137a288f1611690e08c71ac7422d0b077641e83479c7ac0191abd` |

[Published sample](https://github.com/cincinnatus-management/action-evidence-pilot/tree/532b9bac9ee30b926f29678406a3318faa2559a5/sample-run-output) · [Reproduce the check and interpret its limits](IMPLEMENTATION.md)
