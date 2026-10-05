"""Pinned FastAPI source citations for reviewed whole-module exclusions.

These spans support existing exclusion dispositions only. They do not promote
the referenced behavior to compatibility coverage or alter the exclusion scope.
"""

from __future__ import annotations

from typing import Any


def _source(path: str, start_line: int, end_line: int, role: str) -> dict[str, Any]:
    return {
        "path": path,
        "start_line": start_line,
        "end_line": end_line,
        "role": role,
    }


TEST_MODULE_EXCLUSION_EVIDENCE: dict[str, list[dict[str, Any]]] = {
    "tests/benchmarks/test_general_performance.py": [
        _source(
            "tests/benchmarks/test_general_performance.py",
            11,
            15,
            "Benchmark module is skipped unless the dedicated --codspeed profile is selected.",
        ),
        _source(
            "tests/benchmarks/test_general_performance.py",
            214,
            246,
            "HTTP performance test functions consume pytest benchmark measurements.",
        ),
    ],
    "tests/benchmarks/test_openapi.py": [
        _source(
            "tests/benchmarks/test_openapi.py",
            12,
            22,
            "OpenAPI benchmark is gated by --codspeed and measures generation with benchmark().",
        ),
    ],
    "tests/memory_benchmarks/test_dependency_graph.py": [
        _source(
            "tests/memory_benchmarks/test_dependency_graph.py",
            10,
            14,
            "Memory benchmark module is skipped outside the dedicated --codspeed profile.",
        ),
        _source(
            "tests/memory_benchmarks/test_dependency_graph.py",
            75,
            86,
            "Dependency-graph construction is measured by pytest benchmark().",
        ),
    ],
    "tests/memory_benchmarks/test_openapi.py": [
        _source(
            "tests/memory_benchmarks/test_openapi.py",
            12,
            22,
            "OpenAPI memory benchmark is gated by --codspeed and measures generation "
            "with benchmark().",
        ),
    ],
    "tests/memory_benchmarks/test_route_dependency_graph.py": [
        _source(
            "tests/memory_benchmarks/test_route_dependency_graph.py",
            9,
            13,
            "Route dependency memory benchmark is skipped outside --codspeed.",
        ),
        _source(
            "tests/memory_benchmarks/test_route_dependency_graph.py",
            57,
            64,
            "Route-graph construction is measured by pytest benchmark().",
        ),
    ],
    "tests/test_dependencies_utils.py": [
        _source(
            "tests/test_dependencies_utils.py",
            1,
            8,
            "The test imports and directly invokes the private dependency utility helper.",
        ),
        _source(
            "fastapi/dependencies/utils.py",
            230,
            236,
            "The helper is defined in FastAPI's dependency utility implementation.",
        ),
    ],
    "tests/test_deprecated_responses.py": [
        _source(
            "tests/test_deprecated_responses.py",
            3,
            10,
            "The module selects optional ORJSONResponse and UJSONResponse profiles.",
        ),
        _source(
            "tests/test_deprecated_responses.py",
            33,
            48,
            "ORJSON response and deprecation cases are guarded by needs_orjson.",
        ),
        _source(
            "tests/test_deprecated_responses.py",
            65,
            79,
            "UJSON response and deprecation cases are guarded by needs_ujson.",
        ),
        _source(
            "tests/utils.py",
            13,
            20,
            "The optional response markers skip when orjson or ujson is unavailable.",
        ),
    ],
    "tests/test_fastapi_cli.py": [
        _source(
            "tests/test_fastapi_cli.py",
            1,
            7,
            "The source test imports subprocess and FastAPI CLI module state.",
        ),
        _source(
            "tests/test_fastapi_cli.py",
            10,
            34,
            "The existing CLI cases require process output/exit capture and monkeypatching.",
        ),
    ],
    "tests/test_orjson_response_class.py": [
        _source(
            "tests/test_orjson_response_class.py",
            1,
            16,
            "The module skips when orjson is unavailable before constructing its response app.",
        ),
        _source(
            "tests/test_orjson_response_class.py",
            27,
            32,
            "The response case exercises the selected optional ORJSON implementation.",
        ),
    ],
    "tests/test_prepare_release.py": [
        _source(
            "tests/test_prepare_release.py",
            1,
            17,
            "The test module imports the release preparation script and Typer CLI runner.",
        ),
        _source(
            "tests/test_prepare_release.py",
            203,
            238,
            "CLI cases mutate configured release files and exercise release tooling.",
        ),
        _source(
            "tests/test_prepare_release.py",
            259,
            307,
            "CLI cases inspect current version and release-note output.",
        ),
    ],
    "tests/test_stringified_annotation_dependency_py314.py": [
        _source(
            "tests/test_stringified_annotation_dependency_py314.py",
            1,
            30,
            "The sole test is guarded by needs_py314 and uses Python 3.14 annotation evaluation.",
        ),
        _source(
            "tests/utils.py",
            9,
            10,
            "The needs_py314 marker requires Python 3.14 or newer.",
        ),
    ],
    "tests/test_tutorial/test_custom_response/test_tutorial001b.py": [
        _source(
            "tests/test_tutorial/test_custom_response/test_tutorial001b.py",
            14,
            14,
            "The module is skipped unless the optional orjson package is installed.",
        ),
    ],
    "tests/test_tutorial/test_custom_response/test_tutorial009c.py": [
        _source(
            "tests/test_tutorial/test_custom_response/test_tutorial009c.py",
            4,
            4,
            "The module is skipped unless the optional orjson package is installed.",
        ),
    ],
    "tests/test_tutorial/test_generate_clients/test_tutorial004.py": [
        _source(
            "tests/test_tutorial/test_generate_clients/test_tutorial004.py",
            1,
            20,
            "The test patches pathlib during import, writes a temporary OpenAPI file, "
            "and checks its rewrite.",
        ),
    ],
    "tests/test_tutorial/test_graphql/test_tutorial001.py": [
        _source(
            "tests/test_tutorial/test_graphql/test_tutorial001.py",
            13,
            24,
            "The test imports the tutorial GraphQL app and asserts GraphQL resolver output.",
        ),
        _source(
            "docs_src/graphql_/tutorial001_py310.py",
            1,
            25,
            "The tutorial app is implemented with Strawberry GraphQLRouter and schema types.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial001_tutorial002.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial001_tutorial002.py",
            7,
            18,
            "The test runs standalone Python type modules and checks their printed output.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial003.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial003.py",
            3,
            12,
            "The test calls a plain Python function and checks its TypeError/value behavior.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial004.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial004.py",
            1,
            5,
            "The test imports and calls a plain Python function without a FastAPI app.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial005.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial005.py",
            1,
            12,
            "The test invokes a plain typed Python function with tuple arguments.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial006.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial006.py",
            1,
            16,
            "The test calls a plain Python function and observes builtins.print calls.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial007.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial007.py",
            1,
            8,
            "The test checks a plain Python function's tuple and set values.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial008.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial008.py",
            1,
            17,
            "The test calls a plain Python function and observes builtins.print calls.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial008b.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial008b.py",
            17,
            27,
            "The test imports and calls a plain Python function, observing builtins.print.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial009_tutorial009b.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial009_tutorial009b.py",
            17,
            32,
            "The test calls plain Python functions and asserts their printed values.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial010.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial010.py",
            1,
            5,
            "The test constructs and reads a plain Person object through a Python helper.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial011.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial011.py",
            15,
            24,
            "The test runs the standalone Pydantic example and checks printed model data.",
        ),
    ],
    "tests/test_tutorial/test_python_types/test_tutorial013.py": [
        _source(
            "tests/test_tutorial/test_python_types/test_tutorial013.py",
            1,
            5,
            "The test calls a plain annotated Python function and checks its string value.",
        ),
    ],
    "tests/test_tutorial/test_settings/test_app03.py": [
        _source(
            "tests/test_tutorial/test_settings/test_app03.py",
            21,
            44,
            "The tests import settings code, set ADMIN_EMAIL, and inspect settings-derived values.",
        ),
        _source(
            "docs_src/settings/app03_py310/config.py",
            1,
            9,
            "The tutorial configuration uses Pydantic Settings and dotenv-backed env_file.",
        ),
    ],
    "tests/test_tutorial/test_settings/test_tutorial001.py": [
        _source(
            "tests/test_tutorial/test_settings/test_tutorial001.py",
            8,
            23,
            "The test imports a settings tutorial and observes environment-derived fields.",
        ),
        _source(
            "docs_src/settings/tutorial001_py310.py",
            1,
            12,
            "The tutorial constructs a Pydantic BaseSettings object before its FastAPI app.",
        ),
    ],
    "tests/test_tutorial/test_sql_databases/test_tutorial001.py": [
        _source(
            "tests/test_tutorial/test_sql_databases/test_tutorial001.py",
            5,
            14,
            "The test imports SQLModel and SQLAlchemy integration dependencies.",
        ),
        _source(
            "tests/test_tutorial/test_sql_databases/test_tutorial001.py",
            31,
            50,
            "The fixture configures an in-memory SQLite engine and manages its session lifecycle.",
        ),
        _source(
            "docs_src/sql_databases/tutorial001_py310.py",
            1,
            25,
            "The tutorial's persistence model and session behavior are implemented with SQLModel.",
        ),
    ],
    "tests/test_tutorial/test_templates/test_tutorial001.py": [
        _source(
            "tests/test_tutorial/test_templates/test_tutorial001.py",
            9,
            30,
            "The test copies template/static directories and asserts rendered HTML and static CSS.",
        ),
        _source(
            "docs_src/templates/tutorial001_py310.py",
            1,
            18,
            "The tutorial app uses Starlette StaticFiles and Jinja2Templates.",
        ),
    ],
    "tests/test_tutorial/test_wsgi/test_tutorial001.py": [
        _source(
            "tests/test_tutorial/test_wsgi/test_tutorial001.py",
            1,
            17,
            "The tests exercise the tutorial's mounted Flask adapter and FastAPI route.",
        ),
        _source(
            "docs_src/wsgi/tutorial001_py310.py",
            1,
            23,
            "The tutorial uses third-party a2wsgi and Flask for the mounted WSGI app.",
        ),
    ],
}
