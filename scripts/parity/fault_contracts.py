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

# metadata.yaml is the policy authority; metadata-check enforces this runtime
# dispatch table against the reviewed registry.
FAULT_POINT_CONTRACTS: dict[str, str] = {
    HTTP_ROUTE_INVOCATION_FAULT_POINT: HTTP_ROUTE_INVOCATION_CONTRACT,
    HTTP_ROUTE_DEPENDENCY_CLEANUP_FAULT_POINT: HTTP_ROUTE_DEPENDENCY_CLEANUP_CONTRACT,
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
    expected_contract = FAULT_POINT_CONTRACTS.get(point)
    if expected_contract is None:
        raise FaultContractError(f"fault point is not allow-listed: {point!r}")
    if contract != expected_contract:
        raise FaultContractError(
            f"fault point {point!r} is bound to contract {expected_contract!r}, not {contract!r}"
        )
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


CONTRACT_ASSERTIONS: dict[str, Callable[[Mapping[str, Any]], None]] = {
    HTTP_ROUTE_INVOCATION_CONTRACT: _assert_http_route_invocation_error_and_recovery,
    HTTP_ROUTE_DEPENDENCY_CLEANUP_CONTRACT: _assert_http_route_invocation_error_cleans_dependencies,
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
