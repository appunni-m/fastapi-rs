"""Independent public Python and ASGI inputs for Depends and Security records."""

import dataclasses
import inspect
from collections.abc import AsyncIterator, Callable, Mapping
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query, Security, param_functions, params
from fastapi.encoders import jsonable_encoder

DependsRecord = type(Depends())
SecurityRecord = type(Security())


class IndependentToken:
    def __init__(self, label: str) -> None:
        self.label = label


class MatchingKeyword(str):
    def __new__(cls, text: str, parameter: str, trace: list[str]):
        value = super().__new__(cls, text)
        value.parameter = parameter
        value.trace = trace
        return value

    def __eq__(self, other: object) -> bool:
        self.trace.append(f"{type(other).__name__}:{other}")
        return other == self.parameter

    __hash__ = str.__hash__


class IndependentKeywordComparisonError(RuntimeError):
    pass


class RaisingKeyword(str):
    def __new__(cls, text: str, trace: list[str]):
        value = super().__new__(cls, text)
        value.trace = trace
        return value

    def __eq__(self, other: object) -> bool:
        self.trace.append(f"{type(other).__name__}:{other}")
        raise IndependentKeywordComparisonError("independent keyword comparison failure")

    __hash__ = str.__hash__


class RecordDependsChild(DependsRecord):
    pass


class RecordSecurityChild(SecurityRecord):
    pass


class PayloadReader:
    def __init__(self, seed: int = 3) -> None:
        self.seed = seed


class ResponseTimeline:
    def __init__(self, app: Any, timeline: list[str]) -> None:
        self.app = app
        self.timeline = timeline

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        async def record_send(message: dict[str, Any]) -> None:
            if message.get("type") == "http.response.start":
                self.timeline.append("response-start")
            elif message.get("type") == "http.response.body" and not message.get(
                "more_body", False
            ):
                self.timeline.append("response-end")
            await send(message)

        await self.app(scope, receive, record_send)


def _qualified_name(value: type[Any]) -> str:
    return f"{value.__module__}.{value.__qualname__}"


def _record_values(value: Any) -> dict[str, Any]:
    result = {
        "dependency": value.dependency,
        "use_cache": value.use_cache,
        "scope": value.scope,
    }
    if isinstance(value, SecurityRecord):
        result["scopes"] = value.scopes
    return result


def _record_state(value: Any) -> dict[str, Any]:
    return {
        "class": _qualified_name(type(value)),
        "fields": _record_values(value),
        "dictionary": dict(value.__dict__),
    }


def _capture(operation: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"outcome": "return", "value": operation()}
    except Exception as error:
        return {
            "outcome": "raise",
            "exception_class": _qualified_name(type(error)),
            "exception_message": str(error),
        }


def _signature_projection(value: Any) -> dict[str, Any]:
    signature = inspect.signature(value)
    return {
        "signature": str(signature),
        "parameter_kinds": [
            [parameter.name, parameter.kind.name] for parameter in signature.parameters.values()
        ],
        "annotations": {
            name: str(annotation) for name, annotation in value.__annotations__.items()
        },
    }


def _field_projection(value: Any) -> list[dict[str, Any]]:
    return [
        {
            "name": field.name,
            "type": str(field.type),
            "default": field.default,
            "default_factory_is_missing": field.default_factory is dataclasses.MISSING,
            "init": field.init,
            "repr": field.repr,
            "hash": field.hash,
            "compare": field.compare,
            "kw_only": field.kw_only,
            "metadata": dict(field.metadata),
        }
        for field in dataclasses.fields(value)
    ]


def create_app(factory_input: Mapping[str, Any], event_trace: list[str]) -> Any:
    app = FastAPI()
    timeline: list[str] = []
    shallow_scopes = ["record:read"]
    shallow_record = SecurityRecord(31, True, "request", shallow_scopes)
    bypass_record = DependsRecord(41, False, "request")
    calls = {"counted": 0}

    @app.get("/identity", include_in_schema=False)
    def identity() -> dict[str, Any]:
        depends = Depends()
        security = Security(scopes=["record:read"])
        return {
            "depends_root_is_factory": Depends is param_functions.Depends,
            "security_root_is_factory": Security is param_functions.Security,
            "depends_factory_is_class": param_functions.Depends is DependsRecord,
            "security_factory_is_class": param_functions.Security is SecurityRecord,
            "depends_return_class_is_params_alias": DependsRecord is params.Depends,
            "security_return_class_is_params_alias": SecurityRecord is params.Security,
            "depends_is_class": inspect.isclass(DependsRecord),
            "security_is_class": inspect.isclass(SecurityRecord),
            "security_is_depends_subclass": issubclass(SecurityRecord, DependsRecord),
            "depends_mro": [_qualified_name(base) for base in DependsRecord.__mro__],
            "security_mro": [_qualified_name(base) for base in SecurityRecord.__mro__],
            "depends_return_class": _qualified_name(type(depends)),
            "security_return_class": _qualified_name(type(security)),
            "depends_return_is_declared_class": type(depends) is DependsRecord,
            "security_return_is_declared_class": type(security) is SecurityRecord,
            "security_return_is_depends": isinstance(security, DependsRecord),
            "fields": {
                "depends": _record_values(depends),
                "security": _record_values(security),
            },
        }

    @app.get("/signatures", include_in_schema=False)
    def signatures() -> dict[str, Any]:
        return {
            "depends_class": _signature_projection(DependsRecord),
            "security_class": _signature_projection(SecurityRecord),
            "depends_initializer": _signature_projection(DependsRecord.__init__),
            "security_initializer": _signature_projection(SecurityRecord.__init__),
            "depends_bound_initializer": _signature_projection(DependsRecord().__init__),
            "security_bound_initializer": _signature_projection(SecurityRecord().__init__),
            "depends_factory": _signature_projection(Depends),
            "security_factory": _signature_projection(Security),
            "depends_match_args": list(DependsRecord.__match_args__),
            "security_match_args": list(SecurityRecord.__match_args__),
        }

    @app.get("/binding", include_in_schema=False)
    def binding() -> dict[str, Any]:
        def reinitialize() -> dict[str, Any]:
            record = SecurityRecord()
            returned = record.__init__(17, False, "function", ("record:write",))
            return {"returned": returned, "fields": _record_values(record)}

        def keyword_alias(
            constructor: Callable[..., Any],
            parameter: str,
            value: Any,
            positional: tuple[Any, ...] = (),
        ) -> dict[str, Any]:
            trace: list[str] = []
            key = MatchingKeyword("unknown", parameter, trace)
            result = _capture(lambda: _record_values(constructor(*positional, **{key: value})))
            return {"binding": result, "comparison_trace": list(trace)}

        def keyword_comparison_error(constructor: Callable[..., Any]) -> dict[str, Any]:
            trace: list[str] = []
            key = RaisingKeyword("unknown", trace)
            result = _capture(lambda: _record_values(constructor(**{key: 29})))
            return {"binding": result, "comparison_trace": list(trace)}

        def keyword_initializer_self() -> dict[str, Any]:
            trace: list[str] = []
            key = MatchingKeyword("unknown", "self", trace)
            record = DependsRecord(31, False, "request")

            def initialize() -> dict[str, Any]:
                returned = DependsRecord.__init__(**{key: record}, dependency=37)
                return {"returned": returned, "fields": _record_values(record)}

            result = _capture(initialize)
            return {"binding": result, "comparison_trace": list(trace)}

        return {
            "depends_positional": _capture(
                lambda: _record_values(DependsRecord(7, False, "function"))
            ),
            "security_positional": _capture(
                lambda: _record_values(SecurityRecord(11, False, "function", ["read"]))
            ),
            "depends_keywords": _capture(
                lambda: _record_values(DependsRecord(scope="request", dependency=13))
            ),
            "reinitialize_frozen_record": _capture(reinitialize),
            "depends_duplicate_dependency": _capture(lambda: DependsRecord(1, dependency=2)),
            "depends_duplicate_use_cache": _capture(
                lambda: DependsRecord(1, False, use_cache=True)
            ),
            "security_duplicate_scopes": _capture(
                lambda: SecurityRecord(1, True, None, ["first"], scopes=["second"])
            ),
            "depends_too_many_positional": _capture(lambda: DependsRecord(1, True, None, 4)),
            "security_too_many_positional": _capture(lambda: SecurityRecord(1, True, None, [], 5)),
            "depends_unexpected_keyword": _capture(lambda: DependsRecord(extra=3)),
            "security_unexpected_keyword": _capture(lambda: SecurityRecord(extra=3)),
            "depends_factory_keyword_only": _capture(lambda: Depends(1, False)),
            "security_factory_keyword_only": _capture(lambda: Security(1, ["read"])),
            "security_factory_scope_keyword": _capture(lambda: Security(scope="function")),
            "depends_keyword_rich_match": keyword_alias(DependsRecord, "dependency", 9),
            "security_keyword_rich_match": keyword_alias(
                SecurityRecord, "scopes", ["independent-scope"]
            ),
            "depends_keyword_rich_duplicate": keyword_alias(DependsRecord, "dependency", 19, (17,)),
            "depends_keyword_rich_self_duplicate": keyword_alias(DependsRecord, "self", 23),
            "depends_keyword_initializer_self": keyword_initializer_self(),
            "depends_keyword_comparison_error": keyword_comparison_error(DependsRecord),
            "security_keyword_comparison_error": keyword_comparison_error(SecurityRecord),
        }

    @app.get("/raw-values", include_in_schema=False)
    def raw_values() -> dict[str, Any]:
        dependency = IndependentToken("independent-value")
        cache_value = factory_input["raw_cache"]
        scope_value = factory_input["raw_scope"]
        scopes_value = factory_input["raw_scopes"]
        depends = DependsRecord(dependency, cache_value, scope_value)
        security = SecurityRecord(dependency, cache_value, scope_value, scopes_value)
        factory_depends = Depends(dependency, use_cache=cache_value, scope=scope_value)
        factory_security = Security(dependency, scopes=scopes_value, use_cache=cache_value)
        return {
            "dependency_type": _qualified_name(type(depends.dependency)),
            "dependency_identity_preserved": depends.dependency is dependency,
            "security_dependency_identity_preserved": security.dependency is dependency,
            "factory_depends_dependency_identity_preserved": (
                factory_depends.dependency is dependency
            ),
            "factory_security_dependency_identity_preserved": (
                factory_security.dependency is dependency
            ),
            "use_cache": depends.use_cache,
            "use_cache_type": _qualified_name(type(depends.use_cache)),
            "scope": depends.scope,
            "scope_type": _qualified_name(type(depends.scope)),
            "scopes": security.scopes,
            "scopes_type": _qualified_name(type(security.scopes)),
            "cache_identity_preserved": security.use_cache is cache_value,
            "scope_identity_preserved": security.scope is scope_value,
            "scopes_identity_preserved": security.scopes is scopes_value,
            "factory_depends_cache_identity_preserved": (factory_depends.use_cache is cache_value),
            "factory_depends_scope_identity_preserved": factory_depends.scope is scope_value,
            "factory_security_scopes_identity_preserved": (factory_security.scopes is scopes_value),
        }

    @app.get("/repr-equality", include_in_schema=False)
    def repr_equality() -> dict[str, Any]:
        depends = DependsRecord(23, False, "function")
        same = DependsRecord(23, False, "function")
        changed = DependsRecord(23, True, "function")
        security = SecurityRecord(23, False, "function", ("read", "write"))
        child = RecordDependsChild(23, False, "function")
        recursive = Depends()
        object.__setattr__(recursive, "dependency", recursive)
        return {
            "depends_repr": repr(depends),
            "security_repr": repr(security),
            "depends_child_repr": repr(child),
            "security_child_repr": repr(RecordSecurityChild(23, False, "function", [])),
            "recursive_repr": repr(recursive),
            "same_fields_equal": depends == same,
            "changed_fields_equal": depends == changed,
            "depends_security_equal": depends == security,
            "base_child_equal": depends == child,
            "same_child_equal": child == RecordDependsChild(23, False, "function"),
            "unrelated_equal": depends == {"dependency": 23},
            "different_class_returns_not_implemented": (depends.__eq__(security) is NotImplemented),
            "child_class_returns_not_implemented": depends.__eq__(child) is NotImplemented,
            "unrelated_returns_not_implemented": security.__eq__(object()) is NotImplemented,
        }

    @app.get("/hash", include_in_schema=False)
    def hash_values() -> dict[str, Any]:
        depends = DependsRecord(17, False, 5)
        security = SecurityRecord(19, True, 7, (2, 3))
        return {
            "depends_hash": hash(depends),
            "security_hash": hash(security),
            "depends_hash_matches_field_tuple": hash(depends) == hash((17, False, 5)),
            "security_hash_matches_field_tuple": hash(security) == hash((19, True, 7, (2, 3))),
            "equal_depends_have_equal_hashes": (hash(depends) == hash(DependsRecord(17, False, 5))),
            "list_scopes_hash": _capture(lambda: hash(SecurityRecord(19, True, 7, [2, 3]))),
            "dictionary_dependency_hash": _capture(lambda: hash(DependsRecord({}, True, 5))),
        }

    @app.get("/scopes", include_in_schema=False)
    def scopes() -> dict[str, Any]:
        return {
            "fields": _record_values(shallow_record),
            "list_identity_preserved": shallow_record.scopes is shallow_scopes,
            "hash": _capture(lambda: hash(shallow_record)),
        }

    @app.post("/scopes/append/{label}", include_in_schema=False)
    def append_scope(label: str) -> dict[str, Any]:
        shallow_record.scopes.append(label)
        return {
            "scopes": list(shallow_record.scopes),
            "replace_scopes_attribute": _capture(
                lambda: setattr(shallow_record, "scopes", ["replacement"])
            ),
        }

    @app.get("/frozen", include_in_schema=False)
    def frozen() -> dict[str, Any]:
        result = {}
        for label, record in [("depends", DependsRecord()), ("security", SecurityRecord())]:
            result[label] = {
                "assign_declared": _capture(lambda record=record: setattr(record, "dependency", 5)),
                "assign_new": _capture(lambda record=record: setattr(record, "note", "new")),
                "delete_declared": _capture(lambda record=record: delattr(record, "use_cache")),
                "delete_missing": _capture(lambda record=record: delattr(record, "missing")),
                "dictionary": dict(record.__dict__),
            }
        result["security_scopes_assignment"] = _capture(
            lambda: setattr(SecurityRecord(), "scopes", ["new"])
        )
        result["security_scopes_deletion"] = _capture(lambda: delattr(SecurityRecord(), "scopes"))
        return result

    @app.get("/bypass", include_in_schema=False)
    def bypass_state() -> dict[str, Any]:
        return _record_state(bypass_record)

    @app.post("/bypass/dictionary", include_in_schema=False)
    def bypass_dictionary() -> dict[str, Any]:
        bypass_record.__dict__["use_cache"] = "dictionary-value"
        bypass_record.__dict__["note"] = "independent-note"
        return _record_state(bypass_record)

    @app.post("/bypass/object", include_in_schema=False)
    def bypass_object() -> dict[str, Any]:
        object.__setattr__(bypass_record, "scope", ["object-value"])
        object.__setattr__(bypass_record, "extra", 53)
        object.__delattr__(bypass_record, "dependency")
        return _record_state(bypass_record)

    @app.get("/subclasses", include_in_schema=False)
    def subclasses() -> dict[str, Any]:
        result = {}
        for label, record in [
            ("depends", RecordDependsChild(59, False, "request")),
            ("security", RecordSecurityChild(61, True, "function", ["read"])),
        ]:
            assigned = _capture(lambda record=record: setattr(record, "note", "child-note"))
            note = record.__dict__.get("note")
            result[label] = {
                "assign_new": assigned,
                "new_attribute": note,
                "assign_inherited_field": _capture(
                    lambda record=record: setattr(record, "dependency", 2)
                ),
                "delete_inherited_field": _capture(lambda record=record: delattr(record, "scope")),
                "delete_new": _capture(lambda record=record: delattr(record, "note")),
                "delete_missing": _capture(lambda record=record: delattr(record, "missing")),
                "dictionary": dict(record.__dict__),
                "is_dataclass": dataclasses.is_dataclass(record),
            }
        result["security_declared_scopes_assignment"] = _capture(
            lambda: setattr(RecordSecurityChild(), "scopes", ["new"])
        )
        return result

    @app.get("/dataclass-fields", include_in_schema=False)
    def dataclass_fields() -> dict[str, Any]:
        return {
            "depends_class_is_dataclass": dataclasses.is_dataclass(DependsRecord),
            "security_class_is_dataclass": dataclasses.is_dataclass(SecurityRecord),
            "depends_instance_is_dataclass": dataclasses.is_dataclass(DependsRecord()),
            "security_instance_is_dataclass": dataclasses.is_dataclass(SecurityRecord()),
            "depends_class_fields": _field_projection(DependsRecord),
            "security_class_fields": _field_projection(SecurityRecord),
            "depends_instance_fields": _field_projection(DependsRecord()),
            "security_child_fields": _field_projection(RecordSecurityChild()),
            "depends_field_records_are_fields": all(
                isinstance(field, dataclasses.Field) for field in dataclasses.fields(DependsRecord)
            ),
            "inherited_field_identity": [
                child is parent
                for child, parent in zip(
                    dataclasses.fields(SecurityRecord),
                    dataclasses.fields(DependsRecord),
                    strict=False,
                )
            ],
        }

    @app.get("/dataclass-operations", include_in_schema=False)
    def dataclass_operations() -> dict[str, Any]:
        scopes_list = ["first"]
        original = SecurityRecord(67, False, "function", scopes_list)
        replaced = dataclasses.replace(original, use_cache=True, scope="request")
        copied = dataclasses.asdict(original)
        copied["scopes"].append("copy-only")
        nested = SecurityRecord(DependsRecord(71, False, "function"), True, None, ["nested"])
        return {
            "original": _record_values(original),
            "replaced": _record_values(replaced),
            "replacement_is_new": replaced is not original,
            "replacement_type_preserved": type(replaced) is type(original),
            "replacement_shares_scopes": replaced.scopes is scopes_list,
            "asdict": copied,
            "asdict_copies_scopes": copied["scopes"] is not scopes_list,
            "asdict_nested_records": dataclasses.asdict(nested),
            "asdict_list_factory": dataclasses.asdict(
                DependsRecord(73, True, "request"), dict_factory=list
            ),
            "replace_child": _record_state(
                dataclasses.replace(RecordDependsChild(79), use_cache=False)
            ),
            "replace_unrecognized_field": _capture(lambda: dataclasses.replace(original, extra=3)),
            "asdict_class_error": _capture(lambda: dataclasses.asdict(DependsRecord)),
            "replace_class_error": _capture(lambda: dataclasses.replace(SecurityRecord)),
        }

    @app.get("/encoding")
    def encoding():
        record = SecurityRecord(DependsRecord(83, False, "function"), True, None, ["read"])
        return {
            "automatic": record,
            "explicit": jsonable_encoder(record),
            "included": jsonable_encoder(record, include={"scopes", "use_cache"}),
            "excluded": jsonable_encoder(record, exclude={"dependency"}),
        }

    def read_seed(seed: int = 3) -> int:
        return seed * 2

    def first_selected(seed: int = 3) -> int:
        return seed + 1

    def last_selected(seed: int = 3) -> int:
        return seed + 10

    @app.post("/registration/{mode}", include_in_schema=False)
    def registration(mode: str) -> dict[str, Any]:
        def last_dependency(
            value: Annotated[int, DependsRecord(first_selected), SecurityRecord(last_selected)],
        ) -> dict[str, int]:
            return {"value": value}

        def field_then_dependency(
            value: Annotated[int, Query(..., alias="selected"), DependsRecord(last_selected)],
        ) -> dict[str, int]:
            return {"value": value}

        def dependency_then_field(
            value: Annotated[int, DependsRecord(first_selected), Query(..., alias="selected")],
        ) -> dict[str, int]:
            return {"value": value}

        def annotated_dependency_default(
            value: Annotated[int, DependsRecord(read_seed)] = DependsRecord(read_seed),  # noqa: B008
        ) -> dict[str, int]:
            return {"value": value}

        def annotated_field_default(
            value: Annotated[int, Query(...)] = DependsRecord(read_seed),  # noqa: B008
        ) -> dict[str, int]:
            return {"value": value}

        def parameterless_noncallable() -> dict[str, str]:
            return {"value": "independent-endpoint"}

        endpoints = {
            "last-dependency": last_dependency,
            "field-then-dependency": field_then_dependency,
            "dependency-then-field": dependency_then_field,
            "annotated-dependency-default": annotated_dependency_default,
            "annotated-field-default": annotated_field_default,
            "parameterless-noncallable": parameterless_noncallable,
        }

        def register_endpoint() -> dict[str, str]:
            dependencies = [DependsRecord(17)] if mode == "parameterless-noncallable" else []
            app.get(f"/registered/{mode}", dependencies=dependencies)(endpoints[mode])
            return {"registered_path": f"/registered/{mode}"}

        return _capture(register_endpoint)

    @app.get("/injection")
    def injection(
        default_value: int = DependsRecord(read_seed),  # noqa: B008
        annotated_value: Annotated[int, SecurityRecord(read_seed, scopes=["record:read"])] = 0,
        factory_value: Annotated[int, Depends(read_seed)] = 0,
        factory_security_value: Annotated[int, Security(read_seed, scopes=["record:write"])] = 0,
    ) -> dict[str, int]:
        return {
            "default": default_value,
            "annotated": annotated_value,
            "factory": factory_value,
            "factory_security": factory_security_value,
        }

    def side_effect() -> None:
        event_trace.append("parameterless")

    inferred_depends = DependsRecord()
    inferred_security = SecurityRecord(scopes=["record:read"])

    @app.get("/inferred", dependencies=[DependsRecord(side_effect)])
    def inferred(
        reader: Annotated[PayloadReader, inferred_depends],
        secured_reader: Annotated[PayloadReader, inferred_security],
    ) -> dict[str, Any]:
        return {
            "reader_seed": reader.seed,
            "secured_reader_seed": secured_reader.seed,
            "same_inferred_value": reader is secured_reader,
            "depends_declaration_unchanged": inferred_depends.dependency is None,
            "security_declaration_unchanged": inferred_security.dependency is None,
            "security_scopes": inferred_security.scopes,
            "events": list(event_trace),
        }

    def counted(seed: int = 3) -> dict[str, int]:
        calls["counted"] += 1
        event_trace.append(f"counted:{calls['counted']}")
        return {"seed": seed, "call": calls["counted"]}

    parameterless_uncached = DependsRecord(counted, use_cache=False)

    @app.get("/cache", dependencies=[parameterless_uncached])
    def cache(
        first: Annotated[dict[str, int], DependsRecord(counted)],
        second: Annotated[dict[str, int], SecurityRecord(counted, scopes=["cache:read"])],
        uncached: Annotated[dict[str, int], DependsRecord(counted, use_cache=False)],
    ) -> dict[str, Any]:
        return {
            "first": first,
            "second": second,
            "uncached": uncached,
            "cached_identity": first is second,
            "uncached_identity": first is uncached,
            "parameterless_declaration_use_cache": parameterless_uncached.use_cache,
            "calls": calls["counted"],
            "events": list(event_trace),
        }

    async def resource() -> AsyncIterator[str]:
        event_trace.append("dependency-enter")
        timeline.append("dependency-enter")
        try:
            yield "independent-resource"
        finally:
            event_trace.append("dependency-cleanup")
            timeline.append("dependency-cleanup")

    @app.get("/yield/function")
    async def function_scope(
        value: Annotated[str, SecurityRecord(resource, scope="function", scopes=["yield:read"])],
    ) -> dict[str, Any]:
        timeline.append("endpoint")
        return {"value": value, "events": list(event_trace)}

    @app.get("/yield/request")
    async def request_scope(
        value: Annotated[str, DependsRecord(resource, scope="request")],
    ) -> dict[str, Any]:
        timeline.append("endpoint")
        return {"value": value, "events": list(event_trace)}

    @app.get("/state", include_in_schema=False)
    def state() -> dict[str, list[str]]:
        return {"events": list(event_trace)}

    @app.get("/timeline", include_in_schema=False)
    def recorded_timeline() -> dict[str, list[str]]:
        return {"timeline": list(timeline)}

    return ResponseTimeline(app, timeline)
