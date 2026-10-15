"""Additive per-case workflow links for the path-parameter doc examples.

Source rationale and supporting spans remain owned by the existing reviewed
documentation-example mappings. Each row here adds only one recipe/case link
and the selectors projected from that exact case.
"""

DOC_EXAMPLE_WORKFLOW_CASE_EXTENSIONS_PATH_1016 = {
    "docs_src/path_params/tutorial001_py310.py": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.basic-string",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params/tutorial002_py310.py": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.integer-path",
            "observation_selectors": ["http.body.bytes", "http.status"],
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.integer-path-validation",
            "observation_selectors": ["http.body.bytes", "http.status"],
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.documentation",
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
        },
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.redoc",
            "observation_selectors": ["http.body.bytes", "http.status"],
        },
    ],
    "docs_src/path_params/tutorial003_py310.py": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.route-order",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params/tutorial003b_py310.py": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.route-order",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params/tutorial004_py310.py": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.path-converter",
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
        }
    ],
    "docs_src/path_params/tutorial005_py310.py": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml",
            "case_id": "fastapi.docs.path-params-1016.enum-model",
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial001_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.metadata",
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "openapi.document",
                "openapi.paths",
            ],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial002_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.parameter-order",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial002_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.parameter-order",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial003_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.keyword-only-order",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial003_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.keyword-only-order",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial004_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.ge-boundary",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial005_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.gt-le-boundary",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
    "docs_src/path_params_numeric_validations/tutorial006_an_py310.py": [
        {
            "recipe_path": (
                "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"
            ),
            "case_id": "fastapi.docs.path-params-numeric-1016.float-query-boundary",
            "observation_selectors": ["http.body.bytes", "http.status"],
        }
    ],
}
