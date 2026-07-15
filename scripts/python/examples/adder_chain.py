"""
adder_chain.py
==============
A two-stage ripple-carry adder chain (two 8-bit full adders in series).

Circuit topology
----------------
  A (Pin) ──┐
            ├──> Adder0 ──> SUM0 (LED)  carry-out ──> Adder1 ──> SUM1 (LED)
  B (Pin) ──┘                                  │
  C (Pin) ─────────────────────────────────────┘

Stage 0: A + B  →  SUM0, carry
Stage 1: carry + C  →  SUM1 (demonstrates how adders chain to handle
         wider operands using only 1-bit primitives)

Run offline to generate a JSON blueprint; or run inside Logisim
(embedded Python) to place directly on the active canvas.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_INPUTS  = 60
X_ADDER0  = 240
X_CARRY   = 360
X_ADDER1  = 500
X_OUTPUTS = 680

Y_A    = 100
Y_B    = 160
Y_C    = 280
Y_MID0 = 130   # vertical centre of Adder0
Y_MID1 = 280   # vertical centre of Adder1

output = Path(__file__).with_name("adder_chain_blueprint.json")

builder = BlueprintBuilder("adder_chain")

# ── Inputs ──────────────────────────────────────────────────────────────────
builder.add_pin("a",  x=X_INPUTS, y=Y_A,  label="A")
builder.add_pin("b",  x=X_INPUTS, y=Y_B,  label="B")
builder.add_pin("c",  x=X_INPUTS, y=Y_C,  label="C (carry-in)")

# ── Stage 0: A + B ──────────────────────────────────────────────────────────
builder.add_adder("add0", x=X_ADDER0, y=Y_MID0, label="Adder0 (A+B)")

# A → Adder0, B → Adder0
builder.add_wire("w_a",  f"{X_INPUTS},{Y_A}", f"{X_ADDER0},{Y_A}")
builder.add_wire("w_b",  f"{X_INPUTS},{Y_B}", f"{X_ADDER0},{Y_B}")

# SUM0 output LED
builder.add_led("sum0", x=X_OUTPUTS, y=Y_MID0, label="SUM0")
builder.add_wire("w_s0", f"{X_ADDER0+60},{Y_MID0}", f"{X_OUTPUTS},{Y_MID0}")

# ── Carry bridge ────────────────────────────────────────────────────────────
# Adder0 carry-out ──> Adder1 carry-in (vertical routing via X_CARRY)
builder.add_wire("w_cout0a", f"{X_ADDER0+60},{Y_MID0+20}", f"{X_CARRY},{Y_MID0+20}")
builder.add_wire("w_cout0b", f"{X_CARRY},{Y_MID0+20}",     f"{X_CARRY},{Y_MID1}")
builder.add_wire("w_cout0c", f"{X_CARRY},{Y_MID1}",        f"{X_ADDER1},{Y_MID1}")

# ── Stage 1: carry + C ──────────────────────────────────────────────────────
builder.add_adder("add1", x=X_ADDER1, y=Y_MID1, label="Adder1 (carry+C)")

builder.add_wire("w_c",  f"{X_INPUTS},{Y_C}", f"{X_ADDER1},{Y_C}")

# SUM1 output LED
builder.add_led("sum1", x=X_OUTPUTS, y=Y_MID1, label="SUM1")
builder.add_wire("w_s1", f"{X_ADDER1+60},{Y_MID1}", f"{X_OUTPUTS},{Y_MID1}")

# Final carry-out LED
builder.add_led("cout", x=X_OUTPUTS, y=Y_MID1 + 60, label="C-OUT")
builder.add_wire("w_co", f"{X_ADDER1+60},{Y_MID1+20}", f"{X_OUTPUTS},{Y_MID1+60}")

builder.save(output)
print(f"[adder_chain] blueprint written → {output}")
