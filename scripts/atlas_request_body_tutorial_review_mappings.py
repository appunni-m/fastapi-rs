"""Function-level source review for FastAPI's request-body tutorial tests.

This sidecar links only the two assigned test directories to independent,
input-only ASGI cases. It is review evidence, not a support claim or parity
result. Original FastAPI remains source-oracle/development material only.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
RECIPE_PATH = "tests/fixtures/input-recipes/parity/request-body-tutorial-source-review-2026.yaml"
WORKLOAD_PATH = "tests/fixtures/workloads/request_body_tutorial_source_review.py"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "pinned source oracle and development evidence only",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole selected generic request, response, and TestClient contract",
    },
    "starlette-rs": {
        "version": "0.1.0",
        "commit": "baea19981ba3119d362be8c3a1b0913e4824313e",
        "role": "implements the separate Starlette 1.6.0 contract",
    },
    "python": {
        "minimum": ">=3.10",
        "oracle": "CPython 3.12.13",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "public model validation and schema semantics",
    },
}

OWNER_BOUNDARIES = {
    "fastapi_source": (
        "FastAPI 0.141.1 is isolated source-oracle/development material; the target has zero FastAPI runtime dependency or import."
    ),
    "fastapi_control_flow": (
        "fastapi-rs/ owns FastAPI request-body selection and parsing integration, body-field composition, request validation and error projection, route control flow, and OpenAPI requestBody projection."
    ),
    "python_facade": (
        "fastapi-rs-py/ contains direct native re-exports and literal __all__ only; it contains no helpers, body parsing, validation, routing, response, or fallback control flow."
    ),
    "starlette_generic_contract": (
        "Starlette 1.6.0 is the sole generic Request, Response, and TestClient contract; Starlette-RS implements that contract. FastAPI owns its body and route integration edges."
    ),
    "pydantic": (
        "Pydantic 2.13.4 owns public model field validation, scalar coercion, and model JSON Schema semantics; FastAPI owns endpoint/body integration and OpenAPI requestBody assembly."
    ),
}

COMPATIBILITY_GATES = (
    "The source checkout identity is FastAPI 0.141.1 at the pinned commit, with Starlette 1.6.0 as the sole generic-framework oracle and Pydantic 2.13.4 for model semantics.",
    "The upstream functions use Starlette TestClient. These direct-ASGI inputs do not test HTTPX/TestClient request encoding, response wrappers, or transport behavior; those remain Starlette-RS-owned.",
    "HTTP tests compare status plus raw response bytes in the workflow, while the upstream assertions generally compare parsed response JSON. Raw-byte identity is an additional observation and is not claimed by the source tests.",
    "Each source OpenAPI function asserts its full tutorial-app snapshot. The independent app selects only requestBody paths and component schemas; full document metadata, operation identifiers, and exact source-app snapshots remain gated.",
    "The independent workload uses new routes and values. Multi-body tutorial 003, 004, and 005 cases include separate default-value and Annotated declarations in each case.",
    "test_other_exceptions is excluded because its only stimulus replaces the process-wide json.loads callable with a test-only side effect; it does not describe a request-reachable public input contract.",
    "This review performs static source, schema, and link checks only. No oracle or target workload was executed, and no parity or compatibility result is claimed.",
)

__all__ = [
    "COMPATIBILITY_GATES",
    "EXPECTED_TEST_FUNCTIONS",
    "FUNCTION_DENOMINATORS",
    "MAPPED_CASE_COUNT",
    "MODULE_COUNT",
    "OWNER_BOUNDARIES",
    "REQUEST_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS",
    "SOURCE_BACKED_EXCLUSION_COUNT",
    "SOURCE_IDENTITIES",
    "TOTAL_FUNCTION_COUNT",
    "validate_request_body_tutorial_review_mappings",
]


EXPECTED_TEST_FUNCTIONS: dict[str, tuple[str, ...]] = {
    "tests/test_tutorial/test_body/test_tutorial001.py": (
        "test_body_float",
        "test_post_with_str_float",
        "test_post_with_str_float_description",
        "test_post_with_str_float_description_tax",
        "test_post_with_only_name",
        "test_post_with_only_name_price",
        "test_post_with_no_data",
        "test_post_with_none",
        "test_post_broken_body",
        "test_post_form_for_json",
        "test_explicit_content_type",
        "test_geo_json",
        "test_no_content_type_json",
        "test_wrong_headers",
        "test_other_exceptions",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body/test_tutorial002.py": (
        "test_post_with_tax",
        "test_post_without_tax",
        "test_post_with_no_data",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body/test_tutorial003.py": (
        "test_put_all",
        "test_put_only_required",
        "test_put_with_no_data",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body/test_tutorial004.py": (
        "test_put_all",
        "test_put_only_required",
        "test_put_with_no_data",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body_multiple_params/test_tutorial001.py": (
        "test_post_body_q_bar_content",
        "test_post_no_body_q_bar",
        "test_post_no_body",
        "test_post_id_foo",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body_multiple_params/test_tutorial002.py": (
        "test_post_all",
        "test_post_required",
        "test_post_no_body",
        "test_post_no_item",
        "test_post_no_user",
        "test_post_missing_required_field_in_item",
        "test_post_missing_required_field_in_user",
        "test_post_id_foo",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body_multiple_params/test_tutorial003.py": (
        "test_post_body_valid",
        "test_post_body_no_data",
        "test_post_body_empty_list",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body_multiple_params/test_tutorial004.py": (
        "test_put_all",
        "test_put_only_required",
        "test_put_missing_body",
        "test_put_empty_body",
        "test_put_invalid_importance",
        "test_openapi_schema",
    ),
    "tests/test_tutorial/test_body_multiple_params/test_tutorial005.py": (
        "test_post_all",
        "test_post_required",
        "test_post_no_body",
        "test_post_like_not_embedded",
        "test_post_missing_required_field_in_item",
        "test_openapi_schema",
    ),
}

MODULE_COUNT = len(EXPECTED_TEST_FUNCTIONS)
FUNCTION_DENOMINATORS = {path: len(names) for path, names in EXPECTED_TEST_FUNCTIONS.items()}
TOTAL_FUNCTION_COUNT = sum(FUNCTION_DENOMINATORS.values())
SOURCE_BACKED_EXCLUSION_COUNT = 1
MAPPED_CASE_COUNT = TOTAL_FUNCTION_COUNT - SOURCE_BACKED_EXCLUSION_COUNT

_BODY_SOURCE = (
    {
        "path": "fastapi/routing.py",
        "start_line": 425,
        "end_line": 473,
        "role": "FastAPI reads request bytes, selects JSON decoding by content type, and turns decoding failures into request errors",
    },
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 951,
        "end_line": 998,
        "role": "FastAPI validates one request body field or extracts and validates multiple embedded body fields",
    },
    {
        "path": "fastapi/routing.py",
        "start_line": 751,
        "end_line": 755,
        "role": "FastAPI raises RequestValidationError when request body or dependency validation returns errors",
    },
)
_MULTI_BODY_SOURCE = (
    {
        "path": "fastapi/dependencies/utils.py",
        "start_line": 1001,
        "end_line": 1048,
        "role": "FastAPI composes multiple body parameters into one embedded body field and determines its requiredness",
    },
)
_OPENAPI_SOURCE = (
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 231,
        "end_line": 263,
        "role": "FastAPI derives requestBody requiredness, media type, and Pydantic field schema",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 331,
        "end_line": 385,
        "role": "FastAPI assembles operation path/query parameters and requestBody metadata",
    },
    {
        "path": "fastapi/openapi/utils.py",
        "start_line": 585,
        "end_line": 647,
        "role": "FastAPI generates the OpenAPI document and component definitions from routes",
    },
)
_STARLETTE_SOURCE = (
    {
        "path": "starlette/requests.py",
        "start_line": 234,
        "end_line": 266,
        "role": "Starlette 1.6.0 owns generic request-body streaming, buffering, and JSON decoding",
    },
    {
        "path": "starlette/responses.py",
        "start_line": 35,
        "end_line": 81,
        "role": "Starlette 1.6.0 owns generic response body rendering and header initialization",
    },
    {
        "path": "starlette/testclient.py",
        "start_line": 225,
        "end_line": 370,
        "role": "Starlette 1.6.0 TestClient owns generic HTTP request transport and response capture",
    },
)


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_span(test_path: str, function_name: str) -> dict[str, Any]:
    source_path = FASTAPI_ROOT / test_path
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    start_line = min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)])
    return _source(
        test_path,
        start_line,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test function {function_name} and its asserted observations",
    )


def _case_id(test_path: str, function_name: str) -> str:
    group = "body" if "/test_body/" in test_path else "body-multiple-params"
    filename = Path(test_path).stem.removeprefix("test_")
    return f"fastapi.request-body-tutorial.{group}.{filename}.{function_name.replace('_', '-')}"


def _action_ids(test_path: str, function_name: str) -> list[str]:
    if function_name == "test_openapi_schema":
        return ["openapi"]
    if (
        test_path.endswith("test_body/test_tutorial001.py")
        and function_name == "test_wrong_headers"
    ):
        return ["text-plain", "json-sequence", "unknown-media-type"]
    if test_path.endswith("test_body/test_tutorial002.py") and function_name in {
        "test_post_with_tax",
        "test_post_without_tax",
    }:
        return ["string-price", "number-price"]
    if "/test_body_multiple_params/" in test_path and Path(test_path).stem in {
        "test_tutorial003",
        "test_tutorial004",
        "test_tutorial005",
    }:
        return ["default-declaration", "annotated-declaration"]
    return ["request"]


def _selectors(test_path: str, function_name: str) -> list[str]:
    if function_name == "test_openapi_schema":
        return [
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ]
    if test_path.endswith("test_body/test_tutorial001.py") and function_name in {
        "test_explicit_content_type",
        "test_geo_json",
        "test_no_content_type_json",
    }:
        return ["http.status"]
    return ["http.body.bytes", "http.status"]


def _rationale(test_path: str, function_name: str) -> str:
    if function_name == "test_openapi_schema":
        return (
            "The upstream function asserts its tutorial app's complete OpenAPI snapshot. "
            "This case selects requestBody path values and component schemas from an "
            "independently named workload; the full snapshot is outside the observation."
        )
    if function_name == "test_wrong_headers":
        return (
            "The upstream function sends the same JSON bytes under three non-JSON media "
            "types. The independent case keeps those as three separately observed ASGI actions."
        )
    if function_name in {"test_post_with_tax", "test_post_without_tax"}:
        return (
            "The upstream function is parametrized with string and numeric price inputs. "
            "The independent case preserves both input forms with new values and observes "
            "each response separately."
        )
    if "/test_body_multiple_params/" in test_path and Path(test_path).stem in {
        "test_tutorial003",
        "test_tutorial004",
        "test_tutorial005",
    }:
        return (
            "The upstream fixture runs this function against both default-value and "
            "Annotated declarations. The independent case exercises both declarations "
            "through separate route actions."
        )
    if function_name in {
        "test_post_broken_body",
        "test_post_form_for_json",
        "test_no_content_type_json",
    }:
        return (
            "The upstream function exercises FastAPI's request-body content decoding or "
            "body validation branch; the case sends an independently authored ASGI body."
        )
    return (
        "The upstream function asserts a request status and parsed response value. The "
        "case sends an independent body, omission, or path-value stimulus and observes "
        "status plus raw response bytes."
    )


def _docs_sources(test_path: str) -> tuple[dict[str, Any], ...]:
    path = Path(test_path)
    tutorial = path.stem.removeprefix("test_")
    if "test_body_multiple_params" in path.parts:
        directory = "body_multiple_params"
        variants = [f"docs_src/{directory}/{tutorial}_py310.py"]
        if tutorial in {"tutorial003", "tutorial004", "tutorial005"}:
            variants.append(f"docs_src/{directory}/{tutorial}_an_py310.py")
    else:
        directory = "body"
        variants = [f"docs_src/{directory}/{tutorial}_py310.py"]
    sources = []
    for relative_path in variants:
        source_file = FASTAPI_ROOT / relative_path
        line_count = len(source_file.read_text(encoding="utf-8").splitlines())
        sources.append(
            _source(
                relative_path,
                1,
                line_count,
                "pinned FastAPI tutorial fixture supplying the model, endpoint signature, and response behavior",
            )
        )
    return tuple(sources)


def _function_review(test_path: str, function_name: str) -> dict[str, Any]:
    if function_name == "test_other_exceptions":
        return {
            "review_status": "reviewed_excluded",
            "feature_ids": [],
            "observation_selectors": [],
            "exclusion_reason": (
                "The test patches json.loads to raise an arbitrary Exception and then "
                "asserts FastAPI's fallback 400 response. The injected process-wide "
                "monkeypatch is not an ASGI request input and is test-only behavior, so "
                "this function has no independent input recipe case."
            ),
            "supporting_sources": [_test_span(test_path, function_name)],
        }

    selectors = _selectors(test_path, function_name)
    action_ids = _action_ids(test_path, function_name)
    case_id = _case_id(test_path, function_name)
    return {
        "review_status": "reviewed_partial",
        "feature_ids": (
            ["openapi-docs", "request-validation"]
            if function_name == "test_openapi_schema"
            else ["request-validation", "response-serialization"]
        ),
        "observation_selectors": selectors,
        "rationale": _rationale(test_path, function_name),
        "replace_features": True,
        "contract_gate": (
            "Partial: request inputs and selected public observations are mapped; the "
            "full source assertion or generic TestClient boundary is not claimed."
        ),
        "workflow_cases": [
            {
                "recipe_path": RECIPE_PATH,
                "case_id": case_id,
                "action_ids": action_ids,
                "observation_selectors": selectors,
            }
        ],
        "stimulus_notes": (
            "The recipe contains independent request stimuli and observation selectors "
            "only. It stores no expected output and does not copy the upstream test body."
        ),
        "supporting_sources": [
            _test_span(test_path, function_name),
            *_docs_sources(test_path),
            *_BODY_SOURCE,
            *(_MULTI_BODY_SOURCE if "/test_body_multiple_params/" in test_path else ()),
            *(_OPENAPI_SOURCE if function_name == "test_openapi_schema" else ()),
            *_STARLETTE_SOURCE,
        ],
    }


def _module_review(test_path: str, test_functions: tuple[str, ...]) -> dict[str, Any]:
    functions = {
        function_name: _function_review(test_path, function_name)
        for function_name in test_functions
    }
    links: dict[tuple[str, str], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for function_review in functions.values():
        for link in function_review.get("workflow_cases", []):
            links.setdefault((link["recipe_path"], link["case_id"]), link)
        for source in function_review["supporting_sources"]:
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources.setdefault(key, source)
    source_path = FASTAPI_ROOT / test_path
    module_lines = len(source_path.read_text(encoding="utf-8").splitlines())
    sources.setdefault(
        (test_path, 1, module_lines, "assigned upstream test module"),
        _source(test_path, 1, module_lines, "assigned upstream test module"),
    )
    return {
        "review_status": "reviewed_partial",
        "rationale": (
            "Function-level review of the assigned FastAPI 0.141.1 request-body tutorial "
            "module. Every top-level test function has a case link or source-backed exclusion."
        ),
        "functions": functions,
        "workflow_cases": list(links.values()),
        "supporting_sources": list(sources.values()),
        "module_observation_selectors": sorted(
            {
                selector
                for review in functions.values()
                for selector in review["observation_selectors"]
            }
        ),
        "stimulus_notes": (
            "Independent input-only request-body cases. FastAPI request/body control flow "
            "is Rust-owned; generic Starlette behavior is Starlette-RS-owned; Pydantic "
            "model semantics remain Pydantic 2.13.4-owned."
        ),
    }


REQUEST_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    test_path: _module_review(test_path, test_functions)
    for test_path, test_functions in EXPECTED_TEST_FUNCTIONS.items()
}


def _selectors_from_case(case: dict[str, Any], action_ids: list[str]) -> list[str]:
    selected: set[str] = set()
    actions = {action["action_id"]: action for action in case.get("actions", [])}
    for action_id in action_ids:
        action = actions[action_id]
        for observation in action.get("observations", []):
            if observation.get("kind") == "http_response":
                selectors = set(observation.get("selectors", []))
                if "status" in selectors:
                    selected.add("http.status")
                if "body" in selectors:
                    selected.add("http.body.bytes")
            elif observation.get("kind") == "openapi":
                selected.add("openapi.document")
                for pointer in observation.get("json_pointers", []):
                    if pointer.startswith("/paths/"):
                        selected.add("openapi.paths")
                    if "/requestBody" in pointer:
                        selected.add("openapi.request_schema")
                    if pointer.startswith("/components/schemas"):
                        selected.add("openapi.request_schema")
    return sorted(selected)


def _top_level_test_names(test_path: str) -> tuple[str, ...]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return tuple(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    )


def _contains_expected_output(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            "expected" in str(key).lower() or _contains_expected_output(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_expected_output(child) for child in value)
    return False


def validate_request_body_tutorial_review_mappings() -> list[str]:
    """Run static source, recipe-schema, and mapping-link checks only."""

    errors: list[str] = []
    actual_test_paths = {
        str(path.relative_to(FASTAPI_ROOT)).replace("\\", "/")
        for relative_dir in (
            "tests/test_tutorial/test_body",
            "tests/test_tutorial/test_body_multiple_params",
        )
        for path in sorted((FASTAPI_ROOT / relative_dir).glob("test_*.py"))
        if path.name != "__init__.py"
    }
    if actual_test_paths != set(EXPECTED_TEST_FUNCTIONS):
        errors.append("assigned test modules differ from the reviewed 9-module scope")

    actual_function_count = 0
    for test_path, expected_names in EXPECTED_TEST_FUNCTIONS.items():
        actual_names = _top_level_test_names(test_path)
        actual_function_count += len(actual_names)
        if actual_names != expected_names:
            errors.append(f"top-level test function inventory changed for {test_path}")
        module = REQUEST_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS[test_path]
        if set(module["functions"]) != set(actual_names):
            errors.append(f"function mapping denominator mismatch for {test_path}")

    if actual_function_count != TOTAL_FUNCTION_COUNT:
        errors.append(
            f"expected {TOTAL_FUNCTION_COUNT} top-level functions, found {actual_function_count}"
        )

    recipe_file = PROJECT_ROOT / RECIPE_PATH
    try:
        recipe = yaml.safe_load(recipe_file.read_text(encoding="utf-8"))
    except Exception as exc:  # static loader diagnostics are part of the check
        return [f"could not load request-body tutorial recipe: {exc}"]
    if not isinstance(recipe, dict) or recipe.get("schema") != "fastapi-rs/python-asgi-workflow@2":
        errors.append("recipe does not use the Python ASGI workflow v2 schema")
        return errors
    workflow_schema = json.loads(
        (PROJECT_ROOT / "tests/fixtures/schemas/python-asgi-workflow-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    schema_errors = sorted(
        Draft202012Validator(workflow_schema).iter_errors(recipe),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )
    for error in schema_errors:
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append(f"recipe JSON Schema violation at {pointer}: {error.message}")
    workload = recipe.get("workload", {})
    if workload.get("file") != WORKLOAD_PATH or workload.get("factory") != "create_app":
        errors.append("recipe does not link to the unique request-body workload factory")
    if workload.get("instantiate_per_case") is not True:
        errors.append("each request-body source-review case must instantiate independently")
    try:
        ast.parse((PROJECT_ROOT / WORKLOAD_PATH).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"workload source is not valid Python syntax: {exc}")
    if _contains_expected_output(recipe):
        errors.append("input recipe contains an expected-output field")

    recipe_cases = recipe.get("cases", [])
    cases_by_id = {case.get("case_id"): case for case in recipe_cases}
    if len(cases_by_id) != len(recipe_cases):
        errors.append("recipe contains duplicate case IDs")
    if len(recipe_cases) != MAPPED_CASE_COUNT:
        errors.append(f"expected {MAPPED_CASE_COUNT} independent cases, found {len(recipe_cases)}")

    linked_case_ids: list[str] = []
    excluded_count = 0
    for test_path, module in REQUEST_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS.items():
        for function_name, review in module["functions"].items():
            if review["review_status"] == "reviewed_excluded":
                excluded_count += 1
                if review.get("workflow_cases") or not review.get("exclusion_reason"):
                    errors.append(
                        f"invalid source-backed exclusion for {test_path}::{function_name}"
                    )
                continue
            links = review.get("workflow_cases", [])
            if len(links) != 1:
                errors.append(f"expected one independent case for {test_path}::{function_name}")
                continue
            link = links[0]
            case_id = link["case_id"]
            linked_case_ids.append(case_id)
            case = cases_by_id.get(case_id)
            if case is None:
                errors.append(f"missing recipe case {case_id}")
                continue
            if link["recipe_path"] != RECIPE_PATH:
                errors.append(f"wrong recipe path for {test_path}::{function_name}")
            if case.get("source_evidence") != [{"path": test_path, "kind": "upstream_test"}]:
                errors.append(f"case source evidence does not match {test_path}::{function_name}")
            if len(set(link["action_ids"])) != len(link["action_ids"]):
                errors.append(f"duplicate action link for {case_id}")
            if any(
                action_id not in {action.get("action_id") for action in case.get("actions", [])}
                for action_id in link["action_ids"]
            ):
                errors.append(f"case action link is incomplete for {case_id}")
            elif _selectors_from_case(case, link["action_ids"]) != link["observation_selectors"]:
                errors.append(f"observation selector link differs for {case_id}")
            if link["observation_selectors"] != review["observation_selectors"]:
                errors.append(f"function selector mapping differs for {test_path}::{function_name}")

    if len(set(linked_case_ids)) != len(linked_case_ids):
        errors.append("a recipe case is linked by more than one top-level test function")
    if set(linked_case_ids) != set(cases_by_id):
        errors.append("recipe cases and mapped test functions do not have one-to-one links")
    if excluded_count != SOURCE_BACKED_EXCLUSION_COUNT:
        errors.append(
            f"expected {SOURCE_BACKED_EXCLUSION_COUNT} source-backed exclusions, found {excluded_count}"
        )
    return errors


if __name__ == "__main__":
    problems = validate_request_body_tutorial_review_mappings()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)
    print(
        "static request-body tutorial review links valid: "
        f"{MODULE_COUNT} modules, {TOTAL_FUNCTION_COUNT} functions, "
        f"{MAPPED_CASE_COUNT} input cases, {SOURCE_BACKED_EXCLUSION_COUNT} exclusion"
    )
