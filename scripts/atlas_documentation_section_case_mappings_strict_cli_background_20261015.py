"""Reviewed mappings and exclusions for strict-content-type, CLI, and reference docs.

The source baseline is FastAPI 0.141.1 with Starlette 1.6.0 as the generic ASGI
oracle. The Starlette-RS validation checkout is
``/private/tmp/fastapi-rs-starlette-rs-b4c8-validation`` at ``b4c8a65c``; these
documentation mappings are input evidence, not parity results.
"""

_STRICT_RECIPE = "tests/fixtures/input-recipes/parity/strict_content_type.yaml"
_CLI_RECIPE = (
    "tests/fixtures/input-recipes/parity/fastapi-cli-documented-process-v2.yaml"
)
_BACKGROUND_RECIPE = "tests/fixtures/input-recipes/parity/docs-reference-http.yaml"


DOC_SECTION_CASE_MAPPINGS_STRICT_CLI_BACKGROUND_20261015 = {
    ("advanced/strict-content-type.md", "strict-content-type-checking"): {
        "heading": "Strict Content-Type Checking { #strict-content-type-checking }",
        "start_line": 1,
        "end_line": 88,
        "recipe_path": _STRICT_RECIPE,
        "case_ids": ["fastapi.docs.strict-content-type.missing-header"],
        "action_ids": ["strict-default"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "Partial: the selected POST sends a JSON-shaped body without Content-Type to "
            "the default FastAPI app and observes only response status, ordered headers, "
            "and body bytes. It samples the default server-side body parsing branch; it "
            "does not cover the page's browser threat model, every media type, malformed "
            "or empty bodies, or the opt-out setting."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 documents the default requirement for a valid "
            "Content-Type on JSON request bodies (../fastapi/docs/en/docs/advanced/"
            "strict-content-type.md:1-3). FastAPI defaults ``strict_content_type`` to "
            "True (../fastapi/fastapi/applications.py:840-862), passes it into the root "
            "router (:984-999), and only decodes an untyped request body as JSON when "
            "that setting is false (../fastapi/fastapi/routing.py:401-449). The selected "
            "``strict-default`` action in ``fastapi.docs.strict-content-type.missing-header`` "
            "has no Content-Type header, and its recipe carries this exact documentation "
            "page with kind ``upstream_documentation``."
        ),
    },
    ("advanced/strict-content-type.md", "csrf-risk"): {
        "status": "excluded",
        "heading": "CSRF Risk { #csrf-risk }",
        "start_line": 5,
        "end_line": 18,
        "exclusion_reason": (
            "This section describes browser CORS-preflight conditions, credentials, and "
            "local-network trust assumptions. Those platform and deployment conditions "
            "are not a distinct FastAPI request input; the server-side strict body parsing "
            "branch is sampled under the parent section."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/strict-content-type.md:5-18 "
            "describes when browsers send requests without Content-Type or credentials "
            "and when the local-network scenario matters. FastAPI's source documents and "
            "implements only the server setting that controls untyped JSON parsing "
            "(../fastapi/fastapi/applications.py:840-862; ../fastapi/fastapi/routing.py:"
            "436-449). The selected parent-section workflow observes that server branch, "
            "not browser preflight, origin, or credential behavior, so this narrative "
            "section has no separate FastAPI-owned fixture claim."
        ),
    },
    ("advanced/strict-content-type.md", "example-attack"): {
        "heading": "Example Attack { #example-attack }",
        "start_line": 19,
        "end_line": 65,
        "recipe_path": _STRICT_RECIPE,
        "case_ids": ["fastapi.docs.strict-content-type.missing-header"],
        "action_ids": ["strict-default"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "Partial: the selected action makes one no-Content-Type POST to a JSON body "
            "route and records its HTTP response. It samples the server response to an "
            "untyped body only; it does not reproduce the local agent, malicious origin, "
            "browser fetch/Blob behavior, CORS preflight, or any side effect described by "
            "the narrative."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/strict-content-type.md:19-65 "
            "illustrates an unauthenticated local API reached by a browser request whose "
            "body lacks Content-Type. The selected input in "
            "``fastapi.docs.strict-content-type.missing-header`` posts JSON-shaped bytes "
            "without that header and carries the exact docs page as "
            "``upstream_documentation`` evidence; it intentionally maps only the server "
            "parsing consequence. FastAPI's route body parser leaves an untyped body "
            "unparsed as JSON under the default setting (../fastapi/fastapi/routing.py:"
            "425-450), while the surrounding browser and CORS scenario has no behavior "
            "in this ASGI workflow."
        ),
    },
    ("fastapi-cli.md", "fastapi-cli"): {
        "heading": "FastAPI CLI { #fastapi-cli }",
        "start_line": 1,
        "end_line": 138,
        "recipe_path": _CLI_RECIPE,
        "case_ids": [
            "fastapi.cli.process.root-help",
            "fastapi.cli.process.dev-auto-discovery-environment-default",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "process.exit_code",
            "process.stderr",
            "process.stdout",
        ],
        "scope_note": (
            "Partial: the selected process cases capture the top-level help output and "
            "one successful default ``fastapi dev`` server request. They do not cover "
            "every subcommand, project-management commands, all entrypoint discovery "
            "rules, reload output, deployment, or the complete CLI terminal transcript."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/fastapi-cli.md:1-7 introduces the "
            "optional command-line program and its ``fastapi dev`` usage. Its ``standard`` "
            "extra requires ``fastapi-cli[standard] >=0.0.32`` and exposes "
            "``fastapi = fastapi.cli:main`` (../fastapi/pyproject.toml:59-62, 119-120); "
            "the standard oracle pins fastapi-cli 0.0.32 (metadata.yaml:102). FastAPI's "
            "entrypoint delegates to that optional package (../fastapi/fastapi/cli.py:1-13). "
            "Both selected cases in ``fastapi-cli-documented-process-v2.yaml`` cite this "
            "exact docs page as ``upstream_documentation``; they observe process output "
            "for root help and process completion plus one HTTP response for the dev app."
        ),
    },
    ("fastapi-cli.md", "fastapi-dev-with-path-or-with-entrypoint-cli-option"): {
        "heading": (
            "`fastapi dev` with path or with `--entrypoint` CLI option "
            "{ #fastapi-dev-with-path-or-with-entrypoint-cli-option }"
        ),
        "start_line": 98,
        "end_line": 115,
        "recipe_path": _CLI_RECIPE,
        "case_ids": [
            "fastapi.cli.process.dev-path-preserves-environment",
            "fastapi.cli.process.dev-explicit-entrypoint",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "process.exit_code",
        ],
        "scope_note": (
            "Partial: one isolated process passes ``main.py`` as the path and one passes "
            "a module-qualified app through ``--entrypoint``; both make one GET request "
            "to the selected app and observe process exit plus HTTP status/body. The cases "
            "do not compare precedence, invalid paths, the ``pyproject.toml`` entrypoint, "
            "or CLI output."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/fastapi-cli.md:98-115 documents the path "
            "argument, ``--entrypoint``, and the recommendation to configure the entrypoint "
            "in ``pyproject.toml``. The selected ``dev-path-preserves-environment`` and "
            "``dev-explicit-entrypoint`` cases in "
            "``fastapi-cli-documented-process-v2.yaml`` use those two command forms and "
            "each carries the exact page as ``upstream_documentation`` evidence. The pin "
            "is FastAPI 0.141.1's optional ``fastapi-cli[standard] >=0.0.32`` integration "
            "(../fastapi/pyproject.toml:59-62; metadata.yaml:102); the cases sample only "
            "the selected server response and process exit."
        ),
    },
    ("fastapi-cli.md", "fastapi-dev"): {
        "heading": "`fastapi dev` { #fastapi-dev }",
        "start_line": 116,
        "end_line": 125,
        "recipe_path": _CLI_RECIPE,
        "case_ids": [
            "fastapi.cli.process.dev-auto-discovery-environment-default",
            "fastapi.cli.process.dev-path-preserves-environment",
        ],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "process.exit_code",
        ],
        "scope_note": (
            "Partial: one default ``fastapi dev`` process exposes the inserted "
            "``FASTAPI_ENV=development`` value through its route response, and one process "
            "preserves a pre-existing ``FASTAPI_ENV=staging`` value. Both observe process "
            "exit and HTTP status/body. They do not observe reload output, filesystem "
            "watching, or the default loopback bind address."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/fastapi-cli.md:116-125 documents the "
            "development command, auto-reload, loopback address, and ``FASTAPI_ENV`` "
            "default/preservation rules. The selected process cases use the same pinned "
            "optional CLI workflow and exact page-level ``upstream_documentation`` evidence; "
            "the route input returns the environment value so the chosen HTTP body selector "
            "observes only that limited behavior. FastAPI exposes the pinned CLI through "
            "``fastapi-cli[standard]`` (../fastapi/pyproject.toml:59-62, 119-120; "
            "../fastapi/fastapi/cli.py:1-13), while this mapping makes no claim about "
            "reload or bind-address results."
        ),
    },
    ("fastapi-cli.md", "fastapi-run"): {
        "heading": "`fastapi run` { #fastapi-run }",
        "start_line": 126,
        "end_line": 138,
        "recipe_path": _CLI_RECIPE,
        "case_ids": ["fastapi.cli.process.run-auto-discovery-no-path"],
        "observation_selectors": [
            "http.body.bytes",
            "http.status",
            "process.exit_code",
        ],
        "scope_note": (
            "Partial: one ``fastapi run`` invocation auto-discovers the app and serves a "
            "single GET request; the process exit and response status/body are selected. "
            "The case explicitly sets host to 127.0.0.1, so this mapping does not establish "
            "the documented default bind address, reload setting, proxy setup, or a full "
            "production deployment."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/fastapi-cli.md:126-138 describes ``fastapi "
            "run`` as the production-mode command and links deployment guidance. The "
            "selected ``fastapi.cli.process.run-auto-discovery-no-path`` case in "
            "``fastapi-cli-documented-process-v2.yaml`` invokes that command, sends one "
            "request, and carries this exact page as ``upstream_documentation`` evidence. "
            "FastAPI 0.141.1 exposes this optional integration through its pinned "
            "fastapi-cli standard extra (../fastapi/pyproject.toml:59-62, 119-120; "
            "metadata.yaml:102); the case's explicit host override is why no default "
            "production bind claim is made."
        ),
    },
    ("reference/background.md", "@line:1"): {
        "heading": "Background Tasks - `BackgroundTasks`",
        "start_line": 1,
        "end_line": 11,
        "recipe_path": _BACKGROUND_RECIPE,
        "case_ids": ["fastapi.docs.reference-wave.http.background-task-injection"],
        "action_ids": ["schedule", "read-state"],
        "observation_selectors": [
            "http.body.bytes",
            "http.headers.ordered",
            "http.status",
        ],
        "scope_note": (
            "Partial: one route injects ``BackgroundTasks``, schedules one task, and a "
            "later request observes the recorded effect. The selected actions observe only "
            "the two HTTP responses; they do not record send/task ordering, sync-versus-async "
            "callables, errors, or the full public constructor/signature surface."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/reference/background.md:1-11 documents "
            "the injected ``BackgroundTasks`` parameter and the ``fastapi`` import. FastAPI "
            "recognizes Starlette BackgroundTasks subclasses and injects a shared instance "
            "(../fastapi/fastapi/dependencies/utils.py:365-367, 715-729); its public class "
            "subclasses Starlette's class (../fastapi/fastapi/background.py:5, 11-17). "
            "Starlette 1.6.0 owns execution after the response send "
            "(../starlette/starlette/responses.py:169-170; "
            "../starlette/starlette/background.py:26-36). The selected case in "
            "``docs-reference-http.yaml`` has this exact page with kind "
            "``upstream_documentation``. The validation checkout "
            "/private/tmp/fastapi-rs-starlette-rs-b4c8-validation at b4c8a65c contains the "
            "native BackgroundTasks binding (starlette-rs-py/src/background.rs:114-169); "
            "this crosswalk records the input and upstream ownership only, not target parity."
        ),
    },
    (
        "tutorial/dependencies/global-dependencies.md",
        "dependencies-for-groups-of-path-operations",
    ): {
        "status": "excluded",
        "heading": (
            "Dependencies for groups of *path operations* "
            "{ #dependencies-for-groups-of-path-operations }"
        ),
        "start_line": 14,
        "end_line": 16,
        "exclusion_reason": (
            "These lines are a cross-reference to the separate Bigger Applications tutorial "
            "for router-level groups; they add no input or behavior to the application-wide "
            "global-dependency section above. The existing global-dependency workflow is "
            "app-level and cannot evidence APIRouter group behavior."
        ),
        "rationale": (
            "Pinned FastAPI 0.141.1 docs/en/docs/tutorial/dependencies/global-dependencies.md:"
            "14-16 only points readers to Bigger Applications. That tutorial shows "
            "dependencies attached to an ``APIRouter`` for its path operations "
            "(../fastapi/docs/en/docs/tutorial/bigger-applications.md:143-152). The existing "
            "``fastapi.docs.documentation-wave.dependencies-security.global-dependencies`` "
            "case instead constructs ``FastAPI(dependencies=[...])`` and dispatches "
            "``/reports`` (tests/fixtures/workloads/docs_dependencies_security.py:64-79; "
            "tests/fixtures/input-recipes/parity/docs-dependencies-security.yaml:225-275); "
            "although its recipe cites the global-dependencies page, that input is app-wide "
            "and does not exercise router-level group behavior. Excluding this cross-reference "
            "avoids mapping the wrong dependency scope."
        ),
    },
}
