"""Strict loading and reference validation for Python/ASGI workflows."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from yaml import SafeLoader

from scripts.parity.fault_contracts import (
    HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_CONTRACT,
    HTTP_FRONTEND_LOOKUP_OS_ERROR_CONTRACT,
    HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_CONTRACT,
    HTTP_FRONTEND_LOOKUP_VALUE_ERROR_CONTRACT,
    HTTP_REQUEST_FORM_PARSE_CONTRACT,
    HTTP_REQUEST_JSON_DECODE_CONTRACT,
    OPENAPI_CACHE_PUBLISH_RETRY_CONTRACT,
    FaultContractError,
    verification_mode,
)
from scripts.parity.schema_ids import MATERIALIZED_INPUT_INDEX_SCHEMA_ID

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_SCHEMA = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v2.schema.json"
WORKFLOW_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v3.schema.json"
WORKFLOW_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v4.schema.json"
WORKFLOW_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v5.schema.json"
WORKFLOW_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v6.schema.json"
WORKFLOW_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v7.schema.json"
WORKFLOW_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v8.schema.json"
WORKFLOW_SCHEMA_V9 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v9.schema.json"
WORKFLOW_SCHEMA_V10 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v10.schema.json"
WORKFLOW_SCHEMA_V11 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v11.schema.json"
WORKFLOW_SCHEMA_V12 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v12.schema.json"
WORKFLOW_SCHEMA_V13 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v13.schema.json"
WORKFLOW_SCHEMA_V14 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v14.schema.json"
WORKFLOW_SCHEMA_V15 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v15.schema.json"
WORKFLOW_SCHEMA_V16 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v16.schema.json"
WORKFLOW_SCHEMA_V17 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-v17.schema.json"
PROCESS_WORKFLOW_SCHEMA = ROOT / "tests/fixtures/schemas/python-process-workflow.schema.json"
PROCESS_WORKFLOW_SCHEMA_V2 = ROOT / "tests/fixtures/schemas/python-process-workflow-v2.schema.json"
API_WORKFLOW_SCHEMA = ROOT / "tests/fixtures/schemas/python-api-workflow.schema.json"
API_WORKFLOW_SCHEMA_V2 = ROOT / "tests/fixtures/schemas/python-api-workflow-v2.schema.json"
API_WORKFLOW_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-api-workflow-v3.schema.json"
API_WORKFLOW_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-api-workflow-v4.schema.json"
API_WORKFLOW_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-api-workflow-v5.schema.json"
API_WORKFLOW_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-api-workflow-v6.schema.json"
API_WORKFLOW_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-api-workflow-v7.schema.json"
API_WORKFLOW_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-api-workflow-v8.schema.json"
API_WORKFLOW_SCHEMA_V9 = ROOT / "tests/fixtures/schemas/python-api-workflow-v9.schema.json"
API_WORKFLOW_SCHEMA_V10 = ROOT / "tests/fixtures/schemas/python-api-workflow-v10.schema.json"
API_WORKFLOW_SCHEMA_V11 = ROOT / "tests/fixtures/schemas/python-api-workflow-v11.schema.json"
API_WORKFLOW_SCHEMA_V12 = ROOT / "tests/fixtures/schemas/python-api-workflow-v12.schema.json"
API_WORKFLOW_SCHEMA_V13 = ROOT / "tests/fixtures/schemas/python-api-workflow-v13.schema.json"
API_RESULT_SCHEMA = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v2.schema.json"
API_RESULT_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v3.schema.json"
API_RESULT_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v4.schema.json"
API_RESULT_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v5.schema.json"
API_RESULT_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v6.schema.json"
API_RESULT_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v7.schema.json"
API_RESULT_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v8.schema.json"
API_RESULT_SCHEMA_V9 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v9.schema.json"
API_RESULT_SCHEMA_V10 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v10.schema.json"
API_RESULT_SCHEMA_V11 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v11.schema.json"
API_RESULT_SCHEMA_V12 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v12.schema.json"
API_RESULT_SCHEMA_V13 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v13.schema.json"
API_RESULT_SCHEMA_V14 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v14.schema.json"
API_RESULT_SCHEMA_V15 = ROOT / "tests/fixtures/schemas/python-api-workflow-result-v15.schema.json"
API_COMPARISON_SCHEMA = ROOT / "tests/fixtures/schemas/python-api-comparison-v1.schema.json"
API_COMPARISON_SCHEMA_V2 = ROOT / "tests/fixtures/schemas/python-api-comparison-v2.schema.json"
API_COMPARISON_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-api-comparison-v3.schema.json"
API_COMPARISON_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-api-comparison-v4.schema.json"
API_COMPARISON_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-api-comparison-v5.schema.json"
API_COMPARISON_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-api-comparison-v6.schema.json"
API_COMPARISON_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-api-comparison-v7.schema.json"
API_COMPARISON_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-api-comparison-v8.schema.json"
API_COMPARISON_SCHEMA_V9 = ROOT / "tests/fixtures/schemas/python-api-comparison-v9.schema.json"
API_COMPARISON_SCHEMA_V10 = ROOT / "tests/fixtures/schemas/python-api-comparison-v10.schema.json"
API_COMPARISON_SCHEMA_V11 = ROOT / "tests/fixtures/schemas/python-api-comparison-v11.schema.json"
API_COMPARISON_SCHEMA_V12 = ROOT / "tests/fixtures/schemas/python-api-comparison-v12.schema.json"
API_COMPARISON_SCHEMA_V13 = ROOT / "tests/fixtures/schemas/python-api-comparison-v13.schema.json"
RESULT_SCHEMA = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v2.schema.json"
RESULT_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v3.schema.json"
RESULT_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v4.schema.json"
RESULT_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v5.schema.json"
RESULT_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v6.schema.json"
RESULT_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v7.schema.json"
RESULT_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v8.schema.json"
RESULT_SCHEMA_V9 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v9.schema.json"
RESULT_SCHEMA_V10 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v10.schema.json"
RESULT_SCHEMA_V11 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v11.schema.json"
RESULT_SCHEMA_V12 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v12.schema.json"
RESULT_SCHEMA_V13 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v13.schema.json"
RESULT_SCHEMA_V14 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v14.schema.json"
RESULT_SCHEMA_V15 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v15.schema.json"
RESULT_SCHEMA_V16 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v16.schema.json"
RESULT_SCHEMA_V17 = ROOT / "tests/fixtures/schemas/python-asgi-workflow-result-v17.schema.json"
COMPARISON_SCHEMA = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v2.schema.json"
COMPARISON_SCHEMA_V3 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v3.schema.json"
COMPARISON_SCHEMA_V4 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v4.schema.json"
COMPARISON_SCHEMA_V5 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v5.schema.json"
COMPARISON_SCHEMA_V6 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v6.schema.json"
COMPARISON_SCHEMA_V7 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v7.schema.json"
COMPARISON_SCHEMA_V8 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v8.schema.json"
COMPARISON_SCHEMA_V9 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v9.schema.json"
COMPARISON_SCHEMA_V10 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v10.schema.json"
COMPARISON_SCHEMA_V11 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v11.schema.json"
COMPARISON_SCHEMA_V12 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v12.schema.json"
COMPARISON_SCHEMA_V13 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v13.schema.json"
COMPARISON_SCHEMA_V14 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v14.schema.json"
COMPARISON_SCHEMA_V15 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v15.schema.json"
COMPARISON_SCHEMA_V16 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v16.schema.json"
COMPARISON_SCHEMA_V17 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v17.schema.json"
COMPARISON_SCHEMA_V18 = ROOT / "tests/fixtures/schemas/python-asgi-comparison-v18.schema.json"
WORKFLOW_SCHEMA_ID = "fastapi-rs/python-asgi-workflow@2"
WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-asgi-workflow@3"
WORKFLOW_SCHEMA_V4_ID = "fastapi-rs/python-asgi-workflow@4"
WORKFLOW_SCHEMA_V5_ID = "fastapi-rs/python-asgi-workflow@5"
WORKFLOW_SCHEMA_V6_ID = "fastapi-rs/python-asgi-workflow@6"
WORKFLOW_SCHEMA_V7_ID = "fastapi-rs/python-asgi-workflow@7"
WORKFLOW_SCHEMA_V8_ID = "fastapi-rs/python-asgi-workflow@8"
WORKFLOW_SCHEMA_V9_ID = "fastapi-rs/python-asgi-workflow@9"
WORKFLOW_SCHEMA_V10_ID = "fastapi-rs/python-asgi-workflow@10"
WORKFLOW_SCHEMA_V11_ID = "fastapi-rs/python-asgi-workflow@11"
WORKFLOW_SCHEMA_V12_ID = "fastapi-rs/python-asgi-workflow@12"
WORKFLOW_SCHEMA_V13_ID = "fastapi-rs/python-asgi-workflow@13"
WORKFLOW_SCHEMA_V14_ID = "fastapi-rs/python-asgi-workflow@14"
WORKFLOW_SCHEMA_V15_ID = "fastapi-rs/python-asgi-workflow@15"
WORKFLOW_SCHEMA_V16_ID = "fastapi-rs/python-asgi-workflow@16"
WORKFLOW_SCHEMA_V17_ID = "fastapi-rs/python-asgi-workflow@17"
PROCESS_WORKFLOW_SCHEMA_ID = "fastapi-rs/python-process-workflow@1"
PROCESS_WORKFLOW_SCHEMA_V2_ID = "fastapi-rs/python-process-workflow@2"
PROCESS_WORKFLOW_SCHEMA_IDS = frozenset({PROCESS_WORKFLOW_SCHEMA_ID, PROCESS_WORKFLOW_SCHEMA_V2_ID})
PROCESS_RESULT_SCHEMA_ID = "fastapi-rs/python-process-workflow-result@1"
PROCESS_RESULT_SCHEMA_V2_ID = "fastapi-rs/python-process-workflow-result@2"
PROCESS_COMPARISON_SCHEMA_ID = "fastapi-rs/python-process-comparison@1"
PROCESS_COMPARISON_SCHEMA_V2_ID = "fastapi-rs/python-process-comparison@2"
FIXTURE_BACKLOG_SCHEMA_ID = "fastapi-rs/fixture-backlog@2"
API_WORKFLOW_SCHEMA_ID = "fastapi-rs/python-api-workflow@1"
API_WORKFLOW_SCHEMA_V2_ID = "fastapi-rs/python-api-workflow@2"
API_WORKFLOW_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow@3"
API_WORKFLOW_SCHEMA_V4_ID = "fastapi-rs/python-api-workflow@4"
API_WORKFLOW_SCHEMA_V5_ID = "fastapi-rs/python-api-workflow@5"
API_WORKFLOW_SCHEMA_V6_ID = "fastapi-rs/python-api-workflow@6"
API_WORKFLOW_SCHEMA_V7_ID = "fastapi-rs/python-api-workflow@7"
API_WORKFLOW_SCHEMA_V8_ID = "fastapi-rs/python-api-workflow@8"
API_WORKFLOW_SCHEMA_V9_ID = "fastapi-rs/python-api-workflow@9"
API_WORKFLOW_SCHEMA_V10_ID = "fastapi-rs/python-api-workflow@10"
API_WORKFLOW_SCHEMA_V11_ID = "fastapi-rs/python-api-workflow@11"
API_WORKFLOW_SCHEMA_V12_ID = "fastapi-rs/python-api-workflow@12"
API_WORKFLOW_SCHEMA_V13_ID = "fastapi-rs/python-api-workflow@13"
API_RESULT_SCHEMA_ID = "fastapi-rs/python-api-workflow-result@2"
API_RESULT_SCHEMA_V3_ID = "fastapi-rs/python-api-workflow-result@3"
API_RESULT_SCHEMA_V4_ID = "fastapi-rs/python-api-workflow-result@4"
API_RESULT_SCHEMA_V5_ID = "fastapi-rs/python-api-workflow-result@5"
API_RESULT_SCHEMA_V6_ID = "fastapi-rs/python-api-workflow-result@6"
API_RESULT_SCHEMA_V7_ID = "fastapi-rs/python-api-workflow-result@7"
API_RESULT_SCHEMA_V8_ID = "fastapi-rs/python-api-workflow-result@8"
API_RESULT_SCHEMA_V9_ID = "fastapi-rs/python-api-workflow-result@9"
API_RESULT_SCHEMA_V10_ID = "fastapi-rs/python-api-workflow-result@10"
API_RESULT_SCHEMA_V11_ID = "fastapi-rs/python-api-workflow-result@11"
API_RESULT_SCHEMA_V12_ID = "fastapi-rs/python-api-workflow-result@12"
API_RESULT_SCHEMA_V13_ID = "fastapi-rs/python-api-workflow-result@13"
API_RESULT_SCHEMA_V14_ID = "fastapi-rs/python-api-workflow-result@14"
API_RESULT_SCHEMA_V15_ID = "fastapi-rs/python-api-workflow-result@15"
API_COMPARISON_SCHEMA_ID = "fastapi-rs/python-api-comparison@1"
API_COMPARISON_SCHEMA_V2_ID = "fastapi-rs/python-api-comparison@2"
API_COMPARISON_SCHEMA_V3_ID = "fastapi-rs/python-api-comparison@3"
API_COMPARISON_SCHEMA_V4_ID = "fastapi-rs/python-api-comparison@4"
API_COMPARISON_SCHEMA_V5_ID = "fastapi-rs/python-api-comparison@5"
API_COMPARISON_SCHEMA_V6_ID = "fastapi-rs/python-api-comparison@6"
API_COMPARISON_SCHEMA_V7_ID = "fastapi-rs/python-api-comparison@7"
API_COMPARISON_SCHEMA_V8_ID = "fastapi-rs/python-api-comparison@8"
API_COMPARISON_SCHEMA_V9_ID = "fastapi-rs/python-api-comparison@9"
API_COMPARISON_SCHEMA_V10_ID = "fastapi-rs/python-api-comparison@10"
API_COMPARISON_SCHEMA_V11_ID = "fastapi-rs/python-api-comparison@11"
API_COMPARISON_SCHEMA_V12_ID = "fastapi-rs/python-api-comparison@12"
API_COMPARISON_SCHEMA_V13_ID = "fastapi-rs/python-api-comparison@13"
API_WORKFLOW_SCHEMA_IDS = frozenset(
    {
        API_WORKFLOW_SCHEMA_ID,
        API_WORKFLOW_SCHEMA_V2_ID,
        API_WORKFLOW_SCHEMA_V3_ID,
        API_WORKFLOW_SCHEMA_V4_ID,
        API_WORKFLOW_SCHEMA_V5_ID,
        API_WORKFLOW_SCHEMA_V6_ID,
        API_WORKFLOW_SCHEMA_V7_ID,
        API_WORKFLOW_SCHEMA_V8_ID,
        API_WORKFLOW_SCHEMA_V9_ID,
        API_WORKFLOW_SCHEMA_V10_ID,
        API_WORKFLOW_SCHEMA_V11_ID,
        API_WORKFLOW_SCHEMA_V12_ID,
        API_WORKFLOW_SCHEMA_V13_ID,
    }
)
API_RESULT_SCHEMA_IDS_BY_WORKFLOW = {
    API_WORKFLOW_SCHEMA_ID: API_RESULT_SCHEMA_ID,
    API_WORKFLOW_SCHEMA_V2_ID: API_RESULT_SCHEMA_V3_ID,
    API_WORKFLOW_SCHEMA_V3_ID: API_RESULT_SCHEMA_V4_ID,
    API_WORKFLOW_SCHEMA_V4_ID: API_RESULT_SCHEMA_V6_ID,
    API_WORKFLOW_SCHEMA_V5_ID: API_RESULT_SCHEMA_V7_ID,
    API_WORKFLOW_SCHEMA_V6_ID: API_RESULT_SCHEMA_V8_ID,
    API_WORKFLOW_SCHEMA_V7_ID: API_RESULT_SCHEMA_V9_ID,
    API_WORKFLOW_SCHEMA_V8_ID: API_RESULT_SCHEMA_V10_ID,
    API_WORKFLOW_SCHEMA_V9_ID: API_RESULT_SCHEMA_V11_ID,
    API_WORKFLOW_SCHEMA_V10_ID: API_RESULT_SCHEMA_V12_ID,
    API_WORKFLOW_SCHEMA_V11_ID: API_RESULT_SCHEMA_V13_ID,
    API_WORKFLOW_SCHEMA_V12_ID: API_RESULT_SCHEMA_V14_ID,
    API_WORKFLOW_SCHEMA_V13_ID: API_RESULT_SCHEMA_V15_ID,
}
API_RESULT_SCHEMAS_BY_ID = {
    API_RESULT_SCHEMA_ID: API_RESULT_SCHEMA,
    API_RESULT_SCHEMA_V3_ID: API_RESULT_SCHEMA_V3,
    API_RESULT_SCHEMA_V4_ID: API_RESULT_SCHEMA_V4,
    API_RESULT_SCHEMA_V5_ID: API_RESULT_SCHEMA_V5,
    API_RESULT_SCHEMA_V6_ID: API_RESULT_SCHEMA_V6,
    API_RESULT_SCHEMA_V7_ID: API_RESULT_SCHEMA_V7,
    API_RESULT_SCHEMA_V8_ID: API_RESULT_SCHEMA_V8,
    API_RESULT_SCHEMA_V9_ID: API_RESULT_SCHEMA_V9,
    API_RESULT_SCHEMA_V10_ID: API_RESULT_SCHEMA_V10,
    API_RESULT_SCHEMA_V11_ID: API_RESULT_SCHEMA_V11,
    API_RESULT_SCHEMA_V12_ID: API_RESULT_SCHEMA_V12,
    API_RESULT_SCHEMA_V13_ID: API_RESULT_SCHEMA_V13,
    API_RESULT_SCHEMA_V14_ID: API_RESULT_SCHEMA_V14,
    API_RESULT_SCHEMA_V15_ID: API_RESULT_SCHEMA_V15,
}
API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW = {
    API_WORKFLOW_SCHEMA_ID: API_COMPARISON_SCHEMA_ID,
    API_WORKFLOW_SCHEMA_V2_ID: API_COMPARISON_SCHEMA_V2_ID,
    API_WORKFLOW_SCHEMA_V3_ID: API_COMPARISON_SCHEMA_V3_ID,
    API_WORKFLOW_SCHEMA_V4_ID: API_COMPARISON_SCHEMA_V4_ID,
    API_WORKFLOW_SCHEMA_V5_ID: API_COMPARISON_SCHEMA_V5_ID,
    API_WORKFLOW_SCHEMA_V6_ID: API_COMPARISON_SCHEMA_V6_ID,
    API_WORKFLOW_SCHEMA_V7_ID: API_COMPARISON_SCHEMA_V7_ID,
    API_WORKFLOW_SCHEMA_V8_ID: API_COMPARISON_SCHEMA_V8_ID,
    API_WORKFLOW_SCHEMA_V9_ID: API_COMPARISON_SCHEMA_V9_ID,
    API_WORKFLOW_SCHEMA_V10_ID: API_COMPARISON_SCHEMA_V10_ID,
    API_WORKFLOW_SCHEMA_V11_ID: API_COMPARISON_SCHEMA_V11_ID,
    API_WORKFLOW_SCHEMA_V12_ID: API_COMPARISON_SCHEMA_V12_ID,
    API_WORKFLOW_SCHEMA_V13_ID: API_COMPARISON_SCHEMA_V13_ID,
}
API_COMPARISON_SCHEMAS_BY_ID = {
    API_COMPARISON_SCHEMA_ID: API_COMPARISON_SCHEMA,
    API_COMPARISON_SCHEMA_V2_ID: API_COMPARISON_SCHEMA_V2,
    API_COMPARISON_SCHEMA_V3_ID: API_COMPARISON_SCHEMA_V3,
    API_COMPARISON_SCHEMA_V4_ID: API_COMPARISON_SCHEMA_V4,
    API_COMPARISON_SCHEMA_V5_ID: API_COMPARISON_SCHEMA_V5,
    API_COMPARISON_SCHEMA_V6_ID: API_COMPARISON_SCHEMA_V6,
    API_COMPARISON_SCHEMA_V7_ID: API_COMPARISON_SCHEMA_V7,
    API_COMPARISON_SCHEMA_V8_ID: API_COMPARISON_SCHEMA_V8,
    API_COMPARISON_SCHEMA_V9_ID: API_COMPARISON_SCHEMA_V9,
    API_COMPARISON_SCHEMA_V10_ID: API_COMPARISON_SCHEMA_V10,
    API_COMPARISON_SCHEMA_V11_ID: API_COMPARISON_SCHEMA_V11,
    API_COMPARISON_SCHEMA_V12_ID: API_COMPARISON_SCHEMA_V12,
    API_COMPARISON_SCHEMA_V13_ID: API_COMPARISON_SCHEMA_V13,
}
RESULT_SCHEMA_ID = "fastapi-rs/python-asgi-workflow-result@2"
RESULT_SCHEMA_V3_ID = "fastapi-rs/python-asgi-workflow-result@3"
RESULT_SCHEMA_V4_ID = "fastapi-rs/python-asgi-workflow-result@4"
RESULT_SCHEMA_V5_ID = "fastapi-rs/python-asgi-workflow-result@5"
RESULT_SCHEMA_V6_ID = "fastapi-rs/python-asgi-workflow-result@6"
RESULT_SCHEMA_V7_ID = "fastapi-rs/python-asgi-workflow-result@7"
RESULT_SCHEMA_V8_ID = "fastapi-rs/python-asgi-workflow-result@8"
RESULT_SCHEMA_V9_ID = "fastapi-rs/python-asgi-workflow-result@9"
RESULT_SCHEMA_V10_ID = "fastapi-rs/python-asgi-workflow-result@10"
RESULT_SCHEMA_V11_ID = "fastapi-rs/python-asgi-workflow-result@11"
RESULT_SCHEMA_V12_ID = "fastapi-rs/python-asgi-workflow-result@12"
RESULT_SCHEMA_V13_ID = "fastapi-rs/python-asgi-workflow-result@13"
RESULT_SCHEMA_V14_ID = "fastapi-rs/python-asgi-workflow-result@14"
RESULT_SCHEMA_V15_ID = "fastapi-rs/python-asgi-workflow-result@15"
RESULT_SCHEMA_V16_ID = "fastapi-rs/python-asgi-workflow-result@16"
RESULT_SCHEMA_V17_ID = "fastapi-rs/python-asgi-workflow-result@17"
COMPARISON_SCHEMA_ID = "fastapi-rs/python-asgi-comparison@2"
COMPARISON_SCHEMA_V3_ID = "fastapi-rs/python-asgi-comparison@3"
COMPARISON_SCHEMA_V4_ID = "fastapi-rs/python-asgi-comparison@4"
COMPARISON_SCHEMA_V5_ID = "fastapi-rs/python-asgi-comparison@5"
COMPARISON_SCHEMA_V6_ID = "fastapi-rs/python-asgi-comparison@6"
COMPARISON_SCHEMA_V7_ID = "fastapi-rs/python-asgi-comparison@7"
COMPARISON_SCHEMA_V8_ID = "fastapi-rs/python-asgi-comparison@8"
COMPARISON_SCHEMA_V9_ID = "fastapi-rs/python-asgi-comparison@9"
COMPARISON_SCHEMA_V10_ID = "fastapi-rs/python-asgi-comparison@10"
COMPARISON_SCHEMA_V11_ID = "fastapi-rs/python-asgi-comparison@11"
COMPARISON_SCHEMA_V12_ID = "fastapi-rs/python-asgi-comparison@12"
COMPARISON_SCHEMA_V13_ID = "fastapi-rs/python-asgi-comparison@13"
COMPARISON_SCHEMA_V14_ID = "fastapi-rs/python-asgi-comparison@14"
COMPARISON_SCHEMA_V15_ID = "fastapi-rs/python-asgi-comparison@15"
COMPARISON_SCHEMA_V16_ID = "fastapi-rs/python-asgi-comparison@16"
COMPARISON_SCHEMA_V17_ID = "fastapi-rs/python-asgi-comparison@17"
COMPARISON_SCHEMA_V18_ID = "fastapi-rs/python-asgi-comparison@18"

WORKFLOW_SCHEMAS = {
    WORKFLOW_SCHEMA_ID: WORKFLOW_SCHEMA,
    WORKFLOW_SCHEMA_V3_ID: WORKFLOW_SCHEMA_V3,
    WORKFLOW_SCHEMA_V4_ID: WORKFLOW_SCHEMA_V4,
    WORKFLOW_SCHEMA_V5_ID: WORKFLOW_SCHEMA_V5,
    WORKFLOW_SCHEMA_V6_ID: WORKFLOW_SCHEMA_V6,
    WORKFLOW_SCHEMA_V7_ID: WORKFLOW_SCHEMA_V7,
    WORKFLOW_SCHEMA_V8_ID: WORKFLOW_SCHEMA_V8,
    WORKFLOW_SCHEMA_V9_ID: WORKFLOW_SCHEMA_V9,
    WORKFLOW_SCHEMA_V10_ID: WORKFLOW_SCHEMA_V10,
    WORKFLOW_SCHEMA_V11_ID: WORKFLOW_SCHEMA_V11,
    WORKFLOW_SCHEMA_V12_ID: WORKFLOW_SCHEMA_V12,
    WORKFLOW_SCHEMA_V13_ID: WORKFLOW_SCHEMA_V13,
    WORKFLOW_SCHEMA_V14_ID: WORKFLOW_SCHEMA_V14,
    WORKFLOW_SCHEMA_V15_ID: WORKFLOW_SCHEMA_V15,
    WORKFLOW_SCHEMA_V16_ID: WORKFLOW_SCHEMA_V16,
    WORKFLOW_SCHEMA_V17_ID: WORKFLOW_SCHEMA_V17,
    API_WORKFLOW_SCHEMA_ID: API_WORKFLOW_SCHEMA,
    API_WORKFLOW_SCHEMA_V2_ID: API_WORKFLOW_SCHEMA_V2,
    API_WORKFLOW_SCHEMA_V3_ID: API_WORKFLOW_SCHEMA_V3,
    API_WORKFLOW_SCHEMA_V4_ID: API_WORKFLOW_SCHEMA_V4,
    API_WORKFLOW_SCHEMA_V5_ID: API_WORKFLOW_SCHEMA_V5,
    API_WORKFLOW_SCHEMA_V6_ID: API_WORKFLOW_SCHEMA_V6,
    API_WORKFLOW_SCHEMA_V7_ID: API_WORKFLOW_SCHEMA_V7,
    API_WORKFLOW_SCHEMA_V8_ID: API_WORKFLOW_SCHEMA_V8,
    API_WORKFLOW_SCHEMA_V9_ID: API_WORKFLOW_SCHEMA_V9,
    API_WORKFLOW_SCHEMA_V10_ID: API_WORKFLOW_SCHEMA_V10,
    API_WORKFLOW_SCHEMA_V11_ID: API_WORKFLOW_SCHEMA_V11,
    API_WORKFLOW_SCHEMA_V12_ID: API_WORKFLOW_SCHEMA_V12,
    API_WORKFLOW_SCHEMA_V13_ID: API_WORKFLOW_SCHEMA_V13,
}
RECIPE_WORKFLOW_SCHEMAS = {
    **WORKFLOW_SCHEMAS,
    PROCESS_WORKFLOW_SCHEMA_ID: PROCESS_WORKFLOW_SCHEMA,
    PROCESS_WORKFLOW_SCHEMA_V2_ID: PROCESS_WORKFLOW_SCHEMA_V2,
}
RESULT_SCHEMAS = {
    RESULT_SCHEMA_ID: RESULT_SCHEMA,
    RESULT_SCHEMA_V3_ID: RESULT_SCHEMA_V3,
    RESULT_SCHEMA_V4_ID: RESULT_SCHEMA_V4,
    RESULT_SCHEMA_V5_ID: RESULT_SCHEMA_V5,
    RESULT_SCHEMA_V6_ID: RESULT_SCHEMA_V6,
    RESULT_SCHEMA_V7_ID: RESULT_SCHEMA_V7,
    RESULT_SCHEMA_V8_ID: RESULT_SCHEMA_V8,
    RESULT_SCHEMA_V9_ID: RESULT_SCHEMA_V9,
    RESULT_SCHEMA_V10_ID: RESULT_SCHEMA_V10,
    RESULT_SCHEMA_V11_ID: RESULT_SCHEMA_V11,
    RESULT_SCHEMA_V12_ID: RESULT_SCHEMA_V12,
    RESULT_SCHEMA_V13_ID: RESULT_SCHEMA_V13,
    RESULT_SCHEMA_V14_ID: RESULT_SCHEMA_V14,
    RESULT_SCHEMA_V15_ID: RESULT_SCHEMA_V15,
    RESULT_SCHEMA_V16_ID: RESULT_SCHEMA_V16,
    RESULT_SCHEMA_V17_ID: RESULT_SCHEMA_V17,
    API_RESULT_SCHEMA_ID: API_RESULT_SCHEMA,
    API_RESULT_SCHEMA_V3_ID: API_RESULT_SCHEMA_V3,
    API_RESULT_SCHEMA_V4_ID: API_RESULT_SCHEMA_V4,
    API_RESULT_SCHEMA_V5_ID: API_RESULT_SCHEMA_V5,
    API_RESULT_SCHEMA_V6_ID: API_RESULT_SCHEMA_V6,
    API_RESULT_SCHEMA_V7_ID: API_RESULT_SCHEMA_V7,
    API_RESULT_SCHEMA_V8_ID: API_RESULT_SCHEMA_V8,
    API_RESULT_SCHEMA_V9_ID: API_RESULT_SCHEMA_V9,
    API_RESULT_SCHEMA_V10_ID: API_RESULT_SCHEMA_V10,
    API_RESULT_SCHEMA_V11_ID: API_RESULT_SCHEMA_V11,
    API_RESULT_SCHEMA_V12_ID: API_RESULT_SCHEMA_V12,
    API_RESULT_SCHEMA_V13_ID: API_RESULT_SCHEMA_V13,
    API_RESULT_SCHEMA_V14_ID: API_RESULT_SCHEMA_V14,
    API_RESULT_SCHEMA_V15_ID: API_RESULT_SCHEMA_V15,
}
COMPARISON_SCHEMAS = {
    COMPARISON_SCHEMA_ID: COMPARISON_SCHEMA,
    COMPARISON_SCHEMA_V3_ID: COMPARISON_SCHEMA_V3,
    COMPARISON_SCHEMA_V4_ID: COMPARISON_SCHEMA_V4,
    COMPARISON_SCHEMA_V5_ID: COMPARISON_SCHEMA_V5,
    COMPARISON_SCHEMA_V6_ID: COMPARISON_SCHEMA_V6,
    COMPARISON_SCHEMA_V7_ID: COMPARISON_SCHEMA_V7,
    COMPARISON_SCHEMA_V8_ID: COMPARISON_SCHEMA_V8,
    COMPARISON_SCHEMA_V9_ID: COMPARISON_SCHEMA_V9,
    COMPARISON_SCHEMA_V10_ID: COMPARISON_SCHEMA_V10,
    COMPARISON_SCHEMA_V11_ID: COMPARISON_SCHEMA_V11,
    COMPARISON_SCHEMA_V12_ID: COMPARISON_SCHEMA_V12,
    COMPARISON_SCHEMA_V13_ID: COMPARISON_SCHEMA_V13,
    COMPARISON_SCHEMA_V14_ID: COMPARISON_SCHEMA_V14,
    COMPARISON_SCHEMA_V15_ID: COMPARISON_SCHEMA_V15,
    COMPARISON_SCHEMA_V16_ID: COMPARISON_SCHEMA_V16,
    COMPARISON_SCHEMA_V17_ID: COMPARISON_SCHEMA_V17,
    COMPARISON_SCHEMA_V18_ID: COMPARISON_SCHEMA_V18,
    API_COMPARISON_SCHEMA_ID: API_COMPARISON_SCHEMA,
    API_COMPARISON_SCHEMA_V2_ID: API_COMPARISON_SCHEMA_V2,
    API_COMPARISON_SCHEMA_V3_ID: API_COMPARISON_SCHEMA_V3,
    API_COMPARISON_SCHEMA_V4_ID: API_COMPARISON_SCHEMA_V4,
    API_COMPARISON_SCHEMA_V5_ID: API_COMPARISON_SCHEMA_V5,
    API_COMPARISON_SCHEMA_V6_ID: API_COMPARISON_SCHEMA_V6,
    API_COMPARISON_SCHEMA_V7_ID: API_COMPARISON_SCHEMA_V7,
    API_COMPARISON_SCHEMA_V8_ID: API_COMPARISON_SCHEMA_V8,
    API_COMPARISON_SCHEMA_V9_ID: API_COMPARISON_SCHEMA_V9,
    API_COMPARISON_SCHEMA_V10_ID: API_COMPARISON_SCHEMA_V10,
    API_COMPARISON_SCHEMA_V11_ID: API_COMPARISON_SCHEMA_V11,
    API_COMPARISON_SCHEMA_V12_ID: API_COMPARISON_SCHEMA_V12,
    API_COMPARISON_SCHEMA_V13_ID: API_COMPARISON_SCHEMA_V13,
}
RESULT_SCHEMA_IDS_BY_WORKFLOW = {
    WORKFLOW_SCHEMA_ID: RESULT_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID: RESULT_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID: RESULT_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID: RESULT_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID: RESULT_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V7_ID: RESULT_SCHEMA_V7_ID,
    WORKFLOW_SCHEMA_V8_ID: RESULT_SCHEMA_V8_ID,
    WORKFLOW_SCHEMA_V9_ID: RESULT_SCHEMA_V9_ID,
    WORKFLOW_SCHEMA_V10_ID: RESULT_SCHEMA_V10_ID,
    WORKFLOW_SCHEMA_V11_ID: RESULT_SCHEMA_V11_ID,
    WORKFLOW_SCHEMA_V12_ID: RESULT_SCHEMA_V12_ID,
    WORKFLOW_SCHEMA_V13_ID: RESULT_SCHEMA_V13_ID,
    WORKFLOW_SCHEMA_V14_ID: RESULT_SCHEMA_V14_ID,
    WORKFLOW_SCHEMA_V15_ID: RESULT_SCHEMA_V15_ID,
    WORKFLOW_SCHEMA_V16_ID: RESULT_SCHEMA_V16_ID,
    WORKFLOW_SCHEMA_V17_ID: RESULT_SCHEMA_V17_ID,
    **API_RESULT_SCHEMA_IDS_BY_WORKFLOW,
}
COMPARISON_SCHEMA_IDS_BY_WORKFLOW = {
    WORKFLOW_SCHEMA_ID: COMPARISON_SCHEMA_ID,
    WORKFLOW_SCHEMA_V3_ID: COMPARISON_SCHEMA_V3_ID,
    WORKFLOW_SCHEMA_V4_ID: COMPARISON_SCHEMA_V4_ID,
    WORKFLOW_SCHEMA_V5_ID: COMPARISON_SCHEMA_V5_ID,
    WORKFLOW_SCHEMA_V6_ID: COMPARISON_SCHEMA_V6_ID,
    WORKFLOW_SCHEMA_V7_ID: COMPARISON_SCHEMA_V10_ID,
    WORKFLOW_SCHEMA_V8_ID: COMPARISON_SCHEMA_V10_ID,
    WORKFLOW_SCHEMA_V9_ID: COMPARISON_SCHEMA_V10_ID,
    WORKFLOW_SCHEMA_V10_ID: COMPARISON_SCHEMA_V11_ID,
    WORKFLOW_SCHEMA_V11_ID: COMPARISON_SCHEMA_V12_ID,
    WORKFLOW_SCHEMA_V12_ID: COMPARISON_SCHEMA_V13_ID,
    WORKFLOW_SCHEMA_V13_ID: COMPARISON_SCHEMA_V14_ID,
    WORKFLOW_SCHEMA_V14_ID: COMPARISON_SCHEMA_V15_ID,
    WORKFLOW_SCHEMA_V15_ID: COMPARISON_SCHEMA_V16_ID,
    WORKFLOW_SCHEMA_V16_ID: COMPARISON_SCHEMA_V17_ID,
    WORKFLOW_SCHEMA_V17_ID: COMPARISON_SCHEMA_V18_ID,
    **API_COMPARISON_SCHEMA_IDS_BY_WORKFLOW,
}


class ContractError(ValueError):
    """A malformed workflow or stale reference in the parity contract."""


class _UniqueKeyLoader(SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ContractError(f"duplicate YAML mapping key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ContractError(f"non-finite JSON number is forbidden: {value}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc


def read_manifest() -> dict[str, Any]:
    """Load the one manifest and enforce the pinned oracle profile shape."""
    manifest_path = ROOT / "tests/fixtures/manifest.yaml"
    try:
        with manifest_path.open(encoding="utf-8") as stream:
            manifest = yaml.load(stream, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read manifest {manifest_path}: {exc}") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema") != "fastapi-rs/contract-foundation@1"
    ):
        raise ContractError("manifest schema identity is missing or unsupported")
    profile = manifest.get("oracle_profile")
    if not isinstance(profile, dict) or profile.get("id") != (
        "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13"
    ):
        raise ContractError("manifest must define the fixed FastAPI/Starlette 1.6.0 oracle profile")
    selected = manifest.get("selected_contracts")
    if not isinstance(selected, dict):
        raise ContractError("manifest selected_contracts must be a mapping")
    expected_commits = {
        "fastapi": "95f8322ee1dcda7ceace7b1c4f6c9915b36d748f",
        "starlette": "4f250d6b814587e20c5365f0a5f0c4d42bcb929f",
    }
    for contract_name, commit in expected_commits.items():
        contract = selected.get(contract_name)
        if not isinstance(contract, dict):
            raise ContractError(f"manifest selected contract {contract_name} must be a mapping")
        expected_version = "0.141.1" if contract_name == "fastapi" else "1.6.0"
        if contract.get("version") != expected_version or contract.get("commit") != commit:
            raise ContractError(
                f"manifest {contract_name} contract changed without updating "
                "the fixed oracle profile"
            )
    if profile.get("python") != {"implementation": "CPython", "version": "3.12.13"}:
        raise ContractError("manifest oracle runtime must remain CPython 3.12.13")
    if profile.get("source_commits") != expected_commits:
        raise ContractError("manifest oracle commits do not match the selected source contracts")
    pydantic = selected.get("pydantic")
    if not isinstance(pydantic, dict):
        raise ContractError("manifest Pydantic contract must be a mapping")
    if (pydantic.get("version"), pydantic.get("pydantic_core_version")) != (
        "2.13.4",
        "2.46.4",
    ):
        raise ContractError(
            "manifest Pydantic baseline changed without updating the oracle profile"
        )
    expected_packages = {
        "annotated-doc": "0.0.4",
        "annotated-types": "0.7.0",
        "anyio": "4.12.1",
        "fastapi": "0.141.1",
        "idna": "3.18",
        "pydantic": "2.13.4",
        "pydantic-core": "2.46.4",
        "starlette": "1.6.0",
        "typing-extensions": "4.16.0",
        "typing-inspection": "0.4.2",
    }
    if profile.get("packages") != expected_packages:
        raise ContractError("manifest oracle runtime package pins are incomplete or changed")
    expected_extensions = {
        "standard-multipart": {
            "id": "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-standard-multipart-0.0.32",
            "base_profile": profile["id"],
            "added_packages": {"python-multipart": "0.0.32"},
            "fastapi_extra": "standard",
            "prepare_target": "parity-prepare-oracle-standard",
        },
        "testclient": {
            "id": "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-standard-httpx-0.28.1",
            "base_profile": profile["id"],
            "added_packages": {
                "certifi": "2026.1.4",
                "h11": "0.16.0",
                "httpcore": "1.0.9",
                "httpx": "0.28.1",
            },
            "fastapi_extra": "standard",
            "prepare_target": "parity-prepare-oracle-testclient",
        },
        "email-validation": {
            "id": "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-email-validation-2.3.0",
            "base_profile": profile["id"],
            "lock": {
                "path": "requirements/email-validation-cpython-3.12.13.lock",
                "sha256": "031d2b004bf6427b8d771cf172b36878ec7fe3299a1e5806f92d7066eb1d41b3",
                "profile": "CPython 3.12.13 with email-validator 2.3.0",
            },
            "added_packages": {"dnspython": "2.8.0", "email-validator": "2.3.0"},
            "fastapi_extra": "standard",
            "prepare_target": "parity-prepare-oracle-email-validation",
        },
        "templates": {
            "id": (
                "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-templates-"
                "jinja2-3.1.6-markupsafe-3.0.3"
            ),
            "base_profile": profile["id"],
            "lock": {
                "path": "requirements/templates-cpython-3.12.13.lock",
                "sha256": "eee2f5509c1d8645caf971998f6a777e144901b0a0847ee329c62ebd4b31fdb0",
                "profile": "CPython 3.12.13 with Jinja2 3.1.6 and MarkupSafe 3.0.3",
            },
            "added_packages": {"jinja2": "3.1.6", "markupsafe": "3.0.3"},
            "fastapi_extra": None,
            "prepare_target": "parity-prepare-oracle-templates",
        },
        "json-serializers": {
            "id": (
                "fastapi-0.141.1-starlette-1.6.0-cpython-3.12.13-json-serializers-"
                "orjson-3.13.0-ujson-6.0.0"
            ),
            "base_profile": profile["id"],
            "lock": {
                "path": "requirements/json-serializers-cpython-3.12.13.lock",
                "sha256": "c43d6393010e9f0e8b95831d8cb2127dd4f4371c539bb7270675e9ba042fac86",
                "profile": "CPython 3.12.13 with orjson 3.13.0 and ujson 6.0.0",
            },
            "added_packages": {"orjson": "3.13.0", "ujson": "6.0.0"},
            "fastapi_extra": None,
            "prepare_target": "parity-prepare-oracle-json-serializers",
        },
    }
    if manifest.get("oracle_profile_extensions") != expected_extensions:
        raise ContractError(
            "manifest oracle optional profiles differ from the pinned package environments"
        )
    target = manifest.get("target")
    if not isinstance(target, dict) or target.get("version") != "0.1.0":
        raise ContractError(
            "manifest target version must remain the pinned development version 0.1.0"
        )
    try:
        project_metadata = yaml.safe_load((ROOT / "metadata.yaml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot read FastAPI-RS metadata: {exc}") from exc
    starlette_rs_metadata = (
        project_metadata.get("starlette_rs") if isinstance(project_metadata, dict) else None
    )
    metadata_starlette_rs_commit = (
        starlette_rs_metadata.get("commit") if isinstance(starlette_rs_metadata, dict) else None
    )
    if (
        not isinstance(metadata_starlette_rs_commit, str)
        or len(metadata_starlette_rs_commit) != 40
        or any(character not in "0123456789abcdef" for character in metadata_starlette_rs_commit)
    ):
        raise ContractError("metadata.yaml must pin a full lowercase Starlette-RS commit")
    if target.get("starlette_rs_distribution") != {
        "name": "starlette-rs-py",
        "version": "0.1.0",
        "starlette_contract": "1.6.0",
        "commit": metadata_starlette_rs_commit,
    }:
        raise ContractError("manifest target must select Starlette-RS 0.1.0 for the 1.6.0 contract")
    expected_target_extensions = {
        "standard-multipart": {
            "id": "fastapi-rs-standard-multipart-cpython-3.12.13-python-multipart-0.0.32",
            "base_profile": target["id"],
            "lock": {
                "path": "requirements/target-standard-multipart-cpython-3.12.13.lock",
                "sha256": "3aee8269ac560768cc04dc8bb7ad6d55db75dd042f3a1a962fc5b8b3bfa853d6",
                "profile": "CPython 3.12.13 with python-multipart 0.0.32",
            },
            "added_packages": {"python-multipart": "0.0.32"},
            "fastapi_extra": "standard",
            "prepare_target": "parity-prepare-target-standard-multipart",
        },
        "testclient": {
            "id": "fastapi-rs-testclient-cpython-3.12.13-httpx-0.28.1",
            "base_profile": target["id"],
            "lock": {
                "path": "requirements/target-testclient-cpython-3.12.13.lock",
                "sha256": "c72266c50b04909783777ddf9949a79b4504d5af787c9ecbfe1014141f41f318",
                "profile": "CPython 3.12.13 with HTTPX 0.28.1 fallback",
            },
            "added_packages": {
                "certifi": "2026.1.4",
                "h11": "0.16.0",
                "httpcore": "1.0.9",
                "httpx": "0.28.1",
            },
            "fastapi_extra": "testclient",
            "prepare_target": "parity-prepare-target-testclient",
        },
        "email-validation": {
            "id": "fastapi-rs-email-validation-cpython-3.12.13-email-validator-2.3.0",
            "base_profile": target["id"],
            "lock": {
                "path": "requirements/email-validation-cpython-3.12.13.lock",
                "sha256": "031d2b004bf6427b8d771cf172b36878ec7fe3299a1e5806f92d7066eb1d41b3",
                "profile": "CPython 3.12.13 with email-validator 2.3.0",
            },
            "added_packages": {"dnspython": "2.8.0", "email-validator": "2.3.0"},
            "fastapi_extra": "standard",
            "prepare_target": "parity-prepare-target-email-validation",
        },
        "templates": {
            "id": "fastapi-rs-templates-cpython-3.12.13-jinja2-3.1.6-markupsafe-3.0.3",
            "base_profile": target["id"],
            "lock": {
                "path": "requirements/templates-cpython-3.12.13.lock",
                "sha256": "eee2f5509c1d8645caf971998f6a777e144901b0a0847ee329c62ebd4b31fdb0",
                "profile": "CPython 3.12.13 with Jinja2 3.1.6 and MarkupSafe 3.0.3",
            },
            "added_packages": {"jinja2": "3.1.6", "markupsafe": "3.0.3"},
            "fastapi_extra": "templates",
            "prepare_target": "parity-prepare-target-templates",
        },
        "json-serializers": {
            "id": "fastapi-rs-json-serializers-cpython-3.12.13-orjson-3.13.0-ujson-6.0.0",
            "base_profile": target["id"],
            "lock": {
                "path": "requirements/json-serializers-cpython-3.12.13.lock",
                "sha256": "c43d6393010e9f0e8b95831d8cb2127dd4f4371c539bb7270675e9ba042fac86",
                "profile": "CPython 3.12.13 with orjson 3.13.0 and ujson 6.0.0",
            },
            "added_packages": {"orjson": "3.13.0", "ujson": "6.0.0"},
            "fastapi_extra": None,
            "prepare_target": "parity-prepare-target-json-serializers",
        },
    }
    if manifest.get("target_profile_extensions") != expected_target_extensions:
        raise ContractError(
            "manifest target optional profile differs from the pinned TestClient profile"
        )
    source_artifacts = manifest.get("source_artifacts")
    if not isinstance(source_artifacts, dict):
        raise ContractError("manifest source_artifacts must be a mapping")
    for artifact_name in (
        "api_inventory",
        "api_classification_review",
        "api_import_binding_classification_review",
        "compatibility_atlas",
        "fixture_backlog",
        "observation_selector_catalog",
        "runtime_api_surface_core",
        "runtime_api_surface_standard",
        "materialized_input_index",
    ):
        artifact = source_artifacts.get(artifact_name)
        if not isinstance(artifact, dict):
            raise ContractError(f"manifest {artifact_name} reference is missing")
        _verify_digest_ref(artifact.get("path"), artifact.get("sha256"), artifact_name)
        if artifact_name == "materialized_input_index":
            if artifact.get("schema") != MATERIALIZED_INPUT_INDEX_SCHEMA_ID:
                raise ContractError("manifest materialized input index schema is unsupported")
            _verify_digest_ref(
                artifact.get("schema_path"),
                artifact.get("schema_sha256"),
                "materialized input index schema",
            )

    atlas_artifact = source_artifacts["compatibility_atlas"]
    atlas = read_json(_resolve_repo_file(atlas_artifact["path"], "compatibility atlas"))
    fixture_backlog_artifact = source_artifacts["fixture_backlog"]
    fixture_backlog = read_json(
        _resolve_repo_file(fixture_backlog_artifact["path"], "fixture backlog")
    )
    fixture_backlog_ref = atlas.get("fixture_backlog_ref") if isinstance(atlas, dict) else None
    backlog_schema = fixture_backlog_artifact.get("schema")
    if (
        not isinstance(fixture_backlog_ref, dict)
        or backlog_schema != FIXTURE_BACKLOG_SCHEMA_ID
        or fixture_backlog.get("schema") != FIXTURE_BACKLOG_SCHEMA_ID
        or fixture_backlog_ref.get("schema") != FIXTURE_BACKLOG_SCHEMA_ID
        or fixture_backlog_ref.get("path") != fixture_backlog_artifact.get("path")
    ):
        raise ContractError("manifest, atlas, and fixture-backlog schemas or paths differ")
    review_artifact = source_artifacts["api_classification_review"]
    review_link = atlas.get("api_classification_review") if isinstance(atlas, dict) else None
    if not isinstance(review_link, dict) or any(
        review_link.get(atlas_key) != review_artifact.get(manifest_key)
        for atlas_key, manifest_key in (
            ("path", "path"),
            ("schema", "schema"),
            ("sha256", "sha256"),
        )
    ):
        raise ContractError("manifest callable-classification review differs from atlas evidence")
    review = read_json(_resolve_repo_file(review_artifact["path"], "API classification review"))
    if (
        not isinstance(review, dict)
        or review.get("schema") != review_artifact.get("schema")
        or review.get("source_identity", {}).get("selected_starlette_profile") != "1.6.0"
    ):
        raise ContractError("API callable-classification review identity is unsupported")

    import_binding_review_artifact = source_artifacts["api_import_binding_classification_review"]
    import_binding_review_link = atlas.get("api_import_binding_classification_review")
    if not isinstance(import_binding_review_link, dict) or any(
        import_binding_review_link.get(atlas_key)
        != import_binding_review_artifact.get(manifest_key)
        for atlas_key, manifest_key in (
            ("path", "path"),
            ("schema", "schema"),
            ("sha256", "sha256"),
        )
    ):
        raise ContractError("manifest import-binding review differs from atlas evidence")
    import_binding_review = read_json(
        _resolve_repo_file(
            import_binding_review_artifact["path"], "API import-binding classification review"
        )
    )
    if not isinstance(import_binding_review, dict):
        raise ContractError("API import-binding classification review must be an object")
    scope = import_binding_review.get("scope", {})
    source_identity = import_binding_review.get("source_identity", {})
    counts = import_binding_review_artifact.get("counts", {})
    recommendations = scope.get("recommendation_counts", {})
    expected_review_counts = {
        "candidates": scope.get("candidate_count"),
        "supported": recommendations.get("supported"),
        "private_or_internal": recommendations.get("private/internal"),
        "uncertain": recommendations.get("uncertain"),
        "starlette_rs_reviewed_candidates": scope.get("starlette_rs_reviewed_candidate_count"),
        "starlette_rs_unreviewed_unique_targets": scope.get(
            "starlette_rs_unreviewed_unique_target_count"
        ),
    }
    pinned_sources = import_binding_review.get("pinned_starlette_rs_sources", {})
    pinned_files = pinned_sources.get("files", {}) if isinstance(pinned_sources, dict) else {}
    source_digests = {
        f"{name}_sha256": pinned_files.get(name, {}).get("sha256")
        for name in ("metadata", "manifest", "api_catalog", "api_review")
    }
    if (
        import_binding_review.get("schema") != import_binding_review_artifact.get("schema")
        or source_identity != import_binding_review_artifact.get("source_identity")
        or not isinstance(pinned_sources, dict)
        or pinned_sources.get("contract_id")
        != import_binding_review_artifact.get("starlette_rs_contract_id")
        or import_binding_review.get("scope", {}).get("candidate_ids_sha256")
        != import_binding_review_artifact.get("candidate_ids_sha256")
        or expected_review_counts != {key: counts.get(key) for key in expected_review_counts}
        or source_digests != import_binding_review_artifact.get("pinned_starlette_rs_sources")
    ):
        raise ContractError("API import-binding classification review metadata is unsupported")

    unresolved = manifest.get("unresolved")
    process_workflow_contract = (
        unresolved.get("python_process_workflow") if isinstance(unresolved, dict) else None
    )
    if not isinstance(process_workflow_contract, dict):
        raise ContractError("manifest Python process workflow v1 contract is missing")
    if (
        process_workflow_contract.get("schema_id") != PROCESS_WORKFLOW_SCHEMA_ID
        or process_workflow_contract.get("result_schema_id") != PROCESS_RESULT_SCHEMA_ID
        or process_workflow_contract.get("comparison_schema_id") != PROCESS_COMPARISON_SCHEMA_ID
    ):
        raise ContractError("manifest Python process workflow v1 schema identities are unsupported")
    process_v1_schema_refs = (
        ("schema_path", "schema_sha256", "python process workflow v1 schema"),
        ("result_schema_path", "result_schema_sha256", "python process result v1 schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "python process comparison v1 schema",
        ),
    )
    for path_key, digest_key, label in process_v1_schema_refs:
        _verify_digest_ref(
            process_workflow_contract.get(path_key),
            process_workflow_contract.get(digest_key),
            label,
        )
    process_workflow_v2_contract = (
        unresolved.get("python_process_workflow_v2") if isinstance(unresolved, dict) else None
    )
    if not isinstance(process_workflow_v2_contract, dict):
        raise ContractError("manifest Python process workflow v2 contract is missing")
    if (
        process_workflow_v2_contract.get("schema_id") != PROCESS_WORKFLOW_SCHEMA_V2_ID
        or process_workflow_v2_contract.get("result_schema_id") != PROCESS_RESULT_SCHEMA_V2_ID
        or process_workflow_v2_contract.get("comparison_schema_id")
        != PROCESS_COMPARISON_SCHEMA_V2_ID
    ):
        raise ContractError("manifest Python process workflow v2 schema identities are unsupported")
    process_v2_schema_refs = (
        ("schema_path", "schema_sha256", "python process workflow v2 schema"),
        ("result_schema_path", "result_schema_sha256", "python process result v2 schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "python process comparison v2 schema",
        ),
    )
    for path_key, digest_key, label in process_v2_schema_refs:
        _verify_digest_ref(
            process_workflow_v2_contract.get(path_key),
            process_workflow_v2_contract.get(digest_key),
            label,
        )
    workflow_contract = (
        unresolved.get("python_asgi_workflow") if isinstance(unresolved, dict) else None
    )
    if not isinstance(workflow_contract, dict):
        raise ContractError("manifest Python/ASGI workflow contract is missing")
    schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison schema"),
        ("recipe_path", "recipe_sha256", "workflow input recipe"),
    )
    for path_key, digest_key, label in schema_refs:
        _verify_digest_ref(
            workflow_contract.get(path_key),
            workflow_contract.get(digest_key),
            label,
        )
    workflow_v3_contract = (
        unresolved.get("python_asgi_workflow_v3") if isinstance(unresolved, dict) else None
    )
    if not isinstance(workflow_v3_contract, dict):
        raise ContractError("manifest Python/ASGI v3 workflow contract is missing")
    workflow_v3_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v3 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v3 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v3 schema"),
    )
    for path_key, digest_key, label in workflow_v3_schema_refs:
        _verify_digest_ref(
            workflow_v3_contract.get(path_key),
            workflow_v3_contract.get(digest_key),
            label,
        )
    workflow_v4_contract = unresolved.get("python_asgi_workflow_v4")
    if not isinstance(workflow_v4_contract, dict):
        raise ContractError("manifest Python/ASGI v4 workflow contract is missing")
    if (
        workflow_v4_contract.get("schema_id") != WORKFLOW_SCHEMA_V4_ID
        or workflow_v4_contract.get("result_schema_id") != RESULT_SCHEMA_V4_ID
        or workflow_v4_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V4_ID
    ):
        raise ContractError("manifest Python/ASGI v4 schema identities are unsupported")
    workflow_v4_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v4 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v4 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v4 schema"),
    )
    for path_key, digest_key, label in workflow_v4_schema_refs:
        _verify_digest_ref(
            workflow_v4_contract.get(path_key),
            workflow_v4_contract.get(digest_key),
            label,
        )
    workflow_v5_contract = unresolved.get("python_asgi_workflow_v5")
    if not isinstance(workflow_v5_contract, dict):
        raise ContractError("manifest Python/ASGI v5 workflow contract is missing")
    if (
        workflow_v5_contract.get("schema_id") != WORKFLOW_SCHEMA_V5_ID
        or workflow_v5_contract.get("result_schema_id") != RESULT_SCHEMA_V5_ID
        or workflow_v5_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V5_ID
    ):
        raise ContractError("manifest Python/ASGI v5 schema identities are unsupported")
    workflow_v5_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v5 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v5 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v5 schema"),
    )
    for path_key, digest_key, label in workflow_v5_schema_refs:
        _verify_digest_ref(
            workflow_v5_contract.get(path_key),
            workflow_v5_contract.get(digest_key),
            label,
        )
    workflow_v6_contract = unresolved.get("python_asgi_workflow_v6")
    if not isinstance(workflow_v6_contract, dict):
        raise ContractError("manifest Python/ASGI v6 workflow contract is missing")
    if (
        workflow_v6_contract.get("schema_id") != WORKFLOW_SCHEMA_V6_ID
        or workflow_v6_contract.get("result_schema_id") != RESULT_SCHEMA_V6_ID
        or workflow_v6_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V6_ID
    ):
        raise ContractError("manifest Python/ASGI v6 schema identities are unsupported")
    workflow_v6_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v6 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v6 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v6 schema"),
    )
    for path_key, digest_key, label in workflow_v6_schema_refs:
        _verify_digest_ref(
            workflow_v6_contract.get(path_key),
            workflow_v6_contract.get(digest_key),
            label,
        )
    workflow_v7_contract = unresolved.get("python_asgi_workflow_v7")
    if not isinstance(workflow_v7_contract, dict):
        raise ContractError("manifest Python/ASGI v7 workflow contract is missing")
    if (
        workflow_v7_contract.get("schema_id") != WORKFLOW_SCHEMA_V7_ID
        or workflow_v7_contract.get("result_schema_id") != RESULT_SCHEMA_V7_ID
        or workflow_v7_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V10_ID
    ):
        raise ContractError("manifest Python/ASGI v7 schema identities are unsupported")
    workflow_v7_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v7 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v7 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v10 schema"),
    )
    for path_key, digest_key, label in workflow_v7_schema_refs:
        _verify_digest_ref(
            workflow_v7_contract.get(path_key),
            workflow_v7_contract.get(digest_key),
            label,
        )
    workflow_v8_contract = unresolved.get("python_asgi_workflow_v8")
    if not isinstance(workflow_v8_contract, dict):
        raise ContractError("manifest Python/ASGI v8 workflow contract is missing")
    if (
        workflow_v8_contract.get("schema_id") != WORKFLOW_SCHEMA_V8_ID
        or workflow_v8_contract.get("result_schema_id") != RESULT_SCHEMA_V8_ID
        or workflow_v8_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V10_ID
    ):
        raise ContractError("manifest Python/ASGI v8 schema identities are unsupported")
    workflow_v8_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v8 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v8 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v10 schema"),
    )
    for path_key, digest_key, label in workflow_v8_schema_refs:
        _verify_digest_ref(
            workflow_v8_contract.get(path_key),
            workflow_v8_contract.get(digest_key),
            label,
        )
    workflow_v9_contract = unresolved.get("python_asgi_workflow_v9")
    if not isinstance(workflow_v9_contract, dict):
        raise ContractError("manifest Python/ASGI v9 workflow contract is missing")
    if (
        workflow_v9_contract.get("schema_id") != WORKFLOW_SCHEMA_V9_ID
        or workflow_v9_contract.get("result_schema_id") != RESULT_SCHEMA_V9_ID
        or workflow_v9_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V10_ID
    ):
        raise ContractError("manifest Python/ASGI v9 schema identities are unsupported")
    workflow_v9_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v9 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v9 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v10 schema"),
    )
    for path_key, digest_key, label in workflow_v9_schema_refs:
        _verify_digest_ref(
            workflow_v9_contract.get(path_key),
            workflow_v9_contract.get(digest_key),
            label,
        )
    workflow_v10_contract = unresolved.get("python_asgi_workflow_v10")
    if not isinstance(workflow_v10_contract, dict):
        raise ContractError("manifest Python/ASGI v10 workflow contract is missing")
    if (
        workflow_v10_contract.get("schema_id") != WORKFLOW_SCHEMA_V10_ID
        or workflow_v10_contract.get("result_schema_id") != RESULT_SCHEMA_V10_ID
        or workflow_v10_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V11_ID
    ):
        raise ContractError("manifest Python/ASGI v10 schema identities are unsupported")
    workflow_v10_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v10 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v10 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v11 schema"),
    )
    for path_key, digest_key, label in workflow_v10_schema_refs:
        _verify_digest_ref(
            workflow_v10_contract.get(path_key),
            workflow_v10_contract.get(digest_key),
            label,
        )
    workflow_v11_contract = unresolved.get("python_asgi_workflow_v11")
    if not isinstance(workflow_v11_contract, dict):
        raise ContractError("manifest Python/ASGI v11 workflow contract is missing")
    if (
        workflow_v11_contract.get("schema_id") != WORKFLOW_SCHEMA_V11_ID
        or workflow_v11_contract.get("result_schema_id") != RESULT_SCHEMA_V11_ID
        or workflow_v11_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V12_ID
    ):
        raise ContractError("manifest Python/ASGI v11 schema identities are unsupported")
    workflow_v11_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v11 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v11 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v12 schema"),
    )
    for path_key, digest_key, label in workflow_v11_schema_refs:
        _verify_digest_ref(
            workflow_v11_contract.get(path_key),
            workflow_v11_contract.get(digest_key),
            label,
        )
    workflow_v12_contract = unresolved.get("python_asgi_workflow_v12")
    if not isinstance(workflow_v12_contract, dict):
        raise ContractError("manifest Python/ASGI v12 workflow contract is missing")
    if (
        workflow_v12_contract.get("schema_id") != WORKFLOW_SCHEMA_V12_ID
        or workflow_v12_contract.get("result_schema_id") != RESULT_SCHEMA_V12_ID
        or workflow_v12_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V13_ID
    ):
        raise ContractError("manifest Python/ASGI v12 schema identities are unsupported")
    workflow_v12_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v12 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v12 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v13 schema"),
    )
    for path_key, digest_key, label in workflow_v12_schema_refs:
        _verify_digest_ref(
            workflow_v12_contract.get(path_key),
            workflow_v12_contract.get(digest_key),
            label,
        )
    workflow_v13_contract = unresolved.get("python_asgi_workflow_v13")
    if not isinstance(workflow_v13_contract, dict):
        raise ContractError("manifest Python/ASGI v13 workflow contract is missing")
    if (
        workflow_v13_contract.get("schema_id") != WORKFLOW_SCHEMA_V13_ID
        or workflow_v13_contract.get("result_schema_id") != RESULT_SCHEMA_V13_ID
        or workflow_v13_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V14_ID
    ):
        raise ContractError("manifest Python/ASGI v13 schema identities are unsupported")
    workflow_v13_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v13 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v13 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v14 schema"),
    )
    for path_key, digest_key, label in workflow_v13_schema_refs:
        _verify_digest_ref(
            workflow_v13_contract.get(path_key),
            workflow_v13_contract.get(digest_key),
            label,
        )
    workflow_v14_contract = unresolved.get("python_asgi_workflow_v14")
    if not isinstance(workflow_v14_contract, dict):
        raise ContractError("manifest Python/ASGI v14 workflow contract is missing")
    if (
        workflow_v14_contract.get("schema_id") != WORKFLOW_SCHEMA_V14_ID
        or workflow_v14_contract.get("result_schema_id") != RESULT_SCHEMA_V14_ID
        or workflow_v14_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V15_ID
    ):
        raise ContractError("manifest Python/ASGI v14 schema identities are unsupported")
    workflow_v14_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v14 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v14 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v15 schema"),
    )
    for path_key, digest_key, label in workflow_v14_schema_refs:
        _verify_digest_ref(
            workflow_v14_contract.get(path_key),
            workflow_v14_contract.get(digest_key),
            label,
        )
    workflow_v15_contract = unresolved.get("python_asgi_workflow_v15")
    if not isinstance(workflow_v15_contract, dict):
        raise ContractError("manifest Python/ASGI v15 workflow contract is missing")
    if (
        workflow_v15_contract.get("schema_id") != WORKFLOW_SCHEMA_V15_ID
        or workflow_v15_contract.get("result_schema_id") != RESULT_SCHEMA_V15_ID
        or workflow_v15_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V16_ID
    ):
        raise ContractError("manifest Python/ASGI v15 schema identities are unsupported")
    workflow_v15_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v15 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v15 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v16 schema"),
    )
    for path_key, digest_key, label in workflow_v15_schema_refs:
        _verify_digest_ref(
            workflow_v15_contract.get(path_key),
            workflow_v15_contract.get(digest_key),
            label,
        )
    workflow_v16_contract = unresolved.get("python_asgi_workflow_v16")
    if not isinstance(workflow_v16_contract, dict):
        raise ContractError("manifest Python/ASGI v16 workflow contract is missing")
    if (
        workflow_v16_contract.get("schema_id") != WORKFLOW_SCHEMA_V16_ID
        or workflow_v16_contract.get("result_schema_id") != RESULT_SCHEMA_V16_ID
        or workflow_v16_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V17_ID
    ):
        raise ContractError("manifest Python/ASGI v16 schema identities are unsupported")
    workflow_v16_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v16 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v16 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v17 schema"),
    )
    for path_key, digest_key, label in workflow_v16_schema_refs:
        _verify_digest_ref(
            workflow_v16_contract.get(path_key),
            workflow_v16_contract.get(digest_key),
            label,
        )
    workflow_v17_contract = unresolved.get("python_asgi_workflow_v17")
    if not isinstance(workflow_v17_contract, dict):
        raise ContractError("manifest Python/ASGI v17 workflow contract is missing")
    if (
        workflow_v17_contract.get("schema_id") != WORKFLOW_SCHEMA_V17_ID
        or workflow_v17_contract.get("result_schema_id") != RESULT_SCHEMA_V17_ID
        or workflow_v17_contract.get("comparison_schema_id") != COMPARISON_SCHEMA_V18_ID
    ):
        raise ContractError("manifest Python/ASGI v17 schema identities are unsupported")
    workflow_v17_schema_refs = (
        ("schema_path", "schema_sha256", "python-asgi-workflow v17 schema"),
        ("result_schema_path", "result_schema_sha256", "workflow result v17 schema"),
        ("comparison_schema_path", "comparison_schema_sha256", "comparison v18 schema"),
    )
    for path_key, digest_key, label in workflow_v17_schema_refs:
        _verify_digest_ref(
            workflow_v17_contract.get(path_key),
            workflow_v17_contract.get(digest_key),
            label,
        )
    api_workflow_contract = (
        unresolved.get("python_api_workflow") if isinstance(unresolved, dict) else None
    )
    if not isinstance(api_workflow_contract, dict):
        raise ContractError("manifest direct Python API workflow contract is missing")
    api_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API comparison schema",
        ),
    )
    for path_key, digest_key, label in api_schema_refs:
        _verify_digest_ref(
            api_workflow_contract.get(path_key),
            api_workflow_contract.get(digest_key),
            label,
        )
    api_workflow_v2_contract = unresolved.get("python_api_workflow_v2")
    if not isinstance(api_workflow_v2_contract, dict):
        raise ContractError("manifest direct Python API v2 workflow contract is missing")
    if (
        api_workflow_v2_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V2_ID
        or api_workflow_v2_contract.get("result_schema_id") != API_RESULT_SCHEMA_V3_ID
        or api_workflow_v2_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V2_ID
    ):
        raise ContractError("manifest direct Python API v2 schema identities are unsupported")
    api_v2_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v2 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v3 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v2 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v2_schema_refs:
        _verify_digest_ref(
            api_workflow_v2_contract.get(path_key),
            api_workflow_v2_contract.get(digest_key),
            label,
        )
    api_workflow_v3_contract = unresolved.get("python_api_workflow_v3")
    if not isinstance(api_workflow_v3_contract, dict):
        raise ContractError("manifest direct Python API v3 workflow contract is missing")
    if (
        api_workflow_v3_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V3_ID
        or api_workflow_v3_contract.get("result_schema_id") != API_RESULT_SCHEMA_V4_ID
        or api_workflow_v3_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V3_ID
    ):
        raise ContractError("manifest direct Python API v3 schema identities are unsupported")
    api_v3_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v3 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v4 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v3 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v3_schema_refs:
        _verify_digest_ref(
            api_workflow_v3_contract.get(path_key),
            api_workflow_v3_contract.get(digest_key),
            label,
        )
    api_workflow_v4_contract = unresolved.get("python_api_workflow_v4")
    if not isinstance(api_workflow_v4_contract, dict):
        raise ContractError("manifest direct Python API v4 workflow contract is missing")
    if (
        api_workflow_v4_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V4_ID
        or api_workflow_v4_contract.get("result_schema_id") != API_RESULT_SCHEMA_V6_ID
        or api_workflow_v4_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V4_ID
    ):
        raise ContractError("manifest direct Python API v4 schema identities are unsupported")
    api_v4_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v4 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v6 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v4 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v4_schema_refs:
        _verify_digest_ref(
            api_workflow_v4_contract.get(path_key),
            api_workflow_v4_contract.get(digest_key),
            label,
        )
    api_workflow_v5_contract = unresolved.get("python_api_workflow_v5")
    if not isinstance(api_workflow_v5_contract, dict):
        raise ContractError("manifest direct Python API v5 workflow contract is missing")
    if (
        api_workflow_v5_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V5_ID
        or api_workflow_v5_contract.get("result_schema_id") != API_RESULT_SCHEMA_V7_ID
        or api_workflow_v5_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V5_ID
    ):
        raise ContractError("manifest direct Python API v5 schema identities are unsupported")
    api_v5_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v5 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v7 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v5 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v5_schema_refs:
        _verify_digest_ref(
            api_workflow_v5_contract.get(path_key),
            api_workflow_v5_contract.get(digest_key),
            label,
        )
    api_workflow_v6_contract = unresolved.get("python_api_workflow_v6")
    if not isinstance(api_workflow_v6_contract, dict):
        raise ContractError("manifest direct Python API v6 workflow contract is missing")
    if (
        api_workflow_v6_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V6_ID
        or api_workflow_v6_contract.get("result_schema_id") != API_RESULT_SCHEMA_V8_ID
        or api_workflow_v6_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V6_ID
    ):
        raise ContractError("manifest direct Python API v6 schema identities are unsupported")
    api_v6_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v6 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v8 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v6 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v6_schema_refs:
        _verify_digest_ref(
            api_workflow_v6_contract.get(path_key),
            api_workflow_v6_contract.get(digest_key),
            label,
        )
    api_workflow_v7_contract = unresolved.get("python_api_workflow_v7")
    if not isinstance(api_workflow_v7_contract, dict):
        raise ContractError("manifest direct Python API v7 workflow contract is missing")
    if (
        api_workflow_v7_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V7_ID
        or api_workflow_v7_contract.get("result_schema_id") != API_RESULT_SCHEMA_V9_ID
        or api_workflow_v7_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V7_ID
    ):
        raise ContractError("manifest direct Python API v7 schema identities are unsupported")
    api_v7_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v7 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v9 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v7 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v7_schema_refs:
        _verify_digest_ref(
            api_workflow_v7_contract.get(path_key),
            api_workflow_v7_contract.get(digest_key),
            label,
        )
    api_workflow_v8_contract = unresolved.get("python_api_workflow_v8")
    if not isinstance(api_workflow_v8_contract, dict):
        raise ContractError("manifest direct Python API v8 workflow contract is missing")
    if (
        api_workflow_v8_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V8_ID
        or api_workflow_v8_contract.get("result_schema_id") != API_RESULT_SCHEMA_V10_ID
        or api_workflow_v8_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V8_ID
    ):
        raise ContractError("manifest direct Python API v8 schema identities are unsupported")
    api_v8_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v8 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v10 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v8 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v8_schema_refs:
        _verify_digest_ref(
            api_workflow_v8_contract.get(path_key),
            api_workflow_v8_contract.get(digest_key),
            label,
        )
    api_workflow_v9_contract = unresolved.get("python_api_workflow_v9")
    if not isinstance(api_workflow_v9_contract, dict):
        raise ContractError("manifest direct Python API v9 workflow contract is missing")
    if (
        api_workflow_v9_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V9_ID
        or api_workflow_v9_contract.get("result_schema_id") != API_RESULT_SCHEMA_V11_ID
        or api_workflow_v9_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V9_ID
    ):
        raise ContractError("manifest direct Python API v9 schema identities are unsupported")
    api_v9_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v9 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v11 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v9 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v9_schema_refs:
        _verify_digest_ref(
            api_workflow_v9_contract.get(path_key),
            api_workflow_v9_contract.get(digest_key),
            label,
        )
    api_workflow_v10_contract = unresolved.get("python_api_workflow_v10")
    if not isinstance(api_workflow_v10_contract, dict):
        raise ContractError("manifest direct Python API v10 workflow contract is missing")
    if (
        api_workflow_v10_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V10_ID
        or api_workflow_v10_contract.get("result_schema_id") != API_RESULT_SCHEMA_V12_ID
        or api_workflow_v10_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V10_ID
    ):
        raise ContractError("manifest direct Python API v10 schema identities are unsupported")
    api_v10_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v10 workflow schema"),
        ("result_schema_path", "result_schema_sha256", "direct Python API v12 result schema"),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v10 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v10_schema_refs:
        _verify_digest_ref(
            api_workflow_v10_contract.get(path_key),
            api_workflow_v10_contract.get(digest_key),
            label,
        )
    api_workflow_v11_contract = unresolved.get("python_api_workflow_v11")
    if not isinstance(api_workflow_v11_contract, dict):
        raise ContractError("manifest direct Python API v11 workflow contract is missing")
    if (
        api_workflow_v11_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V11_ID
        or api_workflow_v11_contract.get("result_schema_id") != API_RESULT_SCHEMA_V13_ID
        or api_workflow_v11_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V11_ID
    ):
        raise ContractError("manifest direct Python API v11 schema identities are unsupported")
    api_v11_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v11 workflow schema"),
        (
            "result_schema_path",
            "result_schema_sha256",
            "direct Python API v13 result schema",
        ),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v11 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v11_schema_refs:
        _verify_digest_ref(
            api_workflow_v11_contract.get(path_key),
            api_workflow_v11_contract.get(digest_key),
            label,
        )
    api_workflow_v12_contract = unresolved.get("python_api_workflow_v12")
    if not isinstance(api_workflow_v12_contract, dict):
        raise ContractError("manifest direct Python API v12 workflow contract is missing")
    if (
        api_workflow_v12_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V12_ID
        or api_workflow_v12_contract.get("result_schema_id") != API_RESULT_SCHEMA_V14_ID
        or api_workflow_v12_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V12_ID
    ):
        raise ContractError("manifest direct Python API v12 schema identities are unsupported")
    api_v12_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v12 workflow schema"),
        (
            "result_schema_path",
            "result_schema_sha256",
            "direct Python API v14 result schema",
        ),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v12 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v12_schema_refs:
        _verify_digest_ref(
            api_workflow_v12_contract.get(path_key),
            api_workflow_v12_contract.get(digest_key),
            label,
        )
    api_workflow_v13_contract = unresolved.get("python_api_workflow_v13")
    if not isinstance(api_workflow_v13_contract, dict):
        raise ContractError("manifest direct Python API v13 workflow contract is missing")
    if (
        api_workflow_v13_contract.get("schema_id") != API_WORKFLOW_SCHEMA_V13_ID
        or api_workflow_v13_contract.get("result_schema_id") != API_RESULT_SCHEMA_V15_ID
        or api_workflow_v13_contract.get("comparison_schema_id") != API_COMPARISON_SCHEMA_V13_ID
    ):
        raise ContractError("manifest direct Python API v13 schema identities are unsupported")
    api_v13_schema_refs = (
        ("schema_path", "schema_sha256", "direct Python API v13 workflow schema"),
        (
            "result_schema_path",
            "result_schema_sha256",
            "direct Python API v15 result schema",
        ),
        (
            "comparison_schema_path",
            "comparison_schema_sha256",
            "direct Python API v13 comparison schema",
        ),
    )
    for path_key, digest_key, label in api_v13_schema_refs:
        _verify_digest_ref(
            api_workflow_v13_contract.get(path_key),
            api_workflow_v13_contract.get(digest_key),
            label,
        )
    asgi_workflow_contract = (
        unresolved.get("python_asgi_workflow") if isinstance(unresolved, dict) else None
    )
    workload = (
        asgi_workflow_contract.get("first_slice_workload")
        if isinstance(asgi_workflow_contract, dict)
        else None
    )
    if not isinstance(workload, dict):
        raise ContractError("manifest first-slice workload reference is missing")
    _verify_digest_ref(workload.get("path"), workload.get("sha256"), "first-slice workload")
    return manifest


def select_oracle_profile(
    manifest: dict[str, Any], extension_id: str | None = None
) -> dict[str, Any]:
    """Resolve a pinned package overlay while retaining the sole Starlette profile."""
    base = manifest["oracle_profile"]
    if extension_id is None:
        return base
    extension = manifest["oracle_profile_extensions"].get(extension_id)
    if extension is None:
        raise ContractError(f"unknown oracle package extension: {extension_id}")
    return {
        **base,
        "id": extension["id"],
        "packages": {**base["packages"], **extension["added_packages"]},
    }


def select_target_profile(
    manifest: dict[str, Any], extension_id: str | None = None
) -> dict[str, Any]:
    """Resolve the paired target package extension, when the input declares one."""
    base = manifest["target"]
    if extension_id is None:
        return base
    extension = manifest["target_profile_extensions"].get(extension_id)
    if extension is None:
        return base
    if extension.get("base_profile") != base.get("id"):
        raise ContractError(f"target package extension has the wrong base: {extension_id}")
    return {**base, "optional_runtime_packages": extension["added_packages"]}


def _verify_digest_ref(path_value: Any, digest_value: Any, label: str) -> None:
    if not isinstance(path_value, str) or not isinstance(digest_value, str):
        raise ContractError(f"manifest {label} path/digest reference is malformed")
    path = _resolve_repo_file(path_value, f"manifest {label}")
    if sha256_file(path) != digest_value:
        raise ContractError(f"manifest {label} digest is stale: {path_value}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_repo_file(value: str, label: str) -> Path:
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ContractError(f"{label} resolves outside the repository: {value}") from exc
    if not candidate.is_file():
        raise ContractError(f"{label} does not exist: {value}")
    return candidate


def _validate_json_pointer(pointer: str, context: str) -> None:
    for segment in pointer.split("/")[1:]:
        index = 0
        while index < len(segment):
            if segment[index] == "~":
                if index + 1 >= len(segment) or segment[index + 1] not in "01":
                    raise ContractError(f"{context} has an invalid RFC 6901 escape: {pointer}")
                index += 2
            else:
                index += 1


def _validate_unique_ids(rows: list[dict[str, Any]], key: str, context: str) -> None:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise ContractError(f"{context} contains duplicate {key} values")


def load_workflow(
    input_path: Path,
    *,
    source_root: Path | None = None,
) -> tuple[dict[str, Any], Path, str, Path]:
    """Load an input-only workflow and verify every local/source reference."""
    workflow_path = input_path if input_path.is_absolute() else ROOT / input_path
    workflow_path = workflow_path.resolve()
    try:
        workflow_path.relative_to(ROOT)
    except ValueError as exc:
        raise ContractError("workflow inputs must live inside the repository") from exc
    if not workflow_path.is_file():
        raise ContractError(f"workflow input does not exist: {workflow_path}")

    workflow = read_json(workflow_path)
    if not isinstance(workflow, dict):
        raise ContractError("workflow input must be a JSON object")
    workflow_schema_id = workflow.get("schema")
    schema_path = WORKFLOW_SCHEMAS.get(workflow_schema_id)
    if schema_path is None:
        raise ContractError(f"unsupported workflow schema: {workflow_schema_id!r}")

    schema = read_json(schema_path)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema exposes several schema-specific exception types.
        raise ContractError(f"workflow schema is invalid: {exc}") from exc
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(workflow),
        key=lambda error: (tuple(str(part) for part in error.absolute_path), error.message),
    )
    if errors:
        details = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise ContractError(f"workflow input does not match its schema: {details}")
    workload_path = _resolve_repo_file(workflow["workload"]["file"], "workload file")
    try:
        workload_path.relative_to((ROOT / "tests/fixtures/workloads").resolve())
    except ValueError as exc:
        raise ContractError("workflow workload must live under tests/fixtures/workloads") from exc
    _validate_unique_ids(workflow["cases"], "case_id", "workflow cases")
    for case in workflow["cases"]:
        if workflow_schema_id in {
            WORKFLOW_SCHEMA_V7_ID,
            WORKFLOW_SCHEMA_V8_ID,
            WORKFLOW_SCHEMA_V9_ID,
            WORKFLOW_SCHEMA_V10_ID,
            WORKFLOW_SCHEMA_V11_ID,
            WORKFLOW_SCHEMA_V12_ID,
            WORKFLOW_SCHEMA_V13_ID,
            WORKFLOW_SCHEMA_V14_ID,
            WORKFLOW_SCHEMA_V15_ID,
            WORKFLOW_SCHEMA_V16_ID,
            WORKFLOW_SCHEMA_V17_ID,
        }:
            try:
                mode = verification_mode(case)
            except FaultContractError as exc:
                raise ContractError(
                    f"invalid fault-contract case {case['case_id']}: {exc}"
                ) from exc
            if mode == "fault-contract":
                actions = case["actions"]
                if case["fault"]["contract"] in {
                    HTTP_REQUEST_FORM_PARSE_CONTRACT,
                    HTTP_REQUEST_JSON_DECODE_CONTRACT,
                }:
                    if (
                        len(actions) != 1
                        or actions[0]["kind"] != "http_request"
                        or not any(
                            observation["kind"] == "http_response"
                            and "status" in observation["selectors"]
                            for observation in actions[0]["observations"]
                        )
                    ):
                        raise ContractError(
                            "JSON body decode fault contract requires one status-observing "
                            "HTTP request"
                        )
                elif case["fault"]["contract"] in {
                    HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_CONTRACT,
                    HTTP_FRONTEND_LOOKUP_VALUE_ERROR_CONTRACT,
                    HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_CONTRACT,
                    HTTP_FRONTEND_LOOKUP_OS_ERROR_CONTRACT,
                }:
                    if (
                        len(actions) != 1
                        or actions[0]["kind"] != "http_request"
                        or not any(
                            observation["kind"] == "http_response"
                            and "status" in observation["selectors"]
                            for observation in actions[0]["observations"]
                        )
                    ):
                        raise ContractError(
                            "frontend lookup fault contract requires one status-observing "
                            "HTTP request"
                        )
                    if case["fault"][
                        "contract"
                    ] == HTTP_FRONTEND_LOOKUP_OS_ERROR_CONTRACT and not any(
                        observation["kind"] == "application_error"
                        and observation["selector"] == "exception"
                        for observation in actions[0]["observations"]
                    ):
                        raise ContractError(
                            "propagated frontend OSError fault requires an exception observation"
                        )
                elif case["fault"]["contract"] == OPENAPI_CACHE_PUBLISH_RETRY_CONTRACT:
                    request_actions = [
                        action
                        for action in actions
                        if action["kind"] == "http_request"
                        and action["scope"]["method"] == "GET"
                        and action["scope"]["path"] == "/openapi.json"
                    ]
                    if len(actions) != 3 or len(request_actions) != 3:
                        raise ContractError(
                            "OpenAPI cache publication fault requires an initial request and "
                            "two later requests to /openapi.json"
                        )
                    first_kinds = {
                        (observation["kind"], observation.get("selector"))
                        for observation in actions[0]["observations"]
                    }
                    if not {
                        ("application_error", "exception"),
                        ("asgi_send", "message_types"),
                    }.issubset(first_kinds) or not any(
                        observation["kind"] == "http_response"
                        and {"status"}.issubset(observation["selectors"])
                        for observation in actions[0]["observations"]
                    ):
                        raise ContractError(
                            "OpenAPI cache publication fault must observe the initial error, "
                            "complete ASGI send, and HTTP status"
                        )
                    if any(
                        not any(
                            observation["kind"] == "http_response"
                            and {"status", "body"}.issubset(observation["selectors"])
                            for observation in action["observations"]
                        )
                        for action in actions[1:]
                    ):
                        raise ContractError(
                            "OpenAPI retry and cache requests must observe response status and body"
                        )
                elif (
                    len(actions) < 2
                    or actions[0]["kind"] != "http_request"
                    or not any(
                        observation["kind"] == "application_error"
                        and observation["selector"] == "exception"
                        for observation in actions[0]["observations"]
                    )
                    or not any(
                        action["kind"] == "http_request"
                        and any(
                            observation["kind"] == "http_response"
                            and "status" in observation["selectors"]
                            for observation in action["observations"]
                        )
                        for action in actions[1:]
                    )
                ):
                    raise ContractError(
                        "fault-contract route recovery requires an initial HTTP application-error "
                        "observation followed by a status-observing HTTP request"
                    )
        if workflow_schema_id in {
            WORKFLOW_SCHEMA_ID,
            WORKFLOW_SCHEMA_V3_ID,
            WORKFLOW_SCHEMA_V4_ID,
            WORKFLOW_SCHEMA_V5_ID,
            WORKFLOW_SCHEMA_V6_ID,
            WORKFLOW_SCHEMA_V7_ID,
            WORKFLOW_SCHEMA_V8_ID,
            WORKFLOW_SCHEMA_V9_ID,
            WORKFLOW_SCHEMA_V10_ID,
            WORKFLOW_SCHEMA_V11_ID,
            WORKFLOW_SCHEMA_V12_ID,
            WORKFLOW_SCHEMA_V13_ID,
            WORKFLOW_SCHEMA_V14_ID,
            WORKFLOW_SCHEMA_V15_ID,
            WORKFLOW_SCHEMA_V16_ID,
            WORKFLOW_SCHEMA_V17_ID,
        }:
            _validate_unique_ids(case["actions"], "action_id", f"actions in {case['case_id']}")
            if workflow_schema_id in {
                WORKFLOW_SCHEMA_V12_ID,
                WORKFLOW_SCHEMA_V13_ID,
                WORKFLOW_SCHEMA_V14_ID,
                WORKFLOW_SCHEMA_V15_ID,
                WORKFLOW_SCHEMA_V16_ID,
                WORKFLOW_SCHEMA_V17_ID,
            } and any(action["kind"] == "testclient_request" for action in case["actions"]):
                if workflow.get("oracle_profile_extension") != "testclient":
                    raise ContractError(
                        "testclient_request actions require the paired TestClient profile"
                    )
                if any(action["kind"] == "lifespan" for action in case["actions"]):
                    raise ContractError(
                        "testclient_request owns its lifecycle; do not also declare "
                        "a lifespan action"
                    )
            if workflow_schema_id in {
                WORKFLOW_SCHEMA_V3_ID,
                WORKFLOW_SCHEMA_V4_ID,
                WORKFLOW_SCHEMA_V5_ID,
                WORKFLOW_SCHEMA_V6_ID,
                WORKFLOW_SCHEMA_V7_ID,
                WORKFLOW_SCHEMA_V8_ID,
                WORKFLOW_SCHEMA_V9_ID,
                WORKFLOW_SCHEMA_V10_ID,
                WORKFLOW_SCHEMA_V11_ID,
                WORKFLOW_SCHEMA_V12_ID,
                WORKFLOW_SCHEMA_V13_ID,
                WORKFLOW_SCHEMA_V14_ID,
                WORKFLOW_SCHEMA_V15_ID,
                WORKFLOW_SCHEMA_V16_ID,
                WORKFLOW_SCHEMA_V17_ID,
            }:
                lifespan_positions = [
                    index
                    for index, action in enumerate(case["actions"])
                    if action["kind"] == "lifespan"
                ]
                if len(lifespan_positions) > 1:
                    raise ContractError(
                        f"case {case['case_id']} may contain only one lifespan action"
                    )
                if lifespan_positions and lifespan_positions[0] != 0:
                    raise ContractError(f"lifespan action must be first in case {case['case_id']}")
            for action in case["actions"]:
                if action["kind"] == "lifespan":
                    continue
                if workflow_schema_id == WORKFLOW_SCHEMA_V5_ID and action["kind"] == "http_request":
                    receive_mode = action.get("receive_mode")
                    timeout_present = "cancel_after_seconds" in action
                    has_cancellation_observation = any(
                        observation["kind"] == "asgi_cancellation"
                        for observation in action["observations"]
                    )
                    if receive_mode == "wait_until_cancelled" and not timeout_present:
                        raise ContractError(
                            "wait_until_cancelled requires a finite cancel_after_seconds timeout"
                        )
                    if timeout_present:
                        timeout = action["cancel_after_seconds"]
                        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                            raise ContractError(
                                "cancel_after_seconds must be a positive finite number"
                            )
                        try:
                            finite_timeout = math.isfinite(float(timeout))
                        except (OverflowError, ValueError):
                            finite_timeout = False
                        if not finite_timeout or float(timeout) <= 0:
                            raise ContractError(
                                "cancel_after_seconds must be a positive finite number"
                            )
                    if timeout_present and receive_mode != "wait_until_cancelled":
                        raise ContractError(
                            "cancel_after_seconds is permitted only with wait_until_cancelled"
                        )
                    if has_cancellation_observation and receive_mode != "wait_until_cancelled":
                        raise ContractError(
                            "asgi_cancellation observations require wait_until_cancelled"
                        )
                if (
                    action["kind"] == "websocket_session"
                    and action["receive_events"][-1]["type"] != "websocket.disconnect"
                ):
                    raise ContractError(
                        "WebSocket receive events must end with an explicit websocket.disconnect"
                    )
                if (
                    workflow_schema_id
                    in {
                        WORKFLOW_SCHEMA_V6_ID,
                        WORKFLOW_SCHEMA_V7_ID,
                        WORKFLOW_SCHEMA_V8_ID,
                        WORKFLOW_SCHEMA_V9_ID,
                        WORKFLOW_SCHEMA_V10_ID,
                        WORKFLOW_SCHEMA_V11_ID,
                        WORKFLOW_SCHEMA_V12_ID,
                        WORKFLOW_SCHEMA_V13_ID,
                        WORKFLOW_SCHEMA_V14_ID,
                        WORKFLOW_SCHEMA_V15_ID,
                        WORKFLOW_SCHEMA_V16_ID,
                        WORKFLOW_SCHEMA_V17_ID,
                    }
                    and action["kind"] == "websocket_conversation"
                ):
                    sessions = {session["session_id"] for session in action["sessions"]}
                    if len(sessions) != len(action["sessions"]):
                        raise ContractError(
                            "WebSocket conversation session IDs must be unique in "
                            f"{case['case_id']}"
                        )
                    selectors = {
                        observation["selector"]
                        for observation in action["observations"]
                        if observation["kind"] == "websocket"
                    }
                    if selectors != {"event_order", "messages"}:
                        raise ContractError(
                            "WebSocket conversations must compare both event_order and messages"
                        )
                    received_sessions = {
                        step["session_id"]
                        for step in action["steps"]
                        if step["kind"] == "receive_next"
                    }
                    if received_sessions != sessions:
                        raise ContractError(
                            "WebSocket conversations must receive an observable event from each "
                            "session"
                        )
                    states = {session_id: "new" for session_id in sessions}
                    for step in action["steps"]:
                        session_id = step["session_id"]
                        if session_id not in states:
                            raise ContractError(
                                "WebSocket conversation step references unknown session "
                                f"{session_id!r}"
                            )
                        state = states[session_id]
                        kind = step["kind"]
                        if kind == "connect":
                            if state != "new":
                                raise ContractError(
                                    f"WebSocket session {session_id!r} connects more than once "
                                    "or after activity"
                                )
                            states[session_id] = "connected"
                        elif kind == "disconnect":
                            if state != "connected":
                                raise ContractError(
                                    f"WebSocket session {session_id!r} disconnects outside "
                                    "its active interval"
                                )
                            states[session_id] = "closed"
                        elif state != "connected":
                            raise ContractError(
                                f"WebSocket session {session_id!r} has activity before "
                                "connect or after disconnect"
                            )
                    incomplete = sorted(
                        session_id for session_id, state in states.items() if state != "closed"
                    )
                    if incomplete:
                        raise ContractError(
                            "WebSocket conversation sessions must each connect and disconnect: "
                            + ", ".join(incomplete)
                        )
                for observation in action["observations"]:
                    if observation["kind"] == "openapi":
                        for pointer in observation["json_pointers"]:
                            _validate_json_pointer(
                                pointer, f"{case['case_id']}:{action['action_id']}"
                            )
        elif workflow_schema_id in API_WORKFLOW_SCHEMA_IDS:
            _validate_unique_ids(case["probes"], "probe_id", f"probes in {case['case_id']}")

        if source_root is not None:
            for evidence in case["source_evidence"]:
                source_path = (source_root / evidence["path"]).resolve()
                try:
                    source_path.relative_to(source_root.resolve())
                except ValueError as exc:
                    raise ContractError(
                        "source evidence resolves outside the pinned source tree: "
                        f"{evidence['path']}"
                    ) from exc
                if not source_path.is_file():
                    raise ContractError(f"source evidence does not exist: {evidence['path']}")
                if workflow_schema_id in API_WORKFLOW_SCHEMA_IDS:
                    if sha256_file(source_path) != evidence["sha256"]:
                        raise ContractError(
                            f"direct API source evidence digest is stale: {evidence['path']}"
                        )

    return workflow, workflow_path, sha256_file(workflow_path), workload_path
