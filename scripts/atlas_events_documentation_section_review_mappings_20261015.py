"""Reviewed section mappings for FastAPI 0.141.1's Lifespan Events page.

This sidecar separates FastAPI registration/deprecation evidence from generic
ASGI lifecycle behavior owned by Starlette-RS. The atlas builder consumes only
the section-keyed mappings; the richer review notes remain evidence metadata.
"""

from __future__ import annotations

FASTAPI_SOURCE = {
    "version": "0.141.1",
    "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "path": "docs/en/docs/advanced/events.md",
}

STARLETTE_RS_TARGET = {
    "commit": "4139a72449bf5751e8902fb1c7175ee7f191d338",
    "role": "target implementation of the separate Starlette 1.6.0 generic contract",
}

EXISTING_RECIPE = "tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml"
SUPPRESSION_RECIPE = (
    "tests/fixtures/input-recipes/parity/fastapi-lifespan-event-suppression-review-20261015.yaml"
)

_LIFESPAN_SELECTORS = (
    "asgi.lifespan.application_errors",
    "asgi.lifespan.event_order",
    "asgi.lifespan.shutdown",
    "asgi.lifespan.startup",
    "asgi.lifespan.workload_trace",
)
_CONSTRUCTION_SELECTORS = (
    "construction.exception_class",
    "construction.exception_message",
    "construction.outcome",
)
_HTTP_SELECTORS = ("http.body.bytes", "http.status")

# These are the exact observed selector scopes. The ``fastapi_owned`` entries
# distinguish FastAPI registration effects from ASGI and HTTP transport output.
CASE_ACTION_SCOPES = {
    "fastapi.lifecycle.app-lifespan-state": {
        "recipe_path": EXISTING_RECIPE,
        "actions": {
            "construction_observation": {
                "observed": _CONSTRUCTION_SELECTORS,
                "fastapi_owned": (),
            },
            "lifespan": {
                "observed": _LIFESPAN_SELECTORS,
                "fastapi_owned": ("asgi.lifespan.workload_trace",),
            },
            "request": {"observed": _HTTP_SELECTORS, "fastapi_owned": ()},
        },
        "limit": (
            "The case uses a null yielded state and synthetic callback markers. It does not "
            "claim the tutorial's module-level model dictionary, request-time model lookup, "
            "or request interleaving between lifespan startup and shutdown."
        ),
    },
    "fastapi.lifecycle.router-events-legacy": {
        "recipe_path": EXISTING_RECIPE,
        "actions": {
            "construction_observation": {
                "observed": (*_CONSTRUCTION_SELECTORS, "python.warnings"),
                "fastapi_owned": ("python.warnings",),
            },
            "lifespan": {
                "observed": (*_LIFESPAN_SELECTORS, "warnings.category_message"),
                "fastapi_owned": ("asgi.lifespan.workload_trace",),
            },
            "request": {
                "observed": (*_HTTP_SELECTORS, "warnings.category_message"),
                "fastapi_owned": (),
            },
        },
        "limit": (
            "The case selects ordered callback effects and the construction warning. It has "
            "one handler per phase at each app/router level; it does not claim two decorators "
            "on the same app or request-gating timing."
        ),
    },
    "fastapi.lifecycle.async-shutdown-handler": {
        "recipe_path": EXISTING_RECIPE,
        "actions": {
            "construction_observation": {
                "observed": _CONSTRUCTION_SELECTORS,
                "fastapi_owned": (),
            },
            "lifespan": {
                "observed": _LIFESPAN_SELECTORS,
                "fastapi_owned": ("asgi.lifespan.workload_trace",),
            },
            "request": {"observed": _HTTP_SELECTORS, "fastapi_owned": ()},
        },
        "limit": "The case samples one async shutdown callback; it does not sample async startup.",
    },
    "fastapi.lifecycle.lifespan-suppresses-legacy-events": {
        "recipe_path": SUPPRESSION_RECIPE,
        "actions": {
            "construction_observation": {
                "observed": (*_CONSTRUCTION_SELECTORS, "python.warnings"),
                "fastapi_owned": ("python.warnings",),
            },
            "lifespan": {
                "observed": _LIFESPAN_SELECTORS,
                "fastapi_owned": ("asgi.lifespan.workload_trace",),
            },
            "request": {"observed": _HTTP_SELECTORS, "fastapi_owned": ()},
        },
        "limit": (
            "The input supplies a FastAPI lifespan context, constructor startup/shutdown "
            "callbacks, and legacy app handlers, then compares lifecycle markers plus "
            "registration warnings. The request is a separate action after the complete "
            "lifespan action, so no request-gating or interleaving claim is made."
        ),
    },
}

FASTAPI_EVENTS_DOCUMENTATION_REVIEW = {
    "source_spans": [
        {
            "selector": "#lifespan-events",
            "start_line": 1,
            "end_line": 165,
            "status": "mapped_partial",
            "case_ids": [
                "fastapi.lifecycle.app-lifespan-state",
                "fastapi.lifecycle.router-events-legacy",
            ],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "Callback setup/cleanup markers are observed. Before-request and after-all-"
                "requests timing belongs to the generic ASGI lifespan runner and is not "
                "established by this page mapping."
            ),
        },
        {
            "selector": "#use-case",
            "start_line": 11,
            "end_line": 24,
            "status": "excluded_example_logic",
            "case_ids": ["fastapi.lifecycle.app-lifespan-state"],
            "observed_selectors": list(_LIFESPAN_SELECTORS) + list(_HTTP_SELECTORS),
            "exclusion_reason": (
                "The fake ML function, module-level dictionary, disk-loading cost, and test "
                "startup optimization are user/example logic. The existing case is only a "
                "FastAPI lifespan-registration sample and does not model those values."
            ),
        },
        {
            "selector": "#lifespan",
            "start_line": 25,
            "end_line": 86,
            "status": "mapped_partial",
            "case_ids": ["fastapi.lifecycle.app-lifespan-state"],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "The case passes a context-manager lifespan through FastAPI and selects its "
                "startup/cleanup callback trace. Generic ASGI startup/shutdown protocol "
                "selectors remain Starlette-RS-owned."
            ),
        },
        {
            "selector": "#lifespan-function",
            "start_line": 47,
            "end_line": 56,
            "status": "mapped_partial",
            "case_ids": ["fastapi.lifecycle.app-lifespan-state"],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "The callback trace observes before-yield and after-yield effects. It does not "
                "observe their timing relative to individual HTTP requests."
            ),
        },
        {
            "selector": "#async-context-manager",
            "start_line": 57,
            "end_line": 86,
            "status": "mapped_partial",
            "case_ids": ["fastapi.lifecycle.app-lifespan-state"],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "The sample uses an async context-manager input. Python's contextlib mechanics "
                "and Starlette's generic context entry/exit are excluded from FastAPI-owned "
                "behavior."
            ),
        },
        {
            "selector": "#alternative-events-deprecated",
            "start_line": 87,
            "end_line": 148,
            "status": "mapped_partial",
            "case_ids": [
                "fastapi.lifecycle.router-events-legacy",
                "fastapi.lifecycle.async-shutdown-handler",
                "fastapi.lifecycle.lifespan-suppresses-legacy-events",
            ],
            "fastapi_selectors": [
                "python.warnings",
                "asgi.lifespan.workload_trace",
            ],
            "scope_note": (
                "The legacy decorator case captures the FastAPI deprecation warning and "
                "callback effects; an async shutdown case samples async callback dispatch. "
                "The combined case samples the documented lifespan/legacy-handler exclusion."
            ),
        },
        {
            "selector": "#startup-event",
            "start_line": 103,
            "end_line": 114,
            "status": "mapped_partial",
            "case_ids": ["fastapi.lifecycle.router-events-legacy"],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "The selected case records app and included-router startup callbacks. It has "
                "one startup handler per level and does not establish that concurrent HTTP "
                "requests are held until every callback completes."
            ),
        },
        {
            "selector": "#shutdown-event",
            "start_line": 115,
            "end_line": 140,
            "status": "mapped_partial",
            "case_ids": [
                "fastapi.lifecycle.router-events-legacy",
                "fastapi.lifecycle.async-shutdown-handler",
            ],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "The cases sample sync and async callback effects. The tutorial's file open, "
                "append mode, and log contents are example code, not FastAPI behavior."
            ),
        },
        {
            "selector": "#startup-and-shutdown-together",
            "start_line": 141,
            "end_line": 148,
            "status": "mapped_partial",
            "case_ids": ["fastapi.lifecycle.app-lifespan-state"],
            "fastapi_selectors": ["asgi.lifespan.workload_trace"],
            "scope_note": (
                "The selected case records both sides of one lifespan context. The rationale "
                "for preferring one context manager is documentation guidance, not an additional "
                "observable contract."
            ),
        },
    ],
    "supporting_sources": [
        {
            "path": "fastapi/applications.py",
            "start_line": 527,
            "end_line": 538,
            "role": (
                "FastAPI constructor lifespan parameter and documented replacement of event "
                "handlers"
            ),
        },
        {
            "path": "fastapi/applications.py",
            "start_line": 4654,
            "end_line": 4681,
            "role": "FastAPI app on_event deprecation and delegation to its router",
        },
        {
            "path": "fastapi/routing.py",
            "start_line": 2520,
            "end_line": 2537,
            "role": (
                "FastAPI router chooses the default event-handler lifespan or supplied lifespan "
                "context"
            ),
        },
        {
            "path": "fastapi/routing.py",
            "start_line": 6363,
            "end_line": 6445,
            "role": "FastAPI event callback dispatch and deprecated on_event registration",
        },
    ],
    "exclusions": [
        {
            "selector": "#technical-details",
            "start_line": 149,
            "end_line": 162,
            "case_ids": ["fastapi.lifecycle.app-lifespan-state"],
            "observed_selectors": list(_LIFESPAN_SELECTORS),
            "exclusion_reason": (
                "ASGI lifespan message ordering, stage outcomes, and protocol errors are the "
                "generic Starlette 1.6.0 contract implemented by Starlette-RS. The linked "
                "Starlette state guidance is likewise not a FastAPI-specific claim."
            ),
        },
        {
            "selector": "#sub-applications",
            "start_line": 163,
            "end_line": 165,
            "case_ids": ["fastapi.lifecycle.mounted-subapp-lifespan-exclusion"],
            "observed_selectors": list(_LIFESPAN_SELECTORS) + list(_HTTP_SELECTORS),
            "exclusion_reason": (
                "The available input observes mount and lifespan behavior, but FastAPI 0.141.1 "
                "does not own generic mount dispatch. Starlette-RS owns that inherited contract; "
                "do not count these selectors as FastAPI event behavior."
            ),
        },
        {
            "selector": "#startup-event/request-gating",
            "start_line": 111,
            "end_line": 113,
            "case_ids": [
                "fastapi.lifecycle.router-events-legacy",
                "fastapi.lifecycle.lifespan-suppresses-legacy-events",
            ],
            "observed_selectors": [
                "asgi.lifespan.workload_trace",
                "http.body.bytes",
                "http.status",
            ],
            "exclusion_reason": (
                "The recipes run one complete lifespan action followed by a separate HTTP action; "
                "they do not interleave or race requests against startup callbacks. Request "
                "gating is generic server/Starlette lifecycle behavior."
            ),
        },
        {
            "selector": "#shutdown-event/file-append-example",
            "start_line": 121,
            "end_line": 139,
            "case_ids": ["fastapi.lifecycle.async-shutdown-handler"],
            "observed_selectors": ["asgi.lifespan.workload_trace"],
            "exclusion_reason": (
                "The workload trace records only the handler callback marker; file creation, "
                "append semantics, and log contents are user code and are not observed."
            ),
        },
        {
            "selector": "#unmentioned-router-lifespan-cases",
            "source_case_ids": [
                "fastapi.lifecycle.nested-lifespan-state",
                "fastapi.lifecycle.parent-lifespan-state-override",
                "fastapi.lifecycle.empty-merged-lifespan-state",
                "fastapi.lifecycle.mixed-merged-lifespan-state",
                "fastapi.lifecycle.sync-generator-lifespan",
                "fastapi.lifecycle.async-generator-lifespan",
                "fastapi.lifecycle.parameter-event-handlers",
                "fastapi.lifecycle.add-event-handler-invalid-string",
            ],
            "exclusion_reason": (
                "This page does not document APIRouter lifespan state merging, raw sync/async "
                "generator acceptance, constructor on_startup/on_shutdown parameters, or "
                "invalid event strings. Keep those independent inputs linked to their own "
                "source review rather than attributing them to this page."
            ),
        },
        {
            "selector": "#testclient-specific-observations",
            "source_spans": [
                {"path": "tests/test_router_events.py", "start_line": 71, "end_line": 87},
                {"path": "tests/test_router_events.py", "start_line": 104, "end_line": 112},
                {"path": "tests/test_router_events.py", "start_line": 155, "end_line": 171},
                {"path": "tests/test_router_events.py", "start_line": 197, "end_line": 243},
            ],
            "exclusion_reason": (
                "Those upstream assertions rely on TestClient context management or app_state. "
                "The independent inputs use direct ASGI; TestClient lifecycle driving and "
                "client state belong to the pinned Starlette-RS contract."
            ),
        },
    ],
}


def _workflow(heading, start, end, recipe, case_ids, action_ids, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": case_ids,
        "action_ids": action_ids,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_EVENTS_PAGE = "advanced/events.md"
_EVENTS_LIFESPAN = list(_LIFESPAN_SELECTORS)
_EVENTS_LEGACY_LIFESPAN = [*_LIFESPAN_SELECTORS, "warnings.category_message"]

DOC_SECTION_CASE_MAPPINGS_EVENTS_20261015 = {
    (_EVENTS_PAGE, "lifespan-events"): _workflow(
        "Lifespan Events { #lifespan-events }",
        1,
        165,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.app-lifespan-state", "fastapi.lifecycle.router-events-legacy"],
        ["lifespan"],
        _EVENTS_LEGACY_LIFESPAN,
        (
            "The selector projection includes generic ASGI lifespan observations and the "
            "lifespan action's warning-category capture channel. FastAPI-owned scope is the "
            "callback trace; the deprecation warning is construction-scoped and outside this "
            "action mapping. Separate lifespan and request actions do not establish "
            "before-request/after-all-requests timing."
        ),
        (
            "FastAPI wires its lifespan context into the router (fastapi/routing.py:2520-2537) "
            "and dispatches legacy event callbacks (fastapi/routing.py:6363-6445). The selected "
            "FastAPI-specific evidence is the callback trace; the page's resource setup and "
            "generic ASGI timing are not separately claimed."
        ),
    ),
    (_EVENTS_PAGE, "use-case"): _excluded(
        "Use Case { #use-case }",
        11,
        24,
        (
            "The machine-learning model, disk loading, module-level state, and test startup "
            "optimization are illustrative application logic."
        ),
        (
            "The independent lifespan case uses callback markers and null state; it does not "
            "model loading cost, resource sharing, or request-time model access."
        ),
    ),
    (_EVENTS_PAGE, "lifespan"): _workflow(
        "Lifespan { #lifespan }",
        25,
        86,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.app-lifespan-state"],
        ["lifespan"],
        _EVENTS_LIFESPAN,
        (
            "The selector projection includes generic ASGI protocol observations. FastAPI-owned "
            "scope is the synthetic callback trace from the supplied async context-manager "
            "lifespan; the case does not inspect the tutorial model dictionary or time requests "
            "against startup and shutdown."
        ),
        (
            "FastAPI 0.141.1 accepts a lifespan parameter and chooses it for router lifespan "
            "dispatch (fastapi/applications.py:527-538; fastapi/routing.py:2520-2537). The "
            "ASGI protocol outcome itself remains Starlette-RS behavior."
        ),
    ),
    (_EVENTS_PAGE, "lifespan-function"): _workflow(
        "Lifespan function { #lifespan-function }",
        47,
        56,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.app-lifespan-state"],
        ["lifespan"],
        _EVENTS_LIFESPAN,
        (
            "The selector projection includes generic ASGI protocol observations. FastAPI-owned "
            "scope is the before-yield and after-yield callback trace; it does not make a "
            "request-interleaving or Python generator-semantics claim."
        ),
        (
            "FastAPI passes the supplied lifespan context into router lifespan handling "
            "(fastapi/routing.py:2520-2537); the callback trace is the only selected FastAPI "
            "observation."
        ),
    ),
    (_EVENTS_PAGE, "async-context-manager"): _workflow(
        "Async Context Manager { #async-context-manager }",
        57,
        86,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.app-lifespan-state"],
        ["lifespan"],
        _EVENTS_LIFESPAN,
        (
            "The selector projection includes generic ASGI protocol observations. FastAPI-owned "
            "scope is the callback trace from the async context-manager input; Python contextlib "
            "mechanics and Starlette's generic ASGI lifespan runner remain outside that claim."
        ),
        (
            "FastAPI's constructor accepts and forwards the lifespan parameter "
            "(fastapi/applications.py:527-538; fastapi/routing.py:2520-2537)."
        ),
    ),
    (_EVENTS_PAGE, "alternative-events-deprecated"): _workflow(
        "Alternative Events (deprecated) { #alternative-events-deprecated }",
        87,
        148,
        SUPPRESSION_RECIPE,
        [
            "fastapi.lifecycle.lifespan-suppresses-legacy-events",
        ],
        ["lifespan"],
        _EVENTS_LIFESPAN,
        (
            "The linked case supplies both lifespan and legacy app handlers, but this mapping "
            "selects only its lifespan action. The selector projection includes generic ASGI "
            "observations; FastAPI-owned scope is the callback trace showing lifespan takes "
            "precedence. Construction-time warning capture is outside this action-scoped link."
        ),
        (
            "FastAPI's on_event method delegates registration and is deprecated "
            "(fastapi/applications.py:4654-4681; fastapi/routing.py:6363-6445). The combined "
            "recipe directly supplies both APIs; its lifespan action supports the selected "
            "callback-precedence observation, while generic protocol selectors remain harness "
            "observations."
        ),
    ),
    (_EVENTS_PAGE, "startup-event"): _workflow(
        "`startup` event { #startup-event }",
        103,
        114,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.router-events-legacy"],
        ["lifespan"],
        _EVENTS_LEGACY_LIFESPAN,
        (
            "The selector projection includes generic ASGI lifespan observations and the "
            "warning-category capture channel. FastAPI-owned scope is the ordered app and "
            "included-router callback trace; the deprecation warning is construction-scoped and "
            "outside this action mapping. It does not observe concurrent-request gating or the "
            "tutorial's database dictionary."
        ),
        (
            "FastAPI registers deprecated startup handlers through on_event and includes the "
            "router event callback list (fastapi/routing.py:6363-6445). Request scheduling is "
            "outside this selected behavior."
        ),
    ),
    (_EVENTS_PAGE, "shutdown-event"): _workflow(
        "`shutdown` event { #shutdown-event }",
        115,
        140,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.router-events-legacy", "fastapi.lifecycle.async-shutdown-handler"],
        ["lifespan"],
        _EVENTS_LEGACY_LIFESPAN,
        (
            "The selector projection includes generic ASGI lifespan observations and the "
            "legacy action's warning-category capture channel. FastAPI-owned scope is the "
            "synthetic synchronous and asynchronous callback trace; the deprecation warning is "
            "construction-scoped and outside this action mapping. File creation, append "
            "semantics, and log contents are not observed."
        ),
        (
            "FastAPI's deprecated on_event registration is in fastapi/routing.py:6363-6445. "
            "The selected workload traces callbacks only; file I/O is application code."
        ),
    ),
    (_EVENTS_PAGE, "startup-and-shutdown-together"): _workflow(
        "`startup` and `shutdown` together { #startup-and-shutdown-together }",
        141,
        148,
        EXISTING_RECIPE,
        ["fastapi.lifecycle.app-lifespan-state"],
        ["lifespan"],
        _EVENTS_LIFESPAN,
        (
            "The selector projection includes generic ASGI lifespan observations. FastAPI-owned "
            "scope is both callback markers around one lifespan context; it does not claim "
            "request interleaving or test the documentation's rationale about sharing variables."
        ),
        (
            "The lifespan parameter is a FastAPI constructor input "
            "(fastapi/applications.py:527-538); the selected callback trace represents its "
            "startup/cleanup integration."
        ),
    ),
    (_EVENTS_PAGE, "technical-details"): _excluded(
        "Technical Details { #technical-details }",
        149,
        162,
        (
            "ASGI lifespan protocol event ordering and state behavior are generic Starlette/ASGI "
            "contracts rather than FastAPI-specific behavior."
        ),
        (
            "The existing lifespan case records generic protocol observations for diagnosis, "
            "but only the FastAPI callback trace is selected for this page's FastAPI behavior."
        ),
    ),
    (_EVENTS_PAGE, "sub-applications"): _excluded(
        "Sub Applications { #sub-applications }",
        163,
        165,
        "The documented mount/sub-application lifespan behavior is owned by Starlette-RS.",
        (
            "The available mounted-subapp input observes generic mount and lifespan dispatch. "
            "FastAPI delegates to Starlette routing and does not own this contract."
        ),
    ),
}

__all__ = [
    "CASE_ACTION_SCOPES",
    "DOC_SECTION_CASE_MAPPINGS_EVENTS_20261015",
    "EXISTING_RECIPE",
    "FASTAPI_EVENTS_DOCUMENTATION_REVIEW",
    "FASTAPI_SOURCE",
    "STARLETTE_RS_TARGET",
    "SUPPRESSION_RECIPE",
]
