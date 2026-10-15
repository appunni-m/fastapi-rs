"""Reviewed section mappings for the FastAPI WebSocket and OAuth2 docs."""


def _w(heading, start, end, recipe, cases, selectors, note, rationale, actions=None):
    row = {
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
        row["action_ids"] = actions
    return row


def _x(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


ECHO = "tests/fixtures/input-recipes/parity/websocket-echo.yaml"
ECHO_CASE = ["fastapi.websocket.echo-text"]
ECHO_ACTION = ["echo-text-session"]
ECHO_SELECTORS = ["websocket.event_order", "websocket.messages"]
WS_DEPS = "tests/fixtures/input-recipes/parity/atlas-testing-websocket-websockets-tutorial002.yaml"
WS_DEPS_CASE = ["fastapi.atlas-testing.websocket-tutorial002"]
WS_DEPS_ACTIONS = [
    "cookie-plain",
    "cookie-annotated",
    "query-token-plain",
    "query-token-annotated",
    "query-token-q-plain",
    "query-token-q-annotated",
    "no-credentials-plain",
    "no-credentials-annotated",
    "invalid-query-plain",
    "invalid-query-annotated",
]
WS_DEPS_SELECTORS = ["websocket.close_code", "websocket.event_order", "websocket.messages"]
OAUTH_FORM = "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml"
OAUTH_FORM_CASE = ["fastapi.docs.documentation-wave.dependencies-security.simple-oauth2-token-form"]
OAUTH_SELECTORS = ["http.body.bytes", "http.headers.ordered", "http.status"]
OAUTH_INACTIVE = (
    "tests/fixtures/input-recipes/parity/security-oauth2-inactive-user-source-wave.yaml"
)
OAUTH_INACTIVE_CASE = ["fastapi.security.tutorial-003.oauth2-inactive-user"]

DOC_SECTION_CASE_MAPPINGS_WAVE_L = {
    ("advanced/websockets.md", "websockets"): _x(
        "WebSockets { #websockets }",
        1,
        186,
        "The page title aggregates independently reviewed examples and adds no separate operation.",
        "Concrete claims map to anchored child sections; the page-level mapping remains partial.",
    ),
    ("advanced/websockets.md", "install-websockets"): _x(
        "Install `websockets` { #install-websockets }",
        5,
        18,
        "The section installs a separate client package, not FastAPI server behavior.",
        "The commands target the client environment; server behavior is mapped separately.",
    ),
    ("advanced/websockets.md", "websockets-client"): _w(
        "WebSockets client { #websockets-client }",
        19,
        42,
        ECHO,
        ECHO_CASE,
        ECHO_SELECTORS,
        (
            "The server action observes one accepted connection and two text "
            "exchanges; it does not run the HTML/JavaScript client or browser."
        ),
        (
            "The route is FastAPI integration; client code and rendering belong to "
            "the external browser surface."
        ),
        ECHO_ACTION,
    ),
    ("advanced/websockets.md", "in-production"): _w(
        "In production { #in-production }",
        21,
        42,
        ECHO,
        ECHO_CASE,
        ECHO_SELECTORS,
        (
            "The embedded FastAPI server route is exercised by one accepted echo "
            "session; production-client recommendations, HTML, and browser JavaScript "
            "are not run."
        ),
        (
            "The referenced server example uses FastAPI WebSocket integration; the "
            "external client choices are outside this observation."
        ),
        ECHO_ACTION,
    ),
    ("advanced/websockets.md", "create-a-websocket"): _w(
        "Create a `websocket` { #create-a-websocket }",
        43,
        56,
        ECHO,
        ECHO_CASE,
        ECHO_SELECTORS,
        (
            "The action samples FastAPI route integration through an accepted "
            "WebSocket and text echo; it does not assert import identity or the "
            "re-export's full API."
        ),
        "The input cites this page; generic connection mechanics belong to Starlette 1.6.0.",
        ECHO_ACTION,
    ),
    ("advanced/websockets.md", "await-for-messages-and-send-messages"): _w(
        "Await for messages and send messages { #await-for-messages-and-send-messages }",
        57,
        64,
        ECHO,
        ECHO_CASE,
        ECHO_SELECTORS,
        (
            "The action sends and observes two text messages on one connection; "
            "binary/JSON helper semantics are generic Starlette behavior."
        ),
        "The page's server example is sampled with ordered WebSocket observations.",
        ECHO_ACTION,
    ),
    ("advanced/websockets.md", "try-it"): _w(
        "Try it { #try-it }",
        65,
        98,
        "tests/fixtures/input-recipes/parity/websockets-cli-startup.yaml",
        ["fastapi.cli.process.websockets-startup-readiness"],
        ["http.body.bytes", "http.status", "process.exit_code"],
        (
            "Runs the documented fastapi dev command with a WebSocket app and "
            "observes startup plus HTTP readiness; WebSocket exchanges are mapped in "
            "route/message sections, browser UI is not run."
        ),
        (
            "CLI startup is process behavior; browser controls and images are "
            "presentation/client behavior."
        ),
    ),
    ("advanced/websockets.md", "using-depends-and-others"): _w(
        "Using `Depends` and others { #using-depends-and-others }",
        99,
        152,
        WS_DEPS,
        WS_DEPS_CASE,
        WS_DEPS_SELECTORS,
        (
            "Cookie/query variants, accepted messages, and policy closes are "
            "observed. Header, Security scopes, and explicit Path markers are not "
            "covered; the test named with-header sends a query parameter."
        ),
        (
            "These docs-example actions expose FastAPI dependency and parameter "
            "binding; generic framing remains Starlette-owned."
        ),
        WS_DEPS_ACTIONS,
    ),
    ("advanced/websockets.md", "try-the-websockets-with-dependencies"): _w(
        "Try the WebSockets with dependencies { #try-the-websockets-with-dependencies }",
        122,
        152,
        WS_DEPS,
        WS_DEPS_CASE,
        WS_DEPS_SELECTORS,
        (
            "The actions exercise server-side cookie/query dependencies and "
            "WebSocket outcomes, not browser UI or Header/Security parameters."
        ),
        "Only FastAPI WebSocket dependency integration is claimed.",
        WS_DEPS_ACTIONS,
    ),
    ("advanced/websockets.md", "handling-disconnections-and-multiple-clients"): _w(
        (
            "Handling disconnections and multiple clients { "
            "#handling-disconnections-and-multiple-clients }"
        ),
        153,
        180,
        "tests/fixtures/input-recipes/parity/websockets-tutorial003-upstream-subset.yaml",
        ["fastapi.websockets.tutorial003.single-client-session"],
        ECHO_SELECTORS,
        (
            "The current input declares two clients, broadcast delivery, and a "
            "disconnect; it observes app-owned manager output plus WebSocket events. "
            "No matching pinned Oracle result exists yet."
        ),
        (
            "This maps the documented integration scenario and integer path binding; "
            "connection-manager and broadcast policy are application-owned."
        ),
        ["two-client-broadcast-and-disconnect"],
    ),
    ("advanced/websockets.md", "more-info"): _x(
        "More info { #more-info }",
        181,
        186,
        "This section links to Starlette's generic WebSocket API and class-based endpoint docs.",
        (
            "FastAPI's integration is scoped elsewhere; Starlette 1.6.0 owns the "
            "referenced generic contracts."
        ),
    ),
    ("tutorial/security/simple-oauth2.md", "simple-oauth2-with-password-and-bearer"): _x(
        "Simple OAuth2 with Password and Bearer { #simple-oauth2-with-password-and-bearer }",
        1,
        289,
        "The page title aggregates independently reviewed examples and adds no separate operation.",
        (
            "Form parsing and authentication map to child sections; tutorial token "
            "logic is application-owned."
        ),
    ),
    ("tutorial/security/simple-oauth2.md", "get-the-username-and-password"): _w(
        "Get the `username` and `password` { #get-the-username-and-password }",
        5,
        46,
        OAUTH_FORM,
        OAUTH_FORM_CASE,
        OAUTH_SELECTORS,
        (
            "Submits valid form-encoded username/password and observes the response; "
            "this fixture also supplies its required tenant header and omits scope."
        ),
        (
            "The form dependency is FastAPI behavior; credential policy and response "
            "payload belong to the fixture app."
        ),
        ["dispatch"],
    ),
    ("tutorial/security/simple-oauth2.md", "scope"): _w(
        "`scope` { #scope }",
        21,
        46,
        "tests/fixtures/input-recipes/parity/simple-oauth2-form-scopes.yaml",
        ["fastapi.docs.simple-oauth2.form.scope-splitting"],
        ["http.body.bytes", "http.status"],
        (
            "Two form inputs observe parsed scopes for a space-separated value and "
            "an omitted scope field."
        ),
        (
            "FastAPI owns OAuth2PasswordRequestForm scope splitting; the fixture "
            "only returns parsed values."
        ),
        ["scope-present", "scope-absent"],
    ),
    ("tutorial/security/simple-oauth2.md", "code-to-get-the-username-and-password"): _w(
        "Code to get the `username` and `password` { #code-to-get-the-username-and-password }",
        47,
        152,
        OAUTH_FORM,
        OAUTH_FORM_CASE,
        OAUTH_SELECTORS,
        (
            "Exercises one valid username/password form dependency, not the "
            "example's fake database, hashing, or invalid-credential branches."
        ),
        "This partial mapping isolates FastAPI form binding from tutorial-owned credential policy.",
        ["dispatch"],
    ),
    ("tutorial/security/simple-oauth2.md", "oauth2passwordrequestform"): _w(
        "`OAuth2PasswordRequestForm` { #oauth2passwordrequestform }",
        51,
        86,
        OAUTH_FORM,
        OAUTH_FORM_CASE,
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
            "openapi.request_schema",
        ],
        (
            "Submits username/password and selects the /token request-body schema; "
            "optional scope/client inputs, the strict class, and missing/wrong "
            "grant-type branches are not exercised."
        ),
        (
            "The actions sample FastAPI form binding and request-schema projection "
            "without claiming every OAuth2 form option."
        ),
        ["dispatch", "openapi"],
    ),
    ("tutorial/security/simple-oauth2.md", "use-the-form-data"): _w(
        "Use the form data { #use-the-form-data }",
        87,
        104,
        OAUTH_FORM,
        OAUTH_FORM_CASE,
        OAUTH_SELECTORS,
        (
            "Binds submitted username/password through the form dependency; it does "
            "not expose parsed scopes."
        ),
        "FastAPI parses and injects the OAuth2 form fields; response content is fixture-owned.",
        ["dispatch"],
    ),
    ("tutorial/security/simple-oauth2.md", "check-the-password"): _x(
        "Check the password { #check-the-password }",
        105,
        152,
        (
            "This section describes fake user lookup, hashing, comparison, and "
            "Pydantic model construction owned by the tutorial app."
        ),
        "FastAPI form binding is mapped nearby; the credential policy is not a FastAPI contract.",
    ),
    ("tutorial/security/simple-oauth2.md", "password-hashing"): _x(
        "Password hashing { #password-hashing }",
        115,
        130,
        "The example's password hashing is application-owned security logic.",
        "The pinned span invokes no FastAPI API to compute or compare a hash.",
    ),
    ("tutorial/security/simple-oauth2.md", "why-use-password-hashing"): _x(
        "Why use password hashing { #why-use-password-hashing }",
        123,
        130,
        "This section is security rationale prose without independent FastAPI runtime behavior.",
        "The described hashing implementation is application logic and is separately excluded.",
    ),
    ("tutorial/security/simple-oauth2.md", "about-user-dict"): _x(
        "About `**user_dict` { #about-user-dict }",
        131,
        152,
        (
            "This section explains Python keyword argument expansion and Pydantic "
            "model construction in the tutorial app."
        ),
        "The syntax and UserInDB validation are outside FastAPI's runtime contract.",
    ),
    ("tutorial/security/simple-oauth2.md", "return-the-token"): _x(
        "Return the token { #return-the-token }",
        153,
        184,
        (
            "The access-token value, type, and issuance policy are chosen by the "
            "tutorial endpoint; FastAPI does not issue OAuth tokens."
        ),
        (
            "Generic response behavior is mapped elsewhere; this is not a distinct "
            "OAuth token service contract."
        ),
    ),
    ("tutorial/security/simple-oauth2.md", "update-the-dependencies"): _w(
        "Update the dependencies { #update-the-dependencies }",
        185,
        216,
        OAUTH_INACTIVE,
        OAUTH_INACTIVE_CASE,
        OAUTH_SELECTORS,
        (
            "Exercises valid Bearer syntax and the disabled-user path, not "
            "missing-token, wrong-scheme, active-user, or cleanup-order behavior."
        ),
        "FastAPI resolves the security dependency; the inactive-user 400 is raised by app code.",
        ["authenticated-inactive-user"],
    ),
    ("tutorial/security/simple-oauth2.md", "see-it-in-action"): _w(
        "See it in action { #see-it-in-action }",
        217,
        280,
        OAUTH_FORM,
        OAUTH_FORM_CASE,
        OAUTH_SELECTORS,
        (
            "Maps the direct /token request only. Swagger UI clicks and /docs "
            "rendering are not observed; /users/me actions map below."
        ),
        "The fixture samples the HTTP endpoint reached by authentication, not browser UI.",
        ["dispatch"],
    ),
    ("tutorial/security/simple-oauth2.md", "authenticate"): _w(
        "Authenticate { #authenticate }",
        221,
        236,
        OAUTH_FORM,
        OAUTH_FORM_CASE,
        OAUTH_SELECTORS,
        (
            "Posts valid credentials directly to /token without exercising Swagger "
            "UI authorization or /docs."
        ),
        (
            "The form request is FastAPI behavior; the browser authorization "
            "interface is not an endpoint observation."
        ),
        ["dispatch"],
    ),
    ("tutorial/security/simple-oauth2.md", "get-your-own-user-data"): _w(
        "Get your own user data { #get-your-own-user-data }",
        237,
        262,
        OAUTH_INACTIVE,
        OAUTH_INACTIVE_CASE,
        OAUTH_SELECTORS,
        (
            "Samples the documented active-user response and unauthenticated 401 "
            "directly over ASGI; it does not drive Swagger UI."
        ),
        (
            "The input covers FastAPI's security dependency boundary while keeping "
            "the account decision app-owned."
        ),
        ["authenticated-active-user", "missing-token"],
    ),
    ("tutorial/security/simple-oauth2.md", "inactive-user"): _w(
        "Inactive user { #inactive-user }",
        263,
        280,
        OAUTH_INACTIVE,
        OAUTH_INACTIVE_CASE,
        OAUTH_SELECTORS,
        (
            "Matches the disabled-user branch and exact HTTP response; the 400 and "
            "detail are produced by the example's HTTPException."
        ),
        (
            "Authentication dependency resolution is FastAPI-owned; the "
            "inactive-user rule is app-owned."
        ),
        ["authenticated-inactive-user"],
    ),
    ("tutorial/security/simple-oauth2.md", "recap"): _x(
        "Recap { #recap }",
        281,
        289,
        (
            "This recap restates form, token, and dependency examples without adding "
            "a separate behavior."
        ),
        (
            "Runtime claims map to earlier anchored sections; the recap and "
            "next-chapter link add no independent output."
        ),
    ),
}
