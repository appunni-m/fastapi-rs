# Existing route-invocation fault companion: bounded feasibility

Inactive static note, 2026-10-05. No fault case is authored or activated here.
The three proposed recovery inputs remain ordinary live-oracle parity cases.

## Existing point and contract

Schema @9 already pairs `http.route.invoke.before` with
`http-route-invocation-error-and-recovery`
(`tests/fixtures/schemas/python-asgi-workflow-v9.schema.json:520-569`). The point
is reached in native `application_runtime.rs:10915-10935`, after route matching
and included-field materialization, before ordinary dependencies/endpoint
invocation. The inspected pre-traversal7 matching path calls field
materialization at `application_runtime.rs:10274` before selecting/invoking its
matched route; later traversal7 implementation review must preserve that point
placement when this note is reconsidered.

The canonical target worker arms the existing private native control before
running the case and clears it in finally
(`scripts/parity/target_worker.py:550-575`). The public workload must never call
those controls. The oracle skips this target-only case as not_applicable and
performs no case actions (`scripts/parity/worker.py:1388-1401`); it supplies no
reference outcome for construction/callback/cache state.

## Small feasible companion

One fresh unarmed included traced-field app could supply **one target-only case
with two HTTP actions**: first GET the cold included endpoint with application
exception + send sequence + status observations; then GET the same endpoint
again with HTTP status/body observations. It would reuse the normal workload's
public declarations, handler for its own schema error and callback journal,
without arming a schema rejection. That handler does not catch RuntimeError.
The native point can thus expose the existing generic 500/re-raised error and
later public success. A third `/state` read could retain the full callback,
warning and raw-send journal as diagnostics if admitted separately.

There must be no earlier `/state` or `/arm` action: the point is armed before
the case and the first eligible direct route would consume it. The basic named
contract requires exactly one application_error observation in the whole case.
Unlike the normal recipe's shared observations, only the first fault action
should select application_error; successful observations with null exception
fields still count as application_error rows. Canonical static validation also
requires the initial exception action followed by a status-observing HTTP
action (`scripts/parity/contract.py:815-903`).

## What the comparator actually verifies

`scripts/parity/fault_contracts.py:125-210` requires:

1. The target case has completed status.
2. Exactly one application_error observation selects exception and records
   `builtins.RuntimeError`; that action has completed status.
3. Exactly one ASGI-send observation on that action has the ordered two-message
   sequence http.response.start, http.response.body.
4. Exactly one HTTP response observation on that action reports status 500.
5. At least one later completed HTTP response reports integer status 200.

`scripts/parity/comparator.py:618-651` checks this named target contract rather
than comparing its observations with an oracle record. This is honest evidence
for a public internal error and later success on the supplied input. The chosen
same-path second action makes its successful request diagnostically useful,
but the comparator itself does not require recovery at the same path.

It does **not** assert the RuntimeError message, error/recovery headers or body,
exact full raw send fields, callback execution/order/counts, endpoint-call
absence on the failing action, warning restoration, validation/serialization
reuse, field identity, cache retention, branch readiness/version, absence of
partial construction publication or lack of reconstruction on recovery.
Adding these journals as selected result data alone does not make their values
an asserted fault contract. A passed companion cannot claim response-adapter
cache state or equivalence to the source.

## Boundaries and decision

This companion is feasible for the existing **error/500/later-200** contract,
with the existing feature-controlled build, fixed normal/fault binary identity,
separate receipt lane and N/A oracle treatment. It is lower-value evidence for
response-field retention than the three normal public schema-hook controls:
the point occurs after successful construction, and the existing comparator
does not inspect the recovery journal. No support or live outcome is claimed.

The dependency-cleanup contracts on
`http.route.invoke.after_dependencies.before` are unsuitable substitutes:
they require one later 200 response body with an exact pre-existing dependency
event shape (`fault_contracts.py:213-260`), and they do not assert adapter state.
Extra state actions or adapter journals cannot be substituted for that shape.
No comparator/hook extension or contract weakening is proposed. Stronger
target-only adapter-retention assertions would require a separately reviewed
contract and admission; this task does not authorize them.
