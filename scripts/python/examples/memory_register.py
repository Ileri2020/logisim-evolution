"""
memory_register.py
==================
A clocked 8-bit register with write-enable, reset, and output display.

Circuit topology
----------------
  D0..D7 (Pins)  ──────────────────────> Register data-in
  CLK    (Pin)   ──────────────────────> Register clock
  WE     (Pin)   ──> AND gate ─────────> Register write-enable
  RST    (Pin)   ──> NOT ──────────────> Register reset (active-low)

  Register Q0..Q7 ──> Probe + HEX display + 8 LEDs

Behaviour
---------
  WE=0  : Register holds its stored value (no update)
  WE=1  : On CLK↑, register captures D0..D7 into its storage
  RST=1 : Asynchronous reset – Q returns to 0x00 immediately

  The hex display shows the current register value in hexadecimal.
  Individual LEDs show each bit of the stored byte.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
BITS     = 8
X_DATA   = 60
X_CTRL   = 60
X_AND    = 220
X_NOT    = 220
X_REG    = 380
X_HEX    = 580
X_LEDS   = 740

Y_DATA_0 = 60    # first data pin
Y_STEP   = 40
Y_CLK    = Y_DATA_0 + BITS * Y_STEP + 20
Y_WE     = Y_CLK + 50
Y_RST    = Y_WE  + 50

output = Path(__file__).with_name("memory_register_blueprint.json")

builder = BlueprintBuilder("memory_register")

# ── 8-bit Data input bus ─────────────────────────────────────────────────────
for bit in range(BITS):
    y = Y_DATA_0 + bit * Y_STEP
    builder.add_pin(f"d{bit}", x=X_DATA, y=y, label=f"D{bit}")

# ── Control inputs ───────────────────────────────────────────────────────────
builder.add_clock("clk", x=X_CTRL, y=Y_CLK, label="CLK")
builder.add_pin("we",    x=X_CTRL, y=Y_WE,  label="WE")
builder.add_pin("rst",   x=X_CTRL, y=Y_RST, label="RST")

# Write-enable AND gate (gating CLK with WE)
builder.add_and_gate("and_we",  x=X_AND, y=Y_WE,  label="WE-Gate")
builder.add_wire("w_we_in",  f"{X_CTRL},{Y_WE}", f"{X_AND},{Y_WE}")

# RST inverter (RST pin active-high → register reset active-low)
builder.add_not_gate("inv_rst", x=X_NOT, y=Y_RST, label="INV-RST")
builder.add_wire("w_rst_in",  f"{X_CTRL},{Y_RST}", f"{X_NOT},{Y_RST}")
builder.add_wire("w_rst_out", f"{X_NOT+50},{Y_RST}", f"{X_REG},{Y_RST}")

# ── Register ─────────────────────────────────────────────────────────────────
builder.add_register("reg0", x=X_REG, y=Y_DATA_0, label="8-bit Reg")

# D0..D7 → Register data-in
for bit in range(BITS):
    y = Y_DATA_0 + bit * Y_STEP
    builder.add_wire(f"w_d{bit}", f"{X_DATA},{y}", f"{X_REG},{y}")

# CLK → Register clock
builder.add_wire("w_clk",   f"{X_CTRL},{Y_CLK}",       f"{X_REG},{Y_CLK}")
# WE-gate out → Register write-enable
builder.add_wire("w_we_out", f"{X_AND+50},{Y_WE}",     f"{X_REG},{Y_WE}")

# ── Outputs ───────────────────────────────────────────────────────────────────
# Hex display for byte value
builder.add_hex_digit_display("hex0", x=X_HEX, y=Y_DATA_0, label="HEX-Q")
builder.add_wire("w_hex", f"{X_REG+80},{Y_DATA_0}", f"{X_HEX},{Y_DATA_0}")

# Individual bit LEDs
for bit in range(BITS):
    y = Y_DATA_0 + bit * Y_STEP
    builder.add_led(f"q{bit}", x=X_LEDS, y=y, label=f"Q{bit}")

# Probe on MSB
builder.add_probe("msb_probe", x=X_LEDS, y=Y_DATA_0 - 40, label="Q7-probe")
builder.add_wire("w_msb_p", f"{X_LEDS},{Y_DATA_0}", f"{X_LEDS},{Y_DATA_0 - 40}")

builder.save(output)
print(f"[memory_register] 8-bit register blueprint written → {output}")
