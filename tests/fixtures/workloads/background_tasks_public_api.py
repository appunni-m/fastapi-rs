"""Argument bundles for direct FastAPI BackgroundTasks API parity."""

from fastapi import BackgroundTasks


def record_task(value: str, *, label: str) -> None:
    del value, label


def create_argument_bundles() -> dict[str, dict[str, object]]:
    return {
        "unused": {"args": [], "kwargs": {}},
        "task-call": {
            "args": [BackgroundTasks(), record_task, "queued"],
            "kwargs": {"label": "background-api"},
        },
    }
