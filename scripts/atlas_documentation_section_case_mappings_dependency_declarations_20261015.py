"""Reviewed section mappings for FastAPI tutorial dependency declarations."""


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
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


_INDEX = "tutorial/dependencies/index.md"
_CLASSES = "tutorial/dependencies/classes-as-dependencies.md"
_SUB_DEPENDENCIES = "tutorial/dependencies/sub-dependencies.md"
_DECORATOR_DEPENDENCIES = "tutorial/dependencies/dependencies-in-path-operation-decorators.md"

_TUTORIAL_REVIEW = "tests/fixtures/input-recipes/parity/dependency-tutorial-review-upstream.yaml"
_QUERY_COOKIE = (
    "tests/fixtures/input-recipes/parity/dependency-tutorial005-query-cookie-fallback.yaml"
)
_CACHE = "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml"
_DYNAMIC_CACHE = "tests/fixtures/input-recipes/parity/dependency-dynamic-cache-policy.yaml"
_DECORATOR_RETURN = (
    "tests/fixtures/input-recipes/parity/dependency-declarations-section-review-20261015.yaml"
)
_ROUTER_GROUP = "tests/fixtures/input-recipes/parity/bigger-applications-sections-20261015.yaml"
_GLOBAL_DEPENDENCIES = "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml"

_HTTP = ["http.body.bytes", "http.status"]
_HTTP_OPENAPI = ["http.body.bytes", "http.status", "openapi.paths"]
_OPENAPI = ["docs.response.status", "http.status", "openapi.document", "openapi.paths"]
_GLOBAL_HTTP_OPENAPI = [
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
]
_CONSTRUCTION_HTTP = [
    "construction.exception_class",
    "construction.exception_message",
    "construction.outcome",
    "http.body.bytes",
    "http.status",
]


DOC_SECTION_CASE_MAPPINGS_DEPENDENCY_DECLARATIONS_20261015 = {
    (_INDEX, "create-a-dependency-or-dependable"): _workflow(
        'Create a dependency, or "dependable" { #create-a-dependency-or-dependable }',
        28,
        63,
        _TUTORIAL_REVIEW,
        [
            "fastapi.dependencies.tutorial-review.basic-defaults",
            "fastapi.dependencies.tutorial-review.basic-partial-query",
        ],
        None,
        _HTTP,
        (
            "The two requests resolve a function dependency that declares optional `q` and "
            "numeric `skip`/`limit` parameters, then observe the endpoint's returned mapping. "
            "They sample default and supplied query values on analogous workload functions; "
            "they do not claim the source example's exact `limit=100` value or arbitrary "
            "dependency signatures."
        ),
        (
            "The pinned example defines `common_parameters(q, skip, limit)` and returns its "
            "values (`../fastapi/docs_src/dependencies/tutorial001_an_py310.py:8-9`). "
            "FastAPI 0.141.1 inspects a dependency callable's signature and builds its "
            "parameter fields in `get_dependant` "
            "(`../fastapi/fastapi/dependencies/utils.py:271-347`), then resolves it for the "
            "request (`../fastapi/fastapi/dependencies/utils.py:619-690`)."
        ),
    ),
    (_INDEX, "import-depends"): _excluded(
        "Import `Depends` { #import-depends }",
        64,
        67,
        "The subsection shows only the `Depends` import statement and no request workflow.",
        (
            "The import is setup for the adjacent declaration example; it adds no separate "
            "FastAPI dependency graph or request observation."
        ),
    ),
    (_INDEX, "declare-the-dependency-in-the-dependant"): _workflow(
        'Declare the dependency, in the "dependant" { #declare-the-dependency-in-the-dependant }',
        68,
        116,
        _TUTORIAL_REVIEW,
        [
            "fastapi.dependencies.tutorial-review.basic-defaults",
            "fastapi.dependencies.tutorial-review.basic-partial-query",
        ],
        None,
        _HTTP,
        (
            "The requests pass default and supplied query values through a function "
            "dependency to the path operation and observe its response. The workload also "
            "has one direct `Annotated` declaration; it does not cover the full public "
            "`Depends` signature or every parameter source."
        ),
        (
            "The pinned example declares `Depends(common_parameters)` on both route "
            "functions and returns the injected value "
            "(`../fastapi/docs_src/dependencies/tutorial001_an_py310.py:13-19`). "
            "FastAPI 0.141.1 recursively adds the declared callable as a dependant and "
            "inserts its resolved result under the parameter name "
            "(`../fastapi/fastapi/dependencies/utils.py:302-331,677-680`)."
        ),
    ),
    (_INDEX, "share-annotated-dependencies"): _workflow(
        "Share `Annotated` dependencies { #share-annotated-dependencies }",
        117,
        142,
        _TUTORIAL_REVIEW,
        ["fastapi.dependencies.tutorial-review.basic-partial-query"],
        ["set-query-and-use-numeric-defaults"],
        _HTTP,
        (
            "One route resolves a function dependency declared with `Annotated` and "
            "returns its value. The case samples direct `Annotated` dependency injection; "
            "it does not test reuse of the tutorial's `CommonsDep` type alias, editor "
            "completion, or static type-checker behavior."
        ),
        (
            "The pinned `tutorial001_02` example assigns `Annotated[dict, "
            "Depends(common_parameters)]` to `CommonsDep` and annotates two routes with it "
            "(`../fastapi/docs_src/dependencies/tutorial001_02_an_py310.py:12-22`). "
            "FastAPI 0.141.1 extracts `Depends` metadata from `Annotated` while analyzing "
            "the callable signature (`../fastapi/fastapi/dependencies/utils.py:381-445`)."
        ),
    ),
    (_INDEX, "to-async-or-not-to-async"): _workflow(
        "To `async` or not to `async` { #to-async-or-not-to-async }",
        143,
        158,
        _DYNAMIC_CACHE,
        ["fastapi.dependencies.dynamic-cache-policy.nested-sync-parent-async-child"],
        [
            "async-child-mutates-synchronous-parent-policy",
            "resolve-children-again-in-next-request",
        ],
        _HTTP,
        (
            "The selected nested requests exercise a synchronous parent with an "
            "asynchronous child, including resolution in a later request. The response "
            "observations sample that mixed callable path, not timing, concurrency, or "
            "all dependency shapes."
        ),
        (
            "The page states that synchronous and asynchronous path/dependency functions "
            "can be mixed. FastAPI 0.141.1 awaits coroutine dependencies and sends other "
            "callables through `run_in_threadpool` in `solve_dependencies` "
            "(`../fastapi/fastapi/dependencies/utils.py:619-680`); that helper is provided "
            "by the pinned Starlette 1.6.0."
        ),
    ),
    (_INDEX, "integrated-with-openapi"): _workflow(
        "Integrated with OpenAPI { #integrated-with-openapi }",
        159,
        166,
        _TUTORIAL_REVIEW,
        ["fastapi.dependencies.tutorial-review.openapi-projection"],
        ["inspect-dependency-parameter-schema"],
        _OPENAPI,
        (
            "The generated document is inspected for request parameters and validation "
            "references on the selected function and class dependency routes. It does not "
            "cover every dependency type or every OpenAPI field."
        ),
        (
            "The pinned tutorial says dependency and sub-dependency requirements appear in "
            "OpenAPI. FastAPI 0.141.1 walks each route's dependency graph to collect its "
            "path, query, header, and cookie fields before generating operation parameters "
            "(`../fastapi/fastapi/openapi/utils.py:99-129,311-360`)."
        ),
    ),
    (_INDEX, "simple-usage"): _excluded(
        "Simple usage { #simple-usage }",
        167,
        184,
        (
            "This section restates framework dispatch and dependency injection at a general "
            "level without introducing a separate FastAPI input or outcome."
        ),
        (
            "The section describes matching a path operation and calling its dependencies; "
            "the concrete declaration and injection path is mapped above. Generic ASGI "
            "routing belongs to Starlette 1.6.0."
        ),
    ),
    (_INDEX, "simple-and-powerful"): _workflow(
        "Simple and Powerful { #simple-and-powerful }",
        206,
        245,
        _QUERY_COOKIE,
        [
            "fastapi.dependencies.tutorial005.query-cookie.fallback",
            "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
            "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
        ],
        None,
        _HTTP,
        (
            "The selected tutorial route resolves one query dependency beneath a parent "
            "query-or-cookie dependency and exposes the leaf result. This is a two-level "
            "sample; it does not establish behavior for arbitrary graph depth, security "
            "policies, or unrelated routes."
        ),
        (
            "The pinned `tutorial005` example declares `query_or_cookie_extractor` with a "
            "`Depends(query_extractor)` child "
            "(`../fastapi/docs_src/dependencies/tutorial005_an_py310.py:8-25`). "
            "FastAPI 0.141.1 recursively constructs and solves sub-dependencies "
            "(`../fastapi/fastapi/dependencies/utils.py:302-331,619-680`)."
        ),
    ),
    (_INDEX, "integrated-with-openapi_1"): _workflow(
        "Integrated with **OpenAPI** { #integrated-with-openapi_1 }",
        246,
        250,
        _QUERY_COOKIE,
        ["fastapi.dependencies.tutorial005.query-cookie.openapi-parameters"],
        ["inspect-query-and-cookie-parameter-definitions"],
        _OPENAPI,
        (
            "The action inspects the selected `/items/` operation's query and cookie "
            "parameter definitions. It samples this nested dependency's declared fields, "
            "not the complete OpenAPI document or all dependency combinations."
        ),
        (
            "The pinned `tutorial005` page says nested dependency requirements are added "
            "to OpenAPI. FastAPI 0.141.1 traverses dependant nodes, gathers their fields, "
            "and emits operation parameters "
            "(`../fastapi/fastapi/openapi/utils.py:99-129,159-210,311-360`)."
        ),
    ),
    (_CLASSES, "classes-as-dependencies"): _excluded(
        "Classes as Dependencies { #classes-as-dependencies }",
        1,
        288,
        (
            "The H1 introduces class dependencies and groups several distinct child topics. "
            "Those behaviors are mapped at their source-specific headings below."
        ),
        (
            "FastAPI 0.141.1 analyzes dependency callable signatures in `get_dependant` "
            "(`../fastapi/fastapi/dependencies/utils.py:271-347`); this page-level heading "
            "adds no separate request or observation."
        ),
    ),
    (_CLASSES, "a-dict-from-the-previous-example"): _excluded(
        "A `dict` from the previous example { #a-dict-from-the-previous-example }",
        5,
        16,
        (
            "This section discusses the editor and static-typing limitations of a Python "
            "`dict` result; it adds no distinct FastAPI dependency behavior."
        ),
        (
            "The pinned text concerns editor completion and key typing for a dictionary "
            "returned by the earlier example. Those Python tooling observations are outside "
            "the FastAPI and Starlette runtime contract."
        ),
    ),
    (_CLASSES, "what-makes-a-dependency"): _workflow(
        "What makes a dependency { #what-makes-a-dependency }",
        17,
        40,
        _TUTORIAL_REVIEW,
        ["fastapi.dependencies.tutorial-review.catalog-default-window"],
        ["explicit-class-dependency"],
        _HTTP,
        (
            "The selected route passes a class as the dependency callable and observes its "
            "constructed value through the response. It samples this class case only; "
            "arbitrary callable objects, custom `__call__` signatures, and zero-argument "
            "callables are not claimed."
        ),
        (
            "The page explains that classes are callable and that FastAPI analyzes callable "
            "parameters. FastAPI 0.141.1 obtains a typed signature and uses it to build "
            "dependency fields (`../fastapi/fastapi/dependencies/utils.py:198-227,271-347`). "
            "The active case exercises an analogous class dependency."
        ),
    ),
    (_CLASSES, "classes-as-dependencies_1"): _workflow(
        "Classes as dependencies { #classes-as-dependencies_1 }",
        41,
        91,
        _TUTORIAL_REVIEW,
        [
            "fastapi.dependencies.tutorial-review.catalog-default-window",
            "fastapi.dependencies.tutorial-review.catalog-custom-window",
        ],
        None,
        _HTTP,
        (
            "The requests construct an analogous class dependency with omitted and "
            "explicit query values, then use its instance in the route. The workload's "
            "`CatalogWindow` has `limit=3`; it does not assert the documentation example's "
            "`CommonQueryParams` class or its `limit=100` default."
        ),
        (
            "The pinned `tutorial002` class declares `q`, `skip`, and `limit` on `__init__` "
            "and the path operation depends on `CommonQueryParams` "
            "(`../fastapi/docs_src/dependencies/tutorial002_an_py310.py:11-25`). "
            "FastAPI 0.141.1 inspects the callable signature and recursively analyzes its "
            "parameters (`../fastapi/fastapi/dependencies/utils.py:271-347`)."
        ),
    ),
    (_CLASSES, "use-it"): _workflow(
        "Use it { #use-it }",
        92,
        99,
        _TUTORIAL_REVIEW,
        ["fastapi.dependencies.tutorial-review.catalog-default-window"],
        ["explicit-class-dependency"],
        _HTTP,
        (
            "The selected path operation receives and uses the returned `CatalogWindow` "
            "instance to form its response. It does not test application-specific effects "
            "beyond this route's filtering and response."
        ),
        (
            "The pinned section says FastAPI calls the class and passes the instance to "
            "the route (`../fastapi/docs/en/docs/tutorial/dependencies/classes-as-"
            "dependencies.md:92-99`). FastAPI 0.141.1 solves the dependency and stores its "
            "result under the declared parameter name "
            "(`../fastapi/fastapi/dependencies/utils.py:619-680`)."
        ),
    ),
    (_CLASSES, "type-annotation-vs-depends"): _workflow(
        "Type annotation vs `Depends` { #type-annotation-vs-depends }",
        100,
        195,
        _TUTORIAL_REVIEW,
        ["fastapi.dependencies.tutorial-review.catalog-default-window"],
        [
            "explicit-class-dependency",
            "untyped-class-dependency",
            "inferred-class-dependency",
        ],
        _HTTP,
        (
            "The actions compare an explicit class in `Depends`, an untyped `Depends` "
            "default, and a typed `Annotated` declaration with an empty `Depends()`. They "
            "sample response behavior for `CatalogWindow`; the legacy typed default syntax, "
            "`Any` annotation, editor behavior, and every validation detail are not covered."
        ),
        (
            "The pinned section distinguishes the callable passed to `Depends` from the "
            "parameter's type annotation. FastAPI 0.141.1 reads `Depends` from `Annotated` "
            "or a default and infers an omitted callable from the type annotation "
            "(`../fastapi/fastapi/dependencies/utils.py:381-471`)."
        ),
    ),
    (_CLASSES, "shortcut"): _workflow(
        "Shortcut { #shortcut }",
        196,
        288,
        _TUTORIAL_REVIEW,
        [
            "fastapi.dependencies.tutorial-review.catalog-default-window",
            "fastapi.dependencies.tutorial-review.catalog-custom-window",
        ],
        None,
        _HTTP,
        (
            "The two actions use the class annotation with `Annotated[..., Depends()]` "
            "to infer the class dependency and exercise default and explicit query values. "
            "They do not cover the non-`Annotated` shortcut form or other class signatures."
        ),
        (
            "The pinned `tutorial004` example uses `Annotated[CommonQueryParams, "
            "Depends()]` (`../fastapi/docs_src/dependencies/tutorial004_an_py310.py:11-25`). "
            "FastAPI 0.141.1 copies an empty `Depends`, fills its dependency from the "
            "annotation, and builds the resulting callable graph "
            "(`../fastapi/fastapi/dependencies/utils.py:443-471,271-347`)."
        ),
    ),
    (_SUB_DEPENDENCIES, "sub-dependencies"): _excluded(
        "Sub-dependencies { #sub-dependencies }",
        1,
        105,
        (
            "The H1 summarizes dependency nesting and cache reuse; its concrete graph and "
            "cache behaviors are mapped at the child headings."
        ),
        (
            "The nested query/cookie graph and repeated-call cache cases are mapped below; "
            "the page introduction adds no separate request workflow."
        ),
    ),
    (_SUB_DEPENDENCIES, "first-dependency-dependable"): _workflow(
        'First dependency "dependable" { #first-dependency-dependable }',
        9,
        18,
        _QUERY_COOKIE,
        [
            "fastapi.dependencies.tutorial005.query-cookie.fallback",
            "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
            "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
        ],
        None,
        _HTTP,
        (
            "Each request resolves the optional query extractor beneath the documented "
            "parent and exposes whether its `q` value reached the final response. This "
            "does not call the first dependency as a top-level route parameter."
        ),
        (
            "The pinned example's `query_extractor` accepts optional `q` and returns it "
            "(`../fastapi/docs_src/dependencies/tutorial005_an_py310.py:8-9`). FastAPI "
            "0.141.1 constructs that child from the parent's `Depends` annotation and "
            "passes the solved value to the parent "
            "(`../fastapi/fastapi/dependencies/utils.py:302-331,640-680`)."
        ),
    ),
    (_SUB_DEPENDENCIES, "second-dependency-dependable-and-dependant"): _workflow(
        'Second dependency, "dependable" and "dependant" '
        "{ #second-dependency-dependable-and-dependant }",
        19,
        31,
        _QUERY_COOKIE,
        [
            "fastapi.dependencies.tutorial005.query-cookie.fallback",
            "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
            "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
        ],
        None,
        _HTTP,
        (
            "The requests exercise the parent's query-extractor sub-dependency plus its "
            "optional cookie field, covering cookie fallback, query precedence, and an "
            "absent pair. They do not sample other dependency graph shapes."
        ),
        (
            "The pinned `query_or_cookie_extractor` declares `Depends(query_extractor)` "
            "and a `Cookie()` parameter (`../fastapi/docs_src/dependencies/tutorial005_"
            "an_py310.py:12-19`). FastAPI 0.141.1 recursively builds the child dependant "
            "and resolves it before calling its parent "
            "(`../fastapi/fastapi/dependencies/utils.py:302-331,640-680`)."
        ),
    ),
    (_SUB_DEPENDENCIES, "use-the-dependency"): _workflow(
        "Use the dependency { #use-the-dependency }",
        32,
        56,
        _QUERY_COOKIE,
        [
            "fastapi.dependencies.tutorial005.query-cookie.fallback",
            "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
            "fastapi.dependencies.tutorial005.query-cookie.no-query-or-cookie",
        ],
        None,
        _HTTP,
        (
            "The route declares only the parent dependency; the selected responses expose "
            "the value produced after FastAPI resolves its query child and cookie field. "
            "The inputs do not measure call order or all possible graph depths."
        ),
        (
            "The pinned route declares `Depends(query_or_cookie_extractor)` and returns its "
            "result (`../fastapi/docs_src/dependencies/tutorial005_an_py310.py:22-25`). "
            "FastAPI 0.141.1 recursively solves child dependencies before invoking their "
            "parent (`../fastapi/fastapi/dependencies/utils.py:619-680`)."
        ),
    ),
    (_SUB_DEPENDENCIES, "using-the-same-dependency-multiple-times"): _workflow(
        "Using the same dependency multiple times { #using-the-same-dependency-multiple-times }",
        57,
        88,
        _CACHE,
        ["fastapi.dependencies.cache-reuse", "fastapi.dependencies.cache-bypass"],
        ["first-request", "next-request"],
        _HTTP,
        (
            "The route actions resolve one callable twice with the default cache policy "
            "and once with `use_cache=False`, exposing returned values and call counts. "
            "They do not test two parent dependencies sharing a common child node."
        ),
        (
            "The pinned section documents request-local dependency reuse and the `use_cache` "
            "opt-out. FastAPI 0.141.1 computes a cache key, reuses a present value when the "
            "edge is cache-enabled, and stores solved results "
            "(`../fastapi/fastapi/dependencies/utils.py:656-680`)."
        ),
    ),
    (_SUB_DEPENDENCIES, "recap"): _workflow(
        "Recap { #recap }",
        89,
        105,
        _QUERY_COOKIE,
        [
            "fastapi.dependencies.tutorial005.query-cookie.fallback",
            "fastapi.dependencies.tutorial005.query-cookie.query-precedence",
        ],
        None,
        _HTTP,
        (
            "The recap's graph claim is sampled with the documented two-level query/cookie "
            "example and two input branches. It does not prove arbitrary depth or general "
            "security behavior."
        ),
        (
            "The pinned recap states that dependencies can form nested graphs; the preceding "
            "`tutorial005` source supplies a concrete parent/child graph "
            "(`../fastapi/docs_src/dependencies/tutorial005_an_py310.py:8-25`). FastAPI "
            "0.141.1 recursively calls `get_dependant` while analyzing child declarations "
            "(`../fastapi/fastapi/dependencies/utils.py:302-331`)."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "dependencies-in-path-operation-decorators"): _excluded(
        "Dependencies in path operation decorators { #dependencies-in-path-operation-decorators }",
        1,
        69,
        (
            "The H1 introduces decorator-level dependencies, their errors and ignored return "
            "values, router-level dependencies, and application-wide dependencies. The "
            "behavior-specific child headings are mapped individually."
        ),
        (
            "FastAPI 0.141.1 builds parameterless route dependency nodes in routing and "
            "solves them through the dependency solver "
            "(`../fastapi/fastapi/routing.py:855-869`; "
            "`../fastapi/fastapi/dependencies/utils.py:619-680`). This overview does not "
            "add a separate request contract."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "add-dependencies-to-the-path-operation-decorator"): _workflow(
        "Add `dependencies` to the *path operation decorator* "
        "{ #add-dependencies-to-the-path-operation-decorator }",
        11,
        38,
        _TUTORIAL_REVIEW,
        [
            "fastapi.dependencies.tutorial-review.headers-missing",
            "fastapi.dependencies.tutorial-review.headers-invalid-token",
            "fastapi.dependencies.tutorial-review.headers-invalid-key",
        ],
        None,
        _HTTP,
        (
            "The requests reach one operation with two decorator-level dependencies and "
            "observe missing-header and dependency-raised error outcomes. This case set "
            "does not include a successful request or claim dependency call order when both "
            "checks pass."
        ),
        (
            "The pinned `tutorial006` example declares two `Depends` values in the path "
            "operation decorator "
            "(`../fastapi/docs_src/dependencies/tutorial006_an_py310.py:8-20`). "
            "FastAPI 0.141.1 converts parameterless declarations into dependant nodes "
            "(`../fastapi/fastapi/routing.py:855-869`) and recursively resolves them "
            "(`../fastapi/fastapi/dependencies/utils.py:619-680`)."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "dependencies-errors-and-return-values"): _excluded(
        "Dependencies errors and return values { #dependencies-errors-and-return-values }",
        39,
        62,
        (
            "This parent section groups declared requirements, raised exceptions, and "
            "ignored return values. Those independently observable paths are mapped by its "
            "three child headings."
        ),
        (
            "The child mappings select their own inputs and observations; a parent row "
            "would combine validation, exception, and successful return behavior without "
            "adding a distinct dependency operation."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "dependency-requirements"): _workflow(
        "Dependency requirements { #dependency-requirements }",
        43,
        48,
        _TUTORIAL_REVIEW,
        ["fastapi.dependencies.tutorial-review.headers-missing"],
        ["omit-both-required-headers"],
        _HTTP,
        (
            "One request omits the two required header fields declared by the route's "
            "dependency functions and observes the public validation response. It does not "
            "cover body, query, cookie, or nested-dependency requirements."
        ),
        (
            "The pinned example declares `Header()` parameters inside dependency callables "
            "(`../fastapi/docs_src/dependencies/tutorial006_an_py310.py:8,13`). FastAPI "
            "0.141.1 analyzes each dependant signature and collects header fields "
            "(`../fastapi/fastapi/dependencies/utils.py:271-347,681-690`)."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "raise-exceptions"): _workflow(
        "Raise exceptions { #raise-exceptions }",
        49,
        54,
        _TUTORIAL_REVIEW,
        [
            "fastapi.dependencies.tutorial-review.headers-invalid-token",
            "fastapi.dependencies.tutorial-review.headers-invalid-key",
        ],
        None,
        _HTTP,
        (
            "Each request supplies the prior requirement needed to reach one of the two "
            "dependency functions' `HTTPException` branches. The mappings do not cover "
            "custom exception handlers or other exception classes."
        ),
        (
            "The pinned example raises `HTTPException` from each dependency when its "
            "header value is invalid (`../fastapi/docs_src/dependencies/tutorial006_an_"
            "py310.py:8-16`). FastAPI 0.141.1 solves decorator dependencies through its "
            "dependency graph (`../fastapi/fastapi/dependencies/utils.py:619-680`); "
            "Starlette 1.6.0 owns generic HTTP exception response dispatch."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "return-values"): _workflow(
        "Return values { #return-values }",
        55,
        62,
        _DECORATOR_RETURN,
        ["fastapi.docs.dependency-declarations.section-review.decorator-return-value-not-injected"],
        None,
        _CONSTRUCTION_HTTP,
        (
            "The valid request resolves two decorator dependencies, then reads a separate "
            "trace route. The second dependency returns a string while the endpoint accepts "
            "no dependency parameter and returns its own fixed stock result. This samples "
            "one successful non-null ignored value, not arbitrary return types or reuse of "
            "the dependency as an injected parameter."
        ),
        (
            "The pinned `tutorial006` example returns a header value from one decorator "
            "dependency while its path operation has no dependency parameter "
            "(`../fastapi/docs_src/dependencies/tutorial006_an_py310.py:13-21`). This "
            "independently authored input uses different routes, names, header values, and "
            "payloads to sample that shape. FastAPI 0.141.1 creates parameterless dependant "
            "nodes (`../fastapi/fastapi/routing.py:855-869`) and adds solved values to the "
            "parent only when the node has a parameter name "
            "(`../fastapi/fastapi/dependencies/utils.py:677-678`)."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "dependencies-for-a-group-of-path-operations"): _workflow(
        "Dependencies for a group of *path operations* "
        "{ #dependencies-for-a-group-of-path-operations }",
        63,
        66,
        _ROUTER_GROUP,
        ["fastapi.docs.bigger-applications.main-router-composition"],
        ["items-read-route", "items-missing-header", "items-rejected-header"],
        _HTTP,
        (
            "The selected route belongs to an `APIRouter` with a shared header dependency; "
            "the actions observe its accepted, missing, and rejected header paths. They "
            "sample one grouped route and do not establish behavior for every router "
            "inclusion option."
        ),
        (
            "This section links to the pinned Bigger Applications tutorial, whose router "
            "declares a `dependencies` list in `docs_src/bigger_applications/app_an_py310/"
            "main.py` and applies it to its route. FastAPI 0.141.1 copies router-level "
            "dependencies into each added API route "
            "(`../fastapi/fastapi/routing.py:2300-2311,2927-2945`)."
        ),
    ),
    (_DECORATOR_DEPENDENCIES, "global-dependencies"): _workflow(
        "Global Dependencies { #global-dependencies }",
        67,
        69,
        _GLOBAL_DEPENDENCIES,
        ["fastapi.docs.documentation-wave.dependencies-security.global-dependencies"],
        ["dispatch", "openapi"],
        _GLOBAL_HTTP_OPENAPI,
        (
            "One route in an application configured with a global tenant-key dependency "
            "is requested and its parameter schema is inspected. This samples one "
            "application dependency and does not cover every route or dependency type."
        ),
        (
            "The pinned section introduces application-wide dependencies. FastAPI 0.141.1 "
            "passes the constructor's dependency list into its root `APIRouter` "
            "(`../fastapi/fastapi/applications.py:984-999`), whose route graph is built "
            "and solved by FastAPI's dependency utilities "
            "(`../fastapi/fastapi/dependencies/utils.py:271-347,619-680`)."
        ),
    ),
}
