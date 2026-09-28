"""Source-reviewed mappings for query and header parameter tutorial tests.

The recipes are input-only candidates. They contain request stimuli and public
observation selectors, with no expected outputs and no claim of live parity.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
STARLETTE_ROOT = PROJECT_ROOT.parent / "starlette"
RECIPE_ROOT = PROJECT_ROOT / "tests/fixtures/input-recipes/parity"
WORKLOAD_PATH = "tests/fixtures/workloads/query_header_parameter_tutorial_review.py"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "source-oracle and development-only dependency",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic request, response, and TestClient contract via Starlette-RS",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "field/model validation and schema generation where applicable",
    },
}

TARGET_OWNERSHIP = {
    "fastapi_control_flow": "Rust owns FastAPI behavior and control flow.",
    "python_runtime": (
        "The fastapi Python runtime exposes direct native re-exports and literal "
        "__all__ only; it contains no helpers, functions, branches, loops, or fallback behavior."
    ),
    "starlette_contract": (
        "Starlette 1.6.0 is the sole generic request/response/TestClient contract, "
        "provided through Starlette-RS."
    ),
    "pydantic_contract": (
        "Pydantic 2.13.4 owns field and model validation plus schema generation where "
        "applicable; Rust-owned FastAPI control flow classifies parameters, extracts "
        "values, and assembles request errors and OpenAPI operations."
    ),
}

HEADER_CLIENT_LIMITATION = (
    "The upstream header tests request /items through Starlette TestClient and follow "
    "the slash redirect to /items/. A single ASGI dispatch cannot represent that client "
    "redirect sequence, so these input-only cases dispatch directly to /items/ and do "
    "not claim coverage of redirect following. The explicit user-agent: testclient "
    "header represents TestClient's default request header where relevant."
)

_P = "tests/fixtures/input-recipes/parity/"


def _query_recipe(tutorial: str) -> str:
    return f"{_P}query-header-parameter-query-tutorial{tutorial}.yaml"


def _header_recipe(tutorial: str, form: str) -> str:
    return f"{_P}query-header-parameter-header-tutorial{tutorial}-{form}.yaml"


def _case(suffix: str, recipe: str, action_id: str) -> dict[str, str]:
    return {
        "case_id": f"fastapi.query-header-review.{suffix}",
        "recipe_path": recipe,
        "action_id": action_id,
    }


def _query_cases(tutorial: str, suffixes: tuple[str, ...]) -> list[dict[str, str]]:
    recipe = _query_recipe(tutorial)
    return [_case(f"query{tutorial}.{suffix}", recipe, "request") for suffix in suffixes]


def _header_cases(
    tutorial: str, forms: tuple[str, ...], suffixes: tuple[str, ...]
) -> list[dict[str, str]]:
    return [
        _case(
            f"header{tutorial}.{form}.{suffix}",
            _header_recipe(tutorial, form),
            suffix,
        )
        for form in forms
        for suffix in suffixes
    ]


def _header_openapi_cases(tutorial: str) -> list[dict[str, str]]:
    return [
        _case(
            f"header{tutorial}.{form}.openapi",
            _header_recipe(tutorial, form),
            "openapi",
        )
        for form in ("direct", "annotated")
    ]


_QUERY_MODULES: dict[str, dict[str, Any]] = {
    "test_tutorial001.py": {
        "tutorial": "001",
        "docs": ["docs_src/query_params/tutorial001_py310.py"],
        "functions": {
            "test_read_user_item": {
                "case_suffixes": (
                    "items-default",
                    "items-skip",
                    "items-skip-limit",
                ),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": (
                    "Covers default pagination and integer query coercion for skip/limit."
                ),
            },
            "test_openapi_schema": {
                "case_suffixes": ("openapi",),
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the complete serialized OpenAPI response and selected document sections.",
            },
        },
        "parameters": [
            {
                "name": "skip",
                "location": "query",
                "type": "integer",
                "alias": "skip",
                "required": False,
                "default": 0,
                "coercion": "query-string integer input",
            },
            {
                "name": "limit",
                "location": "query",
                "type": "integer",
                "alias": "limit",
                "required": False,
                "default": 10,
                "coercion": "query-string integer input",
            },
        ],
    },
    "test_tutorial002.py": {
        "tutorial": "002",
        "docs": ["docs_src/query_params/tutorial002_py310.py"],
        "functions": {
            "test_read_user_item": {
                "case_suffixes": ("item-without-query", "item-with-query"),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers a required path string and an omitted/present optional query string.",
            },
            "test_openapi_schema": {
                "case_suffixes": ("openapi",),
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the complete serialized OpenAPI response and selected document sections.",
            },
        },
        "parameters": [
            {
                "name": "item_id",
                "location": "path",
                "type": "string",
                "alias": "item_id",
                "required": True,
            },
            {
                "name": "q",
                "location": "query",
                "type": "string | null",
                "alias": "q",
                "required": False,
                "default": None,
            },
        ],
    },
    "test_tutorial003.py": {
        "tutorial": "003",
        "docs": ["docs_src/query_params/tutorial003_py310.py"],
        "functions": {
            "test_read_user_item": {
                "case_suffixes": (
                    "item-without-query",
                    "item-with-query",
                    "item-short",
                ),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers optional q and boolean short coercion from short=true.",
            },
            "test_openapi_schema": {
                "case_suffixes": ("openapi",),
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the complete serialized OpenAPI response and selected document sections.",
            },
        },
        "parameters": [
            {
                "name": "item_id",
                "location": "path",
                "type": "string",
                "alias": "item_id",
                "required": True,
            },
            {
                "name": "q",
                "location": "query",
                "type": "string | null",
                "alias": "q",
                "required": False,
                "default": None,
            },
            {
                "name": "short",
                "location": "query",
                "type": "boolean",
                "alias": "short",
                "required": False,
                "default": False,
                "coercion": "short=true is parsed as a boolean",
            },
        ],
    },
    "test_tutorial004.py": {
        "tutorial": "004",
        "docs": ["docs_src/query_params/tutorial004_py310.py"],
        "functions": {
            "test_read_user_item": {
                "case_suffixes": ("item-default", "item-with-query", "item-short"),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers integer path coercion, optional q, and boolean short coercion.",
            },
            "test_openapi_schema": {
                "case_suffixes": ("openapi",),
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the complete serialized OpenAPI response and selected document sections.",
            },
        },
        "parameters": [
            {
                "name": "user_id",
                "location": "path",
                "type": "integer",
                "alias": "user_id",
                "required": True,
                "coercion": "decimal path strings are parsed as integers",
            },
            {
                "name": "item_id",
                "location": "path",
                "type": "string",
                "alias": "item_id",
                "required": True,
            },
            {
                "name": "q",
                "location": "query",
                "type": "string | null",
                "alias": "q",
                "required": False,
                "default": None,
            },
            {
                "name": "short",
                "location": "query",
                "type": "boolean",
                "alias": "short",
                "required": False,
                "default": False,
                "coercion": "short=true is parsed as a boolean",
            },
        ],
    },
    "test_tutorial005.py": {
        "tutorial": "005",
        "docs": ["docs_src/query_params/tutorial005_py310.py"],
        "functions": {
            "test_foo_needy_very": {
                "case_suffixes": ("required-query-present",),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers a supplied required query string.",
            },
            "test_foo_no_needy": {
                "case_suffixes": ("required-query-missing",),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers the 422 validation response and query location for a missing required value.",
            },
            "test_openapi_schema": {
                "case_suffixes": ("openapi",),
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the complete serialized OpenAPI response and selected document sections.",
            },
        },
        "parameters": [
            {
                "name": "item_id",
                "location": "path",
                "type": "string",
                "alias": "item_id",
                "required": True,
            },
            {
                "name": "needy",
                "location": "query",
                "type": "string",
                "alias": "needy",
                "required": True,
            },
        ],
    },
    "test_tutorial006.py": {
        "tutorial": "006",
        "docs": ["docs_src/query_params/tutorial006_py310.py"],
        "functions": {
            "test_foo_needy_very": {
                "case_suffixes": ("required-query-present",),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers required needy, omitted integer default, and nullable integer default.",
            },
            "test_foo_no_needy": {
                "case_suffixes": ("required-query-missing-and-invalid-optional-integers",),
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": "Covers missing required needy and Pydantic integer parsing errors for skip/limit.",
            },
            "test_openapi_schema": {
                "case_suffixes": ("openapi",),
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the complete serialized OpenAPI response and selected document sections.",
            },
        },
        "parameters": [
            {
                "name": "item_id",
                "location": "path",
                "type": "string",
                "alias": "item_id",
                "required": True,
            },
            {
                "name": "needy",
                "location": "query",
                "type": "string",
                "alias": "needy",
                "required": True,
            },
            {
                "name": "skip",
                "location": "query",
                "type": "integer",
                "alias": "skip",
                "required": False,
                "default": 0,
                "coercion": "query-string integer; invalid strings produce a parsing error",
            },
            {
                "name": "limit",
                "location": "query",
                "type": "integer | null",
                "alias": "limit",
                "required": False,
                "default": None,
                "coercion": "query-string integer; invalid strings produce a parsing error",
            },
        ],
    },
}

_HEADER_MODULES: dict[str, dict[str, Any]] = {
    "test_tutorial001.py": {
        "tutorial": "001",
        "docs": {
            "direct": "docs_src/header_params/tutorial001_py310.py",
            "annotated": "docs_src/header_params/tutorial001_an_py310.py",
        },
        "request_case_suffixes": (
            "default-user-agent",
            "irrelevant-x-header",
            "user-agent-override",
        ),
        "functions": {
            "test": {
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": (
                    "Covers Header(default=None) and equivalent Annotated Header() input "
                    "forms, TestClient's default User-Agent, unrelated X-Header input, "
                    "and an explicit user-agent override."
                ),
            },
            "test_openapi_schema": {
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the aliased optional header parameter and the complete OpenAPI response.",
            },
        },
        "parameters": [
            {
                "name": "user_agent",
                "location": "header",
                "type": "string | null",
                "alias": "user-agent",
                "required": False,
                "default": None,
                "alias_rule": "default convert_underscores maps user_agent to user-agent",
            }
        ],
    },
    "test_tutorial002.py": {
        "tutorial": "002",
        "docs": {
            "direct": "docs_src/header_params/tutorial002_py310.py",
            "annotated": "docs_src/header_params/tutorial002_an_py310.py",
        },
        "request_case_suffixes": (
            "default-underscore-alias",
            "irrelevant-x-header",
            "underscore-alias",
            "hyphen-does-not-match-underscore-alias",
        ),
        "functions": {
            "test": {
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": (
                    "Covers convert_underscores=False for direct and Annotated forms: "
                    "strange_header is the accepted alias and strange-header does not match."
                ),
            },
            "test_openapi_schema": {
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the literal underscore header alias and complete OpenAPI response.",
            },
        },
        "parameters": [
            {
                "name": "strange_header",
                "location": "header",
                "type": "string | null",
                "alias": "strange_header",
                "required": False,
                "default": None,
                "alias_rule": "convert_underscores=False preserves the underscore in the alias",
            }
        ],
    },
    "test_tutorial003.py": {
        "tutorial": "003",
        "docs": {
            "direct": "docs_src/header_params/tutorial003_py310.py",
            "annotated": "docs_src/header_params/tutorial003_an_py310.py",
        },
        "request_case_suffixes": (
            "missing-list-header",
            "single-list-header-value",
            "repeated-list-header-values",
        ),
        "functions": {
            "test": {
                "selectors": ["http.status", "http.body.bytes"],
                "rationale": (
                    "Covers optional list-valued x-token header extraction with zero, one, "
                    "and repeated values in direct and Annotated forms."
                ),
            },
            "test_openapi_schema": {
                "selectors": [
                    "docs.response.body.bytes",
                    "docs.response.status",
                    "http.body.bytes",
                    "http.status",
                    "openapi.document",
                    "openapi.paths",
                ],
                "rationale": "Covers the optional array-of-strings header schema and complete OpenAPI response.",
            },
        },
        "parameters": [
            {
                "name": "x_token",
                "location": "header",
                "type": "array<string> | null",
                "alias": "x-token",
                "required": False,
                "default": None,
                "alias_rule": "default convert_underscores maps x_token to x-token",
                "coercion": "repeated x-token fields are collected in input order",
            }
        ],
    },
}


def _src_span(path: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    start_line = min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)])
    return {
        "path": path,
        "start_line": start_line,
        "end_line": node.end_lineno or node.lineno,
        "role": f"FastAPI 0.141.1 upstream test function {node.name}",
    }


def _test_spans(test_path: str) -> dict[str, dict[str, Any]]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    spans: dict[str, dict[str, Any]] = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != "test" and not node.name.startswith("test_"):
            continue
        spans[node.name] = _src_span(test_path, node)
    return spans


def _function_rows(test_path: str, module: dict[str, Any], kind: str) -> dict[str, Any]:
    tutorial = module["tutorial"]
    functions: dict[str, Any] = {}
    source_spans = _test_spans(test_path)
    for name, function in module["functions"].items():
        if kind == "query":
            recipe = _query_recipe(tutorial)
            cases = [
                _case(
                    f"query{tutorial}.{suffix}",
                    recipe,
                    "openapi" if suffix == "openapi" else "request",
                )
                for suffix in function["case_suffixes"]
            ]
        elif name == "test":
            cases = _header_cases(
                tutorial,
                ("direct", "annotated"),
                module["request_case_suffixes"],
            )
        else:
            cases = _header_openapi_cases(tutorial)
        functions[name] = {
            "source_span": source_spans[name],
            "mapping_status": "mapped-input-only",
            "workflow_cases": cases,
            "observation_selectors": function["selectors"],
            "rationale": function["rationale"],
            "coverage_notes": [
                "Input-only request and OpenAPI observations; no expected output is stored in the recipe.",
                *([HEADER_CLIENT_LIMITATION] if kind == "header" and name == "test" else []),
            ],
        }
    return functions


def build_review_mappings() -> dict[str, dict[str, Any]]:
    mappings: dict[str, dict[str, Any]] = {}
    for test_name, module in _QUERY_MODULES.items():
        test_path = f"tests/test_tutorial/test_query_params/{test_name}"
        mappings[test_path] = {
            "mapping_status": "mapped-input-only",
            "feature_ids": ["request.query.parameters", "openapi.parameters"],
            "source_test_path": test_path,
            "supporting_docs": module["docs"],
            "parameter_contracts": module["parameters"],
            "functions": _function_rows(test_path, module, "query"),
        }
    for test_name, module in _HEADER_MODULES.items():
        test_path = f"tests/test_tutorial/test_header_params/{test_name}"
        mappings[test_path] = {
            "mapping_status": "mapped-input-only",
            "feature_ids": ["request.header.parameters", "openapi.parameters"],
            "source_test_path": test_path,
            "supporting_docs": module["docs"],
            "parameter_contracts": module["parameters"],
            "functions": _function_rows(test_path, module, "header"),
        }
    return mappings


QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS = build_review_mappings()


def _recipe_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    recipe_names = [
        f"query-header-parameter-query-tutorial{tutorial}.yaml"
        for tutorial in _query_module_tutorials()
    ] + [
        f"query-header-parameter-header-tutorial{tutorial}-{form}.yaml"
        for tutorial in _header_module_tutorials()
        for form in ("direct", "annotated")
    ]
    for name in recipe_names:
        path = RECIPE_ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for case in data.get("cases", []):
            case_id = case["case_id"]
            if case_id in index:
                raise ValueError(f"duplicate recipe case ID {case_id}")
            index[case_id] = {
                "recipe_path": str(path.relative_to(PROJECT_ROOT)),
                "recipe": data,
                "case": case,
                "actions": {action["action_id"]: action for action in case.get("actions", [])},
            }
    return index


def _query_module_tutorials() -> tuple[str, ...]:
    return tuple(module["tutorial"] for module in _QUERY_MODULES.values())


def _header_module_tutorials() -> tuple[str, ...]:
    return tuple(module["tutorial"] for module in _HEADER_MODULES.values())


def _action_selectors(action: dict[str, Any]) -> set[str]:
    selected: set[str] = set()
    openapi_endpoint = action.get("scope", {}).get("path") == "/openapi.json"
    for observation in action.get("observations", []):
        if observation.get("kind") == "http_response":
            values = set(observation.get("selectors", []))
            if "status" in values:
                selected.add("http.status")
                if openapi_endpoint:
                    selected.add("docs.response.status")
            if "body" in values:
                selected.add("http.body.bytes")
                if openapi_endpoint:
                    selected.add("docs.response.body.bytes")
        elif observation.get("kind") == "openapi":
            for pointer in observation.get("json_pointers", []):
                if pointer.startswith("/paths/") or pointer == "/paths":
                    selected.update(("openapi.document", "openapi.paths"))
                else:
                    selected.add("openapi.document")
    return selected


def _scan_input_only(value: Any, location: str, errors: list[str]) -> None:
    forbidden = {
        "expected",
        "expected_output",
        "expected_outputs",
        "measurement",
        "measurements",
        "benchmark",
    }
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in forbidden:
                errors.append(f"non-input field {key!r} in {location}")
            _scan_input_only(item, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_input_only(item, f"{location}[{index}]", errors)


def _validate_source_identity(errors: list[str]) -> None:
    manifest = yaml.safe_load(
        (PROJECT_ROOT / "tests/fixtures/manifest.yaml").read_text(encoding="utf-8")
    )
    for name, source_root in (("fastapi", FASTAPI_ROOT), ("starlette", STARLETTE_ROOT)):
        actual_commit = subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        expected = SOURCE_IDENTITIES[name]
        selected = manifest["selected_contracts"][name]
        if actual_commit != expected["commit"] or selected.get("commit") != expected["commit"]:
            errors.append(f"pinned source identity mismatch for {name}")
        if selected.get("version") != expected["version"]:
            errors.append(f"manifest version mismatch for {name}")
    pydantic = manifest.get("selected_contracts", {}).get("pydantic", {})
    if pydantic.get("version") != SOURCE_IDENTITIES["pydantic"]["version"]:
        errors.append("manifest Pydantic version differs from reviewed identity")


def validate_query_header_parameter_tutorial_mappings() -> list[str]:
    errors: list[str] = []
    _validate_source_identity(errors)
    expected_modules = {
        f"tests/test_tutorial/test_query_params/{name}" for name in _QUERY_MODULES
    } | {f"tests/test_tutorial/test_header_params/{name}" for name in _HEADER_MODULES}
    actual_modules = {
        str(path.relative_to(FASTAPI_ROOT))
        for directory in (
            FASTAPI_ROOT / "tests/test_tutorial/test_query_params",
            FASTAPI_ROOT / "tests/test_tutorial/test_header_params",
        )
        for path in directory.glob("test_*.py")
        if path.name != "__init__.py"
    }
    if actual_modules != expected_modules:
        errors.append("source module set differs from the exact reviewed tutorial directories")
    if set(QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS) != expected_modules:
        errors.append("mapping denominator does not cover the exact reviewed source modules")

    try:
        recipe_index = _recipe_index()
    except (FileNotFoundError, KeyError, ValueError, yaml.YAMLError) as error:
        return [*errors, f"recipe index could not be loaded: {error}"]

    workload_ast = ast.parse((PROJECT_ROOT / WORKLOAD_PATH).read_text(encoding="utf-8"))
    workload_factories = {
        node.name
        for node in workload_ast.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    function_count = 0
    case_link_count = 0
    linked_case_actions: set[tuple[str, str]] = set()
    all_case_actions = {
        (case_id, action_id)
        for case_id, case_row in recipe_index.items()
        for action_id in case_row["actions"]
    }
    expected_recipe_names = {
        f"query-header-parameter-query-tutorial{tutorial}.yaml"
        for tutorial in _query_module_tutorials()
    } | {
        f"query-header-parameter-header-tutorial{tutorial}-{form}.yaml"
        for tutorial in _header_module_tutorials()
        for form in ("direct", "annotated")
    }
    for recipe_name in expected_recipe_names:
        path = RECIPE_ROOT / recipe_name
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("schema") != "fastapi-rs/python-asgi-workflow@2":
            errors.append(f"unsupported recipe schema in {recipe_name}")
        workload = data.get("workload", {})
        if workload.get("file") != WORKLOAD_PATH or not workload.get("instantiate_per_case"):
            errors.append(f"recipe does not use the isolated review workload in {recipe_name}")
        if workload.get("factory") not in workload_factories:
            errors.append(f"recipe factory is missing from workload: {recipe_name}")
        _scan_input_only(data, recipe_name, errors)
        for case in data.get("cases", []):
            for action in case.get("actions", []):
                scope = action.get("scope", {})
                if (
                    action.get("kind") != "http_request"
                    or scope.get("type") != "http"
                    or scope.get("method") != "GET"
                    or not isinstance(scope.get("path"), str)
                    or not isinstance(scope.get("query_string"), str)
                ):
                    errors.append(
                        f"invalid HTTP input action in {recipe_name}:{action.get('action_id')}"
                    )
                if not any(
                    observation.get("kind") == "http_response"
                    and {"status", "body"} <= set(observation.get("selectors", []))
                    for observation in action.get("observations", [])
                ):
                    errors.append(
                        f"missing public response selectors in {recipe_name}:{action.get('action_id')}"
                    )

    for test_path, module in QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS.items():
        source_spans = _test_spans(test_path)
        functions = module["functions"]
        if set(functions) != set(source_spans):
            errors.append(f"test function denominator mismatch for {test_path}")
        if module["mapping_status"] != "mapped-input-only":
            errors.append(f"unexpected module mapping status for {test_path}")
        for docs_path in (
            module["supporting_docs"].values()
            if isinstance(module["supporting_docs"], dict)
            else module["supporting_docs"]
        ):
            if not (FASTAPI_ROOT / docs_path).is_file():
                errors.append(f"missing supporting documentation source {docs_path}")
        source_test = (FASTAPI_ROOT / test_path).read_text(encoding="utf-8").splitlines()
        for name, function in functions.items():
            function_count += 1
            if function.get("source_span") != source_spans.get(name):
                errors.append(f"source span mismatch for {test_path}:{name}")
            span = function["source_span"]
            if not (1 <= span["start_line"] <= span["end_line"] <= len(source_test)):
                errors.append(f"source span outside test module for {test_path}:{name}")
            if function.get("mapping_status") == "source-backed-exclusion":
                if function.get("workflow_cases") or not function.get("exclusion_reason"):
                    errors.append(f"invalid source-backed exclusion {test_path}:{name}")
                continue
            if function.get("mapping_status") != "mapped-input-only":
                errors.append(f"unexpected function mapping status for {test_path}:{name}")
            if not function.get("workflow_cases"):
                errors.append(f"mapped function has no workflow cases for {test_path}:{name}")
                continue
            for workflow in function["workflow_cases"]:
                case_link_count += 1
                case_row = recipe_index.get(workflow["case_id"])
                if case_row is None:
                    errors.append(f"unknown case ID {workflow['case_id']}")
                    continue
                if workflow["recipe_path"] != case_row["recipe_path"]:
                    errors.append(f"recipe path mismatch for {workflow['case_id']}")
                case = case_row["case"]
                source_paths = {
                    source.get("path")
                    for source in case.get("source_evidence", [])
                    if source.get("kind") == "upstream_test"
                }
                if test_path not in source_paths:
                    errors.append(
                        f"recipe case omits upstream source evidence for {workflow['case_id']}"
                    )
                docs_paths = {
                    source.get("path")
                    for source in case.get("source_evidence", [])
                    if source.get("kind") == "upstream_documentation"
                }
                expected_docs = set(
                    module["supporting_docs"].values()
                    if isinstance(module["supporting_docs"], dict)
                    else module["supporting_docs"]
                )
                if len(docs_paths) != 1 or not docs_paths <= expected_docs:
                    errors.append(
                        f"recipe case has unexpected documentation evidence for {workflow['case_id']}"
                    )
                linked_case_action = (workflow["case_id"], workflow["action_id"])
                if linked_case_action in linked_case_actions:
                    errors.append(
                        f"case action is linked more than once: {workflow['case_id']}:{workflow['action_id']}"
                    )
                linked_case_actions.add(linked_case_action)
                action = case_row["actions"].get(workflow["action_id"])
                if action is None:
                    errors.append(
                        f"missing action for {workflow['case_id']}:{workflow['action_id']}"
                    )
                    continue
                if not set(function["observation_selectors"]) <= _action_selectors(action):
                    errors.append(
                        f"selector mismatch for {workflow['case_id']}:{workflow['action_id']}"
                    )

    if function_count != 20:
        errors.append(f"expected 20 top-level test functions, found {function_count}")
    if case_link_count != 47:
        errors.append(f"expected 47 function-to-case links, found {case_link_count}")
    if linked_case_actions != all_case_actions:
        errors.append("recipe action set differs from the function-to-case linkage set")
    return errors


if __name__ == "__main__":
    validation_errors = validate_query_header_parameter_tutorial_mappings()
    if validation_errors:
        raise SystemExit("\n".join(validation_errors))
    functions = sum(
        len(module["functions"])
        for module in QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS.values()
    )
    links = sum(
        len(function["workflow_cases"])
        for module in QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS.values()
        for function in module["functions"].values()
    )
    print(
        f"validated {len(QUERY_HEADER_PARAMETER_TUTORIAL_REVIEW_MAPPINGS)} exact tutorial modules, "
        f"{functions} top-level test functions, {links} function-to-case links, "
        "0 exclusions; recipes are input-only and parity remains unverified"
    )
