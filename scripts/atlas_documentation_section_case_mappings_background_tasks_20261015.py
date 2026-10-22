"""Reviewed section mappings for FastAPI's background-tasks tutorial."""

_PAGE = "tutorial/background-tasks.md"

_DOC_HTTP_RECIPE = "tests/fixtures/input-recipes/parity/docs-http-behaviors.yaml"
_DOC_HTTP_CASE = "fastapi.docs.documentation-wave.http-behaviors.background-task-effect"
_KEYWORD_RECIPE = (
    "tests/fixtures/input-recipes/parity/background-task-keyword-arguments-tutorial-review.yaml"
)
_KEYWORD_CASE = (
    "fastapi.test.test-tutorial-test-background-tasks-test-tutorial001.keyword-argument-forwarding"
)
_DEPENDENCY_RECIPE = (
    "tests/fixtures/input-recipes/parity/background-tasks-injection-precedence.yaml"
)
_DEPENDENCY_CASE = (
    "fastapi.test.test-response-dependency."
    "test-background-tasks-with-depends-annotated.normal-response"
)
_ALIAS_RECIPE = "tests/fixtures/input-recipes/parity/root-alias-identity.yaml"
_ALIAS_CASE = "fastapi.root-alias-identity.http-reexports"

_HTTP = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_BODY = ["http.body.bytes", "http.status"]


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


DOC_SECTION_CASE_MAPPINGS_BACKGROUND_TASKS_20261015 = {
    (_PAGE, "background-tasks"): _workflow(
        "Background Tasks { #background-tasks }",
        1,
        86,
        _DOC_HTTP_RECIPE,
        _DOC_HTTP_CASE,
        ["dispatch", "observe-state"],
        _HTTP,
        (
            "The independent POST route accepts one BackgroundTasks parameter, queues one "
            "in-memory effect, and a later GET returns the recorded state. The selected "
            "responses show the successful dispatch and follow-up observation; they do not "
            "measure response-send ordering or worker latency."
        ),
        (
            "The pinned page introduces tasks that run after returning a response and gives "
            "email and processing examples (docs/en/docs/tutorial/background-tasks.md:1-12). "
            "FastAPI 0.157.0 classifies the injected parameter in "
            "../fastapi/fastapi/dependencies/utils.py:392-413, injects it at :803-819, "
            "and attaches it to response arguments in ../fastapi/fastapi/routing.py:380-395. "
            "Starlette 1.6.0 owns generic execution after the response send."
        ),
    ),
    (_PAGE, "using-backgroundtasks"): _workflow(
        "Using `BackgroundTasks` { #using-backgroundtasks }",
        14,
        21,
        _DOC_HTTP_RECIPE,
        _DOC_HTTP_CASE,
        ["dispatch", "observe-state"],
        _HTTP,
        (
            "One independent route declares the public BackgroundTasks parameter, returns a "
            "successful HTTP response, and exposes its queued effect from a later request. "
            "This samples one injection path and does not inspect the import object's identity "
            "or every parameter annotation form."
        ),
        (
            "The pinned section shows the BackgroundTasks parameter and says FastAPI creates "
            "and supplies the object (docs/en/docs/tutorial/background-tasks.md:14-20). "
            "FastAPI 0.157.0 recognizes StarletteBackgroundTasks subclasses in "
            "../fastapi/fastapi/dependencies/utils.py:407-409 and supplies the shared value at "
            ":803-819; the linked case observes the route response and subsequent public "
            "state response."
        ),
    ),
    (_PAGE, "create-a-task-function"): _excluded(
        "Create a task function { #create-a-task-function }",
        22,
        35,
        (
            "This section describes user-authored callable definitions and generic sync/async "
            "task invocation. FastAPI's BackgroundTasks subclass only forwards add_task to "
            "Starlette; Starlette 1.6.0 owns callable classification, awaiting, and worker-pool "
            "dispatch."
        ),
        (
            "The pinned text says task functions may be ordinary or async callables and can "
            "receive parameters (docs/en/docs/tutorial/background-tasks.md:22-35). "
            "FastAPI 0.157.0 forwards the registration call in "
            "../fastapi/fastapi/background.py:41-62. Starlette 1.6.0 selects async invocation "
            "or run_in_threadpool in ../starlette/starlette/background.py:12-23; the section "
            "therefore adds no FastAPI-owned task-callable behavior to this crosswalk."
        ),
    ),
    (_PAGE, "add-the-background-task"): _workflow(
        "Add the background task { #add-the-background-task }",
        36,
        47,
        _KEYWORD_RECIPE,
        _KEYWORD_CASE,
        ["queue-delivery", "read-delivery-ledger"],
        _HTTP,
        (
            "The independent route passes one path-derived positional value and one keyword "
            "value to add_task, then a separate GET returns the recorded effect. It samples "
            "one positional-plus-keyword call; it does not establish all signatures, callable "
            "modes, or execution-order semantics."
        ),
        (
            "The pinned section describes calling add_task from a path operation and its "
            "function, positional-argument, and keyword-argument inputs "
            "(docs/en/docs/tutorial/background-tasks.md:36-46). FastAPI 0.157.0 declares "
            "*args/**kwargs and forwards both in ../fastapi/fastapi/background.py:41-62. The "
            "independent recipe uses a different route, target, task, and keyword label; the "
            "follow-up response exposes the effect."
        ),
    ),
    (_PAGE, "dependency-injection"): _workflow(
        "Dependency Injection { #dependency-injection }",
        48,
        63,
        _DEPENDENCY_RECIPE,
        _DEPENDENCY_CASE,
        ["normal-response", "normal-task-effects"],
        _HTTP_BODY,
        (
            "The independent case injects BackgroundTasks into nested and parent dependencies "
            "and the path operation; the selected follow-up response returns their recorded "
            "effects. It samples this merge path only and does not claim every dependency "
            "graph or task failure mode."
        ),
        (
            "The pinned example declares BackgroundTasks in dependencies and a path operation, "
            "then describes the shared collection and merged tasks "
            "(docs/en/docs/tutorial/background-tasks.md:48-62). FastAPI 0.157.0 propagates the "
            "solved task collection through ../fastapi/fastapi/dependencies/utils.py:803-819 "
            "and attaches it to the response in ../fastapi/fastapi/routing.py:380-395. "
            "Starlette owns execution of the attached collection."
        ),
    ),
    (_PAGE, "technical-details"): _workflow(
        "Technical Details { #technical-details }",
        64,
        75,
        _ALIAS_RECIPE,
        _ALIAS_CASE,
        ["read-http-identity-relations"],
        _HTTP_BODY,
        (
            "The returned JSON identity bit checks that fastapi.BackgroundTasks is the same "
            "public class as fastapi.background.BackgroundTasks. This does not test its "
            "Starlette base-class identity or the separate Starlette BackgroundTask plus "
            "Response.background construction described later in the section."
        ),
        (
            "The pinned section says BackgroundTasks is made available from FastAPI and "
            "distinguishes it from Starlette's singular BackgroundTask "
            "(docs/en/docs/tutorial/background-tasks.md:64-72). FastAPI 0.157.0 exports the "
            "class at ../fastapi/fastapi/__init__.py:8 and defines its subclass of "
            "StarletteBackgroundTasks at ../fastapi/fastapi/background.py:6-13. The linked "
            "case returns the root-to-public-module identity check; generic BackgroundTask "
            "execution and Response attachment remain Starlette-owned."
        ),
    ),
    (_PAGE, "caveat"): _excluded(
        "Caveat { #caveat }",
        76,
        83,
        (
            "The section recommends when to choose a distributed task queue and describes "
            "deployment/configuration tradeoffs; it specifies no FastAPI request or public API "
            "behavior."
        ),
        (
            "The pinned text discusses heavy computation, sharing process memory, and external "
            "tools such as Celery, RabbitMQ, and Redis "
            "(docs/en/docs/tutorial/background-tasks.md:76-82). These are architecture and "
            "deployment recommendations, not a distinct FastAPI operation that an input-only "
            "HTTP case can observe."
        ),
    ),
    (_PAGE, "recap"): _excluded(
        "Recap { #recap }",
        84,
        86,
        (
            "The recap restates BackgroundTasks injection in path operations and dependencies; "
            "those behaviors are already mapped to their narrower sections above, and the "
            "recap adds no distinct request input or observation."
        ),
        (
            "The only sentence in the pinned recap says to import and use BackgroundTasks from "
            "path-operation functions and dependencies to add tasks "
            "(docs/en/docs/tutorial/background-tasks.md:84-86). The path-operation injection, "
            "add_task arguments, and dependency aggregation are mapped separately under "
            "`using-backgroundtasks`, `add-the-background-task`, and `dependency-injection`."
        ),
    ),
}
