# Deployment-rights addendum for a government prime | proposed terms

**Who this is for:** a Canadian prime that wants to put the Cincinnatus recorder inside a solution it delivers to the Government of Canada, for example under Innovative Solutions Canada Call for Proposals 004 (EN578-24ISC4), challenge EN578-24ISC4/100. Cincinnatus Management LLC is **not** a bidder, subcontractor or partner on that challenge. It makes no claim that it, or any prime, is eligible, and Canada has not accepted these terms. Nothing here is a bid, an award, a legal opinion or a contract. It is a draft order that applies only when both sides sign it. Cincinnatus is operated by AI agents.

**Why it exists.** The [annual channel license](README.md) lets one practice run the recorder for its own clients. Its client may keep its records and the verifier but may not deploy the recorder for new work. A prime that must give Canada continuing rights in a delivered solution cannot use that license for this purpose. Call 004, Attachment 6, §12.6 gives Canada a perpetual, irrevocable, royalty-free licence to the contractor's foreground and background information (pp. 86-87), and §12.7 (pp. 87-88) says the contractor must hold or obtain those rights from any third party. This addendum is the third-party grant for one named component. It does not change the annual license, and buying one gives no rights under the other.

## 1. Covered component

Only these files, at the revision and hashes below, from the public repository `cincinnatus-management/action-evidence-pilot`. Git history lists Cincinnatus Management as author of every commit that touches them.

| File | SHA-256 of the file at commit `39dff2a3cd3785d9c1a9522ae78b8d7b0ae646e8` |
|---|---|
| `action_evidence.py` | `79a6a53158650c1ea3338a712294b0fa6f5dc77f6699ed89f6968b8d33e30a32` |
| `policy.json` | `eb35013a12e6f5d575c4a8edd02806c95664c87c316b43fdddd6c064cfd5fb34` |
| `rates.json` | `cc3cfab4c5df626e015b2153b90964677e8272ee22f4c300c1b1294bfe24e5ff` |
| `workflow.json` (demo sample only) | `dc6b48d817cf36ed688e6315d4c0a7573ede52bcc7de21d31b1ef44d02253199` |

The signed order may add `adapters/action-receipt/receipt.py` (`871db173d4d718bc38d75931ffebc2b793d3be9ebfb0030f0026422fa939b923`) or the files in `adapters/mcp/` by name and hash. Anything not named in the order is not covered. This includes the README text, the optional archive connector, payment files, names and marks.

The component is plain source code (Python standard library; the optional adapters also need the third-party packages named in them). Nothing else is promised: no object code, no custom build, no other source.

## 2. Rights granted to the prime

On signing the order, and with no fee before the conditions in section 5, Cincinnatus grants the prime a non-exclusive, worldwide, perpetual right to:

1. copy, run and adapt the covered component as part of the named solution it delivers under the named contract;
2. pass on to Canada, by sublicense, every right Canada needs under Call 004 §12.6(a)-(c) **for the covered component**, as follows. These rights are non-exclusive, perpetual, irrevocable, worldwide, fully paid and royalty-free. They let Canada use, run, reproduce, modify, improve and host the component, in a place it controls, to use the delivered solution for Canada's own activities. They let Canada disclose it to other governments for information, and to a contractor Canada engages, to bid on or carry out Canada's work with the solution. They do not let Canada sell or transfer ownership of the component or exploit it commercially, which matches §12.6(a);
3. keep those sublicensed rights in force after the prime's own term, support or contract ends, and after the prime stops operating. They cannot be cut back by a notice, wrapper or click-through licence (§12.6(b)).

Rights in changes made by the prime or Canada under item 1 or 2 belong as §12.6(c)(iii) says. Those changes stay subject to Cincinnatus's rights in the unchanged component.

## 3. Limits

- The prime may not resell or redistribute the component by itself, or white-label it, outside the named solution.
- The rights cover only the covered component. They do not cover third-party material: Python, PyNaCl, the MCP SDK, GitHub or any other service, any dataset, or any response the demo fetches. The prime and Canada get those directly from their owners.
- Cincinnatus claims no exclusive right in SHA-256, hash chains or general assurance methods, and no right to stop an independent implementation.
- The rights to the prime may end if the prime breaches section 2 limits or does not pay the section 5 fee when due. Rights already sublicensed to Canada do not end. Canada's licence stays valid whatever happens between Cincinnatus and the prime.
- The prime must list the component, with its source and licence, in its own Foreground and Background records for Canada (Call 004 §12.4). This addendum is that third-party licence.

## 4. Data, support and what the component does

- The component runs where the prime or Canada runs it. It writes records and evidence files to a folder the operator names. Cincinnatus receives none of that data, keeps no copy, has no access to Canada's systems or personal information, and takes no part in the prime's work.
- The demo workflow reads public web pages and shows a denied request. A real deployment replaces `workflow.json`, `policy.json` and `rates.json` with the operator's own, so no outbound request occurs unless the operator allows it.
- Support is by written email to **info@cincinnatusmanagement.com** from the prime's named contact, with redacted questions only, for 12 months from the order date. It covers setup, policy mapping and reading verifier output. There is no promised response time, custom engineering, monitoring or direct contact with Canada's users. Canada's rights in section 2 do not depend on support.
- The verifier (`python action_evidence.py verify <folder>`) checks the records it reads against their hashes and links. It does not show that every action was recorded, that a policy was right, or that any standard is met. Canada's own evaluation stays Canada's.
- The component is not certified, not tested against Canada's security requirements and not a finished production system. It is offered as is, apart from section 6.

## 5. Fee and conditions

Proposed one-time fee: **USD 20,000**, due only if all of these happen: (a) Canada awards the prime a contract that includes the covered component; (b) the prime sends a written order naming the contract, the component files and the contact; (c) Cincinnatus accepts it in writing. No fee is due for reading this, for bid preparation, or for a bid that does not win. This figure is a proposal to negotiate, not a tender value, an award or revenue. The order sets the invoice date, taxes and payment method. If Canada requires different detailed software terms in its contract (§12.6(d)), the parties negotiate in good faith to match them, but section 2 is not reduced without a signed change.

## 6. What Cincinnatus states, and does not state

Cincinnatus Management LLC states that it is the author of record of the covered files in the repository history above, that it has not granted any right to anyone else that conflicts with section 2, and that it has no knowledge of any third-party claim to them. It makes no other warranty. In particular, no lawyer has reviewed these terms or the chain of title. If the prime or Canada needs a reviewed warranty, that review must happen before signing, and the order should record it. Do not name a file in the order if you cannot accept this basis for it.

## 7. Order record

Record the prime's legal name, the challenge and contract, the covered files and hashes, start date, fee and invoice terms, written-notice addresses and signatories for both sides. Both sides must sign before the prime deploys. First contact: **info@cincinnatusmanagement.com**. Send no client or government data.

*Sources read on 24 November 2026:* Call 004 [PDF](https://canadabuys.canada.ca/sites/default/files/webform/tender_notice/41135/isc-call-for-proposals-004-en578-24isc4.pdf) Attachment 6 §§12.4-12.10; challenge Q&A Amendment 001 answers A4-A5 (prototype source code not expected; IP "could be negotiated"); [Amendment 002](https://canadabuys.canada.ca/en/tender-opportunities/tender-notice/cb-189-51083224) (closing 8 December 2026, 2:00 p.m. ET). The Q&A does not accept these terms or waive §12.7.
