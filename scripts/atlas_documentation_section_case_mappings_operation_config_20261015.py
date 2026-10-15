"""Reviewed documentation section mappings for metadata and route configuration."""


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


_META_PAGE = "tutorial/metadata.md"
_CONFIG_PAGE = "tutorial/path-operation-configuration.md"
_ADVANCED_PAGE = "advanced/path-operation-advanced-configuration.md"

_META_API_RECIPE = "tests/fixtures/input-recipes/parity/metadata-tutorial001-upstream.yaml"
_META_LICENSE_RECIPE = "tests/fixtures/input-recipes/parity/metadata-tutorial001-1-upstream.yaml"
_META_TAGS_RECIPE = "tests/fixtures/input-recipes/parity/metadata-tutorial004-upstream.yaml"
_META_ROUTE_TAGS_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial002-upstream.yaml"
)
_META_OPENAPI_URL_RECIPE = "tests/fixtures/input-recipes/parity/metadata-tutorial002-upstream.yaml"
_META_DOCS_URL_RECIPE = "tests/fixtures/input-recipes/parity/metadata-tutorial003-upstream.yaml"

_CONFIG_STATUS_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-post-status-code-isolated.yaml"
)
_CONFIG_TAGS_RECIPE = "tests/fixtures/input-recipes/parity/path-operation-post-tags-isolated.yaml"
_CONFIG_ENUM_TAGS_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial002b-upstream.yaml"
)
_CONFIG_SUMMARY_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial003-upstream.yaml"
)
_CONFIG_DOCSTRING_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-configurations-tutorial004-upstream.yaml"
)
_CONFIG_RESPONSE_DESCRIPTION_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-post-response-description-isolated.yaml"
)
_CONFIG_DEPRECATED_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-post-deprecated-isolated.yaml"
)

_ADVANCED_FUNCTION_ID_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-advanced-config"
    "urations-tutorial002-upstream.yaml"
)
_ADVANCED_EXCLUDE_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-advanced-config"
    "urations-tutorial003-upstream.yaml"
)
_ADVANCED_DOCSTRING_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-advanced-config"
    "urations-tutorial004-upstream.yaml"
)
_ADVANCED_RESPONSES_RECIPE = "tests/fixtures/input-recipes/parity/additional-responses.yaml"
_ADVANCED_EXTRA_RECIPE = "tests/fixtures/input-recipes/parity/openapi-extra-deep-merge.yaml"
_ADVANCED_SCHEMA_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-advanced-config"
    "urations-tutorial006-upstream.yaml"
)
_ADVANCED_CONTENT_TYPE_RECIPE = (
    "tests/fixtures/input-recipes/parity/path-operation-advanced-config"
    "urations-tutorial007-upstream.yaml"
)

_OPENAPI = ["openapi.document"]
_OPENAPI_PATHS = ["openapi.document", "openapi.paths"]
_HTTP_AND_OPENAPI_PATHS = ["http.status", "openapi.document", "openapi.paths"]

_META_API_RATIONALE = (
    "The pinned section lists FastAPI application metadata. FastAPI 0.141.1 stores these "
    "fields on the application in fastapi/applications.py:875-885 and passes them into "
    "get_openapi() at :1084-1097; fastapi/openapi/utils.py:590-612 emits the selected Info "
    "fields. The recipe observes OpenAPI data only; Starlette 1.6.0 owns generic ASGI and "
    "HTTP transport."
)

_META_TAGS_RATIONALE = (
    "FastAPI 0.141.1 accepts ordered openapi_tags metadata on FastAPI in "
    "fastapi/applications.py:222-255 and passes it to OpenAPI generation at :1097; "
    "fastapi/openapi/utils.py:675-676 adds the metadata array to the document. The selected "
    "pointer is one tag's externalDocs object, not a rendered docs UI."
)

_META_ROUTE_TAGS_RATIONALE = (
    "The pinned example assigns tags to path operations. FastAPI 0.141.1 forwards route "
    "decorator metadata through fastapi/applications.py:1167-1219, and "
    "fastapi/openapi/utils.py:291-293 emits route tags into each operation. The selected "
    "OpenAPI paths are route metadata; Starlette 1.6.0 owns generic route dispatch."
)

_META_URL_RATIONALE = (
    "FastAPI 0.141.1 registers the OpenAPI endpoint and conditional Swagger UI/ReDoc routes "
    "in fastapi/applications.py:1106-1158. The selected route status, body, and OpenAPI "
    "pointers are ASGI-visible configuration results; Starlette 1.6.0 owns generic dispatch "
    "and response transport."
)

_ROUTE_CONFIGURATION_RATIONALE = (
    "FastAPI 0.141.1 exposes path-operation configuration through its route decorators in "
    "fastapi/applications.py:1167-1219 and stores it on APIRoute in "
    "fastapi/routing.py:984-1037. "
    "fastapi/openapi/utils.py:281-306 projects summary, operationId, tags, and deprecation "
    "metadata into the OpenAPI operation."
)

_OPENAPI_EXTRA_RATIONALE = (
    "FastAPI 0.141.1 merges each APIRoute.openapi_extra into its generated operation using "
    "deep_dict_update in fastapi/openapi/utils.py:537-538. The recipe exercises a direct "
    "route and a router-included route; the OpenAPI document and paths are the selected "
    "observations."
)

_CUSTOM_SCHEMA_RATIONALE = (
    "The pinned example reads request bytes through Request and "
    "declares a requestBody schema "
    "with openapi_extra. FastAPI 0.141.1 merges that fragment at "
    "fastapi/openapi/utils.py:537-538; Starlette 1.6.0 owns Request body consumption and "
    "generic ASGI transport. The selected route result and OpenAPI "
    "request schema are distinct "
    "observations."
)

_CUSTOM_CONTENT_TYPE_RATIONALE = (
    "FastAPI 0.141.1 merges the tutorial's manually declared YAML requestBody through "
    "APIRoute.openapi_extra at fastapi/openapi/utils.py:537-538. "
    "Starlette 1.6.0 owns Request "
    "body delivery. YAML decoding and Pydantic validation in the workload are authored "
    "endpoint behavior; they are not FastAPI's built-in YAML parsing or request validation."
)


DOC_SECTION_CASE_MAPPINGS_OPERATION_CONFIG_20261015 = {
    (_META_PAGE, "metadata-and-docs-urls"): _excluded(
        "Metadata and Docs URLs { #metadata-and-docs-urls }",
        1,
        120,
        (
            "The page title and introduction do not add behavior beyond the "
            "separately reviewed metadata and URL child sections."
        ),
        (
            "Pinned docs/en/docs/tutorial/metadata.md:1-3 is a title and "
            "overview; the concrete API metadata, tag metadata, OpenAPI URL, "
            "and docs URL claims appear in child sections and are mapped "
            "independently."
        ),
    ),
    (_META_PAGE, "metadata-for-api"): _workflow(
        "Metadata for API { #metadata-for-api }",
        5,
        32,
        _META_API_RECIPE,
        ["fastapi.docs.metadata.tutorial001.openapi-info-fields"],
        ["selected-openapi-info-fields"],
        _OPENAPI,
        (
            "This samples summary, description, terms of service, contact, and "
            "license fields in one generated OpenAPI Info object. It does not "
            "exercise title or version, Markdown rendering, metadata "
            "validation, or the browser docs UI."
        ),
        _META_API_RATIONALE,
    ),
    (_META_PAGE, "license-identifier"): _workflow(
        "License identifier { #license-identifier }",
        33,
        40,
        _META_LICENSE_RECIPE,
        ["fastapi.test.test-tutorial-test-metadata-test-tutorial001-1.test-openapi-schema"],
        ["openapi"],
        ["docs.response.status", "http.status", "openapi.document"],
        (
            "This samples one SPDX license identifier in the generated Info "
            "license object. It does not exercise the mutually exclusive URL "
            "form, conflicting values, or invalid identifiers."
        ),
        (
            "The pinned section links docs_src/metadata/tutorial001_1_py310.py "
            "and FastAPI passes license_info to get_openapi() in "
            "fastapi/applications.py:1094; fastapi/openapi/utils.py:611-613 "
            "emits the Info license. The recipe observes the OpenAPI document, "
            "not UI rendering."
        ),
    ),
    (_META_PAGE, "metadata-for-tags"): _workflow(
        "Metadata for tags { #metadata-for-tags }",
        41,
        94,
        _META_TAGS_RECIPE,
        ["fastapi.test.test-tutorial-test-metadata-test-tutorial004.test-openapi-schema"],
        ["openapi"],
        ["docs.response.status", "http.status", "openapi.document"],
        (
            "This samples the externalDocs object for one configured tag. It "
            "does not establish tag descriptions, list ordering, Markdown "
            "rendering, metadata for undeclared tags, or rendered docs UI "
            "behavior."
        ),
        _META_TAGS_RATIONALE,
    ),
    (_META_PAGE, "create-metadata-for-tags"): _workflow(
        "Create metadata for tags { #create-metadata-for-tags }",
        55,
        70,
        _META_TAGS_RECIPE,
        ["fastapi.test.test-tutorial-test-metadata-test-tutorial004.test-openapi-schema"],
        ["openapi"],
        ["docs.response.status", "http.status", "openapi.document"],
        (
            "This samples one configured tag's externalDocs object. The input "
            "does not compare the tag name, description, ordering, Markdown "
            "presentation, or missing metadata for other used tags."
        ),
        _META_TAGS_RATIONALE,
    ),
    (_META_PAGE, "use-your-tags"): _workflow(
        "Use your tags { #use-your-tags }",
        71,
        82,
        _META_ROUTE_TAGS_RECIPE,
        ["fastapi.path-operation-configurations.tutorial002"],
        ["route-tags"],
        _OPENAPI_PATHS,
        (
            "This samples tags on three direct path operations. It does not "
            "exercise APIRouter-level tag composition, Enum tags, or the "
            "separate openapi_tags metadata definitions."
        ),
        _META_ROUTE_TAGS_RATIONALE,
    ),
    (_META_PAGE, "openapi-url"): _workflow(
        "OpenAPI URL { #openapi-url }",
        95,
        106,
        _META_OPENAPI_URL_RECIPE,
        ["fastapi.test.test-tutorial-test-metadata-test-tutorial002.test-openapi-schema"],
        ["configured-openapi-location"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "This samples an OpenAPI endpoint configured at a non-default path. "
            "It does not exercise openapi_url=None, root_path mounting, or "
            "every interaction with the documentation routes."
        ),
        _META_URL_RATIONALE,
    ),
    (_META_PAGE, "docs-urls"): _workflow(
        "Docs URLs { #docs-urls }",
        107,
        120,
        _META_DOCS_URL_RECIPE,
        [("fastapi.test.test-tutorial-test-metadata-test-tutorial003.test-swagger-ui-custom-url")],
        ["configured-swagger-url", "disabled-redoc-url"],
        ["http.body.bytes", "http.status"],
        (
            "This samples a custom Swagger URL and a disabled ReDoc route. It "
            "does not exercise a custom ReDoc URL, docs_url=None, browser "
            "rendering, or external UI asset behavior."
        ),
        _META_URL_RATIONALE,
    ),
    (_CONFIG_PAGE, "path-operation-configuration"): _excluded(
        "Path Operation Configuration { #path-operation-configuration }",
        1,
        107,
        (
            "The page heading and introduction group the path-operation options "
            "mapped in the child sections; they do not specify a separate "
            "operation."
        ),
        (
            "Pinned docs/en/docs/tutorial/path-operation-configuration.md:1-7 "
            "introduces decorator configuration and distinguishes decorator "
            "parameters from endpoint function parameters. The independently "
            "observable status, tags, summary, description, response, and "
            "deprecation behaviors are mapped under their own headings."
        ),
    ),
    (_CONFIG_PAGE, "response-status-code"): _workflow(
        "Response Status Code { #response-status-code }",
        11,
        30,
        _CONFIG_STATUS_RECIPE,
        ["fastapi.path-operation.post-status-code-isolated"],
        ["post-explicit-status", "openapi-post-status"],
        _HTTP_AND_OPENAPI_PATHS,
        (
            "This samples one explicit response status and its OpenAPI response "
            "entry. It does not exercise every status value or the "
            "fastapi.status re-export identity and constants individually."
        ),
        (
            "The pinned tutorial example sets one route status through the "
            "decorator. FastAPI's route decorator passes it into route "
            "registration in fastapi/applications.py:1167-1219, and OpenAPI "
            "response construction is in fastapi/openapi/utils.py:405-418. The "
            "fastapi.status convenience alias is described as a Starlette "
            "re-export and is outside these HTTP/OpenAPI observations."
        ),
    ),
    (_CONFIG_PAGE, "tags"): _workflow(
        "Tags { #tags }",
        31,
        50,
        _CONFIG_TAGS_RECIPE,
        ["fastapi.path-operation.post-tags-isolated"],
        ["openapi-post-tags"],
        _OPENAPI_PATHS,
        (
            "This samples one string tag on one path operation. It does not "
            "cover Enum conversion, tag metadata declarations, APIRouter "
            "composition, or docs UI rendering."
        ),
        _ROUTE_CONFIGURATION_RATIONALE,
    ),
    (_CONFIG_PAGE, "tags-with-enums"): _workflow(
        "Tags with Enums { #tags-with-enums }",
        41,
        50,
        _CONFIG_ENUM_TAGS_RECIPE,
        ["fastapi.path-operation-configurations.tutorial002b"],
        ["enum-route-tags"],
        _OPENAPI_PATHS,
        (
            "This samples Enum-backed tags on two route operations. It does not "
            "cover Enum validation, router-level tag composition, or metadata "
            "for the declared tags."
        ),
        (
            "The pinned section's tutorial002b example supplies Enum members as "
            "route tags. FastAPI accepts str or Enum tags in its APIRoute "
            "surface (fastapi/routing.py:1172-1174), and "
            "fastapi/openapi/utils.py:291-293 emits those tags on the "
            "operation. The selector observes the resulting OpenAPI paths."
        ),
    ),
    (_CONFIG_PAGE, "summary-and-description"): _workflow(
        "Summary and description { #summary-and-description }",
        51,
        56,
        _CONFIG_SUMMARY_RECIPE,
        ["fastapi.path-operation-configurations.tutorial003-explicit-description"],
        ["operation-description"],
        _OPENAPI_PATHS,
        (
            "This samples one explicit summary and description on a POST "
            "operation. It does not cover automatic summary generation, "
            "docstring extraction, Markdown rendering, or alternate route "
            "methods."
        ),
        _ROUTE_CONFIGURATION_RATIONALE,
    ),
    (_CONFIG_PAGE, "description-from-docstring"): _workflow(
        "Description from docstring { #description-from-docstring }",
        57,
        68,
        _CONFIG_DOCSTRING_RECIPE,
        ["fastapi.path-operation-configurations.tutorial004-docstring-description"],
        ["operation-description"],
        _OPENAPI_PATHS,
        (
            "This samples a cleaned multi-line endpoint docstring as an OpenAPI "
            "description. It does not exercise form-feed truncation, Markdown "
            "rendering, or external documentation consumers."
        ),
        (
            "FastAPI 0.141.1 uses inspect.cleandoc on an endpoint docstring in "
            "fastapi/routing.py:1033-1037; the operation description is "
            "assembled in fastapi/openapi/utils.py:291-294. Starlette 1.6.0 "
            "owns only the generic HTTP request path used to retrieve OpenAPI."
        ),
    ),
    (_CONFIG_PAGE, "response-description"): _workflow(
        "Response description { #response-description }",
        69,
        90,
        _CONFIG_RESPONSE_DESCRIPTION_RECIPE,
        ["fastapi.path-operation.post-response-description-isolated"],
        ["openapi-post-response-descriptions"],
        _OPENAPI_PATHS,
        (
            "This samples one explicit response description together with the "
            "default and empty description forms on the fixture routes. It does "
            "not cover additional response codes, media types, or every "
            "response class."
        ),
        (
            "FastAPI's APIRoute stores response_description in "
            "fastapi/routing.py:999, and OpenAPI generation assigns it to the "
            "response object in fastapi/openapi/utils.py:416-418. The workflow "
            "compares the resulting OpenAPI paths only."
        ),
    ),
    (_CONFIG_PAGE, "deprecate-a-path-operation"): _workflow(
        "Deprecate a *path operation* { #deprecate-a-path-operation }",
        91,
        104,
        _CONFIG_DEPRECATED_RECIPE,
        ["fastapi.path-operation.post-deprecated-isolated"],
        ["openapi-post-deprecated"],
        _OPENAPI_PATHS,
        (
            "This samples the deprecated flag on one POST operation in "
            "generated OpenAPI. It does not test Python deprecation warnings, "
            "removal of the route, or browser UI rendering."
        ),
        _ROUTE_CONFIGURATION_RATIONALE,
    ),
    (_CONFIG_PAGE, "recap"): _excluded(
        "Recap { #recap }",
        105,
        107,
        (
            "The recap restates that path operations accept decorator metadata "
            "and introduces no distinct configuration behavior."
        ),
        (
            "Pinned docs/en/docs/tutorial/path-operation-configuration.md:105-1"
            "07 is a one-sentence recap of the status, tags, summary, "
            "description, response description, and deprecation child sections, "
            "each mapped separately."
        ),
    ),
    (_ADVANCED_PAGE, "path-operation-advanced-configuration"): _excluded(
        "Path Operation Advanced Configuration { #path-operation-advanced-configuration }",
        1,
        166,
        (
            "The page heading is a container for the individually mapped "
            "advanced operationId, schema visibility, description, response, "
            "and OpenAPI extension sections."
        ),
        (
            "Pinned docs/en/docs/advanced/path-operation-advanced-configuration"
            ".md:1 is only the page title; its independently observable claims "
            "are under the child headings. The OpenAPI operationId and OpenAPI "
            "Extensions child anchors already have reviewed mappings and are "
            "not duplicated here."
        ),
    ),
    (_ADVANCED_PAGE, "using-the-path-operation-function-name-as-the-operationid"): _workflow(
        (
            "Using the *path operation function* name as the operationId { "
            "#using-the-path-operation-function-name-as-the-operationid }"
        ),
        17,
        32,
        _ADVANCED_FUNCTION_ID_RECIPE,
        ["fastapi.path-operation-advanced-configurations.tutorial002"],
        ["generated-operation-id"],
        _OPENAPI_PATHS,
        (
            "This samples one custom generate_unique_id_function based on a "
            "route function name. It does not test duplicate names across "
            "modules, uniqueness enforcement, or every route method."
        ),
        (
            "FastAPI 0.141.1 invokes the selected unique-ID function while "
            "configuring APIRoute in fastapi/routing.py:1022-1028; "
            "fastapi/openapi/utils.py:296-305 writes the route ID into "
            "operationId. The selected OpenAPI pointer is the route operation "
            "ID."
        ),
    ),
    (_ADVANCED_PAGE, "exclude-from-openapi"): _workflow(
        "Exclude from OpenAPI { #exclude-from-openapi }",
        33,
        38,
        _ADVANCED_EXCLUDE_RECIPE,
        ["fastapi.path-operation-advanced-configurations.tutorial003"],
        ["schema-visible-paths"],
        _OPENAPI_PATHS,
        (
            "This samples the generated paths for a fixture with one "
            "include_in_schema=False operation. It does not separately assert "
            "that the route remains reachable over HTTP or inspect rendered "
            "documentation UI."
        ),
        (
            "FastAPI 0.141.1 retains include_in_schema on APIRoute and gates "
            "OpenAPI emission in fastapi/openapi/utils.py:331 and :562. The "
            "fixture's OpenAPI paths observation is the documented visibility "
            "boundary."
        ),
    ),
    (_ADVANCED_PAGE, "advanced-description-from-docstring"): _workflow(
        "Advanced description from docstring { #advanced-description-from-docstring }",
        39,
        48,
        _ADVANCED_DOCSTRING_RECIPE,
        ["fastapi.path-operation-advanced-configurations.tutorial004"],
        ["item-operation-schema"],
        _OPENAPI_PATHS,
        (
            "This samples the operation description produced from the "
            "tutorial's docstring before its form-feed delimiter. It does not "
            "test Sphinx output or the text after the delimiter in another "
            "documentation tool."
        ),
        (
            "FastAPI 0.141.1 cleans the route docstring and truncates it at the "
            "first form-feed in fastapi/routing.py:1033-1037; "
            "fastapi/openapi/utils.py:291-294 includes the result in the "
            "operation. The case selects that operation metadata in OpenAPI."
        ),
    ),
    (_ADVANCED_PAGE, "additional-responses"): _workflow(
        "Additional Responses { #additional-responses }",
        49,
        58,
        _ADVANCED_RESPONSES_RECIPE,
        ["fastapi.docs.additional-responses.openapi"],
        ["read-stock-openapi"],
        [
            "docs.response.headers",
            "docs.response.status",
            "http.headers.ordered",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "This samples one generated operation's 200 and 404 response "
            "metadata and schema references. It does not exercise every status "
            "code, response model, media type, runtime response branch, or "
            "error handler. The OpenAPI endpoint's status and headers are "
            "captured by the same action as transport observations."
        ),
        (
            "FastAPI 0.141.1 builds declared response metadata while creating "
            "APIRoute and emits response objects in "
            "fastapi/openapi/utils.py:405-537. The case reads the generated "
            "OpenAPI for one inventory operation; Starlette 1.6.0 owns the "
            "OpenAPI endpoint's generic ASGI response transport."
        ),
    ),
    (_ADVANCED_PAGE, "openapi-extra"): _workflow(
        "OpenAPI Extra { #openapi-extra }",
        59,
        166,
        _ADVANCED_EXTRA_RECIPE,
        ["fastapi.openapi-extra.deep-merge-and-router-inclusion"],
        ["openapi"],
        _OPENAPI_PATHS,
        (
            "This samples selected nested openapi_extra fields on one direct "
            "route and one router-included route. It does not cover every merge "
            "shape, the custom requestBody example, or the YAML content-type "
            "example; the OpenAPI Extensions child has its own existing "
            "reviewed mapping."
        ),
        _OPENAPI_EXTRA_RATIONALE,
    ),
    (_ADVANCED_PAGE, "custom-openapi-path-operation-schema"): _workflow(
        "Custom OpenAPI *path operation* schema { #custom-openapi-path-operation-schema }",
        126,
        141,
        _ADVANCED_SCHEMA_RECIPE,
        ["fastapi.path-operation-advanced-configurations.tutorial006"],
        ["raw-body", "declared-request-body"],
        [
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "This samples a raw-byte request route alongside its manually "
            "declared OpenAPI requestBody schema. It does not exercise FastAPI "
            "JSON parsing or validation, other media types, or arbitrary custom "
            "schema fragments."
        ),
        _CUSTOM_SCHEMA_RATIONALE,
    ),
    (_ADVANCED_PAGE, "custom-openapi-content-type"): _workflow(
        "Custom OpenAPI content type { #custom-openapi-content-type }",
        142,
        166,
        _ADVANCED_CONTENT_TYPE_RECIPE,
        ["fastapi.path-operation-advanced-configurations.tutorial007"],
        ["valid-yaml", "malformed-yaml", "yaml-with-invalid-item", "yaml-request-schema"],
        [
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "This samples a YAML request media type, its declared schema, and "
            "the tutorial workload's valid and invalid request branches. YAML "
            "parsing and Pydantic validation are authored endpoint behavior; "
            "the mapping does not claim built-in FastAPI YAML support or "
            "automatic request validation for that media type."
        ),
        _CUSTOM_CONTENT_TYPE_RATIONALE,
    ),
}
