"""Build the source mapping index for independently authored parity workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scripts.atlas_documentation_example_review_mappings import (
    DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS,
)
from scripts.parity.contract import (
    API_WORKFLOW_SCHEMA_IDS,
    MATERIALIZED_INPUT_INDEX_SCHEMA_ID,
    ROOT,
    ContractError,
    load_workflow,
    read_json,
    sha256_file,
)
from scripts.parity.materialized import _api_probe_selectors, _source_selectors_for_case

INDEX_PATH = ROOT / "tests/fixtures/materialized-input-index.json"
INPUT_DIR = ROOT / "tests/fixtures/inputs/parity"
FASTAPI_SOURCE = (ROOT / "../fastapi").resolve()
MANIFEST_PATH = ROOT / "tests/fixtures/manifest.yaml"
INDEX_SCHEMA = MATERIALIZED_INPUT_INDEX_SCHEMA_ID


def _source_item_id(
    evidence: dict[str, Any], coverage_by_path: dict[str, list[dict[str, Any]]]
) -> str | None:
    expected_kind = {
        "upstream_test": "upstream_test_module",
        "upstream_documentation": "documented_feature_page",
        "upstream_documentation_example": "documented_python_example_source",
    }.get(evidence["kind"])
    if expected_kind is None:
        return None
    if evidence["kind"] == "upstream_documentation_example":
        source_path = evidence["path"]
        if (
            not source_path.startswith("docs_src/")
            or not source_path.endswith(".py")
            or source_path not in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS
        ):
            raise ContractError(
                "upstream_documentation_example must name a reviewed docs_src Python example: "
                f"{source_path}"
            )
    for row in coverage_by_path.get(evidence["path"], []):
        if row["kind"] == expected_kind:
            return row["id"]
    if evidence["kind"] == "upstream_documentation_example":
        raise ContractError(
            "reviewed documentation example is absent from the compatibility atlas: "
            f"{evidence['path']}"
        )
    return None


def _validate_reviewed_documentation_example_mappings(index: dict[str, Any]) -> None:
    workflows_by_id = {row["id"]: row for row in index["workflows"]}
    mappings_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for mapping in index["mappings"]:
        mappings_by_source[mapping["source_item_id"]].append(mapping)

    for source_path, review in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.items():
        source_id = "documented-example:" + source_path
        expected_by_recipe: dict[str, dict[str, set[str]]] = {}
        for workflow_case in review["workflow_cases"]:
            expected = expected_by_recipe.setdefault(
                workflow_case["recipe_path"], {"case_ids": set(), "selectors": set()}
            )
            expected["case_ids"].update(workflow_case["case_ids"])
            expected["selectors"].update(workflow_case["observation_selectors"])
        expected = sorted(
            (recipe_path, tuple(sorted(values["case_ids"])), tuple(sorted(values["selectors"])))
            for recipe_path, values in expected_by_recipe.items()
        )
        actual = sorted(
            (
                workflows_by_id[mapping["workflow_id"]]["recipe_path"],
                tuple(mapping["case_ids"]),
                tuple(mapping["observation_selectors"]),
            )
            for mapping in mappings_by_source.get(source_id, [])
        )
        if actual != expected:
            raise ContractError(
                "indexed documentation-example cases/selectors differ from reviewed mapping: "
                f"{source_path}; expected {expected!r}, found {actual!r}"
            )


def _scope(case_count: int, selectors: set[str]) -> str:
    selected = ", ".join(sorted(selectors))
    return (
        f"Partial independent sample across {case_count} case(s); observes {selected}. "
        "Unlisted functions, branches, configurations, and edge cases are not claimed."
    )


def _manifest_with_current_index(text: str, index: dict[str, Any]) -> str:
    index_bytes = (json.dumps(index, indent=2) + "\n").encode("utf-8")
    values = {
        "schema": index["schema"],
        "sha256": hashlib.sha256(index_bytes).hexdigest(),
        "schema_sha256": sha256_file(
            ROOT / "tests/fixtures/schemas/materialized-input-index.schema.json"
        ),
        "workflows": len(index["workflows"]),
        "cases": sum(len(row["case_ids"]) for row in index["workflows"]),
        "partial_source_mappings": sum(
            row["coverage_status"] == "partial" for row in index["mappings"]
        ),
    }
    lines = text.splitlines(keepends=True)
    try:
        start = next(i for i, line in enumerate(lines) if line == "  materialized_input_index:\n")
    except StopIteration as exc:
        raise ContractError("manifest has no materialized_input_index artifact block") from exc
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip() and not lines[i][0].isspace()),
        len(lines),
    )
    replacements = {
        "schema": re.compile(r"^    schema: .*(\n?)$"),
        "sha256": re.compile(r"^    sha256: .*(\n?)$"),
        "schema_sha256": re.compile(r"^    schema_sha256: .*(\n?)$"),
        "workflows": re.compile(r"^      workflows: .*(\n?)$"),
        "cases": re.compile(r"^      cases: .*(\n?)$"),
        "partial_source_mappings": re.compile(r"^      partial_source_mappings: .*(\n?)$"),
    }
    found: set[str] = set()
    for i in range(start + 1, end):
        for key, pattern in replacements.items():
            match = pattern.match(lines[i])
            if match:
                indent = "    " if key in {"schema", "sha256", "schema_sha256"} else "      "
                lines[i] = f"{indent}{key}: {values[key]}{match[1]}"
                found.add(key)
                break
    if found != set(values):
        missing = ", ".join(sorted(set(values) - found))
        raise ContractError(f"manifest materialized index block is missing fields: {missing}")
    return "".join(lines)


def build_index() -> dict[str, Any]:
    current = read_json(INDEX_PATH)
    atlas = read_json(ROOT / "tests/fixtures/compatibility-atlas.json")
    backlog = read_json(ROOT / "tests/fixtures/fixture-backlog.json")
    selector_catalog = read_json(ROOT / "tests/fixtures/observation-selectors.json")
    selector_support = {
        row["id"]: row["workflow_support"] for row in selector_catalog["selectors"] if "id" in row
    }
    supported_api_symbols = {
        row["id"] for row in atlas["api_candidates"] if row["classification"] == "supported"
    }
    coverage_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in atlas["coverage_matrix"]:
        coverage_by_path[row["source_path"]].append(row)
    backlog_by_source = {row["source_item_id"]: row for row in backlog["fixture_designs"]}

    # Derive the active index from disk every time. Carrying rows forward kept
    # stale workflow IDs after input files were renamed and made new source
    # citations invisible for cases that already had an index mapping.
    workflow_rows: dict[str, dict[str, Any]] = {}
    mappings: dict[tuple[str, str], dict[str, Any]] = {}

    for input_path in sorted(INPUT_DIR.glob("*.json")):
        # Workflow IDs follow the materialized-index slug schema even when an
        # older input filename uses underscores.
        workflow_id = input_path.stem.replace("_", "-")
        workflow, _, input_digest, workload_path = load_workflow(
            input_path, source_root=FASTAPI_SOURCE
        )
        api_definitions = []
        api_probes = []
        for case in workflow["cases"]:
            public_symbol_ids: set[str] = set()
            case_probes = case.get("probes", [])
            for probe in case_probes:
                for key in ("public_callable", "public_attribute"):
                    reference = probe.get(key)
                    if isinstance(reference, dict):
                        public_symbol_ids.add(f"{reference['module']}.{reference['attribute']}")
            if workflow["schema"] in API_WORKFLOW_SCHEMA_IDS:
                for probe in case_probes:
                    reference = probe.get("public_callable", probe.get("public_attribute"))
                    symbol_id = f"{reference['module']}.{reference['attribute']}"
                    if symbol_id not in supported_api_symbols:
                        raise ContractError(
                            "direct API workflow probe is outside the supported source API "
                            f"contract: {case['case_id']} -> {symbol_id}"
                        )
                    api_probes.append(
                        {
                            "case_id": case["case_id"],
                            "probe_id": probe["probe_id"],
                            "symbol_id": symbol_id,
                            "probe_kind": (
                                "callable" if "public_callable" in probe else "attribute"
                            ),
                            "observation_selectors": _api_probe_selectors(probe, selector_support),
                        }
                    )
            for evidence in case["source_evidence"]:
                if evidence["kind"] != "upstream_api_definition":
                    continue
                if evidence["symbol_id"] not in public_symbol_ids:
                    raise ContractError(
                        "upstream API definition evidence must bind to a probed public symbol: "
                        f"{case['case_id']} -> {evidence['symbol_id']}"
                    )
                api_definitions.append(
                    {
                        "case_id": case["case_id"],
                        "symbol_id": evidence["symbol_id"],
                        "path": evidence["path"],
                        "sha256": evidence["sha256"],
                    }
                )
        input_rel_path = input_path.relative_to(ROOT).as_posix()
        if (
            workflow_id in workflow_rows
            and workflow_rows[workflow_id]["input_path"] != input_rel_path
        ):
            raise ContractError(f"workflow ID is shared by different files: {workflow_id}")
        workflow_ref: dict[str, Any] = {
            "id": workflow_id,
            "input_path": input_path.relative_to(ROOT).as_posix(),
            "input_sha256": input_digest,
            "recipe_path": (
                Path("tests/fixtures/input-recipes/parity") / f"{input_path.stem}.yaml"
            ).as_posix(),
            "recipe_sha256": sha256_file(
                ROOT / "tests/fixtures/input-recipes/parity" / f"{input_path.stem}.yaml"
            ),
            "workload_path": workload_path.relative_to(ROOT).as_posix(),
            "workload_sha256": sha256_file(workload_path),
            "case_ids": [case["case_id"] for case in workflow["cases"]],
        }
        if "oracle_profile_extension" in workflow:
            workflow_ref["oracle_profile_extension"] = workflow["oracle_profile_extension"]
        if api_definitions:
            workflow_ref["api_definitions"] = sorted(
                api_definitions,
                key=lambda row: (row["case_id"], row["symbol_id"], row["path"]),
            )
        if api_probes:
            workflow_ref["api_probes"] = sorted(
                api_probes,
                key=lambda row: (row["case_id"], row["probe_id"], row["symbol_id"]),
            )
        workflow_rows[workflow_id] = workflow_ref

        new_mapping_cases: dict[str, dict[str, Any]] = {}
        reviewed_doc_required_selectors: dict[str, set[str]] = {}
        reviewed_doc_case_selectors = {
            (source_path, case_id): set(workflow_case["observation_selectors"])
            for source_path, review in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.items()
            for workflow_case in review["workflow_cases"]
            if workflow_case["recipe_path"] == workflow_ref["recipe_path"]
            for case_id in workflow_case["case_ids"]
        }
        for source_path, review in DOCUMENTATION_EXAMPLE_REVIEW_MAPPINGS.items():
            for workflow_case in review["workflow_cases"]:
                if workflow_case["recipe_path"] == workflow_ref["recipe_path"]:
                    reviewed_doc_required_selectors.setdefault(source_path, set()).update(
                        workflow_case["observation_selectors"]
                    )
        reviewed_doc_observed_selectors: dict[str, set[str]] = {}
        for case in workflow["cases"]:
            candidates: list[tuple[str, set[str]]] = []
            for evidence in case["source_evidence"]:
                source_id = _source_item_id(evidence, coverage_by_path)
                if source_id is None:
                    continue
                coverage = next(row for row in atlas["coverage_matrix"] if row["id"] == source_id)
                source_selectors = set(coverage["observation_selectors"])
                if evidence["kind"] == "upstream_documentation_example":
                    source_selectors = set(
                        coverage["mapping_evidence"].get("example_observation_selectors", [])
                    )
                usable = _source_selectors_for_case(
                    case,
                    source_selectors,
                    workflow_schema=workflow["schema"],
                )
                usable = {
                    selector
                    for selector in usable
                    if selector_support.get(selector) in {"supported", "partial"}
                }
                if evidence["kind"] == "upstream_documentation_example":
                    reviewed = reviewed_doc_case_selectors.get((evidence["path"], case["case_id"]))
                    if reviewed is None:
                        raise ContractError(
                            "documentation example source evidence has no reviewed case mapping: "
                            f"{evidence['path']} -> {case['case_id']}"
                        )
                    usable &= reviewed
                    reviewed_doc_observed_selectors.setdefault(evidence["path"], set()).update(
                        usable
                    )
                if usable and source_id in backlog_by_source:
                    candidates.append((source_id, usable))
            if not candidates:
                if any(
                    evidence.get("kind") == "upstream_api_definition"
                    for evidence in case["source_evidence"]
                ):
                    continue
                raise ContractError(
                    "workflow case has no source row with a supported observed selector: "
                    f"{case['case_id']}"
                )
            for source_id, usable in candidates:
                mapping = new_mapping_cases.setdefault(
                    source_id,
                    {"case_ids": set(), "observation_selectors": set()},
                )
                mapping["case_ids"].add(case["case_id"])
                mapping["observation_selectors"].update(usable)

        for source_path, required in reviewed_doc_required_selectors.items():
            missing = required - reviewed_doc_observed_selectors.get(source_path, set())
            if missing:
                raise ContractError(
                    "reviewed documentation-example selectors are not observed by the mapped "
                    f"workflow cases: {source_path}: {', '.join(sorted(missing))}"
                )

        for source_id, detail in new_mapping_cases.items():
            old = mappings.get((source_id, workflow_id))
            all_case_ids = set(detail["case_ids"])
            all_selectors = set(detail["observation_selectors"])
            if old:
                all_case_ids.update(old["case_ids"])
                all_selectors.update(old["observation_selectors"])
            mappings[(source_id, workflow_id)] = {
                "source_item_id": source_id,
                "fixture_id": backlog_by_source[source_id]["id"],
                "workflow_id": workflow_id,
                "coverage_status": "partial",
                "coverage_scope": _scope(len(all_case_ids), all_selectors),
                "case_ids": sorted(all_case_ids),
                "observation_selectors": sorted(all_selectors),
            }

    generated = {
        "schema": INDEX_SCHEMA,
        "authority": current["authority"],
        "workflows": sorted(workflow_rows.values(), key=lambda row: row["id"]),
        "mappings": sorted(
            mappings.values(), key=lambda row: (row["workflow_id"], row["source_item_id"])
        ),
    }
    _validate_reviewed_documentation_example_mappings(generated)
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the index does not already match the current workflow inputs",
    )
    args = parser.parse_args()
    current = read_json(INDEX_PATH)
    generated = build_index()
    manifest_text = MANIFEST_PATH.read_text(encoding="utf-8")
    expected_manifest = _manifest_with_current_index(manifest_text, generated)
    if args.check:
        if generated != current:
            raise ContractError("materialized input index is stale; rebuild without --check")
        if expected_manifest != manifest_text:
            raise ContractError("manifest materialized index digest or counts are stale")
        print(
            f"materialized input index is current: {len(generated['workflows'])} workflows, "
            f"{sum(len(row['case_ids']) for row in generated['workflows'])} cases, "
            f"{len(generated['mappings'])} source mappings"
        )
        return 0
    INDEX_PATH.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(
        _manifest_with_current_index(MANIFEST_PATH.read_text(encoding="utf-8"), generated),
        encoding="utf-8",
    )
    print(
        f"wrote {INDEX_PATH.relative_to(ROOT)}: {len(generated['workflows'])} workflows, "
        f"{sum(len(row['case_ids']) for row in generated['workflows'])} cases, "
        f"{len(generated['mappings'])} source mappings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
