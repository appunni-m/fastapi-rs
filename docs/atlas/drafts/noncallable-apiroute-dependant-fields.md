# Draft review: non-callable `APIRoute` and `Dependant` fields

**State:** superseded draft; do not use its proposed classifications. The active pinned review now classifies all 56 `APIRoute`/`Dependant` candidates: 3 supported, 50 private/internal, and 3 uncertain. See `tests/fixtures/api-public-candidate-classification-review.json` and generated `tests/fixtures/compatibility-atlas.json`. This file remains outside active atlas inputs.

## Pinned evidence

- FastAPI `0.141.1`, commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` (the authority pin in `metadata.yaml`). The sibling checkout is clean at that revision.
- `fastapi/routing.py` SHA-256: `7b1ef65fb6b209445dc43be070a23324b7879aef9c6b9f63e6968234b7723b55`.
- `fastapi/dependencies/models.py` SHA-256: `dc4a46a8003677cf398ebd4435df8f8fc7b56fcd2e1983ed3226239d41dba777`.
- The current atlas has 51 matching field candidates: 32 `fastapi.routing.APIRoute.*` and 19 `fastapi.dependencies.models.Dependant.*`. All 51 are currently `uncertain`, have `visibility: public`, and have empty `public_evidence`.

The atlas policy permits `supported` only when a consumer-facing source/docs contract exists; it permits `private/internal` where review finds implementation use but no consumer contract. This review treats documentation of a path-operation argument as evidence for that input's behavior, but not automatically as a guarantee that consumers may read the corresponding `APIRoute` instance attribute. Where that exact attribute contract is not established, the proposal remains `uncertain`.

## `APIRoute` fields (32)

`APIRoute` declares these fields at `fastapi/routing.py:1126-1159`; `_populate_api_route_state` assigns or derives them at `fastapi/routing.py:992-1124`. The documented custom-route guide demonstrates subclassing and overriding `get_route_handler` (`docs/en/docs/how-to/custom-request-and-route.md:49-51,101-103`). The release notes describe custom `APIRoute` subclasses as undocumented/experimental (`docs/en/docs/release-notes.md:376-387`). This supports being cautious about extending that guide into contracts for every instance field.

### Supported

| Candidate ID | Proposal | Evidence and rationale |
|---|---|---|
| `fastapi.routing.APIRoute.response_class` | `supported` | Exact instance-attribute evidence: pinned release notes explicitly discuss advanced access to `route.response_class` and its `DefaultPlaceholder` behavior (`docs/en/docs/release-notes.md:6177-6179`). Declaration: `fastapi/routing.py:1140`. |

### Uncertain: documented route inputs, unproven instance-attribute contract

The referenced docs describe these values as path-operation/router configuration (for example, `operation_id`, `include_in_schema`, and `openapi_extra` in `docs/en/docs/advanced/path-operation-advanced-configuration.md:11-37,83-128`; response-model options in `docs/en/docs/tutorial/response-model.md`; `response_description` in `docs/en/docs/tutorial/path-operation-configuration.md:71-77`; and `strict_content_type` in `docs/en/docs/advanced/strict-content-type.md:78-80`). The matching fields are assigned to the route in the pinned source, but those docs do not promise reading them as stable `APIRoute` attributes. Keep these candidates uncertain pending an explicit member-level contract decision.

| Candidate ID | Proposal | Source declaration |
|---|---|---|
| `fastapi.routing.APIRoute.callbacks` | `uncertain` | `fastapi/routing.py:1142` |
| `fastapi.routing.APIRoute.dependencies` | `uncertain` | `fastapi/routing.py:1152` |
| `fastapi.routing.APIRoute.deprecated` | `uncertain` | `fastapi/routing.py:1131` |
| `fastapi.routing.APIRoute.description` | `uncertain` | `fastapi/routing.py:1153` |
| `fastapi.routing.APIRoute.include_in_schema` | `uncertain` | `fastapi/routing.py:1139` |
| `fastapi.routing.APIRoute.openapi_extra` | `uncertain` | `fastapi/routing.py:1143` |
| `fastapi.routing.APIRoute.operation_id` | `uncertain` | `fastapi/routing.py:1132` |
| `fastapi.routing.APIRoute.response_description` | `uncertain` | `fastapi/routing.py:1130` |
| `fastapi.routing.APIRoute.response_model` | `uncertain` | `fastapi/routing.py:1128` |
| `fastapi.routing.APIRoute.response_model_by_alias` | `uncertain` | `fastapi/routing.py:1135` |
| `fastapi.routing.APIRoute.response_model_exclude` | `uncertain` | `fastapi/routing.py:1134` |
| `fastapi.routing.APIRoute.response_model_exclude_defaults` | `uncertain` | `fastapi/routing.py:1137` |
| `fastapi.routing.APIRoute.response_model_exclude_none` | `uncertain` | `fastapi/routing.py:1138` |
| `fastapi.routing.APIRoute.response_model_exclude_unset` | `uncertain` | `fastapi/routing.py:1136` |
| `fastapi.routing.APIRoute.response_model_include` | `uncertain` | `fastapi/routing.py:1133` |
| `fastapi.routing.APIRoute.responses` | `uncertain` | `fastapi/routing.py:1147` |
| `fastapi.routing.APIRoute.status_code` | `uncertain` | `fastapi/routing.py:1149` |
| `fastapi.routing.APIRoute.strict_content_type` | `uncertain` | `fastapi/routing.py:1145` |
| `fastapi.routing.APIRoute.summary` | `uncertain` | `fastapi/routing.py:1129` |
| `fastapi.routing.APIRoute.tags` | `uncertain` | `fastapi/routing.py:1146` |

### Uncertain: route callback and generated identifier fields

| Candidate ID | Proposal | Evidence and rationale |
|---|---|---|
| `fastapi.routing.APIRoute.generate_unique_id_function` | `uncertain` | Declared/assigned at `fastapi/routing.py:1144,1013`. The advanced configuration docs say the configured function receives an `APIRoute` and returns an operation ID (`docs/en/docs/advanced/path-operation-advanced-configuration.md:19-21`), but do not promise this particular attribute as a readable member. |
| `fastapi.routing.APIRoute.unique_id` | `uncertain` | Declared at `fastapi/routing.py:1148`, computed from `operation_id` or the configured generator at `fastapi/routing.py:1028-1030`, and used for OpenAPI/model naming. The public docs establish operation-ID behavior but do not establish `APIRoute.unique_id` as an attribute contract. |

### Private/internal: derived runtime and model state

These fields are created for FastAPI's request, dependency, response-model, and OpenAPI machinery. The cited source demonstrates implementation consumers; the reviewed docs do not promise field-level access.

| Candidate ID | Proposal | Evidence and rationale |
|---|---|---|
| `fastapi.routing.APIRoute.body_field` | `private/internal` | Built from the dependency graph and body parameters at `fastapi/routing.py:1058-1068`; passed to the request handler at `fastapi/routing.py:1233-1240`. |
| `fastapi.routing.APIRoute.dependant` | `private/internal` | Built by `_build_dependant_with_parameterless_dependencies` at `fastapi/routing.py:1058-1064`; consumed by request handling and OpenAPI generation (`fastapi/routing.py:1233`; `fastapi/openapi/utils.py:331-379`). |
| `fastapi.routing.APIRoute.dependency_overrides_provider` | `private/internal` | Wiring passed into request handling at `fastapi/routing.py:1244` and dependency solving; no field-level consumer docs found. |
| `fastapi.routing.APIRoute.is_json_stream` | `private/internal` | Derived from the endpoint/response class at `fastapi/routing.py:1072-1078`; controls request handling and OpenAPI generation (`fastapi/routing.py:1246-1248`; `fastapi/openapi/utils.py:421-439`). |
| `fastapi.routing.APIRoute.is_sse_stream` | `private/internal` | Derived from generator and response class at `fastapi/routing.py:1072-1078`; used to select stream handling/OpenAPI behavior (`fastapi/routing.py:520-528`; `fastapi/openapi/utils.py:436-441`). |
| `fastapi.routing.APIRoute.response_field` | `private/internal` | Constructed from the response model for serialization at `fastapi/routing.py:1102-1114`; passed into request handling at `fastapi/routing.py:1236-1238`. |
| `fastapi.routing.APIRoute.response_fields` | `private/internal` | Builds fields for additional response models at `fastapi/routing.py:1039-1054`; read by OpenAPI generation (`fastapi/openapi/utils.py:473-490`). |
| `fastapi.routing.APIRoute.stream_item_field` | `private/internal` | Constructed from inferred stream item type at `fastapi/routing.py:1115-1124`; consumed by stream serialization/OpenAPI (`fastapi/routing.py:1247-1248`; `fastapi/openapi/utils.py:421-441`). |
| `fastapi.routing.APIRoute.stream_item_type` | `private/internal` | Inferred from the endpoint return annotation at `fastapi/routing.py:1081-1098`; it is not an `APIRoute.__init__` argument and feeds internal stream-field construction. |

## `Dependant` fields (19)

Propose `private/internal` for all 19 fields. `Dependant` is a slotted dataclass in the implementation module `fastapi/dependencies/models.py:32-51`; it is not re-exported from the pinned FastAPI package root (`fastapi/__init__.py:1-25`), and no consumer-facing docs for `Dependant` or these attributes were found. `get_dependant` creates/populates the graph from endpoint signatures and `Depends` metadata (`fastapi/dependencies/utils.py:274-344`); `solve_dependencies` and OpenAPI code consume it (`fastapi/dependencies/utils.py:619-723`; `fastapi/openapi/utils.py:109-125`). Public dependency declaration behavior does not establish a supported API for inspecting or mutating this internal graph.

| Candidate ID | Proposal | Source declaration and implementation role |
|---|---|---|
| `fastapi.dependencies.models.Dependant.background_tasks_param_name` | `private/internal` | `models.py:45`; populated by parameter analysis and injected during solving (`utils.py:354-369,716-718`). |
| `fastapi.dependencies.models.Dependant.body_params` | `private/internal` | `models.py:37`; populated during signature analysis and converted by the body solver (`utils.py:342-344,698-707`). |
| `fastapi.dependencies.models.Dependant.call` | `private/internal` | `models.py:40`; the graph's callable is used for recursive analysis, invocation, cache identity, and scope inference (`utils.py:274-344,619-675`; `models.py:89-132,230-232`). |
| `fastapi.dependencies.models.Dependant.cookie_params` | `private/internal` | `models.py:36`; populated/classified and consumed by request solving (`utils.py:554-564,688-695`). |
| `fastapi.dependencies.models.Dependant.dependencies` | `private/internal` | `models.py:38`; populated recursively and traversed by dependency solving/security-scope analysis (`utils.py:321-331,619-660`; `models.py:108-118`). |
| `fastapi.dependencies.models.Dependant.header_params` | `private/internal` | `models.py:35`; populated/classified and consumed by request solving (`utils.py:554-564,685-695`). |
| `fastapi.dependencies.models.Dependant.http_connection_param_name` | `private/internal` | `models.py:43`; set for injected connection parameters and read during solving (`utils.py:354-363,709-710`). |
| `fastapi.dependencies.models.Dependant.name` | `private/internal` | `models.py:39`; carries dependency-edge names used when placing dependency results into the internal values mapping (`utils.py:274-293,657-658`). |
| `fastapi.dependencies.models.Dependant.own_oauth_scopes` | `private/internal` | `models.py:47`; used by internal scope/cache-key helpers (`models.py:69-110`). |
| `fastapi.dependencies.models.Dependant.parent_oauth_scopes` | `private/internal` | `models.py:48`; used by internal scope/cache-key helpers and override reconstruction (`models.py:69-79`; `utils.py:627-636`). |
| `fastapi.dependencies.models.Dependant.path` | `private/internal` | `models.py:50`; carries the route path into dependency analysis and override reconstruction (`utils.py:274-293,631-636`). |
| `fastapi.dependencies.models.Dependant.path_params` | `private/internal` | `models.py:33`; populated from signature fields and consumed by request solving/OpenAPI traversal (`utils.py:554-564,682-684`; `openapi/utils.py:109-125`). |
| `fastapi.dependencies.models.Dependant.query_params` | `private/internal` | `models.py:34`; populated from signature fields and consumed by request solving/OpenAPI traversal (`utils.py:554-564,685-687`; `openapi/utils.py:109-125`). |
| `fastapi.dependencies.models.Dependant.request_param_name` | `private/internal` | `models.py:41`; set for injected request parameters and read during solving (`utils.py:354-357,711-714`). |
| `fastapi.dependencies.models.Dependant.response_param_name` | `private/internal` | `models.py:44`; set for injected response parameters and read during solving (`utils.py:363-366,719-720`). |
| `fastapi.dependencies.models.Dependant.scope` | `private/internal` | `models.py:51`; used for dependency scope validation, caching, and generator teardown selection (`utils.py:280-294,619-675`; `models.py:230-232`). |
| `fastapi.dependencies.models.Dependant.security_scopes_param_name` | `private/internal` | `models.py:46`; set during parameter analysis and used to construct injected `SecurityScopes` (`utils.py:366-369,721-723`; `models.py:108-111`). |
| `fastapi.dependencies.models.Dependant.use_cache` | `private/internal` | `models.py:49`; initialized from dependency metadata and used by the internal dependency cache (`utils.py:274-293,654-675`). |
| `fastapi.dependencies.models.Dependant.websocket_param_name` | `private/internal` | `models.py:42`; set for injected WebSocket parameters and read during solving (`utils.py:357-360,711-714`). |

## Remaining decision points

The main ambiguity is the 22 `APIRoute` fields proposed as `uncertain`: they mirror documented path-operation settings, but source/docs evidence reviewed here establishes their configuration semantics rather than a stable instance-attribute contract. The one direct member-level documentation hit among these 32 fields is `route.response_class`, so only that field is proposed as supported. A later atlas review can resolve the uncertain fields with explicit policy evidence; this draft intentionally does not turn constructor presence, runtime use, or tests into a public-member claim.

The `Dependant` fields have extensive source implementation evidence but no consumer-facing class/field contract. `private/internal` is therefore the conservative proposal under the current atlas policy, while acknowledging that downstream applications may inspect implementation objects without that behavior being a pinned FastAPI contract.
