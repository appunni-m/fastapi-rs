"""Reviewed section mappings for FastAPI's advanced dependencies page."""


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


_CALLABLE = "tests/fixtures/input-recipes/parity/advanced_dependencies.yaml"
_SCOPE = "tests/fixtures/input-recipes/parity/advanced_dependencies_scope_review_20261015.yaml"
_LIFECYCLE = (
    "tests/fixtures/input-recipes/parity/advanced_dependencies_lifecycle_review_20261015.yaml"
)
_EXCEPT = "tests/fixtures/input-recipes/parity/advanced_dependencies_except_review_20261015.yaml"

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_BODY_STATUS = ["http.body.bytes", "http.status"]


DOC_SECTION_CASE_MAPPINGS_ADVANCED_DEPENDENCIES_20261015 = {
    ("advanced/advanced-dependencies.md", "advanced-dependencies"): _excluded(
        "Advanced Dependencies { #advanced-dependencies }",
        1,
        163,
        (
            "The page-level heading introduces two distinct topics: callable parameterized "
            "dependencies and yielded-dependency lifecycle details. It defines no independent "
            "request or outcome beyond the mapped child sections."
        ),
        (
            "The callable checker cases are mapped under the five parameterization headings. "
            "Scope, streaming, suppressed-exception, and background-task observations are "
            "mapped under their specific lifecycle headings; an H1-level workflow would "
            "broaden those separate contracts."
        ),
    ),
    ("advanced/advanced-dependencies.md", "parameterized-dependencies"): _workflow(
        "Parameterized dependencies { #parameterized-dependencies }",
        3,
        12,
        _CALLABLE,
        [
            "fastapi.docs.advanced-dependencies.matching-query",
            "fastapi.docs.advanced-dependencies.nonmatching-query",
        ],
        None,
        _HTTP,
        (
            "The paired requests use the documented callable checker with its fixed content "
            "`bar` and vary only query `q`: one contains that content and one does not. The "
            "responses observe status, ordered headers, and body bytes; multiple checker "
            "instances or configurable query names are not sampled."
        ),
        (
            "The pinned example "
            "`../fastapi/docs_src/dependencies/tutorial011_an_py310.py:9-23` stores the fixed "
            "content on a checker instance and uses its result for the endpoint. "
            "These two recipe cases observe its matching and nonmatching outcomes."
        ),
    ),
    ("advanced/advanced-dependencies.md", "a-callable-instance"): _workflow(
        'A "callable" instance { #a-callable-instance }',
        13,
        24,
        _CALLABLE,
        [
            "fastapi.docs.advanced-dependencies.matching-query",
            "fastapi.docs.advanced-dependencies.nonmatching-query",
        ],
        None,
        _HTTP,
        (
            "Both requests execute the callable instance as the dependency and expose the "
            "endpoint result in the HTTP response. They sample its declared query input and "
            "the returned dependency value, not arbitrary `__call__` signatures or nested "
            "dependencies."
        ),
        (
            "FastAPI 0.157.0 inspects typed dependency signatures and builds its graph "
            "(`../fastapi/fastapi/dependencies/utils.py:241-270,314-389`), then resolves "
            "dependencies in `solve_dependencies` "
            "(`../fastapi/fastapi/dependencies/utils.py:657-819`). "
            "The mapped responses are the pinned example's two checker outcomes."
        ),
    ),
    ("advanced/advanced-dependencies.md", "parameterize-the-instance"): _workflow(
        "Parameterize the instance { #parameterize-the-instance }",
        25,
        32,
        _CALLABLE,
        [
            "fastapi.docs.advanced-dependencies.matching-query",
            "fastapi.docs.advanced-dependencies.nonmatching-query",
        ],
        None,
        _HTTP,
        (
            "The workload constructs the documented checker with fixed content `bar`; the "
            "paired query inputs distinguish a match from a nonmatch. They do not vary "
            "constructor arguments or compare two configured instances."
        ),
        (
            "The example's `__init__` stores the caller-supplied content "
            "(`../fastapi/docs_src/dependencies/tutorial011_an_py310.py:9-10`), "
            "and the case inputs "
            "observe the documented instance configuration through endpoint results. "
            "FastAPI does not participate in instance construction."
        ),
    ),
    ("advanced/advanced-dependencies.md", "create-an-instance"): _workflow(
        "Create an instance { #create-an-instance }",
        33,
        40,
        _CALLABLE,
        [
            "fastapi.docs.advanced-dependencies.matching-query",
            "fastapi.docs.advanced-dependencies.nonmatching-query",
        ],
        None,
        _HTTP,
        (
            "The documented instance is created with fixed content `bar` in the workload. "
            "The response pair shows how that instance affects matching; it does not claim "
            "constructor execution as a FastAPI operation or test other constructor values."
        ),
        (
            "`../fastapi/docs_src/dependencies/tutorial011_an_py310.py:17-18` creates the checker "
            "directly in application code. The selected query cases observe the configured "
            "instance through its downstream predicate."
        ),
    ),
    ("advanced/advanced-dependencies.md", "use-the-instance-as-a-dependency"): _workflow(
        "Use the instance as a dependency { #use-the-instance-as-a-dependency }",
        41,
        66,
        _CALLABLE,
        [
            "fastapi.docs.advanced-dependencies.matching-query",
            "fastapi.docs.advanced-dependencies.nonmatching-query",
        ],
        None,
        _HTTP,
        (
            "The requests target the documented route that declares `Depends(checker)`. "
            "Their status, ordered headers, and response bodies expose the checker's accepted "
            "and rejected outcomes. They do not cover class-as-dependency behavior or other "
            "return values."
        ),
        (
            "The pinned example declares the instance in `Depends` and injects its returned "
            "boolean into the path operation "
            "(`../fastapi/docs_src/dependencies/tutorial011_an_py310.py:20-23`). "
            "FastAPI's dependency graph and solver implement that call path "
            "(`../fastapi/fastapi/dependencies/utils.py:314-389,657-819`)."
        ),
    ),
    (
        "advanced/advanced-dependencies.md",
        "dependencies-with-yield-httpexception-except-and-background-tasks",
    ): _excluded(
        (
            "Dependencies with `yield`, `HTTPException`, `except` and Background Tasks "
            "{ #dependencies-with-yield-httpexception-except-and-background-tasks }"
        ),
        67,
        163,
        (
            "This heading summarizes several lifecycle changes but specifies no separate "
            "request. Its scope, streaming, yielded-exception, and background-task details "
            "are independently mapped in the child sections."
        ),
        (
            "Each child has a narrower input and observed selector set. Mapping the umbrella "
            "to a union would hide which lifecycle behavior a recipe actually exercises."
        ),
    ),
    ("advanced/advanced-dependencies.md", "dependencies-with-yield-and-scope"): _workflow(
        "Dependencies with `yield` and `scope` { #dependencies-with-yield-and-scope }",
        79,
        88,
        _SCOPE,
        ["fastapi.docs.advanced-dependencies.scope-timing"],
        ["nested-request-scope", "named-function-scope", "http-scope-cleanup"],
        _HTTP_BODY_STATUS,
        (
            "The selected requests compare a yielded request-scoped resource used by a "
            "StreamingResponse with a function-scoped resource, then read the cleanup event "
            "state. Status and body bytes expose resource state and recorded cleanup. The "
            "case samples these HTTP paths only; WebSocket scope and all dependency nesting "
            "patterns are not claimed."
        ),
        (
            "FastAPI 0.157.0 places the function and request exit stacks around endpoint "
            "execution and response sending (`../fastapi/fastapi/routing.py:143-158`); "
            "dependency scope is validated while building the graph "
            "(`../fastapi/fastapi/dependencies/utils.py:314-389`). "
            "The selected input actions observe these scope timings and their cleanup state."
        ),
    ),
    (
        "advanced/advanced-dependencies.md",
        "dependencies-with-yield-and-streamingresponse-technical-details",
    ): _workflow(
        (
            "Dependencies with `yield` and `StreamingResponse`, Technical Details "
            "{ #dependencies-with-yield-and-streamingresponse-technical-details }"
        ),
        89,
        138,
        _LIFECYCLE,
        ["fastapi.docs.advanced-dependencies.streaming-resource-lifetime"],
        ["stream-resource-open", "stream-resource-cleanup"],
        _HTTP_BODY_STATUS,
        (
            "The first HTTP action streams by iterating a resource yielded by a dependency; "
            "the second reads its cleanup event after streaming. The status and body bytes "
            "observe both the consumed stream and later cleanup. This samples the current "
            "resource-in-stream path, not the historical pre-0.118 behavior."
        ),
        (
            "FastAPI 0.157.0 keeps the request-scoped dependency exit stack around response "
            "sending (`../fastapi/fastapi/routing.py:143-158`). Starlette 1.6.0 sends each "
            "`StreamingResponse` body chunk before its response background step "
            "(`../starlette/starlette/responses.py:248-284`); the selected input verifies "
            "the yielded "
            "resource remains consumable by the stream and is later cleaned up."
        ),
    ),
    ("advanced/advanced-dependencies.md", "use-cases-with-early-exit-code"): _excluded(
        "Use Cases with Early Exit Code { #use-cases-with-early-exit-code }",
        107,
        138,
        (
            "No active input case reproduces the documented SQLModel/SQLAlchemy pattern in "
            "which a yielded session is used only for authorization and explicitly closed "
            "before a slow stream that does not use it. The closest streaming case consumes "
            "the yielded resource during streaming, which is the opposite lifetime."
        ),
        (
            "The page cites `../fastapi/docs_src/dependencies/tutorial013_an_py310.py:19-38` "
            "and `../fastapi/docs_src/dependencies/tutorial014_an_py310.py:24-39`, but "
            "the active streaming recipe exercises an "
            "in-memory inventory, not either session lookup or manual early close. It would "
            "not support those user-code and database-session claims."
        ),
    ),
    (
        "advanced/advanced-dependencies.md",
        "dependencies-with-yield-and-except-technical-details",
    ): _workflow(
        (
            "Dependencies with `yield` and `except`, Technical Details "
            "{ #dependencies-with-yield-and-except-technical-details }"
        ),
        139,
        144,
        _EXCEPT,
        ["fastapi.docs.advanced-dependencies.suppressed-yield-exception"],
        ["observed-original-exceptions"],
        _HTTP_BODY_STATUS,
        (
            "This mapping selects only the `/exception-messages` readback after a yielded "
            "dependency catches an endpoint exception. It observes the returned status and "
            "body; it does not claim the request that triggered teardown. The separate "
            "upstream-test mapping covers the pinned FastAPIError and 500 outcomes."
        ),
        (
            "The page documents catching and suppressing an exception in a yielded dependency. "
            "This documentation link is limited to reading the captured exception value; the "
            "pinned test mapping independently records the FastAPI 0.157.0 guard at "
            "`../fastapi/fastapi/routing.py:143-164` that raises FastAPIError when suppression "
            "occurs before a response exists."
        ),
    ),
    (
        "advanced/advanced-dependencies.md",
        "background-tasks-and-dependencies-with-yield-technical-details",
    ): _workflow(
        (
            "Background Tasks and Dependencies with `yield`, Technical Details "
            "{ #background-tasks-and-dependencies-with-yield-technical-details }"
        ),
        145,
        163,
        _LIFECYCLE,
        ["fastapi.docs.advanced-dependencies.yield-background-cleanup-order"],
        ["response-with-background-task", "observe-background-and-cleanup-completion"],
        _HTTP_BODY_STATUS,
        (
            "One request schedules a background task while using nested yielded resources; "
            "a follow-up request observes task and teardown events. Status and body bytes "
            "show the selected event order. It does not cover task failure, independent task "
            "resource creation, or arbitrary dependency graphs."
        ),
        (
            "Starlette 1.6.0 runs a response background task after sending the response "
            "(`../starlette/starlette/responses.py:163-170`), while FastAPI 0.157.0 manages "
            "yielded dependency exit stacks in the routing response path "
            "(`../fastapi/fastapi/routing.py:143-158`). "
            "The selected pair observes the current background and cleanup order."
        ),
    ),
}
