"""Reviewed section mappings for OpenAPI callbacks and webhooks documentation.

All source paths in ``SOURCE_SPANS`` are relative to the pinned FastAPI 0.141.1
checkout at 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f. Workflow links reuse
existing independent recipe/workload inputs; this sidecar adds no expected
outputs and does not copy upstream tests.
"""

from __future__ import annotations

_CALLBACKS = "advanced/openapi-callbacks.md"
_WEBHOOKS = "advanced/openapi-webhooks.md"

_CALLBACK_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-callback-interface-review.yaml"
)
_WEBHOOK_TUTORIAL_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-webhook-interface-review.yaml"
)
_WEBHOOK_CONSTRUCTOR_RECIPE = "tests/fixtures/input-recipes/parity/webhooks-constructor.yaml"

_HTTP = ["http.status", "http.body.bytes"]
_OPENAPI = ["docs.response.status", "http.status", "openapi.document"]


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    workflow = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        workflow["action_ids"] = actions
    return workflow


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_CALLBACK_CASE = "fastapi.atlas-openapi-tutorial.callback-documentation"
_CALLBACK_REQUEST_CASE = "fastapi.atlas-openapi-tutorial.callback-route-request"
_WEBHOOK_CASE = "fastapi.atlas-openapi-tutorial.webhook-documentation"
_WEBHOOK_ROUTE_CASE = "fastapi.atlas-openapi-tutorial.webhook-adjacent-route"

_CALLBACK_SCHEMA_RATIONALE = (
    "The pinned example declares a callback APIRouter route and passes its routes to an "
    "owning operation (docs_src/openapi_callbacks/tutorial001_py310.py:23-34). FastAPI "
    "0.141.1 accepts callback routes on APIRoute "
    "(fastapi/routing.py:1187-1222), stores them on route state "
    "(fastapi/routing.py:961-1012), and "
    "projects each callback into the owning OpenAPI operation "
    "(fastapi/openapi/utils.py:386-402). The linked action observes the generated OpenAPI "
    "document for an independently authored callback input. Its path-expression values "
    "differ from the docs example, so the case maps callback projection behavior and does "
    "not claim equality with the example's literal URL expression."
)

_WEBHOOK_SCHEMA_RATIONALE = (
    "The pinned tutorial declares a POST webhook operation and an ordinary /users route "
    "(docs_src/openapi_webhooks/tutorial001_py310.py:15-24); its upstream tutorial test "
    "requests /openapi.json (tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py:23-26). "
    "FastAPI 0.141.1 stores webhooks in a separate APIRouter "
    "(fastapi/applications.py:937-948), passes its routes to get_openapi "
    "(fastapi/applications.py:1084-1101), and emits them under the OpenAPI webhooks member "
    "(fastapi/openapi/utils.py:648-675). The linked independent recipe samples one POST "
    "webhook schema; it does not execute webhook delivery, test other methods, or render a "
    "browser UI."
)


DOC_SECTION_CASE_MAPPINGS_OPENAPI_CALLBACKS_WEBHOOKS_20261015 = {
    (_CALLBACKS, "openapi-callbacks"): _excluded(
        "OpenAPI Callbacks { #openapi-callbacks }",
        1,
        186,
        "Page overview; the behavior-bearing example sections are mapped below.",
        (
            "The page-level story spans normal inbound request handling, OpenAPI callback "
            "metadata, application-owned outbound HTTP, and browser-rendered docs. The "
            "narrower sections below separate those contracts."
        ),
    ),
    (_CALLBACKS, "an-app-with-callbacks"): _excluded(
        "An app with callbacks { #an-app-with-callbacks }",
        9,
        25,
        "Narrative setup only; it specifies no distinct FastAPI input or OpenAPI projection.",
        (
            "Lines 11-24 describe a hypothetical invoice workflow and the application's "
            "notification delivery. The concrete FastAPI request is mapped under "
            "`the-normal-fastapi-app`; outbound notification code belongs to the user's "
            "application."
        ),
    ),
    (_CALLBACKS, "the-normal-fastapi-app"): _workflow(
        "The normal **FastAPI** app { #the-normal-fastapi-app }",
        26,
        43,
        _CALLBACK_RECIPE,
        [_CALLBACK_REQUEST_CASE],
        ["submit-independent-transfer"],
        _HTTP,
        (
            "The recipe sends an independent JSON body and callback URL query value to one "
            "inbound POST operation, then observes its HTTP response. Its /transfers and "
            "notification_url inputs intentionally differ from the docs example's /invoices "
            "and callback_url; no callback request is sent."
        ),
        (
            "The docs include the invoice body and callback_url parameter "
            "(docs_src/openapi_callbacks/tutorial001_py310.py:7-11, 33-34). The linked "
            "input is an independent analogue of the inbound request, grounded by the "
            "tutorial's request test "
            "(tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py:29-35). "
            "The selected action observes only this inbound operation response; it does not "
            "observe an external callback."
        ),
    ),
    (_CALLBACKS, "documenting-the-callback"): _workflow(
        "Documenting the callback { #documenting-the-callback }",
        44,
        72,
        _CALLBACK_RECIPE,
        [_CALLBACK_CASE],
        ["callback-openapi-document"],
        _OPENAPI,
        (
            "The selected /openapi.json action observes the callback-bearing schema only. "
            "The HTTPX example at lines 52-55 is application-owned outbound delivery and "
            "is excluded; the recipe also does not render Swagger UI."
        ),
        _CALLBACK_SCHEMA_RATIONALE,
    ),
    (_CALLBACKS, "write-the-callback-documentation-code"): _workflow(
        "Write the callback documentation code { #write-the-callback-documentation-code }",
        73,
        186,
        _CALLBACK_RECIPE,
        [_CALLBACK_CASE],
        ["callback-openapi-document"],
        _OPENAPI,
        (
            "This introductory section says the callback declaration describes an external "
            "API and is not executed by the app. The action observes generated callback "
            "metadata; the APIRouter, callback operation, expression, and attachment details "
            "are mapped in the child sections."
        ),
        _CALLBACK_SCHEMA_RATIONALE,
    ),
    (_CALLBACKS, "create-a-callback-apirouter"): _workflow(
        "Create a callback `APIRouter` { #create-a-callback-apirouter }",
        89,
        94,
        _CALLBACK_RECIPE,
        [_CALLBACK_CASE],
        ["callback-openapi-document"],
        _OPENAPI,
        (
            "The action observes the resulting callback entry in OpenAPI for an independently "
            "authored APIRouter-based input. It does not inspect Python object identity or "
            "assert an outbound callback."
        ),
        _CALLBACK_SCHEMA_RATIONALE,
    ),
    (_CALLBACKS, "create-the-callback-path-operation"): _workflow(
        "Create the callback *path operation* { #create-the-callback-path-operation }",
        95,
        110,
        _CALLBACK_RECIPE,
        [_CALLBACK_CASE],
        ["callback-openapi-document"],
        _OPENAPI,
        (
            "The whole-document OpenAPI observation includes the callback operation, its "
            "request-body model, and response metadata. The callback endpoint is a schema "
            "declaration; the selected action sends no request to the callback path."
        ),
        _CALLBACK_SCHEMA_RATIONALE,
    ),
    (_CALLBACKS, "the-callback-path-expression"): _workflow(
        "The callback path expression { #the-callback-path-expression }",
        111,
        165,
        _CALLBACK_RECIPE,
        [_CALLBACK_CASE],
        ["callback-openapi-document"],
        _OPENAPI,
        (
            "The independent recipe uses a query-derived URL and a request-body expression "
            "(`{$notification_url}/transfers/{$request.body.reference}`), then selects the "
            "whole generated document. Its values differ from the docs expression "
            "`{$callback_url}/invoices/{$request.body.id}`; this is not an exact-value "
            "observation of the latter. The JSON body and response examples in the page are "
            "illustrations, not callback deliveries."
        ),
        _CALLBACK_SCHEMA_RATIONALE,
    ),
    (_CALLBACKS, "add-the-callback-router"): _workflow(
        "Add the callback router { #add-the-callback-router }",
        166,
        179,
        _CALLBACK_RECIPE,
        [_CALLBACK_CASE],
        ["callback-openapi-document"],
        _OPENAPI,
        (
            "The workload passes callback_routes.routes to the owning operation and the "
            "selected action observes the resulting callback projection. It sends no request "
            "to the callback path, so this mapping makes no dispatch claim."
        ),
        _CALLBACK_SCHEMA_RATIONALE,
    ),
    (_CALLBACKS, "check-the-docs"): _excluded(
        "Check the docs { #check-the-docs }",
        180,
        186,
        "The cited Swagger UI panel and screenshot are browser-rendered presentation behavior.",
        (
            "The recipe observes /openapi.json, not /docs HTML or browser rendering. FastAPI "
            "serves Swagger HTML from fastapi/applications.py:1121-1158, while the page's "
            "visible callback panel is rendered by the Swagger UI client. No linked input "
            "claims that screenshot or UI behavior."
        ),
    ),
    (_WEBHOOKS, "openapi-webhooks"): _excluded(
        "OpenAPI Webhooks { #openapi-webhooks }",
        1,
        55,
        (
            "Page overview; webhook delivery, the OpenAPI declaration, and docs UI are "
            "separated below."
        ),
        (
            "The page-level overview combines application-owned event delivery with FastAPI's "
            "OpenAPI webhook projection and browser docs. The child sections below keep those "
            "owners separate."
        ),
    ),
    (_WEBHOOKS, "webhooks-steps"): _excluded(
        "Webhooks steps { #webhooks-steps }",
        9,
        18,
        (
            "Scheduling events, registering destination URLs, and sending requests are "
            "application-owned."
        ),
        (
            "The section assigns message selection, delivery timing, destination registration, "
            "and the send operation to the user's own code. FastAPI's `app.webhooks` contract "
            "is documented and mapped separately."
        ),
    ),
    (_WEBHOOKS, "documenting-webhooks-with-fastapi-and-openapi"): _workflow(
        (
            "Documenting webhooks with **FastAPI** and OpenAPI "
            "{ #documenting-webhooks-with-fastapi-and-openapi }"
        ),
        19,
        30,
        _WEBHOOK_TUTORIAL_RECIPE,
        [_WEBHOOK_CASE],
        ["webhook-openapi-document"],
        _OPENAPI,
        (
            "The selected action observes one generated OpenAPI document containing one POST "
            "webhook and its request-body schema. It does not sample all methods, delivery, "
            "client generation, or the version-history statement at lines 25-29."
        ),
        _WEBHOOK_SCHEMA_RATIONALE,
    ),
    (_WEBHOOKS, "an-app-with-webhooks"): _workflow(
        "An app with webhooks { #an-app-with-webhooks }",
        31,
        55,
        _WEBHOOK_TUTORIAL_RECIPE,
        [_WEBHOOK_CASE, _WEBHOOK_ROUTE_CASE],
        None,
        ["docs.response.status", "http.body.bytes", "http.status", "openapi.document"],
        (
            "The schema action corresponds to the documented `new-subscription` operation; "
            "the second action samples an independent ordinary `/accounts/` route, rather "
            "than the tutorial's `/users/` path. Neither action attempts webhook delivery "
            "or displays the docs UI. The event-name-versus-inbound-path distinction has "
            "the separate supplemental input in "
            "RELATED_WORKFLOW_INPUTS below."
        ),
        _WEBHOOK_SCHEMA_RATIONALE,
    ),
    (_WEBHOOKS, "check-the-docs"): _excluded(
        "Check the docs { #check-the-docs }",
        49,
        55,
        "The cited docs UI screenshot is browser-rendered presentation behavior.",
        (
            "The linked tutorial workflow observes /openapi.json and its independent "
            "/accounts/ route, not the tutorial's /users/ path, Swagger UI HTML, or a "
            "rendered browser. FastAPI builds the Swagger HTML route in "
            "fastapi/applications.py:1121-1158; the image depicts client-side docs UI."
        ),
    ),
}


# The page's event identifier is not an inbound URL path. This focused existing
# input supplements the exact tutorial example without broadening its primary
# documentation-section selectors or encoding an expected HTTP status.
RELATED_WORKFLOW_INPUTS = {
    (_WEBHOOKS, "an-app-with-webhooks"): [
        {
            "recipe_path": _WEBHOOK_CONSTRUCTOR_RECIPE,
            "case_id": "fastapi.webhooks.constructor-router.openapi-and-route-separation",
            "action_ids": [
                "inspect-constructor-supplied-webhook-openapi",
                "request-webhook-identifier-as-inbound-path",
            ],
            "observation_selectors": [
                "docs.response.status",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
            "scope_note": (
                "The OpenAPI action records the `/openapi.json` response status, document, "
                "and paths including `/webhooks/stock-updated`; the request action records "
                "the `/stock-updated` response status. The recipe supplies inputs and "
                "selectors only and makes no fixed-status claim."
            ),
            "rationale": (
                "The page calls the webhook text an event identifier and says users choose "
                "the destination path elsewhere (docs/en/docs/advanced/openapi-webhooks.md:45-47). "
                "The existing constructor workflow independently probes the OpenAPI location "
                "and a request to that identifier; FastAPI keeps app.webhooks separate from "
                "the routes traversed for ordinary paths "
                "(fastapi/applications.py:937-948, 1084-1101; "
                "fastapi/openapi/utils.py:648-675)."
            ),
        }
    ]
}


def _span(path, start, end, role):
    return {"path": path, "start_line": start, "end_line": end, "role": role}


# Exact pinned-source spans reviewed for each anchored page section. These are
# kept beside the mappings because this additive sidecar is intentionally not
# wired into the shared atlas registry in this change.
SOURCE_SPANS = {
    (_CALLBACKS, "openapi-callbacks"): [
        _span("docs/en/docs/advanced/openapi-callbacks.md", 1, 186, "page overview"),
    ],
    (_CALLBACKS, "an-app-with-callbacks"): [
        _span("docs/en/docs/advanced/openapi-callbacks.md", 9, 25, "hypothetical invoice scenario"),
    ],
    (_CALLBACKS, "the-normal-fastapi-app"): [
        _span("docs/en/docs/advanced/openapi-callbacks.md", 26, 43, "inbound operation section"),
        _span("docs_src/openapi_callbacks/tutorial001_py310.py", 7, 11, "invoice request model"),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py", 33, 51, "inbound invoice operation"
        ),
        _span(
            "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py",
            29,
            35,
            "tutorial inbound request assertions",
        ),
    ],
    (_CALLBACKS, "documenting-the-callback"): [
        _span(
            "docs/en/docs/advanced/openapi-callbacks.md",
            44,
            72,
            "application delivery boundary and docs explanation",
        ),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py",
            23,
            30,
            "callback router operation declaration",
        ),
        _span("fastapi/openapi/utils.py", 386, 402, "callback OpenAPI projection"),
    ],
    (_CALLBACKS, "write-the-callback-documentation-code"): [
        _span(
            "docs/en/docs/advanced/openapi-callbacks.md",
            73,
            186,
            "callback documentation overview and nested sections",
        ),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py",
            23,
            34,
            "callback declaration and owning route",
        ),
    ],
    (_CALLBACKS, "create-a-callback-apirouter"): [
        _span("docs/en/docs/advanced/openapi-callbacks.md", 89, 94, "callback APIRouter section"),
        _span("docs_src/openapi_callbacks/tutorial001_py310.py", 1, 1, "APIRouter import"),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py", 23, 23, "callback APIRouter instance"
        ),
    ],
    (_CALLBACKS, "create-the-callback-path-operation"): [
        _span("docs/en/docs/advanced/openapi-callbacks.md", 95, 110, "callback operation section"),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py",
            14,
            20,
            "callback request and response models",
        ),
        _span("docs_src/openapi_callbacks/tutorial001_py310.py", 26, 30, "callback path operation"),
        _span(
            "tests/test_tutorial/test_openapi_callbacks/test_tutorial001.py",
            42,
            45,
            "OpenAPI request/status assertion",
        ),
    ],
    (_CALLBACKS, "the-callback-path-expression"): [
        _span(
            "docs/en/docs/advanced/openapi-callbacks.md",
            111,
            165,
            "callback expression and illustrative payloads",
        ),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py",
            26,
            30,
            "query/body callback expression source",
        ),
        _span("fastapi/openapi/utils.py", 386, 402, "callback path stored in generated operation"),
    ],
    (_CALLBACKS, "add-the-callback-router"): [
        _span(
            "docs/en/docs/advanced/openapi-callbacks.md",
            166,
            179,
            "callback routes attached to the owning operation",
        ),
        _span(
            "docs_src/openapi_callbacks/tutorial001_py310.py",
            33,
            34,
            "callback routes passed to decorator",
        ),
        _span("fastapi/routing.py", 1187, 1222, "APIRoute callback parameter"),
        _span("fastapi/routing.py", 961, 1012, "callback declaration stored on route state"),
        _span("fastapi/openapi/utils.py", 386, 402, "callback route OpenAPI projection"),
    ],
    (_CALLBACKS, "check-the-docs"): [
        _span(
            "docs/en/docs/advanced/openapi-callbacks.md", 180, 186, "Swagger UI screenshot section"
        ),
        _span("fastapi/applications.py", 1121, 1158, "FastAPI Swagger HTML route"),
    ],
    (_WEBHOOKS, "openapi-webhooks"): [
        _span("docs/en/docs/advanced/openapi-webhooks.md", 1, 55, "page overview"),
    ],
    (_WEBHOOKS, "webhooks-steps"): [
        _span(
            "docs/en/docs/advanced/openapi-webhooks.md", 9, 18, "application-owned webhook steps"
        ),
    ],
    (_WEBHOOKS, "documenting-webhooks-with-fastapi-and-openapi"): [
        _span(
            "docs/en/docs/advanced/openapi-webhooks.md",
            19,
            30,
            "OpenAPI webhook declaration overview",
        ),
        _span(
            "docs_src/openapi_webhooks/tutorial001_py310.py",
            15,
            20,
            "tutorial POST webhook operation",
        ),
        _span(
            "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
            23,
            26,
            "tutorial OpenAPI request/status assertions",
        ),
        _span("fastapi/openapi/utils.py", 648, 675, "webhook collection and OpenAPI projection"),
    ],
    (_WEBHOOKS, "an-app-with-webhooks"): [
        _span(
            "docs/en/docs/advanced/openapi-webhooks.md",
            31,
            55,
            "app.webhooks example, identifier explanation, and nested docs section",
        ),
        _span(
            "docs_src/openapi_webhooks/tutorial001_py310.py", 15, 24, "webhook plus ordinary route"
        ),
        _span(
            "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
            10,
            13,
            "ordinary route request assertions",
        ),
        _span(
            "tests/test_tutorial/test_openapi_webhooks/test_tutorial001.py",
            23,
            26,
            "OpenAPI request/status assertions",
        ),
        _span("fastapi/applications.py", 937, 948, "documentation-only app.webhooks router"),
        _span(
            "fastapi/applications.py", 1084, 1101, "webhook routes supplied to schema generation"
        ),
        _span(
            "fastapi/openapi/utils.py", 648, 675, "webhook routes emitted under OpenAPI webhooks"
        ),
    ],
    (_WEBHOOKS, "check-the-docs"): [
        _span("docs/en/docs/advanced/openapi-webhooks.md", 49, 55, "Swagger UI screenshot section"),
        _span("fastapi/applications.py", 1121, 1158, "FastAPI Swagger HTML route"),
    ],
}
