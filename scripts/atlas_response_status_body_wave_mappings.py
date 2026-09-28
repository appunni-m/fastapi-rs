"""Reviewed links for response status/body source checks and existing inputs.

The source checks already have direct-ASGI input cases, so this sidecar reuses
their recipe cases instead of adding duplicate stimuli. FastAPI selects route
status and constructs a response; Starlette 1.6.0 owns generic response headers,
body rendering, and ASGI emission.
"""


def _source(path, start, end, role):
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(
    test_path,
    test_start,
    test_end,
    feature_ids,
    observation_selectors,
    rationale,
    workflow,
    *,
    implementation_sources,
    contract_sources=(),
    contract_gate,
):
    return {
        "feature_ids": list(feature_ids),
        "observation_selectors": list(observation_selectors),
        "rationale": rationale,
        "replace_features": True,
        "supporting_sources": [
            _source(
                test_path, test_start, test_end, "upstream test stimulus and asserted behavior"
            ),
            *implementation_sources,
            *contract_sources,
        ],
        "stimulus_notes": workflow,
        "contract_gate": contract_gate,
    }


_STATUS_SELECTION = _source(
    "fastapi/routing.py",
    357,
    372,
    "FastAPI selects configured or dependency-mutated response status",
)
_RESPONSE_BUILD = _source(
    "fastapi/routing.py",
    716,
    750,
    "FastAPI serializes endpoint output, constructs the selected response class, and applies its no-body status policy",
)
_TEMP_RESPONSE = _source(
    "fastapi/dependencies/utils.py",
    611,
    614,
    "FastAPI creates the mutable temporary Response used to carry a dependency-selected status",
)
_INJECT_RESPONSE = _source(
    "fastapi/dependencies/utils.py",
    719,
    720,
    "FastAPI injects the temporary Response into a path operation or dependency",
)
_STARLETTE_RESPONSE_HEADERS = _source(
    "starlette/responses.py",
    33,
    81,
    "Starlette 1.6.0 renders response bytes and initializes content headers, including Content-Length policy",
)
_STARLETTE_RESPONSE_SEND = _source(
    "starlette/responses.py",
    163,
    168,
    "Starlette 1.6.0 sends the HTTP response start and body ASGI messages",
)
_STARLETTE_STREAM_SEND = _source(
    "starlette/responses.py",
    248,
    255,
    "Starlette 1.6.0 emits StreamingResponse status and body chunks",
)


RESPONSE_STATUS_BODY_TEST_REVIEW_MAPPINGS = {
    "tests/test_response_code_no_body.py": {
        "functions": {
            "test_get_response": _case(
                "tests/test_response_code_no_body.py",
                41,
                45,
                ["response-serialization"],
                ["http.status", "http.headers.ordered", "http.body.bytes"],
                "A configured 204 route uses an explicit JSONResponse subclass; the test checks the status, absence of content-length, and empty body.",
                "Reuse response-policy-matrix.yaml case fastapi.response.bodyless-204, action empty-response. It sends a direct ASGI GET and observes status, headers, and body; its route uses FastAPI's default JSONResponse rather than the source's custom media-type subclass.",
                implementation_sources=[
                    _source(
                        "tests/test_response_code_no_body.py",
                        10,
                        11,
                        "The source response-class subclass sets a custom media type",
                    ),
                    _source(
                        "tests/test_response_code_no_body.py",
                        23,
                        30,
                        "The source route declares status 204 and the custom response class",
                    ),
                    _STATUS_SELECTION,
                    _RESPONSE_BUILD,
                ],
                contract_sources=[_STARLETTE_RESPONSE_HEADERS, _STARLETTE_RESPONSE_SEND],
                contract_gate="FastAPI selects the configured route status and response class. The source assertion about content-length absence and empty wire bytes is generic Starlette 1.6.0 response behavior. The linked input checks exact headers and uses a different response-class configuration, so this mapping does not claim the source's custom media type or exact header-list parity.",
            ),
        },
    },
    "tests/test_response_set_response_code_empty.py": {
        "functions": {
            "test_dependency_set_status_code": _case(
                "tests/test_response_set_response_code_empty.py",
                26,
                29,
                ["response-serialization"],
                ["http.status", "http.body.json"],
                "A route declared as 204 injects a mutable Response, overrides it to 400, and returns a nonempty JSON object.",
                "Reuse response-policy-matrix.yaml case fastapi.response.status-overwrite, action delete-record. It sends a direct ASGI DELETE and observes status, headers, and raw body bytes; the route and body values are independently authored.",
                implementation_sources=[
                    _source(
                        "tests/test_response_set_response_code_empty.py",
                        10,
                        20,
                        "The source route declares 204, injects Response, and mutates its status to 400 before returning JSON data",
                    ),
                    _TEMP_RESPONSE,
                    _INJECT_RESPONSE,
                    _STATUS_SELECTION,
                ],
                contract_sources=[_STARLETTE_RESPONSE_HEADERS, _STARLETTE_RESPONSE_SEND],
                contract_gate="FastAPI owns Response injection and the precedence of the dependency-mutated status over the decorator status. Starlette 1.6.0 owns JSONResponse byte rendering, header construction, and ASGI emission. The source asserts parsed JSON and nonempty content; the linked case compares raw bytes and headers on a different route/body, so the mapping is limited to status override plus a nonempty JSON response.",
            ),
        },
    },
    "tests/test_stream_status_code.py": {
        "functions": {
            "test_status_code": _case(
                "tests/test_stream_status_code.py",
                138,
                154,
                ["response-serialization"],
                ["http.status"],
                "Nine SSE, JSONL, and raw streaming route combinations select declared or dependency-overridden response statuses.",
                "Reuse stream-status-code-upstream.yaml case fastapi.test.test-stream-status-code.test-status-code. Its nine direct ASGI POST actions use the source's route/status matrix and observe status only.",
                implementation_sources=[
                    _source(
                        "tests/test_stream_status_code.py",
                        52,
                        54,
                        "The source dependency mutates the injected Response status to 202",
                    ),
                    _source(
                        "tests/test_stream_status_code.py",
                        56,
                        68,
                        "The source declares SSE, JSONL, and raw streams with status 201",
                    ),
                    _source(
                        "tests/test_stream_status_code.py",
                        71,
                        97,
                        "The source declares three stream kinds whose dependency selects status 202",
                    ),
                    _source(
                        "tests/test_stream_status_code.py",
                        100,
                        132,
                        "The source declares three stream kinds with status 201 overridden by dependency status 202",
                    ),
                    _STATUS_SELECTION,
                    _source(
                        "fastapi/routing.py",
                        635,
                        646,
                        "FastAPI constructs the SSE streaming response with the resolved status",
                    ),
                    _source(
                        "fastapi/routing.py",
                        674,
                        682,
                        "FastAPI constructs the JSONL streaming response with the resolved status",
                    ),
                    _source(
                        "fastapi/routing.py",
                        700,
                        704,
                        "FastAPI constructs the raw streaming response with the resolved status",
                    ),
                ],
                contract_sources=[_STARLETTE_STREAM_SEND],
                contract_gate="The upstream test asserts status only. FastAPI selects declared/dependency-mutated status for the three stream branches; Starlette 1.6.0 emits generic streaming status and chunks. The mapping makes no claim about stream body bytes, chunk boundaries, response headers, or TestClient transport behavior.",
            ),
        },
    },
}
