# Correct native Annotated subscription

2026-10-05. The first native build at51fa96a compiled, but actual isolated target
initialization failed with AttributeError: type object Annotated has no attribute
__getitem__. No target result artifact or parity comparison was produced. New3
and direct4 helpers failed; full206 orchestration was stopped after repeated
identical bootstrap failures. Partial logs/output are retained. They do not prove
any target parity,210-case completion, or a source-tree mutation.

Root traced this to the main graph's Annotation::MinLength subscription.
CPython3.12.13 typing.py:2067,2120 defines Annotated as a class with
__class_getitem__(cls, params). It accepts the existing single tuple containing
annotation and Field(min_length=1) metadata. Root changed exactly that method
name to __class_getitem__; every descriptor, argument, ownership path and other
Rust source remains unchanged. The frozen main proposal called the wrong member;
Clippy cannot establish Python runtime member availability. Schema's generic
PyObject_GetItem subscription already uses Python's class-subscription dispatch.

Prior main hash b9740531a55c3b8d54a72a5a6ab0e0e9dc4a0cc29985cac438e903d1f52706ec.
Corrected main hash 0f006133186e876f7359fad12b6389c7af100dd2bbdbdf8be3ef6454c2c02129.
Pinned CPython typing.py hash be92d60fb8382bb29ead21c128825d7c96d0e8c915b44f840791e49f5a8d554c.
Root independently proved the current file equals the exact committed prior file
with this one string replacement. No helper Python source, comparator change,
normalization, source import, dependency/facade change or unit test was introduced.

Fresh format/Clippy and actual build/import remain required. The targeted new3
gate will run before the whole206/direct4 reruns, each in new output directories;
failed initial directories remain untouched. Coverage, faults and benchmark
measurement are still pending for the repaired revision.
