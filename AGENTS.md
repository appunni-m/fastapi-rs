# Project rules

- Pin FastAPI 0.141.1, Starlette 1.6.0, Starlette-RS, Python, and Pydantic.
  Starlette 1.6 is sole oracle; sibling owns generic behavior.
- `metadata.yaml` owns identities, policy, and reviewed API overlays. Generate
  candidates/inventory from pinned source; keep classifications and fixture
  mappings in reviewed files. Run `make metadata-check` after changes.
- Complete the manifest before implementation/claims: exports, signatures,
  aliases, deprecations, requirements, operations, identities, and isolated
  Python/ASGI runner/comparator. Inventory is discovery, not support evidence.
- Expose `fastapi`; original FastAPI is source-oracle/dev-only, with zero
  target runtime dependency or import. Python runtime files allow only direct
  native re-exports and literal `__all__`; no helpers, functions, `if`/`else`,
  loops, or fallback behavior. Rust owns FastAPI behavior and control flow.
  Put it in `fastapi-rs/`; limit `fastapi-rs-py/` to PyO3 binding and
  value conversion. Enforce with `make python-facade-check`.
- For Rust changes, forbid unsafe and blanket lint suppressions; run
  `make fmt clippy` and static contract checks. Keep zero unit tests; never run
  pytest, unittest, or Cargo test. Verify with live identity-checked parity
  and static contract checks.
- Map recursive dependencies by feature, purpose, version, native/language
  parts, license, and runtime/optional/build/dev role. Author parity recipes as
  YAML under `tests/fixtures/input-recipes/`; include no expected outputs.
  After recipe edits run `make parity-inputs parity-index-update parity-validate`
  and exercise public interfaces in identity-checked isolated processes.
- After atlas or exclusion changes run `make compatibility-atlas-update`.
  Keep drafts outside active inputs; reviewed schemas cover Python/ASGI. Compare
  HTTP, WebSocket, lifecycle, validation, serialization, and OpenAPI; expose
  unsupported cases and normalize only documented differences.
- Bench only equivalent work after parity; declare boundary, gate, warmups,
  samples, environment, and ASGI/server/facade/native costs. Preserve notices;
  map every public API to manifest/index and never weaken the contract.

<!-- BEGIN KATA (managed by `kata init --with-agents`) -->
Kata is the system of record for intent.

- Never `kata delete` or `kata purge` without explicit user authorization.

~~~dot
digraph kata {
  rankdir=TB; node [shape=box];

  arrive   [shape=diamond label="Work arrives"];
  search   [label="Search first:\nkata search \"<terms>\" --agent\nReuse an open issue or create one."];
  route    [shape=diamond label="Work it, or delegate it?"];

  subgraph cluster_work {
    label="";
    claim  [label="On claim or start, mark it tracked:\nkata meta set <ref> work.attention ok"];
    branch [label="If the work happens on a dedicated branch, stamp it once:\nkata meta set <ref> work.branch <branch>\nor bind at creation:\nkata create ... --meta work.branch=<branch> --idempotency-key <key>"];
    live   [label="Keep state current:\nkata meta set <ref> work.attention stuck|needs-human|ok\nkata meta set <ref> work.attention_msg \"<why>\"\nstuck = blocked; needs-human = input/review; ok = unblocked.\nRequest attention:\nkata notify <ref> --to <actor>[/<teammate>] --message <reason>"];
    claim -> branch -> live;
  }

  subgraph cluster_delegate {
    label="";
    fanout [label="Tracked children: --parent <ref>, --meta work.branch=<branch>,\n--idempotency-key <key>, --json; capture .issue.short_id.\nSubagents: distinct KATA_TEAMMATE and\nKATA_INBOX_USER=<actor>/<teammate>; keep the actor.\nRead requests: kata inbox --for <actor>[/<teammate>].\nAfter handling: kata notify <ref> --to <actor>[/<teammate>] --clear."];
    join   [label="Join with kata wait <refs> --until attention --any\nMatches needs-human or stuck; a close also completes the wait,\nand the reported reason distinguishes which. Use --timeout so a\nwrapper can tell timeout from satisfaction."];
    coord  [label="Read delegated work.*; never write it."];
    fanout -> join -> coord;
  }

  done     [shape=diamond label="Verified complete?"];
  close    [label="kata close <ref> --done\nwith a message and evidence"];
  review   [label="kata label add <ref> needs-review\nplus a comment on what remains"];
  park     [shape=diamond label="Park it?"];
  schedule [label="kata schedule <ref> <date-or-time>\nsets scheduled_on; clear with -"];
  someday  [label="kata meta set <ref> someday true --json-value\nclear with kata meta unset <ref> someday"];

  arrive -> search -> route;
  route -> claim   [label="work it"];
  route -> fanout  [label="delegate it"];
  route -> park    [label="record only"];
  live  -> done;
  coord -> done;
  done -> close    [label="yes"];
  done -> park     [label="no"];
  park -> schedule [label="start date known"];
  park -> someday  [label="start date unknown"];
  park -> review   [label="needs review"];
}
~~~

Parent links group work; they do not gate readiness, but a parent cannot close with open children.
Use --blocks <dependent> / --blocked-by <prerequisite> only for real prerequisites; they gate kata ready.
Use --related <ref> for context only. kata wait observes state without requiring a dependency edge.

One writer per key: only write your own work.*. Ignore work.* on closed issues; never write it there.
Before stopping, close completed work or update both work.attention and work.attention_msg for the handoff.

Schedule/someday defer work; deadlines don’t. kata deadline <ref> <date-or-time> sets deadline_on without changing readiness.
Reached schedules and deadlines use notify.* for the current owner, or the author when unowned; clear with kata notify <ref> --to <recipient> --clear.
<!-- END KATA -->
