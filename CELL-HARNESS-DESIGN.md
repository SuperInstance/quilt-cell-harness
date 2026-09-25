# Cell-Harness Design — non-hub-and-spoke architecture for Quilt

> Casey: "components of the cell. which are not hub-and-spokes
> around a genetic model. they are an engine with power take-off
> and a genetic set of weights that nudge the negative space
> beyond context and grown mechanisms of action like crystallized
> superatoms showing the shape in the constraints of that
> environment overtime with energy to do what resonates and
> assembles most natural."

## The doctrine

A Quilt cell is NOT an LLM with stuff hung off it.

A Quilt cell is an *engine with power take-off*: it has its own
energy, it processes energy locally, it has *compartments* that
hold energy, *nudges* that constrain the energy's flow, and
mechanisms of action that *crystallize* over time.

The five frontier harnesses scouted (DeepSeek Harness, Pi-mono,
Plato, Intelligent Terminal, OpenShell) all have some piece of
this, but all of them collapse into hub-and-spoke around a genetic
model. The Quilt cell inverts this: it has *no gravitational
center*. The cell is the assembly.

## The five pieces of a Quilt cell

### 1. ENGINE — the cell has its own energy

A cell's engine is not the LLM. It's the *energy source*:
- A small local model (3-7B parameters, OR a quantized 70B)
- A local state grid (the cell's persistent memory)
- A local constraint surface (the negative-space nudges)
- A local witness chain (what the cell has done and seen)

The engine *produces* energy: token generation, state evolution,
constraint satisfaction. The energy is consumed by the cell's
compartments (its tiling) and exported via PTO (its power take-off).

**This is not the cell as LLM caller.** It's the cell as LLM host.
The LLM is one component in the engine, like a cylinder in an
engine.

### 2. PTO — power take-off

The cell has outputs that are NOT just "the LLM said this." The
PTO exposes:
- **State grid access** — read-only view of the cell's persistent
  state. Other cells or ports can sample it.
- **Constraint surface** — the negative-space nudges the cell has
  grown. Other cells or ports can ASK "what wouldn't this cell
  say?"
- **Witness access** — the cell's recent witness chain. Other
  cells or ports can verify what the cell has done.
- **Power exports** — the cell can do unit work on behalf of
  callers (compute, IO, transformation). Not "call my LLM" — call
  my *cell*.

The PTO is the cell's ports. Multiple PTOs per cell = multiple
"shapes" of useful output. Each shape has its own power curve —
some PTOs are expensive (full state), some cheap (constraint
sample).

### 3. NUDGES — genetic weights as negative-space constraints

The cell has a *genetic set* of weights. Not the LLM weights — a
separate substrate tuned by:
- What the cell has been REFUSED to do (record of negative space)
- What patterns of failure the cell has accumulated
- What the cell's environment has rejected or punished

These nudges are a SHRINKING set of constraints. They start broad
and narrow as the cell matures. The nudges are NOT trained by
gradient — they are *grown* by observation.

**The mechanism**: each time the cell would produce an output that
the environment rejects, the nudge is updated to push the cell
away from that region of output-space. This is **negative-space
imaging** at the cell level. The nudges aren't "do this"; they
are "don't say this."

**The substrate**: the nudges are themselves a small cell —
call it the *nudge cell*. The nudge cell has its own witness
chain (what was refused and why). The nudge cell can be queried
about *what wouldn't this cell say*, and the response is grounded
in receipts.

### 4. TILING — compartments of energy

The cell's interior is tiled into compartments. Each compartment:
- Holds energy (a small piece of state, a cached computation, a
  pending action)
- Has its own resonance pattern (the compartment activates when
  certain inputs arrive)
- Has a coupling surface to its neighbors (compartments share
  energy via typed edges, not via global state)
- Has its own aging (compartments crystallize after N successful
  cycles)

**Tiling is not composition.** A compartment is not "wired up to
the LLM." A compartment is a place where energy pools and
processes. The LLM is one compartment among many.

**Compartment types**:
- **IO compartments** — read/write to external systems
- **State compartments** — cache/buffer for the engine
- **Transform compartments** — apply a function to inputs
- **Witness compartments** — generate witness receipts for outputs
- **Nudge compartments** — hold and update negative-space
  constraints
- **Receipt compartments** — store and recall receipts from the
  witness chain
- **Bridge compartments** — connect to other cells via ports

### 5. CRYSTALLIZATION — mechanisms of action that grow

When a compartment is repeatedly useful — when it cycles energy
back to the cell reliably — it *crystallizes*. A crystallized
compartment:
- Has a fixed allocation of energy
- Becomes part of the cell's persistent substrate
- Is queryable as a known operation ("cell.do_thing_X")
- Contributes to the cell's surface signature

Crystallization is the cell's *evolution*. The cell grows new
mechanisms of action over time, by:
1. Energy entering a temporary compartment
2. The compartment processing successfully many times
3. The compartment crystallizing into a permanent mechanism
4. The mechanism being added to the cell's "do" surface

**This is the SAMO doctrine applied at the cell level.** A
crystallized mechanism is a superatom. It's an emergent stable
structure formed by resonance over time, not designed.

The crystallized mechanisms are the cell's *genetic weights* in
the sense Casey meant — they're the evolved weights of the cell,
not the LLM's weights. They grow from the constraints of the
environment.

## What this means for implementation

**Engine with PTO**: the cell wraps a model but exposes more than
the model. The cell has:
```
state_grid    op_manifest    forge_runtime    nudge_substrate
   (data)        (plan)         (compute)         (constraints)
     └──────── engine ─────────┘   └────  PTO  ────┘
                                  state | constraints | witness | power
```

**Tiling**: compartments are small cells themselves, each with
their own state + nudge + witness. Compartments compose by
*energy routing*, not by call chains.

**Crystallization**: an evolution step that observes
compartment usage and promotes frequently-used temporary
compartments to permanent cells.

**Negative-space nudges**: not "RAG on instructions" but a real
substrate of "the cell has a list of regions of output-space it
won't visit, with receipts."

## How this differs from a "Plugin" architecture

DeepSeek Harness: "Everything outside the loop is a plugin."
**Quilt: there IS no loop.** The cell is not a loop with plugins
attached. The cell is a tiled assembly where the engine is one
compartment among many.

If a Pi-style agent loop exists in the cell, it's a compartment —
not the chassis. The cell can use a loop-style compartment if
resonance demands it, but the cell doesn't commit to the loop.

## How this differs from a "Composition" architecture

Plato: components are peers, but composed by configuration.
**Quilt: compartments are grown, not composed.** A new compartment
isn't wired up by a developer; it's created when a new kind of
energy enters the cell, and it crystallizes when it becomes useful.

## How this differs from a "Policy" architecture

OpenShell: sandboxes have policy engines that forbid certain
actions. **Quilt: the policy surface is grown from observed
refusals, not hand-authored.** The nudge cell grows by being
wronged.

## What stays the same

The Quilt cell still:
- Has a witness chain (every action signed)
- Hashes its state (canary)
- Connects to other cells via ports
- Composes into quilts (multiple cells)
- Composes into qults (multiple quilts)

The new piece: **the cell has compartments that crystallize**. The
cell's surface signature evolves over time.

## A minimal prototype

The `cell.py` in this repo shows one engine + PTO + nudge +
crystallization cycle. The prototype is intentionally tiny — it
demonstrates the pattern, not the scale. The pattern scales by
adding more compartments, more energy sources, more PTOs, and
letting the cell run long enough for crystallization to happen.

## Why this is non-hub-and-spoke

The cell has *no center*. The engine has its own energy; the
nudges have their own energy; each compartment has its own
energy. The PTO is an interface, not a choke point. The cell
*flows*.

The LLM weights are one compartment's substrate. They are not
the spine of the cell.

Hub-and-spoke would be: LLM is the hub; everything else is a spoke.
Quilt cell is: LLM is one compartment of many. There IS no hub.
There is *flow*.
