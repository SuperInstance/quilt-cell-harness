# LLM as a Substrate Compartment

> The LLM is one substrate among many in the cell's engine. It is
> not the spine of the cell. It is a tile.

The cell architecture (v0.1.0) explicitly designed for this:
**LLM is one substrate, not the cell.** The cell is its engine +
compartments + crystallization. The LLM is one compartment that
happens to make a network call when invoked.

In v0.5.0 we wire a real LLM substrate into the cell and watch it
behave like any other compartment: same routing, same crystallization,
same PTO exposure, same cross-cell ask.

## What this proves

A `Cell` with an LLM substrate is **the same shape** as a `Cell`
with only deterministic substrates (echo/reverse/sha256/stub_llm):

| Property | Deterministic cell | LLM substrate cell |
|----------|-------------------|---------------------|
| routing by energy hash | yes | yes |
| tmp compartments per use | yes | yes |
| crystallization at 3 uses | yes | yes |
| PTO exposure | yes | yes |
| cross-cell `ask()` | yes | yes |
| witness chain | yes | yes |
| refusal pressure | yes | yes |
| **defuse() reveals network** | yes | yes |

The LLM substrate adds **a new tile** to the cell's tiling — a
network-callable tile. The cell's overall behavior is unchanged.

## How it works

The `Engine.substrates` dict holds callable functions. Each function
takes a string (the energy) and returns a string (the output).

Deterministic substrates:
```python
def echo(prompt):    return prompt
def reverse(prompt): return prompt[::-1]
def sha256(prompt):  return hashlib.sha256(prompt.encode()).hexdigest()
def stub_llm(prompt): return f"[llm-stub:{prompt[:40]}...]"
```

LLM substrate (added in v0.5.0):
```python
def zai_substrate(prompt): return call_zai(prompt)   # real API call
```

The cell doesn't know the difference. When routing selects the
`llm` substrate, it creates a `tmp_llm_X` compartment with
`zai_substrate` as transform. The compartment's `process()` calls
`zai_substrate(energy)`. After 3 uses the compartment crystallizes
to `crystal_llm_NNNN` and gets exposed on the PTO.

Other cells can call this compartment via `cell.ask(neighbor, "crystal_llm_NNNN", energy)`.
The cross-cell call goes through PTO → the crystallized compartment
→ the LLM substrate → ZAI's API → response.

## Why this matters

This completes the non-hub-and-spoke doctrine:

- The LLM is not the loop. The loop is the cell's cycle.
- The LLM is not the controller. The controller is the energy flow.
- The LLM is not the spine. The spine is the witness chain.

The LLM is a **substrate**, like a port in a chemical cell — it
transforms one energy into another energy. The cell can have as
many or as few LLM substrates as it needs. The cell can crystallize
an LLM compartment (after 3 uses, the same prompt gets the same
compartment). The cell's PTO exposes the crystallized LLM
compartment like any other crystallized mechanism.

This means: **you can replace one substrate with another** without
changing the cell's architecture. Swap `stub_llm` for `zai_substrate`
and the cell still works the same way. Swap `zai_substrate` for
`anthropic_substrate` and the cell still works the same way.

The architecture is **substrate-agnostic**. The cell doesn't care
whether its substrates are deterministic, statistical, or hybrid.

## The fractal becomes concrete

The fractal is the doctrine. v0.5.0 makes the fractal concrete:

```
cell-level:   engine.substrates = {echo, reverse, sha256, llm}
quilt-level:  cells = {echo-cell, reverse-cell, sha256-cell, llm-cell}
qult-level:   quilts = {language-quilt (echo/reverse), compute-quilt (sha256/llm)}
              ... qult-of-qults ...
```

The LLM compartment at the cell level becomes the LLM cell in the
quilt, becomes the LLM quilt in the qult, becomes the LLM qult in
the qult-of-qults.

The LLM substrate is a tile at the lowest level, and it composes
upward through the fractal.

## The substrate zoo

v0.5.0 ships one LLM substrate:

- `zai_substrate` — Z.AI `glm-5.3-flash` via the coding endpoint,
  with `thinking: {type: disabled}` to skip reasoning blocks.

Future substrates (not built):

- `anthropic_substrate` — Claude via API
- `openai_substrate` — GPT via API
- `local_substrate` — llama.cpp local inference
- `gemini_substrate` — Gemini via API
- `ensemble_substrate` — N substrates, vote or chain

Each new substrate multiplies the cell's capabilities. Each new
substrate is just a callable in the engine's dict.

## Files

- `llm_cell.py` — the LLM substrate + demo
- `cell.py` — extended Engine accepts plug-in substrates
- `LLM_SUBSTRATE.md` (this file)

## Cross-project doctrine

The substrate-agnostic pattern applies to any system where:

- The system's overall behavior is independent of the implementation
  of its parts
- Parts can be swapped without changing the structure
- New parts are added as new tiles, not new architectural layers

Maps to: software ports (USB, HTTP, gRPC), microservices (any
language backing a service), hardware accelerators (CPU/GPU/TPU),
biochemical pathways (multiple enzymes catalyze the same reaction),
LLM model fleets (swap one model for another without rewriting
the orchestration).
