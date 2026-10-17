"""Input-driven FastAPI webhook constructor edge cases."""

from fastapi import FastAPI


class _RaisesOnTruthiness:
    def __bool__(self) -> bool:
        raise RuntimeError("webhooks truthiness failed")


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    if factory_input.get("truthiness_error", False):
        return FastAPI(webhooks=_RaisesOnTruthiness())
    return FastAPI(webhooks=object())
