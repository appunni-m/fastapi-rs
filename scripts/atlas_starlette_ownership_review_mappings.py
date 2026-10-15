"""Reviewed row-keyed Starlette ownership overlays for the 2026-10-15/16 audits.

These mappings classify source observations documented in
docs/atlas/reviews/starlette-ownership-2026-10-16 and earlier upstream-test
reviews. Starlette-RS links identify ownership only and do not establish
FastAPI-RS support or parity. The generator resolves each operation against
its pinned manifest and carries target support gaps into the atlas.
"""

from __future__ import annotations

from typing import Any

STARLETTE_RS_OWNERSHIP_ROW_OVERLAYS: dict[str, dict[str, dict[str, Any]]] = {}
STARLETTE_RS_OWNERSHIP_EXPECTED_FEATURE_COUNTS = {
    "status-codes": 126,
    "request-body": 15,
    "asgi-error-propagation": 4,
    "dependency-overrides": 15,
}


def _review_rows(
    feature_id: str,
    source_paths: tuple[str, ...],
    ownership_boundary: str,
    scope_note: str,
    operation_specs: tuple[tuple[str, str, tuple[str, ...]], ...] = (),
    row_key_prefix: str = "upstream-test",
) -> None:
    for source_path in source_paths:
        row_id = row_key_prefix + ":" + source_path
        row = STARLETTE_RS_OWNERSHIP_ROW_OVERLAYS.setdefault(row_id, {})
        if feature_id in row:
            raise ValueError(
                f"duplicate reviewed Starlette ownership mapping: {row_id}::{feature_id}"
            )
        row[feature_id] = {
            "ownership_boundary": ownership_boundary,
            "scope_note": scope_note,
            "operation_specs": operation_specs,
        }


_RESPONSE_STATUS = (
    (
        "starlette.responses.Response",
        "asgi-call",
        (
            "starlette.responses.Response.asgi-call.empty-response",
            "starlette.responses.Response.asgi-call.non-empty-response",
        ),
    ),
)
_RESPONSE_STATUS_NON_EMPTY = (
    (
        "starlette.responses.Response",
        "asgi-call",
        ("starlette.responses.Response.asgi-call.non-empty-response",),
    ),
)
_RESPONSE_STATUS_EMPTY = (
    (
        "starlette.responses.Response",
        "asgi-call",
        ("starlette.responses.Response.asgi-call.empty-response",),
    ),
)
_STREAMING_RESPONSE_STATUS = (
    *_RESPONSE_STATUS_NON_EMPTY,
    (
        "starlette.responses.StreamingResponse",
        "asgi-call",
        ("starlette.responses.StreamingResponse.asgi-call.unknown-size-content",),
    ),
)
_REQUEST_BODY_JSON = (
    (
        "starlette.requests.Request",
        "body-stream-json",
        (
            "starlette.request.body-cache-reuse",
            "starlette.request.body-chunk-concatenation",
            "starlette.request.json-body-cache",
        ),
    ),
)
_REQUEST_BODY_BYTES = (
    (
        "starlette.requests.Request",
        "body-stream-json",
        (
            "starlette.request.body-cache-reuse",
            "starlette.request.body-chunk-concatenation",
        ),
    ),
)
_REQUEST_DISPATCH_JSON = (
    (
        "starlette.applications.Starlette",
        "request-dispatch",
        ("starlette.request.json-chunked-body",),
    ),
)
_TESTCLIENT_EXCEPTION_POLICY = (
    (
        "starlette.testclient.TestClient",
        "request-response",
        ("starlette.testclient.TestClient.request-response.exception-policy",),
    ),
)


# Status-code review: FastAPI chooses validation, route, injected-response,
# and handled-exception statuses; Starlette's Response emits the unconfigured
# successful default, while Router/RedirectResponse own their exact cases.
_STATUS_VALIDATION = """FastAPI 0.141.1 raises RequestValidationError and its registered request-validation handler selects HTTP 422. This classifies the observed status selection only; the row's other FastAPI/Pydantic behavior and generic response emission are separate. Ownership mapping only; no FastAPI-RS parity claim."""
_STATUS_ROUTE = """FastAPI 0.141.1 selects the observed status through path-operation configuration, an injected Response value, or its HTTPException handler. Starlette emits the resulting response but does not choose this status. Ownership mapping only; no FastAPI-RS parity claim."""
_STATUS_DEFAULT = """The reviewed status observation is the default HTTP 200. Starlette 1.6.0 Response defaults status_code to 200 and emits it in http.response.start; the row does not select another status. The operation link identifies generic ownership only and does not establish FastAPI-RS parity."""

_review_rows(
    "status-codes",
    (
        "tests/test_dependency_overrides.py",
        "tests/test_enforce_once_required_parameter.py",
        "tests/test_forms_single_model.py",
        "tests/test_query.py",
        "tests/test_query_cookie_header_model_extra_params.py",
        "tests/test_regex_deprecated_body.py",
        "tests/test_regex_deprecated_params.py",
        "tests/test_request_params/test_body/test_list.py",
        "tests/test_request_params/test_body/test_optional_list.py",
        "tests/test_request_params/test_body/test_optional_str.py",
        "tests/test_request_params/test_body/test_required_str.py",
        "tests/test_request_params/test_cookie/test_required_str.py",
        "tests/test_request_params/test_file/test_list.py",
        "tests/test_request_params/test_file/test_required.py",
        "tests/test_request_params/test_form/test_list.py",
        "tests/test_request_params/test_form/test_required_str.py",
        "tests/test_request_params/test_header/test_list.py",
        "tests/test_request_params/test_header/test_required_str.py",
        "tests/test_request_params/test_query/test_list.py",
        "tests/test_request_params/test_query/test_required_str.py",
        "tests/test_strict_content_type_router_level.py",
    ),
    "FastAPI-owned validation status selection",
    _STATUS_VALIDATION,
)
_review_rows(
    "status-codes",
    (
        "tests/test_response_change_status_code.py",
        "tests/test_starlette_exception.py",
        "tests/test_stream_status_code.py",
        "tests/test_tutorial/test_path_operation_configurations/test_tutorial001.py",
        "tests/test_tutorial/test_response_change_status_code/test_tutorial001.py",
        "tests/test_tutorial/test_response_status_code/test_tutorial001_tutorial002.py",
        "tests/test_return_none_stringified_annotations.py",
        "tests/test_tutorial/test_authentication_error_status_code/test_tutorial001.py",
        "tests/test_tutorial/test_sql_databases/test_tutorial001.py",
    ),
    "FastAPI-owned route or exception status selection",
    _STATUS_ROUTE,
)
_review_rows(
    "status-codes",
    (
        "tests/benchmarks/test_general_performance.py",
        "tests/test_deprecated_responses.py",
        "tests/test_file_and_form_order_issue_9116.py",
        "tests/test_form_default.py",
        "tests/test_forms_from_non_typing_sequences.py",
        "tests/test_forms_single_param.py",
        "tests/test_get_request_body.py",
        "tests/test_infer_param_optionality.py",
        "tests/test_list_bytes_file_order_preserved_issue_14811.py",
        "tests/test_optional_file_list.py",
        "tests/test_param_class.py",
        "tests/test_param_in_path_and_dependency.py",
        "tests/test_param_include_in_schema.py",
        "tests/test_put_no_body.py",
        "tests/test_repeated_parameter_alias.py",
        "tests/test_request_body_parameters_media_type.py",
        "tests/test_request_params/test_cookie/test_optional_str.py",
        "tests/test_request_params/test_file/test_optional.py",
        "tests/test_request_params/test_file/test_optional_list.py",
        "tests/test_request_params/test_form/test_optional_list.py",
        "tests/test_request_params/test_form/test_optional_str.py",
        "tests/test_request_params/test_header/test_optional_list.py",
        "tests/test_request_params/test_header/test_optional_str.py",
        "tests/test_request_params/test_path/test_required_str.py",
        "tests/test_request_params/test_query/test_optional_list.py",
        "tests/test_request_params/test_query/test_optional_str.py",
        "tests/test_response_model_as_return_annotation.py",
        "tests/test_router_prefix_with_template.py",
        "tests/test_starlette_urlconvertors.py",
        "tests/test_stringified_annotation_dependency.py",
        "tests/test_stringified_annotation_dependency_py314.py",
        "tests/test_stringified_annotations_simple.py",
        "tests/test_tutorial/test_background_tasks/test_tutorial002.py",
        "tests/test_tutorial/test_custom_response/test_tutorial001.py",
        "tests/test_tutorial/test_settings/test_app03.py",
        "tests/test_tutorial/test_settings/test_tutorial001.py",
        "tests/test_tutorial/test_using_request_directly/test_tutorial001.py",
    ),
    "Starlette-owned default response status emission",
    _STATUS_DEFAULT,
    _RESPONSE_STATUS,
)
_review_rows(
    "status-codes",
    ("tests/test_tutorial/test_templates/test_tutorial001.py",),
    "Starlette-owned template and static response status emission",
    """This row observes 200 statuses from Starlette's template and static-file response paths. The exact pinned Jinja2Templates and StaticFiles references preserve their Python-only versus native target support states; they do not establish FastAPI-RS parity.""",
    (
        *_RESPONSE_STATUS,
        (
            "starlette.templating.Jinja2Templates",
            "template-response",
            ("starlette.templating._TemplateResponse.template-context-metadata",),
        ),
        (
            "starlette.staticfiles.StaticFiles",
            "asgi-call",
            ("starlette.staticfiles.StaticFiles.asgi-call.rooted-file-get",),
        ),
    ),
)
_review_rows(
    "status-codes",
    ("tests/test_tutorial/test_wsgi/test_tutorial001.py",),
    "Starlette-owned WSGI response status emission",
    """This row observes the response produced by Starlette 1.6.0 WSGIMiddleware. The response-order requirement carries the Python-only/native-unimplemented support state; this is an ownership link, not FastAPI-RS parity.""",
    (
        (
            "starlette.middleware.wsgi.WSGIMiddleware",
            "__call__",
            ("starlette.middleware.wsgi.WSGIMiddleware.response-order",),
        ),
    ),
)
_review_rows(
    "status-codes",
    ("tests/test_router_include_context.py",),
    "Starlette-owned router miss and response status emission",
    """The module's custom included-route miss is a generic Starlette Router 404 and its matched route returns the default 200. The pinned request-dispatch miss requirement and Response ASGI operation link only these generic observations; FastAPI include-context behavior remains separate. Ownership only; no parity claim.""",
    (
        (
            "starlette.applications.Starlette",
            "request-dispatch",
            ("starlette.routing.items-route-miss-404",),
        ),
        *_RESPONSE_STATUS,
    ),
)
_review_rows(
    "status-codes",
    ("tests/test_router_redirect_slashes.py",),
    "Starlette-owned router redirect and response status selection",
    """Starlette 1.6.0 Router selects 307 for an enabled slash redirect and 404 when redirecting is disabled. The pinned Router and RedirectResponse references cover only these generic outcomes; ownership links do not claim FastAPI-RS parity.""",
    (
        (
            "starlette.routing.Router",
            "route-dispatch",
            (
                "starlette.routing.Router.route-dispatch.redirect-slash-append-root-path-query",
                "starlette.routing.Router.route-dispatch.redirect-disabled",
            ),
        ),
        (
            "starlette.responses.RedirectResponse",
            "asgi-call",
            ("starlette.responses.RedirectResponse.asgi-call.default-relative-location",),
        ),
    ),
)
_review_rows(
    "status-codes",
    (
        "tests/test_path.py",
        "tests/test_frontend.py",
        "tests/test_tutorial/test_graphql/test_tutorial001.py",
    ),
    "Mixed-owner status observations unresolved at module-row granularity",
    """The source audit found distinct status owners inside this module row: FastAPI validation or frontend statuses plus a Starlette route miss/response, or a third-party Strawberry response beside FastAPI OpenAPI. No single exact owner or operation reference represents the row; retain it unresolved until narrower case mappings exist. This does not claim parity.""",
)


# Documented Python examples: source paths and line-level status evidence are
# recorded in the tracked review table; links cover only generic emission.
_STATUS_DOC_NON_EMPTY_NOTE = """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/status-codes.md records the exact status-selection lines for this row. FastAPI or example code selects explicit statuses; Starlette Response supplies the generic default and emits the response. This link covers only non-empty response status/body emission and does not establish FastAPI-RS parity."""
_STATUS_DOC_EMPTY_NOTE = """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/status-codes.md records the exact route configuration for this row. FastAPI configures RedirectResponse with 302; this link covers generic empty-response status emission, not RedirectResponse's unrelated default 307 behavior. No FastAPI-RS parity is claimed."""
_STATUS_DOC_STREAM_NOTE = """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/status-codes.md records the exact status sites for this row. Application/FastAPI code selects error statuses; Starlette StreamingResponse supplies the successful stream's default 200 and emits it. Links cover only generic response and finite synchronous stream emission; no FastAPI-RS parity is claimed."""

_review_rows(
    "status-codes",
    (
        "docs_src/additional_responses/tutorial001_py310.py",
        "docs_src/additional_responses/tutorial003_py310.py",
        "docs_src/additional_status_codes/tutorial001_an_py310.py",
        "docs_src/additional_status_codes/tutorial001_py310.py",
        "docs_src/app_testing/tutorial002_py310.py",
        "docs_src/app_testing/tutorial003_py310.py",
        "docs_src/app_testing/tutorial004_py310.py",
        "docs_src/authentication_error_status_code/tutorial001_an_py310.py",
        "docs_src/bigger_applications/app_an_py310/dependencies.py",
        "docs_src/bigger_applications/app_an_py310/routers/items.py",
        "docs_src/custom_request_and_route/tutorial002_an_py310.py",
        "docs_src/custom_request_and_route/tutorial002_py310.py",
        "docs_src/custom_response/tutorial003_py310.py",
        "docs_src/custom_response/tutorial004_py310.py",
        "docs_src/dependencies/tutorial006_an_py310.py",
        "docs_src/dependencies/tutorial006_py310.py",
        "docs_src/dependencies/tutorial008b_an_py310.py",
        "docs_src/dependencies/tutorial008b_py310.py",
        "docs_src/dependencies/tutorial008c_an_py310.py",
        "docs_src/dependencies/tutorial008c_py310.py",
        "docs_src/dependencies/tutorial008d_an_py310.py",
        "docs_src/dependencies/tutorial008d_py310.py",
        "docs_src/dependencies/tutorial012_an_py310.py",
        "docs_src/dependencies/tutorial012_py310.py",
        "docs_src/dependency_testing/tutorial001_an_py310.py",
        "docs_src/dependency_testing/tutorial001_py310.py",
        "docs_src/handling_errors/tutorial001_py310.py",
        "docs_src/handling_errors/tutorial002_py310.py",
        "docs_src/handling_errors/tutorial003_py310.py",
        "docs_src/handling_errors/tutorial004_py310.py",
        "docs_src/handling_errors/tutorial005_py310.py",
        "docs_src/handling_errors/tutorial006_py310.py",
        "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
        "docs_src/path_operation_configuration/tutorial001_py310.py",
        "docs_src/response_change_status_code/tutorial001_py310.py",
        "docs_src/response_status_code/tutorial001_py310.py",
        "docs_src/response_status_code/tutorial002_py310.py",
        "docs_src/security/tutorial003_an_py310.py",
        "docs_src/security/tutorial003_py310.py",
        "docs_src/security/tutorial004_an_py310.py",
        "docs_src/security/tutorial004_py310.py",
        "docs_src/security/tutorial005_an_py310.py",
        "docs_src/security/tutorial005_py310.py",
        "docs_src/security/tutorial007_an_py310.py",
        "docs_src/security/tutorial007_py310.py",
        "docs_src/sql_databases/tutorial001_an_py310.py",
        "docs_src/sql_databases/tutorial001_py310.py",
        "docs_src/sql_databases/tutorial002_an_py310.py",
        "docs_src/sql_databases/tutorial002_py310.py",
    ),
    "FastAPI/application status selection with generic Starlette response emission",
    _STATUS_DOC_NON_EMPTY_NOTE,
    _RESPONSE_STATUS_NON_EMPTY,
    row_key_prefix="documented-example",
)
_review_rows(
    "status-codes",
    ("docs_src/custom_response/tutorial006c_py310.py",),
    "FastAPI-configured redirect status with generic empty-response emission",
    _STATUS_DOC_EMPTY_NOTE,
    _RESPONSE_STATUS_EMPTY,
    row_key_prefix="documented-example",
)
_review_rows(
    "status-codes",
    (
        "docs_src/dependencies/tutorial013_an_py310.py",
        "docs_src/dependencies/tutorial014_an_py310.py",
    ),
    "Application-selected errors with generic streaming-response status emission",
    _STATUS_DOC_STREAM_NOTE,
    _STREAMING_RESPONSE_STATUS,
    row_key_prefix="documented-example",
)


# Request-body review: link only generic receive/parse/value operations and
# leave FastAPI extraction, validation, OpenAPI, and app-defined behavior local.
_BODY_FORM_URLENCODED = (
    (
        "starlette.requests.Request",
        "form",
        ("starlette.request.form.urlencoded-fields",),
    ),
)
_BODY_FORM_MULTIPART = (
    (
        "starlette.requests.Request",
        "form",
        ("starlette.request.form.multipart-form-data",),
    ),
    (
        "starlette.datastructures.FormData",
        "multidict-lookups",
        ("starlette.datastructures.FormData.close",),
    ),
    (
        "starlette.datastructures.UploadFile",
        "file-operations",
        ("starlette.datastructures.UploadFile.file-operations",),
    ),
)
_BODY_JSON = (*_REQUEST_BODY_JSON, *_REQUEST_DISPATCH_JSON)
_BODY_BYTES = _REQUEST_BODY_BYTES
_BODY_DOC_CACHE_REUSE = (
    (
        "starlette.requests.Request",
        "body-stream-json",
        ("starlette.request.body-cache-reuse",),
    ),
)

_review_rows(
    "request-body",
    ("tests/test_datastructures.py",),
    "FastAPI cleanup plus generic Starlette multipart and upload behavior",
    """FastAPI schedules request-scoped cleanup; Starlette 1.6.0 parses multipart data and owns FormData.close and UploadFile operations. The exact generic references expose Python-only/native-unimplemented gaps; they do not cover FastAPI cleanup or claim parity.""",
    _BODY_FORM_MULTIPART,
)
_review_rows(
    "request-body",
    ("tests/test_forms_single_param.py",),
    "FastAPI form binding with generic Starlette form parsing",
    """Starlette 1.6.0 parses URL-encoded fields into FormData; FastAPI binds Form() to the endpoint parameter and owns validation and OpenAPI projection. The parser reference retains its native-unimplemented status and is not a FastAPI-RS support claim.""",
    _BODY_FORM_URLENCODED,
)
_review_rows(
    "request-body",
    ("tests/test_get_request_body.py",),
    "FastAPI body inference with generic Starlette JSON receipt",
    """FastAPI owns GET-body inference, field extraction, validation/error placement, and response integration. Starlette 1.6.0 owns generic body buffering/JSON decoding; its Request object is Python-package-only for this operation, while request-dispatch JSON coverage is bounded and partial. Ownership only; no parity claim.""",
    _BODY_JSON,
)
_review_rows(
    "request-body",
    ("tests/test_regex_deprecated_body.py",),
    "FastAPI Form validation with generic Starlette form parsing",
    """Starlette 1.6.0 parses URL-encoded form values; FastAPI owns Form binding, deprecated regex metadata/warnings, request error placement, and schema projection, while Pydantic supplies the pattern validator. The form reference preserves the native-unimplemented gap and makes no parity claim.""",
    _BODY_FORM_URLENCODED,
)
_review_rows(
    "request-body",
    ("tests/test_request_body_parameters_media_type.py",),
    "FastAPI-owned OpenAPI request-body projection",
    """The mapped test observes Body(media_type), embed, and a combined OpenAPI request schema; it sends no HTTP body. No Starlette parser reference applies, and this association is not runtime request-body support evidence.""",
)
_review_rows(
    "request-body",
    ("tests/test_router_include_context.py",),
    "Mixed FastAPI body-field composition and generic Starlette JSON receipt",
    """Starlette 1.6.0 receives and decodes the JSON body; FastAPI owns app/router/include/route body-field merging, extraction, validation/error mapping, and OpenAPI projection. The native request-dispatch link is bounded; the Python Request operation is unimplemented in the Rust-native lane. These ownership links do not imply parity.""",
    _BODY_JSON,
)
_review_rows(
    "request-body",
    ("tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial006.py",),
    "Generic Starlette raw-body access plus FastAPI OpenAPI projection",
    """The endpoint reads generic Request.body() bytes and passes them to tutorial code; it declares no FastAPI body parameter or Pydantic request validation. The separate openapi_extra schema is FastAPI-owned. The Request reference is Python-package-only; no FastAPI-RS parity is claimed.""",
    _BODY_BYTES,
)
_review_rows(
    "request-body",
    ("tests/test_tutorial/test_path_operation_advanced_configurations/test_tutorial007.py",),
    "Generic Starlette raw-body access with application-defined parsing",
    """Only Request.body() byte collection is generic Starlette behavior. YAML decoding, explicit Item.model_validate, HTTPException conversion, and custom OpenAPI requestBody data are endpoint/FastAPI behavior. The Request reference is Python-package-only; this does not claim FastAPI-RS parity.""",
    _BODY_BYTES,
)
_review_rows(
    "request-body",
    ("tests/test_tutorial/test_generate_clients/test_tutorial004.py",),
    "FastAPI-owned OpenAPI snapshot; runtime body behavior excluded",
    """This excluded test rewrites and snapshots a generated OpenAPI document containing requestBody entries; it does not send an ASGI request or exercise body receipt, extraction, or validation. Keep its existing exclusion; the association is not runtime support evidence.""",
)
_review_rows(
    "request-body",
    ("tests/test_tutorial/test_sql_databases/test_tutorial001.py",),
    "Excluded FastAPI body parameter with generic Starlette JSON receipt",
    """The source includes FastAPI JSON parameter/OpenAPI behavior with generic JSON decoding, but the SQLModel/SQLAlchemy/SQLite tutorial remains excluded as a whole. The links classify ownership only and do not turn this row into independent request-body parity evidence.""",
    _BODY_JSON,
)

_BODY_DOC_CACHE_NOTE = """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/request-body.md identifies the exact example and independent input. The link is limited to repeated Request.body() byte-content reuse; FastAPI field parsing/validation, custom route behavior, and OpenAPI projection remain separate. These HTTP observations do not prove Python bytes-object identity or FastAPI-RS parity."""
_review_rows(
    "request-body",
    (
        "docs_src/custom_request_and_route/tutorial002_an_py310.py",
        "docs_src/custom_request_and_route/tutorial002_py310.py",
        "docs_src/openapi_callbacks/tutorial001_py310.py",
    ),
    "FastAPI/Pydantic body behavior with narrowly observed generic Request cache reuse",
    _BODY_DOC_CACHE_NOTE,
    _BODY_DOC_CACHE_REUSE,
    row_key_prefix="documented-example",
)
_review_rows(
    "request-body",
    (
        "docs_src/path_operation_advanced_configuration/tutorial006_py310.py",
        "docs_src/path_operation_advanced_configuration/tutorial007_py310.py",
    ),
    "Generic raw Request body access with application-defined processing and FastAPI OpenAPI projection",
    """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/request-body.md records the exact endpoint lines and mapped actions. Each action reads one complete raw body once; no existing sibling requirement isolates that observation. YAML parsing/manual Pydantic validation (where present) is application-owned, openapi_extra is FastAPI-owned, and no FastAPI-RS parity is claimed.""",
    row_key_prefix="documented-example",
)


# Error and dependency review: link the outer Starlette HTTP policy only where
# the reports identify it; accepted-session WebSocket propagation stays open.
_review_rows(
    "asgi-error-propagation",
    ("tests/test_dependency_after_yield_raise.py",),
    "FastAPI dependency cleanup plus generic Starlette TestClient exception policy",
    """FastAPI owns yield-dependency cleanup and the caught-error-to-HTTPException 418 transformation. The exact Starlette TestClient reference applies only to uncaught HTTP exception propagation/suppression cases in this module; it does not own FastAPI cleanup or the handled 418 response and does not imply parity.""",
    _TESTCLIENT_EXCEPTION_POLICY,
)
_review_rows(
    "asgi-error-propagation",
    ("tests/test_dependency_after_yield_websockets.py",),
    "FastAPI dependency wiring; accepted-WebSocket app-error propagation unresolved",
    """FastAPI owns dependency resolution and the request exit stack. The observed ValueError occurs after websocket.accept and is surfaced when the accepted session exits; the pinned Starlette-RS contract has no exact post-accept/context-exit reference. Keep this generic gap unresolved until that exact sequence is covered; no parity claim.""",
)
_review_rows(
    "asgi-error-propagation",
    ("tests/test_response_model_as_return_annotation.py",),
    "FastAPI response validation plus generic Starlette TestClient exception policy",
    """FastAPI owns inferred response-model validation, ResponseValidationError, and invalid response-field construction. The exact TestClient reference covers only default HTTP exception re-raise behavior; the tests assert the FastAPI exception, not a generic Starlette 500 body. Ownership only; no parity claim.""",
    _TESTCLIENT_EXCEPTION_POLICY,
)
_review_rows(
    "asgi-error-propagation",
    ("tests/test_tutorial/test_dependencies/test_tutorial008c.py",),
    "FastAPI swallowed-yield guard plus generic Starlette HTTP 500/TestClient policy",
    """FastAPI owns the swallowed-yield-exception guard and FastAPIError. Starlette owns the outer default 500 response and TestClient raise_server_exceptions policy; handled FastAPI HTTPException behavior in the module remains separate. These exact links are ownership only and do not claim parity.""",
    (
        (
            "starlette.applications.Starlette",
            "__call__",
            ("starlette.asgi.server-error.default-response",),
        ),
        *_TESTCLIENT_EXCEPTION_POLICY,
    ),
)
_review_rows(
    "dependency-overrides",
    ("tests/test_dependency_overrides.py",),
    "FastAPI-owned dependency override lookup and graph reconstruction",
    """FastAPI looks up the original dependency, rebuilds a Dependant from the replacement callable, and recursively solves the replacement graph. The cases cover direct/nested overrides and validation, not repeated dependency cache semantics; no exact generic Starlette operation or parity claim applies.""",
)
_review_rows(
    "dependency-overrides",
    ("tests/test_frontend.py",),
    "FastAPI-owned frontend dependency injection and overrides",
    """FastAPI applies frontend app/router dependencies and the dependency_overrides solver; the observed 401 is a handled FastAPI HTTPException, not unhandled ASGI propagation. The tests do not measure dependency cache behavior; no exact generic Starlette operation or parity claim applies.""",
)
_review_rows(
    "dependency-overrides",
    ("tests/test_tutorial/test_settings/test_app02.py",),
    "FastAPI-owned settings dependency override",
    """FastAPI replaces get_settings through dependency_overrides and passes the replacement Settings value to the route. The source does not assert cache hits or invalidation; no exact generic Starlette operation or parity claim applies.""",
)

_DEPENDENCY_OVERRIDE_DOC_NOTE = """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/dependency-overrides.md identifies the paired example and independent ASGI case. FastAPI owns override lookup, replacement dependency graph construction, and solving; Starlette app dispatch and response emission are separate atlas boundaries. The link records ownership only and does not claim FastAPI-RS parity."""
_review_rows(
    "dependency-overrides",
    (
        "docs_src/dependency_testing/tutorial001_an_py310.py",
        "docs_src/dependency_testing/tutorial001_py310.py",
        "docs_src/settings/app02_an_py310/main.py",
        "docs_src/settings/app02_an_py310/test_main.py",
        "docs_src/settings/app02_py310/main.py",
        "docs_src/settings/app02_py310/test_main.py",
    ),
    "FastAPI-owned dependency override resolution",
    _DEPENDENCY_OVERRIDE_DOC_NOTE,
    row_key_prefix="documented-example",
)
_review_rows(
    "dependency-overrides",
    (
        "docs_src/settings/app01_py310/main.py",
        "docs_src/settings/app03_an_py310/main.py",
        "docs_src/settings/app03_py310/main.py",
        "docs_src/settings/tutorial001_py310.py",
    ),
    "Page-inherited dependency-override association; no override observed",
    """The tracked source audit at docs/atlas/reviews/starlette-ownership-2026-10-16/dependency-overrides.md records these exact settings example rows. Their source/workload demonstrates global settings projection or ordinary Depends injection, not dependency_overrides lookup or replacement. The association is inherited from the page; no sibling operation or parity claim applies.""",
    row_key_prefix="documented-example",
)
_review_rows(
    "dependency-overrides",
    ("advanced/settings.md",),
    "FastAPI-owned dependency override resolution documented by the settings page",
    """The pinned page documents a get_settings dependency replacement at docs/en/docs/advanced/settings.md:175-184; the settings-doc-review-20261015 case observes one replacement response. FastAPI owns override lookup and solving. Generic ASGI/response behavior is represented by separate feature mappings; no Starlette operation or FastAPI-RS parity is claimed here.""",
    row_key_prefix="documented-page",
)
_review_rows(
    "dependency-overrides",
    ("reference/fastapi.md",),
    "FastAPI-owned dependency_overrides public attribute documented by the API reference",
    """The pinned API reference lists dependency_overrides at docs/en/docs/reference/fastapi.md:17, and FastAPI initializes the public mapping in fastapi/applications.py:967-984. This page's selected OpenAPI case does not exercise overrides; the separate dependency-lifecycle case fastapi.dependencies.override-resolution covers one mapping and request result. Starlette has no dependency-override operation, and no FastAPI-RS parity is claimed by this association.""",
    row_key_prefix="documented-page",
)
