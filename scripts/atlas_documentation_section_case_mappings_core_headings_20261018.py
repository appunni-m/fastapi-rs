"""Reviewed mappings for core no-signal tutorial headings."""

_CLASS_RECIPE = "tests/fixtures/input-recipes/parity/core-headings-fastapi-class-20261018.yaml"
_TAG_ORDER_RECIPE = (
    "tests/fixtures/input-recipes/parity/core-headings-openapi-tag-order-20261018.yaml"
)


def _workflow(
    heading,
    start,
    end,
    recipe,
    case_ids,
    actions,
    selectors,
    feature_ids,
    note,
    rationale,
):
    mapping = {
        "status": "workflow",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": recipe,
        "case_ids": case_ids,
        "observation_selectors": selectors,
        "feature_ids": feature_ids,
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


DOC_SECTION_CASE_MAPPINGS_CORE_HEADINGS_20261018 = {
    ("tutorial/first-steps.md", "check-it"): _workflow(
        "Check it { #check-it }",
        65,
        74,
        "tests/fixtures/input-recipes/parity/first-steps-application-testing-upstream.yaml",
        ["fastapi.first-steps.async-home"],
        ["home"],
        ["http.body.bytes", "http.status"],
        ["app-routing", "response-serialization"],
        (
            "The existing independent root-route input selects status and exact JSON body bytes, "
            "matching the documented route output. It does not claim browser navigation or the "
            "local Uvicorn process output shown in the surrounding tutorial."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/tutorial/first-steps.md:65-74 tells the reader "
            "to request `/` and shows `{'message': 'Hello World'}`. The linked "
            "docs_src/first_steps/tutorial001_py310.py:6-8 defines that GET route and"
            " return value; "
            "the existing input-only `fastapi.first-steps.async-home` case observes its HTTP "
            "status and body bytes."
        ),
    ),
    ("tutorial/first-steps.md", "data-schema"): _excluded(
        'Data "schema" { #data-schema }',
        105,
        110,
        (
            "This span defines the general term for the shape of JSON data; it names no "
            "FastAPI option, model declaration, request, or generated-schema behavior."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 105-110 give standards vocabulary only. The "
            "application's concrete OpenAPI generation is covered by the separate "
            "`Check the openapi.json` section, and this paragraph adds no runtime contract."
        ),
    ),
    ("tutorial/first-steps.md", "schema"): _excluded(
        '"Schema" { #schema }',
        95,
        98,
        (
            "This span defines the generic word schema and adds no FastAPI operation or "
            "observable output."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/tutorial/first-steps.md:95-98 explains schema "
            "as an abstract description. The FastAPI OpenAPI document and API-specific schema "
            "behavior are reviewed in the neighboring OpenAPI sections."
        ),
    ),
    ("tutorial/first-steps.md", "deploy-your-app-optional"): _excluded(
        "Deploy your app (optional) { #deploy-your-app-optional }",
        207,
        228,
        (
            "This section documents the optional `fastapi deploy` command, FastAPI Cloud "
            "deployment, app discovery, and browser authentication rather than behavior of "
            "an already constructed FastAPI application."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 209-227 describe a CLI process that discovers and "
            "deploys user code to the external FastAPI Cloud service. CLI, browser, and cloud "
            "deployment behavior is outside the FastAPI library's ASGI runtime contract."
        ),
    ),
    ("tutorial/first-steps.md", "step-1-import-fastapi"): _workflow(
        "Step 1: import `FastAPI` { #step-1-import-fastapi }",
        231,
        244,
        _CLASS_RECIPE,
        ["fastapi.docs.core-headings.fastapi-class-instance"],
        ["class-and-instance-contract"],
        ["http.body.bytes", "http.status"],
        ["app-routing"],
        (
            "The independent request returns its class and binding identity facts as response "
            "JSON. This section claims only the exact response status and body; construction "
            "outcomes are not attributed to this heading."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 231-244 identify the root `FastAPI` import as a "
            "class and state its direct Starlette inheritance. The independent input observes "
            "those public class and identity facts in the exact response body; generic ASGI "
            "behavior remains Starlette's contract."
        ),
    ),
    ("tutorial/first-steps.md", "step-2-create-a-fastapi-instance"): _workflow(
        'Step 2: create a `FastAPI` "instance" { #step-2-create-a-fastapi-instance }',
        245,
        252,
        _CLASS_RECIPE,
        ["fastapi.docs.core-headings.fastapi-class-instance"],
        ["class-and-instance-contract"],
        ["http.body.bytes", "http.status"],
        ["app-routing"],
        (
            "The independent request returns the instance's exact FastAPI and Starlette type "
            "facts as response JSON. This section claims only the exact response status and "
            "body, not every method on the application."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 245-252 describe the result of calling `FastAPI()` "
            "as the application instance used to define an API. The case observes construction "
            "and the resulting public instance type under the `app-routing` feature."
        ),
    ),
    ("tutorial/first-steps.md", "step-6-deploy-it"): _excluded(
        "Step 6: Deploy it { #step-6-deploy-it }",
        400,
        419,
        (
            "This recap step and its children describe deployment to FastAPI Cloud or other "
            "providers; no input exercises FastAPI library behavior."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 400-419 contain a `fastapi deploy` instruction and "
            "external cloud-provider guidance. The CLI and hosting process are outside the "
            "FastAPI application's ASGI runtime contract."
        ),
    ),
    ("tutorial/first-steps.md", "about-fastapi-cloud"): _excluded(
        "About FastAPI Cloud { #about-fastapi-cloud }",
        404,
        413,
        (
            "This section describes the external FastAPI Cloud service, its product experience, "
            "and sponsorship; it specifies no behavior of the FastAPI library."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 404-413 are service description and sponsorship "
            "information. FastAPI Cloud's build, deployment, and access behavior belongs to "
            "that external service."
        ),
    ),
    ("tutorial/first-steps.md", "deploy-to-other-cloud-providers"): _excluded(
        "Deploy to other cloud providers { #deploy-to-other-cloud-providers }",
        414,
        419,
        (
            "This section gives general hosting advice and directs readers to cloud-provider "
            "guides; it defines no FastAPI runtime input or output."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 414-419 discuss where user applications may be "
            "deployed. Cloud-provider deployment behavior is outside the package's library "
            "contract."
        ),
    ),
    ("tutorial/handling-errors.md", "reuse-fastapis-exception-handlers"): _workflow(
        "Reuse **FastAPI**'s exception handlers { #reuse-fastapis-exception-handlers }",
        238,
        244,
        "tests/fixtures/input-recipes/parity/handling-errors-doc-tutorial006-review.yaml",
        [
            "fastapi.docs-example.handling-errors.tutorial006.delegated-http-error",
            "fastapi.docs-example.handling-errors.tutorial006.delegated-validation-error",
        ],
        None,
        ["http.body.bytes", "http.status"],
        ["public-api-errors", "request-validation"],
        (
            "The existing independent workload imports and invokes both documented default "
            "handlers, with one HTTP exception response and one request-validation response. "
            "The selected outputs do not cover arbitrary custom handlers or every exception "
            "type."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 238-244 direct users to import and reuse "
            "`http_exception_handler` and `request_validation_exception_handler`. The linked "
            "workload performs those imports and registrations, then selects both response "
            "behaviors; Starlette 1.6.0 owns generic exception dispatch."
        ),
    ),
    ("tutorial/metadata.md", "order-of-tags"): _workflow(
        "Order of tags { #order-of-tags }",
        89,
        94,
        _TAG_ORDER_RECIPE,
        ["fastapi.docs.core-headings.openapi-tag-order"],
        ["read-openapi-tag-order"],
        ["docs.response.status", "http.status", "openapi.document"],
        ["openapi-docs"],
        (
            "The independent input selects the full generated `/tags` array, including its "
            "order. That OpenAPI list is the input to the documentation UI; the case does not "
            "run a browser or claim UI rendering behavior."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 89-94 state that the order of `openapi_tags` "
            "metadata controls the order exposed to the docs UI. The case compares the full "
            "generated OpenAPI tag list for deliberately nonalphabetic metadata, tying the "
            "documented behavior to the `openapi-docs` feature."
        ),
    ),
    ("tutorial/metadata.md", "check-the-docs"): _workflow(
        "Check the docs { #check-the-docs }",
        83,
        88,
        "tests/fixtures/input-recipes/parity/constructor-openapi-tags.yaml",
        ["fastapi.applications.constructor.openapi-tags"],
        ["observe-openapi-tag-metadata"],
        ["docs.response.status", "http.status", "openapi.document"],
        ["openapi-docs"],
        (
            "The independent case selects the configured tag objects in generated `/openapi.json`, "
            "the data consumed by the interactive docs UI. It does not run a browser or claim "
            "Swagger UI Markdown rendering."
        ),
        (
            "Pinned FastAPI 0.157.0 docs/en/docs/tutorial/metadata.md:83-88 states that configured "
            "tag metadata appears in the docs. The linked"
            " docs_src/metadata/tutorial004_py310.py:3-18 "
            "sets names, descriptions, and externalDocs through `FastAPI(openapi_tags=...)`; the "
            "existing input-only `fastapi.applications.constructor.openapi-tags` case selects the "
            "generated OpenAPI `/tags` array."
        ),
    ),
    ("tutorial/response-model.md", "type-annotations-and-tooling"): _excluded(
        "Type Annotations and Tooling { #type-annotations-and-tooling }",
        151,
        160,
        (
            "This section explains what editors, mypy, and other static type tools accept; it "
            "does not describe a FastAPI runtime action."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 151-160 discuss the static subtype relation between "
            "`BaseUser` and `UserIn` as understood by Python tooling. Runtime response "
            "filtering is separately covered by the adjacent FastAPI data-filtering section."
        ),
    ),
    ("tutorial/security/first-steps.md", "how-it-looks"): _excluded(
        "How it looks { #how-it-looks }",
        15,
        18,
        (
            "This is a navigation sentence introducing the example-first order of the page; "
            "it states no security or FastAPI runtime behavior."
        ),
        (
            "Pinned FastAPI 0.157.0 lines 15-18 only tell readers to run an example before "
            "returning to its explanation. The OAuth2 behavior and OpenAPI security projection "
            "are described in the later sections."
        ),
    ),
}
