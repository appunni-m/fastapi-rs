"""Reviewed mapping for FastAPI's jsonable encoder tutorial section."""


DOC_SECTION_CASE_MAPPINGS_JSONABLE_ENCODER_20261015 = {
    ("tutorial/encoder.md", "using-the-jsonable-encoder"): {
        "heading": "Using the `jsonable_encoder` { #using-the-jsonable-encoder }",
        "start_line": 9,
        "end_line": 35,
        "recipe_path": "tests/fixtures/input-recipes/parity/encoding.yaml",
        "case_ids": ["fastapi.jsonable-encoder.tutorial.datetime-model"],
        "observation_selectors": ["python.attribute_value", "python.signature"],
        "scope_note": (
            "The direct `jsonable_encoder` call uses a Pydantic Item with the tutorial's "
            "title, datetime timestamp, and optional description fields. Its independent "
            "values include an explicit description, and only the converted return value "
            "and callable signature are observed. This does not cover database writes, "
            "HTTP/ASGI dispatch, the section's note about FastAPI's internal use, other "
            "input types, or encoder option behavior."
        ),
        "rationale": (
            "FastAPI 0.141.1's pinned docs/en/docs/tutorial/encoder.md:11-29 describe "
            "converting the tutorial's Pydantic model and datetime to JSON-compatible "
            "Python data, and docs_src/encoder/tutorial001_py310.py:10-13,19-22 define "
            "and call the example. The active case uses the same Item field types and "
            "direct call with independent values. FastAPI's fastapi/encoders.py:129-230 "
            "defines the callable and its stated conversion purpose; "
            "fastapi/encoders.py:243-258 calls "
            "model_dump in JSON mode for BaseModel inputs and recursively encodes the "
            "result. Pydantic supplies model JSON-mode serialization. The recipe emits "
            "python.attribute_value for the exact return value and python.signature for "
            "the callable signature."
        ),
    }
}
