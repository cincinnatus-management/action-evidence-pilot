#!/usr/bin/env python3
"""Verify Cincinnatus Management's published payment-key proof of control.

Reads PAYMENT.json from this repository and checks that the signature
recovers to the published address. Run:

    pip install eth-keys
    python scripts/verify_payment_key.py            # from the repo root
    python scripts/verify_payment_key.py path/to/PAYMENT.json

Prints PASS lines for each check, or FAIL with the reason, and exits 0/1.
Requires Python 3.8+ and eth-keys (secp256k1 recovery, EIP-55 checksums).
"""
import json
import sys
from pathlib import Path

try:
    from eth_keys import keys
    from eth_hash.auto import keccak
except ImportError:
    print("FAIL: missing dependency. Run: pip install eth-keys")
    sys.exit(1)


def eip55_ok(addr: str) -> bool:
    """The published address must be valid EIP-55 checksummed (per ERC-55)."""
    if not addr.startswith("0x") or len(addr) != 42:
        print("FAIL: address is not a 20-byte 0x-prefixed hex string")
        return False
    lower = addr[2:].lower()
    digest = keccak(lower.encode("ascii")).hex()
    checksum = "0x" + "".join(
        c.upper() if int(digest[i], 16) >= 8 else c.lower()
        for i, c in enumerate(lower)
    )
    return addr == checksum


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "PAYMENT.json"
    doc = json.loads(path.read_text(encoding="utf-8"))

    address = doc["address"]
    message = doc["message"]
    signature = doc["signature"]

    checks = []

    checks.append(("address is EIP-55 checksummed", eip55_ok(address)))

    raw = bytes.fromhex(signature[2:] if signature.startswith("0x") else signature)
    checks.append(("signature is 65 bytes (r, s, recovery id)", len(raw) == 65))

    sig = keys.Signature(signature_bytes=raw)
    recovered = sig.recover_public_key_from_msg(message.encode("utf-8")).to_checksum_address()
    checks.append(("signature recovers to the published address", recovered == address))

    msg = doc.get("message", "")
    checks.append((
        "message names the business and this repository",
        "Cincinnatus Management LLC" in msg and "cincinnatus-management" in msg,
    ))

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("PASS" if ok else "FAIL") + ": " + name)
    print()
    print("Address:      " + address)
    print("Issued (UTC): " + str(doc.get("issued_utc", "not stated")))
    print("Invoice rail: " + str(doc.get("note", "")))
    if failed:
        print("\nVERIFY FAILED (%d check(s))" % len(failed))
        return 1
    print("VERIFY OK: proof of control confirmed for " + address)
    return 0


if __name__ == "__main__":
    sys.exit(main())
