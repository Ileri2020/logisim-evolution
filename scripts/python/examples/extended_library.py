"""
extended_library.py
===================
Showcase of the logisim_py extended component library.

This script places one representative component from every supported
category onto a grid layout so you can see the full breadth of what
the Python API can place on the canvas.

Categories demonstrated
-----------------------
  Wiring      : Pin, Probe, Splitter, Clock, Constant, Power, Ground, Tunnel
  Gates       : NOT, AND, OR, NAND, NOR, XOR, Buffer
  Plexers     : Multiplexer, Demultiplexer, Decoder, Priority Encoder
  Arithmetic  : Adder, Subtractor, Multiplier, Comparator, Shifter
  Floating-pt : FP Adder, FP Comparator
  Memory      : Register, RAM, ROM, Shift Register, Counter
  I/O         : Button, LED, DIP Switch, Hex Digit Display, Keyboard
  Flip-Flops  : D-FF, T-FF, JK-FF, SR-Latch
  TTL         : TTL 7400 (NAND quad)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("extended_library_blueprint.json")

builder = BlueprintBuilder("extended_library")

# ── Grid helper ──────────────────────────────────────────────────────────────
COLS   = 6
X0     = 60
Y0     = 60
DX     = 140
DY     = 90

def cell(idx):
    """Return (x, y) for component index idx in the grid."""
    col = idx % COLS
    row = idx // COLS
    return X0 + col * DX, Y0 + row * DY

components = [
    # Wiring
    ("pin",       "pin0",    "Pin"),
    ("probe",     "probe0",  "Probe"),
    ("splitter",  "split0",  "Splitter"),
    ("clock",     "clk0",    "Clock"),
    ("constant",  "const0",  "Constant"),
    ("power",     "pwr0",    "Power"),
    ("ground",    "gnd0",    "Ground"),
    ("tunnel",    "tun0",    "Tunnel"),
    # Gates
    ("not",       "inv0",    "NOT"),
    ("and",       "and0",    "AND"),
    ("or",        "or0",     "OR"),
    ("nand",      "nand0",   "NAND"),
    ("nor",       "nor0",    "NOR"),
    ("xor",       "xor0",    "XOR"),
    ("buffer",    "buf0",    "Buffer"),
    # Plexers
    ("mux",       "mux0",    "MUX"),
    ("demux",     "demux0",  "DEMUX"),
    ("decoder",   "dec0",    "Decoder"),
    # Arithmetic
    ("adder",     "add0",    "Adder"),
    ("subtractor","sub0",    "Subtractor"),
    ("multiplier","mul0",    "Multiplier"),
    ("comparator","cmp0",    "Comparator"),
    ("shifter",   "shf0",    "Shifter"),
    # Memory
    ("register",      "reg0",  "Register"),
    ("counter",       "cnt0",  "Counter"),
    ("shift_register","sr0",   "Shift Reg"),
    ("ram",           "ram0",  "RAM"),
    ("rom",           "rom0",  "ROM"),
    # I/O
    ("button",         "btn0",  "Button"),
    ("led",            "led0",  "LED"),
    ("dip_switch",     "sw0",   "DIP-SW"),
    ("hex_digit",      "hex0",  "Hex Disp"),
    ("keyboard",       "kbd0",  "Keyboard"),
    # Flip-flops
    ("d_flip_flop",    "dff0",  "D-FF"),
    ("t_flip_flop",    "tff0",  "T-FF"),
    ("jk_flip_flop",   "jkff0", "JK-FF"),
    ("sr_latch",       "sr_l0", "SR-Latch"),
    # Floating-point
    ("fp_adder",       "fpa0",  "FP-Adder"),
    ("fp_comparator",  "fpc0",  "FP-Cmp"),
    # TTL
    ("ttl_7400",       "ttl0",  "TTL-7400"),
]

for idx, (kind, name, label) in enumerate(components):
    x, y = cell(idx)
    # Use specific builder methods where available, else generic add_gate
    method_name = f"add_{kind}"
    if hasattr(builder, method_name):
        getattr(builder, method_name)(name, x=x, y=y, label=label)
    else:
        builder.add_gate(kind, name, x=x, y=y, label=label)

builder.save(output)
print(f"[extended_library] {len(components)} components placed → {output}")
