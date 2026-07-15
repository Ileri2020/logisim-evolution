"""
advanced_counter.py
===================
A 4-bit modulo-N counter with synchronous load and enable control.

Circuit topology
----------------
  CLK  ──────────────────────────> Counter (sync)
  EN   (Pin) ──> AND gate ──────> Counter enable-in
  LOAD (Pin) ──> Counter load-in
  D0..D3 (Pins) ──> Counter data-in

  Counter Q0..Q3 ──> LEDs

Features demonstrated
---------------------
* Gate-controlled counter enable (only counts when EN = 1)
* Synchronous load from external 4-bit bus (D0–D3)
* Output displayed on four individual bit LEDs plus a hex display
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_CTRL   = 60    # control inputs column
X_GATE   = 220   # enable AND gate
X_CNT    = 380   # counter
X_DATA   = 60    # data input pins column
X_HEX    = 560   # hex display
X_LEDS   = 700   # bit LEDs

Y_CLK    = 100
Y_EN     = 160
Y_LOAD   = 220
Y_DATA_0 = 320
Y_STEP   = 50

output = Path(__file__).with_name("advanced_counter_blueprint.json")

builder = BlueprintBuilder("advanced_counter")

# ── Control signals ──────────────────────────────────────────────────────────
builder.add_clock("clk",   x=X_CTRL, y=Y_CLK,  label="CLK")
builder.add_pin("en",      x=X_CTRL, y=Y_EN,   label="EN")
builder.add_pin("load",    x=X_CTRL, y=Y_LOAD, label="LOAD")

# Data input bus D0..D3
for bit in range(4):
    builder.add_pin(f"d{bit}", x=X_DATA, y=Y_DATA_0 + bit * Y_STEP, label=f"D{bit}")

# ── Enable gate: EN → AND → counter-enable ───────────────────────────────────
builder.add_and_gate("and_en", x=X_GATE, y=Y_EN, label="EN-Gate")
builder.add_wire("w_en",  f"{X_CTRL},{Y_EN}",  f"{X_GATE},{Y_EN}")

# ── Counter ──────────────────────────────────────────────────────────────────
builder.add_counter("cnt0", x=X_CNT, y=Y_CLK, label="4-bit Counter")

# CLK → Counter
builder.add_wire("w_clk",  f"{X_CTRL},{Y_CLK}",   f"{X_CNT},{Y_CLK}")
# AND-gate out → Counter enable
builder.add_wire("w_gate", f"{X_GATE+60},{Y_EN}", f"{X_CNT},{Y_EN}")
# LOAD → Counter
builder.add_wire("w_load", f"{X_CTRL},{Y_LOAD}",  f"{X_CNT},{Y_LOAD}")

# D0..D3 → Counter data-in
for bit in range(4):
    y = Y_DATA_0 + bit * Y_STEP
    builder.add_wire(f"w_d{bit}", f"{X_DATA},{y}", f"{X_CNT},{y}")

# ── Outputs ──────────────────────────────────────────────────────────────────
# Hex digit display for full 4-bit value
builder.add_hex_digit_display("hex0", x=X_HEX, y=Y_CLK, label="HEX")
builder.add_wire("w_hex", f"{X_CNT+80},{Y_CLK}", f"{X_HEX},{Y_CLK}")

# Individual bit LEDs
for bit in range(4):
    y = Y_DATA_0 + bit * Y_STEP
    builder.add_led(f"q{bit}", x=X_LEDS, y=y, label=f"Q{bit}")

builder.save(output)
print(f"[advanced_counter] blueprint written → {output}")
