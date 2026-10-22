"""Reviewed source-to-input links for newly introduced FastAPI 0.157.0 tests."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"
RECIPE_ROOT = PROJECT_ROOT / "tests/fixtures/input-recipes/parity"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.157.0",
        "commit": "386a28af2f87af1a32ac26d88f07b7f58ab2dfb1",
        "role": "isolated source oracle and development evidence",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole generic ASGI, response, WebSocket, and TestClient oracle",
    },
    "pydantic": {"version": "2.13.5", "role": "pinned model validation dependency"},
}


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _module_sources(test_path: str) -> list[dict[str, Any]]:
    tree = ast.parse((FASTAPI_ROOT / test_path).read_text(encoding="utf-8"))
    return [
        _source(
            test_path,
            min([node.lineno, *(item.lineno for item in node.decorator_list)]),
            node.end_lineno or node.lineno,
            f"FastAPI 0.157.0 source test {node.name}; independent module mapping is partial",
        )
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]


def _case_selectors(recipe_path: str, case_id: str) -> list[str]:
    recipe = yaml.safe_load((PROJECT_ROOT / recipe_path).read_text(encoding="utf-8"))
    case = next((row for row in recipe.get("cases", []) if row.get("case_id") == case_id), None)
    if case is None:
        raise ValueError(f"missing source-reviewed workflow case {recipe_path}::{case_id}")
    selected: set[str] = set()
    construction = case.get("construction_observation", {})
    for selector in construction.get("selectors", []):
        selected.add(f"construction.{selector}")
    for action in case.get("actions", []):
        if action.get("kind") == "lifespan":
            selected.update(
                f"asgi.lifespan.{row['selector']}" for row in action.get("observations", [])
            )
            continue
        for observation in action.get("observations", []):
            kind = observation.get("kind")
            if kind == "http_response":
                selectors = set(observation.get("selectors", []))
                if "status" in selectors:
                    selected.add("http.status")
                if "headers" in selectors:
                    selected.add("http.headers.ordered")
                if "body" in selectors:
                    selected.add("http.body.bytes")
                if "body_json" in selectors:
                    selected.add("http.body.json")
            elif kind == "openapi":
                selected.add("openapi.document")
                if any(
                    pointer.startswith("/paths/")
                    for pointer in observation.get("json_pointers", [])
                ):
                    selected.add("openapi.paths")
            elif kind == "websocket":
                selected.add(f"websocket.{observation['selector']}")
            elif kind == "asgi_send":
                selected.add(f"asgi.send.{observation['selector']}")
    return sorted(selected)


def _link(recipe_path: str, case_ids: tuple[str, ...]) -> dict[str, Any]:
    selectors = sorted(
        {selector for case_id in case_ids for selector in _case_selectors(recipe_path, case_id)}
    )
    return {
        "recipe_path": recipe_path,
        "case_ids": list(case_ids),
        "observation_selectors": selectors,
    }


def _module(rationale: str, links: tuple[tuple[str, tuple[str, ...]], ...]):
    workflow_cases = [_link(recipe_path, case_ids) for recipe_path, case_ids in links]
    selectors = sorted(
        {selector for workflow in workflow_cases for selector in workflow["observation_selectors"]}
    )
    return {
        "rationale": rationale,
        "supporting_sources": [],
        "module_observation_selectors": selectors,
        "workflow_cases": workflow_cases,
        "stimulus_notes": (
            "Partial source-backed mapping to independently authored YAML recipes. The linked "
            "workloads use new inputs and record no expected outputs; unlinked source branches "
            "and edge cases remain outside this mapping."
        ),
        "contract_gate": (
            "Partial coverage only. The selectors describe observations available in the linked "
            "independent workflow and do not claim complete upstream test or branch parity."
        ),
    }


_ALIASES = "tests/fixtures/input-recipes/parity/parameter-alias-choices-0157.yaml"
_COMBINED = "tests/fixtures/input-recipes/parity/parameter-models-combined-locations-0157.yaml"
_MODULES: dict[str, dict[str, Any]] = {
    "tests/test_body_alias_choices.py": _module(
        "Body AliasChoices input, selected alias, and OpenAPI projection have independent requests; nested-error and default branches are not claimed.",
        (
            (
                _ALIASES,
                (
                    "fastapi.parameter-alias-choices-0157.body-choice",
                    "fastapi.parameter-alias-choices-0157.openapi",
                ),
            ),
        ),
    ),
    "tests/test_header_cookie_alias_choices.py": _module(
        "Independent header and cookie requests exercise a later AliasChoices entry; duplicate values, extras, and all capitalization cases remain outside this partial sample.",
        (
            (
                _ALIASES,
                (
                    "fastapi.parameter-alias-choices-0157.header-choice",
                    "fastapi.parameter-alias-choices-0157.cookie-choice",
                    "fastapi.parameter-alias-choices-0157.openapi",
                ),
            ),
        ),
    ),
    "tests/test_multiple_parameter_models.py": _module(
        "The independent fixture covers distinct query, header, cookie, literal-header, dependency, and OpenAPI locations. The AliasChoices/extra-field cross-product remains only partially represented.",
        (
            (
                _COMBINED,
                tuple(
                    f"fastapi.parameter-models.combined-locations.{case}"
                    for case in (
                        "defaults",
                        "independent-values",
                        "independent-validation",
                        "forbid-extras-around-dependencies",
                        "openapi-parameters",
                    )
                ),
            ),
            (
                _ALIASES,
                (
                    "fastapi.parameter-alias-choices-0157.query-choice",
                    "fastapi.parameter-alias-choices-0157.header-choice",
                    "fastapi.parameter-alias-choices-0157.cookie-choice",
                ),
            ),
        ),
    ),
    "tests/test_path_alias_choices.py": _module(
        "Independent path parameter and WebSocket requests exercise validation aliases. Router-prefix matching, constraints, alias paths, and path-choice error locations remain outside this sample.",
        (
            (
                _ALIASES,
                (
                    "fastapi.parameter-alias-choices-0157.path-choice",
                    "fastapi.parameter-alias-choices-0157.websocket-security",
                    "fastapi.parameter-alias-choices-0157.openapi",
                ),
            ),
        ),
    ),
    "tests/test_query_alias_choices.py": _module(
        "An independent query request selects a non-first AliasChoices value, and OpenAPI input is captured. Model extras, repeated values, alias-path extraction, and all error variants remain outside this sample.",
        (
            (
                _ALIASES,
                (
                    "fastapi.parameter-alias-choices-0157.query-choice",
                    "fastapi.parameter-alias-choices-0157.openapi",
                ),
            ),
        ),
    ),
    "tests/test_route_handler_wrapping.py": _module(
        "Independent route-class and late-route workflows cover observable custom-route dispatch and live route registration. Internal monkeypatch wrapper counts and private context-variable recovery are not asserted.",
        (
            (
                "tests/fixtures/input-recipes/parity/route-class-override.yaml",
                ("fastapi.routing.apirouter.add-api-route.route-class-override",),
            ),
            (
                "tests/fixtures/input-recipes/parity/router-live-route-after-include-source-review.yaml",
                ("fastapi.router.include-context.live-route-after-include",),
            ),
        ),
    ),
    "tests/test_security_websockets.py": _module(
        "The independent WebSocket workflow supplies HTTP Bearer credentials through FastAPI Security and observes accepted messages and close order. Other security schemes and denial responses are outside this partial sample.",
        ((_ALIASES, ("fastapi.parameter-alias-choices-0157.websocket-security",)),),
    ),
    "tests/test_stream_non_finite_floats.py": _module(
        "An independent SSE request streams non-finite float values and observes response headers and bytes. Model serialization modes, nested values, JSONL, and raw event variants remain outside this partial sample.",
        ((_ALIASES, ("fastapi.parameter-alias-choices-0157.stream-non-finite",)),),
    ),
    "tests/test_tutorial/test_query_param_models/test_tutorial003.py": _module(
        "The independent combined-location workload exercises query parameter models and their OpenAPI projection; tutorial-specific names, snapshots, and exact values are not claimed.",
        (
            (
                _COMBINED,
                tuple(
                    f"fastapi.parameter-models.combined-locations.{case}"
                    for case in (
                        "defaults",
                        "independent-values",
                        "independent-validation",
                        "forbid-extras-around-dependencies",
                        "openapi-parameters",
                    )
                ),
            ),
        ),
    ),
    "tests/test_tutorial/test_templates/test_tutorial002.py": _module(
        "The independent template response workflow renders an item page using the optional templates profile. StaticFiles serving and the full root_path/mount_path matrix are not represented.",
        (
            (
                "tests/fixtures/input-recipes/parity/fastapi-templating-asgi.yaml",
                ("fastapi.templating.jinja-template-response",),
            ),
        ),
    ),
    "tests/test_union_form_normalization.py": _module(
        "Independent form-union requests cover accepted, empty, and invalid form shapes. The new empty-scalar normalization, multipart duplicate fields, validator mutation, and file-placeholder branches are not fully represented.",
        (
            (
                "tests/fixtures/input-recipes/parity/union-forms-tutorial-review.yaml",
                (
                    "fastapi.request-union-forms.tutorial.user",
                    "fastapi.request-union-forms.tutorial.company",
                    "fastapi.request-union-forms.tutorial.invalid-mixed-fields",
                    "fastapi.request-union-forms.tutorial.empty",
                ),
            ),
            (
                "tests/fixtures/input-recipes/parity/request-forms.yaml",
                ("fastapi.request-forms.union-forms.test-post-user-form",),
            ),
        ),
    ),
    "tests/test_upload_file_read_position.py": _module(
        "The independent multipart upload workflow reads, seeks, and rereads an UploadFile. It does not reproduce the source tests' shared dependency/endpoint object and automatic-read failure branches.",
        (
            (
                "tests/fixtures/input-recipes/parity/request-form-upload-source-review-2026.yaml",
                ("fastapi.request-form-upload.uploadfile.read-seek-replay",),
            ),
        ),
    ),
    "tests/test_security_http_base_optional.py": _module(
        "Independent HTTP Base workflows exercise required/optional credential handling and OpenAPI projection; WebSocket cases and all credential error details are outside this sample.",
        (
            (
                "tests/fixtures/input-recipes/parity/security_credentials_upstream.yaml",
                (
                    "fastapi.security.http-base-optional.test-security-http-base",
                    "fastapi.security.http-base-optional.test-security-http-base-no-credentials",
                    "fastapi.security.http-base-optional.test-openapi-schema",
                ),
            ),
        ),
    ),
    "tests/test_security_http_bearer.py": _module(
        "Independent HTTP Bearer workflows cover valid, absent, wrong-scheme, and OpenAPI inputs. The source test's subclass constructor branch remains outside this mapping.",
        (
            (
                "tests/fixtures/input-recipes/parity/security_credentials_upstream.yaml",
                (
                    "fastapi.security.http-bearer.test-security-http-bearer",
                    "fastapi.security.http-bearer.test-security-http-bearer-no-credentials",
                    "fastapi.security.http-bearer.test-security-http-bearer-incorrect-scheme-credentials",
                    "fastapi.security.http-bearer.test-openapi-schema",
                ),
            ),
        ),
    ),
}

for _test_path, _module_mapping in _MODULES.items():
    _module_mapping["supporting_sources"] = _module_sources(_test_path)

TRANSLATION_TEST_EXCLUSION = {
    "reason": (
        "This source test commits translated documentation changes and checks repository localization tooling; it does not exercise the FastAPI runtime or public API."
    ),
    "supporting_sources": _module_sources("tests/test_translate.py"),
}

__all__ = ["FASTAPI_0157_DELTA_TEST_REVIEW_MAPPINGS", "TRANSLATION_TEST_EXCLUSION"]
FASTAPI_0157_DELTA_TEST_REVIEW_MAPPINGS = _MODULES
