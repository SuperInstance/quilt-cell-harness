"""
quilt.py — multi-cell community on top of cell.py.

A Quilt holds multiple cells. Cells can ask each other via PTO ports.
Cross-cell calls are witnessed on BOTH sides and recorded in a shared
meta-witness chain. The community has its own canary (composed hash) and
its own alive check.

Run:
    python3 quilt.py --demo         # 3-cell community demo with 80 cycles
    python3 quilt.py --cells 5      # 5-cell community
    python3 quilt.py --cycles 30    # shorter run

A community is "alive" when:
  1. Distinct specialisations (cells have different primary substrates)
  2. Cross-cell dependencies (at least one PTO call between cells)
  3. Shared meta-witness (the cross-cell call chain is non-empty)
"""

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Re-use Cell from cell.py
sys.path.insert(0, str(Path(__file__).parent))
from cell import Cell, COMPULSORY_TISSUE


@dataclass
class Quilt:
    """A community of cells. Cross-cell calls + shared meta-witness."""
    name: str
    cells: dict = field(default_factory=dict)        # name -> Cell
    meta_witness: list = field(default_factory=list)  # cross-cell call history
    cycles: int = 0

    def add(self, cell):
        self.cells[cell.name] = cell
        return cell

    def ask(self, caller_name: str, target_name: str, port: str, energy):
        """Cell A asks cell B to invoke a crystallized mechanism on energy.

        Both sides witness the call. The result is the target's output.
        """
        self.cycles += 1
        caller = self.cells.get(caller_name)
        target = self.cells.get(target_name)
        if not caller or not target:
            return {"status": "error", "error": "unknown cell"}
        try:
            output = target.pto.do(target, port, energy)
        except Exception as e:
            output = {"error": str(e)}

        # Witness on both sides
        event = {
            "cycle": self.cycles,
            "caller": caller_name,
            "target": target_name,
            "port": port,
            "energy_hash": hashlib.sha256(str(energy).encode()).hexdigest()[:8],
            "output_hash": hashlib.sha256(str(output).encode()).hexdigest()[:8],
        }
        self.meta_witness.append(event)
        caller.witness_chain.append({"event": "ASKED", **event})
        target.witness_chain.append({"event": "WAS_ASKED", **event})
        return {"status": "ok", "from": target_name, "port": port, "output": output}

    def route_ask(self, caller_name: str, port: str, energy):
        """Cell A asks for `port` and we route to whichever cell has it."""
        candidates = [c for c in self.cells.values()
                      if c.name != caller_name and port in c.pto.ports]
        if not candidates:
            return {"status": "error", "error": f"no cell exposes port '{port}'"}
        target = random.choice(candidates)
        return self.ask(caller_name, target.name, port, energy)

    def call_graph(self):
        """Return {(caller, target): count} from the meta-witness."""
        graph = Counter()
        for ev in self.meta_witness:
            if "caller" in ev and "target" in ev:
                graph[(ev["caller"], ev["target"])] += 1
        return dict(graph)

    def specialisations(self):
        """For each cell, return its top crystallized substrate (= role)."""
        roles = {}
        for name, cell in self.cells.items():
            top = cell.defuse().get("substrate_routing", {})
            if top:
                role = max(top, key=top.get)
                roles[name] = role
        return roles

    def canary(self):
        """Composed canary: each cell's canary + the meta-witness."""
        components = [c.canary() for c in self.cells.values()]
        witness_blob = json.dumps(self.meta_witness[-20:], sort_keys=True, default=str)
        return hashlib.sha256(
            "||".join(components).encode() + witness_blob.encode()
        ).hexdigest()

    def is_alive(self):
        """Community-level alive check.

        A community is alive when:
          1. ALL member cells are alive (each has crystallized >= 1 mechanism)
          2. Distinct specialisations (>= 2 cells have different top substrates)
          3. Cross-cell dependencies (>= 1 call between cells)
          4. Shared meta-witness (meta-witness non-empty)
          5. Compulsory organ types covered (the union of cell specialisations
             covers the community's required substrate set — at the
             COMMUNITY level, the compulsory tissues are distributed across
             cells, not concentrated in one)
        """
        reasons = []

        # 1. Member cells alive (each cell just needs ONE crystallized mechanism)
        cells_alive = {}
        for name, cell in self.cells.items():
            ok, _ = cell.is_alive()
            cells_alive[name] = ok
        if not all(cells_alive.values()):
            dead = [n for n, ok in cells_alive.items() if not ok]
            reasons.append(f"dead cells: {dead}")

        # 2. Distinct specialisations
        roles = self.specialisations()
        if len(set(roles.values())) < 2:
            reasons.append(f"insufficient specialisation: roles={roles}")

        # 3. Cross-cell dependencies
        if not self.call_graph():
            reasons.append("no cross-cell calls")

        # 4. Shared meta-witness
        if not self.meta_witness:
            reasons.append("empty meta-witness")

        # 5. Compulsory organ coverage at community level
        all_substrates = set()
        for cell in self.cells.values():
            for c in cell.compartments.values():
                if c.crystallized:
                    fn_name = getattr(c.transform, '__name__', 'unknown')
                    all_substrates.add(fn_name)
        required = set(COMPULSORY_TISSUE.values())
        missing_organs = required - all_substrates
        if missing_organs:
            reasons.append(f"missing community organs (substrates): {missing_organs}")

        return len(reasons) == 0, reasons

    def defuse(self):
        """Defuse the community: return the high-level organ graph."""
        return {
            "quilt_name": self.name,
            "cells": [
                {
                    "name": c.name,
                    "alive": c.is_alive()[0],
                    "role": self.specialisations().get(c.name),
                    "crystallized": len([x for x in c.compartments.values() if x.crystallized]),
                }
                for c in self.cells.values()
            ],
            "edges": [
                {"caller": c, "target": t, "port": p, "calls": n}
                for (c, t), n in self.call_graph().items()
                for p in {ev["port"] for ev in self.meta_witness if ev["caller"] == c and ev["target"] == t}
            ],
            "specialisations": self.specialisations(),
            "call_count": len(self.meta_witness),
            "quilt_canary": self.canary()[:16],
            "alive": self.is_alive()[0],
            "alive_reasons_if_not": self.is_alive()[1],
        }

    def prune(self, threshold=1):
        """Remove dead cells from the quilt (organ failure / apoptosis).

        A cell is removed when its crystallized compartment count drops
        below the threshold (default 1 — one crystallized mechanism is
        the minimum to participate). Removal is logged on each cell's
        witness chain and the meta-witness; the cell's contributions
        remain visible (no erasure).
        """
        removed = []
        for name, cell in list(self.cells.items()):
            crystallized_count = sum(1 for c in cell.compartments.values() if c.crystallized)
            if crystallized_count < threshold:
                # Witness: the community records the cell's exit (no erasure)
                event = {
                    "cycle": self.cycles,
                    "event": "CELL_PRUNED",
                    "cell": cell.name,
                    "crystallized_at_prune": crystallized_count,
                    "witnesses_at_prune": len(cell.witness_chain.chain),
                }
                self.meta_witness.append(event)
                cell.witness_chain.append({**event, "scope": "self"})
                removed.append(name)
                del self.cells[name]
        return removed


# === DEMO ===

def demo(n_cells=3, n_cycles=80):
    print(f"=== COMMUNITY DEMO ({n_cells} cells, {n_cycles} cycles) ===\n")

    # Build the community
    quilt = Quilt(name="first")
    for i in range(n_cells):
        cell = Cell(name=f"cell_{chr(ord('a') + i)}")
        quilt.add(cell)
    print(f"Seeded {n_cells} cells: {list(quilt.cells.keys())}")
    print(f"Seeded nudges (each cell): {list(quilt.cells['cell_a'].nudges.forbidden)}\n")

    # Energies — biased so different cells naturally crystallize different substrates
    # (echo-heavy, sha-heavy, reverse-heavy in rotation)
    energy_buckets = {
        "echo": ["echo this back", "echo again", "echo one more", "echo please"],
        "reverse": ["reverse that", "reverse this", "reverse again", "reverse please"],
        "sha256": ["hash this", "compute sha256", "compute hash", "sha256 of X"],
        "stub_llm": ["ask the llm", "stub a call", "fake llm", "llm stub"],
    }

    # Phase 1: each cell runs on its own biases for some cycles (independent morphogenesis)
    per_cell_cycles = max(8, n_cycles // 4)
    for cell_name, cell in quilt.cells.items():
        # Pick a substrate bias for this cell
        substrate = random.choice(list(energy_buckets.keys()))
        for _ in range(per_cell_cycles):
            energy = random.choice(energy_buckets[substrate])
            cell.process(energy)
        crystal = [c.name for c in cell.compartments.values() if c.crystallized]
        print(f"  {cell_name} (biased {substrate}): {len(crystal)} crystallized after {per_cell_cycles} cycles")

    print()

    # Phase 2: cross-cell calls — each cell asks others for what they don't have
    print("Phase 2: cross-cell asks...")
    for round_idx in range(n_cycles - per_cell_cycles * n_cells):
        # Pick a random caller
        caller = random.choice(list(quilt.cells.values()))
        # Pick a port to ask for (any crystallized port from any cell)
        all_ports = []
        for c in quilt.cells.values():
            for p in c.pto.ports:
                if p.startswith("crystal_"):
                    all_ports.append(p)
        if not all_ports:
            continue
        port = random.choice(all_ports)
        energy = f"ask_{round_idx}"
        result = quilt.route_ask(caller.name, port, energy)
        if round_idx < 5 or round_idx % 20 == 0:
            print(f"  [{round_idx:03d}] {caller.name} asks '{port}' → {result.get('status')}")

    print()

    # Phase 3: defuse the community
    print("=== COMMUNITY DEFUSE ===")
    network = quilt.defuse()
    print(f"\n  alive: {network['alive']}")
    if not network['alive']:
        print(f"  reasons: {network['alive_reasons_if_not']}")
    print(f"\n  cells:")
    for c in network['cells']:
        print(f"    {c['name']:10s} role={c['role']:10s} crystallized={c['crystallized']} alive={c['alive']}")
    print(f"\n  specialisations: {network['specialisations']}")
    print(f"\n  edges (cross-cell calls):")
    for e in network['edges'][:10]:
        print(f"    {e['caller']:10s} → {e['target']:10s} port={e['port']:30s} calls={e['calls']}")
    print(f"\n  total calls: {network['call_count']}")
    print(f"  community canary: {network['quilt_canary']}...")

    # Phase 4: demonstrate cross-cell call through the quilt
    print("\n=== LIVE CROSS-CELL CALL ===")
    # Find a crystallized port on any cell
    if network['edges']:
        first_edge = network['edges'][0]
        caller = quilt.cells[first_edge['caller']]
        target = quilt.cells[first_edge['target']]
        port = first_edge['port']
        print(f"  {caller.name}.ask({target.name}, '{port}', 'hello world')")
        result = quilt.ask(caller.name, target.name, port, "hello world")
        print(f"    → {result}")
    else:
        print("  no crystallized cross-cell ports yet — community not fully formed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--cells", type=int, default=3)
    ap.add_argument("--cycles", type=int, default=80)
    args = ap.parse_args()

    if args.demo or args.cells == 3:
        demo(args.cells, args.cycles)
    else:
        demo(args.cells, args.cycles)


if __name__ == "__main__":
    main()
