"""Probe a prepared parity profile without executing a workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.parity.target_worker import _target_identity
from scripts.parity.worker import _oracle_identity


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lane", choices=("oracle", "target"))
    parser.add_argument("--profile-json", required=True)
    parser.add_argument("--fastapi-source", type=Path)
    parser.add_argument("--starlette-source", type=Path)
    parser.add_argument("--target-source", type=Path)
    parser.add_argument("--starlette-rs-source", type=Path)
    parser.add_argument("--fault-injection-required", choices=("none", "true", "false"))
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        profile: Any = json.loads(args.profile_json)
        if not isinstance(profile, dict):
            raise ValueError("profile must be a JSON object")
        if args.lane == "oracle":
            if args.fastapi_source is None or args.starlette_source is None:
                raise ValueError("oracle identity requires FastAPI and Starlette source paths")
            identity = _oracle_identity(
                args.fastapi_source.resolve(), args.starlette_source.resolve(), profile
            )
        else:
            if args.target_source is None or args.starlette_rs_source is None:
                raise ValueError("target identity requires target and Starlette-RS source paths")
            fault_injection_required = (
                None
                if args.fault_injection_required in (None, "none")
                else args.fault_injection_required == "true"
            )
            identity = _target_identity(
                args.target_source.resolve(),
                args.starlette_rs_source.resolve(),
                target_profile=profile,
                fault_injection_required=fault_injection_required,
            )
    except Exception as exc:
        print(json.dumps({"identity_error": type(exc).__name__, "message": str(exc)}))
        return 2
    print(json.dumps(identity, ensure_ascii=False, allow_nan=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
