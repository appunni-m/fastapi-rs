"""Reviewed section mappings for the Bigger Applications tutorial page."""

_PAGE = "tutorial/bigger-applications.md"
_RECIPE = "tests/fixtures/input-recipes/parity/bigger-applications-sections-20261015.yaml"


def _workflow(heading, start, end, cases, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": _RECIPE,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": selectors,
        "scope_note": note,
        "rationale": rationale,
    }


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


_MAIN = "fastapi.docs.bigger-applications.main-router-composition"
_REPEATED = "fastapi.docs.bigger-applications.repeated-router-prefixes"
_NESTED = "fastapi.docs.bigger-applications.nested-router-live-addition"
_HTTP = ["http.body.bytes", "http.status"]
_HTTP_OPENAPI = ["http.body.bytes", "http.status", "openapi.document", "openapi.paths"]
_OPENAPI = ["openapi.document", "openapi.paths"]

_ROUTING_RATIONALE = (
    "FastAPI 0.157.0 APIRouter registration and include_router route composition are the "
    "feature under review (fastapi/routing.py:2255-2326, 2889-2971, 3133-3320; "
    "fastapi/applications.py:1441-1545). Starlette 1.6.0 owns "
    "generic ASGI dispatch and response emission. The workload's handler values are "
    "user-code stimuli, not FastAPI guarantees."
)

_DEPENDENCY_RATIONALE = (
    "FastAPI 0.157.0 builds and resolves the Depends graph for router-level dependencies "
    "(fastapi/dependencies/utils.py:271-349, 619-714). FastAPI extracts declared query and "
    "header parameters and delegates their value validation to Pydantic; the accept/reject "
    "branches and exception details are authored workload behavior. Starlette 1.6.0 owns "
    "generic ASGI dispatch and response emission."
)

_APP_DEPENDENCY_RATIONALE = (
    "FastAPI 0.157.0 accepts application-wide dependencies and passes them to its root "
    "APIRouter (fastapi/applications.py:331-349, 984-999); router registration and "
    "inclusion carry dependency declarations to path operations "
    "(fastapi/routing.py:2889-2971, 3133-3320). FastAPI builds and solves the dependency "
    "graph and extracts query fields (fastapi/dependencies/utils.py:271-349, 619-697). "
    "The reject branch is workload-authored; Starlette 1.6.0 owns generic ASGI dispatch "
    "and response emission."
)

DOC_SECTION_CASE_MAPPINGS_BIGGER_APPLICATIONS_20261015 = {
    (_PAGE, "bigger-applications-multiple-files"): _excluded(
        "Bigger Applications - Multiple Files { #bigger-applications-multiple-files }",
        1,
        546,
        (
            "The H1 introduces a broad multi-file organization topic and combines package "
            "layout, router declarations, dependencies, router inclusion, CLI setup, and "
            "OpenAPI. Those distinct behaviors are reviewed at their narrower headings; the "
            "overview is not one independently observable operation."
        ),
        (
            "A page-wide workflow would join unrelated Python packaging, FastAPI routing, "
            "FastAPI dependency/OpenAPI, and CLI behavior. Narrow section mappings keep each "
            "claim tied to its own request or schema observation."
        ),
    ),
    (_PAGE, "an-example-file-structure"): _excluded(
        "An example file structure { #an-example-file-structure }",
        13,
        73,
        (
            "The section explains directories, __init__.py files, modules, subpackages, and "
            "Python import notation. These are Python packaging and import semantics and "
            "introduce no FastAPI or ASGI input."
        ),
        (
            "Filesystem layout and Python module resolution are outside the FastAPI runtime "
            "contract. The later router sections map the FastAPI behavior declared by the "
            "example modules."
        ),
    ),
    (_PAGE, "apirouter"): _workflow(
        "`APIRouter` { #apirouter }",
        74,
        111,
        [_MAIN],
        ["users-me-route"],
        _HTTP,
        (
            "The selected request reaches one GET operation declared on an APIRouter and "
            "included in FastAPI. It samples this route only; the prose's claim that router "
            "options generally match FastAPI is not exhaustive."
        ),
        _ROUTING_RATIONALE,
    ),
    (_PAGE, "import-apirouter"): _excluded(
        "Import `APIRouter` { #import-apirouter }",
        84,
        89,
        (
            "The section shows importing APIRouter and constructing a router variable. It "
            "does not define a path operation or an independently observable request."
        ),
        (
            "The constructor's route-composition behavior is observable only after a route is "
            "declared and included, which is sampled in the following path-operation section."
        ),
    ),
    (_PAGE, "path-operations-with-apirouter"): _workflow(
        "*Path operations* with `APIRouter` { #path-operations-with-apirouter }",
        90,
        111,
        [_MAIN],
        ["users-me-route"],
        _HTTP,
        (
            "The request targets the documented users router's `/users/me` path after "
            "inclusion and observes its HTTP status and body. The selected route is one "
            "example, not a claim about every APIRouter option."
        ),
        _ROUTING_RATIONALE,
    ),
    (_PAGE, "dependencies"): _workflow(
        "Dependencies { #dependencies }",
        112,
        129,
        [_MAIN],
        ["items-read-route", "items-missing-header", "items-rejected-header"],
        _HTTP,
        (
            "The actions send an accepted router header, omit the required header, and send a "
            "value rejected by the dependency. They observe only status and response bytes; "
            "they do not claim a full validation-error structure or dependency call order."
        ),
        _DEPENDENCY_RATIONALE,
    ),
    (_PAGE, "another-module-with-apirouter"): _workflow(
        "Another module with `APIRouter` { #another-module-with-apirouter }",
        130,
        290,
        [_MAIN],
        ["items-read-route", "items-openapi-route"],
        _HTTP_OPENAPI,
        (
            "The selected item request and two OpenAPI pointers sample one router prefix, "
            "router tag, and additional 404 response declaration with a router-level "
            "dependency. The example's item database and lookup response remain user code."
        ),
        _ROUTING_RATIONALE
        + " FastAPI's OpenAPI generator projects router metadata into the operation schema "
        "(fastapi/openapi/utils.py:287-308, fastapi/openapi/utils.py:311-400, "
        "fastapi/openapi/utils.py:473-516).",
    ),
    (_PAGE, "import-the-dependencies"): _excluded(
        "Import the dependencies { #import-the-dependencies }",
        202,
        274,
        (
            "This subsection shows a relative Python import from a sibling module. It adds no "
            "separate FastAPI request or router behavior beyond the dependency and router "
            "configuration mapped on this page."
        ),
        (
            "Relative module resolution is Python behavior. The dependency callable's "
            "FastAPI-facing parameter extraction and resolution are sampled in the "
            "Dependencies and router-configuration mappings."
        ),
    ),
    (_PAGE, "how-relative-imports-work"): _excluded(
        "How relative imports work { #how-relative-imports-work }",
        212,
        274,
        (
            "The section explains Python's one-dot, two-dot, and three-dot relative import "
            "rules with filesystem examples; it declares no FastAPI or ASGI behavior."
        ),
        (
            "Python package resolution is outside the FastAPI contract and has no input or "
            "observation in the ASGI recipe."
        ),
    ),
    (_PAGE, "add-some-custom-tags-responses-and-dependencies"): _workflow(
        (
            "Add some custom `tags`, `responses`, and `dependencies` "
            "{ #add-some-custom-tags-responses-and-dependencies }"
        ),
        275,
        290,
        [_MAIN],
        ["items-custom-put-route", "items-custom-openapi-route"],
        _HTTP_OPENAPI,
        (
            "The PUT request supplies the router dependency inputs; its 403 response body is "
            "workload-authored behavior. OpenAPI pointers sample the operation's `custom` "
            "tag and declared 403 response alongside the inherited 404 response. The mapping "
            "does not claim general response-merge precedence or dependency combinations."
        ),
        _ROUTING_RATIONALE
        + " FastAPI emits operation tags and merges additional response declarations in "
        "OpenAPI (fastapi/openapi/utils.py:287-308, fastapi/openapi/utils.py:473-516).",
    ),
    (_PAGE, "the-main-fastapi"): _excluded(
        "The main `FastAPI` { #the-main-fastapi }",
        291,
        466,
        (
            "This heading groups imports and module wiring with app-wide dependency setup, "
            "router inclusion/metadata, and a directly declared operation. The independently "
            "observable dependency, route, and schema behaviors are mapped in narrower child "
            "sections."
        ),
        (
            "The parent combines Python module wiring and multiple FastAPI behaviors. The "
            "app-wide dependency is sampled by the import-FastAPI section's missing and "
            "rejected-token requests; routes and metadata are mapped under their operation "
            "sections. Python import wiring itself is not an ASGI observation."
        ),
    ),
    (_PAGE, "import-fastapi"): _workflow(
        "Import `FastAPI` { #import-fastapi }",
        301,
        308,
        [_MAIN],
        ["global-dependency-missing-token", "global-dependency-rejected-token"],
        _HTTP,
        (
            "Requests to `/users/me` omit the app-wide query token or provide a rejected "
            "token. The users router has no router-level header dependency, so these actions "
            "observe the app-wide dependency's required and reject outcomes; the rejection "
            "body is workload-authored."
        ),
        _APP_DEPENDENCY_RATIONALE,
    ),
    (_PAGE, "import-the-apirouter"): _excluded(
        "Import the `APIRouter` { #import-the-apirouter }",
        309,
        316,
        (
            "This section demonstrates importing local router modules and binding their "
            "objects to names. The imports themselves are Python module behavior."
        ),
        (
            "The FastAPI composition performed with those router objects is sampled under the "
            "include-router section; local import binding is not an ASGI contract."
        ),
    ),
    (_PAGE, "how-the-importing-works"): _excluded(
        "How the importing works { #how-the-importing-works }",
        317,
        358,
        (
            "The section explains Python package names, relative imports, and module execution. "
            "Those language and packaging details do not specify FastAPI behavior."
        ),
        (
            "The ASGI workload cannot independently observe Python import resolution; route "
            "composition from the imported modules is reviewed separately."
        ),
    ),
    (_PAGE, "avoid-name-collisions"): _excluded(
        "Avoid name collisions { #avoid-name-collisions }",
        359,
        377,
        (
            "The section shows aliasing Python imports to avoid local name collisions. It "
            "does not describe a FastAPI API option or request behavior."
        ),
        (
            "Import aliases are evaluated by Python before the ASGI application is built and "
            "are outside the pinned FastAPI runtime contract."
        ),
    ),
    (_PAGE, "include-the-apirouters-for-users-and-items"): _workflow(
        (
            "Include the `APIRouter`s for `users` and `items` "
            "{ #include-the-apirouters-for-users-and-items }"
        ),
        378,
        413,
        [_MAIN],
        ["users-me-route", "items-read-route", "items-openapi-route"],
        _HTTP_OPENAPI,
        (
            "Selected requests reach the included users and items routes; the OpenAPI "
            "observation samples the items path/tag projection. It does not claim complete "
            "router-merge precedence or all routes in either module."
        ),
        _ROUTING_RATIONALE + " OpenAPI path and tag projection is produced by FastAPI "
        "(fastapi/openapi/utils.py:287-308, 311-400).",
    ),
    (
        _PAGE,
        "include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies",
    ): _workflow(
        (
            "Include an `APIRouter` with a custom `prefix`, `tags`, `responses`, and "
            "`dependencies` "
            "{ #include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies }"
        ),
        414,
        442,
        [_MAIN],
        ["admin-post-route", "admin-openapi-route"],
        _HTTP_OPENAPI,
        (
            "The selected POST samples the included admin path and router dependency; the "
            "OpenAPI pointers sample the prefix-derived operation path, inherited tag, and "
            "418 response declaration. The separate response-precedence case remains a "
            "page-level supplemental contract probe: this heading documents included "
            "responses but does not prescribe cross-level overwrite order, so that case is "
            "not attributed as a behavior of this subsection. The response body is user-code "
            "output."
        ),
        _ROUTING_RATIONALE
        + " FastAPI also projects included response declarations and tags into OpenAPI "
        "(fastapi/openapi/utils.py:287-308, fastapi/openapi/utils.py:311-400, "
        "fastapi/openapi/utils.py:473-516).",
    ),
    (_PAGE, "include-a-path-operation"): _workflow(
        "Include a *path operation* { #include-a-path-operation }",
        443,
        466,
        [_MAIN],
        ["root-route", "root-openapi-route"],
        _HTTP_OPENAPI,
        (
            "The GET request reaches one operation declared directly on the FastAPI instance; "
            "the OpenAPI pointer samples the root path's required query parameter. It does "
            "not claim other direct-operation options."
        ),
        _ROUTING_RATIONALE + " FastAPI generates the operation parameter schema "
        "(fastapi/openapi/utils.py:311-400).",
    ),
    (_PAGE, "configure-the-entrypoint-in-pyproject-toml"): _excluded(
        (
            "Configure the `entrypoint` in `pyproject.toml` "
            "{ #configure-the-entrypoint-in-pyproject-toml }"
        ),
        467,
        497,
        (
            "The section specifies the FastAPI CLI's project entrypoint setting and command "
            "line invocation. It has no ASGI request input; process startup, project-file "
            "discovery, and CLI behavior require the separately scoped FastAPI CLI process "
            "contract."
        ),
        (
            "The CLI package and process invocation are a separate public surface from the "
            "FastAPI APIRouter/FastAPI application runtime. The page's CLI commands are not "
            "represented by a router or OpenAPI selector."
        ),
    ),
    (_PAGE, "check-the-automatic-api-docs"): _workflow(
        "Check the automatic API docs { #check-the-automatic-api-docs }",
        498,
        517,
        [_MAIN],
        ["all-routes-openapi-docs"],
        ["docs.response.status", "http.status", "openapi.document", "openapi.paths"],
        (
            "The direct `/openapi.json` action samples successful schema retrieval and selected "
            "paths, tags, and root parameters from the composed application. The screenshot, "
            "CLI launch, and rendered `/docs` UI are outside this mapping."
        ),
        (
            "FastAPI builds the OpenAPI operations from the included routers and direct route "
            "(fastapi/openapi/utils.py:287-308, fastapi/openapi/utils.py:311-400, "
            "fastapi/openapi/utils.py:473-516); its application setup "
            "registers the `/openapi.json` route (fastapi/applications.py:1105-1120). "
            "Starlette 1.6.0 owns generic HTTP dispatch/response behavior, and the interactive "
            "docs page is not observed here."
        ),
    ),
    (
        _PAGE,
        "include-the-same-router-multiple-times-with-different-prefix",
    ): _workflow(
        (
            "Include the same router multiple times with different `prefix` "
            "{ #include-the-same-router-multiple-times-with-different-prefix }"
        ),
        518,
        525,
        [_REPEATED],
        ["first-prefix-route", "second-prefix-route"],
        _HTTP,
        (
            "Two requests target the same APIRouter operation under `/api/v1` and "
            "`/api/latest`. This samples those two prefix inclusions and does not claim "
            "conflict, ordering, or every prefix combination."
        ),
        _ROUTING_RATIONALE,
    ),
    (_PAGE, "include-an-apirouter-in-another"): _workflow(
        "Include an `APIRouter` in another { #include-an-apirouter-in-another }",
        526,
        546,
        [_NESTED],
        ["nested-original-route", "nested-late-route", "nested-openapi-routes"],
        _HTTP_OPENAPI,
        (
            "The actions sample a router nested before app inclusion, a new child operation "
            "declared after the nested router was included in the app, and the two resulting "
            "OpenAPI paths. They do not cover direct mutation of router.routes or every "
            "inclusion order."
        ),
        (
            "FastAPI 0.157.0 builds effective included-router candidates "
            "(fastapi/routing.py:1590-1655), matches and dispatches the selected route "
            "(fastapi/routing.py:1728-1802), and consults router versions during iteration "
            "(fastapi/routing.py:2570-2601, 3133-3320). Starlette 1.6.0 owns "
            "generic ASGI dispatch/response behavior; the endpoint bodies are user code."
        ),
    ),
}
