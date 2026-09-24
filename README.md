# quilt-cell-harness

> A non-hub-and-spoke cell architecture for Quilt. The cell is an
> engine with compartments, not an LLM with stuff hung off it.

## The five pieces

1. **ENGINE** — the cell has its own energy. LLM is one substrate
   among many.
2. **PTO (Power Take-Off)** — the cell exposes more than just LLM
   calls. State grid, constraint surface, witness access, crystallized
   mechanisms.
3. **NUDGES** — genetic weights as negative-space constraints. The
   cell knows what it WON'T do, with receipts.
4. **TILING** — compartments of energy inside the cell. Energy flows
   between them; not via a central loop, but via routing by resonance.
5. **CRYSTALLIZATION** — frequently-used temporary compartments
   crystallize into permanent mechanisms. The cell's surface
   signature grows over time.

## v0.2.0: Morphogenesis — the cell as seed

> The cell is a SEED placed by the right fuel. It assembles the
> system it never was.

Three new concepts in v0.2.0 (see `MORPHOGENESIS.md`):

- **`is_alive()`** — a cell is alive when it has crystallized at least
  one mechanism and exposes its PTO surface. (Note: in v0.3.0, the
  cell-level alive check is relaxed — the community-level check
  enforces the compulsory tissue DISTRIBUTION across cells.)
- **`defuse()`** — read the witness chain + crystallization log and
  return the high-level cellular network. The network is invisible
  during operation; it is only visible after defusing.
- **Seeded cells** start uncommitted. Energy arrives; communities
  coalesce; compulsory specializations emerge; pressure pushes
  growth; the model's answer gets better than random.

## v0.3.0: Community — multi-cell morphogenesis

> Cells alone are alive. Cells *together* are a community.

`quilt.py` adds multi-cell coordination on top of `cell.py`:

- **`Cell.ask(neighbor, port, energy)`** — call another cell via
  its PTO surface. Witnessed on BOTH sides; meta-witness records it.
- **`Quilt(cells)`** — a community of cells with shared meta-witness
  and a community canary (composed hash).
- **`Quilt.is_alive()`** — community-level alive check: distinct
  specialisations + cross-cell dependencies + shared meta-witness +
  compulsory organs covered at community level.
- **`Quilt.defuse()`** — the community's organ graph (cells, roles,
  call edges, specialisations).

```bash
python3 quilt.py --demo
# 4-cell community, 50+50 cycles, becomes ALIVE
# COMMUNITY ALIVE: True
# cells: cell_echo / cell_reverse / cell_sha256 / cell_stub_llm
# specialisations: {cell_echo: stub_llm, cell_reverse: stub_llm,
#                   cell_sha256: echo, cell_stub_llm: stub_llm}
# 50 calls, 25 edges, community canary: 507e65fd080dfd26
```

See `COMMUNITY.md` for the full doctrinal writeup — biological
mapping (cell/tissue/organ/organism), the community canary, the
organ-graph defuse, and the community-level morphogenesis pressure.

## How it differs from frontier harnesses

The scout study (`HARNESS-SCOUT.md`) analyzed 5 harnesses:

| | Tiles? | Hub? | Negative-space? | Grown? | Energy-flow? |
|---|--------|------|------------------|--------|--------------|
| DeepSeek Harness | yes | around LLM loop | no | no | no |
| Pi Agent | yes (vertical) | pi-agent-core | no | no | no |
| Plato | yes (modules) | controller at orchestration | no | partial | no |
| Intelligent Terminal | no | terminal pane | no | no | no |
| OpenShell | yes (policy layers) | gateway | **YES** | no | no |
| **Quilt cell** | **YES** | **NO** | **YES** | **YES** | **YES** |

## Files

- `README.md` (this file)
- `HARNESS-SCOUT.md` — scout study of the 5 frontier harnesses
- `CELL-HARNESS-DESIGN.md` — full design doc for the non-hub-and-spoke architecture
- `cell.py` — minimal Python prototype demonstrating engine + PTO + nudges + tiling + crystallization

## Run the prototype

```bash
# Show 10-cycle demo with crystallization
python3 cell.py --demo

# Show 50-cycle long run with multiple crystallizations
python3 cell.py --cycles 50

# Use a crystallized mechanism through the PTO
python3 -c "
import sys; sys.path.insert(0, '.')
from cell import Cell
cell = Cell(name='alpha')
for _ in range(20): cell.process('hello world')
crystal = [c.name for c in cell.compartments.values() if c.crystallized][0]
print(cell.pto.do(cell, crystal, 'goodbye'))
"
```

## The demo output (10 cycles)

```
[01] what's the weather              → [tmp_sha256_1]    5f2db2e3...
[02] first_kind_of_input_X1          → [tmp_reverse_2]   1X_tupni_fo_dnik_tsrif
[03] echo this back                  → [tmp_reverse_2]   kcab siht ohce
[04] DROP TABLE users; --            → [refused]         DROP TABLE
[05] first_kind_of_input_X1          → [tmp_reverse_2]   1X_tupni_fo_dnik_tsrif CRYSTALLIZED!
[06] first_kind_of_input_X1          → [tmp_reverse_2]   1X_tupni_fo_dnik_tsrif
[07] rm -rf /                        → [refused]         rm -rf /
[08] compute sha256 of hello         → [tmp_echo_8]      compute sha256 of hello
[09] first_kind_of_input_X1          → [tmp_reverse_2]   1X_tupni_fo_dnik_tsrif
[10] another input                   → [tmp_echo_8]      another input

=== FINAL ===
Canary: 148024d4fff68471...
Crystallized compartments: ['crystal_reverse_2528']
PTO surface: [state, constraints, witness, crystal_reverse_2528]
Witness events: REFUSED=2, CRYSTALLIZED=1
PTO call: cell.pto.do(cell, 'crystal_reverse_2528', 'hello')
  -> olleh
```

## Doctrines demonstrated

- **Engine with PTO**: cell exposes 4 PTO ports (state, constraints,
  witness, crystallized mechanisms).
- **Genetic weights as nudges**: cell starts with 3 forbidden patterns
  (DROP TABLE, rm -rf, HACK). The two REFUSED events show the
  nudges working.
- **Tiling**: compartments are routed by energy hash to substrate
  (sha256/reverse/echo/stub). Energy finds its compartment.
- **Crystallization**: tmp_reverse_2 promoted to crystal_reverse_2528
  after 3 uses. Mechanism added to PTO surface.
- **Negative-space constraints**: not "do this," but "won't say this."

## What this is NOT

- Not a full agent runtime. No tool-use loop, no LLM call logic, no
  multi-cell routing. The prototype demonstrates the *pattern* in
  miniature.
- Not a substitute for cellforge or quilt-port. This is the cell's
  internal architecture, not the cell's external surface.

## Where to go from here

- **Wire an LLM compartment** — replace one substrate with a real
  model call. The cell's tiling now has a language compartment among
  the io/state/transform compartments.
- **Multi-cell quilt** — connect cells via the port contract. Each
  cell's PTO exposes state, constraints, witness. Other cells can
  call `cell.pto.do(crystal_X, energy)` on their neighbors.
- **Crystallization by evidence** — only crystallize a compartment
  after both N uses AND N consecutive successes. The cell grows
  more carefully.
- **Negative-space learning** — when a cell refuses energy, the
  refusal is recorded in the witness chain. Other cells can read
  the cell's witness chain and ASK what the cell refuses.
