"""Reviewed section mappings for the FastAPI path-parameter tutorials."""

_PATH = "tests/fixtures/input-recipes/parity/docs-path-params-1016.yaml"
_NUMERIC = "tests/fixtures/input-recipes/parity/docs-path-params-numeric-validations-1016.yaml"

_HTTP = ["http.body.bytes", "http.status"]
_OPENAPI = ["openapi.document", "openapi.paths"]
_HTTP_OPENAPI = sorted([*_HTTP, *_OPENAPI])


def _workflow(heading, start, end, recipe, cases, actions, selectors, note, rationale):
    row = {
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
        row["action_ids"] = actions
    return row


def _excluded(heading, start, end, reason, rationale):
    return {
        "status": "excluded",
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "exclusion_reason": reason,
        "rationale": rationale,
    }


DOC_SECTION_CASE_MAPPINGS_PATH_PARAMS_1016 = {
    ("tutorial/path-params.md", "path-parameters"): _workflow(
        "Path Parameters { #path-parameters }",
        1,
        251,
        _PATH,
        ["fastapi.docs.path-params-1016.basic-string"],
        ["string-path-value"],
        _HTTP,
        "The H1 span includes the descendant sections; this link scopes o"
        "nly the introductory untyped route and returned string value. De"
        "scendant features are mapped separately, and editor support is n"
        "ot measured.",
        "The pinned FastAPI example binds the path segment to an unannota"
        "ted endpoint parameter; generic URL matching is supplied by Star"
        "lette 1.6.0.",
    ),
    ("tutorial/path-params.md", "path-parameters-with-types"): _workflow(
        "Path parameters with types { #path-parameters-with-types }",
        15,
        28,
        _PATH,
        ["fastapi.docs.path-params-1016.integer-path"],
        ["integer-path-value"],
        _HTTP,
        "The selected request sends an integer path value through the doc"
        "umented int-annotated route and observes its numeric JSON value."
        " The editor-support tip is not measured.",
        "FastAPI classifies the annotated path parameter and Pydantic val"
        "idates and serializes its integer value; Starlette 1.6.0 supplie"
        "s generic request dispatch.",
    ),
    ("tutorial/path-params.md", "data-validation"): _workflow(
        "Data validation { #data-validation }",
        45,
        78,
        _PATH,
        ["fastapi.docs.path-params-1016.integer-path-validation"],
        ["invalid-integer-path-text", "invalid-integer-path-decimal"],
        _HTTP,
        "The actions send non-integer and decimal text to the int-annotat"
        "ed path parameter and observe the handled HTTP status and exact "
        "response bytes; they do not claim every validation error form.",
        "FastAPI routes path-field validation failures through its reques"
        "t-validation response handling; Pydantic owns integer parsing an"
        "d Starlette owns the ASGI transport.",
    ),
    ("tutorial/path-params.md", "documentation"): _workflow(
        "Documentation { #documentation }",
        79,
        92,
        _PATH,
        ["fastapi.docs.path-params-1016.documentation"],
        ["typed-openapi-schema", "swagger-ui-route"],
        _HTTP_OPENAPI,
        "The selected OpenAPI pointer checks the typed path parameter sch"
        "ema, while the /docs action observes Swagger UI route availabili"
        "ty. It does not compare rendered pixels or browser behavior.",
        "FastAPI constructs the operation parameter schema and serves the"
        " configured docs route; Starlette 1.6.0 provides the outer HTTP "
        "response boundary.",
    ),
    (
        "tutorial/path-params.md",
        "standards-based-benefits-alternative-documentation",
    ): _workflow(
        "Standards-based benefits, alternative documentation { #standards"
        "-based-benefits-alternative-documentation }",
        93,
        102,
        _PATH,
        ["fastapi.docs.path-params-1016.redoc"],
        ["redoc-ui-route"],
        _HTTP,
        "The action observes the ReDoc endpoint response. It does not ass"
        "ert interoperability with external OpenAPI tools or code generat"
        "ors.",
        "The pinned page identifies FastAPI's ReDoc route as the alternat"
        "ive documentation endpoint; external standards consumers are out"
        "side this runtime observation.",
    ),
    ("tutorial/path-params.md", "pydantic"): _workflow(
        "Pydantic { #pydantic }",
        103,
        110,
        _PATH,
        ["fastapi.docs.path-params-1016.scalar-types"],
        ["bool-float-scalar-path"],
        _HTTP,
        "The action samples bool and float path conversion through one en"
        "dpoint. It does not claim every Pydantic type, custom type, or P"
        "ydantic behavior in isolation.",
        "FastAPI extracts the annotated path values and Pydantic validate"
        "s and serializes these representative scalar types.",
    ),
    ("tutorial/path-params.md", "order-matters"): _workflow(
        "Order matters { #order-matters }",
        111,
        130,
        _PATH,
        ["fastapi.docs.path-params-1016.route-order"],
        ["static-route-before-dynamic", "dynamic-user-route", "duplicate-route-first"],
        _HTTP,
        "The selected requests observe the fixed /users/me route before t"
        "he dynamic user route and the first duplicate route. The sample "
        "does not generalize ordering across all route converters or meth"
        "ods.",
        "FastAPI registers the documented path operations in declaration "
        "order; Starlette 1.6.0 owns ordered route matching and first-mat"
        "ch dispatch.",
    ),
    ("tutorial/path-params.md", "predefined-values"): _workflow(
        "Predefined values { #predefined-values }",
        131,
        201,
        _PATH,
        ["fastapi.docs.path-params-1016.enum-model"],
        ["enum-valid-model", "enum-invalid-model", "enum-openapi-schema"],
        _HTTP_OPENAPI,
        "The actions sample one declared enum member, one rejected value,"
        " and its OpenAPI enum schema. The child sections separately scop"
        "e comparison, value access, and response serialization.",
        "FastAPI uses the endpoint's string Enum annotation for path vali"
        "dation and OpenAPI generation; Pydantic supplies field validatio"
        "n and schema details.",
    ),
    ("tutorial/path-params.md", "create-an-enum-class"): _excluded(
        "Create an `Enum` class { #create-an-enum-class }",
        135,
        150,
        "The section teaches creation of a standard-library `str, Enum` c"
        "lass and its fixed attributes; FastAPI's use of those values is "
        "exercised in the parameter and OpenAPI child sections.",
        "The pinned span defines Python's Enum subclass and members but d"
        "oes not declare a FastAPI operation; route binding and schema ge"
        "neration are independently mapped below.",
    ),
    ("tutorial/path-params.md", "declare-a-path-parameter"): _workflow(
        "Declare a *path parameter* { #declare-a-path-parameter }",
        151,
        156,
        _PATH,
        ["fastapi.docs.path-params-1016.enum-model"],
        ["enum-valid-model"],
        _HTTP,
        "The request supplies a declared enum value to the enum-annotated"
        " path parameter and observes the route response. It does not cla"
        "im all possible enum declarations.",
        "FastAPI binds and validates the documented enum annotation on a "
        "path operation, with Pydantic supplying enum field validation.",
    ),
    ("tutorial/path-params.md", "check-the-docs"): _workflow(
        "Check the docs { #check-the-docs }",
        157,
        162,
        _PATH,
        ["fastapi.docs.path-params-1016.enum-model"],
        ["enum-openapi-schema"],
        _OPENAPI,
        "The selected pointer checks the operation's enum parameter schem"
        "a. It does not compare Swagger UI rendering or image pixels.",
        "FastAPI emits the enum's available path values in its generated "
        "OpenAPI schema; the input selects that schema pointer.",
    ),
    ("tutorial/path-params.md", "working-with-python-enumerations"): _workflow(
        "Working with Python *enumerations* { #working-with-python-enumerations }",
        163,
        201,
        _PATH,
        ["fastapi.docs.path-params-1016.enum-model"],
        ["enum-valid-model"],
        _HTTP,
        "The selected request observes one enum member reaching the endpo"
        "int. Child mappings select member comparison, `.value` access, a"
        "nd response serialization separately.",
        "FastAPI validates the enum path value before endpoint invocation"
        "; the endpoint example then receives a Python enum member.",
    ),
    ("tutorial/path-params.md", "compare-enumeration-members"): _excluded(
        "Compare *enumeration members* { #compare-enumeration-members }",
        167,
        172,
        "The section explains Python `Enum` member identity comparison in"
        "side application logic; enum path binding is covered by the pare"
        "nt section.",
        "The pinned example's `is ModelName.alexnet` branch is ordinary P"
        "ython application behavior and adds no independent FastAPI contr"
        "act.",
    ),
    ("tutorial/path-params.md", "get-the-enumeration-value"): _excluded(
        "Get the *enumeration value* { #get-the-enumeration-value }",
        173,
        184,
        "The section describes Python's standard `Enum.value` accessor in"
        "side application code; enum parameter conversion and response se"
        "rialization are mapped separately.",
        "The pinned example reads `model_name.value` after FastAPI has su"
        "pplied an enum member; the accessor itself has no independent Fa"
        "stAPI behavior.",
    ),
    ("tutorial/path-params.md", "return-enumeration-members"): _workflow(
        "Return *enumeration members* { #return-enumeration-members }",
        185,
        201,
        _PATH,
        ["fastapi.docs.path-params-1016.enum-model"],
        ["enum-resnet-member-return"],
        _HTTP,
        "The resnet request selects a return value containing the enum me"
        "mber and observes the serialized response. Nested containers and"
        " other enum shapes are outside this sample.",
        "FastAPI's response serialization converts the returned string En"
        "um member into its JSON string value; generic response transport"
        " belongs to Starlette 1.6.0.",
    ),
    ("tutorial/path-params.md", "path-parameters-containing-paths"): _workflow(
        "Path parameters containing paths { #path-parameters-containing-paths }",
        202,
        239,
        _PATH,
        ["fastapi.docs.path-params-1016.path-converter"],
        ["nested-file-path", "file-path-openapi-schema"],
        _HTTP_OPENAPI,
        "The request samples one multi-segment `/files/{file_path:path}` "
        "value and the OpenAPI action selects that route. Generic path-co"
        "nverter matching belongs to Starlette 1.6.0.",
        "FastAPI registers the documented converter route and generates i"
        "ts operation schema; Starlette 1.6.0 owns matching the multi-seg"
        "ment path value.",
    ),
    ("tutorial/path-params.md", "openapi-support"): _workflow(
        "OpenAPI support { #openapi-support }",
        210,
        217,
        _PATH,
        ["fastapi.docs.path-params-1016.path-converter"],
        ["file-path-openapi-schema"],
        _OPENAPI,
        "The pointer observes the generated operation parameter for the p"
        "ath-converter route; it does not claim OpenAPI can express slash"
        "-containing path values or that the docs explain this limitation"
        ".",
        "The page distinguishes the OpenAPI specification's path-value li"
        "mitation from FastAPI's generated route documentation; the selec"
        "ted pointer observes only the latter.",
    ),
    ("tutorial/path-params.md", "path-convertor"): _workflow(
        "Path convertor { #path-convertor }",
        218,
        239,
        _PATH,
        ["fastapi.docs.path-params-1016.path-converter"],
        ["nested-file-path"],
        _HTTP,
        "The action requests one nested file path and observes the endpoi"
        "nt's returned `file_path`; leading-slash handling is not sampled"
        ".",
        "FastAPI exposes the documented Starlette converter syntax on the"
        " route; Starlette 1.6.0 supplies generic path-converter matching"
        ".",
    ),
    (
        "tutorial/path-params-numeric-validations.md",
        "path-parameters-and-numeric-validations",
    ): _workflow(
        "Path Parameters and Numeric Validations { #path-parameters-and-numeric-validations }",
        1,
        154,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.ge-boundary"],
        ["ge-equal-boundary", "ge-below-boundary"],
        _HTTP,
        "The H1 span includes the descendant sections; these actions scop"
        "e the introductory Path constraint at and below its inclusive bo"
        "undary. Query metadata and other numeric bounds are mapped separ"
        "ately.",
        "FastAPI forwards Path constraints into request-field validation;"
        " Pydantic enforces the numeric boundary and Starlette 1.6.0 carr"
        "ies the request.",
    ),
    ("tutorial/path-params-numeric-validations.md", "import-path"): _workflow(
        "Import `Path` { #import-path }",
        5,
        20,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.metadata"],
        ["metadata-success"],
        _HTTP,
        "The workload imports `Path` from FastAPI to construct the select"
        "ed metadata route, then observes a valid request. It does not as"
        "sert import-path identity or the historical Annotated version no"
        "te.",
        "The pinned example imports the public Path factory and uses it i"
        "n a route declaration; the request confirms the constructed para"
        "meter participates in routing and validation.",
    ),
    ("tutorial/path-params-numeric-validations.md", "declare-metadata"): _workflow(
        "Declare metadata { #declare-metadata }",
        21,
        34,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.metadata"],
        ["metadata-success", "metadata-openapi"],
        _HTTP_OPENAPI,
        "The valid request exercises the annotated Path parameter, and th"
        "e OpenAPI pointer selects its parameter schema and title. The in"
        "put does not claim alternate defaults or nullable declarations.",
        "FastAPI's Path factory carries title and location metadata into "
        "field creation and OpenAPI; Pydantic contributes the integer sch"
        "ema.",
    ),
    ("tutorial/path-params-numeric-validations.md", "order-the-parameters-as-you-need"): _workflow(
        "Order the parameters as you need { #order-the-parameters-as-you-need }",
        35,
        62,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.parameter-order"],
        ["default-parameter-order", "annotated-parameter-order"],
        _HTTP,
        "The actions call equivalent routes whose required query and Path"
        " parameters have the two documented Python declaration forms. Th"
        "ey do not exhaust all parameter kinds or defaults.",
        "FastAPI classifies endpoint parameters from their names, annotat"
        "ions, and Path declarations rather than relying on source argume"
        "nt order.",
    ),
    (
        "tutorial/path-params-numeric-validations.md",
        "order-the-parameters-as-you-need-tricks",
    ): _workflow(
        "Order the parameters as you need, tricks { #order-the-parameters-as-you-need-tricks }",
        63,
        93,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.keyword-only-order"],
        ["keyword-only-path-query", "keyword-only-annotated-path-query"],
        _HTTP,
        "The requests sample the documented `*` keyword-only form and its"
        " Annotated counterpart with a required query value. They do not "
        "assert Python's general argument-binding rules.",
        "FastAPI recognizes the same Path/query locations in both documen"
        "ted endpoint declarations; Python owns keyword-only call syntax.",
    ),
    ("tutorial/path-params-numeric-validations.md", "better-with-annotated"): _workflow(
        "Better with `Annotated` { #better-with-annotated }",
        88,
        93,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.keyword-only-order"],
        ["keyword-only-annotated-path-query"],
        _HTTP,
        "The selected request exercises only the Annotated declaration fr"
        "om the preceding keyword-only example; it does not compare edito"
        "r diagnostics.",
        "The annotated Path metadata is read from the endpoint annotation"
        ", so a Python default value is not needed for this form.",
    ),
    (
        "tutorial/path-params-numeric-validations.md",
        "number-validations-greater-than-or-equal",
    ): _workflow(
        "Number validations: greater than or equal { #number-validations-greater-than-or-equal }",
        94,
        101,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.ge-boundary"],
        ["ge-equal-boundary", "ge-below-boundary"],
        _HTTP,
        "The actions probe the `ge=1` Path bound at its inclusive boundar"
        "y and immediately below it while supplying the example's require"
        "d query parameter.",
        "FastAPI forwards the documented Path bound into request validati"
        "on; Pydantic enforces the inclusive numeric comparison.",
    ),
    (
        "tutorial/path-params-numeric-validations.md",
        "number-validations-greater-than-and-less-than-or-equal",
    ): _workflow(
        "Number validations: greater than and less than or equal { #numbe"
        "r-validations-greater-than-and-less-than-or-equal }",
        102,
        110,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.gt-le-boundary"],
        ["gt-zero-rejected", "le-equal-boundary", "le-above-boundary-rejected"],
        _HTTP,
        "The actions probe the source example's `gt=0` lower bound and `l"
        "e=1000` upper bound at and outside representative boundaries; al"
        "l requests supply its required query parameter.",
        "FastAPI extracts Path metadata and Pydantic enforces strict lowe"
        "r and inclusive upper numeric bounds.",
    ),
    (
        "tutorial/path-params-numeric-validations.md",
        "number-validations-floats-greater-than-and-less-than",
    ): _workflow(
        "Number validations: floats, greater than and less than { #number"
        "-validations-floats-greater-than-and-less-than }",
        111,
        122,
        _NUMERIC,
        ["fastapi.docs.path-params-numeric-1016.float-query-boundary"],
        ["float-fraction-valid", "float-zero-rejected", "float-upper-bound-rejected"],
        _HTTP,
        "The actions sample the code block's float Query constraint (`gt="
        "0`, `lt=10.5`) with a valid fraction and both exclusive boundari"
        "es. The route's integer Path bounds are setup only.",
        "FastAPI classifies the size field as a query parameter and Pydan"
        "tic validates its float value against the exclusive bounds.",
    ),
    ("tutorial/path-params-numeric-validations.md", "recap"): _workflow(
        "Recap { #recap }",
        123,
        154,
        _NUMERIC,
        [
            "fastapi.docs.path-params-numeric-1016.ge-boundary",
            "fastapi.docs.path-params-numeric-1016.gt-le-boundary",
            "fastapi.docs.path-params-numeric-1016.float-query-boundary",
        ],
        None,
        _HTTP,
        "These complete input cases sample inclusive and exclusive numeri"
        "c boundaries from the recap's `ge`, `gt`, `le`, and `lt` bullets"
        ". The Param class and editor-typing explanation is not asserted.",
        "The selected examples exercise FastAPI's Path and Query paramete"
        "r declaration with Pydantic numeric validation; the recap's cons"
        "tructor implementation explanation is outside this request sampl"
        "e.",
    ),
}
