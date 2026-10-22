"""Reviewed section mapping for FastAPI path-parameter data conversion."""

DOC_SECTION_CASE_MAPPINGS_DATA_CONVERSION_20261015 = {
    ("tutorial/path-params.md", "data-conversion"): {
        "status": "excluded",
        "heading": (
            'Data <dfn title="also known as: serialization, parsing, marshalling">'
            "conversion</dfn> { #data-conversion }"
        ),
        "start_line": 29,
        "end_line": 44,
        "exclusion_reason": (
            "This explanatory conversion section reuses the same typed integer path input "
            "and response already mapped under the preceding path-parameters-with-types "
            "section; it adds no distinct request or observation."
        ),
        "rationale": (
            "Pinned FastAPI 0.157.0 docs/en/docs/tutorial/path-params.md:29-44 explains the "
            "integer conversion from the same tutorial002 typed route whose independent "
            "integer-path-value action is linked to #path-parameters-with-types. That linked "
            "action already supplies the path value and observes the numeric JSON response. "
            "This follow-on section adds explanatory detail but no independent FastAPI input "
            "or result selector, so it is excluded as a separate fixture mapping."
        ),
    }
}
