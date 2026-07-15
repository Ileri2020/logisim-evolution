"""
sr_latch.py
===========
An SR latch built using the dedicated SRLatch component, with debounced
button inputs and output probes.

Circuit topology
----------------
  S-Button (Button) ──> Debouncer ──> SR-Latch S input
  R-Button (Button) ──> Debouncer ──> SR-Latch R input

  SR-Latch Q  ──> Q_LED  + Q-Probe
  SR-Latch Q' ──> QB_LED + QB-Probe

Using Buttons with Debouncers
------------------------------
Physical buttons bounce (toggle rapidly) for a few ms on each press.
A debouncer filters out this noise so the latch sees only clean edges.
In Logisim this models the real-world concern even though the simulator
doesn't model bouncing; the Debouncer component is still instructive.

Truth table
-----------
  S  R  |  Q   Q'  | State
  ───────┼───────────┼──────────────
  0  0  |  Q   Q'  | Hold
  0  1  |  0   1   | Reset
  1  0  |  1   0   | Set
  1  1  |  X   X   | Forbidden
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_BTN  = 60
X_DEB  = 180
X_LAT  = 360
X_OUT  = 540
X_PRB  = 660

Y_S    = 120
Y_R    = 220

output = Path(__file__).with_name("sr_latch_blueprint.json")

builder = BlueprintBuilder("sr_latch")

# ── Inputs (buttons with debounce) ───────────────────────────────────────────
builder.add_button("btn_s", x=X_BTN, y=Y_S, label="S")
builder.add_button("btn_r", x=X_BTN, y=Y_R, label="R")

builder.add_debouncer("deb_s", x=X_DEB, y=Y_S, label="Deb-S")
builder.add_debouncer("deb_r", x=X_DEB, y=Y_R, label="Deb-R")

# Buttons → Debouncers
builder.add_wire("w_s_btn", f"{X_BTN+40},{Y_S}", f"{X_DEB},{Y_S}")
builder.add_wire("w_r_btn", f"{X_BTN+40},{Y_R}", f"{X_DEB},{Y_R}")

# ── SR Latch ─────────────────────────────────────────────────────────────────
builder.add_sr_latch("latch0", x=X_LAT, y=Y_S, label="SR-Latch")

# Debouncers → Latch
builder.add_wire("w_s", f"{X_DEB+40},{Y_S}", f"{X_LAT},{Y_S}")
builder.add_wire("w_r", f"{X_DEB+40},{Y_R}", f"{X_LAT},{Y_R}")

# ── Outputs ───────────────────────────────────────────────────────────────────
builder.add_led("q_led",  x=X_OUT, y=Y_S, label="Q")
builder.add_led("qb_led", x=X_OUT, y=Y_R, label="Q'")

builder.add_probe("q_prb",  x=X_PRB, y=Y_S, label="Q-probe")
builder.add_probe("qb_prb", x=X_PRB, y=Y_R, label="Q'-probe")

# Latch Q  → LED and probe
builder.add_wire("w_q",    f"{X_LAT+80},{Y_S}", f"{X_OUT},{Y_S}")
builder.add_wire("w_q_p",  f"{X_OUT},{Y_S}",    f"{X_PRB},{Y_S}")
# Latch Q' → LED and probe
builder.add_wire("w_qb",   f"{X_LAT+80},{Y_R}", f"{X_OUT},{Y_R}")
builder.add_wire("w_qb_p", f"{X_OUT},{Y_R}",    f"{X_PRB},{Y_R}")

builder.save(output)
print(f"[sr_latch] SR-latch with debounced buttons blueprint written → {output}")
