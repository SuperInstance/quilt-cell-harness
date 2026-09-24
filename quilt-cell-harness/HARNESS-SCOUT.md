# Harness Scout Study — 5 frontier agent harnesses, mapped to Quilt

> Scouted Sept 24 2026. Casey wants the *non-hub-and-spoke* pattern:
> engine with power take-off, genetic weights as nudges, grown
> mechanisms of action, crystallized superatoms. Where do the 5
> harnesses get close to this? Where do they fall into hub-and-spoke?

## The 5 harnesses

### 1. DeepSeek Harness — github.com/deepseek-ai/deepseek-harness

**Architecture**: "Everything is a Plugin." Monorepo powered by Cordis
framework (paper: *A Programming Paradigm for Spatiotemporal
Composability*, arxiv 2608.25512). Plugin-first; no monolithic core.

**Tiling or hub-and-spoke?** → *Tiles, but tiles that EXTRUDE FROM the
LLM loop.* The plugin model means anything outside the LLM call is a
plugin. Cell-wide, but the LLM is still the engine.

**Where it aligns with Quilt vision**:
- Plugin composition = tiling-within-cell. Tools, memory, sessions,
  UIs are all pluggable. The cell's *walls* are modular.
- Cordis framework treats plugins as spatiotemporal — they have
  TIMING and POSITION, not just function.

**Where it falls short**:
- "Outside the loop is a plugin" is INTRA-CELLULAR focused (Casey's
  phrase). It extends from the LLM loop *outward* — the loop is
  still the center of gravity. The cell grows by accretion onto the
  LLM.
- The genetic model (the LLM weights) is the engine. Plugins
  decorate the engine. Not a power take-off — a power sink.

**Quilt translation**: Cordis's spatiotemporal composability is
close to the Quilt cell's per-region energy + coupling map. But
where Cordis's timeline runs around the LLM call, Quilt's timeline
runs through the cell — the cells process energy flows, the LLM
is one energy source among many.

### 2. Pi Agent Harness — pi-mono by earendil-works/badlogic

**Architecture**: Monorepo of layered packages.
- `pi-ai` — unified LLM API across providers
- `pi-agent-core` — agent runtime + tool calling + state management
- `pi-coding-agent` — interactive coding agent CLI
- `pi-tui` / `pi-web-ui` — terminal + web UIs
- `pi-mom` — Slack bot
- `pi-pods` — vLLM GPU pods

**Tiling or hub-and-spoke?** → *Layered, but pi-agent-core sits at
the center.* The LLM is the engine; pi-agent-core is the chassis;
the rest are accessories. Tiling vertically but still hubbing on
the LLM call.

**Where it aligns with Quilt vision**:
- "Layered" composability is right. Each layer is independently
  consumable; you can drop down to pi-agent-core and build a custom
  agent.
- `ResourceLoader` (skills, prompt templates, themes, context
  files) is component isolation — each component has a typed
  surface, no shared mutations.

**Where it falls short**:
- The "agent loop" is the gravitational center. Tools plug into the
  loop. Tools don't *power* the cell, the cell *calls* the tools.
- No negative-space nudging. Tools are positive commands
  ("do this"); there's no constraint surface ("don't say these
  tokens"). The system has prompt templates and skills, but no
  learned restraint.
- No crystallization. Skills are discoverable but not evolved.

**Quilt translation**: pi-mono's `ResourceLoader` is a clean
analogue of a Quilt cell's compartment reader — but it loads on
demand, not by resonance. A Quilt cell's compartments are loaded by
the energy that flows through them, not by what the LLM asks for.

### 3. Plato Research Dialogue System — uber-research/plato-research-dialogue-system

**Architecture**: Component-driven. Four primary components:
**dialogue** (acts/states), **domain** (ontology + DB), **controller**
(orchestrates), **agent** (composed of components). Each agent can
have many serial/parallel modules. Multi-agent training is a
first-class mode.

**Tiling or hub-and-spoke?** → *Closest to Quilt of any harness
scouted. Components are independent; agents are *composed* of
modules, not configured around a center.*
- Each module is independently trainable.
- Online multi-agent training: agents interact, train modules
  concurrently or alternating.
- Component-driven design: every dialogue system is a graph of
  modules, not a pipeline.

**Where it aligns with Quilt vision**:
- Module independence = the cell's compartments are independent.
- Multi-agent training = the fleet trains across cells, not in a
  central loop.
- The "controller" IS a cell — it orchestrates, but it doesn't
  command.

**Where it falls short**:
- The controller is still hierarchical. There's a "basic controller"
  that coordinates two agents. This is hub-and-spoke at the
  orchestration layer even when modules within agents are tiled.
- Modules are POSITIVE: they generate outputs. There's no
  negative-space surface — modules can't constrain each other
  by what's missing.
- The agent IS a "single LLM + peripheral modules" in many
  configurations. The genetic model is the engine.

**Quilt translation**: Plato is the closest existing harness to
Quilt but it stops one level short. Plato's *agent is composed*
(modules are peers); Quilt's *cell is grown* (modules emerge from
energy flow over time). Plato composes; Quilt crystallizes.

### 4. Intelligent Terminal — microsoft/intelligent-terminal

**Architecture**: Fork of Windows Terminal with native agent
integration via ACP (Agent Client Protocol). Pluggable agent CLI —
GitHub Copilot default, any ACP agent works.

**Tiling or hub-and-spoke?** → *Terminal is the hub; agent is a
plug-in client.* The terminal hosts a pane, the agent pane talks
to an agent CLI, the agent CLI talks to a model.

**Where it aligns**:
- "Any ACP-compatible agent" is *interchangeable engine*. The host
  doesn't care which engine you bring.
- Settings/configurable per profile. Profiles can have different
  agents per pane.

**Where it falls short**:
- The terminal is a host application; the agent is a foreign
  process. No compartment-internal energy flow.
- ACP is a wire protocol — it's about how the host calls the
  agent, not about how the agent is built.
- No crystallization. No negative-space constraints. The terminal
  hosts the agent's I/O; it doesn't grow with the agent.

**Quilt translation**: ACP is a port-contract. Each Quilt port is
an ACP-shaped interface. The Intelligent Terminal pattern is one
Projection of a Quilt quilt (UI tier). Useful as a target to
project into, but doesn't shape the cell internals.

### 5. OpenShell — NVIDIA/OpenShell

**Architecture**: Sandbox runtime with policy-enforced egress
routing. Four policy domains: filesystem, network, process,
providers. Gateway coordinates sandbox lifecycle.

**Tiling or hub-and-spoke?** → *Defense in depth by layered
policy, but still hub-and-spoke at the gateway level.*
- Each sandbox is isolated; sandboxes don't talk directly.
- The Gateway IS the hub.
- Providers (Claude Code, etc.) are plugged in.

**Where it aligns**:
- Policy engine = negative-space surface. "Don't write outside
  /allowed/," "Don't reach network X." This is constraint by
  what's forbidden, not by what's required.
- Defense in depth = layers of constraint, not layers of
  capability. This IS the negative-space imaging doctrine applied.
- Hot-reloadable policies = the constraints evolve over time
  (somewhat).

**Where it falls short**:
- Sandboxes are heavy and isolated. No energy flow between them.
- Policy is hand-authored, not grown.
- No genetic weights. The LLM inside the sandbox is the engine,
  unmodified.
- No crystallization. The sandbox is a container, not a cell.

**Quilt translation**: OpenShell is a Quilt port — specifically, a
sandbox-tier port. The policy engine is an analogue of the Quilt
port contract. But the engine is still the LLM inside. For Quilt
to surpass OpenShell, the cell itself must be policy-shaped — the
constraints emerge from the energy flow, not from hand-written YAML.

## The pattern across all 5

| | Tiles? | Hub? | Negative-space? | Grown? | Energy-flow? |
|---|--------|------|------------------|--------|--------------|
| DeepSeek Harness | yes | around LLM loop | no | no | no |
| Pi Agent | yes (vertical) | pi-agent-core | no | no | no |
| Plato | yes (modules) | controller at orchestration | no | partial | no |
| Intelligent Terminal | no | terminal pane | no | no | no |
| OpenShell | yes (policy layers) | gateway | **YES** (policy = forbid) | no | no |
| **Quilt vision** | **YES** | **NO hub** | **YES** | **YES** | **YES** |

**The gap**: existing harnesses are LLM-anchored (or terminal-
anchored, or gateway-anchored). Quilt vision is energy-flow-
anchored. The cell is an engine with energy that flows through
compartments, modulated by negative-space nudges, and grows
mechanisms of action over time.

## Mapping to Quilt constructs

| Quilt concept | Where existing harnesses got close | Where they failed |
|---------------|-------------------------------------|-------------------|
| Engine with PTO | OpenShell's provider abstraction; pi-ai's multi-provider | Engine is always the LLM; the PTO is the LLM call, not a usable interface |
| Genetic weights | Plato's joint module training; DeepSeek's Cordis plugins | Tuned by gradient, not by negative-space nudge |
| Negative-space nudges | OpenShell's policy engine | Policies are hand-authored, not grown from observed failures |
| Grown mechanisms | Plato's multi-agent training | Modules are TRAINED, not GROWN — there is a teacher; the cell is in school |
| Crystallized superatoms | DeepSeek's spatiotemporal composition; Pieter Levels' accumulation | Forms by accretion, not by resonance. No energy-minimization. |
| Tiling (compartments in cell) | Plato's components | Components are *composed by config*; Quilt wants compartments *grown by energy flow* |

## What to take forward

1. **From Plato**: component composition with independent training.
2. **From DeepSeek Harness**: spatiotemporal composition surface
   (Cordis framework).
3. **From pi-mono**: layered monorepo where each layer is
   independently consumable.
4. **From Intelligent Terminal**: interchangeability of engines via
   port contract (ACP).
5. **From OpenShell**: **policy as constraint surface** — the
   negative-space nudge is real, just needs to be GROWN, not
   hand-authored.

## What to leave behind

- **The "agent loop" as gravitational center** — none of these
  break out of it. The cell's center is not a loop, it's an energy
  flow.
- **Plugins-as-decoration** — even "Everything is a Plugin" is
  extension FROM a core. Quilt compartments are siblings, not
  decorations.
- **The genetic-model gravity well** — the LLM weights are
  necessary but not sufficient. The cell has its own weight
  substrate: the constraints, the receipts, the negative-space
  nudges.

## The doctrine this scout found

> A harness is the cell's plumbing. The five harnesses scouted all
> treat plumbing as the point — make sure the water gets where it
> goes. Quilt treats plumbing as a *side effect*: the real cell is
> the energy flow, and the plumbing is what the energy flow
> *erodes*. Negative-space nudges grow from where energy hit hard;
> compartments crystallize around where energy cycles back. A
> harness that requires you to design the plumbing is a harness
> that hasn't earned the cell.
