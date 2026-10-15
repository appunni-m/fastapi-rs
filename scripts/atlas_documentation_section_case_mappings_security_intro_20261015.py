"""Reviewed section mappings for the introductory FastAPI security pages."""

_SCHEMES = "tests/fixtures/input-recipes/parity/docs-security-schemes.yaml"
_BEARER = "tests/fixtures/input-recipes/parity/security-dependencies.yaml"
_CURRENT_USER = "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml"
_HTTP_BASIC = "tests/fixtures/input-recipes/parity/http-basic.yaml"

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_OPENAPI_SCHEMES = [
    "docs.response.body.bytes",
    "docs.response.status",
    "http.body.bytes",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.security",
]
_OPENAPI_BEARER = [
    "docs.response.headers",
    "docs.response.status",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.security",
]
_OPENAPI_BASIC = [
    "docs.response.headers",
    "docs.response.status",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.security",
]
_CURRENT_USER_ALL = [
    "docs.response.status",
    "http.body.bytes",
    "http.headers.ordered",
    "http.status",
    "openapi.document",
    "openapi.paths",
    "openapi.security",
]


def _workflow(
    recipe,
    heading,
    start,
    end,
    case_ids,
    actions,
    selectors,
    scope_note,
    rationale,
):
    mapping = {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": case_ids,
        "observation_selectors": selectors,
        "scope_note": scope_note,
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


DOC_SECTION_CASE_MAPPINGS_SECURITY_INTRO_20261015 = {
    ("tutorial/security/index.md", "security"): _excluded(
        "Security { #security }",
        1,
        106,
        (
            "This is an overview heading spanning standards terminology, OpenAPI, and the "
            "FastAPI utilities subsection. The individual utility sample is mapped on its "
            "child section; the parent adds no single independent input."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L1-L106. Its "
            "introductory generalizations do not select a distinct FastAPI operation; the "
            "query/cookie API-key cases are reviewed on the exact child heading."
        ),
    ),
    ("tutorial/security/index.md", "in-a-hurry"): _excluded(
        "In a hurry? { #in-a-hurry }",
        13,
        16,
        "This section only directs readers to later chapters and defines no executable input.",
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L13-L16; this is "
            "navigation prose."
        ),
    ),
    ("tutorial/security/index.md", "oauth2"): _excluded(
        "OAuth2 { #oauth2 }",
        17,
        40,
        (
            "This section describes OAuth2 as a standard and mentions third-party login and "
            "HTTPS. It contains no FastAPI configuration or ASGI input."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L17-L40. OAuth2 "
            "protocol concepts and third-party identity-provider behavior are not "
            "FastAPI-owned runtime behavior."
        ),
    ),
    ("tutorial/security/index.md", "oauth-1"): _excluded(
        'OAuth 1 { #oauth-1 }',
        27,
        40,
        (
            "The subsection compares the OAuth 1 and OAuth2 specifications and discusses "
            "HTTPS; it selects no FastAPI security utility or request."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L27-L40; these are "
            "standards notes."
        ),
    ),
    ("tutorial/security/index.md", "openid-connect"): _excluded(
        "OpenID Connect { #openid-connect }",
        41,
        58,
        (
            "This section describes OpenID Connect and an identity-provider use case; no "
            "FastAPI dependency, route, or provider interaction is selected."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L41-L58. OpenID "
            "Connect protocol and external identity-provider behavior are outside the "
            "FastAPI-owned runtime sample."
        ),
    ),
    ("tutorial/security/index.md", "openid-not-openid-connect"): _excluded(
        'OpenID (not "OpenID Connect") { #openid-not-openid-connect }',
        51,
        58,
        (
            "This subsection distinguishes OpenID terminology from OpenID Connect and "
            "selects no FastAPI input or operation."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L51-L58; this is "
            "standards prose."
        ),
    ),
    ("tutorial/security/index.md", "openapi"): _workflow(
        _SCHEMES,
        "OpenAPI { #openapi }",
        59,
        99,
        ["fastapi.docs.security-schemes.query-api-key"],
        ["query-key-openapi"],
        _OPENAPI_SCHEMES,
        (
            "The selected OpenAPI request observes the QueryApiKey scheme and the query-key "
            "operation's security pointer, plus the response and selected OpenAPI projections. "
            "It does not cover the whole OpenAPI standard, other scheme families, browser docs, "
            "or external OAuth flows."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L59-L99. FastAPI "
            "0.141.1 at 95f8322 builds API-key security metadata in "
            "fastapi/security/api_key.py#L55-L68, #L134-L145 and projects security "
            "dependencies in fastapi/openapi/utils.py#L99-L156. The exact case cites this "
            "documentation page; Starlette 1.6.0 at 4f250d6 provides generic ASGI response "
            "transport in starlette/responses.py#L163-L171."
        ),
    ),
    ("tutorial/security/index.md", "fastapi-utilities"): _workflow(
        _SCHEMES,
        "**FastAPI** utilities { #fastapi-utilities }",
        100,
        106,
        ["fastapi.docs.security-schemes.cookie-api-key"],
        None,
        _OPENAPI_SCHEMES,
        (
            "This case samples one APIKeyCookie dependency, its cookie-key route response, "
            "and its OpenAPI security entry. It does not establish behavior for every "
            "FastAPI security utility or run the browser documentation UI."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/index.md#L100-L106. The "
            "cookie input is extracted by FastAPI 0.141.1 in "
            "fastapi/security/api_key.py#L235-L242, #L267-L320; OpenAPI security projection "
            "is in fastapi/openapi/utils.py#L99-L156. The recipe already carries this exact "
            "documentation source. Generic ASGI response transport is Starlette 1.6.0 at "
            "4f250d6, starlette/responses.py#L163-L171."
        ),
    ),
    ("tutorial/security/first-steps.md", "security-first-steps"): _excluded(
        "Security - First Steps { #security-first-steps }",
        1,
        203,
        (
            "This parent heading groups an OAuth2 dependency sample, CLI/server startup, "
            "interactive docs, and password-flow discussion. The executable Bearer and "
            "OpenAPI behaviors are mapped on their child sections."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L1-L203. "
            "FastAPI-owned dependency and OpenAPI behavior is mapped below; `fastapi dev` "
            "and browser interaction are not selected by the linked ASGI workflows."
        ),
    ),
    ("tutorial/security/first-steps.md", "create-main-py"): _workflow(
        _BEARER,
        "Create `main.py` { #create-main-py }",
        19,
        24,
        ["fastapi.docs.security.bearer-required-valid"],
        ["required-bearer-provided"],
        _HTTP,
        (
            "The selected request sends a non-empty Bearer value to a protected operation "
            "and observes only its HTTP response. The workload uses `/records/rec-91`, "
            "`session/token`, and a declared scope rather than the page snippet's `/items/` "
            "and `token`; it does not issue or validate a token."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L19-L24. "
            "FastAPI 0.141.1 extracts an opaque Bearer parameter in "
            "fastapi/security/oauth2.py#L536-L544 and injects dependencies in "
            "fastapi/dependencies/utils.py#L619-L655. The recipe's source_evidence includes "
            "this exact page. Starlette 1.6.0 at 4f250d6 owns generic response transport "
            "through starlette/responses.py#L163-L171."
        ),
    ),
    ("tutorial/security/first-steps.md", "run-it"): _excluded(
        "Run it { #run-it }",
        25,
        54,
        (
            "This section describes optional dependency installation and starting a server "
            "with the FastAPI CLI or Uvicorn. The selected recipe invokes an ASGI app "
            "directly and does not test CLI/process startup."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L25-L54. "
            "Process launching and package installation are not FastAPI ASGI behavior "
            "selected by the current security workflows."
        ),
    ),
    ("tutorial/security/first-steps.md", "check-it"): _workflow(
        _BEARER,
        "Check it { #check-it }",
        55,
        88,
        ["fastapi.docs.security.openapi"],
        ["inspect-security-schemes-and-operations"],
        _OPENAPI_BEARER,
        (
            "The request observes selected generated security-scheme and operation-security "
            "OpenAPI pointers. It does not request `/docs`, run Swagger UI, open a browser, "
            "or exercise the authorization button."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L55-L88. "
            "FastAPI 0.141.1 gathers dependency security declarations in "
            "fastapi/openapi/utils.py#L99-L156 and serves the generated document; the "
            "recipe source_evidence includes this page. Starlette 1.6.0 at 4f250d6 handles "
            "generic ASGI HTTP responses in starlette/responses.py#L163-L171."
        ),
    ),
    ("tutorial/security/first-steps.md", "the-password-flow"): _excluded(
        "The `password` flow { #the-password-flow }",
        89,
        114,
        (
            "This section introduces the OAuth2 password flow as a protocol and explicitly "
            "says its token endpoint has not yet been created. The linked selected inputs "
            "cover Bearer extraction and OpenAPI metadata, not a password form or token "
            "issuance operation."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L89-L114. "
            "FastAPI 0.141.1's OAuth2PasswordBearer records flow metadata at "
            "fastapi/security/oauth2.py#L433-L535; that metadata does not implement the "
            "external protocol or issue tokens."
        ),
    ),
    ("tutorial/security/first-steps.md", "fastapis-oauth2passwordbearer"): _workflow(
        _BEARER,
        "**FastAPI**'s `OAuth2PasswordBearer` { #fastapis-oauth2passwordbearer }",
        115,
        186,
        ["fastapi.docs.security.openapi"],
        ["inspect-security-schemes-and-operations"],
        _OPENAPI_BEARER,
        (
            "The selected OpenAPI action observes one declared OAuth2 password-flow scheme, "
            "its configured token URL and scope, and selected path security requirements. "
            "The input does not create that token endpoint, issue/validate tokens, integrate "
            "with a provider, or render browser docs."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L115-L186. "
            "FastAPI 0.141.1 stores tokenUrl/scopes on OAuth2PasswordBearer in "
            "fastapi/security/oauth2.py#L433-L535 and projects security dependencies in "
            "fastapi/openapi/utils.py#L99-L156. The selected recipe includes exact page "
            "source_evidence; its workload's declared token URL and scope differ from the "
            "tutorial snippet."
        ),
    ),
    ("tutorial/security/first-steps.md", "use-it"): _workflow(
        _BEARER,
        "Use it { #use-it }",
        169,
        186,
        ["fastapi.docs.security.bearer-required-valid"],
        ["required-bearer-provided"],
        _HTTP,
        (
            "The selected route receives an opaque Bearer parameter through a FastAPI "
            "dependency and returns its application-defined response. This is one "
            "successful request to a different workload path; it does not validate the "
            "token or exercise the browser documentation UI."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L169-L186. "
            "OAuth2PasswordBearer reads and returns the Bearer parameter in FastAPI 0.141.1 "
            "at fastapi/security/oauth2.py#L536-L544; dependency solving is in "
            "fastapi/dependencies/utils.py#L619-L655. The recipe cites this exact page."
        ),
    ),
    ("tutorial/security/first-steps.md", "what-it-does"): _workflow(
        _BEARER,
        "What it does { #what-it-does }",
        187,
        200,
        [
            "fastapi.docs.security.bearer-required-missing",
            "fastapi.docs.security.bearer-required-valid",
            "fastapi.docs.security.bearer-required-wrong-scheme",
        ],
        None,
        _HTTP,
        (
            "The three single-action cases sample one valid Bearer header, a missing header, "
            "and a non-Bearer scheme, observing response body bytes, ordered headers, and "
            "status. A token is treated as opaque input: neither token validity nor token "
            "issuance is tested, and no browser is involved."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L187-L200. "
            "FastAPI 0.141.1 parses the Authorization scheme and either returns its opaque "
            "parameter or raises the required-auth error in "
            "fastapi/security/oauth2.py#L536-L544. Each selected recipe case includes the "
            "exact documentation source; Starlette 1.6.0 at 4f250d6 carries generic HTTP "
            "response status, headers, and bytes in starlette/responses.py#L163-L171."
        ),
    ),
    ("tutorial/security/first-steps.md", "recap"): _excluded(
        "Recap { #recap }",
        201,
        203,
        (
            "This short recap summarizes the earlier dependency sample and adds no new "
            "input or behavior."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/first-steps.md#L201-L203; "
            "behavior is mapped above."
        ),
    ),
    ("tutorial/security/get-current-user.md", "get-current-user"): _excluded(
        "Get Current User { #get-current-user }",
        1,
        105,
        (
            "This page-level heading groups a Pydantic model, a user lookup helper, "
            "dependency injection, and summary prose. The independently sampled current-user "
            "dependency is mapped on its specific child sections."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L1-L105. "
            "The linked workload exercises one successful dependent route that returns an "
            "application-defined dict; it does not define the page's Pydantic User model or "
            "its fake lookup helper."
        ),
    ),
    ("tutorial/security/get-current-user.md", "create-a-user-model"): _excluded(
        "Create a user model { #create-a-user-model }",
        11,
        18,
        (
            "This section declares a Pydantic User model in application code. The linked "
            "current-user workload returns a dict and selects no Pydantic User model "
            "validation, serialization, or generated schema."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L11-L18 "
            "and includes the tutorial002 model snippet. The relevant input recipe's "
            "current-user workload instead returns `dict[str, str]`; it cannot support a "
            "claim about this model-specific behavior."
        ),
    ),
    ("tutorial/security/get-current-user.md", "create-a-get-current-user-dependency"): _workflow(
        _CURRENT_USER,
        "Create a `get_current_user` dependency { #create-a-get-current-user-dependency }",
        19,
        30,
        ["fastapi.docs.documentation-wave.dependencies-security.current-user"],
        ["dispatch"],
        _HTTP,
        (
            "The selected successful request passes a Bearer parameter through an "
            "application-defined dependency chain and observes the response. The workload "
            "checks a fixed reader token and returns a dict; it does not decode a real token "
            "or construct the tutorial's Pydantic User."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L19-L30. "
            "FastAPI 0.141.1 returns the opaque Bearer parameter in "
            "fastapi/security/oauth2.py#L536-L544 and solves nested dependencies in "
            "fastapi/dependencies/utils.py#L619-L655. The selected case source_evidence "
            "names this exact page."
        ),
    ),
    ("tutorial/security/get-current-user.md", "get-the-user"): _excluded(
        "Get the user { #get-the-user }",
        31,
        36,
        (
            "This section's distinguishing behavior is the example application's fake "
            "token-to-user lookup and Pydantic User construction. The linked workload "
            "returns an app-defined dict after a fixed-token check and does not implement "
            "that helper."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L31-L36 "
            "and references tutorial002_an_py310.py. The selected current-user case has no "
            "token decoder, user record lookup, or Pydantic User output to attribute to "
            "FastAPI."
        ),
    ),
    ("tutorial/security/get-current-user.md", "inject-the-current-user"): _workflow(
        _CURRENT_USER,
        "Inject the current user { #inject-the-current-user }",
        37,
        62,
        ["fastapi.docs.documentation-wave.dependencies-security.current-user"],
        None,
        _CURRENT_USER_ALL,
        (
            "The case selects one successful `/users/me` dependency dispatch and the "
            "operation's generated security pointers. Its dependent returns an "
            "application-defined dict, not the documented Pydantic User; the OpenAPI "
            "projection contains no User model schema. It does not test alternate "
            "dependables or browser interaction."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L37-L62. "
            "FastAPI 0.141.1 solves dependency inputs in "
            "fastapi/dependencies/utils.py#L619-L655 and projects security dependencies in "
            "fastapi/openapi/utils.py#L99-L156. The exact recipe case cites this page; "
            "Starlette 1.6.0 at 4f250d6 provides generic response transport in "
            "starlette/responses.py#L163-L171."
        ),
    ),
    ("tutorial/security/get-current-user.md", "other-models"): _workflow(
        _CURRENT_USER,
        "Other models { #other-models }",
        63,
        78,
        ["fastapi.docs.documentation-wave.dependencies-security.current-user"],
        ["dispatch"],
        _HTTP,
        (
            "The selected response demonstrates one injected dict from one dependency. It "
            "does not establish compatibility for every model, class, database object, or "
            "authentication mechanism listed in the prose."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L63-L78. "
            "FastAPI 0.141.1 resolves the selected dependency graph in "
            "fastapi/dependencies/utils.py#L619-L655; the exact current-user recipe case "
            "cites this page and returns only an app-defined dict."
        ),
    ),
    ("tutorial/security/get-current-user.md", "code-size"): _workflow(
        _CURRENT_USER,
        "Code size { #code-size }",
        79,
        96,
        ["fastapi.docs.documentation-wave.dependencies-security.current-user"],
        ["dispatch"],
        _HTTP,
        (
            "The case samples a single protected path operation using one dependency chain. "
            "It does not establish the prose's thousand-endpoint scale, dependency reuse "
            "across many routes, or performance claims."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L79-L96. "
            "FastAPI 0.141.1's dependency solver is in "
            "fastapi/dependencies/utils.py#L619-L655; the selected case contains one route "
            "and one successful request, so only that bounded composition is mapped."
        ),
    ),
    ("tutorial/security/get-current-user.md", "recap"): _excluded(
        "Recap { #recap }",
        97,
        105,
        (
            "The recap summarizes the previously mapped current-user dependency and points "
            "to the future username/password endpoint; it adds no selected runtime input."
        ),
        (
            "The pinned page is docs/en/docs/tutorial/security/get-current-user.md#L97-L105; "
            "the referenced behavior is mapped above."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "http-basic-auth"): _workflow(
        _HTTP_BASIC,
        "HTTP Basic Auth { #http-basic-auth }",
        1,
        107,
        ["fastapi.advanced.security.http-basic.missing"],
        ["missing-basic-credentials"],
        _HTTP,
        (
            "The selected request omits Authorization and observes FastAPI HTTPBasic's "
            "401 response with its Basic challenge. This covers the ASGI challenge only; "
            "the text's integrated browser prompt and automatic browser retry are not run."
        ),
        (
            "The pinned page is docs/en/docs/advanced/security/http-basic-auth.md#L1-L107. "
            "FastAPI 0.141.1's HTTPBasic emits the realm-aware challenge and handles a "
            "missing header in fastapi/security/http.py#L197-L219. The selected case cites "
            "this page; Starlette 1.6.0 at 4f250d6 carries generic exception responses in "
            "starlette/middleware/exceptions.py#L18-L47 and "
            "starlette/responses.py#L163-L171."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "simple-http-basic-auth"): _workflow(
        _HTTP_BASIC,
        "Simple HTTP Basic Auth { #simple-http-basic-auth }",
        15,
        28,
        ["fastapi.advanced.security.http-basic.valid"],
        ["valid-basic-credentials"],
        _HTTP,
        (
            "The selected Basic request returns the parsed username and password fields "
            "through the sample route. It does not exercise browser prompts or any "
            "username/password authorization policy."
        ),
        (
            "The pinned page is docs/en/docs/advanced/security/http-basic-auth.md#L15-L28. "
            "FastAPI 0.141.1 defines HTTPBasicCredentials and parses a Basic header into "
            "that model in fastapi/security/http.py#L16-L27 and #L202-L219. The exact "
            "recipe case cites this page; generic ASGI responses use Starlette 1.6.0 at "
            "4f250d6, starlette/responses.py#L163-L171."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "check-the-username"): _workflow(
        _HTTP_BASIC,
        "Check the username { #check-the-username }",
        29,
        107,
        ["fastapi.advanced.security.http-basic.valid"],
        ["valid-basic-credentials"],
        _HTTP,
        (
            "Partial mapping: the request confirms FastAPI extracts the supplied Basic "
            "username/password and delivers them to an application route. The workload does "
            "not execute this page's `secrets.compare_digest()` check, reject wrong "
            "credentials, or test the resulting application-authored HTTPException branch."
        ),
        (
            "The pinned page is docs/en/docs/advanced/security/http-basic-auth.md#L29-L107. "
            "FastAPI 0.141.1 performs credential parsing in fastapi/security/http.py#L202-L219; "
            "the compare_digest and credential policy appear in the user-owned "
            "docs_src/security/tutorial007_an_py310.py#L12-L30 and are absent from "
            "tests/fixtures/workloads/http_basic.py. The valid case cites the exact page."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "timing-attacks"): _excluded(
        "Timing Attacks { #timing-attacks }",
        55,
        102,
        (
            "This section explains a threat model and the timing behavior of application "
            "string comparisons. The selected inputs do not run those comparisons or "
            "measure elapsed time."
        ),
        (
            "The pinned page is docs/en/docs/advanced/security/http-basic-auth.md#L55-L102. "
            "The examples and `secrets.compare_digest()` use are application/Python "
            "standard-library behavior in docs_src/security/tutorial007_an_py310.py; no "
            "timing-security property is attributed to FastAPI or asserted by this mapping."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "fix-it-with-secrets-compare-digest"): _excluded(
        "Fix it with `secrets.compare_digest()` { #fix-it-with-secrets-compare-digest }",
        95,
        102,
        (
            "The section's claimed comparison-time property is implemented by Python's "
            "standard-library `secrets.compare_digest()` in user application code. The "
            "HTTPBasic workload does not call it or measure timing."
        ),
        (
            "The pinned page is docs/en/docs/advanced/security/http-basic-auth.md#L95-L102. "
            "The call is in docs_src/security/tutorial007_an_py310.py#L12-L24; FastAPI "
            "only supplies parsed credentials, and no timing-security claim is selected."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "return-the-error"): _workflow(
        _HTTP_BASIC,
        "Return the error { #return-the-error }",
        103,
        107,
        ["fastapi.advanced.security.http-basic.missing"],
        ["missing-basic-credentials"],
        _HTTP,
        (
            "Partial mapping: the selected action observes FastAPI HTTPBasic's built-in "
            "missing-header 401 and Basic challenge, which share the documented status and "
            "challenge shape. It does not send wrong username/password values or exercise "
            "the tutorial's app-authored HTTPException, detail, and custom header branch."
        ),
        (
            "The pinned page is docs/en/docs/advanced/security/http-basic-auth.md#L103-L107. "
            "The specific wrong-credential HTTPException is constructed by the user example "
            "in docs_src/security/tutorial007_an_py310.py#L26-L30, while FastAPI's "
            "missing-header Basic challenge is in fastapi/security/http.py#L197-L219. The "
            "existing missing-credentials case cites the exact page and provides only the "
            "limited response-shape observation stated here."
        ),
    ),
}
