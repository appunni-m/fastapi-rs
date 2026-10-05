# Narrow runtime-boundary checker proposal

TMP-only author freeze, 2026-10-05. No active file was changed and no checker,
application, build, unit framework or synthetic execution was run. Parent
owns application and subsequent canonical static CLI verification.

- Scan every FastAPI module literal with `finditer`; an allowed first pyclass
  literal can no longer suppress a later import in the same Rust file.
- Recognize the exact value position of pyclass `module` metadata and direct
  `set_item`/`setattr` assignments to literal `module` or `__module__` keys.
  The old whole-line/whole-attribute match could allow a different literal on
  the same line. The new exception is tied to the scanned offset.
- A fixed `const NAME: &str = "fastapi..."` is allowed only if every matching
  identifier occurrence, apart from its declaration, is the direct value of
  one of those metadata assignments. Importing it, aliasing it, or any other
  use disqualifies its declaration literal and fails the boundary. This uses
  no whitelist of constant names. Identifier matching is conservative: even
  a nonmetadata comment/string mention rejects the exception.
- Logger data is allowed only in the direct
  `py.import("logging")?.getattr("getLogger")?.call1(("fastapi",))` chain
  (with ordinary whitespace, and `py` or `python` receiver). No logger alias,
  name constant, alternate call path or module-name family is exempted.
  Pinned `fastapi/logger.py:1-3` imports logging and calls
  `logging.getLogger("fastapi")`; the name is data, not an original import.
- The original literal matcher, dynamic Python execution detector, declared
  dependency policy, installed-package check and every Python facade rule are
  unchanged. There is no string splitting or broad import allowlist.

Read-only source inspection shows the new MODEL_MODULE declaration's four
uses are direct `module`/`__module__` metadata assignments. Native email's
logger chain is the direct source-equivalent form. Existing direct metadata
also includes the enum's `module` option in security.rs. Actual illegal
literal imports remain unmatched by these value exceptions; constant imports
invalidate the all-uses condition. This is static reasoning, not a run claim.

The original failure remains in
`parity-results/openapi-final-model-static.log`; no output was removed or
reclassified. Parent review and the canonical source-only boundary CLI must
close the gate after applying the narrow proposal.

| File | SHA256 |
|---|---|
| check_target_runtime_boundary-base.py | 7c0a8c87b96207c3aa63068dbcd497eb9366c6f2a0ca728c7d69a564bf911363 |
| check_target_runtime_boundary.py | cce45ff5073b9f3923bd29a591cbe31a4a1ad005e64a927ea1c54ccfed831f11 |
| runtime-boundary-checker.patch | bf5991a9a8eb90f499e7c99f762386012d9dfa3b0fce7376a74f89c3317ed690 |
