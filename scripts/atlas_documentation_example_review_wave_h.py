"""Reviewed source-to-input links for Wave H FastAPI documentation examples."""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(recipe: str, *case_ids: str, selectors: list[str]) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": list(case_ids),
        "observation_selectors": sorted(selectors),
    }


def _text(*parts: str) -> str:
    return " ".join(parts)


def _review(
    rationale: str,
    spans: list[dict[str, object]],
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "rationale": rationale,
        "supporting_sources": spans,
        "workflow_cases": cases,
    }


HTTP = ["http.body.bytes", "http.status"]
OPENAPI_PATHS = ["http.status", "openapi.paths"]


DOC_EXAMPLE_CITATION_WAVE_H = {
    "docs_src/behind_a_proxy/tutorial001_01_py310.py": _review(
        _text(
            "This file defines one GET route that returns a list.",
            "The independent GET samples route status/body with different list values;",
            "proxy root-path handling is not claimed.",
        ),
        [
            _span(
                "docs_src/behind_a_proxy/tutorial001_01_py310.py",
                6,
                8,
                "GET route and returned list",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.proxy-items-route",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/bigger_applications/app_an_py310/dependencies.py": _review(
        _text(
            "These functions read query/header tokens.",
            "Independent item/admin requests supply valid values and sample extraction/invocation;",
            "rejection details are not claimed.",
        ),
        [
            _span(
                "docs_src/bigger_applications/app_an_py310/dependencies.py",
                6,
                13,
                "header and query token dependencies",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.items-router",
                "fastapi.documentation-example.wave-h.bigger-applications.admin-router",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/bigger_applications/app_an_py310/internal/admin.py": _review(
        _text(
            "The example registers an admin POST route on an APIRouter.",
            "The independent request samples dispatch/status/body; OpenAPI selects",
            "its operation path.",
            "The tutorial response literal is not claimed.",
        ),
        [
            _span(
                "docs_src/bigger_applications/app_an_py310/internal/admin.py",
                6,
                8,
                "admin POST route",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.admin-router",
                selectors=HTTP,
            ),
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.openapi-projection",
                selectors=OPENAPI_PATHS,
            ),
        ],
    ),
    "docs_src/bigger_applications/app_an_py310/main.py": _review(
        _text(
            "The app includes routers with application/router dependencies and metadata.",
            "Independent requests sample router dispatch and OpenAPI operation metadata;",
            "other routes and response literals are not claimed.",
        ),
        [
            _span(
                "docs_src/bigger_applications/app_an_py310/main.py",
                7,
                18,
                "dependencies and router inclusion",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.users-router",
                "fastapi.documentation-example.wave-h.bigger-applications.items-router",
                "fastapi.documentation-example.wave-h.bigger-applications.admin-router",
                selectors=HTTP,
            ),
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.openapi-projection",
                selectors=OPENAPI_PATHS,
            ),
        ],
    ),
    "docs_src/bigger_applications/app_an_py310/routers/items.py": _review(
        _text(
            "The router declares a prefix, dependency, tags, response metadata, and GET routes.",
            "The independent item request samples valid dispatch and OpenAPI response metadata;",
            "update-item branches are not claimed.",
        ),
        [
            _span(
                "docs_src/bigger_applications/app_an_py310/routers/items.py",
                5,
                25,
                "item router metadata and GET routes",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.items-router",
                selectors=HTTP,
            ),
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.openapi-projection",
                selectors=OPENAPI_PATHS,
            ),
        ],
    ),
    "docs_src/bigger_applications/app_an_py310/routers/users.py": _review(
        _text(
            "The router registers user-list, current-user, and username routes.",
            "The independent request samples current-user dispatch and its OpenAPI tag;",
            "other route outputs are not claimed.",
        ),
        [
            _span(
                "docs_src/bigger_applications/app_an_py310/routers/users.py",
                6,
                18,
                "user router route declarations",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.users-router",
                selectors=HTTP,
            ),
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.bigger-applications.openapi-projection",
                selectors=OPENAPI_PATHS,
            ),
        ],
    ),
    "docs_src/dependencies/tutorial003_py310.py": _review(
        _text(
            "The endpoint passes a callable class to Depends and reads its query values.",
            "The independent route samples callable-class dependency resolution only;",
            "item values and response literals are not claimed.",
        ),
        [
            _span(
                "docs_src/dependencies/tutorial003_py310.py",
                9,
                22,
                "callable dependency class and route",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.dependencies.callable-class",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/dependencies/tutorial003_an_py310.py": _review(
        _text(
            "The Annotated variant passes a callable class to Depends.",
            "The independent route samples equivalent resolution; Any annotation and item values",
            "are not claimed.",
        ),
        [
            _span(
                "docs_src/dependencies/tutorial003_an_py310.py",
                11,
                25,
                "annotated callable dependency and route",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.dependencies.callable-class",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/dependencies/tutorial004_an_py310.py": _review(
        _text(
            "The typed parameter uses Depends() to infer CommonQueryParams.",
            "The independent route samples inference/query extraction with different values;",
            "response literals are not claimed.",
        ),
        [
            _span(
                "docs_src/dependencies/tutorial004_an_py310.py",
                11,
                24,
                "typed class dependency inferred by Depends()",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.dependencies.inferred-class",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/settings/app01_py310/main.py": _review(
        _text(
            "The route returns configured values as JSON.",
            "The independent route samples FastAPI dictionary serialization only;",
            "BaseSettings loading and environment handling are not claimed.",
        ),
        [_span("docs_src/settings/app01_py310/main.py", 5, 14, "settings-backed info route")],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.settings.global-projection",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/settings/app03_an_py310/main.py": _review(
        _text(
            "The route injects settings from a dependency and returns selected values.",
            "The independent route samples dependency result injection and JSON serialization;",
            "settings parsing and lru_cache behavior are not claimed.",
        ),
        [
            _span(
                "docs_src/settings/app03_an_py310/main.py",
                8,
                22,
                "cached settings dependency and route",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.settings.dependency-projection",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/settings/app03_py310/main.py": _review(
        _text(
            "The route injects settings with Depends and returns selected values.",
            "The independent route samples dependency result injection and JSON serialization;",
            "settings parsing and lru_cache behavior are not claimed.",
        ),
        [
            _span(
                "docs_src/settings/app03_py310/main.py", 7, 21, "settings dependency and info route"
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.settings.dependency-projection",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/settings/tutorial001_py310.py": _review(
        _text(
            "The app constructs settings and returns selected values from an info route.",
            "The independent route samples FastAPI response serialization only;",
            "BaseSettings construction and environment sources are not claimed.",
        ),
        [
            _span(
                "docs_src/settings/tutorial001_py310.py",
                5,
                21,
                "settings declaration and info route",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.settings.global-projection",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/custom_request_and_route/tutorial003_py310.py": _review(
        _text(
            "TimedRoute wraps a router handler and adds a response header after dispatch.",
            "The independent route samples wrapped dispatch/status/body; duration, prints,",
            "and header value are not claimed.",
        ),
        [
            _span(
                "docs_src/custom_request_and_route/tutorial003_py310.py",
                8,
                39,
                "TimedRoute and included router",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.custom-route.timed-dispatch",
                selectors=HTTP,
            )
        ],
    ),
    "docs_src/websockets_/tutorial001_py310.py": _review(
        _text(
            "The endpoint accepts a WebSocket, receives text, and sends a derived message.",
            "The independent session samples event order and echo behavior with different text;",
            "tutorial wording is not claimed.",
        ),
        [
            _span(
                "docs_src/websockets_/tutorial001_py310.py",
                46,
                51,
                "WebSocket accept/receive/send loop",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.websockets.echo",
                selectors=["websocket.event_order", "websocket.messages"],
            )
        ],
    ),
    "docs_src/frontend/tutorial003_py310.py": _review(
        _text(
            "The example mounts a frontend directory at the root with an explicit 404 fallback.",
            "The independent request samples a different fallback file's status/body only;",
            "static asset contents are not claimed.",
        ),
        [
            _span(
                "docs_src/frontend/tutorial003_py310.py",
                3,
                5,
                "frontend mount and explicit fallback",
            )
        ],
        [
            _case(
                "documentation-example-review-wave-h.yaml",
                "fastapi.documentation-example.wave-h.frontend.explicit-404",
                selectors=HTTP,
            )
        ],
    ),
}


DOC_EXAMPLE_EXCLUSION_WAVE_H = {
    "docs_src/async_tests/app_a_py310/test_main.py": _text(
        "Lines 1-14 are a pytest/HTTPX async test using ASGITransport and response assertions.",
        "This is test harness code and defines no FastAPI runtime application behavior.",
    ),
    "docs_src/generate_clients/tutorial004_py310.py": _text(
        "Lines 1-15 read OpenAPI JSON, rewrite operationId strings, and write JSON.",
        "This standalone post-processor is not FastAPI runtime behavior.",
    ),
    "docs_src/settings/app01_py310/config.py": _text(
        "Lines 1-10 define a Pydantic BaseSettings class and instance only.",
        "The file has no FastAPI application, route, dependency, or request handling.",
    ),
    "docs_src/settings/app02_an_py310/config.py": _text(
        "Lines 1-7 define an Annotated Pydantic BaseSettings model only.",
        "The file contains no FastAPI runtime application behavior.",
    ),
    "docs_src/settings/app03_an_py310/config.py": _text(
        "Lines 1-9 define Pydantic settings and env_file configuration only.",
        "Settings parsing is outside FastAPI runtime behavior.",
    ),
    "docs_src/settings/app03_py310/config.py": _text(
        "Lines 1-9 define Pydantic settings and env_file configuration only.",
        "Settings parsing is outside FastAPI runtime behavior.",
    ),
}
