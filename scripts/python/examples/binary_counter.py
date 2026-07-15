"""
binary_counter.py
=================
A 4-bit binary counter driven by a clock signal.

Circuit topology
----------------
  CLK (Pin) ──> Counter (4-bit) ──> Q0..Q3 (LED x4)

The counter increments on every rising clock edge and rolls over from
15 (0b1111) back to 0 automatically.  Four LEDs show the current state
of each output bit.

Works in both offline (saves a JSON blueprint) and live embedded mode
(places components directly onto the active Logisim canvas).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_CLK    = 80
X_CNT    = 260
X_LEDS   = 440
Y_BASE   = 100
Y_STEP   = 50

output = Path(__file__).with_name("binary_counter_blueprint.json")

builder = BlueprintBuilder("binary_counter")

# Clock source
builder.add_clock("clk", x=X_CLK, y=Y_BASE + Y_STEP, label="CLK")

# 4-bit synchronous counter
builder.add_counter("cnt0", x=X_CNT, y=Y_BASE + Y_STEP, label="4-bit Counter")

# Clock wire: CLK → Counter clock-enable input
builder.add_wire("w_clk", f"{X_CLK},{Y_BASE + Y_STEP}", f"{X_CNT},{Y_BASE + Y_STEP}")

# One LED per output bit (Q0 = LSB, Q3 = MSB)
for bit in range(4):
    y = Y_BASE + bit * Y_STEP
    builder.add_led(f"q{bit}", x=X_LEDS, y=y, label=f"Q{bit}")

builder.save(output)
print(f"[binary_counter] blueprint written → {output}")
