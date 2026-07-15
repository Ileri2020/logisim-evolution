"""
d_flip_flop.py
==============
D flip-flop with asynchronous clear (reset) and output probe.

Circuit topology
----------------
  D   (Pin) ────────────────> DFF data-input (D)
  CLK (Pin) ────────────────> DFF clock
  CLR (Pin) ──> NOT ────────> DFF clear (active-low → invert)

  DFF Q  ──> Q_LED  (data output)
  DFF Q' ──> QB_LED (complement output)

Behaviour
---------
  On every rising CLK edge the DFF captures the value present on D and
  presents it at Q.  Asserting CLR (=1) resets Q to 0 asynchronously
  (independently of the clock), giving an active-high clear interface
  via the inverter.

  Verifying the circuit:
    CLR=0, D=1, CLK↑  →  Q=1, Q'=0
    CLR=1             →  Q=0, Q'=1  (async)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_IN   = 60
X_INV  = 200   # NOT gate for CLR
X_DFF  = 360
X_OUT  = 560

Y_D    = 100
Y_CLK  = 160
Y_CLR  = 220
Y_QB   = 220   # Q-bar output row

output = Path(__file__).with_name("d_flip_flop_blueprint.json")

builder = BlueprintBuilder("d_flip_flop")

# ── Inputs ───────────────────────────────────────────────────────────────────
builder.add_pin("d",   x=X_IN, y=Y_D,   label="D")
builder.add_pin("clk", x=X_IN, y=Y_CLK, label="CLK")
builder.add_pin("clr", x=X_IN, y=Y_CLR, label="CLR")

# ── Active-high → active-low clear conversion ─────────────────────────────
builder.add_not_gate("inv_clr", x=X_INV, y=Y_CLR, label="INV-CLR")
builder.add_wire("w_clr_in",  f"{X_IN},{Y_CLR}",      f"{X_INV},{Y_CLR}")
builder.add_wire("w_clr_out", f"{X_INV+50},{Y_CLR}",  f"{X_DFF},{Y_CLR}")

# ── D flip-flop ───────────────────────────────────────────────────────────────
builder.add_d_flip_flop("dff0", x=X_DFF, y=Y_D, label="DFF")

# D → DFF
builder.add_wire("w_d",   f"{X_IN},{Y_D}",   f"{X_DFF},{Y_D}")
# CLK → DFF
builder.add_wire("w_clk", f"{X_IN},{Y_CLK}", f"{X_DFF},{Y_CLK}")

# ── Outputs ───────────────────────────────────────────────────────────────────
builder.add_led("q_led",  x=X_OUT, y=Y_D,   label="Q")
builder.add_led("qb_led", x=X_OUT, y=Y_QB,  label="Q'")
builder.add_probe("q_probe", x=X_OUT, y=Y_D + 60, label="Q-probe")

# DFF Q  → LED and probe
builder.add_wire("w_q",  f"{X_DFF+80},{Y_D}",  f"{X_OUT},{Y_D}")
builder.add_wire("w_qp", f"{X_DFF+80},{Y_D}",  f"{X_OUT},{Y_D + 60}")
# DFF Q' → LED
builder.add_wire("w_qb", f"{X_DFF+80},{Y_QB}", f"{X_OUT},{Y_QB}")

builder.save(output)
print(f"[d_flip_flop] blueprint written → {output}")
