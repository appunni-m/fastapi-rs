"""Allow-listed target-only fault contracts for ASGI workflow cases.

This module validates declarative fault references and checks the resulting
public observations. Fault point identifiers select injection behavior;
contract identifiers select assertions. Case IDs are deliberately not used
for dispatch.
"""

from __future__ import annotations

import base64
import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any


class FaultContractError(ValueError):
    """A malformed fault declaration or a failed public fault contract."""


HTTP_ROUTE_INVOCATION_FAULT_POINT = "http.route.invoke.before"
HTTP_ROUTE_INVOCATION_CONTRACT = "http-route-invocation-error-and-recovery"
HTTP_ROUTE_DEPENDENCY_CLEANUP_FAULT_POINT = "http.route.invoke.after_dependencies.before"
HTTP_ROUTE_DEPENDENCY_CLEANUP_CONTRACT = "http-route-invocation-error-cleans-dependencies"
HTTP_REQUEST_JSON_DECODE_FAULT_POINT = "http.request.json_decode.before"
HTTP_REQUEST_JSON_DECODE_CONTRACT = "http-body-json-decode-error-returns-400"
HTTP_REQUEST_FORM_PARSE_FAULT_POINT = "http.request.form_parse.before"
HTTP_REQUEST_FORM_PARSE_CONTRACT = "http-body-form-parse-error-returns-400"
HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_FAULT_POINT = "http.frontend.lookup.permission-error"
HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_CONTRACT = "frontend-static-lookup-permission-denied-401"
HTTP_FRONTEND_LOOKUP_VALUE_ERROR_FAULT_POINT = "http.frontend.lookup.value-error"
HTTP_FRONTEND_LOOKUP_VALUE_ERROR_CONTRACT = "frontend-static-lookup-value-error-404"
HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_FAULT_POINT = "http.frontend.lookup.name-too-long"
HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_CONTRACT = "frontend-static-lookup-name-too-long-404"
HTTP_FRONTEND_LOOKUP_OS_ERROR_FAULT_POINT = "http.frontend.lookup.os-error"
HTTP_FRONTEND_LOOKUP_OS_ERROR_CONTRACT = "frontend-static-lookup-os-error-propagates"
HTTP_ROUTE_SCOPED_DEPENDENCY_CLEANUP_CONTRACT = (
    "http-route-invocation-error-orders-function-and-request-dependency-cleanup"
)
FUNCTION_REQUEST_ERROR_EVENTS = [
    "function-enter",
    "request-enter",
    "function-cleanup",
    "request-cleanup",
    "response-start",
    "response-end",
]

# metadata.yaml is the policy authority; metadata-check enforces this runtime
# dispatch table against the reviewed registry.
FAULT_POINT_CONTRACTS: dict[str, frozenset[str]] = {
    HTTP_ROUTE_INVOCATION_FAULT_POINT: frozenset({HTTP_ROUTE_INVOCATION_CONTRACT}),
    HTTP_ROUTE_DEPENDENCY_CLEANUP_FAULT_POINT: frozenset(
        {
            HTTP_ROUTE_DEPENDENCY_CLEANUP_CONTRACT,
            HTTP_ROUTE_SCOPED_DEPENDENCY_CLEANUP_CONTRACT,
        }
    ),
    HTTP_REQUEST_JSON_DECODE_FAULT_POINT: frozenset({HTTP_REQUEST_JSON_DECODE_CONTRACT}),
    HTTP_REQUEST_FORM_PARSE_FAULT_POINT: frozenset({HTTP_REQUEST_FORM_PARSE_CONTRACT}),
    HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_FAULT_POINT: frozenset(
        {HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_CONTRACT}
    ),
    HTTP_FRONTEND_LOOKUP_VALUE_ERROR_FAULT_POINT: frozenset(
        {HTTP_FRONTEND_LOOKUP_VALUE_ERROR_CONTRACT}
    ),
    HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_FAULT_POINT: frozenset(
        {HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_CONTRACT}
    ),
    HTTP_FRONTEND_LOOKUP_OS_ERROR_FAULT_POINT: frozenset({HTTP_FRONTEND_LOOKUP_OS_ERROR_CONTRACT}),
}


def verification_mode(case: Mapping[str, Any]) -> str:
    """Validate and return a case lane, defaulting legacy cases to parity."""
    if not isinstance(case, Mapping):
        raise FaultContractError("workflow case must be an object")

    mode = case.get("verification", "parity")
    if mode == "parity":
        if "fault" in case:
            raise FaultContractError("parity cases must not declare a fault")
        return mode
    if mode != "fault-contract":
        raise FaultContractError(f"unsupported case verification mode: {mode!r}")

    fault = case.get("fault")
    if not isinstance(fault, Mapping):
        raise FaultContractError("fault-contract cases must declare a fault object")
    if set(fault) != {"point", "contract"}:
        raise FaultContractError("fault must contain exactly point and contract")

    point = fault.get("point")
    contract = fault.get("contract")
    if not isinstance(point, str) or not isinstance(contract, str):
        raise FaultContractError("fault point and contract must be strings")
    expected_contracts = FAULT_POINT_CONTRACTS.get(point)
    if expected_contracts is None:
        raise FaultContractError(f"fault point is not allow-listed: {point!r}")
    if contract not in expected_contracts:
        raise FaultContractError(f"fault point {point!r} is not bound to contract {contract!r}")
    return mode


def _observation_rows(case_result: Mapping[str, Any]) -> list[tuple[int, Mapping[str, Any]]]:
    actions = case_result.get("actions")
    if not isinstance(actions, Sequence) or isinstance(actions, (str, bytes)):
        raise FaultContractError("fault result case must contain an actions array")

    rows: list[tuple[int, Mapping[str, Any]]] = []
    for action_index, action in enumerate(actions):
        if not isinstance(action, Mapping):
            raise FaultContractError("fault result action must be an object")
        observations = action.get("observations")
        if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
            raise FaultContractError("fault result action must contain an observations array")
        for observation in observations:
            if not isinstance(observation, Mapping):
                raise FaultContractError("fault result observation must be an object")
            rows.append((action_index, observation))
    return rows


def _error_action(case_result: Mapping[str, Any]) -> tuple[Sequence[Any], int, Mapping[str, Any]]:
    if case_result.get("status") != "completed":
        raise FaultContractError("fault-contract case did not complete")

    actions = case_result.get("actions")
    rows = _observation_rows(case_result)
    error_observations = [
        (action_index, observation)
        for action_index, observation in rows
        if observation.get("kind") == "application_error"
    ]
    if len(error_observations) != 1:
        raise FaultContractError(
            "route invocation fault must produce exactly one application_error observation"
        )

    error_action_index, error_observation = error_observations[0]
    if error_observation.get("selector") != "exception":
        raise FaultContractError("application_error observation must select exception")
    error_values = error_observation.get("values")
    if not isinstance(error_values, Mapping):
        raise FaultContractError("application_error observation values must be an object")
    if error_values.get("exception_class") != "builtins.RuntimeError":
        raise FaultContractError("route invocation fault must expose builtins.RuntimeError")
    if actions[error_action_index].get("status") != "completed":
        raise FaultContractError("captured application_error action must complete")
    return actions, error_action_index, error_observation


def _assert_server_error_response(actions: Sequence[Any], error_action_index: int) -> None:
    send_observations = [
        observation
        for action_index, observation in _observation_rows({"actions": actions})
        if action_index == error_action_index and observation.get("kind") == "asgi_send"
    ]
    if len(send_observations) != 1:
        raise FaultContractError("injected HTTP error must have exactly one ASGI send observation")
    values = send_observations[0].get("values")
    if not isinstance(values, Mapping) or values.get("message_types") != [
        "http.response.start",
        "http.response.body",
    ]:
        raise FaultContractError("injected HTTP error must send the complete ASGI 500 response")

    responses = [
        observation
        for action_index, observation in _observation_rows({"actions": actions})
        if action_index == error_action_index and observation.get("kind") == "http_response"
    ]
    if len(responses) != 1:
        raise FaultContractError("injected HTTP error must expose exactly one HTTP response")
    response_values = responses[0].get("values")
    if not isinstance(response_values, Mapping) or response_values.get("status") != 500:
        raise FaultContractError("injected HTTP error must expose an HTTP 500 response")


def _later_successful_http_responses(
    actions: Sequence[Any], error_action_index: int
) -> list[Mapping[str, Any]]:
    return [
        observation
        for action_index, observation in _observation_rows({"actions": actions})
        if action_index > error_action_index
        and observation.get("kind") == "http_response"
        and isinstance(observation.get("values"), Mapping)
        and type(observation["values"].get("status")) is int
        and observation["values"].get("status") == 200
        and actions[action_index].get("status") == "completed"
    ]


def _assert_http_route_invocation_error_and_recovery(
    case_result: Mapping[str, Any],
) -> None:
    actions, error_action_index, _ = _error_action(case_result)
    _assert_server_error_response(actions, error_action_index)

    if not _later_successful_http_responses(actions, error_action_index):
        raise FaultContractError(
            "a later completed action must expose an HTTP response with status 200"
        )


def _assert_http_route_invocation_error_cleans_dependencies(
    case_result: Mapping[str, Any],
) -> None:
    actions, error_action_index, _ = _error_action(case_result)
    _assert_server_error_response(actions, error_action_index)

    responses = _later_successful_http_responses(actions, error_action_index)
    if len(responses) != 1:
        raise FaultContractError(
            "dependency cleanup fault must have one later completed HTTP 200 response"
        )
    body = responses[0]["values"].get("body")
    if not isinstance(body, Mapping) or body.get("encoding") != "base64":
        raise FaultContractError("dependency cleanup recovery body must use the base64 selector")
    data = body.get("data")
    if not isinstance(data, str):
        raise FaultContractError("dependency cleanup recovery body must contain base64 data")
    try:
        observed = json.loads(base64.b64decode(data, validate=True))
    except (ValueError, json.JSONDecodeError) as exc:
        raise FaultContractError("dependency cleanup recovery body must be JSON") from exc
    if observed != {"events": ["dependency-enter", "dependency-cleanup"]}:
        raise FaultContractError(
            "request dependency cleanup must run once before the endpoint and recovery request"
        )


def _assert_http_route_invocation_error_orders_scoped_dependency_cleanup(
    case_result: Mapping[str, Any],
) -> None:
    actions, error_action_index, _ = _error_action(case_result)
    _assert_server_error_response(actions, error_action_index)

    responses = _later_successful_http_responses(actions, error_action_index)
    if len(responses) != 1:
        raise FaultContractError(
            "scoped dependency fault must have one later completed HTTP 200 response"
        )
    body = responses[0]["values"].get("body")
    if not isinstance(body, Mapping) or body.get("encoding") != "base64":
        raise FaultContractError("scoped dependency recovery body must use the base64 selector")
    data = body.get("data")
    if not isinstance(data, str):
        raise FaultContractError("scoped dependency recovery body must contain base64 data")
    try:
        observed = json.loads(base64.b64decode(data, validate=True))
    except (ValueError, json.JSONDecodeError) as exc:
        raise FaultContractError("scoped dependency recovery body must be JSON") from exc
    if observed != {"events": FUNCTION_REQUEST_ERROR_EVENTS}:
        raise FaultContractError(
            "function- and request-scope dependencies must clean up before the "
            "unhandled error response is sent"
        )


def _assert_http_400_error_response(case_result: Mapping[str, Any], context: str) -> None:
    if case_result.get("status") != "completed":
        raise FaultContractError(f"{context} case did not complete")
    responses = [
        observation
        for _, observation in _observation_rows(case_result)
        if observation.get("kind") == "http_response"
    ]
    if len(responses) != 1:
        raise FaultContractError(f"{context} must expose exactly one HTTP response")
    values = responses[0].get("values")
    if not isinstance(values, Mapping) or type(values.get("status")) is not int:
        raise FaultContractError(f"{context} response must expose an integer status")
    if values["status"] != 400:
        raise FaultContractError(f"{context} must expose HTTP 400")
    body = values.get("body")
    if not isinstance(body, Mapping) or body.get("encoding") != "base64":
        raise FaultContractError(f"{context} response body must use base64 encoding")
    encoded_body = body.get("data")
    if not isinstance(encoded_body, str):
        raise FaultContractError(f"{context} response body must contain base64 data")
    try:
        observed_body = json.loads(base64.b64decode(encoded_body, validate=True))
    except (ValueError, json.JSONDecodeError) as exc:
        raise FaultContractError(f"{context} response body must be JSON") from exc
    if observed_body != {"detail": "There was an error parsing the body"}:
        raise FaultContractError(f"{context} must expose FastAPI's 400 detail")


def _assert_http_body_json_decode_error_returns_400(case_result: Mapping[str, Any]) -> None:
    _assert_http_400_error_response(case_result, "JSON body decode fault")


def _assert_http_body_form_parse_error_returns_400(case_result: Mapping[str, Any]) -> None:
    _assert_http_400_error_response(case_result, "Form parse fault")


def _assert_http_response_status(
    case_result: Mapping[str, Any], expected_status: int, context: str
) -> None:
    if case_result.get("status") != "completed":
        raise FaultContractError(f"{context} case did not complete")
    responses = [
        observation
        for _, observation in _observation_rows(case_result)
        if observation.get("kind") == "http_response"
    ]
    if len(responses) != 1:
        raise FaultContractError(f"{context} must expose exactly one HTTP response")
    values = responses[0].get("values")
    if not isinstance(values, Mapping) or type(values.get("status")) is not int:
        raise FaultContractError(f"{context} response must expose an integer status")
    if values["status"] != expected_status:
        raise FaultContractError(f"{context} must expose HTTP {expected_status}")


def _assert_http_frontend_lookup_permission_denied_401(
    case_result: Mapping[str, Any],
) -> None:
    _assert_http_response_status(case_result, 401, "Frontend PermissionError lookup fault")


def _assert_http_frontend_lookup_value_error_404(case_result: Mapping[str, Any]) -> None:
    _assert_http_response_status(case_result, 404, "Frontend ValueError lookup fault")


def _assert_http_frontend_lookup_name_too_long_404(
    case_result: Mapping[str, Any],
) -> None:
    _assert_http_response_status(case_result, 404, "Frontend ENAMETOOLONG lookup fault")


def _assert_http_frontend_lookup_os_error_propagates(
    case_result: Mapping[str, Any],
) -> None:
    if case_result.get("status") != "completed":
        raise FaultContractError("Frontend OSError lookup fault case did not complete")
    errors = [
        (action_index, observation)
        for action_index, observation in _observation_rows(case_result)
        if observation.get("kind") == "application_error"
    ]
    if len(errors) != 1:
        raise FaultContractError("Frontend OSError lookup fault must expose one application error")
    action_index, observation = errors[0]
    values = observation.get("values")
    if (
        observation.get("selector") != "exception"
        or not isinstance(values, Mapping)
        or values.get("exception_class") != "builtins.OSError"
    ):
        raise FaultContractError("Frontend OSError lookup fault must propagate builtins.OSError")
    actions = case_result.get("actions")
    if not isinstance(actions, Sequence) or actions[action_index].get("status") != "completed":
        raise FaultContractError("Frontend OSError application-error action must complete")
    _assert_http_response_status(case_result, 500, "Propagated frontend OSError lookup fault")


CONTRACT_ASSERTIONS: dict[str, Callable[[Mapping[str, Any]], None]] = {
    HTTP_ROUTE_INVOCATION_CONTRACT: _assert_http_route_invocation_error_and_recovery,
    HTTP_ROUTE_DEPENDENCY_CLEANUP_CONTRACT: _assert_http_route_invocation_error_cleans_dependencies,
    HTTP_ROUTE_SCOPED_DEPENDENCY_CLEANUP_CONTRACT: (
        _assert_http_route_invocation_error_orders_scoped_dependency_cleanup
    ),
    HTTP_REQUEST_JSON_DECODE_CONTRACT: _assert_http_body_json_decode_error_returns_400,
    HTTP_REQUEST_FORM_PARSE_CONTRACT: _assert_http_body_form_parse_error_returns_400,
    HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_CONTRACT: (
        _assert_http_frontend_lookup_permission_denied_401
    ),
    HTTP_FRONTEND_LOOKUP_VALUE_ERROR_CONTRACT: _assert_http_frontend_lookup_value_error_404,
    HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_CONTRACT: (_assert_http_frontend_lookup_name_too_long_404),
    HTTP_FRONTEND_LOOKUP_OS_ERROR_CONTRACT: _assert_http_frontend_lookup_os_error_propagates,
}


def assert_fault_contract(case: Mapping[str, Any], case_result: Mapping[str, Any]) -> None:
    """Validate a fault case and assert its named public contract on its result."""
    if verification_mode(case) != "fault-contract":
        raise FaultContractError("public fault assertions require a fault-contract case")

    fault = case["fault"]
    contract = fault["contract"]
    assertion = CONTRACT_ASSERTIONS.get(contract)
    if assertion is None:
        raise FaultContractError(f"fault contract is not registered: {contract!r}")
    assertion(case_result)
