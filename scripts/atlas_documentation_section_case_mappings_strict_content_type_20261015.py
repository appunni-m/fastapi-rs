"""Reviewed section mapping for FastAPI's strict Content-Type opt-out docs."""

_PAGE = "advanced/strict-content-type.md"
_RECIPE = (
    "tests/fixtures/input-recipes/parity/strict-content-type-documentation-example-independent.yaml"
)


DOC_SECTION_CASE_MAPPINGS_STRICT_CONTENT_TYPE_20261015 = {
    (_PAGE, "allowing-requests-without-content-type"): {
        "heading": (
            "Allowing Requests Without Content-Type { #allowing-requests-without-content-type }"
        ),
        "start_line": 76,
        "end_line": 88,
        "recipe_path": _RECIPE,
        "case_ids": ["fastapi.docs.strict-content-type.independent-legacy-no-content-type"],
        "action_ids": ["legacy-route-parses-untyped-json"],
        "observation_selectors": ["http.status", "http.body.bytes"],
        "scope_note": (
            "Partial: one successful POST omits Content-Type and sends a JSON-shaped body to "
            "an independently authored /legacy/items/ route; the selected observations are "
            "only HTTP status and response body bytes. This does not establish the tutorial "
            "route's literal output, rejection behavior, malformed or empty-body behavior, "
            "form parsing, or the documented CSRF/CORS scenario."
        ),
        "rationale": (
            "The pinned FastAPI 0.157.0 section at "
            "docs/en/docs/advanced/strict-content-type.md:76-88 documents setting "
            "strict_content_type=False, the no-Content-Type JSON behavior, and the 0.132.0 "
            "version boundary. Its source_evidence entry in the input recipe cites this exact "
            "page as upstream_documentation. The adjacent example, "
            "docs_src/strict_content_type/tutorial001_py310.py:1-14, configures that option "
            "and declares POST /items/ with an Item body. The independent workload instead "
            "uses /legacy/items/, a different model, and different values. FastAPI 0.157.0 "
            "declares strict_content_type with default True and documents its JSON handling "
            "in fastapi/applications.py:847, then forwards the configured value to the "
            "router in fastapi/applications.py:995; request handling applies the no-header "
            "branch in fastapi/routing.py:412-475. The selected case exercises only the "
            "successful no-header request branch and observes HTTP status and body bytes."
        ),
    }
}
