"""Reviewed partial mappings for custom-docs and frontend examples in Wave J.

The mappings were checked against FastAPI 0.141.1 source. Existing independent
workflow cases sample only the cited behavior and selectors; they do not claim
the complete tutorial examples or their documentation pages.
"""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(
    recipe: str,
    case_ids: list[str],
    selectors: list[str],
) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": case_ids,
        "observation_selectors": sorted(selectors),
    }


def _review(
    rationale: str,
    spans: list[dict[str, object]],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {"rationale": rationale, "supporting_sources": spans, "workflow_cases": cases}


_HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]
_HTTP_RESPONSE = ["http.body.bytes", "http.headers.ordered", "http.status"]


DOC_EXAMPLE_CITATION_WAVE_J = {
    "docs_src/configure_swagger_ui/tutorial002_py310.py": _review(
        (
            "The example supplies a nested syntaxHighlight theme parameter. The independent "
            "case uses a different nested theme value and observes the Swagger UI response "
            "status/body. It samples this configuration path only; the obsidian theme value, "
            "tutorial route, and response literal are not claimed."
        ),
        [
            _span(
                "docs_src/configure_swagger_ui/tutorial002_py310.py",
                3,
                3,
                "nested Swagger UI syntaxHighlight theme parameter",
            ),
        ],
        [
            _case(
                "atlas-openapi-swagger-parameters-interface-review.yaml",
                ["fastapi.atlas-openapi-tutorial.nested-theme-configuration"],
                _HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/configure_swagger_ui/tutorial003_py310.py": _review(
        (
            "The example sets deepLinking to false. The independent case exercises that "
            "parameter through a different mounted app and observes the Swagger UI response "
            "status/body. It samples this configuration path only; the tutorial route and "
            "response literal are not claimed."
        ),
        [
            _span(
                "docs_src/configure_swagger_ui/tutorial003_py310.py",
                3,
                3,
                "Swagger UI deepLinking parameter override",
            ),
        ],
        [
            _case(
                "atlas-openapi-swagger-parameters-interface-review.yaml",
                ["fastapi.atlas-openapi-tutorial.default-parameter-override"],
                _HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/custom_docs_ui/tutorial002_py310.py": _review(
        (
            "This example defines several custom docs routes and mounts local assets. The "
            "independent case directly returns get_swagger_ui_oauth2_redirect_html() from a "
            "separately named route and observes response status, headers, and body. This "
            "supports that helper response only; custom Swagger/ReDoc URLs, local static "
            "assets, disabled generated docs, and the other routes are not claimed."
        ),
        [
            _span(
                "docs_src/custom_docs_ui/tutorial002_py310.py",
                25,
                27,
                "route returning the Swagger UI OAuth2 redirect HTML helper",
            )
        ],
        [
            _case(
                "openapi-docs.yaml",
                [
                    "fastapi.openapi.tutorial-custom-docs-ui-tutorial002.swagger-ui-oauth2-redirect-html"
                ],
                _HTTP_RESPONSE,
            )
        ],
    ),
    "docs_src/frontend/tutorial001_py310.py": _review(
        (
            "The example registers a frontend at the app root. The independent workflow also "
            "registers a root frontend and observes selected response status/body values, but "
            "configures an explicit index fallback and adds other routes. It samples root "
            "frontend registration and dispatch only; the default fallback policy, dist files, "
            "and tutorial route contents are not claimed."
        ),
        [
            _span(
                "docs_src/frontend/tutorial001_py310.py",
                5,
                5,
                "root frontend registration",
            )
        ],
        [
            _case(
                "frontend-fallback-routing-source-review.yaml",
                ["fastapi.frontend.fallback-routing-surface"],
                _HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/frontend/tutorial004_py310.py": _review(
        (
            "The example registers an index-fallback frontend on an APIRouter and includes "
            "that router under /app. The independent workflow exercises the same router "
            "frontend and include-router prefix composition with different files and an "
            "additional authentication dependency, observing selected response status/body "
            "values. It samples route composition and fallback dispatch only; authentication "
            "behavior and tutorial file contents are not claimed."
        ),
        [
            _span(
                "docs_src/frontend/tutorial004_py310.py",
                6,
                7,
                "router frontend with index fallback included under an app prefix",
            )
        ],
        [
            _case(
                "frontend-fallback-routing-source-review.yaml",
                ["fastapi.frontend.fallback-routing-surface"],
                _HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/frontend/tutorial005_py310.py": _review(
        (
            "The example explicitly disables frontend fallback with fallback=None. The "
            "independent case makes a request beneath another frontend configured with "
            "fallback=None and observes response status/body, sampling missing-path behavior "
            "without a fallback. Its directory, prefix, and response bytes differ from the "
            "tutorial."
        ),
        [
            _span(
                "docs_src/frontend/tutorial005_py310.py",
                5,
                5,
                "frontend registration with fallback explicitly disabled",
            )
        ],
        [
            _case(
                "frontend-fallback-routing-source-review.yaml",
                ["fastapi.frontend.fallback-routing-surface"],
                _HTTP_BODY_STATUS,
            )
        ],
    ),
    "docs_src/frontend/tutorial006_py310.py": _review(
        (
            "The example sets check_dir=False on frontend registration. The independent "
            "construction case uses a nonexistent directory, observes successful app "
            "construction, then observes the deferred ASGI application exception on request. "
            "This samples deferred directory checking for a missing path only; the tutorial's "
            "dist directory, its files, and its request response are not claimed."
        ),
        [
            _span(
                "docs_src/frontend/tutorial006_py310.py",
                5,
                5,
                "frontend registration with directory checking deferred",
            )
        ],
        [
            _case(
                "frontend-fallback-routing-source-review.yaml",
                ["fastapi.frontend.configuration.check-dir-false-defers-check"],
                [
                    "asgi.application_error.exception",
                    "construction.exception_class",
                    "construction.exception_message",
                    "construction.outcome",
                ],
            )
        ],
    ),
}
