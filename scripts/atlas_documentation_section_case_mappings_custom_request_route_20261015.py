"""Reviewed section mappings for FastAPI's custom request and route guide."""

_PAGE = "how-to/custom-request-and-route.md"
_CUSTOM_ROUTE = "tests/fixtures/input-recipes/parity/source-wave-b-custom-routes.yaml"
_ROUTER_CLASS = (
    "tests/fixtures/input-recipes/parity/custom-request-route-sections-review-20261015.yaml"
)


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


_HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]


DOC_SECTION_CASE_MAPPINGS_CUSTOM_REQUEST_ROUTE_20261015 = {
    (_PAGE, "custom-request-and-apiroute-class"): _workflow(
        "Custom Request and APIRoute class { #custom-request-and-apiroute-class }",
        1,
        109,
        _CUSTOM_ROUTE,
        [
            "fastapi.source-wave-b.custom-request.uncompressed-json",
            "fastapi.source-wave-b.custom-request.request-subclass",
        ],
        None,
        _HTTP_BODY_STATUS,
        (
            "The page-level heading and introduction aggregate the use-case list and the "
            "child request/route examples. These selected inputs partially sample a custom "
            "Request/APIRoute wrapper on uncompressed JSON; they do not cover gzip bytes, "
            "message-pack conversion, or request logging."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/how-to/custom-request-and-route.md:1-109 "
            "introduces custom Request/APIRoute extension points and groups the body-encoding, "
            "exception-handler, and router examples. The selected source-wave-b cases pair an "
            "independently authored custom Request subclass with a custom route-handler wrapper "
            "and compare HTTP status/body bytes. The page's other child sections have their own "
            "narrower mappings below."
        ),
    ),
    (_PAGE, "handling-custom-request-body-encodings"): _workflow(
        "Handling custom request body encodings { #handling-custom-request-body-encodings }",
        25,
        80,
        _CUSTOM_ROUTE,
        [
            "fastapi.source-wave-b.custom-request.uncompressed-json",
            "fastapi.source-wave-b.custom-request.request-subclass",
        ],
        None,
        _HTTP_BODY_STATUS,
        (
            "The selected inputs sample the uncompressed branch and FastAPI route-handler "
            "integration for a custom Request subclass. The valid gzip-compressed body branch "
            "is excluded under the GzipRequest child section."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/how-to/custom-request-and-route.md:25-80 "
            "introduces gzip request handling and then expands it under the GzipRequest and "
            "GzipRoute headings. The source-wave-b independent route tests ordinary JSON input "
            "and custom Request construction; its workflow sources cite the pinned tutorial "
            "example and upstream test but it does not claim the compressed branch."
        ),
    ),
    (_PAGE, "create-a-custom-gziprequest-class"): _excluded(
        "Create a custom `GzipRequest` class { #create-a-custom-gziprequest-class }",
        31,
        46,
        (
            "The documented gzip decompression branch is user-provided Python code, and the "
            "current HTTP recipe input shape cannot carry arbitrary compressed bytes. The "
            "existing uncompressed-body case covers only the non-gzip path; no decompression "
            "claim is made."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/how-to/custom-request-and-route.md:31-46 "
            "describes overriding Request.body() and conditionally calling gzip.decompress; "
            "the included docs_src/custom_request_and_route/tutorial001_py310.py:8-15 and "
            "tests/test_tutorial/test_custom_request_and_route/test_tutorial001.py "
            "supply the source example and test. This is custom extension code over "
            "Starlette's Request body API, while the recipe schema's HTTP receive body is "
            "text and cannot supply a valid gzip byte stream."
        ),
    ),
    (_PAGE, "create-a-custom-gziproute-class"): _workflow(
        "Create a custom `GzipRoute` class { #create-a-custom-gziproute-class }",
        47,
        80,
        _CUSTOM_ROUTE,
        [
            "fastapi.source-wave-b.custom-request.uncompressed-json",
            "fastapi.source-wave-b.custom-request.request-subclass",
        ],
        None,
        _HTTP_BODY_STATUS,
        (
            "The independent cases send uncompressed JSON through a custom APIRouter route "
            "class, once to a typed body route and once to expose the replacement Request "
            "subclass. They select route-handler delegation and body processing only; gzip "
            "decompression is excluded under the GzipRequest section."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/how-to/custom-request-and-route.md:47-80 "
            "describes an APIRoute.get_route_handler() wrapper that constructs GzipRequest and "
            "delegates to FastAPI's original handler. The source example is "
            "docs_src/custom_request_and_route/tutorial001_py310.py:18-34; the selected "
            "source-wave-b-custom-routes.yaml cases use an independently authored Request and "
            "APIRoute subclass and observe exact HTTP status/body bytes for uncompressed JSON. "
            "Their source_evidence names the pinned tutorial example and upstream test."
        ),
    ),
    (_PAGE, "accessing-the-request-body-in-an-exception-handler"): _workflow(
        (
            "Accessing the request body in an exception handler "
            "{ #accessing-the-request-body-in-an-exception-handler }"
        ),
        81,
        100,
        _CUSTOM_ROUTE,
        ["fastapi.source-wave-b.custom-route.validation-context"],
        ["post-invalid-shape-with-context"],
        _HTTP_BODY_STATUS,
        (
            "The selected invalid JSON-shape request reaches a custom route wrapper that "
            "catches RequestValidationError, reads the request body, and returns a response "
            "containing the validation context and submitted body. Only status and body bytes "
            "are selected."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/how-to/custom-request-and-route.md:81-100 "
            "shows accessing Request.body() after request validation fails. Its included "
            "docs_src/custom_request_and_route/tutorial002_py310.py:9-29 and upstream "
            "test_tutorial002.py source evidence the custom handler path. The independent "
            "source-wave-b case exercises that wrapper/error/body interaction with separately "
            "authored input and observes http.status plus http.body.bytes."
        ),
    ),
    (_PAGE, "custom-apiroute-class-in-a-router"): _workflow(
        "Custom `APIRoute` class in a router { #custom-apiroute-class-in-a-router }",
        101,
        109,
        _ROUTER_CLASS,
        ["fastapi.docs.custom-request-route.router-class-hook-20261015"],
        ["get-router-route"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        (
            "The selected GET reaches a route registered on an APIRouter with its own custom "
            "APIRoute subclass and compares status, ordered headers, and body bytes. The "
            "workload's fixed marker header makes wrapper execution observable; the "
            "time-dependent X-Response-Time value and duration in the tutorial are not claimed."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/how-to/custom-request-and-route.md:101-109 "
            "sets APIRouter.route_class and describes the extra X-Response-Time response "
            "header. The included tutorial003_py310.py:8-39 and test_tutorial003.py provide "
            "source evidence. The independent custom-request-route-sections-review-20261015 "
            "input installs a separate APIRoute subclass on an APIRouter; its stable response "
            "marker is selected through http.headers.ordered along with status and body bytes. "
            "This establishes route-class hook execution without asserting the tutorial's "
            "dynamic timing value or treating the example as a benchmark."
        ),
    ),
}
