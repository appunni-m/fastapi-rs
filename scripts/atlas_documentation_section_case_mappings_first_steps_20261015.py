"""Reviewed section mappings for FastAPI 0.141.1's First Steps page."""

_RECIPE = "tests/fixtures/input-recipes/parity/first-steps-page-review-20261015.yaml"


def _workflow(heading, start, end, case_ids, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": _RECIPE,
        "case_ids": case_ids,
        "action_ids": actions,
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


DOC_SECTION_CASE_MAPPINGS_FIRST_STEPS_20261015 = {
    ("tutorial/first-steps.md", "first-steps"): _excluded(
        "First Steps { #first-steps }",
        1,
        427,
        (
            "This page-level heading combines independently reviewable route, OpenAPI, "
            "documentation-HTML, CLI, and deployment sections; it defines no single "
            "additional input or observable behavior."
        ),
        (
            "FastAPI owns route registration and OpenAPI generation, while Starlette 1.6.0 "
            "owns generic ASGI routing and HTTP transport. The CLI invokes optional "
            "fastapi-cli and user code, and deployment invokes FastAPI Cloud; concrete ASGI "
            "cases are mapped on their child sections."
        ),
    ),
    ("tutorial/first-steps.md", "interactive-api-docs"): _workflow(
        "Interactive API docs { #interactive-api-docs }",
        75,
        82,
        ["fastapi.docs.first-steps-page.documentation-routes"],
        ["swagger-ui"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "GET /docs maps the generated response status, ordered headers, and HTML body "
            "bytes from a default FastAPI app. The input does not run a browser or load "
            "Swagger UI's external JavaScript and CSS."
        ),
        (
            "FastAPI 0.141.1 registers the Swagger UI HTML endpoint and embeds the OpenAPI "
            "URL; Starlette 1.6.0 owns route dispatch and HTTP transport. Swagger UI browser "
            "rendering is third-party client behavior and is outside this ASGI input."
        ),
    ),
    ("tutorial/first-steps.md", "alternative-api-docs"): _workflow(
        "Alternative API docs { #alternative-api-docs }",
        83,
        90,
        ["fastapi.docs.first-steps-page.documentation-routes"],
        ["redoc-ui"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "GET /redoc maps the generated response status, ordered headers, and HTML body "
            "bytes from a default FastAPI app. The input does not run a browser or load "
            "ReDoc's external JavaScript and CSS."
        ),
        (
            "FastAPI 0.141.1 registers the ReDoc HTML endpoint and embeds the OpenAPI URL; "
            "Starlette 1.6.0 owns route dispatch and HTTP transport. ReDoc browser rendering "
            "is third-party client behavior and is outside this ASGI input."
        ),
    ),
    ("tutorial/first-steps.md", "openapi"): _excluded(
        "OpenAPI { #openapi }",
        91,
        151,
        (
            "This parent section groups standards terminology, the concrete /openapi.json "
            "endpoint, and downstream code-generation uses. The endpoint is mapped under "
            "its child section; the remaining material adds no separate FastAPI input."
        ),
        (
            "FastAPI generates an application's OpenAPI document, while OpenAPI and JSON "
            "Schema define external standards. The endpoint is sampled under Check the "
            "openapi.json; generated-client behavior belongs to downstream consumers."
        ),
    ),
    ("tutorial/first-steps.md", "api-schema"): _excluded(
        'API "schema" { #api-schema }',
        99,
        104,
        (
            "This subsection defines the word schema and lists information an API description "
            "can contain; it does not configure or exercise a FastAPI operation."
        ),
        (
            "The text is standards vocabulary. FastAPI's generated-document behavior is "
            "separately scoped to /openapi.json, while generic HTTP handling belongs to "
            "Starlette 1.6.0."
        ),
    ),
    ("tutorial/first-steps.md", "openapi-and-json-schema"): _excluded(
        "OpenAPI and JSON Schema { #openapi-and-json-schema }",
        111,
        114,
        (
            "This subsection explains how OpenAPI and JSON Schema relate as standards; it "
            "introduces no application input, schema option, or model."
        ),
        (
            "FastAPI composes an OpenAPI document and Pydantic supplies JSON Schema for "
            "declared models, but this conceptual paragraph selects neither behavior. The "
            "page-specific endpoint input is mapped in its child section."
        ),
    ),
    ("tutorial/first-steps.md", "check-the-openapi-json"): _workflow(
        "Check the `openapi.json` { #check-the-openapi-json }",
        115,
        143,
        ["fastapi.docs.first-steps-page.openapi-document"],
        ["openapi-json"],
        [
            "docs.response.body.bytes",
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "GET /openapi.json projects the documented response status, body bytes, generated "
            "document, and selected path pointers for the independently authored app. It does "
            "not claim the illustrative /items/ document or every OpenAPI field."
        ),
        (
            "FastAPI 0.141.1 constructs and serves the OpenAPI document from registered "
            "routes. Starlette 1.6.0 owns generic HTTP transport. This workload has no "
            "Pydantic model, so model JSON Schema generation is not claimed."
        ),
    ),
    ("tutorial/first-steps.md", "what-is-openapi-for"): _excluded(
        "What is OpenAPI for { #what-is-openapi-for }",
        144,
        151,
        (
            "This subsection lists downstream uses of an OpenAPI document, including other "
            "documentation systems and generated clients; it specifies no additional "
            "FastAPI request or schema option."
        ),
        (
            "FastAPI owns the document producer, but browser tools and generated-client "
            "behavior belong to downstream consumers. The producer response is sampled by "
            "the adjacent /openapi.json case."
        ),
    ),
    ("tutorial/first-steps.md", "configure-the-app-entrypoint-in-pyproject-toml"): _excluded(
        (
            "Configure the app `entrypoint` in `pyproject.toml` "
            "{ #configure-the-app-entrypoint-in-pyproject-toml }"
        ),
        152,
        188,
        (
            "The section configures app discovery for the fastapi console command and "
            "demonstrates importing a user module. That optional CLI process is not an ASGI "
            "request to an already constructed FastAPI application."
        ),
        (
            "Entrypoint parsing and user-module loading belong to optional fastapi-cli and "
            "the user's project layout. The mapped library inputs exercise an already "
            "constructed app, so this section does not attribute CLI, Uvicorn, or user-import "
            "behavior to FastAPI route handling."
        ),
    ),
    (
        "tutorial/first-steps.md",
        "fastapi-dev-with-path-or-with-entrypoint-cli-option",
    ): _excluded(
        (
            "`fastapi dev` with path or with `--entrypoint` CLI option "
            "{ #fastapi-dev-with-path-or-with-entrypoint-cli-option }"
        ),
        189,
        206,
        (
            "This section documents two fastapi dev invocation forms and recommends a "
            "project-level entrypoint; its operation is CLI app discovery and startup, not "
            "an ASGI action on a constructed app."
        ),
        (
            "The command delegates app discovery and development-server startup to optional "
            "fastapi-cli and Uvicorn, then imports user code. Those process, server, and "
            "project-layout behaviors are outside this FastAPI library workflow slice."
        ),
    ),
    ("tutorial/first-steps.md", "recap-step-by-step"): _excluded(
        "Recap, step by step { #recap-step-by-step }",
        229,
        419,
        (
            "This parent heading repeats route concepts and includes deployment guidance; "
            "concrete route and OpenAPI claims are scoped in child sections and it defines "
            "no additional input."
        ),
        (
            "Route child mappings cover FastAPI registration and response generation; "
            "Starlette 1.6.0 owns generic dispatch and transport. The final deploy step "
            "delegates to FastAPI Cloud and is outside the library contract."
        ),
    ),
    ("tutorial/first-steps.md", "step-3-create-a-path-operation"): _excluded(
        "Step 3: create a *path operation* { #step-3-create-a-path-operation }",
        253,
        361,
        (
            "This parent heading groups URL and HTTP-method terminology with the concrete "
            "GET decorator example. The example is mapped under Define a path operation "
            "decorator; the parent adds no distinct request."
        ),
        (
            "FastAPI owns registration of the documented GET operation. URL and method "
            "vocabulary is HTTP/Starlette contract, and the concrete action is scoped once "
            "under its child heading."
        ),
    ),
    ("tutorial/first-steps.md", "path"): _excluded(
        "Path { #path }",
        255,
        278,
        (
            "This child defines URL path terminology and gives an example URL; it does not "
            "declare or call a FastAPI route."
        ),
        (
            "URL syntax and generic route matching are HTTP and Starlette 1.6.0 behavior. "
            "The FastAPI route-registration sample is mapped under the decorator child."
        ),
    ),
    ("tutorial/first-steps.md", "operation"): _excluded(
        "Operation { #operation }",
        279,
        313,
        (
            "This child lists HTTP methods and conventional create/read/update/delete "
            "meanings, then explicitly says those meanings are guidelines rather than "
            "requirements; it specifies no FastAPI method semantics."
        ),
        (
            "HTTP method vocabulary and route matching belong to the HTTP and Starlette "
            "1.6.0 contracts. User code chooses an operation's business meaning; FastAPI "
            "does not enforce the conventional mapping described here."
        ),
    ),
    ("tutorial/first-steps.md", "define-a-path-operation-decorator"): _workflow(
        "Define a *path operation decorator* { #define-a-path-operation-decorator }",
        314,
        361,
        ["fastapi.docs.first-steps-page.async-route"],
        ["get-root"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "GET / invokes the async root operation in the independent workload. It samples "
            "one GET registration and does not claim the listed POST, PUT, DELETE, OPTIONS, "
            "HEAD, PATCH, or TRACE routes."
        ),
        (
            "FastAPI 0.141.1 registers the endpoint and invokes its user function. Starlette "
            "1.6.0 owns generic route matching and HTTP transport; the returned dictionary "
            "is user code and response wire behavior follows the shared Starlette contract."
        ),
    ),
    ("tutorial/first-steps.md", "step-4-define-the-path-operation-function"): _workflow(
        (
            "Step 4: define the **path operation function** "
            "{ #step-4-define-the-path-operation-function }"
        ),
        362,
        389,
        [
            "fastapi.docs.first-steps-page.async-route",
            "fastapi.docs.first-steps-page.sync-route",
        ],
        ["get-root"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected GET actions invoke an async root handler and an independently "
            "authored sync handler. They sample invocation and returned responses, not "
            "application business logic or every sync/async callable edge case."
        ),
        (
            "FastAPI 0.141.1 dispatches the endpoint according to whether user code is async "
            "or sync; Starlette 1.6.0 supplies generic thread-pool and HTTP/ASGI transport "
            "behavior. Both returned dictionaries are authored by the workload."
        ),
    ),
    ("tutorial/first-steps.md", "step-5-return-the-content"): _workflow(
        "Step 5: return the content { #step-5-return-the-content }",
        390,
        399,
        [
            "fastapi.docs.first-steps-page.async-route",
            "fastapi.docs.first-steps-page.sync-route",
        ],
        ["get-root"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected async and sync actions return independently authored dictionaries "
            "and observe status, ordered headers, and body bytes. This does not claim "
            "list/scalar conversion, Pydantic models, ORM integration, or custom serialization."
        ),
        (
            "FastAPI applies its response path to user-returned values, and Starlette 1.6.0 "
            "owns JSONResponse wire behavior. Pydantic owns model validation and JSON Schema "
            "when models are used, but this input uses plain dictionaries and no Pydantic model."
        ),
    ),
    ("tutorial/first-steps.md", "recap"): _excluded(
        "Recap { #recap }",
        420,
        427,
        (
            "This closing checklist summarizes already mapped route concepts and adds CLI "
            "development/deployment commands; it defines no new ASGI request or response."
        ),
        (
            "The route items are covered by the focused child mapping. fastapi dev delegates "
            "to optional fastapi-cli/Uvicorn, while fastapi deploy invokes FastAPI Cloud; "
            "neither is FastAPI library behavior in this workflow."
        ),
    ),
}
