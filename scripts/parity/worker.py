"""Run input-only FastAPI workflows in one isolated Python product process."""

from __future__ import annotations

import argparse
import asyncio
import base64
import copy
import datetime as dt
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import platform
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_SCHEMA_ID = "fastapi-rs/python-asgi-workflow@2"
WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-asgi-workflow@3"
RESULT_SCHEMA_ID = "fastapi-rs/python-asgi-workflow-result@2"
RESULT_SCHEMA_V3_ID = "fastapi-rs/python-asgi-workflow-result@3"
ORACLE_PROFILE_ID = "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13"
ORACLE_PROFILE_PACKAGE_EXTENSIONS = {
    "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-standard-multipart-0.0.32": {
        "python-multipart": "0.0.32"
    }
}
ORACLE_BASE_PACKAGES = {
    "annotated-doc": "0.0.4",
    "annotated-types": "0.7.0",
    "anyio": "4.12.1",
    "fastapi": "0.141.1",
    "idna": "3.18",
    "pydantic": "2.13.4",
    "pydantic-core": "2.46.4",
    "starlette": "1.6.0",
    "typing-extensions": "4.16.0",
    "typing-inspection": "0.4.2",
}
PINNED_SOURCE_COMMITS = {
    "fastapi": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
    "starlette": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
}
PINNED_SOURCE_VERSIONS = {"fastapi": "0.141.1", "starlette": "1.6.0"}


class WorkerError(ValueError):
    """A product worker identity or execution contract error."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit(path: Path, label: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if completed.returncode != 0:
        raise WorkerError(f"cannot identify {label} source revision: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _assert_clean_source_tree(
    path: Path,
    label: str,
    *,
    allowed_untracked: frozenset[str] = frozenset(),
) -> None:
    """Reject working-tree changes that could change the imported oracle."""
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ],
        check=False,
        capture_output=True,
        timeout=10,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise WorkerError(f"cannot inspect {label} source working tree: {detail}")

    dirty_paths: list[str] = []
    for record in completed.stdout.split(b"\0"):
        if not record:
            continue
        status = record[:2].decode("ascii", errors="replace")
        separator = 3
        source_path = record[separator:].decode("utf-8", errors="replace")
        if status == "??" and source_path in allowed_untracked:
            continue
        dirty_paths.append(source_path)
    if dirty_paths:
        paths = ", ".join(sorted(dirty_paths))
        raise WorkerError(f"{label} source working tree is dirty: {paths}")


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _validate_workload_path(path: Path) -> Path:
    """Keep executable parity workloads inside the reviewed fixture directory."""
    resolved = path.resolve()
    workload_root = ROOT / "tests/fixtures/workloads"
    if not _is_under(resolved, workload_root):
        raise WorkerError("workflow workload must live under tests/fixtures/workloads")
    return resolved


def _oracle_identity(
    fastapi_root: Path,
    starlette_root: Path,
    profile: dict[str, Any],
) -> dict[str, Any]:
    profile_id = profile.get("id")
    added_packages = ORACLE_PROFILE_PACKAGE_EXTENSIONS.get(profile_id)
    if profile_id == ORACLE_PROFILE_ID:
        added_packages = {}
    elif added_packages is None:
        raise WorkerError("worker received an unsupported oracle profile")
    if profile.get("packages") != {**ORACLE_BASE_PACKAGES, **added_packages}:
        raise WorkerError("worker received an unsupported oracle package set")
    expected_commits = profile["source_commits"]
    if expected_commits != PINNED_SOURCE_COMMITS:
        raise WorkerError("oracle profile does not select the pinned FastAPI/Starlette commits")
    packages = profile["packages"]
    for distribution, version in PINNED_SOURCE_VERSIONS.items():
        if packages.get(distribution) != version:
            raise WorkerError(f"oracle profile does not select {distribution} {version}")

    _assert_clean_source_tree(fastapi_root, "FastAPI")
    _assert_clean_source_tree(
        starlette_root,
        "Starlette",
        allowed_untracked=frozenset({".DS_Store"}),
    )
    fastapi_commit = _git_commit(fastapi_root, "FastAPI")
    starlette_commit = _git_commit(starlette_root, "Starlette")
    if fastapi_commit != expected_commits["fastapi"]:
        raise WorkerError(f"FastAPI source commit mismatch: {fastapi_commit}")
    if starlette_commit != expected_commits["starlette"]:
        raise WorkerError(f"Starlette source commit mismatch: {starlette_commit}")
    import fastapi  # noqa: PLC0415
    import starlette  # noqa: PLC0415

    if not _is_under(Path(fastapi.__file__), fastapi_root / "fastapi"):
        raise WorkerError(
            f"FastAPI imported outside the pinned source checkout: {fastapi.__file__}"
        )
    if not _is_under(Path(starlette.__file__), starlette_root / "starlette"):
        raise WorkerError(
            f"Starlette imported outside the selected 1.6.0 checkout: {starlette.__file__}"
        )

    actual_packages: dict[str, str] = {}
    for distribution, expected_version in packages.items():
        try:
            actual_version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError as exc:
            raise WorkerError(f"oracle package is missing: {distribution}") from exc
        if actual_version != str(expected_version):
            raise WorkerError(
                f"oracle package version mismatch for {distribution}: "
                f"expected {expected_version}, got {actual_version}"
            )
        actual_packages[distribution] = actual_version

    python_identity = {
        "implementation": platform.python_implementation(),
        "version": platform.python_version(),
    }
    if python_identity != profile["python"]:
        raise WorkerError(f"oracle Python identity mismatch: {python_identity}")

    return {
        "distribution": "fastapi",
        "version": actual_packages["fastapi"],
        "python": python_identity,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "repositories": {
            "fastapi_source": fastapi_commit,
            "starlette_source": starlette_commit,
            "fastapi_rs": None,
            "starlette_rs": None,
        },
        "target_revision": None,
        "source_tree_sha256": None,
        "target_binary_sha256": None,
        "packages": actual_packages,
    }


def _load_workload(workload_path: Path, input_digest: str, factory_name: str) -> Any:
    module_name = f"fastapi_rs_parity_workload_{input_digest[:16]}"
    spec = importlib.util.spec_from_file_location(module_name, workload_path)
    if spec is None or spec.loader is None:
        raise WorkerError(f"cannot load workload module: {workload_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    factory = getattr(module, factory_name, None)
    if not callable(factory):
        raise WorkerError(f"workload factory is not callable: {factory_name}")
    return factory


def _make_scope(encoded_scope: dict[str, Any]) -> dict[str, Any]:
    scope = dict(encoded_scope)
    scope["asgi"] = dict(encoded_scope["asgi"])
    scope["query_string"] = encoded_scope["query_string"].encode("ascii")
    scope["headers"] = [
        (name.encode("ascii"), value.encode("utf-8")) for name, value in encoded_scope["headers"]
    ]
    scope["client"] = (
        tuple(encoded_scope["client"]) if encoded_scope["client"] is not None else None
    )
    scope["server"] = (
        tuple(encoded_scope["server"]) if encoded_scope["server"] is not None else None
    )
    raw_path = encoded_scope.get("raw_path_base64")
    scope["raw_path"] = (
        base64.b64decode(raw_path, validate=True)
        if raw_path
        else encoded_scope["path"].encode("utf-8")
    )
    scope.pop("raw_path_base64", None)
    return scope


def _make_receive(
    events: list[dict[str, Any]], event_trace: list[dict[str, Any]] | None = None
) -> Any:
    messages = []
    for event in events:
        message = {key: value for key, value in event.items() if key != "bytes_base64"}
        if event["type"] == "http.request":
            message["body"] = event["body"].encode("utf-8")
        elif event["type"] == "websocket.receive" and "bytes_base64" in event:
            message["bytes"] = base64.b64decode(event["bytes_base64"], validate=True)
        messages.append(message)
    offset = 0
    last_websocket_disconnect = next(
        (message for message in reversed(messages) if message["type"] == "websocket.disconnect"),
        None,
    )

    async def receive() -> dict[str, Any]:
        nonlocal offset
        if offset < len(messages):
            message = messages[offset]
            offset += 1
        elif last_websocket_disconnect is not None:
            message = last_websocket_disconnect
        elif messages and messages[0]["type"] == "websocket.connect":
            # Workflows are validated to carry a terminal disconnect event.
            raise WorkerError("validated WebSocket input lost its terminal disconnect event")
        else:
            message = {"type": "http.disconnect"}
        if event_trace is not None:
            event_trace.append({"direction": "receive", **copy.deepcopy(message)})
        return message

    return receive


def _encoded_bytes(value: bytes) -> dict[str, str]:
    return {"encoding": "base64", "data": base64.b64encode(value).decode("ascii")}


def _header_pairs(headers: Any) -> list[list[str]]:
    if not isinstance(headers, (list, tuple)):
        raise TypeError("ASGI response headers are not a sequence")
    pairs: list[list[str]] = []
    for pair in headers:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise TypeError("ASGI response header is not a byte pair")
        name, value = pair
        if not isinstance(name, bytes) or not isinstance(value, bytes):
            raise TypeError("ASGI response header values must be bytes")
        pairs.append(
            [base64.b64encode(name).decode("ascii"), base64.b64encode(value).decode("ascii")]
        )
    return pairs


def _pointer_get(document: Any, pointer: str) -> tuple[bool, Any]:
    value = document
    for escaped_segment in pointer.split("/")[1:]:
        segment = escaped_segment.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and segment in value:
            value = value[segment]
        elif isinstance(value, list) and segment.isdecimal():
            index = int(segment)
            if index >= len(value):
                return False, None
            value = value[index]
        else:
            return False, None
    return True, value


def _observe(
    observations: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    *,
    validation_error_class: str | None = None,
    event_trace: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    starts = [message for message in messages if message.get("type") == "http.response.start"]
    start = starts[0] if starts else None
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message.get("type") == "http.response.body"
    )
    message_types = [message.get("type") for message in messages]
    result: list[dict[str, Any]] = []
    for index, observation in enumerate(observations):
        kind = observation["kind"]
        if kind == "http_response":
            values: dict[str, Any] = {}
            selectors = observation["selectors"]
            if "status" in selectors:
                values["status"] = start.get("status") if start is not None else None
            if "headers" in selectors:
                values["headers"] = (
                    _header_pairs(start.get("headers", [])) if start is not None else []
                )
            if "body" in selectors:
                values["body"] = _encoded_bytes(body)
            result.append({"index": index, "kind": kind, "values": values})
        elif kind == "openapi":
            try:
                document = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                values = {"body_status": "invalid-json", "pointers": []}
            else:
                pointers = []
                for pointer in observation["json_pointers"]:
                    present, selected = _pointer_get(document, pointer)
                    entry = {"pointer": pointer, "present": present}
                    if present:
                        entry["value"] = selected
                    pointers.append(entry)
                values = {"body_status": "parsed", "pointers": pointers}
            result.append({"index": index, "kind": kind, "values": values})
        elif kind == "asgi_send":
            result.append(
                {"index": index, "kind": kind, "values": {"message_types": message_types}}
            )
        elif kind == "application_error":
            result.append(
                {"index": index, "kind": kind, "values": {"class": validation_error_class}}
            )
        elif kind == "websocket":
            selector = observation["selector"]
            trace = event_trace or []
            if selector == "close_code":
                close_events = [
                    message for message in messages if message.get("type") == "websocket.close"
                ]
                value = close_events[-1].get("code") if close_events else None
                values = {"close_code": value}
            elif selector == "close_reason":
                close_events = [
                    message for message in messages if message.get("type") == "websocket.close"
                ]
                value = close_events[-1].get("reason") if close_events else None
                values = {"close_reason": value}
            elif selector == "event_order":
                values = {"event_order": [event["type"] for event in trace]}
            elif selector == "messages":
                payloads = []
                for event in trace:
                    if event.get("type") not in {"websocket.receive", "websocket.send"}:
                        continue
                    if "text" in event:
                        payloads.append(
                            {
                                "direction": event["direction"],
                                "kind": "text",
                                "value": event["text"],
                            }
                        )
                    elif "bytes" in event:
                        payloads.append(
                            {
                                "direction": event["direction"],
                                "kind": "bytes",
                                "value": _encoded_bytes(event["bytes"]),
                            }
                        )
                values = {"messages": payloads}
            else:
                raise WorkerError(f"worker does not support WebSocket selector: {selector}")
            result.append({"index": index, "kind": kind, "selector": selector, "values": values})
        else:
            raise WorkerError(f"worker does not support observation kind: {kind}")
    return result


async def _run_case(case: dict[str, Any], factory: Any) -> dict[str, Any]:
    try:
        app = factory()
        if inspect.isawaitable(app):
            app = await app
        if not callable(app):
            raise TypeError("workload factory did not return an ASGI callable")
    except Exception as exc:
        return {
            "case_id": case["case_id"],
            "status": "product_error",
            "error": {"class": type(exc).__name__, "message": str(exc)},
            "actions": [],
        }

    action_results = []
    first_error: dict[str, str] | None = None
    for action in case["actions"]:
        scope = _make_scope(action["scope"])
        event_trace: list[dict[str, Any]] = []
        receive = _make_receive(action["receive_events"], event_trace)
        messages: list[dict[str, Any]] = []
        captures_validation_error_class = any(
            observation["kind"] == "application_error"
            and observation["selector"] == "validation_error_class"
            for observation in action["observations"]
        )

        dispatch_error: Exception | None = None
        try:
            await app(scope, receive, _make_send(messages, event_trace))
        except Exception as exc:
            dispatch_error = exc

        if dispatch_error is not None and not captures_validation_error_class:
            error = {
                "class": type(dispatch_error).__name__,
                "message": str(dispatch_error),
            }
            first_error = first_error or error
            action_results.append(
                {
                    "action_id": action["action_id"],
                    "status": "product_error",
                    "error": error,
                    "observations": [],
                }
            )
            continue

        try:
            qualified_error_class = None
            if dispatch_error is not None:
                error_type = type(dispatch_error)
                qualified_error_class = f"{error_type.__module__}.{error_type.__qualname__}"
            observations = _observe(
                action["observations"],
                messages,
                validation_error_class=qualified_error_class,
                event_trace=event_trace,
            )
            action_results.append(
                {
                    "action_id": action["action_id"],
                    "status": "completed",
                    "observations": observations,
                }
            )
        except Exception as exc:
            error = {"class": type(exc).__name__, "message": str(exc)}
            first_error = first_error or error
            action_results.append(
                {
                    "action_id": action["action_id"],
                    "status": "product_error",
                    "error": error,
                    "observations": [],
                }
            )

    result: dict[str, Any] = {
        "case_id": case["case_id"],
        "status": "product_error" if first_error else "completed",
        "actions": action_results,
    }
    if first_error:
        result["error"] = first_error
    return result


def _qualified_exception(exc: Exception) -> dict[str, str]:
    error_type = type(exc)
    return {
        "class": f"{error_type.__module__}.{error_type.__qualname__}",
        "message": str(exc),
    }


def _observe_lifespan(
    observations: list[dict[str, Any]],
    protocol_event_trace: list[dict[str, str]],
    lifecycle_results: dict[str, dict[str, Any]],
    application_errors: list[dict[str, str]],
    workload_trace: list[str],
) -> list[dict[str, Any]]:
    event_order = [
        f"{event['stage']}:{event['direction']}:{event['type']}" for event in protocol_event_trace
    ]

    result = []
    for index, observation in enumerate(observations):
        selector = observation["selector"]
        if selector == "event_order":
            values = {"event_order": event_order}
        elif selector in {"startup", "shutdown"}:
            values = {selector: copy.deepcopy(lifecycle_results[selector])}
        elif selector == "application_errors":
            values = {"application_errors": copy.deepcopy(application_errors)}
        elif selector == "workload_trace":
            values = {"workload_trace": copy.deepcopy(workload_trace)}
        else:
            raise WorkerError(f"worker does not support ASGI lifespan selector: {selector}")
        result.append(
            {
                "index": index,
                "kind": "asgi_lifespan",
                "selector": selector,
                "values": values,
            }
        )
    return result


async def _run_action_v3(
    action: dict[str, Any],
    app: Any,
    *,
    lifespan_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scope = _make_scope(action["scope"])
    if lifespan_state is not None:
        # ASGI servers make a shallow copy of lifespan state for each request scope.
        scope["state"] = copy.copy(lifespan_state)
    event_trace: list[dict[str, Any]] = []
    receive = _make_receive(action["receive_events"], event_trace)
    messages: list[dict[str, Any]] = []
    captures_validation_error_class = any(
        observation["kind"] == "application_error"
        and observation["selector"] == "validation_error_class"
        for observation in action["observations"]
    )

    dispatch_error: Exception | None = None
    try:
        await app(scope, receive, _make_send(messages, event_trace))
    except Exception as exc:
        dispatch_error = exc

    if dispatch_error is not None and not captures_validation_error_class:
        return {
            "action_id": action["action_id"],
            "status": "product_error",
            "error": {"class": type(dispatch_error).__name__, "message": str(dispatch_error)},
            "observations": [],
        }

    try:
        qualified_error_class = None
        if dispatch_error is not None:
            error_type = type(dispatch_error)
            qualified_error_class = f"{error_type.__module__}.{error_type.__qualname__}"
        observations = _observe(
            action["observations"],
            messages,
            validation_error_class=qualified_error_class,
            event_trace=event_trace,
        )
    except Exception as exc:
        return {
            "action_id": action["action_id"],
            "status": "product_error",
            "error": {"class": type(exc).__name__, "message": str(exc)},
            "observations": [],
        }
    return {
        "action_id": action["action_id"],
        "status": "completed",
        "observations": observations,
    }


async def _run_lifespan_action_v3(
    action: dict[str, Any],
    app: Any,
    request_actions: list[dict[str, Any]],
    workload_trace: list[str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    """Run ASGI lifespan around request actions and always signal shutdown after startup."""
    incoming: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    outgoing: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    protocol_event_trace: list[dict[str, str]] = []
    application_errors: list[dict[str, str]] = []
    lifecycle_results = {
        "startup": {
            "outcome": "no_response",
            "response_type": None,
            "message": None,
        },
        "shutdown": {
            "outcome": "not_sent",
            "response_type": None,
            "message": None,
        },
    }
    stage = "startup"
    reported_exception_ids: set[int] = set()

    async def receive() -> dict[str, Any]:
        message = await incoming.get()
        protocol_event_trace.append(
            {"stage": stage, "direction": "receive", "type": str(message["type"])}
        )
        return message

    async def send(message: dict[str, Any]) -> None:
        if not isinstance(message, dict):
            raise TypeError("ASGI lifespan send message must be a mapping")
        captured = copy.deepcopy(message)
        message_type = str(captured.get("type", "<missing-type>"))
        protocol_event_trace.append({"stage": stage, "direction": "send", "type": message_type})
        await outgoing.put(captured)

    scope = {
        "type": "lifespan",
        "asgi": {"version": "3.0", "spec_version": "2.0"},
        "state": copy.deepcopy(action.get("initial_state", {})),
    }
    application_task = asyncio.create_task(app(scope, receive, send))

    async def exchange(stage_name: str, event_type: str) -> dict[str, Any] | None:
        nonlocal stage
        stage = stage_name
        # Even if the application has already returned, enqueue the shutdown input
        # after successful startup so cleanup is attempted in the ASGI protocol.
        await incoming.put({"type": event_type})
        response_task = asyncio.create_task(outgoing.get())
        done, _ = await asyncio.wait(
            {response_task, application_task}, return_when=asyncio.FIRST_COMPLETED
        )
        response = response_task.result() if response_task in done else None
        if response_task not in done:
            response_task.cancel()
            await asyncio.gather(response_task, return_exceptions=True)
        if application_task.done() and not application_task.cancelled():
            try:
                error = application_task.exception()
            except asyncio.CancelledError:
                error = None
            if error is not None and id(error) not in reported_exception_ids:
                reported_exception_ids.add(id(error))
                application_errors.append({"stage": stage_name, **_qualified_exception(error)})
        response_type = (
            str(response.get("type")) if isinstance(response, dict) and "type" in response else None
        )
        message = (
            response.get("message")
            if isinstance(response, dict) and isinstance(response.get("message"), str)
            else None
        )
        if response_type == f"{event_type}.complete":
            outcome = "complete"
        elif response_type == f"{event_type}.failed":
            outcome = "failed"
        elif response is not None:
            outcome = "unexpected"
        elif any(error["stage"] == stage_name for error in application_errors):
            outcome = "error"
        else:
            outcome = "no_response"
        lifecycle_results[stage_name] = {
            "outcome": outcome,
            "response_type": response_type,
            "message": message,
        }
        return response

    lifecycle_state: dict[str, Any] | None = {}
    startup_response = await exchange("startup", "lifespan.startup")
    startup_succeeded = (
        startup_response is not None and startup_response.get("type") == "lifespan.startup.complete"
    )
    if startup_succeeded:
        state = startup_response.get("state")
        if isinstance(state, dict):
            lifecycle_state = state
        else:
            lifecycle_state = scope["state"]
        if not isinstance(lifecycle_state, dict):
            lifecycle_state = {}

    action_results: dict[str, dict[str, Any]] = {}
    if startup_succeeded:
        try:
            for request_action in request_actions:
                action_results[request_action["action_id"]] = await _run_action_v3(
                    request_action,
                    app,
                    lifespan_state=lifecycle_state,
                )
        finally:
            # The same application and lifespan task stay live until request actions
            # finish. Cleanup executes even when a request action raises unexpectedly.
            await exchange("shutdown", "lifespan.shutdown")
            if not application_task.done():
                try:
                    await application_task
                except Exception as exc:
                    if id(exc) not in reported_exception_ids:
                        reported_exception_ids.add(id(exc))
                        application_errors.append(
                            {"stage": "shutdown", **_qualified_exception(exc)}
                        )
    else:
        for request_action in request_actions:
            action_results[request_action["action_id"]] = {
                "action_id": request_action["action_id"],
                "status": "not_run",
                "reason": "ASGI lifespan startup did not complete",
                "observations": [],
            }
        if not application_task.done():
            application_task.cancel()
        await asyncio.gather(application_task, return_exceptions=True)

    lifespan_result = {
        "action_id": action["action_id"],
        "status": "completed",
        "observations": _observe_lifespan(
            action["observations"],
            protocol_event_trace,
            lifecycle_results,
            application_errors,
            workload_trace,
        ),
    }
    action_results[action["action_id"]] = lifespan_result
    return lifespan_result, action_results


async def _run_case_v3(case: dict[str, Any], factory: Any) -> dict[str, Any]:
    workload_trace: list[str] = []
    try:
        app = factory(copy.deepcopy(case["factory_input"]), workload_trace)
        if inspect.isawaitable(app):
            app = await app
        if not callable(app):
            raise TypeError("workload factory did not return an ASGI callable")
    except Exception as exc:
        error = _qualified_exception(exc)
        construction = {
            "kind": "construction",
            "selectors": ["outcome", "exception_class", "exception_message"],
            "values": {
                "outcome": "error",
                "exception_class": error["class"],
                "exception_message": error["message"],
            },
        }
        action_results = [
            {
                "action_id": action["action_id"],
                "status": "not_run",
                "reason": "application construction failed",
                "observations": [],
            }
            for action in case["actions"]
        ]
        return {
            "case_id": case["case_id"],
            "status": "completed",
            "construction_observation": construction,
            "actions": action_results,
        }

    construction = {
        "kind": "construction",
        "selectors": ["outcome", "exception_class", "exception_message"],
        "values": {
            "outcome": "ok",
            "exception_class": None,
            "exception_message": None,
        },
    }
    actions = case["actions"]
    if actions and actions[0]["kind"] == "lifespan":
        lifespan_action = actions[0]
        _, action_results = await _run_lifespan_action_v3(
            app, lifespan_action, actions[1:], workload_trace
        )
        ordered_results = [action_results[action["action_id"]] for action in actions]
    else:
        ordered_results = [await _run_action_v3(action, app) for action in actions]
    return {
        "case_id": case["case_id"],
        "status": "completed",
        "construction_observation": construction,
        "actions": ordered_results,
    }


def _make_send(
    messages: list[dict[str, Any]], event_trace: list[dict[str, Any]] | None = None
) -> Any:
    async def send(message: dict[str, Any]) -> None:
        captured = copy.deepcopy(message)
        messages.append(captured)
        if event_trace is not None:
            event_trace.append({"direction": "send", **copy.deepcopy(captured)})

    return send


async def _run_cases(workflow: dict[str, Any], factory: Any) -> list[dict[str, Any]]:
    results = []
    for case in workflow["cases"]:
        results.append(await _run_case(case, factory))
    return results


async def _run_cases_v3(workflow: dict[str, Any], factory: Any) -> list[dict[str, Any]]:
    results = []
    for case in workflow["cases"]:
        results.append(await _run_case_v3(case, factory))
    return results


def run_oracle(
    input_path: Path,
    fastapi_root: Path,
    starlette_root: Path,
    *,
    input_sha256: str,
    workload_sha256: str,
    manifest_sha256: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    if Path.cwd().resolve() != ROOT:
        raise WorkerError(f"worker must run from the repository root: {ROOT}")
    workflow_path = input_path.resolve()
    try:
        workflow_path.relative_to(ROOT)
    except ValueError as exc:
        raise WorkerError("workflow input must live inside the repository") from exc
    if _sha256_file(workflow_path) != input_sha256:
        raise WorkerError("workflow input changed after host-side validation")
    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkerError(f"cannot read validated workflow: {exc}") from exc
    if not isinstance(workflow, dict) or workflow.get("schema") not in {
        WORKFLOW_SCHEMA_ID,
        WORKFLOW_SCHEMA_V3_ID,
    }:
        raise WorkerError("workflow schema identity changed after host-side validation")
    fastapi_root = fastapi_root.resolve()
    starlette_root = starlette_root.resolve()
    workload_path = _validate_workload_path(ROOT / workflow["workload"]["file"])
    try:
        workload_path.relative_to(ROOT)
    except ValueError as exc:
        raise WorkerError("validated workload file resolves outside the repository") from exc
    if _sha256_file(workload_path) != workload_sha256:
        raise WorkerError("workload file changed after host-side validation")
    started = dt.datetime.now(dt.UTC)
    identity = _oracle_identity(fastapi_root, starlette_root, profile)
    factory = _load_workload(workload_path, input_sha256, workflow["workload"]["factory"])
    if workflow["schema"] == WORKFLOW_SCHEMA_V3_ID:
        cases = asyncio.run(_run_cases_v3(workflow, factory))
        result_schema_id = RESULT_SCHEMA_V3_ID
    else:
        cases = asyncio.run(_run_cases(workflow, factory))
        result_schema_id = RESULT_SCHEMA_ID
    finished = dt.datetime.now(dt.UTC)
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    result = {
        "schema": result_schema_id,
        "run_id": str(uuid.uuid4()),
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "product": "oracle",
        "identity": identity,
        "manifest": {
            "path": manifest_path.relative_to(ROOT).as_posix(),
            "sha256": manifest_sha256,
        },
        "input": {
            "path": workflow_path.relative_to(ROOT).as_posix(),
            "sha256": input_sha256,
            "schema": workflow["schema"],
        },
        "workload": {
            "path": workload_path.relative_to(ROOT).as_posix(),
            "sha256": workload_sha256,
            "factory": workflow["workload"]["factory"],
        },
        "command": {
            "argv": [sys.executable, "-m", "scripts.parity.worker", *sys.argv[1:]],
            "cwd": ".",
        },
        "status": "completed",
        "cases": cases,
        "infrastructure_errors": [],
    }
    expected_cases = [case["case_id"] for case in workflow["cases"]]
    actual_cases = [case["case_id"] for case in cases]
    if actual_cases != expected_cases:
        raise WorkerError("worker case result order or cardinality differs from input")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--fastapi-source", required=True, type=Path)
    parser.add_argument("--starlette-source", required=True, type=Path)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--workload-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--oracle-profile", required=True)
    args = parser.parse_args()
    try:
        profile = json.loads(args.oracle_profile)
        if not isinstance(profile, dict):
            raise WorkerError("oracle profile must be a JSON object")
        result = run_oracle(
            args.input,
            args.fastapi_source,
            args.starlette_source,
            input_sha256=args.input_sha256,
            workload_sha256=args.workload_sha256,
            manifest_sha256=args.manifest_sha256,
            profile=profile,
        )
    except Exception as exc:
        print(json.dumps({"worker_error": type(exc).__name__, "message": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
