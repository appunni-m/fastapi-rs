"""Argument bundles for direct FastAPI BackgroundTasks API parity."""

from fastapi import BackgroundTasks


def record_task(value: str, *, label: str) -> None:
    del value, label


def record_sync_task(value: str, *, label: str, priority: int) -> None:
    del value, label, priority


async def record_async_task(value: int, *, label: str, priority: int) -> None:
    del value, label, priority


def create_argument_bundles() -> dict[str, dict[str, object]]:
    multi_call_receiver = BackgroundTasks()
    duplicate_func_receiver = BackgroundTasks()
    duplicate_self_receiver = BackgroundTasks()
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
