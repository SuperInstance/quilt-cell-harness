"""
qult.py — multiple quilts as one organism (fractal composition).

A Qult holds multiple Quilts. Quilts can ask each other via PTO
surfaces. Cross-quilt calls are witnessed on both quilts AND on
the qult. The qult has its own canary (composed from quilt
canaries) and its own alive check.

Run:
    python3 qult.py --demo

A Qult is "alive" when:
  1. All member quilts are alive
  2. Distinct quilt specializations
  3. Cross-quilt dependencies (>= 1 call between quilts)
  4. Qult-level meta-witness non-empty
  5. Qult-level compulsory organs (substrates) covered across quilts
"""

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cell import Cell
from quilt import Quilt


@dataclass
class Qult:
    """Multiple quilts as one organism."""
    name: str
    quilts: dict = field(default_factory=dict)        # name -> Quilt
    meta_meta_witness: list = field(default_factory=list)  # cross-quilt calls
    cycles: int = 0

    def add(self, quilt):
        self.quilts[quilt.name] = quilt
        return quilt

    def ask(self, caller_quilt_name: str, target_quilt_name: str, port: str, energy):
        """Quilt A asks Quilt B to invoke a crystallized mechanism.

        Both quilts witness the call. The qult meta-meta-witness records it.
        """
        self.cycles += 1
        caller = self.quilts.get(caller_quilt_name)
        target = self.quilts.get(target_quilt_name)
        if not caller or not target:
            return {"status": "error", "error": "unknown quilt"}

        # Route to a cell in the target quilt that exposes the port
        target_cells_with_port = [c for c in target.cells.values() if port in c.pto.ports]
        if not target_cells_with_port:
            return {"status": "error", "error": f"no cell in '{target_quilt_name}' exposes port '{port}'"}
        cell = random.choice(target_cells_with_port)

        try:
            output = cell.pto.do(cell, port, energy)
        except Exception as e:
            output = {"error": str(e)}

        # Event uses quilt-compatible schema so call_graph() works on
        # the recipient's meta-witness (quilt semantics). We tag the
        # cross-quilt entries distinctly so the qult is still traceable.
        event = {
            "cycle": self.cycles,
            "caller": caller_quilt_name,
            "target": target_quilt_name,
            "target_cell": cell.name,
            "port": port,
            "energy_hash": hashlib.sha256(str(energy).encode()).hexdigest()[:8],
            "output_hash": hashlib.sha256(str(output).encode()).hexdigest()[:8],
            "qult_event": True,
        }
        self.meta_meta_witness.append(event)
        caller.meta_witness.append({**event, "event": "ASKED_QUILT"})
        target.meta_witness.append({**event, "event": "WAS_ASKED_QUILT"})
        return {"status": "ok", "from_quilt": target_quilt_name, "from_cell": cell.name, "port": port, "output": output}

    def call_graph(self):
        """Return {(caller_quilt, target_quilt): count}."""
        graph = Counter()
        for ev in self.meta_meta_witness:
            graph[(ev["caller"], ev["target"])] += 1
        return dict(graph)

    def specialisations(self):
        """For each quilt, return its primary substrate (= lead role).

        The primary is the substrate with the highest total calls across
        the quilt's cells (or alphabetically first if all zero).
        """
        roles = {}
        for name, quilt in self.quilts.items():
            substrate_totals = Counter()
            for cell in quilt.cells.values():
                for substrate, count in cell.engine.calls.items():
                    substrate_totals[substrate] += count
            if substrate_totals:
                roles[name] = max(substrate_totals, key=substrate_totals.get)
            else:
                roles[name] = "empty"
        return roles

    def canary(self):
        """Composed qult canary: each quilt's canary + the meta-meta-witness."""
        components = [q.canary() for q in self.quilts.values()]
        witness_blob = json.dumps(self.meta_meta_witness[-20:], sort_keys=True, default=str)
        return hashlib.sha256(
            "||".join(components).encode() + witness_blob.encode()
        ).hexdigest()

    def is_alive(self):
        """Qult-level alive check."""
        reasons = []

        # 1. All member quilts alive
        quilts_alive = {}
        for name, quilt in self.quilts.items():
            ok, _ = quilt.is_alive()
            quilts_alive[name] = ok
        if not all(quilts_alive.values()):
            dead = [n for n, ok in quilts_alive.items() if not ok]
            reasons.append(f"dead quilts: {dead}")

        # 2. Distinct quilt specializations
        roles = self.specialisations()
        # Quilt roles differ if their PRIMARY substrates differ.
        # (Mirror biology: an organism has organ systems with distinct roles,
        # even if many cell types are similar.)
        primary_substrates = list(roles.values())
        if len(set(primary_substrates)) < len(roles):
            reasons.append(f"quilt roles not distinct enough: {roles}")

        # 3. Cross-quilt dependencies
        if not self.call_graph():
            reasons.append("no cross-quilt calls")

        # 4. Qult-level meta-witness
        if not self.meta_meta_witness:
            reasons.append("empty meta-meta-witness")

        # 5. Qult-level compulsory organ coverage
        all_substrates = set()
        for quilt in self.quilts.values():
            for cell in quilt.cells.values():
                for c in cell.compartments.values():
                    if c.crystallized:
                        fn_name = getattr(c.transform, '__name__', 'unknown')
                        all_substrates.add(fn_name)
        required = {"echo", "reverse", "sha256", "stub_llm"}
        missing = required - all_substrates
        if missing:
            reasons.append(f"missing qult organs: {missing}")

        return len(reasons) == 0, reasons

    def defuse(self):
        """Defuse the qult: return the organ-system-level graph."""
        return {
            "qult_name": self.name,
            "quilts": [
                {
                    "name": q.name,
                    "alive": q.is_alive()[0],
                    "cells": len(q.cells),
                    "crystallized": sum(
                        sum(1 for c in cell.compartments.values() if c.crystallized)
                        for cell in q.cells.values()
                    ),
                }
                for q in self.quilts.values()
            ],
            "edges": [
                {"caller": c, "target": t, "calls": n}
                for (c, t), n in self.call_graph().items()
            ],
            "specialisations": self.specialisations(),
            "call_count": len(self.meta_meta_witness),
            "qult_canary": self.canary()[:16],
            "alive": self.is_alive()[0],
            "alive_reasons_if_not": self.is_alive()[1],
        }


def demo():
    """Build a qult of 2 quilts; each quilt has 4 cells biased across
    all substrates; phase 2 fires intra-quilt calls (so quilts become
    alive); phase 3 fires inter-quilt calls (so qult becomes alive)."""
    random.seed(42)
    print("=== QULT DEMO ===\n")

    qult = Qult(name="first_qult")

    substrates = ['echo', 'reverse', 'sha256', 'stub_llm']    # Build a cell pre-seeded with crystallized compartments for ONE
    # substrate. This makes the cell a specialist by design — natural
    # morphogenesis would converge here but for the demo we skip the
    # random walk to keep the demo stable across seeds.
    def specialist_cell(name, substrate):
        from cell import Compartment
        cell = Cell(name=name)
        # Map substrate to its substrate function
        substrate_fn = cell.engine.substrates[substrate]
        # Pre-create one crystallized compartment for this substrate
        crystal_name = f"crystal_seed_{substrate}"
        cell.compartments[crystal_name] = Compartment(
            name=crystal_name,
            transform=substrate_fn,
            crystallized=True,
            uses=10,
        )
        cell.crystallizations.append({"cycle": 0, "from": "seed", "to": crystal_name, "uses_before_promotion": 10})
        # Expose the crystal as a PTO port
        cell.pto.expose(crystal_name, lambda c, energy, _n=crystal_name: c.compartments[_n].process(energy))
        # Make sure the cell's substrate_routing shows this substrate
        # as its primary (engine.calls is the seed for that).
        cell.engine.calls = {s: 0 for s in cell.engine.substrates}
        cell.engine.calls[substrate] = 100
        return cell

    # Build a quilte from specialist cells, biased so each quilt has a
    # designated LEAD cell whose substrate is that quilt's primary role.
    def build_quilt(name, lead_substrate, all_subs=('echo', 'reverse', 'sha256', 'stub_llm')):
        quilt = Quilt(name=name)
        # First cell is the LEAD — handles engine.calls weighting so
        # the cell has a clear primary substrate.
        lead_cell = specialist_cell(f"{name}_lead_{lead_substrate}", lead_substrate)
        # Boost its engine.calls so it dominates substrate_routing
        lead_cell.engine.calls[lead_substrate] = 1000
        quilt.add(lead_cell)
        # Add the OTHER substrates as supporting specialists
        for sub in all_subs:
            if sub == lead_substrate:
                continue
            cell = specialist_cell(f"{name}_{sub}", sub)
            quilt.add(cell)
        return quilt

    # Quilt alpha: lead substrate = echo ("language" quilt).
    quilt_a = build_quilt("quilt_alpha", lead_substrate="echo")
    qult.add(quilt_a)

    # Quilt beta: lead substrate = sha256 ("compute" quilt).
    quilt_b = build_quilt("quilt_beta", lead_substrate="sha256")
    qult.add(quilt_b)

    print(f"Quilt alpha cells: {list(quilt_a.cells.keys())}")
    print(f"Quilt beta cells: {list(quilt_b.cells.keys())}")

    # Phase 2 — intra-quilt calls to make quilts alive
    print("\nPhase 2: intra-quilt calls (80 cycles per quilt)...")
    for round_idx in range(80):
        for quilt in [quilt_a, quilt_b]:
            cells = list(quilt.cells.values())
            caller = random.choice(cells)
            target = random.choice([c for c in cells if c.name != caller.name])
            target_ports = [p for p in target.pto.ports if p.startswith("crystal_")]
            if not target_ports:
                continue
            port = random.choice(target_ports)
            quilt.ask(caller.name, target.name, port, f"intra_{round_idx}")

    print(f"  Quilt alpha alive: {quilt_a.is_alive()[0]}  ({quilt_a.is_alive()[1]})")
    print(f"  Quilt beta alive : {quilt_b.is_alive()[0]}  ({quilt_b.is_alive()[1]})")

    # Phase 3 — inter-quilt calls
    print("\nPhase 3: cross-quilt asks (40 cycles)...")
    for round_idx in range(40):
        caller_quilt = random.choice([quilt_a, quilt_b])
        target_quilt = quilt_b if caller_quilt is quilt_a else quilt_a
        target_cells = list(target_quilt.cells.values())
        target_cell = random.choice(target_cells)
        target_ports = [p for p in target_cell.pto.ports if p.startswith("crystal_")]
        if not target_ports:
            continue
        port = random.choice(target_ports)
        energy = f"qult_call_{round_idx}"
        result = qult.ask(caller_quilt.name, target_quilt.name, port, energy)
        if round_idx < 5 or round_idx % 10 == 0:
            print(f"  [{round_idx:02d}] {caller_quilt.name}.ask({target_quilt.name}, '{port}') → {result.get('status')}")

    print()

    # Phase 4 — defuse the qult
    print("=== QULT DEFUSE ===")
    network = qult.defuse()
    print(f"\n  alive: {network['alive']}")
    if not network['alive']:
        print(f"  reasons: {network['alive_reasons_if_not']}")
    print(f"\n  quilts:")
    for q in network['quilts']:
        print(f"    {q['name']:18s} alive={q['alive']}  cells={q['cells']}  crystallized={q['crystallized']}")
    print(f"\n  specialisations (each quilt's crystallized-substrate set):")
    for name, ro in network['specialisations'].items():
        print(f"    {name:18s} → {ro}")
    print(f"\n  edges (cross-quilt calls):")
    for e in network['edges']:
        print(f"    {e['caller']:18s} → {e['target']:18s}  calls={e['calls']}")
    print(f"\n  total calls: {network['call_count']}")
    print(f"  qult canary: {network['qult_canary']}...")

    # Phase 5 — live cross-quilt call
    print("\n=== LIVE CROSS-QUILT CALL ===")
    quilt_b_cells = list(quilt_b.cells.values())
    target_cell = quilt_b_cells[0]
    target_ports = [p for p in target_cell.pto.ports if p.startswith("crystal_")]
    if target_ports:
        port = target_ports[0]
        print(f"  quilt_alpha.ask(quilt_beta, '{port}', 'hello world')")
        result = qult.ask("quilt_alpha", "quilt_beta", port, "hello world")
        print(f"    → {result}")

    # Phase 6 — apoptosis (organ failure / cell death)
    # Force one of quilt_alpha's cells to lose its crystallized
    # compartments, then prune it. Watch the community refuse the death
    # silently — the witness chain records the exit.
    print("\n=== APOPTOSIS (organ failure / cell death) ===")
    dying_cell_name = list(quilt_a.cells.keys())[1]   # second cell of quilt_alpha
    print(f"  Killing cell: {dying_cell_name}")
    for c in quilt_a.cells[dying_cell_name].compartments.values():
        c.crystallized = False
    pruned = quilt_a.prune(threshold=1)
    print(f"  Quilt alpha pruned cells: {pruned}")
    print(f"  Quilt alpha still alive? {quilt_a.is_alive()[0]}  ({quilt_a.is_alive()[1]})")
    print(f"  Qult still alive? {qult.is_alive()[0]}  ({qult.is_alive()[1]})")

    # Phase 7 — final defuse (cell shrunk, evidence survives)
    print("\n=== FINAL QULT DEFUSE (after apoptosis) ===")
    network = qult.defuse()
    print(f"  alive: {network['alive']}")
    print(f"  quilts:")
    for q in network['quilts']:
        print(f"    {q['name']:18s} alive={q['alive']}  cells={q['cells']}  crystallized={q['crystallized']}")
    print(f"  qult canary (now): {network['qult_canary']}...")
    print(f"  (Earlier canary was: 000b7bc8f33be562...)")


if __name__ == "__main__":
    demo()
