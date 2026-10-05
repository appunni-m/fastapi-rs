# Independent inactive metadata admission review

2026-10-05. Static review only. No application/factory/native module was imported,
no active file was changed, and no build, installer, generator, parity run or unit
test was executed. The only written file is this temporary review.

## Result and frozen identities

No correction is required to the reviewed metadata proposal. It adds exactly 19
fixture references to seven existing operations. Removing those 19 new list
entries makes the complete parsed proposal equal to active `metadata.yaml`,
including the old fixture-reference order. There are no other structured changes.

| Artifact | SHA256 |
| --- | --- |
| Active metadata.yaml | 09038fbb5d1778405e94fa482197abe111835e7185ebb5cf98f285a43048781d |
| metadata-proposal.yaml | 24e916145a0174644a48295b6065d28569325267e1db3fc44495e4fbe1989ef1 |
| Corrected candidate recipe | e1243762e877e182bffadeb4eed6668d852bfb4d1bc31f8c98a7cceb9f8ce132 |
| Candidate workload | d1c2824c616533127910a459075af4b020e6e97a8d9f260dd838d3b0ef7733bf |
| Candidate review plan | 98582838fbde27dbf649a9cae9b49caac7d97c8b22bacb05aee9bab26a8ced3b |
| Prior independent source/input review | 4fce530a1e92cc51792fafe3ddf129fc5d73b291077eeea39906902fe84d6bb7 |

The corrected recipe uses workflow schema 9 and contains three ordinary parity
cases / 19 HTTP actions. The canonical `read_recipe` schema check passed again.
Both metadata files also parsed successfully with the repository's duplicate-key
loader. These checks do not run full metadata/index admission: the inactive
recipe's future active paths are not materialized by this review.

## Exact reference delta and public ownership

Every added reference has exactly `recipe_path`, `case_id`, `workload_path` and
`observation_selectors`. Its intended recipe/workload paths are respectively
`tests/fixtures/input-recipes/parity/next-openapi-response-fields.yaml` and
`tests/fixtures/workloads/next_openapi_response_fields.py`.

The three corrected IDs are:

- `fastapi.next-openapi-response-fields.annotated-metadata-outer-titles-retained-hooks`
- `fastapi.next-openapi-response-fields.shared-primitive-definition`
- `fastapi.next-openapi-response-fields.late-json-hook-error-public-retry-cache`

| Existing operation | New refs | Public activity represented |
| --- | ---: | --- |
| fastapi.applications.FastAPI.__init__ | 3 | Each factory constructs its own app. |
| fastapi.applications.FastAPI.__call__ | 3 | The user ASGI observer delegates all selected requests to that app. |
| fastapi.applications.FastAPI.get | 3 | Public registration of the probe and schema-excluded helper routes. |
| fastapi.applications.FastAPI.openapi | 3 | All cases request the FastAPI-owned docs route, which calls the method; the retry case also calls the public method through `/document`. |
| fastapi.applications.FastAPI.exception_handler | 3 | Each case registers the ordinary user error handler. Actual handler invocation is positively selected only by the retry case. |
| fastapi.responses.JSONResponse | 3 | State/document/error response construction and ordinary ASGI execution. Existing sibling ownership is unchanged. |
| fastapi.Request | 1 | Only the retry case receives the actual Request in the invoked handler and reads `request.url.path`. |

The six three-case links declare exact HTTP status, ordered headers, full body
bytes, ASGI message types, application error, full OpenAPI document, and
construction outcome/class/message. The one Request link declares only
`http.status` and `http.body.bytes`. All declared selectors are present in their
case's canonical selected-selector set.

Request annotations on the other two registered handlers do not establish
Request injection or URL access. The Pydantic `Field` and metadata-hook protocols
are user dependency inputs. No Pydantic object is promoted to a FastAPI export.
There is no new mapping for APIRouter/include_router, private ModelField,
DefaultPlaceholder or direct public invocation of the `get_openapi` utility.

## Unchanged manifest and policy

The complete equality check after removing the added references verifies that
source identities, runtime policy, target statuses, Rust/Python bindings,
requirements, aliases, public classifications, supported-slice text, exclusions,
gaps, source evidence and operation-level aggregate selectors remain unchanged.
The operation key set is identical. Each existing fixture-reference suffix is
identical, so prior input mappings are not removed or reordered.

These are input links, not new support evidence. No live oracle/target outcome or
target compatibility follows from this review. The inner Annotated metadata
case selects generated outer response-field titles; it does not establish the
nondefault/empty OUTER FieldInfo alias/title branches. The candidate plan and
existing independent review retain that distinction.

## OpenAPI source-definition range

The pinned FastAPI source at commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f` has applications.py SHA256
`38dccb19b2a0b0b984c8d7541263842954a37c087cf96b4463aea17873c6183c`.
An AST read confirms `FastAPI.openapi` starts at line 1070 and ends at line 1103,
the `return self.openapi_schema` statement. The unchanged operation definition
evidence already covers that complete method.

Line 1110 is the `self.openapi()` call inside `setup`'s async docs callback; it is
not part of the method definition. Extending the current end to 1110 would mix
the next method into the definition evidence. No range correction is needed.
The candidate recipe/plan separately provides source evidence for the shared
generation/title/cache behavior and explains the indirect docs invocation.

## Existing generator provenance limit

`scripts/parity/api_contract.py:978` onward validates reviewed operation fixture
links through the materialized case. At lines 1059–1080 it derives and returns
the entire case's `_selected_selectors` set rather than projecting the link's
declared `observation_selectors`. The call at lines 2445–2467 retains that behavior.

For each candidate case, that generated set contains the nine declared wide
selectors plus `docs.response.status`, `docs.response.headers` and
`docs.response.body.bytes`. The Request link will therefore also inherit the
whole retry case's selector provenance in generated output despite its reviewed
status/body declaration. That does not make OpenAPI construction, hook journals,
warnings or other case activity independently attributable to Request. The
operation-specific scope above must remain the basis for claims; this review
does not change the generator or widen the declared mapping.

Warnings and raw send journals are selected inside exact HTTP response bodies;
no new independent Python-warning selector is claimed. Whole OpenAPI documents
are also parsed JSON observations, whose mapping comparison ignores object-key
order. Their independently selected HTTP body bytes and lossless send journal
retain wire order. Neither observation is normalized by this proposal.

## Admission gates remaining

No static metadata-proposal blocker remains. After the source/input/build freeze
permits activation, the existing materialization/index/atlas/metadata contracts
must run against the admitted paths, followed by pinned source-first and unchanged
target execution on one fixed input digest with preserved mismatches and exact
identity receipts. This review has performed none of those live stages and
contains no expected outputs. Proposal SHA256 remains `24e91614…`; there is no
corrected metadata hash because no metadata correction is required.
