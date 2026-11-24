"""Project a closed prospective/1 receipt to a local binary OTLP traces request."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from uuid import UUID

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.trace.v1.trace_pb2 import Span

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'prospective'))
import recorder

VERSION = '1.0.0'
PREFIX = 'cincinnatus.'
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def nanos(stamp):
    delta = datetime.fromisoformat(stamp) - EPOCH
    return (delta.days * 86400 + delta.seconds) * 10**9 + delta.microseconds * 1000


def attr(target, key, value):
    a = target.attributes.add(key=key)
    if isinstance(value, int):
        a.value.int_value = value
    else:
        a.value.string_value = value


def project(folder, pin):
    # Map exactly the bytes verified, even if the source directory changes.
    with TemporaryDirectory() as tmp:
        snapshot = Path(tmp)
        for name in ('trail.jsonl', 'result.bin'):
            (snapshot / name).write_bytes((folder / name).read_bytes())
        recorder.verify(snapshot, False, pin)
        lines = (snapshot / 'trail.jsonl').read_bytes().splitlines()
    rows = [json.loads(line) for line in lines]
    first, last = rows[0], rows[-1]
    req = ExportTraceServiceRequest()
    resource = req.resource_spans.add()
    attr(resource.resource, 'service.name', 'cincinnatus-prospective-recorder')
    group = resource.scope_spans.add()
    group.scope.name = 'cincinnatus.prospective.projection'
    group.scope.version = VERSION
    # Separate synthetic span identity from native receipt IDs. UUIDv4 session
    # identity already supplies 16 nonzero trace-ID bytes; UUIDv4's version
    # nibble also guarantees a nonzero first eight bytes for this span ID.
    span = group.spans.add(name='cincinnatus.receipt_session', kind=Span.SPAN_KIND_INTERNAL,
                           trace_id=UUID(first['session_id']).bytes,
                           span_id=UUID(first['record_id']).bytes[:8],
                           start_time_unix_nano=nanos(first['timestamp']),
                           end_time_unix_nano=nanos(last['timestamp']))
    attr(span, PREFIX + 'session_id', first['session_id'])
    attr(span, PREFIX + 'schema', first['detail']['schema'])
    for row, line in zip(rows, lines):
        event = span.events.add(name=PREFIX + row['event'], time_unix_nano=nanos(row['timestamp']))
        for key in ('record_id', 'seq', 'phase', 'parent_record_id', 'prev_hash'):
            if row[key] is not None:
                attr(event, PREFIX + key, row[key])
        attr(event, PREFIX + 'record_sha256', hashlib.sha256(line).hexdigest())
        for key in ('recording_mode', 'recorder', 'policy_sha256', 'operation', 'artifact', 'decision',
                    'reason', 'authorization_record_id', 'status', 'bytes', 'sha256', 'record_count', 'session_hash'):
            if key in row['detail']:
                attr(event, PREFIX + key, row['detail'][key])
    return req.SerializeToString(deterministic=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('output', type=Path, help='new .pb file (will not overwrite)')
    parser.add_argument('--decision-head', help='optional SHA-256 retained before releasing the read')
    args = parser.parse_args()
    data = project(args.directory, args.decision_head)
    with args.output.open('xb') as f:
        f.write(data)
    print(f'OTLP protobuf {len(data)} bytes | sha256 {hashlib.sha256(data).hexdigest()}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        sys.exit(f'STOP: {exc}')
