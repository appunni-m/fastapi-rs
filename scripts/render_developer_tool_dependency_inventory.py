#!/usr/bin/env python3
"""Check or render the hash-locked developer-tool dependency inventory."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "requirements" / "developer-tools-inventory.toml"
DEV_REQUIREMENTS = ROOT / "requirements-dev.txt"
NAME_VERSION = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)\s*$")
LOCK_PACKAGE = re.compile(
    r"^([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s;\\]+)"
    r"(?:\s*;\s*([^\\]+?))?(?:\s+\\)?$"
)
LOCK_HASH = re.compile(r"^--hash=sha256:([0-9a-f]{64})$")
UV_VERSION = re.compile(r"^uv\s+([^\s]+)")


@dataclass
class LockedPackage:
    name: str
    version: str
    marker: str | None = None
    hashes: set[str] = field(default_factory=set)
    parents: set[str] = field(default_factory=set)
    direct_input: str | None = None

    @property
    def is_direct(self) -> bool:
        return self.direct_input is not None


def canonical_name(name: str) -> str:
    """Normalize Python distribution names according to PEP 503."""
    return re.sub(r"[-_.]+", "-", name).lower()


def read_exact_pins(path: Path) -> dict[str, tuple[str, str]]:
    pins: dict[str, tuple[str, str]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = NAME_VERSION.fullmatch(stripped)
        if match is None:
            raise ValueError(
                f"{path.relative_to(ROOT)}:{line_number}: expected exact pin, got {stripped!r}"
            )
        name, version = match.groups()
        normalized = canonical_name(name)
        if normalized in pins:
            raise ValueError(f"{path.relative_to(ROOT)} repeats normalized package {name!r}")
        pins[normalized] = (name, version)
    if not pins:
        raise ValueError(f"{path.relative_to(ROOT)} contains no exact pins")
    return pins


def read_lock(path: Path) -> tuple[dict[str, LockedPackage], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    packages: dict[str, LockedPackage] = {}
    package: LockedPackage | None = None
    in_parent_block = False

    def finish_package() -> None:
        nonlocal package
        if package is None:
            return
        normalized = canonical_name(package.name)
        if normalized in packages:
            raise ValueError(f"{path.relative_to(ROOT)} repeats package {package.name!r}")
        if not package.hashes:
            raise ValueError(f"{path.relative_to(ROOT)} has no SHA-256 hashes for {package.name}")
        packages[normalized] = package
        package = None

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            in_parent_block = False
            continue
        match = LOCK_PACKAGE.fullmatch(stripped)
        if match is not None:
            finish_package()
            name, version, marker = match.groups()
            package = LockedPackage(name=name, version=version, marker=marker)
            in_parent_block = False
            continue
        hash_text = stripped.removesuffix("\\").rstrip()
        hash_match = LOCK_HASH.fullmatch(hash_text)
        if hash_match is not None and package is not None:
            package.hashes.add(hash_match.group(1))
            continue
        if stripped.startswith("# via ") and package is not None:
            via_target = stripped.removeprefix("# via ").strip()
            if via_target.startswith("-r "):
                package.direct_input = via_target
            elif via_target:
                package.parents.add(via_target)
            in_parent_block = False
            continue
        if stripped == "# via" and package is not None:
            in_parent_block = True
            continue
        if line.startswith("    #   ") and package is not None and in_parent_block:
            package.parents.add(stripped.removeprefix("#").strip())
            continue
        if stripped.startswith("#"):
            in_parent_block = False
            continue
        raise ValueError(
            f"{path.relative_to(ROOT)}:{line_number}: unsupported lock line {stripped!r}"
        )
    finish_package()
    if not packages:
        raise ValueError(f"{path.relative_to(ROOT)} contains no package entries")
    return packages, lines


def load_profile() -> dict[str, Any]:
    profile = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    required_fields = {
        "profile",
        "python",
        "input",
        "lock",
        "output",
        "exclude_newer",
        "resolver_version",
        "packages",
    }
    missing = required_fields - profile.keys()
    if missing:
        raise ValueError(f"{PROFILE_PATH.relative_to(ROOT)} is missing fields: {sorted(missing)}")
    return profile


def validate_requirements_aggregate(profile: dict[str, Any]) -> None:
    expected = {
        f"-r {profile['input']}",
        "-r requirements/build-tools-cpython-3.12.13.in",
    }
    actual = {
        line.strip()
        for line in DEV_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if actual != expected:
        raise ValueError(
            "requirements-dev.txt must aggregate the separate developer and build-tool inputs: "
            f"expected={sorted(expected)}, actual={sorted(actual)}"
        )


def validate_profile(
    profile: dict[str, Any],
) -> tuple[dict[str, tuple[str, str]], dict[str, LockedPackage]]:
    input_path = ROOT / profile["input"]
    lock_path = ROOT / profile["lock"]
    output_path = ROOT / profile["output"]
    input_pins = read_exact_pins(input_path)
    validate_requirements_aggregate(profile)
    lock_packages, lock_lines = read_lock(lock_path)
    reviewed = {canonical_name(record["name"]): record for record in profile["packages"]}
    if len(reviewed) != len(profile["packages"]):
        raise ValueError("developer-tool inventory repeats a normalized package name")
    if set(reviewed) != set(lock_packages):
        raise ValueError(
            "reviewed inventory and hash lock package sets differ: "
            f"metadata_only={sorted(set(reviewed) - set(lock_packages))}, "
            f"lock_only={sorted(set(lock_packages) - set(reviewed))}"
        )
    if set(input_pins) != {name for name, package in lock_packages.items() if package.is_direct}:
        raise ValueError("direct lock entries do not match the developer-tool input pins")
    for normalized, (name, version) in input_pins.items():
        package = lock_packages[normalized]
        if package.version != version:
            raise ValueError(f"{name} is pinned to {version} but lock resolves {package.version}")
        if package.direct_input != f"-r {profile['input']}":
            raise ValueError(
                f"{name} does not identify the reviewed developer-tool input in the lock"
            )

    allowed_roles = {"dev", "build"}
    for normalized, record in reviewed.items():
        package = lock_packages[normalized]
        roles = record.get("roles")
        if not isinstance(roles, list) or not roles or not set(roles) <= allowed_roles:
            raise ValueError(f"{record['name']} must declare one or more dev/build roles")
        for key in ("purpose", "implementation", "license"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                raise ValueError(f"{record['name']} must declare {key}")
        if package.is_direct and package.parents:
            raise ValueError(f"direct lock entry {package.name} also declares transitive parents")
        if not package.is_direct and not package.parents:
            raise ValueError(f"transitive lock entry {package.name} has no parent evidence")
        unknown_parents = package.parents - set(lock_packages)
        if unknown_parents:
            raise ValueError(
                f"{package.name} refers to unknown lock parents: {sorted(unknown_parents)}"
            )

    expected_header = (
        "#    uv pip compile --universal --python-version 3.12 --only-binary :all: "
        "--generate-hashes --exclude-newer "
        f"{profile['exclude_newer']} --output-file {profile['lock']} {profile['input']}"
    )
    if expected_header not in lock_lines[:2]:
        raise ValueError("developer-tool lock header does not record the reviewed resolver command")
    if not output_path.parent.is_dir():
        raise ValueError(f"inventory output directory is missing: {output_path.parent}")
    return input_pins, lock_packages


def markdown_cell(value: object) -> str:
    return " ".join(str(value or "—").split()).replace("|", "\\|")


def render_inventory(profile: dict[str, Any], lock_packages: dict[str, LockedPackage]) -> str:
    output: list[str] = [
        "# Developer-tool dependency profile",
        "",
        f"This inventory records the recursive hash-locked {profile['profile']} profile for "
        f"{profile['python']}. Its direct pins come from "
        f"[`{profile['input']}`](../{profile['input']}); "
        f"the generated lock is [`{profile['lock']}`](../{profile['lock']}).",
        "",
        "These packages are developer/build tools and their transitive support libraries. They "
        "are separate from the FastAPI-RS target runtime lock and are not product runtime "
        "dependencies. Maturin remains in the separate, hash-locked build-tools profile.",
        "",
        "Regenerate the lock and this inventory with `make developer-tools-inventory-update`; "
        "check the reviewed data without network access with "
        "`make developer-tools-inventory-check`. "
        "Install the locked tool environment with `make developer-tools-prepare`.",
        "",
        f"The uv resolver is pinned at {profile['resolver_version']}; updates exclude releases "
        f"published after {profile['exclude_newer']}. Only binary distributions are admitted, "
        "and every eligible artifact is SHA-256 hashed in the lock.",
        "",
        "| Package | Locked version | Role | Marker | Resolved through | Purpose | "
        "Python/native implementation | License | Hashes |",
        "|---|---:|---|---|---|---|---|---|---:|",
    ]
    reviewed = {canonical_name(record["name"]): record for record in profile["packages"]}
    for normalized in sorted(lock_packages):
        package = lock_packages[normalized]
        record = reviewed[normalized]
        name = record["name"]
        package_link = f"https://pypi.org/project/{normalized}/{package.version}/"
        license_link = f"https://pypi.org/pypi/{normalized}/{package.version}/json"
        roles = ", ".join(record["roles"])
        parents = "direct input" if package.is_direct else ", ".join(sorted(package.parents))
        output.append(
            "| "
            + " | ".join(
                (
                    f"[{name}]({package_link})",
                    package.version,
                    markdown_cell(roles),
                    markdown_cell(package.marker),
                    markdown_cell(parents),
                    markdown_cell(record["purpose"]),
                    markdown_cell(record["implementation"]),
                    f"[{markdown_cell(record['license'])}]({license_link})",
                    str(len(package.hashes)),
                )
            )
            + " |"
        )
    output.extend(
        [
            "",
            "Transitive parent paths are taken from uv's `# via` records in the lock. The "
            "Python marker on `typing-extensions` keeps that conditional package in the "
            "universal CPython 3.12 lock; the preparation command verifies "
            "the patch-level interpreter.",
            "",
        ]
    )
    return "\n".join(output)


def check_uv_version(uv: str, expected: str) -> None:
    result = subprocess.run([uv, "--version"], check=False, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"{uv} --version failed")
    match = UV_VERSION.match(result.stdout.strip())
    if match is None or match.group(1) != expected:
        actual = result.stdout.strip() or "(no version output)"
        raise RuntimeError(f"developer-tool update requires uv {expected}; found {actual}")


def update_lock(profile: dict[str, Any], uv: str) -> None:
    input_pins = read_exact_pins(ROOT / profile["input"])
    uv_pin = input_pins.get("uv")
    if uv_pin is None or uv_pin[1] != profile["resolver_version"]:
        raise ValueError(
            "uv input pin must match resolver_version in developer-tools-inventory.toml"
        )
    check_uv_version(uv, profile["resolver_version"])
    command = [
        uv,
        "pip",
        "compile",
        "--universal",
        "--python-version",
        "3.12",
        "--only-binary",
        ":all:",
        "--generate-hashes",
        "--exclude-newer",
        profile["exclude_newer"],
        "--output-file",
        profile["lock"],
        profile["input"],
    ]
    result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "uv pip compile failed")
    if result.stderr.strip():
        print(result.stderr.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="check lock and generated inventory")
    mode.add_argument(
        "--update", action="store_true", help="resolve lock and update generated inventory"
    )
    parser.add_argument("--uv", default="uv", help="uv executable used for updates (default: uv)")
    args = parser.parse_args()

    try:
        profile = load_profile()
        if args.update:
            update_lock(profile, args.uv)
        _, lock_packages = validate_profile(profile)
        output_path = ROOT / profile["output"]
        rendered = render_inventory(profile, lock_packages)
        if args.update:
            output_path.write_text(rendered, encoding="utf-8")
            print(
                f"Updated {profile['lock']} and {profile['output']} ({len(lock_packages)} packages)"
            )
            return 0
        current = output_path.read_text(encoding="utf-8")
        if current != rendered:
            print(
                f"{profile['output']} is stale; run make developer-tools-inventory-update",
                file=sys.stderr,
            )
            return 1
        print(f"Developer-tool inventory is current ({len(lock_packages)} packages)")
    except (OSError, tomllib.TOMLDecodeError, ValueError, RuntimeError) as exc:
        print(f"developer-tool dependency inventory error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
