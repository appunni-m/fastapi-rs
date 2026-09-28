"""Source-reviewed mappings for selected FastAPI advanced/how-to pages.

This bounded wave reuses existing recipes only. Workflow selectors describe
observations encoded by those inputs, not parity results. The upstream source
review is FastAPI 0.141.1 with Starlette 1.6.0 as the sole generic-framework
authority; Starlette behavior remains assigned to the separate Starlette-RS
contract.
"""


def _source(path, start, end, role):
    return {
        "path": path,
        "start_line": start,
        "end_line": end,
        "role": role,
    }


def _workflow(recipe_path, case_ids, selectors, coverage):
    return {
        "recipe_path": recipe_path,
        "case_ids": list(case_ids),
        "observation_selectors": list(selectors),
        "coverage": coverage,
    }


def _review(feature_ids, selectors, rationale, workflows, gate, sources, starlette=()):
    contract_areas = set()
    for span in starlette:
        path = span["path"]
        if path.endswith("/routing.py") or path.endswith("/applications.py"):
            contract_areas.add("routing-converters-mounts-hosts-and-errors")
        if path.endswith("/requests.py") or path.endswith("/responses.py"):
            contract_areas.add("applications-requests-responses-background-concurrency")
        if path.endswith("/responses.py") or path.endswith("/requests.py"):
            contract_areas.add("streaming-headers-cookies-errors-and-cleanup")
        if path.endswith("/middleware/exceptions.py"):
            contract_areas.add("middleware-authentication-endpoints-datastructures-status")
    stimulus_notes = "; ".join(
        f"{workflow['recipe_path']} case(s) {', '.join(workflow['case_ids'])}; "
        f"selectors: {', '.join(workflow['observation_selectors'])}"
        for workflow in workflows
    )
    return {
        "replace_features": True,
        "feature_ids": list(feature_ids),
        "observation_selectors": list(selectors),
        "rationale": rationale,
        "stimulus_notes": (
            "Source-reviewed existing input mappings only; these are stimuli, not parity results. "
            + stimulus_notes
        ),
        "workflow_cases": list(workflows),
        "contract_gate": gate,
        "supporting_sources": list(sources),
        "starlette_contract_sources": list(starlette),
        "starlette_contract_areas": sorted(contract_areas),
    }


_STARLETTE_RESPONSE = (
    _source(
        "starlette/responses.py",
        29,
        65,
        "Starlette 1.6.0 Response status, body rendering, and header initialization; generic response behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/responses.py",
        163,
        168,
        "Starlette 1.6.0 ASGI response start/body emission; generic response dispatch belongs to Starlette-RS.",
    ),
)
_STARLETTE_REQUEST = (
    _source(
        "starlette/requests.py",
        214,
        266,
        "Starlette 1.6.0 Request construction, stream/body accumulation, and JSON parsing; generic request behavior belongs to Starlette-RS.",
    ),
    _source(
        "starlette/requests.py",
        152,
        166,
        "Starlette 1.6.0 Request.client reads the ASGI client tuple; request properties belong to Starlette-RS.",
    ),
)
_STARLETTE_MOUNT = (
    _source(
        "starlette/applications.py",
        98,
        100,
        "Starlette 1.6.0 Application.mount delegates to Router.mount; generic mount registration belongs to Starlette-RS.",
    ),
    _source(
        "starlette/routing.py",
        363,
        424,
        "Starlette 1.6.0 Mount matches prefixes and creates the child ASGI scope; generic mounted dispatch belongs to Starlette-RS.",
    ),
)
_STARLETTE_EXCEPTION = (
    _source(
        "starlette/middleware/exceptions.py",
        47,
        65,
        "Starlette 1.6.0 ExceptionMiddleware handles generic HTTP exceptions; dispatch behavior belongs to the separate Starlette-RS contract.",
    ),
)


DOC_PAGE_REVIEW_MAPPINGS = {
    "advanced/additional-responses.md": _review(
        ["openapi-docs", "response-serialization"],
        [
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "FastAPI owns the path-operation `responses` declaration, additional response-model schema generation, and merge into OpenAPI. Starlette owns direct Response/JSONResponse rendering and ASGI emission, tracked by Starlette-RS. The input demonstrates one documented custom media type plus a not-found model; it does not imply every response merge form is covered.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/additional-responses.yaml",
                [
                    "fastapi.docs.additional-responses.found",
                    "fastapi.docs.additional-responses.not-found",
                    "fastapi.docs.additional-responses.openapi",
                ],
                [
                    "docs.response.headers",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "Successful and not-found HTTP responses plus selected OpenAPI response/schema pointers.",
            )
        ],
        "Partial: selected response statuses and schema pointers do not cover every media type, response-class combination, default response, merge precedence, or arbitrary OpenAPI response object shown by the page. The cases do not establish schema generation parity by themselves.",
        [
            _source(
                "docs/en/docs/advanced/additional-responses.md",
                17,
                60,
                "FastAPI response-model declarations and generated additional-response schemas in OpenAPI.",
            ),
            _source(
                "docs/en/docs/advanced/additional-responses.md",
                172,
                206,
                "Additional media types and combining response-model and response metadata.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                473,
                537,
                "FastAPI generates the primary response content and processes declared additional responses/models.",
            ),
            _source(
                "fastapi/routing.py",
                1161,
                1193,
                "FastAPI APIRoute stores response declarations and models for dispatch/OpenAPI.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/additional-status-codes.md": _review(
        ["response-serialization"],
        ["http.body.bytes", "http.status"],
        "FastAPI supplies the injected Response object and applies a status changed by the endpoint to the final response. Returning a concrete Starlette response and its wire bytes use Starlette response semantics, tracked by Starlette-RS.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/additional-status-codes-tutorial-upstream.yaml",
                [
                    "fastapi.additional-status-codes.tutorial-update-existing",
                    "fastapi.additional-status-codes.tutorial-create-new",
                ],
                ["http.body.bytes", "http.status"],
                "One updated-record and one created-record response observe status and raw body bytes.",
            )
        ],
        "Partial: the two branches do not exercise all status values, response classes, headers, or cases where a returned Response overrides the injected status. They do not measure OpenAPI because the page explicitly describes returned Response statuses as absent from the generated schema.",
        [
            _source(
                "docs/en/docs/advanced/additional-status-codes.md",
                7,
                39,
                "Endpoint-controlled additional status codes and the page's OpenAPI limitation.",
            ),
            _source(
                "fastapi/routing.py",
                357,
                372,
                "FastAPI resolves route and injected Response status precedence.",
            ),
            _source(
                "fastapi/routing.py",
                375,
                455,
                "FastAPI builds the request handler and receives/uses the injected request Response.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/advanced-dependencies.md": _review(
        ["dependency-security"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        "Parameterized callable dependency inspection, graph construction, invocation, and value injection are FastAPI behavior. Request parsing and ASGI response emission remain Starlette-RS contract behavior. The linked recipe samples the page's callable-instance example only.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/advanced_dependencies.yaml",
                [
                    "fastapi.docs.advanced-dependencies.matching-query",
                    "fastapi.docs.advanced-dependencies.nonmatching-query",
                ],
                ["http.body.bytes", "http.headers.ordered", "http.status"],
                "Parameterized callable dependency accepts/rejects matching query values and observes HTTP output.",
            )
        ],
        "Partial: these cases do not cover yield-dependency scope/timing, exception suppression or re-raise, streaming resource lifetime, cleanup errors, or background-task ordering from the rest of the page. Dependency call/cleanup selectors are planned, not observed here.",
        [
            _source(
                "docs/en/docs/advanced/advanced-dependencies.md",
                3,
                64,
                "Parameterized dependency and callable-instance example.",
            ),
            _source(
                "docs/en/docs/advanced/advanced-dependencies.md",
                67,
                147,
                "Yield dependency scope, exception, streaming, and background-task discussion.",
            ),
            _source(
                "fastapi/dependencies/utils.py",
                198,
                349,
                "FastAPI inspects callable signatures and constructs dependency nodes.",
            ),
            _source(
                "fastapi/dependencies/utils.py",
                566,
                710,
                "FastAPI resolves dependency callables and enters generator dependency managers.",
            ),
        ],
        _STARLETTE_REQUEST + _STARLETTE_RESPONSE,
    ),
    "advanced/dataclasses.md": _review(
        ["response-serialization", "openapi-docs"],
        [
            "docs.response.body.bytes",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "FastAPI integrates dataclass annotations with response-model validation/serialization and its generated OpenAPI schema; Pydantic supplies schema/model conversion primitives. Generic response transport stays with Starlette-RS.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/dataclasses.yaml",
                ["fastapi.docs.dataclasses.response-model-and-openapi"],
                [
                    "docs.response.body.bytes",
                    "docs.response.headers",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
                "One dataclass response-model route and the selected Item OpenAPI schema.",
            )
        ],
        "Partial: one response model does not cover dataclass request bodies, nested dataclass combinations, standard-library/Pydantic dataclass variations, invalid inputs, or all field metadata. The recipe observes response bytes and one schema pointer only.",
        [
            _source(
                "docs/en/docs/advanced/dataclasses.md",
                1,
                52,
                "Dataclass request/response declarations and nested-data examples.",
            ),
            _source(
                "fastapi/utils.py",
                58,
                77,
                "FastAPI creates the Pydantic-backed model field for an annotated type.",
            ),
            _source(
                "fastapi/routing.py",
                301,
                342,
                "FastAPI validates and serializes response-model output.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                551,
                580,
                "FastAPI collects route model fields for OpenAPI schemas.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/generate-clients.md": _review(
        ["openapi-docs"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "FastAPI owns the OpenAPI operation identifiers, request/response schemas, and tags used as inputs by client generators. SDK generation, emitted source code, client runtime behavior, and generator command output belong to external tools and are not FastAPI behavior.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/generate-clients-tutorial001-upstream.yaml",
                [
                    "fastapi.test.test-tutorial-test-generate-clients-test-tutorial001.client-requests-and-openapi"
                ],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "Two API requests and selected OpenAPI paths/model pointers; no SDK process is run.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
                ["fastapi.docs.documentation-wave.openapi-schema.generate-clients"],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "A separate OpenAPI case observes operationId and request/response schema nodes.",
            ),
        ],
        "Partial: the selected cases evidence only FastAPI's HTTP/OpenAPI inputs to an SDK generator. They do not verify a generator's compatibility, generated client names or code, tagged-client grouping, custom preprocessors, or SDK request behavior.",
        [
            _source(
                "docs/en/docs/advanced/generate-clients.md",
                19,
                41,
                "FastAPI OpenAPI schema as the source used by SDK tooling.",
            ),
            _source(
                "docs/en/docs/advanced/generate-clients.md",
                108,
                132,
                "FastAPI's operationId/unique-ID behavior that informs client method names.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                266,
                306,
                "FastAPI operationId metadata generation and assignment.",
            ),
            _source("fastapi/utils.py", 95, 110, "FastAPI unique route identifier generation."),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/openapi-callbacks.md": _review(
        ["openapi-docs"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "FastAPI stores callback APIRoutes on the owning operation and constructs their callback schema entries in OpenAPI. The callback example is documentation metadata; actual outbound HTTP callbacks are application code and are not performed by FastAPI.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.advanced-openapi-callbacks.callback-operation"],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "One inbound operation request plus selected callback and requestBody OpenAPI pointers.",
            )
        ],
        "Partial: one callback operation and a small OpenAPI projection do not cover callback path expressions, multiple callbacks, callback security, generated docs rendering, or any outbound HTTP request. The recipe's inbound request is not evidence that a callback is executed.",
        [
            _source(
                "docs/en/docs/advanced/openapi-callbacks.md",
                73,
                110,
                "Callback APIRouter and documentation-only callback path operation.",
            ),
            _source(
                "docs/en/docs/advanced/openapi-callbacks.md",
                166,
                177,
                "The callback routes are attached to the owning operation for OpenAPI generation.",
            ),
            _source(
                "fastapi/routing.py",
                1161,
                1219,
                "FastAPI APIRoute accepts and stores callback route declarations.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                311,
                400,
                "FastAPI builds operation metadata, request body, and callback OpenAPI entries.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/openapi-webhooks.md": _review(
        ["openapi-docs"],
        ["docs.response.status", "http.status", "openapi.document", "openapi.security"],
        "FastAPI's `webhooks` APIRouter is collected separately and emitted in the OpenAPI 3.1 document. The documented webhook declarations describe a remote caller-facing contract; they do not add inbound FastAPI dispatch routes or send webhook requests.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/webhooks-security.yaml",
                ["fastapi.webhooks.security.openapi-contract"],
                ["docs.response.status", "http.status", "openapi.document", "openapi.security"],
                "The OpenAPI endpoint is observed at webhook requestBody/security and HTTPBearer scheme pointers.",
            )
        ],
        "Partial: this is an OpenAPI-only case for one webhook operation/security scheme. It does not cover webhook delivery, all HTTP methods, multiple webhooks, response schemas, or docs-browser behavior.",
        [
            _source(
                "docs/en/docs/advanced/openapi-webhooks.md",
                19,
                37,
                "FastAPI webhook declaration and generated OpenAPI/docs behavior.",
            ),
            _source(
                "fastapi/applications.py",
                937,
                948,
                "FastAPI stores the documentation-only webhooks APIRouter.",
            ),
            _source(
                "fastapi/applications.py",
                1084,
                1103,
                "FastAPI passes webhook routes into OpenAPI generation.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                585,
                660,
                "FastAPI traverses webhook routes and emits the OpenAPI webhooks object.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/path-operation-advanced-configuration.md": _review(
        ["openapi-docs", "response-serialization", "request-validation"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "FastAPI owns path-operation metadata, visibility, operation ID generation, custom OpenAPI fragments, and route request/response integration. The recipes sample named operations and schema nodes; the OpenAPI standard's interpretation and client tooling remain external contracts.",
        [
            _workflow(
                f"tests/fixtures/input-recipes/parity/path-operation-advanced-configurations-tutorial00{i}-upstream.yaml",
                [f"fastapi.path-operation-advanced-configurations.tutorial00{i}"],
                ["http.body.bytes", "http.status", "openapi.document"]
                + (["openapi.paths"] if i != 3 else []),
                "Page-linked route response and/or focused OpenAPI pointers for tutorial section "
                + str(i)
                + ".",
            )
            for i in range(1, 8)
        ]
        + [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-schema.yaml",
                [
                    "fastapi.docs.documentation-wave.openapi-schema.path-operation-configuration",
                    "fastapi.docs.documentation-wave.openapi-schema.advanced-operation-configuration",
                ],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "Independent summary/tag/response-description and operationId/openapi_extra projections.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/additional-response-openapi-wave.yaml",
                ["fastapi.additional-response-openapi-wave.media-content.test-openapi-schema"],
                ["openapi.document", "openapi.paths"],
                "Additional response media-content schema projection linked by this page.",
            ),
        ],
        "Partial: the selected cases cover operation IDs, `include_in_schema`, docstring truncation, `openapi_extra`, request schema, and selected additional-response metadata. They do not cover all route decorator parameters, all merge shapes, duplicate operation-ID warnings, or every custom content-type example.",
        [
            _source(
                "docs/en/docs/advanced/path-operation-advanced-configuration.md",
                3,
                58,
                "Operation IDs, OpenAPI exclusion, docstring description, and additional-response references.",
            ),
            _source(
                "docs/en/docs/advanced/path-operation-advanced-configuration.md",
                59,
                95,
                "OpenAPI extra fields and path-operation extension behavior.",
            ),
            _source(
                "docs/en/docs/advanced/path-operation-advanced-configuration.md",
                126,
                158,
                "Deep merge, custom request schema, and custom OpenAPI content type.",
            ),
            _source(
                "fastapi/routing.py",
                1161,
                1192,
                "FastAPI APIRoute configuration surface, including operation_id, include_in_schema, responses, and openapi_extra.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                287,
                306,
                "FastAPI operationId and summary/description metadata.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                311,
                400,
                "FastAPI includes route operations and selected schema/request metadata in OpenAPI.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                473,
                540,
                "FastAPI merges additional responses and openapi_extra into operation documents.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "advanced/strict-content-type.md": _review(
        ["request-validation", "public-api-errors"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        "FastAPI owns whether an untyped request body is interpreted as JSON and exposes the `strict_content_type` application/router/route option. Starlette owns raw request-body accumulation, with that generic behavior assigned to Starlette-RS.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/strict_content_type.yaml",
                ["fastapi.docs.strict-content-type.missing-header"],
                ["http.body.bytes", "http.headers.ordered", "http.status"],
                "One no-Content-Type JSON body is dispatched through the default strict behavior.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/request-coercion.yaml",
                [
                    "fastapi.request-coercion.strict-content-type.test-default-strict-rejects-no-content-type"
                ],
                ["http.body.bytes", "http.status"],
                "A second input confirms the default no-header branch on a separately authored route.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/strict-content-type-router-level-upstream.yaml",
                ["fastapi.request.strict-content-type.router-level-upstream"],
                ["http.body.bytes", "http.status"],
                "Router-level explicit configuration is exercised independently.",
            ),
        ],
        "Partial: these cases do not cover every valid/invalid media type, `+json` subtypes, malformed JSON, route-level override precedence, or the complete CSRF scenario. Documentation security rationale is not browser/CORS evidence.",
        [
            _source(
                "docs/en/docs/advanced/strict-content-type.md",
                1,
                4,
                "FastAPI default strict JSON Content-Type rule.",
            ),
            _source(
                "docs/en/docs/advanced/strict-content-type.md",
                76,
                88,
                "FastAPI opt-out configuration and version boundary.",
            ),
            _source(
                "fastapi/routing.py",
                375,
                450,
                "FastAPI request handler gates JSON parsing on strict_content_type and the Content-Type media type.",
            ),
            _source(
                "fastapi/routing.py",
                1126,
                1192,
                "FastAPI APIRoute stores the strict-content setting.",
            ),
        ],
        _STARLETTE_REQUEST + _STARLETTE_RESPONSE,
    ),
    "advanced/sub-applications.md": _review(
        ["app-routing", "openapi-docs"],
        [
            "docs.response.body.bytes",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "FastAPI provides independent sub-application instances and adjusts its generated docs/OpenAPI URLs for the mounted root path. Prefix matching, child ASGI scopes, and generic mount dispatch are Starlette-owned and remain in the Starlette-RS mount/routing contract.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/sub_applications.yaml",
                ["fastapi.docs.sub-applications.mount-and-own-openapi"],
                [
                    "docs.response.body.bytes",
                    "docs.response.headers",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
                "One mounted sub-app request and selected OpenAPI document/path projection.",
            )
        ],
        "Partial: this case does not cover multiple nested mounts, each app's `/docs` and `/redoc` HTML, root_path override combinations, URL reversal, host mounts, or mount error behavior.",
        [
            _source(
                "docs/en/docs/advanced/sub-applications.md",
                1,
                29,
                "Independent FastAPI applications and mount registration example.",
            ),
            _source(
                "docs/en/docs/advanced/sub-applications.md",
                45,
                65,
                "Separate docs/OpenAPI paths and root_path description.",
            ),
            _source(
                "fastapi/applications.py",
                1105,
                1163,
                "FastAPI constructs OpenAPI/docs URLs using the ASGI root_path.",
            ),
            _source(
                "fastapi/applications.py",
                42,
                45,
                "FastAPI application subclasses Starlette and inherits its generic mount surface.",
            ),
        ],
        _STARLETTE_MOUNT + _STARLETTE_RESPONSE,
    ),
    "advanced/using-request-directly.md": _review(
        ["app-routing", "request-validation", "openapi-docs"],
        [
            "docs.response.body.bytes",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "FastAPI recognizes a `Request`-typed endpoint parameter and injects it, while ordinary declared parameters still use FastAPI extraction/validation/OpenAPI behavior. Request.client and other Request properties are Starlette behavior, tracked by Starlette-RS.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/using_request_directly.yaml",
                ["fastapi.docs.using-request-directly.client-host"],
                [
                    "docs.response.body.bytes",
                    "docs.response.headers",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
                "The case reads the client host in one endpoint response.",
            )
        ],
        "Partial: only the client-host property is observed. The recipe does not test direct body reads, skipped validation/OpenAPI behavior for manually read data, simultaneous declared parameters, or Request import/object identity.",
        [
            _source(
                "docs/en/docs/advanced/using-request-directly.md",
                16,
                42,
                "FastAPI Request injection and its boundary with normally declared parameters.",
            ),
            _source(
                "docs/en/docs/advanced/using-request-directly.md",
                46,
                54,
                "The Request class and properties are imported from Starlette.",
            ),
            _source(
                "fastapi/dependencies/utils.py",
                350,
                374,
                "FastAPI classifies Request as a special non-field endpoint dependency parameter.",
            ),
            _source(
                "fastapi/routing.py",
                375,
                425,
                "FastAPI invokes the endpoint with the current Starlette Request object.",
            ),
        ],
        _STARLETTE_REQUEST + _STARLETTE_RESPONSE,
    ),
    "how-to/authentication-error-status-code.md": _review(
        ["dependency-security", "public-api-errors"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.security",
        ],
        "FastAPI HTTPBearer calls `make_not_authenticated_error` on missing/invalid bearer credentials; a user subclass can choose the exception status, and FastAPI's default HTTPException handler produces the response. Header parsing and generic exception middleware dispatch remain Starlette-owned contract behavior.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml",
                [
                    "fastapi.docs.documentation-wave.dependencies-security.authentication-error-status"
                ],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.security",
                ],
                "The custom authentication-error branch observes the selected status, headers, and response bytes.",
            )
        ],
        "Partial: one missing-credential path does not cover malformed credentials, wrong scheme, successful bearer authentication, custom `WWW-Authenticate` values, or all FastAPI/Starlette exception handler combinations.",
        [
            _source(
                "docs/en/docs/how-to/authentication-error-status-code.md",
                1,
                17,
                "FastAPI HTTPBearer error-status change and the supported subclass override.",
            ),
            _source(
                "fastapi/security/http.py",
                222,
                317,
                "FastAPI HTTPBearer dependency calls the overridable unauthenticated-error factory for invalid credentials.",
            ),
            _source(
                "fastapi/exception_handlers.py",
                11,
                17,
                "FastAPI serializes HTTPException status/detail/headers into the response.",
            ),
            _source(
                "fastapi/applications.py",
                1000,
                1005,
                "FastAPI registers its default HTTPException handler.",
            ),
        ],
        _STARLETTE_REQUEST + _STARLETTE_RESPONSE + _STARLETTE_EXCEPTION,
    ),
    "how-to/conditional-openapi.md": _review(
        ["openapi-docs"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "FastAPI's configured `openapi_url` controls registration of the schema, Swagger UI, and ReDoc endpoints. The page's settings object and environment parsing come from Pydantic Settings/application code; they are not assigned to FastAPI. Endpoint response transport is Starlette behavior.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                [
                    "fastapi.docs.openapi-interface.how-to-conditional-openapi.disabled-schema-endpoint",
                ],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
                "The disabled endpoint response and enabled schema's paths object are observed in the same case.",
            ),
        ],
        "Partial: the existing case compares disabled and enabled schema endpoints, but does not run environment-variable parsing, settings construction, `/docs` or `/redoc` absence checks, or deployment process behavior.",
        [
            _source(
                "docs/en/docs/how-to/conditional-openapi.md",
                1,
                4,
                "Conditional setting is presented as user application configuration.",
            ),
            _source(
                "docs/en/docs/how-to/conditional-openapi.md",
                26,
                50,
                "FastAPI endpoint behavior when openapi_url is set or disabled.",
            ),
            _source(
                "fastapi/applications.py",
                881,
                890,
                "FastAPI stores the configured OpenAPI/docs URLs and schema-mode option on the application.",
            ),
            _source(
                "fastapi/applications.py",
                1105,
                1158,
                "FastAPI registers the OpenAPI/docs routes only when their URLs are configured.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "how-to/configure-swagger-ui.md": _review(
        ["openapi-docs"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        "FastAPI owns Swagger UI HTML generation, default parameter selection, and merge of configured UI parameters; Swagger UI's JavaScript behavior and browser rendering belong to the external frontend. Starlette's HTMLResponse performs generic response emission.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.how-to-configure-swagger-ui.configured-swagger"],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
                "The `/docs` HTML bytes and a selected `/openapi.json` info projection are observed.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/swagger-ui-config-default-wave.yaml",
                ["fastapi.docs-ui.swagger-parameters.default-config"],
                ["http.body.bytes", "http.status"],
                "Default Swagger UI parameter HTML is observed as raw bytes.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/swagger-ui-config-override-wave.yaml",
                ["fastapi.docs-ui.swagger-parameters.override-default"],
                ["http.body.bytes", "http.status"],
                "An explicit UI parameter override is observed as HTML bytes.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/swagger-ui-config-theme-wave.yaml",
                ["fastapi.docs-ui.swagger-parameters.nested-theme"],
                ["http.body.bytes", "http.status"],
                "A nested theme/configuration value is observed in the generated HTML bytes.",
            ),
        ],
        "Partial: generated HTML/config serialization is sampled, but no browser executes the JavaScript. Syntax highlighting and every JavaScript-only option, theme combination, CDN asset, OAuth flow, and escaping edge are not covered by these cases.",
        [
            _source(
                "docs/en/docs/how-to/configure-swagger-ui.md",
                1,
                55,
                "Swagger UI options documented by the page, including default parameter overrides.",
            ),
            _source(
                "fastapi/openapi/docs.py",
                40,
                194,
                "FastAPI creates Swagger UI HTML and merges `swagger_ui_parameters` with defaults.",
            ),
            _source(
                "fastapi/applications.py",
                1121,
                1137,
                "FastAPI docs route passes URLs and configured parameters into its HTML helper.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "how-to/custom-docs-ui-assets.md": _review(
        ["openapi-docs", "app-routing"],
        [
            "docs.response.body.bytes",
            "docs.response.headers",
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "FastAPI owns the custom docs route pattern and its `get_swagger_ui_html`/OpenAPI URL integration. StaticFiles serving, mount-prefix dispatch, CDN behavior, browser asset fetching, and the JavaScript UI are delegated to Starlette-RS or external browser/assets behavior.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.how-to-custom-docs-ui-assets.custom-docs-assets"],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                ],
                "One custom docs HTML response and its configured OpenAPI document metadata are observed.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-static-files-mount-boundary.yaml",
                ["fastapi.docs.static-files.mount-parent-openapi-docs-boundary"],
                [
                    "docs.response.body.bytes",
                    "docs.response.headers",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "A separate case checks parent OpenAPI/docs endpoints beside a mounted static path; it does not fetch an asset file.",
            ),
        ],
        "Partial: cases cover generated custom docs HTML and one mount/schema boundary only. They do not fetch JavaScript/CSS/image assets, assert browser rendering, cover local filesystem serving, exercise every custom URL combination, or validate external CDN availability.",
        [
            _source(
                "docs/en/docs/how-to/custom-docs-ui-assets.md",
                1,
                53,
                "Custom CDN and custom docs route generation.",
            ),
            _source(
                "docs/en/docs/how-to/custom-docs-ui-assets.md",
                116,
                181,
                "Self-hosted static asset and custom docs examples.",
            ),
            _source(
                "fastapi/openapi/docs.py",
                40,
                194,
                "FastAPI HTML helper builds the custom Swagger UI page.",
            ),
            _source(
                "fastapi/applications.py",
                1105,
                1137,
                "FastAPI uses OpenAPI URLs and docs-route setup for its own automatic documentation pages.",
            ),
        ],
        _STARLETTE_MOUNT + _STARLETTE_RESPONSE,
    ),
    "how-to/custom-request-and-route.md": _review(
        ["app-routing", "request-validation", "response-serialization"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        "FastAPI owns APIRoute registration and lets subclasses wrap its generated request handler; the example's custom Request class derives from Starlette Request. Request body stream/decompression and response transport use Starlette APIs and the external Python wrapper in the documented app, so they are not recast as independent FastAPI behavior.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/custom-route-observations-upstream.yaml",
                [
                    "fastapi.custom-request-route.tutorial001-request-subclass-body",
                    "fastapi.custom-request-route.tutorial001-request-subclass-identity",
                    "fastapi.custom-request-route.tutorial003-plain-route",
                    "fastapi.custom-request-route.tutorial003-measured-route-body",
                ],
                ["http.body.bytes", "http.headers.ordered", "http.status"],
                "The cases observe decompressed-route output, Request subclass identity as returned output, and custom APIRoute output; no timing measurement selector is present.",
            )
        ],
        "Partial: cases do not compare compressed and uncompressed body variants, exception-handler body rereads, all custom route subclasses, request import/object identity, or timing values. Do not treat the measured-route example name as benchmark evidence.",
        [
            _source(
                "docs/en/docs/how-to/custom-request-and-route.md",
                25,
                69,
                "Custom Request and APIRoute wrappers for body handling.",
            ),
            _source(
                "docs/en/docs/how-to/custom-request-and-route.md",
                81,
                109,
                "Exception-handler body access and router-specific custom route class.",
            ),
            _source(
                "fastapi/routing.py",
                1126,
                1250,
                "FastAPI APIRoute constructs and returns the framework request handler; subclasses can wrap this hook.",
            ),
            _source(
                "fastapi/routing.py",
                2889,
                2970,
                "FastAPI APIRouter registers configured APIRoute subclasses.",
            ),
        ],
        _STARLETTE_REQUEST + _STARLETTE_RESPONSE,
    ),
    "how-to/extending-openapi.md": _review(
        ["openapi-docs"],
        ["docs.response.status", "http.status", "openapi.document"],
        "FastAPI owns `app.openapi()` caching and delegates document construction to its `get_openapi` utility; users may override the method and add fields. OpenAPI specification semantics and any external documentation renderer are not claimed by the input.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.how-to-extending-openapi.custom-openapi-fields"],
                ["docs.response.status", "http.status", "openapi.document"],
                "The schema endpoint response and selected info/custom-root-field/path pointers are observed.",
            )
        ],
        "Partial: a single customized document projection does not exercise cache hit/invalidation behavior, all `get_openapi` inputs, custom route-tree traversal, or all possible merge/override shapes.",
        [
            _source(
                "docs/en/docs/how-to/extending-openapi.md",
                1,
                34,
                "FastAPI's normal OpenAPI route, cache property, and generator utility.",
            ),
            _source(
                "docs/en/docs/how-to/extending-openapi.md",
                44,
                83,
                "Custom schema fields, caching, and overriding `app.openapi()`.",
            ),
            _source(
                "fastapi/applications.py",
                1070,
                1103,
                "FastAPI builds and caches app.openapi() and refreshes it when routes change.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                585,
                670,
                "FastAPI builds the OpenAPI document from application route metadata.",
            ),
        ],
        _STARLETTE_RESPONSE,
    ),
    "how-to/separate-openapi-schemas.md": _review(
        ["openapi-docs", "request-validation", "response-serialization"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        "FastAPI selects validation versus serialization fields and assembles the resulting input/output schemas in OpenAPI; Pydantic 2 generates the field schemas. HTTP request and response transport is Starlette-RS behavior.",
        [
            _workflow(
                "tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml",
                [
                    "fastapi.docs.openapi-interface.how-to-separate-openapi-schemas.input-output-models"
                ],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "One POST/GET model route and selected operation/component schema nodes are observed.",
            ),
            _workflow(
                "tests/fixtures/input-recipes/parity/separate-openapi-schemas-tutorial002-upstream.yaml",
                [
                    "fastapi.test.test-tutorial-test-separate-openapi-schemas-test-tutorial002.shared-model-requests-and-openapi"
                ],
                [
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "A shared model receives requests and its selected OpenAPI component is observed.",
            ),
        ],
        "Partial: selected operations and schema pointers do not enumerate every field/default/requiredness combination, nested model or union, Pydantic JSON Schema option, or both values of FastAPI's separate_input_output_schemas switch. Pydantic schema-generation details are not FastAPI-owned internals.",
        [
            _source(
                "docs/en/docs/how-to/separate-openapi-schemas.md",
                1,
                75,
                "Pydantic v2 input/output schema distinction, required output field, and separate generated schemas.",
            ),
            _source(
                "docs/en/docs/how-to/separate-openapi-schemas.md",
                80,
                101,
                "Page's shared-schema configuration example.",
            ),
            _source(
                "fastapi/applications.py",
                1084,
                1101,
                "FastAPI passes `separate_input_output_schemas` into OpenAPI generation.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                231,
                263,
                "FastAPI builds request-body schemas using validation-mode model fields.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                311,
                400,
                "FastAPI emits route request/response schemas with the selected input/output mode.",
            ),
            _source(
                "fastapi/openapi/utils.py",
                585,
                650,
                "FastAPI constructs validation/serialization field mappings for the document.",
            ),
        ],
        _STARLETTE_REQUEST + _STARLETTE_RESPONSE,
    ),
}
