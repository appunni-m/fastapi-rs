"""Reviewed partial mappings from response documentation examples to inputs."""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(recipe: str, case_id: str, selectors: list[str]) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": [case_id],
        "observation_selectors": sorted(selectors),
    }


def _review(
    rationale: str,
    spans: list[dict[str, object]],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {"rationale": rationale, "supporting_sources": spans, "workflow_cases": cases}


DOC_EXAMPLE_CITATION_WAVE_G = {
    "docs_src/custom_response/tutorial005_py310.py": _review(
        (
            "The example returns a string through PlainTextResponse. The independent route "
            "uses a different path and string and observes the response status, headers, "
            "and bytes. It samples this response-class path only."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial005_py310.py",
                7,
                9,
                "PlainTextResponse route and returned text",
            )
        ],
        [
            _case(
                "starlette-response-runtime-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial005.test-get",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial006_py310.py": _review(
        (
            "The example returns a RedirectResponse instance. The independent route returns "
            "a direct redirect instance at another path and location; the selected case "
            "observes its status, headers, and body. The route's configured JSON response "
            "class is bypassed by the returned response instance."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial006_py310.py",
                7,
                9,
                "route returning a RedirectResponse instance",
            )
        ],
        [
            _case(
                "starlette-response-runtime-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial006.test-get",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial006b_py310.py": _review(
        (
            "The example declares RedirectResponse as the route response class and returns "
            "a URL string. The independent case uses the same response-class path with a "
            "different route and destination, observing status and headers only; its body "
            "is not claimed."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial006b_py310.py",
                7,
                9,
                "RedirectResponse route class and URL return value",
            )
        ],
        [
            _case(
                "responses-background-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial006b.test-redirect-response-class",
                ["http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial007_py310.py": _review(
        (
            "The example streams chunks from an async generator. The independent streaming "
            "route also uses an async generator and observes response status, headers, and "
            "stream bytes, with different chunk values. Generator timing and the source "
            "video payload are not claimed."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial007_py310.py",
                8,
                16,
                "async generator and StreamingResponse route",
            )
        ],
        [
            _case(
                "starlette-response-runtime-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial007.test-get",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial008_py310.py": _review(
        (
            "The example streams a synchronous file iterator with StreamingResponse. The "
            "independent route uses a separately sourced synchronous iterator and observes "
            "response status, headers, and stream bytes. The named video file and its "
            "content are not covered."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial008_py310.py",
                4,
                14,
                "synchronous file iterator and StreamingResponse route",
            )
        ],
        [
            _case(
                "starlette-response-runtime-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial008.test-get",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial009_py310.py": _review(
        (
            "The example returns FileResponse for a file path. The independent route returns "
            "FileResponse for a different local file and observes response status, headers, "
            "and bytes; the tutorial file path and video content are not claimed."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial009_py310.py",
                4,
                10,
                "file path and direct FileResponse route",
            )
        ],
        [
            _case(
                "starlette-response-runtime-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial009.test-get",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial009b_py310.py": _review(
        (
            "The example declares FileResponse as the route response class and returns a "
            "path string. The independent case exercises that route-class construction with "
            "a different local file, observing status, headers, and bytes only."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial009b_py310.py",
                4,
                10,
                "FileResponse route class and path return value",
            )
        ],
        [
            _case(
                "starlette-response-runtime-upstream.yaml",
                "fastapi.test.test-tutorial-test-custom-response-test-tutorial009b.test-get",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_response/tutorial010_py310.py": _review(
        (
            "The example selects HTMLResponse as the application default for an unannotated "
            "route. The independent app selects a different default response class and "
            "returns different data; its status, headers, and body sample application-level "
            "default selection, not HTML rendering."
        ),
        [
            _span(
                "docs_src/custom_response/tutorial010_py310.py",
                4,
                9,
                "application default response class and route",
            )
        ],
        [
            _case(
                "default-response-class-precedence-wave.yaml",
                "fastapi.test.test-default-response-class.test-app",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/response_directly/tutorial002_py310.py": _review(
        (
            "The example returns a raw Response with XML content and an explicit media type. "
            "The independent route returns a different XML Response and selects the "
            "operation's OpenAPI path; it observes response status, headers, and bytes, not "
            "the tutorial's XML literals."
        ),
        [
            _span(
                "docs_src/response_directly/tutorial002_py310.py",
                6,
                18,
                "raw XML Response construction and route",
            )
        ],
        [
            _case(
                "responses-background-upstream.yaml",
                "fastapi.test.test-tutorial-test-response-directly-test-tutorial002.test-path-operation",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            ),
            _case(
                "responses-background-upstream.yaml",
                "fastapi.test.test-tutorial-test-response-directly-test-tutorial002.test-openapi-schema",
                ["http.status", "openapi.paths"],
            ),
        ],
    ),
    "docs_src/response_model/tutorial001_py310.py": _review(
        (
            "The example explicitly declares response_model for input and returned item "
            "data. The independent case uses an explicit response model on a different route "
            "and model, observing its response body, status, and selected schema paths; it "
            "does not claim the tutorial's model fields or values."
        ),
        [
            _span(
                "docs_src/response_model/tutorial001_py310.py",
                9,
                27,
                "item model and explicit response_model route declarations",
            )
        ],
        [
            _case(
                "response-model-tutorials-upstream.yaml",
                "fastapi.response-model.tutorial001-defaults-and-list-output",
                ["http.body.bytes", "http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/response_model/tutorial001_01_py310.py": _review(
        (
            "This example infers a response model from the handler's return annotation. The "
            "selected independent route uses a different Pydantic model and return annotation "
            "to sample that inference and its response filtering; list annotations and the "
            "example's model defaults are not claimed."
        ),
        [
            _span(
                "docs_src/response_model/tutorial001_01_py310.py",
                15,
                17,
                "route return annotation used to infer the response model",
            )
        ],
        [
            _case(
                "response-model-tutorials-upstream.yaml",
                "fastapi.response-model.tutorial003-01-return-annotation-filters-derived-input",
                ["http.body.bytes", "http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/response_model/tutorial003_02_py310.py": _review(
        (
            "The example annotates a route as Response and returns JSONResponse or "
            "RedirectResponse depending on a query value. The independent cases exercise "
            "both branches and the selected OpenAPI path with different values; they do not "
            "claim the tutorial's destination or response text."
        ),
        [
            _span(
                "docs_src/response_model/tutorial003_02_py310.py",
                7,
                11,
                "Response return annotation and JSON/redirect branches",
            )
        ],
        [
            _case(
                "response-model-tutorials-upstream.yaml",
                "fastapi.response-model.tutorial003-02-response-annotation-allows-response-values",
                [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
            )
        ],
    ),
    "docs_src/response_model/tutorial003_03_py310.py": _review(
        (
            "The example annotates its route as RedirectResponse and returns that response "
            "class. The independent route returns a redirect to a different destination and "
            "selects its OpenAPI response path; status, headers, and body are the runtime "
            "observations."
        ),
        [
            _span(
                "docs_src/response_model/tutorial003_03_py310.py",
                7,
                9,
                "RedirectResponse return annotation and route result",
            )
        ],
        [
            _case(
                "response-model-tutorials-upstream.yaml",
                "fastapi.response-model.tutorial003-03-redirect-response-return-annotation",
                [
                    "http.body.bytes",
                    "http.headers.ordered",
                    "http.status",
                    "openapi.paths",
                ],
            )
        ],
    ),
    "docs_src/response_model/tutorial005_py310.py": _review(
        (
            "The example uses response_model_include and response_model_exclude for top-level "
            "fields. The independent nested-model cases exercise the same projection options "
            "only on nested fields and observe status/body; they do not establish the tutorial's "
            "top-level field selection, data, or schema projection."
        ),
        [
            _span(
                "docs_src/response_model/tutorial005_py310.py",
                7,
                36,
                "item model and response include/exclude route declarations",
            )
        ],
        [
            _case(
                "response-model-include-exclude-source-review.yaml",
                "fastapi.response-model.include.nested.model",
                ["http.body.bytes", "http.status"],
            ),
            _case(
                "response-model-include-exclude-source-review.yaml",
                "fastapi.response-model.exclude.nested.model",
                ["http.body.bytes", "http.status"],
            ),
        ],
    ),
    "docs_src/response_headers/tutorial001_py310.py": _review(
        (
            "The example returns JSONResponse with explicit headers. The independent direct "
            "JSON response uses another body and header set and observes status, ordered "
            "headers, and body bytes; it does not claim the source header values."
        ),
        [
            _span(
                "docs_src/response_headers/tutorial001_py310.py",
                7,
                11,
                "JSONResponse route with response headers",
            )
        ],
        [
            _case(
                "response-surface.yaml",
                "fastapi.response.direct-json",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/response_headers/tutorial002_py310.py": _review(
        (
            "The example mutates the injected FastAPI Response before returning a JSON "
            "object. The independent case applies a different header and body on a separate "
            "route and observes status, ordered headers, and body bytes."
        ),
        [
            _span(
                "docs_src/response_headers/tutorial002_py310.py",
                6,
                9,
                "injected Response header mutation and returned object",
            )
        ],
        [
            _case(
                "responses-background-upstream.yaml",
                "fastapi.test.test-tutorial-test-response-headers-test-tutorial002.test-path-operation",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/response_status_code/tutorial001_py310.py": _review(
        (
            "The example declares status 201 with a numeric literal. The independent POST "
            "case declares the same status on a separately named route and observes status "
            "and body; its output does not establish the tutorial's route or query value."
        ),
        [
            _span(
                "docs_src/response_status_code/tutorial001_py310.py",
                6,
                8,
                "literal 201 route status declaration",
            )
        ],
        [
            _case(
                "response-surface.yaml",
                "fastapi.response.declared-status",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/response_status_code/tutorial002_py310.py": _review(
        (
            "The example declares status.HTTP_201_CREATED. The independent POST case samples "
            "the same numeric status and response body on a different route; it does not "
            "distinguish the symbolic constant from the value 201."
        ),
        [
            _span(
                "docs_src/response_status_code/tutorial002_py310.py",
                6,
                8,
                "FastAPI status constant route declaration",
            )
        ],
        [
            _case(
                "response-surface.yaml",
                "fastapi.response.declared-status",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/response_cookies/tutorial002_py310.py": _review(
        (
            "The example sets a cookie on the injected Response and returns a JSON object. "
            "The independent case uses a different cookie and response body and observes "
            "status, ordered headers, and body bytes."
        ),
        [
            _span(
                "docs_src/response_cookies/tutorial002_py310.py",
                6,
                9,
                "injected Response cookie mutation and returned object",
            )
        ],
        [
            _case(
                "responses-background-upstream.yaml",
                "fastapi.test.test-tutorial-test-response-cookies-test-tutorial002.test-path-operation",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/background_tasks/tutorial002_py310.py": _review(
        (
            "The example injects BackgroundTasks into a dependency and endpoint so both can "
            "schedule work. The independent case schedules tasks through nested dependencies "
            "and the endpoint, then observes the response and completed effects; conditional "
            "query logging and file output are not covered."
        ),
        [
            _span(
                "docs_src/background_tasks/tutorial002_py310.py",
                6,
                23,
                "dependency task scheduling and endpoint injection",
            )
        ],
        [
            _case(
                "background-tasks-injection-precedence.yaml",
                "fastapi.test.test-response-dependency.test-background-tasks-with-depends-annotated.normal-response",
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/background_tasks/tutorial002_an_py310.py": _review(
        (
            "The Annotated example injects BackgroundTasks into a dependency and endpoint "
            "so both can schedule work. The independent case schedules work through nested "
            "dependencies and the endpoint and observes completed effects; its query branch, "
            "file output, and values are not covered."
        ),
        [
            _span(
                "docs_src/background_tasks/tutorial002_an_py310.py",
                13,
                25,
                "Annotated dependency task scheduling and endpoint injection",
            )
        ],
        [
            _case(
                "background-tasks-injection-precedence.yaml",
                "fastapi.test.test-response-dependency.test-background-tasks-with-depends-annotated.normal-response",
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/encoder/tutorial001_py310.py": _review(
        (
            "The example passes a Pydantic model to jsonable_encoder before storing the "
            "result. The independent ASGI route uses the encoder on a different Pydantic "
            "model before returning JSONResponse and observes response status, headers, "
            "and bytes; the fake database mutation is not covered."
        ),
        [
            _span(
                "docs_src/encoder/tutorial001_py310.py",
                10,
                22,
                "Pydantic input model and jsonable_encoder call",
            )
        ],
        [
            _case(
                "response-directly-tutorial001-wave.yaml",
                "fastapi.response-directly.tutorial001.path-response",
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/extra_data_types/tutorial001_py310.py": _review(
        (
            "The example parses UUID, datetime, time, and timedelta inputs and uses the "
            "derived values in its response. The independent route submits other values and "
            "observes the response and selected OpenAPI paths; arithmetic literals and the "
            "complete schema are not claimed."
        ),
        [
            _span(
                "docs_src/extra_data_types/tutorial001_py310.py",
                9,
                27,
                "typed path/body parameters and temporal response calculation",
            )
        ],
        [
            _case(
                "pydantic-extra-type-body-wave.yaml",
                "fastapi.pydantic-extra-type-body-wave.datetime-duration.test-extra-types",
                ["http.body.bytes", "http.status"],
            ),
            _case(
                "pydantic-extra-type-body-wave.yaml",
                "fastapi.pydantic-extra-type-body-wave.datetime-duration.test-openapi-schema",
                ["openapi.paths"],
            ),
        ],
    ),
    "docs_src/dataclasses_/tutorial001_py310.py": _review(
        (
            "The example accepts and returns a standard-library dataclass with required "
            "string/float fields and nullable fields defaulting to None. The independent route "
            "mirrors those "
            "field types/defaults and the request-return flow under different class/route names, "
            "with independent values; it claims the request schema and response serialization only."
        ),
        [
            _span(
                "docs_src/dataclasses_/tutorial001_py310.py",
                6,
                19,
                "stdlib dataclass request type and route returning that instance",
            )
        ],
        [
            _case(
                "docs-example-dataclass-request-wave-g.yaml",
                "fastapi.docs-wave-g.dataclasses.stdlib-request-and-return",
                ["http.body.bytes", "http.status", "openapi.paths"],
            )
        ],
    ),
}


DOC_EXAMPLE_EXCLUSION_WAVE_G = {
    "docs_src/custom_response/tutorial001b_py310.py": (
        "This example delegates response serialization to Starlette's optional ORJSONResponse "
        "backend and the third-party orjson package. That serializer implementation is not "
        "FastAPI-owned runtime behavior."
    ),
    "docs_src/custom_response/tutorial009c_py310.py": (
        "The example defines a user-owned Response subclass whose render method calls optional "
        "orjson. Its serialization logic is application code, not FastAPI runtime behavior."
    ),
}
