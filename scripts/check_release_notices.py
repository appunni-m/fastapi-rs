"""Check source notice evidence and license files in FastAPI-RS archives."""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]
NOTICE_FILE = ROOT / "THIRD_PARTY_NOTICES.md"
PROJECT_LICENSE = ROOT / "LICENSE.md"
NOTICE_NAME = "THIRD_PARTY_NOTICES.md"
LICENSE_NAME = "LICENSE.md"
BEGIN_STARLETTE = "<!-- BEGIN PINNED STARLETTE-RS LICENSE -->"
END_STARLETTE = "<!-- END PINNED STARLETTE-RS LICENSE -->"
BEGIN_FASTAPI = "<!-- BEGIN PINNED FASTAPI LICENSE -->"
END_FASTAPI = "<!-- END PINNED FASTAPI LICENSE -->"
BEGIN_CARGO = "<!-- BEGIN LOCKED RUST DEPENDENCY NOTICES -->"
END_CARGO = "<!-- END LOCKED RUST DEPENDENCY NOTICES -->"
PACKAGE_NAMES = ("fastapi-rs", "fastapi-rs-py")
LICENSE_FILE_RE = re.compile(
    r"(?i)^(?:license|licence|unlicense|copying|copyright|authors|notice)(?:[-_.].*)?$"
)


def _normalize_line_endings(contents: bytes) -> bytes:
    return contents.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _dependency_roles() -> dict[tuple[str, str], tuple[str, str]]:
    report = ROOT / "docs/RUST_TARGET_DEPENDENCIES.md"
    try:
        lines = report.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise SystemExit(f"cannot read Rust dependency inventory {report}: {exc}") from exc
    roles: dict[tuple[str, str], tuple[str, str]] = {}
    for line in lines:
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 9:
            continue
        identity = cells[0].rsplit(" ", 1)
        if len(identity) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", identity[1]):
            continue
        roles[(identity[0], identity[1])] = (cells[1], cells[3])
    return roles


def _registry_archive(package: dict[str, object]) -> bytes:
    name = str(package["name"])
    version = str(package["version"])
    cargo_home = Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo"))
    matches = sorted(
        (cargo_home / "registry/cache").glob(f"index.crates.io-*/{name}-{version}.crate")
    )
    if not matches:
        raise SystemExit(
            f"no cached locked crate archive found for {name} {version}; run `cargo fetch --locked`"
        )
    expected = package.get("checksum")
    if not isinstance(expected, str):
        raise SystemExit(f"Cargo.lock has no checksum for registry crate {name} {version}")
    for path in matches:
        archive_bytes = path.read_bytes()
        actual = hashlib.sha256(archive_bytes).hexdigest()
        if actual == expected:
            return archive_bytes
    raise SystemExit(f"no cached archive matches Cargo.lock checksum for {name} {version}")


def _read_crate_notice_sources(
    package: dict[str, object], archive_bytes: bytes
) -> tuple[str, list[tuple[str, bytes]]]:
    name = str(package["name"])
    version = str(package["version"])
    root_prefix = f"{name}-{version}/"
    try:
        archive = tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz")
    except tarfile.TarError as exc:
        raise SystemExit(f"invalid locked crate archive for {name} {version}: {exc}") from exc
    with archive:
        members = archive.getmembers()
        cargo_member = [m for m in members if m.name == f"{root_prefix}Cargo.toml"]
        if len(cargo_member) != 1 or not cargo_member[0].isfile():
            raise SystemExit(f"{name} {version} crate archive has no unique Cargo.toml")
        cargo_stream = archive.extractfile(cargo_member[0])
        if cargo_stream is None:
            raise SystemExit(f"cannot read Cargo.toml for {name} {version}")
        try:
            manifest = tomllib.loads(cargo_stream.read().decode("utf-8"))
        except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
            raise SystemExit(f"invalid normalized Cargo.toml for {name} {version}: {exc}") from exc
        package_data = manifest.get("package")
        license_expression = package_data.get("license") if isinstance(package_data, dict) else None
        if not isinstance(license_expression, str):
            raise SystemExit(f"{name} {version} crate archive has no package license expression")

        sources: list[tuple[str, bytes]] = []
        for member in members:
            if not member.name.startswith(root_prefix):
                continue
            relative = member.name[len(root_prefix) :]
            relative_path = PurePosixPath(relative)
            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
                or not LICENSE_FILE_RE.fullmatch(relative_path.name)
                or not member.isfile()
            ):
                continue
            if name == "libz-sys" and version == "1.1.29" and relative == "src/zlib/LICENSE":
                # This C source notice is duplicated in a separate conditional block below.
                continue
            stream = archive.extractfile(member)
            if stream is None:
                raise SystemExit(f"cannot read {member.name} in {name} {version} crate archive")
            contents = stream.read()
            try:
                contents.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise SystemExit(f"non-UTF-8 license source {member.name}: {exc}") from exc
            sources.append((relative, contents))
        if not sources:
            raise SystemExit(f"{name} {version} crate archive has no top-level license source file")
        return license_expression, sorted(sources)


def _cargo_notice_body() -> str:
    try:
        lock = tomllib.loads((ROOT / "Cargo.lock").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"cannot read Cargo.lock: {exc}") from exc
    roles = _dependency_roles()
    packages = [
        item
        for item in lock.get("package", [])
        if isinstance(item, dict) and str(item.get("source", "")).startswith("registry+")
    ]
    packages.sort(key=lambda item: (str(item["name"]), str(item["version"])))

    rows: list[tuple[str, str, str, str, str, list[tuple[str, bytes]]]] = []
    text_sources: dict[str, list[tuple[str, str, str]]] = {}
    text_contents: dict[str, bytes] = {}
    for package in packages:
        name = str(package["name"])
        version = str(package["version"])
        identity = (name, version)
        if identity not in roles:
            raise SystemExit(
                f"{name} {version} is in Cargo.lock but missing from "
                "docs/RUST_TARGET_DEPENDENCIES.md; regenerate that inventory first"
            )
        expression, package_roles = roles[identity]
        crate_bytes = _registry_archive(package)
        source_expression, license_sources = _read_crate_notice_sources(package, crate_bytes)
        if source_expression != expression:
            raise SystemExit(
                f"license expression mismatch for {name} {version}: inventory has "
                f"{expression!r}, locked archive has {source_expression!r}"
            )
        for relative, contents in license_sources:
            digest = hashlib.sha256(contents).hexdigest()
            text_sources.setdefault(digest, []).append((name, version, relative))
            text_contents[digest] = _normalize_line_endings(contents)
        rows.append(
            (name, version, str(package["checksum"]), expression, package_roles, license_sources)
        )

    lines = [
        "## Locked Rust Cargo dependency license sources",
        "",
        "This source-derived inventory covers license/copyright-named files in every registry",
        "package in the pinned `Cargo.lock`;",
        "the role labels match [`RUST_TARGET_DEPENDENCIES.md`](docs/RUST_TARGET_DEPENDENCIES.md).",
        "License source bytes below are copied from the exact `.crate` archives whose SHA-256",
        "checksums are recorded in `Cargo.lock`. This is the locked dependency-source union, not",
        "a claim that every package is linked into every wheel: target-specific, optional,",
        "build-only, and adapter-only roles remain conditional on the selected artifact/profile.",
        "Source digests cover original bytes; rendered license text normalizes line endings to LF.",
        "The bundled zlib source license is emitted separately below because it applies only",
        "when the artifact selects that backend.",
        "The wheel's actual native links must be inspected per artifact.",
        "",
        "| Crate | Locked `.crate` SHA-256 | Cargo license expression | "
        "Inventory role | Source file(s) |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, version, archive_checksum, expression, package_roles, license_sources in rows:
        source_names = ", ".join(
            f"`{filename}` (`{hashlib.sha256(contents).hexdigest()}`)"
            for filename, contents in license_sources
        )
        lines.append(
            f"| `{name} {version}` | `{archive_checksum}` | `{expression}` | "
            f"{package_roles} | {source_names} |"
        )

    for digest, references in sorted(text_sources.items()):
        lines.extend(
            [
                "",
                f"### Exact license source text `{digest}`",
                "",
                "Verbatim source files: "
                + ", ".join(
                    f"`{name}-{version}/{filename}`" for name, version, filename in references
                )
                + ".",
                f"<!-- BEGIN CARGO LICENSE TEXT {digest} -->",
            ]
        )
        lines.append(text_contents[digest].decode("utf-8"))
        lines.extend([f"<!-- END CARGO LICENSE TEXT {digest} -->", ""])

    libz_package = next(
        (item for item in packages if item["name"] == "libz-sys" and item["version"] == "1.1.29"),
        None,
    )
    if libz_package is None:
        raise SystemExit("Cargo.lock does not contain pinned libz-sys 1.1.29")
    libz_bytes = _registry_archive(libz_package)
    with tarfile.open(fileobj=io.BytesIO(libz_bytes), mode="r:gz") as archive:
        license_path = "libz-sys-1.1.29/src/zlib/LICENSE"
        version_path = "libz-sys-1.1.29/src/zlib/zlib.h"
        license_members = [m for m in archive.getmembers() if m.name == license_path]
        version_members = [m for m in archive.getmembers() if m.name == version_path]
        if len(license_members) != 1 or len(version_members) != 1:
            raise SystemExit(
                "libz-sys 1.1.29 archive lacks unique bundled zlib license/version sources"
            )
        zlib_license_stream = archive.extractfile(license_members[0])
        zlib_header_stream = archive.extractfile(version_members[0])
        if zlib_license_stream is None or zlib_header_stream is None:
            raise SystemExit("cannot read bundled zlib license/version source")
        zlib_license = zlib_license_stream.read()
        zlib_header = zlib_header_stream.read().decode("utf-8")
    if not re.search(r'^#define ZLIB_VERSION "1\.3\.2"$', zlib_header, re.MULTILINE):
        raise SystemExit("libz-sys 1.1.29 bundled zlib source is not exactly version 1.3.2")
    zlib_digest = hashlib.sha256(zlib_license).hexdigest()
    lines.extend(
        [
            "",
            "## Conditional bundled zlib notice",
            "",
            "This notice applies only to an artifact whose `libz-sys` backend compiles the",
            "bundled zlib source. It does not apply when that artifact links a host/system zlib.",
            "Backend selection is artifact-specific; Cargo.lock alone does not settle it.",
            "Source: locked `libz-sys` 1.1.29 archive, `src/zlib/LICENSE`; the bundled version",
            "is verified as 1.3.2 from `src/zlib/zlib.h`. License SHA-256: `"
            + zlib_digest
            + "`; locked `.crate` SHA-256: `"
            + str(libz_package["checksum"])
            + "`.",
            "<!-- BEGIN BUNDLED ZLIB 1.3.2 LICENSE -->",
            _normalize_line_endings(zlib_license).decode("utf-8"),
            "<!-- END BUNDLED ZLIB 1.3.2 LICENSE -->",
            "",
        ]
    )
    return "\n".join(lines)


def _source_identity() -> tuple[dict[str, object], dict[str, object]]:
    try:
        metadata = yaml.safe_load((ROOT / "metadata.yaml").read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SystemExit(f"cannot read pinned source identity from metadata.yaml: {exc}") from exc
    authority = metadata.get("authority") if isinstance(metadata, dict) else None
    starlette_rs = metadata.get("starlette_rs") if isinstance(metadata, dict) else None
    if not isinstance(authority, dict) or not isinstance(starlette_rs, dict):
        raise SystemExit("metadata.yaml must pin FastAPI and Starlette-RS source identities")
    if not isinstance(authority.get("commit"), str) or not isinstance(
        starlette_rs.get("commit"), str
    ):
        raise SystemExit("metadata.yaml must contain pinned FastAPI and Starlette-RS commits")
    return authority, starlette_rs


def _git_file(source: Path, revision: str, filename: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(source), "show", f"{revision}:{filename}"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            f"cannot read pinned source {revision}:{filename} from {source}: {exc}"
        ) from exc
    return result.stdout


def _replace_region(text: str, heading: str, next_heading: str, replacement: str) -> str:
    if text.count(heading) != 1 or (next_heading != "\0" and text.count(next_heading) != 1):
        raise SystemExit(f"expected one {heading!r} section followed by {next_heading!r}")
    start = text.index(heading)
    end = len(text) if next_heading == "\0" else text.index(next_heading, start + len(heading))
    return text[:start] + replacement + text[end:]


def _replace_marked_region(text: str, begin: str, end: str, replacement: str) -> str:
    if text.count(begin) != 1 or text.count(end) != 1:
        raise SystemExit(f"expected one marked region from {begin!r} through {end!r}")
    start = text.index(begin) + len(begin)
    finish = text.index(end, start)
    return text[:start] + "\n" + replacement + text[finish:]


def _sync_source_notices(fastapi_source: Path, starlette_rs_source: Path) -> None:
    authority, starlette_rs = _source_identity()
    fastapi_commit = str(authority["commit"])
    starlette_commit = str(starlette_rs["commit"])
    fastapi_license = _git_file(fastapi_source, fastapi_commit, "LICENSE")
    starlette_license = _git_file(starlette_rs_source, starlette_commit, "LICENSE.md")
    try:
        text = NOTICE_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"cannot read {NOTICE_FILE}: {exc}") from exc

    starlette_heading = "## Starlette-RS — BSD 3-Clause"
    fastapi_heading = "## FastAPI 0.141.1 signature metadata — MIT"
    starlette_section = (
        f"{starlette_heading}\n\n"
        f"Source: pinned Starlette-RS `LICENSE.md` at commit `{starlette_commit}`.\n\n"
        f"{BEGIN_STARLETTE}\n"
        f"{starlette_license.decode('utf-8')}"
        f"{END_STARLETTE}\n\n"
    )
    text = _replace_region(text, starlette_heading, fastapi_heading, starlette_section)
    text = _replace_region(
        text,
        fastapi_heading,
        "\0",  # Replace through EOF; this sentinel cannot occur in the notice file.
        (
            f"{fastapi_heading}\n\n"
            "The route and parameter-factory signature metadata and annotation text in\n"
            "`fastapi-rs/src/route_signature.json` and\n"
            "`fastapi-rs/src/parameter_signature_contract.json` were copied from FastAPI 0.141.1 "
            "at the\n"
            f"source commit `{fastapi_commit}` recorded in that file.\n\n"
            f"{BEGIN_FASTAPI}\n"
            f"{fastapi_license.decode('utf-8')}"
            f"{END_FASTAPI}\n"
        ),
    )
    text = _replace_marked_region(text, BEGIN_CARGO, END_CARGO, _cargo_notice_body())
    NOTICE_FILE.write_text(text, encoding="utf-8")

    for package_name in PACKAGE_NAMES:
        package_notice = ROOT / package_name / NOTICE_NAME
        package_notice.write_bytes(NOTICE_FILE.read_bytes())


def _region(text: str, begin: str, end: str, label: str) -> bytes:
    if text.count(begin) != 1 or text.count(end) != 1:
        raise SystemExit(f"{NOTICE_NAME} must contain exactly one marked {label} notice")
    begin_index = text.index(begin) + len(begin)
    if not text.startswith("\n", begin_index):
        raise SystemExit(f"{label} notice must start on the line after its begin marker")
    end_index = text.index(end, begin_index + 1)
    return text[begin_index + 1 : end_index].encode("utf-8")


def _check_source(fastapi_source: Path, starlette_rs_source: Path) -> None:
    authority, starlette_rs = _source_identity()
    expected_fastapi = _git_file(fastapi_source, str(authority["commit"]), "LICENSE")
    expected_starlette = _git_file(starlette_rs_source, str(starlette_rs["commit"]), "LICENSE.md")
    try:
        notice_bytes = NOTICE_FILE.read_bytes()
        notice_text = notice_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"cannot read UTF-8 third-party notices: {exc}") from exc
    if _region(notice_text, BEGIN_FASTAPI, END_FASTAPI, "FastAPI") != expected_fastapi:
        raise SystemExit("FastAPI license excerpt differs from its pinned LICENSE source")
    if _region(notice_text, BEGIN_STARLETTE, END_STARLETTE, "Starlette-RS") != expected_starlette:
        raise SystemExit("Starlette-RS license excerpt differs from its pinned LICENSE.md source")
    if _region(
        notice_text, BEGIN_CARGO, END_CARGO, "Cargo dependencies"
    ) != _cargo_notice_body().encode("utf-8"):
        raise SystemExit(
            "Cargo dependency license texts differ from checksum-verified locked crate sources; "
            "run scripts/check_release_notices.py --sync"
        )

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8")).get("project")
    if not isinstance(project, dict):
        raise SystemExit("pyproject.toml must contain project metadata")
    declared_wheel_files = {Path(str(name)).name for name in project.get("license-files", [])}
    required_files = {LICENSE_NAME, NOTICE_NAME}
    if not required_files.issubset(declared_wheel_files):
        raise SystemExit(
            "pyproject.toml license-files omits required release files: "
            f"{sorted(required_files - declared_wheel_files)}"
        )

    if not PROJECT_LICENSE.is_file():
        raise SystemExit(f"missing project license: {PROJECT_LICENSE}")
    for package_name in PACKAGE_NAMES:
        package_root = ROOT / package_name
        package_manifest = package_root / "Cargo.toml"
        package_data = tomllib.loads(package_manifest.read_text(encoding="utf-8")).get("package")
        if not isinstance(package_data, dict):
            raise SystemExit(f"{package_manifest} must contain package metadata")
        license_file = package_data.get("license-file")
        if (
            not isinstance(license_file, str)
            or (package_root / license_file).resolve() != PROJECT_LICENSE
        ):
            raise SystemExit(f"{package_manifest} must use the root LICENSE.md as license-file")
        local_notice = package_root / NOTICE_NAME
        if not local_notice.is_file() or local_notice.read_bytes() != notice_bytes:
            raise SystemExit(
                f"{local_notice.relative_to(ROOT)} must match the root {NOTICE_NAME}; "
                "run scripts/check_release_notices.py --sync"
            )

    print(
        "verified source notices against FastAPI "
        f"{authority['commit']} and Starlette-RS {starlette_rs['commit']}"
    )
    print("verified root notice and project license declarations for wheel and both Cargo packages")


def _manifest_identity(package_name: str) -> tuple[str, Path]:
    if package_name not in PACKAGE_NAMES:
        raise SystemExit(f"unsupported Cargo package for notice check: {package_name}")
    package_root = ROOT / package_name
    package = tomllib.loads((package_root / "Cargo.toml").read_text(encoding="utf-8"))["package"]
    version = package.get("version")
    if version == {"workspace": True}:
        version = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))["workspace"]
        version = version["package"]["version"]
    if not isinstance(version, str):
        raise SystemExit(f"cannot resolve {package_name} Cargo package version")
    return f"{package_name}-{version}", package_root


def _check_crate_archive(package_name: str, archive_path: Path) -> None:
    directory_name, _ = _manifest_identity(package_name)
    try:
        archive = tarfile.open(archive_path, mode="r:gz")
    except (OSError, tarfile.TarError) as exc:
        raise SystemExit(f"cannot read Cargo archive {archive_path}: {exc}") from exc
    with archive:
        members = archive.getmembers()
        if not members:
            raise SystemExit(f"Cargo archive is empty: {archive_path}")
        indexed: dict[str, list[tarfile.TarInfo]] = {}
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise SystemExit(f"unsafe Cargo archive path in {archive_path}: {member.name}")
            indexed.setdefault(member.name, []).append(member)
        required = {
            f"{directory_name}/{LICENSE_NAME}": PROJECT_LICENSE.read_bytes(),
            f"{directory_name}/{NOTICE_NAME}": NOTICE_FILE.read_bytes(),
        }
        for member_name, expected_bytes in required.items():
            occurrences = indexed.get(member_name, [])
            if len(occurrences) != 1 or not occurrences[0].isfile():
                raise SystemExit(
                    f"{archive_path} must contain exactly one regular file {member_name}"
                )
            stream = archive.extractfile(occurrences[0])
            if stream is None or stream.read() != expected_bytes:
                raise SystemExit(f"{archive_path} has stale or changed notice file {member_name}")
    print(f"verified Cargo notice archive: {archive_path}")


def _parse_crate(value: str) -> tuple[str, Path]:
    package_name, separator, archive_path = value.partition("=")
    if not separator or not archive_path:
        raise SystemExit("--crate must be given as PACKAGE=PATH")
    return package_name, Path(archive_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fastapi-source",
        type=Path,
        default=Path(os.environ.get("FASTAPI_SOURCE", ROOT.parent / "fastapi")),
        help="FastAPI checkout containing the pinned commit",
    )
    parser.add_argument(
        "--starlette-rs-source",
        type=Path,
        default=Path(os.environ.get("STARLETTE_RS_SOURCE", ROOT.parent / "starlette-rs")),
        help="Starlette-RS checkout containing the pinned commit",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="refresh pinned license excerpts and package-local notice mirrors",
    )
    parser.add_argument("--wheel", type=Path, help="validate an already-built wheel archive")
    parser.add_argument(
        "--crate",
        action="append",
        default=[],
        metavar="PACKAGE=PATH",
        help="validate an already-built Cargo .crate archive; repeat for each package",
    )
    parser.add_argument(
        "--require-all-crates",
        action="store_true",
        help="require exactly one archive for each configured Cargo package",
    )
    args = parser.parse_args()
    if args.sync:
        _sync_source_notices(args.fastapi_source, args.starlette_rs_source)
    _check_source(args.fastapi_source, args.starlette_rs_source)

    if args.wheel is not None:
        from check_release_wheel import validate_wheel

        validate_wheel(args.wheel)
        print(f"verified wheel notice archive: {args.wheel}")
    parsed_crates = [_parse_crate(value) for value in args.crate]
    if len({name for name, _ in parsed_crates}) != len(parsed_crates):
        raise SystemExit("each Cargo package may be specified only once")
    if args.require_all_crates and set(name for name, _ in parsed_crates) != set(PACKAGE_NAMES):
        raise SystemExit(f"--require-all-crates needs exactly {list(PACKAGE_NAMES)}")
    for package_name, archive_path in parsed_crates:
        _check_crate_archive(package_name, archive_path)
    if args.wheel is None and not parsed_crates:
        print("archive check skipped: pass --wheel and/or --crate with already-built artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
