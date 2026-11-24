"""Read-only buyer check. Run from a full public clone; see README.md here."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/cincinnatus-management/action-evidence-pilot'
OFFER = 'https://cincinnatusmanagement.com/action-evidence-pilot/'
BASE = '2e5e34a44b85a7123b58ee7878b7279355fd2c74'
CHANNEL_BASE = '25bbc6a2c4d4fd1e6c2528429b244c6c4824fa25'
HEAD = '81e62ef666f97a857d480fda7bbf414963d06673e7867fc1ba195f9f716b2038'
CHANNEL = ('channel/README.md', 'channel/IMPLEMENTATION.md', 'channel/VERIFICATION.md')
ACTION = ('action_evidence.py', 'policy.json', 'rates.json', 'workflow.json',
          'sample-run-output/record.jsonl', 'sample-run-output/summary.json',
          'sample-run-output/evidence/action-01.bin', 'sample-run-output/evidence/action-02.bin')
KEY = ('scripts/verify_payment_key.py', 'PAYMENT.json')


def command(*args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=30)
    if result.returncode:
        detail = (result.stderr or result.stdout).decode(errors='replace').strip().splitlines()
        raise ValueError(detail[-1] if detail else f'command exited {result.returncode}')
    return result.stdout


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_file(path):
    expected = command('git', '--no-replace-objects', 'cat-file', 'blob', f'{BASE}:{path}')
    require((ROOT / path).read_bytes() == expected, 'working bytes differ from the public baseline')


def source(pin):
    require(re.fullmatch('[0-9a-f]{40}', pin), 'supply a retained full commit ID, not a branch name')
    require(command('git', 'rev-parse', 'HEAD').decode().strip() == pin, 'checkout does not match supplied commit')
    require(command('git', 'remote', 'get-url', 'origin').decode().strip() in (REPO, REPO + '.git'), 'origin is not the documented HTTPS URL')
    expected = command('git', '--no-replace-objects', 'cat-file', 'blob', f'{pin}:buyer/probe.py')
    require(Path(__file__).read_bytes() == expected, 'probe bytes differ from supplied commit')


def inventory(pin):
    def paths(ref):
        names = command('git', '--no-replace-objects', 'ls-tree', '-r', '--name-only', '-z', ref)
        return {p for p in names.split(b'\0') if p and not p.startswith(b'buyer/')}
    changes = paths(BASE) ^ paths(pin)
    require(not changes, 'added or removed paths need review: ' + repr(sorted(changes)))


def action():
    output = command(sys.executable, '-I', ACTION[0], 'verify', 'sample-run-output').decode().strip()
    require(output == f'VERIFY OK: 4 records, chain head {HEAD}', 'count or chain head does not match the published sample')
    print('  ' + output)
    rows = [json.loads(line) for line in (ROOT / ACTION[4]).read_bytes().splitlines()]
    require([r['decision'] for r in rows] == ['allowed', 'allowed', 'denied', 'denied'], 'recorded decisions differ')
    require([r['result'].get('status') for r in rows[:2]] == [200, 200] and
            all(r['result'] == {'blocked': True} and r['evidence'] is None for r in rows[2:]), 'recorded outcomes differ')


def signature():
    address = json.loads((ROOT / KEY[1]).read_bytes())['address']
    output = command(sys.executable, '-I', *KEY).decode().splitlines()
    require(f'VERIFY OK: proof of control confirmed for {address}' in output, 'signature recovery not confirmed')


def archive(path):
    with ZipFile(path) as z:
        members = [i for i in z.infolist() if i.filename != 'channel/']
        require(sorted(i.filename for i in members) == sorted(CHANNEL), 'expected exactly the three original channel files')
        for item in members:
            ref = command('git', '--no-replace-objects', 'cat-file', 'blob', f'{CHANNEL_BASE}:{item.filename}')
            require(item.file_size == len(ref) and z.read(item) == ref, item.filename + ' differs from the original channel revision')


class OfferText(HTMLParser):
    """Read text and links in the WordPress post, not the navigation/footer."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.hidden = False
        self.words = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and (self.depth or 'entry-content' in (attrs.get('class') or '').split()):
            self.depth += 1
        if self.depth and tag == 'a':
            self.links.append(attrs.get('href'))
        if tag in ('script', 'style'):
            self.hidden = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.depth:
            self.depth -= 1
        if tag in ('script', 'style'):
            self.hidden = False

    def handle_data(self, data):
        if self.depth and not self.hidden:
            self.words.append(data)


def live():
    parser = OfferText()
    with urlopen(OFFER, timeout=15) as res:
        require(res.geturl() == OFFER and res.status == 200, 'offer URL or status changed')
        parser.feed(res.read().decode('utf-8'))
    text = ' '.join(' '.join(parser.words).split())
    for phrase in ('$3,000, fixed', 'One workflow, one agent setup.', '10 business days',
                   'invoiced after the written scope is accepted.'):
        require(phrase in text, 'offer text no longer contains: ' + phrase)
    require(REPO in parser.links, 'public repository link differs')
    require('mailto:info@cincinnatusmanagement.com?subject=Pilot' in parser.links, 'published inquiry link differs')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--commit', required=True, help='independently retained full public probe revision')
    cli.add_argument('--live-offer', action='store_true', help='also read selected terms and links on the live pilot page')
    cli.add_argument('--channel-zip', type=Path, help='also compare a supplied original channel ZIP without extracting it')
    args = cli.parse_args()
    failures = []

    def check(label, fn, *params):
        try:
            fn(*params)
        except Exception as exc:
            failures.append(label)
            print(f'FAIL {label}: {exc}')
            return False
        print(f'PASS {label}')
        return True

    if not check('configured origin and checkout match the supplied probe pin', source, args.commit):
        return 1
    print('Evidence baseline:', BASE)
    verified = {p: check(p, same_file, p) for p in ('README.md', *CHANNEL, *ACTION, *KEY)}
    if verified['README.md'] and verified[CHANNEL[0]]:
        print('PASS pinned documents: $3,000 fixed pilot; separate proposed $15,000/year channel license')
    check('tracked paths outside buyer/ match the baseline inventory', inventory, args.commit)
    print('ORDER BOUNDARY: the baseline contains proposed terms, not a separate order packet.')
    for paths, label, fn in [(ACTION, 'sample chain, response bytes and recorded outcomes (2 HTTP 200; 2 blocked)', action),
                             (KEY, 'published signature recovers the address in PAYMENT.json', signature)]:
        if all(verified[p] for p in paths):
            check(label, fn)
        else:
            print('NOT RUN ' + label + ': required input failed')
    if args.live_offer:
        check('live pilot page: price, scope, time box, invoicing text, repository and inquiry links', live)
    else:
        print('NOT CHECKED live pilot page (use --live-offer)')
    if args.channel_zip:
        check('supplied ZIP contents match original channel revision ' + CHANNEL_BASE, archive, args.channel_zip)
    else:
        print('NOT CHECKED external channel ZIP (use --channel-zip FILE)')
    print('RESULT:', 'FAIL' if failures else 'PASS')
    return int(bool(failures))


if __name__ == '__main__':
    sys.exit(main())
