"""Reviewed mappings for cookie and encoder documentation sections."""


def _workflow(
    heading,
    start_line,
    end_line,
    recipe_path,
    case_id,
    action_ids,
    observation_selectors,
    scope_note,
    rationale,
):
    mapping = {
        "heading": heading,
        "start_line": start_line,
        "end_line": end_line,
        "recipe_path": recipe_path,
        "case_ids": [case_id],
        "observation_selectors": observation_selectors,
        "scope_note": scope_note,
        "rationale": rationale,
    }
    if action_ids is not None:
        mapping["action_ids"] = action_ids
    return mapping


def _excluded(heading, start_line, end_line, exclusion_reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start_line,
        "end_line": end_line,
        "exclusion_reason": exclusion_reason,
        "rationale": rationale,
    }


_COOKIE_MODEL_CASE = "fastapi.docs.request-schema.tutorial-cookie-param-models.cookie-model"
_COOKIE_MODEL_RECIPE = "tests/fixtures/input-recipes/parity/docs-request-schema.yaml"
_COOKIE_PARAMETER_CASE = "fastapi.pending.tutorials-source-wave.cookie-parameter-cases"
_COOKIE_PARAMETER_RECIPE = (
    "tests/fixtures/input-recipes/parity/atlas-pending-tutorials-source-wave.yaml"
)
_HTTP_MODEL = ["http.body.bytes", "http.headers.ordered", "http.status"]
_HTTP_COOKIE = ["http.body.bytes", "http.status"]


DOC_SECTION_CASE_MAPPINGS_COOKIE_ENCODER_20261015 = {
    ("tutorial/cookie-param-models.md", "cookie-parameter-models"): _workflow(
        "Cookie Parameter Models { #cookie-parameter-models }",
        1,
        76,
        _COOKIE_MODEL_RECIPE,
        _COOKIE_MODEL_CASE,
        ["dispatch"],
        _HTTP_MODEL,
        (
            "The selected `dispatch` action sends two cookie fields to the documented "
            "Pydantic model route and observes only HTTP status, ordered headers, and body "
            "bytes. It samples model extraction for this one example. It does not cover "
            "model reuse, Query or Header models, all validation metadata, docs UI behavior, "
            "or the extra-cookie policy described later on the page. Generic Cookie header "
            "parsing is owned by Starlette 1.6.0 and Starlette-RS."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-param-models.md:1-26` "
            "introduces grouping Cookie fields in a Pydantic model and extracting them "
            "from a request. The exact-page-evidenced case "
            "`fastapi.docs.request-schema.tutorial-cookie-param-models.cookie-model` in "
            "`tests/fixtures/input-recipes/parity/docs-request-schema.yaml:248-324` cites "
            "that page with kind `upstream_documentation`; its `dispatch` action sends "
            "`session-id=sid-28; theme=night` and observes status, headers, and body. "
            "FastAPI puts cookie parameters in `dependant.cookie_params` and resolves them "
            "from `request.cookies` (`fastapi/dependencies/utils.py:550-563, 681-696`). "
            "Starlette 1.6.0 parses Cookie headers into `Request.cookies` "
            "(`starlette/requests.py:149-159`); generic parsing and transport remain in the "
            "Starlette / Starlette-RS lane."
        ),
    ),
    ("tutorial/cookie-param-models.md", "cookies-with-a-pydantic-model"): _workflow(
        "Cookies with a Pydantic Model { #cookies-with-a-pydantic-model }",
        19,
        26,
        _COOKIE_MODEL_RECIPE,
        _COOKIE_MODEL_CASE,
        ["dispatch"],
        _HTTP_MODEL,
        (
            "The selected action covers only the documented Pydantic model route: it sends "
            "two cookie fields and observes HTTP status, ordered headers, and body bytes. "
            "The companion OpenAPI action, the docs UI, other field types, invalid values, "
            "and extra-cookie handling are outside this section mapping."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-param-models.md:19-26` "
            "says to declare cookie parameters in a Pydantic model, use it as a `Cookie` "
            "parameter, and extract each field from request cookies. The selected "
            "`dispatch` action of "
            "`fastapi.docs.request-schema.tutorial-cookie-param-models.cookie-model` "
            "(`tests/fixtures/input-recipes/parity/docs-request-schema.yaml:248-284`) "
            "is linked to that exact page using kind `upstream_documentation`. FastAPI "
            "collects cookie fields and resolves values from `request.cookies` "
            "(`fastapi/dependencies/utils.py:550-563, 681-696`); Starlette 1.6.0 owns "
            "Cookie header parsing (`starlette/requests.py:149-159`)."
        ),
    ),
    ("tutorial/cookie-param-models.md", "check-the-docs"): _excluded(
        "Check the Docs { #check-the-docs }",
        27,
        44,
        (
            "This section describes the interactive `/docs` page and browser JavaScript "
            "cookie-submission behavior. The exact-page-evidenced independent case only "
            "dispatches the documented route and reads `/openapi.json`; it does not request "
            "`/docs`, execute the browser UI, or observe a cookie submission from that UI."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-param-models.md:27-44` "
            "describes seeing cookie parameters in `/docs` and the browser limitation when "
            "executing the form. The only case citing this exact page with kind "
            "`upstream_documentation`, "
            "`fastapi.docs.request-schema.tutorial-cookie-param-models.cookie-model`, "
            "has a route `dispatch` action and an `/openapi.json` action "
            "(`tests/fixtures/input-recipes/parity/docs-request-schema.yaml:248-324`); "
            "neither action observes the interactive docs UI."
        ),
    ),
    ("tutorial/cookie-param-models.md", "forbid-extra-cookies"): _excluded(
        "Forbid Extra Cookies { #forbid-extra-cookies }",
        45,
        73,
        (
            "The existing extra-cookie input follows the page's tutorial 002 example, but "
            "its case cites only the example source, not this exact documentation page with "
            "kind `upstream_documentation`. The required page-evidence gate therefore "
            "prevents linking that case to this section."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-param-models.md:45-73` "
            "describes Pydantic `extra='forbid'` and the resulting extra-cookie validation "
            "error. The input-only case "
            "`fastapi.docs-example-wave-f.cookie-model.extra-forbidden` in "
            "`tests/fixtures/input-recipes/parity/"
            "docs-example-wave-f-request-parameter-models.yaml:156-196` "
            "sends an extra cookie and observes status/body, but its source evidence has "
            "only `docs_src/cookie_param_models/tutorial002_*.py` entries of kind "
            "`upstream_documentation_example`; it has no exact page-path evidence. The "
            "other case that cites this page exactly covers the ordinary tutorial 001 model "
            "and cannot establish the extra-cookie behavior."
        ),
    ),
    ("tutorial/cookie-param-models.md", "summary"): _workflow(
        "Summary { #summary }",
        74,
        76,
        _COOKIE_MODEL_RECIPE,
        _COOKIE_MODEL_CASE,
        ["dispatch"],
        _HTTP_MODEL,
        (
            "The recap's claim that Pydantic models can declare FastAPI cookies is sampled "
            "by the ordinary two-field model route. This does not claim coverage of the "
            "separate extra-cookie restriction or docs UI behavior."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-param-models.md:74-76` "
            "summarizes declaring cookies with a Pydantic model. The selected `dispatch` "
            "action in "
            "`tests/fixtures/input-recipes/parity/docs-request-schema.yaml:248-284` "
            "cites the exact page as kind `upstream_documentation` and sends the two cookie "
            "fields used by that documented model. FastAPI collects cookie fields and "
            "passes request-cookie values through its dependency solver "
            "(`fastapi/dependencies/utils.py:550-563, 681-696`)."
        ),
    ),
    ("tutorial/cookie-params.md", "cookie-parameters"): _workflow(
        "Cookie Parameters { #cookie-parameters }",
        1,
        45,
        _COOKIE_PARAMETER_RECIPE,
        _COOKIE_PARAMETER_CASE,
        ["cookie-annotated-absent", "cookie-annotated-present"],
        _HTTP_COOKIE,
        (
            "The selected annotated optional-cookie actions cover an absent value and one "
            "present value, observing only HTTP status and body bytes. They do not cover "
            "required cookies, aliases, validation attributes, OpenAPI, the import identity, "
            "or the browser docs UI note. Cookie-header parsing belongs to Starlette 1.6.0 "
            "and Starlette-RS."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-params.md:1-17` "
            "introduces Cookie parameters and illustrates the annotated declaration. "
            "`fastapi.pending.tutorials-source-wave.cookie-parameter-cases` in "
            "`tests/fixtures/input-recipes/parity/atlas-pending-tutorials-source-wave.yaml:7-285` "
            "contains exact page evidence (`docs/en/docs/tutorial/cookie-params.md`, kind "
            "`upstream_documentation`) and the selected annotated absent/present actions. "
            "FastAPI marks `Cookie` as `ParamTypes.cookie` (`fastapi/params.py:387-389`) "
            "and extracts cookie fields from `request.cookies` "
            "(`fastapi/dependencies/utils.py:550-563, 681-696`); Starlette 1.6.0 parses "
            "the Cookie header (`starlette/requests.py:149-159`)."
        ),
    ),
    ("tutorial/cookie-params.md", "import-cookie"): _excluded(
        "Import `Cookie` { #import-cookie }",
        5,
        10,
        (
            "This section shows the Python import statement. The exact-page-evidenced "
            "Cookie tutorial case exercises route requests but observes no import binding, "
            "public export identity, or callable signature, so it cannot substantiate this "
            "heading."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-params.md:5-10` asks the "
            "reader to import `Cookie` and includes the import line from the example. The "
            "available case `fastapi.pending.tutorials-source-wave.cookie-parameter-cases` "
            "cites the exact page with kind `upstream_documentation`, but its observations "
            "are only HTTP status and body for requests "
            "(`tests/fixtures/input-recipes/parity/"
            "atlas-pending-tutorials-source-wave.yaml:7-285`). "
            "No selected observation establishes the import/export binding itself."
        ),
    ),
    ("tutorial/cookie-params.md", "recap"): _workflow(
        "Recap { #recap }",
        43,
        45,
        _COOKIE_PARAMETER_RECIPE,
        _COOKIE_PARAMETER_CASE,
        ["cookie-annotated-absent", "cookie-annotated-present"],
        _HTTP_COOKIE,
        (
            "The recap's Cookie declaration pattern is sampled by one optional annotated "
            "cookie with its absent and present input forms. Only HTTP status/body are "
            "observed; required parameters, aliases, OpenAPI, imports, and docs UI are not "
            "claimed."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/cookie-params.md:43-45` recaps "
            "declaring cookies with `Cookie`. The selected annotated absent/present actions "
            "in `fastapi.pending.tutorials-source-wave.cookie-parameter-cases` "
            "(`tests/fixtures/input-recipes/parity/"
            "atlas-pending-tutorials-source-wave.yaml:7-285`) "
            "cite this exact page with kind `upstream_documentation`. FastAPI tags Cookie "
            "parameters as cookies (`fastapi/params.py:387-389`) and resolves them from "
            "request cookies (`fastapi/dependencies/utils.py:681-696`)."
        ),
    ),
    ("reference/encoders.md", "@line:1"): _workflow(
        "Encoders - `jsonable_encoder`",
        1,
        3,
        "tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml",
        "fastapi.direct-api-reference-wave.encoder-reference-dataclass",
        None,
        ["python.attribute_value", "python.signature"],
        (
            "The direct API probe encodes one dataclass and observes the returned Python "
            "value plus the callable signature. It does not cover the encoder's full input "
            "type matrix, options, recursive edge cases, exception behavior, or HTTP/ASGI "
            "use."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/reference/encoders.md:1-3` documents "
            "`fastapi.encoders.jsonable_encoder`. The case "
            "`fastapi.direct-api-reference-wave.encoder-reference-dataclass` "
            "(`tests/fixtures/input-recipes/parity/direct-api-reference-wave.yaml:61-81`) "
            "cites that exact page with kind `upstream_documentation` and observes the "
            "dataclass return value and signature. FastAPI defines the callable and its "
            "filter/conversion arguments at `fastapi/encoders.py:129-190`; Pydantic "
            "conversion primitives remain owned by Pydantic, and this direct API workflow "
            "does not cross the Starlette 1.6.0 / Starlette-RS HTTP boundary."
        ),
    ),
    ("tutorial/encoder.md", "json-compatible-encoder"): _workflow(
        "JSON Compatible Encoder { #json-compatible-encoder }",
        1,
        35,
        "tests/fixtures/input-recipes/parity/encoding.yaml",
        "fastapi.jsonable-encoder.tutorial.datetime-model",
        None,
        ["python.attribute_value", "python.signature"],
        (
            "The independent direct call uses the tutorial's Pydantic model and datetime, "
            "observing its JSON-compatible Python return value and callable signature. It "
            "does not perform database I/O or HTTP/ASGI dispatch and does not cover other "
            "encoder input types or option combinations."
        ),
        (
            "Pinned FastAPI 0.141.1 `docs/en/docs/tutorial/encoder.md:1-35` introduces "
            "conversion to JSON-compatible Python values and includes the Pydantic model / "
            "datetime example. The case `fastapi.jsonable-encoder.tutorial.datetime-model` "
            "(`tests/fixtures/input-recipes/parity/encoding.yaml:7-30`) cites that exact "
            "page with kind `upstream_documentation` and observes the direct call's return "
            "value and signature. FastAPI handles BaseModel inputs through `model_dump` in "
            "JSON mode and recursively encodes the result (`fastapi/encoders.py:243-258`); "
            "Pydantic owns its model serialization primitives. No Starlette 1.6.0 or "
            "Starlette-RS HTTP behavior is claimed by this Python-callable sample."
        ),
    ),
}
