# Observe a decision before a read

Can you inspect the approval **before** the recorder opens the approved file? This local demo pauses at that point. The saved example shows the final records; only a live run lets you observe their timing yourself.

From the repository root, using Python 3.8+ and a new output directory (no packages, keys or network needed after cloning):

```
python prospective/recorder.py verify prospective/example
python prospective/recorder.py run my-read --pause
```

Leave the recorder paused. From a second terminal at the same repository root:

```
python prospective/recorder.py prefix my-read
```

Expect `PREFIX OK (not a completed read)`. Inspect `my-read/trail.jsonl`: the first row opens the session, the second denies `action-02.bin`, the third permits `action-01.bin`. No result file should be present. Save the printed **decision** hash somewhere outside `my-read`. In the first terminal enter `read`. In the second terminal replace `YOUR_SAVED_HASH` with that hash:

```
python prospective/recorder.py verify my-read --decision-head YOUR_SAVED_HASH
```

Expect `CLOSED OK (one denied, one read)`. The saved bytes in `my-read/result.bin` must match the approved file in `adapters/action-receipt/example/evidence/` in this checkout. They come from a **new local read** of an old public artifact, not a replay of the original HTTP request. The decision hash must still match what you saw before releasing the read. For unattended capture omit `--pause`; that does not give an observer a checkpoint before execution.

The recorder flushes and calls `fsync` on each row before continuing. The allow row contains no result. If a decision write fails, execution stops before opening that artifact. If a read, later write or clock check fails, the directory may contain partial evidence; do not resume or infer whether a read completed. `verify` requires the full fixed sequence, including the result and close. The pause is a timing aid, not an identity check or a signed human approval.

## What the verifier checks

The verifier expects the exact local policy and both requests; it checks their decisions, UUIDv4 IDs, local UTC times, contiguous positions, predecessor IDs and hashes. The result references its approval and binds the saved bytes by length and SHA-256. The close binds the count and the digest of all preceding raw record hashes in order. A record hash covers its sorted, compact ASCII JSON bytes without the newline. Keep the checkout and output directory under your control. No key signs the log: someone able to replace the records can recompute a chain, and a retained decision hash does not authenticate the final result. The process, OS clock, filesystem and checkout are trusted. No host-wide mediation or proof that an unobserved action never happened.

See [draft comparison and unsupported fields](LIMITS.md). No changes to the original signed example or the historical recorder are needed.
