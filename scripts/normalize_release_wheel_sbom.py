"""Remove local Cargo checkout paths from an SBOM embedded in a release wheel."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path
from typing import Any


def _portable_purl_value(purl: str) -> str:
    if not isinstance(purl, str) or not purl.startswith("pkg:cargo/"):
        raise SystemExit(
            "local Cargo SBOM component has no package URL; cannot create a portable reference"
        )
    base, separator, query = purl.partition("?download_url=")
    fragment = query.partition("#")[2] if separator else ""
    return f"{base}#{fragment}" if fragment else base


def _portable_purl(component: dict[str, Any]) -> str:
    purl = component.get("purl")
    if not isinstance(purl, str):
        raise SystemExit(
            "local Cargo SBOM component has no package URL; cannot create a portable reference"
        )
    return _portable_purl_value(purl)


def _collect_local_components(value: Any, replacements: dict[str, str]) -> None:
    if isinstance(value, dict):
        old_ref = value.get("bom-ref")
        if isinstance(old_ref, str) and old_ref.startswith("path+file://"):
            new_ref = _portable_purl(value)
            if new_ref in replacements.values():
                raise SystemExit(f"portable SBOM reference is not unique: {new_ref}")
            replacements[old_ref] = new_ref
        for child in value.values():
            _collect_local_components(child, replacements)
    elif isinstance(value, list):
        for child in value:
            _collect_local_components(child, replacements)


def _rewrite_local_references(value: Any, replacements: dict[str, str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"bom-ref", "ref"} and isinstance(child, str):
                value[key] = replacements.get(child, child)
            elif key == "purl" and isinstance(child, str):
                if "?download_url=" in child:
                    value[key] = _portable_purl_value(child)
            elif isinstance(child, (dict, list)):
                _rewrite_local_references(child, replacements)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str):
                value[index] = replacements.get(child, child)
            elif isinstance(child, (dict, list)):
                _rewrite_local_references(child, replacements)


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def validate_sbom_document(document: Any, source: str = "SBOM") -> None:
    """Reject non-portable or structurally inconsistent CycloneDX JSON."""
    if not isinstance(document, dict) or document.get("bomFormat") != "CycloneDX":
        raise SystemExit(f"{source} is not a CycloneDX document")
    if document.get("specVersion") not in {"1.4", "1.5"}:
        raise SystemExit(f"{source} is not CycloneDX 1.4 or 1.5")

    local_markers = (
        "file://",
        "path+file",
        "/private/",
        "/Users/",
        "/tmp/",
        "/home/",
        "/var/folders/",
        "C:\\Users\\",
        "C:/Users/",
    )
    for value in _strings(document):
        if any(marker in value for marker in local_markers):
            raise SystemExit(f"{source} contains a local build path: {value}")

    references: list[str] = []

    def collect_refs(value: Any) -> None:
        if isinstance(value, dict):
            ref = value.get("bom-ref")
            if isinstance(ref, str):
                references.append(ref)
            for child in value.values():
                collect_refs(child)
        elif isinstance(value, list):
            for child in value:
                collect_refs(child)

    collect_refs(document)
    known_refs = set(references)
    if len(known_refs) != len(references):
        raise SystemExit(f"{source} contains duplicate bom-ref values")

    dependencies = document.get("dependencies", [])
    if not isinstance(dependencies, list):
        raise SystemExit(f"{source} has an invalid dependencies array")
    for dependency in dependencies:
        if not isinstance(dependency, dict) or dependency.get("ref") not in known_refs:
            raise SystemExit(f"{source} has a dependency entry with an unknown ref")
        targets = dependency.get("dependsOn", [])
        if not isinstance(targets, list) or any(target not in known_refs for target in targets):
            raise SystemExit(f"{source} has a dependency edge with an unknown bom-ref")


def _record_bytes(members: dict[str, bytes], record_name: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    for name in sorted(members):
        if name == record_name:
            continue
        content = members[name]
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        writer.writerow((name, f"sha256={digest}", str(len(content))))
    writer.writerow((record_name, "", ""))
    return stream.getvalue().encode("utf-8")


def normalize_wheel(wheel_path: Path) -> None:
    if not wheel_path.is_file() or wheel_path.suffix != ".whl":
        raise SystemExit(f"wheel does not exist: {wheel_path}")

    with zipfile.ZipFile(wheel_path) as archive:
        infos = archive.infolist()
        members = {info.filename: archive.read(info.filename) for info in infos}

    sbom_names = sorted(
        name
        for name in members
        if ".dist-info/sboms/" in name and name.endswith(".json")
    )
    for name in sbom_names:
        try:
            document = json.loads(members[name])
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SystemExit(f"cannot parse wheel SBOM {name}: {exc}") from exc
        replacements: dict[str, str] = {}
        _collect_local_components(document, replacements)
        _rewrite_local_references(document, replacements)
        validate_sbom_document(document, name)
        members[name] = (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )

    record_names = [name for name in members if name.endswith(".dist-info/RECORD")]
    if len(record_names) != 1:
        raise SystemExit("wheel must contain exactly one dist-info/RECORD")
    record_name = record_names[0]
    members[record_name] = _record_bytes(members, record_name)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{wheel_path.name}.", suffix=".tmp", dir=wheel_path.parent
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    mode = stat.S_IMODE(wheel_path.stat().st_mode)
    try:
        with zipfile.ZipFile(temporary_path, "w") as output:
            with zipfile.ZipFile(wheel_path) as source:
                for info in source.infolist():
                    output.writestr(info, members[info.filename])
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, wheel_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path, help="wheel archive to normalize")
    args = parser.parse_args()
    normalize_wheel(args.wheel)
    print(f"normalized portable SBOM references in {args.wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
