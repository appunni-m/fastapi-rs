# Prospective generator awaitable adapter

## Status and frozen artifacts

This is an unapplied, uncompiled Rust draft. Only files under `/private/tmp` were
written. No formatter, build, application execution, parity runner or unit tests
were run by this author. Root owns later admission and verification.

The base is the exact current `fastapi-rs/src/awaitable.rs` snapshot captured at
repository HEAD `a03de4bb06bce926a92b947430272381b71b8285`:

| Artifact | SHA256 |
| --- | --- |
| `fastapi-rs-generator-awaitable-base-edb5dcc2.rs` | `edb5dcc26a44581467067d17830cb16e17079678c7d792c9c2adc7bd6c3cb2b1` |
| `fastapi-rs-generator-awaitable.rs` | `27efe46f9e046d5cd9d40d4254cd76280362c011b334d2cd8b0496cceb342dc6` |
| `fastapi-rs-generator-awaitable.patch` | `d804df721ae99e647d3bd3d9e72610b83f5860d86031a3d3f7d8bab90b3846cd` |

## Source evidence

Pinned CPython 3.12.13
[`genobject.c:940-996`](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c#L940-L996)
accepts an original exact native coroutine or iterable-coroutine generator
directly. A native coroutine or flagged generator returned by `__await__` is
rejected before checking iterator status. Ordinary noniterator errors use the
source wording.

[`_gen_throw:440-475`](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c#L440-L475)
distinguishes exact generator/coroutine delegation from generic iterator throw.
Generic forwarding stops at the first absent argument; an incoming
single-instance throw is not universally expanded to three arguments.
[`gen_throw:537-562`](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c#L537-L562)
warns for the public multiargument form. Pinned `asyncio/tasks.py:316` supplies a
single exception; `contextlib.py:231` likewise uses single-instance `athrow`.

Pinned `types.py:275-297` and `inspect.py:468-474` establish the public decorator
and awaitability inputs. FastAPI 0.141.1 `dependencies/utils.py:659-676` retains
generator classification before coroutine await and worker invocation;
`routing.py:342-354` defines the endpoint boundary.

## Draft behavior and ownership

`DelegatedIterator` holds one owned Python object and a Rust throw-protocol flag.
Original exact native coroutines and flagged generators keep their original
identity and receive single-exception throw. This retains original-object
provenance and avoids converting native coroutines into coroutine wrappers.

Returned exact ordinary generators also receive single-exception throw. The
existing three-argument Rust branch for generic user-returned iterators,
including coroutine wrappers, is retained as an unproven arity gap. Rejected
returned coroutines/generators never enter delegated state.
The integer-result error wording is corrected.

All decisions use safe PyO3 APIs and Rust control flow. Type identities come from
immutable pinned `types` bindings; generator flags use the pinned `0x100` code
flag. PyO3 0.29.2 `err/mod.rs:236-247` shows that `into_value` retains the original
exception object and attaches its saved traceback before single-argument throw.

Reading public `gi_code` invokes
[`gen_getcode:711-724`](https://github.com/python/cpython/blob/v3.12.13/Objects/genobject.c#L711-L724),
which emits an audit event. CPython's internal code lookup does not emit this
extra event. Audit hooks can observe it, introduce side effects or reject the
read; that fidelity is outside the 13-case boundary.

The existing drive/resume/close state machine owns sequencing and cleanup. Its
yielded Future, sent value, completion value and failure paths keep the same
representation. This patch adds no Python facade code, public class, export,
runtime dependency, unsafe block or lint suppression.

## Inputs and remaining boundaries

The independently authored, corrected proposal under
`/private/tmp/fastapi-rs-generator-awaitable-proposal-2026-10-05/` remains
**13 parity cases / 40 HTTP actions**. Its positional factory and ordered ASGI
selector match schema @9. It preserves full error class/message, warning
category/message, raw sends, generator identity/state, Future failures, scoped
cleanup and explicit recovery. No expected outputs or normalization were added.

These inputs have not been admitted against live source or target by this
reviewer. Their genuine async bridge is success-only; native coroutine warning
behavior under Future failure is not a passing claim. Arbitrary returned
coroutine wrappers and generic iterator throw protocols need separate inputs.

Independent runtime review gave bounded static clearance for original native
coroutine/flagged-generator acceptance, returned coroutine/generator rejection,
and native/returned ordinary-generator single-instance throw. It found no
apparent new Rust type, borrow, unsafe or panic issue. Drive/send/close and
result/error routing remain unchanged. This is static review, with no build or
live execution. The present revision changes comments and documentation only.

Other outstanding boundaries include mutable standard-library bindings,
type-slot versus instance `__await__` lookup, ABC-only registration, native
coroutine reuse/already-awaited checks, exact traceback/frame observations,
arbitrary send/throw normalization, cancellation and concurrent warning capture.
Classification history, endpoint/worker selection, dependency caching, generic
sibling scheduling and background-task transfer remain separate work.

Root may apply only after the current regression receipt freezes. Formatting,
Clippy, static contracts, identity-checked source/target parity and public
metadata activation are pending.
