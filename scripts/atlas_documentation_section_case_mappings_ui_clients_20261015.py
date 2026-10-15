"""Reviewed source-section mappings for FastAPI docs UI and client guides."""

_CUSTOM_DOCS = "how-to/custom-docs-ui-assets.md"
_CONFIGURE_SWAGGER = "how-to/configure-swagger-ui.md"
_CONDITIONAL_OPENAPI = "how-to/conditional-openapi.md"
_GENERATE_CLIENTS = "advanced/generate-clients.md"

_UI_RECIPE = "tests/fixtures/input-recipes/parity/docs-ui-clients-sections-20261015.yaml"
_CLIENT_VERSION_RECIPE = (
    "tests/fixtures/input-recipes/parity/docs-clients-openapi-version-20261015.yaml"
)
_CLIENT_BASIC_RECIPE = (
    "tests/fixtures/input-recipes/parity/generate-clients-tutorial001-upstream.yaml"
)
_CLIENT_TAGGED_RECIPE = (
    "tests/fixtures/input-recipes/parity/generate-clients-tutorial002-upstream.yaml"
)
_CLIENT_IDS_RECIPE = (
    "tests/fixtures/input-recipes/parity/generate-clients-tutorial003-upstream.yaml"
)
_SWAGGER_DEFAULT_RECIPE = (
    "tests/fixtures/input-recipes/parity/swagger-ui-config-default-wave.yaml"
)
_SWAGGER_THEME_RECIPE = (
    "tests/fixtures/input-recipes/parity/swagger-ui-config-theme-wave.yaml"
)
_SWAGGER_OVERRIDE_RECIPE = (
    "tests/fixtures/input-recipes/parity/swagger-ui-config-override-wave.yaml"
)
_CONDITIONAL_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-openapi-conditional-interface-review.yaml"
)

_UI_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_UI_HTTP_BODY = ["http.body.bytes", "http.status"]
_OPENAPI_VERSION = ["docs.response.status", "http.status", "openapi.document"]
_OPENAPI_PATHS = [
    "docs.response.status",
    "http.status",
    "openapi.document",
    "openapi.paths",
]


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
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


_UI_RATIONALE = (
    "FastAPI 0.141.1 get_swagger_ui_html and get_redoc_html build HTML responses from the "
    "configured OpenAPI and asset URLs (fastapi/openapi/docs.py:40-194, 197-298); "
    "get_swagger_ui_oauth2_redirect_html emits its redirect document at lines 301-380. "
    "FastAPI stores the docs URLs and parameters, then conditionally registers its own "
    "OpenAPI, Swagger, OAuth redirect, and ReDoc routes (fastapi/applications.py:881-890, "
    "1105-1158). Starlette 1.6.0 owns generic route/mount dispatch and StaticFiles service "
    "(starlette/applications.py:98-100; starlette/routing.py:380-425; "
    "starlette/staticfiles.py:39-56, 110-152). The selected HTTP actions compare only the "
    "emitted response or mounted-file response; they do not execute a browser, fetch a CDN, "
    "or render the Swagger UI or ReDoc JavaScript."
)

_SWAGGER_RATIONALE = (
    "FastAPI 0.141.1 copies its default Swagger UI parameter dictionary, applies the provided "
    "parameter overrides, and serializes values into generated HTML "
    "(fastapi/openapi/docs.py:13-37, 148-172). FastAPI.applications passes the stored values "
    "to its docs HTML helper (fastapi/applications.py:881-890, 1121-1137). Starlette 1.6.0 "
    "emits the HTML response; the selected action observes response bytes and status only. "
    "It does not execute Swagger UI JavaScript or establish browser rendering."
)

_OPENAPI_VERSION_RATIONALE = (
    "FastAPI 0.141.1 exposes its configured OpenAPI version through get_openapi, places it "
    "in the root schema object, and serves that schema from the configured OpenAPI endpoint "
    "(fastapi/openapi/utils.py:585-614; fastapi/applications.py:1085-1120). The pinned page "
    "states that SDK generators must support OpenAPI 3.1 at "
    "docs/en/docs/advanced/generate-clients.md:17-20. The linked action observes only the "
    "server-generated version field; it does not run or claim compatibility for any external "
    "SDK generator."
)

_CLIENT_BASIC_RATIONALE = (
    "The pinned tutorial declares request and response models and path operations in "
    "docs_src/generate_clients/tutorial001_py310.py:7-26. FastAPI 0.141.1 collects route "
    "fields and builds the OpenAPI paths and schema components in fastapi/openapi/utils.py:"
    "620-679; the app serves the resulting schema from applications.py:1105-1120. "
    "Starlette 1.6.0 owns generic ASGI dispatch. The case supplies API and OpenAPI input to "
    "a client generator; it does not generate, compile, or execute a client."
)

_CLIENT_TAGGED_RATIONALE = (
    "FastAPI 0.141.1 records route tags and operation metadata in the OpenAPI document "
    "(fastapi/openapi/utils.py:287-305, 620-679); the selected tutorial case observes its "
    "tagged paths and schema values. Grouping generated services or methods by those tags is "
    "external SDK-generator behavior and is not claimed."
)

_CLIENT_IDS_RATIONALE = (
    "FastAPI 0.141.1 accepts generate_unique_id_function on FastAPI, passes it to API routes, "
    "computes each route unique_id, and uses that value as the OpenAPI operationId "
    "(fastapi/applications.py:765-779, 997-999; fastapi/routing.py:1013-1028; "
    "fastapi/openapi/utils.py:287-305). The selected action observes the resulting OpenAPI "
    "operationId fields only; client method names and generated output are not observed."
)

DOC_SECTION_CASE_MAPPINGS_UI_CLIENTS_20261015 = {
    (_CUSTOM_DOCS, "custom-docs-ui-static-assets-self-hosting"): _workflow(
        "Custom Docs UI Static Assets (Self-Hosting) "
        "{ #custom-docs-ui-static-assets-self-hosting }",
        1,
        185,
        _UI_RECIPE,
        [
            "fastapi.docs.ui-clients.custom-cdn",
            "fastapi.docs.ui-clients.custom-self-hosted",
        ],
        ["swagger-html", "redoc-html"],
        _UI_HTTP,
        (
            "The two selected actions compare FastAPI-generated Swagger and ReDoc HTML for "
            "the documented CDN and local-asset URL forms. Child sections review route "
            "disabling, a user path operation, static file responses, and browser-only claims "
            "separately. No browser, CDN request, asset execution, or UI rendering is sampled."
        ),
        _UI_RATIONALE,
    ),
    (_CUSTOM_DOCS, "custom-cdn-for-javascript-and-css"): _workflow(
        "Custom CDN for JavaScript and CSS { #custom-cdn-for-javascript-and-css }",
        9,
        58,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-cdn"],
        ["swagger-html", "oauth-redirect", "redoc-html"],
        _UI_HTTP,
        (
            "The selected custom routes emit HTML containing the configured CDN URLs, and "
            "the OAuth helper emits an HTML response. The actions do not fetch those URLs, "
            "authenticate with a provider, or render either JavaScript UI."
        ),
        _UI_RATIONALE,
    ),
    (_CUSTOM_DOCS, "include-the-custom-docs"): _workflow(
        "Include the custom docs { #include-the-custom-docs }",
        23,
        48,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-cdn"],
        ["swagger-html", "oauth-redirect", "redoc-html"],
        _UI_HTTP,
        (
            "The selected responses cover custom Swagger and ReDoc HTML plus the OAuth redirect "
            "helper. They expose URL strings and server response bytes only; the OAuth provider "
            "flow and browser-side Swagger/ReDoc code are outside the actions."
        ),
        _UI_RATIONALE,
    ),
    (_CUSTOM_DOCS, "create-a-path-operation-to-test-it"): _workflow(
        "Create a *path operation* to test it { #create-a-path-operation-to-test-it }",
        49,
        54,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-cdn"],
        ["api-route"],
        _UI_HTTP_BODY,
        (
            "The request reaches the documented users path operation and observes its status "
            "and response bytes. It does not exercise the client-side UI."
        ),
        (
            "The pinned example defines GET /users/{username} at "
            "docs_src/custom_docs_ui/tutorial001_py310.py:36-38, and its upstream tutorial "
            "test requests /users/john at tests/test_tutorial/test_custom_docs_ui/"
            "test_tutorial001.py:34-37. FastAPI binds the path parameter; Starlette 1.6.0 "
            "owns generic request dispatch and response emission."
        ),
    ),
    (_CUSTOM_DOCS, "self-hosting-javascript-and-css-for-docs"): _workflow(
        "Self-hosting JavaScript and CSS for docs { #self-hosting-javascript-and-css-for-docs }",
        59,
        185,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-self-hosted"],
        [
            "swagger-html",
            "redoc-html",
            "static-swagger-bundle",
            "static-swagger-css",
            "static-redoc",
        ],
        _UI_HTTP,
        (
            "The selected actions inspect emitted HTML URLs and three synthetic files served "
            "through a StaticFiles mount. The file contents are input markers, not Swagger or "
            "ReDoc distributions; this does not prove offline UI rendering or interaction."
        ),
        _UI_RATIONALE,
    ),
    (_CUSTOM_DOCS, "project-file-structure"): _excluded(
        "Project file structure { #project-file-structure }",
        65,
        87,
        (
            "The pinned section shows application and static-directory layouts only "
            "(docs/en/docs/how-to/custom-docs-ui-assets.md:65-87). It declares no FastAPI "
            "call, ASGI request, or independently observable framework behavior."
        ),
        (
            "Filesystem organization and Python package layout are application setup choices. "
            "FastAPI does not inspect this diagram during request handling; the later "
            "StaticFiles mount and HTTP requests are reviewed under their own sections."
        ),
    ),
    (_CUSTOM_DOCS, "download-the-files"): _excluded(
        "Download the files { #download-the-files }",
        88,
        115,
        (
            "The pinned section instructs the reader to fetch vendor JavaScript and CSS from "
            "external CDN URLs and place those bytes in a local directory "
            "(docs/en/docs/how-to/custom-docs-ui-assets.md:88-115). It has no FastAPI or ASGI "
            "operation."
        ),
        (
            "Downloading third-party distributions and choosing a local project directory are "
            "external setup behavior. FastAPI emits asset URL strings; Starlette serves a "
            "mounted local file when requested. Neither library performs the download."
        ),
    ),
    (_CUSTOM_DOCS, "serve-the-static-files"): _workflow(
        "Serve the static files { #serve-the-static-files }",
        116,
        122,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-self-hosted"],
        ["static-swagger-bundle"],
        _UI_HTTP_BODY,
        (
            "The request reaches one file under the documented /static mount and observes its "
            "status and body bytes. The synthetic file content proves route-to-file serving "
            "for this workload only, not the vendor distribution's operation."
        ),
        (
            "The pinned example imports FastAPI.staticfiles.StaticFiles and mounts it at "
            "/static (docs_src/custom_docs_ui/tutorial002_py310.py:7-11). FastAPI re-exports "
            "the Starlette implementation; Starlette 1.6.0 owns mount matching and StaticFiles "
            "lookup/response behavior (starlette/applications.py:98-100; "
            "starlette/routing.py:380-425; starlette/staticfiles.py:39-56, 110-152)."
        ),
    ),
    (_CUSTOM_DOCS, "test-the-static-files"): _workflow(
        "Test the static files { #test-the-static-files }",
        123,
        140,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-self-hosted"],
        ["static-redoc"],
        _UI_HTTP_BODY,
        (
            "The selected GET returns the independent input marker at the ReDoc asset path. "
            "The observation is HTTP status and bytes only; it does not assert that the file "
            "is the vendor bundle or that a browser executes it."
        ),
        (
            "The pinned section opens /static/redoc.standalone.js and describes the returned "
            "JavaScript bytes (docs/en/docs/how-to/custom-docs-ui-assets.md:123-140). The "
            "example mounts StaticFiles at /static (docs_src/custom_docs_ui/"
            "tutorial002_py310.py:7-11); Starlette 1.6.0 performs static path lookup and "
            "response dispatch (starlette/staticfiles.py:110-152)."
        ),
    ),
    (_CUSTOM_DOCS, "disable-the-automatic-docs-for-static-files"): _workflow(
        "Disable the automatic docs for static files "
        "{ #disable-the-automatic-docs-for-static-files }",
        141,
        148,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.automatic-docs-disabled"],
        ["swagger-disabled", "redoc-disabled"],
        ["http.status"],
        (
            "The two requests observe that the default Swagger and ReDoc routes are not "
            "registered when the app is built with docs_url=None and redoc_url=None. The "
            "case does not sample their replacement custom routes."
        ),
        (
            "The pinned tutorial constructs FastAPI(docs_url=None, redoc_url=None) at "
            "docs_src/custom_docs_ui/tutorial002_py310.py:9. FastAPI stores those options "
            "and adds the corresponding routes only when their configured URLs are truthy "
            "(fastapi/applications.py:881-890, 1121-1158). Starlette 1.6.0 supplies the "
            "generic unmatched-route response."
        ),
    ),
    (_CUSTOM_DOCS, "include-the-custom-docs-for-static-files"): _workflow(
        "Include the custom docs for static files { #include-the-custom-docs-for-static-files }",
        149,
        174,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-self-hosted"],
        ["swagger-html", "oauth-redirect", "redoc-html"],
        _UI_HTTP,
        (
            "The selected custom responses expose the local JavaScript/CSS URLs and OpenAPI "
            "URL in generated HTML, and serve the OAuth redirect helper document. They do "
            "not establish browser asset fetching, authentication, or rendering."
        ),
        _UI_RATIONALE,
    ),
    (_CUSTOM_DOCS, "create-a-path-operation-to-test-static-files"): _workflow(
        "Create a *path operation* to test static files "
        "{ #create-a-path-operation-to-test-static-files }",
        175,
        180,
        _UI_RECIPE,
        ["fastapi.docs.ui-clients.custom-self-hosted"],
        ["api-route"],
        _UI_HTTP_BODY,
        (
            "The request reaches the documented users path operation in the self-hosted "
            "configuration and observes its status and response bytes; no UI client executes."
        ),
        (
            "The pinned example declares GET /users/{username} at "
            "docs_src/custom_docs_ui/tutorial002_py310.py:39-41 and its upstream test "
            "requests /users/john at tests/test_tutorial/test_custom_docs_ui/"
            "test_tutorial002.py:34-37. FastAPI extracts the path parameter; Starlette 1.6.0 "
            "owns generic dispatch and response emission."
        ),
    ),
    (_CUSTOM_DOCS, "test-static-files-ui"): _excluded(
        "Test Static Files UI { #test-static-files-ui }",
        181,
        185,
        (
            "The pinned section asks the reader to disconnect WiFi and inspect/interact with "
            "Swagger UI in a browser (docs/en/docs/how-to/custom-docs-ui-assets.md:181-185). "
            "No browser or external asset request is part of the FastAPI ASGI contract."
        ),
        (
            "This claim depends on the downloaded Swagger/ReDoc JavaScript, CSS, browser "
            "execution, and offline network state. The section declares no new FastAPI "
            "operation. The server-generated HTML and synthetic local-file responses are "
            "mapped separately, without inferring that the UI renders."
        ),
    ),
    (_CONFIGURE_SWAGGER, "configure-swagger-ui"): _workflow(
        "Configure Swagger UI { #configure-swagger-ui }",
        1,
        70,
        _SWAGGER_OVERRIDE_RECIPE,
        ["fastapi.docs-ui.swagger-parameters.override-default"],
        ["swagger-html"],
        _UI_HTTP_BODY,
        (
            "The selected /docs action observes generated HTML for the documented override "
            "example. It does not execute JavaScript or cover all possible Swagger UI "
            "parameters."
        ),
        _SWAGGER_RATIONALE,
    ),
    (_CONFIGURE_SWAGGER, "disable-syntax-highlighting"): _workflow(
        "Disable Syntax Highlighting { #disable-syntax-highlighting }",
        11,
        26,
        _SWAGGER_DEFAULT_RECIPE,
        ["fastapi.docs-ui.swagger-parameters.default-config"],
        ["swagger-html"],
        _UI_HTTP_BODY,
        (
            "The selected response bytes contain the configured syntaxHighlight value and "
            "FastAPI's generated Swagger UI bootstrap. The resulting browser appearance is "
            "not observed."
        ),
        _SWAGGER_RATIONALE,
    ),
    (_CONFIGURE_SWAGGER, "change-the-theme"): _workflow(
        "Change the Theme { #change-the-theme }",
        27,
        36,
        _SWAGGER_THEME_RECIPE,
        ["fastapi.docs-ui.swagger-parameters.nested-theme"],
        ["swagger-html"],
        _UI_HTTP_BODY,
        (
            "The selected response bytes contain the nested syntaxHighlight theme option. "
            "No browser color rendering or other theme values are sampled."
        ),
        _SWAGGER_RATIONALE,
    ),
    (_CONFIGURE_SWAGGER, "change-default-swagger-ui-parameters"): _workflow(
        "Change Default Swagger UI Parameters { #change-default-swagger-ui-parameters }",
        37,
        50,
        _SWAGGER_OVERRIDE_RECIPE,
        ["fastapi.docs-ui.swagger-parameters.override-default"],
        ["swagger-html"],
        _UI_HTTP_BODY,
        (
            "The response bytes expose one deepLinking override and the generated defaults "
            "selected by the workload. This is not an exhaustive inventory of parameters or "
            "override combinations."
        ),
        _SWAGGER_RATIONALE,
    ),
    (_CONFIGURE_SWAGGER, "other-swagger-ui-parameters"): _excluded(
        "Other Swagger UI Parameters { #other-swagger-ui-parameters }",
        51,
        54,
        (
            "This pinned span points readers to Swagger's external configuration reference "
            "without declaring an additional FastAPI option or example "
            "(docs/en/docs/how-to/configure-swagger-ui.md:51-54)."
        ),
        (
            "The external Swagger UI documentation owns the list and behavior of its other "
            "JavaScript options. FastAPI-specific parameter serialization is reviewed under "
            "the neighboring mapped examples."
        ),
    ),
    (_CONFIGURE_SWAGGER, "javascript-only-settings"): _workflow(
        "JavaScript-only settings { #javascript-only-settings }",
        55,
        70,
        _SWAGGER_DEFAULT_RECIPE,
        ["fastapi.docs-ui.swagger-parameters.default-config"],
        ["swagger-html"],
        _UI_HTTP_BODY,
        (
            "The generated HTML response includes FastAPI's JavaScript bootstrap presets as "
            "source bytes. It does not accept arbitrary Python-supplied JavaScript objects, "
            "execute the script, or validate a browser override."
        ),
        _SWAGGER_RATIONALE,
    ),
    (_CONDITIONAL_OPENAPI, "conditional-openapi"): _workflow(
        "Conditional OpenAPI { #conditional-openapi }",
        1,
        56,
        _CONDITIONAL_RECIPE,
        ["fastapi.atlas-openapi-tutorial.conditional-hidden-docs"],
        ["hidden-openapi", "hidden-swagger-ui", "hidden-redoc"],
        ["http.status"],
        (
            "The selected actions observe hidden OpenAPI, Swagger, and ReDoc route statuses "
            "for a mounted app configured with an empty OpenAPI URL. The page's Pydantic "
            "Settings parsing and environment-variable/server process are outside this case."
        ),
        (
            "The pinned page's server-visible route behavior is conditional on FastAPI's "
            "openapi_url, docs_url, and redoc_url configuration "
            "(docs/en/docs/how-to/conditional-openapi.md:26-50; "
            "fastapi/applications.py:881-890, 1105-1158). The ASGI case uses an app with "
            "openapi_url='' and docs_url/redoc_url disabled. Starlette 1.6.0 owns generic "
            "mounted routing and 404 dispatch."
        ),
    ),
    (_CONDITIONAL_OPENAPI, "about-security-apis-and-docs"): _excluded(
        "About security, APIs, and docs { #about-security-apis-and-docs }",
        5,
        25,
        (
            "The pinned section gives security advice and explains that hiding API docs does "
            "not remove path operations (docs/en/docs/how-to/conditional-openapi.md:5-25). "
            "It defines no permission, dependency, authentication, or OpenAPI runtime input."
        ),
        (
            "The section's model design, permission, password storage, cryptography, and "
            "scope recommendations are application security policy. They are not behavior "
            "implemented by this FastAPI docs configuration page."
        ),
    ),
    (_GENERATE_CLIENTS, "generating-sdks"): _workflow(
        "Generating SDKs { #generating-sdks }",
        1,
        192,
        _CLIENT_VERSION_RECIPE,
        ["fastapi.docs.ui-clients.openapi-version-for-generators"],
        ["openapi-version"],
        _OPENAPI_VERSION,
        (
            "The selected action observes FastAPI's OpenAPI version field, one item the page "
            "says SDK tools consume. It does not generate an SDK, test a generator, compile "
            "TypeScript, or establish client runtime behavior."
        ),
        _OPENAPI_VERSION_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "open-source-sdk-generators"): _workflow(
        "Open Source SDK Generators { #open-source-sdk-generators }",
        9,
        22,
        _CLIENT_VERSION_RECIPE,
        ["fastapi.docs.ui-clients.openapi-version-for-generators"],
        ["openapi-version"],
        _OPENAPI_VERSION,
        (
            "The action observes the server schema version that the section says SDK "
            "generators must support. It does not invoke OpenAPI Generator, Hey API, "
            "OpenAPI.Tools, or verify their version support."
        ),
        _OPENAPI_VERSION_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "create-a-typescript-sdk"): _workflow(
        "Create a TypeScript SDK { #create-a-typescript-sdk }",
        23,
        78,
        _CLIENT_BASIC_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial001.client-requests-and-openapi"
        ],
        ["create-item", "list-items", "openapi-schema"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The actions exercise the documented API requests and selected OpenAPI path/model "
            "data used as generator input. They do not run Hey API or inspect generated "
            "TypeScript, IDE suggestions, or client-side validation."
        ),
        _CLIENT_BASIC_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "api-docs"): _workflow(
        "API Docs { #api-docs }",
        31,
        42,
        _CLIENT_BASIC_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial001.client-requests-and-openapi"
        ],
        ["openapi-schema"],
        _OPENAPI_PATHS,
        (
            "The selected pointers inspect the documented request/response paths and model "
            "components from /openapi.json. The action does not fetch or render /docs in a "
            "browser."
        ),
        _CLIENT_BASIC_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "hey-api"): _workflow(
        "Hey API { #hey-api }",
        43,
        54,
        _CLIENT_VERSION_RECIPE,
        ["fastapi.docs.ui-clients.openapi-version-for-generators"],
        ["openapi-version"],
        _OPENAPI_VERSION,
        (
            "The selected pointer observes only FastAPI's OpenAPI version value presented as "
            "input to the named tool. The npx command and generated client files are external "
            "and are not run."
        ),
        _OPENAPI_VERSION_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "fastapi-app-with-tags"): _workflow(
        "FastAPI App with Tags { #fastapi-app-with-tags }",
        79,
        113,
        _CLIENT_TAGGED_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial002.tagged-client-requests-and-openapi"
        ],
        ["openapi-schema"],
        _OPENAPI_PATHS,
        (
            "The selected schema pointers expose tagged path operations and their model "
            "components. Service grouping in generated TypeScript is not observed."
        ),
        _CLIENT_TAGGED_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "client-method-names"): _workflow(
        "Client Method Names { #client-method-names }",
        100,
        113,
        _CLIENT_BASIC_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial001.client-requests-and-openapi"
        ],
        ["openapi-schema"],
        _OPENAPI_PATHS,
        (
            "The OpenAPI path objects supplied by the basic example include the server's "
            "operationId values that a generator can consume. The action does not observe "
            "generated method names or naming policy in a client."
        ),
        _CLIENT_BASIC_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "custom-operation-ids-and-better-method-names"): _workflow(
        "Custom Operation IDs and Better Method Names "
        "{ #custom-operation-ids-and-better-method-names }",
        114,
        177,
        _CLIENT_IDS_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial003.custom-operation-ids"
        ],
        ["openapi-operation-ids"],
        _OPENAPI_PATHS,
        (
            "The selected OpenAPI pointers expose the custom operationId values produced by "
            "the documented FastAPI callback. They do not establish the client generator's "
            "method names or generated source."
        ),
        _CLIENT_IDS_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "custom-generate-unique-id-function"): _workflow(
        "Custom Generate Unique ID Function { #custom-generate-unique-id-function }",
        122,
        133,
        _CLIENT_IDS_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial003.custom-operation-ids"
        ],
        ["openapi-operation-ids"],
        _OPENAPI_PATHS,
        (
            "The action observes the operationId fields returned from the documented custom "
            "generate_unique_id_function. It does not cover missing tags, collisions, or "
            "generated client method output."
        ),
        _CLIENT_IDS_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "generate-a-typescript-client-with-custom-operation-ids"): _workflow(
        "Generate a TypeScript Client with Custom Operation IDs "
        "{ #generate-a-typescript-client-with-custom-operation-ids }",
        134,
        141,
        _CLIENT_IDS_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial003.custom-operation-ids"
        ],
        ["openapi-operation-ids"],
        _OPENAPI_PATHS,
        (
            "The selected action observes the custom OpenAPI operationId input to the "
            "external client generator only. It does not execute that generator or claim "
            "its TypeScript output."
        ),
        _CLIENT_IDS_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "preprocess-the-openapi-specification-for-the-client-generator"): _workflow(
        "Preprocess the OpenAPI Specification for the Client Generator "
        "{ #preprocess-the-openapi-specification-for-the-client-generator }",
        142,
        165,
        _CLIENT_IDS_RECIPE,
        [
            "fastapi.test.test-tutorial-test-generate-clients-test-tutorial003.custom-operation-ids"
        ],
        ["openapi-operation-ids"],
        _OPENAPI_PATHS,
        (
            "The selected OpenAPI pointers show the server-produced operationIds before the "
            "documented user script modifies a saved file. The Python/Node file transformation "
            "and its output are not part of this FastAPI case."
        ),
        _CLIENT_IDS_RATIONALE,
    ),
    (_GENERATE_CLIENTS, "generate-a-typescript-client-with-the-preprocessed-openapi"): _excluded(
        "Generate a TypeScript Client with the Preprocessed OpenAPI "
        "{ #generate-a-typescript-client-with-the-preprocessed-openapi }",
        166,
        177,
        (
            "The pinned section runs the Hey API CLI with a locally preprocessed openapi.json "
            "and describes the generated client output "
            "(docs/en/docs/advanced/generate-clients.md:166-177)."
        ),
        (
            "The consumed file has already been modified by the application-side preprocessing "
            "script, and client source generation belongs to the external SDK tool. The section "
            "adds no FastAPI route or OpenAPI generation behavior."
        ),
    ),
    (_GENERATE_CLIENTS, "benefits"): _excluded(
        "Benefits { #benefits }",
        178,
        192,
        (
            "The pinned section describes client autocomplete, inline diagnostics, and TypeScript "
            "build feedback from generated code "
            "(docs/en/docs/advanced/generate-clients.md:178-192)."
        ),
        (
            "IDE completion and compile-time mismatch detection belong to the generated client, "
            "editor, language service, and compiler. No FastAPI or ASGI operation is independently "
            "observable in this section."
        ),
    ),
}
