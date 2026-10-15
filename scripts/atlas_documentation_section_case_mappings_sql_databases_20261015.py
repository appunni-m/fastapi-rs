"""Reviewed mappings for FastAPI's SQL database tutorial sections.

FastAPI 0.141.1 is the application contract. Starlette 1.6.0 owns generic
ASGI routing and lifecycle behavior. The linked inputs replace SQLModel
storage with Pydantic-shaped request models and isolated in-memory values.
"""

_PAGE = "tutorial/sql-databases.md"
_RECIPE = "tests/fixtures/input-recipes/parity/sql-databases-sections-20261015.yaml"
_FAKE_DEPENDENCY_RECIPE = (
    "tests/fixtures/input-recipes/parity/docs-sql-databases-fake-dependency.yaml"
)


def _workflow(heading, start, end, recipe, cases, selectors, note, rationale, actions=None):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
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


_HTTP_SELECTORS = ["http.body.bytes", "http.headers.ordered", "http.status"]
_OPENAPI_SELECTORS = [
    "docs.response.body.bytes",
    "docs.response.headers",
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.request_schema",
]
_CONSTRUCTION_SELECTORS = [
    "construction.exception_class",
    "construction.exception_message",
    "construction.outcome",
]
_HTTP_WITH_CONSTRUCTION_SELECTORS = sorted(set(_CONSTRUCTION_SELECTORS).union(_HTTP_SELECTORS))
_OPENAPI_WITH_CONSTRUCTION_SELECTORS = sorted(
    set(_CONSTRUCTION_SELECTORS).union(_OPENAPI_SELECTORS)
)
_INVALID_MODEL_SELECTORS = [
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "validation.error_class",
    "validation.error_details",
]
_SINGLE_MODEL_SELECTORS = sorted(
    set(_CONSTRUCTION_SELECTORS).union(
        _OPENAPI_SELECTORS, _HTTP_SELECTORS, _INVALID_MODEL_SELECTORS
    )
)
_MULTIPLE_MODEL_SELECTORS = sorted(
    set(_CONSTRUCTION_SELECTORS).union(
        _OPENAPI_SELECTORS, _HTTP_SELECTORS, _INVALID_MODEL_SELECTORS
    )
)


DOC_SECTION_CASE_MAPPINGS_SQL_DATABASES_20261015 = {
    (_PAGE, "sql-relational-databases"): _excluded(
        "SQL (Relational) Databases { #sql-relational-databases }",
        1,
        357,
        (
            "This top-level page combines SQLModel installation and database configuration "
            "with FastAPI request models, yielded dependencies, OpenAPI, and a CLI launch. "
            "The narrower child sections below either map a FastAPI-visible ASGI input or "
            "exclude third-party/process behavior."
        ),
        (
            "FastAPI 0.141.1 says an application may use any database library and presents "
            "SQLModel only as its example (docs/en/docs/tutorial/sql-databases.md:1-28). "
            "A page-wide workflow would mix FastAPI request/schema behavior with SQLModel, "
            "SQLAlchemy, SQLite, CLI, and Starlette lifecycle behavior."
        ),
    ),
    (_PAGE, "create-the-app-with-a-single-model"): _workflow(
        "Create the App with a Single Model { #create-the-app-with-a-single-model }",
        48,
        167,
        _RECIPE,
        [
            "fastapi.docs.sql-databases.single-model.create-hero",
            "fastapi.docs.sql-databases.single-model.invalid-hero",
            "fastapi.docs.sql-databases.single-model.openapi",
        ],
        _SINGLE_MODEL_SELECTORS,
        (
            "The cases independently send one valid model request, one invalid model request, "
            "and one OpenAPI request. The Pydantic shape mirrors the documented Hero fields; "
            "these selected actions do not claim SQLModel table creation, database writes, "
            "or CLI process startup. The startup subsection excludes SQLModel table creation "
            "and points to lifecycle coverage that lacks this page's source evidence."
        ),
        (
            "The pinned single-model example annotates the POST body and response with `Hero` "
            "(docs_src/sql_databases/tutorial001_an_py310.py:40-45), while the page states that "
            "FastAPI reads the model from JSON and uses its shape in API docs "
            "(docs/en/docs/tutorial/sql-databases.md:118-129, 148-167). The recipe selects "
            "construction outcome/class/message for each case, `http.status`, "
            "`http.headers.ordered`, and `http.body.bytes` for each HTTP action, "
            "`validation.error_class` and `validation.error_details` for the invalid body, and "
            "the exact OpenAPI document/path/request-schema projections for the schema action. "
            "Generic HTTP routing remains Starlette 1.6.0 behavior."
        ),
    ),
    (_PAGE, "create-models"): _workflow(
        "Create Models { #create-models }",
        54,
        73,
        _RECIPE,
        ["fastapi.docs.sql-databases.single-model.openapi"],
        _OPENAPI_WITH_CONSTRUCTION_SELECTORS,
        (
            "The single-model OpenAPI action observes the public schema and POST body/response "
            "references generated from the Pydantic-shaped Hero model. It does not observe "
            "SQLModel's `table=True`, primary-key, index, or SQL-column behavior."
        ),
        (
            "The page describes `Hero` as Pydantic-shaped but also documents SQLModel-only "
            "table, primary-key, and index metadata "
            "(docs/en/docs/tutorial/sql-databases.md:54-73). "
            "The source example defines those fields in "
            "`docs_src/sql_databases/tutorial001_an_py310.py:1-11`; "
            "this input selects the FastAPI OpenAPI boundary using the equivalent Pydantic fields. "
            "Selectors are construction outcome/class/message plus the OpenAPI response "
            "metadata/body, document, path, and request schema."
        ),
    ),
    (_PAGE, "create-an-engine"): _excluded(
        "Create an Engine { #create-an-engine }",
        74,
        85,
        (
            "The section configures a SQLModel/SQLAlchemy engine and SQLite connection arguments. "
            "It does not specify a FastAPI operation that can be exercised without the database "
            "libraries."
        ),
        (
            "The pinned example creates an engine with `create_engine` and SQLite `connect_args` "
            "(`docs_src/sql_databases/tutorial001_an_py310.py:14-18`). Those are SQLAlchemy and "
            "SQLite responsibilities, not FastAPI or Starlette ASGI behavior."
        ),
    ),
    (_PAGE, "create-a-session-dependency"): _workflow(
        "Create a Session Dependency { #create-a-session-dependency }",
        92,
        101,
        _FAKE_DEPENDENCY_RECIPE,
        ["fastapi.docs.sql-databases.fake-yield.create-and-cleanup"],
        _HTTP_SELECTORS,
        (
            "The selected create request uses a yielded fake session dependency, then a second "
            "request reads its cleanup counter. The response bodies expose the request and "
            "post-request state without loading SQLModel, SQLAlchemy, or SQLite."
        ),
        (
            "The pinned example yields one `Session` per request through an `Annotated` "
            "`Depends` alias (`docs_src/sql_databases/tutorial001_an_py310.py:25-30`). The "
            "existing fake dependency workload replaces that session with an in-memory value "
            "and increments a cleanup counter in "
            "`tests/fixtures/workloads/docs_sql_databases_fake_dependency.py:27-51`); "
            "its create and cleanup-state actions are grounded by the pinned tutorial test "
            "(`tests/test_tutorial/test_sql_databases/test_tutorial002.py`). The exact selected "
            "selectors are HTTP status, ordered headers, and response bytes; FastAPI owns "
            "dependency resolution, while Starlette 1.6.0 owns HTTP dispatch."
        ),
        actions=[
            "create-hero-with-public-response-model",
            "observe-yield-dependency-cleanup",
        ],
    ),
    (_PAGE, "create-database-tables-on-startup"): _excluded(
        "Create Database Tables on Startup { #create-database-tables-on-startup }",
        102,
        117,
        (
            "This subsection's startup side effect is SQLModel table creation through SQLAlchemy. "
            "The existing FastAPI lifecycle case covers callback and ASGI lifecycle behavior, "
            "but its source evidence does not identify this SQL tutorial page; it cannot support "
            "a section-to-case link here. SQLModel DDL and database access are excluded."
        ),
        (
            "The pinned page describes `SQLModel.metadata.create_all(engine)` at lines 86-90 and "
            "says the tables are created on startup at lines 102-110; the pinned example "
            'registers `@app.on_event("startup")` around `create_db_and_tables()` '
            "(`docs_src/sql_databases/tutorial001_an_py310.py:21-22, 32-37`). FastAPI 0.141.1 "
            "marks `APIRouter.on_event` deprecated and retains its registration decorator at "
            "`fastapi/routing.py:6415-6445`; callback dispatch remains in `_startup` and "
            "`_shutdown` at lines 6363-6393. The independent "
            "`fastapi.lifecycle.router-events-legacy` case in "
            "`tests/fixtures/input-recipes/parity/router-events-lifespan-upstream.yaml` covers "
            "callback order, startup/shutdown, lifecycle errors and workload trace, plus the "
            "deprecation warning. Its source evidence points to the events documentation, not "
            "`docs/en/docs/tutorial/sql-databases.md`, so it is existing lifecycle coverage rather "
            "than evidence for this SQL section. SQLModel table creation remains excluded."
        ),
    ),
    (_PAGE, "create-a-hero"): _workflow(
        "Create a Hero { #create-a-hero }",
        118,
        129,
        _RECIPE,
        ["fastapi.docs.sql-databases.single-model.create-hero"],
        _HTTP_WITH_CONSTRUCTION_SELECTORS,
        (
            "The valid POST action exercises FastAPI's JSON body model parsing and typed response "
            "serialization for the documented Hero shape. Its handler returns the parsed value; "
            "database insertion, commit, refresh, and persistence are not selected."
        ),
        (
            "The documented route receives `Hero` from JSON and returns `Hero` "
            "(`docs_src/sql_databases/tutorial001_an_py310.py:40-45`); the following SQLModel "
            "session operations are in lines 47-53 and remain outside this scope. The recipe "
            "selects `http.status`, `http.headers.ordered`, and `http.body.bytes` for one "
            "independent POST."
        ),
    ),
    (_PAGE, "run-the-app"): _workflow(
        "Run the App { #run-the-app }",
        148,
        167,
        _RECIPE,
        ["fastapi.docs.sql-databases.single-model.openapi"],
        _OPENAPI_WITH_CONSTRUCTION_SELECTORS,
        (
            "The OpenAPI action samples the model schema consumed by the documented `/docs` UI. "
            "It does not launch `fastapi dev`, measure Uvicorn logs, or compare rendered Swagger "
            "HTML."
        ),
        (
            "The section instructs users to run `fastapi dev` and inspect `/docs` "
            "(docs/en/docs/tutorial/sql-databases.md:148-167). The linked input requests "
            "`/openapi.json` and selects `docs.response.status`, `docs.response.headers`, "
            "`docs.response.body.bytes`, `openapi.document`, `openapi.paths`, and "
            "`openapi.request_schema`, plus construction outcome/class/message. This maps the "
            "FastAPI schema presented by the UI while leaving CLI process startup to the separate "
            "CLI contract."
        ),
    ),
    (_PAGE, "update-the-app-with-multiple-models"): _workflow(
        "Update the App with Multiple Models { #update-the-app-with-multiple-models }",
        168,
        352,
        _RECIPE,
        [
            "fastapi.docs.sql-databases.multiple-models.openapi",
            "fastapi.docs.sql-databases.multiple-models.create-public",
            "fastapi.docs.sql-databases.multiple-models.invalid-create",
            "fastapi.docs.sql-databases.multiple-models.read-public-list",
            "fastapi.docs.sql-databases.multiple-models.update-sparse",
        ],
        _MULTIPLE_MODEL_SELECTORS,
        (
            "The cases independently sample model schemas, a valid and invalid create body, a "
            "public list response, and a sparse PATCH body. The inputs do not claim database "
            "IDs, storage, SQLModel update behavior, single-record lookup, deletion, or CLI "
            "startup."
        ),
        (
            "The pinned multiple-model example declares `HeroCreate`, `HeroPublic`, and "
            "`HeroUpdate` models and uses request/response models on CRUD routes "
            "(`docs_src/sql_databases/tutorial002_an_py310.py:7-28, 56-103`). The Pydantic-only "
            "workload preserves those FastAPI-visible shapes while using a fresh app per case. "
            "Each linked case also projects construction outcome/class/message. Selected action "
            "outputs are HTTP status/headers/bytes, request validation class/details, the OpenAPI "
            "response metadata/body, document, paths, and request schema."
        ),
    ),
    (_PAGE, "create-multiple-models"): _workflow(
        "Create Multiple Models { #create-multiple-models }",
        180,
        280,
        _RECIPE,
        ["fastapi.docs.sql-databases.multiple-models.openapi"],
        _OPENAPI_WITH_CONSTRUCTION_SELECTORS,
        (
            "The multi-model OpenAPI action selects HeroCreate, HeroPublic, and HeroUpdate "
            "schemas and the request/response references that expose them. The inherited "
            "HeroBase shape is included through those Pydantic subclasses; SQLModel table "
            "metadata is not modeled."
        ),
        (
            "The page documents the model fields and optional update model, with the pinned "
            "example definitions at `docs_src/sql_databases/tutorial002_py310.py:7-28`. The "
            "OpenAPI pointers and construction outcome/class/message select "
            "`docs.response.status`, `docs.response.headers`, `docs.response.body.bytes`, "
            "`openapi.document`, `openapi.paths`, and `openapi.request_schema`."
        ),
    ),
    (_PAGE, "create-with-herocreate-and-return-a-heropublic"): _workflow(
        "Create with `HeroCreate` and return a `HeroPublic` "
        "{ #create-with-herocreate-and-return-a-heropublic }",
        281,
        302,
        _RECIPE,
        ["fastapi.docs.sql-databases.multiple-models.create-public"],
        _HTTP_WITH_CONSTRUCTION_SELECTORS,
        (
            "The POST action accepts HeroCreate and declares HeroPublic as its response model. "
            "The returned input record contains a private field so FastAPI response-model "
            "filtering remains observable; no SQLModel object or database operation is used."
        ),
        (
            "The pinned example declares `hero: HeroCreate` and "
            "`response_model=HeroPublic` (`docs_src/sql_databases/tutorial002_py310.py:56-62`). "
            "The input selects construction outcome/class/message and `http.status`, "
            "`http.headers.ordered`, and `http.body.bytes` for the resulting response. The "
            "upstream tutorial tests exercise this route through "
            "an isolated test database "
            "(`tests/test_tutorial/test_sql_databases/test_tutorial002.py`)."
        ),
    ),
    (_PAGE, "read-heroes-with-heropublic"): _workflow(
        "Read Heroes with `HeroPublic` { #read-heroes-with-heropublic }",
        303,
        308,
        _RECIPE,
        ["fastapi.docs.sql-databases.multiple-models.read-public-list"],
        _HTTP_WITH_CONSTRUCTION_SELECTORS,
        (
            "The GET action returns a list containing a private field under the declared "
            "`list[HeroPublic]` response model. It observes FastAPI response filtering without "
            "claiming SQLModel query or database behavior."
        ),
        (
            "The pinned example uses `response_model=list[HeroPublic]` for the list operation "
            "(`docs_src/sql_databases/tutorial002_py310.py:65-72`). The independent GET action "
            "selects `http.status`, `http.headers.ordered`, and `http.body.bytes`, alongside "
            "construction outcome/class/message; generic route dispatch is Starlette 1.6.0 "
            "behavior."
        ),
    ),
    (_PAGE, "run-the-app-again"): _workflow(
        "Run the App Again { #run-the-app-again }",
        333,
        352,
        _RECIPE,
        ["fastapi.docs.sql-databases.multiple-models.openapi"],
        _OPENAPI_WITH_CONSTRUCTION_SELECTORS,
        (
            "The OpenAPI action checks the updated model and operation schemas that the docs UI "
            "would present. The `fastapi dev` process, Uvicorn logs, browser UI, and SQLModel "
            "startup are outside this selected HTTP action."
        ),
        (
            "The pinned page asks users to rerun `fastapi dev` and says the updated docs no "
            "longer request an ID on create (docs/en/docs/tutorial/sql-databases.md:333-352). "
            "The selected GET `/openapi.json` action observes response metadata/body and the "
            "OpenAPI document, paths, and request schemas for create, list, and PATCH operations, "
            "plus construction outcome/class/message."
        ),
    ),
    (_PAGE, "recap"): _excluded(
        "Recap { #recap }",
        353,
        357,
        (
            "The recap summarizes the use of SQLModel and links to its longer tutorial. It adds "
            "no independent FastAPI request, dependency, response, or OpenAPI operation."
        ),
        (
            "The recap attributes SQL database interaction and table/data models to SQLModel "
            "(docs/en/docs/tutorial/sql-databases.md:353-357). Those external library behaviors "
            "are excluded; FastAPI-visible model operations are linked to the narrower sections."
        ),
    ),
}
