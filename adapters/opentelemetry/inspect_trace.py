"""Decode a local OTLP protobuf request without using the mapper or source log."""
import argparse
from pathlib import Path
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from google.protobuf import text_format

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('payload', type=Path)
parser.add_argument('--full', action='store_true', help='print all fields as protobuf text')
a = parser.parse_args()
request = ExportTraceServiceRequest.FromString(a.payload.read_bytes())
if a.full:
    print(text_format.MessageToString(request), end='')
else:
    for resource in request.resource_spans:
        for group in resource.scope_spans:
            for s in group.spans:
                print(f'{s.name} | mapping {group.scope.version} | trace {s.trace_id.hex()} | {len(s.events)} events')
                for e in s.events:
                    fields = {k.key: getattr(k.value, k.value.WhichOneof('value')) for k in e.attributes}
                    keys = ('seq', 'phase', 'decision', 'artifact', 'status', 'bytes', 'record_id', 'authorization_record_id')
                    print(e.name, *(f'{key}={fields["cincinnatus." + key]}' for key in keys if 'cincinnatus.' + key in fields))
