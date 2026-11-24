"""Observe a local policy decision before the permitted read. Python 3.8+."""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'adapters/action-receipt/example/evidence'
ALLOW = 'action-01.bin'
DENY = 'action-02.bin'
POLICY = {'operation': 'read_published_artifact', 'allow': [ALLOW], 'default': 'deny'}
FORMAT = 'cincinnatus.prospective/1'


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def start():
    return {'schema': FORMAT, 'recorder': 'local-python', 'recording_mode': 'self',
            'policy': POLICY, 'policy_sha256': digest(encode(POLICY))}


def decision(name):
    return {'operation': POLICY['operation'], 'artifact': name,
            'policy_sha256': digest(encode(POLICY)),
            'decision': 'allow' if name in POLICY['allow'] else 'deny',
            'reason': 'exact allow-list match' if name in POLICY['allow'] else 'default deny'}


def result(body, approval):
    return {'operation': POLICY['operation'], 'artifact': ALLOW, 'authorization_record_id': approval,
            'status': 'read', 'bytes': len(body), 'sha256': digest(body)}


def close(hashes):
    return {'record_count': len(hashes) + 1,
            'session_hash': digest(b''.join(bytes.fromhex(h) for h in hashes))}


def row(seq, sid, rid, stamp, prev_id, prev_hash, event, phase, detail):
    return dict(seq=seq, session_id=sid, record_id=rid, timestamp=stamp, parent_record_id=prev_id,
                prev_hash=prev_hash, event=event, phase=phase, detail=detail)


def store(path, data, mode):
    with path.open(mode) as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def run(out, pause):
    out.mkdir()  # one writer, one new directory; never resume or overwrite
    sid = str(uuid4())
    prev_id, last_stamp, hashes = None, '', []

    def append(event, phase, detail):
        nonlocal prev_id, last_stamp
        stamp = datetime.now(timezone.utc).isoformat(timespec='microseconds')
        require(stamp >= last_stamp, 'wall clock moved backwards; retire this directory')
        rid = str(uuid4())
        data = encode(row(len(hashes), sid, rid, stamp, prev_id, hashes[-1] if hashes else None,
                          event, phase, detail))
        store(out / 'trail.jsonl', data + b'\n', 'ab' if hashes else 'xb')
        hashes.append(digest(data))
        prev_id, last_stamp = rid, stamp
        return rid

    append('session_start', 'concurrent', start())
    for name in (DENY, ALLOW):
        d = decision(name)
        approval = append('policy_decision', 'pre_execution', d)
        if d['decision'] == 'deny':
            continue
        print('DECISION HEAD', hashes[-1], flush=True)
        if pause:
            print('Paused before opening the artifact. Type read to continue.', flush=True)
            require(sys.stdin.readline().strip() == 'read', 'not released; no read performed')
        body = (SOURCE / name).read_bytes()
        store(out / 'result.bin', body, 'xb')
        append('read_result', 'post_execution', result(body, approval))
    append('session_end', 'post_execution', close(hashes))
    print('CLOSED HEAD', hashes[-1])


def uuid_ok(value):
    parsed = UUID(value)
    return parsed.version == 4 and str(parsed) == value


def verify(out, prefix, pin):
    data = (out / 'trail.jsonl').read_bytes()
    require(len(data) <= 65536 and data.endswith(b'\n'), 'incomplete or oversized log')
    lines = data[:-1].split(b'\n')
    require(len(lines) == (3 if prefix else 5), 'expected decision prefix' if prefix else 'expected closed session')
    rows = [json.loads(line) for line in lines]
    schedule = [('session_start', 'concurrent', start()),
                ('policy_decision', 'pre_execution', decision(DENY)),
                ('policy_decision', 'pre_execution', decision(ALLOW))]
    hashes = [digest(line) for line in lines]
    if prefix:
        require(not (out / 'result.bin').exists(), 'result file already present')
    else:
        body = (out / 'result.bin').read_bytes()
        require(body == (SOURCE / ALLOW).read_bytes(), 'saved bytes differ from public source in this checkout')
        schedule.extend([('read_result', 'post_execution', result(body, rows[2]['record_id'])),
                         ('session_end', 'post_execution', close(hashes[:-1]))])
    sid = rows[0]['session_id']
    require(uuid_ok(sid), 'invalid session id')
    seen, last_stamp, prev_id = {sid}, '', None
    for i, (r, line, spec) in enumerate(zip(rows, lines, schedule)):
        rid, stamp = r['record_id'], r['timestamp']
        require(uuid_ok(rid) and rid not in seen, 'duplicate or invalid record id')
        t = datetime.fromisoformat(stamp)
        require(t.tzinfo == timezone.utc and t.isoformat(timespec='microseconds') == stamp
                and stamp >= last_stamp, 'invalid or decreasing UTC time')
        expected = row(i, sid, rid, stamp, prev_id, hashes[i-1] if i else None, *spec)
        require(line == encode(expected), 'broken link, content or encoding at row %d' % i)
        seen.add(rid)
        prev_id, last_stamp = rid, stamp
    require(pin is None or pin == hashes[2], 'decision head differs from supplied observation')
    print('PREFIX OK (not a completed read)' if prefix else 'CLOSED OK (one denied, one read)',
          '| decision', hashes[2], '| head', hashes[-1])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    r = sub.add_parser('run'); r.add_argument('directory', type=Path)
    r.add_argument('--pause', action='store_true')
    for name in ('prefix', 'verify'):
        v = sub.add_parser(name); v.add_argument('directory', type=Path)
        v.add_argument('--decision-head', help='hash you retained while paused')
    a = p.parse_args()
    if a.command == 'run':
        run(a.directory, a.pause)
    else:
        verify(a.directory, a.command == 'prefix', a.decision_head)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        sys.exit('STOP: ' + str(exc))
