"""Replay the public receipt into a new, disposable loopback Phoenix database."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import build_opener, ProxyHandler, Request, HTTPRedirectHandler

from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

ROOT = Path(__file__).resolve().parents[2]
SHA = '5c8d2fd542e92365f441dce5c452a31436e4583329b12274601a50420754de59'
PROJECT = 'action-evidence-local'
SPANS = f'/v1/projects/{PROJECT}/spans'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def check(ok, message):
    if not ok:
        raise ValueError(message)


def attrs(row):
    return {a.key: getattr(a.value, a.value.WhichOneof('value')) for a in row.attributes}


def same_time(stamp, ns):
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = datetime.fromisoformat(stamp) - epoch
    return ns == ((delta.days * 86400 + delta.seconds) * 10**6 + delta.microseconds) * 1000


def verify(span, saved):
    check(saved['context'] == {'trace_id': span.trace_id.hex(), 'span_id': span.span_id.hex()}, 'wrong span identity')
    check(saved['name'] == span.name and saved['parent_id'] is None, 'wrong name or parent')
    check(all(saved['attributes'].get(k) == v for k, v in attrs(span).items()), 'span attributes changed')
    check(same_time(saved['start_time'], span.start_time_unix_nano) and same_time(saved['end_time'], span.end_time_unix_nano), 'span bounds changed')
    print(f"GET {SPANS}: {saved['name']} trace={span.trace_id.hex()} span={span.span_id.hex()} Phoenix kind={saved['span_kind']}")
    for src, dst in zip(span.events, saved['events'], strict=True):
        a = dst['attributes']
        check(src.name == dst['name'] and same_time(dst['timestamp'], src.time_unix_nano), 'event name, order or time changed')
        check(json.dumps(attrs(src), sort_keys=True) == json.dumps(a, sort_keys=True), f'{src.name}: event attributes differ: {a}')
        print(dst['name'], ' '.join(f'{k}={a["cincinnatus." + k]}' for k in ('seq', 'phase', 'decision', 'artifact', 'status', 'bytes', 'record_id', 'authorization_record_id') if 'cincinnatus.' + k in a))
    print(f"Verified {len(saved['events'])} ordered events, their timestamps and all projected event attributes against the pinned payload.")


def run(folder):
    print('Python', sys.version.split()[0], '|', ' | '.join(f'{p}=={version(p)}' for p in ('arize-phoenix', 'opentelemetry-proto', 'protobuf')), flush=True)
    check(version('arize-phoenix') == '22.0.1', 'use pinned Phoenix version')
    folder.mkdir()  # never reuse a database or overwrite a receipt
    payload = folder / 'receipt.pb'
    subprocess.run([sys.executable, str(ROOT / 'adapters/opentelemetry/project.py'), str(ROOT / 'prospective/example'), str(payload)], check=True)
    data = payload.read_bytes()
    check(hashlib.sha256(data).hexdigest() == SHA, 'not the published payload; nothing sent')
    span = ExportTraceServiceRequest.FromString(data).resource_spans[0].scope_spans[0].spans[0]
    # Request two distinct available ports; do not attach to a configured service.
    with socket.socket() as a, socket.socket() as b:
        a.bind(('127.0.0.1', 0)); b.bind(('127.0.0.1', 0))
        port, grpc_port = a.getsockname()[1], b.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    client = build_opener(ProxyHandler({}), NoRedirect())
    env = {k: v for k, v in os.environ.items() if k.upper() in {'PATH', 'SYSTEMROOT', 'WINDIR', 'USERPROFILE', 'HOME', 'APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP', 'LANG', 'LC_ALL', 'SYSTEMDRIVE', 'COMSPEC'}}
    env.update(PHOENIX_HOST='127.0.0.1', PHOENIX_PORT=str(port), PHOENIX_GRPC_PORT=str(grpc_port), PHOENIX_WORKING_DIR=str(folder / 'store'), PHOENIX_ALLOW_EXTERNAL_RESOURCES='false', PHOENIX_TELEMETRY_ENABLED='false', PHOENIX_DISABLE_AGENT_ASSISTANT='true', PYTHONUTF8='1')
    log = folder / 'phoenix.log'
    with log.open('wb') as out:
        proc = subprocess.Popen([sys.executable, '-m', 'phoenix.server.main', 'serve'], env=env, cwd=folder, stdout=out, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline:
                check(proc.poll() is None, f'Phoenix exited: see {log}')
                try:
                    with client.open(base + '/healthz', timeout=2) as r:
                        if r.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(0.25)
            else:
                raise TimeoutError(f'Phoenix did not become ready: see {log}')
            req = Request(base + '/v1/traces', data=data, headers={'Content-Type': 'application/x-protobuf', 'x-project-name': PROJECT})
            with client.open(req, timeout=10) as r:
                print(f'POST /v1/traces: HTTP {r.status}, {len(data)} original bytes, project={PROJECT}')
                check(r.status == 200, 'unexpected ingestion status')
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    with client.open(base + SPANS, timeout=5) as r:
                        body = json.load(r)
                    if body['data']:
                        check(len(body['data']) == 1 and not body.get('next_cursor'), 'expected one stored span')
                        (folder / 'readback.json').write_text(json.dumps(body, indent=2), encoding='utf-8')
                        verify(span, body['data'][0])
                        return
                except HTTPError as e:
                    if e.code != 404:
                        raise
                time.sleep(0.25)
            raise TimeoutError(f'No span read back: see {log}')
        finally:
            proc.terminate()
            proc.wait(timeout=15)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='new directory for the payload, Phoenix store, log and API response')
    run(parser.parse_args().directory.resolve())
