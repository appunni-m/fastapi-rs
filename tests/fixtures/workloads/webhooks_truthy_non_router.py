"""Truthy non-router webhook value passed through FastAPI construction."""

from fastapi import FastAPI


def create_app(factory_input: dict[str, object], event_trace: list[str]) -> FastAPI:
    return FastAPI(webhooks=object())
