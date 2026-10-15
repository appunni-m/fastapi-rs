"""Reviewed section-to-workflow links for query parameter tutorials."""


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


DOC_SECTION_CASE_MAPPINGS_QUERY_PARAMS_1016 = {
    (
        "tutorial/query-params-str-validations.md",
        "query-parameters-and-string-validations",
    ): _workflow(
        "Query Parameters and String Validations { #query-parameters-and-string-validations }",
        1,
        450,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-section-cases-1016.yaml",
        ["fastapi.docs-section.query-params-str-validations.optional-query"],
        [
            "optional-query-omitted",
            "optional-query-supplied",
            "optional-query-openapi-parameter",
        ],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The page-level mapping samples only the opening plain optional-string query example: "
            "it submits q both omitted and supplied and projects that route's OpenAPI parameter. "
            "The independent anchored sections map their own constraints and metadata; this row "
            "does not claim those child behaviors."
        ),
        (
            "The pinned opening example declares q as str | None with a None default. FastAPI "
            "binds that value from the query string and derives its optional OpenAPI parameter; "
            "the workflow uses an independent echo response to avoid treating catalog output as "
            "framework behavior."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "additional-validation"): _workflow(
        "Additional validation { #additional-validation }",
        19,
        41,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial002"],
        ["annotated-over-limit", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The opening claim that q may be omitted but is limited to 50 characters is sampled "
            "with an over-limit request to the Annotated example and its selected OpenAPI "
            "parameter. Imports and version-history prose are reviewed in the child section."
        ),
        (
            "FastAPI turns Query metadata on the Annotated parameter into request validation and "
            "an OpenAPI parameter; the application response and generic HTTP transport are not "
            "the compatibility claim."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "import-query-and-annotated"): _excluded(
        "Import `Query` and `Annotated` { #import-query-and-annotated }",
        23,
        41,
        "This section teaches imports and gives version-upgrade guidance;"
        " it adds no behavior independent of the Annotated Query example "
        "mapped in the following section.",
        "The code listing is the same tutorial002 declaration used to map"
        " the max_length behavior. Import syntax and historical version n"
        "otes are not FastAPI runtime observations.",
    ),
    (
        "tutorial/query-params-str-validations.md",
        "use-annotated-in-the-type-for-the-q-parameter",
    ): _excluded(
        "Use `Annotated` in the type for the `q` parameter { #use-annotat"
        "ed-in-the-type-for-the-q-parameter }",
        42,
        63,
        "This section explains Python typing equivalence for Annotated[st"
        "r | None] before adding FastAPI metadata, so it defines no separ"
        "ate FastAPI behavior.",
        "The pinned source shows no Query or other FastAPI FieldInfo in t"
        "his annotation; the Python type expression and its editor suppor"
        "t belong to Python tooling.",
    ),
    (
        "tutorial/query-params-str-validations.md",
        "add-query-to-annotated-in-the-q-parameter",
    ): _workflow(
        "Add `Query` to `Annotated` in the `q` parameter { #add-query-to-"
        "annotated-in-the-q-parameter }",
        64,
        85,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial002"],
        ["annotated-over-limit", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected Annotated action submits a value longer than 50 characters and projects "
            "the query parameter in OpenAPI. The shared OpenAPI action also includes the direct "
            "comparison endpoint, which is not claimed by this section; optional omission and "
            "the tutorial's catalog response are outside this sample."
        ),
        (
            "FastAPI consumes Query metadata stored in Annotated to validate the query value and "
            "describe it in OpenAPI. Pydantic supplies field validation and Starlette owns generic "
            "HTTP response transport."
        ),
    ),
    (
        "tutorial/query-params-str-validations.md",
        "alternative-old-query-as-the-default-value",
    ): _workflow(
        "Alternative (old): `Query` as the default value { #alternative-o"
        "ld-query-as-the-default-value }",
        86,
        162,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial002"],
        ["direct-over-limit", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected direct-style request exercises the documented max_length=50 rejection "
            "and the matching OpenAPI parameter. The shared schema action also projects the "
            "Annotated comparison route; this row does not claim behavior from FastAPI versions "
            "before the pinned release."
        ),
        (
            "FastAPI interprets Query used as a parameter default as query metadata and applies "
            "the declared constraint; the mapping is limited to this direct-style declaration "
            "under FastAPI 0.141.1."
        ),
    ),
    (
        "tutorial/query-params-str-validations.md",
        "query-as-the-default-value-or-in-annotated",
    ): _workflow(
        "`Query` as the default value or in `Annotated` { #query-as-the-d"
        "efault-value-or-in-annotated }",
        125,
        150,
        "tests/fixtures/input-recipes/parity/core-ambiguous-params-construction-upstream.yaml",
        ["fastapi.request.ambiguous-params.query-default-in-annotated"],
        None,
        ["construction.exception_class", "construction.exception_message", "construction.outcome"],
        (
            "The selected construction input covers only rejection of a Query default placed "
            "inside Annotated; the prose's valid alternatives and sample literal values are "
            "not separately exercised."
        ),
        (
            "FastAPI 0.141.1 rejects a FieldInfo default inside Annotated during parameter "
            "analysis and directs callers to set the function parameter default with =."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "advantages-of-annotated"): _excluded(
        "Advantages of `Annotated` { #advantages-of-annotated }",
        151,
        162,
        "This section makes recommendations about Python function calls, "
        "editor diagnostics, and interoperability with Typer rather than "
        "defining an independently observable FastAPI contract.",
        "The pinned text describes Python's own signature/default behavio"
        "r and another tool's metadata use; FastAPI's parameter binding i"
        "s mapped in the adjacent runtime sections.",
    ),
    ("tutorial/query-params-str-validations.md", "add-more-validations"): _workflow(
        "Add more validations { #add-more-validations }",
        163,
        168,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial003"],
        ["annotated-below-minimum", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The selected Annotated request is below min_length=3; the linked OpenAPI action "
            "projects the parameter's constraints. Its pointer also includes the direct-style "
            "comparison endpoint, which is not claimed by this section."
        ),
        (
            "FastAPI turns the Query min_length metadata into validation and OpenAPI parameter "
            "constraints; Pydantic performs field validation."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "add-regular-expressions"): _workflow(
        "Add regular expressions { #add-regular-expressions }",
        169,
        184,
        "tests/fixtures/input-recipes/parity/query-params-str-validations"
        "-doc-pattern-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial004"],
        ["annotated-pattern-mismatch", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated example receives a value that does not match the anchored pattern, "
            "and the OpenAPI action projects that parameter schema. Its schema action also has "
            "the direct-style comparison pointer; no regular-expression behavior outside this "
            "declared query parameter is claimed."
        ),
        (
            "FastAPI passes the Query pattern constraint into request field validation and "
            "OpenAPI generation; regex engine details remain part of the declared Python/Pydantic "
            "validation contract."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "default-values"): _workflow(
        "Default values { #default-values }",
        185,
        198,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial005"],
        ["annotated-default-value", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The request omits q so the Annotated route's non-None default is used; its OpenAPI "
            "parameter is projected as well. The shared OpenAPI action also includes the direct "
            "comparison endpoint, and the independent echo response is not th"
            "e documented catalog output."
        ),
        (
            "FastAPI uses the Python parameter default to make the query optional and applies the "
            "Query min_length constraint to supplied values; the selected omission exercises the "
            "documented non-None default path."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "required-parameters"): _workflow(
        "Required parameters { #required-parameters }",
        199,
        230,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial006"],
        ["annotated-required-value-omitted", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated request omits q and observes the handled validation response; the "
            "OpenAPI action projects the required query parameter. The selected pointers also "
            "include the direct-style comparison route."
        ),
        (
            "FastAPI infers requiredness from the missing Python default, validates the request, "
            "and documents the parameter as required; Starlette owns generic HTTP transport."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "required-can-be-none"): _workflow(
        "Required, can be `None` { #required-can-be-none }",
        223,
        230,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial006c"],
        ["annotated-required-nullable-omitted", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated request omits q and observes requiredness in the handled validation "
            "response; the OpenAPI parameter projection records the nullable required declaration. "
            "An HTTP query string cannot carry Python None as a distinct value, so this mapping "
            "does not claim a wire representation for None."
        ),
        (
            "FastAPI separates nullable type annotation from parameter requiredness, which is "
            "inferred from the absence of a default. Query-string transport supplies text values; "
            "the docs' Python None wording does not define a separate wire value."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "query-parameter-list-multiple-values"): _workflow(
        "Query parameter list / multiple values { #query-parameter-list-multiple-values }",
        231,
        304,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial011"],
        ["annotated-repeated-values", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated action sends two q occurrences and observes the endpoint response; the "
            "OpenAPI action projects the collection parameter. Its shared pointer action also "
            "includes the direct-style comparison endpoint; browser UI rendering is not run."
        ),
        (
            "FastAPI recognizes the Query-declared sequence as a query parameter and extracts "
            "repeated values; Starlette supplies the generic query multi-dict transport."
        ),
    ),
    (
        "tutorial/query-params-str-validations.md",
        "query-parameter-list-multiple-values-with-defaults",
    ): _workflow(
        "Query parameter list / multiple values with defaults { #query-pa"
        "rameter-list-multiple-values-with-defaults }",
        268,
        304,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial012"],
        ["annotated-default-list", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated action omits q to exercise its nonempty default list, then the OpenAPI "
            "action projects the declared query collection. The shared OpenAPI pointer also "
            "includes the direct-style comparison route; the page's example response literal is "
            "not embedded as an expected value."
        ),
        (
            "FastAPI treats the parameter's Python list default as the value used when no query "
            "items are sent and builds the corresponding query parameter schema."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "using-just-list"): _workflow(
        "Using just `list` { #using-just-list }",
        291,
        304,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-section-cases-1016.yaml",
        ["fastapi.docs-section.query-params-str-validations.untyped-list-items"],
        [
            "bare-list-repeated-text-values",
            "typed-integer-list-rejects-text",
            "list-item-openapi-schemas",
        ],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The independent workflow sends repeated text items to a bare list and a non-integer "
            "item to a list[int] comparator, then projects both query parameter schemas. This "
            "isolates item-type validation and schema detail; it does not claim default-list "
            "behavior, which is mapped in the parent section."
        ),
        (
            "FastAPI classifies sequence query annotations, while Pydantic validates declared "
            "item types and contributes their schema; a bare list has no declared item type."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "declare-more-metadata"): _workflow(
        "Declare more metadata { #declare-more-metadata }",
        305,
        326,
        "tests/fixtures/input-recipes/parity/query-params-str-validations"
        "-doc-title-description-examples.yaml",
        [
            "fastapi.docs-example.query-params-str-validations.tutorial007",
            "fastapi.docs-example.query-params-str-validations.tutorial008",
        ],
        ["openapi-query-contract"],
        ["docs.response.status", "http.status", "openapi.document", "openapi.paths"],
        (
            "The selected OpenAPI actions project the title and description parameter objects for "
            "the two Annotated examples. Each shared action also includes its direct-style "
            "comparison pointer; external tools and their display choices are not exercised."
        ),
        (
            "FastAPI carries Query title and description metadata into generated OpenAPI; "
            "third-party UI support is not a FastAPI runtime guarantee."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "alias-parameters"): _workflow(
        "Alias parameters { #alias-parameters }",
        327,
        346,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial009"],
        ["annotated-aliased-value", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated action sends the hyphenated item-query name and projects its OpenAPI "
            "parameter. The shared schema pointer also includes the direct-style comparison route."
        ),
        (
            "FastAPI uses Query(alias=...) to bind the wire name to the Python parameter and "
            "describe that name in OpenAPI."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "deprecating-parameters"): _workflow(
        "Deprecating parameters { #deprecating-parameters }",
        347,
        360,
        "tests/fixtures/input-recipes/parity/query-params-str-validations"
        "-doc-pattern-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial010"],
        ["openapi-query-contract"],
        ["docs.response.status", "http.status", "openapi.document", "openapi.paths"],
        (
            "The selected OpenAPI action projects the deprecated Annotated parameter object. The "
            "same pointer action includes the direct-style comparison route and other metadata; "
            "the screenshot and generated UI rendering are not observed."
        ),
        (
            "FastAPI passes Query(deprecated=True) into the operation's OpenAPI parameter; the "
            "rendered documentation interface belongs to the UI consumer."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "exclude-parameters-from-openapi"): _workflow(
        "Exclude parameters from OpenAPI { #exclude-parameters-from-openapi }",
        361,
        366,
        "tests/fixtures/input-recipes/parity/query-params-str-validations"
        "-doc-exclude-schema-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial014"],
        ["annotated-hidden-query-value", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The Annotated action sends the hidden query value and the OpenAP"
            "I action projects both "
            "example operations to show that the parameter is omitted. The shared OpenAPI action "
            "includes a direct-style comparison operation as context."
        ),
        (
            "FastAPI continues to bind the query parameter at runtime while i"
            "nclude_in_schema=False "
            "keeps it out of the generated OpenAPI operation; generic HTTP tr"
            "ansport is not the claim."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "custom-validation"): _workflow(
        "Custom Validation { #custom-validation }",
        367,
        428,
        "tests/fixtures/input-recipes/parity/query-params-str-validations-doc-examples.yaml",
        ["fastapi.docs-example.query-params-str-validations.tutorial015"],
        ["annotated-valid-prefix", "annotated-invalid-prefix", "openapi-query-contract"],
        [
            "docs.response.status",
            "http.body.bytes",
            "http.status",
            "openapi.document",
            "openapi.paths",
        ],
        (
            "The independent Annotated workflow submits one accepted and one rejected ID, then "
            "projects the query parameter schema. It does not reproduce the tutorial catalog, "
            "random fallback, external dependency advice, or browser UI."
        ),
        (
            "FastAPI integrates the query parameter with Pydantic's AfterValidator and returns the "
            "validation result through its request handling; Pydantic owns th"
            "e validator's value rule."
        ),
    ),
    ("tutorial/query-params-str-validations.md", "a-random-item"): _excluded(
        "A Random Item { #a-random-item }",
        413,
        428,
        "This section explains Python dict/list iteration, random.choice("
        "), and application-owned fallback data rather than FastAPI behav"
        "ior.",
        "The pinned example selects a catalog entry when the request omit"
        "s an ID; its random result and Python collection operations do n"
        "ot define a FastAPI contract.",
    ),
}
