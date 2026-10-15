# Documented dependency-override ownership review

Date: 2026-10-16  
Kata: `m4d4`  
Scope: documented Python example rows in `tests/fixtures/compatibility-atlas.json` whose `feature_ids` include `dependency-overrides` and whose sibling mapping says `ownership_boundary: owner review required`.

## Result

The filter finds ten `documented_python_example_source` rows: atlas coverage-matrix indexes 162, 163, 416, 419, 420, 423, 424, 427, 430, and 431. Six rows map to independent ASGI inputs that exercise dependency replacement in FastAPI. Four rows are settings projections or ordinary dependency injection without an override; their `dependency-overrides` association comes from the containing settings documentation page.

The override map, replacement lookup, replacement-signature analysis, and dependency graph solving are FastAPI-owned. Every mapped workflow also traverses the generic Starlette ASGI application/router and response path. The recipes call the application as ASGI and observe response status/body; they do not invoke the examples' `TestClient`. A sibling Starlette link identifies generic ownership only. It is not evidence of FastAPI-RS parity.

Pinned sources used:

- FastAPI 0.141.1: `/Users/lazytrot/work/fastapi`, exact tag `0.141.1`, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`.
- Starlette 1.6.0: `/Users/lazytrot/work/starlette`, exact tag `1.6.0`, commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
- Starlette-RS: `/private/tmp/fastapi-rs-starlette-rs-4139`, commit `4139a72449bf5751e8902fb1c7175ee7f191d338`.

## Ownership evidence

FastAPI documents `FastAPI.dependency_overrides` as an instance dictionary keyed by the original callable and valued by the callable to use instead (`fastapi/applications.py:967-983`). FastAPI passes the app as the router's override provider (`fastapi/applications.py:984-988`). During solving, FastAPI looks up the original dependency, rebuilds a `Dependant` from the replacement callable, and recursively solves that replacement graph (`fastapi/dependencies/utils.py:619-649`). Those behaviors have no generic Starlette operation counterpart.

For the tutorial cases with `q`, FastAPI reads `request.query_params` when extracting dependency parameters (`fastapi/dependencies/utils.py:681-695, 749-777`). Starlette's `Request.query_params` constructs a `QueryParams` from the ASGI `query_string` (`starlette/requests.py:138-142`). This is a generic request-value boundary; FastAPI owns the choice of dependency fields, defaults, validation, and replacement signature.

The independent inputs use the `fastapi-rs/python-asgi-workflow` schema and send ASGI requests directly. The tutorial recipe declares `http_request` actions and exact status/body observations (`tests/fixtures/input-recipes/parity/atlas-testing-websocket-dependency-overrides.yaml:7-43`); its workload installs the override on a FastAPI app (`tests/fixtures/workloads/atlas_testing_websocket_dependency_overrides.py:14-28`). The settings recipes do the same for `/info` (`tests/fixtures/input-recipes/parity/docs-settings-injection.yaml:7-40`; `tests/fixtures/workloads/docs_settings_injection.py:18-34`) and `/profile` (`tests/fixtures/input-recipes/parity/middleware-proxy-static-settings-source-review.yaml:128-161`; `tests/fixtures/workloads/middleware_proxy_source_review.py:103-120`).

The ASGI request itself traverses Starlette's app call and router dispatch (`starlette/applications.py:92-96`; `starlette/routing.py:666-720`). FastAPI's route wrapper invokes the response as an ASGI application (`fastapi/routing.py:134-145`); Starlette `Response.__call__` sends `http.response.start` and `http.response.body` (`starlette/responses.py:163-171`). Those are separate generic boundaries from dependency override resolution.

The documented source examples import or construct `TestClient` (for example, the tutorial rows use `docs_src/dependency_testing/tutorial001_an_py310.py:4, 23` and `docs_src/dependency_testing/tutorial001_py310.py:2, 21`; settings test examples use `test_main.py:1, 6`). Their mapped ASGI recipes do not execute those calls, so no `starlette.testclient.TestClient` operation or requirement should be attached to these rows.

## Row-by-row findings

| Atlas row key | Source and mapped input | Override observation and ownership |
| --- | --- | --- |
| `documented-example:docs_src/dependency_testing/tutorial001_an_py310.py` | FastAPI source defines the shared dependency and two routes at lines 9-20, creates `override_dependency` and registers it at lines 23-30. Mapped case: `fastapi.atlas-testing-dependency.overrides`. | The ASGI workload registers the replacement and observes item/user response status/body for default, `q`, and supplied `skip`/`limit` inputs, including plain and `Annotated` declarations. Override lookup/replacement is FastAPI-owned. The `q` query-string value also passes through generic `Request.query_params`; the recipe does not probe `TestClient`. |
| `documented-example:docs_src/dependency_testing/tutorial001_py310.py` | The source dependency/routes are at lines 7-18; `TestClient` and override registration are at lines 21-28. Same mapped case as above. | Same classification as the annotated variant: FastAPI-owned override and replacement signature; generic request/ASGI and response boundaries are separate. |
| `documented-example:docs_src/settings/app01_py310/main.py` | Source returns module-level settings from `/info` at lines 3-14. Mapped case: `fastapi.documentation-example.wave-h.settings.global-projection`. | No `Depends`, `dependency_overrides`, or replacement is present in this source or the mapped workload. It observes a settings response only. The override feature is inherited from the page and is not an example-level override observation. |
| `documented-example:docs_src/settings/app02_an_py310/main.py` | Source defines cached `get_settings` and injects it with `Annotated`/`Depends` at lines 11-22. Paired source `test_main.py` installs the replacement at lines 9-13. Mapped case: `fastapi.docs.settings.dependency-override`. | The independent ASGI workload observes the replacement route response, but does not execute this source file or its `TestClient`. This row supplies the original dependency/route side of a FastAPI-owned override case; override registration is explicit in the paired test row. Pydantic Settings parsing, environment behavior, and cache behavior are outside the mapped input. |
| `documented-example:docs_src/settings/app02_an_py310/test_main.py` | Source creates `TestClient`, defines `get_settings_override`, registers it, and asserts `/info` at lines 1-23. Same mapped case as above. | Direct FastAPI override registration and replacement-result observation. The independent input calls ASGI directly; it does not test `TestClient` mechanics or `lru_cache`. |
| `documented-example:docs_src/settings/app02_py310/main.py` | Source defines cached `get_settings` and injects it with `Depends` at lines 10-21. Paired `test_main.py` installs the replacement at lines 9-13. Mapped case: `fastapi.middleware-proxy.settings-dependency-override`. | The case observes dependency replacement through an independent `/profile` workload. The source row supplies the original dependency/route side; FastAPI owns replacement resolution. The input does not exercise Pydantic settings or cache behavior. |
| `documented-example:docs_src/settings/app02_py310/test_main.py` | Source creates `TestClient`, defines and registers `get_settings_override`, then asserts `/info` at lines 1-23. Same mapped case as above. | Direct FastAPI override registration. The mapped workflow substitutes a profile dependency and observes status/body through ASGI; it does not exercise `TestClient` or the source's Settings class. |
| `documented-example:docs_src/settings/app03_an_py310/main.py` | Source defines cached `get_settings` and uses `Annotated`/`Depends` at lines 11-22. Mapped case: `fastapi.documentation-example.wave-h.settings.dependency-projection`. | No override is registered in the source. The mapped `settings-dependency` workload uses the original dependency with no replacement. This is FastAPI dependency injection, not dependency override behavior; cache semantics are not observed. |
| `documented-example:docs_src/settings/app03_py310/main.py` | Source defines cached `get_settings` and uses `Depends` at lines 10-21. Same mapped case as above. | Same as the annotated variant: no replacement, no override lookup observation, and no cache claim. |
| `documented-example:docs_src/settings/tutorial001_py310.py` | Source constructs module-level `Settings` and returns its values at lines 5-21. Mapped case: `fastapi.documentation-example.wave-h.settings.global-projection`. | No dependency or override is present in this source or the mapped workload. It is global settings projection and response serialization only; the override feature is page-inherited. |

## Generic Starlette contract references

These references describe only the generic behavior observed around the FastAPI feature. The support states below are from the pinned Starlette-RS contract, not FastAPI-RS.

| Observed generic boundary | Pinned sibling contract reference | Sibling target support and limit |
| --- | --- | --- |
| All mapped recipes call the app through HTTP ASGI dispatch and observe status/body. | Surface `starlette.applications.Starlette`; operation `__call__`; requirement `starlette.asgi.get-hello.dispatch`. The related router operation is `request-dispatch`. | `python-package: supported`; `rust-native: partial` for both operations. These inputs observe successful route dispatch only; they do not cover the sibling requirement's complete headers/event comparison, route misses, wrong methods, or callable-form variants. Keep this generic reference under the existing app-routing boundary, not under dependency-overrides. |
| The tutorial override inputs pass a single-key query string and observe the injected `q` value in the response. | Surface `starlette.datastructures.QueryParams`; operation `construction-and-mapping-sequence`; relevant requirements `starlette.datastructures.QueryParams.constructor-string-and-percent-decoding` and `starlette.datastructures.QueryParams.immutable-multidict-lookup-and-iteration`. | `python-package: supported`; `rust-native: supported` in the sibling manifest. Only simple query construction and lookup are implicated here; repeated-key, percent-escape, and full multi-dict cases are not claimed. FastAPI still owns dependency parameter selection and validation. This is a separate request-input boundary, not an operation for dependency overrides. |
| The ASGI recipes observe non-empty FastAPI response status/body emitted by the generic response call. | Surface `starlette.responses.Response`; operation `asgi-call`; related requirement `starlette.responses.Response.asgi-call.non-empty-response`. | `python-package: supported`; `rust-native: supported` in the sibling manifest. The inputs do not isolate Starlette response construction or media-type defaults; FastAPI owns dictionary/JSON conversion. This identifies the send boundary only. |
| The source snippets use Starlette's `TestClient`, but the mapped parity inputs do not. | No `starlette.testclient.TestClient` operation or requirement is applicable to these independent ASGI workflows. | Do not add a client link based only on source imports/assertions that the mapped recipe does not execute. |

## Row-keyed overlay recommendation

For the six rows with an actual override case (the two dependency-testing examples and the two `app02` main/test pairs), add row-keyed `dependency-overrides` dispositions classifying the behavior as FastAPI-owned. Use empty `operation_specs`: Starlette-RS has no dependency override operation. Scope notes should distinguish the original dependency source row from its paired test row and state that the independent workload observes one response slice only.

For the four rows `app01_py310/main.py`, `app03_an_py310/main.py`, `app03_py310/main.py`, and `settings/tutorial001_py310.py`, record a row-keyed disposition that the `dependency-overrides` association is page-inherited and that no override is observed in the example or mapped workflow. Prefer removing those four from example-level `dependency-overrides` evidence if the atlas model supports it; otherwise preserve the association only with an explicit “no override observed” scope note and empty `operation_specs`.

The concrete row keys are the ten `documented-example:` IDs in the table. The existing helper in `scripts/atlas_starlette_ownership_review_mappings.py` manufactures only `upstream-test:` keys (`:22-40`), and `apply_starlette_ownership_row_overlay` currently rejects non-`upstream_test_module` rows (`scripts/build_fastapi_compatibility_atlas.py:10041-10051`). Supporting these entries therefore requires a deliberate generator extension for `documented_python_example_source`; do not silently route them through the upstream-test helper. If all ten entries are added, update the expected `dependency-overrides` overlay count from 3 to 13 (`scripts/atlas_starlette_ownership_review_mappings.py:14-19`; generator count guard at `scripts/build_fastapi_compatibility_atlas.py:11949-11961`).

Keep generic app dispatch, query parsing, and response emission in their own feature/ownership relationships. A sibling operation link records generic ownership and the sibling's target support state; it does not establish FastAPI-RS implementation, support, or parity.

## Work limits observed

Read the project `AGENTS.md`; did not edit active atlas overlays, generator, recipes, fixtures, metadata, or implementation. No tests, builds, parity runs, or benchmarks were run. This file is the only artifact written for the review.
