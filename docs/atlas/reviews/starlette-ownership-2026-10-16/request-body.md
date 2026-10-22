# Request-body ownership review for documented examples — 2026-10-16

> Historical review against the 2026-10-16 atlas/source snapshot. Its row pointers and FastAPI 0.141.1 evidence are not active 0.157.0 source support; use the regenerated atlas and current mappings for the pinned baseline.

## Scope and pins

Read-only source audit of every documented-example row in tests/fixtures/compatibility-atlas.json whose request-body mapping has ownership_boundary set to “owner review required”. The five exact mapping pointers are /coverage_matrix/104/starlette_rs_contract_mappings/2, /coverage_matrix/105/starlette_rs_contract_mappings/2, /coverage_matrix/230/starlette_rs_contract_mappings/2, /coverage_matrix/239/starlette_rs_contract_mappings/2, and /coverage_matrix/240/starlette_rs_contract_mappings/3.

Sources checked:

- FastAPI 0.141.1, commit 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f.
- Starlette 1.6.0, commit 4f250d6b814587e20c5365f0a5f0c4d42bcb929f.
- Starlette-RS commit 4139a72449bf5751e8902fb1c7175ee7f191d338, pinned manifest SHA-256 86f69fc791088794fcd59483d6a91cc08bb9b3999586665f73c2f722f9946029.

No active overlay, generator, fixture, or recipe changed. No test, build, parity, or benchmark command was run.

## Ownership rule

FastAPI selects and parses declared Body fields, chooses automatic JSON decoding from Content-Type, extracts parameters, invokes validation, and maps request validation errors. Pydantic supplies field/model validation and schema generation. Starlette owns generic Request.body(), Request.stream(), and Request.json() mechanics. Endpoint code owns any manual interpretation of raw bytes, such as the magic-data mapping or YAML parsing.

A generated or custom OpenAPI requestBody is documentation output; it does not establish that an HTTP request body was parsed or validated. This distinction matters for the callback declaration and both openapi_extra examples.

In FastAPI routing, the handler reads request.body() and, for JSON media types, calls request.json() before sending the parsed value into FastAPI dependency/body solving (fastapi/routing.py:425-450). For Body fields, FastAPI extracts the value and invokes its model-field validator (fastapi/dependencies/utils.py:975-998; fastapi/_compat/v2.py:173-188, where TypeAdapter.validate_python is called). Starlette implements the underlying body stream, byte cache, and JSON decode at starlette/requests.py:234-266.

## Findings by exact row

### 1. Annotated custom APIRoute example

Atlas row: documented-example:docs_src/custom_request_and_route/tutorial002_an_py310.py, pointer /coverage_matrix/104/starlette_rs_contract_mappings/2.

The example declares numbers as Annotated[list[int], Body()] (../fastapi/docs_src/custom_request_and_route/tutorial002_an_py310.py:28-30). Its custom APIRoute wraps the normal handler, catches RequestValidationError, calls request.body() again, and includes the decoded original bytes in an HTTPException (lines 9-21). The mapped independent case is fastapi.source-wave-b.custom-route.validation-context, which sends one JSON object in one complete ASGI request event and observes HTTP status/body. It does not use fragmented body events.

Ownership is mixed but separable: FastAPI selects the Body field, reads the request and chooses JSON parsing (fastapi/routing.py:425-450); Pydantic validates list[int] through the FastAPI field adapter (fastapi/_compat/v2.py:173-188); Starlette supplies JSON decoding and cached raw bytes (starlette/requests.py:254-266); and the example's custom route formats the validation error and body into its HTTPException (docs source lines 13-19). The repeat body read exercises cached byte reuse. The HTTP response exposes byte content, not Python bytes-object identity.

### 2. Non-Annotated custom APIRoute example

Atlas row: documented-example:docs_src/custom_request_and_route/tutorial002_py310.py, pointer /coverage_matrix/105/starlette_rs_contract_mappings/2.

This variant declares numbers as list[int] = Body() and has the same custom wrapper and endpoint (../fastapi/docs_src/custom_request_and_route/tutorial002_py310.py:8-29). Its mapped cases are fastapi.source-wave-b.custom-route.valid-request and fastapi.source-wave-b.custom-route.validation-context. Both use one complete body event; the invalid-shape case also observes that the wrapper can read and return the submitted body after FastAPI has parsed it.

The owner split and generic Starlette scope are the same as row 104. The additional valid request observes successful FastAPI/Pydantic field processing. Neither case establishes chunk concatenation, repeated Request.json() caching, malformed JSON handling, or the Python object identity of cached bytes.

### 3. Callback example

Atlas row: documented-example:docs_src/openapi_callbacks/tutorial001_py310.py, pointer /coverage_matrix/230/starlette_rs_contract_mappings/2.

The source defines an InvoiceEvent callback route with a body model (../fastapi/docs_src/openapi_callbacks/tutorial001_py310.py:14-30), then attaches it to a separate /invoices/ route whose live body parameter is Invoice (lines 33-34). FastAPI documents callbacks as OpenAPI-only and says they are not used directly (fastapi/routing.py:3610-3624); OpenAPI generation places the route's requestBody in the operation and separately projects callback routes (fastapi/openapi/utils.py:377-402). Thus the InvoiceEvent callback body and its {$request.body.id} expression are schema declarations, not an incoming HTTP callback request. The root Invoice parameter is a live FastAPI/Pydantic body declaration.

The mapped independent case fastapi.docs.openapi-interface.advanced-openapi-callbacks.callback-operation dispatches a different typed body to /subscriptions and observes the HTTP response plus callback/requestBody OpenAPI pointers (tests/fixtures/input-recipes/parity/docs-openapi-interface.yaml). It does not deliver a callback and does not verify this source's Invoice or InvoiceEvent schemas. For the dispatched main route, FastAPI performs body selection and JSON decoding, Pydantic validates the model, and generic Starlette Request.body()/json() provides the underlying body/cache. Keep the callback declaration explicitly scoped to OpenAPI.

### 4. Raw body and manual OpenAPI example

Atlas row: documented-example:docs_src/path_operation_advanced_configuration/tutorial006_py310.py, pointer /coverage_matrix/239/starlette_rs_contract_mappings/2.

The route has a Request parameter, no FastAPI Body field, and reads await request.body() once before passing the bytes to magic_data_reader (../fastapi/docs_src/path_operation_advanced_configuration/tutorial006_py310.py:6-14,17-40). The mapped action sends one text/plain body in one complete ASGI request event. Starlette owns the raw byte read; magic_data_reader and the response data shape are application code. FastAPI is not automatically parsing or validating this payload as JSON or a Pydantic model.

The requestBody declaration in openapi_extra is a separate documentation projection (source lines 17-36); FastAPI merges route.openapi_extra into the generated operation (fastapi/openapi/utils.py:537-538). The paired GET /openapi.json observation checks that projection, not HTTP body handling. No existing sibling requirement precisely describes a single raw Request.body() call with one complete body event, so attach the operation reference without claiming body-cache-reuse, chunk-concatenation, or JSON-cache requirements.

### 5. Raw YAML body and manual Pydantic validation

Atlas row: documented-example:docs_src/path_operation_advanced_configuration/tutorial007_py310.py, pointer /coverage_matrix/240/starlette_rs_contract_mappings/3.

The endpoint receives Request, reads raw bytes once, calls yaml.safe_load, explicitly invokes Item.model_validate, catches YAML/Pydantic errors, and converts them to HTTPException (../fastapi/docs_src/path_operation_advanced_configuration/tutorial007_py310.py:22-32). Item.model_json_schema() supplies the schema embedded in openapi_extra (lines 8-19). The mapped valid, malformed, and invalid-item cases each send one complete body event; none is chunked. Starlette owns only the raw Request.body() byte collection. YAML interpretation and error conversion are endpoint code; Pydantic owns explicit model validation and schema generation. This is not FastAPI's declared-body parsing path.

The application/x-yaml requestBody added through openapi_extra is documentation, merged by FastAPI into the generated OpenAPI operation (fastapi/openapi/utils.py:537-538). The recipe separately observes HTTP results and the OpenAPI schema. Do not attribute YAML decoding or Item.model_validate to FastAPI or Starlette.

## Row-keyed overlay recommendations

For every reference below, use contract_id starlette-1.6.0-full, manifest_path tests/fixtures/manifest.yaml, and manifest SHA-256 86f69fc791088794fcd59483d6a91cc08bb9b3999586665f73c2f722f9946029. The exact generic operation is surface_id starlette.requests.Request, operation_id body-stream-json, source_path “starlette.requests.Request.body, Request.stream, and Request.json”. In the pinned manifest, its target support is python-package=supported and rust-native=unimplemented (tests/fixtures/manifest.yaml:17919,17986-18004).

| Atlas pointer / row key | Suggested ownership_boundary and scope | Exact generic Starlette requirement IDs |
| --- | --- | --- |
| /coverage_matrix/104/starlette_rs_contract_mappings/2 — custom_request_and_route/tutorial002_an_py310.py | FastAPI/Pydantic body validation with generic Starlette cached body; application-owned validation-error body projection. Link only the cached raw-body reuse; keep the custom route response and validation outside that reference. | starlette.request.body-cache-reuse, limited to byte-content reuse; object identity is not observable here. |
| /coverage_matrix/105/starlette_rs_contract_mappings/2 — custom_request_and_route/tutorial002_py310.py | Same boundary as row 104; add successful Body-field/Pydantic processing from the valid action. | starlette.request.body-cache-reuse, limited to byte-content reuse; object identity is not observable here. |
| /coverage_matrix/230/starlette_rs_contract_mappings/2 — openapi_callbacks/tutorial001_py310.py | FastAPI/Pydantic main-operation body; callback body is OpenAPI-only. Scope the Starlette reference to the actual dispatched main request, never to callback delivery. | starlette.request.body-cache-reuse for the dispatched typed JSON request's body()/json() flow; no callback runtime requirement. |
| /coverage_matrix/239/starlette_rs_contract_mappings/2 — path_operation_advanced_configuration/tutorial006_py310.py | Generic Starlette raw-body access plus application-defined response and FastAPI OpenAPI requestBody projection. Keep HTTP input and OpenAPI selectors separate. | None: one raw-body call, one complete ASGI message, no repeated read. |
| /coverage_matrix/240/starlette_rs_contract_mappings/3 — path_operation_advanced_configuration/tutorial007_py310.py | Generic Starlette raw-body access plus application YAML/Pydantic processing and FastAPI OpenAPI requestBody projection. Keep the HTTP YAML parser/validator distinct from the schema projection. | None: one raw-body call per action, one complete ASGI message, no repeated read. |

For the two Body-model custom-route examples and the dispatched typed main request in the callback mapping, body-cache-reuse is relevant because FastAPI's JSON path calls Request.body() before Request.json(), and the custom error path calls body() again. The sibling requirement specifically compares returned byte-object identity as well as values; these HTTP workflows can establish reusable body content but cannot establish object identity. The sibling contract describes this requirement at tests/fixtures/manifest.yaml:18008-18020.

Do not attach starlette.request.body-chunk-concatenation: all five mapped workflows supply one complete request event rather than fragmented chunks (pinned requirement description at tests/fixtures/manifest.yaml:18023-18033). Do not attach starlette.request.json-body-cache: none calls Request.json() repeatedly (requirement description at tests/fixtures/manifest.yaml:18143-18155). Do not attach starlette.request.json-chunked-body or starlette.applications.Starlette/request-dispatch for these body observations; the mapped JSON inputs are not split across request messages (the pinned JSON chunk requirement is at tests/fixtures/manifest.yaml:3063-3073). No support status should be attached to the FastAPI, Pydantic, or application-owned parts.

I recommend replacing the five generic owner-review placeholders with the explicit mixed-boundary labels above, adding only the Request operation reference and applicable requirement IDs, and setting those mapping statuses to linked-to-current-contract-slice. Preserve scope notes that the linked operation covers only generic Request mechanics and makes no FastAPI-RS parity claim. None needs to remain unresolved once each runtime body path and OpenAPI-only facet is stated separately; in particular, the callback row becomes clear when its callback body is called out as schema-only.

