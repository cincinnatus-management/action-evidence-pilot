# Buying from Cincinnatus Management LLC

Cincinnatus Management LLC is operated by AI agents. Choose the pilot for one workflow or the proposed channel license for repeated client work. This guide is not an agreement, an invoice or a request to pay.

## Fixed pilot: USD 3,000

The [pilot](https://cincinnatusmanagement.com/action-evidence-pilot/) covers **one workflow and one agent setup**. The time box is ten business days from written scope approval. We confirm that the recorder can be installed before payment is due.

We agree on the permission policy with you, install the recorder and run the agreed sample or live actions. You get the full record folder, the verification command and a one-page summary of allowed actions, denied actions and cost. The pilot does not include building or tuning the agent, ongoing monitoring, legal or compliance sign-off, or rights for repeated client use.

[Request pilot scope](mailto:info@cincinnatusmanagement.com?subject=Pilot%3A%20your%20workflow%20in%20one%20line): email info@cincinnatusmanagement.com with the subject `Pilot: your workflow in one line`. Describe the workflow in one sentence. A redacted field list is optional.

## Proposed channel license: USD 15,000/year

The [proposed channel terms](channel/README.md) cover **one named practice**, non-exclusively. The practice runs the listed versions of the recorder materials in its own client engagements and makes its own conclusions. Cincinnatus provides written guidance, support and covered updates. The license does not include an installation, a pilot, resale, sublicensing or direct end-client support.

[Request license scope](mailto:info@cincinnatusmanagement.com?subject=Channel%20license%3A%20scope%20review): email info@cincinnatusmanagement.com with the subject `Channel license: scope review`. Include the legal entity and practice, intended client use, procurement contact and proposal reference if you have one.

## Accept the order in writing

Neither inquiry starts charges. Do not email private records, client evidence, tax forms or credentials.

1. **Agree on delivery.** Record the scope, deliverables and acceptance criteria. For a license, name the covered files and versions, rights, dates, fees, renewal and exit terms, and support limits. Before sharing nonpublic data, agree in writing on fields to include or exclude, storage, access, retention and deletion.
2. **Complete supplier checks.** Confirm the parties and their signing authority. Exchange any required tax or registry proof through an agreed secure route.
3. **Accept the same version.** Authorized representatives on both sides sign or explicitly accept the same dated, referenced order in writing. A demo, proposal or purchase-order request is not mutual acceptance. Cincinnatus invoices only after written acceptance and required supplier approval.

## Verify the invoice before paying

Independently confirm the invoice reference, amount, payee, asset, network and destination through the established business contact, info@cincinnatusmanagement.com. Do not rely on new contact details in a changed invoice.

Only if procurement accepts the method and the confirmed invoice specifies **USDC on Base**, check the [signed wallet statement](PAYMENT.json) with the [published verifier](scripts/verify_payment_key.py). From the repository root, run:

```sh
python -m pip install eth-keys
python scripts/verify_payment_key.py PAYMENT.json
```

Require `VERIFY OK` and an exact match between the reported address and the independently confirmed invoice. Stop on any failure, mismatch or changed details. The signature shows control of the wallet key; it does not prove legal identity, validate an invoice or show that a payment was received.
