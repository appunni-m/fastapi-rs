"""Enforce FastAPI-RS-specific Rust source policies without compiling tests."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST_ROOTS = (ROOT / "fastapi-rs", ROOT / "fastapi-rs-py")
SUPPRESSION_ATTRIBUTE = re.compile(
    r"#(?P<inner>!)?\s*\[\s*(?P<kind>allow|expect)\s*\((?P<body>.*?)\)\s*\]",
    re.DOTALL,
)
UNIT_TEST_ATTRIBUTE = re.compile(
    r"#\s*\[\s*(?:test|tokio::test|async_std::test|actix_rt::test|rstest|test_case)\b"
)
UNIT_TEST_CFG = re.compile(r"#\s*\[\s*cfg(?:_attr)?\s*\([^]]*\btest\b[^]]*\)\s*\]")
UNIT_TEST_MODULE = re.compile(r"\bmod\s+tests\s*\{")
FORBIDDEN_SUPPRESSION = re.compile(
    r"\b(?:warnings|unsafe_code|unused|dead_code|clippy::(?:all|pedantic|nursery|restriction|cargo))\b"
)


def line_number(source: str, offset: int) -> int:
    """Return a one-based source line for a byte offset."""
    return source.count("\n", 0, offset) + 1


def preceding_comment(source: str, offset: int) -> str:
    """Return the nearest preceding nonblank line."""
    previous_lines = source[:offset].splitlines()
    for line in reversed(previous_lines):
        if line.strip():
            return line.strip()
    return ""


def main() -> int:
    errors: list[str] = []
    workspace_manifest = (ROOT / "Cargo.toml").read_text(encoding="utf-8")
    if not re.search(r'(?m)^\s*unsafe_code\s*=\s*"forbid"\s*(?:#.*)?$', workspace_manifest):
        errors.append('Cargo.toml must set workspace Rust lint `unsafe_code = "forbid"`')

    rust_files = sorted(
        path for rust_root in RUST_ROOTS for path in rust_root.rglob("*.rs") if path.is_file()
    )
    if not rust_files:
        errors.append("no FastAPI-RS Rust source files were found")

    for path in rust_files:
        relative_path = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        for pattern in (UNIT_TEST_ATTRIBUTE, UNIT_TEST_CFG, UNIT_TEST_MODULE):
            match = pattern.search(source)
            if match:
                errors.append(
                    f"{relative_path}:{line_number(source, match.start())}: "
                    "Rust unit-test source is forbidden; parity workflows are the test surface"
                )
                break

        for match in SUPPRESSION_ATTRIBUTE.finditer(source):
            body = match.group("body")
            line = line_number(source, match.start())
            if match.group("inner"):
                errors.append(
                    f"{relative_path}:{line}: crate-level lint suppressions are forbidden"
                )
                continue
            if FORBIDDEN_SUPPRESSION.search(body):
                errors.append(f"{relative_path}:{line}: blanket lint suppression is forbidden")
                continue
            if "reason" not in body or "lint-exception:" not in preceding_comment(
                source, match.start()
            ):
                errors.append(
                    f"{relative_path}:{line}: item-level lint exceptions need a preceding "
                    "`// lint-exception: ...` comment and a Rust `reason = ...`"
                )

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(
        f"Rust policy valid: {len(rust_files)} source files, no unit-test code, "
        "no blanket lint suppressions, and workspace unsafe code forbidden"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
