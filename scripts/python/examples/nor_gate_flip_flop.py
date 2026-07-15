"""
nor_gate_flip_flop.py
=====================
NOR-gate SR latch (set-reset flip-flop) built from two cross-coupled
NOR gates.  This is the most fundamental bistable memory element in
digital logic.

Circuit topology
----------------
  SET   (Pin) ─────────────┐
                           ├──> NOR0 ──> Q   ──> Q_LED
                    ┌──────┘              │
  RESET (Pin) ─────┼──────┐              │ (feedback)
                   │      └──> NOR1 ──> Q'──> QB_LED
                   └─────────────────────┘

Truth table (SR latch)
----------------------
  SET  RESET  |  Q   Q'   | State
  ────────────┼────────────┼──────────────────
   0     0    |  Q   Q'   | Hold (memory)
   0     1    |  0   1    | Reset
   1     0    |  1   0    | Set
   1     1    |  ?   ?    | Forbidden (both gates race)

The forbidden state (SET=RESET=1) is visually observable as both LEDs
may show 0 simultaneously when returning to S=R=0.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_IN     = 60
X_NOR    = 280
X_OUT    = 480
X_FB_L   = 180   # x of feedback vertical rail (left of NOR gates)
X_NOR_W  = 70    # approximate gate output x offset

Y_NOR0   = 120   # Q  row (NOR0 → set path)
Y_NOR1   = 240   # Q' row (NOR1 → reset path)
Y_SET    = Y_NOR0
Y_RESET  = Y_NOR1
Y_FB_TOP = Y_NOR0 + 30   # feedback wire routing rows
Y_FB_BOT = Y_NOR1 + 30

output = Path(__file__).with_name("nor_gate_flip_flop_blueprint.json")

builder = BlueprintBuilder("nor_gate_flip_flop")

# ── Inputs ───────────────────────────────────────────────────────────────────
builder.add_pin("set",   x=X_IN, y=Y_SET,   label="SET")
builder.add_pin("reset", x=X_IN, y=Y_RESET, label="RESET")

# ── NOR gates ─────────────────────────────────────────────────────────────────
builder.add_nor_gate("nor0", x=X_NOR, y=Y_NOR0, label="NOR0 (Q)")
builder.add_nor_gate("nor1", x=X_NOR, y=Y_NOR1, label="NOR1 (Q')")

# SET   → NOR0 input A
builder.add_wire("w_set",   f"{X_IN},{Y_SET}",   f"{X_NOR},{Y_NOR0}")
# RESET → NOR1 input A
builder.add_wire("w_reset", f"{X_IN},{Y_RESET}", f"{X_NOR},{Y_NOR1}")

# ── Cross-coupled feedback ────────────────────────────────────────────────────
# Q  (NOR0 out) ──> NOR1 input B  (routed right → down → left)
x_nor0_out = X_NOR + X_NOR_W
builder.add_wire("w_q_right",  f"{x_nor0_out},{Y_NOR0}",  f"{X_OUT - 20},{Y_NOR0}")
builder.add_wire("w_q_down",   f"{X_OUT - 20},{Y_NOR0}",  f"{X_OUT - 20},{Y_NOR1 - 10}")
builder.add_wire("w_q_to_nor1",f"{X_OUT - 20},{Y_NOR1 - 10}", f"{X_NOR},{Y_NOR1 - 10}")
builder.add_wire("w_q_nor1in", f"{X_NOR},{Y_NOR1 - 10}", f"{X_NOR},{Y_NOR1}")

# Q' (NOR1 out) ──> NOR0 input B  (routed right → up → left)
x_nor1_out = X_NOR + X_NOR_W
builder.add_wire("w_qb_right",  f"{x_nor1_out},{Y_NOR1}",   f"{X_OUT - 40},{Y_NOR1}")
builder.add_wire("w_qb_up",     f"{X_OUT - 40},{Y_NOR1}",   f"{X_OUT - 40},{Y_NOR0 + 10}")
builder.add_wire("w_qb_to_nor0",f"{X_OUT - 40},{Y_NOR0 + 10}", f"{X_NOR},{Y_NOR0 + 10}")
builder.add_wire("w_qb_nor0in", f"{X_NOR},{Y_NOR0 + 10}", f"{X_NOR},{Y_NOR0}")

# ── Outputs ───────────────────────────────────────────────────────────────────
builder.add_led("q_led",  x=X_OUT, y=Y_NOR0, label="Q")
builder.add_led("qb_led", x=X_OUT, y=Y_NOR1, label="Q'")
builder.add_probe("q_probe",  x=X_OUT + 80, y=Y_NOR0, label="Q-probe")
builder.add_probe("qb_probe", x=X_OUT + 80, y=Y_NOR1, label="Q'-probe")

# NOR0 → Q LED and probe
builder.add_wire("w_q_led",  f"{x_nor0_out},{Y_NOR0}", f"{X_OUT},{Y_NOR0}")
builder.add_wire("w_q_prb",  f"{X_OUT},{Y_NOR0}",      f"{X_OUT + 80},{Y_NOR0}")
# NOR1 → Q' LED and probe
builder.add_wire("w_qb_led", f"{x_nor1_out},{Y_NOR1}", f"{X_OUT},{Y_NOR1}")
builder.add_wire("w_qb_prb", f"{X_OUT},{Y_NOR1}",      f"{X_OUT + 80},{Y_NOR1}")

builder.save(output)
print(f"[nor_gate_flip_flop] SR latch blueprint written → {output}")
