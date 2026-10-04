# Starlette-RS pin audit: 5345783

FastAPI-RS advances its reviewed Starlette-RS contract pin from
`1a271cd650a90eaf98559033b370c25bba9cdd9b` to
`534578339d9c2487abb23fd8ee589fcf03be0778`. At pin selection, local `main`,
`origin/main`, and remote `main` resolved to the selected commit, and the
checkout was clean.

The intervening Starlette-RS commits add input-only sibling evidence for a
synchronous background task failing after a 204 response and literal Router
converter dispatch. They also update parity adapters, the contract, and
coverage records. The latest commits refresh compatibility, parity, benchmark,
prioritized-backlog, and atlas documentation. These revisions do not change
Starlette-RS runtime code, dependencies, the API catalog, or the API review.
The sibling manifest is unchanged since the Router input was added at
`9da93566cce0b30a9678e58336fbdc8a158281fa`; its SHA-256 remains
`c0ec486cd19397c73d46eba18cf54ea2d396a74b92478343cd576b4c8c77d04c`.
The contract ID and distribution version remain unchanged.

FastAPI-RS consumes the sibling through its existing local path dependency. It
records the new commit and reviewed source provenance; it does not copy the
sibling implementation or generic fixtures into FastAPI inputs. These sibling
cases establish no FastAPI-RS parity by themselves.
