"""
shift_register.py
=================
An 8-bit serial-in / parallel-out (SIPO) shift register with:
  - Serial data input
  - Synchronous clock
  - Active-high parallel load override
  - Asynchronous clear
  - All 8 output bits displayed on individual LEDs

Circuit topology
----------------
  DATA_IN (Pin) ──────────────> ShiftReg serial-in
  CLK     (Pin) ──────────────> ShiftReg clock
  LOAD    (Pin) ──────────────> ShiftReg parallel-load
  CLR     (Pin) ──────────────> ShiftReg clear
  D0..D7  (Pins) ─────────────> ShiftReg parallel data-in

  ShiftReg Q0..Q7 ──> LEDs + Probe on Q0 (LSB, first shifted out)

Operation
---------
  On each CLK↑ the register shifts its stored bits one position to the
  right and captures DATA_IN as the new MSB (Q7).  Q0 is the oldest
  bit and exits the register.  Asserting LOAD captures D0..D7 directly
  in parallel on the next clock edge.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
BITS     = 8
X_CTRL   = 60
X_DATA   = 60
X_SR     = 320
X_LEDS   = 540

Y_CTRL_0 = 60     # top of control signals column
Y_STEP_C = 50
Y_DATA_0 = Y_CTRL_0 + 4 * Y_STEP_C + 20   # data bus starts below controls
Y_STEP_D = 40

Y_SERIAL = Y_CTRL_0
Y_CLK    = Y_CTRL_0 + Y_STEP_C
Y_LOAD   = Y_CTRL_0 + 2 * Y_STEP_C
Y_CLR    = Y_CTRL_0 + 3 * Y_STEP_C

output = Path(__file__).with_name("shift_register_blueprint.json")

builder = BlueprintBuilder("shift_register")

# ── Control signals ──────────────────────────────────────────────────────────
builder.add_pin("data_in", x=X_CTRL, y=Y_SERIAL, label="DATA-IN")
builder.add_clock("clk",   x=X_CTRL, y=Y_CLK,    label="CLK")
builder.add_pin("load",    x=X_CTRL, y=Y_LOAD,   label="LOAD")
builder.add_pin("clr",     x=X_CTRL, y=Y_CLR,    label="CLR")

# ── Parallel data bus ────────────────────────────────────────────────────────
for bit in range(BITS):
    y = Y_DATA_0 + bit * Y_STEP_D
    builder.add_pin(f"d{bit}", x=X_DATA, y=y, label=f"D{bit}")

# ── Shift register ────────────────────────────────────────────────────────────
builder.add_shift_register("sr0", x=X_SR, y=Y_SERIAL, label="8-bit Shift Reg")

# Control wires
builder.add_wire("w_din",  f"{X_CTRL},{Y_SERIAL}", f"{X_SR},{Y_SERIAL}")
builder.add_wire("w_clk",  f"{X_CTRL},{Y_CLK}",    f"{X_SR},{Y_CLK}")
builder.add_wire("w_load", f"{X_CTRL},{Y_LOAD}",   f"{X_SR},{Y_LOAD}")
builder.add_wire("w_clr",  f"{X_CTRL},{Y_CLR}",    f"{X_SR},{Y_CLR}")

# Parallel data wires
for bit in range(BITS):
    y = Y_DATA_0 + bit * Y_STEP_D
    builder.add_wire(f"w_d{bit}", f"{X_DATA},{y}", f"{X_SR},{y}")

# ── Outputs ───────────────────────────────────────────────────────────────────
for bit in range(BITS):
    y = Y_DATA_0 + bit * Y_STEP_D
    builder.add_led(f"q{bit}", x=X_LEDS, y=y, label=f"Q{bit}")

# Probe on Q0 (LSB / serial output)
builder.add_probe("serial_out", x=X_LEDS + 80, y=Y_DATA_0, label="SOUT-probe")
builder.add_wire("w_sout_probe", f"{X_LEDS},{Y_DATA_0}", f"{X_LEDS + 80},{Y_DATA_0}")

builder.save(output)
print(f"[shift_register] 8-bit SIPO shift register blueprint written → {output}")
