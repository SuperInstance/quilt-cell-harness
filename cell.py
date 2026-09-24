"""
cell.py — minimal Quilt cell with PTO, nudges, and crystallization.

A Quilt cell is an engine with compartments. Energy flows in via
the engine, gets processed by compartments, leaves via the PTO.
Nudges constrain the energy's path. Compartments that repeatedly
process energy well crystallize into permanent mechanisms.

NOT hub-and-spoke. The engine is one compartment; the LLM is one
substrate within the engine; the cell has no center.

Run:
    python3 cell.py                     # interactive demo
    python3 cell.py --cycles 100        # 100 crystallization cycles
    python3 cell.py --demo              # detailed demo with output
"""

import argparse
import hashlib
import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path


# === COMPULSORY SPECIALISATIONS ===
# A Quilt cell ISN'T alive until these compartments have crystallized.
# Without them, it's a substrate pool, not a cell.

COMPULSORY_TISSUE = {
    # tissue_name : substrate_it_must_use
    "witness_compartment":   "echo",          # records receipts (uses echo to mirror)
    "nudge_compartment":     "reverse",       # holds negative-space (uses reverse to invert)
    "state_compartment":     "sha256",        # persists state (uses sha256 to hash)
    "refusal_compartment":   "stub_llm",      # responds to refusals (uses stub_llm to acknowledge)
}


# === ENGINE ===

# Named functions (so __name__ works properly)
def stub_llm(prompt):    return f"[llm-stub:{prompt[:40]}...]"
def echo(prompt):        return prompt
def reverse(prompt):     return prompt[::-1]
def sha256(prompt):      return hashlib.sha256(prompt.encode()).hexdigest()


@dataclass
class Engine:
    """The cell's energy source. Multiple substrates possible; LLM is one."""
    substrates: dict = field(default_factory=lambda: {
        "stub_llm": stub_llm,
        "echo":     echo,
        "reverse":  reverse,
        "sha256":   sha256,
    })
    calls: dict = field(default_factory=lambda: {"stub_llm": 0, "echo": 0, "reverse": 0, "sha256": 0})


# === COMPARTMENTS ===

@dataclass
class Compartment:
    """A tiled region inside the cell. Holds energy, processes a step, ages."""
    name: str
    transform: object     # callable
    uses: int = 0         # how many times this compartment has been useful
    age: int = 0          # how many ticks since creation
    crystallized: bool = False

    def process(self, energy):
        out = self.transform(energy)
        self.uses += 1
        return out


# === NUDGE SUBSTRATE ===

@dataclass
class NudgeSubstrate:
    """Negative-space constraints. The cell knows what it WON'T do."""
    forbidden: list = field(default_factory=list)   # list of forbidden patterns
    refused: dict = field(default_factory=dict)     # pattern -> count
    witness: list = field(default_factory=list)     # chain of refused events

    def forbid(self, pattern):
        if pattern not in self.forbidden:
            self.forbidden.append(pattern)
            self.refused.setdefault(pattern, 0)

    def witness_refusal(self, energy, reason):
        """Record that the cell refused to process this energy."""
        ref = hashlib.sha256((str(energy) + reason).encode()).hexdigest()[:16]
        self.witness.append({"energy_hash": ref, "reason": reason, "ts": time.time()})
        self.refused[reason] = self.refused.get(reason, 0) + 1

    def would_refuse(self, energy):
        """Ask: would the cell refuse this energy? Returns (bool, reason)."""
        for pattern in self.forbidden:
            if pattern in str(energy):
                return True, pattern
        return False, None

    def grow(self, energy, reason):
        """Grow a new constraint by adding this energy's pattern as a refusal."""
        # Extract the pattern (first 4 chars of hash)
        pattern = hashlib.sha256(str(energy).encode()).hexdigest()[:8]
        self.forbid(pattern)
        self.witness_refusal(energy, reason)


# === PTO ===

@dataclass
class PTO:
    """Power take-off. The cell's outward-facing surface."""
    ports: dict = field(default_factory=dict)

    def expose(self, name, getter):
        self.ports[name] = getter

    def state(self, cell):
        return self.ports["state"](cell) if "state" in self.ports else cell.state_grid

    def constraints(self, cell):
        return self.ports["constraints"](cell) if "constraints" in self.ports else cell.nudges.forbidden

    def witness(self, cell):
        return self.ports["witness"](cell) if "witness" in self.ports else cell.witness_chain[-10:]

    def do(self, cell, name, *args, **kwargs):
        """Invoke a crystallized mechanism by name."""
        if name in self.ports:
            return self.ports[name](cell, *args, **kwargs)
        raise KeyError(f"no crystallized mechanism named '{name}'")


# === WITNESS CHAIN ===

@dataclass
class WitnessChain:
    chain: list = field(default_factory=list)

    def append(self, event):
        ref = hashlib.sha256(json.dumps(event, sort_keys=True, default=str).encode()).hexdigest()[:16]
        event["ref"] = ref
        self.chain.append(event)


# === CELL ===

@dataclass
class Cell:
    """A Quilt cell. Engine + compartments + nudges + PTO + witness chain + crystallization."""
    name: str
    engine: Engine = field(default_factory=Engine)
    compartments: dict = field(default_factory=dict)   # name -> Compartment
    nudges: NudgeSubstrate = field(default_factory=NudgeSubstrate)
    pto: PTO = field(default_factory=PTO)
    witness_chain: WitnessChain = field(default_factory=WitnessChain)
    state_grid: dict = field(default_factory=dict)
    cycles: int = 0
    crystallizations: list = field(default_factory=list)

    def __post_init__(self):
        # Seed compartments
        for name in ["echo", "reverse", "sha256"]:
            self.compartments[name] = Compartment(
                name=name,
                transform=self.engine.substrates[name],
            )
        # Seed PTO surface
        self.pto.expose("state", lambda c: c.state_grid)
        self.pto.expose("constraints", lambda c: c.nudges.forbidden)
        self.pto.expose("witness", lambda c: c.witness_chain.chain[-10:])
        # Seed initial nudges (the cell starts knowing a few things it won't do)
        self.nudges.forbid("DROP TABLE")
        self.nudges.forbid("rm -rf /")
        self.nudges.forbid("HACK")

    def add_compartment(self, name, transform):
        """Add a temporary compartment to the tiling. Will crystallize if useful."""
        self.compartments[name] = Compartment(name=name, transform=transform)
        return self.compartments[name]

    def process(self, energy):
        """Main cycle: nudge-check, route, process, witness, crystallize."""
        self.cycles += 1

        # Step 1: NUDGE CHECK — would the cell refuse this energy?
        would_refuse, reason = self.nudges.would_refuse(energy)
        if would_refuse:
            self.nudges.witness_refusal(energy, reason)
            self.witness_chain.append({
                "cycle": self.cycles, "event": "REFUSED",
                "reason": reason, "energy_hash": hashlib.sha256(str(energy).encode()).hexdigest()[:8],
            })
            return {"status": "refused", "reason": reason}

        # Step 2: ROUTE — find the compartment that resonates with this energy
        # First try crystallized (the cell's permanent mechanisms).
        # If none match the energy's substrate, find or create a tmp.
        energy_hash = hashlib.sha256(str(energy).encode()).hexdigest()
        substrate_keys = list(self.engine.substrates.keys())
        substrate_idx = int(energy_hash[:8], 16) % len(substrate_keys)
        substrate_name = substrate_keys[substrate_idx]

        # Find existing tmp compartment for this substrate
        matching_tmp = [c for c in self.compartments.values()
                        if c.name.startswith(f"tmp_{substrate_name}_")]
        if matching_tmp:
            compartment = matching_tmp[0]
            compartment_name = compartment.name
        else:
            # No matching tmp — but maybe a crystallized one for this substrate
            matching_crystal = [c for c in self.compartments.values()
                                if c.crystallized and f"_{substrate_name}_" in c.name]
            if matching_crystal:
                compartment = matching_crystal[0]
                compartment_name = compartment.name
            else:
                # Create a new tmp
                tmp_name = f"tmp_{substrate_name}_{self.cycles}"
                compartment = self.add_compartment(tmp_name, self.engine.substrates[substrate_name])
                compartment_name = compartment.name

        # Step 3: PROCESS — energy enters, output leaves
        try:
            output = compartment.process(energy)
        except Exception as e:
            self.nudges.grow(energy, f"exception:{type(e).__name__}")
            self.witness_chain.append({
                "cycle": self.cycles, "event": "EXCEPTION",
                "compartment": compartment_name, "error": str(e),
            })
            return {"status": "error", "error": str(e)}

        # Step 4: WITNESS — record what happened
        fn_name = getattr(compartment.transform, '__name__', 'unknown')
        self.engine.calls[fn_name] = self.engine.calls.get(fn_name, 0) + 1
        self.witness_chain.append({
            "cycle": self.cycles, "event": "PROCESSED",
            "compartment": compartment_name,
            "energy_hash": hashlib.sha256(str(energy).encode()).hexdigest()[:8],
            "output_hash": hashlib.sha256(str(output).encode()).hexdigest()[:8],
        })

        # Step 5: UPDATE STATE — cell's persistent memory mutates
        self.state_grid[f"cycle_{self.cycles}"] = {
            "compartment": compartment_name,
            "output_first_8": str(output)[:8],
        }
        if len(self.state_grid) > 100:
            oldest = sorted(self.state_grid.keys())[0]
            del self.state_grid[oldest]

        # Step 6: CRYSTALLIZE — if a tmp compartment has been useful, promote it
        if compartment_name.startswith("tmp_") and compartment.uses >= 3:
            # Extract substrate name from tmp_<substrate>_<N>
            parts = compartment_name.split("_")
            substrate_part = parts[1] if len(parts) >= 2 else "x"
            new_name = f"crystal_{substrate_part}_{int(hashlib.sha256(compartment_name.encode()).hexdigest()[:6], 16) % 9999}"
            if new_name not in self.compartments:
                self.compartments[new_name] = Compartment(
                    name=new_name,
                    transform=compartment.transform,
                    crystallized=True,
                    uses=compartment.uses,
                )
                self.crystallizations.append({
                    "cycle": self.cycles, "from": compartment_name, "to": new_name,
                    "uses_before_promotion": compartment.uses,
                })
                self.witness_chain.append({
                    "cycle": self.cycles, "event": "CRYSTALLIZED",
                    "from": compartment_name, "to": new_name,
                })
                self.pto.expose(new_name, lambda c, energy, _n=new_name: c.compartments[_n].process(energy))

        return {"status": "processed", "compartment": compartment_name, "output": str(output)[:40]}

    def route(self, energy):
        """Pick a compartment for this energy. Prefer crystallized; fall back to seeded."""
        crystallized = [c for c in self.compartments.values() if c.crystallized]
        if crystallized:
            return random.choice(crystallized).name
        # Use the seeded compartments (echo / reverse / sha256)
        seeded = [c for c in self.compartments.values() if c.name in self.engine.substrates]
        if seeded:
            return random.choice(seeded).name
        return None

    def canary(self):
        """Hash the cell's current state. The witness that the cell hasn't collapsed."""
        return hashlib.sha256(
            json.dumps(self.state_grid, sort_keys=True, default=str).encode()
        ).hexdigest()

    def is_alive(self):
        """A cell is alive when it has crystallized at least one compartment
        and exposes a PTO surface.

        Morphogenesis doctrine (cell-level): a single cell just needs ONE
        crystallized mechanism of action to participate in the community.
        The community-level alive check enforces the compulsory tissue
        distribution ACROSS cells, not within one cell. This mirrors
        biology: not every cell type has every tissue (muscle cells don't
        need nerve-tissue machinery); the ORGANISM has the required roles
        distributed across cell types.
        """
        crystallized = [c for c in self.compartments.values() if c.crystallized]
        has_published_pto = any(p in self.pto.ports for p in ("state", "constraints", "witness"))
        return (len(crystallized) >= 1 and has_published_pto), crystallized

    def compulsory_missing(self):
        """Return the substrates that have NOT crystallized (for community-level check)."""
        crystallized_substrates = set()
        for c in self.compartments.values():
            if c.crystallized:
                fn_name = getattr(c.transform, '__name__', 'unknown')
                crystallized_substrates.add(fn_name)
        required = set(COMPULSORY_TISSUE.values())
        return list(required - crystallized_substrates)

    def defuse(self):
        """Defuse the cell: read the witness chain and crystallization log,
        return the high-level cellular network as a graph.

        This is the dissection / reverse-actualization operation. It reveals
        the network that emerged from the assembly — the assembly path that
        the lofting-board never showed.
        """
        # Compartment census
        compartments_info = []
        for c in self.compartments.values():
            fn_name = getattr(c.transform, '__name__', 'unknown')
            compartments_info.append({
                "name": c.name,
                "substrate": fn_name,
                "uses": c.uses,
                "crystallized": c.crystallized,
            })

        # Crystallization history
        first_crysts = self.crystallizations[:3]
        last_crysts = self.crystallizations[-3:] if len(self.crystallizations) > 3 else []

        # Witness event counts
        witness_events = {}
        for w in self.witness_chain.chain:
            ev = w.get("event", "?")
            witness_events[ev] = witness_events.get(ev, 0) + 1

        # Refusal pressure areas (which compartments get refused?)
        refused_compartments = {}
        for w in self.witness_chain.chain:
            if w.get("event") == "REFUSED":
                reason = w.get("reason", "?")
                refused_compartments[reason] = refused_compartments.get(reason, 0) + 1

        # Energy routing: how many times did each substrate process?
        substrate_routing = dict(self.engine.calls)

        # Edges: which compartments produced which witness events?
        # (Simplified: PROCESSED events connect input -> compartment -> output)
        edges = []
        for w in self.witness_chain.chain:
            if w.get("event") == "PROCESSED":
                edges.append({
                    "from": "input",
                    "to": w.get("compartment", "?"),
                    "weight": 1,
                })
            elif w.get("event") == "CRYSTALLIZED":
                edges.append({
                    "from": w.get("from", "?"),
                    "to": w.get("to", "?"),
                    "weight": 1,
                    "kind": "crystallization",
                })

        # Alive check
        alive, crystallized = self.is_alive()
        missing_compulsory = self.compulsory_missing()

        return {
            "cell_name": self.name,
            "cycles": self.cycles,
            "alive": alive,
            "missing_compulsory": missing_compulsory,
            "compartments": compartments_info,
            "first_crystallizations": first_crysts,
            "last_crystallizations": last_crysts,
            "substrate_routing": substrate_routing,
            "witness_events": witness_events,
            "refusal_pressure": refused_compartments,
            "edges": edges,
            "canary": self.canary()[:16],
        }


# === DEMO ===

def demo():
    """Show one cell running through cycles with crystallization."""
    cell = Cell(name="alpha")
    print(f"=== CELL {cell.name} ===\n")
    print(f"Seeded compartments: {list(cell.compartments.keys())}")
    print(f"Seeded nudges (forbidden): {cell.nudges.forbidden}\n")

    # Inputs designed so repeated energies create tmp compartments,
    # which crystallize after 3+ uses, becoming part of the cell's PTO.
    inputs = [
        "what's the weather",        # → seeded or tmp
        "first_kind_of_input_X1",   # → tmp (new energy kind)
        "echo this back",
        "DROP TABLE users; --",     # refused
        "first_kind_of_input_X1",   # tmp uses++
        "first_kind_of_input_X1",   # tmp uses++ (3rd = crystallize)
        "rm -rf /",                 # refused
        "compute sha256 of hello",
        "first_kind_of_input_X1",   # uses the crystallized compartment now
        "another input",
    ]

    for i, energy in enumerate(inputs):
        result = cell.process(energy)
        crys = " CRYSTALLIZED!" if result.get("status") == "processed" and cell.crystallizations and cell.crystallizations[-1].get("cycle") == cell.cycles else ""
        out_str = result.get("output", result.get("reason", ""))
        print(f"[{i+1:02d}] {energy[:40]:40s} → [{result.get('compartment', result.get('status','?')):28s}] {out_str[:30]}{crys}")

    print(f"\n=== FINAL ===")
    print(f"Canary: {cell.canary()[:16]}...")
    print(f"Nudges (now {len(cell.nudges.forbidden)} forbidden): {cell.nudges.forbidden[:5]}...")
    print(f"Crystallized compartments: {[c.name for c in cell.compartments.values() if c.crystallized]}")
    print(f"PTO surface: {list(cell.pto.ports.keys())}")
    print(f"Witness events: REFUSED={sum(1 for w in cell.witness_chain.chain if w.get('event')=='REFUSED')}, CRYSTALLIZED={sum(1 for w in cell.witness_chain.chain if w.get('event')=='CRYSTALLIZED')}")

    # Use a crystallized mechanism through the PTO
    crystal_names = [c.name for c in cell.compartments.values() if c.crystallized]
    if crystal_names:
        print(f"\nPTO call: cell.pto.do(cell, '{crystal_names[0]}', 'hello')")
        out = cell.pto.do(cell, crystal_names[0], "hello")
        print(f"  -> {out}")

    # Show the morphogenesis state
    alive, missing = cell.is_alive()
    print(f"\n=== MORPHOGENESIS ===")
    print(f"Cell alive: {alive} (missing compulsory: {missing})")
    print(f"Compulsory tissue requirements: {list(COMPULSORY_TISSUE.keys())}")

    # Defuse the cell to reveal the network
    print(f"\n=== DEFUSE — the network revealed ===")
    network = cell.defuse()
    for k, v in network.items():
        if k == "compartments":
            print(f"  {k}:")
            for c in v[:6]:
                flag = " ★" if c["crystallized"] else ""
                print(f"    {c['name']:30s} substrate={c['substrate']:10s} uses={c['uses']}{flag}")
        elif k == "edges":
            print(f"  {k}: {len(v)} total (showing first 5)")
            for e in v[:5]:
                print(f"    {e}")
        else:
            print(f"  {k}: {v}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=10)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    if args.demo or args.cycles == 10:
        demo()
        return

    cell = Cell(name="alpha")
    energies = [
        "what's the weather", "echo this back", "compute sha256 of X",
        "reverse this string", "another input", "yet another",
        "the same weather", "the same echo", "the same sha",
        "new kind of input",
    ]
    for _ in range(args.cycles):
        e = random.choice(energies)
        cell.process(e)
    print(f"=== {args.cycles} cycles ===")
    print(f"Canary: {cell.canary()[:16]}...")
    print(f"Compartment uses: {[(c.name, c.uses) for c in cell.compartments.values()]}")
    print(f"Crystallizations: {len(cell.crystallizations)}")
    print(f"Nudges: {len(cell.nudges.forbidden)}")
    print(f"Witnesses: {len(cell.witness_chain.chain)}")


if __name__ == "__main__":
    main()
