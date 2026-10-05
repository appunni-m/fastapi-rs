# Annotated bootstrap correction: independent source review

Date: 2026-10-05. Static source review only. No app/model import, builder,
compiler, parity run, native binary read or active edit by this reviewer.

The parent reported that the first graph build at
`51fa96a4ce439502a4878447f545c1e1389890a5` failed at native module bootstrap with
AttributeError while the main helper looked up `typing.Annotated.__getitem__`.
Those failed-run artifacts and the original frozen proposal/reviews remain
unchanged. The prior independent review correctly checked declaration data but
missed this call-shape defect; its static clearance did not establish runtime
attribute availability.

The parent's correction at `2135bee7c6fa558eccb98384acc517c113cd6338` changes
only the MinLength annotation helper's lookup from `__getitem__` to
`__class_getitem__`. Read-only Git diff against 51fa96a confirms that one-line
Rust delta. Corrected active main source SHA256 is
`0f006133186e876f7359fad12b6389c7af100dd2bbdbdf8be3ef6454c2c02129`.

Pinned CPython 3.12.13 `Lib/typing.py:2120–2123` defines
`Annotated.__class_getitem__(cls, params)`. It accepts one tuple of annotation
and metadata and forwards its elements to `_class_getitem_inner`. The native
call's existing `((annotation, metadata),)` outer argument tuple supplies
exactly that one params value. The remaining tuple layers and metadata are
unchanged, including ServerVariable.enum's Field(min_length=1). The source
typing.py SHA256 is
`be92d60fb8382bb29ead21c128825d7c96d0e8c915b44f840791e49f5a8d554c`.

Union and Literal are separate SpecialForm objects with `__getitem__` at
typing.py:516–524; their existing native lookups are valid by source reading
and must not receive a global replacement. The Schema companion already uses
PyObject_GetItem through Bound.get_item for Annotated, which dispatches class
subscription correctly. No companion change is required.

No source-backed blocker was found in the one-line correction. This is bounded
source clearance of the lookup and argument shape, not successful model
construction, module import or compatibility evidence. Parent owns the fresh
build and new source/target artifact directory after the preserved failed stage,
then all graph/new-case/prior-regression gates. Earlier source descriptor counts
and hashes remain historical checks of their exact frozen proposal, not proof
of the corrected live source's behavior.
