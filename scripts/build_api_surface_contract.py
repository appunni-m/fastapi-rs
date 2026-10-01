#!/usr/bin/env python3
"""Generate the per-symbol source contract embedded in manifest.yaml."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.parity.api_contract import build_api_surface_contract
from scripts.parity.contract import ContractError, read_json, read_manifest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
START_MARKER = "# BEGIN GENERATED PER-SYMBOL API CONTRACT"
END_MARKER = "# END GENERATED PER-SYMBOL API CONTRACT"


def _read_manifest_text() -> tuple[str, dict[str, Any]]:
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    return text, read_manifest()


def _build(manifest: dict[str, Any]) -> dict[str, Any]:
    refs = manifest.get("source_artifacts")
    if not isinstance(refs, dict):
        raise ContractError("manifest source_artifacts is missing")

    def artifact(name: str) -> dict[str, Any]:
        ref = refs.get(name)
        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
            raise ContractError(f"manifest source artifact {name} is missing")
        return read_json(ROOT / ref["path"])

    return build_api_surface_contract(
        inventory=artifact("api_inventory"),
        atlas=artifact("compatibility_atlas"),
        backlog=artifact("fixture_backlog"),
        materialized_input_index=artifact("materialized_input_index"),
        runtime_core=artifact("runtime_api_surface_core"),
        runtime_standard=artifact("runtime_api_surface_standard"),
    )


def _replace_contract_block(text: str, contract: dict[str, Any]) -> str:
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start >= 0:
        if end < start:
            raise ContractError("manifest generated API contract block is unterminated")
        text = text[:start].rstrip()
    elif end >= 0:
        raise ContractError("manifest has an unmatched generated API contract end marker")
    serialized = yaml.safe_dump(
        {"api_surface_contract": contract},
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    ).rstrip()
    return f"{text.rstrip()}\n\n{START_MARKER}\n{serialized}\n{END_MARKER}\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the manifest is stale")
    args = parser.parse_args()
    try:
        text, manifest = _read_manifest_text()
        contract = _build(manifest)
        expected_text = _replace_contract_block(text, contract)
        if args.check:
            if expected_text != text:
                raise ContractError("manifest per-symbol API contract is stale; regenerate it")
        else:
            MANIFEST_PATH.write_text(expected_text, encoding="utf-8")
    except (ContractError, OSError, ValueError, yaml.YAMLError) as error:
        print(f"API surface contract generation failed: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "current" if args.check else "written",
                "manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
                "counts": contract["counts"],
            },
            sort_keys=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
