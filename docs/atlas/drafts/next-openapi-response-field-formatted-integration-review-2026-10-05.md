# Independent formatted OpenAPI integration review

2026-10-05. Reviewer: `/root/dependency_records_native` (Sol).

## Result and scope

Source-only integration verification is closed. All three active Rust files are
byte-identical to Rustfmt output of the reviewed frozen version-2 proposals.
No additional active Rust, Python facade, admitted input or dependency change
was found against `bbac9b5e16aace4a29bfd2521ba623eb4f2b55fe`.

The reviewer ran only the source formatter on stdin and Git/file static checks.
No frozen original or active source was modified. No compiler, builder,
installer, application import/execution, parity process, unit framework or
native binary read was performed. The parent's broader static stage subsequently
closed with exit 2 at its final saved-benchmark receipt check; that chronology
is recorded below. No full-static-success, compatibility or installed-binary
claim follows from formatting.

## Reviewed proposal and formatted identities

Combined v2 patch:
`/private/tmp/fastapi-rs-next-openapi-combined-v2.patch`, SHA256
`ec57db0d992b38325f3e2f8040843342e67c11b367ca95db3def7397d3950be1`.
The preceding independent source review is
`/private/tmp/fastapi-rs-next-openapi-combined-independent-review-2026-10-05.md`,
SHA256 `ba1a4122afea7e93933ac889f5b81566bd9b4d941bd53f6356520c32468b3e21`.

| Source | Frozen v2 proposal SHA256 | Formatted output and active SHA256 | Active bytes |
| --- | --- | --- | ---: |
| application_runtime.rs | `3e64ac2c566682ead3dd9172ca30df51195358efc142f61dd52c1a9cd3df437b` | `d1bdcd3f66118c38df96fbb75528264d298335d27f2ca275dcc699bdc4a280a2` | 460898 |
| response_field.rs | `3ef5dd24768f2ab096aec349ed6d17895a7844531e8dd1840e69f5412482c467` | `3ef5dd24768f2ab096aec349ed6d17895a7844531e8dd1840e69f5412482c467` | 17956 |
| openapi.rs | `483e4ed5b7851f07468a328d6ec7cf0961b9af19ee969d42370aa26d21e7dfcf` | `ce1258b83ef4728aca7ad86fc038bac740022ea687b0a3b795eff629d8a1838f` | 53816 |

Each frozen input hash was checked before formatting and its bytes checked
again afterward. Formatter stderr was empty. Its stdout was saved only in the
fresh temporary directory
`/private/tmp/fastapi-next-openapi-formatted-integration-qx9rh2sj/`.

Formatter invocation per file used frozen bytes on stdin:
`rustfmt --emit stdout --config-path /Users/lazytrot/work/fastapi-rs/rustfmt.toml`.
The repository-selected formatter reported
`rustfmt 1.9.0-stable (48a229ceae 2026-09-01)`.
The toolchain file selects Rust 1.98.1; the config selects edition 2024,
100-column width, four spaces, Unix newlines and Default small heuristics.

Config SHA256: `ecbbdfd04d20e0eeb124dff8d6d4f19bab6e00a9fb18c6bcc94fce476f36c0c3`.
Toolchain file SHA256: `c910997cb152c6dc8ed13b1fdf9fa28a4ed30d6776123e27dd6170e5c66067a0`.
Formatter readback receipt: `format-readback.json` in that temporary directory,
SHA256 `d40861613920b6c00f9f94e928890a1d8e66533d6d5e30845fff9161e3b00827`.

## Diff ownership and unchanged files

At readback HEAD was still the admitted `bbac9b5` commit. Git's diff against
that commit contained exactly these three non-documentation paths:

- `fastapi-rs/src/application_runtime.rs`
- `fastapi-rs/src/openapi.rs`
- `fastapi-rs/src/response_field.rs`

All other tracked paths were unchanged except the draft proposal index README.
The unchanged category counts checked against the complete tracked diff were:
16 other Rust files; 32 files in the Python facade tree; 1,100 fixture-tree
files, including active recipes, workloads and generated artifacts; eight
Cargo/Python dependency and formatter/toolchain manifests; and `metadata.yaml`.
Thus identities/policy/admitted selectors, dependency pins and facade source
were not changed as part of the code integration.

Nonignored untracked files were confined to `docs/atlas/drafts/`: the archived
reviews/designs and the inactive OpenAPI-validation response proposal. That
draft's Python/YAML files are outside active input directories. The parent was
archiving documentation concurrently; this audit does not mistake those files
for active admission or expand the allowed three-code-file delta.

`git diff --check bbac9b5e16aace4a29bfd2521ba623eb4f2b55fe` exited 0 with empty
stdout/stderr. Source-scope readback receipt: `source-scope-readback.json` in the
temporary directory, SHA256
`0331fd2b9ac1c73a05209fbab7d28397e2c9b97bbb9e49aab1c50ccd3a7ada3f`.

## Parent formatter receipt and remaining gates

The parent reported initial `make fmt` exit 2 for formatting only, followed by
successful `cargo fmt --all`. Its preserved initial formatter log is
`parity-results/next-openapi-response-field-initial-fmt.log` (9,258 bytes),
SHA256 `d821a1f3e94dd27109c5612c0882f74a84ad3e9b3f42b67abdaf58fde373447d`.
This review independently verifies the resulting Rust source identities; it
does not infer a compiler/static-contract exit from that log.

The parent subsequently reported the final static stage closed with exit 2
only at `benchmark-contract-check`. Log readback confirms Clippy completion
in 4.09 seconds, the 204-distribution graph success, valid benchmark declarations
for seven workloads/unique IDs, and then the saved suite rejection:
`parity comparison does not reference the current manifest` (lines 66–70).
The parent reports fmt, strict Clippy, API/metadata, boundary and Rust/Pydantic
dependency checks passed earlier in that stage. The old saved benchmark suite
precedes the admitted next-three links; no source-contract or saved-result
weakening is proposed. A fresh seven-workload suite and repeated final static
closure remain pending. The overall static stage is not reported as exit 0.

Preserved log: `parity-results/next-openapi-response-field-final-static.log`,
4,703 bytes, SHA256
`252225e6132ddbddb78658c07ce27f200cb089276f61cae9183d84fe5c44a53b`.
The reviewer read the log and did not rerun any checks or compiler.

Implementation commit, fresh normal build, identity-checked 206-case normal
comparison, separate normal/fault measurements, normal restoration and the
deferred benchmark/final-static gates remain distinct. Source-sensitive limits
recorded in the combined review remain unchanged by Rustfmt.
