# Developer-tool dependency profile

This inventory records the recursive hash-locked developer-tools-cpython-3.12.13 profile for CPython 3.12.13. Its direct pins come from [`requirements/developer-tools-cpython-3.12.13.in`](../requirements/developer-tools-cpython-3.12.13.in); the generated lock is [`requirements/developer-tools-cpython-3.12.13.lock`](../requirements/developer-tools-cpython-3.12.13.lock).

These packages are developer/build tools and their transitive support libraries. They are separate from the FastAPI-RS target runtime lock and are not product runtime dependencies. Maturin remains in the separate, hash-locked build-tools profile.

Regenerate the lock and this inventory with `make developer-tools-inventory-update`; check the reviewed data without network access with `make developer-tools-inventory-check`. Install the locked tool environment with `make developer-tools-prepare`.

The uv resolver is pinned at 0.11.29; updates exclude releases published after 2026-10-13T23:59:59Z. Only binary distributions are admitted, and every eligible artifact is SHA-256 hashed in the lock.

| Package | Locked version | Role | Marker | Resolved through | Purpose | Python/native implementation | License | Hashes |
|---|---:|---|---|---|---|---|---|---:|
| [attrs](https://pypi.org/project/attrs/26.1.0/) | 26.1.0 | dev | — | jsonschema, referencing | Provides compact class and attribute helpers used by JSON Schema validation and reference resolution. | Pure Python distribution. | [MIT](https://pypi.org/pypi/attrs/26.1.0/json) | 2 |
| [jsonschema](https://pypi.org/project/jsonschema/4.26.0/) | 4.26.0 | dev | — | direct input | Validates parity recipes, process workflows, and benchmark declarations against JSON Schema. | Pure Python validator and bundled schema data. | [MIT](https://pypi.org/pypi/jsonschema/4.26.0/json) | 2 |
| [jsonschema-specifications](https://pypi.org/project/jsonschema-specifications/2025.9.1/) | 2025.9.1 | dev | — | jsonschema | Supplies the JSON Schema metaschemas and vocabularies used by jsonschema. | Pure Python package with JSON schema data. | [MIT](https://pypi.org/pypi/jsonschema-specifications/2025.9.1/json) | 2 |
| [PyYAML](https://pypi.org/project/pyyaml/6.0.3/) | 6.0.3 | dev | — | direct input | Loads and emits the reviewed YAML metadata, dependency declarations, and input recipes. | Python package with a native C accelerator in supported wheels. | [MIT](https://pypi.org/pypi/pyyaml/6.0.3/json) | 73 |
| [referencing](https://pypi.org/project/referencing/0.37.0/) | 0.37.0 | dev | — | jsonschema, jsonschema-specifications | Resolves JSON Schema resources and references for jsonschema. | Pure Python distribution. | [MIT](https://pypi.org/pypi/referencing/0.37.0/json) | 2 |
| [rpds-py](https://pypi.org/project/rpds-py/2026.9.1/) | 2026.9.1 | dev | — | jsonschema, referencing | Provides persistent data structures used by JSON Schema resource and reference registries. | Python bindings to a Rust implementation, shipped as native wheels. | [MIT](https://pypi.org/pypi/rpds-py/2026.9.1/json) | 128 |
| [ruff](https://pypi.org/project/ruff/0.14.14/) | 0.14.14 | dev | — | direct input | Formats and lints the Python facade, scripts, and active workloads in make fmt and make format. | Rust-native formatter/linter distributed through a Python wheel. | [MIT](https://pypi.org/pypi/ruff/0.14.14/json) | 19 |
| [typing-extensions](https://pypi.org/project/typing-extensions/4.16.0/) | 4.16.0 | dev | python_full_version < '3.13' | referencing | Provides typing backports required by referencing on the pinned Python 3.12 interpreter. | Pure Python distribution. | [PSF-2.0](https://pypi.org/pypi/typing-extensions/4.16.0/json) | 2 |
| [uv](https://pypi.org/project/uv/0.11.29/) | 0.11.29 | dev, build | — | direct input | Resolves hash-locked Python profiles and creates or synchronizes isolated development and build environments. | Rust-native package and environment manager distributed as a platform-specific Python wheel. | [MIT OR Apache-2.0](https://pypi.org/pypi/uv/0.11.29/json) | 19 |

Transitive parent paths are taken from uv's `# via` records in the lock. The Python marker on `typing-extensions` keeps that conditional package in the universal CPython 3.12 lock; the preparation command verifies the patch-level interpreter.
