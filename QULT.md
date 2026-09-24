# Qult — multiple quilts as one organism

> A qult is what a quilt becomes when it learns to contain other
> quilts.

The fractal: cells → quilts → qults → qults-of-qults. Each level
is the same shape at a different scale. Each level has its own
canary, its own defuse, its own alive-check.

## What this is

`qult.py` adds the next level of fractal composition on top of
`quilt.py`:

- **`Qult(quilts)`** — multiple quilts in a higher-level organism
- **`Quilt.ask(other_quilt, port, energy)`** — cross-quilt PTO call
  (witnessed on both quilts AND on the qult)
- **`Qult.canary()`** — composed hash from all quilt canaries
- **`Qult.is_alive()`** — qult-level alive check (5 conditions at
  the qult level)
- **`Qult.defuse()`** — the organ-system-level graph (quilts as
  organs, calls between them, shared meta-witness)
- **`Quilt.prune()`** — remove cells whose crystallized compartments
  have dropped below threshold (apoptosis / organ failure)

## The fractal at every level

| Level | Class | Members | Alive check | Canary |
|-------|-------|---------|-------------|--------|
| cell | Cell | compartments | ≥ 1 crystallized + PTO | state-grid hash |
| quilt | Quilt | cells | 5 community conditions | composed cell canaries + meta-witness |
| qult | Qult | quilts | 5 qult conditions | composed quilt canaries + meta-meta-witness |
| qult-of-qults | Qult(qults-of-quilts) | qults | recursive | recursive |

**Same shape, different scale.** This is the fractal doctrine:
the cell is the irreducible unit; everything larger is just cells
arranged at higher abstraction levels with the same rules.

## The 5 conditions for a Qult to be alive

1. **All member quilts alive** — each quilt in the qult has
   crystallized its own community (cells + cross-cell deps)
2. **Distinct quilt specializations** — quilts take different roles
   (e.g., one is the "translation" quilt, another is the
   "summarization" quilt, another is the "memory" quilt)
3. **Cross-quilt dependencies** — at least one quilt calls
   another quilt via its PTO surface
4. **Qult-level meta-witness** — shared memory of cross-quilt calls
5. **Qult-level compulsory organs** — the substrates covered
   across the qult's quilts satisfy the qult's required roles
   (organ-system level)

If all 5 are met, the qult is *alive* — it's an organism of
organisms.

## Cell death / apoptosis

In v0.3.0, the community had `Quilt.is_alive()` but no mechanism
for cells to die. In v0.4.0, cells that fail to maintain their
crystallized compartments are pruned from the quilt:

```python
quilt.prune()  # returns list of cells removed
```

A cell is removed when its crystallized count drops below a
threshold (default: 1). This is **organ failure**: the cell
loses its function, the community removes it.

The pruned cell's witness events stay in the meta-witness — its
death is recorded, not erased. **No deletion.** The cell's
contributions remain visible; the cell just isn't in the live
quilt anymore.

## Biological mapping at the qult level

| Biology | Quilt |
|---------|-------|
| organism system | **Qult** (multiple organs cooperating) |
| nervous system | qult meta-witness |
| immune system | qult refusal pressure |
| cell death | **Quilt.prune()** |
| organ transplant | re-introducing a cell or sub-quilt |
| evolutionary pressure | qult-level morphogenesis |

## Why this completes the morphogenesis thread

Casey's morphogenesis doctrine chain:

1. **v0.2.0** — single cell: seed + fuel → morphogenesis
2. **v0.3.0** — community: cells form a quilt with organs
3. **v0.4.0** — qult: quilts form a higher organism with organ systems

Each step is the same pattern at a different scale:
- Energy arrives
- Communities / quilts / qults coalesce
- Specialization is compulsory
- Pressure pushes growth
- Cells / quilts / qults that don't maintain their function
  get pruned (death is real, not abstract)
- The witness chain records everything

The cell doctrine has now been scaled through three levels.
The fractal is intact.

## The doctrine in one line

> A cell is to a quilt as a quilt is to a qult: same shape at
> different scale, alive when the right organs are present, dying
> when the function fails. The fractal is the doctrine.
