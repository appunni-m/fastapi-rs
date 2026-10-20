"""Argument bundles for direct FastAPI BackgroundTasks API parity."""

from fastapi import BackgroundTasks
from starlette.background import BackgroundTask


def record_task(value: str, *, label: str) -> None:
    del value, label


def record_sync_task(value: str, *, label: str, priority: int) -> None:
    del value, label, priority


async def record_async_task(value: int, *, label: str, priority: int) -> None:
    del value, label, priority


def record_variadic_task(*args: object, **kwargs: object) -> None:
    del args, kwargs


class BoundCallbacks:
    def record(self, value: str, *, label: str) -> None:
        del value, label


def create_argument_bundles() -> dict[str, dict[str, object]]:
    multi_call_receiver = BackgroundTasks()
    duplicate_func_receiver = BackgroundTasks()
    duplicate_self_receiver = BackgroundTasks()
    constructor_task = BackgroundTask(record_task, "constructor-original", label="seed")
    constructor_sequence = [constructor_task]
    constructor_receiver = BackgroundTasks(constructor_sequence)
    constructor_task.args = ("shared-task-object-mutated",)
    constructor_sequence.append(
        BackgroundTask(record_task, "external-list-append", label="detached")
    )
    empty_constructor_sequence: list[BackgroundTask] = []
    empty_constructor_receiver = BackgroundTasks(empty_constructor_sequence)
    empty_constructor_sequence.append(
        BackgroundTask(record_task, "empty-external-list-append", label="detached")
    )
    bound_callbacks = BoundCallbacks()
    return {
        "unused": {"args": [], "kwargs": {}},
        "task-call": {
            "args": [BackgroundTasks(), record_task, "queued"],
            "kwargs": {"label": "background-api"},
        },
        "task-first": {
            "args": [multi_call_receiver, record_sync_task, "first-positional"],
            "kwargs": {"label": "first-keyword", "priority": 3},
        },
        "task-second": {
            "args": [multi_call_receiver, record_async_task, 7],
            "kwargs": {"label": "second-keyword", "priority": 9},
        },
        "constructor-sequence-copy": {
            "args": [constructor_receiver, record_sync_task, "registered-after-sequence"],
            "kwargs": {"label": "new-task", "priority": 11},
        },
        "empty-constructor-list-copy": {
            "args": [empty_constructor_receiver, record_task, "registered-after-empty"],
            "kwargs": {"label": "new-task"},
        },
        "bound-method-callable": {
            "args": [BackgroundTasks(), bound_callbacks.record, "bound-value"],
            "kwargs": {"label": "bound-method"},
        },
        "kwargs-order-and-values": {
            "args": [
                BackgroundTasks(),
                record_variadic_task,
                ["nested-positional", {"enabled": True}],
            ],
            "kwargs": {"zeta": [1, 2], "alpha": {"enabled": True}},
        },
        "missing-func": {"args": [BackgroundTasks()], "kwargs": {}},
        "missing-self-and-func": {"args": [], "kwargs": {}},
        "duplicate-func": {
            "args": [duplicate_func_receiver, record_task],
            "kwargs": {"func": record_task},
        },
        "duplicate-self": {
            "args": [duplicate_self_receiver, record_task],
            "kwargs": {"self": duplicate_self_receiver},
        },
    }
