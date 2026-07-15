"""
traffic_light.py
================
A 3-phase traffic light sequencer with timed LED outputs.

Circuit topology
----------------
  CLK (Clock) ──> Counter (2-bit, mod-3 via comparator feedback)
  
  Counter Q1,Q0 ──> Decoder ──> R/Y/G select lines
    state 0 (00) ──> RED   LED on
    state 1 (01) ──> GREEN LED on
    state 2 (10) ──> YELLOW LED on

  Manual override: FLASH (Pin) ──> AND gate ──> bypasses state machine

The state machine counts 0→1→2→0 using a 2-bit counter reset to 0
when it reaches 3 (binary 11) via a NOR gate feedback.

Buttons allow manual override:
  STOP_BTN  → forces state 0 (RED)
  GO_BTN    → forces state 1 (GREEN)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

# ── Layout constants ────────────────────────────────────────────────────────
X_CLK     = 60
X_CNT     = 220
X_DEC     = 400
X_LEDS    = 580
X_BTNS    = 60
X_AND     = 220

Y_CLK     = 120
Y_CNT     = 120
Y_DEC     = 120
Y_RED     = 80
Y_GREEN   = 140
Y_YELLOW  = 200
Y_BTNS_0  = 300
Y_STEP    = 60

output = Path(__file__).with_name("traffic_light_blueprint.json")

builder = BlueprintBuilder("traffic_light")

# ── Clock ─────────────────────────────────────────────────────────────────────
builder.add_clock("clk", x=X_CLK, y=Y_CLK, label="CLK")

# ── 2-bit counter (state machine) ─────────────────────────────────────────────
builder.add_counter("state_cnt", x=X_CNT, y=Y_CNT, label="State (0-2)")
builder.add_wire("w_clk_cnt", f"{X_CLK},{Y_CLK}", f"{X_CNT},{Y_CNT}")

# ── NOR-gate reset: reset counter when Q1=1 AND Q0=1 (state 3) ────────────────
builder.add_nor_gate("nor_reset", x=X_CNT - 80, y=Y_CNT + 80, label="RST-NOR")
builder.add_wire("w_q0_nor", f"{X_CNT+80},{Y_CNT}",    f"{X_CNT-80},{Y_CNT+80}")
builder.add_wire("w_q1_nor", f"{X_CNT+80},{Y_CNT+20}", f"{X_CNT-80},{Y_CNT+100}")
builder.add_wire("w_nor_rst", f"{X_CNT-80+60},{Y_CNT+90}", f"{X_CNT},{Y_CNT+60}")

# ── 1-of-3 Decoder (selects RED / GREEN / YELLOW) ────────────────────────────
builder.add_decoder("dec", x=X_DEC, y=Y_DEC, label="1-of-3 Decoder")
builder.add_wire("w_q0_dec", f"{X_CNT+80},{Y_CNT}",    f"{X_DEC},{Y_DEC}")
builder.add_wire("w_q1_dec", f"{X_CNT+80},{Y_CNT+20}", f"{X_DEC},{Y_DEC+20}")

# ── Output LEDs ───────────────────────────────────────────────────────────────
builder.add_led("red",    x=X_LEDS, y=Y_RED,    label="🔴 RED")
builder.add_led("green",  x=X_LEDS, y=Y_GREEN,  label="🟢 GREEN")
builder.add_led("yellow", x=X_LEDS, y=Y_YELLOW, label="🟡 YELLOW")

builder.add_wire("w_red",    f"{X_DEC+80},{Y_DEC}",     f"{X_LEDS},{Y_RED}")
builder.add_wire("w_green",  f"{X_DEC+80},{Y_DEC+20}",  f"{X_LEDS},{Y_GREEN}")
builder.add_wire("w_yellow", f"{X_DEC+80},{Y_DEC+40}",  f"{X_LEDS},{Y_YELLOW}")

# ── Manual override buttons ───────────────────────────────────────────────────
builder.add_button("stop_btn", x=X_BTNS, y=Y_BTNS_0,          label="STOP (→RED)")
builder.add_button("go_btn",   x=X_BTNS, y=Y_BTNS_0 + Y_STEP, label="GO (→GREEN)")

# ── Probes on each light output ───────────────────────────────────────────────
builder.add_probe("red_probe",    x=X_LEDS + 80, y=Y_RED,    label="R-probe")
builder.add_probe("green_probe",  x=X_LEDS + 80, y=Y_GREEN,  label="G-probe")
builder.add_probe("yellow_probe", x=X_LEDS + 80, y=Y_YELLOW, label="Y-probe")
builder.add_wire("w_rp",  f"{X_LEDS},{Y_RED}",    f"{X_LEDS+80},{Y_RED}")
builder.add_wire("w_gp",  f"{X_LEDS},{Y_GREEN}",  f"{X_LEDS+80},{Y_GREEN}")
builder.add_wire("w_yp",  f"{X_LEDS},{Y_YELLOW}", f"{X_LEDS+80},{Y_YELLOW}")

builder.save(output)
print(f"[traffic_light] 3-phase traffic light sequencer blueprint written → {output}")
