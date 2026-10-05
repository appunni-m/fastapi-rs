# All-stage selected-source builder proposal

TMP-only freeze, 2026-10-05. No active file, sibling, source pin or binary was
changed. No build, package installation, app, parity or unit framework was run.
Only local primary backend/source reads, CLI help, AST syntax parsing and
patch applicability inspection support this prospective change.

- Cargo overlay members are physical directories with byte-copied Cargo.toml
  files; their other entries link to the original source. Cargo cannot resolve
  a symlinked member manifest back into the moving original workspace.
- The overlay pyproject preserves project/runtime/build metadata and replaces
  only python-source with a stable absolute path. Normal uses ROOT source;
  fault uses persistent target/fault-injection/python, with a physical native
  package and source-linked facades. Its initializer bytes are copied from ROOT.
  Editable paths survive temporary Cargo workspace deletion; fault Maturin
  writes cannot overwrite the normal native package.
- uv still installs `--editable ROOT`, retaining ROOT editable direct_url.
  Explicit maturin.build-args sends the physical overlay member manifest,
  selected target directory/interpreter, locked/offline flags and the same
  normal/fault feature list used by final Cargo build. Both metadata and
  editable-wheel hooks receive these arguments. Existing environment flags
  are copied unchanged, with selected CARGO_TARGET_DIR and PYO3_PYTHON applied.
- Metadata verification now requires copied member manifest bytes equal ROOT,
  workspace ownership of the physical overlay manifest, canonical source
  targets inside the original member, and the selected Starlette-RS manifest.
  Existing workspace/feature verification, final atomic installation, isolated
  fault activation and ROOT Cargo.lock restoration remain active.
- There is no editable skip, handwritten distribution metadata, dependency
  bypass or sibling change. Fresh setup uses the same pinned editable build
  path as repeated setup. Parent owns actual .pth/direct_url/build verification.

Primary evidence: installed Maturin1.14.1 `maturin/__init__.py`35-46,100-110,
230-245 forwards config settings to both metadata and editable wheel CLI.
Local CLI help confirms manifest/locked/offline/interpreter/target-dir/features
and uv config-setting support. Independent peer source review confirms Maturin
selects the pyproject above the physical manifest and normalizes Python source
before editable .pth creation.

The closed original failure is preserved in
`parity-results/openapi-final-model-normal-build-v2.log`, SHA256 `fcea11edc3304c207235fe702a66120f0a413baafe252252718c0e0848b295ec`:
editable prebuild selected moving ../starlette-rs and failed with md5 LowerHex
before the final pinned build. This note does not reclassify that failed build
or claim a successful replacement build. Root review and live build closure
remain required.

| File | SHA256 |
|---|---|
| build_target_extension-base.py | 3f5626af2fc01fac58060ccc4d90286971c4129b603cc813547d0f8df956148a |
| build_target_extension.py | 6a196d587fc5b66742ceb3a55f7461b40fa224b8dc1f6484278cd0b12342cc17 |
| all-stage-pinned-builder.patch | 6901a43ea1fbc35f5bd16a63165ff402f053faf6b6e3007d22381a3e156038fd |
