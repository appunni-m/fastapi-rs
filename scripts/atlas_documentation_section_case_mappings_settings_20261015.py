"""Reviewed section mappings for FastAPI's settings documentation page."""

_PAGE = "advanced/settings.md"
_RECIPE = "tests/fixtures/input-recipes/parity/settings-doc-review-20261015.yaml"
_HTTP = ["http.body.bytes", "http.status"]


def _workflow(heading, start, end, case_id, action_id, note, rationale):
    return {
        "heading": heading,
        "start_line": start,
        "end_line": end,
        "recipe_path": _RECIPE,
        "case_ids": [case_id],
        "action_ids": [action_id],
        "observation_selectors": _HTTP,
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


_GLOBAL_CASE = "fastapi.docs.settings.global-settings-projection-20261015"
_GLOBAL_ACTION = "read-global-settings"
_OVERRIDE_CASE = "fastapi.docs.settings.dependency-override-20261015"
_OVERRIDE_ACTION = "read-dependency-override"


DOC_SECTION_CASE_MAPPINGS_SETTINGS_20261015 = {
    (_PAGE, "settings-and-environment-variables"): _excluded(
        "Settings and Environment Variables { #settings-and-environment-variables }",
        1,
        326,
        (
            "The page introduces operating-system configuration, Pydantic Settings, and a "
            "FastAPI dependency example. It defines no additional independent request beyond "
            "the specifically mapped settings response and dependency-override sections."
        ),
        (
            "The operating-system environment contract and Pydantic Settings behavior are "
            "outside FastAPI's contract. The global settings response is sampled under "
            "`use-the-settings`; FastAPI dependency injection and replacement are sampled "
            "under `the-main-app-file` and `settings-and-testing`."
        ),
    ),
    (_PAGE, "types-and-validation"): _excluded(
        "Types and validation { #types-and-validation }",
        19,
        24,
        (
            "The section describes operating-system environment values as strings and "
            "application-side conversion and validation. FastAPI does not read or convert "
            "environment variables for a user-defined settings object."
        ),
        (
            "The pinned text assigns conversion and validation to code using Pydantic "
            "Settings. Those semantics belong to the optional `pydantic-settings` package "
            "and Pydantic validation; the independent workflow avoids both and samples no "
            "environment source."
        ),
    ),
    (_PAGE, "pydantic-settings"): _excluded(
        "Pydantic `Settings` { #pydantic-settings }",
        25,
        124,
        (
            "This section groups Pydantic Settings installation, declaration, environment "
            "parsing, and use. Those behaviors are not implemented by FastAPI; its "
            "FastAPI-specific child material is limited to the server command and is not a "
            "settings API workflow."
        ),
        (
            "The pinned page directs readers to Pydantic Settings. FastAPI 0.157.0 lists "
            "`pydantic-settings` as an optional extra dependency in "
            "`../fastapi/pyproject.toml:82,103,128`, rather than making it part of the core "
            "runtime. Its FastAPI-specific `run-the-server` child is linked separately to "
            "the CLI process workflow in `scripts/atlas_remaining_docs_wave_mappings.py:56-80`, "
            "including `fastapi.cli.process.run-leaves-environment-unchanged`, "
            "`fastapi.cli.process.run-auto-discovery-no-path`, and "
            "`fastapi.cli.process.run-explicit-entrypoint`. Those cases cover CLI startup "
            "and request lifecycle; Pydantic environment loading remains outside this "
            "settings mapping."
        ),
    ),
    (_PAGE, "install-pydantic-settings"): _excluded(
        "Install `pydantic-settings` { #install-pydantic-settings }",
        29,
        52,
        (
            "The commands install an optional third-party package through uv and describe "
            "the `all` extra. Package resolution is not a FastAPI request or API behavior."
        ),
        (
            "FastAPI 0.157.0 declares `pydantic-settings` in optional extras at "
            "`../fastapi/pyproject.toml:82,103,128`. The ordinary oracle workflow does not "
            "assume that optional package is importable, and this page mapping adds no such "
            "runtime dependency."
        ),
    ),
    (_PAGE, "create-the-settings-object"): _excluded(
        "Create the `Settings` object { #create-the-settings-object }",
        53,
        72,
        (
            "The example defines a `pydantic_settings.BaseSettings` subclass and describes "
            "environment-source lookup, type conversion, and validation. It does not call a "
            "FastAPI API."
        ),
        (
            "The page's behavior is supplied by optional `pydantic-settings` and Pydantic, "
            "not by FastAPI. The selected recipe uses an ordinary dataclass so the same "
            "process can exercise the separate FastAPI route and dependency contract without "
            "assuming optional settings-package availability."
        ),
    ),
    (_PAGE, "use-the-settings"): _workflow(
        "Use the `settings` { #use-the-settings }",
        73,
        78,
        _GLOBAL_CASE,
        _GLOBAL_ACTION,
        (
            "The selected action sends one GET request to a route that reads a fixed, "
            "user-created settings value and returns its fields. It observes response status "
            "and exact body bytes only; it does not exercise `BaseSettings`, environment "
            "loading, or field validation."
        ),
        (
            "The pinned tutorial's `tutorial001_py310.py:18-20` reads fields from its "
            "application-level `settings` object in a FastAPI path operation. The independent "
            "case substitutes a fixed dataclass value to sample the FastAPI route response "
            "without importing optional `pydantic-settings`. FastAPI owns path-operation "
            "integration and response projection: `serialize_response` applies "
            "`jsonable_encoder` at `../fastapi/fastapi/routing.py:301-341`, and the request "
            "handler selects and constructs the default JSON response at "
            "`../fastapi/fastapi/routing.py:379-400,741-748`. Generic route dispatch and "
            "response start/body sending follow Starlette 1.6.0 "
            "(`../starlette/starlette/routing.py:672-700` and "
            "`../starlette/starlette/responses.py:163-167`). Starlette-RS's selected "
            "planning checkout provides the target boundary for those generic operations."
        ),
    ),
    (_PAGE, "run-the-server"): _excluded(
        "Run the server { #run-the-server }",
        79,
        124,
        (
            "The Bash and PowerShell snippets configure process environment variables and "
            "start a server process. Their shell assignment, CLI startup, and Uvicorn log "
            "behavior are not an ASGI request contract for settings."
        ),
        (
            "The displayed setting values depend on process environment lookup and the "
            "Pydantic Settings example; Pydantic environment loading is excluded here. The "
            "`uv run fastapi run main.py` process invocation is linked under "
            "`scripts/atlas_remaining_docs_wave_mappings.py:56-80` to "
            "`tests/fixtures/input-recipes/parity/fastapi-cli-documented-process-v2.yaml` "
            "cases `fastapi.cli.process.run-leaves-environment-unchanged`, "
            "`fastapi.cli.process.run-auto-discovery-no-path`, and "
            "`fastapi.cli.process.run-explicit-entrypoint`. That workflow covers CLI "
            "startup and request lifecycle, not the loading of `ADMIN_EMAIL` or `APP_NAME` "
            "by Pydantic Settings. This page mapping remains limited to independently "
            "observable FastAPI request behavior."
        ),
    ),
    (_PAGE, "settings-in-another-module"): _excluded(
        "Settings in another module { #settings-in-another-module }",
        125,
        142,
        (
            "The section demonstrates Python package files, imports, and a module-level "
            "settings instance. The settings construction and module import behavior are "
            "user-code and Pydantic concerns; no distinct FastAPI behavior is added."
        ),
        (
            "The example uses the optional `pydantic-settings` class and a module-level "
            "object. Its route simply reads those values. A response for that global-object "
            "pattern is sampled separately under `use-the-settings`; this section's module "
            "layout and imports are not claimed."
        ),
    ),
    (_PAGE, "settings-in-a-dependency"): _excluded(
        "Settings in a dependency { #settings-in-a-dependency }",
        143,
        184,
        (
            "This parent section groups settings construction, dependency injection, and "
            "dependency overrides. Its Pydantic config child is excluded and its two "
            "FastAPI composition children are mapped separately."
        ),
        (
            "The pinned headings `the-config-file`, `the-main-app-file`, and "
            "`settings-and-testing` "
            "identify distinct contracts. Mapping their union here would obscure that only "
            "the FastAPI `Depends` and override path is sampled by the new input."
        ),
    ),
    (_PAGE, "the-config-file"): _excluded(
        "The config file { #the-config-file }",
        149,
        156,
        (
            "The code defines a `pydantic_settings.BaseSettings` subclass and explains that "
            "it is not instantiated at module import. Settings construction is external to "
            "FastAPI."
        ),
        (
            "The config class and its `BaseSettings` behavior require optional "
            "`pydantic-settings`; the FastAPI dependency source begins in the following "
            "main-app section. No claim is made about Pydantic settings construction or "
            "environment values."
        ),
    ),
    (_PAGE, "the-main-app-file"): _workflow(
        "The main app file { #the-main-app-file }",
        157,
        174,
        _OVERRIDE_CASE,
        _OVERRIDE_ACTION,
        (
            "The selected GET action enters the documented `/info` path operation with "
            "`Depends(get_settings)` after the app registers its test override. Status and "
            "exact body bytes expose the replacement object received by the endpoint. The "
            "sample omits Pydantic construction, `lru_cache`, and unoverridden factory calls."
        ),
        (
            "FastAPI 0.157.0 builds and solves the dependency graph in "
            "`../fastapi/fastapi/dependencies/utils.py:314-389,657-819`; the solver looks up the "
            "original callable in `dependency_overrides` and builds the replacement "
            "dependant at lines 694-728. The pinned app example declares `Depends(get_settings)` "
            "at `../fastapi/docs_src/settings/app02_an_py310/main.py:16-22`. The input uses "
            "a dataclass to isolate that FastAPI composition from optional "
            "`pydantic-settings`. FastAPI's response projection applies `jsonable_encoder` "
            "at `../fastapi/fastapi/routing.py:321-350` and selects/constructs its default "
            "JSON response at `../fastapi/fastapi/routing.py:756-779`. Generic "
            "route dispatch and response start/body sending follow Starlette 1.6.0 "
            "(`../starlette/starlette/routing.py:672-700` and "
            "`../starlette/starlette/responses.py:163-167`); Starlette-RS's selected "
            "planning checkout provides the target boundary for those generic operations."
        ),
    ),
    (_PAGE, "settings-and-testing"): _workflow(
        "Settings and testing { #settings-and-testing }",
        175,
        184,
        _OVERRIDE_CASE,
        _OVERRIDE_ACTION,
        (
            "The action sends one GET to the documented route after mapping its original "
            "dependency callable to an independently authored replacement. It observes only "
            "HTTP status and exact response body bytes; it does not exercise TestClient, "
            "Pydantic Settings validation, or client-side JSON parsing."
        ),
        (
            "The pinned example assigns `app.dependency_overrides[get_settings]` and requests "
            "`/info` in `../fastapi/docs_src/settings/app02_an_py310/test_main.py:9-23`. "
            "FastAPI stores the override mapping in `../fastapi/fastapi/applications.py:967-984` "
            "and `solve_dependencies` invokes the selected callable at "
            "`../fastapi/fastapi/dependencies/utils.py:620-646,662-680`. The new direct-ASGI "
            "action isolates this FastAPI replacement contract. FastAPI response projection "
            "applies `jsonable_encoder` at `../fastapi/fastapi/routing.py:301-341` and "
            "selects/constructs the default JSON response at "
            "`../fastapi/fastapi/routing.py:379-400,741-748`. Starlette 1.6.0 owns generic "
            "route dispatch (`../starlette/starlette/routing.py:672-700`) and response "
            "start/body sending (`../starlette/starlette/responses.py:163-167`); "
            "Starlette-RS's selected planning checkout provides the target boundary for "
            "those generic operations."
        ),
    ),
    (_PAGE, "reading-a-env-file"): _excluded(
        "Reading a `.env` file { #reading-a-env-file }",
        185,
        319,
        (
            "The section describes dotenv files, their parsing, Pydantic `env_file` "
            "configuration, and caching of constructed settings. FastAPI itself does not "
            "read dotenv files or cache user settings."
        ),
        (
            "Dotenv loading is provided by optional Pydantic Settings and `python-dotenv`; "
            "the documented cache is Python's `functools.lru_cache`. Neither behavior is "
            "part of FastAPI's implementation. The FastAPI dependency override composition "
            "is separately mapped under `settings-and-testing`."
        ),
    ),
    (_PAGE, "the-env-file"): _excluded(
        "The `.env` file { #the-env-file }",
        207,
        215,
        (
            "The section supplies user-authored dotenv key/value text. File syntax and "
            "reading are external configuration behavior, not FastAPI behavior."
        ),
        (
            "The following section configures Pydantic Settings to read this file with an "
            "external `python-dotenv` package. This input does not parse or observe those "
            "values."
        ),
    ),
    (_PAGE, "read-settings-from-env"): _excluded(
        "Read settings from `.env` { #read-settings-from-env }",
        216,
        229,
        (
            "The example sets Pydantic `model_config.env_file` and describes reading values "
            "from a dotenv file. This is Pydantic Settings configuration, not a FastAPI "
            "request or API operation."
        ),
        (
            "The pinned page labels the configuration as Pydantic-owned, and the feature "
            "requires optional `pydantic-settings` plus `python-dotenv`. The recipe remains "
            "usable when those packages are absent and does not claim their parsing behavior."
        ),
    ),
    (_PAGE, "creating-the-settings-only-once-with-lru-cache"): _excluded(
        "Creating the `Settings` only once with `lru_cache` "
        "{ #creating-the-settings-only-once-with-lru-cache }",
        230,
        319,
        (
            "The section's once-only construction claim is implemented by Python's "
            "`functools.lru_cache`; the cached value is a Pydantic Settings instance. "
            "FastAPI's dependency system consumes the callable but does not implement its "
            "cache semantics."
        ),
        (
            "The active dependency-override mapping covers FastAPI's replacement behavior. "
            "This recipe makes no repeated-request, cache hit, invalidation, file access, or "
            "object-identity observation, and the optional Pydantic Settings dependency is "
            "not required."
        ),
    ),
    (_PAGE, "lru-cache-technical-details"): _excluded(
        "`lru_cache` Technical Details { #lru-cache-technical-details }",
        257,
        319,
        (
            "The section explains Python standard-library `functools.lru_cache` key and "
            "reuse behavior. It defines no FastAPI-owned operation."
        ),
        (
            "The pinned text attributes the decorator to Python's standard library. "
            "Dependency invocation is a separate FastAPI contract, but this input does not "
            "claim cache behavior or any cached settings object."
        ),
    ),
    (_PAGE, "recap"): _excluded(
        "Recap { #recap }",
        320,
        326,
        (
            "The recap repeats Pydantic Settings, dependency override, dotenv, and "
            "`lru_cache` points already classified in their own sections; it adds no "
            "independent request or behavior."
        ),
        (
            "The settings response and FastAPI dependency override are mapped in their "
            "specific sections, while environment parsing, dotenv loading, and caching are "
            "excluded by ownership. A recap-level mapping would combine those distinct "
            "contracts."
        ),
    ),
}
