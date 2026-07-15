"""
bjt_oscillator.py
=================
Ring oscillator built from an odd number of NOT (inverter) gates.

Background
----------
A ring oscillator is the simplest self-sustaining digital oscillator.
By connecting an odd number of inverters in a feedback loop the output
continuously toggles, generating a square wave.  In hardware this is
used to characterise gate propagation delay; in Logisim it demonstrates
how oscillation emerges from feedback.

Circuit topology (5-stage ring)
---------------------------------
  ┌──> INV0 ──> INV1 ──> INV2 ──> INV3 ──> INV4 ──┐
  └─────────────────────────────────────────────────┘
           │
           └──> PROBE (observe oscillation)

Note: Logisim-evolution does not model propagation delay in the same
way real silicon does, so the oscillation is driven by the simulator's
event loop.  A PROBE is attached at the midpoint to observe the toggle.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
N_STAGES = 5          # must be odd for oscillation
X_START  = 80
X_STEP   = 120
Y_RING   = 160
Y_PROBE  = 280
Y_FEED   = Y_RING + 60   # feedback wire below the ring

output = Path(__file__).with_name("bjt_oscillator_blueprint.json")

builder = BlueprintBuilder("bjt_oscillator")

# ── Ring of N NOT gates ──────────────────────────────────────────────────────
for i in range(N_STAGES):
    x = X_START + i * X_STEP
    builder.add_not_gate(f"inv{i}", x=x, y=Y_RING, label=f"INV{i}")

# Chain: INV0→INV1→…→INV(N-1)
for i in range(N_STAGES - 1):
    x_out = X_START + i * X_STEP + 50          # output side of gate i
    x_in  = X_START + (i + 1) * X_STEP         # input side of gate i+1
    builder.add_wire(f"w{i}", f"{x_out},{Y_RING}", f"{x_in},{Y_RING}")

# Feedback: last gate output → first gate input (route below the ring)
x_last_out = X_START + (N_STAGES - 1) * X_STEP + 50
x_first_in = X_START

builder.add_wire("w_fb_right", f"{x_last_out},{Y_RING}", f"{x_last_out},{Y_FEED}")
builder.add_wire("w_fb_bottom", f"{x_last_out},{Y_FEED}", f"{x_first_in},{Y_FEED}")
builder.add_wire("w_fb_left",  f"{x_first_in},{Y_FEED}", f"{x_first_in},{Y_RING}")

# ── Observation probe at midpoint of ring ────────────────────────────────────
mid = N_STAGES // 2
x_mid_out = X_START + mid * X_STEP + 50
builder.add_probe("osc_out", x=x_mid_out, y=Y_PROBE, label="OSC-OUT")
builder.add_wire("w_probe", f"{x_mid_out},{Y_RING}", f"{x_mid_out},{Y_PROBE}")

# LED to visualise the toggling output
builder.add_led("led_osc", x=x_mid_out + 80, y=Y_PROBE, label="TOGGLE")
builder.add_wire("w_led", f"{x_mid_out},{Y_PROBE}", f"{x_mid_out + 80},{Y_PROBE}")

builder.save(output)
print(f"[bjt_oscillator] {N_STAGES}-stage ring oscillator blueprint written → {output}")
