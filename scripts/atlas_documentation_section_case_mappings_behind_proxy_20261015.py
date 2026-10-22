"""Reviewed mappings for FastAPI's behind-a-proxy documentation sections."""

_PAGE = "advanced/behind-a-proxy.md"
_RECIPE = "tests/fixtures/input-recipes/parity/behind-proxy-sections-20261015.yaml"


def _workflow(heading, start, end, recipe, case, actions, selectors, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": [case],
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


_ROOT_PATH_CASE = "fastapi.docs.behind-proxy.root-path-scope"
_APP_ROOT_PATH_CASE = "fastapi.behind-proxy.tutorial002.app-root-path"
_APP_ROOT_PATH_RECIPE = "tests/fixtures/input-recipes/parity/fastapi-root-path-tutorial-review.yaml"
_NO_AUTO_SERVER_CASE = "fastapi.behind-proxy.tutorial004.openapi-servers"
_NO_AUTO_SERVER_RECIPE = (
    "tests/fixtures/input-recipes/parity/behind-proxy-tutorial004-upstream.yaml"
)

_ROOT_PATH_RATIONALE = (
    "FastAPI 0.157.0 preserves the server-provided ASGI root_path when the app option is "
    "empty; a configured non-empty FastAPI(root_path=...) still overwrites it, though "
    "that constructor parameter is deprecated (fastapi/applications.py:648-666, 938-946, "
    "1175-1178). The "
    "OpenAPI handler reads request scope root_path and conditionally prepends it to "
    "servers (fastapi/applications.py:1120-1135); Swagger and ReDoc handlers prepend it "
    "to their schema URLs (fastapi/applications.py:1136-1173). The pinned docs explain "
    "the stripped-prefix ASGI shape and the server-provided root_path "
    "(docs/en/docs/advanced/behind-a-proxy.md:98-163, 184-209), while the tutorial001 "
    "route and test demonstrate the request-visible root_path "
    "(docs_src/behind_a_proxy/tutorial001_py310.py:1-8; "
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial001.py:6-12). Each input is "
    "the ASGI scope after any external proxy/server processing; Starlette 1.6.0 owns "
    "generic route matching and response dispatch."
)

_SERVER_BOUNDARY = (
    "FastAPI 0.157.0's application consumes the ASGI scope and delegates to Starlette "
    "(fastapi/applications.py:1175-1184); it does not implement the "
    "forwarded-header trust policy described by the pinned docs "
    "(docs/en/docs/advanced/behind-a-proxy.md:9-13, 25-40, 65-97). The FastAPI CLI/server "
    "configuration, peer trust, header interpretation, and proxy rewriting are outside "
    "the FastAPI ASGI application contract and the Starlette 1.6.0 oracle."
)

_APP_ROOT_PATH_RATIONALE = (
    "FastAPI 0.157.0 still stores a non-empty FastAPI(root_path=...) value and writes it "
    "to the request scope, but marks the constructor parameter deprecated and emits a "
    "FastAPIDeprecationWarning (fastapi/applications.py:648-666, 938-946, 1175-1178). "
    "The current docs recommend `fastapi run --root-path` and explicitly label the app "
    "parameter deprecated (docs/en/docs/advanced/behind-a-proxy.md:192-215). The "
    "tutorial002 app and test retain the behavior and assert the deprecation warning "
    "(docs_src/behind_a_proxy/tutorial002_py310.py:1-8; "
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial002.py:1-16). The selected 0.157 "
    "recipe requests the app with a conflicting incoming root_path and observes the "
    "configured value and OpenAPI projection; it does not claim server startup behavior. "
    "Starlette 1.6.0 owns generic route matching and response dispatch."
)

DOC_SECTION_CASE_MAPPINGS_BEHIND_PROXY_20261015 = {
    (_PAGE, "behind-a-proxy"): _excluded(
        "Behind a Proxy { #behind-a-proxy }",
        1,
        437,
        (
            "This page-level heading is an overview spanning proxy trust, server flags, "
            "root_path, OpenAPI/docs URLs, local Traefik configuration, and mounted apps. "
            "The pinned page introduces those topics at lines 3-437; its independently "
            "observable FastAPI and shared-Starlette behavior is reviewed "
            "under the narrower anchored sections below."
        ),
        (
            "A page-wide workflow would conflate server/proxy process behavior with FastAPI "
            "application policy and Starlette routing. The source spans separate forwarded "
            "headers (docs/en/docs/advanced/behind-a-proxy.md:7-97), root_path and docs URLs "
            "(docs/en/docs/advanced/behind-a-proxy.md:98-224, "
            "docs/en/docs/advanced/behind-a-proxy.md:302-357), and mounting "
            "(docs/en/docs/advanced/behind-a-proxy.md:433-437). The child mappings preserve those "
            "ownership boundaries and select only the relevant ASGI actions."
        ),
    ),
    (_PAGE, "proxy-forwarded-headers"): _excluded(
        "Proxy Forwarded Headers { #proxy-forwarded-headers }",
        7,
        97,
        (
            "This parent section explains forwarded-header purpose and groups the server-flag "
            "and HTTPS-redirect child sections. Reading and trusting those headers is server "
            "behavior; the focused child mappings cover the app-visible redirect input and "
            "exclude server trust configuration "
            "(docs/en/docs/advanced/behind-a-proxy.md:9-13, 25-64, 65-97)."
        ),
        _SERVER_BOUNDARY,
    ),
    (_PAGE, "enable-proxy-forwarded-headers"): _excluded(
        "Enable Proxy Forwarded Headers { #enable-proxy-forwarded-headers }",
        25,
        40,
        (
            "The section configures `fastapi run --forwarded-allow-ips` and describes which "
            "remote peers the server trusts. It has no ASGI request action that distinguishes "
            "FastAPI application behavior."
        ),
        _SERVER_BOUNDARY,
    ),
    (_PAGE, "redirects-with-https"): _workflow(
        "Redirects with HTTPS { #redirects-with-https }",
        41,
        64,
        _RECIPE,
        "fastapi.docs.behind-proxy.https-slash-redirect",
        ["request-without-trailing-slash"],
        ["http.headers.ordered", "http.status"],
        (
            "The selected request sends `/items` with ASGI scheme `https` and host "
            "`example.com`, then observes the redirect status and headers. It samples URL "
            "construction from the scope only; it does not send X-Forwarded headers or claim "
            "the proxy's trust policy."
        ),
        (
            "The pinned docs example declares `/items/` and the FastAPI tutorial test sends "
            "an HTTPS-origin request to `/items` "
            "(docs_src/behind_a_proxy/tutorial001_01_py310.py:1-8; "
            "tests/test_tutorial/test_behind_a_proxy/test_tutorial001_01.py:5-16; "
            "docs/en/docs/advanced/behind-a-proxy.md:43-59). FastAPI "
            "uses Starlette routing for this redirect; Starlette 1.6.0 Router performs the "
            "slash retry and builds its URL from the ASGI scope (starlette/routing.py:704-718). "
            "Forwarded-header interpretation remains server-owned."
        ),
    ),
    (_PAGE, "how-proxy-forwarded-headers-work"): _excluded(
        "How Proxy Forwarded Headers Work { #how-proxy-forwarded-headers-work }",
        65,
        97,
        (
            "The diagram and prose describe the proxy adding X-Forwarded headers and the "
            "application server interpreting them. They specify no FastAPI application "
            "operation independently observable from an ASGI scope "
            "(docs/en/docs/advanced/behind-a-proxy.md:65-97)."
        ),
        _SERVER_BOUNDARY,
    ),
    (_PAGE, "proxy-with-a-stripped-path-prefix"): _workflow(
        "Proxy with a stripped path prefix { #proxy-with-a-stripped-path-prefix }",
        98,
        216,
        _RECIPE,
        _ROOT_PATH_CASE,
        [
            "read-app-root-path",
            "read-openapi-servers",
            "read-docs-ui",
        ],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        (
            "The ASGI input supplies `/api/v1` as root_path and requests the unprefixed "
            "application route, OpenAPI endpoint, and docs endpoint. The selected response "
            "shows FastAPI's root_path projection into the scope, OpenAPI servers, and Swagger "
            "URL. The recipe does not run a proxy or assert prefix stripping "
            "(docs/en/docs/advanced/behind-a-proxy.md:98-163)."
        ),
        _ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "providing-the-root-path"): _excluded(
        "Providing the `root_path` { #providing-the-root-path }",
        164,
        183,
        (
            "The section documents `fastapi run --root-path`, which creates the incoming "
            "ASGI scope. This mapping reviews the FastAPI application contract after scope "
            "construction; it does not run or observe the CLI/server process "
            "(docs/en/docs/advanced/behind-a-proxy.md:164-182)."
        ),
        (
            "The pinned docs assign `--root-path` to `fastapi run` server configuration "
            "(docs/en/docs/advanced/behind-a-proxy.md:164-182). FastAPI's application call "
            "consumes the already populated scope and overwrites root_path only when the app "
            "option is non-empty (fastapi/applications.py:648-666, 938-946, 1175-1178). "
            "This mapping excludes the CLI/server workflow and its scope construction."
        ),
    ),
    (_PAGE, "checking-the-current-root-path"): _workflow(
        "Checking the current `root_path` { #checking-the-current-root-path }",
        184,
        216,
        _APP_ROOT_PATH_RECIPE,
        "fastapi.applications.root-path.configured-over-incoming-scope",
        [
            "read-configured-root-path-through-middleware",
            "read-configured-root-path-openapi",
        ],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The recipe configures the deprecated FastAPI(root_path=...) option, supplies a "
            "different incoming scope root_path, and observes the app-visible value and "
            "OpenAPI server projection. It does not run `fastapi run` or claim server scope "
            "construction; the docs recommend the CLI option and label the constructor "
            "parameter deprecated (docs/en/docs/advanced/behind-a-proxy.md:184-216)."
        ),
        _APP_ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "about-proxies-with-a-stripped-path-prefix"): _excluded(
        "About proxies with a stripped path prefix { #about-proxies-with-a-stripped-path-prefix }",
        217,
        224,
        (
            "This section contrasts proxy configurations that strip or retain an external URL "
            "prefix. That transformation is performed before the application receives its "
            "ASGI scope and is not FastAPI library behavior "
            "(docs/en/docs/advanced/behind-a-proxy.md:217-224)."
        ),
        (
            "The pinned docs describe the two proxy path-rewrite choices before requests reach "
            "the application server (docs/en/docs/advanced/behind-a-proxy.md:217-224). "
            "FastAPI receives the resulting ASGI scope (fastapi/applications.py:1175-1178); "
            "the proxy's external URL and rewrite are not application behavior."
        ),
    ),
    (_PAGE, "testing-locally-with-traefik"): _excluded(
        "Testing locally with Traefik { #testing-locally-with-traefik }",
        225,
        357,
        (
            "This parent section instructs the reader to configure and run Traefik and Uvicorn. "
            "Its process, port, and path-rewrite behavior is external; the child response and "
            "docs-URL effects are reviewed independently "
            "(docs/en/docs/advanced/behind-a-proxy.md:225-301, 302-357)."
        ),
        (
            "The pinned example configures Traefik's stripPrefix middleware, ports, and the "
            "Uvicorn command as external processes "
            "(docs/en/docs/advanced/behind-a-proxy.md:225-301). Those are not FastAPI "
            "application actions; the independently observable app and docs URL effects in "
            "the following sections are mapped at lines 302-357."
        ),
    ),
    (_PAGE, "check-the-responses"): _workflow(
        "Check the responses { #check-the-responses }",
        302,
        337,
        _RECIPE,
        _ROOT_PATH_CASE,
        ["read-app-root-path"],
        ["http.body.bytes", "http.status"],
        (
            "The selected request is the app-side ASGI shape after a proxy has stripped "
            "`/api/v1`: path `/app`, root_path `/api/v1`. The endpoint response is observed; "
            "the two network paths and Traefik's path rewrite are not exercised "
            "(docs/en/docs/advanced/behind-a-proxy.md:302-337)."
        ),
        _ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "check-the-docs-ui"): _workflow(
        "Check the docs UI { #check-the-docs-ui }",
        338,
        357,
        _RECIPE,
        _ROOT_PATH_CASE,
        ["read-openapi-servers", "read-docs-ui"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        (
            "The actions select the OpenAPI `/servers` projection and the generated Swagger "
            "HTML under an ASGI root_path of `/api/v1`. They observe FastAPI's URLs; no browser "
            "frontend or proxy network is run (docs/en/docs/advanced/behind-a-proxy.md:338-356)."
        ),
        (
            _ROOT_PATH_RATIONALE
            + " The pinned UI section explains that FastAPI includes root_path in the OpenAPI "
            "server and Swagger schema URL (docs/en/docs/advanced/behind-a-proxy.md:338-356)."
        ),
    ),
    (_PAGE, "disable-automatic-server-from-root-path"): _workflow(
        "Disable automatic server from `root_path` { #disable-automatic-server-from-root-path }",
        425,
        432,
        _NO_AUTO_SERVER_RECIPE,
        _NO_AUTO_SERVER_CASE,
        ["tutorial004-read-openapi-servers"],
        [
            "docs.response.headers",
            "docs.response.status",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
        ],
        (
            "This exact tutorial004 OpenAPI request selects the generated `/servers` value "
            "with `root_path_in_servers=False` and a configured root_path. It does not claim "
            "the behavior of other OpenAPI fields or server configuration "
            "(docs/en/docs/advanced/behind-a-proxy.md:425-432)."
        ),
        (
            "FastAPI 0.157.0 declares `root_path_in_servers` and conditionally prepends the "
            "request scope root_path in its OpenAPI handler "
            "(fastapi/applications.py:667-683, 1120-1135). The pinned tutorial004 example "
            "and test provide the exact configuration "
            "and selected server observation (docs_src/behind_a_proxy/tutorial004_py310.py:1-14; "
            "tests/test_tutorial/test_behind_a_proxy/test_tutorial004.py:4-47; "
            "docs/en/docs/advanced/behind-a-proxy.md:425-431)."
        ),
    ),
    (_PAGE, "mounting-a-sub-application"): _workflow(
        "Mounting a sub-application { #mounting-a-sub-application }",
        433,
        437,
        _RECIPE,
        "fastapi.docs.behind-proxy.mounted-root-path",
        ["read-mounted-subapp-root-path"],
        ["http.body.bytes", "http.status"],
        (
            "The ASGI scope supplies path `/api/v1/subapi/sub` and root_path `/api/v1`; the "
            "response observes the child scope after the documented `/subapi` mount. This "
            "samples one HTTP mount and does not exercise Uvicorn's scope construction, other "
            "mounts, URL reversal, or proxy routing "
            "(docs/en/docs/advanced/behind-a-proxy.md:433-437)."
        ),
        (
            "FastAPI 0.157.0 preserves the supplied root_path when the app option is empty "
            "(fastapi/applications.py:1175-1178). Starlette 1.6.0 strips a matching root_path "
            "from path before routing (starlette/_utils.py:96-110), then Mount appends its "
            "matched prefix to the child scope and Router dispatches that child "
            "(starlette/routing.py:394-424, 684-691). The docs say a mounted sub-application "
            "works with a proxy root_path (docs/en/docs/advanced/behind-a-proxy.md:433-437); "
            "the pinned sub-application example and test establish the `/subapi` mount and "
            "`/subapi/sub` route without a proxy root_path "
            "(docs_src/sub_applications/tutorial001_py310.py:11-19; "
            "tests/test_tutorial/test_sub_applications/test_tutorial001.py:15-18). This action "
            "provides a post-server ASGI scope and makes no claim about how the proxy/server "
            "constructs it."
        ),
    ),
}
