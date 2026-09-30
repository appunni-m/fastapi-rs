# FastAPI dynamic runtime surface review

## Scope and pinned authority

This review concerns the observable Python surface of FastAPI `0.141.1` under
CPython `3.12.13`, Pydantic `2.13.4`, and Starlette `1.6.0` as the sole generic
ASGI oracle. The pinned source checkout is `/Users/lazytrot/work/fastapi`, tag
`0.141.1`, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`; the selected
Starlette source is commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
Runtime reflection metadata independently records the same versions and Python
identity in `tests/fixtures/runtime-api-surface-core.json` and
`tests/fixtures/runtime-api-surface-standard.json`.

The manifest still marks
`unresolved.dynamic_python_surface` as unresolved and asks about runtime-added
attributes, wrappers, signatures, and warnings (`tests/fixtures/manifest.yaml:277-283`).
This draft records what the existing evidence covers and what is still missing;
it does not change support classification or claim parity.

## Findings at a glance

The current reflection work is broad and useful: the source inventory contains
48 modules, 651 import bindings, and 19 source-deprecation records. The core
profile reflects 1,590 source candidates; the standard plus docs-tests profile
reflects 1,592, with `fastapi.__main__` intentionally skipped. The profiles
also record 43/44 runtime-only names, 197 object-identity groups, 49
Pydantic-generated model classes, signatures, and one import warning. The
manifest links these artifacts to a reviewed 452-symbol API contract
(`tests/fixtures/manifest.yaml:99-111, 215-234, 484-525`).

There is documentation count drift to resolve before citing a single denominator:
`docs/API_SCOPE.md:20-29` still describes 439 symbols, 215 reflected signatures,
and 222 non-callable values, while the manifest contract reports 452 symbols,
222 reflected signatures, and 228 non-callable values. The detailed runtime
surface counts are profile-specific and should remain separate from the
reviewed target-contract count.

The remaining gap is mostly *behavioral and process-shaped*, not absence of a
source or reflection inventory. The artifacts record imported object identity,
callable signatures, and `__deprecated__` metadata. They do not establish
cold-import behavior, call-time warning behavior, logging, implicit package
attributes as a supported API, or attributes created on app/router instances.
The direct Python API workflow can call reviewed functions and read reviewed
module attributes, but cannot import/compare aliases through its selectors or
read attributes from a newly constructed instance.

## Observable package and module attributes

`fastapi/__init__.py` defines `__version__ = "0.141.1"` at line 3 and has no
`__all__`. It binds `status` and 19 FastAPI names at lines 5-25; the 20 names
are documented in `docs/API_SCOPE.md` under “Root import surface.” The source
inventory counts these as 21 root candidates when `__version__` is included.
Root `status` is an identity reexport of `starlette.status`, not a FastAPI-owned
module.

Importing the package also leaves submodule objects bound on the package
object. The runtime profile records 41 public names on the root module: 20
explicit reexports plus 21 runtime-only names. `__version__` is the 21st
source candidate, but it begins with an underscore and so is excluded from the
reflection script's public-name count. Both the current core and standard rows
report 21 root runtime-only names, chiefly `fastapi.applications`, `fastapi.background`,
`fastapi.responses`, `fastapi.routing`, and other imported submodules. They
are recorded with `included_in___all__ = false`.

One delegated namespace edge remains dynamic: FastAPI binds the entire
`starlette.status` module at `fastapi/__init__.py:5`. Starlette 1.6.0 defines
four deprecated status aliases in `starlette/status.py:182-187`; its module
`__getattr__` warns and returns their integer values, and `__dir__` adds those
names (`starlette/status.py:190-211`). The FastAPI runtime row records the
module's `__deprecated__` mapping as metadata, but the FastAPI source inventory
does not create separate candidates for those nested names or observe access
warnings. Verify the root-module identity and let the Starlette 1.6.0 contract
own the values and warning semantics.

There is a small representation ambiguity: `scripts/inventory_fastapi_runtime.py:492-497`
stores an empty `all_names` list both when `__all__` is absent and when it is
present but empty. `fastapi/__init__.py` is known from source to have no
`__all__`, but the runtime artifact alone cannot express that distinction.
Also, runtime-only attributes are recorded by module path, kind, identity, and
`__all__` membership, but their values are not generally projected. In
particular, `fastapi.responses` conditionally binds `ujson` and `orjson` or
`None` (`fastapi/responses.py:27-36`), so package extras can alter values and
call behavior.

The reflection inventory iterates all pinned FastAPI modules and records
runtime-added module names in `runtime_only_names` (`scripts/inventory_fastapi_runtime.py:485-530`).
It records direct aliases for reflected module, class, and callable objects in
`object_identity_alias_groups` (`:511-531`). This is evidence about those two
oracle profiles, not a target support claim. The API contract records alias
references for 46 reviewed symbols, while identity comparison in a live
workflow remains planned.

## What is already captured

| Surface | Current evidence | Limit |
| --- | --- | --- |
| Source-defined names and import bindings | `tests/fixtures/api-inventory.json`: 48 Python modules, 651 bindings, 21 root candidates, 19 source deprecations. | Inventory is discovery evidence; classification and target support remain separately reviewed. |
| Runtime module namespace names | Core/standard artifacts record public name counts, names absent from source candidates, selected `__all__` members, import errors, and optional-feature gaps. | `__all__` absence and empty value are conflated; runtime-only values are summarized as kind and qualified identity, not generally captured. |
| Callable/class signatures | Reflection stores ordered parameter names/kinds/defaults/annotations and return annotation; the contract currently marks 222 symbols as runtime-signature-reflected and one as unavailable. Direct API workflow supports signature observations. | This is CPython 3.12.13 only. `inspect.signature` output is not proof that a wrapper emits the expected call-time warning or preserves all wrapper metadata. |
| Object aliases | The runtime surface records 197 `is`-identity groups from reflected module/class/callable values. Root exports’ source targets are inventoried. | The direct API workflow has no import-path or identity action; the catalog marks `python.import_path` and `python.object_identity` as planned. |
| PEP 702 deprecation metadata | `_runtime_symbol` records `getattr(value, "__deprecated__", None)` (`scripts/inventory_fastapi_runtime.py:354-371`). The signature encoder also records selected `Annotated` metadata. Deprecated classes and `on_event` methods therefore have reflected metadata. | Metadata is not a warning observation. The artifact does not invoke the decorated object or capture warning category, message, location, count, or ordering. |
| Pydantic-generated structures | Reflection captures typed-dict shape and 49 model classes’ fields plus inherited public Pydantic members (`scripts/inventory_fastapi_runtime.py:213-233, 279-307, 365-371`). | It does not prove model validation/serialization/schema behavior. The manifest separately leaves Pydantic-generated API review unresolved. |
| Module import warnings | Reflection records one `StarletteDeprecationWarning` while importing `fastapi.middleware.wsgi`; it records module, category, and message in `runtime-api-surface-standard.json:125953-125958`. | No filename/line, logging output, or fresh-root-import trace is recorded. Reflection first imports `fastapi` at `scripts/inventory_fastapi_runtime.py:397`, before its per-module warning capture at `:450-483`. |
| Optional modules and CLI entrypoint | Core profile marks `fastapi.templating` and `fastapi.testclient` unavailable; standard plus docs-tests imports them. Both current profiles skip `fastapi.__main__` because importing it calls `main()` (`fastapi/__main__.py:1-3`). | No compatibility claim for other optional-feature sets or CLI behavior. Never import `fastapi.__main__` as part of an ordinary API-surface probe. |

The unversioned `runtime-api-surface.json` is an earlier profile: it attempted
`fastapi.__main__` and records a missing-extra failure. Current contract
references are explicitly the core and standard profiles in
`tests/fixtures/manifest.yaml:215-234, 466-476`.

## Source-backed dynamic cases still needing observation

### Package identity and import behavior

The explicit root bindings and their targets are listed in
`fastapi/__init__.py:5-25`. High-value identity pairs include
`fastapi.FastAPI` / `fastapi.applications.FastAPI`, `fastapi.Query` /
`fastapi.param_functions.Query`, and `fastapi.status` / `starlette.status`.
The reflection file reports identity groups, but the current direct API runner
cannot assert them as input-driven observations. Its supported probe grammar
resolves a reviewed callable or attribute (`scripts/parity/api_worker.py:287-347`)
and the direct workflow v3 schema only defines return value, attribute value,
signature, and call outcome (`tests/fixtures/schemas/python-api-workflow-v3.schema.json:98-144`).
`python.import_path` and `python.object_identity` exist in the selector catalog
but are marked `planned` (`tests/fixtures/observation-selectors.json:233-243`).

A cold-import process probe is also distinct from the current module-reflection
loop. The parity worker's identity check imports `fastapi` before a workflow is
run (`scripts/parity/worker.py:176-186`), while the reflection script itself
imports it before starting per-module warning capture (`scripts/inventory_fastapi_runtime.py:397, 450-483`).
Those are appropriate for identity-checked behavior runs, but cannot capture
warnings or output emitted by a genuinely first `import fastapi`. If cold import
is part of the target contract, collect distribution/source identity without
importing FastAPI, then capture the first import in that isolated process.

### Instance attributes and class wrappers

`FastAPI.__init__` creates observable instance state, including `openapi_schema`,
`webhooks`, `root_path`, `state`, router-related values, and lifecycle/config
fields (`fastapi/applications.py:58-1018`; representative initialization at
`:924-950`). The documented app attributes include `router`, `routes`,
`exception_handlers`, `middleware_stack`, and `openapi_schema`
(`docs/API_SCOPE.md`, “Public app attributes”). Import-surface reflection never
constructs an app. The direct API workflow reads a module-level attribute only;
its path resolver starts at `importlib.import_module(module)` and follows names
from that module (`scripts/parity/api_worker.py:297-316`). It cannot read
`app.router`, compare an instance’s router identity with another object, or
record instance-specific route fields.

`APIRouter` is a FastAPI subclass of `starlette.routing.Router`
(`fastapi/routing.py:91, 2255`); its constructor is at `:2282-2569`. Its
constructed fields and included-route tree have the same gap as app-instance
attributes. Keep generic routing behavior assigned to Starlette 1.6.0, while
testing FastAPI-owned route registration and conversion at the integration
seam.

Runtime signatures do capture Python-visible wrappers, including
`FastAPI.on_event`, `APIRouter.on_event`, and the deprecated response classes.
The reflected signature of the response classes is a generic `(*args,
**kwargs)` wrapper, which differs from the inherited response constructor and
must not be replaced by a hand-written “cleaner” signature. The existing
signature fixture covers `FastAPI` and `APIRouter` HTTP verb decorators, but
does not on its own test wrapper call outcomes or warning effects
(`tests/fixtures/input-recipes/parity/operation-signatures-upstream.yaml:7-152`).

### Warnings, deprecations, and logs

Source evidence distinguishes three observable mechanisms:

| Case | Pinned source evidence | Observation needed |
| --- | --- | --- |
| Deprecated signature parameters | `FastAPI(routes=...)` and `FastAPI(openapi_prefix=...)` have `deprecated(...)` annotation metadata (`fastapi/applications.py:73-94, 625-639`); `APIRouter(routes=...)` has similar metadata (`fastapi/routing.py:2353-2374`). | Preserve annotation/signature metadata. Do not assume each annotated parameter emits a runtime warning. For `routes`, Starlette 1.6.0 owns the inherited constructor path and its exact warning behavior should be observed there. |
| `on_event` decorated methods | Both methods are decorated with `typing_extensions.deprecated` (`fastapi/applications.py:4654-4682`; `fastapi/routing.py:6415-6445`). | Call each method in an isolated direct-API case and compare warning category, message, filename/line, multiplicity, and outcome. The runtime artifact only records `__deprecated__` text. |
| `openapi_prefix` construction log | A nonempty prefix causes `logger.warning(...)` (`fastapi/applications.py:929-949`); `root_path` then falls back to it at `:949`. | Capture a logging record and selected resulting attribute. `python.warnings` does not see `logging.Logger.warning`. |
| `example` / `regex` FieldInfo construction warnings | `Param.__init__` emits `FastAPIDeprecationWarning` for supplied non-sentinel `example` and non-null `regex` (`fastapi/params.py:29-109`); body fields repeat those checks (`:460-554`). The helper signatures expose these deprecated args (`fastapi/param_functions.py`, e.g. `Path` lines 166-176, 236-242). | Call the corresponding public `Path`/`Query`/`Body` helpers with one deprecated value at a time; compare ordered warning records. Check resulting field metadata in a process-level object probe or through OpenAPI output. Signature metadata alone is insufficient. |
| Deprecated helper `**extra` | Helper signatures mark `**extra` with deprecated `Annotated` metadata (for example, `Path` at `fastapi/param_functions.py:289-301`). `Param` and `Body` merge these values into `json_schema_extra`; their explicit warning branches cover `example` and `regex` (`fastapi/params.py:74-110, 519-569`). | Preserve deprecated signature metadata separately from call-time warnings. Do not infer a warning from the annotation; observe any warning and the resulting schema effect independently. |
| Deprecated response wrappers | `UJSONResponse` and `ORJSONResponse` are `@deprecated` classes (`fastapi/responses.py:39-48, 69-78`) and their `render` methods require optional packages (`:64-66, 94-98`). | Observe warning plus return/error outcome in profiles that specify whether `ujson`/`orjson` are present. A missing encoder may fail after the warning; preserve that state rather than attributing it to the decorator. |
| Deprecated helper functions | `generate_operation_id_for_path` and `generate_operation_id` call `warnings.warn` (`fastapi/utils.py:80-92`; `fastapi/openapi/utils.py:266-278`). | If classified as consumer-visible, add call-warning probes; do not infer their runtime warning from source deprecation metadata. |
| Import-time WSGI deprecation | `fastapi/middleware/wsgi.py:1-3` reexports Starlette's middleware; the reflection artifact observes Starlette's deprecation warning. | In a fresh process, import this module and capture warning location as well as category/message and bound-object identity. |

The direct API workflow already supports ordered warning capture for a
selected direct-call/construction probe via `capture_warnings: true`; its
`python.warnings` projection includes category, message, normalized filename,
and line (`tests/fixtures/observation-selectors.json:251-255`,
`scripts/parity/api_worker.py:99-128, 422-528`). It cannot capture logger
records, and an import-path probe is not currently expressible. Source inventory
lists 19 deprecation records; the reviewed symbol contract currently maps 13
deprecation references (`tests/fixtures/manifest.yaml:106-111, 513-525`). These
counts are different review layers; neither alone closes warning behavior.

## Recommended input-only fixture work

Keep these as reviewed designs until their selectors and process handling exist;
do not put expected outputs in the recipes.

1. **Cold package-import process workflow** — add an input-only recipe under
   `tests/fixtures/input-recipes/parity/` and a workload/process fixture under
   `tests/fixtures/workloads/`. Each case should start in a clean interpreter,
   identify the pinned checkout and distribution before the first FastAPI
   import, then report module import success/failure, declared and runtime-only
   root names, `__all__` presence and value, selected import paths, and selected
   alias `is` relations. Run a core profile and the locked standard/docs-tests
   profile separately. Keep `fastapi.__main__` excluded; importing it executes
   the CLI.
2. **Package/import selector support** — promote `python.import_path` and
   `python.object_identity` from `planned` only after the API workflow schema,
   runner, comparator, and reviewed input format can express them. Add a
   namespace or presence selector that distinguishes absent `__all__` from an
   empty list and records only explicit selected names/values. Capture
   import-time warning filename/line and stdout/stderr separately from the
   existing call-warning selector.
3. **Direct signature/deprecation calls** — add cases to a direct-API recipe
   for the root/module aliases; `FastAPI.__init__`, `APIRouter.__init__`, and
   their `on_event` methods; the distinct `param_functions` helper and `params`
   class signatures; and deprecated `UJSONResponse`/`ORJSONResponse`. Use
   `python.signature` for reflected signatures and `python.warnings` plus
   `python.call_outcome` for call-time effects. Separate `example` and `regex`
   arguments so warning ordering is attributable; use explicit dependency
   profiles for optional JSON encoders.
4. **Construction and instance-attribute process workflow** — add a process
   action that constructs `FastAPI` or `APIRouter`, then reads only selected
   JSON-safe attributes and type/identity facts: `root_path`, `webhooks`,
   `state`, `router`, `routes`, `exception_handlers`, `middleware_stack`, and
   `openapi_schema`. Include the `openapi_prefix` case with a captured log
   record. For route lists, project an explicit stable subset such as route
   type, path, methods, and name. Do not serialize arbitrary Python object
   graphs.
5. **ASGI integration for runtime-derived effects** — use existing
   Python/ASGI workflow selectors for OpenAPI output, route behavior, lifecycle,
   validation and serialization once the construction probe has established
   the configuration. Keep Starlette-owned generic behavior in Starlette's
   contract and normalize only documented differences.

The applicable selectors already defined are `python.signature`,
`python.warnings`, `python.call_outcome`, and `python.attribute_value`.
`python.import_path` and `python.object_identity` are present but planned. Add a
logging-record projection and either a selected instance-attribute projection
or a carefully bounded extension of `python.attribute_value` before claiming
the construction cases. Compare oracle and target in identity-checked isolated
processes; do not treat reflection JSON as behavioral parity.

## Review disposition

The source and reflection evidence establishes a strong CPython 3.12.13
candidate inventory, including the root aliases and many dynamic names. It does
not close the manifest's unresolved dynamic-surface item. The next concrete
contract step is to specify cold import, alias identity, constructor/decorator
warning and logging behavior, and constructed app/router attributes as
process-level observations. Any warning semantics inherited from Starlette,
especially deprecated `routes`, remain unclaimed until checked against the
pinned Starlette 1.6.0 oracle.
