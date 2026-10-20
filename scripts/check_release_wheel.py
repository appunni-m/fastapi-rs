"""Validate the contents and runtime metadata of a FastAPI-RS wheel."""

from __future__ import annotations

import argparse
import base64
import csv
import email.parser
import email.policy
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

import tomllib
from normalize_release_wheel_sbom import validate_sbom_document

ROOT = Path(__file__).resolve().parents[1]
NATIVE_SUFFIXES = (".so", ".dylib", ".pyd", ".dll")


def _canonical_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _requirement(value: str) -> tuple[str, str]:
    match = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(.*)$", value.strip())
    if match is None:
        raise SystemExit(f"unsupported project dependency declaration: {value!r}")
    return _canonical_name(match.group(1)), match.group(2).strip()


def _project_data() -> tuple[dict[str, object], dict[str, object]]:
    try:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"cannot read pyproject.toml: {exc}") from exc
    project_data = project.get("project")
    maturin_data = project.get("tool", {}).get("maturin")
    if not isinstance(project_data, dict) or not isinstance(maturin_data, dict):
        raise SystemExit("pyproject.toml must configure project and Maturin metadata")
    return project_data, maturin_data


def _validate_record(archive: zipfile.ZipFile, names: list[str], record_name: str) -> None:
    try:
        text = io.TextIOWrapper(io.BytesIO(archive.read(record_name)), encoding="utf-8", newline="")
        rows = list(csv.reader(text))
    except (KeyError, UnicodeDecodeError, csv.Error) as exc:
        raise SystemExit(f"wheel RECORD is unreadable: {exc}") from exc
    if any(len(row) != 3 for row in rows):
        raise SystemExit("wheel RECORD must have exactly three columns per row")

    entries = {row[0]: row[1:] for row in rows}
    if len(entries) != len(rows) or set(entries) != set(names):
        raise SystemExit("wheel RECORD paths must list every archive member exactly once")
    if entries[record_name] != ["", ""]:
        raise SystemExit("wheel RECORD must leave its own hash and size empty")

    for name in names:
        if name == record_name:
            continue
        expected_hash, expected_size = entries[name]
        contents = archive.read(name)
        actual_hash = base64.urlsafe_b64encode(hashlib.sha256(contents).digest())
        actual_hash = actual_hash.rstrip(b"=").decode("ascii")
        if expected_hash != f"sha256={actual_hash}" or expected_size != str(len(contents)):
            raise SystemExit(f"wheel RECORD hash or size is incorrect for {name}")


def validate_wheel(wheel_path: Path) -> list[str]:
    """Check one built wheel and return its sorted archive member names."""
    if not wheel_path.is_file() or wheel_path.suffix != ".whl":
        raise SystemExit(f"wheel does not exist: {wheel_path}")
    project, maturin = _project_data()
    try:
        archive = zipfile.ZipFile(wheel_path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"cannot read wheel archive {wheel_path}: {exc}") from exc

    with archive:
        names = archive.namelist()
        if not names:
            raise SystemExit("wheel archive is empty")
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        if duplicates:
            raise SystemExit(f"wheel contains duplicate archive members: {duplicates}")
        for name in names:
            member = PurePosixPath(name)
            if member.is_absolute() or ".." in member.parts:
                raise SystemExit(f"wheel contains an unsafe archive member: {name}")
        if any(name.lower().endswith(".pth") for name in names):
            raise SystemExit("release wheel contains a .pth file")
        if any(
            "__pycache__" in PurePosixPath(name).parts or name.endswith(".pyc") for name in names
        ):
            raise SystemExit("release wheel contains Python bytecode cache files")
        sbom_names = sorted(
            name for name in names if ".dist-info/sboms/" in name and name.endswith(".json")
        )
        if not any(name.endswith("/fastapi-rs-py.cyclonedx.json") for name in sbom_names):
            raise SystemExit("release wheel is missing the Rust dependency CycloneDX SBOM")
        for sbom_name in sbom_names:
            try:
                sbom = json.loads(archive.read(sbom_name))
            except (KeyError, UnicodeDecodeError, ValueError) as exc:
                raise SystemExit(f"wheel SBOM is unreadable: {sbom_name}: {exc}") from exc
            validate_sbom_document(sbom, sbom_name)

        metadata_paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        wheel_paths = [name for name in names if name.endswith(".dist-info/WHEEL")]
        record_paths = [name for name in names if name.endswith(".dist-info/RECORD")]
        if len(metadata_paths) != 1 or len(wheel_paths) != 1 or len(record_paths) != 1:
            raise SystemExit("wheel must contain exactly one METADATA, WHEEL, and RECORD")
        _validate_record(archive, names, record_paths[0])
        dist_info = metadata_paths[0].removesuffix("/METADATA")
        try:
            metadata = email.parser.BytesParser(policy=email.policy.default).parsebytes(
                archive.read(metadata_paths[0])
            )
            wheel_metadata = email.parser.BytesParser(policy=email.policy.default).parsebytes(
                archive.read(wheel_paths[0])
            )
        except (KeyError, ValueError) as exc:
            raise SystemExit(f"wheel metadata is unreadable: {exc}") from exc

        expected_name = str(project.get("name", ""))
        if _canonical_name(str(metadata.get("Name", ""))) != _canonical_name(expected_name):
            raise SystemExit(f"wheel Name is {metadata.get('Name')!r}, expected {expected_name!r}")
        if str(wheel_metadata.get("Root-Is-Purelib", "")).lower() != "false":
            raise SystemExit("native FastAPI-RS wheel must set Root-Is-Purelib: false")
        if "Operating System :: OS Independent" in metadata.get_all("Classifier", []):
            raise SystemExit("native FastAPI-RS wheel must not claim OS independence")
        wheel_tags = wheel_metadata.get_all("Tag", [])
        if not wheel_tags or any(tag.endswith("-any") for tag in wheel_tags):
            raise SystemExit("native FastAPI-RS wheel must use platform-specific wheel tags")

        expected_dependencies = [_requirement(value) for value in project.get("dependencies", [])]
        optional_dependencies = project.get("optional-dependencies", {})
        if not isinstance(optional_dependencies, dict):
            raise SystemExit("pyproject.toml optional dependencies must be a table")
        expected_extras = sorted(_canonical_name(extra) for extra in optional_dependencies)
        for extra, requirements in optional_dependencies.items():
            if not isinstance(extra, str) or not isinstance(requirements, list):
                raise SystemExit(
                    "pyproject.toml optional dependencies must map extra names to arrays"
                )
            for requirement in requirements:
                name, specifier = _requirement(requirement)
                expected_dependencies.append(
                    (name, f"{specifier} ; extra == '{_canonical_name(extra)}'")
                )
        actual_dependencies = [
            _requirement(value) for value in metadata.get_all("Requires-Dist", [])
        ]
        if sorted(expected_dependencies) != sorted(actual_dependencies):
            raise SystemExit(
                "wheel Requires-Dist does not match pyproject.toml: "
                f"expected {sorted(expected_dependencies)}, got {sorted(actual_dependencies)}"
            )
        if any(name == "fastapi" for name, _ in actual_dependencies):
            raise SystemExit("release wheel has an original FastAPI runtime dependency")
        actual_extras = sorted(
            _canonical_name(extra) for extra in metadata.get_all("Provides-Extra", [])
        )
        if actual_extras != expected_extras:
            raise SystemExit(
                "wheel Provides-Extra does not match pyproject.toml: "
                f"expected {expected_extras}, got {actual_extras}"
            )

        source_setting = maturin.get("python-source")
        package_names = maturin.get("python-packages")
        if not isinstance(source_setting, str) or not isinstance(package_names, list):
            raise SystemExit("pyproject.toml must declare Maturin Python source packages")
        python_source = ROOT / source_setting
        expected_python_files: dict[str, bytes] = {}
        for package_name in package_names:
            if not isinstance(package_name, str):
                raise SystemExit("Maturin Python package names must be strings")
            package_root = python_source.joinpath(*package_name.split("."))
            if not package_root.is_dir():
                raise SystemExit(f"configured Python package source is missing: {package_name}")
            for source_file in package_root.rglob("*.py"):
                if "__pycache__" in source_file.parts:
                    continue
                archive_name = source_file.relative_to(python_source).as_posix()
                expected_python_files[archive_name] = source_file.read_bytes()
        if "fastapi/__init__.py" not in expected_python_files:
            raise SystemExit("configured source packages omit the public fastapi facade")
        missing_python = sorted(set(expected_python_files) - set(names))
        if missing_python:
            raise SystemExit(f"wheel is missing Python facade files: {missing_python}")
        changed_python = [
            name for name, content in expected_python_files.items() if archive.read(name) != content
        ]
        if changed_python:
            raise SystemExit(f"wheel Python facade differs from source: {sorted(changed_python)}")

        native_modules = [
            name
            for name in names
            if name.startswith("fastapi_rs/_core") and name.endswith(NATIVE_SUFFIXES)
        ]
        if len(native_modules) != 1:
            raise SystemExit(
                "wheel must contain exactly one fastapi_rs._core native extension; "
                f"found {native_modules}"
            )
        if "fastapi_rs/__init__.py" not in names:
            raise SystemExit("wheel is missing the fastapi_rs package initializer")

        license_files = project.get("license-files", [])
        if not isinstance(license_files, list) or not license_files:
            raise SystemExit("pyproject.toml must declare Python license files")
        expected_license_names = {Path(value).name for value in license_files}
        required_license_names = {"LICENSE.md", "THIRD_PARTY_NOTICES.md"}
        if not required_license_names.issubset(expected_license_names):
            raise SystemExit(
                "pyproject.toml license-files must include the project license and third-party "
                f"notices: {sorted(required_license_names)}"
            )
        archive_license_paths = {
            name.removeprefix(f"{dist_info}/licenses/")
            for name in names
            if name.startswith(f"{dist_info}/licenses/")
        }
        if not expected_license_names.issubset(archive_license_paths):
            raise SystemExit(
                "wheel is missing declared license files: "
                f"{sorted(expected_license_names - archive_license_paths)}"
            )
        metadata_license_names = set(metadata.get_all("License-File", []))
        if metadata_license_names != expected_license_names:
            raise SystemExit(
                "wheel License-File metadata does not match pyproject.toml: "
                f"expected {sorted(expected_license_names)}, got {sorted(metadata_license_names)}"
            )
        for license_name in expected_license_names:
            source_path = ROOT / license_name
            archive_path = f"{dist_info}/licenses/{license_name}"
            if not source_path.is_file() or archive.read(archive_path) != source_path.read_bytes():
                raise SystemExit(
                    f"wheel license file differs from repository source: {license_name}"
                )

    return sorted(names)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path, help="wheel archive to validate")
    args = parser.parse_args()
    members = validate_wheel(args.wheel)
    print(f"verified release wheel: {args.wheel}")
    print("archive members:")
    for member in members:
        print(member)
    return 0


if __name__ == "__main__":
    sys.exit(main())
