"""
t_flip_flop.py
==============
A T (Toggle) flip-flop built from a D flip-flop with Q' fed back to D.

Background
----------
A T-FF toggles its state (Q flips) on each rising clock edge when T=1,
and holds when T=0.  This makes it ideal for binary frequency division:
each T-FF stage halves the clock frequency.

Circuit topology (frequency divider chain)
------------------------------------------
  CLK ──────────> DFF0-clk  DFF0-Q ──> DFF1-clk  DFF1-Q ──> DFF2-clk
       ┌── NOT0 <── DFF0-Q'    ┌── NOT1 <── DFF1-Q'    ┌── NOT2 <── DFF2-Q'
       └──> DFF0-D             └──> DFF1-D              └──> DFF2-D

Output frequencies
------------------
  CLK   : base frequency  f
  Q0    : f / 2
  Q1    : f / 4
  Q2    : f / 8

The result is a 3-bit binary ripple counter with LEDs on each stage.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
STAGES  = 3          # number of T-FF stages
X_CLK   = 60
X_STEP  = 200        # horizontal spacing between stages
X_FIRST = 200        # first DFF
Y_DFF   = 120
Y_INV   = 220        # NOT gate (Q' → D feedback)
Y_LED   = 320

output = Path(__file__).with_name("t_flip_flop_blueprint.json")

builder = BlueprintBuilder("t_flip_flop")

# ── Master clock ──────────────────────────────────────────────────────────────
builder.add_clock("clk", x=X_CLK, y=Y_DFF, label="CLK")

for stage in range(STAGES):
    x_dff = X_FIRST + stage * X_STEP
    x_inv = x_dff
    x_led = x_dff + 120

    # D Flip-Flop
    builder.add_d_flip_flop(f"dff{stage}", x=x_dff, y=Y_DFF,
                            label=f"TFF{stage}")
    # NOT gate to feed Q' back to D
    builder.add_not_gate(f"inv{stage}", x=x_inv, y=Y_INV,
                         label=f"INV{stage}")
    # Q output LED
    builder.add_led(f"q{stage}", x=x_led, y=Y_LED,
                    label=f"Q{stage} (f/{2**(stage+1)})")

    # CLK → DFF clock input
    if stage == 0:
        builder.add_wire(f"w_clk{stage}",
                         f"{X_CLK},{Y_DFF}",
                         f"{x_dff},{Y_DFF}")
    else:
        # Previous stage Q → this stage CLK
        x_prev_out = X_FIRST + (stage - 1) * X_STEP + 80
        builder.add_wire(f"w_clk{stage}",
                         f"{x_prev_out},{Y_DFF}",
                         f"{x_dff},{Y_DFF}")

    # Q' (DFF) → NOT input
    builder.add_wire(f"w_qb{stage}",
                     f"{x_dff + 80},{Y_DFF + 20}",
                     f"{x_inv},{Y_INV}")
    # NOT output → DFF D input
    builder.add_wire(f"w_d{stage}",
                     f"{x_inv + 50},{Y_INV}",
                     f"{x_dff},{Y_DFF - 20}")

    # Q → LED
    builder.add_wire(f"w_q{stage}",
                     f"{x_dff + 80},{Y_DFF}",
                     f"{x_led},{Y_LED}")

builder.save(output)
print(f"[t_flip_flop] {STAGES}-stage ripple counter (T-FF chain) blueprint written → {output}")
