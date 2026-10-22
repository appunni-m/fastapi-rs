"""Reviewed section mappings for the tutorial dependencies-with-yield page."""


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


_BASELINE = (
    "tests/fixtures/input-recipes/parity/dependencies-with-yield-section-review-20261015.yaml"
)
_TUTORIAL = "tests/fixtures/input-recipes/parity/dependency-yield-tutorials-upstream.yaml"
_ERRORS = "tests/fixtures/input-recipes/parity/dependency-yield-errors-tutorials-upstream.yaml"
_LIFECYCLE = "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml"
_SCOPE = "tests/fixtures/input-recipes/parity/dependency-lifecycle-security-review.yaml"
_HTTP = ["http.status", "http.body.bytes"]
_HTTP_ERROR = ["http.status", "http.body.bytes", "asgi.application_error.exception"]
_HTTP_RERAISED = ["http.status", "http.body.bytes", "validation.error_class"]


DOC_SECTION_CASE_MAPPINGS_DEPENDENCIES_WITH_YIELD_20261015 = {
    ("tutorial/dependencies/dependencies-with-yield.md", "dependencies-with-yield"): _excluded(
        "Dependencies with yield { #dependencies-with-yield }",
        1,
        290,
        (
            "The page heading introduces generator dependencies but defines no additional "
            "request or response beyond its concrete child sections."
        ),
        (
            "Each behavior-specific heading below names its own recipe cases, actions, and "
            "selectors. The page-level introduction would broaden those separate contracts."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "a-database-dependency-with-yield",
    ): _workflow(
        "A database dependency with `yield` { #a-database-dependency-with-yield }",
        26,
        49,
        _BASELINE,
        ["fastapi.docs.dependencies-with-yield.database-session-lifecycle"],
        ["session-response", "session-cleanup-observation"],
        _HTTP,
        (
            "The first response exposes a value from an async yielded in-memory session; a "
            "second request reads teardown events. This samples value injection and normal "
            "request-scope cleanup, not a database driver, transactions, or a synchronous "
            "generator dependency."
        ),
        (
            "The pinned tutorial example creates a session, yields it, and closes it in "
            "`finally` (`../fastapi/docs_src/dependencies/tutorial007_py310.py:1-6`; "
            "the page describes injection and cleanup at lines 26-48). FastAPI wraps "
            "generator dependencies as context managers and enters them on the selected "
            "exit stack (`../fastapi/fastapi/dependencies/utils.py:566-574,662-672`); "
            "its routing stacks surround response creation and sending "
            "(`../fastapi/fastapi/routing.py:137-158`)."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "a-dependency-with-yield-and-try",
    ): _workflow(
        "A dependency with `yield` and `try` { #a-dependency-with-yield-and-try }",
        50,
        61,
        _BASELINE,
        ["fastapi.docs.dependencies-with-yield.try-finally-error"],
        ["operation-error", "error-cleanup-observation"],
        _HTTP_ERROR,
        (
            "The endpoint raises a `LookupError`; the yielded dependency records the caught "
            "exception, re-raises it, and runs `finally`. A follow-up request observes the "
            "cleanup trace. The generic 500 response and application-error transport are "
            "Starlette behavior; this input uses them to expose FastAPI's dependency "
            "teardown path and does not sample exception translation or suppression."
        ),
        (
            "The tutorial's `tutorial007` dependency wraps `yield` in `try/finally` "
            "(`../fastapi/docs_src/dependencies/tutorial007_py310.py:3-6`). FastAPI enters "
            "the generator as a context manager "
            "(`../fastapi/fastapi/dependencies/utils.py:566-574`) "
            "and exits its request stack around response dispatch "
            "(`../fastapi/fastapi/routing.py:137-158`), returning the endpoint exception "
            "through teardown. Starlette 1.6.0 owns the generic unhandled-error response."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "sub-dependencies-with-yield",
    ): _workflow(
        "Sub-dependencies with `yield` { #sub-dependencies-with-yield }",
        62,
        95,
        _TUTORIAL,
        ["fastapi.dependencies.tutorial008.async-yield-chain-default"],
        ["chain-result", "chain-cleanup"],
        _HTTP,
        (
            "The selected input follows one all-async, three-node yield chain, returns the "
            "leaf value, and reads cleanup afterward. Mixed return/yield graphs, arbitrary "
            "fan-out, and other graph shapes are not sampled."
        ),
        (
            "The pinned example links three yielded dependencies and uses each parent value "
            "during teardown (`../fastapi/docs_src/dependencies/tutorial008_an_py310.py:6-27`). "
            "FastAPI recursively solves sub-dependencies and enters generator dependencies "
            "on their selected exit stack (`../fastapi/fastapi/dependencies/utils.py:640-680`)."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "dependencies-with-yield-and-httpexception",
    ): _workflow(
        (
            "Dependencies with `yield` and `HTTPException` "
            "{ #dependencies-with-yield-and-httpexception }"
        ),
        96,
        115,
        _ERRORS,
        [
            "fastapi.dependencies.tutorial008b.default-parameter-exception-translation",
            "fastapi.dependencies.tutorial008b.annotated-parameter-exception-translation",
        ],
        ["owner-error-translated-by-yield-dependency"],
        _HTTP,
        (
            "Both default and `Annotated` dependency declarations are exercised for the "
            "owner-error path, where teardown catches `OwnerError` and raises `HTTPException`. "
            "The selected action does not claim custom exception handlers or other exception "
            "classes."
        ),
        (
            "The pinned `tutorial008b` example catches the endpoint's `OwnerError` around "
            "`yield` and raises `HTTPException` "
            "(`../fastapi/docs_src/dependencies/tutorial008b_py310.py:16-20`; "
            "the page links this example at lines 96-114). FastAPI's generator solver is "
            "the dependency lifecycle owner (`../fastapi/fastapi/dependencies/utils.py:566-574`)."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "dependencies-with-yield-and-except",
    ): _workflow(
        "Dependencies with `yield` and `except` { #dependencies-with-yield-and-except }",
        116,
        133,
        _ERRORS,
        ["fastapi.dependencies.tutorial008c.suppressed-yield-exception"],
        ["suppressed-default", "suppressed-annotated", "observed-original-exceptions"],
        _HTTP_ERROR,
        (
            "The default and `Annotated` inputs catch and suppress the endpoint error, then "
            "read the dependency's captured exception. FastAPI 0.157.0 additionally raises "
            "its `FastAPIError` guard when suppression prevents response creation; the "
            "generic 500 response is Starlette-owned. Logs are not observed."
        ),
        (
            "The pinned `tutorial008c` example suppresses `InternalError` in the generator "
            "(`../fastapi/docs_src/dependencies/tutorial008c_py310.py:10-15`). In 0.157.0, "
            "routing detects that the response was never awaited and raises `FastAPIError` "
            "(`../fastapi/fastapi/routing.py:137-155`); Starlette 1.6.0 owns its generic "
            "server-error response."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "always-raise-in-dependencies-with-yield-and-except",
    ): _workflow(
        (
            "Always `raise` in Dependencies with `yield` and `except` "
            "{ #always-raise-in-dependencies-with-yield-and-except }"
        ),
        124,
        133,
        _ERRORS,
        ["fastapi.dependencies.tutorial008d.reraised-yield-exception"],
        ["reraised-default", "reraised-annotated", "observed-original-exceptions"],
        _HTTP_RERAISED,
        (
            "The two declaration forms re-raise the original `InternalError`; the later "
            "readback exposes the recorded exception. The input observes the application "
            "error class and HTTP response, not server log output."
        ),
        (
            "The pinned `tutorial008d` example catches `InternalError` and uses bare `raise` "
            "(`../fastapi/docs_src/dependencies/tutorial008d_py310.py:10-15`; the page "
            "describes the case at lines 124-132). FastAPI's routing exit stack carries the "
            "exception through generator teardown (`../fastapi/fastapi/routing.py:137-158`); "
            "Starlette 1.6.0 owns generic unhandled-error response behavior."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "execution-of-dependencies-with-yield",
    ): _excluded(
        "Execution of dependencies with `yield` { #execution-of-dependencies-with-yield }",
        134,
        186,
        (
            "The sequence diagram combines conditional dependency-start errors, endpoint "
            "errors, translated exceptions, response sending, and background-task failures; "
            "it is not one independent request contract."
        ),
        (
            "Yield injection and cleanup, error translation/suppression/re-raise, and scope "
            "timing are mapped in their narrower sections. Background-task ordering belongs "
            "to the separately reviewed lifecycle workflow, where Starlette owns response "
            "background dispatch."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "early-exit-and-scope",
    ): _workflow(
        "Early exit and `scope` { #early-exit-and-scope }",
        187,
        231,
        _LIFECYCLE,
        ["fastapi.dependencies.yield-scope-cleanup"],
        ["first-response", "subsequent-response"],
        _HTTP,
        (
            "A streaming response exposes function- and request-scoped resource state, and "
            "a second response reads cleanup events. FastAPI owns the dependency exit-stack "
            "timing; Starlette 1.6.0 owns stream iteration and ASGI response sending. This "
            "does not cover WebSocket scope or cancellation."
        ),
        (
            "The page specifies function cleanup before the response and request cleanup "
            "after it (lines 187-200), and the pinned `tutorial008e` example selects "
            '`scope="function"` (`../fastapi/docs_src/dependencies/tutorial008e_py310.py:1-13`). '
            "FastAPI closes the function stack before response dispatch and request stack "
            "after it (`../fastapi/fastapi/routing.py:137-158`). Starlette 1.6.0 sends "
            "streaming response bodies (`../starlette/starlette/responses.py:222-282`)."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "scope-for-sub-dependencies",
    ): _workflow(
        "`scope` for sub-dependencies { #scope-for-sub-dependencies }",
        202,
        231,
        _SCOPE,
        ["fastapi.dependencies.nested-yield-scopes-http"],
        [
            "nested-request-scope",
            "named-function-scope",
            "regular-function-scope",
            "http-scope-cleanup",
        ],
        _HTTP,
        (
            "The requests sample a valid request-scoped pair and a function-scoped parent "
            "with yielded function-scoped child, then read cleanup events. This is a small "
            "HTTP graph sample; invalid scope combinations, other graph shapes, and "
            "WebSocket scopes are not claimed."
        ),
        (
            "The pinned scope example describes which child scopes remain alive through a "
            "parent's cleanup (page lines 202-230). FastAPI builds and validates dependency "
            "scope relationships while constructing the graph "
            "(`../fastapi/fastapi/dependencies/utils.py:271-349`); the selected actions "
            "observe valid HTTP graph combinations and teardown."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "dependencies-with-yield-httpexception-except-and-background-tasks",
    ): _excluded(
        (
            "Dependencies with `yield`, `HTTPException`, `except` and Background Tasks "
            "{ #dependencies-with-yield-httpexception-except-and-background-tasks }"
        ),
        232,
        237,
        (
            "This section summarizes historical evolution and links to the advanced guide; "
            "it does not add a separate pinned request workflow."
        ),
        (
            "FastAPI-RS targets the pinned 0.157.0 contract. Current exception and lifecycle "
            "inputs are mapped above and in the linked advanced guide; no pre/post-version "
            "comparison is included."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "context-managers",
    ): _excluded(
        "Context Managers { #context-managers }",
        238,
        290,
        (
            "The parent heading groups Python context-manager background and a FastAPI "
            "dependency example, which have separate ownership and are mapped below."
        ),
        (
            "The Python `with` protocol is language/library behavior, while the nested "
            "context-manager dependency example is covered by its own child mapping. A "
            "parent workflow would combine those distinct contracts."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "what-are-context-managers",
    ): _excluded(
        'What are "Context Managers" { #what-are-context-managers }',
        240,
        257,
        (
            "The file-opening example and `with` cleanup description specify Python context "
            "manager behavior, not an independent FastAPI request behavior."
        ),
        (
            "The section cites Python's context-manager protocol and describes `open()`; "
            "FastAPI's use of generator context managers is an implementation note, while "
            "observable dependency behavior is mapped under the yielded-dependency sections."
        ),
    ),
    (
        "tutorial/dependencies/dependencies-with-yield.md",
        "using-context-managers-in-dependencies-with-yield",
    ): _workflow(
        (
            "Using context managers in dependencies with `yield` "
            "{ #using-context-managers-in-dependencies-with-yield }"
        ),
        258,
        290,
        _TUTORIAL,
        ["fastapi.dependencies.tutorial010.context-manager-in-yield-dependency"],
        ["database-result", "context-cleanup"],
        _HTTP,
        (
            "The selected route injects the resource yielded by a dependency that uses a "
            "synchronous `with` block, then reads context exit and resource cleanup. It "
            "does not test passing `@contextmanager` or `@asynccontextmanager` wrappers "
            "directly as dependencies; the page says FastAPI applies those internally."
        ),
        (
            "The pinned `tutorial010` example uses `with` inside the yielded dependency "
            "(`../fastapi/docs_src/dependencies/tutorial010_py310.py:1-13`; page lines "
            "258-288). FastAPI wraps yield-callable dependencies and enters their context "
            "on its lifecycle stack (`../fastapi/fastapi/dependencies/utils.py:566-574`)."
        ),
    ),
}
