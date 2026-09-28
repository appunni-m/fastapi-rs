"""Source-reviewed input links for FastAPI's nested-body tutorial tests.

This module is atlas input only. It links pinned test functions to independent
ASGI stimuli and records the remaining partial gates; it makes no parity claim.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT.parent / "fastapi"

SOURCE_IDENTITY = {
    "fastapi_version": "0.141.1",
    "fastapi_commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "starlette_version": "1.6.0",
    "starlette_commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}

_HTTP = ["http.body.bytes", "http.status"]
_OPENAPI = ["openapi.document"]
_OPENAPI_PATHS = ["openapi.document", "openapi.paths"]
_CORNER = "tests/fixtures/input-recipes/parity/nested-body-corner-wave.yaml"
_PYDANTIC = "tests/fixtures/input-recipes/parity/pydantic-extra-type-body-wave.yaml"
_NESTED = "tests/fixtures/input-recipes/parity/nested-request-models-upstream.yaml"
_REQUEST_MODELS = "tests/fixtures/input-recipes/parity/request-models.yaml"
_REVIEW = "tests/fixtures/input-recipes/parity/nested-body-tutorial-review.yaml"


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
    return _source(
        test_path,
        node.lineno,
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test input and assertions for {function_name}",
    )


def _case(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
    }


def _review(
    test_path: str,
    function_name: str,
    feature_ids: list[str],
    rationale: str,
    contract_gate: str,
    links: list[dict[str, Any]],
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    selectors = sorted({selector for link in links for selector in link["observation_selectors"]})
    links_note = "; ".join(
        f"{link['recipe_path']}::{link['case_id']} actions "
        f"{', '.join(link['action_ids'])} ({', '.join(link['observation_selectors'])})"
        for link in links
    )
    return {
        "review_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": "Partial: " + contract_gate,
        "workflow_cases": links,
        "stimulus_notes": (
            "Input-only case links: " + links_note + ". The stimuli have no expected outputs."
        ),
        "supporting_sources": [_test_span(test_path, function_name), *sources],
    }


def _module(
    rationale: str,
    functions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    links: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    sources: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    for review in functions.values():
        for link in review["workflow_cases"]:
            key = (link["recipe_path"], link["case_id"], tuple(link["action_ids"]))
            links.setdefault(key, link)
        for source in review["supporting_sources"]:
            key = (
                source["path"],
                source.get("start_line", 0),
                source.get("end_line", 0),
                source["role"],
            )
            sources.setdefault(key, source)
    return {
        "review_status": "reviewed_partial",
        "rationale": rationale,
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
    }


_BODY_READ = _source(
    "fastapi/routing.py",
    425,
    465,
    "FastAPI reads request bodies and converts malformed JSON into request-validation errors",
)
_BODY_VALIDATE = _source(
    "fastapi/dependencies/utils.py",
    951,
    998,
    "FastAPI validates a single request body field or extracts embedded body fields",
)
_VALIDATION_RAISE = _source(
    "fastapi/routing.py",
    751,
    755,
    "FastAPI raises RequestValidationError when body or dependency validation returns errors",
)
_VALIDATION_HANDLER = _source(
    "fastapi/exception_handlers.py",
    20,
    26,
    "FastAPI encodes RequestValidationError as a 422 JSON response",
)
_OPENAPI_BODY = _source(
    "fastapi/openapi/utils.py",
    231,
    263,
    "FastAPI creates the OpenAPI requestBody schema and required flag from the route body field",
)
_OPENAPI_OPERATION = _source(
    "fastapi/openapi/utils.py",
    331,
    385,
    "FastAPI adds requestBody data to each documented path operation",
)
_OPENAPI_MODELS = _source(
    "fastapi/openapi/utils.py",
    551,
    582,
    "FastAPI collects request and response fields used to build OpenAPI component schemas",
)


def _docs(tutorial: str, start: int, end: int, role: str) -> dict[str, Any]:
    return _source(f"docs_src/body_nested_models/{tutorial}_py310.py", start, end, role)


_TEST_ROOT = "tests/test_tutorial/test_body_nested_models/"


def _fn(
    test_file: str,
    name: str,
    feature_ids: list[str],
    rationale: str,
    gate: str,
    links: list[dict[str, Any]],
    sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    return _review(_TEST_ROOT + test_file, name, feature_ids, rationale, gate, links, sources)


def _http(recipe: str, case_id: str, action: str = "dispatch") -> dict[str, Any]:
    return _case(recipe, case_id, [action], _HTTP)


def _openapi(
    recipe: str, case_id: str, action: str = "dispatch", paths: bool = False
) -> dict[str, Any]:
    return _case(recipe, case_id, [action], _OPENAPI_PATHS if paths else _OPENAPI)


NESTED_BODY_TUTORIAL_TEST_REVIEW_MAPPINGS: dict[str, dict[str, Any]] = {
    _TEST_ROOT + "test_tutorial001_tutorial002_tutorial003.py": _module(
        "The parametrized module compares request handling and an OpenAPI snapshot for untyped-list, typed-list, and set-valued tags models.",
        {
            "test_put_all": _fn(
                "test_tutorial001_tutorial002_tutorial003.py",
                "test_put_all",
                ["request-validation", "response-serialization"],
                "Independent requests exercise untyped list retention, typed string-list handling, and set uniqueness for duplicate tag values.",
                "The cases use different names, routes, identifiers, and values. They sample the three field kinds but do not compare the source response objects, source values, or exact TestClient JSON decoding.",
                [
                    _http(
                        _PYDANTIC, "fastapi.pydantic-extra-type-body-wave.nested-item.test-put-all"
                    ),
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.typed-tags-body",
                        "put-typed-entry",
                    ),
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.unique-tags-body",
                        "put-unique-entry",
                    ),
                ],
                (
                    _docs("tutorial001", 7, 18, "untyped list-valued tag model and its route"),
                    _docs("tutorial002", 7, 18, "string-list tag model and its route"),
                    _docs("tutorial003", 7, 18, "set-valued tag model and its route"),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_only_required": _fn(
                "test_tutorial001_tutorial002_tutorial003.py",
                "test_put_only_required",
                ["request-validation", "response-serialization"],
                "Independent minimum-field requests sample optional defaults for the untyped-list, typed-list, and set-valued model shapes.",
                "Values and routes are independently authored; exact source response fields and the three app variants' full responses remain gated.",
                [
                    _http(
                        _PYDANTIC,
                        "fastapi.pydantic-extra-type-body-wave.nested-item.test-put-only-required",
                    ),
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.typed-tags-only-required",
                        "put-typed-entry-with-defaults",
                    ),
                    _http(
                        _CORNER,
                        "fastapi.nested-body-corner-wave.nested-item.test-put-only-required",
                    ),
                ],
                (
                    _docs(
                        "tutorial001",
                        7,
                        18,
                        "optional and default fields of the untyped-list model",
                    ),
                    _docs(
                        "tutorial002", 7, 18, "optional and default fields of the typed-list model"
                    ),
                    _docs(
                        "tutorial003", 7, 18, "optional and default fields of the set-valued model"
                    ),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_empty_body": _fn(
                "test_tutorial001_tutorial002_tutorial003.py",
                "test_put_empty_body",
                ["request-validation", "public-api-errors"],
                "An empty object is submitted to an independently modeled body with required name and price fields.",
                "This samples the missing-required-field path on one body model. It does not assert the source error order, locations, input values, message text, or each tag annotation variant.",
                [
                    _http(
                        _PYDANTIC,
                        "fastapi.pydantic-extra-type-body-wave.nested-item.test-put-empty-body",
                    )
                ],
                (
                    _docs(
                        "tutorial001", 7, 18, "required and optional fields in the request model"
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required": _fn(
                "test_tutorial001_tutorial002_tutorial003.py",
                "test_put_missing_required",
                ["request-validation", "public-api-errors"],
                "A partial object omitting the required name and price fields samples body validation with other data present.",
                "The independent case changes the supplied optional field and value; exact source validation locations and serialized error details are not claimed.",
                [
                    _http(
                        _PYDANTIC,
                        "fastapi.pydantic-extra-type-body-wave.nested-item.test-put-missing-required",
                    )
                ],
                (
                    _docs(
                        "tutorial001", 7, 18, "required and optional fields in the request model"
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial001_tutorial002_tutorial003.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "Focused OpenAPI pointers sample the tags schemas for untyped lists, typed string lists, and string sets.",
                "Only the selected tags schema nodes are observed. The complete snapshot, route metadata, required lists, validation components, and snapshot helper behavior are not covered.",
                [
                    _openapi(
                        _PYDANTIC,
                        "fastapi.pydantic-extra-type-body-wave.nested-item.test-openapi-schema",
                    ),
                    _openapi(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.typed-tags-schema",
                        "inspect-typed-tags",
                    ),
                    _openapi(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.unique-tags-schema",
                        "inspect-unique-tags",
                    ),
                ],
                (
                    _docs("tutorial001", 7, 18, "untyped-list model reflected in component schema"),
                    _docs("tutorial002", 7, 18, "typed-list model reflected in component schema"),
                    _docs("tutorial003", 7, 18, "set-valued model reflected in component schema"),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial004.py": _module(
        "The module exercises a nested image model with optional and required fields and inspects a selected request-body schema pointer.",
        {
            "test_put_all": _fn(
                "test_tutorial004.py",
                "test_put_all",
                ["request-validation", "response-serialization"],
                "A nested item request includes a nested image object and repeated set-valued tags.",
                "The independent case uses different item values, URL, and route. It samples nested model coercion and output but not exact source response JSON or TestClient list matching semantics.",
                [_http(_CORNER, "fastapi.nested-body-corner-wave.nested-item.test-put-all")],
                (
                    _docs("tutorial004", 7, 24, "nested image/item models and the body route"),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_only_required": _fn(
                "test_tutorial004.py",
                "test_put_only_required",
                ["request-validation", "response-serialization"],
                "A nested item request omits optional data and the image object to exercise model defaults.",
                "The independent input uses a different item label and number. Exact response fields and Python-side JSON parsing are not asserted.",
                [
                    _http(
                        _CORNER,
                        "fastapi.nested-body-corner-wave.nested-item.test-put-only-required",
                    )
                ],
                (
                    _docs("tutorial004", 12, 24, "optional nested image field and request model"),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_empty_body": _fn(
                "test_tutorial004.py",
                "test_put_empty_body",
                ["request-validation", "public-api-errors"],
                "An empty object samples missing required fields in a nested item body.",
                "The case checks response status and bytes for an independent route; exact source error ordering, locations, messages, and input payload are not covered.",
                [_http(_CORNER, "fastapi.nested-body-corner-wave.nested-item.test-put-empty-body")],
                (
                    _docs("tutorial004", 12, 24, "required item fields and the nested body route"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required_in_item": _fn(
                "test_tutorial004.py",
                "test_put_missing_required_in_item",
                ["request-validation", "public-api-errors"],
                "An object with optional data but no required item fields samples missing-field errors at the root model level.",
                "The case is from a simpler item model and uses different optional keys. Nested child error locations and exact source errors are not claimed.",
                [
                    _http(
                        _PYDANTIC,
                        "fastapi.pydantic-extra-type-body-wave.nested-item.test-put-missing-required",
                    )
                ],
                (
                    _docs("tutorial004", 12, 24, "required fields of the nested item model"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required_in_image": _fn(
                "test_tutorial004.py",
                "test_put_missing_required_in_image",
                ["request-validation", "public-api-errors"],
                "A nested image object omits its required caption field while the parent model has its required fields.",
                "The independent case uses a string URL and different nested names and values. It samples nested-child validation but not the exact error location or serialized detail.",
                [
                    _http(
                        _CORNER,
                        "fastapi.nested-body-corner-wave.nested-item.test-put-missing-required-in-image",
                    )
                ],
                (
                    _docs("tutorial004", 7, 18, "required nested image properties"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial004.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The workflow observes the request-body schema pointer for a route accepting a nested item model.",
                "The selected pointer samples the request-body reference only; component fields, nested image schema, operation metadata, validation schemas, and the complete snapshot remain gated.",
                [
                    _openapi(
                        _CORNER,
                        "fastapi.nested-body-corner-wave.nested-item.test-openapi-schema",
                        paths=True,
                    )
                ],
                (
                    _docs("tutorial004", 7, 24, "nested item schema and documented route"),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial005.py": _module(
        "The module extends the nested image model with HttpUrl validation and URL-format schema checks.",
        {
            "test_put_all": _fn(
                "test_tutorial005.py",
                "test_put_all",
                ["request-validation", "response-serialization"],
                "Independent requests include a nested HttpUrl value and exercise a populated nested request model.",
                "The linked cases use independent data and route structures; exact source response fields, URL value normalization, and duplicate-tag response contents are not asserted.",
                [_http(_REQUEST_MODELS, "fastapi.request-models.nested-models-005.test-put-all")],
                (
                    _docs("tutorial005", 7, 23, "HttpUrl image model nested in the request item"),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_only_required": _fn(
                "test_tutorial005.py",
                "test_put_only_required",
                ["request-validation", "response-serialization"],
                "A request omits the optional nested image and exercises defaults in an independent nested asset model.",
                "The case has independently named fields and omits more optional properties than the source. It does not assert the exact source response object.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.asset-only-required",
                        "put-asset-with-defaults",
                    )
                ],
                (
                    _docs("tutorial005", 12, 23, "optional image and item properties"),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_empty_body": _fn(
                "test_tutorial005.py",
                "test_put_empty_body",
                ["request-validation", "public-api-errors"],
                "An empty item object samples missing required parent fields for an independently modeled body.",
                "The linked case uses another model and does not cover source error ordering, exact locations, message text, or all schema variants.",
                [_http(_CORNER, "fastapi.nested-body-corner-wave.nested-item.test-put-empty-body")],
                (
                    _docs("tutorial005", 12, 23, "required and optional parent model fields"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required_in_item": _fn(
                "test_tutorial005.py",
                "test_put_missing_required_in_item",
                ["request-validation", "public-api-errors"],
                "A partial body omits the required parent item fields while carrying optional data.",
                "The independent request carries a different optional property. It samples missing required parent fields without asserting exact source validation output.",
                [
                    _http(
                        _PYDANTIC,
                        "fastapi.pydantic-extra-type-body-wave.nested-item.test-put-missing-required",
                    )
                ],
                (
                    _docs(
                        "tutorial005",
                        12,
                        23,
                        "required item fields in the nested HttpUrl model example",
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required_in_image": _fn(
                "test_tutorial005.py",
                "test_put_missing_required_in_image",
                ["request-validation", "public-api-errors"],
                "A nested image object omits its required caption field while providing a URL.",
                "The independent case uses a non-URL typed child model and different names. It samples a nested required-child error, not the exact source path or error bytes.",
                [
                    _http(
                        _CORNER,
                        "fastapi.nested-body-corner-wave.nested-item.test-put-missing-required-in-image",
                    )
                ],
                (
                    _docs(
                        "tutorial005",
                        7,
                        18,
                        "nested image required properties, extended with HttpUrl",
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_wrong_url": _fn(
                "test_tutorial005.py",
                "test_put_wrong_url",
                ["request-validation", "public-api-errors"],
                "A malformed URI value is supplied inside a nested HttpUrl model field.",
                "The independent asset uses the field name href, a different malformed string, and a different route. It samples nested URL rejection; exact error context, message, and JSON detail are gated.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.asset-invalid-url",
                        "put-asset-with-invalid-image-url",
                    )
                ],
                (
                    _docs("tutorial005", 7, 18, "HttpUrl annotation on a nested image field"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial005.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "Selected component schema pointers include the nested HttpUrl format and optional image-list schema.",
                "Only selected component fields are inspected; the complete path operation, URI bounds, validation components, and snapshot equality remain gated.",
                [
                    _openapi(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.asset-request-schema",
                        "inspect-asset-and-image-schema",
                    )
                ],
                (
                    _docs(
                        "tutorial005",
                        7,
                        23,
                        "HttpUrl nested image declaration represented in OpenAPI",
                    ),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial006.py": _module(
        "The module tests an optional list of nested HttpUrl image models, including a wrong container type and the OpenAPI schema.",
        {
            "test_put_all": _fn(
                "test_tutorial006.py",
                "test_put_all",
                ["request-validation", "response-serialization"],
                "An independently authored nested catalog request includes multiple images and set-valued tags.",
                "The independent request uses another route, field names, values, and image count. It samples nested list items and a set field but does not match the source response object.",
                [
                    _http(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial006-nested-entry",
                        "put-catalog-entry",
                    )
                ],
                (
                    _docs(
                        "tutorial006",
                        7,
                        23,
                        "HttpUrl image model and optional image list in the item body",
                    ),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_only_required": _fn(
                "test_tutorial006.py",
                "test_put_only_required",
                ["request-validation", "response-serialization"],
                "The independent asset request omits optional image and image-list fields to exercise their defaults.",
                "The workload names its parent fields differently and adds a singular optional image. Exact source output fields and defaults are not claimed.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.asset-only-required",
                        "put-asset-with-defaults",
                    )
                ],
                (
                    _docs(
                        "tutorial006",
                        12,
                        23,
                        "optional list of nested images on a required-field item model",
                    ),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_empty_body": _fn(
                "test_tutorial006.py",
                "test_put_empty_body",
                ["request-validation", "public-api-errors"],
                "An empty object is submitted to an independently authored required-field model.",
                "The case samples the 422 body-validation path on a different route/model. Exact source error list and the optional list's absent-field behavior are not asserted here.",
                [_http(_CORNER, "fastapi.nested-body-corner-wave.nested-item.test-put-empty-body")],
                (
                    _docs(
                        "tutorial006",
                        12,
                        23,
                        "required item fields and optional nested image-list field",
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_images_not_list": _fn(
                "test_tutorial006.py",
                "test_put_images_not_list",
                ["request-validation", "public-api-errors"],
                "An image object is submitted where a list of nested image models is required.",
                "The linked case uses a differently named catalog model and URI values. It samples list-container validation without claiming exact source error location or details.",
                [
                    _http(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial006-invalid-image-container",
                        "put-invalid-catalog-entry",
                    )
                ],
                (
                    _docs("tutorial006", 7, 23, "list[Image] body field declaration"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial006.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The workflow selects a nested catalog component schema containing an optional list of URL-validated image objects.",
                "Only one component schema is observed; the full operation snapshot, requestBody details, sibling components, and complete URL constraints remain gated.",
                [
                    _openapi(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial006-request-schema",
                        "inspect-catalog-operation",
                    )
                ],
                (
                    _docs(
                        "tutorial006", 7, 23, "nested URL image list reflected in component schema"
                    ),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial007.py": _module(
        "The module validates an offer containing a list of item models, each of which can contain a list of URL-validated images.",
        {
            "test_post_all": _fn(
                "test_tutorial007.py",
                "test_post_all",
                ["request-validation", "response-serialization"],
                "An independent promotion request has multiple nested lines and images, with tags on one line.",
                "The input uses other names, values, URL forms, and collection lengths. It samples multi-level model/list validation and response serialization but not exact source response equality.",
                [
                    _http(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial007-nested-promotion",
                        "post-promotion",
                    )
                ],
                (
                    _docs("tutorial007", 7, 30, "nested image, item, offer models, and POST route"),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_only_required": _fn(
                "test_tutorial007.py",
                "test_put_only_required",
                ["request-validation", "response-serialization"],
                "A minimal independent offer provides required root and line fields while omitting optional descriptions, labels, and images.",
                "The independent offer uses line/cost field names and does not assert the source's exact defaulted response body or URL child values.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.offer-only-required",
                        "post-offer-with-required-fields",
                    )
                ],
                (
                    _docs(
                        "tutorial007", 7, 30, "required and optional fields across nested models"
                    ),
                    _BODY_VALIDATE,
                ),
            ),
            "test_put_empty_body": _fn(
                "test_tutorial007.py",
                "test_put_empty_body",
                ["request-validation", "public-api-errors"],
                "An empty object is submitted to the independent offer body to exercise missing root fields and its required line list.",
                "The workflow samples error response bytes and status, not the source's ordered set of three errors, locations, or messages.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.offer-empty-body",
                        "post-empty-offer",
                    )
                ],
                (
                    _docs("tutorial007", 21, 30, "required offer fields and request route"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required_in_items": _fn(
                "test_tutorial007.py",
                "test_put_missing_required_in_items",
                ["request-validation", "public-api-errors"],
                "A nested line object omits its required fields under a valid parent offer.",
                "The existing independent case omits one required child field while retaining another; the source omits both. Exact array-index error locations and error count are not claimed.",
                [
                    _http(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial007-missing-child-fields",
                        "post-incomplete-promotion",
                    )
                ],
                (
                    _docs(
                        "tutorial007",
                        12,
                        30,
                        "required item fields and list nesting inside the offer",
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_put_missing_required_in_images": _fn(
                "test_tutorial007.py",
                "test_put_missing_required_in_images",
                ["request-validation", "public-api-errors"],
                "A nested image object inside line.images omits both required image fields.",
                "The independent input uses different field names and a separate route while preserving two nested list levels. Exact source error paths and message contents are not claimed.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.offer-missing-nested-image-fields",
                        "post-offer-with-incomplete-image",
                    )
                ],
                (
                    _docs("tutorial007", 7, 30, "list of images nested under list of offer items"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial007.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "The selected OpenAPI component pointer samples a root model with nested item and image-list references.",
                "The workflow observes one component node only, not the complete /offers operation, all child component definitions, validation models, or full snapshot equality.",
                [
                    _openapi(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial007-request-schema",
                        "inspect-promotion-operation",
                    )
                ],
                (
                    _docs(
                        "tutorial007", 7, 30, "nested Offer model graph used for OpenAPI generation"
                    ),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial008.py": _module(
        "The module checks a top-level list of HttpUrl image models, including malformed elements, wrong root container type, and OpenAPI.",
        {
            "test_post_body": _fn(
                "test_tutorial008.py",
                "test_post_body",
                ["request-validation", "response-serialization"],
                "A valid image-list request is exercised through an independently authored route.",
                "The existing case sends one item while the source sends two and uses different image values and endpoint details. It samples list-body acceptance, not the source's full list response.",
                [_http(_REQUEST_MODELS, "fastapi.request-models.nested-models-008.test-post-body")],
                (_docs("tutorial008", 7, 14, "top-level list[Image] request body"), _BODY_VALIDATE),
            ),
            "test_post_invalid_list_item": _fn(
                "test_tutorial008.py",
                "test_post_invalid_list_item",
                ["request-validation", "public-api-errors"],
                "A list body contains one image whose URL field is not absolute.",
                "The independent list and field names differ from the source. It samples URL validation under a list index; the exact error location, context, and JSON detail are not claimed.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.image-batch-invalid-url",
                        "post-image-batch-with-invalid-url",
                    )
                ],
                (
                    _docs(
                        "tutorial008", 7, 14, "HttpUrl field nested inside a top-level list body"
                    ),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_post_not_a_list": _fn(
                "test_tutorial008.py",
                "test_post_not_a_list",
                ["request-validation", "public-api-errors"],
                "An object is supplied to a request field declared as a top-level list of nested models.",
                "The independent object has different values and fields. It samples root-container rejection but not the source error's exact normalized input object or JSON bytes.",
                [
                    _http(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.image-batch-object-body",
                        "post-image-object-instead-of-list",
                    )
                ],
                (
                    _docs("tutorial008", 7, 14, "top-level list[Image] declaration"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial008.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "A selected requestBody pointer samples OpenAPI schema generation for a top-level list of nested URL image models.",
                "Only the request-body schema node is observed; path operation metadata, component schemas, validation components, and the complete snapshot are not covered.",
                [
                    _openapi(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.image-batch-request-schema",
                        "inspect-image-batch-request-schema",
                        paths=True,
                    )
                ],
                (
                    _docs(
                        "tutorial008", 7, 14, "top-level list request model and documented route"
                    ),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
    _TEST_ROOT + "test_tutorial009.py": _module(
        "The module checks request validation and OpenAPI for a mapping with integer keys and numeric values.",
        {
            "test_post_body": _fn(
                "test_tutorial009.py",
                "test_post_body",
                ["request-validation", "response-serialization"],
                "A valid object with integer-like keys and numeric values samples map-body coercion and response serialization.",
                "The independent map uses different keys and values; exact source payload echo and numeric JSON formatting are not claimed.",
                [
                    _http(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial009-integer-key-map",
                        "post-index-weights",
                    )
                ],
                (_docs("tutorial009", 6, 8, "dict[int, float] request body"), _BODY_VALIDATE),
            ),
            "test_post_invalid_body": _fn(
                "test_tutorial009.py",
                "test_post_invalid_body",
                ["request-validation", "public-api-errors"],
                "A map body includes a non-integer key to exercise key parsing errors.",
                "The independent case uses another invalid key and numeric value. It samples the map-key validation path but not exact source key location, input, message, or serialized error.",
                [
                    _http(
                        _NESTED,
                        "fastapi.body-nested-models.tutorial009-invalid-map-key",
                        "post-invalid-index-weights",
                    )
                ],
                (
                    _docs("tutorial009", 6, 8, "integer key conversion in the typed map request"),
                    _BODY_VALIDATE,
                    _VALIDATION_RAISE,
                    _VALIDATION_HANDLER,
                ),
            ),
            "test_openapi_schema": _fn(
                "test_tutorial009.py",
                "test_openapi_schema",
                ["openapi-docs"],
                "A requestBody schema pointer samples OpenAPI generation for integer map keys and numeric values.",
                "Only the requestBody schema is selected; operation metadata, 422 schemas, all OpenAPI components, and full snapshot equality remain gated.",
                [
                    _openapi(
                        _REVIEW,
                        "fastapi.nested-body-tutorial-review.weight-map-request-schema",
                        "inspect-weight-map-request-schema",
                        paths=True,
                    )
                ],
                (
                    _docs(
                        "tutorial009",
                        6,
                        8,
                        "typed integer-to-number mapping represented in OpenAPI",
                    ),
                    _OPENAPI_BODY,
                    _OPENAPI_OPERATION,
                    _OPENAPI_MODELS,
                ),
            ),
        },
    ),
}


NESTED_BODY_TUTORIAL_TEST_MODULE_EXCLUSIONS = {
    _TEST_ROOT + "__init__.py": {
        "mapping_status": "source-backed-exclusion",
        "exclusion_reason": "The package marker contains no executable test functions and is outside the tests/test_*.py module denominator.",
        "supporting_sources": [
            {
                "path": _TEST_ROOT + "__init__.py",
                "role": "pinned FastAPI package marker without test functions",
            }
        ],
    }
}
