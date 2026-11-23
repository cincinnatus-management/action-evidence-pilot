#!/bin/bash
# Clean-workspace run: copies the adapter to a fresh dir, builds an offline fixture, exports, checks, tamper-tests.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
W="$(mktemp -d)"; cp "$SRC"/*.py "$W/"; cp "$SRC/../../action_evidence.py" "$W/"
cd "$W"
python -I make_fixture.py fixture
python -I action_evidence.py verify fixture
python -I export_archive.py export fixture bundle
python -I export_archive.py export fixture bundle2 >/dev/null
cmp bundle/conversation-payload.json bundle2/conversation-payload.json && echo "REPEATABLE: identical payload on re-export"
cp -r fixture tampered
sed -i 's/"decision": "denied"/"decision": "allowed"/' tampered/record.jsonl
if python -I export_archive.py export tampered bundle3; then echo "TAMPER NOT DETECTED"; exit 2; else echo "TAMPER REFUSED (expected)"; fi
echo "CLEAN DIR: $W"
