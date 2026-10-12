# Parity workload source check

`make parity-workload-check` screens the Python sources referenced by the active
YAML recipes in `tests/fixtures/input-recipes/parity/`. It reads each recipe
through the existing workflow-schema validator, resolves the referenced source
under `tests/fixtures/workloads/`, and parses that source with Python's AST. The
check does not import or execute workload code. `make parity-validate` runs this
gate before validating the selected materialized workflow.

The gate reports direct imports from `pytest` or `unittest`, imports whose
dotted module path contains `tests` or a `test_*` component, and `assert`
statements at module scope or inside functions named `test_*`. Application
functions and their helpers may use `assert` when it is part of the synthetic
application's runtime behavior. The current active workload set has five such
application assertions; none is treated as a test-harness assertion.

This is a narrow source heuristic. It catches common test-harness constructs,
but it does not establish that workloads contain no copied upstream material.
Renamed or rewritten test logic, indirect or dynamically computed imports,
assertions in helpers without test-like names, and other equivalent mechanisms
can evade it. The gate does not search application response literals for
expected outputs: those literals are workload behavior supplied to both
implementations. Recipe observations, not workload response values, define
what the comparator checks. Only workload sources referenced by active recipes
are inspected.
