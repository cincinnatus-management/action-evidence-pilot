#!/bin/bash
# Runs inside the container. Offline. Prints PASS/FAIL per step; exit code non-zero on any failure.
set -u
D=/opt/demo; W="$(mktemp -d)"; cd "$W"; cp "$D"/*.py .; fail=0
step() { echo; echo "== $1"; }
step "1. Verify the published sample record chain"
python -I action_evidence.py verify "$D/sample-run-output" || fail=1
step "2. Build an offline fixture record folder (2 allowed, 2 denied actions)"
python -I make_fixture.py fixture || fail=1
python -I action_evidence.py verify fixture || fail=1
step "3. Export the fixture to a Global Relay-style Conversation API payload (local files only)"
python -I export_archive.py export fixture bundle || fail=1
python -I export_archive.py check bundle || fail=1
python -I export_archive.py export fixture bundle2 >/dev/null || fail=1
if cmp bundle/conversation-payload.json bundle2/conversation-payload.json; then
  echo "REPEATABLE: identical payload on re-export"; else echo "NOT REPEATABLE"; fail=1; fi
step "4. Tamper test: change one decision, export must refuse"
cp -r fixture tampered
sed -i 's/"decision": "denied"/"decision": "allowed"/' tampered/record.jsonl
if python -I export_archive.py export tampered bundle3; then echo "TAMPER NOT DETECTED"; fail=1; else echo "TAMPER REFUSED (expected)"; fi
step "Result"
cat <<'TXT'
Limits: demo only. Not Docker-certified, not a Docker partner image, not production-ready, not an existing
integration with any archive vendor. Nothing was sent anywhere. The export check validates only required fields
against the public OpenAPI file, not any vendor validator. Verify proves the records read are internally
consistent; it does not prove completeness or that the agent's decisions were right.
Cincinnatus Management LLC is operated by AI agents.
TXT
if [ "$fail" = 0 ]; then echo "DEMO RESULT: PASS"; else echo "DEMO RESULT: FAIL"; fi
exit $fail
