# Verify the evidence package

Use a fresh clone, Git and Python 3.10 or later. No wallet, login or private workflow data is needed. In the commands below, replace `PIN` with the full 40-character public commit ID you retained for the probe. Do not substitute the current branch tip. Review the code at that commit before running it; a script cannot establish its own trustworthiness.

```
git clone --config core.autocrlf=false https://github.com/cincinnatus-management/action-evidence-pilot.git
cd action-evidence-pilot
git checkout --detach PIN
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS/Linux, or `.\.venv\Scripts\Activate.ps1` in Windows PowerShell. Then run:

```
python -m pip install "eth-keys==0.8.0" "eth-hash[pycryptodome]==0.8.0"
python -I buyer/probe.py --commit PIN
```

The second command works offline. Exit 0 and `RESULT: PASS` mean every requested check passed. A missing file, different bytes, wrong checkout or failed signature check gives a nonzero exit. Keep the pin and output together. Do not use a passing result for a different revision.

| Check | What a pass means |
|---|---|
| Source and offer files | The configured origin and checkout match the expected URL and supplied pin. The listed files match the bytes at evidence commit `2e5e34a44b85a7123b58ee7878b7279355fd2c74`. The [pilot description](../README.md) and [proposed channel terms](../channel/README.md) describe different purchases. The tracked file list at that baseline contains no separate order packet. |
| Action records | The existing verifier recomputes the four record hashes, their links and the two referenced response hashes. Two records report HTTP 200 and two report blocked actions. No workflow is rerun. Matching hashes do not establish that the original record was truthful or complete. |
| Key signature | The published verifier recovers the listed address from the signed message. That is evidence about the signature, not the signer's legal identity, current key custody, an authorized invoice, a balance or money received. |

For the public page, add `--live-offer`. This makes an HTTPS request and checks selected pilot terms plus the repository and email links; it does not send an inquiry. For an original channel archive already in hand, add `--channel-zip PATH`. Its three document contents must match `25bbc6a2c4d4fd1e6c2528429b244c6c4824fa25`; the current repository has a later channel README. ZIP timestamps and compression are not checked. Unrequested checks print `NOT CHECKED`.

This checks named public evidence, not other files, later offers, an executed order, customer use, software integration, certification or legal rights. No payment is requested or made by this probe.
