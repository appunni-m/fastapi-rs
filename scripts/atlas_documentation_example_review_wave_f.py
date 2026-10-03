"""Reviewed source-to-input links for FastAPI request-model examples."""


def _span(path: str, start: int, end: int, role: str) -> dict[str, object]:
    return {"path": path, "start_line": start, "end_line": end, "role": role}


def _case(recipe: str, case_id: str, selectors: list[str]) -> dict[str, object]:
    return {
        "recipe_path": "tests/fixtures/input-recipes/parity/" + recipe,
        "case_ids": [case_id],
        "observation_selectors": sorted(selectors),
    }


def _review(
    path: str,
    rationale: str,
    start: int,
    end: int,
    role: str,
    cases: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "rationale": rationale,
        "supporting_sources": [_span(path, start, end, role)],
        "workflow_cases": cases,
    }


def _family(
    paths: list[str],
    rationale: str,
    spans: dict[str, tuple[int, int, str]],
    cases: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    return {path: _review(path, rationale, *spans[path], cases) for path in paths}


HTTP = ["http.body.bytes", "http.status"]
HTTP_OPENAPI = ["http.body.bytes", "http.status", "openapi.document"]


_MAPPINGS = [
    (
        ["docs_src/body_nested_models/tutorial001_py310.py"],
        (
            "The independent request submits a heterogeneous JSON list to a Pydantic "
            "body field annotated as bare list. It samples unparameterized list item "
            "acceptance and preservation only; optional Item defaults and source "
            "response literals are not claimed."
        ),
        {
            "docs_src/body_nested_models/tutorial001_py310.py": (
                7,
                18,
                "Item bare list field, body parameter, and response route",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.bare-list-values-preserved",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial002_py310.py"],
        (
            "String values exercise successful parsing of the source's list[str] "
            "JSON model field. Other Item fields and the documentation route are "
            "independent."
        ),
        {
            "docs_src/body_nested_models/tutorial002_py310.py": (
                7,
                18,
                "Item model with typed tags and JSON route",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.list-tags-valid",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial003_py310.py"],
        (
            "Repeated tag values exercise set coercion and de-duplication on an "
            "independent JSON model route. Other source fields and route literals "
            "are not claimed."
        ),
        {
            "docs_src/body_nested_models/tutorial003_py310.py": (
                7,
                18,
                "Item set field and JSON route",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.set-tags-deduplicated",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial004_py310.py"],
        (
            "Independent requests sample the source model's set-valued tags and "
            "optional nested-image behavior separately. The nested workload uses "
            "different field names and an HttpUrl image field, so those differences "
            "are not claimed."
        ),
        {
            "docs_src/body_nested_models/tutorial004_py310.py": (
                7,
                24,
                "Item set tags, optional Image model, and route",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.set-tags-deduplicated",
                HTTP,
            ),
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.optional-image-present",
                HTTP,
            ),
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.optional-image-absent",
                HTTP,
            ),
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial005_py310.py"],
        (
            "Independent nested-model requests exercise a present HttpUrl image and "
            "rejection of an invalid URL. They sample HttpUrl behavior only; field "
            "names, set serialization, and other Item fields are not claimed."
        ),
        {
            "docs_src/body_nested_models/tutorial005_py310.py": (
                7,
                24,
                "HttpUrl Image model and optional nested body field",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.optional-image-present",
                HTTP,
            ),
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.optional-image-absent",
                HTTP,
            ),
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.http-url-invalid",
                HTTP,
            ),
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial006_py310.py"],
        (
            "The independent body model accepts an optional list of nested HttpUrl "
            "images; requests cover present and absent lists. Other Item fields and "
            "names are not claimed."
        ),
        {
            "docs_src/body_nested_models/tutorial006_py310.py": (
                7,
                24,
                "Optional list of nested Image models and route",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.optional-image-list-present",
                HTTP,
            ),
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.optional-image-list-absent",
                HTTP,
            ),
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial007_py310.py"],
        (
            "The input contains a model with a list of nested line models and a "
            "nested image list. It samples recursive body-model parsing for this "
            "shape; independent field names and values differ."
        ),
        {
            "docs_src/body_nested_models/tutorial007_py310.py": (
                7,
                30,
                "Offer model with nested Item list and endpoint",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.offer-nested-items",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial008_py310.py"],
        (
            "The request submits a top-level JSON array of nested image models. It "
            "samples list body extraction and valid element parsing; source route "
            "and response literals are not claimed."
        ),
        {
            "docs_src/body_nested_models/tutorial008_py310.py": (
                7,
                14,
                "Top-level list of Image models and POST route",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.top-level-image-list",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/body_nested_models/tutorial009_py310.py"],
        (
            "Numeric string keys and float values sample valid dict[int, float] body "
            "parsing and key conversion. Invalid-key details are outside the "
            "selected cases."
        ),
        {
            "docs_src/body_nested_models/tutorial009_py310.py": (
                6,
                8,
                "Integer-to-float map body endpoint",
            )
        },
        [
            _case(
                "docs-example-wave-f-nested-bodies.yaml",
                "fastapi.docs-example-wave-f.nested-body.integer-float-map",
                HTTP,
            ),
        ],
    ),
    (
        [
            "docs_src/body_multiple_params/tutorial001_py310.py",
            "docs_src/body_multiple_params/tutorial001_an_py310.py",
        ],
        (
            "The independent route combines a bounded path parameter, optional query "
            "value, and optional Pydantic body model; requests cover absent and "
            "present bodies. Source literals and Path title text are not claimed."
        ),
        {
            "docs_src/body_multiple_params/tutorial001_py310.py": (
                7,
                26,
                "Item model and optional body/query/path endpoint",
            ),
            "docs_src/body_multiple_params/tutorial001_an_py310.py": (
                9,
                27,
                "Item model and Annotated optional endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-multiple-body-values.yaml",
                "fastapi.docs-example-wave-f.multiple-body.optional-model-absent",
                HTTP,
            ),
            _case(
                "docs-example-wave-f-multiple-body-values.yaml",
                "fastapi.docs-example-wave-f.multiple-body.optional-model-present",
                HTTP,
            ),
        ],
    ),
    (
        ["docs_src/body_multiple_params/tutorial002_py310.py"],
        (
            "The request body contains two separately declared Pydantic models under "
            "their parameter names. This samples multiple-model body aggregation; "
            "independent model fields and route literals differ."
        ),
        {
            "docs_src/body_multiple_params/tutorial002_py310.py": (
                7,
                22,
                "Item/User model definitions and combined body route",
            )
        },
        [
            _case(
                "docs-example-wave-f-multiple-model-bodies.yaml",
                "fastapi.docs-example-wave-f.multiple-body.two-models",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/body_multiple_params/tutorial003_py310.py",
            "docs_src/body_multiple_params/tutorial003_an_py310.py",
        ],
        (
            "The independent request combines a Pydantic body model with a "
            "separately declared integer Body value. It samples model-plus-scalar "
            "extraction and valid integer parsing; the source's additional User "
            "model, parameter names, and any numeric bounds are not claimed."
        ),
        {
            "docs_src/body_multiple_params/tutorial003_py310.py": (
                7,
                22,
                "Item/User model definitions and scalar body route",
            ),
            "docs_src/body_multiple_params/tutorial003_an_py310.py": (
                9,
                26,
                "Annotated Item/User model definitions and scalar body route",
            ),
        },
        [
            _case(
                "docs-example-wave-f-multiple-body-values.yaml",
                "fastapi.docs-example-wave-f.multiple-body.model-and-scalar",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/body_multiple_params/tutorial005_py310.py",
            "docs_src/body_multiple_params/tutorial005_an_py310.py",
        ],
        (
            "The independent request wraps one model under its parameter key, "
            "matching Body(embed=True). It samples the embedded-model body shape and "
            "successful model parsing only."
        ),
        {
            "docs_src/body_multiple_params/tutorial005_py310.py": (
                7,
                17,
                "Embedded Item body parameter and route",
            ),
            "docs_src/body_multiple_params/tutorial005_an_py310.py": (
                9,
                19,
                "Annotated embedded Item body parameter and route",
            ),
        },
        [
            _case(
                "docs-example-wave-f-multiple-model-bodies.yaml",
                "fastapi.docs-example-wave-f.multiple-body.embedded-model",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/header_param_models/tutorial001_an_py310.py"],
        (
            "The valid request supplies required and optional modeled headers, "
            "including repeated x-tag values. It samples Header model extraction, "
            "default underscore-to-hyphen conversion, and list aggregation only."
        ),
        {
            "docs_src/header_param_models/tutorial001_an_py310.py": (
                9,
                19,
                "CommonHeaders model and Annotated Header endpoint",
            )
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.header-model.repeated-list-default-conversion",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/header_param_models/tutorial002_py310.py",
            "docs_src/header_param_models/tutorial002_an_py310.py",
        ],
        (
            "The request supplies required model headers and one undeclared header "
            "to a model configured with extra='forbid'. It samples rejection of that "
            "extra header only."
        ),
        {
            "docs_src/header_param_models/tutorial002_py310.py": (
                7,
                19,
                "Strict CommonHeaders model and Header endpoint",
            ),
            "docs_src/header_param_models/tutorial002_an_py310.py": (
                9,
                21,
                "Strict CommonHeaders model and Annotated Header endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.header-model.extra-forbidden",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/header_param_models/tutorial003_py310.py",
            "docs_src/header_param_models/tutorial003_an_py310.py",
        ],
        (
            "Underscore-containing wire names and repeated x_tag values sample "
            "Header(convert_underscores=False) and list-valued header extraction "
            "only."
        ),
        {
            "docs_src/header_param_models/tutorial003_py310.py": (
                7,
                17,
                "CommonHeaders model with underscore-preserving Header endpoint",
            ),
            "docs_src/header_param_models/tutorial003_an_py310.py": (
                9,
                21,
                "CommonHeaders model with Annotated underscore-preserving endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.header-model.underscore-preserved",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/query_param_models/tutorial001_py310.py",
            "docs_src/query_param_models/tutorial001_an_py310.py",
        ],
        (
            "Independent requests sample grouped query-model defaults and repeated "
            "lists using matching names, defaults, Literal choices, and numeric "
            "bounds. Only valid model parsing is claimed."
        ),
        {
            "docs_src/query_param_models/tutorial001_py310.py": (
                9,
                18,
                "FilterParams model and Query endpoint",
            ),
            "docs_src/query_param_models/tutorial001_an_py310.py": (
                9,
                18,
                "FilterParams model and Annotated Query endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.query-model.defaults-and-repeated-tags",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/query_param_models/tutorial002_py310.py",
            "docs_src/query_param_models/tutorial002_an_py310.py",
        ],
        (
            "An undeclared query key is submitted to a query model configured with "
            "extra='forbid'. The cases sample the unknown-query rejection branch "
            "only."
        ),
        {
            "docs_src/query_param_models/tutorial002_py310.py": (
                9,
                20,
                "Strict FilterParams model and Query endpoint",
            ),
            "docs_src/query_param_models/tutorial002_an_py310.py": (
                9,
                20,
                "Strict FilterParams model and Annotated Query endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.query-model.extra-forbidden",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/cookie_param_models/tutorial001_an_py310.py"],
        (
            "The request supplies a required cookie-model field and an optional "
            "tracker field. It samples valid Cookie model extraction only; missing "
            "and duplicate-cookie cases are not claimed."
        ),
        {
            "docs_src/cookie_param_models/tutorial001_an_py310.py": (
                9,
                17,
                "Cookies model and Annotated Cookie endpoint",
            )
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.cookie-model.valid-fields",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/cookie_param_models/tutorial002_py310.py",
            "docs_src/cookie_param_models/tutorial002_an_py310.py",
        ],
        (
            "An undeclared cookie is submitted to a Cookie-bound model configured "
            "with extra='forbid'. It samples rejection of the extra cookie only."
        ),
        {
            "docs_src/cookie_param_models/tutorial002_py310.py": (
                7,
                17,
                "Strict Cookies model and Cookie endpoint",
            ),
            "docs_src/cookie_param_models/tutorial002_an_py310.py": (
                9,
                19,
                "Strict Cookies model and Annotated Cookie endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-request-parameter-models.yaml",
                "fastapi.docs-example-wave-f.cookie-model.extra-forbidden",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/request_files/tutorial001_an_py310.py"],
        (
            "Fresh multipart requests sample a required File-bound bytes parameter "
            "and a separate UploadFile parameter. The source uses Annotated[bytes, "
            "File()] for one route and bare UploadFile for the other; the "
            "independent case covers required file extraction and valid dispatch, "
            "not the source route names or annotation spelling."
        ),
        {
            "docs_src/request_files/tutorial001_an_py310.py": (
                8,
                15,
                "Annotated required bytes and UploadFile endpoints",
            )
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-files.required-annotated-files",
                HTTP,
            )
        ],
    ),
    (
        ["docs_src/request_files/tutorial001_02_an_py310.py"],
        (
            "Independent multipart requests cover absent and present optional bytes "
            "and UploadFile values on annotated routes. Empty-file and "
            "upload-lifetime behavior are not claimed."
        ),
        {
            "docs_src/request_files/tutorial001_02_an_py310.py": (
                8,
                21,
                "Annotated optional bytes and UploadFile endpoints",
            )
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-files.optional-presence",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/request_files/tutorial001_03_py310.py",
            "docs_src/request_files/tutorial001_03_an_py310.py",
        ],
        (
            "Fresh uploads exercise described bytes and UploadFile parameters; "
            "OpenAPI observations select their requestBody schemas. Browser "
            "rendering and upload lifetime are not claimed."
        ),
        {
            "docs_src/request_files/tutorial001_03_py310.py": (
                6,
                15,
                "Described bytes and UploadFile parameters",
            ),
            "docs_src/request_files/tutorial001_03_an_py310.py": (
                8,
                17,
                "Annotated described bytes and UploadFile parameters",
            ),
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-files.single-file-description",
                HTTP_OPENAPI,
            )
        ],
    ),
    (
        [
            "docs_src/request_files/tutorial002_py310.py",
            "docs_src/request_files/tutorial002_an_py310.py",
        ],
        (
            "Repeated multipart fields exercise bytes and UploadFile list "
            "parameters. This samples file-list parsing; the source HTML forms and "
            "browser submission are not claimed."
        ),
        {
            "docs_src/request_files/tutorial002_py310.py": (
                7,
                15,
                "Multiple bytes and UploadFile list endpoints",
            ),
            "docs_src/request_files/tutorial002_an_py310.py": (
                9,
                16,
                "Annotated multiple bytes and UploadFile list endpoints",
            ),
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-files.multiple-files",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/request_files/tutorial003_py310.py",
            "docs_src/request_files/tutorial003_an_py310.py",
        ],
        (
            "Repeated multipart fields exercise described byte and UploadFile lists; "
            "OpenAPI observations select their requestBody schemas and descriptions. "
            "HTML routes are not claimed."
        ),
        {
            "docs_src/request_files/tutorial003_py310.py": (
                7,
                18,
                "Described multiple-file parameters",
            ),
            "docs_src/request_files/tutorial003_an_py310.py": (
                9,
                21,
                "Annotated described multiple-file parameters",
            ),
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-files.multiple-file-description",
                HTTP_OPENAPI,
            )
        ],
    ),
    (
        ["docs_src/request_form_models/tutorial001_an_py310.py"],
        (
            "A form-encoded request supplies both required fields to an annotated "
            "Pydantic form model. It samples successful form-to-model extraction "
            "only."
        ),
        {
            "docs_src/request_form_models/tutorial001_an_py310.py": (
                9,
                16,
                "FormData model and Annotated Form endpoint",
            )
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-form-models.valid-model",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/request_form_models/tutorial002_py310.py",
            "docs_src/request_form_models/tutorial002_an_py310.py",
        ],
        (
            "The independent form model has the matching required fields and "
            "extra='forbid'; an unexpected submitted field exercises its rejection "
            "path only."
        ),
        {
            "docs_src/request_form_models/tutorial002_py310.py": (
                7,
                15,
                "Strict FormData model and Form endpoint",
            ),
            "docs_src/request_form_models/tutorial002_an_py310.py": (
                9,
                17,
                "Strict FormData model and Annotated Form endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-form-models.extra-forbidden",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/request_forms/tutorial001_py310.py",
            "docs_src/request_forms/tutorial001_an_py310.py",
        ],
        (
            "Form-encoded requests supply both required scalar Form parameters to "
            "plain and annotated endpoints. They sample successful form field "
            "extraction only."
        ),
        {
            "docs_src/request_forms/tutorial001_py310.py": (
                6,
                8,
                "Username/password Form fields and route",
            ),
            "docs_src/request_forms/tutorial001_an_py310.py": (
                8,
                10,
                "Annotated username/password Form fields and route",
            ),
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-forms.required-fields",
                HTTP,
            )
        ],
    ),
    (
        [
            "docs_src/request_forms_and_files/tutorial001_py310.py",
            "docs_src/request_forms_and_files/tutorial001_an_py310.py",
        ],
        (
            "Multipart requests combine a bytes file, UploadFile part, and text form "
            "field. OpenAPI observations select mixed requestBody schemas; response "
            "literals and browser behavior are not claimed."
        ),
        {
            "docs_src/request_forms_and_files/tutorial001_py310.py": (
                6,
                14,
                "Mixed bytes, UploadFile, Form parameters and endpoint",
            ),
            "docs_src/request_forms_and_files/tutorial001_an_py310.py": (
                8,
                18,
                "Annotated mixed bytes, UploadFile, Form parameters and endpoint",
            ),
        },
        [
            _case(
                "docs-example-wave-f-form-file-inputs.yaml",
                "fastapi.docs-example-wave-f.request-forms-and-files.mixed-multipart",
                HTTP_OPENAPI,
            )
        ],
    ),
]

DOC_EXAMPLE_CITATION_WAVE_F = {
    path: review
    for paths, rationale, spans, cases in _MAPPINGS
    for path, review in _family(paths, rationale, spans, cases).items()
}


DOC_EXAMPLE_EXCLUSION_WAVE_F = {
    "docs_src/python_types/tutorial001_py310.py": (
        "Pinned source only calls a pure Python string-formatting function; no "
        "FastAPI import, route, request parameter, schema, or ASGI behavior "
        "appears."
    ),
    "docs_src/python_types/tutorial002_py310.py": (
        "Pinned source adds annotations to a pure Python string-formatting "
        "function; FastAPI does not consume the annotations and no ASGI app is "
        "defined."
    ),
    "docs_src/python_types/tutorial003_py310.py": (
        "Pinned source is a pure Python function that concatenates a string and "
        "integer; it defines no FastAPI application or runtime surface."
    ),
    "docs_src/python_types/tutorial004_py310.py": (
        "Pinned source converts an integer to text inside a pure Python "
        "function; no FastAPI import, route, parameter, schema, or ASGI behavior "
        "appears."
    ),
    "docs_src/python_types/tutorial005_py310.py": (
        "Pinned source returns annotated Python values from a local function; "
        "the annotations are not consumed by FastAPI and no ASGI app is defined."
    ),
    "docs_src/python_types/tutorial006_py310.py": (
        "Pinned source loops over a Python list and prints values; it has no "
        "FastAPI runtime behavior."
    ),
    "docs_src/python_types/tutorial007_py310.py": (
        "Pinned source returns a built-in tuple and set from a pure Python "
        "function; it declares no FastAPI request or response behavior."
    ),
    "docs_src/python_types/tutorial008_py310.py": (
        "Pinned source loops over a Python dictionary and prints its entries; it "
        "does not define or call FastAPI."
    ),
    "docs_src/python_types/tutorial008b_py310.py": (
        "Pinned source prints an int-or-str function argument; FastAPI does not "
        "inspect the union annotation."
    ),
    "docs_src/python_types/tutorial009_py310.py": (
        "Pinned source branches on an optional Python string and prints text; it "
        "has no request validation, OpenAPI schema, route, or ASGI behavior."
    ),
    "docs_src/python_types/tutorial010_py310.py": (
        "Pinned source defines a plain Python class and reads its attribute; it "
        "is not a FastAPI model or endpoint."
    ),
    "docs_src/python_types/tutorial011_py310.py": (
        "Pinned source constructs and prints a Pydantic BaseModel from local "
        "data; it imports no FastAPI and exercises no FastAPI request, response, "
        "schema, or ASGI behavior."
    ),
    "docs_src/python_types/tutorial013_py310.py": (
        "Pinned source uses Annotated metadata in a plain Python function; no "
        "FastAPI runtime consumes the annotation."
    ),
}
