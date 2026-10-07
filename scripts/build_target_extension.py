"""Build the native target against the selected Starlette-RS source checkout."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
FAULT_INJECTION_ROOT = ROOT / "target" / "fault-injection"
FAULT_INJECTION_FEATURE = "fastapi-rs-py/fault-injection"


def _install_editable_target(
    uv: str,
    target_python: Path,
    overlay_root: Path,
    environment: dict[str, str],
    features: list[str],
) -> int:
    lockfile = ROOT / "Cargo.lock"
    lock_before = lockfile.read_bytes()
    lock_mode = lockfile.stat().st_mode & 0o7777
    environment = environment.copy()
    environment["PYO3_PYTHON"] = str(target_python)
    pep517_arguments = [
        "--manifest-path",
        str(overlay_root / "fastapi-rs-py/Cargo.toml"),
        "--locked",
        "--offline",
        "--interpreter",
        str(target_python),
        "--target-dir",
        environment["CARGO_TARGET_DIR"],
        "--features",
        ",".join(features),
    ]
    try:
        completed = subprocess.run(
            [
                uv,
                "pip",
                "install",
                "--python",
                str(target_python),
                "--no-deps",
                "--config-setting",
                f"maturin.build-args={shlex.join(pep517_arguments)}",
                "--editable",
                str(ROOT),
            ],
            cwd=ROOT,
            env=environment,
            check=False,
        )
    finally:
        try:
            lock_after = lockfile.read_bytes()
        except FileNotFoundError:
            lock_after = None
        if lock_after != lock_before:
            _atomic_write(lockfile, lock_before, lock_mode)
            print("restored Cargo.lock after editable package metadata build")
    return completed.returncode


def _atomic_write(destination: Path, content: bytes, mode: int) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def _workspace_overlay(starlette_rs_source: Path, overlay_root: Path, python_source: Path) -> None:
    manifest = ROOT / "Cargo.toml"
    try:
        manifest_text = manifest.read_text(encoding="utf-8")
        manifest_data = tomllib.loads(manifest_text)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"cannot read Cargo workspace manifest: {exc}") from exc

    dependency = manifest_data.get("workspace", {}).get("dependencies", {}).get("starlette-rs")
    if not isinstance(dependency, dict) or not isinstance(dependency.get("path"), str):
        raise SystemExit("Cargo.toml must declare starlette-rs as a workspace path dependency")
    old_path = f"path = {json.dumps(dependency['path'])}"
    if manifest_text.count(old_path) != 1:
        raise SystemExit("Cargo.toml starlette-rs workspace dependency path is ambiguous")
    pinned_path = starlette_rs_source.resolve() / "starlette-rs"
    overlay_text = manifest_text.replace(old_path, f"path = {json.dumps(str(pinned_path))}", 1)

    overlay_root.mkdir(parents=True, exist_ok=True)
    (overlay_root / "Cargo.toml").write_text(overlay_text, encoding="utf-8")
    shutil.copy2(ROOT / "Cargo.lock", overlay_root / "Cargo.lock")
    for filename in ("README.md", "LICENSE.md", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(ROOT / filename, overlay_root / filename)
    shutil.copy2(ROOT / "metadata.yaml", overlay_root / "metadata.yaml")

    members = manifest_data.get("workspace", {}).get("members", [])
    if not members:
        raise SystemExit("Cargo.toml does not declare workspace members")
    for member in members:
        member_path = Path(member)
        if member_path.is_absolute() or ".." in member_path.parts:
            raise SystemExit(f"unsupported non-workspace Cargo member path: {member}")
        source_member = ROOT / member_path
        if not source_member.exists():
            raise SystemExit(f"Cargo workspace member does not exist: {member}")
        member_overlay = overlay_root / member_path
        member_overlay.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_member / "Cargo.toml", member_overlay / "Cargo.toml")
        for source_entry in source_member.iterdir():
            if source_entry.name == "Cargo.toml":
                continue
            (member_overlay / source_entry.name).symlink_to(
                source_entry, target_is_directory=source_entry.is_dir()
            )

    pyproject_path = ROOT / "pyproject.toml"
    try:
        pyproject_text = pyproject_path.read_text(encoding="utf-8")
        pyproject_data = tomllib.loads(pyproject_text)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"cannot read Python project manifest: {exc}") from exc
    maturin_options = pyproject_data.get("tool", {}).get("maturin", {})
    source_setting = maturin_options.get("python-source")
    if maturin_options.get("manifest-path") != "fastapi-rs-py/Cargo.toml" or not isinstance(
        source_setting, str
    ):
        raise SystemExit("pyproject.toml must configure the native member and Python source")
    old_source = f"python-source = {json.dumps(source_setting)}"
    if pyproject_text.count(old_source) != 1:
        raise SystemExit("pyproject.toml Maturin Python source path is ambiguous")
    overlay_pyproject = pyproject_text.replace(
        old_source, f"python-source = {json.dumps(str(python_source.resolve()))}", 1
    )
    (overlay_root / "pyproject.toml").write_text(overlay_pyproject, encoding="utf-8")


def _verify_overlay_metadata(
    overlay_root: Path,
    starlette_rs_source: Path,
    cargo_command: list[str],
    *,
    all_features: bool = False,
    fault_injection: bool = False,
) -> None:
    command = [
        *cargo_command,
        "metadata",
        "--manifest-path",
        str(overlay_root / "Cargo.toml"),
        "--locked",
        "--offline",
        "--format-version",
        "1",
    ]
    if all_features:
        command.append("--all-features")
    else:
        features = ["pyo3/extension-module"]
        if fault_injection:
            features.append(FAULT_INJECTION_FEATURE)
        command.extend(["--features", ",".join(features)])
    completed = subprocess.run(
        command,
        cwd=overlay_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode:
        raise SystemExit(
            "cannot verify target Cargo workspace before build: "
            + (completed.stderr.strip() or "cargo metadata failed")
        )
    try:
        metadata = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Cargo returned malformed dependency metadata: {exc}") from exc

    if Path(metadata.get("workspace_root", "")).resolve() != overlay_root.resolve():
        raise SystemExit("Cargo metadata did not resolve this FastAPI overlay as its workspace")
    packages = {package["id"]: package for package in metadata.get("packages", [])}
    workspace_members = set(metadata.get("workspace_members", []))
    expected_members = {
        "fastapi-rs": ROOT / "fastapi-rs/Cargo.toml",
        "fastapi-rs-py": ROOT / "fastapi-rs-py/Cargo.toml",
    }
    member_packages: dict[str, dict[str, object]] = {}
    for name, source_manifest in expected_members.items():
        overlay_manifest = overlay_root / source_manifest.relative_to(ROOT)
        if overlay_manifest.is_symlink() or (
            overlay_manifest.read_bytes() != source_manifest.read_bytes()
        ):
            raise SystemExit(f"overlay Cargo member manifest differs from its source: {name}")
        matches = [
            package
            for package in packages.values()
            if package.get("name") == name
            and Path(package.get("manifest_path", "")).resolve() == overlay_manifest.resolve()
            and package.get("id") in workspace_members
        ]
        if len(matches) != 1:
            raise SystemExit(
                "Cargo metadata does not prove the overlay contains FastAPI workspace member "
                f"{name}"
            )
        targets = matches[0].get("targets", [])
        if not targets:
            raise SystemExit(f"Cargo metadata omitted source targets for {name}")
        for target in targets:
            target_source = Path(target.get("src_path", "")).resolve()
            try:
                target_source.relative_to(source_manifest.parent.resolve())
            except ValueError as exc:
                raise SystemExit(
                    f"Cargo metadata resolved {name} source outside its original member: "
                    f"{target_source}"
                ) from exc
            if not target_source.is_file():
                raise SystemExit(
                    f"Cargo metadata resolved a missing source target: {target_source}"
                )
        member_packages[name] = matches[0]

    root_node = next(
        (
            node
            for node in metadata.get("resolve", {}).get("nodes", [])
            if node.get("id") == member_packages["fastapi-rs"].get("id")
        ),
        None,
    )
    if root_node is None:
        raise SystemExit("Cargo metadata omitted the FastAPI-RS implementation dependency node")
    starlette_dependencies = [
        packages[dependency["pkg"]]
        for dependency in root_node.get("deps", [])
        if packages.get(dependency.get("pkg"), {}).get("name") == "starlette-rs"
    ]
    expected_starlette_manifest = (starlette_rs_source / "starlette-rs/Cargo.toml").resolve()
    if (
        len(starlette_dependencies) != 1
        or Path(starlette_dependencies[0].get("manifest_path", "")).resolve()
        != expected_starlette_manifest
    ):
        actual = [package.get("manifest_path") for package in starlette_dependencies]
        raise SystemExit(
            "FastAPI-RS Cargo metadata resolved Starlette-RS outside the selected checkout: "
            f"expected {expected_starlette_manifest}, got {actual}"
        )


def _extension_suffix(target_python: Path) -> str:
    result = subprocess.run(
        [
            str(target_python),
            "-c",
            "import importlib.machinery; print(next("
            "suffix for suffix in importlib.machinery.EXTENSION_SUFFIXES "
            "if suffix.startswith('.abi3')))",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip() or "cannot identify target Python extension suffix")
    suffix = result.stdout.strip()
    if not suffix:
        raise SystemExit("target Python has no abi3 extension suffix")
    return suffix


def _install_extension_atomically(source: Path, destination: Path) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        shutil.copy2(source, temporary_path)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def _fault_site_packages(target_python: Path) -> Path:
    """Require the selected interpreter to use a venv contained in the fault output."""
    site_packages_result = subprocess.run(
        [
            str(target_python),
            "-c",
            "import json, sys, sysconfig; print(json.dumps({"
            "'prefix': sys.prefix, 'purelib': sysconfig.get_paths()['purelib']}))",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if site_packages_result.returncode:
        raise SystemExit(
            site_packages_result.stderr.strip() or "cannot locate the fault target site-packages"
        )
    try:
        environment_paths = json.loads(site_packages_result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit("fault target Python returned malformed environment paths") from exc
    if not isinstance(environment_paths, dict):
        raise SystemExit("fault target Python returned malformed environment paths")
    prefix = Path(environment_paths.get("prefix", ""))
    site_packages = Path(environment_paths.get("purelib", ""))
    if not prefix.is_absolute() or not site_packages.is_absolute():
        raise SystemExit("fault target Python returned non-absolute environment paths")
    try:
        resolved_prefix = prefix.resolve()
        resolved_prefix.relative_to(FAULT_INJECTION_ROOT.resolve())
        site_packages.resolve().relative_to(resolved_prefix)
    except ValueError as exc:
        raise SystemExit(
            "fault target Python must use site-packages inside a venv under target/fault-injection/"
        ) from exc
    return site_packages


def _activate_fault_extension_overlay(site_packages: Path) -> Path:
    """Put the isolated extension package before the editable source package."""
    if not site_packages.is_absolute():
        raise SystemExit("fault target Python returned a non-absolute site-packages path")
    site_packages.mkdir(parents=True, exist_ok=True)

    package_overlay = FAULT_INJECTION_ROOT / "python"
    activation_file = site_packages / "fastapi_rs_fault_injection.pth"
    activation = f"import sys; sys.path.insert(0, {str(package_overlay.resolve())!r})\n"
    activation_mode = activation_file.stat().st_mode & 0o7777 if activation_file.exists() else 0o644
    _atomic_write(activation_file, activation.encode("utf-8"), activation_mode)
    return activation_file


def _fault_python_source() -> Path:
    """Keep editable facade paths stable and the fault native package isolated."""
    source_root = ROOT / "fastapi-rs-py/python"
    package_overlay = FAULT_INJECTION_ROOT / "python"
    package_overlay.mkdir(parents=True, exist_ok=True)
    for source_entry in source_root.iterdir():
        destination = package_overlay / source_entry.name
        if source_entry.name == "fastapi_rs":
            if destination.is_symlink():
                raise SystemExit("fault native package must not link to the normal package")
            destination.mkdir(exist_ok=True)
            shutil.copy2(source_entry / "__init__.py", destination / "__init__.py")
        elif destination.is_symlink():
            if destination.resolve() != source_entry.resolve():
                raise SystemExit(f"fault facade link does not resolve to its source: {destination}")
        elif destination.exists():
            raise SystemExit(f"fault facade path is not a source link: {destination}")
        else:
            destination.symlink_to(source_entry, target_is_directory=source_entry.is_dir())
    return package_overlay


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, help="target virtualenv Python")
    parser.add_argument("--uv", default="uv", help="uv executable")
    parser.add_argument("--cargo", default="cargo", help="Cargo command (supports wrappers)")
    parser.add_argument(
        "--clippy", action="store_true", help="run strict workspace Clippy without installing"
    )
    parser.add_argument(
        "--fault-injection",
        action="store_true",
        help="build into target/fault-injection without replacing the normal extension",
    )
    parser.add_argument(
        "--starlette-rs-source", required=True, type=Path, help="selected Starlette-RS checkout"
    )
    args = parser.parse_args()
    if args.clippy and args.fault_injection:
        parser.error("--fault-injection cannot be combined with --clippy")
    if args.fault_injection and args.python is None:
        parser.error("--fault-injection requires --python inside target/fault-injection/")
    starlette_rs_source = args.starlette_rs_source.resolve()
    if not starlette_rs_source.is_dir():
        raise SystemExit(f"Starlette-RS source directory does not exist: {starlette_rs_source}")
    cargo_command = shlex.split(args.cargo)
    if not cargo_command:
        raise SystemExit("Cargo command must not be empty")
    overlay_parent = ROOT
    default_target_directory = ROOT / "target"
    default_target_directory.mkdir(exist_ok=True)
    target_directory = (
        FAULT_INJECTION_ROOT / "cargo"
        if args.fault_injection
        else Path(os.environ.get("CARGO_TARGET_DIR", default_target_directory)).resolve()
    )
    if args.fault_injection:
        target_directory.mkdir(parents=True, exist_ok=True)
    target_python = None
    fault_site_packages = None
    python_source = ROOT / "fastapi-rs-py/python"
    if not args.clippy:
        if args.python is None:
            raise SystemExit("--python is required unless --clippy is selected")
        target_python = args.python.absolute()
        if not target_python.is_file():
            raise SystemExit(f"target Python does not exist: {target_python}")
        if args.fault_injection:
            try:
                target_python.relative_to(FAULT_INJECTION_ROOT)
            except ValueError as exc:
                raise SystemExit(
                    "fault-injection Python must be inside target/fault-injection/"
                ) from exc
            fault_site_packages = _fault_site_packages(target_python)
            python_source = _fault_python_source()
    with tempfile.TemporaryDirectory(
        prefix=".fastapi-rs-build-", dir=overlay_parent
    ) as temporary_directory:
        overlay_root = Path(temporary_directory)
        _workspace_overlay(starlette_rs_source, overlay_root, python_source)
        _verify_overlay_metadata(
            overlay_root,
            starlette_rs_source,
            cargo_command,
            all_features=args.clippy,
            fault_injection=args.fault_injection,
        )
        environment = os.environ.copy()
        environment["CARGO_TARGET_DIR"] = str(target_directory)
        if args.clippy:
            command = [
                *cargo_command,
                "clippy",
                "--manifest-path",
                str(overlay_root / "Cargo.toml"),
                "--locked",
                "--offline",
                "--workspace",
                "--all-targets",
                "--all-features",
                "--",
                "-D",
                "warnings",
            ]
            return subprocess.run(
                command, cwd=overlay_root, env=environment, check=False
            ).returncode

        if target_python is None:
            raise SystemExit("target Python was not initialized")
        environment["PYO3_PYTHON"] = str(target_python)
        features = ["pyo3/extension-module"]
        if args.fault_injection:
            features.append(FAULT_INJECTION_FEATURE)
        editable_status = _install_editable_target(
            args.uv, target_python, overlay_root, environment, features
        )
        if editable_status:
            return editable_status
        command = [
            *cargo_command,
            "build",
            "--manifest-path",
            str(overlay_root / "Cargo.toml"),
            "--locked",
            "--offline",
            "--release",
            "--features",
            ",".join(features),
        ]
        completed = subprocess.run(command, cwd=overlay_root, env=environment, check=False)
        if completed.returncode:
            return completed.returncode

        artifact_candidates = [
            target_directory / "release" / name
            for name in ("lib_core.dylib", "lib_core.so", "_core.dll", "core.dll")
        ]
        artifacts = [path for path in artifact_candidates if path.is_file()]
        if len(artifacts) != 1:
            raise SystemExit(
                f"expected one built FastAPI-RS library artifact, found {len(artifacts)}"
            )
        suffix = _extension_suffix(target_python)
        if args.fault_injection:
            package_overlay = FAULT_INJECTION_ROOT / "python" / "fastapi_rs"
            package_overlay.mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                ROOT / "fastapi-rs-py/python/fastapi_rs/__init__.py",
                package_overlay / "__init__.py",
            )
            destination = package_overlay / f"_core{suffix}"
        else:
            destination = ROOT / "fastapi-rs-py/python/fastapi_rs" / f"_core{suffix}"
        _install_extension_atomically(artifacts[0], destination)
    if args.fault_injection:
        if fault_site_packages is None:
            raise SystemExit("fault target site-packages were not initialized")
        activation_file = _activate_fault_extension_overlay(fault_site_packages)
        print(
            "installed fault-injection extension under "
            f"{FAULT_INJECTION_ROOT / 'python' / 'fastapi_rs'} "
            f"built against {starlette_rs_source}; activated by {activation_file}"
        )
    else:
        print(f"installed native extension built against {starlette_rs_source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
