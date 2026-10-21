"""Enforce the FastAPI-RS Python pass-through and runtime dependency boundary."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from importlib import metadata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_PACKAGE_ROOT = PROJECT_ROOT / "fastapi-rs-py" / "python"
RUST_SOURCE_ROOTS = (
    PROJECT_ROOT / "fastapi-rs" / "src",
    PROJECT_ROOT / "fastapi-rs-py" / "src",
)
PROJECT_DEPENDENCY_SECTION = "project"
PROJECT_OPTIONAL_DEPENDENCY_SECTION = "project.optional-dependencies"
UPSTREAM_FASTAPI_MODULE_LITERAL = re.compile(
    r"(?P<quote>['\"])fastapi(?:\.[A-Za-z_]\w*)*(?P=quote)"
)
DYNAMIC_PYTHON_EXECUTION = re.compile(
    r"\b(?:py|python)\s*\.\s*(?:run|eval)\s*\(|"
    r"\bPyModule\s*::\s*from_code(?:_bound)?\s*\("
)
# AnyIO task groups accept only genuine Python coroutine objects. PyO3's
# native continuation is merely awaitable, so this exact, behavior-free bridge
# lets AnyIO schedule it without moving stream logic into Python.
NATIVE_TASK_COROUTINE_BRIDGE = re.compile(
    r"PyModule\s*::\s*from_code\(\s*module\.py\(\),\s*"
    r'c"async def _run_native_task\(awaitable\):\\n    return await awaitable\\n",\s*'
    r'c"<fastapi-rs-native-task-adapter>",\s*'
    r'c"_fastapi_rs_native_task_adapter",\s*\)\?'
)
FASTAPI_MODULE_METADATA_ASSIGNMENT = re.compile(
    r"\.\s*(?:setattr|set_item)\s*\(\s*['\"](?:__module__|module)['\"]\s*,\s*"
    r"(?P<value>['\"]fastapi(?:\.[A-Za-z_]\w*)*['\"]|[A-Za-z_]\w*)\s*,?\s*\)"
)
FASTAPI_MODULE_METADATA_CONST = re.compile(
    r"\bconst\s+(?P<name>[A-Za-z_]\w*)\s*:\s*&\s*(?:'static\s+)?str\s*=\s*"
    r"(?P<value>['\"]fastapi(?:\.[A-Za-z_]\w*)*['\"])\s*;"
)
FASTAPI_MODULE_METADATA_GETTER = re.compile(
    r"#\s*\[\s*getter\s*\(\s*__module__\s*\)\s*\]\s*"
    r"fn\s+[A-Za-z_]\w*\s*\(\s*&self\s*\)\s*"
    r"->\s*&\s*'static\s+str\s*\{\s*"
    r"(?P<value>['\"]fastapi(?:\.[A-Za-z_]\w*)*['\"])\s*\}"
)
FASTAPI_LOGGER_NAME = re.compile(
    r"\b(?:py|python)\s*\.\s*import\(\s*['\"]logging['\"]\s*\)\s*\?\s*"
    r"\.\s*getattr\(\s*['\"]getLogger['\"]\s*\)\s*\?\s*"
    r"\.\s*call1\(\s*\(\s*(?P<value>['\"]fastapi['\"])\s*,\s*\)\s*\)"
)
FASTAPI_TARGET_PACKAGE_BOOTSTRAP = re.compile(
    r"\bfn\s+bootstrap_target_fastapi_modules\s*\([^)]*\)[^{]*\{.*?"
    r"modules\s*\.\s*contains\(\s*(?P<value>['\"]fastapi['\"])\s*\)",
    re.DOTALL,
)
PUBLIC_FASTAPI_EXPORTS = [
    "APIRouter",
    "BackgroundTasks",
    "Body",
    "Cookie",
    "Depends",
    "FastAPI",
    "File",
    "Form",
    "Header",
    "HTTPException",
    "Path",
    "Query",
    "Request",
    "Response",
    "Security",
    "UploadFile",
    "WebSocket",
    "WebSocketDisconnect",
    "WebSocketException",
    "__version__",
    "status",
]
# These are FastAPI source aliases whose behavior is owned by the pinned
# Starlette-RS dependency. Keep this allowlist aligned with the corresponding
# reviewed import-binding evidence in metadata.yaml; these entries permit only
# a direct import, never a wrapper or local implementation.
REVIEWED_STARLETTE_REEXPORTS = {
    "fastapi/testclient.py": ("starlette.testclient", frozenset({"TestClient"})),
    "fastapi/templating.py": ("starlette.templating", frozenset({"Jinja2Templates"})),
}
FORBIDDEN_CONTROL_FLOW = tuple(
    node_type
    for node_type in (
        ast.If,
        ast.IfExp,
        ast.For,
        ast.AsyncFor,
        ast.While,
        getattr(ast, "Match", None),
        ast.Try,
        ast.With,
        ast.AsyncWith,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    )
    if node_type is not None
)


def _configured_native_module() -> str:
    """Read the extension module configured for the published wheel."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = None
    for line in pyproject.splitlines():
        section_match = re.fullmatch(r"\s*\[([^]]+)\]\s*", line)
        if section_match:
            section = section_match.group(1)
            continue
        if section != "tool.maturin":
            continue
        module_match = re.fullmatch(
            r'\s*module-name\s*=\s*["\']([A-Za-z_][A-Za-z0-9_.]*)["\']\s*', line
        )
        if module_match:
            return module_match.group(1)
    raise SystemExit("pyproject.toml must configure tool.maturin.module-name")


def _configured_python_packages() -> list[str]:
    """Read the Python packages included in the published wheel."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = None
    array_value = None
    for line in pyproject.splitlines():
        section_match = re.fullmatch(r"\s*\[([^]]+)\]\s*", line)
        if section_match:
            section = section_match.group(1)
            array_value = None
            continue
        if section != "tool.maturin":
            continue
        package_match = re.match(r"\s*python-packages\s*=\s*(\[.*)$", line)
        if package_match:
            array_value = package_match.group(1)
            if _toml_array_is_complete(array_value):
                return _toml_strings(array_value)
            continue
        if array_value is not None:
            array_value += "\n" + line
            if _toml_array_is_complete(array_value):
                return _toml_strings(array_value)
    raise SystemExit("pyproject.toml must configure tool.maturin.python-packages")


def _toml_array_is_complete(value: str) -> bool:
    quote = None
    escaped = False
    for character in value:
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif character in {"'", '"'}:
            quote = character
        elif character == "]":
            return True
    return False


def _toml_strings(value: str) -> list[str]:
    return [
        match.group(1) if match.group(1) is not None else match.group(2)
        for match in re.finditer(
            r"\"([^\"\\]*(?:\\.[^\"\\]*)*)\"|'([^'\\]*(?:\\.[^'\\]*)*)'", value
        )
    ]


def check_declared_runtime_dependency_boundary() -> None:
    """Reject upstream FastAPI in PEP 621 runtime or optional dependencies."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    section = None
    array_value = None
    array_label = None
    dependency_requirements = []

    for line_number, line in enumerate(pyproject.splitlines(), start=1):
        section_match = re.fullmatch(r"\s*\[([^]]+)\]\s*", line)
        if section_match:
            section = section_match.group(1)
            array_value = None
            array_label = None
            continue

        if array_value is not None:
            array_value += "\n" + line
            if _toml_array_is_complete(array_value):
                dependency_requirements.extend(
                    (requirement, array_label, line_number)
                    for requirement in _toml_strings(array_value)
                )
                array_value = None
                array_label = None
            continue

        dependency_key = re.match(r"\s*([A-Za-z0-9_-]+)\s*=\s*(\[.*)$", line)
        if not dependency_key:
            continue
        key = dependency_key.group(1)
        is_runtime_dependency_list = (
            section == PROJECT_DEPENDENCY_SECTION and key == "dependencies"
        ) or section == PROJECT_OPTIONAL_DEPENDENCY_SECTION
        if not is_runtime_dependency_list:
            continue

        array_value = dependency_key.group(2)
        array_label = (
            "project.dependencies"
            if section == PROJECT_DEPENDENCY_SECTION
            else f"project.optional-dependencies.{key}"
        )
        if _toml_array_is_complete(array_value):
            dependency_requirements.extend(
                (requirement, array_label, line_number)
                for requirement in _toml_strings(array_value)
            )
            array_value = None
            array_label = None

    forbidden = []
    for requirement, dependency_group, line_number in dependency_requirements:
        match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement)
        if match and re.sub(r"[-_.]+", "-", match.group(1)).lower() == "fastapi":
            forbidden.append(
                f"pyproject.toml:{line_number}: original FastAPI is declared in "
                f"{dependency_group}: {requirement}"
            )
    if forbidden:
        raise SystemExit("\n".join(forbidden))


def _is_static_all_assignment(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "__all__"
        and isinstance(node.value, (ast.List, ast.Tuple))
        and all(
            isinstance(item, ast.Constant) and isinstance(item.value, str)
            for item in node.value.elts
        )
    )


def _is_native_extension_import(path: Path, node: ast.stmt, module_name: str) -> bool:
    """Accept an absolute or package-relative import from the configured extension."""
    if not isinstance(node, ast.ImportFrom):
        return False
    if node.level == 0:
        return node.module == module_name
    if node.level != 1 or node.module is None:
        return False

    native_package = module_name.rpartition(".")[0]
    source_package = ".".join(path.relative_to(PYTHON_PACKAGE_ROOT).parent.parts)
    imported_module = f"{source_package}.{node.module}"
    return imported_module == module_name and source_package == native_package


def _is_reviewed_starlette_reexport(path: Path, node: ast.stmt) -> bool:
    """Allow an exact source-reviewed direct alias to the Starlette-RS facade."""
    if not isinstance(node, ast.ImportFrom) or node.level != 0:
        return False
    relative_path = path.relative_to(PYTHON_PACKAGE_ROOT).as_posix()
    selected = REVIEWED_STARLETTE_REEXPORTS.get(relative_path)
    if selected is None:
        return False
    module_name, expected_names = selected
    return node.module == module_name and frozenset(
        (alias.name, alias.asname or alias.name) for alias in node.names
    ) == frozenset((name, name) for name in expected_names)


def check_python_facade_pass_through() -> None:
    """Allow only native-extension re-exports and a matching literal ``__all__``."""
    python_files = sorted(PYTHON_PACKAGE_ROOT.rglob("*.py"))
    if not python_files:
        raise SystemExit(f"no Python facade sources found under {PYTHON_PACKAGE_ROOT}")

    native_module = _configured_native_module()
    violations = []
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_names = []
        all_assignments = []
        for node in ast.walk(tree):
            if isinstance(node, FORBIDDEN_CONTROL_FLOW):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: Python runtime "
                    f"facades cannot contain control flow ({type(node).__name__})"
                )
        for index, node in enumerate(tree.body):
            is_docstring = (
                index == 0
                and isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            )
            if is_docstring:
                continue
            if _is_static_all_assignment(node):
                all_assignments.append(node)
                continue
            if isinstance(node, ast.ImportFrom):
                if not _is_native_extension_import(
                    path, node, native_module
                ) and not _is_reviewed_starlette_reexport(path, node):
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: imports must be "
                        "direct re-exports from the configured native module or an exact "
                        "metadata-reviewed Starlette-RS alias"
                    )
                    continue
                if any(alias.name == "*" for alias in node.names):
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: wildcard native "
                        "re-exports are not allowed"
                    )
                    continue
                imported_names.extend(alias.asname or alias.name for alias in node.names)
                continue
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                f"{type(node).__name__} is not a native re-export; Python runtime modules "
                "may contain only native imports and a literal __all__"
            )

        if len(all_assignments) != 1:
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}: Python runtime modules must define "
                "exactly one literal __all__"
            )
        elif all_assignments[0].value.elts:
            exported_names = [item.value for item in all_assignments[0].value.elts]
            if len(exported_names) != len(set(exported_names)):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{all_assignments[0].lineno}: "
                    "__all__ contains duplicate names"
                )
            if imported_names != exported_names:
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{all_assignments[0].lineno}: "
                    f"__all__ must exactly match native re-exports; imports={imported_names!r}, "
                    f"__all__={exported_names!r}"
                )
        elif imported_names:
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}: native imports must be listed in "
                "literal __all__"
            )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                alias.name == "fastapi" or alias.name.startswith("fastapi.") for alias in node.names
            ):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                    "the original FastAPI package cannot be imported by the target facade"
                )
            if isinstance(node, ast.ImportFrom) and (
                node.module == "fastapi" or (node.module or "").startswith("fastapi.")
            ):
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}:{node.lineno}: "
                    "the original FastAPI package cannot be imported by the target facade"
                )
    if violations:
        raise SystemExit("\n".join(violations))


def check_public_fastapi_facade() -> None:
    """Require the public package to re-export only the native API symbols."""
    path = PYTHON_PACKAGE_ROOT / "fastapi" / "__init__.py"
    if not path.is_file():
        raise SystemExit(f"public FastAPI facade source is missing: {path}")

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    native_imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    if len(native_imports) != 1:
        raise SystemExit(f"{path.relative_to(PROJECT_ROOT)} must have one direct native import")

    native_import = native_imports[0]
    imported_names = [alias.name for alias in native_import.names]
    if (
        native_import.level != 0
        or native_import.module != _configured_native_module()
        or any(alias.asname is not None for alias in native_import.names)
        or imported_names != PUBLIC_FASTAPI_EXPORTS
    ):
        raise SystemExit(
            f"{path.relative_to(PROJECT_ROOT)} must directly re-export "
            f"{PUBLIC_FASTAPI_EXPORTS!r} from {_configured_native_module()!r}"
        )

    all_assignments = [node for node in tree.body if _is_static_all_assignment(node)]
    if len(all_assignments) != 1:
        raise SystemExit(f"{path.relative_to(PROJECT_ROOT)} must define one literal __all__")
    exported_names = [item.value for item in all_assignments[0].value.elts]
    if exported_names != PUBLIC_FASTAPI_EXPORTS:
        raise SystemExit(
            f"{path.relative_to(PROJECT_ROOT)} __all__ must be "
            f"{PUBLIC_FASTAPI_EXPORTS!r}; found {exported_names!r}"
        )


def check_wheel_package_sources() -> None:
    """Require each source Python package to be included in the wheel config."""
    configured_package_list = _configured_python_packages()
    package_parts = [_python_package_parts(package) for package in configured_package_list]
    normalized_packages = [".".join(parts) for parts in package_parts]
    if len(normalized_packages) != len(set(normalized_packages)):
        raise SystemExit("tool.maturin.python-packages contains duplicate packages")

    missing_directories = []
    missing_initializers = []
    for parts in package_parts:
        package_directory = PYTHON_PACKAGE_ROOT.joinpath(*parts)
        if not package_directory.is_dir():
            missing_directories.append(package_directory)
        elif not (package_directory / "__init__.py").is_file():
            missing_initializers.append(package_directory / "__init__.py")

    if missing_directories or missing_initializers:
        missing_paths = [*missing_directories, *missing_initializers]
        raise SystemExit(
            "configured Python package source directories must exist and contain "
            "__init__.py: " + ", ".join(str(path) for path in missing_paths)
        )

    configured_packages = set(normalized_packages)
    source_packages = {
        ".".join(path.parent.relative_to(PYTHON_PACKAGE_ROOT).parts)
        for path in PYTHON_PACKAGE_ROOT.rglob("__init__.py")
    }
    if source_packages != configured_packages:
        raise SystemExit(
            "tool.maturin.python-packages must match Python package sources: "
            f"configured={sorted(configured_packages)!r}, source={sorted(source_packages)!r}"
        )


def _python_package_parts(package: str) -> tuple[str, ...]:
    """Normalize Maturin package names and slash-separated source paths."""
    separator = "/" if "/" in package else "."
    parts = tuple(package.split(separator))
    if (
        not parts
        or any(not part.isidentifier() for part in parts)
        or any((separator == "/") and "." in part for part in parts)
    ):
        raise SystemExit(
            f"invalid package name or path in tool.maturin.python-packages: {package!r}"
        )
    return parts


def check_rust_binding_import_boundary() -> None:
    """Reject literal imports of original FastAPI from either Rust crate."""
    violations = []
    check_fastapi_root_module_bootstrap()
    rust_files = sorted(path for root in RUST_SOURCE_ROOTS for path in root.rglob("*.rs"))
    for path in rust_files:
        source = path.read_text(encoding="utf-8")
        for match in UPSTREAM_FASTAPI_MODULE_LITERAL.finditer(source):
            if (
                _is_fastapi_module_metadata(source, match.start())
                or _is_fastapi_module_metadata_const(source, match.start())
                or _is_fastapi_module_metadata_getter(source, match.start())
                or _is_fastapi_logger_name(source, match.start())
                or _is_fastapi_target_package_bootstrap(source, match.start())
            ):
                continue
            line = source.count("\n", 0, match.start()) + 1
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}:{line}: native bindings cannot import "
                "the original FastAPI package"
            )
        approved_task_bridges = list(NATIVE_TASK_COROUTINE_BRIDGE.finditer(source))
        for dynamic_execution in DYNAMIC_PYTHON_EXECUTION.finditer(source):
            if (
                path.name == "application_runtime.rs"
                and len(approved_task_bridges) == 1
                and dynamic_execution.start() == approved_task_bridges[0].start()
            ):
                continue
            line = source.count("\n", 0, dynamic_execution.start()) + 1
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}:{line}: native bindings cannot execute "
                "dynamic Python code, which bypasses the runtime import boundary"
            )
        if path.name == "application_runtime.rs" and len(approved_task_bridges) > 1:
            violations.append(
                f"{path.relative_to(PROJECT_ROOT)}: native task coroutine bridge must appear once"
            )
    if violations:
        raise SystemExit("\n".join(violations))


def check_fastapi_root_module_bootstrap() -> None:
    """Keep the Rust bootstrap exactly aligned with reviewed root module rows."""
    metadata = (PROJECT_ROOT / "metadata.yaml").read_text(encoding="utf-8")
    review_match = re.search(
        r"(?ms)^runtime_root_namespace_review:\n(?P<body>.*?)(?=^[A-Za-z_][A-Za-z0-9_]*:\s*$|\Z)",
        metadata,
    )
    if review_match is None:
        raise SystemExit("metadata.yaml is missing runtime_root_namespace_review")
    review_body = review_match.group("body")
    rows_match = re.search(r"(?ms)^  rows:\n(?P<rows>.*)$", review_body)
    if rows_match is None:
        raise SystemExit("runtime_root_namespace_review has no rows")
    supported_modules = []
    for row in re.split(r"(?m)^    - id: ", rows_match.group("rows"))[1:]:
        identifier = row.splitlines()[0].strip()
        classification = re.search(r"(?m)^      classification: (\w+)\s*$", row)
        if classification is not None and classification.group(1) == "supported":
            if not identifier.startswith("fastapi.") or identifier.count(".") != 1:
                raise SystemExit(f"invalid supported root module in metadata.yaml: {identifier!r}")
            supported_modules.append(identifier.removeprefix("fastapi."))

    binding_source = (PROJECT_ROOT / "fastapi-rs-py" / "src" / "lib.rs").read_text(encoding="utf-8")
    module_list = re.search(
        r"(?s)const FASTAPI_PUBLIC_ROOT_MODULES:\s*&\[&str\]\s*=\s*&\[(?P<items>.*?)\];",
        binding_source,
    )
    if module_list is None:
        raise SystemExit("Rust target package has no reviewed root module bootstrap list")
    rust_modules = re.findall(r"['\"]([a-z_]+)['\"]", module_list.group("items"))
    if rust_modules != supported_modules or len(rust_modules) != len(set(rust_modules)):
        raise SystemExit(
            "Rust FastAPI root module bootstrap must exactly match supported metadata rows: "
            f"rust={rust_modules!r}, metadata={supported_modules!r}"
        )

    for module_name in supported_modules:
        module_file = PYTHON_PACKAGE_ROOT / "fastapi" / f"{module_name}.py"
        package_file = PYTHON_PACKAGE_ROOT / "fastapi" / module_name / "__init__.py"
        if not module_file.is_file() and not package_file.is_file():
            raise SystemExit(
                f"supported FastAPI root module has no runtime facade: fastapi.{module_name}"
            )


def _is_fastapi_target_package_bootstrap(source: str, offset: int) -> bool:
    """Allow only the root package lookup required by its reviewed child imports."""
    return any(
        match.start("value") == offset
        for match in FASTAPI_TARGET_PACKAGE_BOOTSTRAP.finditer(source)
    )


def _is_fastapi_module_metadata(source: str, offset: int) -> bool:
    """Allow public module identity metadata without allowing a runtime import."""
    attribute_start = source.rfind("#[pyclass", 0, offset)
    if attribute_start >= 0:
        attribute_end = source.find("]", attribute_start)
        if attribute_end >= offset:
            attribute = source[attribute_start : attribute_end + 1]
            for match in re.finditer(
                r"\bmodule\s*=\s*(?P<value>['\"]fastapi(?:\.[A-Za-z_]\w*)*['\"])",
                attribute,
            ):
                if attribute_start + match.start("value") == offset:
                    return True
    return any(
        match.start("value") == offset
        for match in FASTAPI_MODULE_METADATA_ASSIGNMENT.finditer(source)
    )


def _is_fastapi_module_metadata_const(source: str, offset: int) -> bool:
    """Allow a fixed module-name const only when all its uses set metadata."""
    declaration = next(
        (
            match
            for match in FASTAPI_MODULE_METADATA_CONST.finditer(source)
            if match.start("value") == offset
        ),
        None,
    )
    if declaration is None:
        return False
    metadata_values = {
        match.start("value") for match in FASTAPI_MODULE_METADATA_ASSIGNMENT.finditer(source)
    }
    identifier = re.compile(rf"\b{re.escape(declaration.group('name'))}\b")
    return all(
        match.start() == declaration.start("name") or match.start() in metadata_values
        for match in identifier.finditer(source)
    )


def _is_fastapi_module_metadata_getter(source: str, offset: int) -> bool:
    """Allow a literal only as the complete return value of a module getter."""
    return any(
        match.start("value") == offset for match in FASTAPI_MODULE_METADATA_GETTER.finditer(source)
    )


def _is_fastapi_logger_name(source: str, offset: int) -> bool:
    """Allow only the direct logging.getLogger('fastapi') name-data chain."""
    return any(match.start("value") == offset for match in FASTAPI_LOGGER_NAME.finditer(source))


def main() -> int:
    check_declared_runtime_dependency_boundary()
    check_python_facade_pass_through()
    check_wheel_package_sources()
    check_public_fastapi_facade()
    check_rust_binding_import_boundary()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="check source boundaries without checking an installed target environment",
    )
    args = parser.parse_args()
    if args.source_only:
        print(
            "Static target boundary valid: no original FastAPI runtime dependency or import, "
            "and Python runtime modules contain only native symbols or reviewed direct "
            "Starlette-RS aliases via literal __all__"
        )
        return 0

    try:
        metadata.distribution("fastapi")
    except metadata.PackageNotFoundError:
        pass
    else:
        raise SystemExit(
            "target environment contains the original FastAPI distribution; "
            "FastAPI is source-oracle-only"
        )

    try:
        target = metadata.distribution("fastapi-rs")
    except metadata.PackageNotFoundError as exc:
        raise SystemExit("target environment is missing the fastapi-rs distribution") from exc

    declared = target.requires or []
    original_fastapi_requirement = next(
        (
            requirement
            for requirement in declared
            if (match := re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", requirement))
            and match.group(1).lower().replace("_", "-") == "fastapi"
        ),
        None,
    )
    if original_fastapi_requirement is not None:
        raise SystemExit(
            "fastapi-rs declares the original FastAPI runtime dependency: "
            + original_fastapi_requirement
        )

    print(
        "target runtime boundary valid: fastapi-rs installed; upstream fastapi absent; "
        "Python facade contains only configured native re-exports and reviewed direct "
        "Starlette-RS aliases; runtime metadata has no "
        "upstream dependency"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
