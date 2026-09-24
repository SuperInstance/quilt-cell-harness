"""
llm_cell.py — wire a real LLM as one substrate compartment in the cell.

The cell architecture (cell.py) is substrate-agnostic. Substrates are
just callable functions in Engine.substrates. Deterministic substrates
(echo/reverse/sha256/stub_llm) and LLM substrates (call_zai) work
exactly the same way.

Run:
    python3 llm_cell.py --demo
"""

import argparse
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cell import Cell, Compartment


# === LLM SUBSTRATE ===

def zai_substrate(prompt: str) -> str:
    """Call Z.AI's glm-5.3-flash via the coding endpoint.

    Returns the model's text response. Falls back to a stub on
    network failure.
    """
    token = os.environ.get("ZAI_TOKEN", "")
    if not token:
        return f"[no-zai-token:{prompt[:40]}...]"

    url = "https://api.z.ai/api/coding/paas/v4/chat/completions"
    payload = {
        "model": "glm-5.3-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 60,
        "thinking": {"type": "disabled"},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "quilt-cell-harness/0.5.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = json.loads(r.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        return f"[zai-error:{type(e).__name__}:{prompt[:40]}...]"


def build_engine_with_llm():
    """Engine with the 4 default substrates + a real LLM substrate."""
    from cell import Engine
    engine = Engine()
    engine.substrates = dict(engine.substrates)  # copy
    engine.substrates["zai_llm"] = zai_substrate
    engine.calls = {s: 0 for s in engine.substrates}
    return engine


def cell_with_llm(name):
    """A cell with a real LLM as one of its substrates."""
    cell = Cell(name=name)
    cell.engine = build_engine_with_llm()
    return cell


def preseed_llm_crystal(cell, crystal_name="crystal_llm_seeded"):
    """Pre-create a crystallized LLM compartment in the cell.

    Real morphogenesis would converge to an LLM crystal after enough
    cycles routed to the LLM substrate. We pre-seed it here so the demo
    fits within the tool timeout (LLM calls are ~2s each).
    """
    cell.compartments[crystal_name] = Compartment(
        name=crystal_name,
        transform=cell.engine.substrates["zai_llm"],
        crystallized=True, uses=10,
    )
    cell.crystallizations.append({
        "cycle": cell.cycles, "from": "seed", "to": crystal_name,
        "uses_before_promotion": 10,
    })
    cell.pto.expose(
        crystal_name,
        lambda c, energy, _n=crystal_name: c.compartments[_n].process(energy),
    )
    cell.engine.calls["zai_substrate"] = cell.engine.calls.get("zai_substrate", 0) + 10
    return crystal_name


# === DEMO ===

def demo(n_cycles=15, with_llm=True):
    print(f"=== LLM SUBSTRATE DEMO ({n_cycles} cycles, with_llm={with_llm}) ===\n")

    cell = cell_with_llm("mixed_cell")
    print(f"Engine substrates: {list(cell.engine.substrates.keys())}\n")

    energies = [
        "echo this back to me",
        "reverse the string hello",
        "sha256 of password123",
        "stub llm: hello there",
        "tell me a joke",
        "describe a sunset in one sentence",
        "what is 2+2?",
        "name a prime number",
        "explain morphogenesis briefly",
        "what is a quilt cell?",
    ]

    print(f"Processing {n_cycles} energies (LLM calls ~2s when routed)...")
    t0 = time.time()

    for i in range(n_cycles):
        energy = random.choice(energies)
        result = cell.process(energy)
        if i < 5 or i % 5 == 0:
            substrate = result.get("compartment", "?")
            output = str(result.get("output", ""))[:80]
            print(f"  [{i:02d}] '{energy[:30]:30s}' → {substrate:18s} → {output}")

    print(f"  ({time.time()-t0:.1f}s wall-clock)\n")

    # If no LLM compartment crystallized naturally, pre-seed one.
    llm_crystal_names = [c.name for c in cell.compartments.values()
                         if c.crystallized and ("llm" in c.name or "zai" in c.name)]
    if not llm_crystal_names:
        print("(pre-seeding a crystallized LLM compartment for PTO demo)")
        preseed_llm_crystal(cell)
        llm_crystal_names = ["crystal_llm_seeded"]

    port = llm_crystal_names[0]
    print(f"\n=== LIVE LLM CALL via PTO ({port}) ===")
    print(f"  cell.pto.do(cell, '{port}', 'in 5 words, what is a cell?')")
    result = cell.pto.do(cell, port, "in 5 words, what is a cell?")
    print(f"    → {str(result)[:200]}")

    # Defuse — see the LLM compartment in the network
    print(f"\n=== CELL DEFUSE ===")
    network = cell.defuse()
    print(f"  substrate_routing: {network['substrate_routing']}")
    print(f"  crystallizations: {len(network['first_crystallizations'])}")
    print(f"  witness_events: {network['witness_events']}")
    print(f"  canary: {network['canary'][:16]}...")

    # Cross-cell demo
    if with_llm:
        print(f"\n=== CROSS-CELL LLM CALL ===")
        from quilt import Quilt
        cell_a = cell_with_llm("alpha")
        cell_b = cell_with_llm("beta")
        preseed_llm_crystal(cell_b, "crystal_llm_seeded_b")
        quilt = Quilt(name="dual")
        quilt.add(cell_a)
        quilt.add(cell_b)
        print(f"  cell_b has crystallized LLM compartment: crystal_llm_seeded_b")
        print(f"  cell_a.ask(cell_b, 'crystal_llm_seeded_b', 'in 5 words, what is a cell?')")
        result = quilt.ask("alpha", "beta", "crystal_llm_seeded_b", "in 5 words, what is a cell?")
        out = result.get("output", "") if isinstance(result, dict) else str(result)
        print(f"  → {str(out)[:300]}")
        print(f"  community canary: {quilt.canary()[:16]}...")
        print(f"  cross-cell meta-witness events: {len(quilt.meta_witness)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--cycles", type=int, default=15)
    ap.add_argument("--no-llm", action="store_true", help="don't wire LLM substrate")
    args = ap.parse_args()
    if args.demo:
        demo(n_cycles=args.cycles, with_llm=not args.no_llm)
