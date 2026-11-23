# Action-evidence -> Global Relay Open Connector export (local proof)

Status: local file export only. Not a production connector, not certified, not a Global Relay partner,
nothing sent to Global Relay. No Global Relay credentials or sandbox were used (none exist).

## Run (clean dir, Python 3 stdlib only)

    bash run_clean.sh          # copies the .py files (recorder from ../../action_evidence.py) to a fresh temp dir and runs everything below
    python -I make_fixture.py fixture            # offline 4-action record folder (2 allowed, 2 denied)
    python -I action_evidence.py verify fixture  # recorder's own hash-chain check
    python -I export_archive.py export fixture bundle
    python -I export_archive.py check bundle

`action_evidence.py` is the recorder in the repository root (copy it next to these files, or run from a folder that holds all four files).
Export refuses a folder that fails the chain check (tamper test in run_clean.sh).

## Mapping (target: public Conversation API v1.6, POST /v2/conversations, one conversation -> one EML)

| Source (record.jsonl)        | Target                                                              |
|------------------------------|---------------------------------------------------------------------|
| chain head                   | requestInfo.requestId and conversationId (uuid5 of head: repeatable); property ChainHead |
| agent                        | conversationOverview.initiatorName, participant (identityType Bot)  |
| policy_id                    | property PolicyId; policy participant (recipient, Bot)              |
| each record                  | one conversationEvents[] item, eventType Message                    |
| `at`                         | eventTime (epoch ms)                                                |
| action/decision/result/cost/evidence sha256/prev+record hash | content.message (plain text) |
| denied records               | participant = policy actor instead of agent                         |
| evidence files               | NOT mapped (would need Files endpoint + fileKey); sha256 carried in text |

Limits: `check` validates only required fields and the eventType enum from the public OpenAPI file
(developers.globalrelay.com, Conversation API 1.6). It is not Global Relay's validator. Initiator email defaults to
`action-evidence-agent@example.invalid`; a real mapped address, tenant, and Open Connector credentials are
Global Relay-side facts we do not have. Whether archived records satisfy any retention rule is unknown; no such claim is made.

