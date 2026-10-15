"""Reviewed section mappings for FastAPI's sub-applications documentation."""

_PAGE = "advanced/sub-applications.md"
_ROUTES = "tests/fixtures/input-recipes/parity/sub-applications-routes-review-20261015.yaml"
_MOUNT = "tests/fixtures/input-recipes/parity/sub_applications.yaml"


def _workflow(heading, start, end, recipe, case, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": [case],
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


_HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]
_HTTP_RESPONSE = ["http.body.bytes", "http.headers.ordered", "http.status"]
_ROUTES_CASE = "fastapi.docs.sub-applications.route-declarations-review"
_DOCS_CASE = "fastapi.docs.sub-applications.built-in-routes-root-path"
_MOUNTED_DOCS_CASE = "fastapi.docs.sub-applications.mount-and-own-openapi"


DOC_SECTION_CASE_MAPPINGS_SUB_APPLICATIONS_20261015 = {
    (_PAGE, "sub-applications-mounts"): _excluded(
        "Sub Applications - Mounts { #sub-applications-mounts }",
        1,
        67,
        (
            "The page title and opening sentence introduce the tutorial's independent-app "
            "topic. Observable mount, route, docs-UI, and root_path behavior is separated "
            "under the anchored sections below."
        ),
        (
            "The page-level heading spans the full tutorial and combines route dispatch, "
            "OpenAPI separation, docs URLs, a CLI invocation, and root_path details. The "
            "narrower source sections below map the ASGI-visible slices individually "
            "(../fastapi/docs/en/docs/advanced/sub-applications.md:1-67)."
        ),
    ),
    (_PAGE, "mounting-a-fastapi-application"): _workflow(
        "Mounting a **FastAPI** application { #mounting-a-fastapi-application }",
        5,
        67,
        _ROUTES,
        _ROUTES_CASE,
        ["top-level-route", "mounted-route"],
        _HTTP_BODY_STATUS,
        (
            "The selected requests exercise one documented top-level path and one path "
            "under its `/subapi` mount, comparing status and response bytes. This is a "
            "partial route sample; docs UIs, CLI startup, OpenAPI details, and nested "
            "mounts are not claimed."
        ),
        (
            "The pinned example declares the main `/app` route, a `/sub` route on a second "
            "FastAPI app, and mounts it at `/subapi` "
            "(../fastapi/docs/en/docs/advanced/sub-applications.md:5-30; "
            "../fastapi/docs_src/sub_applications/tutorial001_py310.py:3-19). The upstream "
            "test sends `/app` and `/subapi/sub` and asserts the corresponding responses "
            "(../fastapi/tests/test_tutorial/test_sub_applications/test_tutorial001.py:9-18); "
            "the selected independent actions reproduce those two routes."
        ),
    ),
    (_PAGE, "top-level-application"): _workflow(
        "Top-level application { #top-level-application }",
        9,
        14,
        _ROUTES,
        _ROUTES_CASE,
        ["top-level-route"],
        _HTTP_BODY_STATUS,
        (
            "The selected request calls the documented `/app` route and compares status "
            "and response bytes. It samples this one top-level route only."
        ),
        (
            "FastAPI's pinned example declares `GET /app` and returns the main-app message "
            "(../fastapi/docs_src/sub_applications/tutorial001_py310.py:3-8); the upstream "
            "test requests `/app` and asserts status and JSON body "
            "(../fastapi/tests/test_tutorial/test_sub_applications/test_tutorial001.py:9-12). "
            "The independent `main-http` action uses the same request and response input."
        ),
    ),
    (_PAGE, "sub-application"): _workflow(
        "Sub-application { #sub-application }",
        15,
        22,
        _ROUTES,
        _ROUTES_CASE,
        ["mounted-route"],
        _HTTP_BODY_STATUS,
        (
            "The selected request reaches the documented sub-application route through "
            "`/subapi/sub`, then compares status and response bytes. Other sub-app "
            "configurations and nested mounts are not claimed."
        ),
        (
            "The pinned example creates a second FastAPI app with `GET /sub` "
            "(../fastapi/docs_src/sub_applications/tutorial001_py310.py:11-16), and its test "
            "requests `/subapi/sub` and asserts the returned sub-app message "
            "(../fastapi/tests/test_tutorial/test_sub_applications/test_tutorial001.py:15-18). "
            "The independent `sub-http` action uses that mounted request and response."
        ),
    ),
    (_PAGE, "mount-the-sub-application"): _workflow(
        "Mount the sub-application { #mount-the-sub-application }",
        23,
        30,
        _ROUTES,
        _ROUTES_CASE,
        ["mounted-route"],
        _HTTP_BODY_STATUS,
        (
            "The selected `/subapi/sub` request observes dispatch through the documented "
            "`/subapi` mount to the sub-application's `/sub` route. It does not claim "
            "other mount paths or methods."
        ),
        (
            "The pinned section names the `/subapi` mount and its code include contains "
            '`app.mount("/subapi", subapi)` '
            "(../fastapi/docs/en/docs/advanced/sub-applications.md:23-30; "
            "../fastapi/docs_src/sub_applications/tutorial001_py310.py:19). The upstream "
            "test sends `/subapi/sub` and checks the sub-app response "
            "(../fastapi/tests/test_tutorial/test_sub_applications/test_tutorial001.py:15-18); "
            "Starlette 1.6.0 owns the generic Mount route dispatch."
        ),
    ),
    (_PAGE, "check-the-automatic-api-docs"): _workflow(
        "Check the automatic API docs { #check-the-automatic-api-docs }",
        31,
        58,
        _MOUNT,
        _DOCS_CASE,
        ["main-docs-root-path", "mounted-docs-root-path"],
        _HTTP_RESPONSE,
        (
            "The selected actions request the main and mounted Swagger UI endpoints and "
            "compare each HTTP response. This samples the two UI routes under an external "
            "`/gateway` root_path; it does not claim that a browser loads their OpenAPI "
            "documents or renders the operation lists."
        ),
        (
            "The pinned section points to `/docs` and `/subapi/docs` for the main and "
            "mounted applications respectively "
            "(../fastapi/docs/en/docs/advanced/sub-applications.md:45-55). The selected "
            "independent actions request those same paths and observe status, ordered "
            "headers, and body bytes; the extra external root_path is explicit in the "
            "input and is not attributed to this section."
        ),
    ),
    (_PAGE, "technical-details-root-path"): _workflow(
        "Technical Details: `root_path` { #technical-details-root-path }",
        59,
        67,
        _MOUNT,
        _MOUNTED_DOCS_CASE,
        ["mounted-docs-ui"],
        _HTTP_RESPONSE,
        (
            "The selected `/subapi/docs` response observes the docs UI generated beneath "
            "one mount, including its mount-prefixed OpenAPI URL. It samples one mounted "
            "app and does not claim nested mounts or arbitrary root_path combinations."
        ),
        (
            "FastAPI builds the Swagger UI OpenAPI URL from request-scope `root_path` "
            "(../fastapi/fastapi/applications.py:1123-1137). Starlette 1.6.0's Mount "
            "appends its matched mount path to the child scope's root_path "
            "(../starlette/starlette/routing.py:394-424). The selected input requests the "
            "mounted docs endpoint and compares its HTTP status, headers, and HTML bytes, "
            "which expose that prefixed docs URL."
        ),
    ),
}
