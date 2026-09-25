# Community — multi-cell morphogenesis

> Cells alone are alive. Cells *together* are a community.

The cell-harness v0.2.0 had a single cell that could crystallize
compartments and become "alive" by hitting 4 compulsory tissue
types. The next layer: multiple cells run together, share fuel,
form communities, and the morphogenesis pressure cascades across
cells.

Casey's "community coalesces and specialisation into compulsory
tissue and organ types" maps to:

- **community** = multiple cells in a quilt
- **coalesces** = shared witness chains + cross-cell calls
- **specialisation** = each cell crystallizes different
  compartments (different roles)
- **compulsory tissue types** = cell-internal (still required)
- **organ types** = cross-cell emergent structures (PTO surfaces
  composed from multiple cells)

## The community doctrine

A cell alone is alive when it has its 4 compulsory tissues.
A *community* is alive when its cells have:

1. **Distinct specialisations** — each cell crystallizes a
   *different* compartment as its primary mechanism. If all cells
   crystallize the same substrate, the community has not
   specialised — it's a herd, not a community.

2. **Cross-cell dependencies** — at least one cell's PTO surface is
   called by another cell. Without dependencies, the cells are
   isolated; they may as well be alone.

3. **Community-level witness** — the cells share a meta-witness
   chain that records cross-cell calls. A community without a
   shared memory of its interactions is just a fleet of hermits.

4. **Compulsory organ types** — at least one cell has crystallized
   *each* of the community's required roles (e.g., a witness cell,
   a refuter cell, a translator cell). The community is the
   organism; the cells are its organs.

## What's new in v0.3.0

The `quilt.py` module adds multi-cell coordination on top of
`cell.py`:

- **`Cell.ask(neighbor, port_name, energy)`** — call another cell
  via its PTO surface. Witnessed on both sides.
- **`Quilt(cells)`** — a community of cells with shared meta-
  witness and a community canary.
- **`Quilt.canary()`** — composed hash from all member cells'
  state + the cross-cell call history.
- **`Quilt.specialisations()`** — which substrate each cell
  crystallizes most (the cell's "tissue type").
- **`Quilt.defuse()`** — the community's assembly graph. Shows
  cells, their roles, and the cross-cell call structure.
- **`Quilt.is_alive()`** — community-level alive check: distinct
  specialisations + cross-cell dependencies + shared witness.

## Biological mapping

| Biology | Quilt |
|---------|-------|
| cell | Cell |
| tissue | crystallized mechanism (within one cell) |
| **organ** | **cell with a tissue role in the community** |
| organism | Quilt (community of cells) |
| **organ system** | **multiple cells cooperating on a function** |
| nervous system | **shared meta-witness chain** |
| immune system | **community-level refusal pressure** |
| apoptosis | compartment dissolution (within cell) |
| **organ failure** | **cell death** (cell removed from quilt) |

## The community canary

A single cell has a canary (its state-grid hash). A community has a
**composed canary**: the canary of each member cell XORed together
with the cross-cell call history.

```python
quilt.canary() = H(cell_1.canary || cell_2.canary || ... || cross_calls)
```

If any cell's state changes OR any cross-cell call happens, the
community canary changes. This is the witness that the *community*
hasn't collapsed — even if individual cells are still alive.

## The community defuse

Defusing a community returns:

```python
{
    "cells": [{name, role, crystallized_substrates, alive}],
    "edges": [(caller, callee, port_name, call_count)],
    "specialisations": {cell_name: top_substrate},
    "shared_meta_witness": [...],   # cross-cell call history
    "community_canary": "...",
    "community_alive": bool,
}
```

This is the high-level cellular network of the **community**, not
just one cell. You can see which cells talk to which, which cells
hold which roles, and whether the community's organs are all
present.

## Why a community, not just more cells

A community is not just "more cells running in parallel." A
community has *roles*. Without roles, the cells are fungible —
swap one out and nothing changes. With roles, the cells are
specialized — swap one out and the community's behavior changes.

The roles emerge from:
- Which substrates each cell happens to crystallize most
- Which PTO ports each cell exposes most
- Which cells other cells call most

Roles are *not* assigned. They are observed.

## How to extend v0.2.0 with v0.3.0

Run:

```bash
python3 quilt.py --demo
```

You'll see:
- 3 cells seeded with the same substrates
- After 30 cycles with cross-cell calls, the cells
  crystallize different substrates (specialization)
- After 60 cycles, the community becomes "alive"
  (distinct roles + cross-cell dependencies + shared witness)
- The defuse reveals the community's organ graph

## What the community can do that a single cell cannot

- **Translation** — one cell crystallizes `echo`, another
  crystallizes `sha256`; together they can hash-then-echo.
- **Refusal cascade** — when cell A refuses an input, cell B
  inherits the refusal as a nudge. The community's
  constraints grow faster than any single cell's.
- **Specialization by environment** — if the energy mix is
  60% hash-input, 30% echo-input, 10% reverse-input, the
  community evolves 2 hashing cells, 1 echo cell, 1 reverse
  cell. Without intervention. Without configuration.

## Cross-cell pressure

The witness chain of one cell becomes selective pressure for
its neighbors. If cell A's outputs are consistently refused by
cell B (B witnesses "I asked A and got something useless"),
then A's uses don't climb, and A's compartments don't crystallize.

This is **the leash**: cells that produce useful output get to
keep their compartments; cells that don't, lose them. The
community's coherence is enforced by its own refusal
witnesses.

## The doctrine in one line

> A cell alone is alive. A community of cells, with distinct
> specialisations and cross-cell dependencies, is an organism —
> and to understand it, you defuse the community, not the cells.
