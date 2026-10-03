"""Reviewed partial mappings from documentation examples to independent inputs."""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {
        "path": path,
        "start_line": start,
        "end_line": end,
        "role": role,
    }


def _cases(recipe: str, case_ids: list[str], selectors: list[str]) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": sorted(case_ids),
        "observation_selectors": sorted(selectors),
    }


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


DOC_EXAMPLE_CITATION_WAVE_D = {
    "docs_src/advanced_middleware/tutorial002_py310.py": _review(
        (
            "The example installs TrustedHostMiddleware with an exact host and wildcard "
            "subdomain. The independent cases exercise accepted exact/wildcard hosts and "
            "rejection of an unlisted host. They use separate routes and do not claim the "
            "example route or response body."
        ),
        [
            _span(
                "docs_src/advanced_middleware/tutorial002_py310.py",
                6,
                13,
                "TrustedHost middleware policy and protected route",
            )
        ],
        [
            _cases(
                "middleware.yaml",
                [
                    "fastapi.middleware.trusted-host-wildcard-allowed",
                    "fastapi.middleware.trusted-host-rejected",
                ],
                ["http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/advanced_middleware/tutorial003_py310.py": _review(
        (
            "The example installs GZipMiddleware with a compression threshold and level. "
            "The independent case exercises gzip response handling on a large response "
            "with a different threshold; the documented threshold boundary, small "
            "response, and compressed body bytes are not claimed."
        ),
        [
            _span(
                "docs_src/advanced_middleware/tutorial003_py310.py",
                6,
                11,
                "GZip middleware configuration and route",
            )
        ],
        [
            _cases(
                "middleware-proxy-advanced-source-review.yaml",
                ["fastapi.middleware-proxy.gzip-response"],
                ["http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/async_tests/app_a_py310/main.py": _review(
        (
            "The documented app registers an async route returning JSON. The independent "
            "ASGI case requests a separately named async route and observes status and "
            "body; it does not exercise AsyncClient, ASGITransport, or the test harness "
            "in the adjacent example."
        ),
        [
            _span(
                "docs_src/async_tests/app_a_py310/main.py",
                6,
                8,
                "documented async route and JSON result",
            )
        ],
        [
            _cases(
                "async_tests.yaml",
                ["fastapi.docs.async-tests.async-route"],
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/behind_a_proxy/tutorial001_py310.py": _review(
        (
            "The example returns the request scope root_path. The independent workflow "
            "supplies a non-empty ASGI root_path and observes the returned value. "
            "Proxy-header processing, URL generation, and the example's route and "
            "response literals are not covered."
        ),
        [
            _span(
                "docs_src/behind_a_proxy/tutorial001_py310.py",
                6,
                8,
                "documented request root_path observation",
            )
        ],
        [
            _cases(
                "middleware-proxy-root-path-source-review.yaml",
                ["fastapi.middleware-proxy.proxy-client-root-path"],
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/configure_swagger_ui/tutorial001_py310.py": _review(
        (
            "The example configures Swagger UI and registers a parameterized route. The "
            "independent case configures other Swagger UI parameters and observes the "
            "docs response; syntaxHighlight=False and the tutorial route are not claimed."
        ),
        [
            _span(
                "docs_src/configure_swagger_ui/tutorial001_py310.py",
                3,
                8,
                "Swagger UI configuration and documented route",
            )
        ],
        [
            _cases(
                "docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.how-to-configure-swagger-ui.configured-swagger"],
                ["docs.response.status", "http.body.bytes", "http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/custom_request_and_route/tutorial002_py310.py": _review(
        (
            "The example installs an APIRoute subclass that converts request validation "
            "errors into HTTPException details containing the original body. Independent "
            "cases exercise a custom route's validation-error context and a valid "
            "request. They do not establish every malformed-body or error-detail branch."
        ),
        [
            _span(
                "docs_src/custom_request_and_route/tutorial002_py310.py",
                8,
                20,
                "custom validation-error route handler",
            ),
            _span(
                "docs_src/custom_request_and_route/tutorial002_py310.py",
                23,
                29,
                "custom route installation and request endpoint",
            ),
        ],
        [
            _cases(
                "source-wave-b-custom-routes.yaml",
                [
                    "fastapi.source-wave-b.custom-route.validation-context",
                    "fastapi.source-wave-b.custom-route.valid-request",
                ],
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/dataclasses_/tutorial002_py310.py": _review(
        (
            "The example uses a dataclass response model and returns a dictionary. The "
            "independent workflow exercises dataclass response serialization and schema "
            "generation using a constructed dataclass instance; dictionary-to-dataclass "
            "validation, optional values, and the source defaults remain uncovered."
        ),
        [
            _span(
                "docs_src/dataclasses_/tutorial002_py310.py",
                6,
                12,
                "documented response dataclass fields",
            ),
            _span(
                "docs_src/dataclasses_/tutorial002_py310.py",
                18,
                25,
                "response-model route and returned dictionary",
            ),
        ],
        [
            _cases(
                "dataclasses.yaml",
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
            )
        ],
    ),
    "docs_src/dependencies/tutorial001_py310.py": _review(
        (
            "The example injects function-based shared query parameters into two routes. "
            "Independent cases exercise dependency defaults, supplied query values, and "
            "their OpenAPI projection. Their limit default and data differ from the "
            "documented example."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial001_py310.py",
                6,
                17,
                "shared dependency and two injected routes",
            )
        ],
        [
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                [
                    "fastapi.dependencies.tutorial-review.basic-defaults",
                    "fastapi.dependencies.tutorial-review.basic-partial-query",
                ],
                ["http.body.bytes", "http.status"],
            ),
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                ["fastapi.dependencies.tutorial-review.openapi-projection"],
                ["http.status", "openapi.paths"],
            ),
        ],
    ),
    "docs_src/dependencies/tutorial002_py310.py": _review(
        (
            "The example injects CommonQueryParams and applies its query values to an "
            "in-memory list. Independent cases exercise class-based dependency expansion, "
            "query overrides, slicing, and an OpenAPI projection with different names and "
            "data; the source limit default is not distinguished by the fixture dataset."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial002_py310.py",
                9,
                23,
                "class dependency and paginated route",
            )
        ],
        [
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                [
                    "fastapi.dependencies.tutorial-review.catalog-default-window",
                    "fastapi.dependencies.tutorial-review.catalog-custom-window",
                ],
                ["http.body.bytes", "http.status"],
            ),
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                ["fastapi.dependencies.tutorial-review.openapi-projection"],
                ["http.status", "openapi.paths"],
            ),
        ],
    ),
    "docs_src/dependencies/tutorial004_py310.py": _review(
        (
            "The example uses Depends() to infer a class dependency. The independent "
            "OpenAPI case projects a class dependency's query parameters, but uses the "
            "Annotated form and does not exercise runtime construction or the documented "
            "defaults."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial004_py310.py",
                9,
                22,
                "inferred class dependency and route",
            )
        ],
        [
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                ["fastapi.dependencies.tutorial-review.openapi-projection"],
                ["http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/dependencies/tutorial006_an_py310.py": _review(
        (
            "The example attaches two header-check dependencies to one path operation. "
            "The independent case samples dependency registration, a separate case "
            "observes the operation parameters in OpenAPI, and neither covers the two "
            "documented header error branches."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial006_an_py310.py",
                8,
                21,
                "two header dependencies and dependent route",
            )
        ],
        [
            _cases(
                "docs-dependencies-security.yaml",
                [
                    "fastapi.docs.documentation-wave.dependencies-security.path-operation-dependencies"
                ],
                ["http.body.bytes", "http.headers.ordered", "http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/dependencies/tutorial006_py310.py": _review(
        (
            "The example attaches two required Header dependencies to one route. "
            "Independent cases exercise missing and invalid values and the OpenAPI "
            "parameter projection with different names, values, and error details."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial006_py310.py",
                6,
                19,
                "two required header dependencies and route",
            )
        ],
        [
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                [
                    "fastapi.dependencies.tutorial-review.headers-missing",
                    "fastapi.dependencies.tutorial-review.headers-invalid-token",
                    "fastapi.dependencies.tutorial-review.headers-invalid-key",
                ],
                ["http.body.bytes", "http.status"],
            ),
            _cases(
                "dependency-tutorial-review-upstream.yaml",
                ["fastapi.dependencies.tutorial-review.openapi-projection"],
                ["http.status", "openapi.paths"],
            ),
        ],
    ),
    "docs_src/dependencies/tutorial008_py310.py": _review(
        (
            "The example defines a nested async yield-dependency chain with ordered "
            "cleanup. The independent workflow exercises nested yield dependencies and "
            "cleanup events through a test resource chain; external database/resource "
            "effects are not covered."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial008_py310.py",
                4,
                25,
                "nested async yield dependencies and cleanup",
            )
        ],
        [
            _cases(
                "dependency-yield-tutorials-upstream.yaml",
                ["fastapi.dependencies.tutorial008.async-yield-chain-default"],
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/dependencies/tutorial010_py310.py": _review(
        (
            "The example yields a database session from a synchronous context manager. "
            "The independent case exercises a context manager around a yielded dependency "
            "and observes cleanup using a fixture resource rather than DBSession."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial010_py310.py",
                1,
                14,
                "synchronous context manager and yielded session",
            )
        ],
        [
            _cases(
                "dependency-yield-tutorials-upstream.yaml",
                ["fastapi.dependencies.tutorial010.context-manager-in-yield-dependency"],
                ["http.body.bytes", "http.status"],
            )
        ],
    ),
    "docs_src/dependencies/tutorial012_an_py310.py": _review(
        (
            "The example installs two global Annotated header dependencies across two "
            "routes. Independent cases exercise missing, invalid, and valid headers on "
            "separate routes and project the parameters into OpenAPI; values and response "
            "payloads differ."
        ),
        [
            _span(
                "docs_src/dependencies/tutorial012_an_py310.py",
                6,
                27,
                "global header dependencies and two routes",
            )
        ],
        [
            _cases(
                "dependency-tutorial012-annotated-upstream.yaml",
                ["fastapi.dependencies.tutorial012.global-headers-annotated"],
                ["http.body.bytes", "http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/extending_openapi/tutorial001_py310.py": _review(
        (
            "The example supplies a custom OpenAPI builder and adds an x-logo field to "
            "the result. The independent case exercises custom OpenAPI assignment and an "
            "Info extension, but uses different schema values and does not establish this "
            "example's cache behavior."
        ),
        [
            _span(
                "docs_src/extending_openapi/tutorial001_py310.py",
                12,
                26,
                "custom OpenAPI builder, extension, and cache",
            ),
            _span(
                "docs_src/extending_openapi/tutorial001_py310.py",
                29,
                29,
                "custom OpenAPI assignment",
            ),
        ],
        [
            _cases(
                "docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.how-to-extending-openapi.custom-openapi-fields"],
                ["http.status", "openapi.document"],
            )
        ],
    ),
    "docs_src/generate_clients/tutorial003_py310.py": _review(
        (
            "The example derives operation IDs from route tags and names. The independent "
            "case reproduces and observes that ID function in OpenAPI; client code "
            "generation itself is not observed."
        ),
        [
            _span(
                "docs_src/generate_clients/tutorial003_py310.py",
                6,
                10,
                "tag/name operation-ID function and app configuration",
            ),
            _span(
                "docs_src/generate_clients/tutorial003_py310.py",
                27,
                42,
                "tagged route declarations",
            ),
        ],
        [
            _cases(
                "generate-clients-tutorial003-upstream.yaml",
                [
                    "fastapi.test.test-tutorial-test-generate-clients-test-tutorial003.custom-operation-ids"
                ],
                ["openapi.paths"],
            )
        ],
    ),
    "docs_src/header_param_models/tutorial001_py310.py": _review(
        (
            "The example injects a Pydantic model from request headers and exposes it in "
            "a route. The independent workflow covers model-based Header extraction and "
            "its parameter schema using different field names and explicit aliases; "
            "implicit underscore conversion and source defaults are not covered."
        ),
        [
            _span(
                "docs_src/header_param_models/tutorial001_py310.py",
                7,
                16,
                "header model and endpoint",
            )
        ],
        [
            _cases(
                "docs-request-schema.yaml",
                ["fastapi.docs.request-schema.tutorial-header-param-models.header-model"],
                ["http.body.bytes", "http.headers.ordered", "http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/metadata/tutorial002_py310.py": _review(
        (
            "The example changes the OpenAPI URL and registers an items route. "
            "Independent cases exercise a route response and retrieve OpenAPI from the "
            "configured location; they do not claim the example payload literals."
        ),
        [
            _span(
                "docs_src/metadata/tutorial002_py310.py",
                3,
                8,
                "configured OpenAPI location and route",
            )
        ],
        [
            _cases(
                "metadata-tutorial-items-upstream.yaml",
                ["fastapi.test.test-tutorial-test-metadata-shared-items.test-items-foo"],
                ["http.body.bytes", "http.status"],
            ),
            _cases(
                "metadata-tutorial002-upstream.yaml",
                ["fastapi.test.test-tutorial-test-metadata-test-tutorial002.test-openapi-schema"],
                ["docs.response.status", "openapi.document"],
            ),
        ],
    ),
    "docs_src/metadata/tutorial003_py310.py": _review(
        (
            "The example changes the docs URL and disables ReDoc while registering an "
            "items route. Independent cases exercise route output and the configured "
            "documentation endpoints; the example's route literals are not claimed."
        ),
        [
            _span(
                "docs_src/metadata/tutorial003_py310.py",
                3,
                8,
                "configured documentation URLs and route",
            )
        ],
        [
            _cases(
                "metadata-tutorial-items-upstream.yaml",
                ["fastapi.test.test-tutorial-test-metadata-shared-items.test-items-foo"],
                ["http.body.bytes", "http.status"],
            ),
            _cases(
                "metadata-tutorial003-upstream.yaml",
                [
                    "fastapi.test.test-tutorial-test-metadata-test-tutorial003.test-swagger-ui-custom-url"
                ],
                ["http.body.bytes", "http.status"],
            ),
        ],
    ),
    "docs_src/middleware/tutorial001_py310.py": _review(
        (
            "The example installs decorator middleware that measures elapsed time and "
            "sets X-Process-Time. The independent case exercises decorator middleware and "
            "observes its response header with a fixed marker; the timing measurement "
            "itself is not covered."
        ),
        [
            _span(
                "docs_src/middleware/tutorial001_py310.py",
                8,
                14,
                "decorator middleware and response header",
            )
        ],
        [
            _cases(
                "middleware-proxy-static-settings-source-review.yaml",
                ["fastapi.middleware-proxy.decorator-middleware"],
                ["http.headers.ordered", "http.status"],
            )
        ],
    ),
    "docs_src/openapi_callbacks/tutorial001_py310.py": _review(
        (
            "The example registers an APIRouter callback on an operation. The independent "
            "case exercises callback route registration and its OpenAPI projection; "
            "callback delivery and the source's invoice schema and expression are not "
            "covered."
        ),
        [
            _span(
                "docs_src/openapi_callbacks/tutorial001_py310.py",
                23,
                34,
                "callback route and operation registration",
            )
        ],
        [
            _cases(
                "docs-openapi-interface.yaml",
                ["fastapi.docs.openapi-interface.advanced-openapi-callbacks.callback-operation"],
                ["http.body.bytes", "http.headers.ordered", "http.status", "openapi.paths"],
            )
        ],
    ),
    "docs_src/path_operation_advanced_configuration/tutorial001_py310.py": _review(
        (
            "The example supplies an explicit operation_id. The independent tutorial case "
            "matches its route behavior and ID projection; separate schema cases exercise "
            "the same option with fixture-specific routes and IDs."
        ),
        [
            _span(
                "docs_src/path_operation_advanced_configuration/tutorial001_py310.py",
                6,
                8,
                "explicit operation ID and route",
            )
        ],
        [
            _cases(
                "path-operation-advanced-configurations-tutorial001-upstream.yaml",
                ["fastapi.path-operation-advanced-configurations.tutorial001"],
                ["http.body.bytes", "http.status", "openapi.paths"],
            ),
            _cases(
                "path-operation-parameter-tutorials-test_path_operation_advanced_configurations_test_tutorial001_test_openapi_schema.yaml",
                [
                    "fastapi.path-operation-parameter-tutorials.test-path-operation-advanced-configurations-test-tutorial001-test-openapi-schema"
                ],
                ["openapi.paths"],
            ),
            _cases(
                "docs-openapi-schema.yaml",
                ["fastapi.docs.documentation-wave.openapi-schema.advanced-operation-configuration"],
                ["openapi.paths"],
            ),
        ],
    ),
    "docs_src/path_operation_advanced_configuration/tutorial005_py310.py": _review(
        (
            "The example sets an openapi_extra extension and returns a route response. "
            "The independent tutorial case reproduces the extension value and response; "
            "its schema behavior does not establish other extension names or values."
        ),
        [
            _span(
                "docs_src/path_operation_advanced_configuration/tutorial005_py310.py",
                6,
                8,
                "openapi_extra option and route",
            )
        ],
        [
            _cases(
                "path-operation-advanced-configurations-tutorial005-upstream.yaml",
                ["fastapi.path-operation-advanced-configurations.tutorial005"],
                ["http.body.bytes", "http.status", "openapi.paths"],
            )
        ],
    ),
}
