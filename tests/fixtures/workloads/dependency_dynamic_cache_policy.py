"""Independent public inputs for dependency cache-policy evaluation timing."""

import asyncio
from collections.abc import AsyncIterator, Mapping
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, Security
from fastapi.responses import JSONResponse
from pydantic import BeforeValidator


class IndependentCachePolicyError(RuntimeError):
    pass


class BoolCachePolicy:
    def __init__(self, label: str, trace: list[str], enabled: bool = True) -> None:
        self.label = label
        self.trace = trace
        self.enabled = enabled
        self.mode = "normal"
        self.calls = 0
        self.decisions: list[bool] = []

    def __bool__(self) -> Any:
        self.calls += 1
        if self.mode != "normal":
            self.trace.append(f"policy:{self.label}:bool:{self.calls}:{self.mode}")
            if self.mode == "raise":
                raise IndependentCachePolicyError(f"{self.label} refused caching")
            if self.mode == "invalid":
                return 9
        value = (
            self.decisions[(self.calls - 1) % len(self.decisions)]
            if self.decisions
            else self.enabled
        )
        self.trace.append(f"policy:{self.label}:bool:{self.calls}:{value}")
        return value

    def describe(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "calls": self.calls,
            "mode": self.mode,
            "enabled": self.enabled,
        }


class LengthCachePolicy:
    def __init__(self, label: str, trace: list[str]) -> None:
        self.label = label
        self.trace = trace
        self.length = 1
        self.mode = "normal"
        self.calls = 0

    def __len__(self) -> int:
        self.calls += 1
        self.trace.append(f"policy:{self.label}:len:{self.calls}:{self.mode}")
        if self.mode == "raise":
            raise IndependentCachePolicyError(f"{self.label} refused its length")
        return self.length

    def describe(self) -> dict[str, Any]:
        return {"label": self.label, "calls": self.calls, "mode": self.mode, "length": self.length}


class CapturedPayload:
    def __init__(self, seed: int = 5) -> None:
        self.seed = seed


def _parameterless_app(placement: str, event_trace: list[str]) -> FastAPI:
    trace: list[str] = []
    ignored_bool = BoolCachePolicy("parameterless-bool", trace)
    ignored_length = LengthCachePolicy("parameterless-length", trace)
    calls = 0

    def counted(seed: int = 3) -> dict[str, int]:
        nonlocal calls
        calls += 1
        trace.append(f"call:parameterless:{calls}")
        return {"seed": seed, "call": calls}

    declarations = [
        Depends(counted, use_cache=ignored_bool),
        Security(counted, scopes=["independent:read"], use_cache=ignored_length),
        Depends(counted, use_cache=False),
    ]
    app = FastAPI(dependencies=declarations if placement == "app" else [])

    def read_parameterless(
        first: Annotated[dict[str, int], Depends(counted)],
        uncached: Annotated[dict[str, int], Depends(counted, use_cache=False)],
    ) -> dict[str, Any]:
        return {
            "placement": placement,
            "first": first,
            "uncached": uncached,
            "same_value": first is uncached,
            "calls": calls,
            "ignored_bool": ignored_bool.describe(),
            "ignored_length": ignored_length.describe(),
            "raw_policy_aliases": [
                declarations[0].use_cache is ignored_bool,
                declarations[1].use_cache is ignored_length,
            ],
            "literal_false_declaration": declarations[2].use_cache,
            "trace": list(trace),
            "events": list(event_trace),
        }

    if placement == "router":
        router = APIRouter(dependencies=declarations)
        router.add_api_route("/parameterless", read_parameterless, methods=["GET"])
        app.include_router(router)
    elif placement in {"app", "route"}:
        app.add_api_route(
            "/parameterless",
            read_parameterless,
            methods=["GET"],
            dependencies=declarations if placement == "route" else [],
        )
    else:
        raise ValueError("unknown parameterless placement")

    # Every declaration has already been registered; these user objects now raise
    # if the framework attempts to evaluate the ignored parameterless policies.
    ignored_bool.mode = "raise"
    ignored_length.mode = "raise"
    return app


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    placement = factory_input.get("parameterless_placement")
    if placement is not None:
        return _parameterless_app(placement, event_trace)

    app = FastAPI()
    trace: list[str] = []
    calls: dict[str, int] = {}

    def next_call(label: str) -> int:
        calls[label] = calls.get(label, 0) + 1
        trace.append(f"call:{label}:{calls[label]}")
        return calls[label]

    capture_original = BoolCachePolicy("capture-original", trace)
    capture_replacement = BoolCachePolicy("capture-replacement", trace)
    capture_inferred = BoolCachePolicy("capture-inferred", trace)
    capture_security = BoolCachePolicy("capture-security", trace)

    def captured_value(seed: int = 5) -> dict[str, int]:
        return {"seed": seed, "call": next_call("captured")}

    capture_declaration = Depends(captured_value, use_cache=capture_original)
    inferred_declaration = Depends(use_cache=capture_inferred)
    security_declaration = Security(
        captured_value, scopes=["capture:read"], use_cache=capture_security
    )

    @app.get("/capture")
    def captured(
        second: Annotated[dict[str, int], capture_declaration],
        inferred: Annotated[CapturedPayload, inferred_declaration],
        secured: Annotated[dict[str, int], security_declaration],
        first: dict[str, int] = capture_declaration,
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "inferred_seed": inferred.seed,
            "secured": secured,
            "same_first_second": first is second,
            "same_second_secured": second is secured,
            "trace": list(trace),
        }

    @app.post("/capture/rebind", include_in_schema=False)
    def rebind_capture() -> dict[str, Any]:
        capture_original.enabled = False
        capture_inferred.enabled = False
        object.__setattr__(capture_declaration, "use_cache", capture_replacement)
        trace.append("configure:capture:replace-field-and-mutate-original")
        return {
            "replacement_field_alias": capture_declaration.use_cache is capture_replacement,
            "original": capture_original.describe(),
            "replacement": capture_replacement.describe(),
            "trace": list(trace),
        }

    sync_sequence = BoolCachePolicy("sync-sequence", trace)

    def sync_value(seed: int = 7) -> dict[str, int]:
        return {"seed": seed, "call": next_call("sync-sequence")}

    sync_declaration = Depends(sync_value, use_cache=sync_sequence)

    @app.get("/sync-sequence")
    def read_sync_sequence(
        first: Annotated[dict[str, int], sync_declaration],
        second: Annotated[dict[str, int], sync_declaration],
        third: Annotated[dict[str, int], sync_declaration],
        fourth: Annotated[dict[str, int], sync_declaration],
    ) -> dict[str, Any]:
        return {
            "values": [first, second, third, fourth],
            "identities": [first is second, first is third, first is fourth],
            "trace": list(trace),
        }

    def none_policy_value(seed: int = 13) -> dict[str, int]:
        return {"seed": seed, "call": next_call("none-policy")}

    @app.get("/none-policy")
    def read_none_policy(
        first: Annotated[dict[str, int], Depends(none_policy_value, use_cache=None)],
        second: Annotated[dict[str, int], Depends(none_policy_value)],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "same_value": first is second,
            "trace": list(trace),
        }

    flat_policy = BoolCachePolicy("flat-validation", trace)

    async def flat_value(number: int) -> dict[str, int]:
        await asyncio.sleep(0)
        return {"number": number, "call": next_call("flat-validation")}

    flat_declaration = Depends(flat_value, use_cache=flat_policy)

    @app.get("/flat-validation")
    async def read_flat_validation(
        first: Annotated[dict[str, int], flat_declaration],
        second: Annotated[dict[str, int], flat_declaration],
        endpoint_number: int = 41,
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "same_value": first is second,
            "endpoint_number": endpoint_number,
            "trace": list(trace),
        }

    flat_cache_policy = BoolCachePolicy("flat-cache-hit", trace)

    def record_validation(value: Any) -> Any:
        trace.append(f"validate:flat-cache-hit:{value}")
        return value

    async def flat_cached_value(
        number: Annotated[int, BeforeValidator(record_validation)],
    ) -> dict[str, int]:
        await asyncio.sleep(0)
        return {"number": number, "call": next_call("flat-cache-hit")}

    flat_cached_declaration = Depends(flat_cached_value, use_cache=flat_cache_policy)

    @app.get("/flat-cache-hit")
    async def read_flat_cached(
        first: Annotated[dict[str, int], flat_cached_declaration],
        second: Annotated[dict[str, int], flat_cached_declaration],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "same_value": first is second,
            "trace": list(trace),
        }

    sync_parent_policy = BoolCachePolicy("sync-parent", trace)
    async_child_policy = BoolCachePolicy("async-child", trace, enabled=False)
    async_parent_policy = BoolCachePolicy("async-parent", trace)
    sync_child_policy = BoolCachePolicy("sync-child", trace, enabled=False)

    async def async_child(leaf_value: int = 11) -> dict[str, int]:
        await asyncio.sleep(0)
        ordinal = next_call("async-child")
        sync_parent_policy.enabled = ordinal % 2 == 0
        trace.append(f"mutate:sync-parent:{sync_parent_policy.enabled}")
        return {"leaf": leaf_value, "call": ordinal}

    def sync_parent(
        child: Annotated[dict[str, int], Depends(async_child, use_cache=async_child_policy)],
    ) -> dict[str, Any]:
        return {"child": child, "call": next_call("sync-parent")}

    sync_parent_declaration = Depends(sync_parent, use_cache=sync_parent_policy)

    @app.get("/nested/sync-parent")
    def read_sync_parent(
        first: Annotated[dict[str, Any], sync_parent_declaration],
        second: Annotated[dict[str, Any], sync_parent_declaration],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "same_value": first is second,
            "trace": list(trace),
        }

    def sync_child(leaf_value: int = 13) -> dict[str, int]:
        ordinal = next_call("sync-child")
        async_parent_policy.enabled = ordinal % 2 == 0
        trace.append(f"mutate:async-parent:{async_parent_policy.enabled}")
        return {"leaf": leaf_value, "call": ordinal}

    async def async_parent(
        child: Annotated[dict[str, int], Depends(sync_child, use_cache=sync_child_policy)],
    ) -> dict[str, Any]:
        await asyncio.sleep(0)
        return {"child": child, "call": next_call("async-parent")}

    async_parent_declaration = Depends(async_parent, use_cache=async_parent_policy)

    @app.get("/nested/async-parent")
    async def read_async_parent(
        first: Annotated[dict[str, Any], async_parent_declaration],
        second: Annotated[dict[str, Any], async_parent_declaration],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "same_value": first is second,
            "trace": list(trace),
        }

    override_outer_original = BoolCachePolicy("override-outer-original", trace)
    override_outer_field = BoolCachePolicy("override-outer-field", trace)
    override_child_original = BoolCachePolicy("override-child-original", trace)
    override_child_field = BoolCachePolicy("override-child-field", trace, enabled=False)

    def override_child(seed: int = 17) -> dict[str, int]:
        return {"seed": seed, "call": next_call("override-child")}

    override_child_declaration = Depends(override_child, use_cache=override_child_original)

    def override_parent(
        child: Annotated[dict[str, int], override_child_declaration],
    ) -> dict[str, Any]:
        return {"kind": "original", "child": child, "call": next_call("override-parent")}

    async def replacement_parent(
        child: Annotated[dict[str, int], override_child_declaration],
    ) -> dict[str, Any]:
        await asyncio.sleep(0)
        return {"kind": "replacement", "child": child, "call": next_call("override-replacement")}

    def unrelated_original() -> str:
        return "independent-original"

    def unrelated_replacement() -> str:
        return "independent-replacement"

    override_outer_declaration = Depends(override_parent, use_cache=override_outer_original)

    @app.get("/override")
    async def read_override(
        first: Annotated[dict[str, Any], override_outer_declaration],
        second: Annotated[dict[str, Any], override_outer_declaration],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "same_parent": first is second,
            "same_child": first["child"] is second["child"],
            "trace": list(trace),
        }

    @app.post("/overrides/{mode}", include_in_schema=False)
    def configure_overrides(mode: str) -> dict[str, Any]:
        if mode == "rebind":
            override_outer_original.enabled = False
            object.__setattr__(override_outer_declaration, "use_cache", override_outer_field)
            object.__setattr__(override_child_declaration, "use_cache", override_child_field)
        elif mode == "unrelated":
            app.dependency_overrides = {unrelated_original: unrelated_replacement}
        elif mode == "self":
            app.dependency_overrides = {
                override_parent: override_parent,
                override_child: override_child,
            }
        elif mode == "replacement":
            app.dependency_overrides = {override_parent: replacement_parent}
        elif mode == "clear":
            app.dependency_overrides = {}
        else:
            raise ValueError("unknown override mode")
        trace.append(f"configure:overrides:{mode}")
        return {
            "mode": mode,
            "override_count": len(app.dependency_overrides),
            "outer_field_alias": override_outer_declaration.use_cache is override_outer_field,
            "child_field_alias": override_child_declaration.use_cache is override_child_field,
            "trace": list(trace),
        }

    failed_child_policy = BoolCachePolicy("failed-child", trace)
    failed_parent_policy = BoolCachePolicy("failed-parent", trace)
    later_policy = BoolCachePolicy("later-sibling", trace)

    def validated_child(child_number: int) -> dict[str, int]:
        return {"number": child_number, "call": next_call("failed-child")}

    async def validated_parent(
        child: Annotated[dict[str, int], Depends(validated_child, use_cache=failed_child_policy)],
        parent_number: int,
    ) -> dict[str, Any]:
        await asyncio.sleep(0)
        return {"child": child, "number": parent_number, "call": next_call("failed-parent")}

    async def later_sibling(later_number: int = 19) -> dict[str, int]:
        await asyncio.sleep(0)
        return {"number": later_number, "call": next_call("later-sibling")}

    later_declaration = Depends(later_sibling, use_cache=later_policy)

    @app.get("/failed-edge")
    async def read_failed_edge(
        parent: Annotated[
            dict[str, Any], Depends(validated_parent, use_cache=failed_parent_policy)
        ],
        later_first: Annotated[dict[str, int], later_declaration],
        later_second: Annotated[dict[str, int], later_declaration],
        endpoint_number: int,
    ) -> dict[str, Any]:
        return {
            "parent": parent,
            "later_first": later_first,
            "later_second": later_second,
            "same_later": later_first is later_second,
            "endpoint_number": endpoint_number,
            "trace": list(trace),
        }

    bool_error_policy = BoolCachePolicy("bool-error", trace)
    length_error_policy = LengthCachePolicy("length-error", trace)
    fault_policy = BoolCachePolicy("fault-yield", trace, enabled=False)

    async def resource() -> AsyncIterator[str]:
        event_trace.append("dependency-enter")
        trace.append("resource:enter")
        try:
            yield "independent-resource"
        except Exception as error:
            trace.append(f"resource:error:{type(error).__name__}")
            raise
        finally:
            event_trace.append("dependency-cleanup")
            trace.append("resource:cleanup")

    def guarded_value(
        resource_value: Annotated[str, Depends(resource, scope="request")],
    ) -> dict[str, Any]:
        return {"resource": resource_value, "call": next_call("guarded")}

    @app.get("/yield/bool")
    async def read_bool_yield(
        value: Annotated[dict[str, Any], Depends(guarded_value, use_cache=bool_error_policy)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace), "trace": list(trace)}

    @app.get("/yield/length")
    async def read_length_yield(
        value: Annotated[dict[str, Any], Depends(guarded_value, use_cache=length_error_policy)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace), "trace": list(trace)}

    @app.get("/yield/fault")
    async def read_fault_yield(
        value: Annotated[dict[str, Any], Depends(guarded_value, use_cache=fault_policy)],
    ) -> dict[str, Any]:
        return {"value": value, "events": list(event_trace), "trace": list(trace)}

    @app.post("/policies/{name}/{mode}", include_in_schema=False)
    def configure_error_policy(name: str, mode: str) -> dict[str, Any]:
        policy = {"bool": bool_error_policy, "length": length_error_policy}[name]
        if mode not in {"normal", "raise", "invalid"}:
            raise ValueError("unknown policy mode")
        policy.mode = mode
        trace.append(f"configure:{name}:{mode}")
        return {"policy": policy.describe(), "events": list(event_trace), "trace": list(trace)}

    async def policy_error_response(_request: Any, error: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {"class": type(error).__name__, "message": str(error)},
                "events": list(event_trace),
                "trace": list(trace),
            },
        )

    app.add_exception_handler(IndependentCachePolicyError, policy_error_response)
    app.add_exception_handler(TypeError, policy_error_response)

    @app.get("/state", include_in_schema=False)
    def read_state() -> dict[str, Any]:
        return {
            "registration_trace": list(registration_trace),
            "trace": list(trace),
            "events": list(event_trace),
            "calls": dict(calls),
            "capture_aliases": {
                "original_field": capture_declaration.use_cache is capture_original,
                "replacement_field": capture_declaration.use_cache is capture_replacement,
                "inferred_policy": inferred_declaration.use_cache is capture_inferred,
                "inference_kept_declaration": inferred_declaration.dependency is None,
                "security_policy": security_declaration.use_cache is capture_security,
            },
            "error_policies": [bool_error_policy.describe(), length_error_policy.describe()],
        }

    @app.get("/cleanup-state", include_in_schema=False)
    def read_cleanup_state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    # Changes affect user policy state after every route has been registered.
    registration_trace = list(trace)
    sync_sequence.decisions = list(factory_input.get("sync_decisions", []))
    return app
