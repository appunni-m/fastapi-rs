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
_APP_ROOT_PATH_RECIPE = "tests/fixtures/input-recipes/parity/behind-proxy-tutorial002-upstream.yaml"
_NO_AUTO_SERVER_CASE = "fastapi.behind-proxy.tutorial004.openapi-servers"
_NO_AUTO_SERVER_RECIPE = (
    "tests/fixtures/input-recipes/parity/behind-proxy-tutorial004-upstream.yaml"
)

_ROOT_PATH_RATIONALE = (
    "FastAPI 0.141.1 stores its configured root_path and, in __call__, writes it to the "
    "incoming scope only when non-empty (fastapi/applications.py:949, 1160-1163). The "
    "OpenAPI handler reads request scope root_path and conditionally prepends it to "
    "servers (fastapi/applications.py:1108-1118); Swagger and ReDoc handlers prepend it "
    "to their schema URLs (fastapi/applications.py:1123-1158). The pinned docs explain "
    "the stripped-prefix ASGI shape and resulting URLs "
    "(docs/en/docs/advanced/behind-a-proxy.md:100-128, 147-164), while the tutorial001 "
    "route and test demonstrate the request-visible root_path "
    "(docs_src/behind_a_proxy/tutorial001_py310.py:1-8; "
    "tests/test_tutorial/test_behind_a_proxy/test_tutorial001.py:6-12). Each input is "
    "the ASGI scope after any external proxy/server processing; Starlette 1.6.0 owns "
    "generic route matching and response dispatch."
)

_SERVER_BOUNDARY = (
    "FastAPI 0.141.1's application __call__ writes configured root_path to the scope and "
    "delegates to Starlette (fastapi/applications.py:1160-1163); it does not implement the "
    "forwarded-header trust policy described by the pinned docs "
    "(docs/en/docs/advanced/behind-a-proxy.md:9-13, 25-39, 67-99). The CLI/server "
    "configuration, peer trust, header interpretation, and proxy rewriting are outside "
    "the FastAPI ASGI application contract and the Starlette 1.6.0 oracle."
)

_APP_ROOT_PATH_RATIONALE = (
    "FastAPI 0.141.1 stores the configured FastAPI(root_path=...) value and applies a "
    "non-empty value to the request scope in __call__ (fastapi/applications.py:949, "
    "1160-1163). The pinned section says the app option is equivalent to the server's "
    "root_path input and shows the unprefixed `/app` request "
    "(docs/en/docs/advanced/behind-a-proxy.md:219-242); tutorial002 supplies that exact "
    "app configuration and route (docs_src/behind_a_proxy/tutorial002_py310.py:1-8), "
    "and its test requests `/app` and observes root_path "
    "(tests/test_tutorial/test_behind_a_proxy/test_tutorial002.py:4-13). Starlette 1.6.0 "
    "owns generic route matching and response dispatch."
)

DOC_SECTION_CASE_MAPPINGS_BEHIND_PROXY_20261015 = {
    (_PAGE, "behind-a-proxy"): _excluded(
        "Behind a Proxy { #behind-a-proxy }",
        1,
        466,
        (
            "This page-level heading is an overview spanning proxy trust, server flags, "
            "root_path, OpenAPI/docs URLs, local Traefik configuration, and mounted apps. "
            "The pinned page introduces those topics at lines 3-466; its independently "
            "observable FastAPI and shared-Starlette behavior is reviewed "
            "under the narrower anchored sections below."
        ),
        (
            "A page-wide workflow would conflate server/proxy process behavior with FastAPI "
            "application policy and Starlette routing. The source spans separate forwarded "
            "headers (docs/en/docs/advanced/behind-a-proxy.md:7-99), root_path and docs URLs "
            "(docs/en/docs/advanced/behind-a-proxy.md:100-243, "
            "docs/en/docs/advanced/behind-a-proxy.md:331-386), and mounting "
            "(docs/en/docs/advanced/behind-a-proxy.md:462-466). The child mappings preserve those "
            "ownership boundaries and select only the relevant ASGI actions."
        ),
    ),
    (_PAGE, "proxy-forwarded-headers"): _excluded(
        "Proxy Forwarded Headers { #proxy-forwarded-headers }",
        7,
        99,
        (
            "This parent section explains forwarded-header purpose and groups the server-flag "
            "and HTTPS-redirect child sections. Reading and trusting those headers is server "
            "behavior; the focused child mappings cover the app-visible redirect input and "
            "exclude server trust configuration "
            "(docs/en/docs/advanced/behind-a-proxy.md:9-13, 25-59, 67-99)."
        ),
        _SERVER_BOUNDARY,
    ),
    (_PAGE, "enable-proxy-forwarded-headers"): _excluded(
        "Enable Proxy Forwarded Headers { #enable-proxy-forwarded-headers }",
        25,
        42,
        (
            "The section configures `fastapi run --forwarded-allow-ips` and describes which "
            "remote peers the server trusts. It has no ASGI request action that distinguishes "
            "FastAPI application behavior."
        ),
        _SERVER_BOUNDARY,
    ),
    (_PAGE, "redirects-with-https"): _workflow(
        "Redirects with HTTPS { #redirects-with-https }",
        43,
        66,
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
            "(docs_src/behind_a_proxy/tutorial001_01_py310.py:1-9; "
            "tests/test_tutorial/test_behind_a_proxy/test_tutorial001_01.py:5-16; "
            "docs/en/docs/advanced/behind-a-proxy.md:43-59). FastAPI "
            "uses Starlette routing for this redirect; Starlette 1.6.0 Router performs the "
            "slash retry and builds its URL from the ASGI scope (starlette/routing.py:704-718). "
            "Forwarded-header interpretation remains server-owned."
        ),
    ),
    (_PAGE, "how-proxy-forwarded-headers-work"): _excluded(
        "How Proxy Forwarded Headers Work { #how-proxy-forwarded-headers-work }",
        67,
        99,
        (
            "The diagram and prose describe the proxy adding X-Forwarded headers and the "
            "application server interpreting them. They specify no FastAPI application "
            "operation independently observable from an ASGI scope "
            "(docs/en/docs/advanced/behind-a-proxy.md:67-99)."
        ),
        _SERVER_BOUNDARY,
    ),
    (_PAGE, "proxy-with-a-stripped-path-prefix"): _workflow(
        "Proxy with a stripped path prefix { #proxy-with-a-stripped-path-prefix }",
        100,
        243,
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
            "(docs/en/docs/advanced/behind-a-proxy.md:100-164)."
        ),
        _ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "providing-the-root-path"): _excluded(
        "Providing the `root_path` { #providing-the-root-path }",
        166,
        189,
        (
            "The section documents Uvicorn/Hypercorn `--root-path` command-line options. "
            "Those server processes create the incoming ASGI scope; no FastAPI CLI process "
            "or server startup behavior is part of the FastAPI application workflow "
            "(docs/en/docs/advanced/behind-a-proxy.md:166-188)."
        ),
        (
            "The pinned docs assign `--root-path` to Uvicorn/Hypercorn server configuration "
            "(docs/en/docs/advanced/behind-a-proxy.md:166-188). FastAPI's application call "
            "consumes the already populated scope and overwrites root_path only when the app "
            "option is non-empty (fastapi/applications.py:949, 1160-1163). The server flag "
            "and scope construction are not modeled as FastAPI or Starlette behavior."
        ),
    ),
    (_PAGE, "checking-the-current-root-path"): _workflow(
        "Checking the current `root_path` { #checking-the-current-root-path }",
        190,
        218,
        _RECIPE,
        _ROOT_PATH_CASE,
        ["read-app-root-path"],
        ["http.body.bytes", "http.status"],
        (
            "The selected `/app` request supplies a non-empty ASGI root_path and observes "
            "the example endpoint's scope-derived response. It does not claim how Uvicorn or "
            "the proxy creates that scope (docs/en/docs/advanced/behind-a-proxy.md:190-218)."
        ),
        _ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "about-root-path"): _workflow(
        "About `root_path` { #about-root-path }",
        227,
        243,
        _APP_ROOT_PATH_RECIPE,
        _APP_ROOT_PATH_CASE,
        ["tutorial002-read-root-path"],
        ["http.body.bytes", "http.status"],
        (
            "The exact tutorial002 action requests `/app` while the FastAPI app is configured "
            "with `/api/v1`; the response selects the scope-visible root_path while the "
            "application route remains unprefixed. Server routing and proxy forwarding are "
            "outside this action (docs/en/docs/advanced/behind-a-proxy.md:227-242)."
        ),
        _APP_ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "about-proxies-with-a-stripped-path-prefix"): _excluded(
        "About proxies with a stripped path prefix { #about-proxies-with-a-stripped-path-prefix }",
        244,
        251,
        (
            "This section contrasts proxy configurations that strip or retain an external URL "
            "prefix. That transformation is performed before the application receives its "
            "ASGI scope and is not FastAPI library behavior "
            "(docs/en/docs/advanced/behind-a-proxy.md:244-250)."
        ),
        (
            "The pinned docs describe the two proxy path-rewrite choices before requests reach "
            "the Uvicorn application server (docs/en/docs/advanced/behind-a-proxy.md:244-250). "
            "FastAPI receives the resulting ASGI scope (fastapi/applications.py:1160-1163); "
            "the proxy's external URL and rewrite are not application behavior."
        ),
    ),
    (_PAGE, "testing-locally-with-traefik"): _excluded(
        "Testing locally with Traefik { #testing-locally-with-traefik }",
        252,
        386,
        (
            "This parent section instructs the reader to configure and run Traefik and Uvicorn. "
            "Its process, port, and path-rewrite behavior is external; the child response and "
            "docs-URL effects are reviewed independently "
            "(docs/en/docs/advanced/behind-a-proxy.md:252-330, 331-386)."
        ),
        (
            "The pinned example configures Traefik's stripPrefix middleware, ports, and the "
            "Uvicorn command as external processes "
            "(docs/en/docs/advanced/behind-a-proxy.md:252-330). Those are not FastAPI "
            "application actions; the independently observable app and docs URL effects in "
            "the following sections are mapped at lines 331-386."
        ),
    ),
    (_PAGE, "check-the-responses"): _workflow(
        "Check the responses { #check-the-responses }",
        331,
        366,
        _RECIPE,
        _ROOT_PATH_CASE,
        ["read-app-root-path"],
        ["http.body.bytes", "http.status"],
        (
            "The selected request is the app-side ASGI shape after a proxy has stripped "
            "`/api/v1`: path `/app`, root_path `/api/v1`. The endpoint response is observed; "
            "the two network paths and Traefik's path rewrite are not exercised "
            "(docs/en/docs/advanced/behind-a-proxy.md:331-366)."
        ),
        _ROOT_PATH_RATIONALE,
    ),
    (_PAGE, "check-the-docs-ui"): _workflow(
        "Check the docs UI { #check-the-docs-ui }",
        367,
        386,
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
            "frontend or proxy network is run (docs/en/docs/advanced/behind-a-proxy.md:367-385)."
        ),
        (
            _ROOT_PATH_RATIONALE
            + " The pinned UI section explains that FastAPI includes root_path in the OpenAPI "
            "server and Swagger schema URL (docs/en/docs/advanced/behind-a-proxy.md:367-385)."
        ),
    ),
    (_PAGE, "disable-automatic-server-from-root-path"): _workflow(
        "Disable automatic server from `root_path` { #disable-automatic-server-from-root-path }",
        454,
        461,
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
            "(docs/en/docs/advanced/behind-a-proxy.md:454-461)."
        ),
        (
            "FastAPI 0.141.1 declares `root_path_in_servers` and conditionally prepends the "
            "scope root_path in its OpenAPI handler (fastapi/applications.py:660-679, "
            "1108-1118). The pinned tutorial004 example and test provide the exact configuration "
            "and selected server observation (docs_src/behind_a_proxy/tutorial004_py310.py:1-14; "
            "tests/test_tutorial/test_behind_a_proxy/test_tutorial004.py:4-47; "
            "docs/en/docs/advanced/behind-a-proxy.md:454-460)."
        ),
    ),
    (_PAGE, "mounting-a-sub-application"): _workflow(
        "Mounting a sub-application { #mounting-a-sub-application }",
        462,
        466,
        _RECIPE,
        "fastapi.docs.behind-proxy.mounted-root-path",
        ["read-mounted-subapp-root-path"],
        ["http.body.bytes", "http.status"],
        (
            "The ASGI scope supplies path `/api/v1/subapi/sub` and root_path `/api/v1`; the "
            "response observes the child scope after the documented `/subapi` mount. This "
            "samples one HTTP mount and does not exercise Uvicorn's scope construction, other "
            "mounts, URL reversal, or proxy routing "
            "(docs/en/docs/advanced/behind-a-proxy.md:462-466)."
        ),
        (
            "FastAPI 0.141.1 preserves the supplied root_path when the app option is empty "
            "(fastapi/applications.py:1160-1163). Starlette 1.6.0 strips a matching root_path "
            "from path before routing (starlette/_utils.py:96-110), then Mount appends its "
            "matched prefix to the child scope and Router dispatches that child "
            "(starlette/routing.py:394-424, 684-691). The docs say a mounted sub-application "
            "works with a proxy root_path (docs/en/docs/advanced/behind-a-proxy.md:462-466); "
            "the pinned sub-application example and test establish the `/subapi` mount and "
            "`/subapi/sub` route without a proxy root_path "
            "(docs_src/sub_applications/tutorial001_py310.py:11-19; "
            "tests/test_tutorial/test_sub_applications/test_tutorial001.py:15-18). This action "
            "provides a post-server ASGI scope and makes no claim about how the proxy/server "
            "constructs it."
        ),
    ),
}
