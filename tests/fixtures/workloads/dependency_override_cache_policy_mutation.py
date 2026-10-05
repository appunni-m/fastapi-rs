"""Independent public inputs for overrides changed inside cache-policy callbacks."""

import asyncio
import inspect
from collections.abc import AsyncIterator, Callable, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BeforeValidator


class IndependentOverrideMutationError(RuntimeError):
    pass


class IndependentInvalidSignatureReplacement:
    def __init__(self, next_call: Callable[[str], int]) -> None:
        self.next_call = next_call

    def __repr__(self) -> str:
        return "IndependentInvalidSignatureReplacement()"

    def __call__(self, invalid_value: int = 23) -> dict[str, Any]:
        return {"kind": "invalid", "value": invalid_value, "call": self.next_call("invalid")}


class MutationPolicy:
    method = "unspecified"

    def __init__(self, trace: list[str], mutate: Callable[[str], None]) -> None:
        self.trace = trace
        self.mutate = mutate
        self.operation = "assign"
        self.armed = False
        self.calls = 0
        self.result = True
        self.raise_after_mutation = False

    def evaluate(self) -> None:
        self.calls += 1
        self.trace.append(f"policy:{self.method}:{self.calls}:armed={self.armed}")
        if self.armed:
            self.mutate(self.operation)
            self.armed = False
            if self.raise_after_mutation:
                raise IndependentOverrideMutationError("cache policy changed overrides then failed")

    def describe(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "operation": self.operation,
            "calls": self.calls,
            "armed": self.armed,
            "result": self.result,
        }


class BoolMutationPolicy(MutationPolicy):
    method = "bool"

    def __bool__(self) -> bool:
        self.evaluate()
        return self.result


class LengthMutationPolicy(MutationPolicy):
    method = "length"

    def __len__(self) -> int:
        self.evaluate()
        return 1 if self.result else 0


class ObservedChildPolicy:
    def __init__(self, label: str, trace: list[str]) -> None:
        self.label = label
        self.trace = trace
        self.calls = 0

    def __bool__(self) -> bool:
        self.calls += 1
        self.trace.append(f"child-policy:{self.label}:{self.calls}")
        return False


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> FastAPI:
    app = FastAPI()
    trace: list[str] = []
    calls: dict[str, int] = {}

    def next_call(label: str) -> int:
        calls[label] = calls.get(label, 0) + 1
        trace.append(f"call:{label}:{calls[label]}")
        return calls[label]

    def trigger(trigger_value: int = 5) -> dict[str, Any]:
        return {"kind": "trigger", "value": trigger_value, "call": next_call("trigger")}

    def trigger_replacement(replacement_trigger_value: int = 7) -> dict[str, Any]:
        return {
            "kind": "trigger-replacement",
            "value": replacement_trigger_value,
            "call": next_call("trigger-replacement"),
        }

    def later(original_value: int = 11) -> dict[str, Any]:
        return {"kind": "original", "value": original_value, "call": next_call("original")}

    def sync_replacement(replacement_value: int = 13) -> dict[str, Any]:
        return {"kind": "sync", "value": replacement_value, "call": next_call("sync")}

    async def async_replacement(replacement_value: int = 17) -> dict[str, Any]:
        trace.append("async-replacement:start")
        await asyncio.sleep(0)
        return {"kind": "async", "value": replacement_value, "call": next_call("async")}

    async def yield_replacement(replacement_value: int = 19) -> AsyncIterator[dict[str, Any]]:
        event_trace.append("dependency-enter")
        trace.append("yield-replacement:enter")
        try:
            await asyncio.sleep(0)
            yield {"kind": "yield", "value": replacement_value, "call": next_call("yield")}
        except Exception as error:
            trace.append(f"yield-replacement:error:{type(error).__name__}")
            raise
        finally:
            event_trace.append("dependency-cleanup")
            trace.append("yield-replacement:cleanup")

    def record_required(value: Any) -> Any:
        trace.append(f"validate:required-replacement:{value}")
        return value

    def required_replacement(
        required_value: Annotated[int, BeforeValidator(record_required)],
    ) -> dict[str, Any]:
        return {"kind": "required", "value": required_value, "call": next_call("required")}

    invalid_replacement = IndependentInvalidSignatureReplacement(next_call)

    replacement = {
        "sync": sync_replacement,
        "async": async_replacement,
        "yield": yield_replacement,
        "required": required_replacement,
    }[factory_input.get("replacement_kind", "sync")]

    def unrelated() -> str:
        return "independent-unrelated"

    def unrelated_replacement() -> str:
        return "independent-unrelated-replacement"

    async def gate(gate_value: int = 29) -> dict[str, int]:
        trace.append("gate:start")
        await asyncio.sleep(0)
        return {"value": gate_value, "call": next_call("gate")}

    def required_trigger(trigger_required: int) -> dict[str, int]:
        return {"value": trigger_required, "call": next_call("required-trigger")}

    def failing_input(failed_value: int) -> dict[str, int]:
        return {"value": failed_value, "call": next_call("failing-input")}

    def dynamic_later(**values: int) -> dict[str, Any]:
        return {"values": values, "call": next_call("dynamic")}

    dynamic_later.__signature__ = inspect.Signature(
        [
            inspect.Parameter(
                "registered", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int, default=31
            )
        ]
    )

    old_child_policy = ObservedChildPolicy("captured-old", trace)
    new_child_policy = ObservedChildPolicy("current-field", trace)

    def old_child(old_child_value: int = 37) -> dict[str, Any]:
        return {"kind": "old-child", "value": old_child_value, "call": next_call("old-child")}

    def new_child(new_child_value: int = 41) -> dict[str, Any]:
        return {"kind": "new-child", "value": new_child_value, "call": next_call("new-child")}

    child_declaration = Depends(old_child, use_cache=old_child_policy)

    def mutate(operation: str) -> None:
        trace.append(f"mutation:before:{operation}")
        if operation in {"insert", "repair"}:
            app.dependency_overrides[later] = replacement
        elif operation == "install-invalid":
            app.dependency_overrides = {later: invalid_replacement}
        elif operation == "assign":
            app.dependency_overrides = {later: replacement}
        elif operation == "clear":
            app.dependency_overrides = {}
        elif operation == "remove":
            app.dependency_overrides.pop(later, None)
        elif operation == "self":
            app.dependency_overrides[trigger] = trigger_replacement
        elif operation == "parent-and-child":
            app.dependency_overrides = {selected_parent: alternate_parent, later: replacement}
        elif operation == "captured-markers":
            object.__setattr__(child_declaration, "dependency", new_child)
            object.__setattr__(child_declaration, "use_cache", new_child_policy)
            app.dependency_overrides = {unrelated: unrelated_replacement}
        elif operation in {"signature-unrelated", "signature-clear"}:
            dynamic_later.__signature__ = inspect.Signature(
                [
                    inspect.Parameter(
                        "changed", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int
                    )
                ]
            )
            app.dependency_overrides = (
                {unrelated: unrelated_replacement} if operation == "signature-unrelated" else {}
            )
        else:
            raise ValueError("unknown override mutation operation")
        trace.append(f"mutation:after:{operation}")

    policy_type = {"bool": BoolMutationPolicy, "length": LengthMutationPolicy}[
        factory_input.get("policy_method", "bool")
    ]
    policy = policy_type(trace, mutate)
    trigger_declaration = Depends(trigger, use_cache=policy)

    def awaited_trigger(ready: Annotated[dict[str, int], Depends(gate)]) -> dict[str, Any]:
        return {"ready": ready, "call": next_call("awaited-trigger")}

    awaited_trigger_declaration = Depends(awaited_trigger, use_cache=policy)

    def selected_parent(
        first: Annotated[dict[str, Any], awaited_trigger_declaration],
        second: Annotated[dict[str, Any], Depends(later, use_cache=False)],
    ) -> dict[str, Any]:
        return {
            "kind": "selected-parent",
            "first": first,
            "second": second,
            "call": next_call("selected-parent"),
        }

    def alternate_parent(
        replacement_child: Annotated[dict[str, Any], Depends(later, use_cache=False)],
    ) -> dict[str, Any]:
        return {
            "kind": "alternate-parent",
            "child": replacement_child,
            "call": next_call("alternate-parent"),
        }

    def captured_parent(
        first: Annotated[dict[str, Any], awaited_trigger_declaration],
        second: Annotated[dict[str, Any], child_declaration],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, "call": next_call("captured-parent")}

    def override_projection() -> list[dict[str, str]]:
        names = {
            trigger: "trigger",
            trigger_replacement: "trigger-replacement",
            later: "later",
            sync_replacement: "sync",
            async_replacement: "async",
            yield_replacement: "yield",
            required_replacement: "required",
            invalid_replacement: "invalid",
            selected_parent: "selected-parent",
            alternate_parent: "alternate-parent",
            unrelated: "unrelated",
            unrelated_replacement: "unrelated-replacement",
        }
        return [
            {"original": names[original], "replacement": names[current]}
            for original, current in app.dependency_overrides.items()
        ]

    def snapshot() -> dict[str, Any]:
        return {
            "trace": list(trace),
            "events": list(event_trace),
            "calls": dict(calls),
            "policy": policy.describe(),
            "overrides": override_projection(),
            "dynamic_signature_fields": list(dynamic_later.__signature__.parameters),
            "child_marker_aliases": {
                "old_callable": child_declaration.dependency is old_child,
                "new_callable": child_declaration.dependency is new_child,
                "old_policy": child_declaration.use_cache is old_child_policy,
                "new_policy": child_declaration.use_cache is new_child_policy,
            },
        }

    @app.get("/root")
    def read_root(
        first: Annotated[dict[str, Any], trigger_declaration],
        second: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, **snapshot()}

    @app.get("/root-await")
    async def read_root_after_await(
        ready: Annotated[dict[str, int], Depends(gate)],
        first: Annotated[dict[str, Any], trigger_declaration],
        second: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {"ready": ready, "first": first, "second": second, **snapshot()}

    @app.get("/selected-call")
    def read_selected_call(
        first: Annotated[dict[str, Any], trigger_declaration],
        second: Annotated[dict[str, Any], Depends(trigger, use_cache=False)],
        third: Annotated[dict[str, Any], Depends(trigger)],
    ) -> dict[str, Any]:
        return {
            "values": [first, second, third],
            "identities": [first is second, first is third],
            **snapshot(),
        }

    @app.get("/nested")
    async def read_nested(
        first: Annotated[dict[str, Any], Depends(selected_parent, use_cache=False)],
        second: Annotated[dict[str, Any], Depends(selected_parent, use_cache=False)],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, **snapshot()}

    @app.get("/captured-markers")
    def read_captured_markers(
        first: Annotated[dict[str, Any], Depends(captured_parent, use_cache=False)],
        second: Annotated[dict[str, Any], Depends(captured_parent, use_cache=False)],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, **snapshot()}

    @app.get("/cached-policy")
    async def read_cached_policy(
        ready: Annotated[dict[str, int], Depends(gate)],
        first: Annotated[dict[str, Any], Depends(trigger)],
        cached: Annotated[dict[str, Any], trigger_declaration],
        final: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {
            "ready": ready,
            "first": first,
            "cached": cached,
            "same_trigger": first is cached,
            "final": final,
            **snapshot(),
        }

    @app.get("/cached-later")
    def read_cached_later(
        first: Annotated[dict[str, Any], Depends(later)],
        middle: Annotated[dict[str, Any], trigger_declaration],
        final: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "middle": middle,
            "final": final,
            "same_later": first is final,
            **snapshot(),
        }

    @app.get("/required-trigger")
    def read_required_trigger(
        first: Annotated[dict[str, int], Depends(required_trigger, use_cache=policy)],
        second: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, **snapshot()}

    @app.get("/failure-before-mutation")
    def read_failure_before_mutation(
        invalid: Annotated[dict[str, int], Depends(failing_input)],
        middle: Annotated[dict[str, Any], trigger_declaration],
        final: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {"invalid": invalid, "middle": middle, "final": final, **snapshot()}

    @app.get("/dynamic-signature")
    def read_dynamic_signature(
        first: Annotated[dict[str, Any], trigger_declaration],
        second: Annotated[dict[str, Any], Depends(dynamic_later)],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, **snapshot()}

    async def guard_resource() -> AsyncIterator[str]:
        event_trace.append("dependency-enter")
        trace.append("guard-resource:enter")
        try:
            yield "independent-guard"
        except Exception as error:
            trace.append(f"guard-resource:error:{type(error).__name__}")
            raise
        finally:
            event_trace.append("dependency-cleanup")
            trace.append("guard-resource:cleanup")

    def guarded_trigger(
        resource: Annotated[str, Depends(guard_resource, scope="request")],
    ) -> dict[str, Any]:
        return {"resource": resource, "call": next_call("guarded-trigger")}

    @app.get("/mutation-error")
    async def read_mutation_error(
        first: Annotated[dict[str, Any], Depends(guarded_trigger, use_cache=policy)],
        second: Annotated[dict[str, Any], Depends(later)],
    ) -> dict[str, Any]:
        return {"first": first, "second": second, **snapshot()}

    @app.get("/later-only")
    async def read_later_only(value: Annotated[dict[str, Any], Depends(later)]) -> dict[str, Any]:
        return {"value": value, **snapshot()}

    @app.post("/reset-invalid-removal", include_in_schema=False)
    def reset_invalid_for_removal() -> dict[str, Any]:
        app.dependency_overrides = {later: invalid_replacement}
        policy.operation = "clear"
        policy.armed = True
        policy.raise_after_mutation = False
        trace.append("configure:invalid-later-removal")
        return snapshot()

    @app.post("/clear-overrides", include_in_schema=False)
    def clear_overrides_for_recovery() -> dict[str, Any]:
        app.dependency_overrides = {}
        policy.armed = False
        policy.raise_after_mutation = False
        trace.append("configure:clear-overrides-for-recovery")
        return snapshot()

    async def mutation_error_response(_request: Any, error: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "class": f"{type(error).__module__}.{type(error).__qualname__}",
                    "message": str(error),
                },
                **snapshot(),
            },
        )

    app.add_exception_handler(IndependentOverrideMutationError, mutation_error_response)
    app.add_exception_handler(TypeError, mutation_error_response)
    app.add_exception_handler(ValueError, mutation_error_response)

    @app.get("/state", include_in_schema=False)
    def read_state() -> dict[str, Any]:
        return snapshot()

    @app.get("/cleanup-state", include_in_schema=False)
    def read_cleanup_state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    # Install source-valid inputs only after all registered plans have been built.
    # Attach the malformed public signature after registration. Earlier policies
    # either repair/remove it or install it after a yielded child has entered.
    invalid_replacement.__signature__ = "independent invalid override signature"
    initial = factory_input.get("initial_overrides", "empty")
    if initial == "mapped":
        app.dependency_overrides = {later: replacement}
    elif initial == "unrelated":
        app.dependency_overrides = {unrelated: unrelated_replacement}
    elif initial == "invalid":
        app.dependency_overrides = {later: invalid_replacement}
    elif initial != "empty":
        raise ValueError("unknown initial override mapping")
    policy.operation = factory_input.get("operation", "assign")
    policy.result = factory_input.get("policy_result", True)
    policy.raise_after_mutation = factory_input.get("raise_after_mutation", False)
    policy.armed = True
    return app
