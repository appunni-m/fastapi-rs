# All-stage pinned builder: independent static review

No concrete blocker found for the selected physical workspace and persistent
fault paths. This is source/AST reading clearance, **not** a successful build,
editable installation, import, or parity result. No active or sibling files,
native bytes, products, compilers, or test frameworks were changed or run.

Bound proposal: script `6a196d587fc5b66742ceb3a55f7461b40fa224b8dc1f6484278cd0b12342cc17`,
patch `6901a43ea1fbc35f5bd16a63165ff402f053faf6b6e3007d22381a3e156038fd`,
author note `140a4fc32463b0bc63e1fa585ff8e611268212ddd31c4ae68f8e062f4ae50298`,
base `3f5626af2fc01fac58060ccc4d90286971c4129b603cc813547d0f8df956148a`.

- Physical member manifests retain source bytes and relative member dependency
  paths. Metadata checks overlay workspace/member ownership, canonical original
  Rust target paths, and the sole selected sibling implementation manifest.
- Both editable phases receive the physical member manifest, selected
  interpreter/target directory, locked/offline flags, and the same normal/fault
  feature vector as final Cargo compilation. Inherited compiler flags remain
  present. Arguments use subprocess lists; shlex.join feeds the backend's
  shlex.split without shell evaluation. Custom --cargo applies to standalone
  Cargo calls; Maturin itself resolves cargo from PATH.
- uv still requests editable ROOT, so its source URL is ROOT. The overlay
  pyproject changes only Python source: stable absolute ROOT source for normal,
  persistent target/fault-injection/python for fault. The fault native package
  is physical; only facade entries link to original sources. Neither editable
  path depends on temporary workspace retention; fault native writes have their
  own destination.
- ROOT lockfile restoration remains in finally, including failed subprocess
  paths. Temporary workspace cleanup, final atomic copy, fault venv validation,
  and isolated activation remain intact.

Pinned primary sources support both-phase argument forwarding and accepted
options: [Maturin PEP517 commands](https://github.com/PyO3/maturin/blob/v1.14.1/src/commands/pep517.rs),
[project layout](https://github.com/PyO3/maturin/blob/v1.14.1/src/project_layout.rs),
and [editable .pth writer](https://github.com/PyO3/maturin/blob/v1.14.1/src/module_writer/mod.rs#L429).
The installed backend was read without import; it forwards config arguments
at metadata and wheel hooks.

AST syntax/no-shell checks and detached-base patch applicability pass. Active
formatted script `79d0d9ce527717a21a7dff957bb93c8384f7dce3855ff61c4c29083184fc46f3`
has the same AST; active apply-check fails because it is already applied.
Static receipt SHA256: `e7e6ff758c6f215242be3c98e6d3d3c0ca495f8044ce359fc2d428fa77498f3f`.

Parent-owned actual builds must still establish metadata selection, ROOT
direct_url, stable .pth after temporary deletion, normal/fault native identity,
and lockfile/source equality. The preserved bootstrap and moving-sibling build
failures provide no replacement-build or parity claim.
