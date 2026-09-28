"""Function-level source review for response serialization and injection cases.

FastAPI 0.141.1 owns route response-field setup, dependency analysis, and the
orchestration that validates/filters endpoint return values. Its Pydantic
adapter delegates model validation and serialization to pinned Pydantic
2.13.4. Starlette 1.6.0 owns generic Response/JSONResponse rendering, ASGI
emission, background-task execution, and TestClient transport. These rows link
independent input-only workflows; they are not parity results.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FASTAPI_ROOT = PROJECT_ROOT.parent / "fastapi"

SOURCE_IDENTITIES = {
    "fastapi": {
        "version": "0.141.1",
        "commit": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "role": "source oracle and development-time source only; never a target runtime dependency",
    },
    "starlette": {
        "version": "1.6.0",
        "commit": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
        "role": "sole owner of generic HTTP Response/JSONResponse transport and TestClient behavior",
    },
    "pydantic": {
        "version": "2.13.4",
        "role": "owner of model/dataclass validation, coercion, defaults, and field serialization called by FastAPI",
    },
}


def _source(path: str, start: int, end: int, role: str) -> dict[str, Any]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _test_function_span(test_path: str, function_name: str) -> dict[str, Any]:
    path = FASTAPI_ROOT / test_path
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one top-level {function_name} in {test_path}")
    node = matches[0]
    starts = [node.lineno, *(decorator.lineno for decorator in node.decorator_list)]
    return _source(
        test_path,
        min(starts),
        node.end_lineno or node.lineno,
        f"pinned FastAPI 0.141.1 test function {function_name} and its assertions",
    )


def _workflow(
    recipe_path: str,
    case_id: str,
    action_ids: list[str],
    selectors: list[str],
    coverage: str,
) -> dict[str, Any]:
    return {
        "recipe_path": recipe_path,
        "case_id": case_id,
        "action_ids": list(action_ids),
        "observation_selectors": list(selectors),
        "coverage": coverage,
    }


def _mapping(
    test_path: str,
    function_name: str,
    *,
    feature_ids: list[str],
    workflows: list[dict[str, Any]],
    rationale: str,
    contract_gate: str,
    implementation_sources: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    selectors = sorted(
        {selector for workflow in workflows for selector in workflow["observation_selectors"]}
    )
    link_text = "; ".join(
        f"{workflow['recipe_path']}::{workflow['case_id']} actions "
        f"{', '.join(workflow['action_ids'])}"
        for workflow in workflows
    )
    return {
        "mapping_status": "reviewed_partial",
        "feature_ids": list(feature_ids),
        "observation_selectors": selectors,
        "rationale": rationale,
        "replace_features": True,
        "contract_gate": f"Partial: {contract_gate}",
        "workflow_cases": list(workflows),
        "stimulus_notes": (
            "Input-only linked workflow(s): "
            + link_text
            + ". The independent workloads contain no expected response values."
        ),
        "supporting_sources": [
            _test_function_span(test_path, function_name),
            *implementation_sources,
        ],
    }


_FASTAPI_RESPONSE_FIELD = _source(
    "fastapi/routing.py",
    1102,
    1114,
    "FastAPI APIRoute creates a serialization-mode response field from response_model or records that no model field is configured",
)
_FASTAPI_SERIALIZE_RESPONSE = _source(
    "fastapi/routing.py",
    301,
    341,
    "FastAPI validates modeled endpoint output, passes response filtering flags to its field adapter, and uses jsonable_encoder when no response field exists",
)
_FASTAPI_RESPONSE_SELECTION = _source(
    "fastapi/routing.py",
    706,
    750,
    "FastAPI selects an endpoint-returned Response directly or serializes ordinary endpoint output and constructs the configured Response",
)
_FASTAPI_MODEL_FIELD_ADAPTER = _source(
    "fastapi/_compat/v2.py",
    141,
    213,
    "FastAPI ModelField constructs a Pydantic TypeAdapter and delegates validation/dump options to it",
)
_FASTAPI_JSONABLE_DATACLASS = _source(
    "fastapi/encoders.py",
    243,
    272,
    "FastAPI jsonable_encoder delegates BaseModel dumping and converts ordinary dataclasses with dataclasses.asdict when no response model is configured",
)
_FASTAPI_DEPENDENCY_ANALYSIS = _source(
    "fastapi/dependencies/utils.py",
    350,
    371,
    "FastAPI classifies injected Request, Response, and BackgroundTasks special parameters",
)
_FASTAPI_DEPENDS_SYNTAX = _source(
    "fastapi/dependencies/utils.py",
    381,
    475,
    "FastAPI analyzes Annotated Depends metadata separately from Depends supplied as a default parameter value",
)
_FASTAPI_DEPENDENCY_RESOLUTION = _source(
    "fastapi/dependencies/utils.py",
    586,
    730,
    "FastAPI recursively resolves dependency values and injects the shared Request, BackgroundTasks, and mutable temporary Response",
)
_FASTAPI_HANDLER_RESPONSE = _source(
    "fastapi/routing.py",
    481,
    490,
    "FastAPI request handling invokes dependency solving before the path operation function",
)
_FASTAPI_BACKGROUND_MERGE = _source(
    "fastapi/routing.py",
    357,
    372,
    "FastAPI carries the solved BackgroundTasks into its response arguments and applies the dependency-mutated response status",
)
_STARLETTE_RESPONSE = _source(
    "starlette/responses.py",
    29,
    81,
    "Starlette 1.6.0 owns generic Response content rendering and response header initialization",
)
_STARLETTE_SEND_BACKGROUND = _source(
    "starlette/responses.py",
    163,
    170,
    "Starlette 1.6.0 emits HTTP response start/body messages and calls response background work after emission",
)
_STARLETTE_JSON_RESPONSE = _source(
    "starlette/responses.py",
    181,
    201,
    "Starlette 1.6.0 JSONResponse owns generic JSON byte rendering",
)
_STARLETTE_BACKGROUND_TASKS = _source(
    "starlette/background.py",
    12,
    36,
    "Starlette 1.6.0 owns ordered BackgroundTask and BackgroundTasks execution",
)

SUPERSEDED_SCOPE_EVIDENCE = {
    "tests/test_response_dependency.py": {
        "prior_wave_source": _source(
            "scripts/atlas_app_dependency_wave_mappings.py",
            1696,
            1699,
            "Earlier broad module exclusion stated response injection/response precedence/background effects were assigned to other waves",
        ),
        "status": "superseded_by_function_level_response_review",
        "reason": (
            "This wave maps all seven test functions individually: five use existing dependency/"
            "response workflows, the direct injection function uses response-surface.yaml, and "
            "the default Depends syntax has a new input-only case. The prior broad exclusion is "
            "retained here only as superseded scope history for integration."
        ),
    }
}

_FACTORY_RECIPE = "tests/fixtures/input-recipes/parity/response-policy-matrix.yaml"
_RESPONSE_ATLAS_RECIPE = "tests/fixtures/input-recipes/parity/response-openapi-atlas-wave.yaml"
_DEPENDENCY_RECIPE = "tests/fixtures/input-recipes/parity/dependency-wave-graphs.yaml"
_RESPONSE_SURFACE_RECIPE = "tests/fixtures/input-recipes/parity/response-surface.yaml"
_DEFAULT_DEPENDS_RECIPE = (
    "tests/fixtures/input-recipes/parity/response-dependency-default-source-review.yaml"
)

_RESPONSE_SELECTORS = ["http.status", "http.body.bytes"]
_RESPONSE_AND_HEADERS = ["http.status", "http.headers.ordered", "http.body.bytes"]


RESPONSE_SERIALIZATION_DEPENDENCY_SOURCE_REVIEW_MAPPINGS = {
    "tests/test_response_model_default_factory.py": {
        "functions": {
            "test_response_model_has_default_factory_return_dict": _mapping(
                "tests/test_response_model_default_factory.py",
                "test_response_model_has_default_factory_return_dict",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _FACTORY_RECIPE,
                        "fastapi.response.model-default-factory",
                        ["factory-from-dict"],
                        _RESPONSE_SELECTORS,
                        "The route return type is a dict and response_model supplies a default-factory field.",
                    )
                ],
                rationale="A response-model field omitted from a dict return is populated by its field default factory before serialization.",
                contract_gate="the workflow uses an independent model, field name, and factory value. FastAPI owns route response-field orchestration; Pydantic owns default-factory and model validation/serialization semantics; Starlette 1.6.0 owns the response transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_response_model_has_default_factory_return_model": _mapping(
                "tests/test_response_model_default_factory.py",
                "test_response_model_has_default_factory_return_model",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _FACTORY_RECIPE,
                        "fastapi.response.model-default-factory",
                        ["factory-from-model"],
                        _RESPONSE_SELECTORS,
                        "The route returns a response-model instance whose default-factory field is serialized.",
                    )
                ],
                rationale="A returned model instance exposes its generated field in FastAPI's response-model serialization path.",
                contract_gate="the workflow uses an independent model, field name, and factory value. FastAPI chooses the response field and serialization path; Pydantic owns the model default and serializer; Starlette 1.6.0 owns response emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
        }
    },
    "tests/test_response_dependency.py": {
        "functions": {
            "test_response_with_depends_annotated": _mapping(
                "tests/test_response_dependency.py",
                "test_response_with_depends_annotated",
                feature_ids=["app-routing", "dependency-security", "response-serialization"],
                workflows=[
                    _workflow(
                        _DEPENDENCY_RECIPE,
                        "fastapi.response.dependency-mutates-response",
                        ["chained-response-headers"],
                        _RESPONSE_AND_HEADERS,
                        "A Response special parameter is injected into a Depends dependency and its header mutation reaches the HTTP response.",
                    )
                ],
                rationale="The independent case covers Annotated Depends resolution for Response and preservation of dependency-added headers.",
                contract_gate="the independent case has two dependency layers and different header/body values than this one-layer source function. FastAPI owns parameter/dependency analysis and response-state propagation; Starlette 1.6.0 owns Response headers, JSON rendering, and ASGI emission.",
                implementation_sources=(
                    _FASTAPI_DEPENDS_SYNTAX,
                    _FASTAPI_DEPENDENCY_ANALYSIS,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _FASTAPI_HANDLER_RESPONSE,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_response_with_depends_default": _mapping(
                "tests/test_response_dependency.py",
                "test_response_with_depends_default",
                feature_ids=["app-routing", "dependency-security", "response-serialization"],
                workflows=[
                    _workflow(
                        _DEFAULT_DEPENDS_RECIPE,
                        "fastapi.response-dependency-default-source-review.response-default-parameter",
                        ["inject-through-default-depends"],
                        _RESPONSE_AND_HEADERS,
                        "A Response special parameter is injected through a dependency declared as the endpoint parameter default.",
                    )
                ],
                rationale="This independently exercises the public Response = Depends(...) signature form. Existing response dependency input only used Annotated[Response, Depends(...)], so a separate input makes FastAPI's default-value parsing observable.",
                contract_gate="the independent workload uses a distinct route, header, and body value and makes no literal output claim. FastAPI owns the distinction between Annotated metadata and a Depends default and propagates injected Response state; Starlette 1.6.0 owns response header/body emission.",
                implementation_sources=(
                    _FASTAPI_DEPENDS_SYNTAX,
                    _FASTAPI_DEPENDENCY_ANALYSIS,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _FASTAPI_HANDLER_RESPONSE,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_response_without_depends": _mapping(
                "tests/test_response_dependency.py",
                "test_response_without_depends",
                feature_ids=["app-routing", "response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_SURFACE_RECIPE,
                        "fastapi.response.injected-headers",
                        ["dispatch"],
                        _RESPONSE_AND_HEADERS,
                        "A path operation directly receives Response, mutates its headers, and returns ordinary JSON data.",
                    )
                ],
                rationale="The existing response-surface action observes direct Response injection and a returned JSON object after header mutation.",
                contract_gate="the independent route and header/body values differ. FastAPI owns recognizing and injecting the special Response parameter and merging its headers with serialized data; Starlette 1.6.0 owns header initialization, JSON rendering, and ASGI emission.",
                implementation_sources=(
                    _FASTAPI_DEPENDENCY_ANALYSIS,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _FASTAPI_RESPONSE_SELECTION,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_response_dependency_chain": _mapping(
                "tests/test_response_dependency.py",
                "test_response_dependency_chain",
                feature_ids=["app-routing", "dependency-security", "response-serialization"],
                workflows=[
                    _workflow(
                        _DEPENDENCY_RECIPE,
                        "fastapi.response.dependency-mutates-response",
                        ["chained-response-headers"],
                        _RESPONSE_AND_HEADERS,
                        "Nested dependencies mutate the same injected Response and the endpoint returns JSON.",
                    )
                ],
                rationale="The independent workflow preserves response mutations across nested Depends resolution before the path operation returns ordinary data.",
                contract_gate="the independent header labels and body differ from the source values. FastAPI owns recursive dependency solving and temporary Response reuse; Starlette 1.6.0 owns response header/body transport.",
                implementation_sources=(
                    _FASTAPI_DEPENDS_SYNTAX,
                    _FASTAPI_DEPENDENCY_ANALYSIS,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _FASTAPI_HANDLER_RESPONSE,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_response_dependency_returns_different_response_instance": _mapping(
                "tests/test_response_dependency.py",
                "test_response_dependency_returns_different_response_instance",
                feature_ids=["app-routing", "dependency-security", "response-serialization"],
                workflows=[
                    _workflow(
                        _DEPENDENCY_RECIPE,
                        "fastapi.response.dependency-selects-response-instance",
                        ["dependency-selected-response"],
                        _RESPONSE_AND_HEADERS,
                        "A dependency returns a separate JSONResponse which the endpoint mutates and returns.",
                    )
                ],
                rationale="The linked case independently covers selecting a dependency-returned Response instance over ordinary endpoint data while retaining endpoint header edits.",
                contract_gate="the route, header, and body values are independent. FastAPI owns dependency resolution and returning the endpoint's Response without response-model serialization; Starlette 1.6.0 owns JSONResponse rendering, headers, and emission.",
                implementation_sources=(
                    _FASTAPI_DEPENDS_SYNTAX,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _FASTAPI_RESPONSE_SELECTION,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_request_with_depends_annotated": _mapping(
                "tests/test_response_dependency.py",
                "test_request_with_depends_annotated",
                feature_ids=["app-routing", "dependency-security", "response-serialization"],
                workflows=[
                    _workflow(
                        _DEPENDENCY_RECIPE,
                        "fastapi.response.dependency-mutates-response",
                        ["request-injected-through-dependency"],
                        _RESPONSE_SELECTORS,
                        "A Request is injected into a dependency that extracts request path and user-agent data for the endpoint body.",
                    )
                ],
                rationale="The existing action observes Request special-type injection through an Annotated dependency and reflects selected request attributes into the response body.",
                contract_gate="the independent path and user-agent are different from the source values. FastAPI owns dependency graph resolution and Request injection; Starlette 1.6.0 owns Request/ASGI scope semantics and response transport.",
                implementation_sources=(
                    _FASTAPI_DEPENDS_SYNTAX,
                    _FASTAPI_DEPENDENCY_ANALYSIS,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_background_tasks_with_depends_annotated": _mapping(
                "tests/test_response_dependency.py",
                "test_background_tasks_with_depends_annotated",
                feature_ids=["app-routing", "dependency-security", "response-serialization"],
                workflows=[
                    _workflow(
                        _DEPENDENCY_RECIPE,
                        "fastapi.response.dependency-background-tasks",
                        ["schedule-background-effects", "read-background-effects"],
                        _RESPONSE_SELECTORS,
                        "The dependency and endpoint append effects to the shared BackgroundTasks object; a follow-up request reads them in order.",
                    )
                ],
                rationale="The two-action workflow observes both response completion and the effects scheduled by the dependency and endpoint.",
                contract_gate="the independent side-effect labels and response body differ. FastAPI owns injection and aggregation of the shared BackgroundTasks parameter; Starlette 1.6.0 owns ordered task execution after sending response messages and generic TestClient transport.",
                implementation_sources=(
                    _FASTAPI_DEPENDS_SYNTAX,
                    _FASTAPI_DEPENDENCY_ANALYSIS,
                    _FASTAPI_DEPENDENCY_RESOLUTION,
                    _FASTAPI_BACKGROUND_MERGE,
                    _STARLETTE_SEND_BACKGROUND,
                    _STARLETTE_BACKGROUND_TASKS,
                ),
            ),
        }
    },
    "tests/test_serialize_response.py": {
        "functions": {
            "test_valid": _mapping(
                "tests/test_serialize_response.py",
                "test_valid",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.pydantic-model-serialization",
                        ["complete-model"],
                        _RESPONSE_SELECTORS,
                        "A dict return is validated and serialized through a Pydantic response model.",
                    )
                ],
                rationale="The linked case observes ordinary response-model validation and serialization for a populated model value.",
                contract_gate="the independent model fields and values differ. FastAPI owns response_model setup and serialization orchestration; Pydantic owns validation/default/serialization details through TypeAdapter; Starlette 1.6.0 owns JSON response bytes and ASGI emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_coerce": _mapping(
                "tests/test_serialize_response.py",
                "test_coerce",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.pydantic-model-serialization",
                        ["coerced-model"],
                        _RESPONSE_SELECTORS,
                        "A string-valued numeric field is validated and serialized by the response-model field.",
                    ),
                    _workflow(
                        _FACTORY_RECIPE,
                        "fastapi.response.model-coercion",
                        ["coerce-model-fields"],
                        _RESPONSE_SELECTORS,
                        "An independently authored string numeric field exercises Pydantic coercion in FastAPI response serialization.",
                    ),
                ],
                rationale="The two existing inputs jointly cover the source's returned dict shape and string-to-number coercion through a FastAPI response model.",
                contract_gate="route values and model names differ. FastAPI owns response validation dispatch; Pydantic 2.13.4 owns conversion and serialization; Starlette 1.6.0 owns transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_validlist": _mapping(
                "tests/test_serialize_response.py",
                "test_validlist",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.pydantic-model-serialization",
                        ["list-of-models"],
                        _RESPONSE_SELECTORS,
                        "A list of dict records is validated and serialized as a list response model.",
                    )
                ],
                rationale="The independent list case covers nested response-model validation and serialization for collections.",
                contract_gate="the independent records and field names differ. FastAPI owns the response field and return-value orchestration; Pydantic owns item validation/default serialization; Starlette 1.6.0 owns JSON rendering and ASGI transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
        }
    },
    "tests/test_serialize_response_dataclass.py": {
        "functions": {
            "test_valid": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_valid",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["dataclass-record"],
                        _RESPONSE_SELECTORS,
                        "A record dict is validated against a dataclass response model.",
                    )
                ],
                rationale="The input covers FastAPI's response-model field handling of a dataclass record with a date and optional fields.",
                contract_gate="input fields and date differ. FastAPI selects and invokes the response field; Pydantic owns dataclass validation and serialization; Starlette 1.6.0 owns JSON response emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_object": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_object",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["dataclass-object"],
                        _RESPONSE_SELECTORS,
                        "A dataclass instance is returned and serialized through the declared response model.",
                    )
                ],
                rationale="The existing object action covers returning a dataclass instance under a FastAPI response_model.",
                contract_gate="the instance values differ. FastAPI owns response-field orchestration; Pydantic owns validating and serializing the dataclass model; Starlette 1.6.0 owns response emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_coerce": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_coerce",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["dataclass-coercion"],
                        _RESPONSE_SELECTORS,
                        "String-valued date and numeric fields are coerced under a dataclass response model.",
                    )
                ],
                rationale="The independent route covers coercion of string inputs into typed dataclass response fields.",
                contract_gate="the independent types and values differ. FastAPI owns response-model validation orchestration; Pydantic owns dataclass field coercion/serialization; Starlette 1.6.0 owns the JSON response transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_validlist": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_validlist",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["dataclass-list"],
                        _RESPONSE_SELECTORS,
                        "A list of record dicts is validated and serialized as a list of dataclass response models.",
                    )
                ],
                rationale="The linked action covers list-item validation, optional defaults, and recursive dataclass response serialization.",
                contract_gate="record values and dates differ. FastAPI owns route response-model orchestration; Pydantic owns dataclass item validation/serialization; Starlette 1.6.0 owns response rendering and emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_objectlist": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_objectlist",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["dataclass-object-list"],
                        _RESPONSE_SELECTORS,
                        "A list of dataclass objects is returned under a list response model.",
                    )
                ],
                rationale="The existing object-list action covers validation and serialization of returned dataclass instances in a response collection.",
                contract_gate="the independent records and values differ. FastAPI owns list response-field dispatch; Pydantic owns dataclass item processing; Starlette 1.6.0 owns JSON transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_no_response_model_object": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_no_response_model_object",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["no-model-dataclass-object"],
                        _RESPONSE_SELECTORS,
                        "A dataclass object is returned without response_model, using FastAPI jsonable_encoder.",
                    )
                ],
                rationale="The existing unmodeled-object action covers the separate no-response-field encoder branch for Python dataclasses.",
                contract_gate="the instance values differ. FastAPI jsonable_encoder converts the dataclass with dataclasses.asdict and recursively encodes values; Pydantic response-model filtering is not involved; Starlette 1.6.0 owns response rendering/emission.",
                implementation_sources=(
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_JSONABLE_DATACLASS,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_no_response_model_objectlist": _mapping(
                "tests/test_serialize_response_dataclass.py",
                "test_no_response_model_objectlist",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.dataclass-serialization",
                        ["no-model-dataclass-list"],
                        _RESPONSE_SELECTORS,
                        "A list of dataclass objects is returned without response_model and recursively encoded.",
                    )
                ],
                rationale="The existing unmodeled-list action covers FastAPI jsonable_encoder handling for a collection of ordinary dataclass objects.",
                contract_gate="the independent records differ. FastAPI owns the no-response-field jsonable_encoder path; Pydantic field validation/filtering is absent; Starlette 1.6.0 owns generic JSON transport.",
                implementation_sources=(
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_JSONABLE_DATACLASS,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
        }
    },
    "tests/test_serialize_response_model.py": {
        "functions": {
            "test_valid": _mapping(
                "tests/test_serialize_response_model.py",
                "test_valid",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["alias-object"],
                        _RESPONSE_SELECTORS,
                        "A returned Pydantic model instance is serialized with its field alias enabled by default.",
                    )
                ],
                rationale="The independent model-object action exercises response_model serialization with by-alias output and included default fields.",
                contract_gate="model names and field values differ. FastAPI owns default by-alias response configuration and invokes the serializer; Pydantic owns model dumping; Starlette 1.6.0 owns JSON rendering and emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_coerce": _mapping(
                "tests/test_serialize_response_model.py",
                "test_coerce",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["alias-object"],
                        _RESPONSE_SELECTORS,
                        "A Pydantic model object is returned and its aliased response fields are serialized.",
                    ),
                    _workflow(
                        _FACTORY_RECIPE,
                        "fastapi.response.model-coercion",
                        ["coerce-model-fields"],
                        _RESPONSE_SELECTORS,
                        "A dict with a numeric string exercises response-model field coercion before JSON serialization.",
                    ),
                ],
                rationale="The independent model-object case covers returned model serialization, and the coercion case covers numeric-string conversion through the response field.",
                contract_gate="the linked values and model shape differ from the source. FastAPI owns response validation/serialization orchestration and alias configuration; Pydantic owns model construction coercion, response-field validation, and dumping; Starlette 1.6.0 owns HTTP bytes.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_validlist": _mapping(
                "tests/test_serialize_response_model.py",
                "test_validlist",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["alias-list"],
                        _RESPONSE_SELECTORS,
                        "A list of Pydantic models is serialized as a response collection with aliases and defaults.",
                    )
                ],
                rationale="The independent case covers aliased list-item serialization, optional defaults, and nested fields.",
                contract_gate="list items and values differ. FastAPI owns response field configuration; Pydantic owns model-list serialization; Starlette 1.6.0 owns JSON response emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_validdict": _mapping(
                "tests/test_serialize_response_model.py",
                "test_validdict",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["alias-map"],
                        _RESPONSE_SELECTORS,
                        "A mapping of keys to Pydantic models is serialized with aliased model fields.",
                    )
                ],
                rationale="The independent map action covers response-model serialization of each value while retaining the mapping keys.",
                contract_gate="mapping keys, model fields, and values differ. FastAPI owns response field dispatch; Pydantic owns nested model serialization and aliases; Starlette 1.6.0 owns JSON rendering/emission.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_valid_exclude_unset": _mapping(
                "tests/test_serialize_response_model.py",
                "test_valid_exclude_unset",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["exclude-unset-object"],
                        _RESPONSE_SELECTORS,
                        "A returned model instance is serialized with response_model_exclude_unset enabled.",
                    )
                ],
                rationale="The existing object case covers FastAPI forwarding the route's exclude-unset policy into model serialization.",
                contract_gate="the model and fields differ. FastAPI owns the response_model_exclude_unset route flag and passes it to the adapter; Pydantic owns which unset fields are omitted; Starlette 1.6.0 owns response transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_coerce_exclude_unset": _mapping(
                "tests/test_serialize_response_model.py",
                "test_coerce_exclude_unset",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["exclude-unset-coercion"],
                        _RESPONSE_SELECTORS,
                        "A string-valued numeric field is coerced while response_model_exclude_unset removes unprovided fields.",
                    )
                ],
                rationale="The input jointly observes coercion of a numeric string and FastAPI's exclude-unset response-model policy.",
                contract_gate="the linked endpoint returns a dict while the source endpoint constructs a Pydantic model, and the input field values differ. FastAPI owns response field orchestration and the exclude-unset flag; Pydantic owns coercion and unset-field serialization; Starlette 1.6.0 owns JSON transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_validlist_exclude_unset": _mapping(
                "tests/test_serialize_response_model.py",
                "test_validlist_exclude_unset",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["exclude-unset-list"],
                        _RESPONSE_SELECTORS,
                        "List response-model items serialize only their explicitly set fields.",
                    )
                ],
                rationale="The independent list case covers forwarding exclude-unset to nested response-model items.",
                contract_gate="the model fields and values differ. FastAPI owns the route response policy; Pydantic owns per-item unset-field selection; Starlette 1.6.0 owns JSON output transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
            "test_validdict_exclude_unset": _mapping(
                "tests/test_serialize_response_model.py",
                "test_validdict_exclude_unset",
                feature_ids=["response-serialization"],
                workflows=[
                    _workflow(
                        _RESPONSE_ATLAS_RECIPE,
                        "fastapi.response-openapi-atlas-wave.aliased-and-exclude-unset-models",
                        ["exclude-unset-map"],
                        _RESPONSE_SELECTORS,
                        "Mapping values serialize as response models with unset fields excluded.",
                    )
                ],
                rationale="The independent map case covers applying exclude-unset to each model value while preserving mapping structure.",
                contract_gate="mapping keys, model fields, and values differ. FastAPI owns route policy and response field dispatch; Pydantic owns nested model dumping with exclude_unset; Starlette 1.6.0 owns response transport.",
                implementation_sources=(
                    _FASTAPI_RESPONSE_FIELD,
                    _FASTAPI_SERIALIZE_RESPONSE,
                    _FASTAPI_MODEL_FIELD_ADAPTER,
                    _STARLETTE_RESPONSE,
                    _STARLETTE_JSON_RESPONSE,
                ),
            ),
        }
    },
}
