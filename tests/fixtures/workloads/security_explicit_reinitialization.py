"""Public security initializer calls followed by request and OpenAPI observations."""

import inspect
from typing import Annotated, Any

from fastapi import FastAPI, Security
from fastapi.security import OAuth2AuthorizationCodeBearer, OpenIdConnect


class NamedAuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    """Exercise the inherited initializer's default subclass scheme name."""


class NamedOpenIdConnect(OpenIdConnect):
    """Exercise the inherited initializer's default subclass scheme name."""


class TracedScopes(dict[str, str]):
    """Record the public scopes truthiness hook without changing its value."""

    def __init__(self, value: dict[str, str], workload_trace: list[str]) -> None:
        super().__init__(value)
        self.workload_trace = workload_trace

    def __bool__(self) -> bool:
        self.workload_trace.append("scopes-truthiness")
        return len(self) != 0


def create_app(factory_input: dict[str, Any], workload_trace: list[str]) -> FastAPI:
    scheme_kind = factory_input["scheme"]
    subclass = factory_input.get("subclass", False)
    trace_scopes = factory_input.get("trace_scopes", False)
    if scheme_kind == "oauth2-code":
        public_class = OAuth2AuthorizationCodeBearer
        instance_class = NamedAuthorizationCodeBearer if subclass else public_class
    else:
        public_class = OpenIdConnect
        instance_class = NamedOpenIdConnect if subclass else public_class

    initial = dict(factory_input["initial"])
    if trace_scopes and "scopes" in initial:
        initial["scopes"] = TracedScopes(initial["scopes"], workload_trace)
    scheme = instance_class(**initial)
    initializer = public_class.__init__
    app = FastAPI()

    def scheme_state() -> dict[str, Any]:
        bound = scheme.__init__
        descriptor_bound = initializer.__get__(scheme, type(scheme))
        return {
            "model": scheme.model.model_dump(mode="json"),
            "scheme_name": scheme.scheme_name,
            "auto_error": scheme.auto_error,
            "binding": {
                "class_descriptor_identity": initializer is public_class.__dict__["__init__"],
                "class_get_identity": initializer.__get__(None, public_class) is initializer,
                "bound_self_identity": bound.__self__ is scheme,
                "bound_function_identity": bound.__func__ is initializer,
                "descriptor_self_identity": descriptor_bound.__self__ is scheme,
                "descriptor_function_identity": descriptor_bound.__func__ is initializer,
                "unbound_signature": str(inspect.signature(initializer)),
                "bound_signature": str(inspect.signature(bound)),
                "descriptor_signature": str(inspect.signature(descriptor_bound)),
            },
            "workload_trace": list(workload_trace),
        }

    @app.get("/state")
    async def read_state() -> dict[str, Any]:
        return scheme_state()

    @app.get("/reinitialize")
    async def reinitialize() -> dict[str, Any]:
        args = list(factory_input["reinitialize"].get("args", []))
        kwargs = dict(factory_input["reinitialize"].get("kwargs", {}))
        if trace_scopes and "scopes" in kwargs:
            kwargs["scopes"] = TracedScopes(kwargs["scopes"], workload_trace)
        old_model = scheme.model
        style = factory_input["call_style"]
        if style == "bound":
            call = scheme.__init__
        elif style == "unbound":
            call = initializer
            args.insert(0, scheme)
        else:
            call = initializer.__get__(scheme, type(scheme))
        try:
            result = call(*args, **kwargs)
        except Exception as exc:
            outcome = {
                "outcome": "raised",
                "exception_class": f"{type(exc).__module__}.{type(exc).__qualname__}",
                "exception_message": str(exc),
            }
        else:
            outcome = {"outcome": "returned", "return_value": result}
        return {
            **outcome,
            "model_replaced": scheme.model is not old_model,
            "state": scheme_state(),
        }

    @app.get("/protected")
    async def protected(
        token: Annotated[str | None, Security(scheme)],
    ) -> dict[str, str | None]:
        return {"token": token}

    return app


def create_argument_bundles() -> dict[str, dict[str, object]]:
    code = OAuth2AuthorizationCodeBearer("/initial-authorize", "/initial-token")
    openid = OpenIdConnect(openIdConnectUrl="/initial-openid")
    return {
        "code-explicit": {
            "args": [code, "/replacement-authorize", "/replacement-token"],
            "kwargs": {"auto_error": False},
        },
        "code-missing-token": {
            "args": [code, "/replacement-authorize"],
            "kwargs": {},
        },
        "code-duplicate-authorization": {
            "args": [code, "/replacement-authorize", "/replacement-token"],
            "kwargs": {"authorizationUrl": "/duplicate-authorize"},
        },
        "code-unexpected-keyword": {
            "args": [code, "/replacement-authorize", "/replacement-token"],
            "kwargs": {"unknown": "value"},
        },
        "code-too-many-positionals": {
            "args": [code, "/authorize", "/token", None, None, None, None, True, "extra"],
            "kwargs": {},
        },
        "openid-explicit": {
            "args": [openid],
            "kwargs": {"openIdConnectUrl": "/replacement-openid", "auto_error": False},
        },
        "openid-missing-url": {"args": [openid], "kwargs": {}},
        "openid-positional-url": {
            "args": [openid, "/replacement-openid"],
            "kwargs": {},
        },
        "openid-extra-positional-and-url": {
            "args": [openid, "extra"],
            "kwargs": {"openIdConnectUrl": "/replacement-openid"},
        },
        "openid-duplicate-receiver": {
            "args": [openid],
            "kwargs": {"self": openid, "openIdConnectUrl": "/replacement-openid"},
        },
        "openid-unexpected-keyword": {
            "args": [openid],
            "kwargs": {"openIdConnectUrl": "/replacement-openid", "unknown": "value"},
        },
    }
