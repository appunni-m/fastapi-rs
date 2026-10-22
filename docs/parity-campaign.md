# Declared parity campaign ledger

`make parity-campaign` writes a deterministic, content-addressed report under
`parity-results/campaign/`. It starts with one `not_run` row for each indexed
parity workflow, case, and requirement reference. The separate
`fault_contract_cases` lane records target-only fault contracts without adding
them to the parity denominator. The target identity includes the combined
FastAPI-RS and pinned Starlette-RS source-tree digest. Evidence is accepted
only when those checkouts are clean, the revisions match their pins, and the
recorded target digest matches the current sources. The campaign command first
runs a read-only recipe, materialized-input, and mapping freshness check.
With no comparison paths, the report keeps all rows at `not_run`.

To include comparison artifacts, pass their repository-relative paths
explicitly:

```sh
make parity-campaign PARITY_CAMPAIGN_COMPARISONS='parity-results/comparisons/<id>.json parity-results/process/comparison/<id>.json'
```

Only a comparison that matches the current indexed input, manifest, workflow
schema, pinned FastAPI and Starlette profiles, Starlette-RS profile, current
FastAPI-RS revision and combined source-tree digest, product result hashes,
selected profiles, and recorded runner commands can assign `pass` or `fail`.
An unselected case remains `not_run`; malformed, stale, incompatible, or
overlapping artifacts are listed in `invalid_evidence`, and affected rows stay
`not_run` with a reason. Conflicting artifacts are both rejected before any of
their rows are counted. The report records accepted comparison and
product-result identities for review.

The denominator is named `declared-indexed-fixtures`. It reflects only the
currently indexed inputs and their reviewed requirement references. The report
carries the manifest's `foundation-incomplete` status and API scope counts; it
does not represent all FastAPI behavior and cannot support a 100 percent
compatibility claim. Generated reports stay in the ignored `parity-results/`
tree.
