"""Reviewed section mapping for FastAPI dependency overrides documentation."""


_RECIPE = "tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml"


DOC_SECTION_CASE_MAPPINGS_DEPENDENCY_OVERRIDES_20261015 = {
    (
        "advanced/testing-dependencies.md",
        "use-the-app-dependency-overrides-attribute",
    ): {
        "heading": (
            "Use the `app.dependency_overrides` attribute "
            "{ #use-the-app-dependency-overrides-attribute }"
        ),
        "start_line": 23,
        "end_line": 53,
        "recipe_path": _RECIPE,
        "case_ids": ["fastapi.dependencies.override-resolution"],
        "action_ids": ["replacement-parameter", "original-parameter-absent"],
        "observation_selectors": ["http.body.bytes", "http.status"],
        "scope_note": (
            "Two GET actions exercise one path-operation dependency that `create_app` "
            "has already overridden. `replacement-parameter` supplies `region=west`; "
            "`original-parameter-absent` supplies the original callable's `q=west` and "
            "omits the replacement's required `region`. The selected HTTP status and "
            "body-byte observations cover replacement-parameter resolution and its "
            "response. They do not sample clearing the dictionary, setting or resetting "
            "overrides inside test functions, decorator or included-router dependencies, "
            "replacement sub-dependencies, or other callable and parameter shapes."
        ),
        "rationale": (
            "The pinned section describes using the original dependency callable as the "
            "dictionary key and an override callable as its value "
            "(`../fastapi/docs/en/docs/advanced/testing-dependencies.md:25-30`); "
            "its example assigns that mapping directly "
            "(`../fastapi/docs_src/dependency_testing/tutorial001_an_py310.py:26-31`). "
            "FastAPI 0.141.1 initializes `dependency_overrides` as a dictionary "
            "(`../fastapi/fastapi/applications.py:967-983`). During request resolution, "
            "`solve_dependencies` looks up the original callable and builds a dependant "
            "from the selected override callable "
            "(`../fastapi/fastapi/dependencies/utils.py:619-638`), then invokes that "
            "callable with its resolved values "
            "(`../fastapi/fastapi/dependencies/utils.py:673-680`). "
            "The workload uses an original `q` parameter and a replacement `region` "
            "parameter, installs that mapping, and attaches the original callable to a "
            "path operation (`tests/fixtures/workloads/dependency_lifecycle.py:36-48`). "
            "The recipe actions at "
            "`tests/fixtures/input-recipes/parity/dependency-lifecycle.yaml:149-214` "
            "supply the corresponding query inputs and observe HTTP status and body bytes. "
            "The identity-checked oracle artifact `parity-results/oracle/"
            "bd14cdf1-f552-4eec-8b0f-44add4a0b1f1.json` records both actions as completed "
            "under FastAPI 0.141.1 and Starlette 1.6.0. This maps the path-operation "
            "override resolution shown by those inputs, not every override location or "
            "the section's reset and test setup guidance."
        ),
    }
}
