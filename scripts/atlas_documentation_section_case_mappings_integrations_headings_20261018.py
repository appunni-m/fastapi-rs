"""Reviewed no-signal documentation headings for database and custom integrations.

FastAPI 0.141.1 is the source oracle. Database persistence, browser execution,
and custom extension code are kept outside the mapped FastAPI observations.
"""

_SQL_PAGE = "tutorial/sql-databases.md"
_CUSTOM_DOCS_PAGE = "how-to/custom-docs-ui-assets.md"
_CUSTOM_REQUEST_PAGE = "how-to/custom-request-and-route.md"

_SQL_RECIPE = "tests/fixtures/input-recipes/parity/sql-databases-sections-20261015.yaml"
_NEW_SQL_RECIPE = (
    "tests/fixtures/input-recipes/parity/sql-databases-no-signal-headings-20261018.yaml"
)
_UI_RECIPE = "tests/fixtures/input-recipes/parity/docs-ui-clients-sections-20261015.yaml"

_CONSTRUCTION_SELECTORS = [
    "construction.exception_class",
    "construction.exception_message",
    "construction.outcome",
]
_HTTP_SELECTORS = ["http.body.bytes", "http.headers.ordered", "http.status"]
_VALIDATION_SELECTORS = ["validation.error_class", "validation.error_details"]
_DOCS_HTTP_SELECTORS = [
    "docs.response.body.bytes",
    "docs.response.headers",
    "docs.response.status",
    *_HTTP_SELECTORS,
]
_OPENAPI_PATH_SELECTORS = [*_DOCS_HTTP_SELECTORS, "openapi.document", "openapi.paths"]
_OPENAPI_REQUEST_SCHEMA_SELECTORS = [*_OPENAPI_PATH_SELECTORS, "openapi.request_schema"]

_QUERY_HERO_SELECTORS = sorted(
    set(_CONSTRUCTION_SELECTORS + _HTTP_SELECTORS + _VALIDATION_SELECTORS + _OPENAPI_PATH_SELECTORS)
)
_ROUTE_HTTP_VALIDATION_SELECTORS = sorted(
    set(_CONSTRUCTION_SELECTORS + _HTTP_SELECTORS + _VALIDATION_SELECTORS)
)
_MULTIPLE_MODEL_OPENAPI_SELECTORS = sorted(
    set(_CONSTRUCTION_SELECTORS + _OPENAPI_REQUEST_SCHEMA_SELECTORS)
)
_MULTIPLE_MODEL_OPENAPI_VALIDATION_SELECTORS = sorted(
    set(_MULTIPLE_MODEL_OPENAPI_SELECTORS + _VALIDATION_SELECTORS)
)


def _workflow(
    heading,
    start,
    end,
    recipe,
    cases,
    feature_ids,
    selectors,
    note,
    rationale,
    actions=None,
):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "feature_ids": feature_ids,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }
    if actions is not None:
        mapping["action_ids"] = actions
    return mapping


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


DOC_SECTION_CASE_MAPPINGS_INTEGRATIONS_HEADINGS_20261018 = {
    (_SQL_PAGE, "install-sqlmodel"): _excluded(
        "Install `SQLModel` { #install-sqlmodel }",
        35,
        47,
        (
            "The section gives a package installation command and describes no FastAPI app, "
            "request, response, or OpenAPI behavior. Installing SQLModel is project setup."
        ),
        (
            "The pinned section is `uv add sqlmodel` and its console rendering "
            "(docs/en/docs/tutorial/sql-databases.md:35-47). This changes an application's "
            "environment; FastAPI does not run or observe the package installation."
        ),
    ),
    (_SQL_PAGE, "create-the-tables"): _excluded(
        "Create the Tables { #create-the-tables }",
        86,
        91,
        (
            "The section calls SQLModel metadata to create database tables. Database DDL and "
            "engine access are SQLModel/SQLAlchemy behavior, not FastAPI request or ASGI behavior."
        ),
        (
            "The page names `SQLModel.metadata.create_all(engine)` "
            "(docs/en/docs/tutorial/sql-databases.md:86-91), and the pinned example implements "
            "it at `docs_src/sql_databases/tutorial001_an_py310.py:21-22`. Its later startup "
            "registration is a separate lifecycle section; this span itself is SQLModel DDL."
        ),
    ),
    (_SQL_PAGE, "read-heroes"): _workflow(
        "Read Heroes { #read-heroes }",
        130,
        135,
        _NEW_SQL_RECIPE,
        [
            "fastapi.docs.sql-databases.single-model.read-heroes",
            "fastapi.docs.sql-databases.single-model.read-heroes.openapi",
        ],
        ["app-routing", "request-validation", "response-serialization", "openapi-docs"],
        _QUERY_HERO_SELECTORS,
        (
            "The independent input uses the documented `GET /heroes/` signature with integer "
            "offset and bounded limit parameters, plus its list response annotation. It checks "
            "valid and over-limit queries and observes the operation parameters and response "
            "schema. Its fixed in-memory records do not claim SQL selection, pagination, or "
            "database behavior."
        ),
        (
            "The heading says the route reads a list and pages it with `limit` and `offset` "
            "(docs/en/docs/tutorial/sql-databases.md:130-135); its exact example signature and "
            "list return type are `docs_src/sql_databases/tutorial001_an_py310.py:48-55`. "
            "FastAPI builds route parameters and validates query values through "
            "`fastapi/dependencies/utils.py:554-556,681-690,780-866`, then serializes the "
            "annotated response in `fastapi/routing.py:301-342,706-750`. Its OpenAPI path "
            "construction is in `fastapi/openapi/utils.py:620-673`. The new recipe observes "
            "those request, response, and schema surfaces while replacing SQLModel's query with "
            "a fixed Pydantic-shaped in-memory list."
        ),
    ),
    (_SQL_PAGE, "read-one-hero"): _workflow(
        "Read One Hero { #read-one-hero }",
        136,
        141,
        _NEW_SQL_RECIPE,
        ["fastapi.docs.sql-databases.single-model.read-one-hero"],
        [
            "app-routing",
            "request-validation",
            "response-serialization",
            "public-api-errors",
        ],
        _ROUTE_HTTP_VALIDATION_SELECTORS,
        (
            "The selected requests cover integer path binding, the documented typed `Hero` "
            "response, a non-integer validation failure, and the example's missing-record "
            "HTTPException response. The record lookup is an in-memory stand-in; no SQL query "
            "or persistence behavior is claimed."
        ),
        (
            "The heading introduces the single-hero GET "
            "(docs/en/docs/tutorial/sql-databases.md:136-141); the pinned route declares "
            "`hero_id: int`, returns `Hero`, and raises HTTPException for a missing row "
            "(`docs_src/sql_databases/tutorial001_an_py310.py:58-63`). FastAPI validates "
            "request parameters in `fastapi/dependencies/utils.py:681-690,780-866` and "
            "validates/serializes typed responses in `fastapi/routing.py:301-342,706-750`; "
            "its registered HTTPException handler returns the documented status/detail shape "
            "(`fastapi/applications.py:1003; fastapi/exception_handlers.py:11-17`). "
            "The independent workload replaces only the SQLModel lookup with fixed memory."
        ),
    ),
    (_SQL_PAGE, "delete-a-hero"): _workflow(
        "Delete a Hero { #delete-a-hero }",
        142,
        147,
        _NEW_SQL_RECIPE,
        ["fastapi.docs.sql-databases.single-model.delete-hero"],
        [
            "app-routing",
            "request-validation",
            "response-serialization",
            "public-api-errors",
        ],
        _ROUTE_HTTP_VALIDATION_SELECTORS,
        (
            "The independent input observes the typed integer path parameter, FastAPI's "
            "rejection of a non-integer path, and the route's JSON response or missing-record "
            "HTTPException response. It does not claim database deletion or transaction behavior."
        ),
        (
            "The heading describes deletion through a path operation "
            "(docs/en/docs/tutorial/sql-databases.md:142-147); its exact example registers "
            "`DELETE /heroes/{hero_id}`, accepts `hero_id: int`, and returns a dict "
            "(`docs_src/sql_databases/tutorial001_an_py310.py:66-73`). FastAPI's parameter "
            "validation is implemented by `fastapi/dependencies/utils.py:681-690,780-866`; "
            "without an explicit response field, `fastapi/routing.py:301-342` uses its JSON "
            "encoder for the returned value. FastAPI registers its HTTPException handler at "
            "`fastapi/applications.py:1003`, which emits a JSON `detail` response "
            "(`fastapi/exception_handlers.py:11-17`). The new in-memory workload samples"
            " these ASGI "
            "surfaces and omits SQLModel deletion/commit behavior."
        ),
    ),
    (_SQL_PAGE, "herobase-the-base-class"): _excluded(
        "`HeroBase` - the base class { #herobase-the-base-class }",
        188,
        196,
        (
            "This section defines shared SQLModel/Pydantic fields and inheritance. The base "
            "class is not itself declared as a FastAPI request or response type; the later "
            "derived API models receive their own mappings."
        ),
        (
            "The exact span lists fields shared by the models and includes the `HeroBase` "
            "declaration (`docs/en/docs/tutorial/sql-databases.md:188-196; "
            "docs_src/sql_databases/tutorial002_an_py310.py:7-10`). SQLModel/Pydantic own the "
            "model inheritance and field definition. The later `HeroCreate`, `HeroPublic`, and "
            "`HeroUpdate` uses at FastAPI route boundaries are reviewed separately; no FastAPI "
            "route directly consumes `HeroBase` here."
        ),
    ),
    (_SQL_PAGE, "hero-the-table-model"): _excluded(
        "`Hero` - the *table model* { #hero-the-table-model }",
        197,
        212,
        (
            "This section describes SQLModel's table marker, table fields, primary key, and "
            "stored secret. Those database model and schema responsibilities are outside the "
            "FastAPI request/response contract; the actual public models are mapped separately."
        ),
        (
            "The exact section and source declaration describe `Hero` as a table model with "
            "database-only fields (`docs/en/docs/tutorial/sql-databases.md:197-212; "
            "docs_src/sql_databases/tutorial002_an_py310.py:12-15`). `table=True`, primary-key "
            "generation, and the SQL table shape belong to SQLModel/SQLAlchemy. The pinned "
            "routes instead accept `HeroCreate` and expose `HeroPublic`, so this heading does "
            "not define a FastAPI route model."
        ),
    ),
    (_SQL_PAGE, "heropublic-the-public-data-model"): _workflow(
        "`HeroPublic` - the public *data model* { #heropublic-the-public-data-model }",
        213,
        238,
        _SQL_RECIPE,
        [
            "fastapi.docs.sql-databases.multiple-models.openapi",
            "fastapi.docs.sql-databases.multiple-models.create-public",
            "fastapi.docs.sql-databases.multiple-models.read-public-list",
        ],
        ["response-serialization", "openapi-docs"],
        _MULTIPLE_MODEL_OPENAPI_SELECTORS,
        (
            "The selected OpenAPI action observes `HeroPublic` as the declared POST, GET, and "
            "PATCH response shape; the create and list actions expose a backing record that "
            "includes `secret_name`, so response filtering is visible in their HTTP bodies. "
            "This covers the FastAPI response contract for the public model, not SQLModel "
            "inheritance or database storage."
        ),
        (
            "The pinned span calls `HeroPublic` the model returned to clients, makes `id` "
            "non-optional, and lists its public fields "
            "(docs/en/docs/tutorial/sql-databases.md:213-238; the declaration is "
            "`docs_src/sql_databases/tutorial002_an_py310.py:17-19`). FastAPI accepts it as "
            "`response_model` on the create/list/read/PATCH routes at lines 56, 65, 75, and "
            "83 of that example. FastAPI creates a serialization response field in "
            "`fastapi/routing.py:1081-1113`, validates and serializes it in "
            "`fastapi/routing.py:301-342,706-750`, and collects the models for OpenAPI in "
            "`fastapi/openapi/utils.py:620-673`. The existing independent cases select the "
            "schemas and HTTP response projections; they do not claim SQLModel inheritance."
        ),
    ),
    (_SQL_PAGE, "herocreate-the-data-model-to-create-a-hero"): _workflow(
        "`HeroCreate` - the *data model* to create a hero "
        "{ #herocreate-the-data-model-to-create-a-hero }",
        239,
        262,
        _SQL_RECIPE,
        [
            "fastapi.docs.sql-databases.multiple-models.openapi",
            "fastapi.docs.sql-databases.multiple-models.create-public",
            "fastapi.docs.sql-databases.multiple-models.invalid-create",
        ],
        ["request-validation", "response-serialization", "openapi-docs"],
        _MULTIPLE_MODEL_OPENAPI_VALIDATION_SELECTORS,
        (
            "The successful create case exercises a `HeroCreate` request body and public "
            "response projection; the invalid case omits the required secret field and selects "
            "FastAPI validation details. OpenAPI observes the request schema. Database writes "
            "and secret hashing/storage are not claimed."
        ),
        (
            "The pinned section says `HeroCreate` is the client input model and describes its "
            "required fields (`docs/en/docs/tutorial/sql-databases.md:239-262`; the model and "
            "route are `docs_src/sql_databases/tutorial002_an_py310.py:21-22,56-62`). FastAPI "
            "builds the request body and validates it through "
            "`fastapi/dependencies/utils.py:681-690` and emits `RequestValidationError` from "
            "`fastapi/routing.py:751-755`; the same route declares `response_model=HeroPublic`, "
            "whose projection is validated/serialized at `fastapi/routing.py:301-342,706-750`. "
            "The existing independent create, invalid-create, and OpenAPI cases observe those "
            "surfaces using Pydantic-shaped input; database persistence and password handling "
            "remain out of scope."
        ),
    ),
    (_SQL_PAGE, "heroupdate-the-data-model-to-update-a-hero"): _workflow(
        "`HeroUpdate` - the *data model* to update a hero "
        "{ #heroupdate-the-data-model-to-update-a-hero }",
        263,
        280,
        _SQL_RECIPE,
        [
            "fastapi.docs.sql-databases.multiple-models.openapi",
            "fastapi.docs.sql-databases.multiple-models.update-sparse",
        ],
        ["request-validation", "response-serialization", "openapi-docs"],
        _MULTIPLE_MODEL_OPENAPI_SELECTORS,
        (
            "The OpenAPI case observes the PATCH body schema; the sparse PATCH case sends one "
            "field to the typed `HeroUpdate` body and observes the public response projection. "
            "The workload does not claim SQLModel's field-update or database mutation behavior."
        ),
        (
            "The pinned section defines optional update fields and describes sending only the "
            "fields to change (`docs/en/docs/tutorial/sql-databases.md:263-280`; source "
            "declaration: `docs_src/sql_databases/tutorial002_an_py310.py:25-28`). The PATCH "
            "route receives `hero: HeroUpdate` and declares `response_model=HeroPublic` at "
            "lines 83-93. FastAPI's request parameter validation and response serialization "
            "are in `fastapi/dependencies/utils.py:681-690` and "
            "`fastapi/routing.py:301-342,706-750`; the OpenAPI builder records route request "
            "and response schemas in `fastapi/openapi/utils.py:620-673`. The selected inputs "
            "exercise the schema and one-field PATCH response, not `sqlmodel_update` or storage."
        ),
    ),
    (_SQL_PAGE, "read-one-hero-with-heropublic"): _workflow(
        "Read One Hero with `HeroPublic` { #read-one-hero-with-heropublic }",
        309,
        314,
        _NEW_SQL_RECIPE,
        ["fastapi.docs.sql-databases.multiple-models.read-one-public"],
        [
            "app-routing",
            "request-validation",
            "response-serialization",
            "public-api-errors",
        ],
        _ROUTE_HTTP_VALIDATION_SELECTORS,
        (
            "The independent GET supplies a secret-bearing in-memory record to the documented "
            "`response_model=HeroPublic` route and observes FastAPI's public response shape, "
            "plus typed path validation and the example's missing-record response. The case "
            "does not claim SQLModel lookup or persistence."
        ),
        (
            "The pinned section introduces a single-hero response using `HeroPublic` "
            "(docs/en/docs/tutorial/sql-databases.md:309-314); the exact route is "
            "`GET /heroes/{hero_id}`, `hero_id: int`, `response_model=HeroPublic` "
            "(`docs_src/sql_databases/tutorial002_an_py310.py:75-80`). FastAPI validates the "
            "path value in `fastapi/dependencies/utils.py:681-690,780-866` and validates and "
            "serializes the response model in `fastapi/routing.py:301-342,706-750`; FastAPI's "
            "registered HTTPException handler returns the missing-record detail "
            "(`fastapi/applications.py:1003; fastapi/exception_handlers.py:11-17`). The "
            "independent workload replaces only the database lookup with fixed memory."
        ),
    ),
    (_SQL_PAGE, "update-a-hero-with-heroupdate"): _workflow(
        "Update a Hero with `HeroUpdate` { #update-a-hero-with-heroupdate }",
        315,
        324,
        _SQL_RECIPE,
        [
            "fastapi.docs.sql-databases.multiple-models.openapi",
            "fastapi.docs.sql-databases.multiple-models.update-sparse",
        ],
        ["request-validation", "response-serialization", "openapi-docs"],
        _MULTIPLE_MODEL_OPENAPI_SELECTORS,
        (
            "The selected PATCH request supplies only `name`, matching the documented sparse "
            "body, and observes the serialized public response. OpenAPI checks the typed body "
            "and output schemas. The case does not observe SQLModel's `sqlmodel_update`, commit, "
            "or refresh operations."
        ),
        (
            "The heading says the operation uses PATCH and `exclude_unset=True` to keep only "
            "client-supplied values (docs/en/docs/tutorial/sql-databases.md:315-324). The "
            "pinned route confirms `HeroUpdate` input, `HeroPublic` response, and "
            "`model_dump(exclude_unset=True)` at"
            " `docs_src/sql_databases/tutorial002_an_py310.py:83-93`. "
            "FastAPI validates the request model and response model at "
            "`fastapi/dependencies/utils.py:681-690` and `fastapi/routing.py:301-342,706-750`; "
            "the OpenAPI builder emits both schemas at `fastapi/openapi/utils.py:620-673`. "
            "The independent sparse-PATCH input covers the HTTP boundary while the SQLModel "
            "update and transaction code remain excluded."
        ),
    ),
    (_SQL_PAGE, "delete-a-hero-again"): _workflow(
        "Delete a Hero Again { #delete-a-hero-again }",
        325,
        332,
        _NEW_SQL_RECIPE,
        ["fastapi.docs.sql-databases.multiple-models.delete-hero-again"],
        [
            "app-routing",
            "request-validation",
            "response-serialization",
            "public-api-errors",
        ],
        _ROUTE_HTTP_VALIDATION_SELECTORS,
        (
            "The independent input observes the documented typed integer path, JSON response, "
            "non-integer validation failure, and missing-record HTTPException response. It "
            "does not claim SQLModel deletion, commit, or refresh behavior."
        ),
        (
            "The pinned section describes the second DELETE route "
            "(docs/en/docs/tutorial/sql-databases.md:325-332), whose source declares "
            "`DELETE /heroes/{hero_id}`, accepts `hero_id: int`, and returns a dict "
            "(`docs_src/sql_databases/tutorial002_an_py310.py:96-103`). FastAPI validates path "
            "values in `fastapi/dependencies/utils.py:681-690,780-866` and JSON-encodes the "
            "route's unmodeled dict response in `fastapi/routing.py:301-342`. FastAPI registers "
            "its HTTPException handler at `fastapi/applications.py:1003`, emitting JSON detail "
            "(`fastapi/exception_handlers.py:11-17`). The case samples "
            "these ASGI surfaces with an in-memory record and excludes database mutation."
        ),
    ),
    (_CUSTOM_DOCS_PAGE, "disable-the-automatic-docs"): _workflow(
        "Disable the automatic docs { #disable-the-automatic-docs }",
        15,
        22,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.automatic-docs-disabled"],
        ["app-routing", "openapi-docs"],
        ["http.status"],
        (
            "The two selected status observations show that FastAPI does not register its "
            "default Swagger and ReDoc endpoints when both documented URL settings are None. "
            "They do not observe the replacement CDN-backed routes or browser asset loading."
        ),
        (
            "The pinned section instructs users to set the FastAPI docs URLs to `None` "
            "(docs/en/docs/how-to/custom-docs-ui-assets.md:15-22), and its example constructs "
            "`FastAPI(docs_url=None, redoc_url=None)` at "
            "`docs_src/custom_docs_ui/tutorial001_py310.py:8`. The reused independent "
            "`swagger-disabled` and `redoc-disabled` actions exercise the identical constructor "
            "settings in the self-hosted sibling example. FastAPI stores these values in "
            "`fastapi/applications.py:881-890` and conditionally registers the docs routes in "
            "`fastapi/applications.py:1121-1158`; only route absence/status is claimed."
        ),
        actions=["swagger-disabled", "redoc-disabled"],
    ),
    (_CUSTOM_DOCS_PAGE, "test-it"): _excluded(
        "Test it { #test-it }",
        55,
        58,
        (
            "This step asks the reader to reload the docs in a browser and confirm external "
            "CDN assets load. Browser network access and JavaScript/CSS execution are outside "
            "the FastAPI ASGI contract."
        ),
        (
            "The exact section describes the CDN-backed page loading in the browser "
            "(docs/en/docs/how-to/custom-docs-ui-assets.md:55-58). FastAPI's generated HTML "
            "and configured asset URL strings are mapped by the parent custom-CDN section; "
            "this heading's result depends on browser behavior and external CDN availability."
        ),
    ),
    (_CUSTOM_REQUEST_PAGE, "use-cases"): _excluded(
        "Use cases { #use-cases }",
        17,
        24,
        (
            "The section lists application-specific ideas for code a user might implement; it "
            "does not specify an independent FastAPI runtime operation. The concrete custom "
            "Request/APIRoute extension hooks are mapped under their child headings."
        ),
        (
            "The pinned list names message-pack conversion, gzip decompression, and request-body "
            "logging (`docs/en/docs/how-to/custom-request-and-route.md:17-24`). Conversion, "
            "decompression, and logging are behavior of user-authored handlers and/or external "
            "libraries, not this introductory list. FastAPI's concrete APIRoute handler hook "
            "is reviewed in the existing child-section mappings, including the custom GzipRoute "
            "span at lines 47-80 and router-specific APIRoute span at lines 101-109."
        ),
    ),
}
