"""
simple_counter.py
=================
The simplest useful circuit: a free-running 4-bit counter clocked by
an AND gate whose inputs are a clock and an enable pin.

Circuit topology
----------------
  CLK  (Pin) ──┐
               ├──> AND gate ──> Counter clock-in
  EN   (Pin) ──┘
  
  Counter Q0..Q3 ──> LEDs Q0..Q3

This example uses the low-level `Circuit` / `Counter` / `Gate` / `Wire`
API rather than the higher-level BlueprintBuilder, demonstrating both
approaches are equivalent.  The AND gate acts as a gated clock so the
counter only increments when EN=1.

Works in embedded mode (places components on the live canvas) and in
offline mode (writes a JSON blueprint to a file).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.api import Circuit, Clock, Counter, Gate, Led, Pin, Wire

# ── Layout constants ────────────────────────────────────────────────────────
X_PINS   = 60
X_GATE   = 220
X_CNT    = 380
X_LEDS   = 560

Y_CLK    = 100
Y_EN     = 160
Y_GATE   = 130   # vertical midpoint of AND gate
Y_CNT    = 100
Y_LED_0  = 80
Y_STEP   = 50

# ── Circuit ──────────────────────────────────────────────────────────────────
circuit = Circuit("simple_counter")

# Inputs
circuit.add(Clock("clk",  x=X_PINS, y=Y_CLK, label="CLK"))
circuit.add(Pin("en",     x=X_PINS, y=Y_EN,  label="EN", is_input=True))

# Gated clock: CLK & EN → counter
circuit.add(Gate("and", "clk_gate", x=X_GATE, y=Y_GATE, label="AND"))
circuit.add(Wire("w_clk", f"{X_PINS},{Y_CLK}", f"{X_GATE},{Y_CLK}"))
circuit.add(Wire("w_en",  f"{X_PINS},{Y_EN}",  f"{X_GATE},{Y_EN}"))

# 4-bit counter
circuit.add(Counter("cnt0", x=X_CNT, y=Y_CNT, label="4-bit Counter"))
circuit.add(Wire("w_gate_cnt", f"{X_GATE+50},{Y_GATE}", f"{X_CNT},{Y_CNT}"))

# One LED per output bit
for bit in range(4):
    y = Y_LED_0 + bit * Y_STEP
    circuit.add(Led(f"q{bit}", x=X_LEDS, y=y, label=f"Q{bit}"))

output = Path(__file__).with_name("simple_counter_blueprint.json")
circuit.save_to(output)
print(f"[simple_counter] blueprint written → {output}")
