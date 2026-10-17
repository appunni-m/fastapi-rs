"""Reviewed dispositions for no-signal advanced documentation headings.

Source pin: FastAPI 0.141.1 at
95f8322ee1dcda7ceace7b1c4f6c9915b36d748f. Workflow inputs are independently
authored; external test tools, generic Starlette responses, Python language
semantics, and generated client behavior are not attributed to FastAPI.
"""

_PLAIN_TEXT = (
    "tests/fixtures/input-recipes/parity/"
    "docs-custom-response-plain-text-response-class-20261018.yaml"
)


def _workflow(heading, start, end, recipe, cases, actions, selectors, features, note, rationale):
    return {
        "status": "workflow",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": cases,
        "action_ids": actions,
        "observation_selectors": selectors,
        "feature_ids": features,
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


DOC_SECTION_CASE_MAPPINGS_ADVANCED_HEADINGS_20261018 = {
    ("advanced/async-tests.md", "pytest-mark-anyio"): _excluded(
        "pytest.mark.anyio { #pytest-mark-anyio }",
        9,
        12,
        (
            "The section documents AnyIO's pytest plugin for running async test functions,"
            " an external test-runner contract."
        ),
        (
            "Pinned FastAPI 0.141.1 docs/en/docs/advanced/async-tests.md:9-12 discusses the"
            " AnyIO marker and pytest scheduling. It specifies no FastAPI application input"
            " or runtime output; the route sample is separately reviewed under Example."
        ),
    ),
    ("advanced/async-tests.md", "httpx"): _excluded(
        "HTTPX { #httpx }",
        13,
        20,
        (
            "This section explains how to use HTTPX from async tests and the sync-to-async"
            " TestClient bridge; it does not define FastAPI-owned testing behavior."
        ),
        (
            "Pinned docs/en/docs/advanced/async-tests.md:13-20 describes calling an ASGI"
            " app from async tests. FastAPI's fastapi/testclient.py is a direct Starlette"
            " re-export, and the TestClient bridge belongs to Starlette 1.6.0; the ASGI"
            " route itself is reviewed under Example."
        ),
    ),
    ("advanced/async-tests.md", "run-it"): _excluded(
        "Run it { #run-it }",
        41,
        54,
        (
            "The section gives the shell command for invoking pytest and contains no"
            " application behavior."
        ),
        (
            "Pinned docs/en/docs/advanced/async-tests.md:41-54 shows uv run pytest. Process"
            " invocation and pytest execution are external tooling, not FastAPI ASGI inputs"
            " or outputs."
        ),
    ),
    ("advanced/custom-response.md", "htmlresponse"): _excluded(
        "`HTMLResponse` { #htmlresponse }",
        125,
        128,
        (
            "The section describes the generic HTMLResponse constructor result; FastAPI"
            " response-class selection is covered by the separate HTML Response section."
        ),
        (
            "Pinned docs/en/docs/advanced/custom-response.md:125-128 says HTMLResponse"
            " accepts text or bytes and returns an HTML response. It has no FastAPI route"
            " or response_class declaration. FastAPI integration is sampled under the HTML"
            " Response heading, while response encoding is owned by Starlette 1.6.0."
        ),
    ),
    ("advanced/custom-response.md", "plaintextresponse"): _workflow(
        "`PlainTextResponse` { #plaintextresponse }",
        129,
        134,
        _PLAIN_TEXT,
        ["fastapi.docs.custom-response.plain-text-response-class"],
        ["request-plain-text"],
        ["http.body.bytes", "http.headers.ordered", "http.status"],
        ["response-serialization"],
        (
            "The independent GET returns a synthetic string from a route declared with"
            " response_class=PlainTextResponse and observes status, ordered headers, and"
            " body bytes. It samples one successful string response-class selection; it"
            " does not cover bytes, custom response constructors, other classes, direct"
            " Response returns, or OpenAPI."
        ),
        (
            "Pinned docs/en/docs/advanced/custom-response.md:129-134 describes"
            " PlainTextResponse and includes"
            " docs_src/custom_response/tutorial005_py310.py:1-10, where a FastAPI GET route"
            " sets response_class=PlainTextResponse and returns a string. FastAPI 0.141.1"
            " resolves the route response class in fastapi/routing.py:396-399 and"
            " constructs it for a non-Response endpoint value at :711-747. The independent"
            " case selects HTTP status, ordered headers, and body bytes; Starlette 1.6.0"
            " owns the generic PlainTextResponse wire representation."
        ),
    ),
    ("advanced/generate-clients.md", "using-the-sdk"): _excluded(
        "Using the SDK { #using-the-sdk }",
        55,
        78,
        (
            "The section describes editor autocomplete and inline errors in generated"
            " TypeScript client code, which are client-generator and editor behaviors."
        ),
        (
            "Pinned docs/en/docs/advanced/generate-clients.md:55-78 discusses importing the"
            " generated client and shows autocomplete screenshots for request payloads and"
            " responses. Those outputs are produced by the TypeScript SDK and editor, not"
            " by FastAPI's runtime."
        ),
    ),
    ("advanced/generate-clients.md", "generate-a-typescript-client-with-tags"): _excluded(
        "Generate a TypeScript Client with Tags { #generate-a-typescript-client-with-tags }",
        87,
        99,
        (
            "This section describes how an external TypeScript client generator groups"
            " generated code by OpenAPI tags."
        ),
        (
            "Pinned docs/en/docs/advanced/generate-clients.md:87-99 attributes ItemsService"
            " and UsersService grouping to client generation. FastAPI's OpenAPI tag"
            " projection is a separate contract; this span defines no FastAPI request"
            " handling or response behavior."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "the-time-to-answer-helps-the-attackers"): _excluded(
        "The time to answer helps the attackers { #the-time-to-answer-helps-the-attackers }",
        83,
        88,
        (
            "The section explains a timing side-channel threat model for ordinary string"
            " comparisons; it does not specify a FastAPI response contract."
        ),
        (
            "Pinned docs/en/docs/advanced/security/http-basic-auth.md:83-88 describes"
            " inferring matching username characters from response timing. This is"
            " explanatory security prose, not an independently selected FastAPI"
            " input/output behavior; the credential-check route is reviewed under its own"
            " section."
        ),
    ),
    ("advanced/security/http-basic-auth.md", "a-professional-attack"): _excluded(
        'A "professional" attack { #a-professional-attack }',
        89,
        94,
        (
            "The section estimates an attacker's scripted guessing process and rate,"
            " outside the FastAPI runtime contract."
        ),
        (
            "Pinned docs/en/docs/advanced/security/http-basic-auth.md:89-94 discusses an"
            " attacker program issuing many guesses and recovering credentials over time."
            " It defines neither a FastAPI API input nor an output selector, and does not"
            " provide a reproducible application contract."
        ),
    ),
    ("advanced/strict-content-type.md", "open-internet"): _excluded(
        "Open Internet { #open-internet }",
        66,
        75,
        (
            "This section gives a deployment threat-model recommendation about exposed"
            " versus local-network applications."
        ),
        (
            "Pinned docs/en/docs/advanced/strict-content-type.md:66-75 discusses when the"
            " preceding browser attack is relevant and recommends authentication for"
            " internet-facing privileged endpoints. It specifies no FastAPI"
            " request-processing behavior."
        ),
    ),
    ("advanced/using-request-directly.md", "request-documentation"): _excluded(
        "`Request` documentation { #request-documentation }",
        46,
        56,
        (
            "The section links to Starlette's Request documentation and notes FastAPI's"
            " convenience re-export; it adds no distinct runtime operation."
        ),
        (
            "Pinned docs/en/docs/advanced/using-request-directly.md:46-56 points readers to"
            " Starlette and states that FastAPI exposes the same Request as a convenience."
            " The direct Request injection behavior is mapped under Use the Request object"
            " directly; export identity belongs to the API manifest, and Request semantics"
            " belong to Starlette 1.6.0."
        ),
    ),
    ("async.md", "technical-details"): _excluded(
        "Technical Details { #technical-details }",
        57,
        66,
        (
            "This heading outlines Python async concepts and links to explanatory sections"
            " without adding a FastAPI operation."
        ),
        (
            "Pinned docs/en/docs/async.md:57-66 introduces coroutines and async/await as"
            " Python language features and lists the following tutorial sections. The"
            " FastAPI path-operation dispatch contract is mapped under its narrower"
            " technical headings."
        ),
    ),
    ("async.md", "concurrency-and-burgers"): _excluded(
        "Concurrency and Burgers { #concurrency-and-burgers }",
        96,
        105,
        (
            "This section introduces a burger analogy to explain concurrency and"
            " parallelism; it defines no application request behavior."
        ),
        (
            "Pinned docs/en/docs/async.md:96-105 contrasts concurrency and parallelism and"
            " introduces a story. The analogy is not a FastAPI API contract or a measurable"
            " performance workload."
        ),
    ),
    ("async.md", "concurrent-burgers"): _excluded(
        "Concurrent Burgers { #concurrent-burgers }",
        106,
        165,
        (
            "This section develops the burger story as a general explanation of"
            " concurrency, waiting, and task switching."
        ),
        (
            "Pinned docs/en/docs/async.md:106-165 describes people, orders, and waiting at"
            " a counter. It contains no FastAPI route, dependency, or ASGI stimulus; the"
            " content explains a general scheduling concept."
        ),
    ),
    ("async.md", "parallel-burgers"): _excluded(
        "Parallel Burgers { #parallel-burgers }",
        166,
        235,
        (
            "This section develops a burger and bank analogy for synchronous work and"
            " parallel workers, not FastAPI behavior."
        ),
        (
            "Pinned docs/en/docs/async.md:166-235 describes cashiers, cooks, and processors"
            " in an analogy. It specifies no FastAPI runtime input or output; Python"
            " process and CPU behavior are outside this section's framework contract."
        ),
    ),
    ("async.md", "is-concurrency-better-than-parallelism"): _excluded(
        "Is concurrency better than parallelism? { #is-concurrency-better-than-parallelism }",
        256,
        292,
        (
            "This section compares general concurrency and parallelism for waiting versus"
            " CPU-bound work, with no FastAPI operation to observe."
        ),
        (
            "Pinned docs/en/docs/async.md:256-292 uses a house-cleaning analogy and lists"
            " CPU-bound examples such as image processing and machine learning. The claims"
            " concern workload characteristics, not FastAPI request dispatch or a"
            " parity-observable result."
        ),
    ),
    ("async.md", "concurrency-parallelism-web-machine-learning"): _excluded(
        (
            "Concurrency + Parallelism: Web + Machine Learning {"
            " #concurrency-parallelism-web-machine-learning }"
        ),
        293,
        302,
        (
            "The section gives broad suitability and deployment guidance for web and"
            " machine-learning workloads, not a specific FastAPI runtime guarantee."
        ),
        (
            "Pinned docs/en/docs/async.md:293-302 says FastAPI can be used for concurrent"
            " web and parallel CPU-bound workloads, then points to deployment guidance. It"
            " supplies no route, input, output, or bounded concurrency contract that an"
            " ASGI workflow could observe."
        ),
    ),
    ("async.md", "write-your-own-async-code"): _excluded(
        "Write your own async code { #write-your-own-async-code }",
        364,
        373,
        (
            "This section recommends user-authored AnyIO and Asyncer code for advanced"
            " concurrency patterns."
        ),
        (
            "Pinned docs/en/docs/async.md:364-373 discusses AnyIO, asyncio, Trio, and"
            " Asyncer for code a user writes directly. It defines no FastAPI endpoint or"
            " dependency behavior; the framework's coroutine path-operation dispatch is"
            " covered under the technical runtime sections."
        ),
    ),
    ("async.md", "coroutines"): _excluded(
        "Coroutines { #coroutines }",
        388,
        393,
        (
            "This section defines Python coroutines and compares them with Go goroutines;"
            " it is language-concept material."
        ),
        (
            "Pinned docs/en/docs/async.md:388-393 describes values returned by async def"
            " and their suspension at await. It does not define how FastAPI invokes path"
            " operations; that behavior is mapped under Path operation functions."
        ),
    ),
    ("async.md", "conclusion"): _excluded(
        "Conclusion { #conclusion }",
        394,
        403,
        (
            "The section summarizes Python's async and coroutine terminology and makes a"
            " broad performance statement without specifying an independent operation."
        ),
        (
            "Pinned docs/en/docs/async.md:394-403 restates Python async syntax and says it"
            " powers FastAPI through Starlette. It adds no route or measurable behavior;"
            " path-operation and dependency dispatch are covered by narrower mappings."
        ),
    ),
    ("python-types.md", "simple-types"): _excluded(
        "Simple types { #simple-types }",
        125,
        137,
        (
            "This section lists Python built-in types and shows a standalone function"
            " annotation, without a FastAPI parameter or request."
        ),
        (
            "Pinned docs/en/docs/python-types.md:125-137 explains int, float, bool, bytes,"
            " and links docs_src/python_types/tutorial005_py310.py. The span contains no"
            " FastAPI route; FastAPI request analysis is reviewed under Type hints in"
            " FastAPI."
        ),
    ),
    ("python-types.md", "list"): _excluded(
        "List { #list }",
        163,
        194,
        (
            "This section demonstrates Python list[str] annotations and editor support for"
            " a local variable, not FastAPI request handling."
        ),
        (
            "Pinned docs/en/docs/python-types.md:163-194 links"
            " docs_src/python_types/tutorial006_py310.py and explains the type of items in"
            " a Python list. It defines no path operation or request parameter; FastAPI's"
            " use of typed parameters is mapped under Type hints in FastAPI."
        ),
    ),
    ("python-types.md", "tuple-and-set"): _excluded(
        "Tuple and Set { #tuple-and-set }",
        195,
        205,
        (
            "This section explains Python tuple and set type parameters for local values,"
            " not FastAPI runtime behavior."
        ),
        (
            "Pinned docs/en/docs/python-types.md:195-205 links"
            " docs_src/python_types/tutorial007_py310.py and describes a tuple and set"
            " variable. There is no FastAPI route declaration or request input in this"
            " span."
        ),
    ),
    ("python-types.md", "dict"): _excluded(
        "Dict { #dict }",
        206,
        221,
        (
            "This section describes Python dictionary key and value annotations on a local"
            " value, not a FastAPI request contract."
        ),
        (
            "Pinned docs/en/docs/python-types.md:206-221 links"
            " docs_src/python_types/tutorial008_py310.py and explains dict[str, float]. It"
            " does not define a route or request body; FastAPI parameter conversion is"
            " reviewed under Type hints in FastAPI."
        ),
    ),
    ("python-types.md", "union"): _excluded(
        "Union { #union }",
        222,
        235,
        (
            "This section explains Python's union annotation syntax using a standalone"
            " value example; it does not document FastAPI validation behavior."
        ),
        (
            "Pinned docs/en/docs/python-types.md:222-235 explains int | str and includes"
            " docs_src/python_types/tutorial008b_py310.py. There is no FastAPI route or"
            " request input in the selected span; FastAPI validation of annotations is"
            " covered under Type hints in FastAPI."
        ),
    ),
    ("python-types.md", "possibly-none"): _excluded(
        "Possibly `None` { #possibly-none }",
        236,
        249,
        (
            "This section explains Python's str | None annotation and editor feedback for"
            " possibly absent values, not FastAPI request validation."
        ),
        (
            "Pinned docs/en/docs/python-types.md:236-249 links"
            " docs_src/python_types/tutorial009_py310.py and discusses the Python union of"
            " str and None. It has no FastAPI endpoint or request input; FastAPI's"
            " typed-parameter behavior is mapped separately under Type hints in FastAPI."
        ),
    ),
}
