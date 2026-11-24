"""Generate or verify the Cincinnatus bare-receipt evaluation (draft -01)."""
import argparse
import base64
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from nacl.bindings import crypto_core_ed25519_is_valid_point
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import action_evidence as recorder

DRAFT = 'draft-noa-scitt-ai-agent-receipt-01'
TAG = b'NOA-Receipt-v0.1-sig:'
RISK = {'http_get': 'LOW', 'write_file': 'HIGH'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def members(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result and key not in ('__proto__', 'prototype', 'constructor'), 'invalid JSON member')
        result[key] = value
    return result


def parse(text):
    return json.loads(text, object_pairs_hook=members)


def lines(path):
    return [parse(row) for row in path.read_text(encoding='utf-8').splitlines()]


def sources(folder):
    policy = parse((ROOT / 'policy.json').read_text())
    workflow = parse((ROOT / 'workflow.json').read_text())
    rows = lines(folder / 'record.jsonl')
    previous = '0' * 64
    need(len(rows) == len(workflow) and rows, 'incomplete recorder workflow')
    for i, (row, action) in enumerate(zip(rows, workflow), 1):
        ok, reason = recorder.allowed(action, policy)
        need(type(row['seq']) is int and row['seq'] == i and row['action'] == action, 'source order/action')
        need(row['agent'] == policy['agent'] and row['policy_id'] == policy['policy_id'] and
             row['policy_sha256'] == recorder.sha(recorder.canon(policy)), 'source policy')
        need(row['decision'] == ('allowed' if ok else 'denied') and row['decision_reason'] == reason, 'source decision')
        need(row['prev_hash'] == previous, 'source link')
        previous = recorder.sha(recorder.canon({k: v for k, v in row.items() if k != 'record_hash'}))
        need(row['record_hash'] == previous, 'source hash')
        ev, res = row['evidence'], row['result']
        if ev is not None:
            filename = f'evidence/action-{i:02d}.bin'
            need(ok and ev['file'] == filename, 'source evidence reference')
            data = (folder / filename).read_bytes()
            need(recorder.sha(data) == ev['sha256'] and len(data) == res['bytes'], 'source evidence bytes')
        else:
            need(('error' in res) if ok else (res == {'blocked': True}), 'source outcome')
    return rows


def projection(row, ts, scope, prev, kid):
    op = row['action']['type']
    return {'spec': 'noa.receipt/0.1', 'id': 'record-' + row['record_hash'], 'ts': ts,
            'scope': {'chain': scope}, 'agent': {'id': row['agent'], 'principal': 'POLICY'},
            'action': {'id': op, 'canonical': op, 'riskClass': RISK[op], 'reversible': False,
                       'paramsHash': 'sha256:' + recorder.sha(recorder.canon(row['action']))},
            'governance': {'mode': 'on', 'sandboxed': False,
                           'verdict': 'ALLOWED' if row['decision'] == 'allowed' else 'BLOCKED'},
            'chain': {'seq': row['seq'] - 1, 'prevHash': prev}, 'sig': {'alg': 'ed25519', 'kid': kid}}


def digest(payload):
    # The projection only produces printable ASCII strings/keys, booleans, null
    # and small integers; sorted compact JSON is JCS on precisely this subset.
    return hashlib.sha256(recorder.canon(payload)).digest()


def public_id(pub):
    return 'sha256:' + recorder.sha(pub)


def generate(folder):
    folder.mkdir(exist_ok=False)
    key = SigningKey.generate()  # only in memory; never serialize the private key
    pub = bytes(key.verify_key)
    scope = uuid.uuid4().hex
    recorder.run(str(folder))
    prev = None
    with (folder / 'receipts.jsonl').open('x', encoding='utf-8', newline='\n') as out:
        for row in sources(folder):
            ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            payload = projection(row, ts, scope, prev, public_id(pub))
            raw = digest(payload)
            prev = payload['chain']['hash'] = 'sha256:' + raw.hex()
            payload['sig']['value'] = base64.b64encode(key.sign(TAG + raw).signature).decode('ascii')
            out.write(recorder.canon(payload).decode('ascii') + '\n')
    print('PIN (retain separately):', pub.hex(), prev)


def verify(folder, public_key, head):
    need(re.fullmatch('[0-9a-f]{64}', public_key), 'noncanonical public key')
    pub = bytes.fromhex(public_key)
    need(crypto_core_ed25519_is_valid_point(pub), 'invalid public point')
    key = VerifyKey(pub)
    rows, receipts = sources(folder), lines(folder / 'receipts.jsonl')
    need(len(rows) == len(receipts), 'incomplete receipt set')
    prev = None
    scope = receipts[0]['scope']['chain']
    need(re.fullmatch('[0-9a-f]{32}', scope), 'invalid local scope')
    for row, payload in zip(rows, receipts):
        ts = payload['ts']
        need(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', ts), 'timestamp spelling')
        datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
        expected = projection(row, ts, scope, prev, public_id(pub))
        actual = payload['chain'].pop('hash')
        encoded = payload['sig'].pop('value')
        need(recorder.canon(payload) == recorder.canon(expected), 'receipt differs from local projection')
        raw = digest(expected)
        prev = 'sha256:' + raw.hex()
        need(actual == prev, 'receipt hash')
        sig = base64.b64decode(encoded, validate=True)
        need(len(sig) == 64 and base64.b64encode(sig).decode('ascii') == encoded, 'signature encoding')
        need(crypto_core_ed25519_is_valid_point(sig[:32]), 'invalid signature point')
        key.verify(TAG + raw, sig)
    need(head == prev, 'wrong terminal hash')
    print(f'VERIFIED {len(rows)} bare receipts | {DRAFT} | pinned key and head | {prev}')
    print('No COSE envelope, transparency registration or external checkpoint. Agent identity not authenticated.')
    print('Named approval: not provided. Independent outcome: not provided. Physical completion: not claimed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('generate').add_argument('new_dir', type=Path)
    check = subs.add_parser('verify')
    check.add_argument('folder', type=Path)
    check.add_argument('public_key', help='trusted raw Ed25519 public key (lowercase hex)')
    check.add_argument('head', help='trusted terminal receipt hash including sha256: prefix')
    args = parser.parse_args()
    if args.command == 'generate':
        generate(args.new_dir)
    else:
        verify(args.folder, args.public_key, args.head)


if __name__ == '__main__':
    try:
        main()
    except (BadSignatureError, ValueError, OSError, KeyError, TypeError, AttributeError, IndexError) as exc:
        sys.exit(f'REFUSED: {exc}')
